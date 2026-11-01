## III. SYSTEM DESIGN

One rule shapes the design: the robot must stop whenever any part of the system above the motors fails, and nothing added for the operator or the victim may weaken that guarantee. Sections III-A to III-D describe the architecture, network, hardware and software. Sections III-E to III-G follow the stop guarantee upward: the firmware enforces it, the control server feeds it, and supervision restores service without bypassing it. Section III-H decides which operator holds control, Section III-I builds victim interaction on that decision, Section III-J adds localization, and Section III-K lists operator aids that were added after the evaluation and are not evaluated.

### A. Architecture

The system has four tiers: an Arduino UNO for real-time control, a Raspberry Pi 4, a local Wi-Fi network, and a browser dashboard on the operator's laptop (Fig. 1). The Pi runs three separate Python processes. P1 (control server) links the dashboard to the Arduino, checks every drive command and collects telemetry and GPS. P2 (media server) streams the robot's camera and microphone to the operator and carries the operator's voice, video and text to a display and speaker that face the victim (the Robot Screen). P3 (watchdog) starts P1 and P2 and restarts either one if it crashes or stops responding. Control and media use separate transports that end in separate processes, so a media failure leaves driving and stopping intact.

![Fig. 1](figures/fig01_system_architecture.png)

**Fig. 1.** System architecture. Solid lines carry data, labelled with the transport; dashed lines are supervision by P3. Control (WebSocket) and media (WebRTC) end in different processes on the Pi.

Fig. 2 follows one drive command through the tiers. A held key sends one motion command; while it is held, heartbeats keep the dead-man timer armed, and releasing the key sends a stop. P2 and P3 take no part in this loop: media never carries a drive or stop command, and the watchdog acts on the processes from outside, so a failure in either cannot delay a stop.

![Fig. 2](figures/fig02_control_loop_sequence.png)

**Fig. 2.** Control loop for one drive command: the command goes down through P1 to the firmware, and telemetry returns at 500 ms (firmware) and 200 ms (P1 broadcast) periods.

### B. Network

The Pi and the operator laptop join one 802.11n cell on the 2.4 GHz band with a 20 MHz width and no Internet uplink. Both hold addresses in the same subnet, issued by the router over DHCP, so traffic between them is neither routed nor address-translated. The project configures no access point, reservation or static address of its own, and the router stays with the operator at the staging point, so the robot works within one radio cell. The access point was on channel 10 (2457 MHz) for most of the campaign and on channel 3 (2422 MHz) for two range stations (Section V-E).

P1 serves the dashboard files, control WebSocket, telemetry, GPS track and offline map tiles on TCP port 8080. P2 serves WebRTC offer and answer exchange and the Robot Screen page on TCP port 8443, and carries audio, video and a data channel over UDP ports negotiated by Interactive Connectivity Establishment (ICE). Control and media use different transports for different reasons. Commands run over TCP because ordered delivery, together with a per-client sequence check, keeps a stale command from overtaking a newer one, and a command that does not arrive within the dead-man window stops the robot rather than leaving it on a stale command. Media runs over UDP, where a lost packet costs picture or voice quality but never delays a command. Table II lists the load and timing the network carries.

**TABLE II.** Network load and timing requirements (design values).

| Quantity | Value |
|---|---|
| Video, robot to operator | 640x480 at 10 fps, 500 kbit/s target |
| Audio, each direction | Opus, 32 kbit/s, 60 ms packets |
| Telemetry | Firmware frame every 500 ms; P1 snapshot to each client every 200 ms |
| Commands | Heartbeat every 500 ms from the controlling dashboard; one drive command per key press and one stop per release |
| Steady-state load per operator | Under 1 Mbit/s (sum of the rows above) |
| Hard delivery deadline | 2000 ms since the last valid command (dead-man) |
| Operator-side link timeout | 3000 ms without telemetry gives mission state STOP |
| WebSocket keep-alive | Ping every 20 s, 20 s timeout |
| Dashboard reconnect back-off | 1 s, doubling, capped at 30 s |

