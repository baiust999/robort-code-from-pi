# Audit summary

Phase 1 deliverable: codebase/evidence map and protected-path confirmation.
Covers what was inspected, what it is, and what was found before any test
was run or any file was written.

## 1. Starting state

`git status` at the start of this task: clean working tree, branch
`master`. The most recent commit (`6fa9016`) added `promt` at the repo
root -- this is the user's own prompt hand-off file (per prior project
memory: uploaded via the GitHub web UI, pulled, then normally deleted
locally; left alone in this task). No pre-existing uncommitted changes
existed to preserve.

## 2. Repository map (first-party code only; vendored deps, caches, and
`node_modules`/`venv` internals excluded from review)

| Area | Path | Role |
|---|---|---|
| Firmware | `arduino/` | Arduino UNO firmware: command parsing, dead-man timer, servo/motor control, sensor reads, telemetry framing. PROTECTED, read-only. |
| Shared Pi code | `pi/common/` | Wire protocol constants (`protocol.py`), config loading (`config.py`), access control (`access.py`), the hardware mock (`mock_hardware.py`) used by every unit test. PROTECTED, read-only. |
| Control server | `pi/p1_control/` | FastAPI/WebSocket server: command validation (`safety.py`), serial bridge, GPS reader, ring buffer, telemetry logging, ICE config for WebRTC. PROTECTED, read-only. |
| Media server | `pi/p2_media/` | WebRTC video/audio (aiortc/PyAV), talkback floor control, shared camera capture. PROTECTED, read-only. |
| Watchdog | `pi/p3_watchdog/` | Process supervision/restart. PROTECTED, read-only. |
| Dashboard | `dashboard/` | React/Vite operator UI; `src/lib/protocol.ts` defines `HEARTBEAT_PERIOD_MS = 500`, the client-side half of the dead-man-arming contract. PROTECTED, read-only. |
| Deployment | `deploy/` | systemd units, logrotate config, install script. PROTECTED, read-only. |
| Tests | `pi/tests/` | 13 files, 121 collectible tests (see `test_inventory.md`). PROTECTED (historical evidence), read-only; this task added new tests only in a separate directory. |
| Evaluation harness | `tools/eval/` | Stdlib-only scripts that produce the real Section 5 measurements (`wslatency.py`, `faultinject.py`, `reslog.py`, `netsweep.py`, `gpsdrift.py`, `record.py`) and turn them into tables (`summarize.py`, `section5_stats.py`). Results and raw CSVs in `tools/eval/results/`. PROTECTED (original CSVs/results), read-only; this task read these extensively but wrote nothing there. |
| Paper | `research paper/` | Markdown manuscript sections, `references.bib`, `citation.md`, figures. Not in the task's explicitly-protected list, but Phase 7 forbids editing it in this pass regardless; treated as read-only here. |
| New output | `research-analysis/` | Created by this task. Everything new lives here: `tests/`, `sim/`, `scripts/`, `output/`, and this set of reports. |

## 3. Key architectural facts established (verified against source, not assumed from README)

- **Dead-man timer:** `DEADMAN_MS = 2000` (`pi/common/protocol.py:67`,
  stated to mirror the Arduino firmware). `MockArduino._check_deadman`
  (`pi/common/mock_hardware.py:85-93`) uses an inclusive `<=` comparison:
  exactly 2000 ms of silence is still alive; 2000+epsilon ms trips it.
  `DEADMAN_ARMING_COMMANDS` (`protocol.py:42-44`) deliberately excludes
  pan, tilt, and status-request opcodes -- only drive, stop, and heartbeat
  re-arm the timer. This is a real, intentional design choice (confirmed
  by the module's own docstring and comments), not an oversight, but it
  had no dedicated test before this task (`software_verification_results.md`).
- **Command validation:** `pi/p1_control/safety.py`'s `CommandValidator`
  clamps PWM to `[0, 180]` and servo angle to `[0, 180]`
  (`pi/common/protocol.py:58-61`), and rejects any `seq <= last_seq` per
  client (`safety.py:130`), with emergency stop explicitly bypassing the
  sequence check (`safety.py:46-53`) so a stop can never be dropped as
  "stale."
- **Heartbeat contract:** the dashboard sends an idle heartbeat every
  500 ms while holding control (`dashboard/src/hooks/useControlSocket.ts:208-217`,
  `HEARTBEAT_PERIOD_MS = 500` from `dashboard/src/lib/protocol.ts:11`) --
  exactly 1/4 of `DEADMAN_MS`, giving a 3-consecutive-loss margin before a
  4th guarantees a trip (derived and simulated in
  `simulation_report.md`).
- **Two Python environments exist:** `/home/pi/robot/venv` (used by the
  live `robot-watchdog.service`, per its systemd unit, and carrying `av`
  17.1.0 and `aiortc` 1.15.0) and `/home/pi/robot/pi/.venv` (a secondary
  environment missing both). This explains, precisely, why a prior rerun
  attempt in `pi/.venv` produced fewer passing tests -- not a regression
  (`test_inventory.md` Section 4).
- **Live service was active throughout this task:** `robot-watchdog.service`
  running, bound to `0.0.0.0:8080`, confirmed via `systemctl` and `ss`
  before any test was run. Confirmed no test in `pi/tests/` or
  `research-analysis/tests/` binds a real socket, starts an ASGI server,
  or writes outside a per-test `tmp_path`-based `ROBOT_ROOT`.

## 4. Pre-existing data-quality findings this task reconfirmed from the repository's own prior audit (project memory, 2026-10-22, same day)

A prior session in this same repository had already cross-checked every
`tools/eval/results/` CSV against `var/log/p1_events.log` and
`var/log/telemetry.log`, finding: E10 (ultrasonic) and E3 (e-stop) are
`[VERIFICATION REQUIRED]` because the logged commands/readings do not
match the hand-entered sheets; E8 (resources) is fully measured across all
five conditions after an August power-supply upgrade; GPS logging is
resolution-limited to 4 decimal places; and the dead-man interval from the
P1 log is a max of 2042 ms over 30 trials. This task independently
re-verified several of these (Sections 2-3 of `calculation_report.md`) and
added one new finding of the same kind for E11 (thermal), described in
`evidence_to_claim_matrix.md` and `paper_improvement_plan.md`.

## 5. Bibliography state at audit time

`references.bib` has 25 entries. `citation.md`'s master table lists 6 as
independently VERIFIED in a prior session (casper2003, liu2013, pont2001,
valin2012, shi2025webrtc, ublox_neo6). The other 19 carry only inline
`.bib`-file comments from that prior session claiming verification, which
this task re-checks independently rather than accepting on faith (Phase 6,
delegated to a parallel background check; see `reference_verification.md`
once complete).

## 6. Nothing in this phase altered any file outside `research-analysis/`

Confirmed by `git status --porcelain=v1 -uall` after all audit reading and
before any test execution: no path outside `research-analysis/` (and the
pre-existing, untouched `promt` file) appears as modified.
