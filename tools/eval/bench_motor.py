#!/usr/bin/env python3
"""Elevated-wheel motor bench test: software-timed command/response logging
over the real control WebSocket, with NO floor-distance measurement.

This is NOT the E3 stopping-distance protocol (see estop_assist.py /
Table 5.4). It exists for a bench condition where the robot is securely
elevated and all wheels are clear of any surface, so the robot cannot
travel. It drives each wheel pair for a software-timed window, sends the
real stop_all (same message the dashboard EMERGENCY STOP button sends),
and logs:

  - the software clock timestamps of the drive command and the stop command
    (cmd_send_ts, stop_send_ts) -- these ARE accurately measured, because
    they are this process's own clock marking its own socket.send() calls;
  - the firmware's self-reported ARMED/DRIVING/STOPPED state as seen in
    telemetry broadcasts, with THIS process's receipt timestamps attached.

These telemetry-derived timestamps are the firmware's own account of its
state, taken by this process at message-receipt time. They are NOT an
independently instrumented measurement of when the wheels physically
started or stopped turning -- this build has no tachometer or encoder.
Do not report cmd_to_driving_s / stop_to_stopped_s as a measured physical
response time, and do not merge any row from bench_motor.csv into Table 5.4
or otherwise present it as a floor stopping-distance result.

Safety:
  - Every run (dry or live) sends the real hello handshake and claims the
    controller role; a live run requires BOTH --confirm WHEELS_OFF_GROUND
    on the command line AND a typed confirmation at the prompt before any
    motor command is sent. --dry-run never sends a motor command at all
    (hello + heartbeat + telemetry capture only), so it is safe to run with
    wheels on the ground.
  - Per-trial duration is hard-capped at --max-trial-s regardless of what
    was requested; total session time is hard-capped at --max-total-s.
  - A stop_all is sent on normal completion, on any exception, on Ctrl-C/
    SIGTERM, and on the per-trial timeout. The dead-man timer and firmware
    PANIC/ESTOP latch are untouched -- this script only ever sends the same
    motor/heartbeat/stop_all messages the dashboard sends.
  - This never touches estop.csv. Results go to results/bench_motor.csv,
    plus one newline-delimited JSON event log per session under
    results/bench_motor_events/ with every sent and received message.

    ROBOT_KEY=... ./bench_motor.py --dry-run
    ROBOT_KEY=... ./bench_motor.py --confirm WHEELS_OFF_GROUND \\
        --trials F:60:1.0,R:60:1.0,L:60:1.0,G:60:1.0

CAVEAT, 2026-10-22: the --confirm flag and the prompt below only record that
someone *said* the wheels were clear; they do not verify it. The first 60
rows in results/bench_motor.csv were logged on exactly that unverified
premise, and the robot was in fact on the floor for all of them (see
README.md "Data caveat, 2026-10-22"). Look at the wheels yourself before
answering YES.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, AsyncIterator

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]

CONFIRM_TOKEN = "WHEELS_OFF_GROUND"

# Mirrors pi/common/protocol.py MIN_PWM/MAX_PWM; the server clamps and warns
# independently (pi/p1_control/safety.py), this is just a client-side sanity
# check so an out-of-range value doesn't silently get clamped unnoticed.
MIN_PWM, MAX_PWM = 0, 180
VALID_DIRECTIONS = ("F", "R", "L", "G")  # forward/reverse/left/right opcodes

# Firmware states as sent in telemetry's fw_state field (common/protocol.py).
# Per arduino/telemetry.cpp:telemetryFwState(), STOPPED(3) is only reported
# for BOOT/ESTOP/PANIC. An ordinary stop_all from driving (MODE_ACTIVE) moves
# the firmware to MODE_READY, which reports ARMED(1) -- that is the signal to
# watch for after a routine stop, not STOPPED.
FW_STATE_NAMES = {1: "ARMED", 2: "DRIVING", 3: "STOPPED"}
FW_STATE_DRIVING, FW_STATE_READY_AFTER_STOP = 2, 1

BENCH_CSV = RESULTS_DIR / "bench_motor.csv"
EVENTS_DIR = RESULTS_DIR / "bench_motor_events"

CSV_COLUMNS = (
    "iso_ts", "test_id", "mode", "direction", "pwm",
    "requested_duration_s", "applied_duration_s",
    "cmd_send_ts", "stop_send_ts", "software_drive_window_s",
    "fw_state_before", "fw_state_driving_first_ts", "fw_state_ready_after_stop_first_ts",
    "cmd_to_driving_s_firmware_reported", "stop_to_ready_s_firmware_reported",
    "range_cm_before", "range_cm_after", "events_file", "notes",
)


class Trial:
    def __init__(self, direction: str, pwm: int, duration_s: float) -> None:
        self.direction = direction
        self.pwm = pwm
        self.requested_duration_s = duration_s


def parse_trials(spec: str) -> list[Trial]:
    trials = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) != 3:
            raise ValueError(f"bad trial spec {chunk!r}; want DIR:PWM:SECONDS")
        direction, pwm_s, dur_s = parts
        direction = direction.strip().upper()
        if direction not in VALID_DIRECTIONS:
            raise ValueError(f"bad direction {direction!r} in {chunk!r}; want one of {VALID_DIRECTIONS}")
        pwm = int(pwm_s)
        if not (MIN_PWM <= pwm <= MAX_PWM):
            raise ValueError(f"pwm {pwm} out of range [{MIN_PWM},{MAX_PWM}] in {chunk!r}")
        trials.append(Trial(direction, pwm, float(dur_s)))
    if not trials:
        raise ValueError("empty --trials")
    return trials


class EventLog:
    """One JSON object per line: every message this process sends/receives."""

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
    """Tracks the most recent telemetry frame and the first-seen time of
    each fw_state since the watcher was told to watch for it."""

    def __init__(self, events: EventLog) -> None:
        self.events = events
        self.latest: dict[str, Any] = {}
        self._watch_for: int | None = None
        self._first_seen: str | None = None
        self._since_monotonic: float = 0.0

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

    def range_cm(self) -> Any:
        return self.latest.get("range_cm")


def next_test_id(path: Path) -> int:
    if not path.exists():
        return 1
    highest = 0
    with path.open() as handle:
        for row in csv.DictReader(handle):
            try:
                highest = max(highest, int(row.get("test_id", 0)))
            except (TypeError, ValueError):
                continue
    return highest + 1


async def run_dry(host: str, port: int, key: str, events_path: Path) -> int:
    """Connect, claim controller, capture telemetry -- send no motor command."""
    url = f"ws://{host}:{port}/control/ws"
    events = EventLog(events_path)
    seq = 0

    def nxt(msg: dict) -> str:
        nonlocal seq
        seq += 1
        full = {**msg, "seq": seq}
        events.write("send", full)
        return json.dumps(full)

    try:
        async with connect(url, open_timeout=10) as socket:
            await socket.send(nxt({"type": "hello", "role": "controller", "key": key}))
            ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
            events.write("recv", ack)
            if ack.get("role") != "controller":
                print(f"refused: role={ack.get('role')} auth={ack.get('auth')} "
                      "(close the dashboard controller session first)", file=sys.stderr)
                return 2
            print(f"dry-run: controller session claimed (session={ack.get('session')}); "
                  "capturing telemetry for 3s, no motor command will be sent")
            watcher = TelemetryWatcher(events)
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                try:
                    raw = await asyncio.wait_for(socket.recv(), timeout=0.5)
                    watcher.on_message(json.loads(raw))
                except asyncio.TimeoutError:
                    pass
            print(f"dry-run: latest fw_state={FW_STATE_NAMES.get(watcher.fw_state(), watcher.fw_state())} "
                  f"range_cm={watcher.range_cm()}")
            await socket.send(nxt({"type": "stop_all"}))
            print("dry-run: stop_all sent (belt-and-suspenders; no motor command was ever sent). Done.")
    finally:
        events.close()
    return 0


async def run_live(host: str, port: int, key: str, trials: list[Trial],
                   max_trial_s: float, max_total_s: float,
                   events_path: Path) -> AsyncIterator[dict[str, Any]]:
    url = f"ws://{host}:{port}/control/ws"
    events = EventLog(events_path)
    seq = 0

    def nxt(msg: dict) -> dict:
        nonlocal seq
        seq += 1
        full = {**msg, "seq": seq}
        events.write("send", full)
        return full

    session_start = time.monotonic()
    rows_written = 0

    async with connect(url, open_timeout=10) as socket:
        await socket.send(json.dumps(nxt({"type": "hello", "role": "controller", "key": key})))
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
        events.write("recv", ack)
        if ack.get("role") != "controller":
            print(f"refused: role={ack.get('role')} auth={ack.get('auth')} "
                  "(close the dashboard controller session first)", file=sys.stderr)
            events.close()
            raise RuntimeError("controller role refused")
        print(f"live bench session up (session={ack.get('session')}): "
              f"{len(trials)} trial(s) queued, max {max_trial_s:.1f}s/trial, "
              f"{max_total_s:.0f}s total cap")

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
            for i, trial in enumerate(trials, start=1):
                if stop_requested.is_set():
                    print("stop requested; ending session early")
                    break
                if time.monotonic() - session_start >= max_total_s:
                    print(f"max-total-s ({max_total_s:.0f}s) reached; "
                          f"stopping before trial {i}/{len(trials)}")
                    break

                applied_duration = min(trial.requested_duration_s, max_trial_s)
                if applied_duration != trial.requested_duration_s:
                    print(f"  trial {i}: duration clamped {trial.requested_duration_s:g}s "
                          f"-> {applied_duration:g}s (--max-trial-s)")

                fw_state_before = watcher.fw_state()
                print(f"\nTrial {i}/{len(trials)}: dir={trial.direction} pwm={trial.pwm} "
                      f"duration={applied_duration:g}s "
                      f"(fw_state before: {FW_STATE_NAMES.get(fw_state_before, fw_state_before)})")

                watcher.watch_for(FW_STATE_DRIVING)
                range_before = watcher.range_cm()
                cmd_send_ts = now_iso()
                drive_deadline = loop.time() + applied_duration
                refresh_s = 0.3  # well inside the 2000ms dead-man window
                try:
                    while loop.time() < drive_deadline and not stop_requested.is_set():
                        await socket.send(json.dumps(nxt({
                            "type": "motor", "dir": trial.direction, "speed": trial.pwm,
                        })))
                        await _sleep_or_stop(refresh_s, stop_requested)
                finally:
                    stop_send_ts = await send_stop()

                driving_first_ts = watcher.first_seen()
                watcher.watch_for(FW_STATE_READY_AFTER_STOP)
                # Give telemetry (200ms cadence) a brief window to report ARMED.
                settle_deadline = loop.time() + 1.5
                while loop.time() < settle_deadline and watcher.first_seen() is None:
                    await asyncio.sleep(0.05)
                ready_after_stop_ts = watcher.first_seen()
                range_after = watcher.range_cm()

                notes = []
                if driving_first_ts is None:
                    notes.append("no DRIVING fw_state observed in telemetry during drive window")
                if ready_after_stop_ts is None:
                    notes.append("no ARMED fw_state observed in telemetry within 1.5s of stop_all "
                                 "(expected after an ordinary stop; STOPPED(3) is BOOT/ESTOP/PANIC-only)")

                row = {
                    "iso_ts": now_iso(),
                    "test_id": "",  # filled by caller after this returns
                    "mode": "live",
                    "direction": trial.direction,
                    "pwm": trial.pwm,
                    "requested_duration_s": f"{trial.requested_duration_s:g}",
                    "applied_duration_s": f"{applied_duration:g}",
                    "cmd_send_ts": cmd_send_ts,
                    "stop_send_ts": stop_send_ts,
                    "software_drive_window_s": round(
                        _iso_diff_s(stop_send_ts, cmd_send_ts), 3),
                    "fw_state_before": FW_STATE_NAMES.get(fw_state_before, fw_state_before),
                    "fw_state_driving_first_ts": driving_first_ts or "",
                    "fw_state_ready_after_stop_first_ts": ready_after_stop_ts or "",
                    "cmd_to_driving_s_firmware_reported": (
                        round(_iso_diff_s(driving_first_ts, cmd_send_ts), 3)
                        if driving_first_ts else ""),
                    "stop_to_ready_s_firmware_reported": (
                        round(_iso_diff_s(ready_after_stop_ts, stop_send_ts), 3)
                        if ready_after_stop_ts else ""),
                    "range_cm_before": range_before if range_before is not None else "",
                    "range_cm_after": range_after if range_after is not None else "",
                    "events_file": str(events_path.relative_to(RESULTS_DIR)),
                    "notes": "; ".join(notes),
                }
                yield row
                rows_written += 1
                print(f"  logged: driving_first_ts={driving_first_ts} "
                      f"ready_after_stop_ts={ready_after_stop_ts} notes={row['notes'] or '(none)'}")
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
    print(f"\nbench session done: {rows_written} trial(s) logged")


async def _sleep_or_stop(seconds: float, stop_event: asyncio.Event) -> None:
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass


def _iso_diff_s(later: str, earlier: str) -> float:
    from datetime import datetime
    return (datetime.fromisoformat(later) - datetime.fromisoformat(earlier)).total_seconds()


async def main_async(args: argparse.Namespace) -> int:
    key = os.environ.get("ROBOT_KEY", "")
    if not key:
        print("ROBOT_KEY not set", file=sys.stderr)
        return 2

    session_tag = now_iso().replace(":", "").replace(".", "")
    events_path = EVENTS_DIR / f"{session_tag}.jsonl"

    if args.dry_run:
        return await run_dry(args.host, args.port, key, events_path)

    if args.confirm != CONFIRM_TOKEN:
        print(f"--confirm {CONFIRM_TOKEN} is required for a live run (not --dry-run).\n"
              "This is a safety gate: it must only be passed after visually confirming\n"
              "every wheel is clear of any surface on a secure elevated support.",
              file=sys.stderr)
        return 2

    try:
        trials = parse_trials(args.trials)
    except ValueError as exc:
        print(f"bad --trials: {exc}", file=sys.stderr)
        return 2

    print("LIVE BENCH RUN -- wheels will spin.")
    print(f"  trials: {[(t.direction, t.pwm, t.requested_duration_s) for t in trials]}")
    reply = input(
        "Type YES to confirm: robot is securely elevated, every wheel is clear of\n"
        "any surface, and the dashboard/physical e-stop is reachable right now: "
    ).strip()
    if reply != "YES":
        print("not confirmed; aborting without sending any motor command", file=sys.stderr)
        return 2

    test_id = next_test_id(BENCH_CSV)
    try:
        async for row in run_live(args.host, args.port, key, trials,
                                  args.max_trial_s, args.max_total_s, events_path):
            row["test_id"] = test_id
            append_row(BENCH_CSV, CSV_COLUMNS, row)
            test_id += 1
    except RuntimeError as exc:
        print(f"live run aborted: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--dry-run", action="store_true",
                        help="connect + capture telemetry only; never sends a motor command")
    parser.add_argument("--confirm", default="",
                        help=f"must equal {CONFIRM_TOKEN!r} to run live trials")
    parser.add_argument("--trials", default="F:60:1.0,R:60:1.0,L:60:1.0,G:60:1.0",
                        help="comma-separated DIR:PWM:SECONDS, e.g. F:60:1.0,F:120:1.0")
    parser.add_argument("--max-trial-s", type=float, default=3.0,
                        help="hard per-trial cap regardless of requested duration (default 3.0)")
    parser.add_argument("--max-total-s", type=float, default=90.0,
                        help="hard cap on total session time (default 90.0)")
    args = parser.parse_args()
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
