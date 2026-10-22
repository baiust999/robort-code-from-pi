# Calculation report

New and reproduced calculations from existing evidence in `tools/eval/results/`.
This is a software-verification artifact under `research-analysis/`; it does
not modify any file under `tools/eval/`, `research paper/`, or any protected
path. ASCII only.

## 1. What already existed before this task

`tools/eval/summarize.py` and `tools/eval/section5_stats.py` already compute,
from the raw CSVs in `tools/eval/results/`:

- n / mean / SD / min / max / median / p95 per metric (`summary.md`)
- 95% CIs (Student t for means, seeded bootstrap for medians, Wilson score
  for proportions, non-overlapping batch means for the autocorrelated 1 Hz
  resource series), dead-man interval decomposition from the P1 event log,
  GPS resolution analysis, and cross-checks of hand-entered rows against
  `var/log` (`section5_stats.md`)

This task's job under Phase 4 is to (a) independently re-derive a sample of
these figures from the raw CSVs with fresh, from-scratch code, not by
re-running the existing scripts, to confirm they are not silently wrong, and
(b) calculate what is justified but not yet present, and (c) formally write
up the known data-quality problem the task was asked to investigate.

## 2. Independent reproduction (fresh code, not the existing scripts)

### 2.1 `deadman_panic`, label `on-pi-2026-10-21`, from `latency.csv`

Formula: sample mean, sample standard deviation (Bessel-corrected, n-1),
median, min/max over `value_ms` where `metric == "deadman_panic"` and
`label == "on-pi-2026-10-21"`. 95% CI for the mean: Student t, df = n-1 = 29,
t_0.975,29 = 2.045.

Script: a one-off `python3 -I` snippet (not saved as a file; reproduced
below verbatim) reading `tools/eval/results/latency.csv` directly with the
stdlib `csv` and `statistics` modules only, independent of
`tools/eval/common.py`.

```python
import csv, statistics
rows = []
with open("tools/eval/results/latency.csv", newline="") as f:
    for r in csv.DictReader(f):
        if r["metric"] == "deadman_panic" and r["label"] == "on-pi-2026-10-21":
            rows.append(float(r["value_ms"]))
mean = statistics.mean(rows); sd = statistics.stdev(rows)
```

| quantity | this independent calculation | `summary.md` / `section5_stats.md` | match |
|---|---|---|---|
| n | 30 | 30 | yes |
| mean (ms) | 2079.12 | 2079.12 | yes |
| SD (ms) | 27.94 | 27.94 | yes |
| median (ms) | 2076.45 | 2076.45 | yes |
| min / max (ms) | 2022.3 / 2122.3 | 2022.3 / 2122.3 | yes |
| 95% CI of mean | 2068.68 to 2089.55 | 2068.7 to 2089.6 | yes (rounding only) |

Observations: all independent, repeated. Not independent experiments in the
causal-inference sense (30 trials of the same probe against the same
assembled robot on the same day), but they are the right unit for a
dispersion/CI statement about that probe's repeatability.

### 2.2 Wilson 95% CI for fault-recovery proportions, from `faults.csv`

Formula (Wilson, 1927; `references.bib:wilson1927`):

```
center = (p + z^2/2n) / (1 + z^2/n)
halfwidth = (z / (1 + z^2/n)) * sqrt(p(1-p)/n + z^2/4n^2)
```
with p = k/n, z = 1.96 for 95%.

Independently coded in `python3 -I` (stdlib `math` only) and checked against
k=10, n=10 (each of F3/F4/F5) and the pooled k=30, n=30:

| case | this independent calculation | `section5_stats.md` | match |
|---|---|---|---|
| F3/F4/F5, 10/10 each | 72.2% to 100.0% | 72.2% to 100.0% | yes |
| pooled, 30/30 | 88.6% to 100.0% | 88.6% to 100.0% | yes |

n here is the number of independent fault-injection trials (10 per fault
type, kill-and-observe-recovery), which are genuinely independent repeated
trials of the same procedure, not sub-samples of one run.

### 2.3 Full-pipeline reproducibility of `section5_stats.py`

Re-ran `tools/eval/section5_stats.py` unmodified, with the same inputs,
writing to a new path (`research-analysis/output/section5_stats_rerun_2026-10-22.md`)
rather than overwriting `tools/eval/results/section5_stats.md`.

Result: byte-identical except for one row:

```
E3 forward drive commands in P1's event logs
| date | PWM | commands |
2026-10-22 | 120 | 3   (committed table, generated earlier on 2026-10-22)
2026-10-22 | 120 | 48  (this rerun, later the same day)
```

Explanation, not a defect: per the script's own docstring, every block
except the "any retained day" E3 scan reads only the frozen
`tools/eval/results/log_excerpts/` snapshots, which do not change. The E3
"any retained day" block is the one exception -- it reads `var/log/p1_events.log*`
directly (live, growing files), explicitly so the scan can see commands on
days outside the frozen excerpt windows. Between the two runs today, the
robot was driven further (more real `F120` commands were logged), so the
count correctly grew from 3 to 48. Every other figure in the script's
output, including all CIs, the dead-man decomposition, the GPS recompute,
and the E10/E11/E12 cross-checks, reproduced exactly.

