# **Software Architecture — Autonomous Rescue Robot System**

**Document status:** Architecture of the system *as implemented*.
**Scope:** The complete software stack in `robot/` — Arduino UNO firmware, the Raspberry Pi 4 three-process edge stack, the IEEE 802.11s mesh fabric, and the React operator dashboard.
**Relationship to the methodology:** The methodology chapters (Sections 8.1–8.15 and the consolidated Sections 1–40) specify the system *as designed*. This document describes the system *as built*, and is numbered independently (A.1–A.10) so that it stands alongside those chapters without renumbering them. Where the implementation resolved a contradiction between the two source documents, or departed from the original design intent, this document states the behaviour of the code and records the divergence explicitly. Every architectural claim is traceable either to a methodology section or to a specific source file.

---

## **A.1  Architectural Overview**

The rescue robot is a teleoperated ground vehicle intended for search-and-rescue reconnaissance in environments an operator cannot safely enter. Its software is distributed across four physical tiers connected by three distinct transports: an Arduino UNO executing the real-time control loop, a Raspberry Pi 4 running three cooperating Python processes, a three-node IEEE 802.11s wireless mesh extending radio range into the structure, and a React single-page application on the operator's laptop. The vehicle carries no autonomy in the navigational sense; every motion originates as an operator intent, and the entire architecture exists to carry that intent to the motors quickly and to carry sensory evidence back, while guaranteeing that the vehicle stops safely when any part of that path fails.

The organising principle of the architecture — the single idea from which most of its structure follows — is that **each tier is an independent failure domain, and safety authority descends to the lowest tier that can still act when the tiers above it are gone.** The dashboard can crash, the operator's laptop can lose radio contact, the mesh can partition, and the Raspberry Pi can lock up or be killed by the kernel, and in every one of those cases the Arduino still stops the motors within two seconds because its dead-man timer is evaluated unconditionally in its own main loop and depends on nothing outside the board. This is not defence-in-depth applied decoratively; it is the reason the system is decomposed the way it is. A monolithic design in which the Pi drove the motor pins directly would place the vehicle's safety behaviour behind a general-purpose preemptive kernel, a Python interpreter, and a scheduler — none of which can offer a bounded guarantee that a stop instruction executes.

The second organising principle is that **the wire protocol is the architecture's only true coupling.** The four tiers share no code and no runtime. What they share is a set of constants and message schemas defined canonically in `pi/common/protocol.py` and hand-mirrored into `arduino/protocol.h` and `dashboard/src/lib/protocol.ts`. Each of the three files names the other two in its header docstring. Because the coupling is narrow and explicit, each tier is independently testable, independently deployable, and — as Section A.10 describes — independently replaceable by a simulator.

