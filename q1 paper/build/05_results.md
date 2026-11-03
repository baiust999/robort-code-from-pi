## V. RESULTS

### A. Firmware Stop Interval (RQ1)

*Procedure.* In the E1 session of 2026-10-21, the probe on the Pi drove the robot at PWM 150 and then stopped sending commands, 30 times. P1's event log time-stamps every command written to the Arduino, the firmware's acknowledgement (ACK) of it, and the PANIC line, all on one clock. Because the firmware emits the PANIC line in the same supervisor pass in which it zeroes the PWM outputs and disables the drivers (Section III-E), the arrival of that line marks the removal of drive, delayed only by serial transit. Every probe trial matched exactly one PANIC line.

**TABLE IX.** Dead-man interval on P1's clock, 2026-10-21, 30 trials. CALCULATED from MEASURED event-log timestamps. Values in ms.

| Interval | Mean | 95% CI | SD | Min | Median | Max |
|---|---|---|---|---|---|---|
| P1 sends last command -> P1 receives PANIC | 2022.5 | 2019.7 to 2025.3 | 7.5 | 2009.0 | 2024.0 | 2042.0 |
| P1 receives ACK of that command -> P1 receives PANIC | 2002.0 | 1998.7 to 2005.2 | 8.7 | 1986.0 | 2002.5 | 2022.0 |
| P1 sends last command -> P1 receives its ACK | 20.5 | 18.8 to 22.2 | 4.6 | 6.0 | 21.0 | 29.0 |

*Result.* The interval from the last command leaving P1 to the PANIC line arriving back never exceeded 2042 ms (Table IX), below the analytical bound of about 2060 ms of (1) in every trial, and it still includes serial transit in both directions. The interval from the firmware's ACK to its PANIC line, in which the return leg cancels, has a mean of 2002.0 ms, which agrees with the 2000 ms window; its spread of 1986 to 2022 ms shows that P1's receive timestamps carry jitter of about 15 ms from USB-serial buffering and event-loop scheduling, which is the resolution of this method. The same trials timed through the telemetry state field gave a mean of 2435.9 ms (SD 110.8 ms), and the difference of 356.8 ms between the two means agrees with the predicted mean reporting delay of about 350 ms on the slower confirmation path. These figures establish when the firmware removed drive. They do not observe the wheels: the wheel-stop time (E4) is [PENDING MEASUREMENT].

*Injected and unplanned link loss.* Two further observations come from outside the scripted probe. In fault F7 (2026-10-21), the Pi's `wlan0` interface was taken down for about 20 s while a dashboard held control. The last controller heartbeat reached the Arduino at 19:52:48.530 UTC and the PANIC line arrived 2.02 s later; P1 closed the dead WebSocket only 23.16 s after the last heartbeat, consistent with the keep-alive of Table II, and the dashboard reconnected 1.91 s after the close. The robot therefore stopped more than 20 s before the control socket closed, so liveness was enforced by the firmware, not the transport. On 2026-10-22, P1's forwarded heartbeats paused three times for reasons that were not recorded (Table X): gaps of 1.902 s and 1.988 s caused no trip, and a gap of 2.080 s produced a PANIC line at its end. On this sample of three gaps, the dead-man tripped when, and only when, the 2000 ms window was exceeded.

*Heartbeat interval actually delivered.* The dashboard is configured to send a heartbeat every 500 ms, and P1 forwards each without rate limiting, so the interval of heartbeats in P1's log is the interval the dashboard delivered. It was not constant (Table X): 0.50 s during the probe session, but 1.00 s in the minutes before F7 and before the unplanned gaps. The cause was not recorded; a browser throttling a background tab's timers is a candidate that was not tested. At 1.00 s a single lost heartbeat leaves 2000 ms of silence and trips the dead-man.

**TABLE X.** Heartbeats written to the Arduino, from P1's event log. MEASURED.

