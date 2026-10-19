#!/usr/bin/env python3
"""Software-observed control latency for paper Section 5.1.

Drives the real WebSocket control path and times how long the robot takes to
confirm each command in telemetry. Four probes:

  pan_echo      servo pan to a fresh angle -> that angle appears in telemetry
                (dashboard -> P1 -> UART -> Arduino -> telemetry -> dashboard)
  motor_start   motor command -> firmware reports DRIVING (ACTIVE)
  motor_stop    emergency stop -> firmware reports READY again
  deadman_trip  commands cease -> fw_state in telemetry reports STOPPED. The
                motors stop at protocol.DEADMAN_MS (2000 ms) plus the
                supervisor period and one loop pass, about 2060 ms; this
                metric adds the telemetry reporting delay below, so expect
                ~2.4 s here.
  deadman_panic same trip, timed from the firmware's immediate PANIC notice
                instead, read out of P1's event log. Expect ~2.06 s. Recorded
                alongside deadman_trip in the same trial.

IMPORTANT, state this in the paper: the Arduino emits a telemetry frame every
500 ms (arduino/config.h, TELEMETRY_PERIOD_MS) and P1 rebroadcasts on its own
200 ms timer (protocol.TELEMETRY_PERIOD_MS, 200 ms), so a confirmation that
waits on a telemetry field can lag the event by up to 700 ms, and by about
350 ms on average. These figures are UPPER BOUNDS, not the control latency
itself; the 240 fps video measurement (record.py latency_video) is the one that
measures true key-press-to-wheel motion. Report both and say which is which.

That delay is avoidable for the dead-man trip. The firmware also emits a
tagged PANIC line in the same supervisor pass that stops the motors, costing
only serial transit, but P1 does not forward it: p1_control/main.py calls
set_handlers with on_event=None, so it never reaches this WebSocket. It is
still written to P1's event log, so the deadman probe tails that log
(--p1-log) and records deadman_panic from the log line's own millisecond
timestamp. The log has to be local, so that metric needs this probe run on the
Pi; without it the probe still records deadman_trip and warns.

Reading the log rather than teaching P1 to forward the event is deliberate:
the control process is the system under test, and changing it partway through
the measurement campaign would put earlier results on a different build.
Forwarding firmware events to the operator remains worth doing as a design
improvement in its own right.

Each trial would otherwise fire immediately after a frame arrives, always
landing at the same point in the reporting cycle and producing a falsely tight
distribution at one phase. A uniform random 0-200 ms delay before each command
spreads trials across the P1 rebroadcast cycle instead. --no-jitter disables
it, which is only useful for demonstrating the artifact.

KNOWN LIMITATION of that jitter: 200 ms is one P1 period, but the slower cycle
a confirmation must clear is the firmware's 500 ms telemetry period, and a
200 ms delay cannot decorrelate a trial from a 500 ms cycle. Phase is therefore
sampled incompletely and the reported spread understates the true quantisation
spread; in the on-pi deadman_trip run this shows up as a minimum near 2200 ms
rather than near the ~2060 ms stop bound. Widening the delay to 500 ms would
fix it and would invalidate existing rows for comparison.

Run from the operator laptop for an end-to-end figure including Wi-Fi, or on
the Pi for the robot-internal figure.

    ./wslatency.py --host 127.0.0.1 --key "$CONTROLLER_KEY" --probe all
    ./wslatency.py --host 192.168.0.9 --key "$CONTROLLER_KEY" --probe pan --trials 30 --label wifi-10m
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]

COLUMNS = ("iso_ts", "probe", "metric", "trial", "label", "value_ms",
           "resolution_ms", "ok", "detail")

TELEMETRY_PERIOD_MS = 200  # P1 rebroadcast, protocol.TELEMETRY_PERIOD_MS
FW_TELEMETRY_PERIOD_MS = 500  # firmware frame, arduino/config.h
# A confirmation that waits on a telemetry field has to clear both cycles, so
# the quantisation on those metrics is the sum, not either one alone. Rows
# collected before this correction carry 200 in the resolution_ms column.
TELEMETRY_RESOLUTION_MS = FW_TELEMETRY_PERIOD_MS + TELEMETRY_PERIOD_MS
# The PANIC notice is timed from P1's own log timestamp, which logging_setup.py
# renders to milliseconds.
LOG_RESOLUTION_MS = 1
# Direct request/response: no telemetry cycle in the path.
DIRECT_RESOLUTION_MS = 0
# arduino/telemetry.cpp:62 maps firmware modes onto the three telemetry values:
# ACTIVE -> 2, READY -> 1, and BOOT/ESTOP/PANIC all -> 3. An ordinary stop
# command takes ACTIVE back to READY (arduino/command_parser.cpp:195), so a
# completed stop reads as 1; a 3 means a latched fault, which is what the
# dead-man trip produces.
FW_ARMED = 1      # READY: at rest and motion permitted
FW_DRIVING = 2    # ACTIVE: executing a motion command
FW_STOPPED = 3    # BOOT, ESTOP or PANIC: latched, motion refused
# Pan targets chosen away from the 90 deg centre and from each other, so each
# trial's echo is unambiguous even if a frame is dropped.
PAN_TARGETS = (20, 40, 60, 110, 130, 150, 170, 30, 70, 120)


class Link:
    """One controller session with a background reader and heartbeat."""

    def __init__(self, socket, label: str, jitter: bool = True) -> None:
        self.socket = socket
        self.label = label
        self.jitter = jitter
        self.frames: asyncio.Queue[dict] = asyncio.Queue()
        self.seq = 0
        self.beating = True
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        self._tasks = [
            asyncio.create_task(self._reader()),
            asyncio.create_task(self._heartbeat()),
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            try:
                await task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass

    async def _reader(self) -> None:
        async for raw in self.socket:
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(message, dict):
                await self.frames.put(message)

    async def _heartbeat(self) -> None:
        """500 ms idle heartbeat (protocol.HEARTBEAT_PERIOD_MS). Suspended by
        the dead-man probe, which needs the link to go deliberately silent."""
        while True:
            if self.beating:
                await self.send({"type": "heartbeat"})
            await asyncio.sleep(0.5)

    async def jittered_send(self, message: dict) -> float:
        """Send after a uniform random fraction of one telemetry period, so
        trials sample the 200 ms cycle evenly instead of all landing at the
        same phase. See the module docstring."""
        if self.jitter:
            await asyncio.sleep(random.uniform(0, TELEMETRY_PERIOD_MS / 1000))
        self.drain()
        return await self.send(message)

    async def send(self, message: dict) -> float:
        self.seq += 1
        message = {**message, "seq": self.seq}
        sent_at = time.perf_counter()
        await self.socket.send(json.dumps(message))
        return sent_at

    async def await_frame(self, predicate, timeout: float) -> tuple[dict | None, float]:
        """Next telemetry frame satisfying `predicate`, and when it arrived."""
        deadline = time.perf_counter() + timeout
        while True:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                return None, time.perf_counter()
            try:
                frame = await asyncio.wait_for(self.frames.get(), timeout=remaining)
            except asyncio.TimeoutError:
                return None, time.perf_counter()
            if frame.get("type") != "telemetry":
                continue
            if predicate(frame):
                return frame, time.perf_counter()

    def drain(self) -> None:
        while not self.frames.empty():
            self.frames.get_nowait()

    async def settle_ready(self, timeout: float = 6.0) -> bool:
        """Leave the firmware in READY so the next trial starts from rest.

        Waits for ARMED rather than merely "not driving": a latched dead-man
        fault also reads as not-driving, but refuses motion until the fault
        clears, which happens one loop after any command refreshes the
        dead-man timer (arduino/arduino.ino:99).
        """
        await self.send({"type": "stop_all"})
        self.drain()
        frame, _ = await self.await_frame(lambda f: f.get("fw_state") == FW_ARMED, timeout)
        return frame is not None


def record(out: Path, probe: str, metric: str, trial: int, label: str,
           value_ms: float | None, detail: str = "",
           resolution_ms: float = TELEMETRY_RESOLUTION_MS) -> None:
    append_row(out, COLUMNS, {
        "iso_ts": now_iso(), "probe": probe, "metric": metric, "trial": trial,
        "label": label, "value_ms": round(value_ms, 1) if value_ms is not None else "",
        "resolution_ms": resolution_ms, "ok": int(value_ms is not None),
        "detail": detail,
    })


def default_p1_log() -> Path:
    """Where P1 writes p1_events.log, mirroring common/config.py Paths."""
    explicit = os.environ.get("ROBOT_LOG_DIR")
    if explicit:
        return Path(explicit) / "p1_events.log"
    root = Path(os.environ.get("ROBOT_ROOT", "")) if os.environ.get("ROBOT_ROOT") else None
    if root is None:
        repo = Path(__file__).resolve().parents[2]
        root = repo / "var"
    log_dir = Path("/var/log/robot") if root == Path("/") else root / "log"
    return log_dir / "p1_events.log"


def _parse_log_ts(line: str) -> float | None:
    """Epoch seconds from the leading [ISO8601] field of an event line."""
    if not line.startswith("["):
        return None
    end = line.find("]")
    if end < 0:
        return None
    try:
        return datetime.fromisoformat(line[1:end]).timestamp()
    except ValueError:
        return None


class PanicLog:
    """Tails P1's event log for the immediate FW_PANIC notice.

    The firmware emits a tagged PANIC line in the same supervisor pass that
    stops the motors (arduino/arduino.ino:83), so that notice costs only serial
    transit. P1 logs it but does not forward it: p1_control/main.py calls
    set_handlers with on_event=None, so it never reaches the control WebSocket.
    Reading the log is therefore the only way to time the fast notice without
    modifying the control process, which would change the system under test
    partway through the measurement campaign.

    The reported value comes from the log line's own timestamp, not from when
    this tail noticed it, so the poll interval below does not affect accuracy.
    """

    POLL_S = 0.005

    def __init__(self, path: Path) -> None:
        self.path = path
        self._handle = None

    def open(self) -> bool:
        try:
            self._handle = self.path.open("r", encoding="utf-8", errors="replace")
        except OSError:
            return False
        self._handle.seek(0, os.SEEK_END)
        return True

    def mark(self) -> None:
        """Drop anything written before this trial's last command."""
        if self._handle is not None:
            self._handle.read()

    async def await_panic(self, timeout: float) -> float | None:
        """Epoch seconds of the next dead-man PANIC line, or None on timeout.

        A read can catch the writer mid-append, so a line is only considered
        once its terminator is present; otherwise the partial read is rewound
        and retried. Without that, a split line would drop a PANIC and the
        trial would look like a miss.
        """
        if self._handle is None:
            return None
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            position = self._handle.tell()
            line = self._handle.readline()
            if not line.endswith("\n"):
                self._handle.seek(position)
                await asyncio.sleep(self.POLL_S)
                continue
            if "[FW_PANIC]" in line and "DEADMAN" in line:
                return _parse_log_ts(line)
        return None

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None


