# Methodology Diagrams - Teleoperated Rescue Robot

Figures for the **Methodology** section of the research paper. Each figure is
written in Mermaid, so it renders directly on GitHub, in VS Code (Markdown
Preview Mermaid Support), Obsidian, Typora, or at <https://mermaid.live>
(paste the code there and export PNG/SVG for Word or LaTeX).

All values are taken from the project's firmware, Pi services and design
documents (`docs/CAPSTONE_METHODOLOGY_FINAL.md`).

| Figure | Suggested place in the methodology |
|---|---|
| 1. Research workflow | Start of methodology (research approach) |
| 2. Overall system architecture | System design / overview |
| 3. Hardware interconnection and power | Hardware design |
| 4. Pi software architecture (+ 4a dashboard) | Software design |
| 5. Command and telemetry sequence | Communication protocol |
| 6. Two-stage command validation | Safety design |
| 7. Firmware state machine | Embedded firmware design |
| 8. Firmware cooperative scheduler | Embedded firmware design |
| 9. Two-way media path | Video / audio communication |
| 10. Layered fault tolerance | Reliability and safety |
| 11. Testing methodology | Testing and evaluation |
| 12. Hardware diagram (+ detailed 12a, simplified 12b) | Hardware design |
| 13. Arduino UNO pin diagram | Hardware design / embedded controller |
| Tables 1-3. Pin map, Pi connections, components | Hardware design |
| Table 4. Software stack | Software design |
| 14-18. Photos and screenshots | Implementation / results |

---

## Figure 1 - Research and development workflow

```mermaid
flowchart LR
    A["1. Problem and requirements<br/>rescue scenario, teleoperation,<br/>video, two-way audio, sensing,<br/>safety, offline operation"]
    B["2. System design<br/>four-layer architecture,<br/>component selection,<br/>UART / WebSocket / WebRTC protocols"]
    C["3. Hardware and firmware<br/>4WD chassis, BTS7960 drivers,<br/>pan-tilt, sensors, power rails,<br/>Arduino UNO firmware"]
    D["4. Edge and operator software<br/>Pi: P1 control, P2 media, P3 watchdog,<br/>React dashboard, robot screen"]
    E["5. Integration<br/>serial and GPS bring-up,<br/>Wi-Fi deployment, systemd service"]
    F["6. Testing and evaluation<br/>unit, hardware, network,<br/>failure-recovery, field test"]
    A --> B --> C --> D --> E --> F
    F -. "issues found -> redesign" .-> B
```

*Figure 1. Iterative research and development workflow followed in this work.*

---

## Figure 2 - Overall system architecture

```mermaid
flowchart TB
    OP["Operator laptop<br/>Web browser - React dashboard<br/>drive | pan/tilt | telemetry | map | talk"]
    RT["Wi-Fi router<br/>local network, WPA2/WPA3<br/>no internet required"]
    OP <-->|Wi-Fi| RT

    subgraph PI["Raspberry Pi 4 - Debian 12, Python 3.11"]
        P3["P3 Watchdog<br/>systemd service<br/>supervises P1 and P2"]
        P1["P1 Control server :8080<br/>WebSocket hub, safety checks,<br/>serial bridge, GPS reader,<br/>telemetry buffer, serves dashboard"]
        P2["P2 Media server :8443<br/>aiortc WebRTC video/audio,<br/>talkback relay"]
        KS["Robot Screen kiosk<br/>Chromium"]
        P3 -. "spawn + /health" .-> P1
        P3 -. "spawn + /health" .-> P2
        P2 --> KS
    end

    RT <-->|"WebSocket: commands / telemetry"| P1
    RT <-->|"WebRTC: video, audio, messages"| P2

    GPS["NEO-6M GPS"] -->|"UART 9600 baud"| P1
    CAM["USB camera<br/>640x480 @ 10 fps"] --> P2
    MIC["USB microphone"] --> P2
    KS --> DSP["7-inch HDMI display<br/>victim-facing"]
    KS --> SPK["Speaker<br/>3.5 mm jack"]

    P1 <-->|"USB serial 115200 baud"| ARD["Arduino UNO ATmega328P<br/>command parser, scheduler,<br/>2 s dead-man, gas panic"]
    ARD -->|PWM| MD["2x BTS7960 drivers<br/>4 DC gear motors"]
    ARD -->|"servo PWM"| SV["Pan-tilt servos<br/>camera 0-180 deg"]
    SN["Sensors<br/>DHT11, MQ-136, HC-SR04"] --> ARD
```

