# A Low-Cost, Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Interaction on Edge Hardware: Design, Implementation and Field Evaluation

## Table of Contents

- Abstract
- Keywords

---

**1. Introduction**

- 1.1 Motivation
  - Disaster burden and the time-critical "golden window" \cite{cred2026,tabib2024}
  - Why teleoperation remains the operationally relevant mode for confined-space
    victim contact, despite the field's shift toward full autonomy \cite{avi2026review}
- 1.2 Problem Statement and Challenges
  - C1: guaranteeing a bounded stop time on a non-real-time software stack
  - C2: single points of failure in low-cost single-board deployments
  - C3: two-way victim audio/video under CPU, power and bandwidth limits
  - C4: affordability as a deployment constraint, not a marketing claim
- 1.3 Contributions
  - RQ1-RQ3 stated here, each mapped to a contribution and answered in Section 7.1
  - Contributions mapped to C1-C4 and to the evaluation in Section 5, summarised
    in Section 7.2
  - (unnumbered closing paragraph: organization of the paper)

**2. Related Work**

- 2.1 Positioning Within the SAR Robotics Literature \cite{avi2026review,kareem2026}
  - The four-way autonomy/HRI taxonomy (Teleoperation, Supervisory Control,
    Shared-Collaborative Control, Fully Autonomous); this work is Teleoperation
  - Teleoperation is 12.8% of the 2025-2026 corpus (5 of 39 papers), yet
    Teleoperation and Supervisory Control are real-world field-validated
    60-75% of the time versus 7.4% for Fully Autonomous systems
- 2.2 Teleoperated Rescue Platforms and Their Reported Contributions
  \cite{casper2003,liu2013,daun2023,megalingam2022}
  - Contribution in existing teleoperated systems concentrates on mechanical
    capability or perception accuracy; control safety and victim-facing
    interaction are deferred or absent \cite{avi2026review}
  - Mine- and tunnel-rescue robotics outside this corpus remains predominantly
    teleoperation-oriented \cite{bakzadeh2026}
- 2.3 Fail-Safe and Fault-Tolerant Architectures for Low-Cost Mobile Robots
  \cite{pont2001,schrick2025,koczi2025,verano2022}
- 2.4 Human-Robot Interaction with Trapped Victims \cite{akgun2023,chitikena2023}
  - Across the screened 2025-2026 corpus, victims appear only as detection
    targets; no system provides two-way victim communication \cite{avi2026review}
- 2.5 Real-Time Media Streaming on Constrained Edge Hardware
  \cite{shi2025webrtc,valin2012}
- 2.6 Research Gap
  - Table 1: qualitative comparison of representative teleoperated rescue
    platforms (cost, bounded stop-time guarantee, process supervision,
    two-way victim audio, real-world field validation)
  - The gap is evidenced from a PRISMA-screened corpus, not asserted

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

- Scope rule: only what is shared across all nine experiments appears here
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
  - Table 3 (the only table in this section): experiment | site | trials (N) |
    tool under tools/eval/ | metric, start point to end point, unit | reported in
  - Nine rows, one per Section 5 subsection (5.1-5.9); tools are wslatency.py,
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

- 6.1 Interpretation of Results
- 6.2 Design Trade-offs and Lessons Learned
- 6.3 Limitations
- 6.4 Threats to Validity

**7. Conclusion**

- 7.1 Answers to the Research Questions
  - One subsection-level answer per research question, each stating the claim,
    the measured evidence from Section 5 that supports it, and the bound within
    which the claim holds
  - RQ labels and their count must match Section 1.3
    [VERIFY: Section 1.3 states RQ1-RQ3, Section 3 maps design pillars to
    RQ1-RQ4; reconcile before writing this subsection]
- 7.2 Summary of Contributions
  - Each contribution restated and mapped back to the challenge it addresses
    (C1-C4, Section 1.2) and to the subsection of Section 5 that evaluates it
  - What the system demonstrates as a whole: a bounded stop time, process
    supervision and two-way victim interaction on low-cost edge hardware
  - (unnumbered closing paragraph: what a deploying team can take from this work)

**8. Future Work**

- One item per limitation recorded in Section 6.3, in the same order, so every
  deferred item has a stated path forward
- Extending radio reach beyond a single Wi-Fi cell: repeater, mesh or second
  radio (deferred in Sections 3.2 and 6.3)
- Transport security: TLS on both ports, removing the insecure-origin exception
  the operator currently sets by hand (Section 3.2)
- Autonomy above the teleoperation tier, kept subordinate to the stop guarantee:
  supervisory or shared-collaborative control in the Section 2.1 taxonomy
- Larger operator study and field validation with trained rescue personnel,
  beyond the sample reported in Section 5.8
- Hardware extensions: thermal or gas sensing for victim detection, extended
  battery endurance, ruggedised chassis

---

- Author Contributions (CRediT)
- Funding
- Data and Code Availability
- Declaration of Competing Interest
- Acknowledgments
- References
- Appendix A: Bill of Materials
- Appendix B: Communication Protocol Specification