async def probe_hello(args: argparse.Namespace, url: str) -> None:
    """Connect + hello -> ack. The transport floor the other probes sit on."""
    for trial in range(1, args.trials + 1):
        start = time.perf_counter()
        try:
            async with connect(url, open_timeout=10) as socket:
                await socket.send(json.dumps(
                    {"type": "hello", "role": "controller", "key": args.key}))
                ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
                elapsed = (time.perf_counter() - start) * 1000
            record(args.out, "hello", "hello_rtt", trial, args.label, elapsed,
                   f"role={ack.get('role')} auth={ack.get('auth')}",
                   resolution_ms=DIRECT_RESOLUTION_MS)
            print(f"  hello {trial}: {elapsed:.1f} ms")
        except (OSError, asyncio.TimeoutError, json.JSONDecodeError) as error:
            record(args.out, "hello", "hello_rtt", trial, args.label, None, str(error))
            print(f"  hello {trial}: FAILED ({error})")
        await asyncio.sleep(args.settle)


async def probe_pan(link: Link, args: argparse.Namespace) -> None:
    for trial in range(1, args.trials + 1):
        angle = PAN_TARGETS[trial % len(PAN_TARGETS)]
        sent_at = await link.jittered_send(
            {"type": "servo", "axis": "pan", "angle": angle})
        frame, arrived = await link.await_frame(
            lambda f, a=angle: f.get("pan_angle") == a, args.timeout)
        elapsed = (arrived - sent_at) * 1000 if frame else None
        record(args.out, "pan", "pan_echo", trial, args.label, elapsed, f"angle={angle}")
        print(f"  pan {trial}: {f'{elapsed:.1f} ms' if elapsed else 'TIMEOUT'} (angle {angle})")
        await asyncio.sleep(args.settle)


