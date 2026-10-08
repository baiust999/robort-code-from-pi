# Rescue Robot — Test Plan and Results

This document records how the system was tested and what the results were.

- **Section 3 (automated unit tests)** contains real results from running the test suite.
- **Sections 4–8 (hardware, network, failure and field tests)** are a plan
  with empty result columns. Fill them in as each test is carried out on the
  real robot.

**How to fill in a result row:** write the measured value, mark it
**PASS** / **FAIL**, add the date and tester initials, and note anything
unusual. If a test fails, describe it in [Section 9](#9-issues-found).

**Harness:** `tools/eval/` runs sections 4-8 and keeps the raw trials as CSV,
so each row below is backed by n measurements rather than one. See
`tools/eval/README.md` for the order to run them in; `tools/eval/summarize.py`
turns the CSVs into the aggregate tables the paper's Section 5 needs.

---

## 1. Scope

| Area | Covered by |
|---|---|
| Pi software logic (validation, parsing, mission state, buffering, talkback) | Automated unit tests (Section 3) |
| Arduino firmware and safety | Hardware tests (Section 4) |
| Dashboard and operator controls | Integration tests (Section 5) |
| Wi-Fi network range and performance | Network tests (Section 6) |
| Recovery from crashes and disconnections | Failure-injection tests (Section 7) |
| Complete rescue scenario | Field test (Section 8) |

## 2. Test environment

| Item | Value |
|---|---|
| Edge computer | Raspberry Pi 4, Linux 6.12 (aarch64), Python 3.11.2 |
| Microcontroller | Arduino UNO, firmware RESCUE-UNO 1.0.0 |
| Network | Local Wi-Fi network (Pi and operator laptop on the same network) |
| Operator laptop | _fill in: model, OS, Chrome version_ |
| Test location(s) | _fill in_ |

---

## 3. Automated unit tests

**Command:** `cd pi && pytest`
**Run on:** Raspberry Pi 4, 2026-10-08
**Result:** **116 passed, 0 failed** (3.8 s)

| Test file | Tests | What it verifies | Result |
|---|---|---|---|
| `test_command_validator.py` | 13 | Motor/servo commands are validated; speed is clamped to 0–180 PWM; unknown directions and axes are rejected; stale sequence numbers are rejected per client; emergency stop bypasses the sequence check. | PASS |
| `test_mission_state.py` | 9 | Mission state goes to STOP on WebSocket loss, serial loss or an ack timeout over 3 s; DRIVING_LIMITED on degraded video; READY and DRIVING when nominal; STOP takes priority. | PASS |
| `test_mock_deadman.py` | 10 | Simulated firmware: dead-man timer trips after 2 s and stops the motors; heartbeat re-arms it; oversized and unknown commands are rejected; PWM is clamped; telemetry arrives at the expected rate. | PASS |
| `test_ring_buffer.py` | 9 | The 300-slot telemetry buffer keeps order, overwrites the oldest entries, returns only newer frames on resume, and reports gaps. | PASS |
| `test_telemetry_parser.py` | 8 | Arduino telemetry lines are parsed correctly; wrong field counts, non-numeric, out-of-range, empty and oversized lines are rejected. | PASS |
| `test_talkback.py` | 22 | Only one operator can hold the robot screen; release and disconnect free it; messages reach the screen; a reconnecting screen gets the current text; Robot Display / VNC mode switching; a session without the controller key can't talk, show video, send text or switch the display, and its media never reaches the screen; a session with the key but not from P1's current controller is also view-only; a takeover moves talk to the new controller and frees the floor. | PASS |
| `test_controller_access.py` | 25 | Controller key: the right key makes a dashboard controller, no key or a wrong one makes it an observer; a stranger connecting first doesn't block the operator; a second keyed dashboard takes over, demoting and telling the first and stopping the robot; observers' drive, servo and emergency-stop commands are rejected and their heartbeats ignored; 5 wrong keys lock an IP out for 5 minutes, even for the right key, without affecting other IPs; no `CONTROLLER_KEY` means nobody controls; P2 gives the talk path only to offers with the key; P1 reports its controller's host to P2 on a localhost-only endpoint. | PASS |
| `test_shared_capture.py` | 5 | Several video sessions share one camera device; the device closes after the last session and reopens; open errors are reported; each session gets its own yuv420p copy of every camera frame (never a shared frame object), from YUYV or yuv420p cameras. | PASS |
| `test_resilient_audio.py` | 4 | The robot mic track sends silence while the mic is missing and switches to it once it opens; a mic lost mid-session is reopened; each outage is reported once; output is one continuous stream of 60 ms Opus packets, paced in real time. | PASS |
| `test_offline_map.py` | 2 | P1 serves the offline map folder at `/maps`, registered before the dashboard's `/` so it isn't swallowed; with no map folder no route is added and nothing changes. | PASS |
| `test_gps_track.py` | 4 | Ground distance is computed correctly; GPS drift of up to ~8 m around a stationary robot adds no track points; driving adds a point about every 10 m; a reading without a fix adds nothing. | PASS |
| `test_telemetry_log.py` | 5 | The telemetry CSV starts with its column header; the header is not duplicated when the log is reopened; a logrotate copytruncate (which empties the file under the open handle) causes the header to be re-emitted, so a rotated log describes its own columns; rows stay aligned with that header; a disabled log writes nothing. | PASS |
| **Total** | **116** | | **116 / 116 PASS** |

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
| H15 | Telemetry rate | Count telemetry frames over 10 s on the serial monitor. | About 2 frames/s (the firmware's 500 ms cycle). P1 re-broadcasts to the dashboard at 5/s. | ___ /s | | |

---

## 5. Dashboard and integration tests

| ID | Test | Procedure | Expected | Result | Pass/Fail | Date / By |
|---|---|---|---|---|---|---|
| I1 | Dashboard loads | Open `http://<pi-ip>:8080` and enter the controller key. | `WS connected`, `CONTROLLER`, `READY`. | | | |
| I2 | Button drive | Hold each drive button, then release. | Robot moves while held and stops on release. | | | |
| I3 | Keyboard drive | Hold arrow keys and WASD. | Same as I2. | | | |
| I4 | Typing doesn't drive | Type "wasd" in the message box. | Robot does not move. | | | |
| I5 | Speed slider | Drive at speeds 60, 120 and 180. | Visibly different speeds; never above 180. | | | |
| I6 | Emergency stop | Drive at full speed, click EMERGENCY STOP. | Stops immediately. Stopping distance: ___ cm. | | | |
| I7 | Observer role | Open a second dashboard (another laptop) without the key. | It shows `OBSERVER — view only`; video, sensors and map work; Drive, Servo, Talk and EMERGENCY STOP are greyed out. | | | |
| I8 | Controller takeover | Enter the key on the second dashboard. | The second becomes controller; the robot stops; the first shows `OBSERVER` and "another dashboard took control", and within about a second its Talk panel is greyed out too ("View only"). | | | |
| I8a | Stranger first | Restart the robot service, open a dashboard without the key, then the operator's with the key. | The operator is controller; the first stays observer. | | | |
| I8b | Wrong key and lockout | On a laptop, enter a wrong key 5 times, then the right key. | "Wrong controller key." four times, then "Too many wrong keys"; the right key is refused for 5 minutes; that laptop can still watch. | | | |
| I9 | Live video | Watch the video panel. | Clear 640×480 video. | | | |
| I10 | Push-to-talk | Hold to talk and speak. | Voice is heard from the robot speaker. | | | |
| I11 | Operator camera | Click My camera. | Operator's face appears on the robot display. | | | |
| I12 | Image | Show an image. | The image appears on the robot display. | | | |
| I13 | Text message | Send a message. | It appears on the robot display; the dashboard shows ✓. | | | |
| I14 | One talker at a time | A second operator tries to talk. | They see "Another operator is talking". | | | |
| I15 | VNC mode | Switch to VNC, then back to Robot Display. | Kiosk closes and reopens; the warning shows while in VNC. | | | |
| I16 | Sensor alerts | Bring an obstacle within 20 cm. | Range card turns red. | | | |
| I17 | Map | Drive outdoors with a GPS fix. | Robot position updates on the map. | | | |
| I17a | Offline map | Disconnect the operator laptop from the internet but keep it on the local Wi-Fi network; reload the dashboard. | Street map still shows around the robot and BAIUST; outside the map area the background is blank. | | | |
| I17b | Follow mode | Open the dashboard, drive; drag the map away; click the locate button. | Map follows the robot (button blue); dragging stops following (button white); the click flies back and follows again. | | | |
| I17c | No drift lines | Leave the robot standing outdoors with a fix for 5 minutes. | No new path lines appear, apart from an occasional short one when the fix jumps. | | | |
| I18 | Video-loss warning | While READY, stop P2 (`sudo pkill -9 -f p2_media`). | Mission state turns amber DRIVING_LIMITED; after P2 restarts, clicking **Retry video** returns it to READY. | | | |
| I19 | Robot audio | Click **Listen** and speak near the robot for a minute. | Voice is heard clearly on the dashboard, without dropouts, and stays in step with the video. | | | |

---

## 6. Network performance tests

Move the robot away from the Wi-Fi router and measure at increasing distances.
Use `ping <pi-ip>` from the operator laptop for latency and loss.

| ID | Setup | Distance / obstacles | Latency avg (ms) | Packet loss (%) | Video quality (good / choppy / lost) | Control responsive? | Notes |
|---|---|---|---|---|---|---|---|
| N1 | Robot near the Wi-Fi router | ___ m, line of sight | | | | | |
| N2 | Robot at medium distance from the Wi-Fi router | ___ m | | | | | |
| N3 | Robot far from the Wi-Fi router | ___ m | | | | | |
| N4 | Through walls | ___ walls | | | | | |
| N5 | Maximum working range | ___ m | | | | | |

| ID | Measurement | Method | Result |
|---|---|---|---|
| N6 | Command latency (key press → wheels move) | Film the screen and robot together at 60 fps; count frames. | ___ ms |
| N7 | Video delay | Film a stopwatch through the robot camera next to the real stopwatch. | ___ ms |
| N8 | Wi-Fi loss | Power off the Wi-Fi router during driving. | Robot stopped? ___ Link recovered in ___ s |

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

1. Check the Wi-Fi covers the course and start the robot at the entry point.
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
| 1 | I19 | Robot audio on the dashboard was choppy: P2 sent only ~75 % of the mic audio (305 of ~400 packets in 8 s, none lost on the network). aiortc encoded each 20 ms frame on a thread pool shared with every viewer's video encoding, which the busy Pi could not keep up with. | High | Yes, 2026-09-28 | The mic track now encodes its own 60 ms Opus packets; measured 99 % of real time afterwards (165 × 60 ms in 10 s). |
| 2 | I19 | A dashboard stayed silent until reloaded if the mic could not be opened when it connected. The USB webcam/mic was seen dropping off USB and re-enumerating when P2 reopened it. | Medium | Yes, 2026-09-28 | Each session's mic track retries every 2 s and switches to the mic when it returns (`MIC_OPEN_FAIL` / `MIC_RESTORED` in `p2_events.log`). |
| 3 | — | P2 crashed with a segmentation fault (exit -11), every 1–2 minutes once two dashboards were watching (13 crashes on 2026-09-28); P3 restarted it after ~10 s each time, dropping the video. | High | Yes, 2026-09-28 | Every `faulthandler` trace showed two VP8 encoder threads at once. The camera's YUYV frames were one object shared by all sessions, and each encoder converted it with `frame.reformat()`, which PyAV runs through a converter cached on the frame with the GIL released. Reproduced off the robot: two encoders on shared YUYV frames segfaulted 3/3 runs; with each session given its own yuv420p copy (`PrivateVideoTrack`), 3/3 runs of 1,500 frame pairs completed. |

---

## 10. Summary

| Area | Tests | Passed | Failed | Not run |
|---|---|---|---|---|
| Unit tests | 116 | 116 | 0 | 0 |
| Hardware | 15 | | | |
| Integration | 21 | | | |
| Network | 8 | | | |
| Failure / recovery | 10 | | | |
| Field test | 1 | | | |

**Conclusion:** _fill in after testing: does the system meet its goals,
and what are the main remaining limitations?_