```
  System Tier Decomposition and Failure Domains:
  ---------------------------------------------------------------

  TIER 4  OPERATOR LAPTOP                    (192.168.10.50)
          React 19 + TypeScript dashboard, browser-hosted
          Failure => Pi keeps logging; Arduino stops in <=2s
                 |
                 |  WebSocket :8080  (control + telemetry)
                 |  WebRTC    :8443  (video + audio)
                 v
  TIER 3  IEEE 802.11s MESH FABRIC           (192.168.10.0/24)
          3 x OpenWrt nodes, WPA3-SAE, mesh_id=robot-mesh
          Failure => mission state degrades; Arduino stops in <=2s
                 |
                 v
  TIER 2  RASPBERRY PI 4 EDGE STACK          (192.168.10.10)
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
| Test suite | `pi/tests/` | 456 | 56 tests over protocol, safety, and buffer logic |
| P2 media server | `pi/p2_media/` | 378 | WebRTC negotiation, camera and microphone tracks |
| P3 watchdog | `pi/p3_watchdog/` | 271 | Process supervision, health checking, restart policy |

***Table A.1 — Implementation Scale by Architectural Layer***

The firmware is compile-verified with `arduino-cli` 1.5.1 against `arduino:avr:uno`, consuming 8,204 bytes of program storage (25% of 32,256) and 377 bytes of SRAM (18% of 2,048, leaving 1,671 bytes for locals). These figures matter architecturally: they are the evidence that the safety-critical tier fits comfortably within an 8-bit microcontroller's resources with substantial headroom, which is what permits the dead-man check to run unconditionally on every loop iteration without contention.

---

## **A.2  Architectural Drivers and Constraints**

An architecture is best understood through the forces that shaped it. Six drivers account for essentially every significant structural decision in this system, and each is traceable to a concrete mechanism in the code. Presenting them first makes the remainder of the document legible: nothing in the component decomposition is arbitrary, and each unusual choice — the cooperative scheduler, the triple-mirrored protocol, the watchdog-spawns-children topology — is a direct response to one of these forces.

**Driver 1 — A stop command must execute within a bounded time, on hardware that cannot be trusted to be responsive.** This is the dominant safety requirement and it produces the dead-man timer in `robot_state.cpp`, the Category 1 unconditional scheduler slot in `arduino.ino`, and the decision to place motor authority on the Arduino rather than the Pi. The timer is a `millis()` comparison rather than a timer interrupt because Timer1 is claimed by the Servo library; the arithmetic uses unsigned subtraction so it remains correct across the approximately 49-day `millis()` rollover.

**Driver 2 — The radio link is unreliable by nature and will partition mid-mission.** A multi-hop 2.4 GHz mesh inside a damaged structure will drop frames, and the operator may walk out of range of the nearest relay. This produces the 300-entry ring buffer providing 60 seconds of telemetry history, the `resume_from` replay protocol, the exponential-backoff reconnection in `useControlSocket.ts`, and the four-state mission machine that degrades the interface rather than freezing it.

**Driver 3 — The compute tier is a general-purpose Linux system and will occasionally fail.** Python processes leak, deadlock on blocking device reads, and are killed by the OOM killer. This produces P3, the two-level liveness model (OS-level `poll()` for crashes plus HTTP `/health` for wedged-but-alive processes), and the exit-code contract by which P1 and P2 tell the supervisor *why* they died so that a misconfiguration does not become a restart loop.

**Driver 4 — Exactly one process may write to the Arduino.** Two writers interleaving bytes on a UART would produce commands neither of them sent. This is Invariant VI in the methodology, and it is enforced twice independently: an advisory `flock` on `/run/robot/p1.lock` via `ProcessLock`, and `O_EXCL` on the serial device through pyserial's `exclusive=True`.

**Driver 5 — The system must be developable and testable without hardware.** A capstone project cannot depend on continuous access to an assembled robot. This produces `mock_hardware.py`, which is architecturally significant precisely because it is not a stub: `MockArduino` reimplements the firmware's four-stage validation, its dead-man semantics, and its 200 ms telemetry cadence faithfully enough that P1 cannot distinguish it from a real board across the serial boundary.

**Driver 6 — One operator, one vehicle, no ambiguity about who is driving.** Multiple dashboards may observe a mission, but a second controller sending contradictory motion commands would be actively dangerous. This produces the single-controller slot in `WebSocketHub.claim_role()`, where the first client to request the controller role holds it until disconnect and all others are silently downgraded to observers.

| **Driver** | **Structural Consequence** | **Implementing Mechanism** |
| --- | --- | --- |
| Bounded stop latency | Motor authority resides on the MCU | `stateCheckDeadman()`, Category 1 loop slot |
| Unreliable radio | History buffering and replay | `RingBuffer`, `resume_from`, mission states |
| Fallible compute tier | External supervision with cause discrimination | `SupervisedProcess`, exit-code contract |
| Single-writer UART | Dual-mechanism exclusion | `ProcessLock` + `exclusive=True` |
| Hardware-free development | Protocol reimplementation, not stubbing | `MockArduino`, `MockGPS`, `MockSerial` |
| Single-operator safety | Explicit role arbitration | `WebSocketHub.claim_role()` |

***Table A.2 — Architectural Drivers and Their Structural Consequences***

Two constraints bound these drivers. The Arduino UNO offers 32 KB of flash, 2 KB of SRAM, and no operating system, which rules out threading, dynamic allocation, and any library that assumes a heap; the firmware is consequently written against a fixed set of module-local static variables. The 802.11s mesh is deployed on unlicensed 2.4 GHz spectrum shared with every other radio in the environment, which places a hard ceiling on video bitrate — hence the 640×480 at 10 fps, 500 kbps budget in `P2Config`.

---

## **A.3  Context View**

The system boundary encloses four software tiers and the physical vehicle. Outside it sit three external entities: the human operator, who supplies all navigational intent and interprets all sensory evidence; the disaster environment, which the vehicle senses but does not model; and the OpenStreetMap tile service, which supplies map imagery to the dashboard and is the only external network dependency in the entire architecture — and one that is not on any mission-critical path, since the loss of map tiles degrades the map panel to a blank canvas with a live GPS polyline still drawn over it.

There is no cloud tier in the deployed configuration. The methodology defines five operational modes; the implementation targets **Mode 2, Local Mesh Only**, per Section 8.11.6, and `ENABLE_OVERLAY=0` in `deploy/etc-robot/p3.env` disables the internet overlay by default. This is a deliberate architectural position: a rescue deployment cannot assume internet connectivity, so the primary mode assumes none, and everything required to fly a mission is present on the local mesh. The ICE configuration endpoint reflects this — `GET /api/ice-config` returns a STUN server on the mesh gateway and `turn: null`, because in a single-subnet local mesh there is no NAT to traverse and therefore no TURN relay to fund.

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
                                         temperature, gas, motion,
                                         obstacles, terrain, GPS sky

  Mission-path transports:  WebSocket :8080  |  WebRTC :8443
  External dependencies:    OSM tiles only (non-critical)
```
***Figure A.3 — System Context, External Actors, and the Mission-Path Boundary***