async def probe_motor(link: Link, args: argparse.Namespace) -> None:
    for trial in range(1, args.trials + 1):
        if not await link.settle_ready():
            record(args.out, "motor", "motor_start", trial, args.label, None,
                   "firmware did not report READY before trial")
            continue
        sent_at = await link.jittered_send(
            {"type": "motor", "dir": "F", "speed": args.speed})
        frame, arrived = await link.await_frame(
            lambda f: f.get("fw_state") == FW_DRIVING, args.timeout)
        start_ms = (arrived - sent_at) * 1000 if frame else None
        record(args.out, "motor", "motor_start", trial, args.label, start_ms,
               f"speed={args.speed}")

        await asyncio.sleep(args.drive_s)
        stop_at = await link.jittered_send({"type": "stop_all"})
        frame, arrived = await link.await_frame(
            lambda f: f.get("fw_state") == FW_ARMED, args.timeout)
        stop_ms = (arrived - stop_at) * 1000 if frame else None
        record(args.out, "motor", "motor_stop", trial, args.label, stop_ms,
               f"speed={args.speed}")
        print(f"  motor {trial}: start {start_ms and round(start_ms, 1)} ms  "
              f"stop {stop_ms and round(stop_ms, 1)} ms")
        await asyncio.sleep(args.settle)


