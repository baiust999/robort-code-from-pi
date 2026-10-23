# 7. Future Work

The eighteen directions below extend the system evaluated in Sections 3-5. Each starts from a limitation stated in Section 3 or measured in Section 5, names a baseline, and fixes its metrics in advance. None is an existing capability of the robot, and none is claimed as novel: whether a direction closes a gap in the literature can only be settled by a dedicated literature review, which Section 2.6 has not performed for these topics. Every direction that adds automated behaviour is bound by one rule: the firmware dead-man stop of Section 3.5.2 stays independent of the new function, keeps its bounded stop time, and is re-tested after each change (Section 7.2.2).

The directions are grouped under six themes (Sections 7.1 to 7.6) and are not equally close to the evidence of this paper. Table 7.1 gives each a priority level.

- **Priority 1** directions extend a limitation that Section 5 demonstrated or left unmeasured, need no new sensing hardware, and have a defined baseline: Sections 7.2.1, 7.2.2, 7.6.1 and 7.6.3.
- **Priority 2** directions address a demonstrated limitation but need new hardware or algorithms before they can be evaluated: Sections 7.1.1, 7.3.1, 7.3.2, 7.3.3, 7.3.4, 7.4.4 and 7.5.1.
- **Priority 3** directions are either platform engineering whose value depends on field requirements, or depend on Priority 1 and 2 results: Sections 7.1.2, 7.2.3, 7.4.1, 7.4.2, 7.4.3, 7.5.2 and 7.6.2.

**Table 7.1.** Future-work directions, the limitation each addresses, and dependencies.

| Section | Direction | Limitation in the current system | Evidence | Priority | Depends on |
|---|---|---|---|---|---|
| 7.1.1 | Multi-hop mesh networking | One 802.11n cell; range sweep partial (16 line-of-sight stations, 5 to 250 m, no failure point reached, no obstacle condition) | 3.2, 5.3 | 2 | 7.6.3 |
| 7.1.2 | Communication-aware mission planning | No route planning; link quality not mapped | 3.10, 5.3 | 3 | 7.1.1, 7.3.1 |
| 7.2.1 | Cross-layer fault detection and recovery | Supervisor sees process liveness and an HTTP health check only; Arduino removal needs a P1 restart | 3.7, 5.4 | 1 | 7.2.2 |
| 7.2.2 | Quantitative safety and fault-injection evaluation | SIGKILL only (10 trials per process); hangs, sensor loss and network faults not injected; ablations not run | 4.3, 5.4 | 1 | - |
| 7.2.3 | Simulation-based validation | Heartbeat-loss model assumes independent loss; the hardware mock differed from the firmware until patched | 5.1a, 5.1b | 3 | 7.2.2 |
| 7.3.1 | Indoor localization and mapping | GPS is the only position source; encoder-equipped motors are fitted but their outputs are not read; no IMU or mapping | 3.3, 3.10, 5.6.1 | 2 | new sensors |
| 7.3.2 | Trajectory tracking and visualization | Dashboard draws a GPS polyline only | 3.10 | 2 | 7.3.1 |
| 7.3.3 | Autonomous return navigation | Teleoperation only; no return behaviour | 2.1 | 2 | 7.3.1, 7.3.4 |
| 7.3.4 | Localization-aware and obstacle-aware navigation | Range sensor is advisory and never stops the motors | 3.5.3 | 2 | 7.3.1 |
| 7.4.1 | Compact, low-profile chassis design | 4WD skid-steer platform, indoor floors only | 3.3 | 3 | 7.4.3 |
| 7.4.2 | Heat-resistant structural protection | Only SoC temperature measured (at most 52.6 deg C), under indoor loads | 5.5 | 3 | 7.4.4 |
| 7.4.3 | Improved disaster-terrain mobility | No rubble, slope or standard-apparatus trials | 2.2, 3.3 | 3 | 7.6.3 |
| 7.4.4 | Energy-aware operation | No in-situ voltage or current sensing; original Pi supply under-volted under driving plus media | 3.3, 5.5 | 2 | new sensors |
| 7.5.1 | Sensor fusion for hazard assessment | Gas reading is uncalibrated ADC counts; DHT11 checked at one set-point | 5.6.3, 5.6.4 | 2 | reference instruments |
| 7.5.2 | Edge-based victim assistance | No detection implemented; media path already uses about 63% of one core | 5.5 | 3 | 7.5.1 |
| 7.6.1 | Secure remote control | Plain HTTP and WebSocket; one shared controller key; sequence check optional | 3.2, 3.8 | 1 | 7.2.2 |
| 7.6.2 | Multi-robot cooperative exploration | Single robot; one controller slot | 3.8 | 3 | 7.1.1, 7.3.1, 7.6.1 |
| 7.6.3 | Reproducible experimental benchmarking | Small N per experiment; rotating logs; no standard test apparatus | 4.2 (Table 4.1), 5.0 | 1 | - |

