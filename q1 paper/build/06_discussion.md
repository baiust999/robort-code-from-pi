## VI. DISCUSSION

### A. Interpretation Against the Challenges

*C1: the stop is bounded on the silence, not on the link.* The firmware removed drive within 2042 ms of the last command in every logged trial, and the decision runs in the firmware's own supervisor task rather than in a Linux process. The Wi-Fi drop of F7 shows the practical consequence: the firmware stopped 2.02 s into the outage, more than 20 s before the control socket closed. Two limits apply. First, "stopped" means that drive was removed electrically; how far and how long the robot coasts afterwards is not established, and the only stopping-distance data contradict the ramp model and the logs. Second, the guarantee is on silence between valid commands, so its margin against a lossy link depends on how often the dashboard sends them. At the configured 500 ms heartbeat two consecutive losses are tolerated, but the dashboard delivered 1.00 s heartbeats in some sessions, at which a single loss trips the dead-man. The stop remained safe in every observation, while its availability under loss was lower than designed in those sessions. Because the window is re-armed by any valid command, including pan and status queries, a dashboard that kept sending camera commands but no heartbeat would also keep the robot armed; this is intended, since the firmware stops motion only when nothing valid arrives, but it means the window bounds silence, not the age of the last drive command.

*C2: supervision turns a crash into a bounded, safe outage.* All 30 SIGKILL trials recovered, in 12.8 to 16.0 s on average. Recovery takes seconds because of the fixed cooldown, so the contribution is not fast recovery in the sense of recovery-oriented computing [@candea2004] but that the outage cannot leave the motors driven, because the dead-man, which depends on no Pi process, holds them stopped meanwhile. The F6 unplug marks the edge of the claim: P1 stayed up, as the isolation intends, but did not reopen the re-enumerated device, so a cable fault needs a P1 restart.

*C3: the victim path fits the processor budget and stays off the control process.* One operator session cost about 63% of one core on P2 while P1 stayed near 4%, so the media load fell on a process that carries no drive or stop command. That holds only with an adequate supply: the original power bank under-volted on 276 of 299 samples under the same load. What this evidence cannot support is any statement about the quality of the victim interaction. Delay, frame rate, intelligibility and the victim's experience were not measured, and no run exercised the path end to end. The C3 result is therefore feasibility and processor cost, consistent with the gap of Section II-F, which is a combination and not a first: two-way voice is common on fielded mine-rescue robots [@bakzadeh2026].

*C4: low cost is receipt-backed but incomplete.* The total of about USD 310 is dominated by the Pi with its display and by the motor drive. It omits the webcam, speaker and power bank, and none of the comparison platforms reports a build cost, so no ratio is claimed.

*Relation to the literature.* The comparison with Table I rests on what each paper reports, so it is qualitative. Within that limit, TXRob sends video and audio one way [@verano2022], a planned victim speaker and microphone is not implemented [@khattab2025], and a LoRa-linked robot offers push-to-talk audio without a video stream [@manuel2022]; no recent platform in the table reports a firmware-bounded stop time or supervised process recovery, while link-loss failsafes are documented in general-purpose autopilot software [@ardupilot_rover_failsafe]. What this paper adds is that the timing, recovery and processor cost of these mechanisms are measured together on one low-cost robot. Because no Wi-Fi latency exists for this robot, its control path cannot yet be placed against the human-factors literature on teleoperation latency [@chen2007; @luz2023].

### B. Design Trade-offs and Lessons

Each major design decision traded one property for another (Table XVIII).

**TABLE XVIII.** Design decisions, what each bought and what each cost.

