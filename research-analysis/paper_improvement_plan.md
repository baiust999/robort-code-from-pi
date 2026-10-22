# Paper improvement plan

Proposed additions only. No manuscript file was edited in this task, per
Phase 7's explicit instruction to produce the verified evidence package
first and let it be reviewed before any manuscript change. Each item names
the exact target file/section/table and the evidence that would support it
(all evidence already exists in `research-analysis/`; nothing here asks for
new fabricated content).

## 1. `docs/TEST_REPORT.md`, Section 3

- Add `test_ice_config.py` as a 13th row (5 tests: ICE config without a
  STUN server, with a configured STUN server, no TURN relay in local mode
  x2 parametrised, per-client rate limiting) and update the total from 116
  to 121. Source: `test_inventory.md` Section 2, confirmed by git history
  (`11b6317` postdates the 116-count commit by about 1h40m the same
  morning).
- Add a dated note under the existing Section 3 table: "Rerun 2026-10-22,
  full dependency environment: 121 passed, 0 failed (3.5 s)," citing
  `research-analysis/test_inventory.md` and
  `research-analysis/output/rerun_full_venv_2026-10-22.txt`, so the
  document shows both the original 2026-10-08 result and a reproduced
  later one, rather than silently replacing one with the other.

## 2. `research paper/section3_methodology.md` or wherever test methodology is described

- Add a short paragraph on the two installed Python environments
  (`/home/pi/robot/venv`, used by the live `robot-watchdog.service` and
  carrying `av`/`aiortc`; `pi/.venv`, a secondary environment missing those
  two packages) and state explicitly that all reported test and evaluation
  results in this paper use the former. This forecloses a reviewer
  question about environment provenance. Source: `test_inventory.md`
  Section 4.

## 3. `research paper/section5_results.md` Section 5.6.2 (ultrasonic) -- strengthen, do not change the verdict

- The table is already `[VERIFICATION REQUIRED]`. Add one sentence citing
  the second, independent reason found in this task: `reading_cm ==
  true_cm` on all 50 rows, which is not plausible as independent sensor
  readings and does not even match the error pattern in the harness's own
  usage example in `tools/eval/README.md`. This makes the existing flag
  more defensible to a reviewer who checks the raw CSV, since it gives a
  second, independent line of evidence beyond the telemetry-log
  contradiction already stated.
- Source: `calculation_report.md` Section 3.

## 4. `research paper/section5_results.md` Section 5.6.3 (temperature/humidity, E11) -- new flag, not previously present

- Currently described as "corroborated by the robot's own logs." That is
  true for the sensor *values* (confirmed again by this task's rerun of
  `section5_stats.py`) but Table 5.9/5.10-equivalent for E11's *error*
  column reads 0.0 deg C on every one of 5 trials. Recommend adding
  `[VERIFICATION REQUIRED: error figures, not sensor values]` to that one
  column, with a sentence explaining the same reading-equals-reference
  pattern found in E10, and recommending a repeat where the reference
  thermometer/hygrometer is read and entered independently per trial (the
  way `gas.csv`, which shows real trial-to-trial variation, already was).
- Source: `calculation_report.md` Section 3.

## 5. New subsection, Section 5.1 (Control Latency and Emergency-Stop Response) or a new 5.1.x

- Add a short subsection, clearly headed SIMULATED, presenting the
  dead-man heartbeat-loss sensitivity analysis: the 3-consecutive-loss
  margin at the real 500 ms heartbeat period, and the Monte Carlo trip-
  probability curve, with the explicit caveat that `p_loss` is an assumed
  sweep pending the Section 5.3 Wi-Fi measurement, not a network
  measurement itself. This is new analytical content the paper does not
  currently have anywhere, and it directly strengthens the fail-safe
  argument (RQ2/C2-type claims) without requiring any new physical trial.
- Source: `simulation_report.md`, `sim/deadman_robustness_sim.py`,
  `research-analysis/output/deadman_sim_report.md`.

## 6. `docs/TEST_REPORT.md` Section 3 or a short new appendix -- boundary-test addendum

- Optionally cite the 17 new boundary tests
  (`research-analysis/tests/`) as supplementary software verification,
  explicitly labelled as outside the historical 116/121-test suite (a
  separate research-analysis artifact, not merged into `pi/tests/`), to
  avoid inflating the headline test count while still giving reviewers the
  boundary-condition evidence if asked. Source:
  `software_verification_results.md`.

## 7. `research paper/references.bib` / `citation.md` -- pending the bibliography fork's findings

- If `reference_verification.md` (produced by a parallel background check
  in this task) finds any entry with a real MISMATCH against Crossref
  (not merely UNVERIFIED), that entry needs correcting or removing before
  the next manuscript revision, per the project's own citation-integrity
  rule (`references.bib`'s header comment: "Do not add an entry until it
  has been verified to exist"). This plan item is intentionally left
  pointing at that file rather than pre-judging its outcome.

## 8. Explicitly NOT recommended

- Do not add the ultrasonic/thermal `error_cm`/`error_c` means as
  measured accuracy figures anywhere in the paper while they read
  identically-zero; doing so would overstate validation that does not
  exist.
- Do not present the SIMULATED dead-man heartbeat-loss curve as a
  real-world robustness guarantee, or cite it in the abstract/claims
  summary without the word SIMULATED attached.
- Do not fill Sections 5.2/5.3/5.7/5.8 (streaming, Wi-Fi range, field
  trial, usability) from anything produced in this task: none of that
  evidence exists yet, and this task was not authorized to create it.

## Priority order (highest value for lowest manuscript risk first)

1. Item 1 (TEST_REPORT.md test count correction) -- purely factual, no
   interpretation risk.
2. Item 3 (ultrasonic second flag) -- strengthens an already-correct
   verdict.
3. Item 4 (thermal new flag) -- closes a real gap the paper does not yet
   know about.
4. Item 5 (SIMULATED dead-man subsection) -- adds genuinely new analytical
   content, clearly labelled.
5. Items 2, 6, 7 -- lower urgency, process/documentation hygiene.
