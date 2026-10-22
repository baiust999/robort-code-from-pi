# Final readiness report

## 1. Safety compliance (final check)

```
git status --porcelain=v1 -uall
```
run just before writing this report shows changes only under
`research-analysis/` (new, this task) and the pre-existing, untouched
`promt` file (uploaded by the user before this task started, per project
memory, and not modified here). No file under `arduino/`, `pi/common/`,
`pi/p1_control/`, `pi/p2_media/`, `pi/p3_watchdog/`, `dashboard/`,
`deploy/`, `var/`, any systemd unit, any original CSV in
`tools/eval/results/`, or `docs/TEST_REPORT.md` was created, edited,
renamed, or deleted. No package was installed or upgraded, no service was
restarted or reloaded, no process was killed, no serial device was opened,
no production port was bound, and the Pi was not rebooted. Nothing was
committed or pushed.

## 2. Every command executed in this task that touched the live system in any way

- `systemctl is-active robot-watchdog`, `systemctl list-units ...`,
  `ss -tlnp` -- read-only status queries, confirming the live service was
  running throughout and identifying its port, before any test was run.
- `/home/pi/robot/venv/bin/python -m pytest ...` (collect-only, then full
  run, twice) -- executes the existing and new unit tests in-process.
  Verified beforehand (Section 3, `test_inventory.md`) that no test in
  either suite binds a socket, starts a server, or writes outside a
  per-test temporary `ROBOT_ROOT`. This is the same interpreter the live
  service uses, but running pytest does not touch the running service's
  process, sockets, or files.
- `/home/pi/robot/pi/.venv/bin/python -m pytest ...` -- same, against the
  secondary, incomplete environment, to characterise the historical
  86-pass result precisely.
- `pip list` against both venvs -- read-only.
- All other commands (`find`, `git log`/`git show`/`git status`, `cat`,
  `grep`, `wc`, `diff`, `mkdir` under `research-analysis/`, and the new
  Python scripts under `research-analysis/sim/`) are read-only against the
  repository or write only within `research-analysis/`.

## 3. New files created

```
research-analysis/
  audit_summary.md
  test_inventory.md
  software_verification_results.md
  calculation_report.md
  simulation_report.md
  reference_verification.md
  evidence_to_claim_matrix.md
  paper_improvement_plan.md
  readiness_report.md          (this file)
  tests/
    test_deadman_boundaries.py
    test_command_validator_boundaries.py
    test_command_framing_boundaries.py
  sim/
    deadman_robustness_sim.py
  output/
    rerun_full_venv_2026-10-22.txt
    rerun_pi_venv_incomplete_2026-10-22.txt
    venv_full_pip_list.txt
    pi_venv_incomplete_pip_list.txt
    new_boundary_tests_2026-10-22.txt
    section5_stats_rerun_2026-10-22.md
    deadman_sim_report.md
  scripts/                      (created, left empty -- no additional
                                  reproduction script was judged necessary
                                  beyond the ones above)
```

## 4. Tests not run, and why

- **Hardware checklist (`docs/TEST_REPORT.md` H1-H15)**, **integration
  checklist (I1-I19)**, **network tests (N1-N8)**, **failure/recovery
  hands-on steps requiring physical action (F1, F2, F6, F8, F9, F10)**,
  **field test (Section 8)**: all require operating the physical robot,
  its motors, its radio link over real distance, or a staged human
  scenario. This task's safety rules forbid operating motors,
  communicating with physical hardware, or changing the robot's runtime
  state, so none of these were attempted.
- **`F3`-`F5` automated fault injection (`faultinject.py run`) and the
  `netsweep.py`/`gpsdrift.py` campaigns**: these already have real,
  measured data in `tools/eval/results/` from a prior session; rerunning
  them now would mean killing live supervised processes or driving the
  robot, which this software-only task does not do. The existing measured
  CSVs were read and independently spot-checked instead (Section 2,
  `calculation_report.md`).
- **A usability/SUS study or a field-trial rerun**: explicitly forbidden
  by the task (no fabricated human-subject or field-trial data).

## 5. Historical vs. fresh results, restated once more for clarity

| | Date | Result | Status |
|---|---|---|---|
| Historical unit-test report | 2026-10-08 | 116 passed, 0 failed | Quoted from `docs/TEST_REPORT.md`, not reproduced by rerunning it under that date |
| Fresh rerun, same suite + 5 later tests, full venv | 2026-10-22 | 121 passed, 0 failed | Genuinely executed in this task |
| Rerun, incomplete `pi/.venv`, forced through collection errors | 2026-10-22 | 86 passed, 7 errors (environment-caused) | Genuinely executed in this task, explains (not contradicts) the previously-reported 86/4 figure |
| New boundary unit tests | 2026-10-22 | 17 passed, 0 failed | Newly written and executed in this task |
| Bibliography re-verification | 2026-10-22 | 18/19 VERIFIED, 1 UNVERIFIABLE-BY-DESIGN, 0 mismatches | Independently re-checked in this task against Crossref/primary sources |
| Dead-man heartbeat-loss model | n/a | SIMULATED only | Software model, explicitly not a measurement |

## 6. Measured vs. calculated vs. software-test vs. simulated -- final distinction

- **MEASURED**: every row of `tools/eval/results/*.csv` that this task did
  not flag as a data-quality concern (latency, faults, resources, gas,
  static GPS), all produced before this task, by a prior session, on the
  assembled robot.
- **CALCULATED**: the CIs, Wilson intervals, and batch-means statistics in
  `section5_stats.md`/`summary.md` (prior session's scripts, independently
  reproduced in Section 2 of `calculation_report.md`), and the dead-man
  consecutive-loss margin derived from two verified source constants.
- **SOFTWARE-TEST**: the 121 historical+postdating unit tests
  (`pi/tests/`) and the 17 new boundary tests (`research-analysis/tests/`),
  all executed in this task against `MOCK_HARDWARE` software, proving
  software logic only, never the physical firmware, motors, or radio link.
- **SIMULATED**: only `sim/deadman_robustness_sim.py`'s output. No other
  file in `research-analysis/` contains simulated data presented as
  measured.
- **NOT CLAIMED**: any physical experiment, field trial, usability result,
  or hardware measurement this task did not and could not run.

## 7. Known problems surfaced, not fixed (by design -- this task does not edit the paper)

1. `ultrasonic.csv` (E10) and now also `thermal.csv`'s error column (E11)
   show reading-equals-reference patterns inconsistent with independent
   measurement (Section 3, `calculation_report.md`). E10 was already
   flagged by the paper; E11's error column is a new finding.
2. `test_ice_config.py` (5 tests) exists but is not reflected in
   `docs/TEST_REPORT.md`'s test-file table (Section 2, `test_inventory.md`).
3. `cred2026`'s bib title is missing its subtitle (minor, noted by the
   bibliography check).
4. `section5_stats.py`'s E3 "any retained day" block reads live logs and
   will report a different, larger count each time it is rerun later in
   the same day the robot is driven further -- documented, not a defect,
   but worth noting if that specific row is ever quoted with a "generated
   on" date (Section 2.3, `calculation_report.md`).

## 8. Explicitly not claimed

This task does not claim: that the 121-test rerun constitutes hardware
validation; that the SIMULATED dead-man analysis describes real Wi-Fi
behaviour; that any bibliography entry's claim-to-citation fit was checked
(only the bibliographic record itself); that Q1/IEEE Access acceptance is
guaranteed by any of this; or that any Section 5 `[PENDING MEASUREMENT]`
item has been filled. None of those things happened in this task.
