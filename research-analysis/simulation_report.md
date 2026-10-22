# Simulation report

All results in this file are SIMULATED / SYNTHETIC. None of them is a
measurement of the real robot, the real Wi-Fi link, or any physical
quantity. Every number here traces either to a software model built in
`research-analysis/sim/`, or to two already-verified source constants cited
by file and line. Nothing here may be copied into the paper's Results
section without the word SIMULATED attached.

## 1. Research question

The paper's Section 5.1 reports a measured dead-man trip time
(`deadman_trip`/`deadman_panic` in `latency.csv`, ~2.0-2.4 s) from 30 trials
on the assembled robot. That measurement answers "how long does the dead-man
take to trip once commands stop arriving," on a link that was not itself
losing packets during the trial. It does not answer: how robust is the
2000 ms dead-man window to a Wi-Fi link that is actually dropping some
fraction of heartbeats? Section 5.3 (Wi-Fi range/performance) has no
measured data yet (`[PENDING MEASUREMENT]` / "Not yet measured" in
`tools/eval/results/summary.md`), so this question cannot be answered from
existing measurements. It can be answered, with explicit assumptions, by a
software model of the two relevant constants.

## 2. Model and assumptions

Script: `research-analysis/sim/deadman_robustness_sim.py`. Inputs are two
literal constants, copied (not live-imported) so a later firmware change
cannot silently invalidate this report:

- `DEADMAN_MS = 2000` -- `pi/common/protocol.py:67`
- `HEARTBEAT_PERIOD_MS = 500` -- `dashboard/src/lib/protocol.ts:11`

Three independent parts:

- **Part A (deterministic boundary analysis).** For a given heartbeat
  period, the minimum number of consecutive lost heartbeats that is
  guaranteed to trip the dead-man, respecting the real, inclusive `<=`
  boundary in `MockArduino._check_deadman` (elapsed == DEADMAN_MS is still
  alive).
- **Part B (Monte Carlo).** 300 s simulated missions; each scheduled
  heartbeat is independently lost with probability `p_loss` (iid Bernoulli,
  no retries, no jitter); trip rate measured over many missions per
  `p_loss`. Seed = 20261022 (date-coded, not tuned for a result), 50,000
  trials per `p_loss` value.
- **Part C (closed-form check).** An independent, non-random recursion for
  "probability of a run of >= k consecutive losses in n iid Bernoulli(p)
  trials," used only to confirm Part B's estimator is unbiased.

Assumptions and their status:

- Heartbeat loss is modelled as independent per heartbeat (no correlation
  between consecutive losses). Real Wi-Fi loss is typically bursty; this
  model understates trip probability at a given mean loss rate relative to
  a burst-loss (e.g. Gilbert-Elliott) model. Flagged as a limitation, not
  corrected for, since no measured burst statistics exist yet either.
- `p_loss` itself is an assumed sweep (0.01 to 0.5), not fit to any
  measurement. It exists to show the shape of the sensitivity curve, not to
  claim the real link's loss rate.
- Transit delay/jitter on a successful heartbeat is not modelled, only
  binary loss.

## 3. A bug this process caught (reported for transparency)

The first version of the Part A boundary function used the condition
`elapsed <= deadman_ms` to decide when to stop counting losses, which
silently required one extra consecutive loss beyond the real boundary
(it computed that 4 losses, not 3, are tolerated at the real 500 ms
heartbeat period). This produced a Part B vs. Part C disagreement of
roughly 10x at `p_loss = 0.10` (5.42% Monte Carlo vs. 0.54% closed-form) --
consistent with needing a run one loss longer at p is approx 0.1, which
cross-checks as `1/p`. The fix changes the stopping condition to
`elapsed < deadman_ms` (trip is guaranteed once `k * period >= deadman_ms`,
since nothing can arrive between that instant and the next scheduled
heartbeat to save it). After the fix, Part B and Part C agree within Part
B's own 95% CI half-width at every `p_loss` tested (see table below). This
is exactly the kind of error boundary/cross-validation analysis is meant to
catch, and it is reported here rather than silently corrected, per the
project's integrity rules.

