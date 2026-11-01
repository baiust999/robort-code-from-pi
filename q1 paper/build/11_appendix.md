## APPENDIX A. BILL OF MATERIALS

**TABLE A.I.** Bill of materials by subsystem, from the authors' itemized procurement receipts. Prices paid in BDT; USD at an indicative 1 USD = 120 BDT (October 2026). [AUTHOR INPUT REQUIRED: confirm the exchange rate and date; add prices for the USB webcam, the speaker, the Pi power bank and its replacement, which the receipt record omits.]

| Subsystem | Cost (BDT) | Cost (USD) |
|---|---|---|
| Edge computer, storage and display (Pi 4, 7-inch LCD, micro-HDMI cable, 64 GB microSD, case with fan) | 20,861 | 173.84 |
| Microcontroller and motor drive (Arduino UNO, 4 geared motors, 2 x BTS7960) | 6,802 | 56.68 |
| Sensors (MQ-136, plus one grouped sensors-and-circuit-board purchase that includes the GPS receiver, servos, HC-SR04 and DHT11) | 4,007 | 33.39 |
| Power (4S3P 18650 pack and cells, holder, 2 x buck converter, fuse, 14 AWG wire, capacitors, switch) | 3,946 | 32.88 |
| Wiring, connectors and mounting | 782 | 6.52 |
| Chassis and body | 700 | 5.83 |
| Shipping within Bangladesh | 60 | 0.50 |
| Total of itemized parts | 37,158 | about 310 |

Tools, labour, printing and a software subscription in the same record are excluded. The operator laptop and the Wi-Fi access point are not part of the robot and are excluded.

## APPENDIX B. SERIAL PROTOCOL

The serial link between P1 and the Arduino runs at 115200 baud, 8N1, over USB. Each command is a line of ASCII terminated by a newline; a carriage return is ignored and the first byte is the opcode. The 32-byte receive buffer limits a command to 31 characters, and an empty or over-length line is rejected with `NACK ? EMPTY`. Tables B.I to B.III are transcribed from the firmware source (`arduino/protocol.h`, `arduino/command_parser.cpp`, `arduino/protocol.cpp`, `arduino/telemetry.cpp` and `arduino/config.h`).

**TABLE B.I.** Inbound commands. The argument must be all digits. Every accepted command re-arms the dead-man timer.

| Opcode | Command | Argument and range | Motion-gated | Reply on accept |
|---|---|---|---|---|
| F | Forward | speed 0-255 | Yes | ACK F |
| R | Reverse | speed 0-255 | Yes | ACK R |
| L | Turn left | speed 0-255 | Yes | ACK L |
| G | Turn right | speed 0-255 | Yes | ACK G |
| P | Pan servo | angle 0-180 | No | ACK P |
| T | Tilt servo | angle 0-180 | No | ACK T |
| S | Stop | none | No | ACK S |
| H | Heartbeat | none | No | ACK H |
| ? | Status query | none | No | STATUS line |

P1 clamps every speed to 0-180 before it reaches the serial port, so the upper part of the firmware range is not used in the evaluated deployment.

**TABLE B.II.** Outbound messages (newline-terminated ASCII).

| Tag | Format | Emitted when |
|---|---|---|
| (none) | `<temp_c>,<humidity_pct>,<gas_raw>,<range_cm>,<pan>,<tilt>,<fw_state>,<uptime_ms>` | Every 500 ms; `fw_state` is 1 (READY), 2 (ACTIVE) or 3 (BOOT, PANIC or ESTOP) |
| READY | `READY <fw_name> <fw_version>` | After boot or reset |
| ACK | `ACK <opcode>` | A command passed all four stages and executed |
| NACK | `NACK <opcode> <reason>` | A command was rejected (Table B.III) |
| HB | `HB <mode> <uptime_ms>` | Every 1000 ms; does not re-arm the dead-man |
| STATUS | `STATUS;FW=..;VER=..;MODE=..;FAULT=..;UPTIME=..;DIR=..;SPD=..;DIST=..;T=..;H=..;GAS=..;GALM=..;PAN=..;TILT=..` | In reply to `?` |
| PANIC | `PANIC <fault>` | In the supervisor pass that removes drive on a dead-man trip |
| EVT | `EVT DEADMAN_CLEARED` | When valid commands resume after a trip |

P1 drops a telemetry frame longer than 80 characters or with any field outside these ranges: temperature -40 to 125 deg C, humidity 0-100%, gas 0-10000 counts, range 0-500 cm, pan and tilt 0-180 deg, state 1-3.

**TABLE B.III.** NACK reason codes.

| Reason | Meaning |
|---|---|
| EMPTY | No data, or a frame too long for the receive buffer |
| UNKNOWN_CMD | Unrecognized opcode |
| ARG_MISSING | The opcode needs an argument and none was given |
| ARG_INVALID | The argument is not all digits |
| ARG_RANGE | The argument is outside the opcode's range |
| REJECTED | A motion command while motion is not allowed (for example the first command after a dead-man trip) |