Two transports cross the system boundary during a mission, and the separation between them is architecturally deliberate. Control and telemetry travel over a single persistent WebSocket to P1 on port 8080; video and audio travel over a WebRTC peer connection to P2 on port 8443. They are carried by different protocols, terminate in different processes, and fail independently. A camera failure or a collapse of the video path leaves the control channel fully operational — the mission continues in `DRIVING_LIMITED`, where the operator drives on sensor telemetry alone. This independence is the reason P2 exists as a separate process rather than as a module inside P1.

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
| Mesh fabric | OpenWrt / 802.11s | 192.168.10.0/24 | Network transport | Manual (physical nodes) |

***Table A.4 — Container Inventory, Failure Domains, and Restart Authority***

The most consequential structural decision visible in this table is that **P1 and P2 are not systemd units.** Only `robot-watchdog.service` is registered with the init system, and it launches P3, which in turn spawns P1 and P2 as child processes. The alternative — three systemd units — was rejected because systemd's restart policy can observe only process exit, whereas the failure mode that most threatens this system is a process that remains alive while wedged on a blocking serial read. P3 detects that condition by polling `GET /health` and killing a child that misses three consecutive checks. The unit file's `KillMode=control-group` ensures the entire process group terminates together, and `After=network.target dev-ttyUSB0.device` prevents P1's handshake from racing udev's creation of the device node.

```
  Container View — Ports, Devices, and Supervision:
  ---------------------------------------------------------------

  OPERATOR LAPTOP
  +--------------------------------------------------------------+
  |  Dashboard (React 19 + TS + Vite + Tailwind + Leaflet)        |
  |  useControlSocket() ------> ws://192.168.10.10:8080/control/ws|
  |  useWebrtcVideo()   ------> POST :8443/webrtc/offer           |
  +--------------------------------------------------------------+
              |                              |
              |   802.11s mesh: .1 gateway / .2 relay+AP / .3 relay
              v                              v
  RASPBERRY PI 4  (192.168.10.10)
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

A second decision worth surfacing is the asymmetry between P1 and P2 regarding hardware locking. P1 holds an exclusive lock because the Arduino tolerates exactly one writer. P2 holds no lock at all: the camera and microphone are opened per session, and multiple simultaneous viewers are explicitly permitted, each receiving its own `RTCPeerConnection` and encoder. The architecture allows several observers to watch a mission while exactly one operator drives it.

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
  sensorsPollSonar(now);   sensorsPollIr(now);
  sensorsPollGas(now);     sensorsPollDht(now);
  telemetryPoll(now);      pollStatusLed(now);
}
```

The separation exists so that a slow sensor cannot delay a stop. The only blocking call anywhere in the firmware is the bit-banged DHT11 read, at roughly 25 milliseconds, and it is precisely because that call blocks that its cadence is set to 2,000 milliseconds — it bounds the worst-case latency of dead-man detection, and that bound must remain far below the 2,000 ms dead-man window itself.

Motors and servos both use a **desired-state / apply split**. `motorsForward()` and its siblings do not touch pins; they update module-local variables, and `motorsApply()` in Category 1 drives the hardware each iteration. Servos extend this with dirty flags so that `servosApply()` writes only on change. The benefit is that command handling and hardware actuation are decoupled, so a command arriving at any point in the loop takes effect at a single well-defined place.

The **state machine** has three states — `ARMED` (1), `DRIVING` (2), `STOPPED` (3). `ARMED → DRIVING` occurs when a motion opcode executes; `DRIVING → ARMED` on an explicit stop or dead-man expiry. `STOPPED` is reached only through `statePanic()` and is **latched until board reset**, because a state-invariant violation means the firmware's own assumptions have been falsified and no recovery path can be trusted. `checkInvariants()` enforces this each iteration, panicking if the state falls outside its legal range or a servo angle exceeds 180 degrees.

The **dead-man timer** is the system's most important safety mechanism. `stateInit()` deliberately sets `lastCommandTime = millis() - (DEADMAN_MS + 1)` and `deadmanTripped = true`, so a freshly reset board boots with the window already expired and never inherits a spurious armed state. Only the arming opcode set `{F, R, L, G, S, H}` refreshes the window; pan, tilt, and status queries do not, on the explicit reasoning that a camera movement is not evidence the drive link is alive.

**Four-stage command validation** filters every inbound line. Stage 1 enforces a length of 1–8 characters, emitting `ERR_LEN` and consuming through the delimiter so that the tail of an overflowed line cannot be reinterpreted as a command. Stage 2 checks the opcode whitelist, emitting `ERR_TOK`. Stage 3 parses and clamps the numeric argument to 0–180, emitting `WARN_CLAMP`; a non-numeric tail becomes zero rather than a rejection, under an explicit clamp-don't-discard policy. Stage 4 is the proximity gate: forward motion is suppressed when the sonar range is at or below 20 cm, emitting `ALERT_OBSTACLE`, while reverse and pivots remain available so the operator can always back away from an obstacle.

One detail in Stage 4 repays close attention, because it is the kind of correctness property that is easy to get wrong and hard to notice: **a suppressed forward command still re-arms the dead-man timer.** Without this, an operator holding forward against a wall would send commands that were all rejected, the dead-man window would expire, and the vehicle would report a link-loss fault when in fact the link was perfectly healthy and the operator was actively driving.

### **A.5.2  P1 Control Server — Serial Ownership and Telemetry Fan-Out**