## 4. Results

### 4.1 Boundary margin by heartbeat period (Part A)

| heartbeat period (ms) | consecutive losses tolerated | losses that guarantee a trip |
|---|---|---|
| 200 | 9 | 10 |
| 500 (actual system) | 3 | 4 |
| 1000 | 1 | 2 |
| 2000 | 0 | 1 |

At the real 500 ms heartbeat period, the dead-man tolerates 3 consecutive
lost heartbeats; a 4th in a row guarantees a trip, occurring an instant
after the 4th heartbeat's scheduled time (2000 ms of silence) -- it does
not wait to see whether a 5th heartbeat would have arrived.

### 4.2 Trip probability vs. per-heartbeat loss rate (Part B, SIMULATED)

300 s missions, 50,000 trials per `p_loss`, seed 20261022:

| p_loss | trip rate | 95% CI half-width |
|---|---|---|
| 0.01 | 0.00% | +/- 0.00 pp |
| 0.02 | 0.01% | +/- 0.01 pp |
| 0.05 | 0.32% | +/- 0.05 pp |
| 0.10 | 5.42% | +/- 0.20 pp |
| 0.15 | 22.86% | +/- 0.37 pp |
| 0.20 | 53.74% | +/- 0.44 pp |
| 0.30 | 96.73% | +/- 0.16 pp |
| 0.50 | 100.00% | +/- 0.00 pp |

Full table including the Part C cross-check is in
`research-analysis/output/deadman_sim_report.md` (machine-generated by the
script; agreement between Part B and Part C is within 0.2 percentage points
at every `p_loss` value after the fix in Section 3).

### 4.3 Reading this result

The curve is steep: a per-heartbeat loss probability as low as 10% already
produces a mission-level trip probability around 5% over 5 minutes, and by
20% loss the mission is more likely to trip than not. This is a property of
requiring 4 independent consecutive losses (probability scales roughly with
`p^4` at small `p`, which is why the curve is so steep), not of any
particular flaw -- it is the direct, correctly-functioning consequence of
the 500 ms/2000 ms ratio chosen in the design. It also means that if a
future hardware or firmware change increased the effective heartbeat period
(e.g. by batching or an added processing delay), the margin shrinks fast:
dropping to a 1000 ms effective period leaves only 1 consecutive loss of
tolerance (Section 4.1).

## 5. Limitations (restated from the script, Phase 5 requirement)

- Not a Wi-Fi measurement. Section 5.3 is still `[PENDING MEASUREMENT]`;
  nothing here estimates the real robot's loss rate at any real distance.
- iid loss model only; real wireless loss is typically bursty, which would
  trip the dead-man sooner at the same mean loss rate than this model
  predicts.
- No jitter/delay model, only binary loss per heartbeat slot.
- Single mission length (300 s) swept; not re-run at other mission
  durations in this pass.
- Does not model the dashboard-to-P1 WebSocket path's own latency or the
  P1-to-Arduino serial leg separately; it treats "heartbeat received by the
  dead-man timer" as the event, which is what `DEADMAN_MS` itself gates on.

## 6. What was NOT simulated, and why

- No motor/physical dynamics model (stopping distance, wheel slip): the
  paper's `estop.csv` already has real measured stopping distances; a
  physics simulation would not improve on measured data and risks being
  mistaken for it.
- No synthetic field-trial or usability-study data: explicitly forbidden by
  the task (never manufacture human-subject or field-trial outcomes).
- No GPS-drift physical simulation: `gpsdrift.py` and the existing GPS
  analysis in `section5_stats.md` already characterise the real logged
  drift; a synthetic GPS noise model would not add information the
  real log does not already provide, and risks being confused with it.
