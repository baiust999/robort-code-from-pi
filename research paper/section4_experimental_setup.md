# 4. Experimental Setup

This section defines the test environment, the experiment matrix, the measurement and validity rules, and the baselines that apply across all fifteen experiments. Each subsection of Section 5 opens with its own procedure paragraph; shared conditions stated here are not repeated there. The hardware, network and software are specified in Sections 3.2-3.4 and are referenced, not restated. Because several experiments could not be run as planned, Table 4.1 gives the planned design and the design actually achieved side by side, and Section 4.4 lists every deviation; Section 5 reports only what was achieved.

## 4.1 Test Conditions

All experiments run on the robot as built (Table 2, Figure 3) with a single operator laptop connected to the same Wi-Fi cell, except where Table 4.1 states that a probe ran on the Pi itself. The network is the 802.11n cell described in Section 3.2: 2.4 GHz, 20 MHz width, no internet uplink, with the access point nominally on channel 10. The channel was read at the start of the E6 sessions and was not constant across the campaign (channel 3 for two stations on 2026-10-22, channel 10 thereafter; Section 5.3), so the channel is recorded per station rather than assumed. The robot runs Raspberry Pi OS 12 (Bookworm, kernel 6.12, arm64) with Python 3.11, and the operator uses Chromium on the same laptop for both the dashboard and the SUS questionnaire. Hardware emulation is disabled for every run, so every command reaches the physical Arduino and motors.

The control-latency probe (E1) is the one exception to the laptop-to-robot path: it runs on the Pi and connects to P1 over the loopback interface, so its figures exclude the Wi-Fi link and the operator laptop (Section 5.1). Link-dependent behaviour is covered separately by E6 and by the SIMULATED heartbeat-loss model of Section 5.1b, which is not a measurement.

Three test sites are used:

- Indoor laboratory (approximately 6 x 8 m): control-latency, fault-injection, resource-utilisation and bench sensor experiments. The operator and robot are within 3 m of the router, so the link is not a variable.
- Indoor corridor and adjoining rooms: field-trial course (Section 5.7) and usability runs (Section 5.8).
- Outdoor open area: Wi-Fi range sweep (Section 5.3) and GPS static precision (Section 5.6), where line-of-sight distances up to link failure are needed.

Each result is tied to the test date and to the log or CSV it came from. Dates, labels and session boundaries are part of the evidence and are reported in Section 5, because several quantities (E1 and E6 in particular) differed between sessions.

**Ethics and human-subject protocol.** The usability evaluation (Section 5.8) involves volunteer operators who complete a timed task and a System Usability Scale questionnaire. The field trial (Section 5.7) includes a role-played victim who interacts with the operator through the robot's display and speaker. Participants are briefed on the task, the data collected and their right to withdraw at any time before the session begins; all give informed consent, participation is voluntary, no deception is involved, and responses are recorded anonymously with a participant number only. No personally identifiable data is collected or stored. The task is a short teleoperation exercise in a controlled indoor environment, which poses minimal risk. [PENDING: the ethics-committee decision or institutional waiver, with its reference number and date, must be stated here before submission; the paper does not assert an exemption on its own authority.] No human-subject data has been collected to date (Sections 5.7 and 5.8).

## 4.2 Experiments, Metrics and Validity Rules

Table 4.1 maps the fifteen experiments (E1 to E15) to the tools in `tools/eval/`, the metric each one produces, the planned and achieved number of trials, and the Section 5 subsection that reports the result. The experiments are grouped into nine evaluation areas, one per Section 5 subsection: control latency and stopping (E1 to E4, Section 5.1), media streaming (E5, 5.2), communication range (E6, 5.3), fault injection (E7, 5.4), resource use (E8, 5.5), sensor accuracy (E9 to E12, 5.6), the field trial (E13, 5.7), usability (E14, 5.8) and cost (E15, 5.9). Every CSV is stored under `tools/eval/results/` and is cited in the Data and Code Availability statement. The evidence status of each experiment is given in Table 5.0.

**Table 4.1.** Experiment matrix: planned design and design achieved.