## 7.1 Communication Resilience

Both directions concern the single-cell assumption of Section 3.2: Section 7.1.1 changes the network, and Section 7.1.2 uses its measured quality to plan routes.

### 7.1.1 Multi-Hop Mesh Networking

The evaluated system uses a single access point, an 802.11n cell with the router at the operator (Section 3.2), and the range sweep reached 250 m line of sight without a failure point, with ping loss of 0 to 16% per burst that did not track distance, and no obstructed-link or upper usable-range figure (Section 5.3). No mesh performance is claimed or implied. Wireless links are reported to be unreliable inside buildings, metal structures and high-radiation areas, while cable links bring spooling and snagging problems, and wireless relays between operator and robot have been proposed [@schneider2016]. At Fukushima, tests showed that high-power 2.4 GHz wireless devices would not work inside reactor buildings, and the robots used a cable and wireless hybrid network with twisted-pair cable links [@nagatani2013]. A LoRa-based architecture has been tested in simulation and an indoor laboratory with a ground robot; it carries destination, position and enable-bit packets, with a reported packet delay of 1.86 s at its chosen parameters at 600 m [@manuel2022]; none of these sources shows two-way audio and video at the quality of Section 3.9 over such a link, and that is not established here and belongs to the literature review noted above.

The proposed work places relay nodes running IEEE 802.11s with HWMP routing along the robot's path and compares them with the single access point, first completing the unfinished baseline sweep of Section 5.3. Conditions are line of sight, obstructed links, relay failure and route change. Metrics are packet delivery ratio, end-to-end latency, route recovery time and control availability. A mesh adds a new failure mode (route flapping), so the dead-man trip time must be re-measured with the mesh active (Section 7.2.2).

### 7.1.2 Communication-Aware Mission Planning

There is no route planning and link quality is not mapped. The proposed work uses measured link quality as a cost in route selection so that a planned route trades length against time spent outside coverage. It requires a map (Section 7.3.1) and a link-quality survey (Section 7.1.1). The baseline is the shortest-distance route. Metrics are route length, connectivity interruptions, control availability and mission completion.

## 7.2 Fault Detection and Quantitative Fail-Safe Validation

These directions turn the fail-safe claims of Challenges C1 and C2 into measured evidence. Section 7.2.2 defines the fault-injection campaign and regression suite that the other directions in this section must pass.

### 7.2.1 Cross-Layer Fault Detection and Recovery

The supervisor of Section 3.7 detects a crashed or unresponsive process, but it does not classify faults across layers, and a removed Arduino requires a P1 restart (Section 5.4). Today the dashboard learns of a firmware trip through the `fw_state` field of telemetry, up to 700 ms after the motors stop (Section 3.5.2); P1 logs the PANIC line but does not forward it as an event.

The proposed work adds a supervisor that watches serial health, process health, telemetry freshness and command delivery, and moves the system through defined recovery states, and forwards the PANIC line to the dashboard. The dead-man stays in the firmware and outside the supervisor's control, and the supervisor may only make the system more conservative. Metrics are detection latency, false-alarm rate, recovery success with a Wilson interval [@wilson1927] and unintended-motion duration, measured against the current supervisor using the fault-injection campaign of Section 7.2.2. A sound detector must be shown not to delay the stop or to cause a spurious one; both are test outcomes, not assumptions.

### 7.2.2 Quantitative Safety and Fault-Injection Evaluation

Section 5.4 injected SIGKILL crashes, 10 trials per process, and single injections of the other faults. Thirty of thirty recoveries give a Wilson lower bound of 88.6% [@wilson1927]; that bound is a statement about bench SIGKILL faults and not a reliability figure. The ablations planned in Section 4.3 (dead-man removed, P3 disabled, control and media merged) have not been run.

The proposed work replaces the single-fault campaign with a fault-injection campaign across the process, serial, network and sensor layers, and runs the ablations, so that each fail-safe claim has a measured effect size against a defined baseline. Process faults extend the SIGKILL crashes to hangs (process alive but unresponsive, injected with SIGSTOP). Serial faults extend the single Arduino unplug to repeated reconnects and to corrupted or truncated frames through a serial fault proxy. Network faults extend the single drop to delay, loss and bandwidth caps (`tc netem`, access-point power-off). Sensor faults cover camera, microphone and GPS loss by device unbind. The ablations remove the dead-man, disable P3, or merge control and media into one process, using build and configuration flags. Metrics for every fault are detection latency, motor-stop response, unintended-motion duration, recovery success with Wilson interval and false-alarm rate. The motor-stop response must be taken at the wheels (E4, 240 fps video), not only from firmware logs, because the log measurements of Section 5.1 establish when the firmware removed drive and not when the wheels stopped. This direction also defines the regression suite that every other direction in this section must pass before any change reaches the robot.

