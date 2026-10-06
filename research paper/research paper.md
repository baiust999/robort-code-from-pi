# A Low-Cost, Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Interaction on Edge Hardware: Design, Implementation and Field Evaluation

## Table of Contents

- Abstract
- Keywords

---

**1. Introduction**

- 1.1 Motivation
- 1.2 Challenges
- 1.3 Research Questions
- 1.4 Contributions
- 1.5 Paper Organization

**2. Related Work**

- 2.1 Teleoperated Search-and-Rescue Robots
- 2.2 Human-Robot Interaction with Trapped Victims
- 2.3 Real-Time Video and Audio Streaming for Teleoperation
- 2.4 Fail-Safe and Fault-Tolerant Architectures for Mobile Robots
- 2.5 Low-Cost Embedded Platforms for Field Robotics
- 2.6 Research Gap

**3. Methodology**

- 3.1 Design Requirements and Principles
- 3.2 System Architecture
- 3.3 Network Configuration
- 3.4 Hardware Platform
- 3.5 Real-Time Firmware and Fail-Safe Control
  - 3.5.1 Task Scheduling and Command Validation
  - 3.5.2 Dead-Man Timer and Stop-Time Guarantee
  - 3.5.3 Redundant Stop Paths and Gas-Triggered Stop
- 3.6 Edge Control Server and Telemetry
  - 3.6.1 Safe Startup and Single-Writer Serial Link
  - 3.6.2 Telemetry Pipeline and Session Resume
- 3.7 Fault Tolerance and Supervision
  - 3.7.1 Process Isolation and Watchdog Supervision
  - 3.7.2 Recovery Time Model and Graceful Degradation
  - 3.7.3 Mission State for Operator Awareness
- 3.8 Access Control and Multi-Operator Arbitration
- 3.9 Two-Way Victim Interaction
  - 3.9.1 The P2 Media Process
  - 3.9.2 Signalling and Session Lifecycle
  - 3.9.3 Data Channel Protocol
  - 3.9.4 Operator-to-Robot Relay
  - 3.9.5 Robot Screen, Floor Control and Push-to-Talk
  - 3.9.6 Low-Latency Audio on a Constrained CPU
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
