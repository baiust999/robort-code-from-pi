## IV. EXPERIMENTAL SETUP

### A. Test Conditions

All experiments ran on the robot as built (Table III) with hardware emulation disabled, so every command reached the physical Arduino and motors. The Pi ran Raspberry Pi OS 12 (Bookworm, kernel 6.12, arm64) with Python 3.11. Experiments were run between 2026-09-29 and 2026-10-23 at two sites: an indoor laboratory, with the robot within 3 m of the router, for latency, fault-injection, resource and bench sensor experiments; and an open outdoor area for the Wi-Fi range sweep and the static GPS window. One exception to the laptop-to-robot path matters for interpretation: the control-latency probe (E1) ran on the Pi and connected to P1 over the loopback interface, so its figures exclude the Wi-Fi link and the operator laptop.

### B. Experiments and Achieved Design

Table VIII lists the fourteen experiments with the design actually achieved; their identifiers (E1, E3-E13, E15, E16) are those of the result files and tools in the repository. Several experiments could not be run as planned; Section V reports only what was achieved, and Table XVII lists what is pending, with the claim each pending experiment tests and its pass criterion. The criteria were fixed before any of those data were collected and are not changed after the data are seen.

**TABLE VIII.** Experiment matrix: planned and achieved design. Tools are in `tools/eval/` of the code repository.

| # | Experiment | Planned | Achieved | Metric |
|---|---|---|---|---|
| E1 | Control-plane latency (on the Pi, loopback) | 30 trials per probe | 2 jittered sessions x 30 per probe, plus 1 phase-locked session | Command to telemetry confirmation (ms); dead-man interval from P1's event log |
| E3 | Emergency-stop distance | 20 per speed x 3; repeat filmed at 240 fps, each stop logged by P1 | 23 hand-entered rows; contradicted by logs; repeat not run | Distance (cm), stop time (s) |
| E4 | Dead-man wheel-stop time, 240 fps video | 20 at PWM 180, on the floor | Not run | Last command to wheels at rest (s) |
| E5 | Media delay and quality | 20 per condition, 3 conditions | Not run | Glass-to-glass and audio delay (ms), frame rate, loss |
| E6 | Wi-Fi range | Outward to link failure, with and without obstacles | 16 line-of-sight stations, 5-250 m, one burst each; no failure reached; no obstacles | ICMP loss, RTT, signal level; operator judgement |
| E7 | Fault injection and recovery | 10 per target | 30 automated SIGKILL trials (3 targets); manual faults F6, F7 | Detection and recovery time, PID change |
| E8 | Resource use | 4 conditions x 30 min | 6 conditions of 3-30 min at 1 Hz | CPU, memory, system-on-chip (SoC) temperature, throttle flags |
| E9 | GPS static precision | 30 min static | 129.1 min archived static window | Radial scatter about the centroid (m) |
| E10 | Ultrasonic accuracy | 5 distances x 10, readings from the telemetry log | 50 hand-entered rows; contradicted by logs; repeat not run | Reading error (cm) |
| E11 | DHT11 accuracy | 5 set-points | 1 set-point, 5 readings | Sensor minus reference |
| E12 | Gas sensor response | Qualitative | 5 puffs, one session | Peak counts, trip time (s) |
| E13 | Field trial with role-played victim | 10 runs, fixed course and success rule | Not run | Run success, time to victim, collisions, two-way exchange |
| E16 | Media isolation (control latency with media off, on, and P2 frozen) | 3 conditions x 30 | Not run | Confirmed commands; motor-stop upper bound (ms) |
| E15 | Cost | Bill of materials | Authors' itemized receipts (BDT) | Total cost |

### C. Evidence Classes, Validity and Data Provenance

Every number in Section V belongs to one of these classes: MEASURED (observed on this robot and stored in the result files or the robot's logs), CALCULATED (derived from measured values or design constants by a stated formula), PREDICTED (from the recovery model (4)), SIMULATED (output of a software model with no physical measurement behind it), SOFTWARE-TEST (passing automated tests, in most cases against a hardware emulator), and PENDING. A trial is valid when all three processes are healthy, the serial link is active, no injected fault is outstanding and the tool reports success; discarded trials are reported, and none occurred in the automated E1 and E7 runs.

Rows written by the automated tools (E1, E6, E7, E8) are machine-generated. Rows entered by hand afterwards (E3, E10, E11, E12) carry the time of entry, about one second apart, not the time of measurement, so they were transcribed after each session. They are accepted only where the robot's independent logs agree with them: P1's event log, which records every line sent to and received from the Arduino with a millisecond timestamp, and the 1 Hz telemetry log. Results the logs contradict are retained but marked [VERIFICATION REQUIRED] and support no claim. Because the logs rotate, the windows used here are preserved in the repository.

### D. Statistical Treatment

Means of independent trials carry a two-sided 95% Student-t confidence interval. Success proportions carry a 95% Wilson score interval [@wilson1927], which stays informative when every trial succeeds. The 1 Hz resource series are autocorrelated, so their means carry a 95% interval from ten non-overlapping batch means. No hypothesis test is reported, and differences between conditions are described, not tested. All figures are reproduced by `tools/eval/section5_stats.py`.

E1 needs one further note. The latency probe waits for telemetry to confirm each command. Because the firmware emits telemetry every 500 ms and P1 rebroadcasts every 200 ms, the confirmation can arrive up to 700 ms after the event, so E1 latencies are upper bounds. The probe randomizes its send phase by 0-200 ms to decorrelate trials from the 200 ms rebroadcast; a phase-locked control session shows the bias this removes. The jitter cannot decorrelate trials from the 500 ms firmware cycle. The dead-man interval avoids this quantization by using P1's event-log timestamps (Section V-A).

### E. Baselines

The dead-man and the watchdog are evaluated by their measured behaviour with the feature present; the paper claims no measured benefit over a system without them. The process split is tested directly on the robot as built (E16): the E1 motor probe is run 30 times with no media session, with one operator media session, and with P2 suspended by SIGSTOP in 15 s windows, short of the 35 s health-check restart. E16 is pending (Table XVII); it can show whether the split isolates control from media on this robot, not how a single merged process would behave. An Opus bitrate comparison, 16 kbit/s instead of 32 kbit/s, was run for processor load only and is confounded (Section V-D). The design constants of Section III (the 2000 ms window, the 3000 ms telemetry timeout and the recovery model) serve as specification targets. The literature platforms of Table I are compared by their published descriptions only.

### F. Human Subjects

No human-subject data have been collected. The field trial (E13) involves an author as operator and a second person who role-plays the victim, and will be run under informed consent with anonymous participant numbers. [AUTHOR INPUT REQUIRED: ethics-committee decision or institutional waiver, with reference number and date, before E13 is run and before submission.]
