---
name: deadman-mock-firmware-mismatch
description: "RESOLVED 2026-10-22: MockArduino's dead-man boundary direction and arming-command set, once found to disagree with real firmware, have been patched to match"
metadata:
  node_type: memory
  type: project
  originSessionId: 389cada6-32c0-4bb8-9b81-7697bdf137d1
  modified: 2026-10-22T18:27:19.046Z
---

On 2026-10-22, a native compile of the real, unmodified `arduino/*.cpp`
sources (`research-analysis/native/`, g++ against a host Arduino-API stub,
10 test functions / 27 checks, 10/10 passed) found that
`pi/common/mock_hardware.py`'s `MockArduino` disagreed with the real
firmware on two dead-man properties: the boundary direction (mock alive at
`elapsed <= DEADMAN_MS`; firmware trips at `elapsed >= DEADMAN_TIMEOUT_MS`)
and the arming set (mock's `DEADMAN_ARMING_COMMANDS` excluded pan/tilt/
status; firmware's `command_parser.cpp::handleLine()` calls
`noteCommandReceived()` for any syntactically valid command).

**Later the same day, this was fixed.** The user asked for a diff-first
review (full diff shown, each line explained in plain language, effect on
`robot-watchdog` identified, `MOCK_HARDWARE` deployment status confirmed),
then explicitly approved applying it. The fix actually applied:
`pi/common/protocol.py`'s `DEADMAN_ARMING_COMMANDS` now equals
`ALL_COMMANDS` (all 9 opcodes); `pi/common/mock_hardware.py`'s
`_check_deadman` now uses `<` instead of `<=`. Both are one-line,
well-commented changes, no refactor. `research-analysis/tests/test_deadman_boundaries.py`'s
3 tests that asserted the old (wrong) behaviour were renamed and flipped to
match, per a second reviewed diff. Verified post-patch: 121/121 `pi/tests/`
pass, 25/25 `research-analysis/tests/` pass. Nothing under `arduino/`,
`pi/p1_control/`, `pi/p2_media/`, `pi/p3_watchdog/`, `dashboard/`,
`deploy/`, or any CSV was touched; nothing committed or pushed.

**Why this matters:** `MOCK_HARDWARE` is only used in development --
confirmed via `systemctl cat robot-watchdog` that the live unit sets
`Environment=MOCK_HARDWARE=0` explicitly (and `pi/common/config.py`
defaults it to `False` on Linux even if unset), so this fix changes
simulated-hardware fidelity for developers only and has no effect on the
deployed robot.

**How to apply:** the "mock disagrees with firmware" framing used
throughout `research paper/section5_results.md` Section 5.1a (Table 5.5d),
`research-analysis/software_verification_results.md`,
`evidence_to_claim_matrix.md`, and `readiness_report.md` is now historical
-- each of those files has a dated 2026-10-22 addendum noting the fix, and
the original findings are preserved, not deleted, per this project's
preserve-and-append convention. Do not re-apply this diff; it is already
live in `pi/common/`. If `pi/common/mock_hardware.py`'s module docstring
("models the firmware closely enough... for driving and telemetry
purposes") is revisited later, it is now accurate for dead-man re-arming
too, not just driving/telemetry.

Supersedes the "not fixed here" framing in the prior version of this
memory. Links: [[research-paper-q1-project]] [[section5-data-audit]].
