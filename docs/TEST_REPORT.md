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
| Pi software logic (validation, parsing, mission state, buffering, talkback, victim marks) | Automated unit tests (Section 3) |
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
| `test_talkback.py` | 32 | Only one operator can hold the robot screen; release and disconnect free it; messages reach the screen; a reconnecting screen gets the current text; Robot Display / VNC mode switching; a session without the controller key can't talk, show video, send text or switch the display, and its media never reaches the screen; a session with the key but not from P1's current controller is also view-only; a takeover moves talk to the new controller and frees the floor. Tap-to-answer questions (10 tests, added 2026-10-30): question text and 2-4 answers are trimmed and capped, and 1 or 5 answers are refused; a question reaches the screen and the tapped answer reaches every dashboard; a late, repeated, out-of-range or non-integer tap is ignored; a new question replaces the old one; expiry and Clear take it off the screen, and expiry after an answer changes nothing; releasing the screen clears it; an observer can't ask but sees the status; a reconnecting screen gets a question that is still waiting; the timeout fires on the real event loop. | PASS |
| `test_controller_access.py` | 25 | Controller key: the right key makes a dashboard controller, no key or a wrong one makes it an observer; a stranger connecting first doesn't block the operator; a second keyed dashboard takes over, demoting and telling the first and stopping the robot; observers' drive, servo and emergency-stop commands are rejected and their heartbeats ignored; 5 wrong keys lock an IP out for 5 minutes, even for the right key, without affecting other IPs; no `CONTROLLER_KEY` means nobody controls; P2 gives the talk path only to offers with the key; P1 reports its controller's host to P2 on a localhost-only endpoint. | PASS |
| `test_shared_capture.py` | 5 | Several video sessions share one camera device; the device closes after the last session and reopens; open errors are reported; each session gets its own yuv420p copy of every camera frame (never a shared frame object), from YUYV or yuv420p cameras. | PASS |
| `test_resilient_audio.py` | 4 | The robot mic track sends silence while the mic is missing and switches to it once it opens; a mic lost mid-session is reopened; each outage is reported once; output is one continuous stream of 60 ms Opus packets, paced in real time. | PASS |
| `test_offline_map.py` | 2 | P1 serves the offline map folder at `/maps`, registered before the dashboard's `/` so it isn't swallowed; with no map folder no route is added and nothing changes. | PASS |
| `test_gps_track.py` | 4 | Ground distance is computed correctly; GPS drift of up to ~8 m around a stationary robot adds no track points; driving adds a point about every 10 m; a reading without a fix adds nothing. | PASS |
| `test_telemetry_log.py` | 5 | The telemetry CSV starts with its column header; the header is not duplicated when the log is reopened; a logrotate copytruncate (which empties the file under the open handle) causes the header to be re-emitted, so a rotated log describes its own columns; rows stay aligned with that header; a disabled log writes nothing. | PASS |
| **Total** | **116** | | **116 / 116 PASS** |

**Addendum, 2026-10-22.** `test_ice_config.py` (5 tests: ICE config with no
STUN server, with a configured STUN server, no TURN relay in local mode x2
parametrised, per-client ICE rate limiting) was added by a later commit the
same morning the table above was recorded and was never added as a 13th row.
Re-running the full suite on 2026-10-22 (`cd pi && /home/pi/robot/venv/bin/python
-m pytest`, same hardware, full dependency environment) gives **121 passed,
0 failed (3.5 s)**: the 116 tests above, all still passing, plus these 5.
See `research-analysis/test_inventory.md` for the exact commands, the
environment-dependency explanation for an earlier, incomplete-venv rerun that
showed fewer passes, and the raw output. The 116-test, 2026-10-08 result above
is left as originally recorded.

**Addendum, 2026-10-28 (Wi-Fi signal indicator).** `test_wifi_signal.py`
(9 tests) was added with the signal-strength feature: the robot's RSSI is
read from `/proc/net/wireless`; a link whose `operstate` is not `up`, a
missing interface, or an interface absent from `/proc` gives `None` rather
than the last level; alert bit 8 (`signal_warn`) is set at -70 dBm or weaker
and bit 9 (`signal_crit`) at -80 dBm or weaker or when there is no reading;
`signal_dbm` is the last `telemetry.log` column and is empty when there is
no reading. Full suite on 2026-10-28 (same command): **130 passed, 0 failed
(5.9 s)** = the 121 above plus these 9. A second run the same day gave
the same 130 passed (4.84 s); its output is saved in
`research-analysis/output/rerun_full_venv_2026-10-28.txt`.