async def probe_deadman(link: Link, args: argparse.Namespace,
                        panic_log: "PanicLog | None" = None) -> None:
    """Drive, then go silent. The motors stop at DEADMAN_MS plus the supervisor
    period and one loop pass, about 2060 ms.

    The firmware announces the trip on two paths, so each trial records two
    metrics rather than conflating them:

      deadman_panic  the tagged PANIC line, emitted in the same supervisor
                     pass that stops the motors. Read from P1's event log,
                     because P1 does not forward firmware events to the
                     WebSocket. This is the responsive path.
      deadman_trip   the fw_state field in periodic telemetry, which carries
                     up to 700 ms of reporting delay on top of the stop. Its
                     definition is unchanged from earlier runs, so previously
                     collected rows stay comparable.

    Neither is the stop time itself. That the wheels physically stop is test
    H7, recorded with record.py deadman_physical.
    """
    print("  (robot will drive briefly then dead-man stop on each trial -- keep it clear)")
    for trial in range(1, args.trials + 1):
        if not await link.settle_ready():
            record(args.out, "deadman", "deadman_trip", trial, args.label, None,
                   "firmware did not report READY before trial")
            continue
        link.beating = True
        await link.send({"type": "motor", "dir": "F", "speed": args.speed})
        frame, _ = await link.await_frame(lambda f: f.get("fw_state") == FW_DRIVING, args.timeout)
        if frame is None:
            record(args.out, "deadman", "deadman_trip", trial, args.label, None,
                   "never reached DRIVING")
            continue

        link.beating = False  # go silent: nothing re-arms the timer now
        if panic_log is not None:
            panic_log.mark()
        last_command = await link.jittered_send(
            {"type": "motor", "dir": "F", "speed": args.speed})
        # The same instant as last_command, on the wall clock the log uses.
        sent_wall = time.time() - (time.perf_counter() - last_command)

        # Both paths are watched concurrently so that waiting on one cannot
        # delay the timestamp taken for the other.
        panic_task = (asyncio.create_task(panic_log.await_panic(10.0))
                      if panic_log is not None else None)
        frame, arrived = await link.await_frame(
            lambda f: f.get("fw_state") == FW_STOPPED, timeout=10.0)
        elapsed = (arrived - last_command) * 1000 if frame else None
        panic_at = await panic_task if panic_task is not None else None
        link.beating = True

        panic_ms = (panic_at - sent_wall) * 1000 if panic_at is not None else None
        if panic_log is not None:
            record(args.out, "deadman", "deadman_panic", trial, args.label, panic_ms,
                   f"FW_PANIC log line, speed={args.speed}",
                   resolution_ms=LOG_RESOLUTION_MS)
        record(args.out, "deadman", "deadman_trip", trial, args.label, elapsed,
               f"fw_state in telemetry, expected ~2400 ms, speed={args.speed}")
        shown = f"{elapsed:.0f} ms" if elapsed else "NO TRIP (FAIL)"
        if panic_log is not None:
            shown += f" (PANIC at {f'{panic_ms:.0f} ms' if panic_ms else 'not seen'})"
        print(f"  deadman {trial}: {shown}")
        await asyncio.sleep(max(args.settle, 1.0))


