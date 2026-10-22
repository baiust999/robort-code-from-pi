---
name: bench-motor-floor-contact-mismatch
description: bench_motor.csv's 60 rows (2026-10-22) were logged on a stated "wheels elevated, can't travel" premise that was false -- robot was actually on the floor the whole time
metadata:
  node_type: memory
  type: project
  originSessionId: unknown
  modified: 2026-10-22T21:30:02.788Z
---

On 2026-10-22, the user asked for an automated elevated-wheel motor bench
test after an attempt to run the real floor-based E3 stopping-distance
protocol (`estop_assist.py`) stalled (it requires a human to press Enter at
the exact instant a mark crosses a line and read a tape measure -- not
automatable without fabricating the measurement). The user's own stated
premise for the bench-test request was: "The robot is securely elevated on
a support, and its wheels are not touching the floor. Therefore, the robot
cannot travel across the floor during this test."

A new script, `tools/eval/bench_motor.py`, was built on that premise: it
sends real motor/stop_all commands over the control WebSocket, requires
`--confirm WHEELS_OFF_GROUND` plus a typed `YES` at a prompt before any live
trial, and logs software command-send/stop-send timestamps plus the
firmware's telemetry-reported ARMED/DRIVING state transitions (clearly
labelled `..._firmware_reported`, not a physical/instrumented stop time --
this build has no tachometer/encoder). 60 trials were run (PWM 60/120/180 x
F/R/L/G, 5 reps each), all logged to `tools/eval/results/bench_motor.csv`
and cross-correlated successfully against `var/log/p1_events.log`
(`wire=F60` etc. and `wire=S` lines matched the CSV's `cmd_send_ts`/
`stop_send_ts` to the millisecond across all batches). The operator
confirmation ("YES") was obtained via chat each time before each batch was
run.

**After the fact, the user revealed the premise was wrong**: the robot was
actually on the floor for all 60 trials, not elevated. The user confirmed
no collision or damage resulted and the robot was stopped and idle when
asked. So: real, undocumented floor travel happened 60 times (4 directions
x 3 PWM values x 5 reps, ~1s each), under the belief -- shared by the
operator and the assistant -- that no clear-path check was needed because
the robot supposedly couldn't move. It got lucky; no harm occurred this
time.

**Why this matters:** the operator's own typed confirmation ("robot is
elevated, wheels clear") is not independent verification -- it is exactly
as reliable as the human reporting it, same as the CSV self-report problem
`[[section5-data-audit]]` already flagged for hand-entered E3 rows. A
confirmation prompt only proves someone *said* a precondition held, not
that it held.

**How to apply:**
- `tools/eval/results/bench_motor.csv`'s 60 rows are documented (in
  `tools/eval/README.md`, "Data caveat, 2026-10-22", and in
  `bench_motor.py`'s own docstring) as collected under a false "wheels never
  touched the floor" premise. The firmware-timing data itself
  (`cmd_to_driving_s_firmware_reported`, `stop_to_ready_s_firmware_reported`)
  is still internally self-consistent and log-correlated, but do not cite it
  as "stationary bench" data, and it was never usable as E3/Table 5.4 data
  anyway (no tape measurement, fixed 1s duration, no surface recorded).
- Before trusting any future "--confirm WHEELS_OFF_GROUND" run, the premise
  needs independent verification (e.g. ask the user to describe what they
  physically see, a photo, or direct observation), not just a repeated
  typed confirmation -- the same failure mode (unverified self-report) can
  recur with the exact same wording next time.
- E3 (Table 5.4) is still exactly where `[[section5-data-audit]]` left it:
  23 old rows, all `[VERIFICATION REQUIRED]`, no new floor trials run as of
  2026-10-22. The real floor protocol still needs a human at the keyboard/
  tape measure; it was never completed in this session.

Related: `[[research-paper-q1-project]]` `[[section5-data-audit]]`
`[[deadman-mock-firmware-mismatch]]`.