The dead-man window is measured from the last valid command, not counted in missed heartbeats. At the configured 500 ms heartbeat, two consecutive lost heartbeats leave a 1500 ms gap and do not stop the robot; a third reaches the window. The firmware's own telemetry frame (500 ms) and status line (1000 ms) are outbound reports and do not re-arm the timer. The WebSocket keep-alive reclaims a dead socket only after up to 40 s, so liveness for safety is enforced by the dead-man at 2000 ms and the dashboard's 3000 ms telemetry timeout, not by the transport. Neither port carries TLS, so the operator's browser must be told to treat the Pi's origin as trusted before it will capture the microphone and camera; this is a deployment workaround, not transport security (Section VI-C).

### C. Hardware

The hardware is chosen so that the lowest tier can stop the robot by itself: the Arduino drives the motor drivers directly and can disable them with one output. Table III lists the components and Fig. 3 the connections and power distribution. The motor supply and the Pi supply are separate, so motor current surges cannot reset the Pi. Each BTS7960 driver drives forward on one pulse-width modulation (PWM) input and reverse on the other, and both drivers share one enable line on pin D4, so one output disables all propulsion. The Pi control server clamps every speed to 0-180 of the firmware's 0-255 PWM range, which keeps the average voltage across the 12 V motors below their rating on the 14.8 V pack (180/255 x 14.8 V = 10.4 V, CALCULATED).

**TABLE III.** Hardware components.

| Component | Part | Function |
|---|---|---|
| Edge computer | Raspberry Pi 4 Model B, 4 GB | Runs P1, P2, P3 and the Robot Screen |
| Microcontroller | Arduino UNO (ATmega328P, 16 MHz) | Real-time motor control and sensing |
| Motor drivers | 2 x BTS7960 | One per side, shared enable line |
| Drive motors | 4 x 25GA-370 geared DC motor, 12 V, 60 RPM no-load, 65 mm wheels | Skid steering, left and right pairs |
| Camera servos | 2 x SG90 micro servo | Pan and tilt, 0-180 deg |
| Sensors | HC-SR04 range, DHT11 temperature and humidity, MQ-136 gas (raw 10-bit ADC, uncalibrated) | Advisory readings for the operator |
| GPS receiver | NEO-6M | Position, fix and satellite count |
| Camera and microphone | USB webcam with built-in microphone | 640x480 video at 10 fps; 48 kHz audio |
| Robot display and speaker | 7-inch HDMI display (1024x600); speaker on the 3.5 mm jack | Victim-facing Robot Screen |
| Battery | 4S3P Li-ion pack, twelve 18650 cells of 1500 mAh, 14.8 V nominal, 4.5 Ah, 4S 40 A battery management system (BMS) | Motor and microcontroller power |
| Regulators | 2 x buck converter, 8 V and 5 V | 8 V to the Arduino; 5 V to the servos |
| Pi supply | 50000 mAh USB power bank | Separate supply for the Pi (replaced during E8, Section V-D) |

![Fig. 3](figures/fig03_hardware_power.png)

**Fig. 3.** Hardware interconnection and power distribution. Thick lines carry power; thin lines carry signals, labelled with the interface and its direction. The motor supply (4S pack) and the Pi supply (USB power bank) are separate.

### D. Software Organization

The software has three layers that share no code and talk only through three interfaces: the serial command protocol between firmware and P1, the control WebSocket between the dashboard and P1, and WebRTC between the dashboard and P2. The firmware is C++ on the Arduino core without an RTOS. The Pi processes are Python 3 with asyncio (FastAPI and uvicorn for P1 and P2, aiortc and PyAV for P2, aiohttp for P3) over a shared module of protocol constants, configuration and access control. The dashboard is a single-page React application in TypeScript, served by P1, in which each network hook owns one connection to one server, so a lost media connection leaves the drive controls and telemetry working. systemd starts only P3, which spawns P1 and P2 as child processes with no shared memory. A development mode replaces the serial link with an in-process Arduino emulator, the GPS with a synthetic track and the camera with a test pattern, so the full stack can be tested without the robot; Section V-A reports where that emulator differed from the firmware.

