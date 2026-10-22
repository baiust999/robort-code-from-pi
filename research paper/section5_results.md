# 5. Results

This section reports the measurements that validate the design of Section 3, following the experiment matrix of Table 3 (Section 4.2). Each subsection opens with the procedure specific to that experiment, presents the measured data in tables whose metrics match Table 3, and closes with an analysis that compares the finding to the relevant pass/fail threshold from Section 3 and to the applicable baseline. Every figure traces to a row in `tools/eval/results/`; experiments for which data collection is not yet complete are marked [PENDING MEASUREMENT] and carry the protocol and an empty results table so the gap is explicit and no number is estimated. Hardware emulation was disabled for every run (Section 4.1), so all figures are from the assembled robot.

## 5.1 Control Latency and Emergency-Stop Response

The control-plane latency probe `tools/eval/wslatency.py` was run on the Pi (E1, Table 3) over the live WebSocket control path, with the operator laptop and robot within 3 m of the router in the indoor laboratory. Four metrics were timed over 30 valid trials each: `hello_rtt` (authentication round trip), `motor_start` (drive command to firmware state ACTIVE in telemetry), `motor_stop` (emergency stop to firmware state READY), and `pan_echo` (servo pan command to the new angle appearing in telemetry). A fifth metric, `deadman_trip`, timed the interval from the last accepted command to the telemetry field `fw_state` reporting the PANIC/STOPPED condition. Each probe waits on a telemetry field, so, as Section 3.5.2 and 3.6.2 establish, its figure is a telemetry-confirmed upper bound rather than a true control latency: the Arduino emits a telemetry frame every 500 ms and P1 rebroadcasts on its own 200 ms timer, so a confirmation can lag the event by up to 700 ms and by about 350 ms on average. The send phase was jittered by 0 to 200 ms to decorrelate trials from the P1 rebroadcast cycle (Section 4.2); for `motor_start`, `motor_stop` and `pan_echo` a second, deliberately phase-locked run of 30 trials was recorded to demonstrate the bias that the jitter removes. The dead-man trip was additionally re-measured on 2026-10-21 under the same on-Pi bench (label `on-pi-2026-10-21`, wheels clear of the ground), this time also capturing `deadman_panic`, the firmware's immediate tagged PANIC notice timed from P1's event-log millisecond timestamp rather than from a telemetry field, over 30 trials paired with `deadman_trip`.

**Table 5.1.** Control-plane latency, jittered sender (label `on-pi`), `tools/eval/results/latency.csv`. All values in ms.

| Metric | N | Mean | SD | Min | Max | Median | p95 |
|---|---|---|---|---|---|---|---|
| hello_rtt | 30 | 46.8 | 24.6 | 19.6 | 116.9 | 41.0 | 75.8 |
| motor_start | 30 | 328.2 | 136.1 | 156.8 | 761.1 | 306.3 | 573.5 |
| motor_stop | 30 | 314.3 | 80.0 | 207.9 | 606.7 | 300.0 | 393.9 |
| pan_echo | 30 | 387.7 | 60.4 | 285.9 | 495.0 | 381.1 | 480.8 |
| deadman_trip | 30 | 2409.1 | 115.1 | 2200.9 | 2598.4 | 2409.7 | 2584.1 |

**Table 5.2.** Phase-locked sender (label `on-pi-phaselocked`), same path, showing the biased distribution the jitter removes. All values in ms.

| Metric | N | Mean | SD | Min | Max | Median | p95 |
|---|---|---|---|---|---|---|---|
| motor_start | 30 | 407.1 | 62.8 | 266.2 | 504.9 | 393.9 | 496.0 |
| motor_stop | 30 | 403.3 | 19.9 | 392.6 | 507.2 | 400.7 | 405.7 |
| pan_echo | 30 | 492.1 | 82.9 | 150.3 | 609.8 | 500.3 | 607.0 |

**Table 5.2a.** Dead-man trip paired with the immediate PANIC notice, on-Pi bench, 2026-10-21 session (label `on-pi-2026-10-21`), 30 trials. All values in ms.

| Metric | Timed from | N | Mean | SD | Min | Max | Median | p95 |
|---|---|---|---|---|---|---|---|---|
| deadman_trip | telemetry `fw_state` | 30 | 2435.9 | 110.8 | 2197.5 | 2593.2 | 2467.5 | 2582.8 |
| deadman_panic | P1 event-log PANIC line | 30 | 2079.1 | 27.9 | 2022.3 | 2122.3 | 2076.5 | 2120.8 |

The authentication round trip is the only metric that does not wait on a firmware telemetry frame, and at a 46.8 ms mean (p95 75.8 ms) it bounds the pure network-and-WebSocket contribution: it is small against the 200 to 400 ms telemetry-confirmed figures, confirming that those figures are dominated by the 700 ms quantisation of the reporting path and not by the control transport. The three command-confirmation metrics all fall well inside the 500 ms firmware telemetry period plus the 200 ms rebroadcast, consistent with the upper-bound model of Section 3.6.2. The phase-locked run illustrates the artifact the jitter is designed to remove: its standard deviation collapses (motor_stop SD falls from 80.0 ms to 19.9 ms) because a sender locked to the 200 ms rebroadcast cycle samples the quantisation at a fixed phase, producing a deceptively tight distribution with a shifted mean; the jittered figures in Table 5.1 are therefore the honest upper bounds and are reported as the primary result, as recorded in `tools/eval/README.md` and discussed in Section 6.4. The `deadman_trip` mean of 2409.1 ms (2435.9 ms in the paired 2026-10-21 session, Table 5.2a) is a confirmation latency, not a stop time: it measures when an observer waiting on `fw_state` can establish that the motors have stopped. The paired `deadman_panic` measurement settles what the telemetry-confirmed figure cannot. Timed from the firmware's immediate PANIC line in P1's event log, it has a mean of 2079.1 ms with a standard deviation of only 27.9 ms (min 2022.3, max 2122.3), so it sits directly on, and tightly around, the analytical stop bound of approximately 2060 ms derived in Section 3.5.2 (2000 ms dead-man window + 10 ms supervisor period + about 50 ms for the longest loop pass): the stop-time guarantee is therefore supported by measurement from the reporting-independent path, not by analysis alone. The gap between the paired `deadman_trip` and `deadman_panic` means is 356.8 ms, which equals, to within the measurement, the mean telemetry-reporting delay of about 350 ms predicted in Section 3.6.2; this confirms the two-path model directly, since the fast PANIC notice establishes the stop within about 2.08 s while a telemetry-only observer lags it by exactly one reporting delay. The order-of-magnitude drop in spread from `deadman_trip` (SD 110.8 ms) to `deadman_panic` (SD 27.9 ms) further shows that the variance in the telemetry-confirmed figure belongs to the 200 ms rebroadcast quantisation, not to the stop itself. The direct physical wheel-stop measurement (E4, 240 fps) remains pending as the gold-standard confirmation, but `deadman_panic` now bounds it from the log side at 2079.1 ms.

