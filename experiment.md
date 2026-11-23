# Experiment Status Map

Last checked: 2026-11-23.
Checked against: `research paper/` (section1-8, Table 5.0 and Table 4.2),
`q1 paper/` (manuscript.md, revision_notes.md, evidence_map.md),
`docs/` (TEST_REPORT.md, CAPSTONE_METHODOLOGY_FINAL.md) and `tools/eval/results/`.

Purpose: one place that shows what is NOT implemented, NOT verified,
or only PARTLY verified. Implement later; for now this is the map.

Rule for every experiment: never change a pass rule after you see the data.

---

## 0. Status codes

| Code | Meaning |
|---|---|
| `[DONE]` | Measured on the robot, data file exists, no big limit |
| `[PARTIAL]` | Measured, but the design was cut or the data has a clear limit |
| `[NOT RUN]` | In the paper with a pass rule, but NO data exists. You must run it |
| `[SIM ONLY]` | Only a software model or software test. Not a robot measurement |
| `[NOT VERIFIED]` | Feature is coded, but never checked on the real device / real conditions |
| `[INVALID]` | Data exists but must NOT be used (wrong setup) |
| `[REMOVED]` | Dropped from the paper. Not planned for this paper |
| `[NO DATA]` | Claim or number in a doc, but no data file behind it |
| `[AUTHOR]` | Needs input from you (not an experiment) |

---

## 1. Master table (all experiments)

| ID | Experiment | Status | One-line reason |
|---|---|---|---|
| E1 | Control latency + dead-man interval | `[PARTIAL]` | Numbers are upper bounds (up to 700 ms extra) |
| E4 | Dead-man physical wheel stop (240 fps) | `[NOT RUN]` | Only the log interval exists, not the filmed wheel stop |
| E5 | Video + audio delay (glass-to-glass) | `[NOT RUN]` | No `glass2glass.csv` |
| E6 | Wi-Fi range | `[PARTIAL]` | 16 stations, line of sight only, never reached failure |
| E7 | Fault injection | `[PARTIAL]` | Automated is good; manual faults run once; F9 invalid |
| E8 | CPU / resource use | `[PARTIAL]` | Done, but 16 kbps run confounded; `driving+media+aids` not run |
| E9 | GPS drift | `[PARTIAL]` | Log has only 4 decimal places (about 11 m) |
| E15 | Cost | `[PARTIAL]` | Receipt-backed, but 3 parts not itemised; FX rate unconfirmed |
| E16 | Media isolation (P2 frozen) | `[NOT RUN]` | Table 5.7e is empty |
| E13 | Field trial (full rescue run) | `[REMOVED]` | Removed 2026-11-23. No per-run data ever existed |
| E17 | Victim communication study | `[REMOVED]` | Removed 2026-11-23. Needs ethics + 15 people + touch screen |
| E18 | Person detector test | `[REMOVED]` | Removed 2026-11-23. Scoring tools exist; no data |
| E2 | True latency at 240 fps | `[REMOVED]` | Removed 2026-11-01 |
| E14 | SUS usability | `[REMOVED]` | Removed 2026-11-01 |
| E3 | E-stop distance | `[REMOVED]` | Removed 2026-11-03 |
| E10 | Ultrasonic accuracy | `[REMOVED]` | Removed 2026-11-03 |
| E11 | DHT11 accuracy | `[REMOVED]` | Removed 2026-11-03 |
| E12 | Gas sensor response | `[REMOVED]` | Removed 2026-11-03 |
| Abl. | Dead-man off / watchdog off ablations | `[REMOVED]` | Removed 2026-11-01 |

E numbers are NOT renumbered. Gaps (E2, E3, E10-E12, E14) are on purpose.

---

## 2. NOT RUN: you must implement these (3 items)

These are the only experiments still marked `[PENDING MEASUREMENT]` in the paper.
Each tests one contribution: E4 tests C1 (firmware stop), E16 tests C2 (process split),
E5 tests C3 (media path). Suggested order: E16, E5, E4.

### E16 - Media isolation `[NOT RUN]`

- **Idea:** If the media program (P2) is busy or frozen, do drive commands (P1) still arrive on time?
- **Pass rule:** In `media-on` and `p2-frozen`: 30 of 30 motor commands confirmed, and median motor-stop within 50 ms of the `media-off` median.
- **How:** On the Pi (loopback). 3 conditions x 30 trials. `wslatency.py --probe motor --trials 30 --label <condition>`. Rows go to `latency.csv` with labels `media-off`, `media-on`, `p2-frozen`.
- **Open point:** How to freeze P2 is not written in the repo. Decide and write it down first (for example pause the process, then resume).
- **Limit:** E1-style numbers are rounded up to 700 ms, so this only finds big blocking.
- **Paper place:** Table 5.7e (empty).

#### E16 - How to do it (step by step)

**What you need:** the robot on a stand or on the floor with space (the motors turn
for 0.6 s in every trial), the Pi powered and running normally, an SSH window to the
Pi, the operator laptop with the dashboard open (for the `media-on` condition).
No camera. No video to upload. The CSV is the evidence.

**Important thing about P3 (the watchdog):** P3 checks P2's `/health` every 10 s.
After 3 missed checks (about 35 s) it kills and restarts P2. If that happens in
the middle, the `p2-frozen` trials are no longer "frozen". Your paper (Section 5.4,
E16 paragraph) already promises: **each freeze lasts at most 15 s**, then SIGCONT.
One motor trial takes about 2-3 s, so do **5 trials per freeze, 6 freezes = 30 trials**.
Check with a stopwatch that one batch of 5 finishes in under 15 s; if not, use 4.

1. SSH to the Pi. Get the key and go to the tools folder:
   ```
   sudo grep CONTROLLER_KEY /etc/systemd/system/robot-watchdog.service.d/controller-key.conf
   export KEY=<the key>
   cd /opt/robot/tools/eval        # or wherever the repo is on the Pi
   ```
2. **Condition `media-off`** (nobody watching video). Close every dashboard tab
   on every device. Then:
   ```
   ../../venv/bin/python wslatency.py --host 127.0.0.1 --key "$KEY" --probe motor --trials 30 --label media-off
   ```
