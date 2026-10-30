# **Software Architecture — Autonomous Rescue Robot System**

**Document status:** Architecture of the system *as implemented*.
**Scope:** The complete software stack in `robot/` — Arduino UNO firmware, the Raspberry Pi 4 three-process edge stack, the local Wi-Fi network, and the React operator dashboard.
**Relationship to the methodology:** The methodology chapters (Sections 8.1–8.15 and the consolidated Sections 1–40) specify the system *as designed*. This document describes the system *as built*, and is numbered independently (A.1–A.11) so that it stands alongside those chapters without renumbering them. Where the implementation resolved a contradiction between the two source documents, or departed from the original design intent, this document states the behaviour of the code and records the divergence explicitly. Every architectural claim is traceable either to a methodology section or to a specific source file.

---

## **A.1  Architectural Overview**

The rescue robot is a teleoperated ground vehicle intended for search-and-rescue reconnaissance in environments an operator cannot safely enter. Its software is distributed across four physical tiers connected by three distinct transports: an Arduino UNO executing the real-time control loop, a Raspberry Pi 4 running three cooperating Python processes, an ordinary local Wi-Fi network that the Pi and the operator laptop share, and a React single-page application on the operator's laptop. The vehicle carries no autonomy in the navigational sense; every motion originates as an operator intent, and the entire architecture exists to carry that intent to the motors quickly and to carry sensory evidence back, while guaranteeing that the vehicle stops safely when any part of that path fails.

The organising principle of the architecture — the single idea from which most of its structure follows — is that **each tier is an independent failure domain, and safety authority descends to the lowest tier that can still act when the tiers above it are gone.** The dashboard can crash, the operator's laptop can lose radio contact, the Wi-Fi network can drop out, and the Raspberry Pi can lock up or be killed by the kernel, and in every one of those cases the Arduino still stops the motors within two seconds because its dead-man timer is evaluated unconditionally in its own main loop and depends on nothing outside the board. This is not defence-in-depth applied decoratively; it is the reason the system is decomposed the way it is. A monolithic design in which the Pi drove the motor pins directly would place the vehicle's safety behaviour behind a general-purpose preemptive kernel, a Python interpreter, and a scheduler — none of which can offer a bounded guarantee that a stop instruction executes.

The second organising principle is that **the wire protocol is the architecture's only true coupling.** The four tiers share no code and no runtime. What they share is a set of constants and message schemas defined canonically in `pi/common/protocol.py` and hand-mirrored into `arduino/protocol.h` and `dashboard/src/lib/protocol.ts`. Each of the three files names the other two in its header docstring. Because the coupling is narrow and explicit, each tier is independently testable, independently deployable, and — as Section A.10 describes — independently replaceable by a simulator.

```
  System Tier Decomposition and Failure Domains:
  ---------------------------------------------------------------

  TIER 4  OPERATOR LAPTOP                    (opens http://<pi-ip>:8080)
          React 19 + TypeScript dashboard, browser-hosted
          Failure => Pi keeps logging; Arduino stops in <=2s
                 |
                 |  WebSocket :8080  (control + telemetry)
                 |  WebRTC    :8443  (video + audio)
                 v
  TIER 3  LOCAL WI-FI NETWORK
          Pi and operator laptop on the same Wi-Fi network
          Failure => mission state degrades; Arduino stops in <=2s
                 |
                 v
  TIER 2  RASPBERRY PI 4 EDGE STACK          (<pi-ip>)
          P1 control (8080) | P2 media (8443) | P3 watchdog
          Failure => P3 respawns the child; Arduino stops in <=2s
                 |
                 |  UART 115200 baud, /dev/ttyUSB0
                 v
  TIER 1  ARDUINO UNO                        (real-time controller)
          Cooperative scheduler, 3-state machine, dead-man timer
          Failure => motors unpowered; no software recovery path
                 |
                 v
          MOTORS - SERVOS - SENSORS  (physical plant)
```
***Figure A.1 — Tier Decomposition, Transports, and Failure-Domain Boundaries***

The implementation is approximately 5,500 lines across all tiers. The distribution is itself architecturally meaningful: the firmware and the shared protocol layer together account for more than a third of the codebase, which is the expected profile for a system whose correctness rests on a narrow, rigorously specified hardware interface rather than on business logic.

| **Layer** | **Path** | **Lines** | **Primary Responsibility** |
| --- | --- | --- | --- |
| Arduino firmware | `arduino/` | 1,089 | Real-time actuation, dead-man safety, sensor acquisition |
| P1 control server | `pi/p1_control/` | 1,400 | Serial ownership, telemetry fan-out, command validation |
| Shared protocol layer | `pi/common/` | 957 | Wire contract, configuration, logging, hardware emulation |
| Operator dashboard | `dashboard/src/` | 980 | Operator interface, transport clients, state derivation |
| Test suite | `pi/tests/` | 456 | 50 tests over protocol, safety, and buffer logic |
| P2 media server | `pi/p2_media/` | 378 | WebRTC negotiation, camera and microphone tracks |
| P3 watchdog | `pi/p3_watchdog/` | 271 | Process supervision, health checking, restart policy |

***Table A.1 — Implementation Scale by Architectural Layer***

The firmware is compile-verified with `arduino-cli` 1.5.1 against `arduino:avr:uno`, consuming 8,204 bytes of program storage (25% of 32,256) and 377 bytes of SRAM (18% of 2,048, leaving 1,671 bytes for locals). These figures matter architecturally: they are the evidence that the safety-critical tier fits comfortably within an 8-bit microcontroller's resources with substantial headroom, which is what permits the dead-man check to run unconditionally on every loop iteration without contention.

---

## **A.2  Architectural Drivers and Constraints**

An architecture is best understood through the forces that shaped it. Six drivers account for essentially every significant structural decision in this system, and each is traceable to a concrete mechanism in the code. Presenting them first makes the remainder of the document legible: nothing in the component decomposition is arbitrary, and each unusual choice — the cooperative scheduler, the triple-mirrored protocol, the watchdog-spawns-children topology — is a direct response to one of these forces.

**Driver 1 — A stop command must execute within a bounded time, on hardware that cannot be trusted to be responsive.** This is the dominant safety requirement and it produces the dead-man timer in `robot_state.cpp`, the Category 1 unconditional scheduler slot in `arduino.ino`, and the decision to place motor authority on the Arduino rather than the Pi. The timer is a `millis()` comparison rather than a timer interrupt because Timer1 is claimed by the Servo library; the arithmetic uses unsigned subtraction so it remains correct across the approximately 49-day `millis()` rollover.

**Driver 2 — The radio link is unreliable by nature and will partition mid-mission.** A 2.4 GHz Wi-Fi link inside a damaged structure will drop frames, and the robot may drive out of range of the Wi-Fi router. This produces the 300-entry ring buffer providing 60 seconds of telemetry history, the `resume_from` replay protocol, the exponential-backoff reconnection in `useControlSocket.ts`, and the four-state mission machine that degrades the interface rather than freezing it.

**Driver 3 — The compute tier is a general-purpose Linux system and will occasionally fail.** Python processes leak, deadlock on blocking device reads, and are killed by the OOM killer. This produces P3, the two-level liveness model (OS-level `poll()` for crashes plus HTTP `/health` for wedged-but-alive processes), and the exit-code contract by which P1 and P2 tell the supervisor *why* they died so that a misconfiguration does not become a restart loop.

**Driver 4 — Exactly one process may write to the Arduino.** Two writers interleaving bytes on a UART would produce commands neither of them sent. This is Invariant VI in the methodology, and it is enforced twice independently: an advisory `flock` on `/run/robot/p1.lock` via `ProcessLock`, and `O_EXCL` on the serial device through pyserial's `exclusive=True`.

**Driver 5 — The system must be developable and testable without hardware.** A capstone project cannot depend on continuous access to an assembled robot. This produces `mock_hardware.py`, which is architecturally significant precisely because it is not a stub: `MockArduino` reimplements the firmware's framing/opcode/argument-clamp validation, its dead-man semantics, and its 200 ms telemetry cadence faithfully enough that P1 cannot distinguish it from a real board across the serial boundary for driving and telemetry purposes; it does not model the firmware's fourth validation stage, the ESTOP/PANIC state-machine gate, since the mock has no fault states to gate against.

**Driver 6 — One operator, one vehicle, no ambiguity about who is driving.** Multiple dashboards may observe a mission, but a second controller sending contradictory motion commands would be actively dangerous. This produces the single-controller slot in `WebSocketHub.claim_role()`. Originally the first client to ask held it until disconnect, so any laptop that joined the network before the operator became the controller. The slot now requires the **controller key** (`CONTROLLER_KEY`, checked by `KeyGate` in `pi/common/access.py`): a dashboard that presents it in `hello` becomes controller, taking the slot over from any earlier holder, which is demoted, told with a `role` message, and the robot is stopped; every other dashboard is a view-only observer. Observers receive all telemetry, video and audio but P1 rejects every command they send, `stop_all` included (their heartbeats are dropped silently), and P2 ignores their media and data-channel messages. Blocking the emergency stop for observers is a deliberate choice: only the operator acts on the robot, and the Arduino's 2 s dead-man remains the backstop if the operator's dashboard is lost. The key may be short, so `KeyGate` locks a host out for 5 minutes after 5 wrong keys, during which even the right key is refused; connecting without a key is not counted, so a locked-out laptop can still watch.

| **Driver** | **Structural Consequence** | **Implementing Mechanism** |
| --- | --- | --- |
| Bounded stop latency | Motor authority resides on the MCU | `stateCheckDeadman()`, Category 1 loop slot |
| Unreliable radio | History buffering and replay | `RingBuffer`, `resume_from`, mission states |
| Fallible compute tier | External supervision with cause discrimination | `SupervisedProcess`, exit-code contract |
| Single-writer UART | Dual-mechanism exclusion | `ProcessLock` + `exclusive=True` |
| Hardware-free development | Protocol reimplementation, not stubbing | `MockArduino`, `MockGPS`, `MockSerial` |
| Single-operator safety | Explicit role arbitration | `WebSocketHub.claim_role()` |

***Table A.2 — Architectural Drivers and Their Structural Consequences***

Two constraints bound these drivers. The Arduino UNO offers 32 KB of flash, 2 KB of SRAM, and no operating system, which rules out threading, dynamic allocation, and any library that assumes a heap; the firmware is consequently written against a fixed set of module-local static variables. The Wi-Fi network runs on unlicensed 2.4 GHz spectrum shared with every other radio in the environment, which places a hard ceiling on video bitrate — hence the 640×480 at 10 fps, 500 kbps budget in `P2Config`.

---

