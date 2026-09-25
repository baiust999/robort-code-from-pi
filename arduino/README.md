# Rescue Robot — Arduino UNO Firmware

Production-ready, modular firmware for the Arduino UNO (ATmega328P) that drives
the mobility, sensing, and camera-gimbal subsystems of a rescue robot. The board
receives ASCII commands over UART (115200 baud) from a host controller
(e.g. a Raspberry Pi) and streams back telemetry, heartbeats, and safety alerts.

The firmware is fully **non-blocking**: a cooperative `millis()` scheduler
services every subsystem without ever calling `delay()` in the main loop.

---

## Features

- **Safe boot sequence** — outputs forced to a known-safe state before anything
  can move; drivers stay disabled until the board reaches `READY`.
- **Cooperative `millis()` scheduler** — 6 periodic tasks, no blocking.
- **Dead-man timer (2000 ms)** — motors fail-safe stop if no valid command
  arrives within the window.
- **Four-stage command validation** — framing → syntax → range → state machine.
- **BTS7960 differential drive** — dual half-bridge, PWM speed control, current-
  friendly ramping, hardware enable line.
- **Pan / tilt servos** — 0–180° clamped.
- **Sensor suite** — HC-SR04 ultrasonic, HC-SR501 PIR (interrupt),
  DHT11 (bit-banged, no external library), MQ-136 gas.
- **Safety supervisor** — gas panic, emergency stop,
  fault latching and recovery.
- **Telemetry** — periodic status line, heartbeat, `READY` banner, `PANIC`
  alerts, per-command `ACK` / `NACK`.

---

## Directory Layout

```
unocode/arduino/
├── arduino.ino          Top-level sketch (setup/loop, boot, safety supervisor)
├── config.h             Pin map + all tunable constants
├── utils.h / .cpp       Clamp / timing / string helpers
├── robot_state.h / .cpp Finite-state machine + shared sensor snapshot
├── scheduler.h / .cpp   Cooperative millis() scheduler
├── motors.h / .cpp      BTS7960 differential drive + ramping
├── servos.h / .cpp      Pan / tilt gimbal
├── sensors.h / .cpp     HC-SR04, PIR, DHT11, MQ-136 acquisition
├── protocol.h / .cpp    UART wire-protocol definitions
├── command_parser.h/.cpp RX framing + 4-stage validation pipeline
├── telemetry.h / .cpp   Outbound message formatting
├── platformio.ini       Optional PlatformIO build config
└── README.md            This file
```

---

## Pin Map (Arduino UNO)

| Function                  | Pin  | Notes                          |
|---------------------------|------|--------------------------------|
| Left  motor RPWM          | D5   | PWM                            |
| Left  motor LPWM          | D6   | PWM                            |
| Right motor RPWM          | D9   | PWM                            |
| Right motor LPWM          | D10  | PWM                            |
| Motor driver ENABLE       | D4   | common BTS7960 enable          |
| Servo PAN                 | D11  |                                |
| Servo TILT                | D3   | PWM                            |
| HC-SR04 TRIG              | D7   |                                |
| HC-SR04 ECHO              | D8   |                                |
| HC-SR501 PIR              | D2   | external interrupt (INT0)      |
| DHT11 data                | A2   | bit-banged single wire         |
| MQ-136 gas (analog)       | A3   |                                |
| Status LED                | D13  | on-board                       |

All pins are defined in `config.h` — change them there, nowhere else.

---

## UART Protocol

**Link:** 115200 baud, 8N1. Commands are ASCII, terminated by `\n`.

### Inbound commands (host → UNO)

| Command      | Meaning        | Argument   |
|--------------|----------------|------------|
| `F<speed>`   | Forward        | 0–255      |
| `R<speed>`   | Reverse        | 0–255      |
| `L<speed>`   | Turn left      | 0–255      |
| `G<speed>`   | Turn right     | 0–255      |
| `S`          | Stop           | —          |
| `H`          | Heartbeat      | —          |
| `P<angle>`   | Pan servo      | 0–180      |
| `T<angle>`   | Tilt servo     | 0–180      |
| `?`          | Status query   | —          |