3. **Condition `media-on`** (video + audio really streaming). Open the dashboard on
   the laptop, start video and two-way audio, and keep it open. Then run the same
   command with `--label media-on`.
4. **Condition `p2-frozen`.** Close the dashboard. Find P2, then freeze, run 5
   trials, un-freeze, all in one line so the freeze cannot last too long:
   ```
   P2=$(pgrep -f p2_media.main); echo $P2     # must print ONE number
   sudo kill -STOP $P2; ../../venv/bin/python wslatency.py --host 127.0.0.1 --key "$KEY" --probe motor --trials 5 --label p2-frozen; sudo kill -CONT $P2
   ```
   Wait 30 s (P2 recovers, P3 sees it healthy again). Check P2 has the same PID
   (`pgrep -f p2_media.main`). Repeat 6 times. Total 30 trials. (The `trial`
   column restarts at 1 in each batch; that is fine, write "batch 1..6" in your notes.)
5. **Check P3 did not restart P2** during a frozen batch:
   `grep -E "PROC_KILL|PROC_SPAWN" /var/log/robot/p3_events.log | tail`.
   If you see a kill/spawn inside a batch, that batch is invalid: write it in
   `notes` and redo it with fewer trials (for example 5).
6. On your PC, run `summarize.py` and compare the `motor_stop` median of
   `media-on` and `p2-frozen` with `media-off`. Pass = 30/30 `ok=1` and the
   median difference is 50 ms or less.

**Will anything go wrong?** Possible problems: P2 PID changes (P3 restarted it),
the dashboard is still open in some tab during `media-off`, or a trial times out
because the robot is on the floor and hits something. Keep the area clear.

**How to put it in the paper:** see Section 10.3.

### E5 - Video and audio delay `[NOT RUN]`

- **Idea:** How old is the picture on the dashboard? Point the camera at a running stopwatch. Photograph the real stopwatch and the dashboard together.
- **Pass rule (only `viewers-1` decides):** median video delay <= 500 ms; median audio delay <= 400 ms each direction.
- **How:** 3 conditions x 20 trials: `viewers-1`, `viewers-2`, `wifi-20m`. `./record.py glass2glass label=viewers-1 real_ms=12480 robot_ms=12190`.
- **Open points:**
  - **Audio** delay: the paper (5.2) names the clap method, but no tool or CSV sheet exists for it yet. Steps below.
  - The 400 ms audio limit is "adopted". If you cite ITU-T G.114 as its basis, add and verify that reference first.
  - Frame rate and packet loss are also listed as outputs. No tool for them is described.
- **Paper place:** Tables 5.4 and 5.4a (empty).

#### E5 - How to do it (step by step)

**Idea in simple words:** one clock is shown in the real world AND in the robot's
video on the laptop. One photo catches both. Real clock minus video clock = delay.

**What you need:**
- A stopwatch that shows milliseconds on a big screen. Use a second phone or a
  monitor with an online millisecond stopwatch. It must show **3 digits of ms**.
- The operator laptop with the dashboard open, video panel big.
- A third phone (any) to take the photos.
- For audio: a phone that can record sound, and Audacity (free) on your PC.

**Video delay (Table 5.4):**
1. Put the stopwatch screen in front of the robot camera, about 30-50 cm away.
2. Put the laptop right next to the stopwatch screen, so one photo can see both
   the stopwatch and the video panel.
3. Start the stopwatch. Wait 30 s so the video is stable.
4. Take a photo with the third phone. Read two numbers from the photo:
   `real_ms` (the real stopwatch) and `robot_ms` (the stopwatch inside the video).
   Write them as milliseconds from zero, for example 12.480 s -> `12480`.
5. Save the row at once:
   `./record.py glass2glass label=viewers-1 real_ms=12480 robot_ms=12190`
6. Wait 5-10 s between photos. Take 20 photos. If a number is blurred and you
   cannot read it, do NOT guess: take one more photo and write "unreadable" in
   the notes of that attempt.
7. **viewers-2:** open the dashboard on a second device too (phone or laptop),
   video playing. Repeat 20 photos with `label=viewers-2`.
8. **wifi-20m:** the router must be 20 m away. Keep the robot, stopwatch and
   laptop together and move the **router** 20 m away (both robot and laptop then
   talk over 20 m). Write this in the paper. Repeat 20 photos.
9. Only `viewers-1` decides pass/fail (median <= 500 ms).
10. Write the limit in the paper: screen refresh (60 Hz = about 17 ms) and photo
    exposure add a small error to each reading.

**Frame rate and packet loss (no new tool needed):** while each condition is
running, open `chrome://webrtc-internals` in the laptop's Chrome. Find the video
`inbound-rtp` entry. Note `framesPerSecond`, `packetsLost` and `packetsReceived`.
Press "Create dump" to save a file. Save one dump per condition. Loss % =
packetsLost / (packetsLost + packetsReceived) x 100.

**Audio delay, robot -> operator (the clap method your paper Section 5.2 already describes):**
1. Put the recording phone so it hears **both** a sound near the robot mic and
   the laptop speaker. (Robot and laptop in the same room, about 1 m apart.)
2. Start recording on the phone. Make a sharp sound near the robot mic (clap or
   two spoons). You hear the clap twice: first the real one, then the copy from
   the laptop speaker.
3. Do this 20 times, 3-5 s apart.
4. Open the recording in Audacity. For each clap, measure the time between the
   first peak and the second peak. That is the audio delay.
5. Small fix: sound needs about 3 ms per metre in air. Keep distances short
   and write them down.

**Audio delay, operator -> robot:** the same, but clap into the laptop mic,
and the phone hears the clap and then the robot speaker.

There is no `record.py` sheet for audio. Save the Audacity numbers in a new
CSV `results/audio_delay.csv` with columns
`trial, direction, label, delay_ms, notes`, or ask to add an `audio_delay`
sheet to `record.py`.

**Evidence to keep:** all photos (name them `e5_viewers-1_01.jpg` ...), the
`webrtc-internals` dumps, and the audio recordings. Upload them to Zenodo (see
Section 9; paper text in Section 10.4).

**Will anything go wrong?** Glare on the screens (turn down room lights), the
camera auto-focus misses the stopwatch digits (move closer), the laptop speaker
echoes back into the robot mic (keep the volume low for the audio test).

