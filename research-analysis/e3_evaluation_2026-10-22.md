# E3 (emergency-stop stopping distance) evaluation, 2026-10-22

Status at close of this session: **E3 is INCOMPLETE.** No new physical
stopping-distance measurement was obtained. This file documents what was
checked, what was run, and what a reader would need before Table 5.4 could
be marked verified. It is a supporting analysis document, not part of the
manuscript; `research paper/section5_results.md` is the manuscript, and it
is updated only where this file's evidence supports a specific added
sentence (see "Manuscript change" at the end).

## 1. What already existed (verified unchanged this session)

- `tools/eval/estop_assist.py` -- the real protocol. Drives forward over the
  control WebSocket, operator presses Enter at the line-crossing instant
  (sends `stop_all`, the same message the dashboard EMERGENCY STOP button
  sends), operator tape-measures and types the distance. This is the only
  script in the repository that can produce a real `distance_cm` value,
  because it is the only one with a human closing the measurement loop.
- `tools/eval/results/estop.csv` -- 23 rows, 2026-10-21, unchanged this
  session (verified: still 24 lines including header, same content as the
  2026-10-22 data audit left it). Independently recomputed in this session
  and confirmed to match the manuscript's Table 5.4 exactly (n, mean, SD,
  min, max per PWM level; see section 2 below).
- `research paper/section5_results.md` Section 5.1 already carries a full,
  dated audit of this data: Table 5.4, a kinematic contradiction analysis
  (measured distances exceed the firmware's documented ramp-stop bound by
  one to two orders of magnitude at all three speeds), a
  `[VERIFICATION REQUIRED]` tag, and a `[PENDING MEASUREMENT: E3 repeat]`
  protocol note calling for 20 trials per speed with `estop_assist.py`. None
  of this needed correction; it is reproduced in section 2 for completeness.

## 2. Real data, independently reverified

### 2.1 `estop.csv` (tape-measured distance; unchanged)

| PWM | N | Mean cm | SD | Min | Max | 95% CI of mean |
|---|---|---|---|---|---|---|
| 60 | 7 | 42.7 | 6.8 | 34 | 54 | 36.1 to 49.3 |
| 120 | 9 | 75.9 | 18.7 | 34 | 92 | 61.2 to 90.6 |
| 180 | 7 | 91.3 | 6.7 | 78 | 98 | 84.8 to 97.7 |

Matches `research paper/section5_results.md` Table 5.4 (small CI differences
are rounding of the Student-t critical value, not a data difference).
`[VERIFICATION REQUIRED]` stands: no `F60` command exists in any retained
`p1_events.log` window for these rows, and all three speeds' distances
contradict the firmware's documented ramp-stop kinematics by 1-2 orders of
magnitude (full derivation already in the manuscript; not repeated here).

### 2.2 `estop_auto.csv` (new this session; command/firmware timing only)

Produced by `tools/eval/estop_auto.py`, a script built this session
specifically because it cannot fabricate a distance: every row's
`distance_cm` field is the literal string `PENDING_MEASUREMENT`. What it
does measure, for real, is the software command path: it sends the actual
forward-drive and `stop_all` messages over the real control WebSocket and
logs this process's own send timestamps plus the firmware's
telemetry-reported ARMED/DRIVING state transitions.

15 trials (5 per PWM level, forward only, 1.0 s drive each) were run with
the robot physically on the floor, the operator present and watching, under
an explicit `--confirm FLOOR_CLEAR_SUPERVISED` safety gate plus a typed
confirmation before each batch. Every trial's `cmd_send_ts`/`stop_send_ts`
was independently cross-checked against `var/log/p1_events.log` (`wire=F60`
/ `wire=F120` / `wire=F180` and `wire=S` entries) and matched to the
millisecond in all 15 cases; zero trials were flagged with a `notes` entry.

| PWM | N | cmd-to-driving mean (s) | SD | stop-to-ready mean (s) | SD |
|---|---|---|---|---|---|
| 60 | 5 | 0.531 | 0.136 | 0.324 | 0.135 |
| 120 | 5 | 0.475 | 0.020 | 0.266 | 0.022 |
| 180 | 5 | 0.575 | 0.234 | 0.248 | 0.037 |

These are telemetry-broadcast latencies (the 200 ms P1 rebroadcast cadence
plus jitter), not a measurement of physical motor response or stopping
distance -- there is no tachometer or encoder reading used here. Their only
value is confirming the command/stop path itself functions correctly, by
real log correlation, at all three PWM levels.

### 2.3 `bench_motor.csv` (same timing method; floor-contact caveat applies)

60 rows (PWM 60/120/180 x forward/reverse/left/right, 5 reps each),
produced by `tools/eval/bench_motor.py` earlier in this session. Same
firmware-timing method as 2.2, same log-correlation verification, same
`distance_cm`-free design (this script predates `estop_auto.py` and has no
distance column at all).

