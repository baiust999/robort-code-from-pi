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
  - RQ1-RQ3 stated here, each mapped to a contribution and answered in Section 8.1
  - Contributions mapped to C1-C4 and to the evaluation in Section 7
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

- 4.1 Test Environment and Hardware Configuration
- 4.2 Evaluation Metrics
- 4.3 Experimental Scenarios and Procedures
- 4.4 Baselines for Comparison

**5. Results**

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

**7. Conclusion and Future Work**

---

- Author Contributions (CRediT)
- Funding
- Data and Code Availability
- Declaration of Competing Interest
- Acknowledgments
- References
- Appendix A: Bill of Materials
- Appendix B: Communication Protocol Specification