## **A.3  Context View**

The system boundary encloses four software tiers and the physical vehicle. Outside it sit three external entities: the human operator, who supplies all navigational intent and interprets all sensory evidence; the disaster environment, which the vehicle senses but does not model; and the OpenStreetMap tile service, which supplies map imagery to the dashboard outside the operating area and is the only external network dependency in the entire architecture — and one that is not on any mission-critical path. Inside the operating area the map is drawn from a vector map file stored on the Pi and served by P1, so it needs no internet at all; outside that area the loss of map tiles degrades the map to a blank canvas with the live GPS polyline still drawn over it.

There is no cloud tier in the deployed configuration. The methodology defines five operational modes; the implementation targets **Mode 2, Local network only**, per Section 8.11.6, and `ENABLE_OVERLAY=0` in `deploy/etc-robot/p3.env` disables the internet overlay by default. This is a deliberate architectural position: a rescue deployment cannot assume internet connectivity, so the primary mode assumes none, and everything required to fly a mission is present on the local network. The ICE configuration endpoint reflects this — `GET /api/ice-config` returns an optional STUN server and `turn: null`, because on a single local subnet there is no NAT to traverse and therefore no TURN relay to fund.

```
  System Context:
  ---------------------------------------------------------------

     [ HUMAN OPERATOR ]                     [ OSM TILE SERVICE ]
       drive intent                          map imagery
       situational judgement                 (non-critical,
            |    ^                            degrades to blank)
            v    |                                  |
  +===================================================v==========+
  |                                                              |
  |   RESCUE ROBOT SYSTEM                                        |
  |                                                              |
  |   Dashboard  <--WS :8080-->  P1  <--UART-->  Arduino         |
  |      |                        ^                  |           |
  |      +------WebRTC :8443-->  P2                  |           |
  |                               ^                  |           |
  |                              P3 (supervises P1,P2)           |
  |                                                  |           |
  +==================================================|===========+
                                                     v
                                       [ DISASTER ENVIRONMENT ]
                                         temperature, gas,
                                         obstacles, terrain, GPS sky

  Mission-path transports:  WebSocket :8080  |  WebRTC :8443
  External dependencies:    OSM tiles outside the offline map area
                            only (non-critical)
```
***Figure A.3 — System Context, External Actors, and the Mission-Path Boundary***

Two transports cross the system boundary during a mission, and the separation between them is architecturally deliberate. Control and telemetry travel over a single persistent WebSocket to P1 on port 8080; video and audio travel over a WebRTC peer connection to P2 on port 8443. They are carried by different protocols, terminate in different processes, and fail independently. A camera failure or a collapse of the video path leaves the control channel fully operational — the mission continues in `DRIVING_LIMITED`, where the operator drives on sensor telemetry alone. This independence is the reason P2 exists as a separate process rather than as a module inside P1.

The WebRTC path is **two-way**. Besides the robot's camera and microphone reaching the operator, the operator's voice, video or a still image, and text messages travel back over the same peer connection to the victim-facing Robot Screen — the robot's own display and speaker. Section A.11 describes that path; it stays inside P2 and never touches the control channel.

---

## **A.4  Container View**

The system comprises six independently deployable units. The table below is the most compressed accurate statement of the architecture: for each container it records the runtime, the failure domain it occupies, and — critically — *who is responsible for restarting it*. That last column encodes the recovery topology, and reading down it reveals the supervision chain: the Arduino answers to no one and recovers only by power cycle; P1 and P2 answer to P3; P3 answers to systemd; the dashboard answers to the operator's browser.

| **Container** | **Runtime** | **Port / Device** | **Failure Domain** | **Restart Authority** |
| --- | --- | --- | --- | --- |
| Arduino firmware | AVR bare metal | UART 115200 | Vehicle actuation | None — power cycle only |
| P1 control server | Python 3 / FastAPI | TCP 8080, `/dev/ttyUSB0`, `/dev/serial0` | Control and telemetry | P3 watchdog |
| P2 media server | Python 3 / aiortc | TCP 8443, `/dev/video0` | Video and audio | P3 watchdog |
| P3 watchdog | Python 3 / asyncio | — | Process supervision | systemd (`Restart=on-failure`) |
| Operator dashboard | Browser / React 19 | — | Operator interface | Operator reload |
| Wi-Fi network | Ordinary Wi-Fi router | Local network | Network transport | Manual (power cycle the router) |

***Table A.4 — Container Inventory, Failure Domains, and Restart Authority***

The most consequential structural decision visible in this table is that **P1 and P2 are not systemd units.** Only `robot-watchdog.service` is registered with the init system, and it launches P3, which in turn spawns P1 and P2 as child processes. The alternative — three systemd units — was rejected because systemd's restart policy can observe only process exit, whereas the failure mode that most threatens this system is a process that remains alive while wedged on a blocking serial read. P3 detects that condition by polling `GET /health` and killing a child that misses three consecutive checks. The unit file's `KillMode=control-group` ensures the entire process group terminates together, and `After=network.target dev-ttyUSB0.device` prevents P1's handshake from racing udev's creation of the device node.

```
  Container View — Ports, Devices, and Supervision:
  ---------------------------------------------------------------

  OPERATOR LAPTOP
  +--------------------------------------------------------------+
  |  Dashboard (React 19 + TS + Vite + Tailwind + Leaflet)        |
  |  useControlSocket() ------> ws://<pi-ip>:8080/control/ws      |
  |  useWebrtcVideo()   ------> POST :8443/webrtc/offer           |
  +--------------------------------------------------------------+
              |                              |
              |   local Wi-Fi network (same network as the Pi)
              v                              v
  RASPBERRY PI 4  (<pi-ip>)
  +--------------------------------------------------------------+
  |  systemd: robot-watchdog.service                              |
  |     |                                                         |
  |     +--> P3 WATCHDOG  (asyncio, no ports)                     |
  |             | spawns + monitors (poll 1s, /health 10s)        |
  |             +--------------------+                            |
  |             v                    v                            |
  |     +---------------+    +----------------+                   |
  |     | P1 CONTROL    |    | P2 MEDIA       |                   |
  |     | FastAPI :8080 |    | aiortc :8443   |                   |
  |     | holds p1.lock |    | no lock; per-  |                   |
  |     | O_EXCL serial |    | session tracks |                   |
  |     +-------|-------+    +----------------+                   |
  +-------------|------------------------------------------------+
                | UART 115200, /dev/ttyUSB0
                v
  ARDUINO UNO — cooperative scheduler, dead-man 2000ms
```
***Figure A.4 — Container Topology with Supervision and Device Ownership***

A second decision worth surfacing is the asymmetry between P1 and P2 regarding hardware locking. P1 holds an exclusive lock because the Arduino tolerates exactly one writer. P2 holds no lock at all: multiple simultaneous viewers are explicitly permitted, each receiving its own `RTCPeerConnection` and encoder, all fed from one shared camera and one shared microphone (Section A.5.3). The architecture allows several observers to watch a mission while exactly one operator drives it.

---

## **A.5  Component View**

### **A.5.1  Arduino Firmware — Cooperative Scheduling Under Hard Safety Constraints**

The firmware is organised around a cooperative scheduler with no operating system, no threads, and no dynamic allocation. Work is partitioned into three categories distinguished by their timing guarantees, and the partition is the firmware's central architectural idea. **Category 1** runs unconditionally on every iteration of `loop()`: parse any pending command, check the dead-man timer, apply motor outputs, apply servo outputs, and verify state invariants. This path executes tens of thousands of times per second and, by construction, cannot be starved by any other work. **Category 2** comprises `millis()`-gated sensor polls and telemetry transmission, each with its own cadence. **Category 3** is two interrupt service routines, each kept under five microseconds.

```cpp
void loop() {
  unsigned long now = millis();
  // --- Category 1: unconditional safety path ---
  commandParserPoll();
  stateCheckDeadman(now);
  motorsApply();
  servosApply();
  checkInvariants();
  // --- Category 2: cadence-gated work ---
  sensorsPollSonar(now);
  sensorsPollGas(now);     sensorsPollDht(now);
  telemetryPoll(now);      pollStatusLed(now);
}
```

The separation exists so that a slow sensor cannot delay a stop. The only blocking call anywhere in the firmware is the bit-banged DHT11 read, at roughly 25 milliseconds, and it is precisely because that call blocks that its cadence is set to 2,000 milliseconds — it bounds the worst-case latency of dead-man detection, and that bound must remain far below the 2,000 ms dead-man window itself.

Motors and servos both use a **desired-state / apply split**. `motorsForward()` and its siblings do not touch pins; they update module-local variables, and `motorsApply()` in Category 1 drives the hardware each iteration. Servos extend this with dirty flags so that `servosApply()` writes only on change. The benefit is that command handling and hardware actuation are decoupled, so a command arriving at any point in the loop takes effect at a single well-defined place.

The **state machine** has three states — `ARMED` (1), `DRIVING` (2), `STOPPED` (3). `ARMED → DRIVING` occurs when a motion opcode executes; `DRIVING → ARMED` on an explicit stop or dead-man expiry. `STOPPED` is reached only through `statePanic()` and is **latched until board reset**, because a state-invariant violation means the firmware's own assumptions have been falsified and no recovery path can be trusted. `checkInvariants()` enforces this each iteration, panicking if the state falls outside its legal range or a servo angle exceeds 180 degrees.

The **dead-man timer** is the system's most important safety mechanism. `stateInit()` deliberately sets `lastCommandTime = millis() - (DEADMAN_MS + 1)` and `deadmanTripped = true`, so a freshly reset board boots with the window already expired and never inherits a spurious armed state. Only the arming opcode set `{F, R, L, G, S, H}` refreshes the window; pan, tilt, and status queries do not, on the explicit reasoning that a camera movement is not evidence the drive link is alive.

**Four-stage command validation** filters every inbound line. Stage 1 enforces a length of 1–8 characters, emitting `ERR_LEN` and consuming through the delimiter so that the tail of an overflowed line cannot be reinterpreted as a command. Stage 2 checks the opcode whitelist, emitting `ERR_TOK`. Stage 3 parses and clamps the numeric argument to 0–180, emitting `WARN_CLAMP`; a non-numeric tail becomes zero rather than a rejection, under an explicit clamp-don't-discard policy. Stage 4 is a state-machine gate: a motion opcode (`F`/`R`/`L`/`G`) is rejected unless the firmware is `READY` or `ACTIVE` with no fault latched, so a command arriving during an e-stop or a dead-man panic cannot move the vehicle; `S` (stop) always passes this gate. A close-range HC-SR04 reading is not part of this pipeline at all: `range_cm` is reported on the telemetry path, where it drives the dashboard's warn/critical coloring and the `range_warn`/`range_crit` bits in the logged alert flags — it never intercepts or rejects a forward command, and the operator decides whether to stop, reverse, or continue.