P1 is the largest component and the system's centre of gravity. It exclusively owns the Arduino UART and the GPS receiver, validates and forwards operator commands, merges data from several sources into a single telemetry snapshot, broadcasts that snapshot every 200 milliseconds, maintains a replay buffer, and writes the mission log.

Its concurrency structure comprises three asyncio tasks and one thread. The task named `serial-reader` drains the UART, polling every 5 ms while data is flowing and every 20 ms when idle — a fraction of the 200 ms frame period, so that no frame is delayed by more than a fifth of its cadence. The task named `telemetry-broadcast` runs the 200 ms cycle. Uvicorn's server task handles HTTP and WebSocket connections. The GPS reader deliberately runs on a **daemon thread** rather than a task, because pyserial reads block and a 1 Hz fix rate has no reason to share an event loop with a 5 Hz broadcast cycle.

The broadcast loop uses **absolute scheduling** — `next_tick += period` rather than sleeping a fixed interval — so that a slow iteration is absorbed rather than accumulating drift across a long mission. Its body is wrapped so that any exception is logged as `BROADCAST_FAIL` without terminating the loop, on the principle that the cadence must not stop.

| **Module** | **Principal Type** | **Responsibility** |
| --- | --- | --- |
| `serial_bridge.py` | `SerialBridge` | Sole UART owner; handshake, frame ingest, command egress |
| `websocket_hub.py` | `WebSocketHub`, `Client` | Client registry, role arbitration, concurrent broadcast |
| `gps_reader.py` | `GPSReader` | Threaded NMEA parsing, track accumulation, GeoJSON export |
| `ring_buffer.py` | `RingBuffer` | 300-entry history; `since()` and `gap_ms()` for replay |
| `safety.py` | `CommandValidator` | Server-side clamp, proximity gate, sequence monotonicity |
| `telemetry_log.py` | `TelemetryLog` | 1 Hz, 21-column CSV with packed alert bitfield |
| `lockfile.py` | `ProcessLock` | Advisory `flock` enforcing the single-writer invariant |

***Table A.5.2 — P1 Module Responsibilities***

The **startup handshake** is a fixed sequence whose ordering encodes hard-won operational knowledge. The port is opened with `exclusive=True`, which sets `O_EXCL` so the kernel rejects a second opener. Opening the port toggles DTR and resets the Arduino, so P1 then waits 2.0 seconds for the board to boot. It flushes both buffers, sends three `S` stop commands at 200 ms intervals — because if the board survived a previous P1 crash while driving, this halts it before anything slower is attempted — then sends `?` and awaits `READY` for up to 5 seconds, accepting either the token or any parseable telemetry frame as evidence of a live board. Handshake failure exits with code 2, which P3 interprets as a crash.

`ProcessLock` merits a note on its choice of location. The lock file lives at `/run/robot/p1.lock`, on tmpfs, which yields two properties: the file cannot survive a reboot and become a stale lock, and the kernel releases the lock automatically when the holder exits — including on `SIGKILL`, where no cleanup handler would run.

The WebSocket endpoint primes each newly registered client with an immediate snapshot so the first render is not delayed by up to a full broadcast period. On disconnect it unregisters the client, resets its sequence state, and — if the departing client held the controller role — sends an immediate stop to the Arduino. The dead-man timer would catch this within two seconds regardless; the explicit stop is simply faster, and the two mechanisms are intentionally redundant.

### **A.5.3  P2 Media Server — Single-Shot Negotiation and Graceful Capture Fallback**

P2 is deliberately the smallest and simplest server component, because a media path that fails should degrade the mission rather than end it. It exposes exactly two endpoints: `POST /webrtc/offer`, which accepts an SDP offer and returns an SDP answer in the same HTTP response, and `GET /health` for the watchdog.

The signaling design is minimal by intent. There is no separate signaling channel and no trickle-ICE round trip; the dashboard POSTs its offer and receives the answer synchronously. This is sound specifically because of the deployment topology: on a single local mesh subnet with no NAT between the peers, candidate gathering is trivial and the elaborate machinery WebRTC normally requires for internet traversal would add latency and failure modes for no benefit.

The track factory implements a fallback whose architectural value is that it makes two different situations behave identically. `open_camera_track()` and `open_mic_track()` are each wrapped so that *any* capture failure logs the fault and substitutes `SyntheticVideoTrack` or `SilentAudioTrack`. Consequently mock mode on a developer laptop and a real Pi whose camera has been knocked loose in the field follow exactly the same code path — the mission continues with a synthetic stream, and the operator sees plainly that video is not live. `SyntheticVideoTrack` renders a sweeping bar, a slow hue cycle, and a font-free clock encoded as a bar whose width grows with elapsed seconds, deliberately avoiding a fontconfig dependency in the media path.

### **A.5.4  P3 Watchdog — Supervision with Cause Discrimination**

P3 supervises P1 and P2 through a four-state machine per child: `SPAWNING`, `MONITORING`, `COOLDOWN`, `STOPPED`. The nominal cycle is spawn, monitor, detect failure, cool down for 10 seconds, spawn again.