| # | Experiment | Site | Planned trials | Achieved | Tool | Metric (start -> end, unit) | Section |
|---|---|---|---|---|---|---|---|
| E1 | Control-plane latency | Indoor lab (on the Pi, loopback) | 30 per probe | 2 jittered sessions x 30 per probe, plus 1 phase-locked session | wslatency.py | Command send -> telemetry confirmation (ms); upper bound, up to 700 ms quantisation | 5.1 |
| E2 | True control latency | Indoor lab | 30 | Not run; substitute: E1 telemetry-confirmed upper bounds (Table 5.1) | record.py latency_video | Key press -> wheel motion at 240 fps (ms); 4.17 ms resolution | 5.1 |
| E3 | Emergency-stop distance | Indoor lab | 20 x 3 speeds | 23 rows (7, 9, 7); [VERIFICATION REQUIRED] | record.py estop | Stop command -> wheels stationary: distance (cm); time not recorded | 5.1 |
| E4 | Dead-man wheel-stop time | Indoor lab | 20 | Not run (firmware-side interval only, from the P1 log) | record.py deadman_physical | Last heartbeat -> wheels stationary at 240 fps (s) | 5.1 |
| E5 | Video and audio streaming | Indoor lab | 20 per viewer count | Not run; no substitute for delay (E8 gives only the CPU cost of media) | record.py glass2glass | Displayed clock vs real clock (ms) | 5.2 |
| E6 | Communication range | Outdoor, line of sight | Progressive distances to link failure, with and without obstacles | 16 stations, 5-250 m, 1 burst each, no obstacle, no failure reached | netsweep.py | ICMP loss (%) and RTT (ms) to the router, RSSI (dBm), tx bitrate, channel, operator video/control judgement | 5.3 |
| E7 | Fault injection and recovery | Indoor lab | 10 per target (automated); manual watch | 30 automated (3 targets x 10); 94 manual-watch rows | faultinject.py run + watch | Detection time (ms), recovery time (ms), PID change (boolean) | 5.4 |
| E8 | Resource utilisation | Indoor lab | 4 conditions x 30 min | 6 labelled conditions of about 3 to 30 min at 1 Hz (only `idle` reached 30 min; `driving+media` spans 196 s) | reslog.py | CPU (% of one core), memory (MB), SoC temperature (C), throttle flags | 5.5 |
| E9 | Sensor accuracy: GPS | Outdoor | 30 min static | 129.1 min archived static window (6888 fixes) | gpsdrift.py | Radial error from centroid: mean, CEP50, CEP95 (m) | 5.6 |
| E10 | Sensor accuracy: ultrasonic | Indoor lab | 5 distances x 10 | 50 rows; [VERIFICATION REQUIRED] | record.py ultrasonic | True distance - reading (cm) | 5.6 |
| E11 | Sensor accuracy: temperature/humidity (DHT11) | Indoor lab | 5 set-points | 1 set-point (about 31 degC, 77% RH), 5 readings; error columns [VERIFICATION REQUIRED] | record.py dht11 | Reference - sensor (degC, %RH) | 5.6 |
| E12 | Sensor accuracy: gas | Indoor lab | Qualitative | 5 rows | record.py gas | Baseline vs peak ADC counts, trip time (s) | 5.6 |
| E13 | Field trial | Indoor course | 5-10 runs | Not run; no substitute (only E7 fault tests and software tests) | record.py field | Time to victim (s), collisions, two-way comms success | 5.7 |
| E14 | Operator usability (SUS) | Indoor | 8-12 operators | Not run; no substitute | record.py sus | SUS score (0-100), task time (s), task success | 5.8 |
| E15 | Cost analysis | N/A | N/A | Authors' itemised receipts (BDT) | Appendix A BOM | Total cost (USD) vs literature platforms | 5.9 |

**Pass/fail thresholds.** The design in Section 3 defines four timing guarantees that the experiments must validate:

1. The dead-man stop bound of approximately 2060 ms (Section 3.5.2), tested by E4 and, for the firmware-side interval, by E1.
2. The telemetry timeout of 3000 ms that triggers mission state STOP at the operator (Section 3.7.3, Table 10). This is a dashboard design constant. No experiment measured it, so it is a specification target only and Section 5 reports no result for it.
3. The recovery-time model of Section 3.7.2 (14.6-19.6 s for a P1 crash, including 10 s cooldown), tested by E7.
4. The lockout threshold of 5 key failures within 300 s (Section 3.8). It is checked only by software tests (`pi/tests/test_controller_access.py`, 25 of 25 passed on 2026-10-23, part of the suite of Section 5.1a), not by a trial on the robot; the evidence class is SOFTWARE-TEST.

In addition, the GPS track filter of 10 m (Section 3.10) sets the boundary below which static drift produces no spurious track points, tested by E9.

**Quantisation and resolution.** The wslatency probe (E1) waits for the telemetry path to confirm a command. Because the Arduino emits telemetry every 500 ms and P1 rebroadcasts on a 200 ms timer (Section 3.6.2), the confirmation can arrive up to 700 ms after the event, making E1 figures upper bounds rather than true latencies. The 240 fps video measurement (E2) is designed to observe wheel motion directly at 4.17 ms resolution and give the true control latency; it has not yet been run. The deadman_panic timestamp in the P1 log has millisecond resolution and is not subject to telemetry quantisation. E1 uses a 0-200 ms random jitter on the send phase (Section 3.6.2) to decorrelate trials from the P1 rebroadcast cycle; without this jitter a phase-locked sender produces a biased, deceptively tight distribution, which the phase-locked session documents. The jitter cannot decorrelate from the 500 ms firmware cycle, which is a known limitation.