The same day the dashboard side was checked off the live service: a test P1
on port 18080 (mock hardware, own log folder) sent the Pi's real RSSI
(-50 to -52 dBm, matching `/proc/net/wireless`, refreshed about once a
second) and its dashboard showed 4 green bars and 62 %. A scripted stand-in
server then sent chosen values and screenshots confirmed each state:
-52 dBm -> 4 green bars, 63 %, no banner; -72 dBm -> 2 amber bars, amber
banner; -85 dBm -> 0 bars, red banner; `null` -> NO SIGNAL; -68 dBm straight
after NO SIGNAL -> stays amber (3 dB hysteresis); -60 dBm -> green again;
frames stopped with the socket still open -> NO SIGNAL within about 1 s.
These are software checks; the on-robot tests are I20-I22 and N1-N5 below.

**Addendum, 2026-10-30 (victim-finding tools).** `test_victim_log.py`
(16 tests) was added with the victim-finding tools: marks round-trip
through `victims.jsonl` and nothing else is written there; the list is
empty before the first mark; a corrupt line is skipped; a mark is stamped
with P1's own GPS fix, satellite count and servo angles and broadcast as
`victim_mark`; without a fix, `lat`/`lon` are null and the last track point
is kept; no key, an empty key or a wrong key gets 403 and stores nothing
(3 parametrised cases); a note over 280 characters gets 400; the body
limit returns small bodies, refuses an oversized body on its declared
length, while streaming a chunked body, and when the length header lies
(3 cases), refuses a non-numeric length with 400, and still fits a full
280-character note; a snapshot sent anyway is not stored. Full suite on
2026-10-30 (same command): **146 passed, 0 failed (5.0 s)** = the 130
above plus these 16; output in
`research-analysis/output/rerun_full_venv_2026-10-30.txt`.

The dashboard side has no automated tests (no JavaScript test runner is
configured); on 2026-10-30 it type-checked cleanly (`tsc --noEmit`) and
`oxlint` reported no errors. One functional check of the detector was
made on 2026-10-29 in headless Chromium on the Pi, with the bundled model
and the dashboard's options: on two photos of a person the CPU delegate
scored 0.95 and 0.98 and the GPU delegate returned nothing (Issue 4).
That is not an accuracy measurement; I23-I28 below and the field test
cover the tools on the robot.

**Addendum, 2026-10-30 (session recording).** The recording has no
automated tests either. Functional checks were scripted in headless
Chromium on the Pi against a separate mock P1/P2 (`MOCK_HARDWARE=1`, own
ports and controller key, so the live robot was not controlled), with a
fake laptop mic playing a 440 Hz tone and a 1 kHz tone served in place of
the uninstalled call-out clip; each file was decoded with `ffprobe`/
`ffmpeg` and its audio searched for the two tones. Results: as
controller, the 440 Hz tone is present only while push-to-talk was held
and the 1 kHz tone right after the call-out click, silent otherwise; as
observer, video with silent outgoing audio; a 2 s connection blip (P2
frozen with SIGSTOP) gives one continuous file; with P2 killed the
recording saved itself 20.9 s later and a new one worked after
reconnecting; a reload after 10 s left an unfinished entry from which
9.4 s were recovered, and Delete (after the confirm) left IndexedDB
empty; with IndexedDB blocked the warning showed and the file still
downloaded; a forced `MediaRecorder.start()` failure showed a message
and the next Record worked. One earlier recording from the live robot
(as observer) held the real camera picture and mic audio. On this busy
Pi, headless recordings were 5-10 % short of audio; a plain
`MediaRecorder` recording with none of the dashboard code lost the same
share, so this is attributed to the load, but the operator laptop has
not been checked (I28).