### **A.5.2  P1 Control Server — Serial Ownership and Telemetry Fan-Out**

P1 is the largest component and the system's centre of gravity. It exclusively owns the Arduino UART and the GPS receiver, validates and forwards operator commands, merges data from several sources into a single telemetry snapshot, broadcasts that snapshot every 200 milliseconds, maintains a replay buffer, and writes the mission log.

Its concurrency structure comprises three asyncio tasks and one thread. The task named `serial-reader` drains the UART, polling every 5 ms while data is flowing and every 20 ms when idle — a fraction of the 200 ms frame period, so that no frame is delayed by more than a fifth of its cadence. The task named `telemetry-broadcast` runs the 200 ms cycle. Uvicorn's server task handles HTTP and WebSocket connections. The GPS reader deliberately runs on a **daemon thread** rather than a task, because pyserial reads block and a 1 Hz fix rate has no reason to share an event loop with a 5 Hz broadcast cycle.

The broadcast loop uses **absolute scheduling** — `next_tick += period` rather than sleeping a fixed interval — so that a slow iteration is absorbed rather than accumulating drift across a long mission. Its body is wrapped so that any exception is logged as `BROADCAST_FAIL` without terminating the loop, on the principle that the cadence must not stop.

Each iteration also refreshes the robot's **Wi-Fi signal strength**, at most once per second. `common/wifi.py:read_signal_dbm()` reads the `wlan0` level from `/proc/net/wireless` (a file read, no subprocess) and returns `None` unless `/sys/class/net/wlan0/operstate` is `up`, because `/proc` can keep reporting the last level after the link has gone. The value goes out as the P1-owned `signal_dbm` field of every snapshot; `None` (JSON `null`) means "no usable link", never "unknown but probably fine". The interface is set by `WIFI_IFACE` (default `wlan0`).

| **Module** | **Principal Type** | **Responsibility** |
| --- | --- | --- |
| `serial_bridge.py` | `SerialBridge` | Sole UART owner; handshake, frame ingest, command egress |
| `websocket_hub.py` | `WebSocketHub`, `Client` | Client registry, role arbitration, concurrent broadcast |
| `gps_reader.py` | `GPSReader` | Threaded NMEA parsing, track accumulation, GeoJSON export |
| `ring_buffer.py` | `RingBuffer` | 300-entry history; `since()` and `gap_ms()` for replay |
| `safety.py` | `CommandValidator` | Server-side clamp, sequence monotonicity |
| `telemetry_log.py` | `TelemetryLog` | 1 Hz, 19-column CSV with packed alert bitfield |
| `lockfile.py` | `ProcessLock` | Advisory `flock` enforcing the single-writer invariant |
| `victim_log.py` | `VictimLog` | Victim marks as JSON lines in `victims/victims.jsonl`; a corrupt line is skipped, not fatal (A.12) |

***Table A.5.2 — P1 Module Responsibilities***

P1 also stores **victim marks** (A.12). `POST /api/victims` takes only a note and the AI score from the controller's browser, stamps the mark with P1's own GPS fix, last track point and servo angles, appends it to `victims.jsonl` and broadcasts it to every dashboard as a `victim_mark` message; `GET /api/victims` returns the list to a dashboard that connects later. The body is read through `read_body_limited()`, which refuses anything over 16 KiB with 413 *before* parsing or checking the key, because parsing a huge JSON body would block the event loop that also runs the 200 ms broadcast and the heartbeat path — and anyone on the network could send one.

The **startup handshake** is a fixed sequence whose ordering encodes hard-won operational knowledge. The port is opened with `exclusive=True`, which sets `O_EXCL` so the kernel rejects a second opener. Opening the port toggles DTR and resets the Arduino, so P1 then waits 2.0 seconds for the board to boot. It flushes both buffers, sends three `S` stop commands at 200 ms intervals — because if the board survived a previous P1 crash while driving, this halts it before anything slower is attempted — then sends `?` and awaits `READY` for up to 5 seconds, accepting either the token or any parseable telemetry frame as evidence of a live board. Handshake failure exits with code 2, which P3 interprets as a crash.

`ProcessLock` merits a note on its choice of location. The lock file lives at `/run/robot/p1.lock`, on tmpfs, which yields two properties: the file cannot survive a reboot and become a stale lock, and the kernel releases the lock automatically when the holder exits — including on `SIGKILL`, where no cleanup handler would run.

The WebSocket endpoint primes each newly registered client with an immediate snapshot so the first render is not delayed by up to a full broadcast period. On disconnect it unregisters the client, resets its sequence state, and — if the departing client held the controller role — sends an immediate stop to the Arduino. The dead-man timer would catch this within two seconds regardless; the explicit stop is simply faster, and the two mechanisms are intentionally redundant.

### **A.5.3  P2 Media Server — Single-Shot Negotiation and Graceful Capture Fallback**

P2 is deliberately the smallest and simplest server component, because a media path that fails should degrade the mission rather than end it. It exposes exactly two endpoints: `POST /webrtc/offer`, which accepts an SDP offer and returns an SDP answer in the same HTTP response, and `GET /health` for the watchdog.

The signaling design is minimal by intent. There is no separate signaling channel and no trickle-ICE round trip; the dashboard POSTs its offer and receives the answer synchronously. This is sound specifically because of the deployment topology: on a single local subnet with no NAT between the peers, candidate gathering is trivial and the elaborate machinery WebRTC normally requires for internet traversal would add latency and failure modes for no benefit.

The track factory implements a fallback whose architectural value is that it makes two different situations behave identically. `open_camera_track()` is wrapped so that *any* capture failure logs the fault and substitutes `SyntheticVideoTrack`. Consequently mock mode on a developer laptop and a real Pi whose camera has been knocked loose in the field follow exactly the same code path — the mission continues with a synthetic stream, and the operator sees plainly that video is not live. The microphone goes one step further, because the robot's USB webcam/mic has been seen to drop off the bus and re-enumerate: each session's mic is a `ResilientAudioTrack`, which sends silence while the mic cannot be opened, retries every 2 s, and switches to the mic as soon as it opens — and back to silence and retrying if it ends mid-session. A session that connected during an outage therefore recovers on its own instead of staying silent until the dashboard is reloaded. Each outage is logged once as `MIC_OPEN_FAIL` and its end as `MIC_RESTORED`. `SyntheticVideoTrack` renders a sweeping bar, a slow hue cycle, and a font-free clock encoded as a bar whose width grows with elapsed seconds, deliberately avoiding a fontconfig dependency in the media path.

Microphone capture has one packaging trap. The PyAV wheel bundles its own `libasound`, built with a prefix of `/tmp/vendor`, so on its own it finds no `alsa.conf` and rejects every ALSA device name — `default` included — with `EIO`; the fallback above then hid the fault behind a silent track. Pointing it at the system `/usr/share/alsa/alsa.conf` is no better, because that pulls in PulseAudio/PipeWire plugins the bundled library cannot load. `open_mic_track()` therefore sets `ALSA_CONFIG_PATH` to `p2_media/alsa.conf`, a minimal file defining a `mic:CARD=<id>,DEV=<n>` device (the same meaning as `plughw`), and resolves `AUDIO_DEVICE=default` to the first capture card by its ALSA id (e.g. `mic:CARD=U20,DEV=0`), so card renumbering across reboots does not matter.

The capture devices are shared between sessions. A V4L2 camera or ALSA microphone can be opened only once, so opening them per session gave every session after the first a busy device (`EBUSY` on the camera, `EIO` on the mic) and the silent fallback — and a second viewer was not the only trigger: a dashboard reload whose new offer arrived before the old connection had timed out was silenced the same way, with no sign on the operator's side. `SharedCapture` (in `media.py`) now opens each device on first use and fans it out through aiortc's `MediaRelay`, one consumer track per session: buffered for audio, so no frame is dropped, and newest-frame-only for video. When the last session's track ends the device is closed again, so an idle robot does not keep capturing. On 2026-09-27 two simultaneous sessions were verified to receive live microphone audio at full rate.

**Robot audio goes out as 60 ms packets that P2 encodes itself.** The robot's audio played choppy on the dashboard. The mic itself delivered the full 48 000 samples/s, but aiortc encodes each 20 ms audio frame on its thread pool, queued behind every viewer's video encoding, and on a busy Pi it sent only ~37 of the 50 packets a second (305 of ~400 in 8 s, none lost on the network), so the browser ran dry and filled the gaps with concealment. `ResilientAudioTrack` therefore resamples the mic to mono and encodes Opus itself, 32 kbps, one packet per 60 ms, the same approach as the screen audio (A.11); the dashboard's audio transceiver is pinned to Opus for this. On 2026-09-28, at load ~2.5, delivery rose to 99 % of real time (165 × 60 ms packets in 10 s). The per-session relay queue is still unbounded, so a Pi overloaded for long stretches can add delay, though no longer gaps.

P2 enables Python's `faulthandler` at start-up. PyAV and FFmpeg run native code, and P2 was seen to die with a segmentation fault while sessions connected and disconnected; with `faulthandler` on, such a crash prints every thread's Python stack to the journal (`journalctl -u robot-watchdog`) instead of leaving only P3's `PROC_CRASH exit_code=-11`. Those traces found the cause. Sharing the camera also shared each camera frame: `MediaRelay` hands every session the same `VideoFrame` object, and each session's VP8 encoder, on its own thread, converted that YUYV frame to yuv420p with `frame.reformat()`. PyAV caches the converter (an `SwsContext`) on the frame and runs it with the GIL released, so two viewers ran one converter at once and corrupted memory — a crash every one to two minutes with two dashboards open. Each session's camera track is therefore wrapped in a `PrivateVideoTrack`, which converts every frame to yuv420p on the event loop with a converter of its own (copying it if it is already yuv420p, where PyAV would hand back the shared frame), so no encoder ever sees a frame another thread can touch. The rule for P2: never let a frame object reach more than one encoder.

P2 is also the relay for talking to the victim. The dashboard's transceivers are `sendrecv` and it opens a `screen` data channel; `negotiate()` hands the operator's inbound tracks and that channel to a `ScreenHub`, and a second endpoint, `POST /webrtc/screen-offer`, accepts only localhost connections from the Robot Screen kiosk. Section A.11 covers the design.

### **A.5.4  P3 Watchdog — Supervision with Cause Discrimination**