Liveness is assessed at two levels because the two failure modes are genuinely different. An OS-level `poll()` every second catches a process that has exited. An HTTP `GET /health` every 10 seconds, with a 5-second timeout and a limit of three consecutive misses, catches a process that is alive but wedged — deadlocked on a blocking serial read, for instance — which `poll()` alone would never detect.

The feature that most distinguishes this supervisor from a naive restart loop is **exit-code discrimination**. P1 publishes a documented contract: 0 means a clean exit or a lock held by a healthy peer, 1 a lock error, 2 a failed Arduino handshake, and 3 an invalid configuration. P3 reads these and responds differently. Exit code 3 is logged as a configuration fault rather than a crash and does not increment the restart counter, because respawning a misconfigured process at speed produces a log flood and no recovery. Exit code 0 is logged distinctly as a lock-held condition, since it most often means the supervisor's own previous instance still owns the hardware during a restart race — not a fault at all.

`adopt(pid)` completes the picture. If P3 itself restarts after a software update, P1 and P2 may still be running. Killing and respawning them would drop the Arduino connection for no reason, so P3 instead attaches to the surviving orphans by verifying them through their health endpoints.

### **A.5.5  Operator Dashboard — Hook-Owned State and Two Independent Transports**

The dashboard is a React 19 single-page application in TypeScript, built by Vite, styled with Tailwind, and rendering GPS data through Leaflet. Ten presentational components are arranged in a three-column grid — controls at 22%, video and map at 52%, telemetry and alerts at 26%.

**A documented divergence from the original design.** The original methodology specified "no Redux — context providers per state slice," and `dashboard/src/context/` exists in the tree. It is empty. The implemented architecture uses **no context providers at all**: all shared state lives in a single `useControlSocket()` hook invoked once in `App.tsx` and threaded to children as explicit props. For a dashboard of this size the simpler structure is defensible — every component's data dependencies are visible in its props, and there is no indirection between the socket and the render. The empty directory should be removed to prevent it from implying a structure that does not exist.

`useControlSocket()` owns the entire control path. State that drives rendering is held in `useState`; values that must persist across renders without triggering them — the socket, the command sequence counter, the last server timestamp, the backoff interval, and timer handles — are held in `useRef`. On connection it sends `hello` to claim the controller role, then `resume_from` with its last-seen timestamp if this is a reconnection. Reconnection backs off exponentially from 1 second to a 30-second ceiling. An idle heartbeat every 500 ms keeps the Arduino's dead-man armed while the operator is not driving.

The hook contains a guard worth documenting because it addresses a genuinely subtle failure. Under React StrictMode, effects are double-invoked in development. Without protection, the abandoned first socket would open moments later, claim the single controller slot, and permanently strand the live hook as an observer — the dashboard would appear connected but every command would be rejected. The hook therefore closes any prior socket before connecting and uses an `isCurrent()` closure to ignore events from superseded sockets.

`useWebrtcVideo()` is entirely separate, self-contained within `VideoSurface`, and notably has **no reconnection logic** — a single negotiation attempt, after which failure is reported and the video panel shows its error state. This asymmetry with the control socket is correct by the architecture's own logic: control must be restored automatically because the vehicle is unsafe without it, whereas video is a convenience whose loss degrades the mission to `DRIVING_LIMITED` and is properly surfaced to the operator as a decision rather than papered over by silent retries.

### **A.5.6  Common Layer — The Contract and Its Enforcement**

`pi/common/` holds what all Pi processes share. `config.py` defines four frozen dataclasses — `Paths`, `P1Config`, `P2Config`, `P3Config` — each constructed from environment variables with defaults. `_default_root()` returns `/` when `/opt/robot` exists and `./var` otherwise, which is the single mechanism that lets the identical code run as a Pi service and as a developer process without root.

`logging_setup.py` implements the methodology's event format, `[TS][PROC][LEVEL][EVENT_CODE][MSG]{k=v ...}`, with UTC timestamps at millisecond precision. Each record is written in a single append-mode call so that concurrent processes never interleave partial lines — a property that matters because P1, P2, and P3 all log independently during a mission.

`mock_hardware.py` is discussed in full in Section A.10, as its significance is architectural rather than merely convenient.

---

## **A.6  Data Architecture and the Protocol Contract**

This section is load-bearing: the protocol contract is the only real coupling between the four tiers, and understanding it is understanding the system's data architecture.

The contract is defined canonically in `pi/common/protocol.py` and hand-mirrored in `arduino/protocol.h` and `dashboard/src/lib/protocol.ts`. Each file names the other two in its header. The Python module is the authoritative superset, carrying not only the constants but `TelemetrySnapshot`, `ValidationResult`, `encode_command()`, `parse_telemetry_line()`, `format_telemetry_line()`, `derive_mission_state()`, and `compute_alert_flags()`.

Manual mirroring is a real risk and should be named as such: a constant changed in one file and not the others produces a silent protocol mismatch that no compiler will catch. The mitigation is partly procedural — the docstrings state the obligation explicitly — and partly structural, in that `derive_mission_state()` is implemented twice against the same first-match rules and the test suite pins the Python side. A stronger design would generate all three files from one source; that is recorded as future work in Section A.10 rather than claimed as present.

