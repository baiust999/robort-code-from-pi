# Software verification results: new tests added by this task

All new tests live under `research-analysis/tests/`, a directory created
by this task (confirmed not to exist before). They import `pi/common` and
`pi/p1_control` read-only (`sys.path` insertion only; no file under `pi/`
was created, edited, or deleted). All 17 pass against the real,
unmodified source. Run with
`/home/pi/robot/venv/bin/python -m pytest research-analysis/tests/ -v`;
full output in `research-analysis/output/new_boundary_tests_2026-10-22.txt`.

These are new unit tests (software logic only, `MOCK_HARDWARE` semantics),
not integration tests, not simulations, and not physical experiments.

## `test_deadman_boundaries.py` (6 tests)

Source under test: `pi/common/mock_hardware.py` (`MockArduino._check_deadman`,
`_handle_line`), `pi/common/protocol.py` (`DEADMAN_MS`,
`DEADMAN_ARMING_COMMANDS`).

| Test | Input | Expected | Actual | Why it is new (not a duplicate of `pi/tests/test_mock_deadman.py`) |
|---|---|---|---|---|
| `test_deadman_alive_at_exactly_deadman_ms` | drive command, then clock advanced by exactly `DEADMAN_MS` (2000 ms), `tick()` | still alive (motors still driving) | PASS | the existing suite only tests `DEADMAN_MS + 1`; the exact boundary (`<=`) was untested |
| `test_deadman_trips_one_ms_past_boundary` | clock advanced `DEADMAN_MS + 1` | tripped, motors stopped | PASS | restates the existing `+1` case with a controlled fake clock instead of direct field mutation, for consistency with the other boundary tests in this file |
| `test_deadman_still_alive_one_ms_before_boundary` | clock advanced `DEADMAN_MS - 1` | still alive | PASS | the `-1` side of the boundary was untested |
| `test_pan_command_does_not_rearm_deadman` | drive command, then repeated `P90` (pan) commands while the clock advances past `DEADMAN_MS` | tripped despite continuous pan activity | PASS (after fixing an off-by-zero in this test's own timing budget, see below) | `CMD_PAN` is deliberately excluded from `DEADMAN_ARMING_COMMANDS` (`protocol.py` lines 42-46); no existing test asserts that panning the camera cannot mask an expired drive command. This is a genuine safety-relevant behaviour with no prior test coverage. |
| `test_tilt_and_status_also_do_not_rearm_deadman` | `T45` and `?` sent before the boundary | tripped once the original window elapses | PASS | same gap as above, for the other two non-arming opcodes |
| `test_heartbeat_at_exact_boundary_rearms` | heartbeat sent at exactly the old boundary, then clock advances `DEADMAN_MS - 1` from there | still alive | PASS | confirms an arming command sent right at the edge correctly resets the window, as a sanity check against the non-arming tests above |

**Process note, reported for transparency:** the first version of
`test_pan_command_does_not_rearm_deadman` advanced the clock by exactly
`DEADMAN_MS` total (5 steps of `DEADMAN_MS/5`) before calling `tick()`,
landing exactly on the inclusive-alive boundary and therefore failing
(the test asserted `tripped is True` when the real, correct behaviour at
that exact instant is "still alive"). This was the test's own arithmetic
error, not a defect in `mock_hardware.py`; it was found immediately by
running the test and fixed by advancing one additional millisecond past
the boundary before the final `tick()`. The corrected test is the one
reported above.

## `test_command_validator_boundaries.py` (8 tests)

Source under test: `pi/p1_control/safety.py` (`CommandValidator`,
`_clamp_int`).

| Test | Boundary checked | Result |
|---|---|---|
| `test_speed_at_max_pwm_is_not_flagged_as_clamped` | `speed == MAX_PWM (180)` produces no clamp warning | PASS |
| `test_speed_one_above_max_pwm_is_clamped` | `speed == 181` is clamped to 180 with a warning | PASS |
| `test_speed_at_min_pwm_is_not_flagged_as_clamped` | `speed == MIN_PWM (0)` produces no clamp warning | PASS |
| `test_speed_one_below_min_pwm_is_clamped` | `speed == -1` is clamped to 0 with a warning | PASS |
| `test_servo_angle_boundaries_not_flagged` | `angle == 0` and `angle == 180` produce no warning | PASS |
| `test_servo_angle_one_past_each_boundary_is_clamped` | `angle == -1` and `angle == 181` are clamped with a warning | PASS |
| `test_sequence_exactly_one_less_than_last_is_stale` | `seq == last - 1` rejected | PASS |
| `test_sequence_exactly_one_more_than_last_is_accepted` | `seq == last + 1` accepted | PASS |
| `test_sequence_zero_then_negative_is_rejected` | ordering check holds across zero (`seq=0` then `seq=-1`) | PASS |

Why these are new: the existing `pi/tests/test_command_validator.py` only
exercises clamping with values far outside range (999, -50), which cannot
distinguish a correct `value > high` comparison from an off-by-one error
(e.g. `value >= high`) at the boundary itself. These tests probe the exact
boundary values, which is the only way to catch that class of defect. None
of the 9 boundaries checked here turned up an actual defect; all passed on
the first correct attempt (unlike the dead-man pan test above).

## `test_command_framing_boundaries.py` (2 tests)

Source under test: `pi/common/mock_hardware.py`
(`MockArduino._handle_line`), `pi/common/protocol.py`
(`MAX_COMMAND_CHARS = 8`).

| Test | Boundary checked | Result |
|---|---|---|
| `test_line_at_exactly_max_command_chars_is_accepted` | an 8-character line (`F1111111`) is not rejected for length | PASS |
| `test_line_one_char_past_max_command_chars_is_rejected` | a 9-character line is rejected with `ERR_LEN` | PASS |

Why new: the existing `test_oversized_command_rejected` sends an
11-character line, proving oversized commands are rejected somewhere, but
not where the cutoff is. This pins the exact cutoff.

## What these new tests prove, and what they do not

A passing test proves only the exact behaviour it exercises, at the exact
inputs it uses. These 17 tests establish:

- the dead-man timer's alive/tripped boundary is exactly where the source
  says it is (inclusive at `DEADMAN_MS`), with no off-by-one in either
  direction, for the `MockArduino` software model;
- panning, tilting, or requesting status does not extend the dead-man
  window, matching the documented design intent in `protocol.py`;
- the server-side command validator's PWM and servo-angle clamps and its
  sequence-monotonicity check have no off-by-one defect at their exact
  boundaries;
- the command-length check's cutoff is exactly 8 characters as named by
  `MAX_COMMAND_CHARS`.

They do not prove anything about the real Arduino firmware's behaviour
(that would require hardware-in-the-loop testing against the physical
board, out of scope here), about timing under real network conditions, or
about any code path not exercised by these specific inputs.

## Addendum, 2026-10-22 (later pass): native firmware tests, and two corrections to the claims above

A later pass in the same task added `research-analysis/native/`: the real,
unmodified `arduino/*.cpp` sources (`protocol.cpp`, `utils.cpp`,
`robot_state.cpp`, `motors.cpp`, `servos.cpp`, `telemetry.cpp`,
`command_parser.cpp`) compiled with `g++` against a small host stub of the
Arduino API (`research-analysis/native/fake_arduino/`), producing a native
test binary that exercises the actual compiled firmware logic rather than
`MockArduino`. `arduino.ino`'s `taskSafety()` is a `static` function in that
one `.ino` translation unit and cannot be linked from a separate binary; it
is reproduced verbatim in `research-analysis/native/tests/mirrored_safety_task.h`,
cited against its exact source lines, rather than re-derived -- the one
piece of control flow in this test not compiled directly from `arduino/`.
Everything else -- the command-parsing pipeline, the dead-man state machine,
motor PWM ramping and the enable line, telemetry formatting -- is the real
source, unmodified, compiled and run as-is.

Build and run command, compiler version, and full output:
`research-analysis/output/native_deadman_tests_2026-10-22.txt`. Result:
**10 test functions, 27 checks, 10 of 10 passed** (`research-analysis/native/tests/test_main.cpp`,
`research-analysis/native/build/deadman_native_tests`).

**This found that two of the claims in the "What these new tests prove"
section above are wrong about the real firmware, though correct about
`MockArduino`:**

1. **Boundary direction.** The paragraph above says the dead-man's
   "alive/tripped boundary is exactly where the source says it is
   (inclusive at `DEADMAN_MS`)" for `MockArduino`, whose `_check_deadman`
   uses `elapsed <= DEADMAN_MS` to mean "alive". The real firmware's
   `taskSafety()` in `arduino/arduino.ino` (lines 79-88) checks
   `(now - lastCommandTime) >= DEADMAN_TIMEOUT_MS` to mean "trip" -- the
   opposite inclusive direction. At exactly 2000 ms of silence, `MockArduino`
   reports alive; the compiled firmware reports tripped. Confirmed by
   `test_at_exactly_boundary` in the native suite.
2. **Pan/tilt/status re-arming.** The paragraph above says "panning,
   tilting, or requesting status does not extend the dead-man window,
   matching the documented design intent in `protocol.py`". That is true of
   `pi/common/protocol.py`'s `DEADMAN_ARMING_COMMANDS`, which deliberately
   excludes `P`/`T`/`?`, and of `MockArduino`, which implements exactly that
   exclusion. It is not true of `arduino/command_parser.cpp`: `handleLine()`
   calls `g_state.noteCommandReceived(now)` for *any* syntactically valid
   command before the state-machine gate even runs, with its own comment
   reading "Any well-formed command counts as comms activity for the
   dead-man timer, even a query or heartbeat." Confirmed by
   `test_pan_command_rearm_behaviour_on_real_firmware` and
   `test_tilt_and_status_rearm_behaviour_on_real_firmware`: both re-arm the
   real firmware's dead-man.

Both are one-line, commented design choices in the real firmware, not bugs
introduced by this test. The point is narrower and more important: `pi/common/mock_hardware.py`
and `pi/common/protocol.py`'s `DEADMAN_ARMING_COMMANDS` do not faithfully
model the Arduino's own re-arming rule, so any test or claim built only on
the mock (including the "17 new tests" and the "138 tests" total above, and
the manuscript text that cited them) was characterising the mock, not the
robot, for these two specific properties.

**Addendum, 2026-10-22 (later same day): mock corrected.** Both discrepancies
above have since been fixed with a minimal, reviewed two-line patch:
`_check_deadman`'s comparison changed from `<=` to `<` (now trips at
`elapsed >= DEADMAN_MS`, matching `taskSafety()`), and
`DEADMAN_ARMING_COMMANDS` expanded from 6 opcodes to all 9 in `ALL_COMMANDS`
(now re-arms on pan/tilt/status too, matching `handleLine()`/`noteCommandReceived()`).
The proposed diff, an isolated proof-of-concept subclass, and an in-memory
regression check against the full `pi/tests/` suite were produced and
reviewed *before* either production file was edited; see
`research-analysis/proposed_patch/` for all of it, including
`PATCH_production.diff` (the diff as applied) and
`PATCH_existing_tests_update.diff` (the matching update to the three
`research-analysis/tests/test_deadman_boundaries.py` tests below that
previously asserted the pre-patch behaviour). After applying both files:
`pi/tests/` -- **121/121 still pass** (no historical test asserted either of
the two specific behaviours that changed); `research-analysis/tests/` --
**25/25 pass**, including the now-renamed, now-flipped
`test_deadman_trips_at_exactly_deadman_ms`, `test_pan_command_rearms_deadman`
and `test_tilt_and_status_also_rearm_deadman`. `MockArduino` now agrees with
the native-firmware findings on both properties; only the GPIO-level
safe-state and post-trip-recovery findings above remain mock-less
(no pin model, no `MODE_PANIC` gate) and still [PENDING MEASUREMENT] at the
hardware level, same as before.