**Finding:** `section5_stats.py` is fully reproducible for every block
sourced from the frozen `log_excerpts/` snapshots and the CSVs. Only the one
block that deliberately reads the live log is time-dependent, and that is
documented behaviour, not a bug. Any reviewer rerunning this script on a
different day should expect that one row to differ and should cite the
`log_excerpts/` snapshot date, not "today", for that figure if it is quoted
in the paper.

## 3. Data-quality finding: ultrasonic and thermal rows are not independent measurements

Investigated per the task's explicit instruction to check the identical
`reading_cm`/`true_cm` values.

`tools/eval/results/ultrasonic.csv`: all 50 rows (5 distances x 10 trials)
have `reading_cm == true_cm` exactly, giving `error_cm == 0.0` on every
single row, at every one of the five tested distances (20, 75, 150, 284,
389 cm).

`tools/eval/results/thermal.csv`: all 5 rows have `error_c == 0.0` exactly;
`error_rh` varies only between 0.0 and 1.0 (a rounding-sized wobble).

This pattern is not physically plausible as genuine independent readings of
an HC-SR04-class ultrasonic sensor or a DHT11-class thermal sensor against a
reference instrument: real analogue-to-digital sensor noise at 10 repeated
trials and 5 different distances essentially never reproduces the exact
integer reference value every single time. By contrast, the harness's own
README usage example for this exact command
(`tools/eval/README.md`: `record.py ultrasonic true_cm=20 reading_cm=21`)
shows a 1 cm example error -- the logged data does not even match the
harness's own worked example's error pattern.

The most likely explanation is that the hand-entry step
(`record.py ultrasonic ...` / `record.py thermal ...`) was run with
`reading_cm` (or `sensor_c`) set equal to `true_cm` (or `ref_c`) as a
placeholder or default, rather than the value actually read off the sensor
at each of the 50 (or 5) trials.

**Conclusion, per the task's integrity rule:** `ultrasonic.csv` and
`thermal.csv` CANNOT be presented as independent sensor validation.
Section 5.6 of the paper must not quote a "0.0 cm mean error" or "+/-0 C
accuracy" for these sensors as a measured result. The existing
`gas.csv` data (ADC rise times, non-trivial variation across 5 trials) does
not show this pattern and is not implicated.

This finding is additive to, and consistent with, the prior session's own
Section 5 audit recorded in project memory (`section5-data-audit`), which
had already flagged E10 (ultrasonic) readings as `[VERIFICATION REQUIRED]`
for a different reason (the entered distances never appear in telemetry.log
at all). Both problems point the same way: `ultrasonic.csv` is not currently
usable as measured evidence.

**Recommendation for the paper (not executed here; Phase 7 proposes this as
a manuscript change):** mark Section 5.6's ultrasonic and thermal/humidity
rows `[VERIFICATION REQUIRED]` or `[PENDING MEASUREMENT]` pending a genuine
re-run where the reference instrument is read independently per trial, the
same way `gas.csv` already was.

## 4. New metric computed from existing evidence: dead-man safety margin in heartbeats

Not previously stated anywhere in the repository in these terms. Uses two
already-verified constants (no new measurement):

- `DEADMAN_MS = 2000` (`pi/common/protocol.py:67`, mirrors the Arduino
  firmware per its own comment)
- `HEARTBEAT_PERIOD_MS = 500` (`dashboard/src/lib/protocol.ts:11`, the
  dashboard's idle-heartbeat send interval)

Margin = floor(DEADMAN_MS / HEARTBEAT_PERIOD_MS) - 1 if DEADMAN_MS is an
exact multiple of HEARTBEAT_PERIOD_MS, else floor(DEADMAN_MS / HEARTBEAT_PERIOD_MS):
with 2000 / 500 = 4 exactly, 3 consecutive heartbeats can be lost without
tripping the dead-man; a 4th in a row is guaranteed to trip it. Full
derivation, boundary proof, and a Monte Carlo sensitivity sweep over
per-heartbeat loss probability are in `simulation_report.md` and
`sim/deadman_robustness_sim.py` (SIMULATED, not a measurement).

## 5. Limitations

- All "independent reproduction" here re-derives numbers from the same raw
  CSVs the original scripts used; it is a check against calculation error
  in the scripts, not an independent physical re-measurement.
- Only two metrics (deadman_panic latency, Wilson CI for fault recovery)
  were spot-checked by hand in this task; the remaining rows of
  `summary.md`/`section5_stats.md` were checked only by rerunning the
  existing script end to end (Section 2.3 above), not re-derived with
  separate code.
- The `latency.csv` quantisation caveats, autocorrelation in `resources.csv`,
  and GPS resolution limits documented in `tools/eval/README.md` and
  `section5_stats.md` all still apply; this report does not relax any of
  them.