| Window (UTC) | Heartbeats | Median interval (s) | 10th-90th percentile (s) |
|---|---|---|---|
| 2026-10-21 11:40-12:30 (E1 probe session) | 5308 | 0.501 | 0.488-0.513 |
| 2026-10-21 19:51:00-19:52:49 (before F7) | 84 | 0.997 | 0.977-1.027 |
| 2026-10-22 12:01:30-12:03:07 | 192 | 0.502 | 0.375-0.618 |
| 2026-10-22 14:00:00-14:01:20 | 80 | 1.000 | 0.903-1.035 |
| Gaps of 1.9 s or more, 2026-10-22 12:00-14:02 | 1.902 s and 1.988 s: no trip; 2.080 s: PANIC at 14:01:17.616 | | |

*Supporting software evidence.* Two lines of non-physical evidence bear on the stop. First, the unmodified firmware sources were compiled natively with g++ against a host-side stub of the Arduino API and driven by tests (SOFTWARE-TEST, 10 test functions, 27 checks, all passed, 2026-10-22). The tests confirmed that the trip is inclusive at exactly 2000 ms, that all four PWM pins go to zero and the enable line goes low on trip, and that pan, tilt and status commands re-arm the timer. They also showed that the first command after a trip is rejected once and the fault clears in the next 10 ms supervisor pass. The Pi-side Arduino emulator used by the 121-test Pi suite had modelled the boundary and the re-arming rule differently; it was corrected to match the firmware, and the suite and 25 supplementary boundary tests passed afterwards. These are tests of software logic, not of the board. Second, Table XI gives the margin of the 2000 ms window against lost heartbeats. It is SIMULATED: the per-heartbeat loss probability is an assumed input, loss is modelled as independent with no jitter, and real Wi-Fi loss, which is often bursty, would trip the dead-man sooner at the same mean loss.

**TABLE XI.** Margin of the dead-man window against lost heartbeats. SIMULATED. Left: deterministic boundary analysis with the inclusive 2000 ms trip and no transit jitter. Right: Monte Carlo trip probability at the configured 500 ms period, 300 s missions, 50,000 trials per value, fixed seed.

| Heartbeat period (ms) | Consecutive losses tolerated | | Assumed per-heartbeat loss | Trip probability per 300 s mission |
|---|---|---|---|---|
| 200 | 8 | | 0.01 | 0.05% |
| 500 (configured) | 2 | | 0.05 | 6.84% |
| 1000 (observed in some sessions) | 0 | | 0.10 | 42.04% |
| 2000 | none (trips with no loss) | | 0.15 | 82.34% |

*Emergency-stop distance (E3), [VERIFICATION REQUIRED].* Twenty-three hand-entered stopping distances after an operator-pressed emergency stop give means of 42.7, 75.9 and 91.3 cm at PWM 60, 120 and 180. Two checks place them outside the evidence. P1's log contains the PWM 120 and 180 drive commands on the trial date but no PWM 60 command on that date. More decisively, with 60 RPM no-load motors and 65 mm wheels the no-load ground speed is 0.20 m/s, and the ramped stop of (2) from PWM 180 takes 120 ms and covers at most 2.5 cm (CALCULATED from the firmware constants); covering 78-98 cm would need 3.8-4.8 s of travel at full speed. The cause of the discrepancy cannot be resolved from the stored data, and no stopping-distance claim is made.

### B. Control-Plane Latency (RQ2)

Table XII gives the E1 command latencies over loopback. Each is an upper bound that can exceed the true latency by up to 700 ms. Only `hello_rtt`, the authentication round trip, does not wait on telemetry.

**TABLE XII.** Control-plane latency on the Pi over loopback, jittered sender, 30 trials per metric and session. MEASURED. Mean (95% CI) in ms.

| Metric | 2026-10-07 | 2026-10-21 |
|---|---|---|
| hello_rtt (no telemetry wait) | 46.8 (37.7 to 56.0) | 138.0 (115.7 to 160.3) |
| motor_start (drive -> state ACTIVE) | 328.2 (277.4 to 379.0) | 275.4 (251.9 to 298.9) |
| motor_stop (stop -> state READY) | 314.4 (284.5 to 344.2) | 302.9 (281.4 to 324.4) |
| pan_echo (pan -> new angle) | 387.7 (365.2 to 410.3) | 389.6 (359.8 to 419.4) |