**Upstream, Arduino to P1**, telemetry is an 11-field positional CSV, at most 80 characters, emitted every 200 ms:

```
temperature_c, humidity_pct, gas_ppm, motion, range_cm, ir_left,
ir_right, pan_angle, tilt_angle, fw_state, uptime_ms
```

Field order is load-bearing — parsing is by index, not by name — which is the correct trade on a link where every byte costs transmission time on an 8-bit MCU. `parse_telemetry_line()` validates in three passes: field count, per-field type coercion, and per-field plausibility range. Any failure at any stage discards the entire frame.

**The discard-don't-retransmit rule is the single most characteristic decision in the data architecture.** There is no retransmission, no sequence numbering, and no acknowledgement on the UART link. A corrupted frame is dropped and nothing is requested. This is correct rather than lazy: the next frame arrives within 200 ms, so the cost of a discard is one dropped sample of a continuously-sampled signal, whereas a retransmission protocol would add buffering, state, and latency to a safety-critical path in exchange for data that will be superseded before it could be re-delivered. The same reasoning drives the PIR motion latch to be edge-reported and cleared after each transmission.

**Downstream, dashboard to P1 to Arduino**, commands are single-character opcodes with optional numeric arguments — `F120\n` is forward at PWM 120. The dashboard speaks JSON WebSocket messages; P1 validates and lowers them to the wire grammar. Six client message types (`hello`, `motor`, `servo`, `heartbeat`, `stop_all`, `resume_from`) and four server types (`telemetry`, `recovery_batch`, `ack`, `error`) constitute the entire application protocol.

**P1 outward to the dashboard**, the unit of exchange is the 22-key `TelemetrySnapshot`: the 11 Arduino fields, plus GPS position and fix quality merged from the reader thread, plus server metadata — sequence number, server timestamp, serial health, client count, and TURN status. `build_snapshot()` re-asserts the P1-owned fields *last*, after merging, so that a malformed or hostile frame can never overwrite the server's own view of its health.

| **Store** | **Medium** | **Retention** | **Purpose** |
| --- | --- | --- | --- |
| Ring buffer | Memory, 300 entries | 60 s at 200 ms | `resume_from` replay after reconnect |
| `telemetry.log` | Disk CSV, 21 columns | Daily rotation, 7 kept | Post-mission analysis at 1 Hz |
| `p{1,2,3}_events.log` | Disk, structured text | Weekly rotation, 8 kept | Fault diagnosis and audit |
| GeoJSON track | Disk, per session | 90 days (cron) | Mission path reconstruction |

***Table A.6 — Data Stores, Retention, and Purpose***

The two telemetry rates are deliberately decoupled. Broadcast runs at 200 ms because the operator needs a responsive interface; disk logging samples at 1 Hz because the full stream would consume roughly 3.2 MB per hour to record data whose post-mission value is trend-level. The ring buffer holds 60 seconds, which bounds the worst case for a reconnecting dashboard: 60 seconds of history against a P1 restart of approximately 8 seconds. When a client's `last_ts` predates the oldest buffered entry, `gap_ms()` reports the shortfall and the dashboard renders an explicit gap marker on the map rather than interpolating across data it never received.

`compute_alert_flags()` packs eight boolean conditions — temperature warn and critical, gas warn and critical, range warn and critical, motion, and GPS loss — into a single integer bitfield per log row, keeping the CSV compact while preserving the full alert history.

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

An operator keypress travels through two independent validators. The dashboard sends `{type:"motor", dir:"F", speed:120, seq:n}`. P1's `CommandValidator` clamps the speed to 0–180, applies the proximity gate against the most recent range reading, checks that the sequence number exceeds the last seen from that client, and encodes `F120\n`. The Arduino then re-validates through all four of its own stages before acting.

The redundancy is deliberate and the two validators serve different purposes. The Arduino enforces safety for its own sake and cannot be bypassed by any Pi-side defect. P1's copy rejects bad input before it consumes UART bandwidth and — equally important — returns a human-readable reason to the operator, which the Arduino's terse `ERR_TOK` cannot. Note that `stop_all` bypasses the sequence check entirely: a stop must never be dropped because a counter arrived out of order.

### **A.7.4  Reconnection and Replay**

On disconnect the dashboard begins backing off from 1 second toward a 30-second ceiling while its mission state falls to `STOP`. On reconnection it sends `hello` to reclaim the controller role, then `resume_from` with the last `server_ts` it saw. P1 answers with a `recovery_batch` drawn from the ring buffer. If the gap exceeds the buffer's 60-second span, `gap_ms()` reports the shortfall and the map renders a discontinuity marker — the operator is shown that data is missing rather than being presented with a smooth line the vehicle never travelled.

---

## **A.8  Safety and Fault-Tolerance Architecture**

Safety in this system is not a subsystem but a property distributed across every tier, and it is arranged so that mechanisms at each level are independent — no single defect disables more than one of them.