### E4 - Dead-man physical stop `[NOT RUN]`

- **Idea:** Cut the command stream. Does the Arduino stop the wheels alone? Prove it on film.
- **Pass rule:** Robot on floor, PWM 180. Wheels still within 2.5 s of the last command in 20 of 20 trials. PANIC DEADMAN logged in 20 of 20.
- **How:** Film wheels at 240 fps with a tape measure on the floor. `./record.py deadman_physical speed_pwm=180 stop_s=2.1 panic_seen=1 distance_cm=6`. Count frames from last command to wheels still.
- **What exists already:** log result only: dead-man interval mean 2022.5 ms, max 2042 ms (this is when drive is removed, NOT when wheels stop).
- **If it fails:** paper can only claim "drive removed within 2042 ms".
- **Paper place:** Table 5.3 (empty).

#### E4 - How to do it (step by step)

**Idea in simple words:** the robot drives, then the commands stop on purpose.
The Arduino must stop the wheels by itself in about 2 s. You film it in slow
motion and count frames.

**The hard part (decide first):** the film must show the exact moment when the
commands stop. The camera cannot "see" a network message. You need a **visible
or audible mark** at that moment. Two choices:
- **Option A (recommended):** add a beep or a full-screen flash to
  `wslatency.py --probe deadman` at the moment it goes silent (`link.beating =
  False`). This changes only the test tool, not the robot code, so it is allowed.
  The laptop stays in the film (or the phone hears the beep).
- **Option B (no code):** use the Pi's log. `deadman_panic` already gives "last
  command -> PANIC" in ms. The film then only needs "PANIC -> wheels still". But
  PANIC is also not visible, so this still needs a mark. Option A is simpler.

The pass rule is 2.5 s and the expected value is about 2.06 s, so a mark that is
accurate to about 20-30 ms is good enough.

**What you need:** a phone with 240 fps slow motion (check it really is 240,
some phones use 120), a tripod or something to hold the phone, a tape measure
on the floor next to the wheel path, a piece of tape on a wheel (so you can see
it turn), good light (slow motion needs a lot of light), the operator laptop.

**Steps:**
1. Put the robot on the floor with about 2 m of clear space in front. Lay the
   tape measure along its path. Put a tape mark on one wheel.
2. Phone on tripod, side view, showing the wheel, the tape measure, and the
   laptop screen (or close enough to hear the beep).
3. Start slow-motion recording. Run ONE trial:
   ```
   ../../venv/bin/python wslatency.py --host 127.0.0.1 --key "$KEY" --probe deadman --trials 1 --speed 180 --label e4-film
   ```
   (Run it on the Pi over SSH so `deadman_panic` is also recorded.)
4. Stop recording. Put the robot back to the start. Repeat for 20 trials.
   Name each video `e4_trial01.mp4` ... `e4_trial20.mp4`.
5. Check P1's log for each trial: `grep "PANIC" /var/log/robot/p1_events.log | tail -1`.
   If you see `DEADMAN` -> `panic_seen=1`.
6. On your PC open each video in a frame-by-frame player (free:
   **Kinovea**, or VLC with the `E` key for next frame). Find:
   - frame A = the beep / flash (last command),
   - frame B = the first frame where the tape mark on the wheel no longer moves.
   - `stop_s = (B - A) / 240`.
   - `distance_cm` = how far the robot moved from frame A to frame B, read on the
     tape measure (optional).
7. Save each row:
   `./record.py deadman_physical speed_pwm=180 stop_s=2.08 panic_seen=1 distance_cm=6`
8. Pass = all 20 trials have `stop_s` < 2.5 and `panic_seen=1`.

**Check the frame rate of the file:** many phones save slow motion as a 30 fps
file. Count frames using the **capture** rate (240), not the playback rate.
Check with `ffprobe e4_trial01.mp4` (look for `r_frame_rate` or the
`com.android.capture.fps` / Apple tag). Write the real rate in the paper.

**Evidence to keep:** the 20 videos + the matching `p1_events.log` lines.
Upload them to Zenodo (Section 9; paper text in Section 10.5). Put one short clip (or 3 still frames:
last command, wheels slowing, wheels still) in the paper as a figure.

**Will anything go wrong?** Too dark -> blurry slow motion. The robot drives
out of the frame (use lower PWM only if you also change the pass rule BEFORE
the test, otherwise keep 180 and move the phone back). Wheels coast for a short
time after the drive is removed; this is real and is exactly what E4 measures.

---

## 3. PARTIAL: done, but limited (6 items)

| ID | What is missing or weak | What would fix it |
|---|---|---|
| E1 | Latencies are quantised: up to 700 ms extra (500 ms Arduino telemetry + 200 ms P1 rebroadcast). They are upper bounds, not true latency. | True latency needs a camera method (that was E2, removed). Keep wording "upper bound". |
| E6 | 16 line-of-sight stations, 5-250 m, one ping burst each. No failure point reached. No obstacle test. Ping loss (0-16%) did not follow distance. Video/control judgements are typed by hand. | Go past 250 m until failure; add walls/obstacles; repeat bursts at one station. Also left for future work (Section 7.1.1). |
| E7 | Automated: 30 of 30 SIGKILL recoveries OK. Manual: F6 (USB unplug) and F7 (Wi-Fi drop) run once each. F9 (Pi reboot) is invalid. P2/P3 logs for the F3 date have rotated away. | Repeat manual faults 10 times; redo F9. |
| E8 | The 16 kbps Opus run is confounded by a P2 restart (not used for claims). Some runs are 3 min, not 30 min. `driving+media+aids` condition not run. Two spliced logger runs in `driving+media`. | Run `reslog.py --condition driving+media+aids --duration 1800` in one uninterrupted run. Re-run 16 kbps. |
| E9 | `telemetry.log` stores lat/lon at 4 decimal places (about 11 m). Resolution-limited. Archived window is 129 min. | Log 6 decimals or raw NMEA; use a known reference point; compare track length with a tape-measured course. |
| E15 | Webcam, speaker and Pi power bank not itemised. USD rate (1 USD = 120 BDT) is indicative. Receipt set not deposited yet. | Price the 3 parts; confirm FX rate and date; deposit receipts. |

