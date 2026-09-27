# Rescue Robot — Test Plan and Results

This document records how the system was tested and what the results were.

- **Section 3 (automated unit tests)** contains real results from running the test suite.
- **Sections 4–8 (hardware, network, failure and field tests)** are a plan
  with empty result columns. Fill them in as each test is carried out on the
  real robot.

**How to fill in a result row:** write the measured value, mark it
**PASS** / **FAIL**, add the date and tester initials, and note anything
unusual. If a test fails, describe it in [Section 9](#9-issues-found).

---

## 1. Scope

| Area | Covered by |
|---|---|
| Pi software logic (validation, parsing, mission state, buffering, talkback) | Automated unit tests (Section 3) |
| Arduino firmware and safety | Hardware tests (Section 4) |
| Dashboard and operator controls | Integration tests (Section 5) |
| Mesh network range and performance | Network tests (Section 6) |
| Recovery from crashes and disconnections | Failure-injection tests (Section 7) |
| Complete rescue scenario | Field test (Section 8) |

## 2. Test environment

| Item | Value |
|---|---|
| Edge computer | Raspberry Pi 4, Linux 6.12 (aarch64), Python 3.11.2 |
| Microcontroller | Arduino UNO, firmware RESCUE-UNO 1.0.0 |
| Mesh routers | 3 × OpenWrt, IEEE 802.11s, channel 6 |
| Operator laptop | _fill in: model, OS, Chrome version_ |
| Test location(s) | _fill in_ |

---

## 3. Automated unit tests

**Command:** `cd pi && pytest`
**Run on:** Raspberry Pi 4, 2026-09-27
**Result:** **68 passed, 0 failed** (4.4 s)

| Test file | Tests | What it verifies | Result |
|---|---|---|---|
| `test_command_validator.py` | 13 | Motor/servo commands are validated; speed is clamped to 0–180 PWM; unknown directions and axes are rejected; stale sequence numbers are rejected per client; emergency stop bypasses the sequence check. | PASS |
| `test_mission_state.py` | 10 | Mission state goes to STOP on WebSocket loss, serial loss or an ack timeout over 3 s; DRIVING_LIMITED on degraded video/mesh; READY and DRIVING when nominal; STOP takes priority. | PASS |
| `test_mock_deadman.py` | 10 | Simulated firmware: dead-man timer trips after 2 s and stops the motors; heartbeat re-arms it; oversized and unknown commands are rejected; PWM is clamped; telemetry arrives at the expected rate. | PASS |
| `test_ring_buffer.py` | 9 | The 300-slot telemetry buffer keeps order, overwrites the oldest entries, returns only newer frames on resume, and reports gaps. | PASS |
| `test_telemetry_parser.py` | 8 | Arduino telemetry lines are parsed correctly; wrong field counts, non-numeric, out-of-range, empty and oversized lines are rejected. | PASS |
| `test_talkback.py` | 15 | Only one operator can hold the robot screen; release and disconnect free it; messages reach the screen; a reconnecting screen gets the current text; Robot Display / VNC mode switching. | PASS |
| `test_shared_capture.py` | 3 | Several video sessions share one camera device; the device closes after the last session and reopens; open errors are reported. | PASS |
| **Total** | **68** | | **68 / 68 PASS** |

**Limitation:** these tests use simulated hardware. They prove the software
logic, not the real motors, sensors or radio link, which are covered in the
sections below.

---

## 4. Hardware and firmware tests

Connect to the Arduino with the Serial Monitor at 115200 baud (line
ending: Newline), or test through the dashboard where noted.

| ID | Test | Procedure | Expected | Measured | Pass/Fail | Date / By |
|---|---|---|---|---|---|---|
| H1 | Boot banner | Reset the Arduino. | `READY RESCUE-UNO 1.0.0` | | | |
| H2 | Forward drive | Send `F150`. | `ACK F`; both motors turn forward. | | | |
| H3 | Reverse / left / right | Send reverse, left and right commands. | Correct wheel directions. | | | |
| H4 | Stop | Send `S` while driving. | `ACK S`; motors stop. | | | |
| H5 | Invalid argument | Send `Fabc`. | `NACK F ARG_INVALID`; no motion. | | | |
| H6 | Out-of-range argument | Send `F999`. | `NACK F ARG_RANGE`; no motion. | | | |
| H7 | **Dead-man stop** | Send `F150`, then send nothing. Time until the motors stop. | `PANIC DEADMAN` and motors stop at about 2.0 s. | ___ s | | |
| H8 | Dead-man recovery | After H7, send `H`. | The robot accepts commands again. | | | |
| H9 | Pan servo | Send `P0`, `P90`, `P180`. | Camera pans to each angle. | | | |
| H10 | Tilt servo | Move tilt 0°, 90°, 180°. | Camera tilts to each angle. | | | |
| H11 | Ultrasonic range | Place an object at 20, 50 and 100 cm. | Reading within ±__ cm. | | | |
| H12 | Temperature/humidity | Compare with a reference thermometer. | Within ±2 °C. | | | |
| H13 | Gas sensor | Expose the sensor to a safe test gas (for example, a lighter's unlit gas). | Reading rises; card turns amber/red. | | | |
| H14 | GPS fix | Outdoors, time from power-on to fix. | Fix obtained; position matches a phone. | ___ min | | |
| H15 | Telemetry rate | Count telemetry frames over 10 s. | About 5 frames/s (200 ms cycle). | ___ /s | | |

---

## 5. Dashboard and integration tests

| ID | Test | Procedure | Expected | Result | Pass/Fail | Date / By |
|---|---|---|---|---|---|---|
| I1 | Dashboard loads | Open `http://192.168.10.10:8080`. | `WS connected`, `role: controller`, `READY`. | | | |
| I2 | Button drive | Hold each drive button, then release. | Robot moves while held and stops on release. | | | |
| I3 | Keyboard drive | Hold arrow keys and WASD. | Same as I2. | | | |
| I4 | Typing doesn't drive | Type "wasd" in the message box. | Robot does not move. | | | |
| I5 | Speed slider | Drive at speeds 60, 120 and 180. | Visibly different speeds; never above 180. | | | |
| I6 | Emergency stop | Drive at full speed, click EMERGENCY STOP. | Stops immediately. Stopping distance: ___ cm. | | | |
| I7 | Observer role | Open a second dashboard. | It shows `role: observer`; its drive controls are disabled. | | | |
| I8 | Controller handover | Close the first dashboard; reload the second. | The second becomes controller. | | | |
| I9 | Live video | Watch the video panel. | Clear 640×480 video. | | | |
| I10 | Push-to-talk | Hold to talk and speak. | Voice is heard from the robot speaker. | | | |
| I11 | Operator camera | Click My camera. | Operator's face appears on the robot display. | | | |
| I12 | Image | Show an image. | The image appears on the robot display. | | | |
| I13 | Text message | Send a message. | It appears on the robot display; the dashboard shows ✓. | | | |
| I14 | One talker at a time | A second operator tries to talk. | They see "Another operator is talking". | | | |
| I15 | VNC mode | Switch to VNC, then back to Robot Display. | Kiosk closes and reopens; the warning shows while in VNC. | | | |
| I16 | Sensor alerts | Bring an obstacle within 20 cm. | Range card turns red. | | | |
| I17 | Map | Drive outdoors with a GPS fix. | Robot position updates on the map. | | | |

---

## 6. Network performance tests

Place the relays in a chain and measure at increasing distances. Use
`ping 192.168.10.10` from the operator laptop for latency and loss.

| ID | Setup | Distance / obstacles | Latency avg (ms) | Packet loss (%) | Video quality (good / choppy / lost) | Control responsive? | Notes |
|---|---|---|---|---|---|---|---|
| N1 | Direct to robot router | ___ m, line of sight | | | | | |
| N2 | Through 1 relay | ___ m | | | | | |
| N3 | Through 2 relays | ___ m | | | | | |
| N4 | Through walls | ___ walls | | | | | |
| N5 | Maximum working range | ___ m | | | | | |

| ID | Measurement | Method | Result |
|---|---|---|---|
| N6 | Command latency (key press → wheels move) | Film the screen and robot together at 60 fps; count frames. | ___ ms |
| N7 | Video delay | Film a stopwatch through the robot camera next to the real stopwatch. | ___ ms |
| N8 | Relay loss | Power off the middle relay during driving. | Robot stopped? ___ Link recovered in ___ s |

---

## 7. Failure and recovery tests

| ID | Fault injected | How | Expected behaviour | Observed | Recovery time | Pass/Fail |
|---|---|---|---|---|---|---|
| F1 | Wi-Fi loss while driving | Turn off the laptop Wi-Fi while holding forward. | Robot stops within 2 s (dead-man). | | ___ s | |
| F2 | Dashboard reconnect | Turn the Wi-Fi back on. | Dashboard reconnects; alert log shows recovered frames. | | ___ s | |
| F3 | P1 control server crash | `sudo pkill -9 -f p1_control` | Watchdog restarts P1; dashboard reconnects. | | ___ s | |
| F4 | P2 media server crash | `sudo pkill -9 -f p2_media` | Watchdog restarts P2; video returns. | | ___ s | |
| F5 | Watchdog crash | `sudo pkill -9 -f p3_watchdog` | systemd restarts the watchdog. | | ___ s | |
| F6 | Arduino unplugged | Unplug the Arduino USB. | `serial down`, mission state STOP, no motion. | | | |
| F7 | Arduino reconnected | Plug the Arduino back in. | Serial recovers; READY. | | ___ s | |
| F8 | Camera unplugged | Unplug the camera. | Control still works; video shows an error or falls back. | | | |
| F9 | Pi reboot | `sudo reboot` | Everything starts on its own; dashboard usable again. | | ___ s | |
| F10 | Robot screen crash | Close Chromium on the robot display. | Kiosk relaunches, or the display switches to VNC mode. | | ___ s | |

---

## 8. Field test (full scenario)

Run one complete simulated rescue:

1. Set up the relays and start the robot at the entry point.
2. Drive the robot through a course with at least one obstacle and one turn
   to a "victim" (a person or mannequin).
3. Use pan/tilt to find the victim on video.
4. Talk to the victim, show an image and send a text message.
5. Record the sensor readings and GPS position at the victim.
6. Drive back to the start.

| Measurement | Result |
|---|---|
| Course length / description | |
| Time to reach the victim | |
| Number of collisions | |
| Number of unplanned stops | |
| Could the victim hear and see the operator clearly? | |
| Could the operator hear and see the victim clearly? | |
| Problems encountered | |
| Overall result (PASS / FAIL) | |

---

## 9. Issues found

List every failure or unexpected behaviour found during testing.

| # | Test ID | Description | Severity (high / medium / low) | Fixed? | Notes |
|---|---|---|---|---|---|
| 1 | | | | | |

---

## 10. Summary

| Area | Tests | Passed | Failed | Not run |
|---|---|---|---|---|
| Unit tests | 68 | 68 | 0 | 0 |
| Hardware | 15 | | | |
| Integration | 17 | | | |
| Network | 8 | | | |
| Failure / recovery | 10 | | | |
| Field test | 1 | | | |

**Conclusion:** _fill in after testing: does the system meet its goals,
and what are the main remaining limitations?_
