# Test inventory

Distinguishes the historical test record, a fresh rerun of that same suite,
why an earlier rerun attempt looked different, and the new tests added by
this task. ASCII only.

## 1. Historical result (do not re-date this)

`docs/TEST_REPORT.md` Section 3: **116 passed, 0 failed (3.8 s)**, "Run on:
Raspberry Pi 4, 2026-10-08." This is the historical record as committed; it
is quoted here, not reproduced here, and `docs/TEST_REPORT.md` is
unmodified by this task.

Git history shows this exact figure was produced by commit `7f5a6fb`
("Add evaluation harness and fix log rotation and telemetry headers",
2026-10-08 07:09:54 local), which added `test_telemetry_log.py` (5 tests)
on top of a prior 111-passed baseline. 111 + 5 = 116, and the table's
12 listed test files already sum to 116 exactly, so the table is internally
consistent for the suite as it stood at that moment.

## 2. A test file added after the 116-count, not reflected in the table

`pi/tests/test_ice_config.py` (5 tests: STUN-optional ICE config, no TURN
in local mode x2 parametrised, per-client ICE rate limiting) was added by
commit `11b6317` ("Make the STUN server optional and address the robot by
hostname"), timestamped 2026-10-08 08:48:05 -- **after** the 116-count was
committed at 07:09:54/07:28:41 the same morning. `docs/TEST_REPORT.md`'s
test-file table was never updated to add this file as a 13th row. This is
not a discrepancy in the historical count (116 is correct for what existed
when it was recorded); it is simply a file that postdates that report and
was never folded into it.

## 3. Fresh rerun, this task, 2026-10-22

**Environment used:** `/home/pi/robot/venv` (Python 3.11.2), confirmed by
`WorkingDirectory=/home/pi/robot/pi`, `venv /home/pi/robot/venv` in the
`robot-watchdog.service` configuration -- this is the same interpreter the
live P1/P2/P3 processes run under, and it has every dependency installed
(`av` 17.1.0, `aiortc` 1.15.0, `pytest` 9.1.1, `pytest-asyncio` 1.4.0; full
list in `research-analysis/output/venv_full_pip_list.txt`).

**Safety check performed before running:** grepped `pi/tests/` for
`uvicorn`, `TestClient`, `ASGITransport`, real socket binds, or hardcoded
production ports; none found (the one apparent hit was a false-positive
substring match of "socket" inside the module name `websocket_hub`).
`ControlServer` and the other server classes are instantiated as plain
Python objects and called directly (e.g. `server.ice_config(...)`); no test
starts an ASGI server or binds a TCP port. Confirmed the live
`robot-watchdog.service` was active and bound to `0.0.0.0:8080` throughout,
and that every test isolates its own `ROBOT_ROOT` via `monkeypatch.setenv`
to a pytest `tmp_path`, so no test reads or writes the live service's
`var/` tree.

**Command:** `cd /home/pi/robot/pi && /home/pi/robot/venv/bin/python -m pytest -v`

**Result: 121 passed, 0 failed, 3.51-3.53 s** (run twice; both runs
recorded in `research-analysis/output/rerun_full_venv_2026-10-22.txt`).
121 = 116 historical tests + the 5 `test_ice_config.py` tests described in
Section 2. Every one of the 116 historically-named test files and tests
still passes; nothing regressed.

This is a genuine fresh execution performed in this task, on 2026-10-22, not
a restatement of the 2026-10-08 result. It is reported separately from the
historical figure per the task's explicit instruction never to claim the
historical 116-pass result as a fresh run.

## 4. Why the previously attempted `pi/.venv` rerun gave 86 passed / collection errors

Reproduced in this task for a precise explanation (not just asserted):

**Environment:** `/home/pi/robot/pi/.venv` -- a second, separate virtualenv
that exists inside the `pi/` directory. `pip list` there
(`research-analysis/output/pi_venv_incomplete_pip_list.txt`) shows
`aiohttp`, `fastapi`, `pytest`, `pytest-asyncio`, `websockets`, but no `av`
and no `aiortc`. This is not the venv the live systemd service uses.

**With default pytest behaviour** (stop after collection errors):
0 tests run; 3 modules fail to import (`test_resilient_audio.py`,
`test_shared_capture.py`, `test_talkback.py`, all failing on `import av` or
`from aiortc...`), and pytest aborts with "Interrupted: 3 errors during
collection" before executing anything.

**With `--continue-on-collection-errors`** (forces pytest past the module
import failures so the rest of the suite still runs):
**86 passed, 7 errors** in 2.54-2.60 s
(`research-analysis/output/rerun_pi_venv_incomplete_2026-10-22.txt`). The 7
errors are: the same 3 whole-module collection errors, plus 4 individual
tests inside `test_controller_access.py`
(`test_p2_offer_with_key_is_controller`,
`test_p2_offer_without_key_is_view_only[None]`,
`test_p2_offer_without_key_is_view_only[123]`, `test_p2_offer_lockout`)
that import `p1_control.main`, which in turn imports `p2_media.main`, which
imports `aiortc` at module scope -- so those 4 fail at test-call time with
the identical `ModuleNotFoundError: No module named 'aiortc'`.

**Conclusion:** the 86-passed/error-count result reported previously
reflects an incomplete test environment (`pi/.venv` lacking `av` and
`aiortc`), not a software regression. Every one of the 7 non-passing items
in `pi/.venv` passes cleanly in the full `/home/pi/robot/venv`
(Section 3). The precise count is 86 passed + 7 total errors (3 module
collection errors + 4 test-level errors from the same two missing
packages), not "4 collection errors" as recalled -- the number of distinct
*modules* that fail to import is 3; the total count of non-passing pytest
items under `--continue-on-collection-errors` is 7.

## 5. New tests added by this task

See `software_verification_results.md` for the detailed writeup. Summary:
3 new files under `research-analysis/tests/` (not under `pi/tests/`,
so the historical/protected suite is untouched), 17 new unit tests, all
passing against the real `pi/common/mock_hardware.py` and
`pi/p1_control/safety.py` modules (imported read-only, nothing in `pi/` was
edited). These are new unit tests targeting boundary conditions the
existing 121 tests do not assert, not duplicates written to inflate a
count.

## 6. Summary table

| Category | Count | Source | Date |
|---|---|---|---|
| Historical unit tests (reported) | 116 passed, 0 failed | `docs/TEST_REPORT.md` | 2026-10-08 |
| Fresh rerun, full suite, full venv | 121 passed, 0 failed | this task | 2026-10-22 |
| Rerun, incomplete `pi/.venv`, forced through | 86 passed, 7 errors (env-caused) | this task | 2026-10-22 |
| New boundary unit tests, this task | 17 passed, 0 failed | `research-analysis/tests/` | 2026-10-22 |
| Native firmware tests (real, compiled `arduino/*.cpp`), this task | 10 test functions / 27 checks, 10 passed, 0 failed | `research-analysis/native/` | 2026-10-22 |
| Hardware checklist (H1-H15) | 0 run | `docs/TEST_REPORT.md` Section 4 | not run -- needs physical hardware access, out of scope (software-only task) |
| Integration checklist (I1-I19) | 0 run | `docs/TEST_REPORT.md` Section 5 | not run -- needs the live dashboard/operator in the loop |
| Network tests (N1-N8) | 0 run | `docs/TEST_REPORT.md` Section 6 | not run -- needs physical distance trials |
| Field test | 0 run | `docs/TEST_REPORT.md` Section 8 | not run -- needs a physical rescue scenario |

## 7. Native firmware tests, this task, 2026-10-22 (later pass)

A distinct evidence class from everything above: instead of importing
`pi/common`/`pi/p1_control` (as sections 3, 5 and 6 do), this test compiles
the real, unmodified `arduino/*.cpp` files with `g++` against a host stub
of the Arduino API and runs the resulting native binary. See
`software_verification_results.md`'s "Addendum, 2026-10-22" for the full
writeup and `research-analysis/output/native_deadman_tests_2026-10-22.txt`
for the exact build command, compiler version (`g++ (Debian 12.2.0-14+deb12u1) 12.2.0`)
and run output. Headline result: 10 of 10 test functions (27 checks) pass,
and two of them show that `pi/common/mock_hardware.py`'s model of the
dead-man timer's boundary direction and arming-command set disagree with
the real firmware it is meant to emulate -- a gap the mock-based tests in
Sections 3-6 above could not have found, because they test the mock, not
the firmware.

Sections 4, 5, 6 and 8 of `docs/TEST_REPORT.md` were not executed in this
task by design: they require operating the physical robot, its motors, its
radio link over distance, or a staged human scenario, all of which this
task's safety rules place out of bounds for a software-only, read-only-on-
the-implementation pass.