The telemetry-confirmed means lie between 275 and 390 ms in both sessions, inside the 700 ms confirmation bound. The sessions agree for `motor_stop` and `pan_echo` but not for `hello_rtt`, whose mean rose from 46.8 to 138.0 ms with non-overlapping intervals; both sessions ran over loopback, so this reflects a change in processing on the Pi whose cause was not recorded, not a network effect. In the phase-locked control session the `motor_stop` median collapsed onto the 200 ms rebroadcast grid (400.7 ms, SD 19.9 ms against 80.0 ms jittered), which is the bias the jitter is designed to remove. No figure in this subsection includes Wi-Fi; no direct measurement of control latency over Wi-Fi is part of this evaluation.

### C. Fault Injection and Recovery (RQ3)

*Procedure.* On 2026-10-07 `faultinject.py` sent SIGKILL to P1 (test F3), P2 (F4) and P3 (F5), ten times each, polling the target's health endpoint about every 50 ms. Detection is the time to the first unhealthy observation; recovery is the time until the endpoint answers healthy with a new PID.

**TABLE XIII.** SIGKILL fault injection, 10 trials per target. MEASURED (times); CALCULATED (Wilson intervals).

| Test | Target | Detection mean (ms) | Recovery mean (s) | Recovery 95% CI (s) | Recovery SD (s) | Recovered | 95% Wilson interval |
|---|---|---|---|---|---|---|---|
| F3 | P1 | 91.1 | 16.03 | 15.93 to 16.13 | 0.14 | 10/10 | 72.2% to 100% |
| F4 | P2 | 123.2 | 14.45 | 13.76 to 15.14 | 0.96 | 10/10 | 72.2% to 100% |
| F5 | P3 | 157.0 | 12.83 | 12.18 to 13.48 | 0.90 | 10/10 | 72.2% to 100% |
| Pooled | | | | | | 30/30 | 88.6% to 100% |

All 30 trials recovered with a confirmed PID change, and P1's event log independently shows ten serial-port re-opens during the F3 campaign. Thirty successes bound the per-trial failure probability under these conditions below 11.4% at 95% confidence; they do not demonstrate long-run reliability. The P1 recovery mean of 16.03 s lies inside the 14.6-19.6 s window of (4) (PREDICTED), and its small SD is consistent with a path dominated by the fixed 10 s cooldown. P2 recovered faster than P1, consistent with P2 opening no serial link; P3 is restarted by systemd after 5 s, a different path. Detection times of 59 to 216 ms show that each outage was visible at the health endpoint within a fraction of a second; they do not measure P3's own detection. During each recovery window the dead-man holds the motors stopped once commands cease, so the outage is a loss of service, not of safety.

In the manual fault F6 (2026-10-21), the Arduino's USB device was unbound from its kernel driver, which removes the serial device as a cable pull would. P1 logged its first serial read failure and the watcher saw the serial flag go false 0.11 s later; P1 stayed up with the same PID and kept serving clients and telemetry. When the device was re-bound, the kernel assigned a new device node, and the serial link stayed down until P1 was restarted. Process supervision as built therefore covers crashes, not hardware faults. Hangs, camera and microphone loss and Robot Screen exit were not injected, and a GPS-loss attempt (F9) did not produce a valid controlled measurement.

### D. Resource Use on the Pi (RQ4)

*Procedure.* `reslog.py` logged, at 1 Hz, total CPU (percent of the four-core processor), per-process CPU (percent of one core), memory, SoC temperature and the firmware throttle word. Conditions: `idle` (no operator); `driving` (driven continuously over the control WebSocket by a scripted client, no operator media stream); `driving+media` (as `driving` with one operator video and audio session); `driving+media-16kbps` (Opus at 16 kbit/s); and `driving+media-throttled` (the first media capture, on the original power bank). The operator stated that the wheels were clear of the ground in the driving conditions; the logs cannot confirm this, so motor current may not be represented.