**Addendum, 2026-10-30 (new-mission tool for `victims.jsonl`).** Marks
left over in `victims.jsonl` from an earlier development session were
found still listed in a later one, because nothing until now reset the
active list between sessions; per-mark deletion (I27) could only remove
them one at a time. Eight tests were added to `test_victim_log.py` for
`VictimLog.rotate()` and the new `POST /api/victims/new-mission`
endpoint: rotating archives every current mark to a dated filename in
the same folder and leaves the active list empty; rotating an empty or
missing log is a no-op (`archive: null`); the operation is broadcast as
`victims_reset`; and it is refused with 403 to no key, an empty key or
a wrong key, same as marking and deleting. Full suite on 2026-10-30
(same command): **172 passed, 0 failed (4.3 s)**; output in
`research-analysis/output/rerun_full_venv_2026-10-30_victim-new-mission.txt`.
The dashboard's "new mission" button (next to "Victims found") was
checked against the live robot's P1 process: a temporary mark was
added directly to the live `victims.jsonl`, confirmed over
`GET /api/victims`, then rotated, confirming the live endpoint, not
only the unit tests, archives the mark and clears the active list; the
temporary mark was removed afterward. No dashboard-side automated test
exists for the new button, same limitation as the rest of the victim
tools (see above).

**Addendum, 2026-10-30 (recording format).** Recording now prefers MP4
(H.264). Chromium 152 on the Pi accepts `video/mp4;codecs=avc1,opus`
but not AAC (Debian build), so H.264 + Opus was exercised; H.264 + AAC
is untested. As recorded by Chromium, WebM has no Duration (Chrome's
player reports `Infinity`) and the fragmented MP4 header declares 0 s.
After `withDuration()`: WebM showed 5.9 s in Chrome's player and seeked
to 4 s; the MP4 headers declared 6.210, 6.169 and 5.909 s against
ffprobe's 6.2103, 6.1695 and 5.9094 s (read from the file, not
estimated); every patched file decoded with no errors. End-to-end
against the mock stack, a normal and a crash-recovered recording were
both `.mp4` (H.264 + Opus) and decoded fully. Players other than
Chrome, VLC and ffmpeg (Windows, QuickTime, phones) were not tried.

Verification run, same day. `fixDuration.ts` compiled on its own and run
in Node 22 on ten files: Chrome's MP4 and WebM, a real crash-recovered
MP4, a 10-minute fragmented MP4 from ffmpeg, an MP4 whose fragments use
`base_data_offset`, MP4 and WebM cut at 60 %, random bytes and an empty
file. No call threw; files it does not handle (base offset, random,
empty) came back byte-identical; in every other file only the header
changed, and a second pass added nothing. Declared MP4 lengths against
the last decoded packet: 5.909/5.876 s, 6.169/6.172 s, 600.023/600.027 s
(the 10-minute file in 100 ms). The cut MP4 first declared 5.2 s with
3.8 s playable, because its last fragment lists samples whose data is
missing; the fixer now ends the length at the fragment before an
incomplete one (3.50 s). In the browser against the mock stack: as
controller, an H.264 + Opus MP4 declaring 13.499 s for 13.478 s of media,
with the fake-mic tone at 3.0-6.3 s (push-to-talk held 3.3-6.5 s) and
the call-out tone at 8.8-10.8 s (clicked at 8.5 s); a crash-recovered
MP4 declaring 7.437 s for 7.416 s; with MP4 made unavailable, a WebM
fallback declaring 5.751 s for 6.103 s of media (the WebM length is the
recording time, here 0.35 s short). All decoded with no errors. Opened
whole in Chrome's player, the MP4s showed 7.437 and 13.499 s and the
WebM 5.751 s, and each seeked to 1.5 s before its end; the unpatched
WebM showed `Infinity`. Served without range requests, Chrome showed
wrong lengths and could not seek, which is a property of that serving,
not of the files.