### 3.1 How to fix the PARTIAL items (simple steps)

These are optional for the paper. If you do not redo them, keep the limit
sentence in the paper. Do NOT delete old rows; add new rows with a new label.

**E1 - nothing to run.** Keep the words "upper bound" everywhere. No action.

**E6 - Wi-Fi range (go further, add walls).** No video needed.
1. Robot (Pi) at the far end, router fixed. Walk the robot away in steps
   (250, 275, 300 m ...) until video or control fails.
2. At each step, on the Pi:
   `./netsweep.py --target 192.168.0.1 --label N17 --distance-m 275 --obstacles none --video good --control yes`
   (`--video` and `--control` are what you see on the dashboard: good/choppy/lost, yes/degraded/no.)
3. Run **3 bursts** at the same spot (labels N17a, N17b, N17c) so you can show the
   spread.
4. Obstacle test: same distance (for example 20 m) with `--obstacles 1-wall`,
   then `2-walls`. Write the wall type (brick/concrete) in `--notes`.
5. Note the GPS position or measure distance with a tape/phone map. A phone
   photo of each spot is good evidence but not required.

**E7 - manual faults, repeat 10 times.**
1. Start the watcher on the Pi: `./faultinject.py watch --label F6-arduino-unplug`.
2. Pull the Arduino USB cable, wait until the dashboard shows the fault, plug it
   back, wait until it recovers. Stop the watcher. That is 1 trial.
3. Do it 10 times. Same for F7 (turn the router Wi-Fi off/on) with
   `--label F7-wifi-drop`.
4. F9 (Pi reboot): run `sudo reboot` while the watcher runs **from the laptop
   side** (the Pi watcher dies with the Pi; that was why F9 was invalid). Record
   the time from reboot to "dashboard connected again" with a stopwatch or from
   the P3 start line in `p3_events.log`. Write in the notes how you timed it.
5. Copy the P1/P2/P3 logs right after the session (`/var/log/robot/*.log`) into
   `results/log_excerpts/`, so logrotate cannot remove them again.

**E8 - CPU / resources.**
1. Make the robot really do all jobs: dashboard open, video + audio on, driving
   now and then, and the aids (victim marks, detector) on.
2. On the Pi: `./reslog.py --condition driving+media+aids --duration 1800`.
   Do NOT stop it. Do not restart any process during the 30 min.
3. After it ends, check `p3_events.log` for any `PROC_KILL`/`PROC_SPAWN` in that
   time. If there is one, the run is confounded: redo it.
4. Redo the 16 kbps Opus run the same way (one uninterrupted 30 min run).

**E9 - GPS drift.**
1. Find where `telemetry.log` writes lat/lon and change it to 6 decimals (or log
   the raw NMEA lines). Note: this is a code change; say in the paper that E9 used
   the new build.
2. Put the robot on a known point (a survey mark, or a point you average from a
   phone GPS for 10 min). Leave it still for 30 min outside, open sky.
3. Run `./gpsdrift.py --minutes 30 --ref-lat <lat> --ref-lon <lon> --label static-30min-6dp`.
4. Optional track test: drive along a straight line you measured with a tape
   (for example 20 m), and compare the GPS track length with 20 m.

**E15 - cost (not an experiment).** Find the price of the webcam, speaker and
Pi power bank (receipt or shop page screenshot with date). Write the BDT->USD
rate you used and the date and source (for example Bangladesh Bank rate on that
day). Scan the receipts into one PDF; upload with the other evidence (Section 9).

---

## 4. SIMULATED / SOFTWARE-TEST ONLY: no robot measurement

| Item | Evidence type | Gap |
|---|---|---|
| Heartbeat-loss margin (Tables 5.3b, 5.3c) | `[SIM ONLY]` Monte Carlo, assumes independent loss | Real Wi-Fi loss is bursty. Real heartbeat loss never measured |
| Unit tests (paper says 146 = 121 + 25) | `[SIM ONLY]` against mocks | Not trials on the robot |
| Native firmware dead-man test | `[SIM ONLY]` | Real PWM duty, real EN pin voltage and UART timing on the ATmega are `[PENDING MEASUREMENT]` |
| Lockout rule (5 failures in 300 s) | `[SIM ONLY]` software test only | No trial on the robot |
| Telemetry timeout 3000 ms (STOP at operator) | `[NO DATA]` design constant | No experiment ever measured it |
| ~2060 ms dead-man bound | calculated | Confirmed only by log (E1) until E4 is run |

**Check this:** `docs/TEST_REPORT.md` says the `pi/tests` suite has 172 tests and the
Unit tests row says 187. The paper says 121 (+25 = 146). The test count in the paper is out of date, or it refers to an older suite. Recount and fix before submission.

---

## 5. NOT VERIFIED: features coded but never checked in real conditions

Source: `docs/TEST_REPORT.md` and `docs/CAPSTONE_METHODOLOGY_FINAL.md`.
These features run in tests and headless browsers, not on real hardware or real people.

| Feature | Status | What was never checked |
|---|---|---|
| Tap-to-answer questions on the robot screen | `[NOT VERIFIED]` | No victim has used it. No touch device was connected to the Pi (only HDMI inputs listed). Issue I29 |
| Repeating voice message | `[NOT VERIFIED]` | Never heard on the real robot speaker; never tried with a real operator mic (I25, I26) |
| Session recording (operator side) | `[NOT VERIFIED]` | Not checked on the operator laptop. Headless recordings were 5-10% short on audio (blamed on Pi load) (I28). WebM duration fix untested |
| Victim marks (photo + position) | `[NOT VERIFIED]` | Not checked on the operator laptop or a phone (I30). Headless browser had no WebGL, so detector did not run |
| Person detector (EfficientDet-Lite0) | `[NOT VERIFIED]` | No accuracy figure at all. Needs WebGL on a real laptop. Dashboard already warns "missing box does not mean nobody is present" |
| E18 capture mode | `[NOT VERIFIED]` | Never exercised in a browser on the live video path. The Pi's headless Chromium stalled |
| Wi-Fi warning banner (robot side) | `[NOT VERIFIED]` | Not calibrated. Capstone limitation #1 |
| Dashboard drawing of replayed log entries | not implemented | "Dashboard does not yet draw the replayed entries" (Capstone doc) |
| Overall performance (latency, range, bandwidth) | `[NOT VERIFIED]` | Capstone limitation #9 "performance not yet measured" (partly covered now by E1, E6, E8, but not end to end) |
| Planning figures, Capstone Section 13.1 | `[NO DATA]` | Design targets, not measured on this robot |
| End-to-end mission time (test F9 in Capstone) | `[NO DATA]` | "Times vary and have not yet been measured end to end" |
| TEST_REPORT Section 10 summary | `[NOT RUN]` | Hardware 15, Integration 35, Network 8, Failure/recovery 10, Field test 1: all blank. Only the 187 unit tests are filled in. The conclusion line is empty |