P3 supervises P1 and P2 through a four-state machine per child: `SPAWNING`, `MONITORING`, `COOLDOWN`, `STOPPED`. The nominal cycle is spawn, monitor, detect failure, cool down for 10 seconds, spawn again.

Liveness is assessed at two levels because the two failure modes are genuinely different. An OS-level `poll()` every second catches a process that has exited. An HTTP `GET /health` every 10 seconds, with a 5-second timeout and a limit of three consecutive misses, catches a process that is alive but wedged — deadlocked on a blocking serial read, for instance — which `poll()` alone would never detect.

The feature that most distinguishes this supervisor from a naive restart loop is **exit-code discrimination**. P1 publishes a documented contract: 0 means a clean exit or a lock held by a healthy peer, 1 a lock error, 2 a failed Arduino handshake, and 3 an invalid configuration. P3 reads these and responds differently. Exit code 3 is logged as a configuration fault rather than a crash and does not increment the restart counter, because respawning a misconfigured process at speed produces a log flood and no recovery. Exit code 0 is logged distinctly as a lock-held condition, since it most often means the supervisor's own previous instance still owns the hardware during a restart race — not a fault at all.

`adopt(pid)` completes the picture. If P3 itself restarts after a software update, P1 and P2 may still be running. Killing and respawning them would drop the Arduino connection for no reason, so P3 instead attaches to the surviving orphans by verifying them through their health endpoints.

### **A.5.5  Operator Dashboard — Hook-Owned State and Two Independent Transports**

The dashboard is a React 19 single-page application in TypeScript, built by Vite, styled with Tailwind, and rendering GPS data through Leaflet. Eighteen components are arranged in a grid of three columns — controls at 22%, video at 52%, telemetry and alerts at 26% — with the controls spanning the full height and one map filling the bottom of the middle and right columns together.

**The map works offline and follows the robot.** `OfflineMapLayer` draws the operating area from `area.pmtiles`, a Protomaps vector map that P1 serves from `MAP_DIR` at `/maps`; the browser reads only the tiles it shows through HTTP range requests, and the layer is limited to the file's bounds so the online OpenStreetMap layer still shows outside it. Its libraries (`protomaps-leaflet`, `pmtiles`) load as a separate chunk after the dashboard starts, which keeps the first load over the local network unchanged, and if P1 has no map file the layer adds nothing. `LocateRobotButton` is a Leaflet control with follow mode: on by default, so a dashboard opened before the first fix moves to the robot once it arrives; turned off by the operator dragging the map; turned back on by the button, which flies to the robot. Panning waits for that fly-to to finish so a fix arriving mid-flight cannot cut it short. The live path takes a point only once the robot has moved 10 m, mirroring `MIN_TRACK_STEP_M` in `gps_reader.py`, so GPS drift around a stationary robot does not scribble the map.

**The Wi-Fi signal indicator warns before the link breaks.** `SignalIndicator` sits in the status bar next to the WebSocket chip and shows the robot's `signal_dbm` as four phone-style bars and a percentage (linear from −90 dBm = 0 % to −30 dBm = 100 %; 4 bars at −60 dBm or better, then −67, −75 and −82 dBm for 3, 2 and 1). `SignalWarningBanner` adds a full-width banner under the status bar: amber *Weak signal — turn back soon* at or below −70 dBm, flashing red *Signal critical — bring the robot back* at or below −80 dBm. Leaving a worse level needs a 3 dB margin, so the warning does not flicker at the edge. Each change of level is also written to the alert log. The pure mapping lives in `lib/signal.ts`; the thresholds are the `signal_dbm` entry of `DEFAULT_THRESHOLDS` and are provisional until the distance sweep (Section 5.3 of the paper) sets them from measured loss and latency.

The indicator never shows an old value as current. P1 cannot report a link that has failed, so `useControlSocket()` judges the link itself: it records when the last live `telemetry` frame arrived and checks four times a second. If the socket is closed or no frame has arrived for 1 s (five missed frames), `telemetryStale` is set and the level becomes `none`. The status bar then shows grey bars and **NO SIGNAL**, and a red *NO SIGNAL* banner appears. The same happens when P1 reports `signal_dbm: null`. Frames replayed in a `recovery_batch` are old and do not count as live. This catches a dead link about 1 s after the last frame, well before the socket's close event.

**A documented divergence from the original design.** The original methodology specified "no Redux — context providers per state slice," and an empty `dashboard/src/context/` directory once stood for it. The implemented architecture uses **no context providers at all**: all shared state lives in a single `useControlSocket()` hook invoked once in `App.tsx` and threaded to children as explicit props. For a dashboard of this size the simpler structure is defensible — every component's data dependencies are visible in its props, and there is no indirection between the socket and the render. The empty directory has since been removed.