*Figure 2. Overall architecture: operator station, local Wi-Fi network, Raspberry Pi edge computer and Arduino real-time controller.*

---

## Figure 3 - Hardware interconnection and power distribution

```mermaid
flowchart LR
    subgraph PWR["Power system"]
        BAT["4S Li-ion battery<br/>14.8 V nominal, 16.8 V full"]
        BMS["4S 40 A BMS"]
        B5["Buck converter<br/>5 V rail"]
        B8["Buck converter<br/>8 V"]
        PB["USB power bank<br/>separate Pi supply"]
        BAT --> BMS
        BMS --> B5
        BMS --> B8
    end

    BMS ==>|"14.8 V"| DL["BTS7960 #1<br/>left side"]
    BMS ==>|"14.8 V"| DR["BTS7960 #2<br/>right side"]
    DL --> ML["Left motors<br/>front-left + rear-left"]
    DR --> MR["Right motors<br/>front-right + rear-right"]

    B8 ==>|"barrel jack"| ARD["Arduino UNO"]
    B5 ==> SV["Pan / tilt servos"]
    ARD ==>|"5 V"| SEN["DHT11 | MQ-136 | HC-SR04"]
    PB ==>|"5 V USB-C"| PI["Raspberry Pi 4"]

    ARD -->|"D5 RPWM, D6 LPWM"| DL
    ARD -->|"D9 RPWM, D10 LPWM"| DR
    ARD -->|"D4 common enable"| DL
    ARD -->|"D4 common enable"| DR
    ARD -->|"D11 pan, D3 tilt"| SV
    SEN -->|"A2 DHT11, A3 MQ-136,<br/>D7/D8 HC-SR04"| ARD

    PI <-->|"USB serial"| ARD
    GPS["NEO-6M GPS"] -->|"GPIO14/15 UART"| PI
    PI <-->|"USB"| CM["USB camera + microphone"]
    PI -->|"micro-HDMI / 3.5 mm"| OUT["7-inch display + speaker"]
```

*Figure 3. Hardware interconnection. Thick arrows are power, thin arrows are signals. The Pi has its own power bank so motor current surges cannot brown it out.*

---

## Figure 4 - Raspberry Pi software architecture and process supervision

```mermaid
flowchart TB
    SD["systemd<br/>robot-watchdog.service<br/>Restart=on-failure, 5 s"]
    P3["P3 Watchdog<br/>crash check: poll every 1 s<br/>hang check: GET /health every 10 s<br/>3 misses -> kill, 10 s cooldown -> respawn"]
    SD -->|starts| P3

    subgraph P1["P1 - Control server (FastAPI, TCP 8080)"]
        direction TB
        WS["WebSocket hub<br/>controller / observer roles"]
        SF["Safety validator<br/>type, clamp, sequence"]
        SB["Serial bridge<br/>/dev/ttyACM0, single-instance lock"]
        GR["GPS reader<br/>NMEA RMC/GGA"]
        RB["Ring buffer 300 snapshots (60 s)<br/>telemetry CSV log 1 Hz"]
        ST["Dashboard files + offline map<br/>GET /health"]
        WS --> SF --> SB
        SB --> RB
        GR --> RB
        RB --> WS
    end

    subgraph P2["P2 - Media server (aiortc, TCP 8443 + UDP)"]
        direction TB
        OS["Operator signalling<br/>POST /webrtc/offer"]
        SC["Shared capture<br/>one camera, one mic"]
        TR["Video / audio tracks<br/>640x480 @ 10 fps, Opus 32 kbps"]
        SH["ScreenHub talkback relay"]
        RS["Robot Screen signalling<br/>localhost only"]
        H2["GET /health"]
        SC --> TR --> OS
        OS --> SH --> RS
    end

    P3 -. "spawn + monitor" .-> P1
    P3 -. "spawn + monitor" .-> P2
```

