# 4. Experimental Setup

This section defines the test environment, the experiment matrix and the baselines that apply across all fifteen experiments. Each subsection of Section 5 opens with its own procedure paragraph; shared conditions stated here are not repeated there. The hardware, network and software are specified in Sections 3.2-3.4 and are referenced, not restated.

## 4.1 Test Conditions

All experiments run on the robot as built (Table 2, Figure 3) with a single operator laptop connected to the same Wi-Fi cell. The network is the 802.11n cell described in Section 3.2: 2.4 GHz, channel 10, 20 MHz width, no internet uplink. The robot runs Raspberry Pi OS 12 (Bookworm, kernel 6.12, arm64) with Python 3.11, and the operator uses Chromium on the same laptop for both the dashboard and the SUS questionnaire. Hardware emulation is disabled for every run, so every command reaches the physical Arduino and motors.

Three test sites are used:

- Indoor laboratory (approximately 6 x 8 m): control-latency, fault-injection and resource-utilisation experiments. The operator and robot are within 3 m of the router, so the link is not a variable.
- Indoor corridor and adjoining rooms: field-trial course (Section 5.7) and usability runs (Section 5.8).
- Outdoor open area: Wi-Fi range sweep (Section 5.3) and GPS static accuracy (Section 5.6), where line-of-sight distances up to link failure are needed.

**Ethics and human-subject protocol.** The usability evaluation (Section 5.8) involves volunteer operators who complete a timed task and a System Usability Scale questionnaire. The field trial (Section 5.7) includes a role-played victim who interacts with the operator through the robot's display and speaker. All participants give informed consent, participation is voluntary, no deception is involved, and responses are recorded anonymously with a participant number only. No personally identifiable data is collected or stored. The study poses minimal risk: operators perform a short teleoperation task in a controlled indoor environment with no deception, no collection of personally identifiable information, and anonymous recording by participant number only. Under these conditions the protocol is exempt from formal ethics-committee review. Participants are briefed on the task, the data collected and their right to withdraw at any time before the session begins.

## 4.2 Experiments, Metrics and Validity Rules

Table 3 maps the fifteen experiments (E1 to E15) to the tools in `tools/eval/`, the metric each one produces, the number of trials and the Section 5 subsection that reports the result. The experiments are grouped into nine evaluation areas, one per Section 5 subsection: control latency and stopping (E1 to E4, Section 5.1), media streaming (E5, 5.2), communication range (E6, 5.3), fault injection (E7, 5.4), resource use (E8, 5.5), sensor accuracy (E9 to E12, 5.6), the field trial (E13, 5.7), usability (E14, 5.8) and cost (E15, 5.9). Every CSV is stored under `tools/eval/results/` and is cited in the Data and Code Availability statement.

**Table 3.** Experiment matrix.

| # | Experiment | Site | Trials (N) | Tool | Metric (start -> end, unit) | Section |
|---|---|---|---|---|---|---|
| E1 | Control-plane latency | Indoor lab | 30 per probe | wslatency.py | Command send -> telemetry confirmation (ms); upper bound, up to 700 ms quantisation | 5.1 |
| E2 | True control latency | Indoor lab | 30 | record.py latency_video | Key press -> wheel motion at 240 fps (ms); 4.17 ms resolution | 5.1 |
| E3 | Emergency-stop distance | Indoor lab | 20 x 3 speeds | record.py estop | Stop command -> wheels stationary: distance (cm), time (s) | 5.1 |
| E4 | Dead-man wheel-stop time | Indoor lab | 20 | record.py deadman_physical | Last heartbeat -> wheels stationary at 240 fps (s) | 5.1 |
| E5 | Video and audio streaming | Indoor lab | 20 per viewer count | record.py glass2glass | Displayed clock vs real clock (ms) | 5.2 |
| E6 | Communication range | Outdoor | Progressive distances | netsweep.py | Packet loss (%), RTT (ms), RSSI (dBm), video/control status | 5.3 |
| E7 | Fault injection and recovery | Indoor lab | 10 per target (automated); manual watch | faultinject.py run + watch | Detection time (ms), recovery time (ms), PID change (boolean) | 5.4 |
| E8 | Resource utilisation | Indoor lab | 4 conditions x 30 min | reslog.py | CPU (% of one core), memory (MB), SoC temperature (C), throttle flags | 5.5 |
| E9 | Sensor accuracy: GPS | Outdoor | 30 min static | gpsdrift.py | Radial error from centroid: mean, CEP50, CEP95 (m) | 5.6 |
| E10 | Sensor accuracy: ultrasonic | Indoor lab | 10 distances x 5 | record.py ultrasonic | True distance - reading (cm) | 5.6 |
| E11 | Sensor accuracy: temperature/humidity (DHT11) | Indoor lab | 5 set-points x 5 | record.py dht11 | Reference - sensor (degC, %RH) | 5.6 |
| E12 | Sensor accuracy: gas | Indoor lab | Qualitative | record.py gas | Baseline vs peak ADC counts, trip time (s) | 5.6 |
| E13 | Field trial | Indoor course | 5-10 runs | record.py field | Time to victim (s), collisions, two-way comms success | 5.7 |
| E14 | Operator usability (SUS) | Indoor | 8-12 operators | record.py sus | SUS score (0-100), task time (s), task success | 5.8 |
| E15 | Cost analysis | N/A | N/A | Appendix A BOM | Total cost (USD) vs literature platforms | 5.9 |