**Caveat (see `tools/eval/README.md`, "Data caveat, 2026-10-22"):** this
script's safety premise ("robot securely elevated, wheels clear of any
surface") was stated by the operator but was false -- the robot was
actually on the floor for all 60 trials. No collision or damage resulted.
The command-timing data itself remains internally consistent and log
-correlated; only the "never left the ground" framing it was originally
logged under is void. These rows carry no distance measurement regardless
of surface contact, so this caveat does not newly invalidate anything with
respect to E3 -- the rows were never usable as stopping-distance evidence
either way -- it only means the dataset's documented *conditions* were
wrong, which is now corrected in the dataset's own README entry and in
project memory for future sessions.

Pooled per PWM (across all 4 directions, n=20 each):

| PWM | N | cmd->driving mean (s) | SD | stop->ready mean (s) | SD |
|---|---|---|---|---|---|
| 60 | 20 | 0.520 | 0.149 | 0.319 | 0.156 |
| 120 | 20 | 0.467 | 0.091 | 0.362 | 0.189 |
| 180 | 20 | 0.506 | 0.104 | 0.278 | 0.062 |

## 3. Simulated illustrative dataset (SIMULATED -- not real)

Because the real distance data (2.1) is insufficient to support any
stopping-distance claim (contradicted by the firmware kinematics and by the
missing `F60` log entries), a separate, explicitly labeled simulated
dataset was generated to give the size of that contradiction a concrete,
reproducible number instead of a prose "one to two orders of magnitude."

- Script: `research-analysis/sim/estop_distance_sim.py`
- Raw per-trial output (every row and the header both carry a `SIMULATED`
  tag): `research-analysis/sim/output/estop_distance_SIMULATED.csv`
  (3000 rows, 1000 per PWM level)
- Aggregate report: `research-analysis/output/estop_sim_report.md`

Model: `distance_cm = v(PWM) x 100 x (ramp_time_s(PWM) + latency_s)`, where
`v(PWM)` and `ramp_time_s(PWM)` are the same verified kinematic constants
the manuscript's own Table 5.4 analysis already cites (0.20 m/s no-load
speed at the PWM 180 cap, scaled linearly with PWM; `ceil(PWM/15) x 10 ms`
ramp time from `arduino/config.h`/`arduino/motors.cpp`), and `latency_s` is
drawn from the manuscript's own measured Table 5.1 `motor_stop` distribution
(mean 314 ms, SD 80 ms, n=30) as a generous stand-in for stop-command
-to-halt delay -- note this still excludes human operator reaction time.

| PWM | N | Simulated mean cm | SD | Real Table 5.4 mean cm | Ratio real/simulated |
|---|---|---|---|---|---|
| 60 | 1000 | 2.35 | 0.53 | 42.7 | 18.1x |
| 120 | 1000 | 5.27 | 1.08 | 75.9 | 14.4x |
| 180 | 1000 | 8.69 | 1.66 | 91.3 | 10.5x |

This simulation does not explain the real anomaly and is not offered as
doing so. It exists only to quantify the gap the manuscript already
describes in prose. It must never be read as, or merged with, real E3 data;
the file and column names enforce this (`SIMULATED_NOT_REAL` column,
`distance_cm_simulated` column name distinct from `distance_cm`).

## 4. Data-quality issues (summary)

1. `estop.csv`'s 23 rows: no `F60` in any retained log window; all three
   speeds' distances contradict the firmware ramp-stop kinematics by 1-2
   orders of magnitude; sample sizes (7, 9, 7) are below the 20/speed
   target in Table 3. Already flagged `[VERIFICATION REQUIRED]` in the
   manuscript; unchanged by this session.
2. `estop_auto.csv` and `bench_motor.csv`: real, log-verified command
   timing, zero distance information by design. Cannot support Table 5.4
   under any circumstance, with or without the floor-contact caveat.
3. `bench_motor.csv` additionally carries the floor-contact-premise caveat
   above (operator's stated "elevated" premise was false).
4. The simulated dataset (section 3) is synthetic and explicitly
   cannot be used as evidence of the robot's real stopping distance.

## 5. Remaining requirements for E3 completion

Per the manuscript's own `[PENDING MEASUREMENT: E3 repeat]` protocol,
unchanged by this session: run `tools/eval/estop_assist.py` for 20 trials
per speed (60/120/180), operator pressing Enter at the line-crossing
instant and tape-measuring each stop, ideally with synchronized 240 fps
video to also obtain `stop_time_s`. This requires a human physically
present with a tape measure and cannot be automated without fabricating
either the stop-trigger timing or the distance reading -- both of which
this session deliberately avoided doing.

## 6. Manuscript change made

One sentence was added to `research paper/section5_results.md` immediately
after the existing `[PENDING MEASUREMENT: E3 repeat]` paragraph, citing this
file, the real `estop_auto.csv` log-correlated command-path verification,
and the simulated illustrative gap analysis -- all three directly supported
by evidence produced this session. Table 5.4, its `[VERIFICATION REQUIRED]`
status, and the existing kinematic-contradiction analysis were left
untouched: no claim in this document supports changing E3's status to
measured or complete.