### E. Firmware and the Dead-Man Stop

The firmware holds the authority to stop the robot, so it must stop the motors without help from the Pi or the network. It defines five modes (Fig. 4): BOOT, READY, ACTIVE, PANIC and a reserved latched operator-stop mode, ESTOP, which is defined but not entered in the current build. Motion is accepted only in READY and ACTIVE with no fault set.

![Fig. 4](figures/fig04_firmware_modes.png)

**Fig. 4.** Firmware operating modes. A dead-man expiry moves READY or ACTIVE to PANIC; valid commands clear the fault. ESTOP is reserved and not entered in the evaluated build.

A cooperative scheduler, rather than a pre-emptive real-time operating system (RTOS), runs the periodic tasks of Table IV from the main loop, following the time-triggered style of [@pont2001], with timing based on unsigned millisecond differences so that counter rollover does not break it. The command parser runs on every loop pass and checks each newline-terminated ASCII command in four stages (Fig. 5): framing (at most 31 characters), syntax (one of nine opcodes, digits-only argument), range (speed 0-255, angle 0-180) and state (motion only in READY or ACTIVE). Appendix B gives the full command and reply grammar.

**TABLE IV.** Firmware tasks.

| Task | Period | Work |
|---|---|---|
| Motor service | 10 ms | Ramp PWM toward the target by 15 units per tick |
| Safety supervisor | 10 ms | Dead-man check and fault recovery |
| Fast sensors | 50 ms | HC-SR04 range (25 ms echo timeout) |
| Slow sensors | 2000 ms | DHT11 and MQ-136 |
| Telemetry | 500 ms | One 8-field CSV frame |
| Status line | 1000 ms | Mode line and LED toggle |

![Fig. 5](figures/fig05_command_validation.png)

**Fig. 5.** Four-stage command validation in the firmware. Any command that passes stages 1 to 3 re-arms the dead-man timer before the state check; a failure at any stage returns a NACK with a reason.

Every command that passes stages 1 to 3 re-arms the dead-man timer, heartbeats included. This is not limited to drive commands: pan, tilt and status queries refresh the timer as well, so the 2000 ms window runs from the last valid command of any kind. When the elapsed time reaches 2000 ms (the check is inclusive), the supervisor sets all four PWM outputs to zero and pulls the shared enable line low at once, without ramping, and the firmware enters PANIC and emits a PANIC line on the serial link in the same pass (Fig. 6). This dead-man pattern behaves like a category-0 stop in the sense of IEC 60204-1 [@iec60204]; it is a design choice, not a claim of compliance.

Two quantities are kept apart throughout the paper: the stop time, when the motors lose drive, and the confirmation latency, when an observer outside the firmware can establish that they have. Only the first is a safety property. The worst-case stop time after the last accepted command is

$$t_{stop} \le T_{DM} + T_{S} + J, \qquad (1)$$

where $T_{DM} = 2000$ ms is the dead-man window, $T_{S} = 10$ ms is the supervisor period, and $J$ is the longest single loop pass. $J$ is set by the two blocking sensor reads, the 25 ms HC-SR04 echo timeout and the DHT11 exchange with its 20 ms start pulse. Because the 2000 ms slow-sensor period is an exact multiple of the 50 ms fast period, both reads fall in one loop pass every 2 s, so $J$ is about 50 ms and the bound is about 2060 ms. The bound is analytical.

