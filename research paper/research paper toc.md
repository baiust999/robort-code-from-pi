# A Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Interaction on Edge Hardware: Design, Implementation and Experimental Evaluation

## Table of Contents

- Abstract
- Keywords

---

**1. Introduction**

- (opening) The robot in two sentences (Arduino UNO firmware, Raspberry Pi 4,
  local Wi-Fi, no Internet uplink); two jobs: bounded stop on link or software
  failure, and two-way contact with a trapped person; roadmap of 1.1-1.3
- 1.1 Motivation
  - Disaster burden (2025: 358 disasters, 16,607 deaths, 110.2 million affected,
    USD 169.68 billion) \cite{cred2026}; rapid SAR is critical to survival and
    communications infrastructure cannot be assumed \cite{tabib2024}; the
    phrase "golden window" is not used because the source does not name it
  - Robots in disaster response since the WTC \cite{murphy2004}; rescue robots
    are typically teleoperated \cite{daun2023}, expected to stay the default
    mode \cite{chen2007}; link loss expected, Fukushima wired link
    \cite{nagatani2013}
  - Victim need: audio-visual link \cite{schneider2016}; 4-10 h to extrication
    \cite{srinivasan2012}; two-way voice common on mine-rescue robots
    \cite{bakzadeh2026}, not reported with its cost on low-cost platforms
- 1.2 Problem Statement and Challenges
  - Design problem in one sentence; one paragraph per challenge, same order
    as Sections 2, 6 and 8, each with the Section that answers it
  - C1: bounded stop time on a non-real-time stack
    \cite{ardupilot_rover_failsafe,madhushankara2024}
  - C2: single points of failure in single-board deployments \cite{candea2004}
  - C3: two-way victim audio/video under CPU, power and bandwidth limits
  - C4: affordability as a deployment constraint; estimate only, no cost ratio
  - Gap as a combination, never a first (Section 2.6)
- 1.3 Research Questions and Contributions
  - RQ1-RQ4 as questions; RQ4 covers both the two-way victim path and GPS and
    mapping (as in Sections 3.0 and 5 and Table 8.1); each answered in
    Section 8.1
  - Four contributions mapped to C1-C4 and to Section 5, with the headline
    figure and evidence class for each (2042 ms in 30 of 30 trials, mean
    2022.5 ms, bound about 2060 ms; 30 of 30 SIGKILL recoveries, Wilson lower
    bound 88.6% \cite{wilson1927}; about 63% of one core on P2, P1 near 4%;
    about USD 320 ESTIMATE); no table, so Table 8.2 is not duplicated
  - Limits paragraph: one robot, operator and access point; drive removal, not
    wheel stop or distance (E3, E4); Wi-Fi latency, media quality, field trial
    and usability [PENDING MEASUREMENT]; ablations not run; category 0 stop,
    no compliance claim \cite{iec60204}; points to Section 6.3
  - (unnumbered closing paragraph: organization of the paper)
  - Full text: section1_introduction.md

**2. Related Work**

- (opening) Roadmap along C1-C4 (Sections 2.1-2.5 literature, 2.6 gap and
  Table 2.1); literature-selection paragraph: non-systematic OpenAlex search
  (query counts, no PRISMA claim), a second round on Pi/ROS rescue robots,
  link-loss failsafes, watchdog timers and fault tolerance, backward
  citation from the 2.1 reviews; inclusion rule for Table 2.1 (peer-reviewed,
  2022 onward, built or simulated SAR robot, full text read, one earlier
  exception); no dead-man or command-timeout study for a teleoperated rescue
  robot found among the results screened
- 2.1 Prior Reviews and Levels of Operator Involvement
  - Reviews organise the field by domain theory \cite{murphy2004hri}, control
    \cite{liu2013}, multi-robot coordination \cite{queralta2020}, deployment
    readiness \cite{delmerico2019}, component requirements
    \cite{schneider2016}, architecture \cite{kareem2026}, platform class
    \cite{sinha2026}, perception \cite{tong2024}, ethics and design
    \cite{chitikena2023}, mine-rescue design requirements
    \cite{bakzadeh2026}; none organises the field by stop-path timing or the
    cost of victim interaction
  - Levels of operator involvement along the LORA spectrum \cite{beer2014}
    (teleoperation, supervisory control, shared-collaborative control, full
    autonomy); SAR robots are tele-operated or semi-autonomous
    \cite{schneider2016}; this work is Teleoperation
    \cite{daun2023,chen2007}; teleoperation as the DARPA SubT baseline
    \cite{isaacs2022}; higher levels deferred to Section 8 as extensions
    subordinate to the Section 3.5 stop guarantee