`useControlSocket()` owns the entire control path. State that drives rendering is held in `useState`; values that must persist across renders without triggering them — the socket, the command sequence counter, the last server timestamp, the backoff interval, and timer handles — are held in `useRef`. On connection it sends `hello` with the controller key (if the operator has entered one, kept in the browser's `localStorage`) to claim the controller role, then `resume_from` with its last-seen timestamp if this is a reconnection. Reconnection backs off exponentially from 1 second to a 30-second ceiling. An idle heartbeat every 500 ms keeps the Arduino's dead-man armed while the operator is not driving; only the controller sends it. A key the robot refuses is dropped from storage at once, since every automatic reconnect would otherwise resend it and count toward the lockout.

The hook contains a guard worth documenting because it addresses a genuinely subtle failure. Under React StrictMode, effects are double-invoked in development. Without protection, the abandoned first socket would open moments later, claim the single controller slot, and permanently strand the live hook as an observer — the dashboard would appear connected but every command would be rejected. The hook therefore closes any prior socket before connecting and uses an `isCurrent()` closure to ignore events from superseded sockets.

The victim-finding tools (A.12) add three hooks that never touch the control path: `usePersonDetection()` runs the AI on the received video element, `useSoundLevel()` / `useReplyListener()` meter the robot microphone from the received audio track, and `useTalkback().callOut()` plays the recorded call-out on the existing talk sender. `useRecorder()` records the received media, mixed with whatever is on the talk sender, to the operator's device; `useWebrtcVideo()` now exposes the received stream (`remoteStream`) for it. `useControlSocket()` gains only the list of victim marks, loaded with `GET /api/victims` on every connect and extended by `victim_mark` broadcasts.

`useWebrtcVideo()` is entirely separate, self-contained within `VideoSurface`, and notably has **no automatic reconnection once video has connected** — a later loss is reported, the video panel shows its error state, and the operator reconnects with its *Retry video* button. Before the first successful connection it does retry every 3 seconds, because P2 starts several seconds after P1 and a dashboard opened during boot would otherwise be stuck on an error. This asymmetry with the control socket is correct by the architecture's own logic: control must be restored automatically because the vehicle is unsafe without it, whereas video is a convenience whose loss degrades the mission to `DRIVING_LIMITED` and is properly surfaced to the operator as a decision rather than papered over by silent retries.

### **A.5.6  Common Layer — The Contract and Its Enforcement**

`pi/common/` holds what all Pi processes share. `config.py` defines four frozen dataclasses — `Paths`, `P1Config`, `P2Config`, `P3Config` — each constructed from environment variables with defaults. `_default_root()` returns `/` when `/opt/robot` exists and `./var` otherwise, which is the single mechanism that lets the identical code run as a Pi service and as a developer process without root.

`logging_setup.py` implements the methodology's event format, `[TS][PROC][LEVEL][EVENT_CODE][MSG]{k=v ...}`, with UTC timestamps at millisecond precision. Each record is written in a single append-mode call so that concurrent processes never interleave partial lines — a property that matters because P1, P2, and P3 all log independently during a mission.

`wifi.py` reads the robot's Wi-Fi signal level for P1 (Section A.5.2).

`mock_hardware.py` is discussed in full in Section A.10, as its significance is architectural rather than merely convenient.

---

## **A.6  Data Architecture and the Protocol Contract**

This section is load-bearing: the protocol contract is the only real coupling between the four tiers, and understanding it is understanding the system's data architecture.

The contract is defined canonically in `pi/common/protocol.py` and hand-mirrored in `arduino/protocol.h` and `dashboard/src/lib/protocol.ts`. Each file names the other two in its header. The Python module is the authoritative superset, carrying not only the constants but `TelemetrySnapshot`, `ValidationResult`, `encode_command()`, `parse_telemetry_line()`, `format_telemetry_line()`, `derive_mission_state()`, and `compute_alert_flags()`.

Manual mirroring is a real risk and should be named as such: a constant changed in one file and not the others produces a silent protocol mismatch that no compiler will catch. The mitigation is partly procedural — the docstrings state the obligation explicitly — and partly structural, in that `derive_mission_state()` is implemented twice against the same first-match rules and the test suite pins the Python side. A stronger design would generate all three files from one source; that is recorded as future work in Section A.10 rather than claimed as present.

**Upstream, Arduino to P1**, telemetry is an 8-field positional CSV, at most 80 characters, emitted every 200 ms:

```
temperature_c, humidity_pct, gas_ppm, range_cm,
pan_angle, tilt_angle, fw_state, uptime_ms
```

Field order is load-bearing — parsing is by index, not by name — which is the correct trade on a link where every byte costs transmission time on an 8-bit MCU. `parse_telemetry_line()` validates in three passes: field count, per-field type coercion, and per-field plausibility range. Any failure at any stage discards the entire frame.

**The discard-don't-retransmit rule is the single most characteristic decision in the data architecture.** There is no retransmission, no sequence numbering, and no acknowledgement on the UART link. A corrupted frame is dropped and nothing is requested. This is correct rather than lazy: the next frame arrives within 200 ms, so the cost of a discard is one dropped sample of a continuously-sampled signal, whereas a retransmission protocol would add buffering, state, and latency to a safety-critical path in exchange for data that will be superseded before it could be re-delivered.

**Downstream, dashboard to P1 to Arduino**, commands are single-character opcodes with optional numeric arguments — `F120\n` is forward at PWM 120. The dashboard speaks JSON WebSocket messages; P1 validates and lowers them to the wire grammar. Six client message types (`hello`, `motor`, `servo`, `heartbeat`, `stop_all`, `resume_from`) and six server types (`telemetry`, `recovery_batch`, `ack`, `error`, `role`, `victim_mark`) constitute the entire WebSocket protocol; victim marks are created over REST (`POST /api/victims`, A.12), never over the WebSocket.

**P1 outward to the dashboard**, the unit of exchange is the `TelemetrySnapshot` (19 keys as sent): the 8 Arduino fields, plus GPS position and fix quality merged from the reader thread, plus server metadata — message type, sequence number, server timestamp, serial health, client count, TURN status, and the robot's Wi-Fi signal `signal_dbm`. `build_snapshot()` re-asserts the P1-owned fields *last*, after merging, so that a malformed or hostile frame can never overwrite the server's own view of its health.

| **Store** | **Medium** | **Retention** | **Purpose** |
| --- | --- | --- | --- |
| Ring buffer | Memory, 300 entries | 60 s at 200 ms | `resume_from` replay after reconnect |
| `telemetry.log` | Disk CSV, 19 columns | Daily rotation, 7 kept | Post-mission analysis at 1 Hz |
| `p{1,2,3}_events.log` | Disk, structured text | Weekly rotation, 8 kept | Fault diagnosis and audit |
| GeoJSON track | Disk, per session | 90 days (cron) | Mission path reconstruction |
| `victims/victims.jsonl` | Disk, one JSON line per mark | Kept until deleted by hand (not rotated) | Victim marks; no images (A.12) |

***Table A.6 — Data Stores, Retention, and Purpose***

The two telemetry rates are deliberately decoupled. Broadcast runs at 200 ms because the operator needs a responsive interface; disk logging samples at 1 Hz because the full stream would consume roughly 3.2 MB per hour to record data whose post-mission value is trend-level. The ring buffer holds 60 seconds, which bounds the worst case for a reconnecting dashboard: 60 seconds of history against a P1 restart of approximately 8 seconds. When a client's `last_ts` predates the oldest buffered entry, `gap_ms()` reports the shortfall and the dashboard renders an explicit gap marker on the map rather than interpolating across data it never received.

`compute_alert_flags()` packs nine boolean conditions — temperature warn and critical, gas warn and critical, range warn and critical, GPS loss, and Wi-Fi signal warn and critical (bits 8 and 9; critical is also set when `signal_dbm` is null) — into a single integer bitfield per log row, keeping the CSV compact while preserving the full alert history.

---

## **A.7  Runtime View**

### **A.7.1  Startup Handshake**

```
  systemd                P3              P1                Arduino
     |                    |               |                    |
     |--start service---->|               |                    |
     |                    |--spawn P1---->|                    |
     |                    |               |--flock p1.lock     |
     |                    |               |--open O_EXCL------>| (DTR reset)
     |                    |               |--wait 2.0s         | booting
     |                    |               |                    |--"READY"
     |                    |               |--flush buffers     |
     |                    |               |--"S" x3 @200ms---->| (halt if driving)
     |                    |               |--"?"-------------->|
     |                    |               |<--READY or frame---|
     |                    |               |--start GPS thread  |
     |                    |               |--start broadcast   |
     |                    |<--/health 200-|                    |
     |                    |--spawn P2---->|                    |
```
***Figure A.7.1 — Startup Handshake and Supervision Establishment***

The triple stop is the step most worth understanding. If P1 crashed while the vehicle was driving and is now restarting, the Arduino's dead-man will have stopped the motors within two seconds — but P1 does not depend on that. It halts the board explicitly before attempting anything slower, and it does so three times because a single command could be lost to a partially-flushed buffer during the reset.

### **A.7.2  The 200 ms Telemetry Cycle**

```
  Arduino --CSV--> [serial-reader task, polls 5/20ms]
                        |
                        v  parse_telemetry_line()  -- malformed -> DISCARD
                        |
                   _latest_frame  (last-value-wins, no queue)
                        |
    [telemetry-broadcast task, absolute 200ms tick]
                        |
                   build_snapshot()
                     +-- _latest_frame      (Arduino fields)
                     +-- gps.snapshot()     (thread-safe merge)
                     +-- signal_dbm         (wlan0 RSSI, read at 1Hz)
                     +-- server metadata    (re-asserted last)
                        |
          +-------------+-------------+
          v             v             v
    RingBuffer    TelemetryLog    WebSocketHub
    (60s history) (1Hz sample)    (gather fan-out)
                                        |
                                        v
                              all clients -> React re-render
```
***Figure A.7.2 — Telemetry Path from UART to Rendered Interface***

The reader and broadcaster are connected only by `_latest_frame`, a single last-value-wins slot with no queue between them. This is the mechanism that decouples the two rates: a serial stall cannot block the broadcast cadence, and a slow broadcast cannot back up the UART. If two frames arrive within one broadcast period, the older is simply superseded — correct behaviour for a continuously-sampled signal where only the current value has operational meaning.

### **A.7.3  Motor Command with Dual Validation**

An operator keypress travels through two independent validators. The dashboard sends `{type:"motor", dir:"F", speed:120, seq:n}`. P1's `CommandValidator` clamps the speed to 0–180, checks that the sequence number exceeds the last seen from that client, and encodes `F120\n`. The Arduino then re-validates through all four of its own stages before acting, including the state-machine gate that P1 does not duplicate, since P1 has no notion of the firmware's fault latch. The HC-SR04 range reading takes a separate path — Arduino to P1 telemetry to dashboard alert — and never enters either validator.

The redundancy is deliberate and the two validators serve different purposes. The Arduino enforces safety for its own sake and cannot be bypassed by any Pi-side defect. P1's copy rejects bad input before it consumes UART bandwidth and — equally important — returns a human-readable reason to the operator, which the Arduino's terse `ERR_TOK` cannot. Note that `stop_all` bypasses the sequence check entirely: a stop must never be dropped because a counter arrived out of order.

### **A.7.4  Reconnection and Replay**

On disconnect the dashboard begins backing off from 1 second toward a 30-second ceiling while its mission state falls to `STOP`. On reconnection it sends `hello` to reclaim the controller role, then `resume_from` with the last `server_ts` it saw. P1 answers with a `recovery_batch` drawn from the ring buffer. If the gap exceeds the buffer's 60-second span, `gap_ms()` reports the shortfall and the map renders a discontinuity marker — the operator is shown that data is missing rather than being presented with a smooth line the vehicle never travelled.

---

## **A.8  Safety and Fault-Tolerance Architecture**

Safety in this system is not a subsystem but a property distributed across every tier, and it is arranged so that mechanisms at each level are independent — no single defect disables more than one of them.

**Layered command validation.** Speed and angle clamping exist at three levels: the dashboard's slider bounds, P1's `CommandValidator`, and the Arduino's four-stage parser (the mock emulator mirrors the framing/opcode/argument stages but not the state-machine gate). The dashboard's bounds are convenience; P1's are efficiency and operator feedback; the Arduino's are authoritative. Obstacle distance from the HC-SR04 is reported through telemetry as a warning, not enforced as a validation stage.

**Dual-mechanism dead-man.** The Arduino's 2,000 ms timer is the guarantee. P1's immediate stop on controller disconnect is the optimisation. Either alone is sufficient to halt the vehicle.

**Mission state as an operator-visible contract.** `derive_mission_state()` evaluates first-match rules: any of WebSocket down, serial down, or command acknowledgement older than 3,000 ms yields `STOP`; loss of video yields `DRIVING_LIMITED`; otherwise `DRIVING` when a command is active and `READY` when idle. Because it is a pure function of current inputs, the indicator can never disagree with the state it describes. It is computed identically on both sides of the link.

**Single-writer enforcement.** Two independent mechanisms — `flock` on tmpfs and `O_EXCL` on the device — each sufficient alone.

**Panic latching.** A state-invariant violation latches `STOPPED` until board reset. Where the dead-man is designed to recover, panic is designed *not* to: it signals that the firmware's assumptions have been falsified, and no automatic recovery from that condition would be trustworthy.

| **Failure Mode** | **Detection** | **Response** | **Recovery** |
| --- | --- | --- | --- |
| Operator link lost | Dead-man expiry | Motors stopped, state → ARMED | Automatic on next command |
| Dashboard closed | WebSocket disconnect | Immediate stop + role released | Operator reconnects, replays |
| P1 crash | `poll()` within 1 s | P3 respawns after 10 s cooldown | Automatic; Arduino safe throughout |
| P1 wedged | 3 health misses (~30 s) | SIGKILL, then respawn | Automatic |
| P1 misconfigured | Exit code 3 | Logged as config fault, not a crash | Manual — deliberately not looped |
| Camera failure | Capture exception | Synthetic track substituted | Mission continues in `DRIVING_LIMITED` |
| Wi-Fi signal weakening | `signal_dbm` ≤ −70 / ≤ −80 dBm | Amber / red banner, bars change colour, alert logged | Operator drives back; clears 3 dB above the threshold |
| Telemetry stops arriving | No frame for 1 s, or socket closed | Indicator shows NO SIGNAL; last value never shown | Automatic on next live frame |
| Wi-Fi network outage | Telemetry gap, ack timeout | Mission state → `STOP` | Backoff reconnect + replay |
| Corrupt frame | Parse or range check | Frame discarded silently | Next frame within 200 ms |
| Obstacle distance ≤ 20 cm | HC-SR04, Category 2 poll | Range warning/critical alert; operator decides movement | N/A — not a fault, no recovery needed |
| State invariant violated | `checkInvariants()` | Panic; motors stopped, latched | Board reset only |
| GPS loss | Fix flag, `gps_lost` bit | Position stale-flagged; drive unaffected | Automatic on reacquisition |

***Table A.8 — Failure Modes, Detection, Response, and Recovery***

Reading this table by recovery column reveals the architecture's intent clearly: nearly every fault recovers automatically, and the two that do not — configuration errors and panic latching — are precisely the two where automatic recovery would mask a condition a human must inspect.

---

## **A.9  Deployment View**

The Pi is provisioned by `deploy/install.sh`, an idempotent eight-stage script that may be re-run after a code update without disturbing operator-customised configuration. It installs system packages, creates the unprivileged `robot` user in the `dialout`, `video`, and `audio` groups, rsyncs the code to `/opt/robot`, builds a virtualenv, copies configuration templates **only where absent**, registers the systemd unit and logrotate policy, and finally prints the manual steps it cannot safely automate — enabling the GPS UART, and verifying the serial device. The Pi's fixed address is set in the Wi-Fi router's settings.

```
  /opt/robot/          pi/ (P1,P2,P3,common) | dashboard/dist | venv/
  /etc/robot/          p1.env p2.env p3.env thresholds.json
  /var/log/robot/      telemetry.log  p{1,2,3}_events.log  gps_track/
  /run/robot/          p1.lock (tmpfs — never survives reboot)

  systemd: robot-watchdog.service  --> P3 --> spawns P1 + P2

  Local Wi-Fi network:
    Wi-Fi router       DHCP server; fixed address reserved for the Pi
    Raspberry Pi       P1 :8080, P2 :8443
    Operator laptop    opens http://<pi-ip>:8080
```
***Figure A.9 — Deployment Layout and Network***

Configuration is environment-file driven, with three files that map one-to-one onto the three processes. Alert thresholds live separately in `thresholds.json` so that they can be tuned in the field without touching process configuration; `load_thresholds()` merges the file over the built-in defaults and falls back silently to those defaults if the file is missing or malformed — a field-tuning error degrades to known-good behaviour rather than a failed start.

The network is an ordinary Wi-Fi network: the Pi and the operator laptop join the same network, and the operator opens `http://<pi-ip>:8080` in the browser. The Pi's address is fixed with a DHCP reservation in the Wi-Fi router's settings so it does not change between missions.

Log rotation is tiered by write rate: `telemetry.log` daily at 50 MB retaining 7; the three event logs (`p1_events.log`, `p2_events.log`, `p3_events.log`) weekly at 10 MB retaining 8. All use `copytruncate` so running processes keep their open file handles. GPS tracks, CSV exports and `victims/victims.jsonl` fall outside logrotate; for GPS tracks a `find -mtime +90 -delete` cron line is documented but not installed by `install.sh`, and victim marks are kept until deleted by hand.

Two housekeeping defects are worth recording. The systemd unit advertises `Documentation=file:///opt/robot/docs`, and until this document was written that directory was empty. The logrotate policy once named `watchdog.log`, `fault.log` and `session.log`, which no code writes, so the real logs were never rotated; since 2026-10-08 it names exactly the files the code opens.

---

## **A.10  Quality Attributes and Architectural Decisions**

### **A.10.1  Quality Attributes**

**Safety** is the attribute to which all others are subordinated, and it is achieved by placing the guarantee at the lowest tier and making every higher-level mechanism redundant rather than necessary. The measurable claim is that the vehicle halts within 2 seconds of losing operator contact by any cause, including total failure of every tier above the Arduino.

**Availability** is pursued through supervision and graceful degradation rather than redundancy — there is no second Pi. P3 restores a crashed or wedged process within roughly 10 to 40 seconds, and during that window the vehicle is stopped but undamaged. Degradation is graded rather than binary: video loss, network loss, and GPS loss each reduce capability by a defined amount while keeping the mission alive.

**Latency** is budgeted at every hop: sensor to telemetry at most 200 ms, telemetry to render one broadcast period, keypress to motor a validation pass plus UART transit. The 200 ms cadence, the 5 ms serial poll, and the absolute-scheduled broadcast loop all exist to keep the operator's perception of the vehicle current.

**Testability** is achieved through the mock hardware layer, which decouples the entire stack from physical hardware. The suite (156 tests on 2026-10-30, `TEST_REPORT.md` §3) exercises the protocol parser, the validation pipeline, ring-buffer wraparound and replay, mission-state derivation, controller access, talk-back, victim marks and the emulated dead-man — with boundary cases pinned deliberately: `STOP` at 3,001 ms but not at exactly 3,000 ms.

**Modifiability** follows from the narrow protocol contract. A new sensor requires a coordinated change to three mirror files and nothing else. The corresponding weakness is that the mirroring is manual.

### **A.10.2  Decision Record**

The methodology's two source documents disagreed in several places. The implementation resolved each contradiction by choosing a default and making it configurable, summarised here.

| **Contradiction** | **Resolution** | **Configurable At** |
| --- | --- | --- |
| Serial device `ttyUSB0` vs `ttyAMA0` | `ttyUSB0` (Sections 8.7/8.8 authoritative) | `p1.env: SERIAL_PORT` |
| Dead-man: `millis()` vs Timer1 ISR | Software check — Timer1 belongs to Servo | `DEADMAN_MS` |
| Telemetry field count (12/22/26) | Schema of §8.10.1.2; as built, 19 keys incl. `signal_dbm` (A.6) | `pi/common/protocol.py` |
| Operational mode count | Build Mode 2, Local network only (§8.11.6) | `p3.env: ENABLE_OVERLAY=0` |

***Table A.10 — Specification Contradictions and Their Resolutions***

Three further decisions are visible only in the code and are recorded here for the first time.

**Hook-owned state rather than context providers.** The plan specified context providers per state slice; the implementation uses a single hook with prop threading and leaves `src/context/` empty. For a dashboard of this size the simpler structure is defensible and arguably preferable — data flow is explicit at every call site. The empty directory has since been removed.

**No reconnection on the video path.** The control socket reconnects indefinitely; the WebRTC path attempts negotiation once. This asymmetry is intentional: control is safety-critical and must self-heal, while video is a capability whose loss should be surfaced to the operator as a decision.

**Mock hardware as protocol reimplementation.** This is the most consequential decision not present in the original plan. `MockArduino` does not stub the firmware — it reimplements the framing/opcode/argument-clamp validation, the dead-man semantics including the boot-expired initial state, and the 200 ms cadence faithfully enough that P1 cannot distinguish it across the serial boundary for driving and telemetry purposes, though it does not model the firmware's ESTOP/PANIC state-machine gate. Its simulated obstacle range even closes while driving forward so the 20 cm warning threshold is reachable in a demonstration. The consequence is that the entire stack runs end-to-end on a laptop, the full test suite executes with no hardware attached, and the protocol has been exercised continuously throughout development rather than only at hardware bring-up. The cost is a second implementation of the firmware's semantics that must be kept in step — an obligation its docstring states explicitly.

### **A.10.3  Known Limitations**

Recorded plainly, as the architecture's own account of where it is incomplete:

1. **Protocol mirroring is manual.** Three files must change together with no compiler enforcement. Code generation from a single source would eliminate an entire class of silent defect.
2. **Test coverage is uneven.** The protocol, validator, ring buffer, and mission-state logic are well covered. `SerialBridge`, `WebSocketHub`, `TelemetryLog`, `ProcessLock`, and `SupervisedProcess` have no direct tests, `GPSReader` is tested only for its track filtering (not NMEA parsing), and there is no JavaScript test runner configured — `package.json` provides only `oxlint`.
3. **Hardware validation is partial.** The firmware runs on the assembled robot, and the dead-man stop, process recovery, media CPU cost and GPS drift have been measured there (paper Section 5). Wheel-stop timing, control latency over Wi-Fi, media delay and quality, and a full field run have not; `TEST_REPORT.md` §4–8 tracks them.
4. **P3 is a single point of supervision failure.** If P3 dies, systemd restarts it and it adopts the surviving orphans — but during that window nothing is watching P1 and P2.
5. **Controller authentication is a shared key over plain HTTP.** A dashboard must present `CONTROLLER_KEY` to drive, stop or talk (A.3, Driver 6), but the key travels unencrypted over `ws://` and `http://`, so anyone who can capture Wi-Fi traffic can read it; confidentiality rests on WPA2/WPA3 at the link layer. A short key (a few digits) is easy to guess, so the 5-tries/5-minute lockout is what makes guessing slow (about 17 hours to try all 1,000 three-digit keys against one service); P1 and P2 count failures separately and in memory, so a restart clears them. There is one key, not per-operator accounts, and logs identify a controller only by IP address.
6. **Housekeeping.** The systemd unit waits for `dev-ttyUSB0.device` while the UNO enumerates as `/dev/ttyACM0`; the GPS-track clean-up cron is documented but not installed; `victims/victims.jsonl` is never rotated or pruned. (The logrotate file names and the empty `src/context/` directory recorded here earlier have been fixed.)
7. **Talk-to-victim is only partly tested on hardware and needs a secure context.** Both audio directions work on the robot, but operator video, images, text and tap-to-answer questions have not been confirmed on a physical display (a first attempt at a question failed because the kiosk showed a cached page from before the update; `/screen` is now sent with `no-cache`), and answering needs the display's touch input, which was not connected to the Pi on 2026-10-30. Mic/camera capture on the operator laptop requires HTTPS or a per-laptop Chrome flag, and a VNC viewer left open can switch the display to VNC mode by accident (Section A.11).
8. **The Wi-Fi warning uses robot-side signal strength only, with provisional thresholds.** Since 2026-10-28 the dashboard shows the robot's RSSI as bars and a percentage, warns at −70 and −80 dBm, and shows NO SIGNAL when telemetry stops (A.5.5). The signal is what the robot hears; the laptop's side of the link can be weaker, and a wall or door can drop the link faster than any warning — the 1 s staleness check and the Arduino dead-man cover that case. The −70/−80 dBm thresholds are not yet calibrated: the distance sweep that relates RSSI to loss and latency has not been run.
9. **The victim-finding tools are not evaluated (A.12).** The AI was trained on everyday photos and will miss people lying down, covered, in dust or in the dark; its accuracy on such scenes, the 10 dB reply threshold and the load on the operator laptop have not been measured. Snapshots live only on the device that took them, so a laptop lost or wiped before they are copied off loses them.

---

## **A.11  Two-Way Communication with the Victim**

**Status: implemented; audio tested on robot hardware.** The path was first exercised end to end against mock hardware — aiortc peers standing in for the operator and the Robot Screen, and headless Chromium with fake camera and microphone driving the real dashboard and kiosk page. On 2026-09-27 both audio directions were verified on the robot: operator push-to-talk heard from the speaker on the 3.5 mm jack, and the robot's USB microphone received over WebRTC. Operator video, images and text on a physical display remain untested, because no HDMI display was attached.

A rescue robot that reaches a conscious victim is more useful if it can reassure and instruct them, not only observe them. The robot carries a victim-facing **robot display** and **speaker**, and the existing WebRTC session is two-way. The operator can push-to-talk, show their face from the laptop camera, show an image or share their screen, and send short text messages that appear in large type on the robot display — which also serves a victim who cannot hear. For a victim who cannot speak, the operator can type a question with two to four answers of their own; the robot display shows it with one large button per answer, and the tapped answer comes back to the dashboard.

```
  Talk-to-Victim Data Path:
  ---------------------------------------------------------------

  OPERATOR LAPTOP (dashboard: useTalkback + TalkPanel)
    laptop mic (push-to-talk) ---> Opus audio   (Track 4)
    laptop camera | image | screen -> video     (Track 3)
    message box ------------------> data channel "screen"
    question + 2-4 answers -------> data channel "screen"
                 |
                 |  same RTCPeerConnection, WebRTC :8443
                 v
  P2 MEDIA SERVER (talkback.ScreenHub)
    floor control: first sending operator holds the floor
    decode operator tracks, re-encode on the screen connection
                 |
                 |  second RTCPeerConnection (localhost only)
                 v
  ROBOT SCREEN  (Chromium --kiosk http://localhost:8443/screen)
    video element  --> robot display (HDMI, 7")
    audio element  --> speaker (3.5 mm jack)
    text banner    <-- "screen" messages
    question layer <-- "screen" messages; tapped answer --> P2 --> dashboards
    idle screen    when no operator media
```
***Figure A.11 — Operator-to-Victim Path***

| **Element** | **Implementation** |
| --- | --- |
| Dashboard `useWebrtcVideo()` | Transceivers are `sendrecv` and a `screen` data channel is opened; exposes the senders and channel as a `TalkLink` |
| Dashboard `useTalkback()` | Mic via `getUserMedia`, toggled by the track's `enabled` flag, and opened (muted) as soon as the link is up when the browser already grants mic permission; camera via `getUserMedia`, screen via `getDisplayMedia`, still images via `canvas.captureStream()` repainted every 500 ms; all attached with `replaceTrack`, so no renegotiation |
| Dashboard `TalkPanel` | Hold-to-talk button (labelled *Enable mic* until the mic is open, see below), video-source picker with local preview, message box with on-screen acknowledgement, robot-screen status, *Release screen*, and the *Robot Display / VNC Mode* radio buttons with a warning while in VNC mode |
| Dashboard `QuestionPanel` | Inside `TalkPanel`: question box, two answer boxes (*+ Add answer* up to four), *Send question* (*Replace question* while one is waiting), *Clear*, and a status line — "Waiting for answer… m:ss left", **Answer: …** or "No answer (5 min)". Nothing is kept between questions |
| Dashboard `VideoSurface` | *Listen to robot mic* toggle — the video element autoplays muted, so the victim's voice was previously never audible |
| Dashboard `DriveControl` | Drive keys are ignored while typing in a text field, so a message containing "w" cannot move the robot |
| P2 `talkback.py` | `ScreenHub` (floor control, message validation and routing, display mode, the current question and its 5-minute timer); `ScreenVideoTrack` / `ScreenAudioTrack`, the outbound tracks on the screen connection |
| P2 `signaling.py` | `negotiate()` hands inbound operator tracks and the `screen` channel to the hub; `negotiate_screen()` answers the kiosk |
| P2 endpoints | `POST /webrtc/screen-offer` (403 unless from localhost), `GET /screen` (sent with `Cache-Control: no-cache`, so the kiosk loads an updated page), `GET /screen/mode`, `POST /screen/mode` (403 unless from localhost); `/health` adds `screen_connected`, `floor_held` and `display_mode` |
| Robot Screen | `pi/p2_media/screen/index.html`, a dependency-free page with a *Hold 3 s for VNC* button in the corner and a full-screen question layer (question in large type, 2–4 buttons, "Answer sent ✓" for 2 s after a tap; the speaking badge and the VNC button stay above it); launched by `deploy/robot-screen/robot-screen.sh` from the desktop session's autostart, which polls the display mode and opens or closes the kiosk to match |
| `install.sh` | Installs Chromium, deploys the launcher, installs the autostart entry for the desktop user, and adds a *Show Robot Screen* entry to the app menu and desktop |

***Table A.11 — Implementation by Component***

| **Message** | **Direction** | **Purpose** |
| --- | --- | --- |
| `media_state` `{talking, video}` | Dashboard → P2 → screen (as `screen_state`) | What the operator is sending; the screen hides the idle overlay only while a video source is active |
| `screen_text` `{text, ts}` / `screen_clear` | Dashboard → P2 → screen | Text banner, trimmed and capped at 280 characters |
| `screen_ack` `{ts}` | Screen → P2 → floor holder | Confirms a message is displayed |
| `question_ask` `{text, options}` / `question_clear` | Dashboard → P2 | A question with 2-4 operator-written answers (each capped at 40 characters); replaces any current one and claims the floor |
| `question_show` `{id, text, options}` / `question_hide` `{id}` | P2 → screen | Shows the question as tap-to-answer buttons, or takes it off (cleared, timed out after 5 minutes, or floor released) |
| `question_answer` `{id, choice}` | Screen → P2 | The tapped option's index; only the first answer to the current question counts |
| `question_status` `{id, text, options, status, answer, remaining_s}` | P2 → every dashboard | `waiting`, `answered`, `expired` or `cleared`; observers see it too, and a reconnecting dashboard gets it at once |
| `floor_release` | Dashboard → P2 | Gives up the robot screen; also released on disconnect |
| `talk_status` `{screen_online, floor, display_mode}` | P2 → every dashboard | Drives the panel's status, enables or disables its controls, and sets the display-mode radio buttons |
| `floor_denied` | P2 → dashboard | Another operator holds the screen |
| `display_mode` `{mode: "robot" \| "vnc"}` | Dashboard → P2 | Shows or hides the Robot Screen kiosk; needs no floor |

***Table A.11b — `screen` Data-Channel Messages***

Nine decisions shape the feature.

**Messages travel through P2, not P1.** P1 owns the safety-critical command path, and nothing about talking to a victim should be able to delay a stop. Carrying messages on a WebRTC data channel keeps the whole feature inside P2's failure domain: if P2 dies, the operator loses video and the ability to talk, but drives on unaffected — exactly the existing `DRIVING_LIMITED` behaviour.

**P2 relays; the browser renders.** aiortc decodes every inbound track, so P2 does decode operator media and re-encode it for the screen connection — a real CPU cost on the Pi, which is why the dashboard caps the laptop camera at 640×480 and 10 fps. What P2 does *not* do is render: Chromium on the robot handles jitter buffering, audio output, and display, and a kiosk crash is contained to the display. The launcher waits for P2 before starting Chromium and relaunches it three seconds after a crash.

**The screen connection never renegotiates.** `ScreenVideoTrack` and `ScreenAudioTrack` exist for the whole life of a screen connection and read whatever the floor holder currently sends. With nothing new, video repeats the last frame after one second (keeping a still image or idle shared screen alive) and audio sends silence on schedule. All frames are restamped on one monotonic clock, because the operator's RTP timestamps, repeated frames and generated silence would otherwise interleave. Every inbound operator track is drained for its whole life whether or not its session holds the floor, because aiortc queues decoded frames without bound when nobody reads them.

**Screen audio goes out as 60 ms packets that P2 encodes itself.** The operator's voice first played on the robot too fast, with pieces missing. aiortc's sender needs one trip through P2's event loop per audio frame, and on a busy Pi that loop ran 24 ms late on average (up to ~400 ms), so 20 ms frames could not keep pace: the track fell seconds behind, then sent in bursts faster than real time, and the operator frames that piled up meanwhile overflowed the 200 ms queue and were dropped — 64 % of the voice in one measurement. `ScreenAudioTrack` therefore encodes mono Opus itself, one packet per 60 ms, and hands aiortc the ready-made packets (the screen transceiver is pinned to Opus for this). That needs a third as many trips through the loop. A packet that is late by more than 100 ms resets the track's clock instead of starting a catch-up burst. Voice is collected in a FIFO with a 120 ms cushion: after running dry the track sends silence until the cushion refills, so speech resumes whole rather than in 60 ms scraps, and anything beyond 400 ms is discarded to bound the delay. Measured under the same load with Chromium playing the result, concealed audio on the robot fell from 62 % to 0 % and the whole of a test tone arrived where half had before. On the live robot at load ~8, a 440 Hz tone arrived at 440 Hz with 6–7 % of 100 ms windows silent, from about 30 % before. The remaining gaps come from CPU contention (development tools running on the Pi), so they should shrink on a robot running only its own processes.

**Only the controller talks.** A P2 session may act only if its `POST /webrtc/offer` carried the right controller key (the same `KeyGate` rule as P1, answered with `role` and `auth` in the SDP answer) *and* it comes from the host P1 currently reports as its controller. P2 asks P1 once a second over a localhost-only `GET /api/controller`, so the talk path follows P1's single controller slot, takeovers included: a laptop that knows the key but has been taken over is view-only, and if it held the floor the floor is released. The key alone was not enough, because two laptops that both know the key would both have been able to talk. While P1 cannot be reached nobody may talk. Matching is by IP address, so two tabs on the controller's laptop both count as the controller. Every other session still receives the robot's video and audio but is view-only: `ScreenHub` answers its messages, including display-mode switches, with `view_only`, and never forwards its media, and `talk_status` reports `can_control` so the dashboard greys the panel out.

**One talker at a time.** Mirroring the single-controller slot of Driver 6, only one controller session may send media or messages to the robot. The first session to send anything claims the floor and holds it until it releases or disconnects; others are refused with `floor_denied` and stay watch-and-listen only, so a victim never hears two voices at once. Releasing the floor clears the screen back to its idle state.

**Push-to-talk rather than open microphone.** The robot's speaker and microphone sit centimetres apart; an open operator microphone would feed the speaker's output back to the operator as echo. Sending audio only while the Talk button is held, with the browser's own echo cancellation on, removes most feedback without an echo canceller on the Pi. The first press used to be lost: it triggered the browser's microphone permission prompt, which takes focus from the button, so the button saw its pointer capture end and stopped talking before the operator had said anything. The dashboard now opens the mic as soon as the link is up if permission is already granted; otherwise the button reads *Enable mic*, its first press only asks for permission, and from then on it reads *Hold to talk* and every press talks.

**A display mode, because VNC shares the robot display.** The Pi's VNC server (wayvnc) mirrors the physical display rather than providing a separate desktop, so the full-screen kiosk also covered the VNC session and made the Pi unusable for maintenance. P2 therefore holds a display mode, `robot` (kiosk shown) or `vnc` (kiosk closed, Pi desktop usable), and the launcher polls `GET /screen/mode` once a second and opens or closes Chromium to match. The mode can be switched from three places: radio buttons on the dashboard (over the data channel), a *Hold 3 s for VNC* button on the kiosk page (to `vnc` only), and a *Show Robot Screen* menu entry on the Pi (both over `POST /screen/mode`, localhost only). Closing the kiosk by hand with Alt+F4 also counts as switching to `vnc`. Every change is broadcast in `talk_status`, so each control shows the mode the robot is really in, and the dashboard warns that the victim can no longer see the operator while in `vnc` mode. Switching needs no floor, because it is a maintenance action rather than talking to the victim, and the mode resets to `robot` whenever P2 starts so a reboot never leaves the victim facing the Pi desktop. This switch has been tested on the robot, and that testing exposed a hazard: because VNC mirrors the display, a VNC viewer left open on the operator laptop sends its clicks and key presses to the kiosk page, and with the kiosk's original one-click radio buttons a stray click — or an arrow key pressed while a radio button had focus — switched the robot to `vnc` and silenced the operator mid-sentence; the logs showed it happening within seconds of the kiosk opening, again and again. The kiosk control is therefore a single button that must be held for three seconds, filling as it is held; releasing early cancels, it is not focusable, and it ignores keys, so neither a click nor a key press can switch. Tested in Chromium: a click, a 1 s hold and Enter/Space/arrow keys left the mode at `robot`; a 3.3 s hold switched it. Operators should still close the VNC viewer while talking to a victim. To make such switches traceable, a local `POST /screen/mode` logs its client in the `DISPLAY_MODE` event, `source=local:127.0.0.1:kiosk` for the kiosk page or `source=local:127.0.0.1:curl` for the launcher and desktop shortcut.

**P2 owns the question and its timeout.** A question for a victim who cannot speak is held in `ScreenHub`, not in the dashboard or the kiosk: it has an id, the answers, a status (`waiting`, `answered`, `expired`, `cleared`) and a 5-minute timer on P2's event loop. Only one exists at a time, so a new question replaces it; *Clear*, the timeout and a floor release take it off the screen. The kiosk sends back the index of the tapped answer with the question's id, and P2 accepts only the first tap on the current, waiting question, so a double tap or a tap on a replaced question counts for nothing. Because P2 holds the state, "no answer" is reported even when the kiosk reloads or the dashboard reconnects; a reconnecting kiosk is shown a waiting question again and a reconnecting dashboard gets its status at once. Observers see the question and the answer but cannot ask. Nothing is stored: the event log records only the id, the number of answers and the chosen index, not the text. Questions claim the floor like text, and travel on the same data channel, so they add no path to P1.

The kiosk plays through the desktop session's default PipeWire sink, so that default must be the 3.5 mm jack (`bcm2835 Headphones`). On the robot it had been saved as the HDMI output and only fell back to the jack because no HDMI audio sink was present; attaching an HDMI display with audio would have moved the operator's voice off the speaker. It is now set with `wpctl set-default <jack sink id>`, which WirePlumber keeps across reboots.

Two constraints remain. Browsers expose the microphone and camera only in a secure context, and the dashboard is served over plain HTTP at `<pi-ip>:8080`; until it is served over HTTPS, each operator laptop's Chrome must list that origin under `chrome://flags/#unsafely-treat-insecure-origin-as-secure`. The origin must match the address bar exactly (scheme, IP and port). Where the flags page is ignored, as on a managed browser, starting Chrome with `--unsafely-treat-insecure-origin-as-secure=<origin> --user-data-dir=<dir>` works, and `isSecureContext` in the console confirms it. Firefox and Safari have no supported equivalent, so the operator browser for talking is Chrome or Edge. Images and text messages need no secure context and work regardless, and the panel says so. And the operator-to-robot video adds roughly 300 kbps to the Wi-Fi budget when the camera is on — within capacity, but it should be measured alongside the existing 500 kbps downstream stream.

---

## **A.12  Victim-Finding Tools**

**Status: implemented; unit-tested on the robot side, not evaluated.** Three tools help the operator notice a person and record where they are: AI person detection on the video, a recorded call-out with a reply cue, and victim marks. A fourth, session recording, keeps the video and both sides of the conversation on the operator's computer. They help the operator look; they never act on the motors and never confirm that someone is there.

| **Element** | **Implementation** |
| --- | --- |
| Dashboard `usePersonDetection()` | MediaPipe Tasks Vision 0.10.21 `ObjectDetector` with `efficientdet_lite0.tflite` (4.6 MB, COCO-trained), `categoryAllowlist: ['person']`, score threshold 0.4, at most 5 boxes, CPU delegate, `VIDEO` running mode on the received `<video>`; at most 5 Hz; "possible person" after 3 frames in a row with a person, cleared after 5 without; on/off remembered in `localStorage` |
| Dashboard `VideoSurface` / `drawPersonBoxes` | Overlay canvas scaled to the `object-contain` picture; boxes red at ≥ 0.7, orange below; *POSSIBLE PERSON* badge; *AI: on / off / loading / error* toggle; a standing reminder that the AI can miss victims |
| Dashboard `App` | At most one "AI: possible person in view" alert per 30 s, on the rising edge only |
| Dashboard `useTalkback().callOut()` | Fetches `audio/callout-en.mp3`, decodes it with Web Audio and puts a `MediaStreamDestination` track on the talk audio sender with `replaceTrack`; restores the mic track when the clip ends; reports `talking` in `media_state` meanwhile, so P2 treats it as speech and floor rules apply |
| Dashboard `useSoundLevel()` | RMS of the robot audio track (2048-sample analyser, every 100 ms) in dBFS, floor −80; meter redrawn at most every 250 ms, showing the loudest sample since the last redraw; works while the robot mic is muted on the laptop |
| Dashboard `useReplyListener()` | Baseline = median of the 2 s before the call-out; for 10 s after it, a rise of ≥ 10 dB raises "sound after call-out"; nothing judged while the clip plays |
| Dashboard `MarkVictimButton` | Captures the frame (with boxes) as JPEG when the form opens; sends note + AI score; then `saveVictimToDevice()` |
| Dashboard `lib/saveVictim.ts` | Snapshot kept in IndexedDB (`robot-victims` / `snapshots`) and as an object URL; downloads `victim-<id>.jpg` and a plain-text `victim-<id>.txt`; manual download links as a fallback |
| Dashboard `VictimList`, `MapPanel` | Every mark, newest first; red **+** on the map, faded when placed at the last known point |
| P1 `victim_log.py` | `VictimLog.add()` / `list()`, append-only JSON lines under a lock; id = local time + 4 hex digits |
| P1 `main.py` | `GET /api/victims`; `POST /api/victims` (body ≤ 16 KiB via `read_body_limited()`, controller key in `X-Controller-Key` checked by the same `KeyGate` as driving, note ≤ 280 characters); `VICTIM_MARK` event logged; `victim_mark` broadcast |
| Dashboard `useRecorder()` | Session recording: `MediaRecorder` on the received video track plus one audio track from an `AudioContext` that mixes the robot mic with `talkLink.audioSender.track` (polled every 250 ms, since `replaceTrack` fires no event); first supported of `video/mp4;codecs=avc1.42E01E,mp4a.40.2`, `video/mp4;codecs=avc1,mp4a`, `video/mp4;codecs=avc1,opus`, `video/webm;codecs=vp8,opus`, `video/webm`; `videoKeyFrameIntervalDuration` 1000 ms; 1 s chunks; stops and saves after 15 s with the video down or when `remoteStream` is replaced; *REC mm:ss · MB* badge and **⏺ Record / ⏹ Stop recording** in `VideoSurface` |
| Dashboard `lib/recordingStore.ts` | IndexedDB `robot-recordings` (`meta` keyed by id, `chunks` keyed `[id, seq]`); each chunk appended as it arrives; a finished recording is kept and listed (*Recordings on this computer*) until deleted; an unfinished one left by a crash is listed as such |
| Dashboard `lib/fixDuration.ts` | `withDuration()` writes the length into the saved file's header: MP4 `mvhd`/`tkhd` durations plus an `mvex/mehd` box, the length read from the first and last complete `moof` (`tfdt` + `trun` sample durations; a final fragment whose `mdat` is cut off is not counted); WebM a `Duration` element in `Info` from the recording time; any file it doesn't recognise is returned unchanged |
| Dashboard `lib/download.ts` | `download()` helper shared by victim snapshots and recordings |
| `scripts/copy-mediapipe.mjs` | `predev` / `prebuild` step that copies MediaPipe's WASM runtime into `public/mediapipe/wasm`, so no CDN is needed in the field |

***Table A.12 — Implementation by Component***

Six decisions shape the feature.

**Inference runs on the operator's laptop, not the Pi.** P2 already uses about 63 % of one core for one media session (paper Section 5.5), so there is no room for a detector on the Pi without hurting video. The laptop has the decoded frames anyway. The cost is that the detector shares the browser's main thread with the drive and stop buttons, so the hook times every inference, waits at least twice the last inference time before the next one, and turns itself off with a message if five frames average more than 150 ms. The controls must stay responsive; the AI is the part that gives way.

**CPU delegate only.** In headless Chromium on the Pi the GPU delegate loaded without error but returned no detections on two photos of a person, where the CPU delegate scored 0.95 and 0.98 — so the AI showed "on" and never drew a box. Empty results never throw, so a GPU-first fallback could not catch it. That test ran on a software renderer and was not repeated on a laptop's real GPU. WebGL is still required (MediaPipe uses it even with the CPU delegate), and its absence is reported before the model loads.

**The call-out is speech, not a new path.** Putting the decoded clip on the existing talk sender means P2, the floor and the Robot Screen need no change, and the call-out works without HTTPS because it never opens the laptop mic. Push-to-talk and the call-out exclude each other.

**The robot keeps the record; the laptop keeps the picture.** The mark (note, P1's own GPS and servo angles, AI score) lives on the robot so it survives a reload or a laptop crash and stays with the mission logs, and every dashboard sees it. P1 never takes position or angles from the browser. The snapshot, an image of an identifiable person, is never sent to the robot: it stays in the browser that took it and in its Downloads folder. Automatic downloads alone proved unreliable in the operator's real Chrome, hence the IndexedDB copy and the manual links.

**Recording happens where the media already is.** The browser already holds the decoded robot video and audio and the operator's outgoing audio, so recording there costs the Pi nothing and keeps footage of victims off the robot, as with snapshots. Mixing from the talk sender, rather than from the laptop mic, records what the robot actually played, including the call-out. Chunks go to IndexedDB every second so a crash keeps the recording, and finished files stay there until deleted for the same reason as snapshots: a held-back download must not lose them. A short Wi-Fi drop used to end the recording at once (found in testing, TEST_REPORT Issue 6); it now waits 15 s. MP4 (H.264) is preferred over WebM because it plays on almost any device, but Chrome's MP4 writer emits data only at key frames, which from steady camera video can be the whole recording; a key frame every second keeps the chunks, and so crash recovery, at about a second (TEST_REPORT Issue 9). Neither format carries a usable length as recorded, so it is written into the header on save.

**The size limit comes before everything else.** `read_body_limited()` refuses an oversized body on its `Content-Length`, or while streaming one with no or a false length, before the key check and before JSON parsing, because a multi-megabyte parse would stall P1's event loop — telemetry and the heartbeat path with it — for every dashboard.

Constraints that remain: detection accuracy on disaster-like scenes has not been measured; the 10 dB reply threshold is a first guess; the call-out clip must be recorded and installed by the team (`dashboard/public/audio/callout-en.mp3`) and is not in the repository; snapshots and recordings exist only on the device that made them; and recording completeness and its load on the operator's laptop have not been measured.

---

*This document describes the system as implemented in `robot/` as of the current build. Where it diverges from the methodology chapters, the code's behaviour is authoritative and the divergence is noted in the relevant section.*