**New coverage with no prior test, mock or native:**

- **Motor safe-state at the GPIO level.** `test_motor_enable_line_and_pwm_go_safe_on_trip`
  confirms that on a trip, the motor enable line goes `LOW` and all four
  BTS7960 PWM pins (`LEFT_RPWM`, `LEFT_LPWM`, `RIGHT_RPWM`, `RIGHT_LPWM`) go
  to 0. `MockArduino` has no pin model at all, so no prior test, including
  the 138 above, checked this at any level.
- **Recovery after a timeout.** `test_recovery_first_command_after_trip`
  shows the real firmware's first command after a trip is rejected
  (`NACK F REJECTED`) because `checkState()` still sees `MODE_PANIC` for
  that one command, but `lastCommandTime` was already refreshed by the same
  command (stage ordering in `handleLine()`), so the very next 10 ms safety
  pass clears the fault (`EVT DEADMAN_CLEARED`) with no further input, and a
  second attempt at the same command succeeds. Re-running `MockArduino`
  directly (recorded in the same output file) shows it accepts the first
  post-trip command immediately, with neither a rejection nor a clear event,
  because it has no `MODE_PANIC`/`MODE_ESTOP` gate at all (stated in its own
  module docstring). Neither recovery path was tested anywhere before this
  pass.

