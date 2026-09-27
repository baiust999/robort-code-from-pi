# Rescue Robot

A teleoperated rescue robot. An operator drives it over a wireless mesh
network from a browser dashboard, watches live video, reads environmental
sensors (gas, temperature/humidity, sonar range, GPS), and talks two-way with
a victim through a screen and speaker mounted on the robot.

![Hardware diagram](hardware%20diagram.drawio.png)

## System at a glance

```
Operator laptop (browser dashboard)
        │  Wi-Fi
IEEE 802.11s mesh  ── relay routers ──  robot router 192.168.10.1
        │  Ethernet
Raspberry Pi 4  192.168.10.10
   ├─ P3 watchdog (systemd)  ── spawns and monitors P1 and P2
   ├─ P1 control server  :8080  WebSocket control, telemetry, GPS, serves the dashboard
   ├─ P2 media server    :8443  WebRTC video/audio, talkback, Robot Screen page
   └─ Robot Screen kiosk (Chromium on the robot's display)
        │  USB serial 115200
Arduino UNO  ── motors, pan/tilt servos, sensors, 2 s dead-man stop
```

Safety is enforced at two levels: P1 clamps and sequence-checks every command,
and the Arduino validates it again and stops the motors if no command arrives
for 2 seconds.

## Repository layout

| Path | Contents |
|---|---|
| `arduino/` | UNO firmware (cooperative scheduler, command parser, motors, servos, sensors). See [`arduino/README.md`](arduino/README.md) for the pin map and serial protocol. |
| `pi/common/` | Shared config, logging, protocol contract and mock hardware. |
| `pi/p1_control/` | P1: serial bridge, safety checks, GPS reader, WebSocket hub, telemetry log. |
| `pi/p2_media/` | P2: WebRTC signaling and media, talkback relay, Robot Screen page. |
| `pi/p3_watchdog/` | P3: process supervisor and health checks. |
| `pi/tests/` | pytest suite. |
| `dashboard/` | Operator dashboard (React + TypeScript + Vite + Tailwind + Leaflet). |
| `deploy/` | Pi install script, systemd unit, `/etc/robot` config templates, mesh router scripts, kiosk launcher, logrotate. |
| `docs/` | Design documentation (see below). |

## Documentation

| Document | What it covers |
|---|---|
| [`docs/CAPSTONE_METHODOLOGY_FINAL.md`](docs/CAPSTONE_METHODOLOGY_FINAL.md) | The full methodology report: hardware, firmware, Pi processes, mesh network, safety, deployment. Start here. |
| [`docs/SOFTWARE_ARCHITECTURE.md`](docs/SOFTWARE_ARCHITECTURE.md) | Software architecture: components, protocol contract, runtime flows, fault tolerance, design decisions and known limitations. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Architecture diagrams: containers, state machines, sequences, failure modes, deployment. |
| [`docs/high level software architure diagram.md`](docs/high%20level%20software%20architure%20diagram.md) | One-page diagram of the whole software stack. |
| [`docs/OPERATOR_MANUAL.md`](docs/OPERATOR_MANUAL.md) | How to drive the robot and talk to a victim from the dashboard, plus troubleshooting. |
| [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md) | Test plan and results: unit tests, hardware, network, failure recovery and field test. |

## Local development (no hardware)

Set `MOCK_HARDWARE=1` to run the Pi processes against simulated serial and
GPS data. Without root, logs and runtime files go under `./var`.

```bash
# Pi services
cd pi
python3 -m venv ../venv && source ../venv/bin/activate
pip install -r requirements.txt                 # P1 + P3
pip install -r requirements-media.txt           # P2 (aiortc, larger download)

MOCK_HARDWARE=1 python -m p1_control.main       # control server on :8080
MOCK_HARDWARE=1 python -m p2_media.main         # media server on :8443
# or run both under the watchdog:
MOCK_HARDWARE=1 python -m p3_watchdog.main

# Tests
pytest
```

```bash
# Dashboard (uses dashboard/.env.development -> localhost)
cd dashboard
npm install
npm run dev
```

## Deploying to the robot

1. **Flash the Arduino.** Open `arduino/arduino.ino` in the Arduino IDE,
   select Arduino UNO, and upload. Check for the `READY RESCUE-UNO` banner
   at 115200 baud.
2. **Build the dashboard.** In `dashboard/`, run `npm install && npm run build`.
   `dashboard/.env` points it at the robot (`192.168.10.10`).
3. **Install on the Pi.** From the cloned repo:
   ```bash
   sudo ./deploy/install.sh
   ```
   This installs system packages, creates the `robot` user, copies code to
   `/opt/robot`, builds the virtualenv, copies config templates to
   `/etc/robot/` (without overwriting existing ones), enables
   `robot-watchdog.service`, and sets up the Robot Screen kiosk. It is safe to
   re-run after pulling updates.
4. **Finish the manual steps** printed at the end of the script: enable the
   GPS UART, set the Pi's static IP `192.168.10.10`, enable desktop autologin,
   and set the 3.5 mm jack as the default audio output.
5. **Provision the mesh routers** (OpenWrt) with `deploy/mesh/robot.sh`,
   `relay1.sh` and `relay2.sh`. The addressing plan is in
   `deploy/etc-robot/mesh.conf`.
6. **Start it:**
   ```bash
   sudo systemctl start robot-watchdog.service
   ```
   Open `http://192.168.10.10:8080` from a laptop on the mesh.

### Configuration

Runtime settings live in `/etc/robot/` on the Pi. Templates are in
`deploy/etc-robot/`:

| File | Used by | Key settings |
|---|---|---|
| `p1.env` | P1 | `SERIAL_PORT` (usually `/dev/ttyACM0`, check with `ls /dev/tty{USB,ACM}*`), `GPS_PORT`, `P1_PORT`, `MOCK_HARDWARE` |
| `p2.env` | P2 | camera/audio device, resolution, FPS, bitrate |
| `p3.env` | P3 | child commands, health-check URLs, mesh gateway |
| `thresholds.json` | P1 | alert thresholds for temperature, gas and range |
| `mesh.conf` | reference only | mesh IP plan and SSIDs |

The full list of options is in `pi/common/config.py`.

### Operator browser note

Browsers only allow microphone and camera access on secure origins. To use
push-to-talk and camera over plain HTTP, open
`chrome://flags/#unsafely-treat-insecure-origin-as-secure` on the operator
laptop and add `http://192.168.10.10:8080`. Video, images and text messages
work without this.

## Logs

- Service: `journalctl -u robot-watchdog.service -f`
- Application logs and telemetry: `/var/log/robot/` (rotated by `deploy/logrotate/robot`)