**TABLE XIV.** Resource use on the Pi. MEASURED; means with 95% batch-means intervals (CALCULATED). P1 and P2 in percent of one core; total in percent of the processor.

| Condition | Date | Rows (1 Hz) | P1 CPU | P2 CPU | Total CPU | SoC temp. max (deg C) | Under-voltage samples |
|---|---|---|---|---|---|---|---|
| idle | 2026-10-08 | 1799 | 2.89 (2.75-3.03) | 0.90 (0.88-0.92) | 14.44 (8.61-20.26) | 52.1 | 0 |
| driving | 2026-10-21 | 309 | 3.74 (3.57-3.93) | 1.12 (0.47-1.81) | 20.70 (19.18-22.51) | 51.6 | 0 |
| driving+media | 2026-10-21 | 299 (two logger runs) | 3.81 (3.72-3.92) | 62.92 (62.22-63.67) | 20.76 (20.00-21.47) | 51.6 | 0 |
| driving+media, 16 kbit/s | 2026-10-21 | 299 | 3.85 (3.69-4.02) | 64.51 (63.30-65.82) | 22.98 (20.69-25.54) | 52.6 | 0 |
| driving+media, original supply | 2026-10-21 | 299 | 8.79 (8.66-8.90) | 118.10 (117.08-118.98) | 68.46 (67.60-69.58) | 48.2 | 276 |

On an adequate supply, the operator media session is carried by P2: 1.12% of one core while driving without a stream against 62.92% with one, about two thirds of one of the four cores. P1 stayed below 4% of one core with and without media (3.74% against 3.81%, overlapping intervals), so the media load did not appear on the process that carries drive and stop commands, which is the isolation the process split is designed to give. Total memory use stayed between 1.9 and 2.5 GB of 4 GB, and the SoC stayed at or below 52.6 deg C in every condition, below the 80 deg C at which the vendor documents progressive throttling [@rpi_docs]. Runs lasted 3 to 30 min indoors, so they say nothing about a full mission or high ambient temperature.

Three properties of the data limit these figures. First, the `driving+media` rows come from two logger runs started 94 s apart under the same label, so the 299 rows span 196 s of wall-clock time with 103 s sampled twice; the two runs give P2 means of 63.01% and 62.87%, so the splice does not change the result, and the rows are reported as logged. Second, the original power bank showed under-voltage and throttling on 276 of 299 samples under the same load, with P2 at 118.1% of one core; that capture is excluded from the clean result, and the supply was replaced before the other media captures. Third, the 16 kbit/s run measured no detectable CPU reduction (64.51% against 62.92%), but it is confounded: P3's log shows P2 was terminated and respawned between the 32 kbit/s and 16 kbit/s captures, so the two runs measured P2 in different states, and the 16 kbit/s setting was applied by an uncommitted change that is not in version control. The effect of bitrate on audio quality was not measured.

### E. Wi-Fi Range (RQ2)

*Procedure.* At each line-of-sight station, `netsweep.py` on the Pi sent 100 ICMP echo requests at 0.2 s intervals to the router and logged loss, round-trip time (RTT), signal level and channel; the operator entered the distance and, from station N7 on, judgements of video (good, choppy, lost) and control (yes, degraded, no). The usable range was defined in advance as the largest distance with both judgements favourable and loss below 5%. Stations N1-N6 ran on 2026-10-22; N7-N10 and a repeat of the first six distances (R1-R6) ran on 2026-10-23 (Table XV).

**TABLE XV.** Wi-Fi range sweep, one 100-ping burst per station. MEASURED (loss, RTT, signal, channel); operator-entered (distance, judgements).

