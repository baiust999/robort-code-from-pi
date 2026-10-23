# 8. Conclusion

This paper presented a teleoperated rescue robot built on commodity single-board hardware and evaluated three properties of it: a stop time enforced by the motor-controller firmware, supervised recovery of the Pi processes, and the processor cost of a two-way audio and video path to a victim. The conclusions apply to the robot as built and tested, with one operator and one access point. No new measurement, metric or citation is introduced here; every figure is taken from Section 5 and keeps the evidence class stated there.

## 8.1 Answers to the Research Questions

**Table 8.1.** Answer to each research question, the evidence behind it and the scope within which it holds.

| RQ | Topic (challenge) | Answer | Evidence (class) | Scope of the claim |
|---|---|---|---|---|
| RQ1 | Bounded stop time (C1) | The firmware removes motor drive within 2042 ms of the last command, whatever the state of the operator link | Table 5.2b: 30 of 30 trials, mean 2022.5 ms, analytical bound about 2060 ms (MEASURED, CALCULATED); drive removed 2.02 s into an injected Wi-Fi drop (Table 5.9a, MEASURED) | Time at which drive is removed, not stopping distance or wheel rest; margin depends on the heartbeat rate (Table 5.9d) |
| RQ2 | Control path, single-writer serial link, session resume | The control path runs with robot-internal latency upper bounds, and the link was exercised to 250 m line of sight without a failure point | Table 5.1 (MEASURED, upper bounds that exclude Wi-Fi); Section 5.3 (MEASURED) | Latency figures are upper bounds; range is a lower bound for this access point and line of sight |
| RQ3 | Process supervision and recovery (C2) | The watchdog restored service with a new PID in 30 of 30 SIGKILL trials, with the dead-man holding the motors stopped meanwhile | Tables 5.8, 5.8a (MEASURED); P1 recovery 16.03 s (95% CI 15.93 to 16.13 s) inside the 14.6 to 19.6 s window (PREDICTED) | Bench crash faults; pooled failure probability below 11.4% at 95% confidence; hardware faults such as F6 need a P1 restart |
| RQ4 | Two-way victim path (C3) and GPS and mapping | One operator media session costs about 63% of one core on P2 while P1 stays near 4%; GPS static precision was computed to the resolution of the log | Tables 5.10, 5.10b (MEASURED); Section 5.6.1 (MEASURED) | Processor cost on an adequate supply; GPS precision is resolution-limited |

**RQ1.** The interval from the last command written to the Arduino to the firmware's PANIC line never exceeded 2042 ms in 30 logged trials, below the analytical bound of about 2060 ms. The decision is taken in the firmware's own safety task and not in a Linux process, so the bound holds on the silence between commands and not on the state of the link: in the injected Wi-Fi drop the firmware stopped drive 2.02 s into the outage, about 21 s before the control socket closed. At the configured 500 ms heartbeat two consecutive lost heartbeats are tolerated, while at the 1.00 s interval seen in some sessions a single loss trips the dead-man (Table 5.9d), so the availability of the control path under loss depends on the heartbeat rate that the dashboard sustains.

**RQ2.** The control-plane latencies of Section 5.1 are measured inside the robot and are upper bounds that exclude Wi-Fi. The range sweep covered 16 line-of-sight stations from 5 to 250 m on one access point and reached no failure point, so 250 m is a lower bound on usable range for that setting. Ping loss of 0 to 16% did not track distance, and the two sessions differed by about 17 dB at the same distances. These results characterise the control path of this robot on this network.

**RQ3.** All 30 SIGKILL trials recovered with a confirmed new PID, with mean recovery between 12.8 s (P3) and 16.0 s (P1). Recovery takes seconds because of the fixed cooldown of the respawn path; the contribution is that the outage cannot be unsafe, since the dead-man holds the motors stopped while the process is down. The result concerns process crashes on the bench. A removed Arduino (F6) is outside it: P1 stayed up but needed a restart to reopen the re-enumerated device.

**RQ4.** For the victim path, the result is a processor budget: 62.92% of one core on the media process with an operator stream (95% CI 62.22 to 63.67) against 1.12% without, with P1 at 3.81% against 3.74% (overlapping intervals) and the SoC at or below 52.6 deg C. This holds on an adequate supply; on the original power bank the same load produced under-voltage on 276 of 299 samples. The path therefore fits within the edge hardware's budget and is isolated from the control process. For GPS, static precision was computed to the four-decimal resolution of the telemetry log, and the 10 m track filter admitted drift from a stationary robot.

## 8.2 Summary of Contributions

**Table 8.2.** Contributions, the challenge each addresses, the Section 5 subsection that evaluates it and what is claimed.

| Contribution | Challenge | Evaluated in | Evidence class | What is claimed |
|---|---|---|---|---|
| Firmware dead-man timer with ramp stop on the motor controller, independent of the Pi (Section 3.5) | C1 | 5.1, 5.1a, 5.1b, 5.4 | MEASURED (log interval); SOFTWARE-TEST and SIMULATED (supporting) | A bounded time at which drive is removed |
| Three-process split with a P3 watchdog and a single serial writer (Sections 3.4, 3.6, 3.7) | C2 | 5.4, 5.5 | MEASURED; PREDICTED (recovery window) | Automatic recovery of a killed process in 30 of 30 bench trials; control process unaffected by media load in the measured conditions |
| Two-way audio and video path on the Pi, isolated in its own process (Section 3.9) | C3 | 5.5 | MEASURED (processor cost) | Feasibility and processor cost for one operator session |
| Commodity bill of materials (Appendix A) | C4 | 5.9 | RECEIPT-BACKED | About USD 310 from itemised receipts (37,158 BDT); no cost ratio |

Taken together, the measurements show a robot on which the stop is timed at the firmware and not the link, a crashed process is restarted without leaving the motors driven, and a media session fits on the edge device beside the control process. As Section 2.6 states, the contribution is a combination of these properties on low-cost hardware and not a first for any one of them: link-loss failsafes exist in general-purpose autopilot software, and two-way voice is common on fielded mine-rescue robots. What is added is that their timing, recovery and cost are reported together for one robot, with the evidence class of every figure stated. Affordability (C4) is supported by the authors' receipts: the recorded commodity parts total about USD 310.

## Closing

A team that adopts this work can take three things from it: a firmware-enforced stop interval that does not depend on the Linux stack or the link, a supervised three-process layout whose measured outage is seconds and safe, and a measured processor budget for one operator media session, together with the practice of cross-checking hand-entered data against the robot's machine logs (Sections 5 and 6.2). The directions that extend these results, including physical timing of the stop, control latency over Wi-Fi and the quality of the victim interaction, are set out in Section 7.
