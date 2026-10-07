#!/usr/bin/env python3
"""Turn the raw result CSVs into paper-ready markdown tables.

Reads whatever exists in tools/eval/results/ and prints one section per paper
subsection, each as n / mean / SD / min / max / median / p95 -- the set a
reviewer expects to see instead of a single number. Sheets with no data yet
are listed as outstanding, so this doubles as a progress check.

    ./summarize.py                        # to the terminal
    ./summarize.py --out results/summary.md
    ./summarize.py --only 5.4

SD is the sample standard deviation; a single trial shows a blank SD rather
than 0. Nothing here invents a value: an empty sheet stays empty.
"""

from __future__ import annotations

import argparse
import io
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, describe, read_rows, to_float  # noqa: E402

STATS = ("n", "mean", "sd", "min", "max", "median", "p95")

REPORTS: tuple[dict, ...] = (
    {
        "section": "5.1", "file": "latency_video.csv",
        "title": "Control latency, 240 fps video (key press -> wheel motion)",
        "kind": "agg", "group": ["label"], "metrics": [("latency_ms", "latency (ms)")],
    },
    {
        "section": "5.1", "file": "latency.csv",
        "title": "Command confirmation latency over the real control path "
                 "(upper bound: 200 ms telemetry quantisation)",
        "kind": "agg", "group": ["metric", "label"], "metrics": [("value_ms", "latency (ms)")],
        "where": ("ok", "1"),
    },
    {
        "section": "5.1", "file": "estop.csv",
        "title": "Emergency-stop stopping distance",
        "kind": "agg", "group": ["speed_pwm", "surface"],
        "metrics": [("distance_cm", "distance (cm)"), ("stop_time_s", "stop time (s)")],
    },
    {
        "section": "5.1", "file": "deadman_physical.csv",
        "title": "Dead-man wheel-stop time (expected 2.0 s)",
        "kind": "agg", "group": ["speed_pwm"], "metrics": [("stop_s", "stop time (s)")],
    },
    {
        "section": "5.2", "file": "glass2glass.csv",
        "title": "End-to-end video delay",
        "kind": "agg", "group": ["label"], "metrics": [("delay_ms", "delay (ms)")],
    },
    {
        "section": "5.3", "file": "network.csv",
        "title": "Wi-Fi range and link degradation",
        "kind": "rows",
        "columns": ["label", "distance_m", "obstacles", "loss_pct", "rtt_avg_ms",
                    "rtt_max_ms", "rtt_mdev_ms", "signal_dbm_start", "tx_bitrate_mbps",
                    "iperf_mbps", "video", "control"],
    },
    {
        "section": "5.4", "file": "faults.csv",
        "title": "Fault injection and automatic recovery",
        "kind": "agg", "group": ["test_id", "fault"],
        "metrics": [("recovery_ms", "recovery (ms)"), ("down_detected_ms", "detection (ms)")],
        "rate": ("ok", "recovered"),
    },
    {
        "section": "5.4", "file": "fault_watch.csv",
        "title": "Manually injected faults: health transitions",
        "kind": "rows",
        "columns": ["label", "t_s", "field", "from_value", "to_value", "held_s"],
    },
    {
        "section": "5.5", "file": "resources.csv",
        "title": "Resource utilisation on the Raspberry Pi 4 (per-process CPU is % of one core)",
        "kind": "agg", "group": ["condition"],
        "metrics": [("cpu_pct", "total CPU (%)"), ("p1_cpu_pct", "P1 CPU (%)"),
                    ("p2_cpu_pct", "P2 CPU (%)"), ("p3_cpu_pct", "P3 CPU (%)"),
                    ("mem_used_mb", "memory used (MB)"), ("temp_c", "SoC temp (C)"),
                    ("tx_kbps", "uplink (kbps)")],
        "flags": [("under_voltage_ever", "under-voltage seen"),
                  ("throttled_now", "throttled samples")],
    },
    {
        "section": "5.6", "file": "ultrasonic.csv",
        "title": "Ultrasonic range error by true distance",
        "kind": "agg", "group": ["true_cm"],
        "metrics": [("error_cm", "error (cm)"), ("reading_cm", "reading (cm)")],
    },
    {
        "section": "5.6", "file": "thermal.csv",
        "title": "Temperature and humidity error vs reference instrument",
        "kind": "agg", "group": [],
        "metrics": [("error_c", "temp error (C)"), ("error_rh", "humidity error (%RH)")],
    },
    {
        "section": "5.6", "file": "gas.csv",
        "title": "Gas sensor response (raw ADC counts, uncalibrated)",
        "kind": "agg", "group": ["source"],
        "metrics": [("rise_adc", "rise (ADC)"), ("trip_s", "time to warn (s)")],
    },
    {
        "section": "5.6", "file": "gps_static.csv",
        "title": "Static GPS accuracy",
        "kind": "rows",
        "columns": ["label", "n_samples", "duration_min", "ref_mode", "mean_m", "sd_m",
                    "rms_m", "cep50_m", "cep95_m", "max_m", "mean_sats"],
    },
    {
        "section": "5.7", "file": "field.csv",
        "title": "End-to-end rescue runs",
        "kind": "agg", "group": ["course"],
        "metrics": [("time_to_victim_s", "time to victim (s)"), ("time_total_s", "total time (s)"),
                    ("collisions", "collisions"), ("unplanned_stops", "unplanned stops")],
        "rate": ("result", "runs passed"),
    },
    {
        "section": "5.8", "file": "sus.csv",
        "title": "Operator usability (System Usability Scale)",
        "kind": "agg", "group": [],
        "metrics": [("sus_score", "SUS score (0-100)"), ("task_time_s", "task time (s)"),
                    ("errors", "operator errors")],
        "rate": ("completed", "participants completing the task"),
    },
    {
        "section": "4-5", "file": "checklist.csv",
        "title": "Hardware and integration checklist (TEST_REPORT sections 4 and 5)",
        "kind": "checklist",
    },
)


