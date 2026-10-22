#!/usr/bin/env python3
"""Uncertainty and audit figures for paper Section 5, from the existing data.

summarize.py gives n / mean / SD / percentiles per CSV. This script adds what
the Results section needs on top of that, without collecting anything new and
without modifying any input file:

  - 95% confidence intervals: Student t for means of independent trials,
    seeded bootstrap for medians, Wilson score for success proportions, and
    non-overlapping batch means for the autocorrelated 1 Hz resource series
  - the dead-man interval decomposed from P1's own event log (one clock)
  - the resources.csv audit: logger runs per condition, overlapping loggers
  - the static GPS figures recomputed from telemetry.log, with the resolution
    of the logged coordinates
  - the F9 gps_fix transitions matched against P1 GPS_FAIL port events

    ./section5_stats.py                       # print markdown
    ./section5_stats.py --out results/section5_stats.md

The var/log inputs rotate; a missing log is reported and its block skipped.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import math
import random
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, haversine_m, percentile  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "var" / "log"

# Two-sided 95% Student t quantiles by degrees of freedom.
T95 = {6: 2.447, 8: 2.306, 9: 2.262, 29: 2.045}

out_lines: list[str] = []


def emit(line: str = "") -> None:
    out_lines.append(line)


def t95(df: int) -> float:
    return T95.get(df, 1.96)


def mean_ci(v: list[float]) -> tuple[float, float, float]:
    m = st.mean(v)
    h = t95(len(v) - 1) * st.stdev(v) / math.sqrt(len(v))
    return m, m - h, m + h


def median_ci(v: list[float], reps: int = 10000, seed: int = 1) -> tuple[float, float]:
    rng = random.Random(seed)
    meds = sorted(st.median(rng.choices(v, k=len(v))) for _ in range(reps))
    return meds[int(0.025 * reps)], meds[int(0.975 * reps) - 1]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def batch_ci(v: list[float], batches: int = 10) -> tuple[float, float, float]:
    """Mean and 95% CI from non-overlapping batch means (series is autocorrelated)."""
    size = len(v) // batches
    means = [st.mean(v[i * size:(i + 1) * size]) for i in range(batches)]
    m = st.mean(means)
    h = t95(batches - 1) * st.stdev(means) / math.sqrt(batches)
    return m, m - h, m + h


def lag1(v: list[float]) -> float:
    m = st.mean(v)
    num = sum((a - m) * (b - m) for a, b in zip(v, v[1:]))
    den = sum((a - m) ** 2 for a in v)
    return num / den if den else 0.0


def rows(name: str) -> list[dict]:
    with (RESULTS_DIR / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def latency() -> None:
    emit("## E1 latency: CIs (latency.csv)")
    emit()
    emit("| metric | label | n | mean | 95% CI mean | median | 95% CI median (bootstrap) | p95 |")
    emit("|---|---|---|---|---|---|---|---|")
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows("latency.csv"):
        if r["ok"] == "1" and r["value_ms"]:
            groups[(r["metric"], r["label"])].append(float(r["value_ms"]))
    for (metric, label), v in sorted(groups.items()):
        m, lo, hi = mean_ci(v)
        mlo, mhi = median_ci(v)
        emit(f"| {metric} | {label} | {len(v)} | {m:.1f} | {lo:.1f} to {hi:.1f} | "
             f"{st.median(v):.1f} | {mlo:.1f} to {mhi:.1f} | {percentile(sorted(v), 95):.1f} |")
    emit()


LOG_LINE = re.compile(r"^\[(\S+)\]\[P1\]\[\w+\]\[(\w+)\]\[[^\]]*\]\{(.*)\}")
ARMING = re.compile(r"wire=(F|B|L|R|H)")


def deadman_log() -> None:
    """Last arming command TX, its ACK and the PANIC line, all on P1's clock."""
    emit("## E1 dead-man interval from P1's event log (on-pi-2026-10-21)")
    emit()
    probe = [(datetime.fromisoformat(r["iso_ts"]), float(r["value_ms"]))
             for r in rows("latency.csv")
             if r["metric"] == "deadman_panic" and r["label"] == "on-pi-2026-10-21"]
    log = LOG_DIR / "p1_events.log"
    if not probe or not log.exists():
        emit("(skipped: probe rows or p1_events.log missing)")
        emit()
        return
    day = probe[0][0].strftime("[%Y-%m-%dT%H")
    events = []
    with log.open(errors="replace") as handle:
        for line in handle:
            if line.startswith(day) and (m := LOG_LINE.match(line)):
                events.append((datetime.fromisoformat(m.group(1)), m.group(2), m.group(3)))
    panics = []
    for i, (t, tag, body) in enumerate(events):
        if tag != "DEBUG_RX" or "PANIC DEADMAN" not in body:
            continue
        j = i - 1
        while j >= 0 and not (events[j][1] == "DEBUG_TX" and ARMING.search(events[j][2])):
            j -= 1
        k = i - 1
        while k > j and not (events[k][1] == "DEBUG_RX" and "ACK" in events[k][2]):
            k -= 1
        if j >= 0 and k > j:
            panics.append((t, events[j][0], events[k][0]))
    tx_panic, ack_panic, tx_ack, ws_leg = [], [], [], []
    for p_ts, p_ms in probe:
        t, tx, ack = min(panics, key=lambda p: abs((p_ts - p[0]).total_seconds()))
        if abs((p_ts - t).total_seconds()) >= 2:
            continue
        tx_panic.append((t - tx).total_seconds() * 1000)
        ack_panic.append((t - ack).total_seconds() * 1000)
        tx_ack.append((ack - tx).total_seconds() * 1000)
        ws_leg.append(p_ms - tx_panic[-1])
    emit(f"Matched {len(tx_panic)} of {len(probe)} probe trials to a PANIC DEADMAN line.")
    emit()
    emit("| interval (ms) | n | mean | SD | 95% CI mean | min | median | max |")
    emit("|---|---|---|---|---|---|---|---|")
    for name, v in (("P1 TX of last command -> P1 RX of PANIC line", tx_panic),
                    ("P1 RX of ACK -> P1 RX of PANIC line", ack_panic),
                    ("P1 TX of last command -> P1 RX of its ACK", tx_ack),
                    ("probe deadman_panic minus first row (WebSocket + P1 leg)", ws_leg)):
        m, lo, hi = mean_ci(v)
        emit(f"| {name} | {len(v)} | {m:.1f} | {st.stdev(v):.1f} | {lo:.1f} to {hi:.1f} | "
             f"{min(v):.1f} | {st.median(v):.1f} | {max(v):.1f} |")
    emit()


