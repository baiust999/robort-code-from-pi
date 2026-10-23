#!/usr/bin/env python3
"""Independent cell check of Section 5 tables against the result CSVs.

Recomputes every figure from tools/eval/results/*.csv with the standard
library only (no use of section5_stats.py or summarize.py), parses the markdown
tables in research paper/section5_results.md (HTML comments removed), and
reports each cell that differs by more than half a unit of its last printed
digit. Run from anywhere:

    python3 -I research-analysis/scripts/audit_section5_2026-10-23.py

Covered: row counts of Table 5.0, Tables 5.1, 5.2, 5.2a (deadman_trip), 5.7,
5.8, 5.8a, 5.10, 5.10a (row counts) and 5.13. Not covered: bootstrap median
intervals (seeded resampling), Tables 5.2a deadman_panic and 5.2b (need the
rotated P1 log excerpts), Tables 5.9 to 5.9c, 5.13a, 5.13b, 5.14 to 5.16.
"""
from __future__ import annotations

import csv
import math
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "tools/eval/results"
MD = ROOT / "research paper/section5_results.md"

T_CRIT = {29: 2.0452296421327034, 9: 2.2621571627982053}  # two-sided 95%, Student t

checked = 0
bad: list[str] = []


def rows(name):
    with open(RES / name, newline="", encoding="utf8") as f:
        return list(csv.DictReader(f))


def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def summary(xs):
    n = len(xs)
    m = st.fmean(xs)
    sd = st.stdev(xs) if n > 1 else float("nan")
    half = T_CRIT.get(n - 1, float("nan")) * sd / math.sqrt(n)
    return dict(n=n, mean=m, sd=sd, lo=m - half, hi=m + half, min=min(xs),
                max=max(xs), med=st.median(xs), p95=pct(xs, 0.95))


def cmp(label, shown, value):
    """Compare a printed cell with a recomputed value to the printed precision."""
    global checked
    shown = shown.strip().replace(",", "")
    checked += 1
    m = re.match(r"^-?\d+(\.(\d+))?$", shown)
    if not m:
        bad.append(f"{label}: unparsable cell {shown!r}")
        return
    dec = len(m.group(2) or "")
    if abs(float(shown) - value) > 0.5 * 10 ** (-dec) + 1e-9:
        bad.append(f"{label}: printed {shown}, recomputed {value:.6g}")