- 2.2 Field Deployments, Benchmarks and Recent Platforms
  - Field deployments: WTC \cite{murphy2004,casper2003}; Fukushima wired
    link \cite{nagatani2013,kawatsuma2012}; Amatrice 2016
    \cite{kruijff2016}; link loss treated as an expected condition (C1, C2)
  - Benchmarks \cite{jacoff2012,chung2023}; Section 5 does not use the
    standard test apparatus, so results are not comparable with benchmark
    scores
  - Recent platforms, contribution on mobility, detection or range rather
    than the control path:
    \cite{megalingam2022,verano2022,pramono2024,deshmukh2025,manuel2022,gehlot2025,cafolla2026,jia2025,yamauchi2022,kim2023,raghavan2026,khattab2025,cantizani2022}
  - Cost asserted without figures: five designs call themselves low-cost,
    none of the recent platforms states a build cost; only Survivor Buddy
    does \cite{murphy2011}; Section 5.9 reports this robot's figure as an
    estimate (C4)
- 2.3 Fail-Safe and Fault-Tolerant Architectures for Low-Cost Mobile Robots
  - Bounded stop (C1): behaves like IEC 60204-1 stop category 0, no
    compliance claim \cite{iec60204}; time-triggered firmware
    \cite{pont2001} (Section 3.5); safety functions moving into software
    \cite{murray2022}; drone-processor watchdog detects a hung processor, not
    absent commands \cite{madhushankara2024}; ArduPilot Rover radio and
    ground-station failsafe timeouts, documentation not measured stop times
    \cite{ardupilot_rover_failsafe}; delayed-observation run-time monitor is
    complementary \cite{narasimhan2024}
  - Process supervision (C2): recovery-oriented computing
    \cite{candea2004}; microservices and state machine \cite{schrick2025};
    robot vitals \cite{ramesh2022}; humanoid safety review
    \cite{koczi2025}; FMEA-based simulation of hardware-failure mitigation
    \cite{sini2022}; none targets a single-board rescue robot; Section 3.7
    applies recovery-oriented supervision; no platform in Table 2.1 reports a
    hardware-level stop guarantee or supervised process recovery
- 2.4 Human-Robot Interaction: Operator and Victim
  - Operator side: situation awareness \cite{endsley1995}; bandwidth, lag and
    frame-rate decrements \cite{chen2007}; network latency
    \cite{kamtam2024,luz2023}; interface design and rescuer needs
    \cite{bakzadeh2025,bakzadeh2026b}; attention cues and LED expressions
    \cite{ruan2025,akgun2023}; addressed by the Section 3.6 dashboard
  - Victim side (C3): audio-visual requirement \cite{schneider2016}; 4-10 h
    between discovery and extrication \cite{srinivasan2012}; non-verbal
    affect \cite{bethel2007}; Survivor Buddy and its evaluations
    \cite{murphy2010,murphy2011,srinivasan2012}; two-way voice fundamental on
    fielded mine-rescue robots, outside the low-cost scope \cite{bakzadeh2026}
  - Recent platforms: victim as detection target
    \cite{raghavan2026,khattab2025,kim2023,cantizani2022,deshmukh2025,sharma2022};
    speech toward the victim described but not tested
    \cite{cafolla2026,yamauchi2022}; one-way microphone \cite{verano2022};
    speaker and microphone provisioned, not implemented \cite{khattab2025};
    walkie-talkie, video recorded not streamed \cite{manuel2022}
  - Conclusion: two-way victim communication is an established requirement,
    not a first; what is not demonstrated is two-way audio and video on
    single-board hardware and its CPU, power and bandwidth cost (C3)
- 2.5 Real-Time Media and Computing on Edge Hardware
  - WebRTC teleoperation \cite{shi2025webrtc,tiberkak2023}, both dependent on
    external servers; multi-operator arbitration and floor control
    (Sections 3.8, 3.9.4); TXRob one-way video without WebRTC
    \cite{verano2022}; this robot runs both WebRTC endpoints and signalling
    locally (Sections 3.2, 3.9)
  - Opus frame sizes \cite{valin2012}; glass-to-glass delay measurement
    \cite{bachhuber2016}; return in Sections 3.9.5 and 5.2
  - Cloud/edge placement: cloud-to-edge-to-IoT continuum \cite{militano2023};
    cloud-dependent platforms \cite{raghavan2026,cafolla2026}; infrastructure-
    free alternatives \cite{manuel2022,nagatani2013}; control, two-way media
    and supervision together on one single-board computer not characterised;
    budget reported in Section 5.5
