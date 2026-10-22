# Evidence-to-claim matrix

Maps the paper's main claims to the class of evidence that actually
supports them, incorporating what this task confirmed, added, or flagged.
`research paper/section5_results.md` already carries a detailed, per-metric
version of this (Table 5.0 and its Section 5.10 summary); this file works
at the claim level and folds in this task's new findings. Evidence classes
used, matching the task's own vocabulary:

- **HISTORICAL-TEST** -- the 2026-10-08 116-test record, quoted not rerun.
- **FRESH-TEST** -- rerun or newly written in this task, executed and passing.
- **NATIVE-FIRMWARE-TEST** -- this task's new evidence class: the real, unmodified `arduino/*.cpp` sources compiled and run natively against a host Arduino-API stub, no board, stronger than a test against `MockArduino` but still not hardware-in-the-loop.
- **MEASURED** -- a real instrument reading on the assembled robot, logged in `tools/eval/results/`.
- **CALCULATED** -- arithmetic/statistics derived from MEASURED or logged data.
- **SIMULATED** -- a software model with no physical measurement behind it.
- **PENDING** -- no evidence exists yet; the paper itself marks this.
- **CONTRADICTED / VERIFICATION REQUIRED** -- existing data conflicts with the robot's own logs.

| Claim | Evidence class | What supports it | This task's contribution |
|---|---|---|---|
| The dead-man timer stops the robot if commands stop arriving | MEASURED + CALCULATED + FRESH-TEST + NATIVE-FIRMWARE-TEST | `latency.csv` deadman_trip/deadman_panic (30 trials); P1-log decomposition in `section5_stats.md` (max 2042 ms); `pi/tests/test_mock_deadman.py` (historical) | Independently reproduced the latency CI by hand (Section 2.1, `calculation_report.md`); added `test_deadman_boundaries.py` proving the exact 2000 ms boundary (for `MockArduino`) and that pan/tilt/status cannot mask an expired drive command *in the mock, at the time*. A later pass compiled the real `arduino/*.cpp` natively and found the opposite was true of the real firmware on both points: it trips at, not after, exactly 2000 ms, and pan/tilt/status *do* re-arm it (`research-analysis/native/`, 10/10 native tests passed). The dead-man still measurably stops the robot either way (Table 5.2b); only the boundary-direction and arming-set details changed, and only the mock's version of them was previously claimed. **Addendum, 2026-10-22, later same day: `pi/common/mock_hardware.py`/`protocol.py` have since been patched (reviewed diff, applied) to match the firmware on both points; `test_deadman_boundaries.py` was updated to match; 121/121 `pi/tests/` and 25/25 `research-analysis/tests/` pass post-patch. See `research-analysis/proposed_patch/` and `software_verification_results.md`'s addendum.** |
| The dead-man window tolerates some heartbeat loss before tripping | SIMULATED | none existed before this task | New: `simulation_report.md` / `sim/deadman_robustness_sim.py` -- derives a 3-consecutive-loss margin at the real 500 ms heartbeat period from verified constants, with a Monte Carlo sensitivity sweep. This is SIMULATED, not a network measurement; Section 5.3 (Wi-Fi) is still PENDING |
| Server-side command validation rejects malformed/out-of-range input | HISTORICAL-TEST + FRESH-TEST | `pi/tests/test_command_validator.py` (13 tests, far-out-of-range values) | New: `test_command_validator_boundaries.py` (8 tests) proves no off-by-one at the exact PWM/angle/sequence boundaries, which the far-out-of-range tests could not distinguish from a correct implementation |
| 116 (now 121) automated unit tests pass, proving the software logic | HISTORICAL-TEST + FRESH-TEST | `docs/TEST_REPORT.md` (116, 2026-10-08) | Reproduced fresh on 2026-10-22: 121 passed, 0 failed, in the full-dependency venv (`test_inventory.md` Section 3). Explained, with an exact mechanism, why an incomplete venv (`pi/.venv`) previously showed 86 passed/7 errors -- missing `av`/`aiortc`, not a regression (`test_inventory.md` Section 4) |
| The watchdog restores a crashed process automatically | MEASURED + CALCULATED | `faults.csv`, 30/30 recoveries, Wilson 95% CI | Independently recomputed the Wilson CI by hand from the Wilson (1927) formula, matching `section5_stats.md` exactly (`calculation_report.md` Section 2.2) |
| Resource use stays bounded under driving + media load | MEASURED + CALCULATED | `resources.csv`, 3608 rows, batch-means CIs in `section5_stats.md` | Reran `section5_stats.py` end to end against the frozen inputs; confirmed byte-identical output for every resource-related block (`calculation_report.md` Section 2.3) |
| The ultrasonic sensor is accurate to within measurement noise | CONTRADICTED / VERIFICATION REQUIRED | the paper already marks E10 `[VERIFICATION REQUIRED]` because the entered distances never appear in `telemetry.log` | This task adds an independent, distinct reason: all 50 `ultrasonic.csv` rows have `reading_cm == true_cm` exactly, which is not physically plausible as independent sensor readings (`calculation_report.md` Section 3). Two separate problems now point the same way: this CSV cannot be cited as sensor-accuracy evidence under any framing |
| The temperature/humidity sensor is accurate to within +/-0 deg C | not currently flagged in the paper as a data-quality concern | `thermal.csv`, 5 rows, `error_c == 0.0` on every row | New finding, not previously documented: the same reading-equals-reference pattern appears in `thermal.csv`. The paper's Section 5.10 currently calls E11 "corroborated by the robot's own logs" for the sensor *values* (which is true per `section5_stats.md`'s E11 cross-check) but does not note that the *error* figures (0.0 deg C on every trial) look like the same non-independent-entry problem as E10, not sensor accuracy. Recommended for `[VERIFICATION REQUIRED]` framing (see `paper_improvement_plan.md`) |
| The emergency stop brings the robot to rest over a short, speed-bounded distance | CONTRADICTED | already marked `[VERIFICATION REQUIRED]` in the paper (Table 5.4); kinematic model predicts cm-scale stopping, measured distances are 1-2 orders of magnitude larger | Not revisited in this task beyond confirming the existing flag is still accurate against the current `estop.csv` |
| True end-to-end control latency, physical stop time, streaming delay, Wi-Fi range, field trial, usability | PENDING | none | Not addressed: all require physical trials this software-only task is not authorized to run. Confirmed the `[PENDING MEASUREMENT]` tags are still accurate and that no fabricated data has been substituted for them anywhere in the repository |
| The bibliography supports the claims it is cited for | mixed VERIFIED/UNVERIFIED | `references.bib` inline comments (prior session's claims) | New: independent re-verification of the 19 entries not already in `citation.md`'s master table, via Crossref/DOI and vendor-page checks, run as a background task in parallel with the rest of this audit. See `reference_verification.md` for the itemised result (added once that check completed) |

## What changed in this task's picture vs. the paper's existing Table 5.0 / Section 5.10

- Nothing in `research paper/` was edited. This matrix is additive.
- No previously-PENDING item became MEASURED; this task did not run any
  physical trial.
- No previously-MEASURED item was invalidated outright; E10 was already
  correctly flagged, and this task's thermal-sensor finding is a new
  concern the paper does not yet carry, not a reversal of an existing one.
- Two new evidence classes now exist that the paper's Table 5.0 does not
  yet have rows for: FRESH-TEST (the 121-test rerun and the 17 new
  boundary tests) and SIMULATED (the dead-man heartbeat-loss model). Both
  are software-verification/analytical evidence, not physical measurement,
  and should not be presented as such if folded into the manuscript.
- A third, added in a later pass the same day: NATIVE-FIRMWARE-TEST (the
  10 tests compiled and run against the real `arduino/*.cpp` sources). This
  one is not purely additive: it corrects two specific claims the earlier
  FRESH-TEST pass made about "the" dead-man boundary and arming behaviour,
  which turn out to describe `pi/common/mock_hardware.py` only. See the
  dead-man row above and `research-analysis/software_verification_results.md`'s
  2026-10-22 addendum for the exact correction.