Confirmation is slower. Besides the immediate PANIC line, the firmware encodes its mode in the state field of the periodic telemetry frame (every 500 ms), which P1 rebroadcasts on its own 200 ms timer. An observer that waits on that field learns of a trip up to 700 ms after the motors stop, about 350 ms on average. In the evaluated build P1 logs the PANIC line but does not forward it to the dashboard, so the operator display is driven by the slower path.

An ordinary stop command ramps the motors down instead:

$$t_{ramp} = \left\lceil u / \Delta u \right\rceil T_{M}, \qquad (2)$$

where $u$ is the current PWM value, $\Delta u = 15$ is the ramp step and $T_{M} = 10$ ms is the motor service period. From the 180 cap this gives 12 ticks, or 120 ms.

![Fig. 6](figures/fig06_deadman_trip_recovery.png)

**Fig. 6.** Dead-man trip and recovery. After 2000 ms without a valid command the firmware zeroes PWM, disables the drivers and reports PANIC; the next valid command re-arms the timer and the fault clears.

Table V lists every path that stops the motors.

**TABLE V.** Stop paths. The dead-man is the firmware's only automatic stop; the firmware never stops the motors on a sensor reading.

| Trigger | Origin | Action |
|---|---|---|
| Drive key released | Dashboard via P1 | S (ramped stop) |
| Emergency-stop button | Dashboard via P1 | S, sent without the sequence check |
| Controller connection closes | P1 | S |
| Another dashboard takes control | P1 | S |
| P1 start-up | P1 | 3 x S, 200 ms apart, before any other command |
| P1 shutdown | P1 | S before the port closes |
| Command flow stops | Firmware | PWM 0 and drivers disabled within $t_{stop}$ of (1) |

### F. Control Server and Telemetry

The firmware assumes that the commands it receives come from one source and arrive in order; P1 provides that assumption. Before it opens any hardware, P1 takes an exclusive, non-blocking lock on a file in a memory-backed directory, which the kernel releases when the process exits for any reason. It then opens the serial port in exclusive mode, and one asynchronous lock serializes all writes, so P1 is the single writer to the Arduino. At start-up P1 waits 2.0 s for the board to reset, sends three stop commands 200 ms apart and a status query, and requires a reply within 5 s; a timeout ends P1 with a handshake-failure exit code that P3 treats as a crash.

The firmware sends a telemetry frame every 500 ms. P1 drops any frame with a field outside its accepted range (Appendix B), without retransmission, and broadcasts a snapshot of the latest valid frame every 200 ms on an absolute schedule, merged with the GPS fix, link status and the robot's received Wi-Fi signal level. On reconnect, the dashboard sends the server timestamp of the last snapshot it received, and P1 replies with every newer snapshot in its buffer and the size of any gap:

$$D = N \cdot T_{b} = 300 \times 200\ \text{ms} = 60\ \text{s}, \qquad g = \max(0,\ t_{oldest} - t_{last}), \qquad (3)$$

where $N$ is the buffer size, $T_{b}$ the broadcast period, $t_{oldest}$ the oldest buffered timestamp and $t_{last}$ the client's last timestamp. The buffer is held in memory and does not survive a P1 restart.

### G. Fault Tolerance and Supervision

Fault tolerance is layered (Fig. 7). Each layer acts on its own, and a failure that passes every layer above ends at the firmware, which stops the motors.

![Fig. 7](figures/fig07_layered_fault_tolerance.png)

**Fig. 7.** Layered fault tolerance, from the dashboard down to the motors. Each layer acts independently; the firmware dead-man is the last.

P3 is the only systemd service (restart on failure after 5 s). It supervises P1 and P2 with the state machine of Fig. 8: it polls for process exit every 1 s, runs an HTTP health check every 10 s with a 5 s timeout, kills a process after three missed checks, and respawns it after a 10 s cooldown. The only link between P1 and P2 is a once-per-second localhost query from P2 for the controller's address. P1 reports why it exited through its exit code, so a clean exit or a lock already held by a healthy peer draws no alarm, a lock error or failed handshake is respawned, and an invalid configuration is logged separately so that it cannot drive a tight respawn loop.