**Communication-range protocol and criterion (E6).** The sweep measures the Pi-to-router radio link, not the operator-to-robot path end to end. At each station `netsweep.py` sends a burst of 100 ICMP echo requests at 0.2 s intervals to the router and logs loss, mean and maximum round-trip time, the signal level at the start and end of the burst, the negotiated transmit bitrate and the channel; the operator then enters the distance, the obstacle description and two judgements (video: good, choppy or lost; control: yes, degraded or no). Three limits follow from this design and are carried into the interpretation in Section 5.3. First, ICMP loss to the router is not the loss rate of the control heartbeat or of the WebRTC media, so it is a proxy for link quality and not a measure of mission-level behaviour. Second, one burst per station gives no estimate of burst-to-burst variation, so a distance effect cannot be separated from a time effect or sampling noise without repeated bursts at a fixed station. Third, distances and the video and control judgements are operator-entered and unverified. The usable range is defined a priori as the largest distance at which both operator judgements are favourable (video good, control yes) and ICMP loss is below 5%. The 5% limit is a criterion adopted by this paper, not a measured tolerance of the robot. Where the two conditions disagree, Section 5.3 reports both and does not select one after the fact. Before any further E6 data is taken, the criterion (loss threshold or operator judgement alone) is to be fixed in advance, distances measured with a tape or wheel, the router's position and channel recorded, and a scan of nearby networks run at the start of each session (the continuation protocol of Section 5.3).

**Validity rule.** A trial is valid when the system is fully started (all three processes healthy, serial link active, no prior fault injected and not cleared), the network link is stable at the test distance, and the tool reports `ok = true`. A trial where the WebSocket connection fails to open, or where an unrelated fault occurs during measurement, is discarded and logged with a reason in the `detail` or `notes` column. Discarded trials are reported in Section 5 alongside the valid count, not silently dropped. For E6 the "stable link" condition cannot be a validity filter, since link degradation is the quantity measured; every logged station is therefore retained, including the repeat stations R1 to R6, and the sessions are reported separately.

**Data integrity and provenance.** Rows written by the automated tools (E1, E6, E7, E8) are machine-generated. Rows entered by hand through `record.py` (E3, E10, E11, E12) carry the time of data entry, not of measurement, and are accepted only where the robot's independent logs (`p1_events.log`, `telemetry.log`) agree with them; the cross-check is summarised in Table 5.0. Results that the logs contradict or cannot support are retained but marked [VERIFICATION REQUIRED] and are not used to support any claim. Each reported number carries an evidence class (MEASURED, CALCULATED, SIMULATED, [PENDING MEASUREMENT] and the others defined at the head of Section 5), so a SIMULATED or SOFTWARE-TEST figure cannot be read as a physical measurement.

**Statistical treatment.** Interval estimates, the handling of autocorrelated 1 Hz series, and the decision not to report hypothesis tests are stated once, at the head of Section 5, and are reproduced by `tools/eval/section5_stats.py`. With the small and unequal sample sizes of Table 4.1, differences between conditions are described, not tested.

## 4.3 Baselines

Three kinds of baseline frame the results.

**Internal ablations.** Four configurations were planned to isolate the contribution of individual design choices:

1. Dead-man timer disabled (firmware compile-time flag): the robot continues driving after the operator link is lost, showing what the dead-man prevents. Not run [PENDING MEASUREMENT].
2. P3 watchdog disabled (P1 and P2 started directly): a crashed process is not restarted, showing the value of process supervision. Not run [PENDING MEASUREMENT]; the recovery times of E7 are measured with the watchdog enabled only.
3. Control and media merged into a single process: a media fault can block the control path, showing the value of the three-process split. Not run [PENDING MEASUREMENT].
4. Alternative Opus bitrate (16 kbps vs the default 32 kbps): trades audio quality against CPU load, reported in Section 5.5. This is the only ablation run, and its run is confounded by a P2 restart (Section 5.5).

Each ablation is run only for the experiment it informs, not across all fifteen rows. Until ablations 1 to 3 are run, the paper claims no measured benefit for the dead-man, the watchdog or the process split beyond what the with-feature measurements show.

**Specification targets.** The timing constants of Section 3 serve as pass/fail lines: the 2000 ms dead-man window, the 3000 ms telemetry timeout, and the recovery-time model bounds. These are design specifications, not measured values; the experiments test whether the implementation meets them.

