## IV. EXPERIMENTAL SETUP

### A. Test Conditions

All experiments ran on the robot as built (Table III) with hardware emulation disabled, so every command reached the physical Arduino and motors. The Pi ran Raspberry Pi OS 12 (Bookworm, kernel 6.12, arm64) with Python 3.11. Experiments were run between 2026-09-29 and 2026-10-23 at two sites: an indoor laboratory, with the robot within 3 m of the router, for latency, fault-injection, resource and bench sensor experiments; and an open outdoor area for the Wi-Fi range sweep and the static GPS window. One exception to the laptop-to-robot path matters for interpretation: the control-latency probe (E1) ran on the Pi and connected to P1 over the loopback interface, so its figures exclude the Wi-Fi link and the operator laptop.

### B. Experiments and Achieved Design

Table VIII lists the twelve experiments with the design actually achieved; their identifiers (E1, E4-E9, E13, E15-E18) are those of the result files and tools in the repository. Several experiments could not be run as planned; Section V reports only what was achieved, and Table XVII lists what is pending, with the claim each pending experiment tests and its pass criterion. The criteria were fixed before any of those data were collected and are not changed after the data are seen.

**TABLE VIII.** Experiment matrix: planned and achieved design. Tools are in `tools/eval/` of the code repository.

| # | Experiment | Planned | Achieved | Metric |
|---|---|---|---|---|
| E1 | Control-plane latency (on the Pi, loopback) | 30 trials per probe | 2 jittered sessions x 30 per probe, plus 1 phase-locked session | Command to telemetry confirmation (ms); dead-man interval from P1's event log |
| E4 | Dead-man wheel-stop time, 240 fps video | 20 at PWM 180, on the floor | Not run | Last command to wheels at rest (s); distance covered (cm) |
| E5 | Media delay and quality | 20 per condition, 3 conditions | Not run | Glass-to-glass and audio delay (ms), frame rate, loss |
| E6 | Wi-Fi range | Outward to link failure, with and without obstacles | 16 line-of-sight stations, 5-250 m, one burst each; no failure reached; no obstacles | ICMP loss, RTT, signal level; operator judgement |
| E7 | Fault injection and recovery | 10 per target | 30 automated SIGKILL trials (3 targets); manual faults F6, F7 | Detection and recovery time, PID change |
| E8 | Resource use | 4 conditions x 30 min | 6 conditions of 3-30 min at 1 Hz | CPU, memory, system-on-chip (SoC) temperature, throttle flags |
| E9 | GPS static precision | 30 min static | 129.1 min archived static window | Radial scatter about the centroid (m) |
| E13 | Field trial with role-played victim | 10 runs, fixed course and success rule | Not run | Run success, time to victim, collisions, two-way exchange |
| E16 | Media isolation (control latency with media off, on, and P2 frozen) | 3 conditions x 30 | Not run | Confirmed commands; motor-stop upper bound (ms) |
| E17 | Victim communication under degraded conditions | 15 participants x 3 communication modes x 2 victim states, counterbalanced | Not run | Scripted items transferred correctly of three; exchange time (s); operator confidence |
| E18 | Person detector on a labelled frame set | 400 frames through the robot's own video path, stratified by posture, occlusion, illumination and distance; 10 min person-free video | Not run | Precision, recall, F1 per stratum; banner false alarms per minute |
| E15 | Cost | Bill of materials | Authors' itemized receipts (BDT) | Total cost |

### C. Evidence Classes, Validity and Data Provenance

Every number in Section V belongs to one of these classes: MEASURED (observed on this robot and stored in the result files or the robot's logs), CALCULATED (derived from measured values or design constants by a stated formula), PREDICTED (from the recovery model (4)), SIMULATED (output of a software model with no physical measurement behind it), SOFTWARE-TEST (passing automated tests, in most cases against a hardware emulator), and PENDING. A trial is valid when all three processes are healthy, the serial link is active, no injected fault is outstanding and the tool reports success; discarded trials are reported, and none occurred in the automated E1 and E7 runs.

Every result reported in Section V is machine-logged: the rows of E1, E7, E8 and E9 are written by the evaluation tools, and the E6 radio figures are logged by `netsweep.py` (only its distances and operator judgements are entered by hand). Rows typed after a session carry the time of entry, not of measurement, and are accepted only where the robot's independent logs agree with them: P1's event log, which records every line sent to and received from the Arduino with a millisecond timestamp, and the 1 Hz telemetry log. A result the logs contradict supports no claim and is not reported. Because the logs rotate, the windows used here are preserved in the repository.

### D. Statistical Treatment

Means of independent trials carry a two-sided 95% Student-t confidence interval. Success proportions carry a 95% Wilson score interval [@wilson1927], which stays informative when every trial succeeds. The 1 Hz resource series are autocorrelated, so their means carry a 95% interval from ten non-overlapping batch means. No hypothesis test is reported for any experiment with data, and differences between those conditions are described, not tested. E17 is the exception and its analysis is fixed here, before its data exist: Cochran's Q across the three communication modes within each victim state on the per-participant binary outcome, exact McNemar tests on the mode pairs with Holm correction only if Q is significant at 0.05, and the difference in proportions with a 95% interval as the effect measure in every case. It is a designed within-subjects experiment with equal cells, so a description alone would waste the design. All figures are reproduced by `tools/eval/section5_stats.py`.

E1 needs one further note. The latency probe waits for telemetry to confirm each command. Because the firmware emits telemetry every 500 ms and P1 rebroadcasts every 200 ms, the confirmation can arrive up to 700 ms after the event, so E1 latencies are upper bounds. The probe randomizes its send phase by 0-200 ms to decorrelate trials from the 200 ms rebroadcast; a phase-locked control session shows the bias this removes. The jitter cannot decorrelate trials from the 500 ms firmware cycle. The dead-man interval avoids this quantization by using P1's event-log timestamps (Section V-A).

### E. Baselines

The dead-man and the watchdog are evaluated by their measured behaviour with the feature present; the paper claims no measured benefit over a system without them. The process split is tested directly on the robot as built (E16): the E1 motor probe is run 30 times with no media session, with one operator media session, and with P2 suspended by SIGSTOP in 15 s windows, short of the 35 s health-check restart. E16 is pending (Table XVII); it can show whether the split isolates control from media on this robot, not how a single merged process would behave. An Opus bitrate comparison, 16 kbit/s instead of 32 kbit/s, was run for processor load only and is confounded (Section V-D). The design constants of Section III (the 2000 ms window, the 3000 ms telemetry timeout and the recovery model) serve as specification targets. The literature platforms of Table I are compared by their published descriptions only.

### F. Human Subjects

No human-subject data have been collected. Two experiments involve people other than the experimenter and share one application: the field trial (E13), with an author as operator and a second person role-playing the victim, and the victim-communication study (E17), with fifteen participants who each role-play the victim under three communication modes and two victim states. Both will be run under informed consent with anonymous participant numbers, participation is voluntary and may be stopped at any moment, and nothing is recorded or stored on the robot. The detector frame set (E18) shows only the authors, who consent; those frames stay on the operator's computer and none is published. [AUTHOR INPUT REQUIRED: ethics-committee decision or institutional waiver, with reference number and date, before E13 or E17 is run and before submission.]