*Figure 4. Three isolated Python processes on the Pi. P1 and P2 share no memory, so driving keeps working if the media server fails.*

---

## Figure 4a - Operator dashboard software architecture

```mermaid
flowchart TB
    subgraph UI["Interface components (React 19, TypeScript)"]
        direction LR
        DC["DriveControl, ServoControl<br/>EmergencyStop"]
        SC["SensorCardGrid, MissionStateIndicator<br/>AlertLog, ConnectionStatusBar"]
        VS["VideoSurface, TalkPanel"]
        MP["MapPanel, GpsStatusCard<br/>OfflineMapLayer"]
    end

    subgraph HK["Hooks and API layer"]
        direction LR
        CS["useControlSocket<br/>commands, heartbeat, telemetry"]
        WV["useWebrtcVideo + useTalkback<br/>one peer connection"]
        API["REST client (lib/api.ts)<br/>session, GPS track, health"]
    end

    DC --> CS
    SC --> CS
    VS --> WV
    MP --> API

    CS <-->|"WebSocket /control/ws"| P1["P1 Control<br/>TCP 8080"]
    API <-->|"HTTP: session, GPS track, map tiles"| P1
    WV <-->|"HTTP offer + WebRTC media and data channel"| P2["P2 Media<br/>TCP 8443 + UDP"]
```

*Figure 4a. The dashboard is a single-page React app served by P1. Components hold no network code; each hook owns one connection to one server, so losing the media connection leaves driving and telemetry working.*

## Table 4 - Software stack

| Layer | Runs on | Language | Main frameworks | Main modules |
|---|---|---|---|---|
| Firmware | Arduino UNO | C++ | Arduino core, no RTOS | scheduler, command_parser, motors, servos, sensors, telemetry |
| Backend | Raspberry Pi 4 | Python 3, asyncio | FastAPI and uvicorn (P1, P2), aiortc and PyAV (P2), aiohttp (P3) | serial_bridge, safety, websocket_hub, gps_reader, signaling, talkback, supervisor |
| Frontend | Operator browser | TypeScript | React 19, Vite, Tailwind CSS, Leaflet with PMTiles | useControlSocket, useWebrtcVideo, useTalkback, DriveControl, EmergencyStop, MapPanel |

The three layers share no code and talk only through the serial command protocol (firmware to P1), the control WebSocket (dashboard to P1) and WebRTC (dashboard to P2).

---

## Figure 5 - Command and telemetry message sequence

```mermaid
sequenceDiagram
    autonumber
    participant D as Operator dashboard
    participant P as P1 control server
    participant A as Arduino UNO

    rect rgb(235, 243, 252)
    Note over D,P: Session set-up
    D->>P: {"type":"hello","role":"controller"}
    P-->>D: {"type":"ack","role":"controller"}
    D->>P: {"type":"resume_from","last_ts":...}
    P-->>D: recovery_batch (telemetry missed while offline)
    end

    rect rgb(235, 248, 235)
    Note over D,A: Drive command
    D->>P: {"type":"motor","dir":"F","speed":120,"seq":17}
    Note over P: validate type and role,<br/>clamp speed 0-180, seq > last
    P->>A: F120
    Note over A: framing, syntax, range, state<br/>-> ramp motors
    A-->>P: ACK F
    end

    rect rgb(253, 243, 228)
    Note over D,A: Continuous loops
    loop every 500 ms
        D->>P: {"type":"heartbeat"}
        P->>A: H (refresh 2 s dead-man)
    end
    loop every 500 ms
        A-->>P: CSV telemetry (temp, humidity, gas, range, servos, state)
    end
    loop every 200 ms
        P-->>D: telemetry snapshot + GPS
    end
    D->>P: {"type":"stop_all"} (release or emergency stop)
    P->>A: S (ramp motors to zero)
    end
```