**Pass/fail thresholds.** The design in Section 3 defines four timing guarantees that the experiments must validate:

1. The dead-man stop bound of approximately 2060 ms (Section 3.5.2), tested by E4.
2. The telemetry timeout of 3000 ms that triggers mission state STOP at the operator (Section 3.6.2), observable in E1 and E7.
3. The recovery-time model of Section 3.7.2 (14.6-19.6 s for a P1 crash, including 10 s cooldown), tested by E7.
4. The lockout threshold of 5 key failures within 300 s (Section 3.8), which is a configuration constant verified during integration.

In addition, the GPS track filter of 10 m (Section 3.10) sets the boundary below which static drift produces no spurious track points, tested by E9.

**Quantisation and resolution.** The wslatency probe (E1) waits for the telemetry path to confirm a command. Because the Arduino emits telemetry every 500 ms and P1 rebroadcasts on a 200 ms timer (Section 3.6.2), the confirmation can arrive up to 700 ms after the event, making E1 figures upper bounds rather than true latencies. The 240 fps video measurement (E2) observes wheel motion directly at 4.17 ms resolution and gives the true control latency. The deadman_panic timestamp in the P1 log has millisecond resolution and is not subject to telemetry quantisation. E1 uses a 0-200 ms random jitter on the send phase (Section 3.6.2) to decorrelate trials from the P1 rebroadcast cycle; without this jitter a phase-locked sender produces a biased, deceptively tight distribution. The jitter cannot decorrelate from the 500 ms firmware cycle, which is a known limitation.

**Validity rule.** A trial is valid when the system is fully started (all three processes healthy, serial link active, no prior fault injected and not cleared), the network link is stable at the test distance, and the tool reports `ok = true`. A trial where the WebSocket connection fails to open, or where an unrelated fault occurs during measurement, is discarded and logged with a reason in the `detail` or `notes` column. Discarded trials are reported in Section 5 alongside the valid count, not silently dropped.

## 4.3 Baselines

Three kinds of baseline frame the results.

**Internal ablations.** Four configurations isolate the contribution of individual design choices:

1. Dead-man timer disabled (firmware compile-time flag): the robot continues driving after the operator link is lost, showing what the dead-man prevents.
2. P3 watchdog disabled (P1 and P2 started directly): a crashed process is not restarted, showing the value of process supervision.
3. Control and media merged into a single process: a media fault can block the control path, showing the value of the three-process split.
4. Alternative Opus bitrate (16 kbps vs the default): trades audio quality against CPU load, reported in Section 5.5.

Each ablation is run only for the experiment it informs, not across all fifteen rows.

**Specification targets.** The timing constants of Section 3 serve as pass/fail lines: the 2000 ms dead-man window, the 3000 ms telemetry timeout, and the recovery-time model bounds. These are design specifications, not measured values; the experiments test whether the implementation meets them.

**Literature baselines.** Figures reported by the platforms in the Section 2.6 comparison (Table 2.1) -- [@megalingam2022], [@verano2022], [@cafolla2026], [@jia2025], [@raghavan2026] and [@khattab2025] -- are taken from their published papers and not re-run on this hardware. The comparison in Sections 5.9 and 6.1 is qualitative plus the reported values; it is not a controlled head-to-head experiment, and the difference in test conditions is noted where each figure is compared.