**Addendum, 2026-10-30 (tap-to-answer questions).** Ten tests were added
to `test_talkback.py` (see the table above). Full suite on 2026-10-30
(same command): **156 passed, 0 failed (4.6 s)** = the 146 above plus
these 10; output in
`research-analysis/output/rerun_full_venv_2026-10-30_questions.txt`.
Functional checks were scripted against a separate mock P2
(`MOCK_HARDWARE=1`, own ports and controller key), a headless Chromium
kiosk on its `/screen` page driven over the DevTools protocol, and two
scripted dashboards (one controller, one observer): 34 of 34 checks
passed, covering the existing text message and its acknowledgement, the
"Rescuer is speaking" badge, observer refusal and floor release as well
as the question itself (2, 3 and 4 answers, first tap only, "Answer
sent", replace, Clear, reload of the kiosk and late-joining dashboards).
The dashboard panel was checked in the same way as controller and as
observer. The real 5-minute timeout was checked once without media
(`ScreenHub` with stub channels): the question expired after 300.4 s,
the screen was told to hide it, both dashboards saw "expired" and a
later tap was ignored. These checks found Issues 7 and 8. The full
video test stack overloaded the Pi when run alongside other desktop
software (P2 missed health checks and the Pi rebooted), so it should be
run with the desktop otherwise idle. No victim has used the screen, and
the feature has not been checked on the physical display (I29). On
2026-10-30 no touch input device was connected to the Pi (only the HDMI
inputs were listed in `/proc/bus/input/devices`), so I29 needs the
display's touch cable connected first.

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
| I20 | Wi-Fi bars | Open the dashboard; hover over the bars; compare with `grep wlan0 /proc/net/wireless` on the Pi. | Bars and % shown next to `WS connected`; tooltip dBm matches the Pi within a few dB. | | | |
| I21 | Weak-signal warning | Drive (or carry) the robot away from the router until the signal passes -70 dBm, then -80 dBm; come back. | Amber banner at -70 dBm, red at -80 dBm, each logged in Alerts; both clear on the way back. | | | |
| I22 | NO SIGNAL | While connected, stop P1 (`sudo pkill -f p1_control`) or switch off the router. | Within about 1 s the bars turn grey and show `NO SIGNAL` with a red banner; the old value is not shown. | | | |
| I19 | Robot audio | Click **Listen** and speak near the robot for a minute. | Voice is heard clearly on the dashboard, without dropouts, and stays in step with the video. | | | |
| I23 | AI person detection | With "AI: on", have a person stand, sit, then lie down at 1, 3 and 5 m from the camera, in good and dim light. Then point the camera at an empty room for 2 minutes. | Note for each pose/distance/light whether a box appears and its %; *POSSIBLE PERSON* shows within about 1 s of a clear view; count false boxes in the empty room. | | | |
| I24 | AI does not slow the controls | With AI on, drive and press EMERGENCY STOP on the slowest laptop that will be used. | No noticeable lag; if the laptop is too slow, AI switches itself off with a message. | | | |
| I25 | Call out | Click **📢 Call out** with the clip installed. | Message heard clearly from the robot speaker; meter shows *(speaker playing)*, then *Listening for a reply…* for 10 s. | | | |
| I26 | Reply cue | After a call-out, a person 2 m and 5 m from the robot knocks three times, then shouts; repeat once with nobody responding. | "sound after call-out" in Alerts for the knock/shout; record the dB rise shown; no alert when nobody responds (note background noise). | | | |
| I27 | Mark victim | Click **📍 Mark victim here**, type a note, Save; then reload the page; then open a second (observer) dashboard. | Mark in *Victims found* and on the map (faded + without GPS); `victim-<id>.jpg` and `.txt` in Downloads; after reload the mark and its snapshot link are still there; the observer sees the mark but no snapshot and cannot mark; `victims/victims.jsonl` on the Pi has the mark and no image. | | | |
| I29 | Tap-to-answer question | With the display's touch cable connected and **Robot Display** on: in *Ask a question* type "Are you hurt?" with Yes / No, **Send question**; tap **Yes** on the robot's touchscreen. Repeat with 3 and 4 answers; then send one and click **Clear**; then send one and leave it for 5 minutes. | Question and large buttons fill the robot display; after a tap "Answer sent ✓" for about 2 s, then the question goes and the dashboard shows **Answer: Yes**; 3 answers in one row, 4 in two; Clear removes it at once; unanswered, it goes after 5 minutes and the dashboard shows "No answer (5 min)". Note whether the buttons are easy to read and tap at arm's length. | | | |
| I28 | Session recording | On the operator laptop with the key: **⏺ Record**; speak with push-to-talk; **📢 Call out**; let someone speak near the robot; walk the robot out of Wi-Fi range for about 5 s and back; **⏹ Stop recording**. Then record again and reload the page midway. | `robot-session-<time>.mp4` in Downloads plays in the laptop's own player and in VLC, shows its full length and can be seeked to near the end, with the video, the robot mic, your voice and the call-out, without gaps and in step; one file despite the short drop; listed under *Recordings on this computer*; after the reload the second is listed as *(unfinished)* and **Save to device** gives a playable file. | | | |

---

## 6. Network performance tests

Move the robot away from the Wi-Fi router and measure at increasing distances.
Use `ping <pi-ip>` from the operator laptop for latency and loss, or
`tools/eval/netsweep.py`, which records these with the robot's RSSI. Measure
distance with a tape or marked spots, not GPS (the log's 4 decimal places
are about 11 m). Read the signal from the dashboard tooltip or the
`signal_dbm` column of `telemetry.log`.

| ID | Setup | Distance / obstacles | Signal (dBm) | Latency avg (ms) | Packet loss (%) | Video quality (good / choppy / lost) | Control responsive? | Notes |
|---|---|---|---|---|---|---|---|
| N1 | Robot near the Wi-Fi router | ___ m, line of sight | | | | | | |
| N2 | Robot at medium distance from the Wi-Fi router | ___ m | | | | | | |
| N3 | Robot far from the Wi-Fi router | ___ m | | | | | | |
| N4 | Through walls | ___ walls | | | | | | |
| N5 | Maximum working range | ___ m | | | | | | |

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
4. Before the victim is in view, use **📢 Call out** and note whether the
   reply cue fires; note when the AI first boxes the victim and when the
   operator first sees them.
5. Talk to the victim, show an image and send a text message.
6. **Mark victim here** with a note; record the sensor readings and GPS
   position at the victim, and compare the mark's position with the
   victim's true position.
7. Drive back to the start.

| Measurement | Result |
|---|---|
| Course length / description | |
| Time to reach the victim | |
| Call-out reply cue fired? (rise in dB) | |
| AI first box vs operator first sighting (s) | |
| Victim-mark position error (m), or "no fix" | |
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
| 4 | — | AI person detection showed "AI: on" but never drew a box. The MediaPipe GPU delegate loaded without error but returned no detections (headless Chromium test on 2026-10-29: two person photos, GPU nothing, CPU 0.95 and 0.98); empty results never throw, so the GPU-to-CPU fallback never ran. | High | Yes, 2026-10-29 | Detector now always uses the CPU delegate; slow laptops are caught by the 150 ms auto-off. GPU test ran on a software renderer, not a laptop GPU. |
| 5 | I27 | Victim photo and details did not reach Downloads in the operator's own Chrome; a headless test that allows downloads could not show this. | Medium | Mitigated, 2026-10-30 | The snapshot is now also kept in the browser (IndexedDB) and "download photo / details" links are shown; recheck with I27. |
| 6 | I28 | A recording stopped and saved itself on any brief connection drop: a 1.5 s "disconnected" state that recovered by itself split the recording (headless test, P2 frozen with SIGSTOP). On weak Wi-Fi this would chop a session into pieces. | Medium | Yes, 2026-10-30 | Recording now continues through a drop and stops only after 15 s down or when the connection is replaced; the same test then gave one continuous file. |
| 7 | I29 | The question layer covered the "Rescuer is speaking" badge and the "Tap to turn on sound" button, so a victim answering a question could not see that the operator was talking (headless test, 2026-10-30). | Low | Yes, 2026-10-30 | Both now sit above the question layer; rechecked in the same test. |
| 8 | I29 | Questions sent from the dashboard never appeared on the physical robot display, although P2 logged them and the kiosk was connected: the kiosk's Chromium was showing a cached copy of the screen page from before the update, which ignores question messages. P2 served `/screen` without `Cache-Control`. | High | Yes, 2026-10-30 | The kiosk cache was cleared, and P2 now sends `/screen` with `Cache-Control: no-cache` (as P1 does for the dashboard HTML), so an update reaches the kiosk on its next load. Recheck with I29. |
| 9 | I28 | With MP4 recording, a recording cut off by a reload was recovered empty. Chrome's MP4 writer emits data only at key frames: with steady, camera-like video and no key-frame request it wrote nothing until Stop (headless test, 8 s), so a crash would lose the whole recording; WebM wrote every second. | High | Yes, 2026-10-30 | The recorder now asks for a key frame every second (`videoKeyFrameIntervalDuration`); MP4 then wrote every 1-2 s and the recovered recording played. |

---

## 10. Summary

| Area | Tests | Passed | Failed | Not run |
|---|---|---|---|---|
| Unit tests | 156 | 156 | 0 | 0 |
| Hardware | 15 | | | |
| Integration | 34 | | | |
| Network | 8 | | | |
| Failure / recovery | 10 | | | |
| Field test | 1 | | | |

**Conclusion:** _fill in after testing: does the system meet its goals,
and what are the main remaining limitations?_