*Figure 5. Message flow between the operator dashboard, the P1 control server and the Arduino.*

---

## Figure 6 - Two-stage command validation

```mermaid
flowchart LR
    IN["Dashboard<br/>JSON command"] --> A1

    subgraph SA["Stage A - P1 on the Raspberry Pi"]
        A1{"A1 Known type?<br/>Sender is controller?"}
        A2{"A2 dir in F,R,L,G<br/>axis in pan, tilt?"}
        A3["A3 Clamp<br/>speed 0-180, angle 0-180"]
        A4{"A4 seq > last seq?<br/>stop_all exempt"}
        A1 -->|yes| A2 -->|yes| A3 --> A4
    end

    A4 -->|"yes: serial line"| B1

    subgraph SB["Stage B - Arduino firmware"]
        B1{"B1 Framing<br/><= 32 bytes, ends in newline"}
        B2{"B2 Syntax<br/>known opcode, numeric arg"}
        B3{"B3 Range<br/>speed 0-255, angle 0-180"}
        B4{"B4 State<br/>motion only in READY / ACTIVE"}
        B1 -->|ok| B2 -->|ok| B3 -->|ok| B4
    end

    B4 -->|ok| OK["ACK + motors driven"]
    A1 -->|no| ER["error to dashboard<br/>nothing sent"]
    A2 -->|no| ER
    A4 -->|no| ER
    B1 -->|fail| NK["NACK reason"]
    B2 -->|fail| NK
    B3 -->|fail| NK
    B4 -->|fail| NK
```

*Figure 6. Every command is checked twice - once on the Pi and again in the firmware - before it can move a motor.*

---

## Figure 7 - Firmware operating-mode state machine

```mermaid
stateDiagram-v2
    [*] --> BOOT: power-on
    BOOT --> READY: init done / "READY RESCUE-UNO"
    READY --> ACTIVE: F / R / L / G
    ACTIVE --> READY: S (stop)
    READY --> PANIC: no command >= 2 s or gas ADC >= 1000
    ACTIVE --> PANIC: no command >= 2 s or gas ADC >= 1000
    PANIC --> READY: commands resume / gas below threshold

    BOOT: BOOT - motors disabled
    READY: READY - fw_state 1 (ARMED)
    ACTIVE: ACTIVE - fw_state 2 (DRIVING)
    PANIC: PANIC - fw_state 3 (STOPPED)
    note right of PANIC
        PWM forced to 0 at once (no ramp)
        driver enable D4 pulled LOW
    end note
```

*Figure 7. Firmware modes. PANIC is entered by the dead-man timeout or the gas alarm and clears automatically.*

---

## Figure 8 - Firmware cooperative scheduler

```mermaid
flowchart TB
    L(["loop()"]) --> PP["Serial parser poll<br/>read bytes, handle complete lines"]
    PP --> SR["Scheduler run<br/>run each task whose period has elapsed (millis)"]
    SR --> L

    SR --> T1["taskMotorService - 10 ms<br/>ramp PWM 15 steps per tick"]
    SR --> T2["taskSafety - 10 ms<br/>dead-man, gas panic, recovery"]
    SR --> T3["taskSensorFast - 50 ms<br/>HC-SR04 range"]
    SR --> T4["taskTelemetry - 500 ms<br/>CSV line to the Pi"]
    SR --> T5["taskHeartbeat - 1000 ms<br/>HB line, LED D13"]
    SR --> T6["taskSensorSlow - 2000 ms<br/>DHT11 + MQ-136 ADC"]
```

*Figure 8. The firmware runs without an RTOS and without `delay()`; periodic tasks are dispatched by a `millis()`-based cooperative scheduler.*

---

## Figure 9 - Two-way media path (WebRTC)