def estop() -> None:
    emit("## E3 stopping distance (estop.csv)")
    emit()
    emit("| speed_pwm | n | mean | 95% CI mean | SD | median | 95% CI median (bootstrap) |")
    emit("|---|---|---|---|---|---|---|")
    groups: dict[int, list[float]] = defaultdict(list)
    for r in rows("estop.csv"):
        groups[int(r["speed_pwm"])].append(float(r["distance_cm"]))
    for speed, v in sorted(groups.items()):
        m, lo, hi = mean_ci(v)
        mlo, mhi = median_ci(v)
        emit(f"| {speed} | {len(v)} | {m:.1f} | {lo:.1f} to {hi:.1f} | {st.stdev(v):.1f} | "
             f"{st.median(v):.1f} | {mlo:.1f} to {mhi:.1f} |")
    emit()


def faults() -> None:
    emit("## E7 fault injection (faults.csv)")
    emit()
    emit("| test | n | recovered | Wilson 95% CI | recovery mean (s) | 95% CI mean (s) | detection mean (ms) | 95% CI (ms) |")
    emit("|---|---|---|---|---|---|---|---|")
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows("faults.csv"):
        groups[r["test_id"]].append(r)
    total = ok_total = 0
    for test, rs in sorted(groups.items()):
        ok = [r for r in rs if r["ok"] == "1" and r["pid_changed"] == "1"]
        rec = [float(r["recovery_ms"]) / 1000 for r in ok]
        det = [float(r["down_detected_ms"]) for r in ok]
        lo, hi = wilson(len(ok), len(rs))
        rm, rlo, rhi = mean_ci(rec)
        dm, dlo, dhi = mean_ci(det)
        emit(f"| {test} | {len(rs)} | {len(ok)} | {lo * 100:.1f}% to {hi * 100:.1f}% | {rm:.2f} | "
             f"{rlo:.2f} to {rhi:.2f} | {dm:.1f} | {dlo:.1f} to {dhi:.1f} |")
        total += len(rs)
        ok_total += len(ok)
    lo, hi = wilson(ok_total, total)
    emit(f"| pooled | {total} | {ok_total} | {lo * 100:.1f}% to {hi * 100:.1f}% | | | | |")
    emit()


