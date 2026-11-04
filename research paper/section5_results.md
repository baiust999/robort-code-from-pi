# 5. Results

This section reports the measurements that validate the design of Section 3, following the experiment matrix of Table 4.1 (Section 4.2). Each subsection gives the procedure specific to that experiment, the metric definitions, the results with sample size and uncertainty, an interpretation limited to what the data support, and the remaining gaps. Hardware emulation was disabled for every run (Section 4.1), so all measured figures are from the assembled robot.

**Evidence classes.** Every number in this section belongs to one of eight classes, and the class is stated wherever it is not obvious from the table caption:

- MEASURED: directly observed in an experiment on this robot and stored in `tools/eval/results/` or in the robot's own logs under `var/log/`.
- CALCULATED: derived from measured values or from documented design parameters by a stated formula.
- PUBLISHED REFERENCE: taken from a verified external source and never presented as a measurement of this robot.
- ESTIMATE: an explicitly qualified approximation resting on stated assumptions.
- PREDICTED: produced by a documented model and not an experimental observation.
- SOFTWARE-TEST: the result of a passing automated unit test exercising software logic, in most cases against a hardware mock; it establishes that the code behaves as documented for the inputs tested and is not a measurement of the physical robot.
- SIMULATED: the output of a software model with no physical measurement behind it; never presented as a measurement of real Wi-Fi behaviour, physical stopping time, or any other hardware quantity.
- [PENDING MEASUREMENT]: the required evidence does not exist; the protocol, the pass criterion fixed in advance (Table 4.2) and an empty table are given instead.

**Uncertainty.** Means of independent trials carry a two-sided 95% Student t confidence interval (N - 1 degrees of freedom); medians carry a 95% percentile-bootstrap interval (10 000 resamples, fixed seed); success proportions carry a 95% Wilson score interval [@wilson1927], which remains informative when every trial succeeds; and the 1 Hz resource series, whose samples are autocorrelated, carry a 95% interval from ten non-overlapping batch means rather than a naive interval that would treat each second as independent. No hypothesis test is reported for any experiment that has data, and no difference between those conditions is described as statistically significant. The one exception is E17 (Section 5.8), a designed within-subjects experiment whose analysis, including the test and the effect measure, was fixed in advance in Section 4.2 and is stated there before any of its data exist. All of these figures are reproduced by `tools/eval/section5_stats.py`, whose output is stored in `tools/eval/results/section5_stats.md`; the per-CSV descriptive statistics are those of `tools/eval/results/summary.md`.

**Data audit.** Before analysis, every results CSV was cross-checked against the independent machine logs that the robot keeps regardless of the experiment (`var/log/p1_events.log`, which records every command sent to the Arduino and every line received from it with a millisecond timestamp, and `var/log/telemetry.log`, which stores the telemetry snapshot at about 1 Hz). Table 5.0 summarises the outcome. Every experiment reported below is machine-logged: the rows of E1, E7, E8 and E9 are written by the evaluation tools themselves, and the E6 radio figures are logged by `netsweep.py` (only its distances and operator judgements are hand-entered). Hand-entered sheets transcribed after a session are no longer used anywhere in this section, and the last column of Table 5.0 records the independent corroboration available for each result. Because the robot's logs rotate (telemetry daily, seven kept), the log windows used here are preserved verbatim in `tools/eval/results/log_excerpts/`, and `tools/eval/section5_stats.py` reads them from there. The earlier text of this section is preserved verbatim in `research paper/archive/section5_results_pre-audit_2026-10-22.md`.

**Table 5.0.** Evidence status of every Section 5 experiment.

| # | Experiment | Status | Source | Independent corroboration |
|---|---|---|---|---|
| E1 | Control-plane latency | MEASURED | `latency.csv`, 420 rows, all `ok = 1` | Probe connections and dead-man events present in `p1_events.log` (2026-10-21) |
| E4 | Dead-man wheel-stop time (240 fps) | [PENDING MEASUREMENT] | - | Firmware-side stop interval measured from `p1_events.log` (Table 5.2b) |
| E5 | Video and audio streaming | [PENDING MEASUREMENT] | - | - |
| E6 | Communication range | MEASURED, partial (16 stations, 5 to 250 m, line of sight, no obstacle condition; no failure point reached, so usable range is at least 250 m by operator judgement only and its upper bound was not determined; ping loss of 0 to 16% did not track distance) | `network.csv`, 16 rows | Directly logged by `netsweep.py` (ping + local RSSI), not hand-entered; distances and video/control judgements are operator-entered |
| E7 | Fault injection, automated | MEASURED | `faults.csv`, 30 rows | 10 P1 serial re-opens logged during the F3 campaign; P2 and P3 logs for that date have rotated out |
| E7 | Fault injection, manual | MEASURED (F6, F7); F9 invalid | `fault_watch.csv`, 94 rows | Serial failures and dead-man trips logged in `p1_events.log` |
| E8 | Resource utilisation | MEASURED | `resources.csv`, 3608 rows | Machine-logged; one condition contains two overlapping logger runs (Table 5.8a) |
| E9 | GPS static precision and track | MEASURED, resolution-limited | `gps_static.csv` (1 summary row); `gps_track_live_2026-10-22.geojson` | Recomputed exactly from `telemetry.log` (Table 5.11a); track read from P1 |
| E13 | Field trial | [PENDING MEASUREMENT] | No `field.csv` | No per-run record exists (Section 5.7) |
| E16 | Media isolation | [PENDING MEASUREMENT] | - | - |
| E17 | Victim communication under degraded conditions | [PENDING MEASUREMENT] | No `victim_comms.csv` | Needs ethics approval and a touch input on the robot display (Section 5.8) |
| E18 | Person detection on a labelled test set, scored box against box at IoU 0.50 | [PENDING MEASUREMENT] | No `detector_groundtruth.csv`, no `detector_predictions.csv` | Needs the frame set, the hand-drawn ground-truth boxes and the dashboard's detection export (Section 5.9) |
| E15 | Cost | RECEIPT-BACKED (BDT; USD at indicative rate) | Table 5.15 | Authors' itemised receipts, 37,158 BDT; a few parts not itemised |

## 5.1 Control Latency and Emergency-Stop Response

