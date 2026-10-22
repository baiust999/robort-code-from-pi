#!/usr/bin/env python3
"""SIMULATED / SYNTHETIC illustration of the E3 kinematic stopping-distance
bound. This is a software model, not a measurement. Every number this
script prints or writes must carry the word SIMULATED when copied anywhere
outside this directory, and must never be merged into tools/eval/results/ or
quoted as if it were a row of estop.csv.

Research question this illustrates: Section 5.1's audit of Table 5.4
(`research paper/section5_results.md`, "Analysis and verification") found
that the real, tape-measured E3 distances exceed the documented kinematic
stop model by one to two orders of magnitude at all three speeds, and named
"a difference between the procedure as run and as described (for example,
the distance including the operator's reaction before the press)" as one
of three unresolved candidate explanations. This script makes that specific
candidate concrete and quantified: it draws the post-stop-command travel
distance from the SAME verified kinematic model the paper already uses,
with an additional randomly-drawn delay representing total latency from
stop command to the motors actually halting, drawn from the ALREADY-
MEASURED command-latency distribution in Table 5.1 (`motor_stop`, mean
314 ms, SD 80 ms, n=30, `tools/eval/results/latency.csv`) rather than an
invented number. Table 5.1's figure does not include human operator
reaction time (it is a telemetry-confirmed command/motor latency only), so
even this generous substitution is expected to still fall far short of the
real Table 5.4 figures -- and this script's own job is only to show by how
much, with an explicit distribution instead of a single order-of-magnitude
sentence.

Verified constants used (re-read from the same files the paper's own audit
cites, not re-derived independently here):
  - No-load speed at PWM 180 (the cap): (60 RPM / 60) x pi x 0.065 m wheel
    diameter = 0.20 m/s (Table 2, `pi/common/protocol.py` MAX_PWM=180).
  - Speed scales linearly with PWM (no-load DC motor model; not itself
    separately verified against this specific motor's datasheet or load,
    so this is an assumption, not a cited measurement).
  - Ramp-stop time(PWM) = ceil(PWM / MOTOR_RAMP_STEP) x MOTOR_SERVICE_PERIOD_MS
    = ceil(PWM / 15) x 10 ms (`arduino/config.h`, `arduino/motors.cpp`,
    re-derived in `research paper/section5_results.md` for PWM 180 = 120 ms;
    this script applies the same formula at PWM 60 and 120).
  - Command latency ~ Normal(314 ms, 80 ms), truncated at 0
    (`tools/eval/results/latency.csv`, Table 5.1, `motor_stop`, n=30).

Model: distance_cm = v(PWM) x 100 x (ramp_time_s(PWM) + latency_s)
where latency_s is drawn once per simulated trial. This is an upper-bound
style sum (ramp time plus latency, not blended), matching how the paper's
own text computes its "at most 2.5 cm" / "at most about 6 cm" bounds.

Usage:
    ./estop_distance_sim.py --out ../output/estop_sim_report.md \\
        --csv-out output/estop_distance_SIMULATED.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from pathlib import Path

NO_LOAD_SPEED_MS_AT_PWM180 = 0.20  # m/s, Table 2 + pi/common/protocol.py MAX_PWM
RAMP_STEP = 15          # arduino/config.h MOTOR_RAMP_STEP
SERVICE_PERIOD_MS = 10  # arduino/config.h MOTOR_SERVICE_PERIOD_MS
LATENCY_MEAN_S = 0.314  # Table 5.1 motor_stop mean, latency.csv
LATENCY_SD_S = 0.080    # Table 5.1 motor_stop SD, latency.csv
SEED = 20261022         # same convention as deadman_robustness_sim.py
PWM_LEVELS = (60, 120, 180)


def speed_ms(pwm: int) -> float:
    return NO_LOAD_SPEED_MS_AT_PWM180 * pwm / 180.0


def ramp_time_s(pwm: int) -> float:
    ticks = math.ceil(pwm / RAMP_STEP)
    return ticks * SERVICE_PERIOD_MS / 1000.0


def simulate(trials_per_pwm: int, rng: random.Random) -> dict[int, list[float]]:
    out: dict[int, list[float]] = {}
    for pwm in PWM_LEVELS:
        v = speed_ms(pwm)
        ramp_s = ramp_time_s(pwm)
        distances = []
        for _ in range(trials_per_pwm):
            latency_s = max(0.0, rng.gauss(LATENCY_MEAN_S, LATENCY_SD_S))
            distance_cm = v * 100.0 * (ramp_s + latency_s)
            distances.append(distance_cm)
        out[pwm] = distances
    return out


def write_csv(path: Path, results: dict[int, list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["SIMULATED_NOT_REAL", "trial", "pwm", "ramp_time_s",
                         "distance_cm_simulated"])
        for pwm, distances in results.items():
            ramp_s = ramp_time_s(pwm)
            for i, d in enumerate(distances, start=1):
                writer.writerow(["SIMULATED", i, pwm, f"{ramp_s:.3f}", f"{d:.3f}"])


def render_report(results: dict[int, list[float]], trials_per_pwm: int) -> str:
    lines = [
        "# E3 kinematic stopping-distance illustration (SIMULATED)",
        "",
        "SIMULATED / SYNTHETIC. Not a measurement. Generated by "
        "`research-analysis/sim/estop_distance_sim.py`. See that script's "
        "docstring for the exact model and which inputs are cited "
        "(Table 5.1, Table 2) versus assumed (linear PWM-to-speed scaling).",
        "",
        f"Seed {SEED}, {trials_per_pwm} simulated trials per PWM level.",
        "",
        "| PWM | N | Mean (SIMULATED) cm | SD | Min | Max | Real Table 5.4 mean cm | Ratio real/simulated |",
        "|---|---|---|---|---|---|---|---|",
    ]
    real_means = {60: 42.7, 120: 75.9, 180: 91.3}  # tools/eval/results/estop.csv, Table 5.4
    for pwm in PWM_LEVELS:
        d = results[pwm]
        n = len(d)
        mean = statistics.fmean(d)
        sd = statistics.stdev(d) if n > 1 else 0.0
        real_mean = real_means[pwm]
        ratio = real_mean / mean if mean else float("inf")
        lines.append(
            f"| {pwm} | {n} | {mean:.2f} | {sd:.2f} | {min(d):.2f} | {max(d):.2f} "
            f"| {real_mean:.1f} | {ratio:.1f}x |"
        )
    lines += [
        "",
        "**Reading this table.** The simulated column uses the paper's own "
        "verified kinematic model (no-load speed, firmware ramp time) plus "
        "the already-measured command-latency distribution of Table 5.1, as "
        "a generous stand-in for total stop-command-to-halt delay -- it does "
        "not include human operator reaction time, which would only widen "
        "the simulated distribution somewhat, not close a ratio measured in "
        "the tens. The real/simulated ratio column shows that Table 5.4's "
        "tape-measured means remain far larger than even this generous "
        "model at every PWM level, which is the same CONTRADICTED finding "
        "the paper's own text states in prose; this table only gives it a "
        "concrete number per speed instead of one order-of-magnitude "
        "sentence.",
        "",
        "**Limitations.** The PWM-to-speed scaling is a linear no-load DC "
        "motor assumption, not independently verified for this specific "
        "motor under its actual rolling load; the command-latency input is a "
        "real measured distribution (Table 5.1) but was measured for a "
        "different purpose (command/telemetry confirmation, not a "
        "stopping-distance proxy) and excludes human reaction time entirely. "
        "This simulation does not explain the real Table 5.4 anomaly and is "
        "not offered as doing so -- the paper's own three candidate "
        "explanations (procedure difference, motor/wheel spec mismatch, "
        "recording error) remain equally open. This file exists only to "
        "give the magnitude of the gap a number, for a reader who wants more "
        "than 'one to two orders of magnitude'.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=1000)
    ap.add_argument("--out", default=None, help="write markdown report to this path")
    ap.add_argument("--csv-out", default=None,
                    help="write per-trial SIMULATED rows to this CSV path")
    args = ap.parse_args()

    rng = random.Random(SEED)
    results = simulate(args.trials, rng)
    report = render_report(results, args.trials)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report)
        print(f"wrote {out_path}")
    else:
        print(report)

    if args.csv_out:
        write_csv(Path(args.csv_out), results)
        print(f"wrote {args.csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