### 7.2.3 Simulation-Based Validation

The heartbeat-loss model of Section 5.1b assumes independent loss, and the hardware mock differed from the firmware until it was patched (Section 5.1a). The proposed work builds a simulation of the robot, its link and its faults for testing policies before hardware runs. Every simulated result must be checked against the robot itself, and simulated results are labeled as such. Metrics are agreement between simulated and measured stop-time and recovery distributions, and the fraction of hardware faults reproduced.

## 7.3 GPS-Denied Localization and Return Navigation

GPS is the only position source, and the four directions form a dependency chain: localization (7.3.1) feeds tracking (7.3.2) and the safety envelope (7.3.4), and return navigation (7.3.3) needs both. All stay under operator supervision.

### 7.3.1 Indoor Localization and Mapping

GPS is the robot's only position source. On an outdoor static test the receiver gave a CEP50 of 8.9 m and a CEP95 of 30.5 m (Section 5.6.1), and behaviour indoors is not measured in Section 5. The motors fitted are encoder-equipped (Table 2), but the firmware does not read the encoder outputs, so no odometry exists.

The proposed work adds wheel odometry from the existing encoders, an IMU and a 2D range sensor, and evaluates SLAM that builds an occupancy-grid map. Skid-steer slip makes odometry unreliable on loose surfaces, so the odometry error must be measured, not assumed. The sensor set and algorithm are chosen against the Pi's CPU budget (Section 5.5), which the media path already loads heavily. The reference is a set of surveyed positions; metrics are absolute position and heading error, map consistency, and CPU and memory cost. Claims about SLAM performance are withheld until these are measured in a real corridor, and the localization stack must not write to the motor path.

### 7.3.2 Trajectory Tracking and Visualization

The dashboard draws a GPS polyline built with a 10 m track filter (Section 3.10). Once Section 7.3.1 provides pose estimates, the dashboard can draw the estimated pose and track on the map and log timestamped poses for post-mission review. This is largely engineering, and its value is the evaluation it enables. Metrics are trajectory error against a ground-truth route, route reconstruction accuracy and display latency.

### 7.3.3 Autonomous Return Navigation

The robot is teleoperated only, and no return behaviour exists. The proposed work adds return-to-start, first by retracing recorded waypoints and later by planning on the map. The behaviour stays under operator supervision, which keeps it within the supervisory tier of the levels of autonomy discussed in Section 2.1 [@beer2014; @schneider2016]. The baseline is an operator-driven return. Metrics are return success rate with a Wilson interval, route length, return time and obstacle-related failures. Return navigation is contingent on Sections 7.3.1 and 7.3.4; no return capability should be described until both are demonstrated.

### 7.3.4 Localization-Aware and Obstacle-Aware Navigation

The ultrasonic range sensor is advisory and the firmware never stops the motors on a sensor reading (Section 3.5.3, Table 7). The proposed work defines a safety envelope for Section 7.3.3: the robot slows, asks the operator to take over, or stops when obstacle range or localization confidence crosses a threshold. The envelope runs on the Pi and can only command a stop or reduced speed. It does not alter the firmware dead-man. The baseline is teleoperation without the envelope. Metrics are collision count, false stops, operator interventions and safe completion rate. Thresholds are calibrated against the sensor error measured in E10, which carries a verification flag in Section 5.6.2 and must be resolved first.

## 7.4 Platform: Mobility, Thermal Protection and Energy

These directions concern the physical platform. Most are established engineering whose value depends on the field requirements of Challenge C4 and the standard test methods of [@jacoff2012], so they are not presented as research contributions on their own.

### 7.4.1 Compact, Low-Profile Chassis Design

The 4WD skid-steer chassis of Section 3.3 has been tested only on indoor floors. Reducing height and width serves confined-space access, but the benefit depends on the dimensions of the spaces targeted, which are not defined in this paper and must be stated from a reference such as the standard apparatus of [@jacoff2012]. The baseline is the current chassis (Table 2). Metrics are minimum navigable clearance, turning radius and deformation under a defined load. This is routine design work and is not presented as a research contribution.

### 7.4.2 Heat-Resistant Structural Protection

The only thermal measurement is the Pi SoC temperature, at most 52.6 deg C under indoor loads (Section 5.5). No exposure to external heat has been tested. The proposed work designs an enclosure from the rated limits of each component, then tests it first on each component and then on the assembled robot. Metrics are internal and component temperature rise, throttling events and uptime under a defined exposure. No thermal resistance is to be stated before both levels of testing are complete, and heat-resistant materials must be chosen against the weight and cost limits of Challenge C4.