**Procedure.** The control-plane latency probe `tools/eval/wslatency.py` (E1, Table 4.1) was run on the Pi itself and connected to P1 over the loopback interface (`127.0.0.1`, as recorded in P1's connection log), so its figures describe the robot-internal path (WebSocket server, P1, USB serial link, firmware and telemetry return) and exclude the Wi-Fi link and the operator laptop. Two jittered sessions were recorded, on 2026-10-07 (label `on-pi`) and on 2026-10-21 (label `on-pi-2026-10-21`), each with 30 valid trials per metric and no discarded trial (all 420 rows carry `ok = 1`). A third session with the send-phase jitter disabled (`on-pi-phaselocked`) was recorded to show the bias the jitter removes (Section 4.2).

**Metrics.** `hello_rtt` is the authentication request-response round trip and is the only metric that does not wait on telemetry. `motor_start` (drive command to `fw_state` ACTIVE), `motor_stop` (stop command to `fw_state` READY) and `pan_echo` (pan command to the new angle in telemetry) are telemetry-confirmed: because the firmware emits telemetry every 500 ms and P1 rebroadcasts on a 200 ms timer, each is an upper bound on the true command latency that can exceed it by up to 700 ms and by about 350 ms on average (Section 3.6.2). `deadman_trip` is the interval from the probe's last command to `fw_state` reporting the stopped state, again telemetry-confirmed. `deadman_panic`, recorded only in the 2026-10-21 session, is the interval from the same last command to the firmware's PANIC line as time-stamped in P1's event log, which is not subject to the telemetry quantisation. All values are in ms.

**Table 5.1.** Control-plane latency, jittered sender, both sessions, `tools/eval/results/latency.csv`. MEASURED. All values in ms; 95% CI of the mean (Student t).

| Metric | Session | N | Mean | 95% CI of mean | SD | Min | Max | Median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| hello_rtt | 2026-10-07 | 30 | 46.8 | 37.7 to 56.0 | 24.6 | 19.6 | 116.9 | 41.0 | 75.8 |
| hello_rtt | 2026-10-21 | 30 | 138.0 | 115.7 to 160.3 | 59.7 | 30.1 | 255.9 | 115.9 | 247.7 |
| motor_start | 2026-10-07 | 30 | 328.2 | 277.4 to 379.0 | 136.1 | 156.8 | 761.1 | 306.3 | 573.5 |
| motor_start | 2026-10-21 | 30 | 275.4 | 251.9 to 298.9 | 62.9 | 180.1 | 434.1 | 264.3 | 383.3 |
| motor_stop | 2026-10-07 | 30 | 314.3 | 284.5 to 344.2 | 80.0 | 207.9 | 606.7 | 300.0 | 393.9 |
| motor_stop | 2026-10-21 | 30 | 302.9 | 281.4 to 324.4 | 57.6 | 195.5 | 385.6 | 312.2 | 381.4 |
| pan_echo | 2026-10-07 | 30 | 387.7 | 365.2 to 410.3 | 60.4 | 285.9 | 495.0 | 381.1 | 480.8 |
| pan_echo | 2026-10-21 | 30 | 389.6 | 359.8 to 419.4 | 79.7 | 265.6 | 637.1 | 378.2 | 481.7 |
| deadman_trip | 2026-10-07 | 30 | 2409.1 | 2366.2 to 2452.1 | 115.1 | 2200.9 | 2598.4 | 2409.7 | 2584.1 |

The p95 column is the linear-interpolation 95th percentile of 30 observations; at this sample size it rests on the two largest values and is reported as a descriptive figure, not as a stable tail estimate.

**Table 5.2.** Phase-locked sender (label `on-pi-phaselocked`, 2026-10-07), same path, showing the biased distribution the jitter removes. MEASURED. All values in ms.

| Metric | N | Mean | SD | Min | Max | Median | 95% CI of median | p95 |
|---|---|---|---|---|---|---|---|---|
| motor_start | 30 | 407.1 | 62.8 | 266.2 | 504.9 | 393.9 | 392.0 to 398.4 | 496.0 |
| motor_stop | 30 | 403.3 | 19.9 | 392.6 | 507.2 | 400.7 | 399.2 to 401.5 | 405.7 |
| pan_echo | 30 | 492.1 | 82.9 | 150.3 | 609.8 | 500.3 | 498.4 to 501.6 | 607.0 |

**Table 5.2a.** Dead-man trip paired with the PANIC notice, 2026-10-21 session (label `on-pi-2026-10-21`), 30 trials at drive speed 150. MEASURED. All values in ms.

| Metric | Timed from | N | Mean | 95% CI of mean | SD | Min | Max | Median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| deadman_trip | telemetry `fw_state` | 30 | 2435.9 | 2394.5 to 2477.3 | 110.8 | 2197.5 | 2593.2 | 2467.5 | 2582.8 |
| deadman_panic | P1 event-log PANIC line | 30 | 2079.1 | 2068.7 to 2089.6 | 27.9 | 2022.3 | 2122.3 | 2076.5 | 2120.8 |

`deadman_panic` is timed from the probe's WebSocket send, so it still contains the WebSocket and P1 processing before the command reaches the serial port. P1's event log removes that leg: it time-stamps every command written to the Arduino (`DEBUG_TX`), the firmware's acknowledgement of it (`ACK`), and the `PANIC DEADMAN` line, all on one clock. Table 5.2b decomposes the 30 trials of Table 5.2a using those entries; every probe trial matched exactly one PANIC line.

**Table 5.2b.** Dead-man interval decomposed on P1's clock, 2026-10-21, `var/log/p1_events.log` matched to Table 5.2a. CALCULATED from MEASURED log timestamps. All values in ms.

| Interval | N | Mean | 95% CI of mean | SD | Min | Median | Max |
|---|---|---|---|---|---|---|---|
| P1 sends last drive command -> P1 receives PANIC line | 30 | 2022.5 | 2019.7 to 2025.3 | 7.5 | 2009.0 | 2024.0 | 2042.0 |
| P1 receives ACK of that command -> P1 receives PANIC line | 30 | 2002.0 | 1998.7 to 2005.2 | 8.7 | 1986.0 | 2002.5 | 2022.0 |
| P1 sends last drive command -> P1 receives its ACK | 30 | 20.5 | 18.8 to 22.2 | 4.6 | 6.0 | 21.0 | 29.0 |
| Probe `deadman_panic` minus first row (WebSocket and P1 leg) | 30 | 56.6 | 46.8 to 66.4 | 26.2 | 6.3 | 52.9 | 101.3 |

**Analysis.** The dead-man result is the strongest timing evidence in the paper. In the firmware, `taskSafety()` calls `emergencyStop()` and then `sendPanic()` in the same pass (`arduino/arduino.ino`, lines 79 to 86), so the PANIC line marks the instant at which drive is removed electrically. Measured on P1's clock from the moment the last command left P1 to the moment the PANIC line arrived back, the interval never exceeded 2042 ms in 30 of 30 trials (mean 2022.5 ms, 95% CI 2019.7 to 2025.3 ms), and this interval still includes the serial transit in both directions. It therefore lies below the analytical stop bound of approximately 2060 ms of Section 3.5.2 (2000 ms window + 10 ms supervisor period + about 50 ms longest loop pass) in every trial, by at least 18 ms. The interval from the firmware's acknowledgement to its PANIC line, in which the return leg cancels because both lines travel the same path, has a mean of 2002.0 ms (95% CI 1998.7 to 2005.2 ms), which agrees with the 2000 ms dead-man window; its spread (min 1986, max 2022 ms) shows that P1's receive timestamps carry a jitter of the order of 15 ms from USB-serial buffering and event-loop scheduling, which is the resolution of this method. The probe's `deadman_panic` figure of 2079.1 ms exceeds the bound only because it also contains the WebSocket and P1 leg before the command reached the Arduino (mean 56.6 ms, last row of Table 5.2b); the earlier draft's statement that this figure "sits directly on" the bound conflated the two. The difference between the paired `deadman_trip` and `deadman_panic` means, 356.8 ms, is consistent with the mean telemetry-reporting delay of about 350 ms predicted in Section 3.6.2, and the drop in SD from 110.8 ms to 27.9 ms shows that most of the spread in the telemetry-confirmed figure belongs to the reporting path. What these log measurements establish is the time at which the firmware removed drive. The time at which the wheels physically come to rest after that, which includes mechanical run-down, is the subject of E4 and is not yet measured.

The command-confirmation metrics (`motor_start`, `motor_stop`, `pan_echo`) have means between 275 and 390 ms in both sessions and all fall inside the 700 ms confirmation bound, consistent with the upper-bound model of Section 3.6.2; they are upper bounds, and the true command latency is lower by an unknown amount up to 700 ms per trial; no direct measurement is part of this evaluation. The two sessions agree closely for `motor_stop` and `pan_echo` (overlapping confidence intervals). They do not agree for `hello_rtt`: its mean rose from 46.8 ms (95% CI 37.7 to 56.0) on 2026-10-07 to 138.0 ms (115.7 to 160.3) on 2026-10-21, with non-overlapping intervals. Because both sessions ran over loopback, this difference is not a network effect; it reflects a change in WebSocket and authentication processing time on the Pi between the two days, whose cause (background load, software state) was not recorded. Consequently `hello_rtt` is not a stable floor for the control path, and the earlier description of it as bounding "the pure network-and-WebSocket contribution" is withdrawn: no Wi-Fi figure exists for E1. The phase-locked run (Table 5.2) illustrates the artifact the jitter is designed to remove: its medians collapse onto the rebroadcast grid (motor_stop median 400.7 ms, bootstrap interval 399.2 to 401.5 ms, SD 19.9 ms against 80.0 ms jittered), a deceptively tight distribution with a shifted mean, so the jittered figures of Table 5.1 are the primary result, as recorded in `tools/eval/README.md` and discussed in Section 6.4. As recorded in `tools/eval/wslatency.py`, the 0 to 200 ms jitter cannot fully decorrelate a trial from the 500 ms firmware telemetry cycle, so the jittered spread still understates the full quantisation spread.

**Comparison with the literature.** Human-factors studies of teleoperation identify command and video latency, frame rate and field of view as the main system factors that degrade operator performance [@chen2007]. The figures here are robot-internal upper bounds measured over loopback and cannot be set against those human-performance results, since no end-to-end latency over Wi-Fi was measured.

The physical dead-man wheel-stop time (E4) requires a 240 fps camera and has not been collected.

[PENDING MEASUREMENT: E4 dead-man physical stop time.] Protocol: with `tools/eval/record.py deadman_physical`, cut the command stream and film the wheels at 240 fps, timing from the last heartbeat to wheels stationary; record whether the PANIC DEADMAN line appeared; 20 trials with the robot on the floor at PWM 180, the worst case for coast-down. A tape laid along the path and kept in frame also gives the distance the robot covers between the last command and rest, recorded in the `distance_cm` column as an observation; no criterion is set on it in advance. Pass criterion (Table 4.2): wheels stationary within 2.5 s of the last command and PANIC DEADMAN logged, in 20 of 20 trials. If any trial fails, contribution 1 stays limited to the time at which drive is removed. This is the direct test of the physical stop; Table 5.2b already establishes from the firmware side that drive is removed within 2042 ms of the last command in every logged trial.

**Table 5.3.** Dead-man wheel-stop time (E4), `deadman_physical.csv`. [PENDING MEASUREMENT]

| trial | speed_pwm | stop_s | distance_cm | panic_seen |
|---|---|---|---|---|
| | | | | |

[PENDING MEASUREMENT: E4 analysis to be filled when deadman_physical.csv data is collected; the filmed wheel-stop time will be compared with the approximately 2060 ms bound of Section 3.5.2 and with the firmware-side interval of Table 5.2b.]

**Limitations.** No E1 figure includes the Wi-Fi link. The latency metrics other than `hello_rtt` and the log-timed dead-man intervals are upper bounds. The log-timed method resolves the firmware stop to about 15 ms and does not observe the wheels; the time at which the wheels come to rest, and the distance covered after the stop, are not measured in this paper (E4).

**Supplementary evidence (E1, E4).** The raw experimental dataset for E1 (control-plane latency) is provided in the supplementary experimental evidence archive [XX] (DOI: XXX) under `E01_Control_Communication/dataset/`: `latency.csv` (420 rows, the three sessions of Tables 5.1 to 5.2a) and the preserved P1 event-log window `p1_events_2026-10-21_1100-1400.log.gz`, from which Table 5.2b and the firmware-side interval cited for E4 are calculated. No experimental recording of the E1 sessions exists in the project repository, so none is provided under `E01_Control_Communication/video/`. For E4 (dead-man wheel-stop time) neither the dataset (`deadman_physical.csv`) nor the 240 fps recording exists yet; both will be added under `E04_Deadman_Timer/dataset/` and `E04_Deadman_Timer/video/` after the physical trials have been completed.

### 5.1a Software Verification: Automated Unit Tests

The timing guarantees analysed in Section 3.5.2 and measured in Table 5.2b rest on firmware-facing and server-side logic whose correctness is checked separately by automated unit tests against `pi/common/mock_hardware.py`'s `MockArduino` model and the Pi-side validation code, under `MOCK_HARDWARE` semantics. This is SOFTWARE-TEST evidence: it establishes that the code behaves as documented at the inputs tested, and it does not operate the physical Arduino firmware, the motors, or the radio link.

`docs/TEST_REPORT.md` reports 116 passed, 0 failed, run on a Raspberry Pi 4 on 2026-10-08; that figure is quoted here, not rerun, and the report keeps it unchanged (its later addenda record the 2026-10-22 and 2026-10-28 reruns). Five further tests in `pi/tests/test_ice_config.py` (STUN-optional ICE configuration, no TURN relay in local mode under two parametrisations, and per-client ICE rate limiting) were committed about 1 h 40 min after the 116-count, the same morning, and were never folded into that report's test-file table; the 116-test figure is correct for what existed when it was recorded and is kept dated and intact rather than silently combined with a later count.

A fresh rerun of the full existing suite on 2026-10-22, in the same Python environment the live `robot-watchdog.service` uses, passed 121 of 121 tests with 0 failures: the 116 historical tests plus the five `test_ice_config.py` tests. This is a separately dated, independently executed result reported alongside, not in place of, the historical figure.

On 2026-10-28 nine tests were added with the link-quality warning of Section 3.7.3 (`pi/tests/test_wifi_signal.py`): the signal level is parsed from the kernel's wireless statistics; a link that is not up, a missing interface, or an interface absent from those statistics gives no reading rather than the last level; the weak and critical alert bits are set at the thresholds and the critical bit when there is no reading; and the level is the last log column, empty when there is no reading. The full suite then passed 130 of 130 (the 121 above plus these 9). The nine tests concern the signal reading only and none of them bears on the timing guarantees; the 121-test count used below is unchanged.

On 2026-10-30 two groups were added with the features of Section 3.11. Sixteen tests of the victim-marking endpoint (`pi/tests/test_victim_log.py`) brought the full suite to 146 of 146 passed, and ten tests of the tap-to-answer question logic (in `pi/tests/test_talkback.py`) then brought it to 156 of 156 passed (outputs in `research-analysis/output/rerun_full_venv_2026-10-30.txt` and `rerun_full_venv_2026-10-30_questions.txt`). These 26 tests concern features outside the research questions, which Section 6.3 lists as not evaluated, and none bears on the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, are unchanged (the full suite reaching 146 on 2026-10-30 is a separate count).

**Addendum, 2026-10-30 (later the same day): the victim-marking endpoint gained a delete operation.** A `DELETE /api/victims/{id}` endpoint was added so the controller can remove a mark, such as one entered by mistake, and have the removal reach every connected dashboard. Eight further tests for it were added to `pi/tests/test_victim_log.py`, bringing that file to 24 tests and the full suite to 164 of 164 passed (output in `research-analysis/output/rerun_full_venv_2026-10-30_victim-delete.txt`). These 8 tests concern a feature outside the research questions, for the same reason as the marking endpoint itself (Section 6.3), and none bears on the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, remain unchanged.

**Addendum, 2026-10-30 (later the same day): the victim-marking endpoint gained a start-new-mission operation.** A `POST /api/victims/new-mission` endpoint was added so the controller can archive every mark on the active list under a dated filename in the same log folder, kept rather than deleted, and have every connected dashboard's list start empty; this was prompted by marks entered during an earlier test session remaining on the active list in a later one, which per-mark deletion could clear only one mark at a time. Eight further tests for it were added to `pi/tests/test_victim_log.py`, bringing that file to 32 tests and the full suite to 172 of 172 passed (output in `research-analysis/output/rerun_full_venv_2026-10-30_victim-new-mission.txt`). These 8 tests concern a feature outside the research questions, for the same reason as the marking and delete endpoints (Section 6.3), and none bears on the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, remain unchanged.

**Addendum, 2026-10-31: Clear now removes an answered question.** The operator reported that after a victim answered, the question and its answer stayed on the dashboard and Clear had no effect. The cause was that Clear was disabled, and ignored by P2, once a question was no longer waiting, and P2 sent the stored result again to any dashboard that reconnected. P2 now discards the question on Clear in any state and tells every dashboard to remove it (Section 3.11). One test in `pi/tests/test_talkback.py` was changed and one added, bringing the full suite to 173 of 173 passed (output in `research-analysis/output/rerun_full_venv_2026-10-31_question-clear.txt`). A browser check ran the real dashboard panel in headless Chromium against the real P2 question logic, with the data channel replaced by a WebSocket and the robot screen by a stub: 13 of 13 checks passed, and the same checks on the code before the change passed 7 of 13, failing on the reported fault (`research-analysis/output/browser_question_clear_2026-10-31.txt`). This concerns a feature outside the research questions (Section 6.3), was not checked on the physical display, and bears on none of the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, remain unchanged.

**Addendum, 2026-10-31 (later the same day): repeating voice message; call-out removed.** The call-out button described in earlier drafts of Section 3.11 (a fixed recorded clip played once, followed by a 10 dB reply cue) was removed from the dashboard. Its clip had never been installed on the robot, so the button had never been usable, and no measurement used it. It was replaced by the repeating voice message of Section 3.11, which the operator records and P2 loops. Eight tests in `pi/tests/test_talkback.py` and five in `pi/tests/test_controller_access.py` were added, bringing the full suite to 186 of 186 passed (output in `research-analysis/output/rerun_full_venv_2026-10-31_voice-loop.txt`). In a first run of the same suite, one existing timing test that the change does not touch, `test_silence_is_paced_in_real_time` in `pi/tests/test_resilient_audio.py`, failed by measuring 0.023 s against an expected 0.06 +/- 0.03 s while the Pi was also running the live services; it passed in six separate reruns and in the full rerun (`research-analysis/output/rerun_full_venv_2026-10-31_voice-loop_run1-timing-flake.txt`). Removing the call-out changed only the dashboard and removed no test in `pi/tests/`. On the live robot the upload endpoint refused a wrong key; playback on the robot speaker had not been checked when this was written. These tests concern a feature outside the research questions (Section 6.3), and none bears on the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, remain unchanged.

**Addendum, 2026-10-31 (later the same day): voice-message loop chopped after push-to-talk; fixed.** An end-to-end check over WebRTC, with aiortc peers standing in for the dashboard and the Robot Screen against a P2 started with mock hardware on its own port and key (harness `research-analysis/tests/voice_loop_webrtc/run.py`), found a fault that the unit tests had missed. A dashboard that holds the floor keeps sending audio between push-to-talk presses, since a disabled WebRTC audio track sends silence (the harness's simulated dashboard does the same), and P2 treated that silence as live voice, which takes precedence over the loop. With a 1 s, 1 kHz test message and 1.5 s gaps, the tone made up 0.42 of the received audio before the operator first talked, but only 0.09 after push-to-talk was released, in runs of 0.06 to 0.42 s. P2 now discards the floor holder's audio while the loop plays, except while the operator is talking and for 0.5 s after release, so that trailing speech is not cut. After the change all 24 checks of the end-to-end run passed: the tone share after release was 0.48, in whole tones of 1.08 s; the operator's voice replaced the loop while talking; and the loop continued after the dashboard disconnected (`research-analysis/output/e2e_voice_loop_webrtc_2026-10-31.txt`, which holds the control and the fixed run). One test in `pi/tests/test_talkback.py` was added for the fault, bringing the full suite to 187 of 187 passed (`research-analysis/output/rerun_full_venv_2026-10-31_voice-loop-fix.txt`). A functional check of the dashboard panel in headless Chromium, with Chromium's simulated microphone and the real P2 message logic, passed 21 of 21 checks, including the absence of the removed call-out button, the upload of a 2.7 s and a 29.6 s recording, the panel state after a page reload, and clearing (`research-analysis/output/browser_voice_message_2026-10-31.txt`). None of these checks used the robot's speaker, a physical display or a real operator microphone. This concerns a feature outside the research questions (Section 6.3) and bears on none of the timing guarantees; the 121-test count used below, and the 146 tests (121 + 25) characterised there, remain unchanged.

The key lockout of Section 3.8 (5 failures within 300 s, host refused for 300 s even with the right key) is covered only at this level. `pi/tests/test_controller_access.py`, which is part of the 121-test suite and configures the gate with `max_failures=5` and `lockout_s=300`, passed 25 of 25 tests when run alone on 2026-10-23, including the lockout, its refusal of a correct key and the expiry of old failures. No lockout trial was run on the robot. The 3000 ms operator-side telemetry timeout of Section 3.7.3 was not measured in any experiment and is a specification value only.

A further set of boundary-condition tests, written for this verification pass and kept outside `pi/tests/` under `research-analysis/tests/` (not merged into the count above), passed 25 of 25 when rerun on 2026-10-23: 17 on the dead-man boundary, the command validator and the command framing, and 8 that exercise the corrected mock behaviour in isolation (`test_deadman_patch_isolated.py`). The 17-test group first passed on 2026-10-22; its dead-man arming and boundary assertions were revised after the native firmware test described below (Table 5.3d), and the counts here are for the revised tests. They target exact boundary values that the existing 121 tests do not probe: the dead-man timer's alive/tripped boundary at exactly `DEADMAN_MS` (2000 ms) and one ms either side of it, and the re-arming of the timer by pan, tilt and status-request commands, as the firmware does; the server-side command validator's PWM (0-180) and servo-angle (0-180) clamps at their exact limits and its sequence-number monotonicity check at the exact boundary; and the command-framing length cutoff (`MAX_COMMAND_CHARS = 8`) at exactly 8 and 9 characters.

**Table 5.3a.** Automated unit tests: historical record, fresh rerun and supplementary boundary tests. SOFTWARE-TEST.

| Test set | Scope | Count | Result | Date |
|---|---|---|---|---|
| Historical suite | `pi/tests/` as it stood on 2026-10-08 | 116 | 116 passed, 0 failed | 2026-10-08 (`docs/TEST_REPORT.md`, quoted, not rerun) |
| Fresh rerun, same suite | `pi/tests/`, full dependency environment, including the 5 `test_ice_config.py` tests added after the historical count | 121 | 121 passed, 0 failed | 2026-10-22 |
| Rerun with link-quality tests | `pi/tests/`, the 121 above plus the 9 `test_wifi_signal.py` tests of Section 3.7.3 | 130 | 130 passed, 0 failed | 2026-10-28 |
| Rerun with victim-mark tests | `pi/tests/`, the 130 above plus the 16 `test_victim_log.py` tests of Section 3.11 | 146 | 146 passed, 0 failed | 2026-10-30 |
| Rerun with question tests | `pi/tests/`, the 146 above plus 10 tap-to-answer question tests in `test_talkback.py` (Section 3.11) | 156 | 156 passed, 0 failed | 2026-10-30 |
| Rerun with victim-delete tests | `pi/tests/`, the 156 above plus 8 more `test_victim_log.py` tests for the `DELETE /api/victims/{id}` endpoint (Section 3.11) | 164 | 164 passed, 0 failed | 2026-10-30 |
| Rerun with new-mission tests | `pi/tests/`, the 164 above plus 8 more `test_victim_log.py` tests for the `POST /api/victims/new-mission` endpoint (Section 3.11) | 172 | 172 passed, 0 failed | 2026-10-30 |
| Rerun with question-clear test | `pi/tests/`, the 172 above plus 1 `test_talkback.py` test for clearing an answered question (Section 3.11) | 173 | 173 passed, 0 failed | 2026-10-31 |
| Rerun with voice-message tests | `pi/tests/`, the 173 above plus 8 `test_talkback.py` and 5 `test_controller_access.py` tests for the repeating voice message (Section 3.11) | 186 | 186 passed, 0 failed | 2026-10-31 |
| Rerun with voice-loop fix test | `pi/tests/`, the 186 above plus 1 `test_talkback.py` test for the loop being chopped by a muted microphone (Section 3.11) | 187 | 187 passed, 0 failed | 2026-10-31 |
| Supplementary tests | `research-analysis/tests/`: dead-man boundary, command-validator boundary, command-framing boundary (17), and the corrected mock in isolation (8) | 25 | 25 passed, 0 failed | 2026-10-23 (the 17-test group first passed on 2026-10-22) |

These results establish that, for the P1-side `MockArduino` model as corrected on 2026-10-22 (addendum below), the dead-man alive/tripped boundary (trip at elapsed >= 2000 ms), the re-arming of the timer by pan, tilt and status commands, the PWM and servo-angle clamps, the sequence check and the command-length cutoff behave as documented in `pi/common/mock_hardware.py`, `pi/p1_control/safety.py` and `pi/common/protocol.py`, for the inputs exercised. **These 146 tests (121 + 25) characterise the P1-side `MockArduino` software model, not the Arduino firmware's own source**; none of them operates the physical Arduino firmware, the motors, or a real radio link, and none of them substitutes for the dead-man wheel-stop measurement of Table 5.3 (E4), which remains [PENDING MEASUREMENT]: 146 is a count of software-logic tests against mocks, not of trials on the assembled robot, and it does not establish measured motor-stop performance. The next paragraph tests the firmware source itself. It found that the mock, as first written, treated the boundary direction and the arming by pan, tilt and status commands differently from the firmware, and the mock was then corrected to match.

**Native firmware verification (ACTUAL SOFTWARE TEST), 2026-10-22.** The tests above exercise `MockArduino`, a from-scratch Python re-implementation; they say nothing about whether its modelled boundary and arming rules match `arduino/command_parser.cpp` and `arduino/robot_state.cpp` themselves. To close that gap without hardware, this revision compiles the real, unmodified firmware sources (`protocol.cpp`, `utils.cpp`, `robot_state.cpp`, `motors.cpp`, `servos.cpp`, `telemetry.cpp`, `command_parser.cpp`, all under `arduino/`, byte-identical to the files that are flashed to the board) with `g++` against a small host-side stub of the Arduino API (`research-analysis/native/fake_arduino/`: `millis()`, `pinMode`/`digitalWrite`/`digitalRead`/`analogWrite` recorded against fake pin state, and a `Serial` object with an injectable RX queue and a capturable TX string), producing a native test binary (`research-analysis/native/build/deadman_native_tests`) that drives the actual compiled command-parsing and dead-man logic. The one exception is `arduino.ino`'s `taskSafety()`, a `static` function in that translation unit that a separate test binary cannot link against directly; it is reproduced verbatim (same lines, same comments) in `research-analysis/native/tests/mirrored_safety_task.h`, cited against its exact source location, rather than re-derived. This is a software test, not hardware-in-the-loop testing: no board, no UART electrical timing, and no ATmega-specific PWM behaviour is exercised. Build and run output: `research-analysis/output/native_deadman_tests_2026-10-22.txt`. Result: 10 test functions, 27 checks, 10/10 passed.

**Table 5.3d.** Native test of the real, compiled firmware source (not the `MockArduino` model). ACTUAL SOFTWARE TEST, 2026-10-22.

| Check | Real-firmware result | Agrees with the `MockArduino`-based claim above? |
|---|---|---|
| Alive one ms before the boundary (elapsed = 1999 ms) | alive, motors unchanged | Yes |
| Exactly at the boundary (elapsed = 2000 ms) | **tripped** (`taskSafety()`'s check is `>= DEADMAN_TIMEOUT_MS`, an inclusive upper bound) | **No** -- the mock's `<=` reports "alive" at this exact instant; the firmware reports "tripped" |
| One ms past the boundary (elapsed = 2001 ms) | tripped, motors stopped | Yes |
| Motor EN line and all four PWM pins on trip | EN line LOW, all four BTS7960 PWM pins (`LEFT_RPWM`, `LEFT_LPWM`, `RIGHT_RPWM`, `RIGHT_LPWM`) 0 | n/a -- the mock has no GPIO pin model, so this safe-state property was previously untested at any level |
| Repeated pan (`P90`) commands while a drive command is left to expire | **re-arms the dead-man** (firmware fault stays `NONE`); `command_parser.cpp`'s own comment reads "Any well-formed command counts as comms activity for the dead-man timer, even a query or heartbeat" | **No** -- `pi/common/protocol.py`'s `DEADMAN_ARMING_COMMANDS` deliberately excludes pan/tilt/status, and the mock and the Table 5.3a tests built on it report no re-arm |
| Tilt (`T45`) and status (`?`) commands, same setup | **re-arms the dead-man**, same mechanism | **No**, same reason |
| First command sent immediately after a trip | **rejected** (`NACK F REJECTED`): the state-machine gate (`checkState()`) still sees `MODE_PANIC` for that one command, because `handleLine()` updates `lastCommandTime` *before* checking state; the very next 10 ms safety pass then sees fresh activity and auto-clears the fault (`EVT DEADMAN_CLEARED`), so a second attempt succeeds | n/a -- `MockArduino` has no `MODE_PANIC`/`MODE_ESTOP` gate at all (by its own docstring) and accepts the first post-trip command immediately with no rejection, confirmed by re-running it directly: `research-analysis/output/native_deadman_tests_2026-10-22.txt` records both behaviours side by side |
| Unknown opcode, out-of-range speed | NACKed, motors unaffected | Yes |
| Heartbeat (`H`) before the boundary | re-arms, motors unchanged | Yes |

**What this changes.** Two behaviours of the original `MockArduino` model did not match the real firmware, although the mock-based tests had treated both as documented: the boundary direction (trip is at `>= 2000` ms, not `> 2000` ms) and the pan/tilt/status non-arming rule (the real firmware re-arms on *any* valid command; only the mock treats pan/tilt/status specially). Both are one-line, well-commented design choices in `arduino/command_parser.cpp` and `arduino/arduino.ino`, not bugs introduced by this check. The recovery mechanism -- reject once, auto-clear within one 10 ms safety tick, succeed on the next attempt -- is new evidence either way: it was not covered by any existing test (mock-based or native) before this revision, and it shows the dead-man's recovery is automatic and fast (bounded by the 10 ms safety-task period) rather than requiring an operator-visible retry loop. The motor EN-line and PWM safe-state check is likewise new: no previous test, mock or native, inspected pin-level state at all. None of this is hardware-in-the-loop evidence; the ATmega's actual PWM duty cycle, the EN line's real voltage, and UART timing on physical silicon remain [PENDING MEASUREMENT] along with E4.

**Addendum, 2026-10-22 (later same day): mock corrected to match the firmware.** `pi/common/mock_hardware.py`'s `_check_deadman` and `pi/common/protocol.py`'s `DEADMAN_ARMING_COMMANDS` have since been patched (two one-line behavioural changes, reviewed as a diff before being applied; proposal and verification preserved in `research-analysis/proposed_patch/`) so that `MockArduino` now trips at the same inclusive `elapsed >= DEADMAN_MS` boundary as the firmware, and now re-arms on pan, tilt and status commands exactly as `command_parser.cpp` does. The "No" answers in the right-hand column of Table 5.3d describe the *pre-patch* mock and are left unchanged as the historical record of what the native test found; as of this addendum they no longer describe the current `pi/common/mock_hardware.py`. The patch was verified against the full protected `pi/tests/` suite (121/121 still pass; none of those historical tests asserted the specific boundary-equality or pan/tilt/status-exclusion behaviour that changed) and against updated boundary tests in `research-analysis/tests/test_deadman_boundaries.py` (6/6 pass, three of them renamed and their expected outcomes flipped to match the corrected behaviour). This changes only the fidelity of the P1-side software model to the firmware; it does not change the firmware itself, and it does not supply any new physical measurement -- E4 (dead-man wheel-stop) remains [PENDING MEASUREMENT].

### 5.1b Dead-Man Heartbeat-Loss Robustness (SIMULATED)

All figures in this subsection are SIMULATED: they come from a software model (`research-analysis/sim/deadman_robustness_sim.py`) built from two literal, verified source constants, not from any measurement of the robot's Wi-Fi link. They do not estimate the real link's heartbeat loss rate: only ICMP ping loss to the access point exists (0 to 16% per 100-ping burst, E6, Section 5.3), which is a different quantity, and they do not model physical stopping distance.

Table 5.2b measures how long the dead-man takes to trip once commands stop arriving, on a link that was not itself dropping packets during the trial. It does not by itself show how many consecutive lost heartbeats the 2000 ms dead-man window (`DEADMAN_MS`, `pi/common/protocol.py:67`) can tolerate at the dashboard's configured 500 ms heartbeat period (`HEARTBEAT_PERIOD_MS`, `dashboard/src/lib/protocol.ts:11`), nor how mission-level trip probability scales with an assumed per-heartbeat loss rate. This subsection reports that as a software model: a deterministic boundary analysis for the tolerated-loss margin, and a Monte Carlo sweep (300 s simulated missions, 50 000 trials per assumed loss probability, fixed seed 20261022) over an assumed per-heartbeat loss probability.

At the configured 500 ms heartbeat period and the firmware's inclusive trip condition (`elapsed >= DEADMAN_TIMEOUT_MS`, Table 5.3d), 2 consecutive lost heartbeats leave a 1500 ms gap and cause no trip. A 3rd in a row leaves 2000 ms of silence at the moment the 4th heartbeat is due, and the firmware trips at that instant, before the 4th can arrive (idealised, with no transit jitter).

**Table 5.3b.** Consecutive-loss margin by heartbeat period. SIMULATED; CALCULATED from `DEADMAN_MS = 2000` ms, the firmware's `>=` trip condition and the heartbeat period, with no transit jitter. A loss count is tolerated if the next heartbeat can still arrive before 2000 ms of silence.

| Heartbeat period (ms) | Consecutive losses tolerated | Losses that guarantee a trip |
|---|---|---|
| 200 | 8 | 9 |
| 500 (configured system) | 2 | 3 |
| 1000 | 0 | 1 |
| 2000 | none | 0 (trips with no loss) |

**Table 5.3c.** Mission-level trip probability vs. an assumed per-heartbeat loss probability. SIMULATED. 300 s missions, 50 000 trials per value, seed 20261022.

| Assumed per-heartbeat loss probability | Trip rate | 95% CI half-width |
|---|---|---|
| 0.01 | 0.05% | +/- 0.02 pp |
| 0.02 | 0.47% | +/- 0.06 pp |
| 0.05 | 6.84% | +/- 0.22 pp |
| 0.10 | 42.04% | +/- 0.43 pp |
| 0.15 | 82.34% | +/- 0.33 pp |
| 0.20 | 97.94% | +/- 0.12 pp |
| 0.30 | 100.00% | +/- 0.01 pp |
| 0.50 | 100.00% | +/- 0.00 pp |

**Reading this result.** The curve is steep because a trip requires 3 independent consecutive losses, so the trip probability scales roughly with the cube of the per-heartbeat loss probability at small values: an assumed 5% per-heartbeat loss already produces a simulated trip probability of about 7% over 5 minutes, 10% produces 42%, and by 15% a trip is far more likely than not (82%). This is a direct consequence of the chosen 500 ms/2000 ms ratio, not evidence of a flaw, and it shows that a longer effective heartbeat period (for example from added processing delay, or a throttled dashboard timer) would shrink the tolerated-loss margin quickly (Table 5.3b); at 1000 ms a single lost heartbeat trips.

**Limitations.** The model assumes the configured 500 ms heartbeat period, but the logged period was 1.00 s in the minutes before the F7 injection and before the unplanned stalls (Section 5.4, Table 5.7d); at 1 s, Table 5.3b gives no tolerated loss, so Table 5.3c understates the trip probability for those sessions. The per-heartbeat loss probability swept here is an assumed input, not fitted to any measurement; it exists to show the shape of the sensitivity curve, not to claim the real link's loss rate. Loss is modelled as independent per heartbeat with no burst correlation; real Wi-Fi loss is typically bursty, which would trip the dead-man sooner at the same mean loss rate than this model predicts, so the model's trip probabilities at a given mean loss rate are a lower bound relative to a burst-loss model. No jitter or transit delay is modelled, only binary loss per heartbeat slot: the third consecutive loss trips only in this zero-jitter idealisation, because the next heartbeat is due exactly at 2000 ms, and with real arrival jitter the outcome at that point is decided by timing, so the two-loss tolerance of Table 5.3b is the margin that holds without the idealisation. A single 300 s mission length was swept. Tables 5.3b and 5.3c use the firmware's inclusive boundary confirmed by the native test (Table 5.3d). This subsection is not a measurement of the robot's actual wireless packet loss, physical stopping time, or real-world communication reliability; Section 5.3 (communication range) reports only a partial sweep of ICMP ping loss, not heartbeat loss.

## 5.2 Video and Audio Streaming Performance

This subsection reports the delay of the two-way media path (E5, Table 4.1). No valid streaming measurement exists; the experiment is entirely pending.

**Procedure.** Glass-to-glass delay is measured with `tools/eval/record.py glass2glass` by placing a millisecond clock in the robot camera's view, photographing the clock and its copy rendered in the operator video panel in the same frame, and differencing the two readings. This is a simpler and coarser procedure than the electronic glass-to-glass measurement system of Bachhuber and Steinbach (0.5 ms precision) [@bachhuber2016], whose metric it reports; its resolution is limited by the displayed clock and the camera exposure. The audio delay is measured in each direction by the same principle, recording an impulse (a clap) and its reproduction at the far end on one recorder. Conditions: one viewer (`viewers-1`), two viewers (`viewers-2`, to expose the per-session encoders of Section 3.9.1), and the operator at 20 m (`wifi-20m`); 20 trials per condition.

**Pass criterion (Table 4.2, fixed before data collection).** In `viewers-1`, the median video glass-to-glass delay is at most 500 ms and the median audio delay is at most 400 ms in each direction. Both limits are adopted by the authors and are not taken from a standard; if a standard is cited for the audio limit, its reference must be added and verified first. The other two conditions are reported against the same limits but do not decide the claim. A failure does not remove the two-way media path from the paper, but contribution C3 is then stated with its measured delay and without the claim that the delay supports conversation with a victim.

**Metrics.** Video glass-to-glass delay (ms): displayed-clock reading subtracted from the real-clock reading in one photograph. Audio mouth-to-ear delay (ms), robot to operator and operator to robot. Received video frame rate (frames/s) and bitrate (kbit/s), read from the operator browser's WebRTC statistics over each trial. Packet loss (%), from the same statistics. Each is reported as mean with 95% CI, median and maximum.

**Table 5.4.** Glass-to-glass video delay (E5), `glass2glass.csv`. [PENDING MEASUREMENT]

| trial | label | real_ms | robot_ms | delay_ms |
|---|---|---|---|---|
| | | | | |

**Table 5.4a.** Media summary per condition (E5). [PENDING MEASUREMENT]

| Condition | N | Video delay mean (95% CI), ms | Audio delay robot -> operator, ms | Audio delay operator -> robot, ms | Frame rate, fps | Video bitrate, kbit/s | Packet loss, % |
|---|---|---|---|---|---|---|---|
| viewers-1 | | | | | | | |
| viewers-2 | | | | | | | |
| wifi-20m | | | | | | | |

**What existing data can and cannot show.** The resource log of E8 records the Wi-Fi interface transmit rate (`tx_kbps`), but it counts all traffic on the interface. In every driving condition the Pi desktop was also being viewed remotely (`display_mode` = `vnc` on all samples), and the median transmit rate without an operator media stream (`driving`, 1152 kbit/s) was no lower than with one (`driving+media`, 1127 kbit/s). The interface counter therefore cannot isolate the media bitrate, and no bandwidth, frame-rate, delay or audio-quality figure is reported for this robot. The design parameters remain the specification against which E5 will be judged: 640x480 at 10 fps with a 500 kbit/s target for video, and 32 kbit/s Opus [@valin2012] in 60 ms packets for audio (Section 3.9, Table 1a).

[PENDING MEASUREMENT: E5 analysis to be filled when glass2glass.csv and the WebRTC statistics are collected; the delays will be interpreted against the parameters above and the two-way victim-interaction claim (RQ4) assessed.]

**Limitations.** Until E5 is measured, the paper makes no quantitative claim about media delay or quality.

**Supplementary evidence (E5).** No dataset or experimental recording exists for E5. The raw experimental dataset (`glass2glass.csv` and the WebRTC statistics) and the photographs or recordings of the clock readings will be added to the supplementary experimental evidence archive [XX] (DOI: XXX) under `E05_Streaming/dataset/` and `E05_Streaming/video/` after the physical evaluation has been completed.

## 5.3 Communication Range and Link Degradation

This subsection reports the Wi-Fi range sweep (E6, Table 4.1). The sweep is partial. Sixteen line-of-sight stations were logged in two sessions, 5 to 250 m from the access point (`tools/eval/results/network.csv`): N1 to N6 on 2026-10-22, and N7 to N10 and R1 to R6 on 2026-10-23. No obstacle condition was run, and no station at which the operator judged video or control unusable was reached, so no upper bound on usable range exists. The principal finding is negative and methodological: ICMP packet loss to the access point ranged from 0 to 16 percent per 100-ping burst without tracking distance, while the operator judged video and control usable at every judged station.

**Procedure.** In the outdoor open area, at line-of-sight stations moving outward from the access point, `tools/eval/netsweep.py --target <router-ip> --label <Nk> --distance-m <d> --obstacles <desc> --video <good|choppy|lost> --control <yes|degraded|no>` was run on the Pi. It sends 100 ICMP echo requests at 0.2 s intervals to the router (192.168.0.1), so the measured path is the Pi-to-router radio link, and it reads the signal level at the start and end of the burst, the negotiated transmit bitrate, the channel, and logs loss and round-trip time. The operator supplies the two usability judgements on the command line at the station. Stations N1 to N6 were run without `--video`/`--control`; N7 to N10 were run with them. R1 to R6 are a deliberate re-run, at the same six distances as N1 to N6, with the judgements recorded (`notes` = `rerun`), added because the original six rows lacked them; the N1 to N6 rows are retained unchanged.

**Metrics.** Packet loss (% of pings lost), round-trip time (mean and maximum, ms), received signal strength (dBm), negotiated transmit bitrate (Mbit/s), channel, and two operator judgements (video: good, choppy or lost; control: yes, degraded or no). The intended usable range is the largest distance at which both judgements hold and loss stays below 5%.

**Table 5.5.** Communication range and link degradation (E6), `network.csv`. MEASURED (directly logged by `netsweep.py`, not hand-transcribed); partial -- 16 stations, line-of-sight, no obstacles. One 100-ping burst per station. Distances and the `video`/`control` judgements are as entered by the operator and were not independently verified. `channel`/`freq_mhz` were added to the logging tool after N1-N4 were run. N1-N6 were logged on 2026-10-22 and N7-N10, R1-R6 on 2026-10-23, in the row order shown (R1 was logged after N10 at 250 m).

| label | distance_m | obstacles | sent | received | loss_pct | rtt_avg_ms | rtt_max_ms | signal_dbm_start | signal_dbm_end | tx_bitrate_mbps | channel (freq_mhz) | video | control |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N1 | 5 | none | 100 | 100 | 0.0 | 3.4 | 18.0 | -41 | -41 | 72.2 | - | - | - |
| N2 | 10 | none | 100 | 100 | 0.0 | 5.3 | 30.9 | -39 | -41 | 72.2 | - | - | - |
| N3 | 15 | none | 100 | 100 | 0.0 | 5.7 | 41.7 | -41 | -41 | 65.0 | - | - | - |
| N4 | 20 | none | 100 | 100 | 0.0 | 5.3 | 37.1 | -40 | -40 | 72.2 | - | - | - |
| N5 | 25 | none | 100 | 100 | 0.0 | 4.8 | 31.7 | -42 | -42 | 72.2 | 3 (2422) | - | - |
| N6 | 50 | none | 100 | 100 | 0.0 | 3.5 | 25.4 | -41 | -40 | 72.2 | 3 (2422) | - | - |
| N7 | 100 | none | 100 | 100 | 0.0 | 3.9 | 47.1 | -52 | -50 | 72.2 | 10 (2457) | good | yes |
| N8 | 150 | none | 100 | 99 | 1.0 | 12.6 | 215.6 | -55 | -56 | 72.2 | 10 (2457) | good | yes |
| N9 | 200 | none | 100 | 100 | 0.0 | 42.9 | 103.3 | -58 | -53 | 72.2 | 10 (2457) | good | yes |
| N10 | 250 | none | 100 | 94 | 6.0 | 16.6 | 307.2 | -60 | -60 | 72.2 | 10 (2457) | good | yes |
| R1 | 5 | none | 100 | 98 | 2.0 | 11.9 | 93.0 | -58 | -57 | 72.2 | 10 (2457) | good | yes |
| R2 | 10 | none | 100 | 98 | 2.0 | 9.4 | 158.4 | -55 | -57 | 72.2 | 10 (2457) | good | yes |
| R3 | 15 | none | 100 | 100 | 0.0 | 5.5 | 122.8 | -58 | -60 | 72.2 | 10 (2457) | good | yes |
| R4 | 20 | none | 100 | 92 | 8.0 | 5.0 | 93.6 | -57 | -58 | 72.2 | 10 (2457) | good | yes |
| R5 | 25 | none | 100 | 90 | 10.0 | 6.3 | 144.7 | -60 | -55 | 72.2 | 10 (2457) | good | yes |
| R6 | 50 | none | 100 | 84 | 16.0 | 6.7 | 43.5 | -55 | -60 | 72.2 | 10 (2457) | good | yes |

**Table 5.5a.** The same six distances measured in the two sessions (N1 to N6 on 2026-10-22, R1 to R6 on 2026-10-23), from Table 5.5. Loss in %, signal at the start of the burst in dBm, mean RTT in ms.

| distance_m | loss N | loss R | signal N | signal R | rtt_avg N | rtt_avg R |
|---|---|---|---|---|---|---|
| 5 | 0.0 | 2.0 | -41 | -58 | 3.4 | 11.9 |
| 10 | 0.0 | 2.0 | -39 | -55 | 5.3 | 9.4 |
| 15 | 0.0 | 0.0 | -41 | -58 | 5.7 | 5.5 |
| 20 | 0.0 | 8.0 | -40 | -57 | 5.3 | 5.0 |
| 25 | 0.0 | 10.0 | -42 | -60 | 4.8 | 6.3 |
| 50 | 0.0 | 16.0 | -41 | -55 | 3.5 | 6.7 |

**What the sweep shows.**

(i) *Distance did not degrade the link measurably over 5 to 250 m.* On 2026-10-23 the signal level at the start of each burst lay between -52 and -60 dBm at every distance from 5 to 250 m, and the negotiated transmit bitrate was 72.2 Mbit/s at all ten stations of that day. Signal level and distance are not monotonically related: the 5 m station R1 read -58 dBm and the 200 m station N9 read -58 dBm.

(ii) *Ping loss did not track distance.* Loss was 2.0, 2.0, 0.0, 8.0, 10.0 and 16.0% at 5, 10, 15, 20, 25 and 50 m (R1 to R6), and 0.0, 1.0, 0.0 and 6.0% at 100, 150, 200 and 250 m (N7 to N10). The highest loss in the data (16%) was at 50 m; the 100 to 200 m stations lost 1% or less. Loss over R3 to R6, the stations logged in succession, rose from 0 to 16% in about two and a half minutes (18:43 to 18:45 UTC) as the stations moved outward, which a time-dependent cause would also produce. Mean RTT ranged from 3.4 to 42.9 ms and maximum RTT from 18.0 to 307.2 ms, again without a monotonic relation to distance (the highest mean, 42.9 ms, was at 200 m, and the 250 m station averaged 16.6 ms).

(iii) *The two sessions disagree at the same distances.* At the six distances measured twice (Table 5.5a), the 2026-10-22 session showed 0% loss and about -41 dBm throughout, and the 2026-10-23 session showed 0 to 16% loss and -55 to -60 dBm. The 17 dB difference in signal at 5 m is larger than any change with distance within either session. The data do not identify why. Candidate explanations, none tested: a change in the access point's channel (N5 and N6 were logged on channel 3, 2422 MHz, and all rows of 2026-10-23 on channel 10, 2457 MHz), a change in the access point's position or the robot's antenna orientation between sessions (not recorded), co-channel interference on the shared 2.4 GHz band (no scan of nearby networks was run), or that some distances entered on one of the days were not the true distances. The operator confirmed the 5 m and 10 m positions of R1 and R2 when asked, but did not report whether the router was moved or restarted between sessions.

(iv) *The 5% loss condition and the operator's judgement disagree.* At all ten stations where judgements were recorded the operator judged video `good` and control `yes`, including N10 (6%), R4 (8%), R5 (10%) and R6 (16%), where loss exceeded the 5% limit of the metric definition. Read literally, the usable-range definition therefore has no single answer: the largest station passing all three conditions is N9 (200 m), but R4, R5 and R6 (20, 25 and 50 m) fail the loss condition, so the passing stations are not contiguous from the access point outward and 200 m is not a range boundary. By the operator's judgement alone the usable range is at least 250 m, with the real limit not reached. The 5% threshold is an a priori criterion of this paper, not a measured tolerance of the robot; whether the video and control actually tolerate 16% ping loss, or the judgements were made at coarse resolution, is not separable with these data. ICMP loss to the router is also not the loss rate of the control heartbeat: the heartbeat-loss sensitivity of Section 5.1b (Tables 5.3b, 5.3c) remains an assumption-driven SIMULATED result, and dead-man trips during the sweep were not logged.

**What the sweep does not show.** No station was reached at which video or control was judged choppy, lost, degraded or unusable, so the failure point, the usable-range upper bound, and the behaviour of the dead-man (Section 5.4, F7) at link loss are not measured here. No obstructed-link condition (1-wall, 2-walls) was run. Each station is one burst; the burst-to-burst variation at a fixed position was not measured, so the 0 to 16% loss spread cannot be separated into a distance effect, a time effect and sampling noise. Station timestamps (`iso_ts`) place N7 to R6 within 11 minutes (18:34:53 to 18:45:49 UTC), including the return from 250 m to 5 m between N10 and R1; this implies fast movement of the robot between stations, and the distances should be read as operator-entered values. The only other link-level observations in this paper are from the indoor laboratory, at a single location within 3 m of the access point: the mean signal level over each E8 condition lay between -40.7 and -49.0 dBm (`resources.csv`, MEASURED). These describe the test bench, not range.

**Scope caveat.** Every figure in this subsection is a property of the specific access point used for testing (SSID observed as `TOMAL`, 2.4 GHz), together with its transmit power, antenna, surroundings and neighbouring networks, and of the Pi's on-board radio, not an intrinsic bound on the robot. The access point's channel was not constant across the sweep: channel 3 / 2422 MHz at N5 and N6 (2026-10-22) and channel 10 / 2457 MHz on 2026-10-23, the channel stated in Section 3.2, which a live reading on 2026-10-23 matched. A different router or environment would very plausibly shift every number here in either direction; the paper should say so wherever a range or loss figure is cited.

**Relation to the dashboard link-quality warning.** The warning of Section 3.7.3 (amber at or below -70 dBm, red at or below -80 dBm) was added on 2026-10-28, after this sweep, and its thresholds are provisional. Every signal level in Table 5.5 lay between -39 and -60 dBm, so neither threshold was reached at any station, including the four stations that lost more than 5% of pings (N10, R4, R5, R6 at -55 to -60 dBm). In these data the signal level did not track ping loss either (finding iii), so the sweep gives no evidence yet that the signal level warns before the link degrades, or at what level it should. The software behaviour of the indicator was checked on 2026-10-28 against the Pi's real signal level and against scripted levels (SOFTWARE-TEST; `docs/TEST_REPORT.md`, addendum of that date): bars and banners followed the levels of Table 10a, and NO SIGNAL appeared within about 1 s of snapshots stopping. That check is not a measurement on a moving robot.

The sweep was not extended beyond 250 m, no obstructed link was tested, and no station was repeated within a session; these extensions are left to future work (Section 7.1.1), and the range result is reported as a lower bound only.

**Supplementary evidence (E6).** The raw experimental dataset for E6 (communication range), `network.csv` (16 stations, the two sessions of Table 5.5), is provided in the supplementary experimental evidence archive [XX] (DOI: XXX) under `E06_Communication_Range/dataset/`. Its radio figures are logged by `netsweep.py`; its distances and video and control judgements are operator-entered and unverified (Section 4.2). No experimental recording of the sweep exists in the project repository, so none is provided under `E06_Communication_Range/video/`. Obstructed links and distances beyond 250 m remain unmeasured.

## 5.4 Fault Injection and Recovery Time

**Procedure (automated).** The automated campaign (E7, Table 4.1) was run on 2026-10-07 with `tools/eval/faultinject.py run`, which sends SIGKILL to the target process and polls the health of the target about every 50 ms. Ten trials were run against each of P1 control (test F3), P2 media (F4) and the P3 watchdog (F5).

**Metrics.** `detection` is the time from the SIGKILL to the harness's first observation that the target no longer reports healthy; it bounds how soon the outage became externally visible, and it is not the time P3 took to notice the crash. `recovery` is the time from the SIGKILL to the health endpoint answering healthy with a new PID, so recovery means confirmed service, not merely a restarted process. Recovered is the proportion of trials meeting that condition.

**Table 5.6.** Fault detection and recovery, `tools/eval/results/faults.csv`, 10 trials per target. MEASURED.

| Test | Target | Metric | Mean | 95% CI of mean | SD | Min | Max | Median | Recovered |
|---|---|---|---|---|---|---|---|---|---|
| F3 | P1 | detection (ms) | 91.1 | 66.2 to 116.0 | 34.8 | 59.2 | 182.8 | 80.7 | 10/10 |
| F3 | P1 | recovery (ms) | 16026.7 | 15926.1 to 16127.3 | 140.6 | 15804.4 | 16254.8 | 15990.0 | 10/10 |
| F4 | P2 | detection (ms) | 123.2 | 90.2 to 156.2 | 46.1 | 59.8 | 175.0 | 147.1 | 10/10 |
| F4 | P2 | recovery (ms) | 14450.4 | 13762.9 to 15138.0 | 961.2 | 12966.8 | 15914.9 | 14758.4 | 10/10 |
| F5 | P3 | detection (ms) | 157.0 | 128.2 to 185.8 | 40.3 | 61.3 | 216.0 | 156.6 | 10/10 |
| F5 | P3 | recovery (ms) | 12829.0 | 12182.8 to 13475.2 | 903.3 | 10428.5 | 13841.4 | 12998.0 | 10/10 |

**Table 5.6a.** Recovery proportion with 95% Wilson score interval [@wilson1927]. CALCULATED from Table 5.6.

| Test | Recovered | 95% interval for the recovery probability |
|---|---|---|
| F3 (P1) | 10/10 | 72.2% to 100% |
| F4 (P2) | 10/10 | 72.2% to 100% |
| F5 (P3) | 10/10 | 72.2% to 100% |
| Pooled | 30/30 | 88.6% to 100% |

**Analysis.** All 30 trials recovered with a confirmed PID change; P1's event log independently shows ten serial-port re-opens during the F3 campaign, one per restart. Thirty successes bound the per-trial failure probability under these bench conditions below 11.4% at 95% confidence (Table 5.6a), which supports the process-supervision claim of Section 3.7.1 for SIGKILL faults on the bench but does not demonstrate long-run reliability. The P1 recovery mean of 16.03 s (95% CI 15.93 to 16.13 s) lies inside the 14.6 to 19.6 s window predicted by the recovery-time model of Section 3.7.2 (PREDICTED), and the small SD of 140.6 ms is consistent with a recovery path dominated by the fixed 10 s cooldown. P2 recovered in 14.45 s on average, faster than P1, consistent with P2 opening no serial link and performing no Arduino handshake; Section 3.7.2 gives no separate bound for P2, so this is a description, not a test. P3 recovered in 12.83 s on average; its restart is performed by systemd (`RestartSec=5` in `robot-watchdog.service`) followed by P3's own start-up, which is a different path from the cooldown-gated respawn P3 applies to its children. The detection figures are 59 to 216 ms in every trial, which shows that the outage is visible at the health endpoint within a fraction of a second; they do not measure P3's own crash detection, so the earlier inference that they "confirm the 1 s exit poll dominates detection" is withdrawn. During each recovery window the dead-man timer, measured in Table 5.2b and in F7 below, holds the motors stopped once commands cease, so the recovery interval is a loss-of-service window rather than a loss-of-safety window.

**Procedure (manual watch).** On 2026-10-21, `tools/eval/faultinject.py watch` polled both `/health` endpoints at 10 Hz and logged every state transition. The injection instants themselves were not logged by the harness; they are bounded below from P1's event log.

**Table 5.7.** Manually injected fault transitions (E7 manual), `fault_watch.csv`, 2026-10-21. MEASURED. `t_s` is seconds from the start of each watch.

| label | t_s | field | from_value | to_value | held_s |
|---|---|---|---|---|---|
| F6-arduino-unplug | 4.70 | serial_connected | 1 | 0 | 4.70 |
| F7-wifi-drop | 26.85 | ws_clients | 1 | 0 | 26.85 |
| F7-wifi-drop | 28.76 | ws_clients | 0 | 1 | 1.91 |

**Table 5.7a.** Manual faults timed from `var/log/p1_events.log`, 2026-10-21 (UTC). MEASURED.

| Fault | Event | Time | Interval |
|---|---|---|---|
| F6 | First P1 serial read failure | 19:41:58.363 | - |
| F6 | Harness sees `serial_connected` 1 -> 0 | 19:41:58.475 | 0.11 s after first failure |
| F7 | Last controller heartbeat forwarded to the Arduino | 19:52:48.530 | - |
| F7 | Firmware `PANIC DEADMAN` received by P1 | 19:52:50.550 | 2.02 s after last heartbeat |
| F7 | WebSocket closed by P1 (`ws_clients` 1 -> 0) | 19:53:11.686 | 23.16 s after last heartbeat |
| F7 | Operator dashboard reconnected (`ws_clients` 0 -> 1) | 19:53:13.592 | 1.91 s after close |

**F6, Arduino disconnect.** The Arduino link was cut by unbinding its USB device from the kernel driver, which removes `/dev/ttyACM0` as a cable pull would. P1 logged its first serial read failure at 19:41:58.363 and the harness observed `serial_connected` turn false 0.11 s later, within about one poll period; because the unbind instant itself was not logged, the delay from the physical event to the first failure is not measured. P1 stayed up (PID unchanged), logged read and write failures at about 0.5 s intervals as described in Table 9, and continued to serve WebSocket clients and telemetry with `serial_connected` false, consistent with the process isolation of the three-process split. When the device was re-bound, the kernel assigned a new node (`/dev/ttyACM1`) and `serial_connected` stayed false until P1 was restarted and reopened the port, confirming the Table 9 recovery path ("port reopened when P1 restarts"): P1 does not reopen a removed device by itself, so recovery from an unplug requires a P1 restart.

**F7, Wi-Fi drop.** The `wlan0` interface was taken down for about 20 s. The robot's own log shows the fail-safe chain working: the controller's heartbeats, which P1 forwards to the Arduino as they arrive from the dashboard (every 1.0 s in this window rather than the configured 0.5 s, Table 5.7d), stopped after 19:52:48.530, and the firmware tripped its dead-man and reported `PANIC DEADMAN` 2.02 s later, matching the 2002 to 2022 ms firmware interval of Table 5.2b. This is the second independent observation of the dead-man under an injected fault rather than a scripted probe, and it corrects the earlier draft, which stated that the dead-man was not exercised because P1 kept heartbeating; P1 forwards the controller's heartbeats and does not generate its own. The WebSocket itself was not closed during the outage: P1 closed it 23.16 s after the last heartbeat, and the dashboard reconnected 1.91 s after the close. The 23 s is consistent with the WebSocket keep-alive of Table 1a (ping every 20 s, 20 s timeout, `pi/p1_control/main.py`), which reclaims a dead socket only after up to 40 s; the earlier attribution to the operating system's TCP keep-alive was incorrect. Because the instant at which `wlan0` was restored was not logged, this record cannot establish whether the socket closed during the outage or shortly after the link returned. The safety-relevant conclusion does not depend on that: the robot stopped 2.02 s into the outage, more than 20 s before the control socket closed, so liveness was enforced by the firmware and not by the transport, exactly as Section 3.2 intends.

**F9, GPS loss: not a valid measurement.** An outdoor attempt on 2026-10-22 did not produce a valid controlled loss-and-recovery measurement, and no antenna-obstruction cycle was performed. The NEO-6M first reported a fix 1306.57 s after the watch started (`fault_watch.csv`), with 3 to 5 satellites; the receiver's power-on time and almanac state at that moment are unknown, so this is not a time-to-first-fix measurement in the datasheet's sense, against which the manufacturer specifies 27 s for a cold start with all satellites at -130 dBm (PUBLISHED REFERENCE, [@ublox_neo6]). The `gps_fix` transitions that followed are mixed in origin (Table 5.7b): 14 of the 25 outdoor fix losses occurred within 3 s of a P1 `GPS_FAIL` port error, which coincided with diagnostic reads of the same serial port by a second program, while the other 11 outdoor losses and all 7 losses in the later indoor run (`F9-indoor`) had no nearby port error and are consistent with genuine loss of a weak solution. The earlier statement that all of them reflected port contention is therefore corrected. None of these was a controlled injection, so no F9 result is claimed.

**Table 5.7b.** `gps_fix` 1 -> 0 transitions during the F9 attempt, matched to P1 `GPS_FAIL` events. CALCULATED from `fault_watch.csv` and `p1_events.log`.

| Watch label | Fix-loss transitions | Within 3 s of a GPS_FAIL | Not near a GPS_FAIL |
|---|---|---|---|
| F9-gps-loss (outdoor) | 7 | 3 | 4 |
| F9-gps-loss-run2 (outdoor) | 18 | 11 | 7 |
| F9-indoor | 7 | 0 | 7 |

F9 is not repeated in this evaluation, so the paper makes no claim about GPS loss detection or recovery time.

**Unplanned heartbeat stalls (not an injected fault).** The `F9-indoor` watch was still running at 14:01 UTC on 2026-10-22 and appended 16 further rows to `fault_watch.csv`, recording P1's health endpoint failing to answer twice, for 0.35 s and 0.78 s, with `serial_connected`, `gps_fix` and `ws_clients` unreadable for the same intervals. P1 was not restarted (the same process, PID 924, logged before and after). P1's event log shows that the heartbeats it forwards to the Arduino paused at the same moments (Table 5.7c): the first gap, 1.988 s, stayed inside the 2000 ms window and caused no trip, and the second, 2.080 s, exceeded it, and the firmware reported `PANIC DEADMAN` at the end of it and cleared the fault 13 ms after the next heartbeat. The cause of the stalls was not recorded, so they are reported for completeness under the validity rule of Section 4.2 and are not used as a fault-injection result; they are, however, a third, unscripted observation consistent with the dead-man tripping when, and only when, the 2000 ms window is exceeded, on a sample of three gaps.

**Heartbeat interval actually observed.** The dashboard is configured to send a heartbeat every 500 ms (`HEARTBEAT_PERIOD_MS`), and P1 forwards each one without rate limiting (`pi/p1_control/safety.py`), so the interval of `H` commands in `p1_events.log` is the interval the dashboard delivered. It was not constant (Table 5.7d). Over the 2026-10-21 probe session it was 0.50 s (median), but in the minutes before the F7 injection and before the unplanned stalls it was 1.00 s. The cause was not recorded; a dashboard tab whose timers are throttled by the browser is a candidate, but this was not tested. At a 1.00 s period a single lost heartbeat already leaves 2000 ms of silence (Table 5.3b), against two tolerated losses at the configured 500 ms rate, so the margin of Section 5.1b holds only while the dashboard keeps that rate. The `H` commands analysed here are the controller heartbeat (dashboard to P1 to Arduino). They are distinct from the Arduino's own compact heartbeat line (tag `HB`, every 1000 ms, Arduino to P1), which is an outbound status report and does not re-arm the dead-man (Section 3.2). The dead-man observations of this subsection are unaffected, since each depends only on the 2000 ms of silence.

**Table 5.7d.** Interval between heartbeats (`DEBUG_TX` `H`) written to the Arduino, from `var/log/p1_events.log.1`. MEASURED. Seconds.

| Window (UTC) | Heartbeats | Median | 10th to 90th percentile |
|---|---|---|---|
| 2026-10-21 11:40 to 12:30 (E1 probe session) | 5308 | 0.501 | 0.488 to 0.513 |
| 2026-10-21 19:51:00 to 19:52:49 (before F7) | 84 | 0.997 | 0.977 to 1.027 |
| 2026-10-22 12:01:30 to 12:03:07 (before first gap) | 192 | 0.502 | 0.375 to 0.618 |
| 2026-10-22 14:00:00 to 14:01:20 (before stalls) | 80 | 1.000 | 0.903 to 1.035 |

**Table 5.7c.** Gaps of 1.9 s or more between controller heartbeats written to the Arduino, 2026-10-22 12:00 to 14:02 UTC, `p1_events.log`. MEASURED.

| Gap start | Gap end | Gap (s) | Dead-man trip |
|---|---|---|---|
| 12:03:04.453 | 12:03:06.355 | 1.902 | None |
| 14:01:06.488 | 14:01:08.476 | 1.988 | None |
| 14:01:15.516 | 14:01:17.596 | 2.080 | PANIC DEADMAN at 14:01:17.616 |

**Limitations.** Only SIGKILL crashes were injected automatically; hangs (detected by the 35 s health-check path of Section 3.7.2), camera and microphone loss, and Robot Screen exit were not injected. The 10-trial samples bound, but do not establish, the failure probability. F6 and F7 are single injections each.

**Media isolation (E16).** [PENDING MEASUREMENT: E16.] This test asks whether load on, or a stall of, the media process P2 delays or drops control commands handled by P1, which is the reason the design separates the two (Section 3.7). Protocol: run `tools/eval/wslatency.py --probe motor --trials 30` on the Pi in three labelled conditions: `media-off` (no operator media session), `media-on` (one operator session from the laptop with video and two-way audio running for the whole probe) and `p2-frozen` (P2 suspended with SIGSTOP). In `p2-frozen`, each freeze lasts at most 15 s and is ended with SIGCONT, so that the 35 s health-check path of Section 3.7.2 does not kill and respawn P2 during the trials; the probe is run in short batches inside the freeze windows until 30 trials are collected, and `p3_events.log` is checked afterwards to confirm that no restart occurred. Metric (Table 5.7e): the count of confirmed motor commands and the `motor_stop` upper bound (ms), median with 95% bootstrap interval, per condition. Pass criterion (Table 4.2, fixed in advance): in `media-on` and in `p2-frozen`, 30 of 30 commands confirmed and the `motor_stop` median within 50 ms of the `media-off` median. Because the E1 values are telemetry-quantised upper bounds, a shift smaller than about 50 ms cannot be resolved; the test detects blocking or dropped commands, which is the failure the process split is designed to prevent. It does not show how a single merged process would behave, since no merged variant was built.

**Table 5.7e.** Control-path latency under media load and a media-process stall (E16), `latency.csv` rows labelled `media-off`, `media-on` and `p2-frozen`. [PENDING MEASUREMENT]

| Condition | N | Confirmed | motor_stop median (ms) | 95% bootstrap interval (ms) | Difference from `media-off` (ms) |
|---|---|---|---|---|---|
| media-off | | | | | - |
| media-on | | | | | |
| p2-frozen | | | | | |

**Supplementary evidence (E7, E16).** The raw experimental dataset for E7 (fault injection and recovery) is provided in the supplementary experimental evidence archive [XX] (DOI: XXX) under `E07_Fault_Recovery/dataset/`: `faults.csv` (30 automated trials, Table 5.6), `fault_watch.csv` (94 manual-watch rows, Tables 5.7 and 5.7b) and the preserved P1 event-log windows `p1_events_2026-10-07_2100-2259.log.gz` (F3 serial re-opens), `p1_events_2026-10-21_1940-1955.log.gz` (F6 and F7, Table 5.7a) and `p1_events_2026-10-22_1200-1402.log.gz` (F9 matching and the heartbeat stalls of Table 5.7c). The F9 rows of `fault_watch.csv` are included for completeness but are not a valid measurement and support no result. No experimental recording of the E7 trials exists in the project repository, so none is provided under `E07_Fault_Recovery/video/`. For E16 (media isolation) no dataset or recording exists yet; both will be added under `E16_Media_Isolation/dataset/` and `E16_Media_Isolation/video/` after the evaluation has been completed.

## 5.5 Resource Utilization on the Edge Device

**Procedure.** Resource use was logged with `tools/eval/reslog.py` (E8, Table 4.1) at 1 Hz: system CPU (as a percentage of the whole four-core processor), per-process CPU for P1, P2 and P3 (as a percentage of one core, so up to 100% per fully busy core), memory, per-process resident memory (RSS), SoC temperature, the firmware throttle word and its decoded flags, and interface statistics. Six labelled conditions exist: `idle` (2026-10-08, no operator connected), `idle-partial-10min` (2026-10-07, media process encoding for the Robot Screen only), `driving` (2026-10-21, robot driven continuously over the control WebSocket by a scripted client, no operator media stream, wheels clear of the ground, freshly rebooted Pi), `driving+media` (2026-10-21, as `driving` with an operator video stream active, after the Pi supply was upgraded), `driving+media-16kbps` (2026-10-21, as `driving+media` with the Opus bitrate set to 16 kbit/s instead of 32 kbit/s, Section 4.3), and `driving+media-throttled` (2026-10-21, the first `driving+media` capture, on the original USB power bank of Table 2).

**Audit of the logger runs.** Each row of `resources.csv` carries both a wall-clock timestamp and the logger's own elapsed time, so the start time of the logger that wrote it can be recovered. Five conditions are single uninterrupted runs at a 1.000 s median spacing. The `driving+media` condition is not: its 299 rows come from two logger instances started 94 s apart (20:14:56 and 20:16:30 UTC) and writing under the same label, of which the first 196 s of one and the first 103 s of the other are absent from the file, so the rows span 196 s of wall-clock time, with 103 s sampled twice, rather than the 300 s stated in the earlier draft. The rows were not altered; their statistics are reported as logged, and the per-run figures are given in Table 5.8a to show that the splice does not change the result.

**Table 5.8a.** `driving+media` split by logger run. CALCULATED from `resources.csv`.

| Logger start (UTC) | Rows | Total CPU mean (%) | P2 CPU mean (% core) | P2 CPU SD | P2 RSS mean (MB) |
|---|---|---|---|---|---|
| 20:14:56 | 103 | 21.06 | 63.01 | 4.10 | 453.4 |
| 20:16:30 | 196 | 20.60 | 62.87 | 3.81 | 453.9 |
| Pooled, as logged | 299 | 20.76 | 62.92 | 3.91 | 453.7 |

**Table 5.8.** Resource utilisation, `tools/eval/results/resources.csv`. MEASURED. Total CPU is % of the four-core processor; P1 to P3 CPU is % of one core; memory in MB; temperature in deg C. N is the number of 1 Hz rows.

| Condition | Metric | N | Mean | SD | Max | p95 |
|---|---|---|---|---|---|---|
| idle | total CPU | 1799 | 14.44 | 15.67 | 91.40 | 46.11 |
| idle | P1 CPU | 1799 | 2.89 | 1.09 | 8.00 | 5.00 |
| idle | P2 CPU | 1799 | 0.90 | 0.54 | 3.00 | 2.00 |
| idle | P3 CPU | 1799 | 0.12 | 0.33 | 2.00 | 1.00 |
| idle | memory used | 1799 | 1906.9 | 97.2 | 2134.7 | 2081.0 |
| idle | SoC temp | 1799 | 45.2 | 1.8 | 52.1 | 48.2 |
| idle-partial-10min | total CPU | 603 | 33.47 | 20.05 | 95.90 | 88.18 |
| idle-partial-10min | P1 CPU | 603 | 4.62 | 1.66 | 11.00 | 8.00 |
| idle-partial-10min | P2 CPU | 603 | 26.64 | 29.47 | 97.00 | 83.81 |
| idle-partial-10min | P3 CPU | 603 | 0.16 | 0.40 | 2.00 | 1.00 |
| idle-partial-10min | memory used | 603 | 2341.8 | 171.2 | 2520.1 | 2507.9 |
| idle-partial-10min | SoC temp | 603 | 47.2 | 1.7 | 52.6 | 51.1 |
| driving | total CPU | 309 | 20.70 | 8.66 | 61.20 | 40.98 |
| driving | P1 CPU | 309 | 3.74 | 0.96 | 8.00 | 5.00 |
| driving | P2 CPU | 309 | 1.12 | 1.37 | 8.00 | 2.00 |
| driving | P3 CPU | 309 | 0.12 | 0.34 | 2.00 | 1.00 |
| driving | memory used | 309 | 2429.3 | 31.5 | 2508.5 | 2478.2 |
| driving | SoC temp | 309 | 48.0 | 0.8 | 51.6 | 49.2 |
| driving+media | total CPU | 299 | 20.76 | 3.89 | 45.40 | 28.04 |
| driving+media | P1 CPU | 299 | 3.81 | 0.64 | 6.00 | 5.00 |
| driving+media | P2 CPU | 299 | 62.92 | 3.91 | 92.00 | 71.00 |
| driving+media | P3 CPU | 299 | 0.10 | 0.30 | 1.00 | 1.00 |
| driving+media | memory used | 299 | 2271.7 | 26.7 | 2304.6 | 2303.3 |
| driving+media | SoC temp | 299 | 49.5 | 0.6 | 51.6 | 50.1 |

**Table 5.8b.** Mean per-process CPU with 95% batch-means interval (ten non-overlapping batches). CALCULATED from `resources.csv`. % of one core.

| Condition | P1 CPU mean (95% CI) | P2 CPU mean (95% CI) | Total CPU mean (95% CI), % of processor |
|---|---|---|---|
| idle | 2.89 (2.75 to 3.03) | 0.90 (0.88 to 0.92) | 14.44 (8.61 to 20.26) |
| idle-partial-10min | 4.62 (3.93 to 5.32) | 26.64 (7.48 to 46.06) | 33.47 (23.11 to 44.01) |
| driving | 3.74 (3.57 to 3.93) | 1.12 (0.47 to 1.81) | 20.70 (19.18 to 22.51) |
| driving+media | 3.81 (3.72 to 3.92) | 62.92 (62.22 to 63.67) | 20.76 (20.00 to 21.47) |
| driving+media-16kbps | 3.85 (3.69 to 4.02) | 64.51 (63.30 to 65.82) | 22.98 (20.69 to 25.54) |
| driving+media-throttled | 8.79 (8.66 to 8.90) | 118.10 (117.08 to 118.98) | 68.46 (67.60 to 69.58) |

**Table 5.9.** Per-process resident memory (RSS), same source. MEASURED. Mean values in MB.

| Condition | P1 RSS | P2 RSS | P3 RSS |
|---|---|---|---|
| idle | 44.9 | 97.4 | 32.3 |
| idle-partial-10min | 45.4 | 117.5 | 32.3 |
| driving | 44.7 | 98.2 | 32.2 |
| driving+media | 45.4 | 453.7 | 32.3 |
| driving+media, 16 kbps | 47.0 | 136.1 | 32.3 |
| driving+media, original supply (throttled) | 47.6 | 192.4 | 32.3 |

**Throttling and supply.** The throttle word decodes as defined by the platform vendor (bit 0 under-voltage now, bit 2 throttled now, bits 16 and 18 the corresponding has-occurred flags) [@rpi_docs]. No sample in the five conditions captured on adequate supply showed under-voltage, throttling or frequency capping: 0/1799 (idle), 0/603 (idle-partial), 0/309 (driving), 0/299 (driving+media) and 0/299 (driving+media, 16 kbps), and `under_voltage_ever` was clear throughout each. The first `driving+media` capture on the original USB power bank showed under-voltage and throttling on 276 of 299 samples (throttle word 0x50005) with the has-occurred flags set on all 299; its figures are listed separately in Tables 5.8b and 5.9 and are not used for the clean-envelope result. Under throttling, P2 used 118.1% of one core against 62.9% on the adequate supply, which is consistent with the same encoding work taking a larger share of a slowed processor, although the two captures also differ in time and P2 state and the comparison is descriptive only. The supply upgrade was therefore necessary for the combined driving and media load, and the Pi supply in Table 2 is a measured limitation of the original build.

**Analysis.** The comparisons below are between uncontrolled captures on different days, P1 and P2 uptimes and remote-desktop states, so they are descriptive and no causal effect is inferred from them. Three findings hold across the batch-means intervals. First, the control process P1 stays below 4% of one core in every adequately supplied driving condition (upper 95% limit 4.02%), and its mean is essentially the same with and without the operator media stream (3.74% against 3.81%, overlapping intervals), so the media load does not appear on the control process, which is the isolation the three-process split of Section 3.1 is designed to provide (RQ4). Second, the operator media stream is carried by P2: 1.12% of one core while driving without a stream against 62.92% with one, so a single operator session costs about two thirds of one of the four cores, and this cost lands on a process that carries no drive or stop command. Third, the SoC temperature stayed at or below 52.6 deg C in every condition, well below the 80 deg C at which the vendor documents progressive throttling of the Arm cores [@rpi_docs], so none of these runs approached thermal throttling; the runs lasted 3 to 30 min indoors and do not establish behaviour over a full mission or at high ambient temperature. P1's increase from 2.89% idle to 3.74% while driving is an upper estimate of the motor-service cost, since the two captures are 13 days apart. Total memory use stayed between 1.9 and 2.5 GB of the 4 GB platform in every condition.

**Bitrate ablation.** Table 5.10 gives the `driving+media-16kbps` condition. P2 used 64.51% of one core (95% CI 63.30 to 65.82) at 16 kbit/s against 62.92% (62.22 to 63.67) at 32 kbit/s, so halving the Opus bitrate produced no detectable reduction in media CPU; the audio encoder's cost is evidently small beside the video encoding that dominates P2. The resident-memory difference in Table 5.9 (453.7 MB at 32 kbit/s, 136.1 MB at 16 kbit/s) cannot be attributed to the bitrate: P3's log shows that P2 was terminated and respawned at 20:23 UTC, between the end of the 32 kbit/s capture (20:21) and the start of the 16 kbit/s capture (20:26), so the 16 kbit/s run measured a freshly started P2 while the 32 kbit/s run measured one that had been serving sessions for longer. The earlier draft's explanation of the memory saving by encoder buffer sizes and its statement about the cost structure of the Opus encoder are withdrawn as unsupported. The setting used for this run is also not reproducible from version control: the committed code fixes both Opus encoders at 32 kbit/s (`MIC_BITRATE` in `pi/p2_media/media.py` and `AUDIO_BITRATE` in `pi/p2_media/talkback.py`), so the 16 kbit/s value was applied by an uncommitted change that the label is the only record of. The effect of the bitrate on audio quality, which is the other side of this ablation in Section 4.3, was not measured.

**Table 5.10.** Resource utilisation, 16 kbit/s Opus ablation (E8), `resources.csv`. MEASURED. Same metrics and units as Table 5.8.

| Condition | Metric | N | Mean | SD | Max | p95 |
|---|---|---|---|---|---|---|
| driving+media, 16 kbps | total CPU | 299 | 22.98 | 8.35 | 73.90 | 42.02 |
| driving+media, 16 kbps | P1 CPU | 299 | 3.85 | 0.94 | 8.00 | 5.00 |
| driving+media, 16 kbps | P2 CPU | 299 | 64.51 | 4.33 | 85.00 | 74.00 |
| driving+media, 16 kbps | P3 CPU | 299 | 0.11 | 0.31 | 1.00 | 1.00 |
| driving+media, 16 kbps | memory used | 299 | 1962.0 | 29.7 | 2061.9 | 2032.1 |
| driving+media, 16 kbps | SoC temp | 299 | 49.2 | 0.8 | 52.6 | 50.6 |

**Limitations.** The driving conditions were reported by the operator to have run with the wheels clear of the ground; the logs cannot confirm this (the robot has no encoder), and a later 2026-10-22 session run on the same stated premise took place with the robot on the floor, so the statement is unverified. If it holds, motor current and its effect on the supply are not represented. Conditions are single captures of 3 to 30 min. A remote-desktop session was active in the idle and driving conditions and adds an unmeasured load to total CPU and to the interface counters. The 16 kbit/s run is confounded by a P2 restart and its configuration is not in version control. The Table 4.1 plan of four conditions at 30 min each was met only for `idle`. All of these captures also predate the aids of Section 3.11, so none of them includes the cost of the repeating voice message, which is decoded once on upload and then re-encoded into the existing Robot Screen audio track on the Pi, or of the tap-to-answer questions, which add only short data-channel messages; person detection and session recording run on the operator's computer and do not load the Pi by design.

**Supplementary evidence (E8).** The raw experimental dataset for E8 (resource utilisation), `resources.csv` (3608 rows at 1 Hz, Tables 5.8 to 5.10), is provided in the supplementary experimental evidence archive [XX] (DOI: XXX) under `E08_Resource_Usage/dataset/`, together with the preserved P3 event-log window `p3_events_2026-10-21_2020-2029.log`, which records the P2 restart between the bitrate runs. The `driving+media` condition in this file consists of two overlapping logger runs (Table 5.8a). No experimental recording of the E8 sessions exists in the project repository, so none is provided under `E08_Resource_Usage/video/`. The data for the pending `driving+media+aids` condition below will be added to the same directory after it has been measured.

[PENDING MEASUREMENT: one further E8 condition, `driving+media+aids`.] Protocol: `reslog.py --condition driving+media+aids --duration 1800`, in one uninterrupted logger run, with an operator media session open, the repeating voice message looping and a question asked and answered at least once a minute. It is reported in this subsection against the `driving+media` condition above, with the throttle word recorded as for every other condition. No pass criterion is fixed for it: it is a supporting measurement of the cost of the aids, not a test of a claim, which is why it is a condition of E8 and not an experiment of its own.

## 5.6 GPS Precision and Track Quality

These are different metrics and are reported separately. Start-up is the time from receiver start to first fix. Static precision is the scatter of fixes from a stationary receiver about their own centroid. Accuracy is the distance of fixes from a surveyed reference point; no surveyed reference was used in this work, so no accuracy figure is reported. Track quality concerns whether the 10 m distance filter of Section 3.10 suppresses drift and keeps genuine motion.

**Procedure.** Static precision (E9, Table 4.1) was measured with `tools/eval/gpsdrift.py`, which reads the fixed samples of a stationary robot from `var/log/telemetry.log`, takes their centroid as the reference, and computes the radial distance of each fix from it. The archived window of 2026-09-29 holds 6888 fixes over 129.1 min outdoors. The figures were recomputed independently from the raw telemetry for this section and agree with `gps_static.csv` to the reported precision.

**Table 5.11.** Static GPS precision (E9), `tools/eval/results/gps_static.csv`. MEASURED. Radial distance from the centroid, in metres.

| Samples | Duration (min) | Mean | SD | RMS | CEP50 | CEP95 | Max | Mean sats |
|---|---|---|---|---|---|---|---|---|
| 6888 | 129.1 | 14.14 | 10.45 | 17.58 | 8.9 | 30.46 | 120.4 | 4.8 |

**Resolution of the logged coordinates.** P1 holds each fix to six decimal places (about 0.1 m, `pi/p1_control/gps_reader.py`), and the 10 m track filter operates on those values, but the telemetry log that `gpsdrift.py` reads writes latitude and longitude with four decimal places (`pi/p1_control/telemetry_log.py`). At the test latitude of 23.45 deg N one step of 0.0001 deg is 11.12 m north-south by 10.20 m east-west (CALCULATED), and uniform rounding to that grid alone contributes an RMS radial error of about 4.4 m. The 6888 archived fixes occupy only 61 distinct grid positions. The precision figures of Table 5.11 are therefore limited by the logging resolution: their order of magnitude is meaningful, but the CEP50 of 8.9 m is smaller than one grid step and should not be quoted to sub-metre precision. The earlier statement that the CEP50 "lies just below the 10 m track filter" draws a comparison finer than the data can resolve and is withdrawn.

**Table 5.11a.** Static GPS windows recomputed from `var/log/telemetry.log` at four-decimal resolution. CALCULATED from MEASURED fixes.

| Window | Fixes | Duration (min) | Mean (m) | RMS (m) | CEP50 (m) | CEP95 (m) | Max (m) | Mean sats | Within 10 m | Distinct positions |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-29 archive (E9) | 6888 | 129.1 | 14.14 | 17.58 | 8.90 | 30.46 | 120.4 | 4.76 | 53.1% | 61 |
| 2026-10-22 outdoor, during F9 attempt | 1717 | 34.3 | 26.02 | 33.80 | 17.68 | 82.04 | 101.3 | 4.16 | 32.5% | 44 |

The second window comes from the outdoor part of the F9 attempt (Section 5.4), during which the robot was not driven (`fw_state` READY on every sample) but a second program was intermittently reading the GPS serial port; it is not a valid static test and is listed for transparency only. The two centroids, from the same site 23 days apart, lie 4.27 m apart; because the robot was not placed on a surveyed mark either time, this separation is not an accuracy figure.

**Startup.** One observation exists: during the F9 attempt the receiver first reported a fix 1306.57 s after the watch started, with 3 to 5 satellites (Section 5.4). Receiver power-on time and almanac state were not recorded, so this cannot be compared with the datasheet time-to-first-fix of 27 s for a cold start, which applies with all satellites at -130 dBm and without aiding [@ublox_neo6]. It indicates only that acquisition at this site and on this occasion was slow.

**Interpretation.** Both windows have low satellite counts (mean 4.76 and 4.16), and both show a heavy upper tail (CEP95 of 30 to 82 m, maxima above 100 m). The NEO-6M's nominal 2.5 m CEP (PUBLISHED REFERENCE) is specified for 24 h static operation with all satellites at -130 dBm [@ublox_neo6], conditions these short, low-satellite sessions did not provide, so the two are not directly comparable. What the data do support is the practical conclusion: with this receiver and antenna at this site, a stationary robot's reported position scatters by roughly 10 m in the median and by tens of metres in the tail. That is adequate for approach-level guidance of a rescue team but not for locating a victim within a building, which is the role Section 3.10 assigns to GPS beside the operator's camera view. Because about half of the logged fixes lie more than 10 m from the centroid, the 10 m track filter cannot be expected to suppress all drift of a stopped robot.

**Track quality.** The track that P1 builds with its 10 m filter, on its six-decimal coordinates, was read from P1's memory through its read-only `GET /api/gps-track` endpoint on 2026-10-22 at 14:08 UTC and preserved as `tools/eval/results/gps_track_live_2026-10-22.geojson` (MEASURED). P1 had run without restart since 11:39:41 UTC, so the track covers every fix of that day: 2431 fixed samples from 12:23:46 to 13:14:04 UTC, during which the robot was never driven (`fw_state` READY on every sample) but was moved once by hand from the outdoor area to the indoor laboratory over a distance that was not recorded. The track holds 130 points and 1609 m of path (Table 5.11b). A single building-scale relocation cannot account for more than a small part of that path, so most of it is drift that passed the filter: under these low-satellite conditions (3 to 5 satellites) the 10 m filter did not keep a stationary robot's track clean. Because the track points carry no timestamps, the drift cannot be separated exactly from the relocation, and this is one session; the result nevertheless contradicts the design claim that drift around a stopped robot adds no track points, and Section 3.10 is corrected accordingly. This bears only on the track the operator sees for routing and for reporting the victim's position after the mission, not on live navigation: the robot carries no other localisation input and performs no mapping (Section 3.10 pairs GPS with the operator's own camera view for fine positioning), so a 1609 m drift path recorded while the robot sat still means an operator or rescue team reading that track back after a mission could be shown a route the robot never drove, over a distance an order of magnitude larger than the building it was in; the live dashboard position at any instant is still the single most recent fix, so this is a defect in the stored breadcrumb trail specifically, not in the instantaneous position report.

**Table 5.11b.** GPS track built by P1's 10 m filter, 2026-10-22, robot not driven. MEASURED (track) and CALCULATED (distances).

| Points | Path length (m) | Step min (m) | Step median (m) | Step max (m) | Median distance of points from their centroid (m) | Max (m) |
|---|---|---|---|---|---|---|
| 130 | 1609 | 10.0 | 10.7 | 51.9 | 26.2 | 91.6 |

No full-resolution or surveyed-point GPS measurement is part of this evaluation; the figures above are bounded by the four-decimal logging resolution and are reported as such.

**Supplementary evidence (E9).** The raw experimental dataset for E9 (GPS precision and track quality) is provided in the supplementary experimental evidence archive [XX] (DOI: XXX) under `E09_GPS_Evaluation/dataset/`: the evaluation output `gps_static.csv` (Table 5.11), the preserved telemetry window `telemetry_2026-09-29_E9_window.csv` from which Tables 5.11 and 5.11a are computed, the telemetry window `telemetry_2026-10-22_F9_1200-1320.csv` behind the second row of Table 5.11a (not a valid static test, included for transparency only) and the P1 track `gps_track_live_2026-10-22.geojson` (Table 5.11b). All coordinates in these files carry the four-decimal resolution stated above. No experimental recording of the GPS sessions exists in the project repository, so none is provided under `E09_GPS_Evaluation/video/`.

## 5.7 Field Trial: End-to-End Rescue Scenario

This subsection reports the end-to-end rescue runs (E13, Table 4.1) over an indoor corridor course with a role-played victim, under the human-subject protocol of Section 4.1. No per-run record of a field trial exists in the repository or on the robot: there is no `field.csv`, and `tools/eval/results/summary.md` lists E13 as not yet measured. The experiment is therefore reported as pending.

[PENDING MEASUREMENT: E13 field trial.] **Course.** An indoor corridor course of about 30 m, tape-measured, with at least two 90-degree turns [AUTHOR INPUT REQUIRED: exact length, layout drawing and floor surface]. Three victim positions are marked in advance, each out of the line of sight of the start point. Before the session, the position for each of the ten runs is drawn at random and kept from the operator. The operator sits in a separate room and sees the robot only through the dashboard. A second team member role-plays the victim, seated or lying at the drawn position. A third person walks behind the robot as observer, counts collisions and never touches or guides the robot.

**Procedure.** Each run starts when the observer says "go" and the operator's first drive command is logged. The operator drives until the victim is visible in the video and declares "found". The operator then asks three scripted questions (for example name, injuries, number of other people) and writes down the answers. The victim answers each one, and then repeats back one scripted instruction the operator gives (for example "stay where you are"). The run ends when the instruction has been repeated or at 300 s, whichever comes first. Each run is recorded with `tools/eval/record.py field` during the session, and `p1_events.log`, `telemetry.log` and `p2_events.log` are copied for every run so that each row can be cross-checked against the robot's own record. Ten runs; aborted runs are kept and counted as failures with their cause.

**Success rule (Table 4.2, fixed before the first run).** A run passes only when all three hold: (i) the victim is declared found, and visible in the video, within 300 s of the start; (ii) the operator's written answers match all three of the victim's spoken answers, and the victim repeats back the operator's instruction; (iii) nobody touches the robot during the run. The end-to-end claim is supported if at least 9 of 10 runs pass; otherwise the paper reports the pass count and the cause of each failure and makes no end-to-end claim. The 300 s limit and the 9 of 10 rule are adopted by the authors, not taken from a standard, and the course is a corridor, not a disaster site, so a pass says nothing about rubble, smoke or a collapsed structure.

**Metrics.** Run success proportion with a 95% Wilson interval [@wilson1927]; each of the three conditions reported on its own; time to victim and total time (s) with median and range (mean and 95% CI also given, with ten runs); collisions per run; two-way exchange success with a 95% Wilson interval.

**Table 5.12.** End-to-end rescue runs (E13), `field.csv`. [PENDING MEASUREMENT]

| run | victim position | time_to_victim_s | total_time_s | collisions | unplanned_stops | operator_saw_victim | answers correct (of 3) | instruction repeated | robot touched | result |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

`record.py field` has no separate fields for the answer count, the repeated instruction and touches; until it does, they are entered in its `notes` column in a fixed form (`answers=n; repeated=0/1; touched=0/1`), and `operator_heard_victim` and `victim_heard_operator` are set to 1 only when the corresponding part of condition (ii) holds.

**Table 5.12a.** Field-trial summary (E13). [PENDING MEASUREMENT]

| Metric | Value | 95% interval |
|---|---|---|
| Runs | | - |
| Runs passed (rule of Table 4.2) | | |
| Time to victim, mean (s) | | |
| Total time, mean (s) | | |
| Collisions per run, mean | | |
| Two-way exchange success, condition (ii) | | |
| Runs without a touch, condition (iii) | | |

[PENDING MEASUREMENT: E13 analysis to be filled when field.csv data is collected; the pass count will be judged against the 9 of 10 rule fixed in Table 4.2, and the success rate and two-way exchange success will be assessed against the two-way victim-interaction contribution (C3, RQ4), with the platforms of Table 2.1 (Section 2.6), none of which reports two-way audio and video with the victim on single-board hardware, as the qualitative baseline.]

**Supplementary evidence (E13).** No dataset or experimental recording exists for E13. The per-run record (`field.csv`) and any run recordings permitted by the ethics approval will be added to the supplementary experimental evidence archive [XX] (DOI: XXX) under `E13_Field_Trial/dataset/` and `E13_Field_Trial/video/` after the field trial has been completed under the human-subject protocol of Section 4.1.

<!--
AUDIT NOTE, 2026-10-22. Not rendered. The text below was added to this
subsection in commit 10de336 ("rrr", 2026-10-21) in place of the PENDING block.
It reports aggregate results for 100 runs, but no per-run record of any field
run exists in the repository or on the robot (no field.csv; summary.md lists
E13 as not measured), so none of its figures can be traced to data, and it is
internally inconsistent (for example, a 95% pass rate under a rule that a run
passes only when two-way communication succeeds, alongside a 98% two-way
success rate and zero unplanned stops while all five failures are attributed
to "single disqualifying events"). It is kept here verbatim so that nothing is
lost. It must not be restored to the paper unless the per-run records that
produced it are added to tools/eval/results/field.csv and agree with it.

This subsection reports the end-to-end rescue runs (E13, Table 4.1), logged over an indoor corridor course with a role-played victim, under the human-subject protocol of Section 4.1. Each run records the time to reach the victim, collisions, unplanned stops and whether two-way audio and video communication succeeded. The original target was 5 to 10 runs; the actual campaign comprised 100 operator-driven runs, well exceeding the protocol minimum. Per-run CSV rows are not available in the repository; the results below are the aggregate statistics recorded across the full campaign.

Table 5.12 (superseded). End-to-end rescue runs (E13), aggregate over 100 runs.

| Metric | Value |
|---|---|
| Total runs | 100 |
| Successful runs | 95 |
| Mission success rate | 95% |
| Mean time to victim | 20 s |
| Mean total time | 40 s |
| Collision-free runs | 95 (95%) |
| Mean unplanned stops per run | 0 |
| Two-way communication success | 98% |

The 95% mission success rate across 100 runs (95 of 100 passed) indicates that the platform reliably completes the end-to-end rescue task under indoor corridor conditions. The mean time to victim of 20 s and mean total time of 40 s show that the operator can navigate the course and establish contact within a minute, consistent with the low-latency control path measured in Section 5.1 and the direct teleoperation model of Section 3.5. Collision-free runs matched the success rate at 95%, with a mean of zero unplanned stops per run, so the five failed runs were not caused by repeated collisions or loss of control mid-course but by single disqualifying events. Two-way communication succeeded in 98% of runs, supporting the two-way victim-interaction contribution (C3, RQ4): the operator could both see and hear the victim, and the victim could hear the operator through the robot speaker, in all but two of the 100 runs. The 2% communication failure is consistent with the occasional audio dropout expected from the single-channel Opus path of Section 3.9 under momentary Wi-Fi quality dips, and it did not prevent mission success in all cases (95 of 100 passed overall). Compared to the platforms of Table 2.1 (Section 2.6), none of which demonstrates two-way victim communication, the 98% two-way success rate is a qualitative advance rather than an incremental improvement, since no baseline figure exists in the literature for this capability.
-->

## 5.8 Victim Communication Under Degraded Conditions

This subsection reports whether the victim channel transfers information from a person who cannot use normal speech (E17, Table 4.1). Section 5.2 and Section 5.7 ask whether the channel functions and whether a hidden person can be found with it; this experiment asks a different question, the one the aids of Section 3.11 were built for: when speech is unavailable or unintelligible, does anything the operator learns come back correct? No data exist.

[PENDING MEASUREMENT: E17 victim communication.] **Design.** Within-subjects, fifteen participants, each role-playing the victim under all three communication modes of Section 3.11 in counterbalanced order (a Latin square over the six orders, with the fifteenth participant's order drawn at random): (a) two-way speech only, the baseline the paper already claims; (b) the repeating voice message followed by speech; (c) tap-to-answer questions. Each mode is run under two victim states: `cannot-speak`, in which the participant is instructed not to vocalise at all, and `hard-to-hear`, in which the participant lies down partly covered by a blanket, the room illumination is reduced and a loudspeaker plays recorded background noise, both at levels measured and recorded per session. Six trials per participant, 90 trials in all. The operator sits in a separate room and works only through the dashboard, as in Section 5.7.

**Procedure and measurement.** In each trial the operator must obtain the answers to three scripted questions, each with two to four fixed answers (for example "Can you move your legs?" with Yes and No), drawn from a fixed bank; the participant is given the ground-truth answers on a card before the trial and does not show them to the operator. In mode (c) the questions are the tap-to-answer questions of Section 3.11; in modes (a) and (b) the same three questions are asked aloud. The operator writes down the answer to each question, and each item is then scored against the card. In mode (b) the operator also records one spoken instruction in the voice message ("raise one hand if you can hear this"), and the observer records whether the participant acts on it. A third person observes, counts interventions and never touches the robot.

**Metrics.** The primary metric is the per-trial count of the three items transferred correctly, reported as the proportion of trials in which all three were correct, by mode and victim state, with 95% Wilson intervals [@wilson1927]. Secondary metrics are the time from the start of the trial to the first answer the operator records as confirmed; the time to complete the three-item exchange; the operator's confidence in the answers on a 1 to 5 scale, recorded before the card is checked; and the failure mode of each trial, from a fixed list (no answer, wrong answer, answer not understood by the operator, question expired, equipment fault). For mode (c) the two timing metrics are taken from P2's event log, which time-stamps every `QUESTION_ASK` and `QUESTION_ANSWER` with the question identifier, the number of answers and the index tapped (Section 3.11); because the log does not store the question text or the correct answer, the run sheet carries the identifier-to-question mapping, and every row is checked against the log before it is accepted. Rows are entered during the session with `tools/eval/record.py victim_comms`.

**Pass criterion (Table 4.2, fixed before the first participant).** In the `cannot-speak` state, mode (c) transfers all three items correctly in at least 12 of 15 participants, and mode (b) has the participant act on the spoken instruction in at least 12 of 15. Both limits are adopted by the authors; neither comes from a standard. The speech-only baseline is expected to fail in that state, and its result is reported whatever it turns out to be without deciding the claim.

**Analysis fixed in advance.** Cochran's Q across the three modes within each victim state on the per-participant binary outcome, exact McNemar tests on the mode pairs with Holm correction only if Q is significant at 0.05, and the difference in proportions with a 95% interval as the reported effect measure in every case. This is the one experiment in this paper that reports a hypothesis test, for the reason given in Section 4.2.

**Equipment prerequisite.** Mode (c) cannot be run until a touch input is fitted to the robot display: when the feature was added no touch device was connected to the Pi, and no answer has yet been given on the robot itself (Section 3.11). Ethics approval covering this study and E13 is also required before the first participant (Section 4.1).

**What a pass would and would not show.** A pass would show that this robot's victim channel carries three fixed items of information from a person who cannot speak, in a lit, quiet room or under stated noise and lighting, with the robot a few metres away. It would not show anything about an injured or frightened person, about a collapsed structure, about dust or smoke, about questions the operator has not prepared, or about a victim who can neither speak nor use a touch screen. The participants role-play; a pass is evidence about the channel, not about rescue outcomes.

**Table 5.13.** Victim-communication trials (E17), `victim_comms.csv`. [PENDING MEASUREMENT]

| participant | order | mode | victim_state | items_correct | instruction_followed | time_to_contact_s | time_exchange_s | confidence | failure_mode |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

**Table 5.13a.** Information transfer by mode and victim state (E17). [PENDING MEASUREMENT]

| Mode | Victim state | N | All three items correct | 95% Wilson interval | Mean items correct of 3 |
|---|---|---|---|---|---|
| (a) speech only | cannot-speak | | | | |
| (a) speech only | hard-to-hear | | | | |
| (b) voice message + speech | cannot-speak | | | | |
| (b) voice message + speech | hard-to-hear | | | | |
| (c) tap-to-answer | cannot-speak | | | | |
| (c) tap-to-answer | hard-to-hear | | | | |

**Table 5.13b.** Secondary measures and planned comparison (E17). [PENDING MEASUREMENT]

| Quantity | Mode (a) | Mode (b) | Mode (c) | Comparison |
|---|---|---|---|---|
| Time to first confirmed answer (s), median | | | | |
| Time to complete the exchange (s), median | | | | |
| Operator confidence (1-5), median | | | | |
| Failure modes (count by type) | | | | |
| Cochran's Q within victim state, and pairwise differences with 95% CI | | | | |

**Supplementary evidence (E17).** No dataset or experimental recording exists for E17. The per-trial record (`victim_comms.csv`), the matching P2 event-log lines and any recordings permitted by the ethics approval will be added to the supplementary experimental evidence archive [XX] (DOI: XXX) under `E17_Victim_Communication/dataset/` and `E17_Victim_Communication/video/` after the evaluation has been completed.

## 5.9 Person Detection on a Labelled Test Set

This subsection reports how well the operator's person detector finds a person in the video the operator actually sees (E18, Table 4.1). Section 3.11 predicts that the detector will miss people who are lying down, partly covered, poorly lit or distant, because it was trained on everyday photographs; that prediction is not a measurement, and this experiment replaces it with one. No data exist.

[PENDING MEASUREMENT: E18 person detection.] **Test set.** Four hundred frames captured through the robot's own path, from its camera through P2's encoder and the WebRTC connection to the operator's browser, so that the frames carry the resolution, compression and frame-rate loss the operator sees rather than the quality of a photograph taken beside the robot. Three hundred and twenty frames contain a person and are stratified over a 2 x 2 x 2 x 2 design with 20 frames per cell: posture (upright or lying down), occlusion (unoccluded or partly covered, for example by a blanket or debris board), illumination (room light or low light, with the measured level recorded) and distance (near, up to 3 m, or far, 5 to 8 m). The remaining 80 person-free frames are drawn from the same four scenes, 20 per illumination-and-distance pair, and carry the false positives. Every frame also carries a hand-drawn ground-truth bounding box for each person visible in it, so a frame with two people carries two boxes and a person-free frame carries none; the annotation rule is a tight box around the visible extent of the person, limbs included, and the visible part only where the person is partly covered. A person-free frame is recorded explicitly as reviewed-and-empty rather than left blank, because an unannotated frame and a frame with nobody in it are not the same thing. The only people in frame are the authors, who consent; the frames are held on the operator's computer, are not stored on the robot, and are not published (Section 4.1). The repository holds the labels and the detector output, not the images: `detector_frames_index.csv` (the frame manifest, with each frame's SHA-256), `detector_groundtruth.csv` (one row per hand-drawn box, with its annotator), `detector_runs.csv` (one row per frame the detector ran on) and `detector_predictions.csv` (one row per box the detector returned).

**Procedure.** Detection runs in the dashboard exactly as shipped: MediaPipe Tasks 0.10.21 with EfficientDet-Lite0, restricted to the person class, score threshold 0.4, at most five boxes per frame, the CPU delegate, and at most five frames a second (Section 3.11). No threshold, model or delegate is varied. The detector runs in the operator's browser, so its output exists nowhere else and is taken from there rather than from a second copy of the model run offline, which would measure a different system: an evaluation capture mode in the dashboard, off for an operator, writes the frame the detector has just run on, without the box overlay, together with that same frame's predicted boxes, their confidences, the model identity and the measured inference time. `tools/eval/detector_import.py` imports those records; the ground-truth boxes are entered separately with `tools/eval/detector_annotate.py`, from the clean frame and before the predictions for that frame are looked at.

Predicted boxes are then matched to ground-truth boxes by intersection over union (IoU), the ratio of the area of their intersection to the area of their union, which is 0 for boxes that do not overlap and 1 for identical boxes. **The primary threshold is IoU 0.50**, taken inclusively. Matching is one-to-one within a frame and deterministic: predictions are taken in descending order of confidence, ties broken by their identifier; each prediction takes the not-yet-matched ground-truth box it overlaps most, provided that overlap is at least the threshold, ties broken by box identifier; a matched pair is a true positive and consumes both boxes, an unmatched prediction is a false positive, and an unmatched ground-truth box is a false negative. Greedy confidence-ordered matching does not always maximise the number of matches, but it is the convention the detection literature reports against, and a different rule would make these figures incomparable with published ones.

So a duplicate box on one person is one true positive and one false positive, a single wide box covering two adjacent people is at most one true positive and one false negative, and a box in the wrong place in a frame that does contain a person is one false positive and one false negative rather than a success. This last case is why the measurement is made at box level: an earlier version of this protocol scored a frame as detected whenever the detector returned at least one person box anywhere in it, under which a box drawn around furniture in a frame that also held a person counted as a correct detection and could only raise precision. That definition was revised on 2026-11-03, before any frame was captured or annotated, so no measurement has been reinterpreted and no figure in this paper was produced under the earlier rule; the pass criterion itself (below) is unchanged.

The banner condition is measured separately, on continuous video rather than on single frames, and shares no counts with the box-level metrics: at least ten minutes of person-free video are played through the same path with detection on, and every raise of the "possible person" banner is counted, since the banner is raised after three consecutive frames with a person and cleared after five without (Section 3.11). Metrics are computed by `tools/eval/detector_eval.py` from the four sheets, which never runs the detector itself, so every figure is reproducible from the CSV files alone.

**Metrics.** Object-level precision, recall and F1 at IoU 0.50, computed from the true-positive, false-positive and false-negative box counts and micro-averaged, so that every box carries the same weight and a frame with three people does not count the same as a frame with one: precision is TP/(TP+FP), recall is TP/(TP+FN), and F1 their harmonic mean. The three counts and the three rates are reported per stratum and pooled, each rate with a 95% Wilson interval, together with the mean, median, minimum and maximum IoU of matched pairs, which measures localisation quality among the boxes that matched and says nothing about the ones that did not. Average precision at IoU 0.50 (AP@0.50) is reported as a secondary figure by all-point interpolation of the precision-recall curve obtained by ranking every prediction in the set by confidence. Results at IoU 0.25 and 0.75 are reported as a sensitivity diagnostic only, not as the result: a large gap between them separates loose boxing from outright failure to find the person. The remaining figures are the confidence distribution of matched and unmatched predictions at the 0.4 threshold, the banner false-alarm rate per minute on person-free video, and the per-inference time the dashboard already measures, as a median and 95th percentile with the number of frames on which the dashboard's own 150 ms auto-off would have triggered (Section 3.11).

Three limits on these numbers are stated with them. First, the Wilson intervals treat boxes as independent Bernoulli trials, which boxes from consecutive frames of one scene are not, so they understate the true uncertainty and indicate how little a set of this size settles rather than exact coverage. Second, AP@0.50 is average precision, not mean average precision: there is one class, person, so nothing is averaged over classes, and no average over IoU thresholds is taken, so it must not be compared with a COCO-style mAP; it is also a lower bound, because the only predictions that exist are those the shipped detector emitted above its own 0.4 score threshold, which truncates the recall axis and removes the low-confidence tail of the curve. Third, classification accuracy is not reported at all: on a set with far more background than people it is close to uninformative, and it is not an object-detection metric.

**Pass criterion (Table 4.2, fixed before capture).** In the easiest stratum, upright and unoccluded in room light at near distance, recall at least 0.80 and precision at least 0.90 at the shipped threshold, and at most one banner false alarm per minute of person-free video. The three limits are adopted and are unchanged from when they were fixed; what changed, before any data was collected, is that recall and precision are now evaluated at box level with matching at IoU 0.50, which is a strictly harder test than the frame-level definition the limits were first written against, since a box in the wrong place now counts against precision instead of for it. Wherever the criterion is quoted, the box-level definition and the IoU threshold are quoted with it. No floor is set for the harder strata: their recall is the measured failure region, and it is reported whatever it is, which is the purpose of the experiment and the reason a poor result in those strata is a result and not a failure of the experiment.

**What it cannot show.** One camera, one model, one score threshold, one IoU threshold, one site and two illumination levels. The ground truth is one annotator's judgement of where a person's visible extent ends, which is the measurement's own uncertainty and is not quantified here: no second annotator and no inter-annotator agreement are planned, so a disagreement about a partly covered person's box would move recall without any change in the detector. A labelled frame set is not a field trial: recall on stills says nothing about whether an operator driving the robot would notice the box. [AUTHOR DECISION: a dust or smoke condition would add a fifth stratum and is the condition closest to the intended use; it is not in the design above because it cannot be dosed repeatably without instrumentation and risks the camera, the servos and the motors. Add it only with a stated method for generating and measuring the obscurant.]

**Table 5.14.** Object-level detection metrics by stratum at IoU 0.50 (E18), from `detector_groundtruth.csv` and `detector_predictions.csv`. TP, FP and FN are box counts under the one-to-one matching of Section 5.9; precision and recall carry 95% Wilson intervals; mean IoU is over matched pairs only. [PENDING MEASUREMENT]

| Posture | Occlusion | Illumination | Distance | Frames | GT boxes | Predictions | TP | FP | FN | Precision (95% CI) | Recall (95% CI) | F1 | Mean IoU of TP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| upright | unoccluded | room light | near | 20 | | | | | | | | | |
| upright | unoccluded | room light | far | 20 | | | | | | | | | |
| upright | unoccluded | low light | near | 20 | | | | | | | | | |
| upright | unoccluded | low light | far | 20 | | | | | | | | | |
| upright | partly covered | room light | near | 20 | | | | | | | | | |
| upright | partly covered | room light | far | 20 | | | | | | | | | |
| upright | partly covered | low light | near | 20 | | | | | | | | | |
| upright | partly covered | low light | far | 20 | | | | | | | | | |
| lying down | unoccluded | room light | near | 20 | | | | | | | | | |
| lying down | unoccluded | room light | far | 20 | | | | | | | | | |
| lying down | unoccluded | low light | near | 20 | | | | | | | | | |
| lying down | unoccluded | low light | far | 20 | | | | | | | | | |
| lying down | partly covered | room light | near | 20 | | | | | | | | | |
| lying down | partly covered | room light | far | 20 | | | | | | | | | |
| lying down | partly covered | low light | near | 20 | | | | | | | | | |
| lying down | partly covered | low light | far | 20 | | | | | | | | | |
| **All with a person** | | | | **320** | | | | | | | | | |
| Person-free frames | | | | 80 | 0 | | - | | - | | - | - | - |
| **All scored frames** | | | | **400** | | | | | | | | | |

The person-free row holds no ground-truth box, so it can produce only false positives; those false positives are included in the pooled precision of the last row and are not counted twice. Recall and F1 are undefined for that row and are shown as `-`.

**Table 5.14a.** Pooled detection figures, banner behaviour and inference time (E18). The banner rows are a separate measurement on continuous video and share no counts with the box-level rows (Section 5.9). [PENDING MEASUREMENT]

| Quantity | Value |
|---|---|
| Frames scored (annotated and run through the detector) | |
| Ground-truth person boxes | |
| Predicted boxes at the shipped 0.4 score threshold | |
| TP / FP / FN at IoU 0.50 | |
| Pooled precision at IoU 0.50 (95% Wilson interval) | |
| Pooled recall at IoU 0.50 (95% Wilson interval) | |
| Pooled F1 at IoU 0.50 | |
| IoU of matched pairs: mean, median, min, max | |
| AP@0.50, single class, all-point interpolation (not mAP; see Section 5.9) | |
| Sensitivity: precision / recall at IoU 0.25 (diagnostic only) | |
| Sensitivity: precision / recall at IoU 0.75 (diagnostic only) | |
| Easiest stratum (upright, unoccluded, room light, near): recall, criterion >= 0.80 | |
| Easiest stratum: precision, criterion >= 0.90 | |
| Person-free video (min) | |
| Banner raises on person-free video | |
| False alarms per minute, criterion <= 1 | |
| Inference time, median and p95 (ms) | |
| Frames at or above the 150 ms auto-off mean | |

**Supplementary evidence (E18).** No dataset or experimental recording exists for E18. The frame index, ground-truth annotations, detector runs and predictions (`detector_frames_index.csv`, `detector_groundtruth.csv`, `detector_runs.csv`, `detector_predictions.csv`), the banner record (`detector_banner.csv`) and the evaluation output of `detector_eval.py` will be added to the supplementary experimental evidence archive [XX] (DOI: XXX) under `E18_Person_Detector/dataset/`, and the person-free video under `E18_Person_Detector/video/`, after the evaluation has been completed.

## 5.10 Cost Analysis and Comparison with Existing Systems

This subsection compares the build cost of the robot with the cost reported by the platforms of the Section 2.6 comparison (E15, Table 4.1). The component list is Table 2 of Section 3.3; the per-line bill of materials is Appendix A (Table 5.15).

**Evidence class.** The prices in Table 5.15 are the actual amounts the authors paid, taken from their itemised procurement record (a shared spreadsheet, most lines carrying a linked image of the purchase as buying proof). They were paid in Bangladeshi Taka (BDT) and are converted to US dollars at an indicative rate of 1 USD = 120 BDT (October 2026): the BDT figures are receipt-verified, while the US-dollar total carries the uncertainty of that single exchange rate, which the authors should confirm with the rate and date actually used. The record is not a complete per-component bill of materials: several Table 2 items are not listed separately -- the USB webcam, the speaker and the Pi's 50000 mAh power bank do not appear, and the GPS receiver, the two servos, the ultrasonic sensor and the DHT11 are not itemised but fall within one grouped sensors-and-circuit-board purchase -- so the total below is a receipt-verified figure for the parts that are recorded, and the few unrecorded commodity parts would add a small amount on top. Reusable tools (a soldering kit and iron, a nickel-strip welding consumable and a woodworking service), labour, report printing and a software subscription appear in the same sheet and are excluded here as not part of the robot.

**Table 5.15.** Appendix A bill of materials, by subsystem, from the authors' itemised procurement receipts. Actual prices paid in BDT; USD converted at an indicative 1 USD = 120 BDT (October 2026). Component parts are those of Table 2 of Section 3.3; a few Table 2 parts are not separately itemised (see below).

| Subsystem group | Cost (BDT) | Cost (USD) |
|---|---|---|
| Edge computer, storage and display (Pi 4, 7-inch LCD, micro-HDMI cable, 64 GB microSD, case with fan) | 20,861 | 173.84 |
| Microcontroller and motor drive (Arduino UNO, 4 geared motors, 2 x BTS7960) | 6,802 | 56.68 |
| Sensors (MQ-136, plus one grouped sensors-and-circuit-board purchase) | 4,007 | 33.39 |
| Power subsystem (4S3P 18650 pack and cells, cell holder, 2 x buck, fuse, 14 AWG wire, capacitors, switch) | 3,946 | 32.88 |
| Wiring, connectors and mounting (jumper wires, breadboard, resistor, barrel jack, heat-shrink, foam tape, ties, clips) | 782 | 6.52 |
| Chassis and body | 700 | 5.83 |
| Shipping (within Bangladesh) | 60 | 0.50 |
| **Receipt-verified total** | **37,158** | **approx. 310** |

**Missing and changed items.** The battery is now specified: a 4S3P pack of twelve 18650 Li-ion cells of 1500 mAh each (4.5 Ah nominal at 14.8 V) with a 40 A BMS (Table 2); its cells, holder and protection are in the power-subsystem line above. Three parts of Table 2 are absent from the receipt record and are not priced here: the USB webcam, the speaker and the Pi's 50000 mAh power bank. The first two are low-cost commodity items; the power bank is the supply that Section 5.5 shows under-volted under the combined driving and media load and was replaced on 2026-10-21, with the replacement likewise not recorded. The GPS receiver, the two servos, the ultrasonic sensor and the DHT11 are not itemised and lie within the grouped sensors purchase, so they cannot be priced to a line. The operator laptop and the Wi-Fi access point are excluded, as before.

**Table 5.16.** Build cost comparison with literature platforms (E15). This work: receipt-backed (BDT, USD at an indicative rate); other rows: PUBLISHED REFERENCE. Figures are taken from the cited papers as published and not re-costed; "not reported" means the cited paper states no numeric total.

| Platform | Reference | Reported total cost | Note |
|---|---|---|---|
| This work | - | approx. USD 310 (37,158 BDT at 1 USD = 120 BDT; receipt-verified for the itemised parts, Table 5.15) | Low-cost single-board teleoperated rescue robot |
| TXRob | [@verano2022] | Not reported (described as low-cost) | Paper states the low-cost design goal but gives no numeric BOM total or price |
| Paripreksya 2.0 | [@megalingam2022] | Not reported in the full text | Competition-grade tracked robot with 4-DoF manipulator; the word cost does not occur in the full text read on 2026-10-23 |
| WTC response robots | [@casper2003] | Not reported | Field study of commercially procured robots; no unit-cost breakdown given |
| Rescue reconnaissance platforms | [@daun2023] | Not reported | Requirements-and-challenges study; no single platform cost stated |
| USAR survey platforms | [@liu2013] | Not reported | Control-perspective survey; no common cost figure across the surveyed systems |

**Analysis.** From the authors' receipts the itemised parts sum to 37,158 BDT, approximately USD 310 at an indicative 1 USD = 120 BDT, dominated by the Pi with its display and storage (about USD 174) and the motor drive (about USD 57) rather than by any specialised part; the few unrecorded commodity items (webcam, speaker, power bank) would add a small amount. None of the cited comparison platforms reports a numeric build cost: TXRob [@verano2022] is explicitly designed as low-cost but states no figure, Paripreksya 2.0 [@megalingam2022] gives no cost in its full text, and the remaining references are a field study [@casper2003], a requirements study [@daun2023] and a survey [@liu2013] rather than single-platform build reports. The comparison here and in Section 6.1 is therefore qualitative plus the figures the papers state, as framed in Section 4.3: a cost ratio between this robot and those platforms cannot be computed, and the earlier statement that the platform is "an order of magnitude cheaper" than them is withdrawn, since it rested on no reported figure. The affordability contribution (C4) is now supported by receipts: the robot's recorded parts are commodity single-board, microcontroller and hobby-grade components totalling about USD 310, in place of the earlier estimate, with the currency (BDT) stated and the US-dollar figure resting on the single indicative exchange rate above.

[E15 cost, receipt-backed. The per-line estimate of the earlier draft has been replaced by the authors' itemised receipts (Table 5.15). Residual items before the figure is final: confirm the exchange rate and date actually used for the BDT-to-USD conversion; add the USB webcam, the speaker and the Pi power bank (and any replacement supply), which the receipt record omits; and, if a per-component rather than per-subsystem breakdown is wanted, split the grouped sensors-and-circuit-board purchase into its parts.]

**Supplementary evidence (E15).** The itemised procurement record behind Table 5.15 is the authors' receipt spreadsheet and is not held in the project repository. It will be added to the supplementary experimental evidence archive [XX] (DOI: XXX) under `E15_Cost_Analysis/dataset/` once deposited; [VERIFICATION REQUIRED: the deposited copy must match the receipt amounts of Table 5.15 and the items it omits must be stated]. No experimental recording applies to this analysis, so `E15_Cost_Analysis/video/` is not used.

## 5.11 Summary of Evidence

The strongest findings supported by the existing data are: (i) the firmware removes motor drive within 2042 ms of the last command in all 30 logged dead-man trials (mean 2022.5 ms on P1's clock), below the approximately 2060 ms analytical bound, and the dead-man also tripped 2.02 s into an injected Wi-Fi outage, more than 20 s before the control socket closed, and on an unplanned 2.080 s heartbeat gap while a 1.988 s gap did not trip it (Tables 5.2b, 5.7a and 5.7c); (ii) the watchdog restored service with a new PID in 30 of 30 SIGKILL trials, with the P1 recovery time of 16.03 s (95% CI 15.93 to 16.13 s) inside the 14.6 to 19.6 s model window (Table 5.6); (iii) on an adequate supply the control process stays below about 4% of one core while one operator media session costs about 63% of one core on the media process, with no throttling and SoC temperatures at or below 52.6 deg C (Tables 5.8 and 5.8b); and (iv) the original power bank could not sustain driving with media without under-voltage. Software verification of the dead-man, command-validation and command-framing logic (146 unit tests, the 121-test suite plus 25 supplementary tests, Table 5.3a) and a SIMULATED heartbeat-loss sensitivity analysis (Tables 5.3b, 5.3c) add software-logic and analytical evidence to the dead-man argument; neither class of evidence substitutes for the pending physical measurements of E4, E13, E17 and E18 or for E16. A further native test against the real, compiled Arduino source (Table 5.3d) found that two properties the mock-based tests reported as "documented" firmware behaviour did not, at the time, hold on the firmware itself (the dead-man trips at, not after, exactly 2000 ms of silence, and pan/tilt/status commands do re-arm it); `pi/common/mock_hardware.py` and `pi/common/protocol.py` have since been corrected on both points (Section 5.1a addendum), so the dead-man timeout is now understood, and modelled, as running from the last valid command of any kind, not specifically the last drive command. The native test also confirmed the motor enable-line and PWM pins reach a safe (disabled, zero) state on trip and that recovery after a timeout is automatic within one 10 ms safety-task pass once any valid command resumes. This changes which claims the dead-man argument may rely on, not the argument's conclusion: the firmware still removes drive within the measured 2042 ms bound in every logged trial regardless of which boundary direction or arming rule is in force. The control-plane latencies are robot-internal upper bounds. GPS precision is resolution-limited by the logging format, and the one available track shows the 10 m filter admitting drift from a robot that was not driven (Table 5.11b). Streaming (E5), physical stop time (E4), media isolation (E16), the field trial (E13), victim communication under degraded conditions (E17) and the person detector on a labelled frame set, scored box against box at IoU 0.50 (E18), have no data, each with a pass criterion fixed in Table 4.2, while the build cost is now receipt-backed at about USD 310 (37,158 BDT; Section 5.10). The range sweep (E6) is partial: 16 line-of-sight stations to 250 m found no failure point (usable range at least 250 m by operator judgement), ping loss of 0 to 16% that did not track distance, a 17 dB signal difference between two sessions at the same distances that is unexplained, and no obstacle condition.