| Decision | Gain (evidence) | Cost (evidence) |
|---|---|---|
| 2000 ms dead-man window, 500 ms heartbeat | Stop bounded at 2042 ms regardless of transport (Table IX); two lost heartbeats tolerated (Table XI) | A 2.080 s silent gap tripped it (Table X); at a 1.00 s heartbeat one loss trips it |
| Control, media and supervision in separate processes | P1 near 4% of one core with or without media (Table XIV) | Recovery of a crashed process takes 12.8-16.0 s (Table XIII); the benefit over one process was not measured |
| Single serial writer, no automatic reopen | No competing writers on the Arduino link | After an unplug the device node changed and recovery needed a P1 restart (F6) |
| 10 m GPS track filter | Intended to suppress drift around a stopped robot | 130 points and 1609 m of path from a robot that was not driven |

Four lessons came from the build and the audit of the data. First, a test count is not evidence about the firmware: the Pi suite passed while its Arduino emulator differed from the compiled firmware on the trip boundary and the re-arming rule, which only a native build of the unmodified firmware sources revealed. Second, resource budgets must be captured on the intended supply with the throttle word recorded, since the first media capture was valid as a finding about the original power bank and invalid as a resource figure. Third, hand-entered data need an independent log: three of the four hand-entered sheets failed the cross-check against the robot's logs, and only those logs could separate sound transcription from unsupported entry. Fourth, experiment configuration and instrument resolution belong in the protocol before the run: the 16 kbit/s setting existed only as an uncommitted change, and the four-decimal GPS log bounded E9 although P1 held six decimals in memory.

### C. Limitations

1. The wheel-stop time and the distance covered after drive is removed (E4) are not established; the paper claims a bounded time at which drive is removed, not a bounded stopping distance.
2. Control latency over Wi-Fi was not measured, media delay and quality (E5), the field trial (E13) and victim communication under degraded conditions (E17) have no data, and operator usability was not evaluated. No claim is made about operator performance, victim experience or rescue effectiveness, and no human-subject data exist.
3. No measured benefit over a baseline is claimed for the dead-man or the watchdog (Section IV-E), and the media-isolation test of the process split (E16) has not been run.
4. Fault coverage is SIGKILL crashes plus single manual injections; hangs and camera and microphone loss were not injected. The range sweep is line-of-sight, partial and without a failure point, on one access point.
5. The control key travels over plain HTTP and WebSocket, there is no TLS on either port, and microphone capture in the operator's browser relies on a manual insecure-origin exception. Security is out of scope beyond a trusted local network.
6. The operator aids of Section III-K are implemented but not evaluated. E17 and E18 now cover the victim channel and the detector, both [PENDING MEASUREMENT] with criteria fixed in Table XVII; victim marks and the session recording remain uncovered, and no claim is made for any of these features.
7. The bill of materials omits three parts and the replacement Pi supply, and its USD figure rests on one indicative exchange rate.

### D. Threats to Validity

*Internal.* The resource conditions were captured on different days with different process uptimes and an active remote-desktop session, so their differences are described, not attributed. The two range sessions differ by about 17 dB at the same distances for an unrecorded reason. The wheels-clear premise of the driving conditions rests on the operator's word; a later session run on the same stated premise is known to have taken place with the robot on the floor, so the premise is unverified. Hand-entered rows carry entry time; the cross-check against machine logs mitigates this only where the logs record the quantity.

*Construct.* Telemetry-confirmed latencies are upper bounds that exclude Wi-Fi. "Stop" is measured as removal of drive. ICMP loss to the router is not heartbeat loss, and the heartbeat-loss model is simulated with independent loss. GPS precision is bounded by the four-decimal log.

*External.* One robot, one operator, one access point and one site per experiment; short indoor runs with the SoC at or below 52.6 deg C. Nothing here estimates variation between units, operators, networks or environments, and no test used rubble, slopes or standard apparatus.

*Conclusion.* Samples are small: 10 to 30 trials per condition and 5 readings for the sensors. Intervals are reported, no significance test is applied, and a 95th percentile of 30 values is descriptive only. The audit checks that entries agree with the robot's logs, not that each entry is the result of the physical procedure described.
