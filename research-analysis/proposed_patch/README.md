# Proposed dead-man mock patch -- NOT APPLIED

This directory holds a proposed, reviewed-but-not-applied fix for the two
dead-man discrepancies between `pi/common/mock_hardware.py`/`protocol.py`
and the real Arduino firmware (`arduino/arduino.ino`,
`arduino/command_parser.cpp`), first reported in
`research-analysis/software_verification_results.md`'s 2026-10-22 addendum
and re-confirmed against the current source in this task.

**Nothing under `pi/` was changed by this task.** Everything here is either
read-only against `pi/common` (imported, never edited) or an isolated copy
that lives only in this directory.

## Files

- `PATCH_production.diff` -- the exact unified diff that would apply the fix
  to `pi/common/protocol.py` and `pi/common/mock_hardware.py` (two small,
  targeted changes; no refactoring). **Not applied.** Needs explicit
  approval, since both files are imported by the live `robot-watchdog`
  service when `MOCK_HARDWARE=1`.
- `PATCH_existing_tests_update.diff` -- the diff that would update the 3
  assertions in `research-analysis/tests/test_deadman_boundaries.py` that
  currently assert the *unpatched* mock's behaviour (exact-boundary-alive,
  pan/tilt/status-do-not-rearm) and would need to flip once the production
  patch above is applied. This file is not imported by the live service, so
  it is lower-risk, but it is still a proposal, not applied, per the
  "show me the diff first" instruction.
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

## What was actually run (this task)

1. `research-analysis/tests/test_deadman_patch_isolated.py` -- 8 new tests
   against `PatchedMockArduino` (the isolated copy). **8/8 passed.** Covers
   both corrections, both at the exact boundary and the
   immediately-before-boundary instant.
2. `run_regression_check.py` against the real `pi/tests/` suite, patched
   in-memory only. **121/121 passed** -- the proposed patch does not break
   any existing historical test, because none of them assert the specific
   boundary-equality or pan/tilt/status-exclusion behaviour that changes.
3. `pytest research-analysis/tests/` (the full existing + new tree,
   unpatched reality) -- **25/25 passed**, confirming this task did not
   break anything already in `research-analysis/`.

## What would still need to happen before applying the production diff

- Your explicit approval (this task does not apply it).
- Decide whether to also apply `PATCH_existing_tests_update.diff` in the
  same change (recommended, so `research-analysis/tests/` keeps documenting
  reality instead of the superseded mock behaviour).
- No change to `arduino/*.cpp` is proposed or needed: the firmware is the
  reference; only the mock moves to match it.