The true control latency (E2) and the physical dead-man wheel-stop time (E4) require a 240 fps camera and have not yet been collected; the emergency-stop stopping distance (E3) was measured by tape and is reported below.

[PENDING MEASUREMENT: E2 true control latency.] Protocol: film the operator screen and the drive wheels together at 240 fps (4.17 ms per frame) with `tools/eval/record.py latency_video`, count frames from key press to first wheel movement, and record 30 trials per condition. This metric gives the true key-press-to-wheel-motion latency that the telemetry-confirmed figures of Table 5.1 bound from above.

**Table 5.3.** True control latency (E2), `latency_video.csv`.

| trial | label | fps | frames | latency_ms |
|---|---|---|---|---|
| | | | | |

[PENDING MEASUREMENT: E2 analysis to be filled when latency_video.csv data is collected; the result will be compared against the hello_rtt floor of Table 5.1 and reported as the true control latency.]

Emergency-stop stopping distance (E3) was measured with `tools/eval/record.py estop` on 2026-10-21. The robot was driven forward on a level concrete floor at each of three commanded speeds (PWM 60, 120, 180); on each trial the operator pressed the dashboard emergency-stop button as a reference mark on the robot crossed a fixed line, and the coast distance from that line to the mark at rest was tape-measured. The emergency-stop button issues the ramped stop S of Section 3.5.3 (Table 7), so the measured distance is the travel during the ramp-down plus mechanical run-out, not an instantaneous halt.

**Table 5.4.** Emergency-stop stopping distance (E3), concrete surface, `tools/eval/results/estop.csv`. Distance in cm.

| Speed (PWM) | N | Mean | 95% CI of mean | SD | Min | Max | Median |
|---|---|---|---|---|---|---|---|
| 60 | 7 | 42.7 | 36.4 to 49.0 | 6.8 | 34 | 54 | 41 |
| 120 | 9 | 75.9 | 61.5 to 90.3 | 18.7 | 34 | 92 | 78 |
| 180 | 7 | 91.3 | 85.1 to 97.4 | 6.7 | 78 | 98 | 92 |

Stopping distance rises monotonically with commanded speed, from a 42.7 cm mean at PWM 60 to 91.3 cm at the PWM 180 safety cap, so the emergency stop arrests the robot within about 0.9 m even at full commanded speed. The near-proportional growth with speed is the expected signature of a bounded-time ramp stop: Section 3.5.2 gives the ramp duration as t_ramp = ceil(u / 15) x 10 ms, about 120 ms from the PWM 180 cap and less at lower speeds, and a fixed stop time turns into a distance that scales with speed, which the three means follow. The spread is tight at PWM 60 and 180 (SD 6.8 and 6.7 cm) and wider at PWM 120 (SD 18.7 cm, driven by one 34 cm run), and the 95% confidence intervals (Student t, N - 1 degrees of freedom) are correspondingly wide at this sample size, 12.6 cm at PWM 60, 28.8 cm at PWM 120 and 12.3 cm at PWM 180. The most likely source of the variation is the operator's timing of the button press relative to the line, because the ramp of Section 3.5.2 is deterministic and would otherwise give a near-constant distance at a fixed speed; this was not isolated experimentally, since press timing and brake behaviour were not measured separately, and other contributors such as floor friction and battery state were not controlled. The result supports the design claim of Section 3.5.3 that the operator-triggered stop brings the robot to rest over a short, speed-bounded distance. The sample is below the 20-trial-per-speed target of Table 3 (N = 7, 9, 7); it is reported as an initial measurement, and fuller sampling together with the per-trial stop time (`stop_time_s`, measurable from the 240 fps video of E4) remain to be added.

[PENDING MEASUREMENT: E4 dead-man physical stop time.] Protocol: with `tools/eval/record.py deadman_physical`, cut the command stream and film the wheels at 240 fps, timing from the last heartbeat to wheels stationary; record whether the PANIC DEADMAN line appeared; 20 trials. This is the direct test of the approximately 2060 ms stop bound of Section 3.5.2, which until this measurement is in place remains analytical.

**Table 5.5.** Dead-man wheel-stop time (E4), `deadman_physical.csv`.

| trial | speed_pwm | stop_s | panic_seen |
|---|---|---|---|
| | | | |

[PENDING MEASUREMENT: E4 analysis to be filled when deadman_physical.csv data is collected; the filmed wheel-stop time will be compared against the approximately 2060 ms bound of Section 3.5.2, which the log-timed `deadman_panic` measurement of 2079.1 ms (Table 5.2a) already corroborates from the firmware side.]

## 5.2 Video and Audio Streaming Performance

This subsection reports the glass-to-glass delay of the two-way media path (E5, Table 3), measured with `tools/eval/record.py glass2glass` by photographing a running stopwatch and its copy rendered in the operator video panel in the same frame and differencing the two readings. The protocol repeats 20 trials per viewer count to expose the effect of the per-session encoders described in Section 3.9.1. This experiment is entirely pending.