| Station | Distance (m) | Loss (%) | Mean RTT (ms) | Signal at start (dBm) | Channel | Video / control |
|---|---|---|---|---|---|---|
| N1-N4 | 5, 10, 15, 20 | 0, 0, 0, 0 | 3.4-5.7 | -39 to -41 | not logged | not recorded |
| N5, N6 | 25, 50 | 0, 0 | 4.8, 3.5 | -42, -41 | 3 | not recorded |
| N7 | 100 | 0.0 | 3.9 | -52 | 10 | good / yes |
| N8 | 150 | 1.0 | 12.6 | -55 | 10 | good / yes |
| N9 | 200 | 0.0 | 42.9 | -58 | 10 | good / yes |
| N10 | 250 | 6.0 | 16.6 | -60 | 10 | good / yes |
| R1-R6 | 5, 10, 15, 20, 25, 50 | 2, 2, 0, 8, 10, 16 | 5.0-11.9 | -55 to -60 | 10 | good / yes at all six |

The operator judged video good and control usable at every judged station, so by judgement alone the usable range is at least 250 m, and its upper limit was not reached. The loss criterion gives no single answer: loss exceeded 5% at 250 m and at 20, 25 and 50 m in the repeat session, while the 100-200 m stations lost 1% or less, so the passing stations are not contiguous and no range boundary follows. Loss did not track distance, and neither did signal level (the 5 m repeat station and the 200 m station both read -58 dBm). At the six distances measured twice, the first session showed 0% loss at about -41 dBm and the second 0-16% loss at -55 to -60 dBm, a difference of about 17 dB at 5 m that is larger than any change with distance within either session. The access point changed channel between the sessions, and its position, the robot's antenna orientation and neighbouring networks were not recorded, so the cause is unresolved. These figures are properties of this access point and site, not bounds on the robot, and ICMP loss to the router is not the loss rate of the control heartbeat. Every signal level lay between -39 and -60 dBm, so the dashboard's -70 and -80 dBm warning thresholds were never reached and remain uncalibrated.

### F. GPS and Sensors (RQ4)

*GPS static precision (E9).* `gpsdrift.py` computed the radial distance of each fix of a stationary robot from the centroid of the window, using 6888 fixes logged over 129.1 min outdoors on 2026-09-29 (Table XVI). No surveyed reference was used, so this is precision, not accuracy. The telemetry log stores latitude and longitude to four decimal places, which at the test latitude is a grid of 11.12 m by 10.20 m (CALCULATED); the 6888 fixes occupy only 61 distinct grid positions, and rounding alone contributes an RMS radial error of about 4.4 m. The figures are therefore limited by the logging resolution: their order of magnitude is meaningful, but the CEP50 is smaller than one grid step and should not be quoted to sub-metre precision. With a mean of 4.8 satellites the scatter has a heavy tail; the datasheet's 2.5 m CEP assumes 24 h static operation with strong signals [@ublox_neo6] and is not comparable.

**TABLE XVI.** Static GPS precision (E9), radial distance from the centroid, at the four-decimal resolution of the log. MEASURED.

| Fixes | Duration (min) | Mean sats | Mean (m) | RMS (m) | CEP50 (m) | CEP95 (m) | Max (m) | Within 10 m | Distinct positions |
|---|---|---|---|---|---|---|---|---|---|
| 6888 | 129.1 | 4.8 | 14.1 | 17.6 | 8.9 | 30.5 | 120.4 | 53.1% | 61 |

*Track filter.* The track that P1 builds with its 10 m filter on six-decimal coordinates was read from P1's memory on 2026-10-22, after 2431 fixed samples during which the robot was never driven but was carried once from the outdoor area into the laboratory over an unrecorded distance. The track held 130 points and 1609 m of path, with points a median of 26.2 m from their centroid. A single building-scale relocation cannot account for more than a small part of that path, so most of it is drift that passed the filter at 3 to 5 satellites. The filter reduces but does not prevent spurious track points, and a stored track read back after a mission can show a route the robot never drove. The live position on the dashboard is the latest fix and is not affected.

*DHT11 (E11).* At one indoor set-point the DHT11 read 31 deg C and 77-78% RH, which matches the telemetry log over the same period. The hand-entered reference readings equal the sensor readings on every trial for temperature, the same reading-equals-reference pattern found in the ultrasonic data below, and no independent record of the reference instrument exists, so the error figures are [VERIFICATION REQUIRED] and no accuracy is claimed.