async def run(args: argparse.Namespace) -> int:
    url = f"ws://{args.host}:{args.port}/control/ws"
    probes = ["pan", "motor", "deadman", "hello"] if args.probe == "all" else [args.probe]

    if "hello" in probes:
        print("probe: hello (connect + hello -> ack)")
        await probe_hello(args, url)
        probes.remove("hello")
    if not probes:
        print(f"\nwritten to {args.out}")
        return 0

    async with connect(url, open_timeout=10) as socket:
        await socket.send(json.dumps({"type": "hello", "role": "controller", "key": args.key}))
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
        if ack.get("role") != "controller":
            auth = ack.get("auth")
            print(f"refused: this session is '{ack.get('role')}' (auth={auth}); "
                  "the drive probes need the controller role.", file=sys.stderr)
            print({
                "no_key": "Pass --key. On the robot the live key is in a root-only drop-in:\n"
                          "  sudo grep CONTROLLER_KEY "
                          "/etc/systemd/system/robot-watchdog.service.d/controller-key.conf",
                "bad_key": "Wrong key. Five wrong keys lock this IP out for 5 minutes "
                           "(access.MAX_FAILURES / LOCKOUT_S), so check it before retrying.",
                "locked": f"This IP is locked out; retry in "
                          f"{ack.get('retry_after_s', '?')}s.",
                "disabled": "CONTROLLER_KEY is not set on the service, so nobody can control "
                            "the robot. Set it and restart robot-watchdog before testing.",
            }.get(auth, "Another dashboard may already hold the controller role."),
                file=sys.stderr)
            return 2

        panic_log = None
        if "deadman" in probes:
            candidate = PanicLog(args.p1_log)
            if candidate.open():
                panic_log = candidate
                print(f"  tailing {args.p1_log} for the FW_PANIC notice")
            else:
                print(f"WARNING: cannot read {args.p1_log}; recording "
                      "deadman_trip only, without the fast PANIC path. "
                      "Run this probe on the Pi, or pass --p1-log.",
                      file=sys.stderr)

        link = Link(socket, args.label, jitter=args.jitter)
        await link.start()
        try:
            for probe in probes:
                print(f"probe: {probe}")
                if probe == "pan":
                    await probe_pan(link, args)
                elif probe == "motor":
                    await probe_motor(link, args)
                elif probe == "deadman":
                    await probe_deadman(link, args, panic_log)
            await link.settle_ready()
        finally:
            await link.stop()
            if panic_log is not None:
                panic_log.close()

    print(f"\nwritten to {args.out}")
    print(f"NOTE: metrics confirmed through telemetry carry up to "
          f"{TELEMETRY_RESOLUTION_MS} ms of quantisation "
          f"({FW_TELEMETRY_PERIOD_MS} ms firmware frame + {TELEMETRY_PERIOD_MS} ms "
          "P1 rebroadcast) and are upper bounds, not stop or control latency. "
          "deadman_panic is the exception: it is timed from P1's log line.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--key", default="", help="CONTROLLER_KEY (required to send commands)")
    parser.add_argument("--probe", default="all", choices=["all", "pan", "motor", "deadman", "hello"])
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--label", default="local", help="condition label, e.g. wifi-10m")
    parser.add_argument("--speed", type=int, default=150, help="motor PWM for drive probes")
    parser.add_argument("--drive-s", type=float, default=0.6, help="how long to drive before stopping")
    parser.add_argument("--settle", type=float, default=0.5, help="pause between trials")
    parser.add_argument("--timeout", type=float, default=5.0, help="per-trial confirmation timeout")
    parser.add_argument("--no-jitter", dest="jitter", action="store_false",
                        help="send without phase jitter (demonstrates the artifact)")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR / "latency.csv")
    parser.add_argument("--p1-log", type=Path, default=default_p1_log(),
                        help="P1 event log, tailed for the FW_PANIC notice "
                             "in the dead-man probe (must be local to P1)")
    args = parser.parse_args()
    if args.probe in ("all", "motor", "deadman"):
        print("WARNING: the motor and dead-man probes make the robot DRIVE. "
              "Put it on blocks or in clear space.")
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