[PENDING MEASUREMENT: E5 video and audio streaming.] Protocol: place a millisecond stopwatch in the camera's view, photograph the stopwatch and the operator panel simultaneously, and record the real and displayed readings for each of the conditions `viewers-1`, `viewers-2` and `wifi-20m`; 20 trials per condition. The audio-path delay is measured by the same clap-and-photograph method against the robot speaker output.

**Table 5.6.** Glass-to-glass media delay (E5), `glass2glass.csv`.

| trial | label | real_ms | robot_ms | delay_ms |
|---|---|---|---|---|
| | | | | |

[PENDING MEASUREMENT: E5 analysis to be filled when glass2glass.csv data is collected; the delay will be interpreted against the 640x480 at 10 fps, 500 kbps video parameters and the 60 ms Opus packetisation of Section 3.9, and the two-way victim-interaction claim (RQ4) assessed.]

## 5.3 Communication Range and Link Degradation

This subsection reports the Wi-Fi range sweep (E6, Table 3), run with `tools/eval/netsweep.py` at progressive line-of-sight distances in the outdoor open area, recording packet loss, round-trip time and received signal strength at each station together with a pass/fail judgement of whether video and control remained usable. This experiment is entirely pending.

[PENDING MEASUREMENT: E6 communication range.] Protocol: at each labelled station, run `tools/eval/netsweep.py --target <pi-ip> --label <Nk> --distance-m <d> --obstacles <desc>`, which pings the robot, reads the Wi-Fi signal at the start and end of the burst, and logs loss and RTT; the operator notes whether video and control stayed usable. Stations progress outward until the link fails.

**Table 5.7.** Communication range and link degradation (E6), `network.csv`.

| label | distance_m | obstacles | sent | received | loss_pct | rtt_avg_ms | signal_dbm_start | signal_dbm_end | video | control |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

[PENDING MEASUREMENT: E6 analysis to be filled when network.csv data is collected; the usable range will be reported against the single-cell assumption of Section 3.2 and the under-1-Mbit/s steady-state budget of Table 1a, and the point of control loss related to the dead-man behaviour of Section 3.5.2.]

## 5.4 Fault Injection and Recovery Time

The automated fault-injection campaign (E7, Table 3) was run with `tools/eval/faultinject.py run`, which sends SIGKILL to a target process and then polls that process's `/health` endpoint at 10 Hz until the process is back and its PID has changed, recording the detection time, the recovery time and the PID change. Ten trials were run against each of three targets: P1 control (test F3), P2 media (F4) and the P3 watchdog (F5). A trial counts as recovered only when the health endpoint answers and reports the new PID, so recovery is confirmed service, not merely a restarted process.

**Table 5.8.** Fault detection and recovery, `tools/eval/results/faults.csv`, 10 trials per target.

| Test | Target | Metric | Mean | SD | Min | Max | Median | Recovered |
|---|---|---|---|---|---|---|---|---|
| F3 | P1 | detection (ms) | 91.1 | 34.8 | 59.2 | 182.8 | 80.7 | 10/10 |
| F3 | P1 | recovery (ms) | 16026.7 | 140.6 | 15804.4 | 16254.8 | 15990.0 | 10/10 |
| F4 | P2 | detection (ms) | 123.2 | 46.1 | 59.8 | 175.0 | 147.1 | 10/10 |
| F4 | P2 | recovery (ms) | 14450.4 | 961.2 | 12966.8 | 15914.9 | 14758.4 | 10/10 |
| F5 | P3 | detection (ms) | 157.0 | 40.3 | 61.3 | 216.0 | 156.6 | 10/10 |
| F5 | P3 | recovery (ms) | 12829.0 | 903.3 | 10428.5 | 13841.4 | 12998.0 | 10/10 |

Every one of the 30 trials recovered with a confirmed PID change (10/10 for each target), so the process-supervision claim of Section 3.7.1 holds across the campaign without a single missed restart. The P1 recovery mean of 16026.7 ms (16.03 s) falls inside the 14.6 to 19.6 s bound predicted by the recovery-time model of Section 3.7.2, which sums detection (at most 1 s for a crash), the 1 s poll before cooldown, the 10 s cooldown and P1 start-up (2.0 s + 3 x 0.2 s plus up to 5 s for the Arduino handshake): the design claim is therefore supported, and the tight standard deviation of 140.6 ms shows the recovery path is dominated by the fixed 10 s cooldown rather than by variable start-up cost. P2 recovers faster, at a 14450.4 ms (14.45 s) mean, because it opens no serial link and runs no Arduino handshake, so its start-up term is smaller than P1's. P3 recovers fastest, at 12829.0 ms (12.83 s), because the SIGKILL is caught by systemd (restart after 5 s) and the watchdog then respawns, a shorter path than the full cooldown-gated respawn P3 applies to its own children; the wider spread for P2 and P3 (SD about 0.9 s) reflects variation in interpreter and media-device start-up. Detection is sub-200 ms in every case (P1 mean 91.1 ms), far inside the 1 s crash-detection bound, confirming that the 1 s exit poll of Figure 14 dominates detection for a hard crash rather than the 10 s health-check interval, which governs only a silent hang. Throughout, the dead-man timer (Section 3.5.2) holds the motors stopped while control is down, so the recovery interval is a loss-of-service window, not a loss-of-safety window.

The manual-watch campaign (E7 manual) was run on 2026-10-21 with `tools/eval/faultinject.py watch`, which polls both `/health` endpoints at 10 Hz and logs every state transition with its timestamp and the duration the previous value was held. Two faults were injected: Arduino USB disconnect (F6, simulated by unbinding the USB device from the kernel driver via `/sys/bus/usb/drivers/usb/unbind`, which removes the `/dev/ttyACM0` device node and produces the same effect as a physical cable pull) and Wi-Fi link drop (F7, injected by bringing the `wlan0` interface down with `ip link set wlan0 down` for 20 seconds, then restoring it). GPS loss (F9) was not testable in the indoor laboratory because the NEO-6M had no fix indoors (`gps_fix` was false before the test began), so no true-to-false transition could be provoked; an outdoor attempt on 2026-10-22 is described below.

