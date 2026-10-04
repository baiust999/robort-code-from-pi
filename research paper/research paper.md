# A Low-Cost, Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Interaction on Edge Hardware: Design, Implementation and Field Evaluation

## Table of Contents

- Abstract
- Keywords

---

**1. Introduction**

- 1.1 Motivation: The Need for Affordable Search-and-Rescue Robots
- 1.2 Challenges: Safety, Communication Reliability and Victim Interaction on Low-Cost Hardware
- 1.3 Research Questions
- 1.4 Contributions
- 1.5 Paper Organization

**2. Related Work**

- 2.1 Teleoperated Search-and-Rescue Robots
- 2.2 Human-Robot Interaction with Trapped Victims
- 2.3 Real-Time Video and Audio Streaming for Teleoperation
- 2.4 Fail-Safe and Fault-Tolerant Architectures for Mobile Robots
- 2.5 Low-Cost Embedded Platforms for Field Robotics
- 2.6 Comparative Summary and Research Gap

**3. System Architecture**

- 3.1 Design Requirements and Architectural Invariants
- 3.2 Overall System Architecture: Four Tiers and Two Independent Transports
- 3.3 Hardware Platform
  - 3.3.1 Locomotion and Actuation
  - 3.3.2 Sensing Suite (Gas, Temperature/Humidity, Ultrasonic Range, GPS)
  - 3.3.3 Audio-Visual Interaction Hardware (Camera, Microphone, Speaker, Robot Display)
  - 3.3.4 Power Architecture and Electrical Isolation of the Edge Computer
- 3.4 Software Stack Overview
  - 3.4.1 Microcontroller Firmware
  - 3.4.2 Edge Processes: Control (P1), Media (P2) and Watchdog (P3)
  - 3.4.3 Operator Dashboard
- 3.5 Network Configuration: Local-Network-Only Operation

**4. Methodology**

- 4.1 Methodology Overview
  - 4.1.1 Design Philosophy: Independent Failure Domains and Lowest-Tier Safety Authority
  - 4.1.2 Architectural Drivers and Their Structural Consequences
  - 4.1.3 Protocol Contract as the Sole Inter-Tier Coupling
  - 4.1.4 End-to-End Command, Telemetry and Media Flows
  - 4.1.5 Emulation-Based Development and Verification Without Hardware
- 4.2 Real-Time Embedded Control
  - 4.2.1 Cooperative Task Scheduler and Bounded Blocking
  - 4.2.2 Timer Allocation for Motor PWM and Servo Control
  - 4.2.3 Four-Stage Command Validation in Firmware
  - 4.2.4 Firmware Operating Modes and Fault Handling
  - 4.2.5 Differential-Drive Control and PWM Ramping
- 4.3 Layered Fail-Safe Command Pipeline
  - 4.3.1 Overview of Defense-in-Depth Command Validation
  - 4.3.2 Edge-Side Validation: Role Check, Clamping and Sequence Monotonicity
  - 4.3.3 Speed Limiting and the PWM-Voltage Relationship
  - 4.3.4 Heartbeat Keep-Alive and Dead-Man Timeout: Stop-Time Guarantee
  - 4.3.5 Redundant Stop on Controller Disconnect
  - 4.3.6 Emergency-Stop Path and Priority Handling
  - 4.3.7 Gas-Triggered Autonomous Panic Stop
  - 4.3.8 Advisory Obstacle Ranging
- 4.4 Edge Control Server and Telemetry Pipeline
  - 4.4.1 Overview of the Telemetry Pipeline
  - 4.4.2 Serial Bridge and Safe Startup Handshake
  - 4.4.3 Single-Writer Enforcement on the Serial Link
  - 4.4.4 Telemetry Framing and the Discard-Don't-Retransmit Policy
  - 4.4.5 Rate Decoupling and Drift-Free Periodic Broadcast
  - 4.4.6 Telemetry Snapshot Construction and Protection of Server-Owned Fields
  - 4.4.7 Ring Buffer and Session-Resume Protocol
  - 4.4.8 Alert Classification, Thresholds and Bit-Packed Logging
- 4.5 Fault-Tolerant Supervision and Recovery
  - 4.5.1 Overview of the Three-Tier Supervision Hierarchy
  - 4.5.2 Process Isolation of Control and Media
  - 4.5.3 Two-Level Liveness Detection: Process Polling and HTTP Health Checks
  - 4.5.4 Exit-Code Discrimination and Restart Policy
  - 4.5.5 Fault Detection and Recovery Time Model
  - 4.5.6 Graceful Degradation and Operational Modes
- 4.6 Mission State Derivation and Operator Awareness
  - 4.6.1 First-Match Mission State Function
  - 4.6.2 Asymmetric Reconnection Policy for Control and Media
- 4.7 Two-Way Victim Interaction Channel
  - 4.7.1 Overview of the Bidirectional WebRTC Architecture
  - 4.7.2 Single-Shot Signalling on a Local Network
  - 4.7.3 Shared Device Capture and Multi-Session Fan-Out
  - 4.7.4 Per-Session Frame Isolation to Prevent Concurrent-Encoder Faults
  - 4.7.5 Application-Level Opus Packetisation for Real-Time Audio on a Constrained CPU
  - 4.7.6 Playout Cushion and Bounded Latency for Victim-Side Audio
  - 4.7.7 Resilient Capture: Synthetic Fallback and Microphone Recovery
  - 4.7.8 Robot-Screen Relay, Floor Control and Push-to-Talk Echo Avoidance
  - 4.7.9 Display-Mode Arbitration and Protection Against Accidental Input
- 4.8 Access Control and Multi-Operator Arbitration
  - 4.8.1 Controller and Observer Roles
  - 4.8.2 Controller-Key Authentication and Takeover
  - 4.8.3 Brute-Force Lockout
  - 4.8.4 Cross-Process Role Consistency Between Control and Media
- 4.9 GPS Localisation and Path Tracking
  - 4.9.1 NMEA Acquisition with Checksum Verification
  - 4.9.2 Ground-Distance Computation (Haversine Formula)
  - 4.9.3 Drift-Suppression Algorithm
  - 4.9.4 Offline Vector-Map Serving with HTTP Range Requests

**5. Experimental Setup**

- 5.1 Test Environment and Hardware Configuration
- 5.2 Evaluation Metrics
- 5.3 Experimental Scenarios and Procedures
- 5.4 Baselines for Comparison

**6. Results**

- 6.1 Control Latency and Emergency-Stop Response Time
- 6.2 Video and Audio Streaming Performance (Latency, Frame Rate, Delivery Ratio)
- 6.3 Communication Range and Link Degradation Behavior
- 6.4 Fault Injection and Recovery Time
- 6.5 Computational Load and Resource Utilization on the Edge Device
- 6.6 Sensor Accuracy and GPS Track Quality
- 6.7 Field Trial: End-to-End Rescue Scenario
- 6.8 Operator Usability Evaluation
- 6.9 Cost Analysis and Comparison with Existing Systems

**7. Discussion**

- 7.1 Interpretation of Results
- 7.2 Design Trade-offs and Lessons Learned
- 7.3 Limitations
- 7.4 Threats to Validity

**8. Conclusion and Future Work**

---

- Author Contributions (CRediT)
- Funding
- Data and Code Availability
- Declaration of Competing Interest
- Acknowledgments
- References
- Appendix A: Bill of Materials
- Appendix B: Communication Protocol Specification
