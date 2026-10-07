#!/usr/bin/env python3
"""Fault injection and recovery timing for paper Section 5.4 (test IDs F1-F10).

Two modes.

`run` kills a supervised process and times the recovery automatically, proving
the restart happened by checking that the PID changed:

    ./faultinject.py run p1 --repeats 10
    ./faultinject.py run p2 --repeats 10
    ./faultinject.py run p3 --repeats 10
    ./faultinject.py run all --repeats 10

`watch` polls both /health endpoints at 10 Hz and records every state
transition with its timestamp, so a fault you have to inject by hand (unplug
the Arduino, unplug the camera, switch off the router) is timed by the harness
instead of by a stopwatch. Start it, inject the fault, restore it, Ctrl-C:

    ./faultinject.py watch --label F6-arduino-unplug

P3 holds a 10 s restart cooldown (protocol.RESTART_COOLDOWN_S) and polls health
every 10 s, so --settle must stay well above that or trial N+1 measures the
tail of trial N. The default is 30 s.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    P1_HEALTH,
    P2_HEALTH,
    RESULTS_DIR,
    append_row,
    http_json,
    now_iso,
    one_pid,
)

RUN_COLUMNS = (
    "iso_ts", "fault", "test_id", "trial", "down_detected_ms", "recovery_ms",
    "old_pid", "new_pid", "pid_changed", "ok", "notes",
)
WATCH_COLUMNS = (
    "iso_ts", "label", "t_s", "field", "from_value", "to_value", "held_s",
)

# Each target: what to kill, which health URL proves it is back, and the extra
# health fields that must be true before recovery counts as complete.
TARGETS = {
    "p1": {
        "test_id": "F3",
        "pattern": "p1_control.main",
        "health": P1_HEALTH,
        "require": {"serial_connected": True},
        "description": "P1 control server SIGKILL; P3 should respawn it",
    },
    "p2": {
        "test_id": "F4",
        "pattern": "p2_media.main",
        "health": P2_HEALTH,
        "require": {"camera_open": True},
        "description": "P2 media server SIGKILL; P3 should respawn it and the camera reopen",
    },
    "p3": {
        "test_id": "F5",
        "pattern": "p3_watchdog.main",
        # The unit is KillMode=control-group, so killing P3 takes P1 and P2
        # down with it. Recovery therefore means the whole stack is back, not
        # just that the watchdog PID exists again.
        "health": P1_HEALTH,
        "require": {"serial_connected": True},
        "extra": [(P2_HEALTH, {"camera_open": True})],
        "description": "P3 watchdog SIGKILL; systemd restarts the unit and P3 respawns P1/P2",
    },
}

WATCH_FIELDS = (
    ("p1_up", "p1"), ("serial_connected", "p1"), ("gps_fix", "p1"), ("ws_clients", "p1"),
    ("p2_up", "p2"), ("camera_open", "p2"), ("active_streams", "p2"),
)


def healthy(target: dict) -> tuple[bool, int | None]:
    """(is recovered, current pid). Needs the process alive, its /health
    answering, and every `require` field satisfied."""
    pid = one_pid(target["pattern"])
    if pid is None:
        return False, None
    url = target["health"]
    if url is None:
        return True, pid
    data = http_json(url, timeout=1.0)
    if data is None:
        return False, pid
    for key, expected in target["require"].items():
        if bool(data.get(key)) is not bool(expected):
            return False, pid
    for url, require in target.get("extra", ()):
        extra = http_json(url, timeout=1.0)
        if extra is None:
            return False, pid
        for key, expected in require.items():
            if bool(extra.get(key)) is not bool(expected):
                return False, pid
    return True, pid


def inject(name: str, target: dict, trial: int, timeout: float, out: Path) -> bool:
    ready, old_pid = healthy(target)
    if not ready:
        print(f"  trial {trial}: system not healthy before injection, skipping")
        append_row(out, RUN_COLUMNS, {
            "iso_ts": now_iso(), "fault": name, "test_id": target["test_id"],
            "trial": trial, "ok": 0, "notes": "not healthy before injection",
        })
        return False

    t0 = time.monotonic()
    subprocess.run(["pkill", "-9", "-f", target["pattern"]], check=False)

    down_ms: float | None = None
    recovery_ms: float | None = None
    new_pid: int | None = None
    while time.monotonic() - t0 < timeout:
        ready, pid = healthy(target)
        if down_ms is None and not ready:
            down_ms = (time.monotonic() - t0) * 1000
        # A restart only counts once the PID differs: a /health that answers
        # before the old process has died would otherwise read as "never down".
        if down_ms is not None and ready and pid is not None and pid != old_pid:
            recovery_ms = (time.monotonic() - t0) * 1000
            new_pid = pid
            break
        time.sleep(0.05)

    ok = recovery_ms is not None
    append_row(out, RUN_COLUMNS, {
        "iso_ts": now_iso(), "fault": name, "test_id": target["test_id"], "trial": trial,
        "down_detected_ms": round(down_ms, 1) if down_ms is not None else "",
        "recovery_ms": round(recovery_ms, 1) if recovery_ms is not None else "",
        "old_pid": old_pid, "new_pid": new_pid if new_pid else "",
        "pid_changed": int(bool(new_pid and new_pid != old_pid)), "ok": int(ok),
        "notes": "" if ok else f"no recovery within {timeout:.0f}s",
    })
    if ok:
        print(f"  trial {trial}: recovered in {recovery_ms / 1000:.2f}s (pid {old_pid} -> {new_pid})")
    else:
        print(f"  trial {trial}: FAILED to recover within {timeout:.0f}s")
    return ok


def cmd_run(args: argparse.Namespace) -> int:
    names = list(TARGETS) if args.target == "all" else [args.target]
    for name in names:
        target = TARGETS[name]
        print(f"\n{target['test_id']} {name}: {target['description']}")
        passed = 0
        for trial in range(1, args.repeats + 1):
            if inject(name, target, trial, args.timeout, args.out):
                passed += 1
            if trial < args.repeats:
                time.sleep(args.settle)
        print(f"{target['test_id']} {name}: {passed}/{args.repeats} recovered")
    print(f"\nwritten to {args.out}")
    return 0


def snapshot() -> dict[str, object]:
    p1 = http_json(P1_HEALTH, timeout=1.0)
    p2 = http_json(P2_HEALTH, timeout=1.0)
    state: dict[str, object] = {"p1_up": int(p1 is not None), "p2_up": int(p2 is not None)}
    state["serial_connected"] = int(bool(p1.get("serial_connected"))) if p1 else ""
    state["gps_fix"] = int(bool(p1.get("gps_fix"))) if p1 else ""
    state["ws_clients"] = p1.get("ws_clients") if p1 else ""
    state["camera_open"] = int(bool(p2.get("camera_open"))) if p2 else ""
    state["active_streams"] = p2.get("active_streams") if p2 else ""
    return state


def cmd_watch(args: argparse.Namespace) -> int:
    print(f"watching health at 10 Hz, label '{args.label}'.")
    print("inject the fault now, restore it, then press Ctrl-C.\n")
    start = time.monotonic()
    state = snapshot()
    since = {field: start for field, _ in WATCH_FIELDS}
    transitions = 0
    for field, _ in WATCH_FIELDS:
        print(f"  start: {field}={state.get(field)}")
    try:
        while True:
            time.sleep(0.1)
            current = snapshot()
            when = time.monotonic()
            for field, _ in WATCH_FIELDS:
                if current.get(field) != state.get(field):
                    held = when - since[field]
                    append_row(args.out, WATCH_COLUMNS, {
                        "iso_ts": now_iso(), "label": args.label,
                        "t_s": round(when - start, 2), "field": field,
                        "from_value": state.get(field), "to_value": current.get(field),
                        "held_s": round(held, 2),
                    })
                    print(f"  {when - start:7.2f}s  {field}: {state.get(field)} -> "
                          f"{current.get(field)}  (held {held:.2f}s)")
                    state[field] = current.get(field)
                    since[field] = when
                    transitions += 1
    except KeyboardInterrupt:
        print(f"\n{transitions} transitions written to {args.out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="kill a process and time the automatic recovery")
    run.add_argument("target", choices=[*TARGETS, "all"])
    run.add_argument("--repeats", type=int, default=10)
    run.add_argument("--settle", type=float, default=30.0, help="seconds between trials (>= 20)")
    run.add_argument("--timeout", type=float, default=90.0, help="give up on recovery after this")
    run.add_argument("--out", type=Path, default=RESULTS_DIR / "faults.csv")
    run.set_defaults(func=cmd_run)

    watch = sub.add_parser("watch", help="log health transitions while you inject a fault by hand")
    watch.add_argument("--label", required=True, help="e.g. F6-arduino-unplug")
    watch.add_argument("--out", type=Path, default=RESULTS_DIR / "fault_watch.csv")
    watch.set_defaults(func=cmd_watch)

    args = parser.parse_args()
    if args.command == "run" and args.settle < 20:
        print("refusing: --settle below 20s collides with P3's 10s restart cooldown", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
