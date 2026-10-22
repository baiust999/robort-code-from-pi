#!/usr/bin/env python3
"""Automated E3 command/firmware-timing logger -- NOT a stopping-distance
measurement, and NOT a substitute for estop_assist.py / Table 5.4.

estop_assist.py's real protocol needs a human to press Enter the instant a
mark crosses a line and read a tape measure afterward -- that is what makes
the recorded distance_cm a measurement of the robot's actual stopping
distance. Neither of those two actions can be automated without fabricating
a number: this process has no camera or sensor that sees where the robot
stopped.

What CAN be automated, and is all this script does: drive forward on the
real control WebSocket for a fixed software-timed duration, send the real
stop_all (same message the dashboard EMERGENCY STOP button sends), and log
the software clock's command/stop timestamps plus the firmware's own
telemetry-reported ARMED/DRIVING state transitions. Every row's distance_cm
is written as the literal string PENDING_MEASUREMENT -- never a guess, never
an ultrasonic/telemetry substitute. If you want real E3 data for a row, tape
-measure that trial while it happens and record it with record.py:

    ./record.py estop speed_pwm=60 distance_cm=42 surface=concrete tester=SA

THE ROBOT IS ON THE FLOOR AND WILL ACTUALLY DRIVE FORWARD. This is not an
elevated bench test (see bench_motor.py and its 2026-10-22 floor-contact
caveat in README.md for why that distinction is being made explicitly).
Clear a straight path of at least a few metres before running this, and run
small batches -- a few trials at a time -- checking the robot is still
inside the clear area before the next batch, since nothing here verifies
that automatically.

Safety, same pattern as estop_assist.py / bench_motor.py / drive_load.py:
  - --confirm FLOOR_CLEAR_SUPERVISED is required, plus a typed YES at a
    runtime prompt, before any motor command is sent.
  - Per-trial drive duration is hard-capped at --max-drive-s; total session
    time at --max-total-s.
  - stop_all is sent on normal completion, on any exception, on Ctrl-C/
    SIGTERM, and after every trial regardless of outcome.
  - The dead-man timer and firmware PANIC/ESTOP latch are untouched.
  - Writes to results/estop_auto.csv, never to estop.csv. The 23 original
    estop.csv rows and the manual estop_assist.py workflow are both
    unaffected by this script's existence.

    ROBOT_KEY=... ./estop_auto.py --confirm FLOOR_CLEAR_SUPERVISED \\
        --speed 60 --trials 5 --drive-s 1.0 --tester SA --surface concrete
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]

CONFIRM_TOKEN = "FLOOR_CLEAR_SUPERVISED"
PENDING = "PENDING_MEASUREMENT"

# arduino/telemetry.cpp:telemetryFwState() -- ACTIVE->DRIVING(2), READY after
# an ordinary stop->ARMED(1). STOPPED(3) is BOOT/ESTOP/PANIC only (see
# tools/eval/README.md "Known starting points").
FW_STATE_NAMES = {1: "ARMED", 2: "DRIVING", 3: "STOPPED"}
FW_STATE_DRIVING, FW_STATE_READY_AFTER_STOP = 2, 1

OUT_CSV = RESULTS_DIR / "estop_auto.csv"
EVENTS_DIR = RESULTS_DIR / "estop_auto_events"

CSV_COLUMNS = (
    "iso_ts", "test_id", "pwm", "drive_duration_s",
    "cmd_send_ts", "stop_send_ts", "software_drive_window_s",
    "fw_state_before", "fw_state_driving_first_ts", "fw_state_ready_after_stop_first_ts",
    "cmd_to_driving_s_firmware_reported", "stop_to_ready_s_firmware_reported",
    "distance_cm", "surface", "tester", "events_file", "notes",
)


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a")

    def write(self, direction: str, payload: dict[str, Any]) -> None:
        record = {"recv_ts" if direction == "recv" else "send_ts": now_iso(),
                  "direction": direction, "payload": payload}
        self._handle.write(json.dumps(record) + "\n")
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


class TelemetryWatcher:
    def __init__(self, events: EventLog) -> None:
        self.events = events
        self.latest: dict[str, Any] = {}
        self._watch_for: int | None = None
        self._first_seen: str | None = None

    def on_message(self, payload: dict[str, Any]) -> None:
        if payload.get("type") != "telemetry":
            self.events.write("recv", payload)
            return
        self.latest = payload
        self.events.write("recv", {"type": "telemetry", "fw_state": payload.get("fw_state"),
                                    "range_cm": payload.get("range_cm"),
                                    "uptime_ms": payload.get("uptime_ms"),
                                    "seq": payload.get("seq")})
        if self._watch_for is not None and self._first_seen is None:
            if payload.get("fw_state") == self._watch_for:
                self._first_seen = now_iso()

    def watch_for(self, fw_state: int) -> None:
        self._watch_for = fw_state
        self._first_seen = None

    def first_seen(self) -> str | None:
        return self._first_seen

    def fw_state(self) -> int | None:
        return self.latest.get("fw_state")


def next_test_id(path: Path) -> int:
    if not path.exists():
        return 1
    import csv
    highest = 0
    with path.open() as handle:
        for row in csv.DictReader(handle):
            try:
                highest = max(highest, int(row.get("test_id", 0)))
            except (TypeError, ValueError):
                continue
    return highest + 1


def _iso_diff_s(later: str, earlier: str) -> float:
    from datetime import datetime
    return (datetime.fromisoformat(later) - datetime.fromisoformat(earlier)).total_seconds()


async def _sleep_or_stop(seconds: float, stop_event: asyncio.Event) -> None:
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass


async def run(args: argparse.Namespace):
    key = os.environ.get("ROBOT_KEY", "")
    if not key:
        print("ROBOT_KEY not set", file=sys.stderr)
        return 2

    if args.confirm != CONFIRM_TOKEN:
        print(f"--confirm {CONFIRM_TOKEN} is required. This is a safety gate: the robot is\n"
              "on the floor and WILL drive forward. Only pass it after clearing a straight\n"
              "path and being ready to physically intervene.", file=sys.stderr)
        return 2

    print(f"AUTOMATED FLOOR TEST -- robot WILL drive forward {args.trials} time(s), "
          f"PWM {args.speed}, {args.drive_s:g}s each.")
    print("distance_cm will be written as PENDING_MEASUREMENT for every row: this script "
          "does not and cannot measure physical stopping distance.")
    reply = input(
        "Type YES to confirm: the path ahead is clear for several metres, you are\n"
        "watching the robot right now, and the dashboard/physical e-stop is reachable: "
    ).strip()
    if reply != "YES":
        print("not confirmed; aborting without sending any motor command", file=sys.stderr)
        return 2

    url = f"ws://{args.host}:{args.port}/control/ws"
    session_tag = now_iso().replace(":", "").replace(".", "")
    events_path = EVENTS_DIR / f"{session_tag}.jsonl"
    events = EventLog(events_path)
    seq = 0

    def nxt(msg: dict) -> dict:
        nonlocal seq
        seq += 1
        full = {**msg, "seq": seq}
        events.write("send", full)
        return full

    test_id = next_test_id(OUT_CSV)
    rows_written = 0
    session_start = time.monotonic()

    async with connect(url, open_timeout=10) as socket:
        await socket.send(json.dumps(nxt({"type": "hello", "role": "controller", "key": key})))
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
        events.write("recv", ack)
        if ack.get("role") != "controller":
            print(f"refused: role={ack.get('role')} auth={ack.get('auth')} "
                  "(close the dashboard controller session first)", file=sys.stderr)
            events.close()
            return 2
        print(f"session up (session={ack.get('session')}): {args.trials} trial(s), "
              f"max {args.max_drive_s:g}s/trial, {args.max_total_s:g}s total cap")

        stop_requested = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_requested.set)
            except (NotImplementedError, RuntimeError):
                pass

        watcher = TelemetryWatcher(events)

        async def heartbeat() -> None:
            while not stop_requested.is_set():
                await socket.send(json.dumps(nxt({"type": "heartbeat"})))
                await asyncio.sleep(0.5)

        async def reader() -> None:
            try:
                async for raw in socket:
                    watcher.on_message(json.loads(raw))
            except Exception:  # noqa: BLE001
                pass

        heartbeat_task = asyncio.create_task(heartbeat())
        reader_task = asyncio.create_task(reader())

        async def send_stop() -> str:
            ts = now_iso()
            await socket.send(json.dumps(nxt({"type": "stop_all"})))
            return ts

        try:
            for i in range(1, args.trials + 1):
                if stop_requested.is_set():
                    print("stop requested; ending session early")
                    break
                if time.monotonic() - session_start >= args.max_total_s:
                    print(f"max-total-s ({args.max_total_s:g}s) reached; "
                          f"stopping before trial {i}/{args.trials}")
                    break

                drive_duration = min(args.drive_s, args.max_drive_s)
                fw_state_before = watcher.fw_state()
                print(f"\nTrial {i}/{args.trials}: F pwm={args.speed} duration={drive_duration:g}s "
                      f"(fw_state before: {FW_STATE_NAMES.get(fw_state_before, fw_state_before)})")

                watcher.watch_for(FW_STATE_DRIVING)
                cmd_send_ts = now_iso()
                drive_deadline = loop.time() + drive_duration
                refresh_s = 0.3  # well inside the 2000ms dead-man window
                try:
                    while loop.time() < drive_deadline and not stop_requested.is_set():
                        await socket.send(json.dumps(nxt({
                            "type": "motor", "dir": "F", "speed": args.speed,
                        })))
                        await _sleep_or_stop(refresh_s, stop_requested)
                finally:
                    stop_send_ts = await send_stop()

                driving_first_ts = watcher.first_seen()
                watcher.watch_for(FW_STATE_READY_AFTER_STOP)
                settle_deadline = loop.time() + 1.5
                while loop.time() < settle_deadline and watcher.first_seen() is None:
                    await asyncio.sleep(0.05)
                ready_after_stop_ts = watcher.first_seen()

                notes = []
                if driving_first_ts is None:
                    notes.append("no DRIVING fw_state observed in telemetry during drive window")
                if ready_after_stop_ts is None:
                    notes.append("no ARMED fw_state observed in telemetry within 1.5s of stop_all")

                row = {
                    "iso_ts": now_iso(),
                    "test_id": test_id,
                    "pwm": args.speed,
                    "drive_duration_s": f"{drive_duration:g}",
                    "cmd_send_ts": cmd_send_ts,
                    "stop_send_ts": stop_send_ts,
                    "software_drive_window_s": round(_iso_diff_s(stop_send_ts, cmd_send_ts), 3),
                    "fw_state_before": FW_STATE_NAMES.get(fw_state_before, fw_state_before),
                    "fw_state_driving_first_ts": driving_first_ts or "",
                    "fw_state_ready_after_stop_first_ts": ready_after_stop_ts or "",
                    "cmd_to_driving_s_firmware_reported": (
                        round(_iso_diff_s(driving_first_ts, cmd_send_ts), 3)
                        if driving_first_ts else ""),
                    "stop_to_ready_s_firmware_reported": (
                        round(_iso_diff_s(ready_after_stop_ts, stop_send_ts), 3)
                        if ready_after_stop_ts else ""),
                    "distance_cm": PENDING,
                    "surface": args.surface,
                    "tester": args.tester,
                    "events_file": str(events_path.relative_to(RESULTS_DIR)),
                    "notes": "; ".join(notes),
                }
                append_row(OUT_CSV, CSV_COLUMNS, row)
                rows_written += 1
                test_id += 1
                print(f"  logged test_id={row['test_id']}: driving_first_ts={driving_first_ts} "
                      f"ready_after_stop_ts={ready_after_stop_ts} "
                      f"distance_cm=PENDING_MEASUREMENT notes={row['notes'] or '(none)'}")
                # Settle pause between trials so the stop clearly completes
                # before the next drive command, independent of the dead-man window.
                await asyncio.sleep(0.5)
        finally:
            try:
                await asyncio.wait_for(send_stop(), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass
            heartbeat_task.cancel()
            reader_task.cancel()
            for task in (heartbeat_task, reader_task):
                try:
                    await task
                except (asyncio.CancelledError, Exception):  # noqa: BLE001
                    pass
            events.close()
    print(f"\ndone: {rows_written} trial(s) logged to {OUT_CSV}, all distance_cm=PENDING_MEASUREMENT")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--confirm", default="", help=f"must equal {CONFIRM_TOKEN!r}")
    parser.add_argument("--speed", type=int, required=True, choices=(60, 120, 180))
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--drive-s", type=float, default=1.0,
                        help="software-timed forward-drive duration before stop_all (default 1.0)")
    parser.add_argument("--max-drive-s", type=float, default=2.0,
                        help="hard per-trial cap regardless of --drive-s (default 2.0)")
    parser.add_argument("--max-total-s", type=float, default=60.0,
                        help="hard cap on total session time (default 60.0)")
    parser.add_argument("--surface", default="concrete")
    parser.add_argument("--tester", default="")
    args = parser.parse_args()
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