```mermaid
flowchart LR
    subgraph OPS["Operator dashboard"]
        VP["Video player"]
        LS["Listen (laptop speaker)"]
        PT["Push-to-talk mic"]
        OC["Laptop camera / image / screen share"]
        TX["Text messages"]
    end

    subgraph P2["P2 media server (Pi)"]
        CAP["Shared capture<br/>one camera, one mic"]
        RL["ScreenHub relay"]
    end

    subgraph RB["Robot - victim side"]
        CAM["USB camera"]
        MIC["USB microphone"]
        KS["Robot Screen kiosk<br/>Chromium"]
        DSP["7-inch HDMI display"]
        SPK["Speaker"]
    end

    CAM --> CAP
    MIC --> CAP
    CAP -->|"video 640x480 @ 10 fps"| VP
    CAP -->|"audio Opus 32 kbps"| LS
    PT -->|"operator voice"| RL
    OC -->|"operator video"| RL
    TX -->|"'screen' data channel"| RL
    RL -->|"local WebRTC peer"| KS
    KS --> DSP
    KS --> SPK
```

*Figure 9. Two-way communication between operator and victim. Signalling uses HTTP POST on TCP 8443; media travels over UDP on the local network.*

---

## Figure 10 - Layered fault tolerance

```mermaid
flowchart TB
    T3["Tier 3 - systemd<br/>restarts the P3 watchdog service<br/>Restart=on-failure, 5 s"]
    T2["Tier 2 - P3 watchdog<br/>restarts crashed or hung P1 / P2<br/>poll 1 s | /health 10 s | 3 misses | 10 s cooldown"]
    T15["Tier 1.5 - P1 control server<br/>sends S when the controller disconnects;<br/>clamps and sequence-checks commands"]
    T1["Tier 1 - Arduino firmware<br/>dead-man: no valid command for 2000 ms -> stop<br/>gas ADC >= 1000 -> PANIC"]
    T3 --> T2 --> T15 --> T1

    subgraph FR["Failure -> response"]
        F1["Browser closed -> P1 sends S; dead-man <= 2 s"]
        F2["Wi-Fi link lost -> dead-man stops motors <= 2 s"]
        F3["P1 / P2 crash -> P3 respawns after 10 s"]
        F4["P1 / P2 hang -> 3 failed /health -> kill and respawn"]
        F5["P3 crash -> systemd restarts it in 5 s"]
        F6["Pi down -> no commands -> dead-man stop"]
        F7["Toxic gas -> firmware PANIC GAS stop"]
        F8["P2 media fails -> driving still works"]
    end
```

*Figure 10. Safety is layered; the lowest tier (firmware dead-man) stops the robot without depending on the network, the Pi or any tier above it.*

---

## Figure 11 - Testing methodology

```mermaid
flowchart LR
    U["Unit tests<br/>pytest: command validator,<br/>telemetry parser, ring buffer,<br/>mission state, GPS track, access"]
    H["Hardware and firmware tests H1-H15<br/>motors, servos, sensors,<br/>dead-man timing, GPS fix"]
    I["Dashboard and integration tests I1-I19<br/>controls, roles, video,<br/>talkback, map, alerts"]
    N["Network tests N1-N8<br/>range, latency, packet loss,<br/>video delay, Wi-Fi loss"]
    R["Failure and recovery tests F1-F10<br/>kill P1 / P2 / P3, unplug Arduino<br/>or camera, Pi reboot"]
    FT["Field test<br/>full rescue scenario:<br/>time to victim, collisions"]
    U --> H --> I --> N --> R --> FT
```

*Figure 11. Bottom-up testing strategy, from isolated software units to a full field scenario (see `docs/TEST_REPORT.md`).*

---

# Hardware figures and tables

## Figure 12 - Hardware diagram (existing)

Use the project's hardware diagram, which already shows the full wiring:

![Hardware diagram](../hardware%20diagram.drawio.png)

*Figure 12. Hardware wiring of the rescue robot. Source: `hardware diagram.drawio.xml`; open it at <https://app.diagrams.net> to edit or export it.*

## Figure 12a - Detailed hardware wiring diagram