![Fig. 8](figures/fig08_per_process_supervision.png)

**Fig. 8.** Per-process supervision in P3: exit polled every 1 s, health checked every 10 s, respawn after a 10 s cooldown.

The time from a failure to a working process is

$$T_{rec} = T_{det} + T_{p} + T_{c} + T_{init}, \qquad (4)$$

where $T_{det}$ is the detection time (at most 1 s for a crash through the exit poll, at most $3 \times 10 + 5 = 35$ s for a hang), $T_{p} = 1$ s is the poll before cooldown, $T_{c} = 10$ s is the cooldown, and $T_{init}$ is the start-up time, which for P1 is $2.0 + 3 \times 0.2$ s plus up to 5 s for the handshake. With $T_{det} = 1$ s, a P1 crash recovers in 14.6 s to 19.6 s plus interpreter start-up. Table VI shows how each failure degrades the mission, and Fig. 9 traces one failure, a Wi-Fi drop, through the tiers.

**TABLE VI.** Failure effects and recovery (design).

| Failure | Detected by | Effect | Recovery |
|---|---|---|---|
| Operator link lost | Dead-man; socket close | Robot stops; mission STOP | Reconnect with back-off; telemetry replay |
| P1 crash or hang | P3 | No control or telemetry; dead-man stops the robot | Respawn; buffered history lost |
| P2 crash | P3 | Video and talk lost; control unaffected | Respawn; operator retries video |
| Arduino link error | Serial read or write error | Mission STOP | Reads retried every 0.5 s; port reopened only when P1 restarts |
| Camera or microphone lost | P2 | Test pattern or silence sent | Microphone reopened every 2 s; camera on the next session |
| GPS port error | P1 | No fix; GPS alert bit set | Port reopened after 2 s |
| P3 crash | systemd | P1 and P2 stop with it; dead-man stops the robot | Restart after 5 s, then P1 and P2 respawn |

![Fig. 9](figures/fig09_wifi_drop_failure_chain.png)

**Fig. 9.** Failure chain for a Wi-Fi drop: the firmware stops the motors after 2000 ms without commands; P1 stops and frees the controller slot when the socket closes; on reconnection the dashboard replays buffered telemetry and its next heartbeat clears the fault.

The dashboard reduces link and firmware status to one of four mission states, in priority order: STOP (control socket or serial link down, or no telemetry for more than 3000 ms), DRIVING LIMITED (video down), DRIVING, and READY. It also shows the robot's received signal level as bars, with an amber warning at or below -70 dBm and a red one at or below -80 dBm. These thresholds are provisional planning values, not measured tolerances (Section V-E), and the warning is advisory; the stop guarantee stays with the dead-man.

### H. Controller Arbitration

Because any dashboard may reconnect after a failure, the system must decide which of several connected dashboards may drive. A dashboard becomes controller only by presenting the robot's controller key, compared in constant time; all others are observers, whose commands, including stop, are rejected. The most recent dashboard with the right key takes the controller slot, the previous holder is demoted, and the robot is stopped. A host that presents a wrong key five times within 300 s is refused for 300 s, even with the right key. P2 applies the same key check and grants talk only to a keyed session from the address P1 reports as controller, so talking follows driving. The key travels over plain HTTP and WebSocket. The threat model assumes a trusted local network at the staging point with no on-path attacker; transport confidentiality beyond WebRTC's own DTLS-SRTP is out of scope.

### I. Two-Way Victim Audio and Video

All communication between the operator and the victim runs through P2, and this path must never delay a stop. Media is kept out of P1 because video encoding is the heaviest load on the Pi and a stall in a codec library must not delay a stop; P2 can also be restarted while P1 keeps driving. P2 is a single Python process built on aiortc, a WebRTC implementation for asyncio, with PyAV (FFmpeg) for capture and coding. aiortc was chosen over server-oriented stacks because it runs inside one Python process on the P2 event loop and needs no separate signalling server.