The "Hardware / Integration / Network / Failure / Field" rows in TEST_REPORT are the
manual tests you planned in `docs/TEST_REPORT.md`. None has been recorded. That is
the biggest hole in the project documents.

### 5.1 How to check the NOT VERIFIED features (simple steps)

These are "does it work on the real thing?" checks. Each is a short yes/no test,
not a big experiment. For each one: do it 3-5 times, write pass/fail and any
problem in `docs/TEST_REPORT.md`, and keep a short phone video as proof (screen
+ robot in the same shot). Do not film people's faces without their permission.

| Feature | How to check it |
|---|---|
| Tap-to-answer (I29) | First connect a touch screen (or USB mouse as a stand-in, and say so) to the Pi display. Operator sends 3 questions. A helper taps answers on the robot screen. Pass = all 3 answers appear on the dashboard correctly. |
| Voice message (I25, I26) | Operator records a message with the laptop mic and starts repeat. Stand 1 m and 3 m from the robot. Pass = you can understand it every time it repeats. Note the speaker volume. |
| Session recording (I28) | Record a 5-minute session on the operator laptop (not headless). Open the file. Pass = video and audio are both about 5:00 long (write both lengths) and play in VLC. |
| Victim marks (I30) | On the laptop and on a phone, place 3 marks. Pass = each has a photo and a GPS position, and they still show after page reload. |
| Person detector | Open the dashboard on a laptop with WebGL (check `chrome://gpu`). Stand in front of the camera. Pass = a box appears. Only say "it runs"; do NOT give an accuracy number (that was E18, removed). |
| E18 capture mode | Same laptop. Press capture. Pass = frames are saved. |
| Wi-Fi warning banner | During the E6 walk, write the RSSI (dBm) when the banner appears. Repeat 3 times. That is your calibration. |
| Unit test count | On the Pi: `cd pi && ../venv/bin/python -m pytest -q` and also `tools/eval/tests`. Write the real numbers in the paper. |

---

## 6. INVALID or NO-DATA: do not cite

| Item | Why |
|---|---|
| `tools/eval/results/bench_motor.csv` (60 rows) | `[INVALID]` Collected with robot on the floor under a false "wheels elevated" premise. Never cite as stationary data or stopping distance |
| Section 5.7 "100-run" field aggregate | `[NO DATA]` No per-run data. Do not restore without real field rows |
| `estop*.csv`, `ultrasonic.csv`, `dht11_environmental.csv`, `gas.csv` | `[REMOVED]` Hand-entered. Kept as record, not cited |
| E7 manual F9 (Pi reboot) | `[INVALID]` |
| E8 16 kbps Opus run | `[PARTIAL]` Confounded by P2 restart |

---

## 7. REMOVED experiments (not planned for this paper)

Removed from the paper. The code behind some still exists, so you can do them later as future work.

| ID | Why removed | Code or tool still present? |
|---|---|---|
| E13 Field trial (2026-11-23) | No per-run data; needs second person | `record.py field` |
| E17 Victim communication (2026-11-23) | Needs ethics, 15 participants, robot touch screen. Outside the paper's contributions | `record.py victim_comms`; tap-to-answer and voice message features in code |
| E18 Person detector (2026-11-23) | Outside the paper's contributions | `tools/eval/detector_*.py` (102 tests), dashboard capture mode (unverified) |
| E2, E14, ablations 1-2 (2026-11-01) | Author request | `record.py latency_video`, `sus` partly |
| E3, E10, E11, E12 (2026-11-03) | Hand-entered, not backed by logs | Tools deleted; raw CSVs kept |

If you bring one back later, write its pass rule BEFORE collecting data.
If E17 returns: needs ethics approval, 15 participants x 3 modes x 2 victim states,
touch input on robot display, stats plan Cochran's Q then exact McNemar with Holm.
If E18 returns: 400 frames (320 with person, 80 without), hand-drawn boxes, IoU 0.50,
recall >= 0.80 and precision >= 0.90 in the easiest group, at most 1 false alarm per minute over 10 minutes.
If E13 returns: 10 runs, pass = victim found in 300 s + 3 questions answered + 1 instruction repeated + no one touches the robot; need 9 of 10.

---

## 8. AUTHOR INPUT still needed (not experiments)

- Author names, affiliations, corresponding author, ORCID
- Repository URL, archived DOI, licence (none yet)
- Procurement receipts: deposit or describe
- Confirm BDT to USD rate and date; price webcam, speaker, Pi power bank (and its replacement)
- CRediT contributions, funding statement, conflict-of-interest, acknowledgments
- AI-writing disclosure (IEEE Access requires it)
- Author biographies and photos
- Figure fixes: Fig. 1 label near GPS line, Fig. 3 label overlap, Figs. 5 and 10 too wide, export vector at 300 dpi
- Recompute Table X heartbeat intervals from `p1_events.log` before submission

---

## 9. Evidence: videos, photos, logs and Zenodo

**Short answer: yes.** Collect the videos, photos and CSV files, upload them to
**Zenodo** (zenodo.org, free, run by CERN) as one dataset, and cite its DOI in the
paper. Your paper ALREADY promises this archive: every "Supplementary evidence"
paragraph in Section 5 says "supplementary experimental evidence archive [XX]
(DOI: XXX)" with a fixed folder layout. So build exactly that layout.

### 9.1 Folder layout (copy it exactly, the paper uses these names)