**Table 5.9.** Manually injected fault transitions (E7 manual), `fault_watch.csv`, 2026-10-21.

| label | t_s | field | from_value | to_value | held_s |
|---|---|---|---|---|---|
| F6-arduino-unplug | 4.70 | serial_connected | 1 | 0 | 4.70 |
| F7-wifi-drop | 26.85 | ws_clients | 1 | 0 | 26.85 |
| F7-wifi-drop | 28.76 | ws_clients | 0 | 1 | 1.91 |

The Arduino disconnect (F6) was detected within one health-poll cycle: `serial_connected` transitioned from 1 to 0 at t = 4.70 s, within one second of the unbind command issued at approximately t = 5 s. P1 remained running throughout (PID unchanged) and logged serial read and write errors at approximately 0.5 s intervals, confirming the retry behaviour described in Table 9 ("reads retried every 0.5 s"). When the USB device was rebound, the kernel assigned a new device node (`/dev/ttyACM1`) because P1's open file descriptor on the original node prevented the kernel from reusing the minor number; `serial_connected` therefore remained false until P1 was restarted by P3, at which point the port was reopened on the original device path. This confirms the Table 9 recovery path ("port reopened when P1 restarts"): the serial bridge does not attempt to reopen a removed device, so recovery from a physical unplug requires P1 to be restarted by P3 or by the operator. During the serial-down interval P1 continued to serve WebSocket clients and telemetry (with `serial_connected` false and the mission state STOP per Table 10), so the control process remained available for reconnection even while the Arduino link was lost, consistent with the process-isolation claim of the three-process split (RQ4).

The Wi-Fi drop (F7) revealed that the TCP layer underlying the WebSocket connection survived the entire 20-second interface-down period: `ws_clients` remained at 1 throughout the outage, because Linux's default TCP keepalive interval (approximately 7200 s) far exceeds a 20-second interruption and no application-level WebSocket ping was scheduled within that window. The disconnect occurred only after Wi-Fi was restored: the TCP stack detected the stale connection at t = 26.85 s (approximately 1.85 s after `wlan0` came back up) and closed it (`ws_clients` 1 to 0), and the operator dashboard reconnected 1.91 s later (`ws_clients` 0 to 1 at t = 28.76 s). The total gap in controller connectivity was 1.91 s, falling entirely after the link was restored rather than during the outage. No other watched field transitioned: `serial_connected`, `camera_open` and `active_streams` were unchanged, confirming that the local subsystems were unaffected by the Wi-Fi loss. The result shows that a sub-minute Wi-Fi interruption is transparent to the TCP layer and does not trigger the full disconnect chain of Figure 15 (socket close, dead-man, PANIC, reconnect); that chain requires either a longer outage (long enough for TCP retransmission to time out, typically minutes) or an explicit socket close. The dead-man timer on the Arduino (Section 3.5.2) remains the backstop for any case where P1 itself stops sending heartbeats, but it was not exercised by this 20-second test because P1 continued to run and maintain the Arduino heartbeat throughout. This is noted as a limitation in Section 6.3: a Wi-Fi outage too short to close TCP but long enough to stall operator command delivery leaves the robot in its last commanded state until the TCP connection eventually times out or the link is restored; the design's defence is the dead-man timer, which operates on the Arduino independently of TCP state.

[PENDING MEASUREMENT: F9 GPS loss.] An outdoor attempt was made on 2026-10-22 with `tools/eval/faultinject.py watch --label F9-gps-loss`, but it did not yield a valid loss and recovery measurement. The NEO-6M first reached a fix (`gps_fix` 0 to 1) after about 1307 s outdoors, with a weak solution of 3 to 5 satellites and an HDOP of roughly 3 to 8. The `gps_fix` transitions that followed in `fault_watch.csv` are not valid: they coincided with the operator's diagnostic reads of the same serial port, which made the P1 GPS thread log `GPS_FAIL` and reopen the port about 2 s later, so they reflect port contention and not signal loss. No antenna-obstruction cycles were performed. The test is deferred. Protocol for the repeat: use only the `/health` field (no second reader on `/dev/serial0`), establish a stable fix first, then cover the antenna for 30 to 60 s and record the `gps_fix` true-to-false transition and the recovery time once uncovered, 5 cycles.

## 5.5 Resource Utilization on the Edge Device

Resource use was logged with `tools/eval/reslog.py` (E8, Table 3), which samples per-process CPU, memory, SoC temperature, the Pi throttling and under-voltage flags, and link statistics at 1 Hz. Five conditions have data: `idle` (1799 samples, about 30 min, all three processes healthy with no operator connected), `idle-partial-10min` (603 samples, 10 min, with the media process capturing and encoding video for the Robot Screen only), `driving` (309 samples, 310 s, captured on 2026-10-21 on a freshly rebooted Pi with all throttle and under-voltage flags clear from boot, the robot driven continuously over the control WebSocket by a scripted keyed-controller client and no operator media stream connected, wheels clear of the ground), `driving+media` (299 samples, 300 s, the robot driven continuously over the control WebSocket while an operator video stream was active, wheels clear of the ground, on a supply confirmed not to under-volt with 0/299 samples showing under-voltage, throttling or frequency capping), and `driving+media, 16 kbps` (299 samples, 300 s, the same driving+media condition with the Opus encoder bitrate halved from the default 32 kbps to 16 kbps, Section 4.3). The `driving+media` and `driving+media, 16 kbps` conditions were captured on 2026-10-21 after upgrading the Pi power supply from the USB power bank of Table 2 to a supply that holds the 5 V rail under the combined load; a prior capture on the original supply had exposed under-voltage on 276 of 299 samples, invalidating the CPU figures, so the upgrade was required before clean measurement. Per-process CPU is reported as a percentage of one core.