```mermaid
flowchart LR
    subgraph PWR["Power distribution"]
        direction TB
        BAT["4S Li-ion battery<br/>14.8 V nominal / 16.8 V full"]
        BMS["4S 40 A BMS"]
        BK5["Buck converter #1<br/>5 V - servo rail"]
        BK8["Buck converter #2<br/>8 V - Arduino"]
        PB["USB power bank<br/>5 V USB-C"]
        BAT ==> BMS
        BMS ==> BK5
        BMS ==> BK8
    end

    subgraph DRV["Motor drivers"]
        direction TB
        BTL["BTS7960 #1 - LEFT<br/>B+ / B- : 14.8 V in<br/>M+ / M- : motor out<br/>RPWM | LPWM | R_EN | L_EN"]
        BTR["BTS7960 #2 - RIGHT<br/>B+ / B- : 14.8 V in<br/>M+ / M- : motor out<br/>RPWM | LPWM | R_EN | L_EN"]
    end

    subgraph MOT["Drive train (4WD)"]
        direction TB
        MFL["Motor front-left"]
        MRL["Motor rear-left"]
        MFR["Motor front-right"]
        MRR["Motor rear-right"]
    end

    subgraph UNO["Arduino UNO"]
        direction TB
        UJ["Barrel jack Vin"]
        UV["5 V | GND"]
        UP["D5 | D6 | D9 | D10 | D4"]
        US["D11 | D3"]
        UT["D7 | D8 | A2 | A3"]
        UU["USB-B"]
    end

    subgraph SRV["Pan-tilt mount"]
        direction TB
        SP["Pan servo<br/>signal | 5 V | GND"]
        ST["Tilt servo<br/>signal | 5 V | GND"]
    end

    subgraph SEN["Sensors"]
        direction TB
        HC["HC-SR04<br/>VCC | TRIG | ECHO | GND"]
        DH["DHT11<br/>VCC | DATA | GND"]
        MQ["MQ-136<br/>VCC | AO | GND"]
    end

    subgraph RPI["Raspberry Pi 4"]
        direction TB
        PC["USB-C power"]
        PUA["USB-A ports"]
        PG["GPIO14 TXD | GPIO15 RXD"]
        PH["micro-HDMI 0"]
        PJ["3.5 mm audio jack"]
        PW["On-board Wi-Fi"]
    end

    GPS["NEO-6M GPS<br/>TX | RX | VCC | GND"]
    CAM["Logitech C270 camera"]
    MIC["USB microphone"]
    LCD["7-inch HDMI LCD 1024x600"]
    SPK["Speaker"]
    RTR["Wi-Fi router"]

    BMS ==>|"14.8 V"| BTL
    BMS ==>|"14.8 V"| BTR
    BTL ==>|"M+ / M-"| MFL
    BTL ==>|"M+ / M-"| MRL
    BTR ==>|"M+ / M-"| MFR
    BTR ==>|"M+ / M-"| MRR

    BK8 ==>|"8 V"| UJ
    BK5 ==>|"5 V"| SRV
    UV ==>|"5 V"| SEN
    PB ==>|"5 V"| PC

    UP -->|"D5->RPWM, D6->LPWM, D4->EN"| BTL
    UP -->|"D9->RPWM, D10->LPWM, D4->EN"| BTR
    US -->|"D11"| SP
    US -->|"D3"| ST
    UT -->|"D7->TRIG"| HC
    HC -->|"ECHO->D8"| UT
    DH <-->|"DATA<->A2"| UT
    MQ -->|"AO->A3"| UT

    UU <-->|"USB serial 115200"| PUA
    CAM -->|USB| PUA
    MIC -->|USB| PUA
    GPS -->|"TX->GPIO15 RXD"| PG
    PG -->|"GPIO14 TXD->RX"| GPS
    PH -->|HDMI| LCD
    PJ -->|audio| SPK
    PW <-.->|"Wi-Fi"| RTR
```

*Figure 12a. Detailed hardware wiring. Thick arrows carry power, thin arrows carry signals. All grounds (battery, buck converters, BTS7960, Arduino, sensors, servos) are tied to a common ground; the Pi is fed from a separate power bank and shares ground with the Arduino through the USB cable.*

If that figure is too detailed for a journal page, use this simplified
component diagram instead:

```mermaid
flowchart TB
    subgraph POWER["Power"]
        BAT["4S Li-ion 14.8 V + 40 A BMS"]
        BK5["Buck 5 V"]
        BK8["Buck 8 V"]
        PB["USB power bank"]
    end

    subgraph COMPUTE["Computing"]
        PI["Raspberry Pi 4 (4 GB)"]
        ARD["Arduino UNO"]
    end

    subgraph ACT["Actuators"]
        DRV["2x BTS7960 drivers"]
        MOT["4x DC gear motors"]
        SRV["2x servos (pan / tilt)"]
    end

    subgraph SENSE["Sensors"]
        DHT["DHT11 temp / humidity"]
        MQ["MQ-136 gas"]
        US["HC-SR04 ultrasonic"]
        GPS["NEO-6M GPS"]
    end

    subgraph HMI["Victim interface"]
        CAM["USB camera"]
        MIC["USB microphone"]
        DSP["7-inch HDMI display"]
        SPK["Speaker"]
    end

    BAT ==> DRV
    BAT ==> BK5
    BAT ==> BK8
    BK8 ==> ARD
    BK5 ==> SRV
    ARD ==>|"5 V"| DHT
    ARD ==>|"5 V"| MQ
    ARD ==>|"5 V"| US
    PB ==> PI

    PI <-->|"USB serial"| ARD
    ARD --> DRV --> MOT
    ARD --> SRV
    DHT --> ARD
    MQ --> ARD
    US --> ARD
    GPS -->|UART| PI
    CAM --> PI
    MIC --> PI
    PI --> DSP
    PI --> SPK
```

*Figure 12b. Simplified hardware component diagram (thick arrows are power, thin arrows are signals).*

---

## Figure 13 - Arduino UNO pin diagram

```mermaid
flowchart LR
    subgraph UNO["Arduino UNO (ATmega328P)"]
        direction TB
        D3["D3 - PWM (Timer2)"]
        D4["D4 - digital out"]
        D5["D5 - PWM (Timer0)"]
        D6["D6 - PWM (Timer0)"]
        D7["D7 - digital out"]
        D8["D8 - digital in"]
        D9["D9 - PWM (Timer1)"]
        D10["D10 - PWM (Timer1)"]
        D11["D11 - PWM (Timer2)"]
        D13["D13 - on-board LED"]
        A2["A2 - digital I/O"]
        A3["A3 - analog in (ADC)"]
        USB["USB - serial 115200"]
    end

    D5 --> LR["BTS7960 #1 RPWM<br/>left forward"]
    D6 --> LL["BTS7960 #1 LPWM<br/>left reverse"]
    D9 --> RR["BTS7960 #2 RPWM<br/>right forward"]
    D10 --> RL["BTS7960 #2 LPWM<br/>right reverse"]
    D4 --> EN["BTS7960 #1 + #2 R_EN / L_EN<br/>common enable"]
    D11 --> PAN["Pan servo signal"]
    D3 --> TILT["Tilt servo signal"]
    D7 --> TRIG["HC-SR04 TRIG"]
    ECHO["HC-SR04 ECHO"] --> D8
    DHTD["DHT11 data"] <--> A2
    GASA["MQ-136 AO"] --> A3
    D13 --> LED["Status LED<br/>heartbeat blink"]
    USB <--> PIU["Raspberry Pi 4<br/>/dev/ttyACM0"]
```

*Figure 13. Arduino UNO pin assignment. Servos run on Timer2 (ServoTimer2Plus) so that Timer1 stays free for right-motor PWM on D9/D10.*

---

## Table 1 - Arduino UNO pin map