**What this is not:** hardware-in-the-loop testing. No board, no real UART
timing, no electrical measurement of the EN line or PWM duty cycle, and no
ATmega-specific behaviour (Timer2, `analogWrite` frequency) is exercised;
`fake_hw::digitalState`/`analogState` are recorded host-side values, not
voltages. This closes the "would require hardware-in-the-loop testing...
out of scope here" gap noted below only insofar as it tests the compiled
logic without a board; it does not establish anything about the physical
electrical signals, which remain [PENDING MEASUREMENT] along with E4.

## Gaps identified but not filled in this pass, with reasons

- **Watchdog (P3) recovery logic using mocks:** `tools/eval/faultinject.py`
  already provides a real, measured recovery-time result
  (`faults.csv`, Section 5.4 of the paper); a mock-based unit test of P3's
  restart logic was not added in this pass because the measured result is
  stronger evidence for the same claim and no specific gap in P3's own
  module-level logic was identified during the audit that a mock test
  would newly expose.
- **Audio-session/shared-capture mocks:** `pi/tests/test_shared_capture.py`
  and `pi/tests/test_resilient_audio.py` already cover device-sharing,
  reopening, and failover with isolated mocks in detail (per
  `docs/TEST_REPORT.md`); no additional gap was identified here within the
  time available for this pass.
- **Mission-state behaviour during simulated link loss:** already covered
  by `pi/tests/test_mission_state.py` per its description in
  `docs/TEST_REPORT.md`; this task's `simulation_report.md` instead adds a
  *probabilistic* link-loss model (heartbeat loss rate vs. dead-man trip
  probability), which is a different kind of evidence (Section 5 of this
  task), not a duplicate of the existing state-transition tests.
