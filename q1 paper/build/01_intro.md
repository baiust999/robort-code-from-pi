## I. INTRODUCTION

In 2025 the Emergency Events Database recorded 358 natural-hazard disasters, which caused 16,607 deaths and affected 110.2 million people [@cred2026]. After such events the communications infrastructure that rescue teams rely on cannot be assumed to work [@tabib2024]. Robots have been used in urban search and rescue (SAR) since the collapse of the World Trade Center in 2001 [@murphy2004], and in actual disasters they are typically teleoperated [@daun2023]; teleoperation is expected to remain an important default mode even for autonomous systems [@chen2007]. The radio link between operator and robot is the weak point of that arrangement. At Fukushima Daiichi, tests indicated that reliable wireless communication would not be possible inside the reactor buildings, and the robot sent there was fitted with a wired communication device [@nagatani2013]. A robot driven over a radio link therefore has to decide for itself what to do when commands stop arriving.

A second requirement appears once the robot reaches a trapped person. A SAR robot should provide audio-visual communication between the operator and the victim, so that a responder can make a basic diagnosis [@schneider2016], and on average four to ten hours pass between discovery and extrication [@srinivasan2012]. Two-way voice is a fundamental function of most mine-rescue robots reviewed in [@bakzadeh2026], but those are specialized, costly platforms. Among the recent low-cost platforms compared in Section II, none reports two-way audio and video with the victim, or how much of a small computer that channel consumes while the same computer also drives and supervises the robot.

### A. Problem Statement and Challenges

The design problem is to build a teleoperated rescue robot on hardware cheap enough to be replaced, in which the stop behaviour does not depend on the weakest part of that hardware. Four challenges follow, and the rest of the paper uses the same labels.

*C1, a bounded stop time on a non-real-time software stack.* A stop decision taken by a Linux process inherits the scheduling and crash behaviour of that process. If the process stalls or dies while the robot is driving, the last drive command stays in force. Link-loss failsafes and watchdog timers are established techniques [@ardupilot_rover_failsafe; @madhushankara2024]; the open questions for a low-cost rescue robot are where the decision runs and what time it achieves.

*C2, single points of failure on one board.* If control, video and supervision share one process, a crash in any of them can end the mission. Recovery by restart, with several lines of defence because recovery can itself fail, is an established dependability strategy [@candea2004]. The challenge is to keep the robot either controllable or stopped when any one process fails, and to restore service without anyone going to the robot.

*C3, two-way victim audio and video under CPU, power and bandwidth limits.* Capturing, encoding and decoding media competes with the control path for processor time, supply current and the one Wi-Fi cell. The challenge is to carry the victim channel on the same board without weakening the stop path, and to report what it costs.

*C4, affordability.* Recent platforms are often described as low-cost, but none of those compared in Section II states a build cost.

Each challenge has prior work taken alone. What the platforms in Table I do not report together is a stop time bounded independently of the higher-level software, supervised recovery of the robot's processes, and two-way audio and video with the victim together with its resource cost, on low-cost hardware. The contribution of this paper is that combination with its measurements; no single part is claimed as new.

### B. Research Questions and Contributions

- RQ1 (C1): Can firmware on the motor controller bound the time at which drive is removed after the last command, whatever the state of the Pi and the operator link?
- RQ2: What latency does the control path add inside the robot, and over what distance does the link remain usable?
- RQ3 (C2): Does a watchdog restore service after a process is killed, without leaving the motors driven?
- RQ4 (C3): What does the two-way victim audio and video path cost the board, and how precise is the GPS position that the operator's map relies on, when both run on the same single-board computer?

The contributions are:

1. A firmware dead-man timer on the motor controller that removes drive without help from the Pi (C1, Section III-E). Drive was removed within 2042 ms of the last command in 30 of 30 logged trials (mean 2022.5 ms), against an analytical bound of about 2060 ms (Section V-A).
2. A three-process split on the Pi with a watchdog process and a single serial writer (C2, Sections III-F and III-G). The watchdog restored service with a new process identifier (PID) in 30 of 30 SIGKILL trials, a 95% Wilson lower bound of 88.6% on the recovery probability [@wilson1927] (Section V-C).
3. A two-way WebRTC audio and video path to the victim, isolated in its own process (C3, Section III-I). One operator session used about 63% of one core on the media process while the control process stayed near 4% (Section V-D).
4. An itemized bill of materials of about USD 310 from procurement receipts (C4, Section V-H and Appendix A).

Every figure in Section V carries an evidence class (measured, calculated, simulated, software test or pending), and each result was cross-checked against the robot's own machine logs before use; hand-entered data sets that failed that check were withdrawn rather than reported, so every result in Section V is machine-logged.

The claims are limited. All results come from one robot, one operator and one access point, indoors or in an open outdoor area. The stop time in contribution 1 is the time at which drive is removed, not the time the wheels stop and not a stopping distance. Control latency over Wi-Fi, media delay and quality, the end-to-end rescue run and the test of whether a media-process stall can delay control were not measured; each has a pass criterion fixed in advance (Table XVII). Operator usability was not evaluated. The firmware stop behaves like a category-0 stop in IEC 60204-1 [@iec60204] but is not a safety-rated implementation, and no compliance is claimed.

Section II reviews related work. Section III describes the system from the firmware upward, Section IV the experimental setup, and Section V the results. Section VI discusses them with their limitations and threats to validity, Section VII sets out future work, and Section VIII concludes.