def resources() -> None:
    emit("## E8 resources: logger runs, batch-means CIs (resources.csv)")
    emit()
    data = rows("resources.csv")
    by: dict[str, list[dict]] = defaultdict(list)
    for r in data:
        by[r["condition"]].append(r)
    emit("Logger runs are grouped by inferred start time (iso_ts - t_s, 2 s tolerance).")
    emit()
    emit("| condition | rows | wall span (s) | logger runs (rows each) | median row spacing (s) |")
    emit("|---|---|---|---|---|")
    for cond, rs in by.items():
        ts = [datetime.fromisoformat(r["iso_ts"]) for r in rs]
        starts: list[list] = []
        for r, t in zip(rs, ts):
            s = t - timedelta(seconds=float(r["t_s"]))
            for run in starts:
                if abs((run[0] - s).total_seconds()) <= 2:
                    run[1] += 1
                    break
            else:
                starts.append([s, 1])
        gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
        runs = ", ".join(f"{s.strftime('%H:%M:%S')} ({n})" for s, n in starts)
        emit(f"| {cond} | {len(rs)} | {(ts[-1] - ts[0]).total_seconds():.0f} | {runs} | {st.median(gaps):.3f} |")
    emit()
    emit("Means with 95% CI from 10 non-overlapping batch means; lag-1 autocorrelation r1 of the raw series.")
    emit()
    emit("| condition | metric | n | mean | 95% CI (batch means) | r1 | median | IQR |")
    emit("|---|---|---|---|---|---|---|---|")
    for cond, rs in by.items():
        for col, name in (("cpu_pct", "total CPU (%)"), ("p1_cpu_pct", "P1 CPU (% core)"),
                          ("p2_cpu_pct", "P2 CPU (% core)"), ("tx_kbps", "uplink tx (kbps)")):
            v = [float(r[col]) for r in rs]
            m, lo, hi = batch_ci(v)
            q = sorted(v)
            emit(f"| {cond} | {name} | {len(v)} | {st.mean(v):.2f} | {lo:.2f} to {hi:.2f} | "
                 f"{lag1(v):.2f} | {st.median(v):.2f} | {percentile(q, 25):.2f} to {percentile(q, 75):.2f} |")
    emit()


TELEMETRY_COLUMNS = (
    "iso_ts", "seq", "temperature_c", "humidity_pct", "gas_ppm", "range_cm",
    "pan_angle", "tilt_angle", "fw_state", "uptime_ms", "lat", "lon",
    "gps_fix", "gps_sats", "serial_ok", "ws_clients", "turn_status", "alert_flags",
)


def fixes(path: Path, lo: str, hi: str) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    found = []
    with opener(path, "rt") as handle:
        next(handle)
        for line in handle:
            parts = line.rstrip("\n").split(",")
            if len(parts) != len(TELEMETRY_COLUMNS):
                continue
            r = dict(zip(TELEMETRY_COLUMNS, parts))
            if lo <= r["iso_ts"][:19] <= hi and r["gps_fix"] in ("1", "True", "true"):
                try:
                    r["lat"], r["lon"] = float(r["lat"]), float(r["lon"])
                except ValueError:
                    continue
                found.append(r)
    return found


def gps_block(name: str, fx: list[dict]) -> tuple[float, float]:
    lat = st.mean(r["lat"] for r in fx)
    lon = st.mean(r["lon"] for r in fx)
    err = sorted(haversine_m(lat, lon, r["lat"], r["lon"]) for r in fx)
    sats = [float(r["gps_sats"]) for r in fx if r["gps_sats"]]
    span = datetime.fromisoformat(fx[-1]["iso_ts"]) - datetime.fromisoformat(fx[0]["iso_ts"])
    emit(f"| {name} | {len(fx)} | {span.total_seconds() / 60:.1f} | {st.mean(err):.2f} | {st.stdev(err):.2f} | "
         f"{math.sqrt(st.mean(e * e for e in err)):.2f} | {percentile(err, 50):.2f} | {percentile(err, 95):.2f} | "
         f"{err[-1]:.1f} | {st.mean(sats):.2f} | {sum(e <= 10 for e in err) / len(err) * 100:.1f}% | "
         f"{len({(r['lat'], r['lon']) for r in fx})} |")
    return lat, lon