### 7.4.3 Improved Disaster-Terrain Mobility

No rubble, slope or standard-apparatus trials were run (Sections 2.2 and 3.3). The proposed work compares wheeled and tracked drives on rubble-like surfaces, loose material and slopes, following the standard test methods [@jacoff2012] so that results can be compared across platforms. The baseline is the current 65 mm wheels. Metrics are traversal success rate, maximum slope, obstacle clearance, slip ratio and energy per metre. Slip estimation needs the odometry of Section 7.3.1.

### 7.4.4 Energy-Aware Operation

The battery is a 4S3P 4.5 Ah Li-ion pack (Section 3.3), but the robot has no voltage or current sensing, and the original Pi supply under-volted under driving plus media load (Section 5.5), which makes the supply a measured constraint. The proposed work adds voltage and current sensing, profiles energy per subsystem, and then tests a return trigger at a validated remaining-energy threshold. The trigger would only raise an operator alert or start Section 7.3.3; it never acts on the motors directly. The baseline is the current supply. Metrics are energy per subsystem, endurance and return-trigger margin.

## 7.5 Hazard Sensing and Edge-Based Victim Assistance

Both directions are limited by the uncalibrated sensing and the CPU budget measured in Sections 5.5 and 5.6. Output of either is advisory to the operator.

### 7.5.1 Sensor Fusion for Hazard Assessment

The gas channel reports raw ADC counts, and the MQ-136 also responds to gases other than its target (Section 5.6.4). The DHT11 was checked at one set-point against an uncharacterised reference (Section 5.6.3). The proposed work calibrates the gas, temperature and humidity channels against reference instruments across their operating range and then combines them to flag abnormal conditions with a stated uncertainty. Fusion is a routine step after calibration and is not claimed as novel. Metrics are measurement error, sensitivity, false-alarm rate and response time. Hazard output remains advisory to the operator.

### 7.5.2 Edge-Based Victim Assistance

No victim detector is implemented. The media process already uses about 63% of one core (Section 5.5), so there is little CPU headroom for inference on the present Pi. Published work on rubble-scene human detection with YOLOv8-s on a Jetson Nano, with alerts sent to a mobile application [@raghavan2026], is a starting point for the literature review. Its camera, dataset and board differ from this robot, so its figures are not a baseline for the Pi. The proposed work tests lightweight detection models on the Pi and on an attached accelerator against a labelled test set, using a public detector as the baseline. Metrics are precision, recall, inference latency, memory, energy and the effect on media frame rate. Detector output is shown to the operator as decision support and is never presented as confirmation of a victim's presence or condition. No detection capability can be claimed until it has been validated on data representative of the target scenes.

## 7.6 Security, Multi-Robot Scale and Reproducibility

Section 7.6.3 underpins every other direction, since no improvement can be claimed without a repeatable baseline. Sections 7.6.1 and 7.6.2 remove the trusted-network and single-robot assumptions.

### 7.6.1 Secure Remote Control

The threat model of Section 3.8 assumes a trusted local network: the controller key crosses plain HTTP, one shared key is used, and the latest client with a valid key takes control. A scoping review of humanoid-robot safety reports that cybersecurity is addressed less often than physical safety [@koczi2025]; this is the only literature support claimed, and it does not cover rescue robots. The proposed work adds TLS on both ports, per-operator credentials with role-based authorization, mandatory sequence numbers against replay, and signed updates. Metrics are unauthorized-command rejection, the latency cost of encryption, and whether the motors stay stopped during authentication failures. TLS runs in P1 and P2 only; the firmware dead-man must stay independent of it and must still trip if authentication stalls the command stream.

### 7.6.2 Multi-Robot Cooperative Exploration

The system has one robot and one controller slot (Section 3.8). Multi-robot search and rescue is surveyed in [@queralta2020], which lists heterogeneous coordination and interoperability among its open questions. The proposed work would extend the system to several robots that share maps and hazard observations. It depends on Sections 7.1.1, 7.3.1 and 7.6.1 and is the most speculative direction here, because the multi-operator arbitration of Section 3.8 allows one controller only. A first experiment should be two robots with a shared map, compared with one robot, with coverage time and communication load as metrics.

### 7.6.3 Reproducible Experimental Benchmarking

Section 5 has small N per experiment, rotating logs and no standard test apparatus, and its data audit found several tables unsupported by the logs. The proposed work publishes the hardware configuration, test procedures, network conditions and raw logs of every experiment, repeats each trial at a stated N, pre-registers pass and fail criteria, and runs the standard test methods [@jacoff2012] where applicable. Results are reported against the baselines named in the other directions of this section, with confidence intervals. This direction underpins all the others, since no other direction can claim an improvement without a repeatable baseline.