```
evidence/
  README.txt                           which file belongs to which table
  SHA256SUMS.txt                       checksums of every file
  E01_Control_Communication/dataset/   latency.csv, p1_events_2026-10-21_1100-1400.log.gz
  E01_Control_Communication/video/     (empty - say so in README)
  E04_Deadman_Timer/dataset/           deadman_physical.csv, P1 log lines of the trials
  E04_Deadman_Timer/video/             e4_trial01.mp4 ... e4_trial20.mp4        <- VIDEO NEEDED
  E05_Streaming/dataset/               glass2glass.csv, audio_delay.csv, webrtc dumps
  E05_Streaming/video/                 e5_viewers-1_01.jpg ..., audio files     <- PHOTOS + AUDIO NEEDED
  E06_Communication_Range/dataset/     network.csv
  E07_Fault_Recovery/dataset/          faults.csv, fault_watch.csv, p1_events_*.log.gz
  E08_Resource_Usage/dataset/          resources.csv, p3_events_2026-10-21_2020-2029.log
  E09_GPS_Evaluation/dataset/          gps_static.csv, telemetry windows, geojson track
  E16_Media_Isolation/dataset/         latency.csv rows media-off/media-on/p2-frozen, p3_events window
```

Empty `video/` folders: the paper already says "no recording exists, so none is
provided". Keep them empty and say so in `README.txt`.

**Which experiments need a video or photo?**

| Exp. | Video / photo? | Why |
|---|---|---|
| E4 | **YES: 240 fps video, all 20 trials** | The measurement IS the video (frame counting). A reviewer must be able to count again |
| E5 | **YES: all 60 photos + the audio recordings** | The measurement IS the photo (two clock readings) |
| E16 | No | CSV + P3 log is the evidence. Optional: a screen recording of the terminal during one freeze |
| E6 | No (optional photo of each station) | netsweep logs it |
| E7 | Optional (phone video of one unplug/replug) | The log is the evidence |
| E1, E8, E9 | No | Machine logs |
| Not-verified features (Section 5.1 of this file) | Short phone video recommended | The only proof that it worked on real hardware |
| E15 | Receipts PDF, only if you want to share it | Cost evidence |

### 9.2 How to upload

1. Make the `evidence/` folder OUTSIDE git (videos are big). Fill it as above.
2. Checksums: `find evidence -type f ! -name SHA256SUMS.txt -exec sha256sum {} + > evidence/SHA256SUMS.txt`
3. Zip each `E..` folder (Zenodo shows files flat; the zip keeps the layout).
4. zenodo.org -> New upload -> Resource type **Dataset**. Title, e.g.
   "Evaluation data and recordings for a teleoperated rescue robot with a
   firmware-enforced stop". Authors = the paper authors. Licence **CC-BY-4.0**.
5. Click **"Reserve DOI"** BEFORE publishing. Now you have the DOI
   (10.5281/zenodo.XXXXXXX) and can write it in the paper. Save as draft.
6. Publish when you submit the paper. After publishing you can add a new
   *version*, but you cannot remove the old files. So check privacy first.
7. Optional: connect the GitHub repo to Zenodo for a code DOI (Section 8 needs one).

**Privacy:** no faces, names or house numbers of other people. Blur or cut them.

---

## 10. How to put each experiment into the paper

### 10.1 Where the paper lives (3 copies - keep them the same)

1. `research paper/section1..8_*.md` - the working sections. **Edit these first.**
2. `research paper/RESEARCH PAPER.md` - the combined paper. Copy the same change in.
3. `q1 paper/manuscript.md` - the IEEE-style version. Same content, but tables
   have Roman numbers (Table VIII, IX ...). Find the place by searching for the
   experiment ID (e.g. `E16`).

### 10.2 The 10 places to update when ONE experiment is finished

Do this list for every experiment you finish (E16, E5, E4). Search for the
experiment ID in each file:

| # | Place | What to change |
|---|---|---|
| 1 | Section 4, **Table 4.1** | "Achieved" column: `Not run` -> e.g. `30 per condition, 2026-12-05` |
| 2 | Section 4.4 **Deviations** | Remove the ID from "Experiments not run"; remove its substitute line (e.g. "E4 ... replaced by the firmware-side interval") |
| 3 | Section 5, **Table 5.0** | Status `[PENDING MEASUREMENT]` -> `MEASURED`; fill Source (e.g. `deadman_physical.csv, 20 rows`) and Corroboration (e.g. `PANIC lines in p1_events.log`) |
| 4 | Section 5.x **protocol paragraph** | Remove `[PENDING MEASUREMENT: ...]`. Keep the protocol, but change future to past ("is run" -> "was run"). Add the date, the git commit of the build, and any change you had to make |
| 5 | Section 5.x **table** | Fill it. In the caption, replace `[PENDING MEASUREMENT]` with `MEASURED.` like the other tables |
| 6 | Section 5.x **analysis line** | Replace `[PENDING MEASUREMENT: ... analysis to be filled ...]` with a **Result** paragraph (templates below) and a **Limitations** paragraph |
| 7 | Section 5.x **Supplementary evidence** | "neither the dataset nor the recording exists yet; both will be added" -> "is provided ... under `E04_Deadman_Timer/dataset/` and `.../video/`" |
| 8 | Section 5.8 **Summary of evidence** | Add one sentence with the main number |
| 9 | Section 6.1 / **6.3 Limitations** / 6.4 | Delete or rewrite the limitation that is now solved (E4 = item 1, E5 = item 2, E16 = item 3) |
| 10 | Section 8 **Table 8.1**, Section 8.2, **Abstract**, Section 1 contributions | Add the new number to the RQ it answers (E4 -> RQ1/C1, E16 -> RQ3/C2, E5 -> RQ4/C3). Abstract: one short phrase |