**Layered command validation.** Clamping and the obstacle gate exist at four levels: the dashboard's slider bounds, P1's `CommandValidator`, the Arduino's four-stage parser, and the mock emulator that mirrors the firmware. The dashboard's bounds are convenience; P1's are efficiency and operator feedback; the Arduino's are authoritative.

**Dual-mechanism dead-man.** The Arduino's 2,000 ms timer is the guarantee. P1's immediate stop on controller disconnect is the optimisation. Either alone is sufficient to halt the vehicle.

**Mission state as an operator-visible contract.** `derive_mission_state()` evaluates first-match rules: any of WebSocket down, serial down, or command acknowledgement older than 3,000 ms yields `STOP`; loss of video or mesh yields `DRIVING_LIMITED`; otherwise `DRIVING` when a command is active and `READY` when idle. Because it is a pure function of current inputs, the indicator can never disagree with the state it describes. It is computed identically on both sides of the link.

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
| Mesh partition | Telemetry gap, ack timeout | Mission state → `STOP` | Backoff reconnect + replay |
| Corrupt frame | Parse or range check | Frame discarded silently | Next frame within 200 ms |
| Obstacle ≤ 20 cm | Sonar, Category 2 poll | Forward suppressed; reverse allowed | Operator reverses |
| State invariant violated | `checkInvariants()` | Panic; motors stopped, latched | Board reset only |
| GPS loss | Fix flag, `gps_lost` bit | Position stale-flagged; drive unaffected | Automatic on reacquisition |

***Table A.8 — Failure Modes, Detection, Response, and Recovery***

Reading this table by recovery column reveals the architecture's intent clearly: nearly every fault recovers automatically, and the two that do not — configuration errors and panic latching — are precisely the two where automatic recovery would mask a condition a human must inspect.

---

## **A.9  Deployment View**

The Pi is provisioned by `deploy/install.sh`, an idempotent eight-stage script that may be re-run after a code update without disturbing operator-customised configuration. It installs system packages, creates the unprivileged `robot` user in the `dialout`, `video`, and `audio` groups, rsyncs the code to `/opt/robot`, builds a virtualenv, copies configuration templates **only where absent**, registers the systemd unit and logrotate policy, and finally prints the manual steps it cannot safely automate — enabling the GPS UART, verifying the serial device, and setting the static IP.

```
  /opt/robot/          pi/ (P1,P2,P3,common) | dashboard/dist | venv/
  /etc/robot/          p1.env p2.env p3.env thresholds.json mesh.conf
  /var/log/robot/      telemetry.log  p{1,2,3}_events.log  gps_track/
  /run/robot/          p1.lock (tmpfs — never survives reboot)

  systemd: robot-watchdog.service  --> P3 --> spawns P1 + P2

  Mesh (192.168.10.0/24, mesh_id=robot-mesh, WPA3-SAE, ch.6 HT20):
    .1  robot router   gateway; Ethernet to Pi; DHCP server
    .2  relay 1        mesh relay + operator AP (robot-mesh-ap)
    .3  relay 2        pure relay, extends range
    .10 Raspberry Pi   static
    .50-.99            operator DHCP pool
```
***Figure A.9 — Deployment Layout and Mesh Addressing***

Configuration is environment-file driven, with three files that map one-to-one onto the three processes. Alert thresholds live separately in `thresholds.json` so that they can be tuned in the field without touching process configuration; `load_thresholds()` merges the file over the built-in defaults and falls back silently to those defaults if the file is missing or malformed — a field-tuning error degrades to known-good behaviour rather than a failed start.

The mesh comprises three OpenWrt nodes on a single `/24`. The robot router at `.1` is the gateway, Ethernet-connected to the Pi and running DHCP. Relay 1 at `.2` both extends the mesh and hosts the operator access point. Relay 2 at `.3` is a pure relay for positions where direct radio range is insufficient. `mesh.conf` in `/etc/robot` is documentation only — no Pi process reads it; `MESH_GATEWAY` in `p3.env` is the value actually consumed.

Log rotation is tiered by write rate: `telemetry.log` daily at 50 MB retaining 7; event and fault logs weekly at 10 MB retaining 8; session logs monthly. All use `copytruncate` so running processes keep their open file handles. GPS tracks and CSV exports fall outside logrotate and are pruned by a documented `find -mtime +90 -delete` cron equivalent.

Two housekeeping defects are worth recording. The systemd unit advertises `Documentation=file:///opt/robot/docs`, and until this document was written that directory was empty. The logrotate policy also names `watchdog.log`, `fault.log`, and `session.log`, which no current code writes — the policy anticipates logs the implementation does not yet produce.

---

## **A.10  Quality Attributes and Architectural Decisions**

### **A.10.1  Quality Attributes**

**Safety** is the attribute to which all others are subordinated, and it is achieved by placing the guarantee at the lowest tier and making every higher-level mechanism redundant rather than necessary. The measurable claim is that the vehicle halts within 2 seconds of losing operator contact by any cause, including total failure of every tier above the Arduino.