def is_pass(value: str) -> bool:
    return str(value).strip().upper() in ("1", "PASS", "TRUE", "YES", "OK")


def table(out: io.StringIO, header: list[str], rows: list[list[str]]) -> None:
    if not rows:
        return
    out.write("| " + " | ".join(header) + " |\n")
    out.write("|" + "|".join("---" for _ in header) + "|\n")
    for row in rows:
        out.write("| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |\n")
    out.write("\n")


def render_agg(out: io.StringIO, report: dict, rows: list[dict]) -> None:
    where = report.get("where")
    if where:
        rows = [row for row in rows if str(row.get(where[0], "")) == where[1]]

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key, "") for key in report["group"])].append(row)

    header = [*report["group"], "measure", *STATS]
    body: list[list[str]] = []
    for key in sorted(groups):
        for column, pretty in report["metrics"]:
            values = [v for v in (to_float(r.get(column)) for r in groups[key]) if v is not None]
            if not values:
                continue
            stats = describe(values)
            body.append([*key, pretty, *[stats.get(name, "") for name in STATS]])
    table(out, header, body)

    rate = report.get("rate")
    if rate:
        column, label = rate
        for key in sorted(groups):
            members = groups[key]
            passed = sum(1 for row in members if is_pass(row.get(column, "")))
            prefix = " / ".join(str(part) for part in key if part != "")
            out.write(f"- {label}{f' [{prefix}]' if prefix else ''}: "
                      f"**{passed}/{len(members)}**\n")
        out.write("\n")

    for column, label in report.get("flags", ()):
        for key in sorted(groups):
            members = groups[key]
            hits = sum(1 for row in members if is_pass(row.get(column, "")))
            prefix = " / ".join(str(part) for part in key if part != "")
            out.write(f"- {label}{f' [{prefix}]' if prefix else ''}: "
                      f"{hits}/{len(members)} samples\n")
        out.write("\n")


def render_rows(out: io.StringIO, report: dict, rows: list[dict]) -> None:
    columns = [c for c in report["columns"] if any(row.get(c, "") != "" for row in rows)]
    table(out, columns, [[row.get(c, "") for c in columns] for row in rows])


def render_checklist(out: io.StringIO, rows: list[dict]) -> None:
    failed = [row for row in rows if not is_pass(row.get("result", ""))]
    out.write(f"- recorded: **{len(rows)}**, passed: **{len(rows) - len(failed)}**, "
              f"failed: **{len(failed)}**\n\n")
    table(out, ["test_id", "result", "measured", "tester", "notes"],
          [[row.get("test_id", ""), row.get("result", ""), row.get("measured", ""),
            row.get("tester", ""), row.get("notes", "")] for row in rows])
    if failed:
        out.write("Failures to write up in TEST_REPORT section 9: "
                  + ", ".join(row.get("test_id", "?") for row in failed) + "\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--only", help="limit to one section, e.g. 5.4")
    parser.add_argument("--out", type=Path, help="write markdown to this file as well")
    args = parser.parse_args()

    out = io.StringIO()
    out.write("# Measured results\n\n")
    out.write(f"Generated from `{args.results_dir}` by tools/eval/summarize.py. "
              "Every figure below is a measurement on the assembled robot.\n\n")

    outstanding: list[str] = []
    current_section = None
    for report in REPORTS:
        if args.only and report["section"] != args.only:
            continue
        rows = read_rows(args.results_dir / report["file"])
        if not rows:
            outstanding.append(f"{report['section']} {report['title']} (`{report['file']}`)")
            continue
        if report["section"] != current_section:
            out.write(f"## Section {report['section']}\n\n")
            current_section = report["section"]
        out.write(f"### {report['title']}\n\n")
        plural = "row" if len(rows) == 1 else "rows"
        out.write(f"Source: `{report['file']}`, {len(rows)} raw {plural}.\n\n")
        if report["kind"] == "agg":
            render_agg(out, report, rows)
        elif report["kind"] == "rows":
            render_rows(out, report, rows)
        else:
            render_checklist(out, rows)

    if outstanding:
        out.write("## Not yet measured\n\n")
        for item in outstanding:
            out.write(f"- [ ] {item}\n")
        out.write("\n")

    text = out.getvalue()
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"written to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
