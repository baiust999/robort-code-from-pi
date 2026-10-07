#!/usr/bin/env python3
"""Typed entry of hand-measured results, for the figures no script can read.

Everything that needs a tape measure, a reference thermometer, a 240 fps
phone camera or a human participant is entered here instead of being typed
straight into a markdown table, so the raw trials survive as CSV and
summarize.py can aggregate them.

    ./record.py --list                      # all sheets
    ./record.py estop --fields              # one sheet's fields
    ./record.py estop speed_pwm=180 distance_cm=42 surface=concrete
    ./record.py latency_video fps=240 frames=19 label=wifi-5m
    ./record.py sus participant=P3 q1=4 q2=2 q3=5 q4=1 q5=4 q6=2 q7=5 q8=1 q9=4 q10=2 \
                task_time_s=96 completed=1 errors=0

Derived fields (latency_ms, error_cm, sus_score, ...) are computed, not typed.
`trial` / `run` / `participant` auto-increment when omitted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso, read_rows, to_float  # noqa: E402


def sus_score(row: dict) -> float | None:
    """Standard SUS: odd items score x-1, even items 5-x, sum x 2.5 -> 0-100."""
    answers = []
    for index in range(1, 11):
        value = to_float(row.get(f"q{index}"))
        if value is None or not 1 <= value <= 5:
            return None
        answers.append(value)
    total = sum(
        (value - 1) if index % 2 == 1 else (5 - value)
        for index, value in enumerate(answers, start=1)
    )
    return round(total * 2.5, 1)


def difference(minuend: str, subtrahend: str):
    def compute(row: dict) -> float | None:
        a, b = to_float(row.get(minuend)), to_float(row.get(subtrahend))
        return None if a is None or b is None else round(a - b, 3)
    return compute


SHEETS: dict[str, dict] = {
    "latency_video": {
        "file": "latency_video.csv",
        "about": "5.1 true control latency: 240 fps film of screen + wheels, frames counted",
        "index": "trial",
        "group": ("label",),
        "fields": {"label": "condition, e.g. wifi-5m", "fps": "camera frame rate (240)",
                   "frames": "frames from key press to first wheel movement",
                   "tester": "", "notes": ""},
        "required": ("fps", "frames"),
        "derived": {"latency_ms": lambda r: round(to_float(r["frames"]) / to_float(r["fps"]) * 1000, 1)},
    },
    "estop": {
        "file": "estop.csv",
        "about": "5.1 emergency-stop stopping distance (test I6), tape measured",
        "index": "trial",
        "group": ("speed_pwm", "surface"),
        "fields": {"speed_pwm": "60 / 120 / 180", "surface": "concrete / tile / grass",
                   "distance_cm": "travel after the stop click",
                   "stop_time_s": "optional, from video", "tester": "", "notes": ""},
        "required": ("speed_pwm", "distance_cm"),
        "derived": {},
    },
    "deadman_physical": {
        "file": "deadman_physical.csv",
        "about": "5.1 dead-man wheel-stop time (test H7), filmed",
        "index": "trial",
        "group": ("speed_pwm",),
        "fields": {"speed_pwm": "", "stop_s": "silence to wheels stationary (expect ~2.0)",
                   "panic_seen": "1 if PANIC DEADMAN appeared", "tester": "", "notes": ""},
        "required": ("stop_s",),
        "derived": {},
    },
    "glass2glass": {
        "file": "glass2glass.csv",
        "about": "5.2 video delay (test N7): photograph a stopwatch and its robot-view copy",
        "index": "trial",
        "group": ("label",),
        "fields": {"label": "viewers-1 / viewers-2 / wifi-20m",
                   "real_ms": "stopwatch reading in milliseconds",
                   "robot_ms": "reading shown in the video panel", "tester": "", "notes": ""},
        "required": ("real_ms", "robot_ms"),
        "derived": {"delay_ms": difference("real_ms", "robot_ms")},
    },
    "ultrasonic": {
        "file": "ultrasonic.csv",
        "about": "5.6 ultrasonic accuracy (test H11): 10 readings at each known distance",
        "index": "trial",
        "group": ("true_cm",),
        "fields": {"true_cm": "tape-measured distance", "reading_cm": "telemetry value",
                   "tester": "", "notes": ""},
        "required": ("true_cm", "reading_cm"),
        "derived": {"error_cm": difference("reading_cm", "true_cm")},
    },
    "thermal": {
        "file": "thermal.csv",
        "about": "5.6 DHT vs reference thermometer/hygrometer (test H12)",
        "index": "trial",
        "group": (),
        "fields": {"ref_c": "", "sensor_c": "", "ref_rh": "", "sensor_rh": "",
                   "tester": "", "notes": ""},
        "required": ("ref_c", "sensor_c"),
        "derived": {"error_c": difference("sensor_c", "ref_c"),
                    "error_rh": difference("sensor_rh", "ref_rh")},
    },
    "gas": {
        "file": "gas.csv",
        "about": "5.6 gas sensor response (test H13). Raw ADC counts, not ppm: "
                 "the MQ-136 has no calibration curve in this build",
        "index": "trial",
        "group": ("source",),
        "fields": {"source": "e.g. unlit-lighter-20cm", "baseline_adc": "",
                   "peak_adc": "", "trip_s": "seconds to cross the warn threshold",
                   "card_colour": "amber / red / none", "tester": "", "notes": ""},
        "required": ("baseline_adc", "peak_adc"),
        "derived": {"rise_adc": difference("peak_adc", "baseline_adc")},
    },
    "field": {
        "file": "field.csv",
        "about": "5.7 end-to-end rescue runs (Section 8). Do 5-10, not 1",
        "index": "run",
        "group": ("course",),
        "fields": {"course": "course name/description", "course_m": "length in metres",
                   "time_to_victim_s": "", "time_total_s": "", "collisions": "",
                   "unplanned_stops": "", "victim_heard_operator": "1/0",
                   "victim_saw_operator": "1/0", "operator_heard_victim": "1/0",
                   "operator_saw_victim": "1/0", "result": "PASS / FAIL",
                   "operator": "", "notes": ""},
        "required": ("time_to_victim_s", "collisions", "unplanned_stops", "result"),
        "derived": {},
    },
    "sus": {
        "file": "sus.csv",
        "about": "5.8 usability: one row per participant, 10 SUS items on 1-5 plus task metrics",
        "index": "participant",
        "group": (),
        "fields": {**{f"q{i}": f"SUS item {i}, 1-5" for i in range(1, 11)},
                   "task_time_s": "time to complete the standard course",
                   "completed": "1/0", "errors": "wrong-command or collision count",
                   "prior_experience": "none / some / expert", "notes": ""},
        "required": tuple(f"q{i}" for i in range(1, 11)),
        "derived": {"sus_score": sus_score},
    },
    "checklist": {
        "file": "checklist.csv",
        "about": "pass/fail rows for TEST_REPORT sections 4 and 5 (H1-H15, I1-I19)",
        "index": None,
        "group": (),
        "fields": {"test_id": "e.g. H2 or I8b", "result": "PASS / FAIL",
                   "measured": "measured value, if the row has one",
                   "tester": "", "notes": ""},
        "required": ("test_id", "result"),
        "derived": {},
    },
}


def next_index(sheet: dict, path: Path, row: dict) -> int:
    """Next value of the sheet's index column within the same group."""
    rows = read_rows(path)
    name = sheet["index"]
    highest = 0
    for existing in rows:
        if any(existing.get(key, "") != str(row.get(key, "")) for key in sheet["group"]):
            continue
        value = to_float(existing.get(name))
        if value is not None:
            highest = max(highest, int(value))
    return highest + 1