**Literature baselines.** The platforms of the Section 2.6 comparison (Table 2.1) are compared by their published descriptions and are not re-run on this hardware. The only quantitative comparison is cost (Table 5.20, [@verano2022], [@megalingam2022], [@casper2003], [@daun2023], [@liu2013]), and none of those papers reports a numeric build cost. The comparison in Sections 5.9 and 6.1 is therefore qualitative; it is not a controlled head-to-head experiment, and no cost ratio is computed.

## 4.4 Deviations from the Planned Design and Threats to Validity

The deviations below are collected here so that a reader of Section 5 can see at once where the achieved design departs from Table 4.1.

- **Substitute evidence for experiments not run.** Each substitute below is a weaker kind of evidence and is not equivalent to the planned experiment; Section 5 labels it with its own evidence class.
  - E2 (true control latency): replaced by the E1 telemetry-confirmed figures (Table 5.1), which are robot-internal upper bounds over loopback, exclude Wi-Fi, and can exceed the true latency by up to 700 ms.
  - E4 (physical dead-man stop): replaced by the firmware-side interval timed on P1's clock (Table 5.2b, maximum 2042 ms in 30 of 30 trials), two fault observations (F7 and the unplanned heartbeat gap, Tables 5.9a and 5.9c) and the native test of the compiled firmware (Table 5.5d). These show when drive is removed, not when the wheels stop.
  - E3 (stop distance): replaced by the CALCULATED ramp bound (120 ms, 2.5 cm at the 180 cap) and the log-verified command path of `estop_auto.py` (15 trials, no distance). The tape-measured table is [VERIFICATION REQUIRED] and supports no claim.
  - E5 (streaming): no substitute for delay or quality. E8 gives only the processor cost of one operator media session (Tables 5.10 and 5.10b).
  - E10 (ultrasonic): no substitute for accuracy.
  - E13 and E14 (field trial, usability): no substitute. The fault tests of E7 and the software tests of Section 5.1a say nothing about rescue performance or operator usability.
  - Ethics: no human-subject data exist, so no approval reference is needed yet; it is required before E13 or E14 is run.
- **Experiments not run:** E2, E4 (video-based), E5, E13 and E14, and ablations 1 to 3. They appear in Section 5 as [PENDING MEASUREMENT] with a protocol and an empty table. Consequently no human-subject data exist, and the usability and end-to-end rescue claims of the design are untested.
- **Reduced or changed designs:** E3 has 23 rows, not 60; E6 is a single-burst, line-of-sight, no-obstacle sweep that never reached a failure point; E8 has six conditions of unequal length, one of which (`driving+media`) is two overlapping logger runs and one of which (`driving+media-16kbps`) is confounded by a P2 restart; E9 uses an archived static window rather than a fresh 30-minute run.
- **Narrow fault and sensor coverage:** E7 injected only SIGKILL crashes automatically (no hangs, camera loss, microphone loss or Robot Screen exit). The manual faults F6 (Arduino unplug) and F7 (Wi-Fi drop) are single injections whose injection instants were not logged, and F9 (GPS loss) is not a valid measurement. E11 covers one set-point (about 31 degC, 77% RH) with five non-independent readings, not the five planned set-points; E12 is five puffs in one session.
- **Configuration and cost records:** the 16 kbit/s Opus setting of the E8 ablation was applied by an uncommitted change and is not in version control. The replacement Pi supply is not identified, and the E15 bill of materials, now taken from the authors' itemised receipts (in BDT, converted at an indicative exchange rate), omits a few parts (the USB webcam, the speaker and the Pi power bank).
- **Software-only checks:** the dead-man boundary and arming behaviour, the command validator and the key lockout were checked by unit tests and by a native build of the firmware sources (Section 5.1a), and the heartbeat-loss analysis (Section 5.1b) is SIMULATED. None is a measurement on the assembled robot.
- **Hand-entered data:** E3, E10, E11 and E12 were transcribed after the session. E3 and E10 are contradicted by the robot's own logs and are [VERIFICATION REQUIRED]; the E11 error columns are also [VERIFICATION REQUIRED].
- **Uncontrolled environment (E6):** the two range sessions differ by about 17 dB in signal level at the same distances, the access point changed channel between them, the router position and neighbouring networks were not recorded, and the 2.4 GHz band is shared. Range and loss figures are properties of this access point and site, not of the robot.
- **Single robot, single operator, single site per experiment:** results do not estimate between-unit or between-operator variation, and no experiment was repeated on a second unit.
- **Resolution limits:** GPS positions in the telemetry log carry four decimal places (about 11 x 10 m), so the E9 statistics are resolution-limited; E1 figures are telemetry-quantised upper bounds.
- **Bench confound:** the E8 `driving` conditions state that the wheels were clear of the ground on the operator's word only, which the logs cannot confirm.
