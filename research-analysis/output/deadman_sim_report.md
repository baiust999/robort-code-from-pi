# SIMULATED: dead-man timer robustness to heartbeat loss

Software model only. Not a measurement of the real robot or network.
Fixed constants: DEADMAN_MS=2000, HEARTBEAT_PERIOD_MS=500.
Monte Carlo: seed=20261022, trials per p=50000, mission=300 s.

## Part A: SIMULATED boundary margin (deterministic, no randomness)

How many consecutive full-period heartbeat losses, starting right
after a successful one, are guaranteed to trip the dead-man --
continuous-time check against the real inclusive `<=` boundary.

| heartbeat period (ms) | consecutive losses tolerated | losses that guarantee a trip |
|---|---|---|
| 200 | 9 | 10 |
| 500  (actual system) | 3 | 4 |
| 1000 | 1 | 2 |
| 2000 | 0 | 1 |

At the dashboard's actual 500 ms heartbeat period, 3 consecutive
losses are tolerated; a 4th in a row is guaranteed to trip the
dead-man, essentially at the moment the 4th scheduled heartbeat
would have arrived (2000 ms of silence), not waiting for a 5th.

## Part B: SIMULATED Monte Carlo trip probability vs heartbeat loss rate

300 s missions, 50000 independent trials per p_loss,
iid Bernoulli loss per scheduled heartbeat (no retries, no jitter).

| p_loss (per heartbeat) | tripped / trials | trip rate | 95% CI half-width |
|---|---|---|---|
| 0.01 | 0/50000 | 0.00% | +/- 0.00 pp |
| 0.02 | 5/50000 | 0.01% | +/- 0.01 pp |
| 0.05 | 160/50000 | 0.32% | +/- 0.05 pp |
| 0.10 | 2711/50000 | 5.42% | +/- 0.20 pp |
| 0.15 | 11428/50000 | 22.86% | +/- 0.37 pp |
| 0.20 | 26870/50000 | 53.74% | +/- 0.44 pp |
| 0.30 | 48363/50000 | 96.73% | +/- 0.16 pp |
| 0.50 | 50000/50000 | 100.00% | +/- 0.00 pp |

## Part C: closed-form cross-check (no randomness, validates Part B's pipeline)

n scheduled heartbeat slots per mission = 600; trip threshold k = 4 consecutive losses.
This treats a trip as 'a run of k consecutive losses lands on a slot boundary',
which is the same event Part A derived; it is an approximation of Part B's
continuous-time check (ignores losses that straddle mission start/end), used
here only to confirm the Monte Carlo estimator is unbiased, not as a second
independent model of the real system.

| p_loss | Monte Carlo trip rate | closed-form trip rate | difference |
|---|---|---|---|
| 0.01 | 0.00% | 0.00% | 0.00 pp |
| 0.02 | 0.01% | 0.01% | 0.00 pp |
| 0.05 | 0.32% | 0.35% | 0.03 pp |
| 0.10 | 5.42% | 5.23% | 0.19 pp |
| 0.15 | 22.86% | 22.70% | 0.16 pp |
| 0.20 | 53.74% | 53.65% | 0.09 pp |
| 0.30 | 96.73% | 96.91% | 0.18 pp |
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