def columns_for(name: str, sheet: dict) -> tuple[str, ...]:
    index = (sheet["index"],) if sheet["index"] else ()
    return ("iso_ts", *index, *sheet["fields"], *sheet["derived"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", nargs="?", help="which measurement sheet")
    parser.add_argument("pairs", nargs="*", help="field=value ...")
    parser.add_argument("--list", action="store_true", help="list the sheets")
    parser.add_argument("--fields", action="store_true", help="list one sheet's fields")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    if args.list or not args.sheet:
        print("sheets:\n")
        for name, sheet in SHEETS.items():
            print(f"  {name:18s} {sheet['about']}")
        print("\n  ./record.py <sheet> --fields   for a sheet's fields")
        return 0

    if args.sheet not in SHEETS:
        print(f"unknown sheet {args.sheet!r}; --list to see them", file=sys.stderr)
        return 2
    sheet = SHEETS[args.sheet]
    path = args.results_dir / sheet["file"]

    if args.fields:
        print(f"{args.sheet}: {sheet['about']}\n")
        if sheet["index"]:
            print(f"  {sheet['index']:24s} auto-increments if omitted")
        for field, help_text in sheet["fields"].items():
            mark = "*" if field in sheet["required"] else " "
            print(f" {mark}{field:24s} {help_text}")
        for field in sheet["derived"]:
            print(f"  {field:24s} (computed)")
        print("\n  * required")
        return 0

    row: dict[str, object] = {}
    for pair in args.pairs:
        if "=" not in pair:
            print(f"expected field=value, got {pair!r}", file=sys.stderr)
            return 2
        key, _, value = pair.partition("=")
        if key not in sheet["fields"] and key != sheet["index"]:
            print(f"{args.sheet} has no field {key!r}; --fields to see them", file=sys.stderr)
            return 2
        row[key] = value

    missing = [field for field in sheet["required"] if not str(row.get(field, "")).strip()]
    if missing:
        print(f"missing required: {', '.join(missing)}", file=sys.stderr)
        return 2

    if sheet["index"] and not row.get(sheet["index"]):
        row[sheet["index"]] = next_index(sheet, path, row)

    for name, compute in sheet["derived"].items():
        try:
            row[name] = compute(row)
        except (TypeError, ValueError, KeyError):
            row[name] = ""

    row["iso_ts"] = now_iso()
    append_row(path, columns_for(args.sheet, sheet), row)

    index_note = f"{sheet['index']}={row[sheet['index']]} " if sheet["index"] else ""
    derived = " ".join(f"{k}={row[k]}" for k in sheet["derived"] if row.get(k) not in (None, ""))
    print(f"{args.sheet}: {index_note}{derived}  -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