**Rules:**
- Pass or fail, you report it. **Never change the pass rule** after seeing data.
- If it fails, the paper already says what happens (each Section 5.x says "if any
  trial fails, contribution ... stays limited to ..."). Use that sentence.
- Numbers come from the tools, not by hand:
  `tools/eval/summarize.py` (n, mean, SD, median, p95 for `deadman_physical.csv`
  and `glass2glass.csv`) and `tools/eval/section5_stats.py` (95% CI, bootstrap
  median; it groups `latency.csv` by label, so the E16 labels appear
  automatically). Save its output to `tools/eval/results/section5_stats.md`.
- Last step for all: replace every `[XX] (DOI: XXX)` with the Zenodo citation and
  add a dataset entry to `references.bib`:
  ```
  @dataset{sarkar2026evidence,
    author    = {Sarkar, Chinmoy and Adib, Sadman and Sultana, Sadia},
    title     = {Evaluation data and recordings for a teleoperated rescue robot},
    year      = {2026}, publisher = {Zenodo},
    doi       = {10.5281/zenodo.XXXXXXX}}
  ```
  Then add a **Data Availability** statement at the end of the paper (IEEE Access
  asks for it): "The datasets, logs and recordings behind Section 5 are openly
  available on Zenodo at doi:10.5281/zenodo.XXXXXXX [@sarkar2026evidence]."

### 10.3 E16 - media isolation -> Section 5.4, Table 5.7e

**Fill Table 5.7e:** one row per condition: N (30), Confirmed (count of `ok=1`
`motor_stop` rows), median `motor_stop`, 95% bootstrap interval (from
`section5_stats.py`), difference from the `media-off` median.

**Protocol paragraph:** remove `[PENDING MEASUREMENT: E16.]`. Add: "The test was
run on <date> on build <git commit>. Each `p2-frozen` freeze held 5 trials and
lasted at most <x> s; `p3_events.log` shows no P2 restart during any freeze."

**Result (PASS) template:**
> In all three conditions, 30 of 30 motor commands were confirmed. The median
> `motor_stop` upper bound was A ms with media off, B ms with one operator media
> session and C ms with P2 suspended, a difference of at most D ms, inside the
> 50 ms criterion (Table 5.7e). A stall of the media process therefore neither
> dropped nor measurably delayed control commands at the resolution of the
> telemetry path.

**Result (FAIL) template:**
> In the `p2-frozen` condition, N of 30 commands were confirmed (median X ms,
> Y ms above `media-off`), which fails the criterion of Table 4.2. Contribution C2
> is therefore limited to process recovery (Section 5.4) and does not include
> isolation of control from the media process.

**Limitations (always write):** values are telemetry-quantised upper bounds
(shifts below about 50 ms cannot be seen); loopback on the Pi, so no Wi-Fi; no
merged single-process build was compared.

**Other places:** Table 5.0 row E16; Section 4.4 ("Until E16 is run, it claims no
measured isolation ..." -> delete); 6.3 item 3; Table 8.1 RQ3 add "and a P2 stall
did not delay control (Table 5.7e)". In the 5.4 "Supplementary evidence (E7, E16)"
paragraph: E16 "is provided under `E16_Media_Isolation/dataset/`"; no recording.

### 10.4 E5 - video and audio delay -> Section 5.2, Tables 5.4 and 5.4a

**Table 5.4** is per trial (60 rows), which is long. Recommended: in the paper,
show a summary per condition (`label | N | mean | 95% CI | median | max`) and put
the 60 rows in the Zenodo dataset. Change the caption to match.

**Table 5.4a:** fill each condition: video delay mean (95% CI), audio delay in
each direction (median), frame rate, bitrate, packet loss (from the
`webrtc-internals` dumps).

**Procedure paragraph:** it already describes the clap method for audio. Keep it
and add what you actually used: stopwatch device and its refresh rate, recorder
phone, distances (clap to mic, speaker to recorder), and how `wifi-20m` was set up
(router 20 m away from robot and laptop).

**Result (PASS) template:**
> In `viewers-1`, the median glass-to-glass video delay was A ms (mean B ms, 95% CI
> C to D ms, n = 20) and the median audio delay was E ms robot to operator and F ms
> operator to robot, inside the 500 ms and 400 ms limits of Table 4.2. A second
> viewer raised the median video delay to G ms; at 20 m it was H ms (Table 5.4a).

**Result (FAIL) template:**
> The median video delay in `viewers-1` was A ms, above the 500 ms limit. As
> stated in Section 4.2, contribution C3 is therefore reported with its measured
> delay and without the claim that the delay supports conversation with a victim.

**Limitations:** clock-photo resolution (screen refresh about 17 ms, exposure),
sound travel in air (about 3 ms per metre), one room, one router, one session.

**Delete or shorten:** the paragraph "What existing data can and cannot show"
(the part saying no delay figure is reported), and the sentence "Until E5 is
measured, the paper makes no quantitative claim about media delay or quality."

**Other places:** Table 5.0 row E5; 4.4 "E5 (streaming): no substitute ..." ->
delete; 6.3 item 2 (rewrite: only true control latency over Wi-Fi stays
unmeasured); Table 8.1 RQ4 add the delay numbers; abstract / C3 add "median video
delay A ms". "Supplementary evidence (E5)": "is provided under
`E05_Streaming/dataset/` and `E05_Streaming/video/` (60 photographs and the audio
recordings)".

**Figure (recommended):** one of the 60 photos (stopwatch and video panel in one
frame). Caption: "Figure X. Example glass-to-glass reading: real clock 12.480 s,
displayed clock 12.190 s, delay 290 ms." Reviewers like to see the method.

### 10.5 E4 - dead-man physical stop -> Section 5.1, Table 5.3

**Table 5.3:** 20 rows is fine here. Add a summary line under it:
mean `stop_s`, SD, max, and trials with `panic_seen = 1`.

**Protocol paragraph:** remove `[PENDING MEASUREMENT: ...]`. Add what you really
did: phone model, **real capture frame rate** (from `ffprobe`), how the "last
command" moment is visible in the film (beep or flash marker), lighting,
frame-counting tool (Kinovea or VLC), one video per trial.

**Result (PASS) template:**
> In 20 of 20 trials at PWM 180, the wheels were stationary within S_max s of the
> last command (mean S_mean s, SD x s; Table 5.3), below the 2.5 s criterion, and
> the PANIC DEADMAN line was logged in all 20. The robot travelled a further
> D_mean cm on average (maximum D_max cm) after the last command. The physical
> stop is consistent with the firmware-side interval of Table 5.2b (maximum
> 2042 ms) plus a coast-down of about (S_mean - 2.02) s.

**Result (FAIL) template:**
> In N of 20 trials the wheels were still moving 2.5 s after the last command
> (Table 5.3). As stated in Section 4.2, contribution C1 is therefore limited to
> the time at which drive is removed (2042 ms, Table 5.2b), not the time at which
> the robot comes to rest.

**Limitations:** one floor surface, one speed (PWM 180), one battery level (write
the voltage), frame resolution 1/240 s = 4.2 ms plus the marker error.

**Figure (recommended):** 3 still frames from one video with the tape visible.
Caption: "Figure X. Dead-man stop, trial 7, 240 fps. (a) last command, t = 0;
(b) t = 1.5 s; (c) wheels at rest, t = 2.08 s, 6 cm travelled."

**Other places:** Table 5.0 E4; Table 4.1; 4.4 "E4 (physical dead-man stop):
replaced by ..." -> delete; 6.3 item 1 (rewrite: you CAN now claim a measured stop
time on this floor at PWM 180, but not stopping distance at other speeds or
surfaces); Table 8.1 RQ1 add "wheels at rest within S_max s in 20 of 20";
abstract. In "Supplementary evidence (E1, E4)": E4 "is provided under
`E04_Deadman_Timer/dataset/` and `E04_Deadman_Timer/video/` (20 recordings at
240 fps)".

### 10.6 PARTIAL experiments - how to update the paper

If you redo one, add the NEW rows with a NEW label and keep the old ones.

| Exp. | Paper place | If you redo it | If you do NOT redo it |
|---|---|---|---|
| E1 | 5.1, Tables 5.1-5.2b | Nothing to redo | Keep the "upper bound" wording. Nothing else |
| E6 | 5.3, Tables 5.5, 5.5a; Table 5.0; 6.3 item 4; 7.1.1 | Add new stations as new rows (N17 ...), add obstacle rows, write the failure distance. Change "usable range is at least 250 m" to "usable range was X m line of sight and Y m through Z walls" | Keep the current "partial" text. It is already correct |
| E7 | 5.4, Tables 5.7, 5.7a; Table 5.0 | New table "Manual faults, 10 trials each" (F6, F7, F9) with mean/max recovery. F9: remove "invalid", give the reboot result | Keep "run once each" and "F9 invalid". Already correct |
| E8 | 5.5, Tables 5.8, 5.10; the `[PENDING MEASUREMENT: one further E8 condition ...]` line | Add a `driving+media+aids` row to Table 5.8 and delete the PENDING line. Replace Table 5.10 with the clean 16 kbps run | Change the PENDING line to "The `driving+media+aids` condition was not measured" and add it to 6.3 Limitations |
| E9 | 5.6, Tables 5.11, 5.11a | New row "6 decimals, known reference" in Table 5.11; give the error from the reference point, not only from the centroid | Keep "resolution-limited (about 11 m)". Already correct |
| E15 | 5.7, Table 5.12; 6.3 item 6 | Add the 3 missing parts as rows; write "USD at 1 USD = N BDT, <source>, <date>" | Keep "indicative rate" and "not itemised" |

### 10.7 SIMULATED / software-only items - how to mention them

They are already in the paper with the right label. Never call them measurements.
- Keep the label in the caption: `SIMULATED` (Tables 5.3b, 5.3c),
  `SOFTWARE-TEST` (Tables 5.3a, 5.3d).
- Fix the unit-test count: recount (`pytest -q`) and update Table 5.3a and every
  place that says 121 or 146 (search for "121" and "146").
- Telemetry timeout 3000 ms: write "design constant, not measured". Never put it
  in a results table.
- Lockout rule (5 failures in 300 s): write "verified by software test only".

### 10.8 NOT VERIFIED features - how to mention them

The paper does not evaluate these (Section 6.3 item 7 already says so). Two choices:

- **Option 1 (recommended, safest):** keep them out of Section 5. Keep 6.3 item 7.
  Mention them only in Section 3.11 (design) and Section 7.5.2 (future work).
- **Option 2 (only if you do the checks in Section 5.1 of this file):** add ONE
  short table, in Section 5 or an appendix, called "Functional checks on the
  assembled robot (pass/fail, not a performance measurement)": one row per
  feature with date, device, result and the Zenodo video file name. Then change
  6.3 item 7 to "... were checked to work on the assembled robot (Table X), but
  their performance was not measured." Never claim accuracy or usability from it.
  Put the videos under a new Zenodo folder `Functional_Checks/video/`.

### 10.9 REMOVED experiments (E2, E3, E10-E14, E17, E18, ablations)

- Never put a number from them in Section 5. Never cite the old CSVs
  (`estop*.csv`, `ultrasonic.csv`, `dht11_environmental.csv`, `gas.csv`,
  `bench_motor.csv`).
- They may appear only in Section 4.4 (one line: removed, and why) and in
  Section 7 future work (7.6.4 operator usability, 7.5.2 victim assistance,
  7.2.2 fault injection). The current paper already does this; just search for
  "E13", "E17", "E18" and "SUS" to make sure no old number is left.
- Do not upload their data to Zenodo (it would look like evidence).

---

## 11. Quick checklist

Must run for the paper:
- [ ] E16 - media isolation, 3 conditions x 30
- [ ] E5 - glass-to-glass delay, 3 conditions x 20 (plus audio method)
- [ ] E4 - dead-man physical stop, 20 trials at 240 fps

Good to improve (partial):
- [ ] E6 - go past 250 m, add obstacles
- [ ] E7 - repeat manual faults, redo F9
- [ ] E8 - `driving+media+aids`, redo 16 kbps
- [ ] E9 - 6-decimal GPS log
- [ ] E15 - price 3 parts, confirm FX

Verify on real hardware (not verified):
- [ ] Touch input on robot display + tap-to-answer (I29)
- [ ] Voice message on real speaker and mic (I25, I26)
- [ ] Recording on operator laptop (I28)
- [ ] Victim marks on laptop and phone (I30)
- [ ] Detector on a laptop with WebGL
- [ ] Wi-Fi warning calibration
- [ ] Fill TEST_REPORT Section 10 (hardware, integration, network, failure, field)
- [ ] Fix unit-test count in paper (121 vs 172/187)