- 2.6 Research Gap
  - Table 2.1: 13 platforms plus this work; columns for platform and control,
    link and computing, C1-C4, code availability, evidence and conditions,
    text read; NR (not reported) distinguished from "(stated)" cells; all
    other-platform C1 and C2 cells NR; Survivor Buddy included
    \cite{murphy2010,murphy2011} as the closest prior work on C3 although it
    predates 2022; mine-rescue robots \cite{bakzadeh2026} and field studies,
    benchmarks and surveys not tabulated
  - Gap stated as a combination (bounded stop C1, supervised recovery C2,
    two-way victim audio/video with resource cost C3, stated cost C4); no
    part claimed as a first; Section 3 combines established mechanisms on
    commodity hardware, Section 5 reports which properties the measurements
    support
  - Full texts read for all 13 other rows (Survivor Buddy: both Murphy
    papers; srinivasan2012 abstract only); cells corrected 2026-10-23 where
    the full text differed (see citation.md)
  - Full text: section2_related_work.md

**3. Methodology**

- 3.1 System Architecture
- 3.2 Network Configuration
- 3.3 Hardware Platform
- 3.4 Software Architecture
- 3.5 Real-Time Firmware and Fail-Safe Control
  - 3.5.1 Task Scheduling and Command Validation
  - 3.5.2 Dead-Man Timer and Stop-Time Guarantee
  - 3.5.3 Redundant Stop Paths
- 3.6 P1 Control Server and Telemetry
  - 3.6.1 Safe Startup and Single-Writer Serial Link
  - 3.6.2 Telemetry Pipeline and Session Resume
- 3.7 Fault Tolerance and Supervision
  - 3.7.1 P3 Watchdog: Process Isolation and Supervision
  - 3.7.2 Recovery Time Model and Graceful Degradation
  - 3.7.3 Mission State for Operator Awareness
- 3.8 Access Control and Multi-Operator Arbitration
- 3.9 Two-Way Victim Interaction
  - 3.9.1 The P2 Media Process
  - 3.9.2 Signalling and Session Lifecycle
  - 3.9.3 Data Channel Protocol
  - 3.9.4 Operator-to-Robot Relay and Floor Control
  - 3.9.5 Low-Latency Audio on a Constrained CPU
- 3.10 GPS Localisation and Offline Mapping

**4. Experimental Setup**

- Scope rule: only what is shared across all fifteen experiments appears here
  (test conditions, metric definitions, baselines). Procedure specific to one
  experiment opens the matching Section 5 subsection, so nothing is described
  twice. Hardware, network and software are specified in Sections 3.2-3.4 and
  are not restated.
- 4.1 Test Conditions
  - One paragraph: the robot as built (Table 2, Figure 3), operator laptop and
    browser, single 802.11n cell (Section 3.2), MOCK_HARDWARE off for all runs
  - Test sites: indoor corridor and lab for latency, fault and resource runs;
    outdoor area for range and GPS runs
- 4.2 Experiments, Metrics and Validity Rules
  - Table 4.1 (the only table in this section): experiment | site | trials (N) |
    tool under tools/eval/ | metric, start point to end point, unit | reported in
  - Fifteen rows (E1-E15) in nine groups, one per Section 5 subsection
    (5.1-5.9); tools are wslatency.py,
    faultinject.py, netsweep.py, reslog.py, gpsdrift.py, record.py and
    summarize.py, raw output under tools/eval/results/
  - Pass/fail thresholds from Section 3, stated in one sentence: 2000 ms
    dead-man window, 3000 ms telemetry timeout, 500 ms telemetry cadence
    (Sections 3.5.2, 3.6.2)
  - Validity rule for a trial and discard criteria, stated once
- 4.3 Baselines
  - Internal ablations: dead-man timer removed, P3 watchdog disabled, control
    and media in one process, alternative audio bitrate
  - Specification targets from Section 3 as pass/fail thresholds
  - Literature baselines: figures reported by the platforms in the Section 2.6
    comparison \cite{casper2003,liu2013,daun2023,megalingam2022}, taken from
    their papers and not re-run; comparison is qualitative plus reported values,
    not a controlled head-to-head

**5. Results**

- Each subsection opens with its own short procedure paragraph (what was run and
  how), then reports the numbers; Section 4 is not repeated and no new metric is
  introduced here
- 5.1 Control Latency and Emergency-Stop Response
- 5.2 Video and Audio Streaming Performance
- 5.3 Communication Range and Link Degradation
- 5.4 Fault Injection and Recovery Time
- 5.5 Resource Utilization on the Edge Device
- 5.6 Sensor Accuracy and GPS Track Quality
- 5.7 Field Trial: End-to-End Rescue Scenario
- 5.8 Operator Usability Evaluation
- 5.9 Cost Analysis and Comparison with Existing Systems

**6. Discussion**

- (opening) Scope: interprets Section 5 against C1-C4; no new measurement or
  metric; every figure is taken from a Section 5 table with its evidence class;
  RQ answers stay in Section 8.1, future directions in Section 7