The webcam and microphone can each be opened only once, so P2 opens each device on first use and fans frames out to every session (Fig. 10). Each dashboard session has its own outbound tracks and its own video encoder, VP8 or H.264 as negotiated. Each dashboard opens one peer connection that carries both directions: the robot's camera and microphone to the operator, and the operator's voice, video, text and images back. The dashboard sends its Session Description Protocol (SDP) offer in one HTTP POST with its controller key, and P2 returns a complete answer after gathering its candidates, so there is no signalling server and no trickle ICE. Both peers are on the same subnet, so host candidates suffice and no STUN or TURN server is used.

![Fig. 10](figures/fig10_two_way_media_path.png)

**Fig. 10.** Two-way media path in P2. Camera and microphone are opened once and shared across sessions; operator media is relayed by P2 to the Robot Screen over localhost under floor control.

The operator's media does not go from the dashboard to the Robot Screen directly. The kiosk browser that drives the victim-facing display connects only to P2 over localhost, and P2 relays the floor holder's media to it, so floor control and the controller check are enforced in one place and no remote host can reach the victim's screen or speaker. The cost is one decode and one re-encode on the Pi. Only one session may hold the Robot Screen at a time, and a takeover moves the talk path to the new driver within about one second. Short JSON messages on a reliable data channel carry screen text (at most 280 characters, acknowledged by the screen), media state and floor status; media and drive commands never travel on it.

P2 encodes 60 ms Opus packets in both directions instead of the usual 20 ms [@valin2012], which cuts the packet rate from 50 to 16.7 packets/s and the per-packet work on the event loop to a third. Table VII lists the media parameters.

**TABLE VII.** Media parameters (design values).

| Parameter | Robot to operator | Operator to robot |
|---|---|---|
| Video | USB webcam, 640x480 at 10 fps, 500 kbit/s target, one encoder per session | Laptop camera 640x480 at 10 fps, still image at 2 fps or shared screen at 5 fps; re-encoded once for the Robot Screen |
| Audio | 48 kHz mono, Opus voice mode, 32 kbit/s, 60 ms packets | Same; inbound queue of about 200 ms with a 120 ms start cushion |
| Source loss | Test pattern (video); silence and reopen every 2 s (audio) | Last frame repeated after 1 s, then black; silence |

### J. GPS and Offline Map

P1 reads NMEA sentences from the NEO-6M receiver, whose datasheet gives 2.5 m circular error probable (CEP) under 24 h static operation with strong signals [@ublox_neo6], merges the latest fix into each snapshot and adds a track point only when the fix lies at least 10 m from the previous point. The filter compares positions held to six decimal places; the 1 Hz telemetry log records them to four. Distance uses the equirectangular approximation

$$d = R \sqrt{(\Delta\varphi)^2 + (\Delta\lambda \cos\bar{\varphi})^2}, \qquad (5)$$

with $R = 6371000$ m, latitude and longitude differences $\Delta\varphi$ and $\Delta\lambda$ in radians and mean latitude $\bar{\varphi}$. The dashboard draws the fix and track over an offline vector map served by P1, so the map needs no Internet.

### K. Operator Aids Added After the Evaluation

Five operator aids were added after the measurements of Section V and have not been evaluated: person detection on the received video, run in the operator's browser rather than on the Pi; a repeating voice message recorded by the operator and looped by P2 on the robot speaker; victim marks that P1 stores with its GPS fix and camera angles while the snapshot image stays on the operator's computer; session recording on the operator's computer; and tap-to-answer questions on the Robot Screen for a victim who cannot speak. None acts on the motors and none confirms that a person is present. No detection rate, false-alarm rate, message intelligibility, recording completeness or answer reliability is claimed for them, and the E8 processor figures of Section V-D were recorded without them.
