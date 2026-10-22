# Dead-man mock patch -- APPLIED 2026-10-22

This directory holds the proposed fix for the two dead-man discrepancies
between `pi/common/mock_hardware.py`/`protocol.py` and the real Arduino
firmware (`arduino/arduino.ino`, `arduino/command_parser.cpp`), first
reported in `research-analysis/software_verification_results.md`'s
2026-10-22 addendum and re-confirmed against the current source in this
task. The diffs below were shown and explained in full, line by line,
before any change was made, and the patch was applied only after explicit
approval.

**Status: APPLIED.** `pi/common/protocol.py` and `pi/common/mock_hardware.py`
now contain exactly the two changes in `PATCH_production.diff` (it is kept
here as the record of what was reviewed and applied, not as an outstanding
proposal). `research-analysis/tests/test_deadman_boundaries.py` now
contains exactly the update in `PATCH_existing_tests_update.diff`. Verified
post-apply: 121/121 `pi/tests/` pass, 25/25 `research-analysis/tests/`
pass. No file under `arduino/`, `pi/p1_control/`, `pi/p2_media/`,
`pi/p3_watchdog/`, `dashboard/`, `deploy/`, or any CSV was touched; nothing
was committed or pushed; no service was restarted; no hardware was
operated. The live `robot-watchdog` unit sets `Environment=MOCK_HARDWARE=0`
(confirmed via `systemctl cat`), so this change has no effect on the
deployed robot.

## Files

- `PATCH_production.diff` -- the exact unified diff that was applied to
  `pi/common/protocol.py` and `pi/common/mock_hardware.py` (two small,
  targeted changes; no refactoring), kept here as the reviewed record of
  what changed.
- `PATCH_existing_tests_update.diff` -- the diff that was applied to the 3
  assertions in `research-analysis/tests/test_deadman_boundaries.py` that
  previously asserted the *pre-patch* mock's behaviour
  (exact-boundary-alive, pan/tilt/status-do-not-rearm), kept here as the
  reviewed record of what changed.
- `mock_hardware_patched.py` -- a `PatchedMockArduino` subclass of the real,
  unmodified `MockArduino`, overriding only the two targeted methods. Lives
  here, imported by nothing outside this directory and
  `research-analysis/tests/test_deadman_patch_isolated.py`.
- `run_regression_check.py` -- monkeypatches the two behaviours onto the
  imported `pi.common` module objects in-memory (never touching the files
  on disk) and runs the full `pi/tests/` suite against the patched objects,
  to check whether the proposed patch would break any of the 121 protected,
  historical tests. Output is reported in the task summary, not re-run
  automatically; re-run with
  `/home/pi/robot/venv/bin/python research-analysis/proposed_patch/run_regression_check.py`.

## What was run, before and after applying

**Before applying (verification that the patch would be safe):**

1. `research-analysis/tests/test_deadman_patch_isolated.py` -- 8 new tests
   against `PatchedMockArduino` (an isolated copy, not the real mock).
   **8/8 passed.** Covers both corrections, both at the exact boundary and
   the immediately-before-boundary instant.
2. `run_regression_check.py` against the real `pi/tests/` suite, patched
   in-memory only (nothing written to disk). **121/121 passed** -- the
   patch would not break any existing historical test, because none of
   them assert the specific boundary-equality or pan/tilt/status-exclusion
   behaviour that changes.
3. `pytest research-analysis/tests/` (the full existing + new tree,
   unpatched reality) -- **25/25 passed**, confirming the task up to that
   point had not broken anything already in `research-analysis/`.

**After applying both diffs for real (same two checks, now against the
actually-modified files):**

4. `cd pi && pytest` (the real, protected 121-test suite, against the now
   genuinely patched `pi/common/`) -- **121/121 passed.**
5. `pytest research-analysis/tests/` (25 tests, including the 3 renamed,
   flipped tests in `test_deadman_boundaries.py`) -- **25/25 passed.**

No change was needed to `arduino/*.cpp`: the firmware is the reference;
only the mock moved to match it.