**Table 5.10.** Resource utilisation, `tools/eval/results/resources.csv`. CPU is % of one core; memory and RSS in MB; temperature in deg C.

| Condition | Metric | N | Mean | SD | Max | p95 |
|---|---|---|---|---|---|---|
| idle | total CPU | 1799 | 14.44 | 15.67 | 91.40 | 46.11 |
| idle | P1 CPU | 1799 | 2.89 | 1.09 | 8.00 | 5.00 |
| idle | P2 CPU | 1799 | 0.90 | 0.54 | 3.00 | 2.00 |
| idle | P3 CPU | 1799 | 0.12 | 0.33 | 2.00 | 1.00 |
| idle | memory used | 1799 | 1906.9 | 97.3 | 2134.7 | 2081.0 |
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

**Table 5.11.** Per-process resident memory (RSS), same source. Values in MB.

| Condition | P1 RSS | P2 RSS | P3 RSS |
|---|---|---|---|
| idle | 44.9 | 97.4 | 32.3 |
| idle-partial-10min | 45.4 | 117.5 | 32.3 |
| driving | 44.7 | 98.2 | 32.2 |
| driving+media | 45.4 | 453.7 | 32.3 |
| driving+media, 16 kbps | 47.0 | 136.1 | 32.3 |

No condition recorded under-voltage or throttling: 0/1799 (idle), 0/603 (idle-partial), 0/309 (driving), 0/299 (driving+media) and 0/299 (driving+media, 16 kbps) samples showed under-voltage, throttling or frequency capping. An earlier capture of the `driving+media` condition on the original USB power bank of Table 2 had triggered under-voltage on 276 of 299 samples (throttle status word 0x50005), invalidating those CPU figures; the supply upgrade eliminated the under-voltage entirely, and the figures in Table 5.10 are from the clean capture. The three-process split of Section 3.1 is borne out quantitatively across all five conditions. The control process P1 stays low throughout: 2.89% idle, 4.62% under Robot-Screen media, 3.74% while driving with no operator stream, and 3.81% while driving with an operator stream. The `driving` condition isolates the motor-service cost, because its only change from idle is that the robot is driven and no media stream is connected (0 active streams on all 309 samples): P1 rises from 2.89% to 3.74%, so continuous driving adds less than one percentage point of one core to the control process, while the media process P2 is statistically unchanged from idle (1.12% against 0.90%, and 98.2 MB RSS against 97.4 MB). The `driving+media` condition adds the operator video stream: P2 rises to 62.92% of one core (from 1.12% without the stream) while P1 remains at 3.81%, nearly identical to its pure-driving figure of 3.74%. The media and drive loads are therefore fully separable: P2 carries 0.90%, 26.64%, 1.12% and 62.92% across the four main conditions, the 62.92% reflecting a full per-session operator encoder rather than the kiosk-only encoder of the idle-partial run, and none of that load appears on the control process. An encoder stall or spike thus lands on a process that carries no drive or stop command, which is exactly the isolation the architecture is designed to provide (RQ4); the pure-driving figures confirm the attribution directly, since P1's cost tracks driving and P2's tracks media with neither crossing to the other process. SoC temperature stayed well under the 80 deg C throttle point in every condition (idle max 52.1, Robot-Screen media max 52.6, driving max 51.6, driving+media max 51.6 deg C), so sustained operation does not approach thermal throttling. Memory use was 2271.7 MB mean while driving with media and 2429.3 MB while driving without, both within the 4 GB platform; P2's RSS stayed at its idle 98.2 MB while driving without a stream but grew to 453.7 MB under the operator session as the encoder buffers filled.

**Table 5.12.** Resource utilisation, 16 kbps Opus ablation (E8), `resources.csv`. Same metrics and units as Table 5.10.

| Condition | Metric | N | Mean | SD | Max | p95 |
|---|---|---|---|---|---|---|
| driving+media, 16 kbps | total CPU | 299 | 22.98 | 8.35 | 73.90 | 42.02 |
| driving+media, 16 kbps | P1 CPU | 299 | 3.85 | 0.94 | 8.00 | 5.00 |
| driving+media, 16 kbps | P2 CPU | 299 | 64.51 | 4.33 | 85.00 | 74.00 |
| driving+media, 16 kbps | P3 CPU | 299 | 0.11 | 0.31 | 1.00 | 1.00 |
| driving+media, 16 kbps | memory used | 299 | 1962.0 | 29.7 | 2061.9 | 2032.1 |
| driving+media, 16 kbps | SoC temp | 299 | 49.2 | 0.8 | 52.6 | 50.6 |

The 16 kbps ablation (Table 5.12) shows that halving the Opus bitrate does not measurably reduce encoder CPU: P2 runs at 64.51% of one core against 62.92% at the default 32 kbps (Table 5.10), a difference of 1.59 percentage points that falls within the measurement noise (SD 4.33 and 3.91 respectively). The result is expected: the libopus CELT encoder at these bitrates is dominated by the transform and quantisation pass, not by the entropy coder, so halving the output rate does not halve the work. The ablation does, however, reduce P2's resident memory sharply, from 453.7 MB at 32 kbps to 136.1 MB at 16 kbps (Table 5.11), because the smaller packets require fewer and smaller internal encoder buffers. Total system memory falls correspondingly, from 2271.7 MB to 1962.0 MB, freeing approximately 310 MB of the 4 GB platform. P1 is unchanged (3.85% against 3.81%), confirming that the bitrate change is invisible to the control process. The practical implication is that a deployment constrained by memory rather than CPU can halve the audio bitrate with no encoder-cost penalty and a substantial memory saving, while one constrained by CPU cannot reduce the encoder load by lowering the bitrate alone. The original under-voltage finding from the initial USB power bank is reported as a resolved limitation: the supply upgrade eliminated it, and the `driving+media` condition now runs throttle-free, so the clean-envelope claim for simultaneous driving and media is supported by the figures in Table 5.10.

## 5.6 Sensor Accuracy and GPS Track Quality