| Pin | Connected to | Signal | Notes |
|---|---|---|---|
| D5 | BTS7960 #1 RPWM | PWM out | Left motors forward (Timer0) |
| D6 | BTS7960 #1 LPWM | PWM out | Left motors reverse (Timer0) |
| D9 | BTS7960 #2 RPWM | PWM out | Right motors forward (Timer1) |
| D10 | BTS7960 #2 LPWM | PWM out | Right motors reverse (Timer1) |
| D4 | Both BTS7960 enables | Digital out | LOW on emergency stop |
| D11 | Pan servo | Servo PWM | ServoTimer2Plus (Timer2), home 90 deg |
| D3 | Tilt servo | Servo PWM | ServoTimer2Plus (Timer2), home 90 deg |
| D7 | HC-SR04 TRIG | Digital out | 10 us trigger pulse |
| D8 | HC-SR04 ECHO | Digital in | `pulseIn`, 25 ms timeout (~ 4 m) |
| A2 | DHT11 data | Single-wire digital | Read every 2 s |
| A3 | MQ-136 analog out | ADC 0-1023 | Read every 2 s; panic at >= 1000 |
| D13 | On-board LED | Digital out | Toggles every 1 s (heartbeat) |
| USB | Raspberry Pi 4 | Serial | 115200 baud, 8-N-1 |

## Table 2 - Raspberry Pi 4 connections

| Pi port | Connected to | Purpose |
|---|---|---|
| USB | Arduino UNO (`/dev/ttyACM0`) | Commands and telemetry, 115200 baud |
| USB | Logitech C270 camera (`/dev/video0`) | Video 640x480 @ 10 fps |
| USB | USB microphone | Victim audio to operator |
| GPIO14 (TXD) / GPIO15 (RXD) | NEO-6M GPS RX / TX (`/dev/serial0`) | NMEA position, 9600 baud |
| micro-HDMI | 7-inch HDMI display (1024x600) | Robot Screen for the victim |
| 3.5 mm jack | Speaker | Operator voice to the victim |
| USB-C | USB power bank | Separate Pi supply |
| On-board Wi-Fi | Wi-Fi router | Link to the operator laptop |

## Table 3 - Hardware components

| Component | Model / rating | Qty | Function |
|---|---|---|---|
| Single-board computer | Raspberry Pi 4 Model B, 4 GB | 1 | Edge processing, network, media |
| Microcontroller | Arduino UNO (ATmega328P, 16 MHz) | 1 | Real-time motor control and safety |
| Chassis | 4WD ground platform | 1 | Mobility |
| DC motors | DC gear motors | 4 | Propulsion (left/right pairs) |
| Motor driver | BTS7960, 43 A dual half-bridge | 2 | One per side |
| Servos | Hobby servo, 0-180 deg | 2 | Camera pan and tilt |
| Temperature / humidity | DHT11 | 1 | Environment monitoring |
| Gas sensor | MQ-136 (H2S-sensitive) | 1 | Hazardous gas detection |
| Ultrasonic sensor | HC-SR04 | 1 | Obstacle range (up to 400 cm) |
| GPS | NEO-6M | 1 | Robot position |
| Camera | Logitech C270 USB | 1 | Video to the operator |
| Microphone | USB audio device | 1 | Victim audio |
| Display | 7-inch HDMI LCD, 1024x600 | 1 | Operator video/text to the victim |
| Speaker | 3.5 mm powered speaker | 1 | Operator voice to the victim |
| Battery | 4S Li-ion, 14.8 V nominal | 1 | Main power |
| BMS | 4S 40 A | 1 | Battery protection |
| Buck converters | 5 V and 8 V outputs | 2 | 8 V to the Arduino, 5 V to the servos |
| Power bank | USB-C | 1 | Raspberry Pi supply |

---

## Photos and screenshots to add (take these yourself)

These can't be drawn; a real photo is the strongest evidence that the system exists.

- **Figure 14 - The assembled robot:** front view showing the camera on its pan-tilt mount and the victim display; a side view if space allows.
- **Figure 15 - Inside the robot:** the electronics bay with the Pi, Arduino, motor drivers and battery visible, with parts labelled.
- **Figure 16 - Operator dashboard:** a screenshot while connected, showing live video, sensor cards, the map and the drive controls.
- **Figure 17 - Robot Screen:** the victim-facing display showing the operator's face or a text message.
- **Figure 18 - Field test:** the robot in the test course or rescue scenario.