Examples: `F200`, `R120`, `L180`, `G90`, `P45`, `T135`, `S`, `H`, `?`

### Four-stage validation

Every inbound line passes through the pipeline before execution:

1. **Framing** — bytes accumulated until `\n`; over-length frames rejected.
2. **Syntax** — opcode must be known; numeric argument required where applicable.
3. **Range** — speed ∈ [0,255], angle ∈ [0,180].
4. **State** — motion commands rejected while `PANIC` / `ESTOP` is latched;
   `S` (stop) is always accepted so the operator can always recover.

Any valid, well-formed line (including `H` and `?`) refreshes the dead-man timer.

### Outbound messages (UNO → host)

| Tag       | Example                                             |
|-----------|-----------------------------------------------------|
| `READY`   | `READY RESCUE-UNO 1.0.0`                             |
| `ACK`     | `ACK F`                                              |
| `NACK`    | `NACK F ARG_RANGE`                                   |
| `HB`      | `HB READY 10345`                                     |
| `TELEM`   | `TELEM;MODE=READY;FAULT=NONE;DIR=S;SPD=0;DIST=124;…` |
| `STATUS`  | `STATUS;FW=RESCUE-UNO;VER=1.0.0;MODE=READY;…`        |
| `PANIC`   | `PANIC GAS`                                          |
| `EVT`     | `EVT DEADMAN_CLEARED`                                |

Telemetry `TELEM` / `STATUS` fields: `MODE, FAULT, DIR, SPD, DIST,
MOT, T, H, GAS, GALM, PAN, TILT`.

---

## State Machine

```
BOOT ──► READY ──► ACTIVE
           ▲          │
           └──────────┘   (S / stop)

  any state ──► ESTOP   (operator stop while faulted)
  any state ──► PANIC   (gas alarm, dead-man timeout)
  PANIC/ESTOP ──► READY (fault cleared: comms resumed / gas cleared / S)
```

Motion is permitted only in `READY` / `ACTIVE` with no latched fault.

---

## Safety Behaviour

- **Dead-man (2000 ms):** no valid command in the window → `emergencyStop()`
  (PWM cut, drivers disabled) → `PANIC DEADMAN`. Auto-recovers when commands
  resume.
- **Gas panic:** `MQ-136` raw ADC ≥ threshold → latched `PANIC GAS`, motors
  cut. Recovers when the reading drops.
- **Obstacle distance:** the HC-SR04 `DIST` reading is reported via telemetry/
  `STATUS` only; it does not auto-stop the motors — the operator decides
  whether to stop, reverse, or continue.
- **Emergency stop:** `S` cuts motion; if faulted with an operator e-stop it
  also clears that latch.

Tune all thresholds and timings in `config.h`.

---

## Build & Upload

### Arduino IDE

1. Open `arduino.ino` (the IDE loads every `.cpp` / `.h` in the folder).
2. Select **Tools → Board → Arduino UNO** and the correct port.
3. Upload. Open Serial Monitor at **115200 baud** — you should see the
   `READY RESCUE-UNO 1.0.0` banner.

Only the built-in **Servo** library is used (bundled with the Arduino AVR core),
so no library installation is required.

### PlatformIO (optional)

```bash
pio run              # compile
pio run -t upload    # flash
pio device monitor -b 115200
```

---

## Quick Test

With the Serial Monitor at 115200 baud (line ending = Newline):

```
?           → STATUS;…
F150        → ACK F      (robot drives forward at PWM 150)
S           → ACK S      (stops)
P30         → ACK P      (pan to 30°)
Fabc        → NACK F ARG_INVALID
F999        → NACK F ARG_RANGE
```

If you stop sending commands for > 2 s, the board emits `PANIC DEADMAN` and cuts
the motors — send any command (e.g. `H`) to recover.
