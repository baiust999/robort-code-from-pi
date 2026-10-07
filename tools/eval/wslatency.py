#!/usr/bin/env python3
"""Software-observed control latency for paper Section 5.1.

Drives the real WebSocket control path and times how long the robot takes to
confirm each command in telemetry. Four probes:

  pan_echo      servo pan to a fresh angle -> that angle appears in telemetry
                (dashboard -> P1 -> UART -> Arduino -> telemetry -> dashboard)
  motor_start   motor command -> firmware reports DRIVING (ACTIVE)
  motor_stop    emergency stop -> firmware reports READY again
  deadman_trip  commands cease -> firmware reports STOPPED (expect ~2.0 s,
                protocol.DEADMAN_MS)

IMPORTANT, state this in the paper: the Arduino emits a telemetry frame every
200 ms and P1 rebroadcasts on its own 200 ms timer (protocol.TELEMETRY_PERIOD_MS),
so a confirmation can lag the command by up to two periods. These figures are
UPPER BOUNDS, not the control latency itself; the 240 fps video measurement
(record.py latency_video) is the one that measures true key-press-to-wheel
motion. Report both and say which is which.

Each trial would otherwise fire immediately after a frame arrives, always
landing at the same point in the 200 ms cycle and producing a falsely tight
distribution at the worst-case phase. A uniform random 0-200 ms delay before
each command samples the cycle evenly instead, so the spread in the results is
the real quantisation spread. --no-jitter disables it, which is only useful for
demonstrating the artifact.

Run from the operator laptop for an end-to-end figure including Wi-Fi, or on
the Pi for the robot-internal figure.

    ./wslatency.py --host 127.0.0.1 --key "$CONTROLLER_KEY" --probe all
    ./wslatency.py --host 192.168.0.9 --key "$CONTROLLER_KEY" --probe pan --trials 30 --label wifi-10m
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]

COLUMNS = ("iso_ts", "probe", "metric", "trial", "label", "value_ms",
           "resolution_ms", "ok", "detail")

TELEMETRY_PERIOD_MS = 200
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
           value_ms: float | None, detail: str = "") -> None:
    append_row(out, COLUMNS, {
        "iso_ts": now_iso(), "probe": probe, "metric": metric, "trial": trial,
        "label": label, "value_ms": round(value_ms, 1) if value_ms is not None else "",
        "resolution_ms": TELEMETRY_PERIOD_MS, "ok": int(value_ms is not None),
        "detail": detail,
    })


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
                   f"role={ack.get('role')} auth={ack.get('auth')}")
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


async def probe_deadman(link: Link, args: argparse.Namespace) -> None:
    """Drive, then go silent. Expect a trip at protocol.DEADMAN_MS (2000 ms).

    The firmware timer is what is measured here; that the wheels physically
    stop is test H7, recorded with record.py deadman_physical.
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
        last_command = await link.jittered_send(
            {"type": "motor", "dir": "F", "speed": args.speed})
        frame, arrived = await link.await_frame(
            lambda f: f.get("fw_state") == FW_STOPPED, timeout=10.0)
        elapsed = (arrived - last_command) * 1000 if frame else None
        link.beating = True
        record(args.out, "deadman", "deadman_trip", trial, args.label, elapsed,
               f"expected ~2000 ms, speed={args.speed}")
        print(f"  deadman {trial}: {f'{elapsed:.0f} ms' if elapsed else 'NO TRIP (FAIL)'}")
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
                    await probe_deadman(link, args)
            await link.settle_ready()
        finally:
            await link.stop()

    print(f"\nwritten to {args.out}")
    print(f"NOTE: {TELEMETRY_PERIOD_MS} ms telemetry quantisation -- these are upper bounds.")
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
    args = parser.parse_args()
    if args.probe in ("all", "motor", "deadman"):
        print("WARNING: the motor and dead-man probes make the robot DRIVE. "
              "Put it on blocks or in clear space.")
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