**Availability** is pursued through supervision and graceful degradation rather than redundancy — there is no second Pi. P3 restores a crashed or wedged process within roughly 10 to 40 seconds, and during that window the vehicle is stopped but undamaged. Degradation is graded rather than binary: video loss, mesh loss, and GPS loss each reduce capability by a defined amount while keeping the mission alive.

**Latency** is budgeted at every hop: sensor to telemetry at most 200 ms, telemetry to render one broadcast period, keypress to motor a validation pass plus UART transit. The 200 ms cadence, the 5 ms serial poll, and the absolute-scheduled broadcast loop all exist to keep the operator's perception of the vehicle current.

**Testability** is achieved through the mock hardware layer, which decouples the entire stack from physical hardware. Fifty-six tests exercise the protocol parser, the validation pipeline, ring-buffer wraparound and replay, mission-state derivation, and the emulated dead-man — with boundary cases pinned deliberately: blocked at exactly 20 cm, permitted at 21 cm; `STOP` at 3,001 ms but not at exactly 3,000 ms.

**Modifiability** follows from the narrow protocol contract. A new sensor requires a coordinated change to three mirror files and nothing else. The corresponding weakness is that the mirroring is manual.

### **A.10.2  Decision Record**

The methodology's two source documents disagreed in several places. The implementation resolved each contradiction by choosing a default and making it configurable, summarised here.

| **Contradiction** | **Resolution** | **Configurable At** |
| --- | --- | --- |
| Serial device `ttyUSB0` vs `ttyAMA0` | `ttyUSB0` (Sections 8.7/8.8 authoritative) | `p1.env: SERIAL_PORT` |
| Router IP plan | Robot router `.1` as gateway (§8.14.5) | Mesh UCI scripts |
| Mesh ID naming | `robot-mesh` (matches the UCI snippet) | Mesh script variable |
| Dead-man: `millis()` vs Timer1 ISR | Software check — Timer1 belongs to Servo | `DEADMAN_MS` |
| IR sensors: boolean vs analog | Analog read plus threshold → boolean | Firmware threshold |
| Telemetry field count (12/22/26) | 22-key schema of §8.10.1.2 | `pi/common/protocol.py` |
| Operational mode count | Build Mode 2, Local Mesh Only (§8.11.6) | `p3.env: ENABLE_OVERLAY=0` |

***Table A.10 — Specification Contradictions and Their Resolutions***

Three further decisions are visible only in the code and are recorded here for the first time.

**Hook-owned state rather than context providers.** The plan specified context providers per state slice; the implementation uses a single hook with prop threading and leaves `src/context/` empty. For ten components the simpler structure is defensible and arguably preferable — data flow is explicit at every call site. The empty directory should be deleted.

**No reconnection on the video path.** The control socket reconnects indefinitely; the WebRTC path attempts negotiation once. This asymmetry is intentional: control is safety-critical and must self-heal, while video is a capability whose loss should be surfaced to the operator as a decision.

**Mock hardware as protocol reimplementation.** This is the most consequential decision not present in the original plan. `MockArduino` does not stub the firmware — it reimplements the four-stage validation, the dead-man semantics including the boot-expired initial state, and the 200 ms cadence faithfully enough that P1 cannot distinguish it across the serial boundary. Its simulated obstacle range even closes while driving forward so the 20 cm gate is reachable in a demonstration. The consequence is that the entire stack runs end-to-end on a laptop, the full test suite executes with no hardware attached, and the protocol has been exercised continuously throughout development rather than only at hardware bring-up. The cost is a second implementation of the firmware's semantics that must be kept in step — an obligation its docstring states explicitly.

### **A.10.3  Known Limitations**

Recorded plainly, as the architecture's own account of where it is incomplete:

1. **Protocol mirroring is manual.** Three files must change together with no compiler enforcement. Code generation from a single source would eliminate an entire class of silent defect.
2. **Test coverage is uneven.** The protocol, validator, ring buffer, and mission-state logic are well covered. `SerialBridge`, `WebSocketHub`, `GPSReader`, `TelemetryLog`, `ProcessLock`, and `SupervisedProcess` have no direct tests, and there is no JavaScript test runner configured — `package.json` provides only `oxlint`.
3. **No real-hardware bring-up has been performed.** The firmware compiles cleanly and the protocol is exercised end-to-end against the emulator, but no flash-and-drive test on the assembled vehicle has been carried out. This is the single largest outstanding validation gap.
4. **P3 is a single point of supervision failure.** If P3 dies, systemd restarts it and it adopts the surviving orphans — but during that window nothing is watching P1 and P2.
5. **No authentication on either transport.** Any host on the mesh may open a WebSocket and claim the controller role. Security rests entirely on WPA3-SAE at the link layer. For a closed operational mesh this is a defensible posture, but it should be stated rather than assumed.
6. **The logrotate policy names logs no code writes**, and the empty `src/context/` directory implies a structure that does not exist. Both are housekeeping defects that mislead a reader of the deployment configuration.

---

*This document describes the system as implemented in `robot/` as of the current build. Where it diverges from the methodology chapters, the code's behaviour is authoritative and the divergence is noted in the relevant section.*
