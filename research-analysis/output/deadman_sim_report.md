# SIMULATED: dead-man timer robustness to heartbeat loss

Software model only. Not a measurement of the real robot or network.
Fixed constants: DEADMAN_MS=2000, HEARTBEAT_PERIOD_MS=500.
Monte Carlo: seed=20261022, trials per p=50000, mission=300 s.

## Part A: SIMULATED boundary margin (deterministic, no randomness)

How many consecutive full-period heartbeat losses, starting right
after a successful one, are guaranteed to trip the dead-man --
continuous-time check against the firmware's inclusive `>=` trip boundary
(zero transit jitter; a heartbeat due exactly at 2000 ms is too late).

| heartbeat period (ms) | consecutive losses tolerated | losses that guarantee a trip |
|---|---|---|
| 200 | 8 | 9 |
| 500  (actual system) | 2 | 3 |
| 1000 | 0 | 1 |
| 2000 | -1 | 0 |

At the dashboard's configured 500 ms heartbeat period, 2 consecutive
losses are tolerated; a 3rd in a row leaves 2000 ms of silence when the
4th heartbeat is due, and the firmware trips at >= 2000 ms.

## Part B: SIMULATED Monte Carlo trip probability vs heartbeat loss rate

300 s missions, 50000 independent trials per p_loss,
iid Bernoulli loss per scheduled heartbeat (no retries, no jitter).

| p_loss (per heartbeat) | tripped / trials | trip rate | 95% CI half-width |
|---|---|---|---|
| 0.01 | 25/50000 | 0.05% | +/- 0.02 pp |
| 0.02 | 235/50000 | 0.47% | +/- 0.06 pp |
| 0.05 | 3422/50000 | 6.84% | +/- 0.22 pp |
| 0.10 | 21020/50000 | 42.04% | +/- 0.43 pp |
| 0.15 | 41172/50000 | 82.34% | +/- 0.33 pp |
| 0.20 | 48972/50000 | 97.94% | +/- 0.12 pp |
| 0.30 | 49999/50000 | 100.00% | +/- 0.01 pp |
| 0.50 | 50000/50000 | 100.00% | +/- 0.00 pp |

## Part C: closed-form cross-check (no randomness, validates Part B's pipeline)

n scheduled heartbeat slots per mission = 600; trip threshold k = 3 consecutive losses.
This treats a trip as 'a run of k consecutive losses lands on a slot boundary',
which is the same event Part A derived; it is an approximation of Part B's
continuous-time check (ignores losses that straddle mission start/end), used
here only to confirm the Monte Carlo estimator is unbiased, not as a second
independent model of the real system.

| p_loss | Monte Carlo trip rate | closed-form trip rate | difference |
|---|---|---|---|
| 0.01 | 0.05% | 0.06% | 0.01 pp |
| 0.02 | 0.47% | 0.47% | 0.00 pp |
| 0.05 | 6.84% | 6.86% | 0.01 pp |
| 0.10 | 42.04% | 41.73% | 0.31 pp |
| 0.15 | 82.34% | 82.33% | 0.01 pp |
| 0.20 | 97.94% | 98.01% | 0.07 pp |
| 0.30 | 100.00% | 100.00% | 0.00 pp |
| 0.50 | 100.00% | 100.00% | 0.00 pp |

Agreement within the Monte Carlo's own 95% CI half-width at every p_loss
confirms the simulator has no systematic bias relative to the closed form.

## Limitations

- p_loss is an assumed sweep, not a measured Wi-Fi loss distribution:
  Section 5.3 (network range/performance) has no [PENDING MEASUREMENT]
  data yet. Do not read any row above as a real-world loss rate.
- Losses are modelled as iid Bernoulli per heartbeat slot. Real Wi-Fi
  loss is bursty (correlated), which this model does not capture; a
  burst-loss (e.g. Gilbert-Elliott) model would trip sooner than this
  iid model at the same mean loss rate.
- Heartbeat transit delay/jitter is not modelled; only binary loss.
- This script never touches the robot, the venv under test, or any
  measured CSV; it imports nothing from pi/ and uses only the two
  cited constants, copied here as literals, not live-imported, so a
  firmware change would not silently invalidate this report.