- 6.1 Interpretation of Results
  - Table 6.1: per challenge (C1-C4), the claim supported, the evidence and its
    class, the bound and what is not shown
  - One paragraph per challenge: C1 bound is on silence not on the link
    (2042 ms; F7 stop 21 s before socket close; margin depends on heartbeat
    rate); C2 supervision turns loss of service into a bounded outage (30/30;
    F6 marks the edge); C3 feasibility and cost only (about 63% of one core;
    P1 unaffected; no quality data; a combination, not a first); C4 plausible
    but not demonstrated (USD 320 ESTIMATE, replacement supply unpriced)
  - Relation to the literature: qualitative, Table 2.1 "NR" is not absence,
    no head-to-head, no cost ratio
    \cite{verano2022,khattab2025,manuel2022,ardupilot_rover_failsafe,candea2004,chen2007,bakzadeh2026}
- 6.2 Design Trade-offs and Lessons Learned
  - Table 6.2: decision | gain | cost, each with its evidence (dead-man window,
    three-process split, single serial writer, 10 m GPS filter)
  - Lessons from the build and audit: a test count is not evidence about the
    firmware (mock vs compiled source); budget resources on the intended
    supply; hand-entered data needs an independent log; experiment
    configuration belongs in version control; choose instrument resolution
    before the run
- 6.3 Limitations
  - Seven claims the paper does not make (physical stop timing, end-to-end
    performance, benefit over a baseline, fault and environment coverage,
    unverified sensors, software-only checks, cost); points to Table 5.0 and
    Section 4.4 instead of repeating them
- 6.4 Threats to Validity
  - Table 6.3: internal, construct, external and conclusion threats with
    mitigation and residual; itemised deviations stay in Section 4.4
  - Two comments: the latency jitter and the phase-locked control run
    (referenced from Section 5.1); the limit of the log audit itself
  - Full text: section6_discussion.md

**7. Future Work**

- (opening) Scope and constraint: every direction starts from a limitation
  stated in Section 3 or measured in Section 5, names its baseline and fixes its
  metrics in advance; none is an existing capability and none is claimed as
  novel; the firmware dead-man stop (Section 3.5.2) stays independent of any
  added automated function; three priority levels
- Table 7.1: future-work directions, limitation addressed, evidence section,
  priority level and dependencies
- 7.1 Communication Resilience
  - 7.1.1 Multi-Hop Mesh Networking
  - 7.1.2 Communication-Aware Mission Planning
- 7.2 Fault Detection and Quantitative Fail-Safe Validation
  - 7.2.1 Cross-Layer Fault Detection and Recovery
  - 7.2.2 Quantitative Safety and Fault-Injection Evaluation
  - 7.2.3 Simulation-Based Validation
- 7.3 GPS-Denied Localization and Return Navigation
  - 7.3.1 Indoor Localization and Mapping
  - 7.3.2 Trajectory Tracking and Visualization
  - 7.3.3 Autonomous Return Navigation
  - 7.3.4 Localization-Aware and Obstacle-Aware Navigation
- 7.4 Platform: Mobility, Thermal Protection and Energy
  - 7.4.1 Compact, Low-Profile Chassis Design
  - 7.4.2 Heat-Resistant Structural Protection
  - 7.4.3 Improved Disaster-Terrain Mobility
  - 7.4.4 Energy-Aware Operation
- 7.5 Hazard Sensing and Edge-Based Victim Assistance
  - 7.5.1 Sensor Fusion for Hazard Assessment
  - 7.5.2 Edge-Based Victim Assistance
- 7.6 Security, Multi-Robot Scale and Reproducibility
  - 7.6.1 Secure Remote Control
  - 7.6.2 Multi-Robot Cooperative Exploration
  - 7.6.3 Reproducible Experimental Benchmarking

**8. Conclusion**

- (opening) Summary of the work; conclusions apply to the robot as built and
  tested; no new measurement, metric or citation
- 8.1 Answers to the Research Questions
  - Table 8.1: RQ | topic (challenge) | answer | evidence and class | scope of
    the claim
  - RQ1 stop time (C1); RQ2 control path, serial link, session resume; RQ3
    supervision (C2); RQ4 victim path (C3) and GPS; labels follow Sections 3 and 5
  - One short paragraph per RQ
- 8.2 Summary of Contributions
  - Table 8.2: contribution | challenge (C1-C4) | evaluated in | evidence class |
    what is claimed
  - What the system shows as a whole; contribution stated as a combination, not
    a first
- (unnumbered closing paragraph: what a deploying team can take; points to
  Section 7)
  - Full text: section8_conclusion.md

---

- Author Contributions (CRediT)
- Funding
- Data and Code Availability
- Declaration of Competing Interest
- Acknowledgments
- References
- Appendix A: Bill of Materials
- Appendix B: Communication Protocol Specification




