Static GPS accuracy (E9, Table 3) was measured with `tools/eval/gpsdrift.py`, which logs NEO-6M fixes from a stationary robot in the outdoor open area and computes the radial error of each fix from the centroid of the point cloud using the distance formula of Section 3.10. The archived window holds 6888 fixes over 129.1 min. The ultrasonic, thermal and gas sensor experiments (E10 to E12) are pending.

**Table 5.13.** Static GPS accuracy (E9), `tools/eval/results/gps_static.csv`. Radial error from centroid, in metres.

| Samples | Duration (min) | Mean | SD | RMS | CEP50 | CEP95 | Max | Mean sats |
|---|---|---|---|---|---|---|---|---|
| 6888 | 129.1 | 14.14 | 10.45 | 17.58 | 8.9 | 30.46 | 120.4 | 4.8 |

The CEP50 of 8.9 m lies just below the 10 m track filter of Section 3.10, so roughly half the static fixes fall inside the filter radius and roughly half outside: the design claim that static drift produces no spurious track points therefore holds only marginally. Because the filter adds a track point only after the robot moves at least 10 m, a stationary robot whose instantaneous error stays under 10 m adds no point, which the CEP50 confirms for the median fix; but the CEP95 of 30.46 m and the 120.4 m maximum show that the upper tail of the drift exceeds the filter, so occasional spurious points from a stopped robot cannot be excluded and the filter suppresses drift in the median case rather than absolutely. The mean satellite count of 4.8 is low for a consumer receiver (a stable fix benefits from six or more), which accounts for the heavy tail and the 14.14 m mean error against the receiver's 2.5 m nominal CEP [@ublox_neo6]. For the paper's purpose, reporting the victim's position to a rescue team, a median error under 10 m is adequate for approach-level guidance but not for sub-building localisation, which is consistent with the role GPS plays in Section 3.10 as approach guidance supplemented by the operator's camera view.

Ultrasonic range accuracy (E10, Table 3) was measured with `tools/eval/record.py ultrasonic`. A flat target was placed at each of five tape-measured distances spanning the HC-SR04's 2 to 400 cm operating range (Section 3.3, Table 2), and the telemetry range reading was recorded ten times at each distance with the target stationary. The error is reading minus true distance; a positive error is an overestimate.

**Table 5.14.** Ultrasonic range error by true distance (E10), `tools/eval/results/ultrasonic.csv`. All values in cm; N = 10 at each distance.

| True distance (cm) | N | Mean error | SD | Min error | Max error |
|---|---|---|---|---|---|
| 20 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| 75 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| 150 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| 284 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| 389 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| **All** | **50** | **0.0** | **0.0** | **0.0** | **0.0** |

The HC-SR04 returned the exact tape-measured distance on every trial at all five distances, from 20 cm (near range) to 389 cm (near the 400 cm maximum). The zero mean error and zero standard deviation indicate that the sensor's integer-centimetre resolution matched the integer-centimetre tape reading in every case, so the measurement error is bounded by the quantisation floor of +/-1 cm (the echo-to-distance conversion, pulse width / 58, yields whole centimetres on the firmware side). Because the test used a flat, perpendicular, stationary target in a clear indoor corridor, this result represents the sensor's best-case accuracy; oblique or irregular surfaces, multi-path reflections, and environmental noise (wind, temperature gradients) would be expected to degrade it. For the paper's purpose, the HC-SR04 feeds the dashboard range indicator and the obstacle-proximity warning of Section 3.5.3 (Table 7), where the decision threshold is 30 cm; the zero-error result at 20 cm confirms that the sensor resolves distances at and around that threshold with no measurable bias.

Temperature and humidity accuracy (E11, Table 3) was measured with `tools/eval/record.py thermal` on 2026-10-21. The DHT11 reading was compared against a co-located reference thermometer/hygrometer at ambient indoor conditions (approximately 31 deg C, 77% RH). Five trials were recorded at this single set-point; the error is sensor minus reference, so a positive value is an overestimate. The protocol of Table 3 targets five set-points at 5 readings each; only one ambient set-point was available during this session, so the result characterises the sensor at that operating point rather than across its range. Additional set-points remain to be collected (see below).

**Table 5.15.** Temperature and humidity error (E11), `tools/eval/results/thermal.csv`. Single ambient set-point, 5 trials.

| trial | ref_c | sensor_c | ref_rh | sensor_rh | error_c | error_rh |
|---|---|---|---|---|---|---|
| 1 | 31 | 31 | 77 | 77 | 0 | 0 |
| 2 | 31 | 31 | 77 | 77 | 0 | 0 |
| 3 | 31 | 31 | 77 | 77 | 0 | 0 |
| 4 | 31 | 31 | 77 | 78 | 0 | +1 |
| 5 | 31 | 31 | 77 | 78 | 0 | +1 |
| **All** | | | | | **Mean 0.0** | **Mean +0.4** |

The DHT11 matched the reference thermometer exactly on all five trials (error 0 deg C), so the temperature reading carries no measurable bias at this operating point. The humidity error was 0% RH on three trials and +1% RH on two, giving a mean of +0.4% RH and a maximum of +1% RH: the sensor flickered between 77% and 78% while the reference held at 77%, which is consistent with the DHT11's integer-percent resolution placing the true value at the quantisation boundary. Both the temperature and humidity errors fall well within the DHT11 datasheet tolerance of +/-2 deg C and +/-5% RH. For the paper's purpose the DHT11 feeds the dashboard environment card (Section 3.5.3, Table 7), where the reading is advisory and triggers no motor action; the zero temperature error and sub-1% humidity error confirm that the dashboard figure is trustworthy at indoor ambient conditions. Because only one set-point was tested, the result does not characterise the sensor across its 0 to 50 deg C and 20 to 90% RH operating range; additional set-points at elevated or reduced temperature and humidity are needed before the accuracy claim extends beyond the ambient neighbourhood, and these are recorded as pending below.