def gps() -> None:
    emit("## E9 static GPS recomputed from telemetry.log")
    emit()
    archive = LOG_DIR / "telemetry.log.5.gz"
    current = LOG_DIR / "telemetry.log"
    emit("| window | fixes | duration (min) | mean | SD | RMS | CEP50 | CEP95 | max | mean sats | within 10 m | distinct positions |")
    emit("|---|---|---|---|---|---|---|---|---|---|---|---|")
    centroids = []
    for path, name, lo, hi in (
            (archive, "2026-09-29 archive", "2026-09-29T15:19:24", "2026-09-29T17:28:32"),
            (current, "2026-10-22 outdoor (before F9-indoor)", "2026-10-22T12:23:46", "2026-10-22T12:58:05")):
        if not path.exists():
            emit(f"| {name} | (log {path.name} missing) |")
            continue
        fx = fixes(path, lo, hi)
        if fx:
            centroids.append(gps_block(name, fx))
            lats = sorted({r["lat"] for r in fx})
            steps = Counter(round((b - a) * 1e6) for a, b in zip(lats, lats[1:]))
    emit()
    if len(centroids) == 2:
        emit(f"Centroid separation between the two windows: {haversine_m(*centroids[0], *centroids[1]):.2f} m.")
    lat0 = math.radians(23.4536)
    dn = 1e-4 * math.pi / 180 * 6371000
    de = dn * math.cos(lat0)
    emit(f"Logged coordinates carry 4 decimals (p1_control/telemetry_log.py); lat step counts (1e-6 deg): "
         f"{dict(steps)}. Grid at 23.4536 N: {dn:.2f} m N-S x {de:.2f} m E-W; "
         f"uniform-rounding RMS radial contribution {math.sqrt((dn * dn + de * de) / 12):.2f} m.")
    emit()


def f9() -> None:
    emit("## F9 gps_fix transitions vs P1 GPS_FAIL events (fault_watch.csv, p1_events.log)")
    emit()
    log = LOG_DIR / "p1_events.log"
    fails = []
    if log.exists():
        with log.open(errors="replace") as handle:
            for line in handle:
                if "[GPS_FAIL]" in line:
                    fails.append(datetime.fromisoformat(line[1:30]))
    groups: dict[str, list[float]] = defaultdict(list)
    for r in rows("fault_watch.csv"):
        if r["field"] == "gps_fix" and r["from_value"] == "1":
            t = datetime.fromisoformat(r["iso_ts"])
            groups[r["label"]].append(min((abs((t - f).total_seconds()) for f in fails), default=1e9))
    emit("| label | fix-loss transitions | within 3 s of a GPS_FAIL | not near a GPS_FAIL |")
    emit("|---|---|---|---|")
    for label, d in groups.items():
        near = sum(x <= 3 for x in d)
        emit(f"| {label} | {len(d)} | {near} | {len(d) - near} |")
    first = [r for r in rows("fault_watch.csv")
             if r["field"] == "gps_fix" and r["from_value"] == "0" and r["label"] == "F9-gps-loss"][:1]
    if first:
        emit()
        emit(f"First gps_fix 0 -> 1 in F9-gps-loss at t = {first[0]['t_s']} s after the watch started "
             f"({first[0]['iso_ts']}).")
    emit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="write markdown here instead of stdout")
    args = parser.parse_args()
    emit("# Section 5 uncertainty and audit figures")
    emit()
    emit("Generated by tools/eval/section5_stats.py from tools/eval/results/*.csv and var/log. "
         "Derived figures only; no input file is modified.")
    emit()
    for block in (latency, deadman_log, estop, faults, resources, gps, f9):
        block()
    text = "\n".join(out_lines) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