*Gas sensor (E12).* Five consecutive butane releases from an unlit lighter about 5 cm from the MQ-136 raised the raw reading by 616 to 809 counts to peaks of 733 to 935 (clean air about 53 counts), and the warn threshold of 450 counts was crossed 1 to 4 s after release, at the 2 s resolution of the slow-sensor cycle. All tabulated values appear in the telemetry log in order. The sensor reports raw counts and responds to gases other than its target, so this shows only that the sensor and the dashboard alert respond to a nearby gas source within a few seconds; the five puffs in one session are not independent trials.

*Ultrasonic range (E10), [VERIFICATION REQUIRED].* Fifty hand-entered readings at five distances from 20 to 389 cm show zero error with zero variance, and the entered reading equals the entered tape distance in every row. The telemetry log over the session never shows 75, 150, 284 or 389 cm, and readings of 284 or 389 cm occur nowhere in the retained telemetry. No row is treated as a sensor reading.

### G. Cost (C4)

The itemized parts sum to 37,158 BDT, about USD 310 at an indicative 1 USD = 120 BDT (October 2026), from the authors' procurement receipts (Appendix A). The Pi with its display and storage (about USD 174) and the motor drive (about USD 57) dominate; no part is specialized. The record is incomplete: the USB webcam, the speaker and the Pi's power bank, and the replacement supply that Section V-D made necessary, are not on the receipts, and the GPS receiver, servos, ultrasonic sensor and DHT11 fall within one grouped purchase. The total therefore understates the full build by the price of those few commodity parts. None of the platforms in Table I other than Survivor Buddy's head reports a build cost, so no cost ratio is computed.

### H. Experiments Without Data

**TABLE XVII.** Planned measurements with no data, the claim each tests and its pass criterion, fixed before data collection. Limits marked "adopted" were chosen by the authors and are not properties of the robot or requirements of a standard. Each has a protocol in the repository. [AUTHOR DECISION: confirm the adopted limits before the first trial.]

| Item | What is missing | Claim tested | Pass criterion |
|---|---|---|---|
| E3 | Stopping distance, repeated with each stop logged by P1 and filmed at 240 fps | Operator stop within the calculated ramp bound (RQ1) | At PWM 180, <= 10 cm in at least 19 of 20 trials (simulated 2.4-8.7 cm plus reading resolution; adopted). Current data [VERIFICATION REQUIRED] |
| E10 | Ultrasonic accuracy, readings taken from the telemetry log | Range reading usable to judge clearance | Median absolute error <= 5 cm at 20, 50, 100, 150 and 200 cm (adopted) |
| E5 | Glass-to-glass video delay, audio delay each way, frame rate and packet loss, for 1 and 2 viewers and at 20 m | Two-way audio and video with the victim (C3, RQ4) | One viewer: median video delay <= 500 ms and median audio delay <= 400 ms each way (adopted) |
| E4 | Wheel-stop time after a dead-man trip, at 240 fps, on the floor at PWM 180 | Firmware stops the moving robot (C1, RQ1) | At rest within 2.5 s of the last command, PANIC logged, 20 of 20 (2060 ms bound plus 440 ms coast allowance; adopted) |
| E16 | Control latency with media off, media on, and P2 frozen by SIGSTOP | A media stall does not delay or drop control (C2) | With media on and with P2 frozen: 30 of 30 commands confirmed and motor-stop median within 50 ms of media off (adopted; detects blocking, not small shifts) |
| E13 | Field trial, 10 runs, corridor course of about 30 m, victim at one of three hidden positions drawn at random | End-to-end find-and-talk with a hidden person (C3, RQ4) | Run passes if the victim is found within 300 s, three scripted answers and one instruction pass correctly both ways, and nobody touches the robot; claim supported if at least 9 of 10 pass (adopted) |

The order of the remaining work follows from the evidence: the repeats of E3 and E10 come first, because tables the robot's own logs contradict must be resolved before new data is added; E5 next, as the only test of the media half of C3; E4 on a 240 fps camera; E16 in any session; and E13 last, after ethics approval.