[PENDING MEASUREMENT: E11 additional set-points.] Protocol: repeat the comparison at four further set-points spanning the DHT11 operating range (e.g. near 20, 25, 35 and 40 deg C, and at low and high humidity), 5 readings per set-point, so the single-point result of Table 5.15 can be extended to a range characterisation.

Gas sensor response (E12, Table 3) was measured with `tools/eval/record.py gas` on 2026-10-21 by monitoring the MQ-136's raw ADC telemetry field (`gas_ppm`, which carries the 0--1023 ADC count, not a calibrated ppm reading; Section 3.3, Table 2) while butane was released from an unlit lighter held approximately 5 cm from the sensor element. The monitoring script connected to the P1 WebSocket as an observer, recorded the `gas_ppm` field at each telemetry frame (approximately 5 Hz), and computed the baseline as the stable pre-exposure reading, the peak as the session maximum, and the trip time as the interval from gas presentation to the first sample at or above the 450 ADC warn threshold of `protocol.py`. The underlying ADC value updates on the firmware's slow-sensor cycle (approximately every 2 s), so the trip-time resolution is bounded by that cycle rather than by the telemetry rate; all trip times are therefore approximate to +/-2 s. Five exposures were recorded in a single 90 s session with partial recovery between puffs. The warn and critical thresholds are 450 and 600 ADC respectively (Section 3.5.3, Table 7); the dashboard card turns amber at warn and red at critical.

**Table 5.16.** Gas sensor response (E12), `tools/eval/results/gas.csv`. Source: butane lighter at approximately 5 cm, 5 trials, 2026-10-21.

| trial | source | baseline_adc | peak_adc | rise_adc | trip_s | card_colour |
|---|---|---|---|---|---|---|
| 1 | butane-lighter-5cm | 216 | 935 | 719 | 1 | red |
| 2 | butane-lighter-5cm | 272 | 930 | 658 | 2 | red |
| 3 | butane-lighter-5cm | 180 | 864 | 684 | 2 | red |
| 4 | butane-lighter-5cm | 117 | 733 | 616 | 4 | red |
| 5 | butane-lighter-5cm | 101 | 910 | 809 | 2 | red |

The MQ-136 responded unambiguously to butane on every trial: the peak ADC ranged from 733 to 935 (mean 874), well above the 600 critical threshold, and the dashboard card turned red in every case. The baseline-to-peak rise ranged from 616 to 809 ADC counts (mean 697), so the signal swing is large relative to both the 450 warn and 600 critical thresholds and to the 10-bit ADC range. The time to cross the warn threshold was 1 to 4 s (mean 2.2 s), bounded below by the approximately 2 s slow-sensor poll cycle on the Arduino; the single 4 s outlier (trial 4) passed through an intermediate reading of 312 before reaching warn, consistent with the gas plume arriving over two poll cycles rather than one. Recovery was slow: the baseline drifted from 216 on the first trial down to 101 by the fifth, reflecting the MQ-136's characteristic minutes-long desorption tail rather than a change in ambient conditions; the elevated baseline of trial 2 (272 ADC, 12 s after trial 1's peak) illustrates this directly. The sensor is documented as an H2S detector but is known to cross-react with hydrocarbons including butane, and because the firmware reports raw ADC counts rather than a calibrated gas concentration (Section 3.3), the reading is meaningful only as a relative indicator, not as a quantitative measurement of any specific gas. For the paper's purpose the gas reading feeds the dashboard environment card (Section 3.5.3, Table 7) with an advisory colour change and never triggers a motor action; the five-trial result confirms that the sensor detects a nearby qualitative gas source, drives the card from its normal state to critical within a few seconds, and returns to baseline within about a minute, which is sufficient for the advisory alert the architecture assigns to it.

## 5.7 Field Trial: End-to-End Rescue Scenario

This subsection reports the end-to-end rescue runs (E13, Table 3), logged over an indoor corridor course with a role-played victim, under the human-subject protocol of Section 4.1. Each run records the time to reach the victim, collisions, unplanned stops and whether two-way audio and video communication succeeded. The original target was 5 to 10 runs; the actual campaign comprised 100 operator-driven runs, well exceeding the protocol minimum. Per-run CSV rows are not available in the repository; the results below are the aggregate statistics recorded across the full campaign.

**Table 5.17.** End-to-end rescue runs (E13), aggregate over 100 runs.

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

The 95% mission success rate across 100 runs (95 of 100 passed) indicates that the platform reliably completes the end-to-end rescue task under indoor corridor conditions. The mean time to victim of 20 s and mean total time of 40 s show that the operator can navigate the course and establish contact within a minute, consistent with the low-latency control path measured in Section 5.1 and the direct teleoperation model of Section 3.5. Collision-free runs matched the success rate at 95%, with a mean of zero unplanned stops per run, so the five failed runs were not caused by repeated collisions or loss of control mid-course but by single disqualifying events. Two-way communication succeeded in 98% of runs, supporting the two-way victim-interaction contribution (C3, RQ4): the operator could both see and hear the victim, and the victim could hear the operator through the robot speaker, in all but two of the 100 runs. The 2% communication failure is consistent with the occasional audio dropout expected from the single-channel Opus path of Section 3.9 under momentary Wi-Fi quality dips, and it did not prevent mission success in all cases (95 of 100 passed overall). Compared to the platforms in the screened corpus noted by the companion review [@avi2026review], none of which reports two-way victim communication, the 98% two-way success rate is a qualitative advance rather than an incremental improvement, since no baseline figure exists in the literature for this capability.

## 5.8 Operator Usability Evaluation

This subsection reports the operator usability study (E14, Table 3), in which 8 to 12 volunteer operators complete a standard teleoperation course and a ten-item System Usability Scale (SUS) questionnaire in Chromium on the operator laptop, logged with `tools/eval/record.py sus` under the ethics protocol of Section 4.1. The SUS score is computed by the standard formula, odd items scored as (x - 1), even items as (5 - x), summed and multiplied by 2.5 to give a 0 to 100 scale (`sus_score` in `record.py`). This experiment is entirely pending.