def parse_tables(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    tables, cur, cap = {}, [], None
    for line in text.split("\n"):
        m = re.match(r"\*\*Table (5\.\d+[a-z]?)\.", line)
        if m:
            cap = m.group(1)
        if line.startswith("|"):
            cur.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif cur:
            if cap and cap not in tables:
                tables[cap] = [r for r in cur if not set("".join(r)) <= set("-: ")]
            cur = []
    if cur and cap and cap not in tables:
        tables[cap] = [r for r in cur if not set("".join(r)) <= set("-: ")]
    return tables


def ci(s):
    return f"{s['lo']:.1f} to {s['hi']:.1f}"


text = MD.read_text(encoding="utf8")
T = parse_tables(text)

# ---- Table 5.0 row counts ---------------------------------------------------
counts = {"latency.csv": 420, "estop.csv": 23, "network.csv": 6, "faults.csv": 30,
          "fault_watch.csv": 94, "resources.csv": 3608, "ultrasonic.csv": 50,
          "gas.csv": 5, "dht11_environmental.csv": 5, "gps_static.csv": 1}
for f, n in counts.items():
    actual = len(rows(f))
    checked += 1
    if actual != n:
        bad.append(f"row count {f}: Table 5.0 value {n}, file has {actual}")
t50 = " ".join(" ".join(r) for r in T["5.0"])
for f, n in counts.items():
    if f"`{f}`" not in t50 or not re.search(rf"{n} (summary )?rows?", t50):
        bad.append(f"Table 5.0 does not state '{n} rows' next to `{f}`")

# ---- latency tables ---------------------------------------------------------
lat = defaultdict(list)
for r in rows("latency.csv"):
    if r["ok"] == "1":
        lat[(r["metric"], r["label"])].append(float(r["value_ms"]))
sessions = {"2026-10-07": "on-pi", "2026-10-21": "on-pi-2026-10-21"}
for r in T["5.1"][1:]:
    s = summary(lat[(r[0], sessions[r[1]])])
    tag = f"T5.1 {r[0]} {r[1]}"
    cmp(tag + " N", r[2], s["n"]); cmp(tag + " mean", r[3], s["mean"])
    checked += 1
    if r[4] != ci(s):
        bad.append(f"{tag} CI: printed {r[4]}, recomputed {ci(s)}")
    for i, k in zip(range(5, 10), ("sd", "min", "max", "med", "p95")):
        cmp(f"{tag} {k}", r[i], s[k])
for r in T["5.2"][1:]:
    s = summary(lat[(r[0], "on-pi-phaselocked")])
    tag = f"T5.2 {r[0]}"
    for i, k in zip((1, 2, 3, 4, 5, 6, 8), ("n", "mean", "sd", "min", "max", "med", "p95")):
        cmp(f"{tag} {k}", r[i], s[k])
r = T["5.2a"][1]
s = summary(lat[("deadman_trip", "on-pi-2026-10-21")])
for i, k in zip((3, 5, 6, 7, 8, 9), ("mean", "sd", "min", "max", "med", "p95")):
    cmp(f"T5.2a deadman_trip {k}", r[i], s[k])
checked += 1
if r[4] != ci(s):
    bad.append(f"T5.2a CI: printed {r[4]}, recomputed {ci(s)}")

# ---- network ----------------------------------------------------------------
net = {r["label"]: r for r in rows("network.csv")}
for r in T["5.7"][1:]:
    n = net[r[0]]
    cmp(f"T5.7 {r[0]} distance", r[1], float(n["distance_m"]))
    cmp(f"T5.7 {r[0]} loss", r[5], float(n["loss_pct"]))
    cmp(f"T5.7 {r[0]} rtt_avg", r[6], float(n["rtt_avg_ms"]))
    cmp(f"T5.7 {r[0]} sig_start", r[7], float(n["signal_dbm_start"]))
    cmp(f"T5.7 {r[0]} sig_end", r[8], float(n["signal_dbm_end"]))
    cmp(f"T5.7 {r[0]} bitrate", r[9], float(n["tx_bitrate_mbps"]))
checked += 1
if len(T["5.7"]) - 1 != len(net):
    bad.append(f"T5.7 has {len(T['5.7'])-1} rows, network.csv has {len(net)}")

# ---- faults -----------------------------------------------------------------
fl = defaultdict(lambda: defaultdict(list))
ok = defaultdict(int)
for r in rows("faults.csv"):
    fl[r["test_id"]]["det"].append(float(r["down_detected_ms"]))
    fl[r["test_id"]]["rec"].append(float(r["recovery_ms"]))
    ok[r["test_id"]] += r["ok"] == "1" and r["pid_changed"] == "1"
for r in T["5.8"][1:]:
    s = summary(fl[r[0]]["det" if r[2].startswith("detection") else "rec"])
    tag = f"T5.8 {r[0]} {r[2]}"
    for i, k in zip((3, 5, 6, 7, 8), ("mean", "sd", "min", "max", "med")):
        cmp(f"{tag} {k}", r[i], s[k])
    checked += 1
    if r[4] != ci(s):
        bad.append(f"{tag} CI: printed {r[4]}, recomputed {ci(s)}")
    checked += 1
    if r[9] != f"{ok[r[0]]}/{len(fl[r[0]]['det'])}":
        bad.append(f"{tag} recovered: printed {r[9]}, recomputed {ok[r[0]]}/{len(fl[r[0]]['det'])}")


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d


for r in T["5.8a"][1:]:
    k, n = map(int, r[1].split("/"))
    lo, hi = wilson(k, n)
    checked += 1
    exp = f"{lo*100:.1f}% to {hi*100:.0f}%" if hi > 0.9999 else f"{lo*100:.1f}% to {hi*100:.1f}%"
    if r[2].replace("72.2", "72.2") != exp and r[2] != exp.replace(".0%", "%"):
        bad.append(f"T5.8a {r[0]}: printed {r[2]}, recomputed {exp}")

# ---- resources --------------------------------------------------------------
res = defaultdict(lambda: defaultdict(list))
for r in rows("resources.csv"):
    for col, name in (("cpu_pct", "total CPU"), ("p1_cpu_pct", "P1 CPU"), ("p2_cpu_pct", "P2 CPU"),
                      ("p3_cpu_pct", "P3 CPU"), ("mem_used_mb", "memory used"), ("temp_c", "SoC temp")):
        res[r["condition"]][name].append(float(r[col]))
for r in T["5.10"][1:]:
    xs = res[r[0]][r[1]]
    dec = 2 if "CPU" in r[1] and r[1] == "total CPU" or r[1] in ("P1 CPU", "P2 CPU", "P3 CPU") else 1
    tag = f"T5.10 {r[0]} {r[1]}"
    cmp(tag + " N", r[2], len(xs)); cmp(tag + " mean", r[3], st.fmean(xs))
    cmp(tag + " sd", r[4], st.stdev(xs)); cmp(tag + " max", r[5], max(xs)); cmp(tag + " p95", r[6], pct(xs, 0.95))
split = [r for r in T["5.10a"][1:] if r[0].startswith("20:")]
checked += 1
if sum(int(r[1]) for r in split) != len(res["driving+media"]["total CPU"]):
    bad.append("T5.10a logger-run rows do not sum to the driving+media row count")

# ---- GPS static -------------------------------------------------------------
g = rows("gps_static.csv")[0]
r = T["5.13"][1]
for i, k in zip(range(0, 9), ("n_samples", "duration_min", "mean_m", "sd_m", "rms_m", "cep50_m", "cep95_m", "max_m", "mean_sats")):
    cmp(f"T5.13 {k}", r[i], float(g[k]))

print(f"cells checked: {checked}")
print(f"mismatches: {len(bad)}")
for b in bad:
    print("  -", b)