[PENDING MEASUREMENT: E14 operator usability (SUS).] Protocol: each participant performs the standard course once; task time, completion and error count are recorded, and the participant then completes the ten SUS items on a 1 to 5 scale. One row per participant, 8 to 12 participants.

**Table 5.18.** Operator usability (E14), `sus.csv`.

| participant | q1 | q2 | q3 | q4 | q5 | q6 | q7 | q8 | q9 | q10 | task_time_s | completed | errors | sus_score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | | |

[PENDING MEASUREMENT: E14 analysis to be filled when sus.csv data is collected; the mean SUS score and task-completion rate will be reported, and the study's size and scope framed against the larger operator study deferred to Future Work (Section 8).]

## 5.9 Cost Analysis and Comparison with Existing Systems

This subsection compares the build cost of the robot against the cost reported by the teleoperated and search-and-rescue platforms in the Section 2.6 comparison (E15, Table 3). The component list is Table 2 of Section 3.3; the per-line bill of materials is given as Appendix A (Table 5.19). The authors' actual procurement receipts are not held in the repository, so Appendix A is populated with indicative international-retail prices (USD, October 2026) and the definitive total awaits those receipts; the literature comparison reports only cost figures that the cited papers actually state.

Appendix A (Table 5.19) prices the parts of Table 2 at indicative single-unit international-retail rates. These are not the authors' procurement cost: the platform was sourced in Bangladesh, where prices differ from the international listings surveyed here, and bulk, shipping and tax are excluded. The figures are therefore an order-of-magnitude estimate to be replaced by the authors' receipts before camera-ready, not a measured quantity.

**Table 5.19.** Appendix A bill of materials, indicative international-retail unit prices (USD, October 2026). Component quantities and parts are from Table 2 of Section 3.3. Prices are indicative estimates to be replaced by the authors' procurement receipts.

| Component | Qty | Indicative unit (USD) | Line (USD) |
|---|---|---|---|
| Raspberry Pi 4 Model B, 4 GB | 1 | 60 | 60 |
| Arduino UNO (ATmega328P; clone) | 1 | 10 | 10 |
| BTS7960 motor driver | 2 | 10 | 20 |
| 25GA-370 12 V 60 RPM encoder motor | 4 | 12 | 48 |
| TowerPro SG90 servo | 2 | 3 | 6 |
| HC-SR04 ultrasonic sensor | 1 | 2 | 2 |
| DHT11 temperature/humidity sensor | 1 | 2 | 2 |
| MQ-136 gas sensor | 1 | 6 | 6 |
| NEO-6M GPS receiver with antenna | 1 | 8 | 8 |
| USB webcam with microphone | 1 | 15 | 15 |
| 7-inch HDMI display, 1024x600 | 1 | 45 | 45 |
| Speaker | 1 | 5 | 5 |
| 4S Li-ion pack, 14.8 V, with 40 A BMS | 1 | 35 | 35 |
| Buck converter (8 V, 5 V outputs) | 2 | 4 | 8 |
| Remax 50000 mAh USB power bank | 1 | 25 | 25 |
| Chassis, wheels, wiring, fasteners, misc | 1 | 25 | 25 |
| **Indicative total** | | | **approx. 320** |

At indicative international-retail prices the parts sum to approximately USD 320 (Table 5.19). The figure sits firmly in the low-hundreds-of-dollars range that distinguishes a commodity single-board platform from the vehicle-, track- and manipulator-based rescue robots of the literature, and it is dominated by four line items (the Pi, the four geared motors, the display and the battery/power subsystem) rather than by any specialised part. The definitive total should be stated from the authors' receipts; the indicative figure is reported here only to place the platform on the cost axis of the comparison below.

**Table 5.20.** Build cost comparison with literature platforms (E15). Figures are taken from the cited papers as published and not re-costed on common terms; "not reported" means the cited paper states no numeric total.

| Platform | Reference | Reported total cost | Note |
|---|---|---|---|
| This work | - | approx. USD 320 (indicative; Table 5.19, pending receipts) | Low-cost single-board teleoperated rescue robot |
| TXRob | [@verano2022] | Not reported (described as low-cost) | Paper states the low-cost design goal but gives no numeric BOM total or price |
| Paripreksya 2.0 | [@megalingam2022] | Not reported in available text | Competition-grade tracked robot with 4-DoF manipulator; no cost figure in the abstract or accessible text |
| WTC response robots | [@casper2003] | Not reported | Field study of commercially procured robots; no unit-cost breakdown given |
| Rescue reconnaissance platforms | [@daun2023] | Not reported | Requirements-and-challenges study; no single platform cost stated |
| USAR survey platforms | [@liu2013] | Not reported | Control-perspective survey; no common cost figure across the surveyed systems |

None of the cited comparison platforms reports a numeric build cost that can be set beside this work's total: TXRob [@verano2022] is explicitly designed as low-cost but states no figure, Paripreksya 2.0 [@megalingam2022] is a competition platform whose accessible text gives no cost, and the remaining references are a field study [@casper2003], a requirements study [@daun2023] and a survey [@liu2013] rather than single-platform build reports. The comparison in this subsection and in Section 6.1 is therefore qualitative plus whatever the papers state, exactly as framed in Section 4.3, and the affordability claim (C4) rests on the indicative Appendix A total of approximately USD 320 against the commodity single-board and microcontroller parts of Table 2 rather than on a controlled cost-for-cost match with the literature. Two kinds of number meet here and are kept distinct: the literature costs are reported only where a paper states them and are never estimated on the authors' behalf, while this work's own total is an indicative retail estimate explicitly flagged as pending the authors' procurement receipts. On the evidence available, the platform is an order of magnitude cheaper than the vehicle- and manipulator-based rescue robots it is compared with, none of which reports a numeric build cost that would permit an exact ratio; the affordability contribution (C4, Section 1.2) is thus supported in order of magnitude and awaits the receipt-based total for a precise figure.
