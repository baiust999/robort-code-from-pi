# Experiments: What Is Done and What Is Left

This file explains the experiments of the rescue robot project in simple English.
Last checked: 2026-11-23. Sources: `research paper/section5_results.md` (Table 5.0),
`research paper/section4_experimental_setup.md` (Table 4.2) and `tools/eval/README.md`.

Important rule: **never change a pass rule after you see the data.** Each pass rule
below was fixed before the test. If the robot fails, you report the failure.

---

## 1. Experiments that are DONE (or partly done)

| Experiment | What it measured | Status |
|---|---|---|
| E1 | Delay between a command and the robot confirming it (WebSocket) | Done. Numbers are upper bounds (up to 700 ms extra, because telemetry is slow). |
| E6 | Wi-Fi range | Partly done. Only 6 stations; the test stopped at 50 m. Full range is not known. |
| E7 | Fault tests (crash, restart, recovery) | Done. The 16 kbps run is affected by a P2 restart. |
| E8 | CPU / resource use (idle, viewers, driving + media) | Done for all conditions. |
| E9 | GPS drift | Done, but weak: GPS in the log has only 4 decimal places. |
| E15 | Cost | Done. 37,158 BDT, about USD 310. Webcam, speaker and Pi power bank are not itemised. |

---

## 2. Experiments NOT done yet (6 of them)

Recommended order: **E18, E16, E5, E4, then E13 and E17.**

---

### E18 - Person detector test (do this FIRST)

**Simple idea:** The dashboard draws a box around a person it sees in the video.
How often is that box right, and in the right place?

**Why first:** No ethics approval, no money. You can do it alone.

**Pass rule (easiest group only: person upright, not hidden, room light, near):**
- Recall >= 0.80 (finds at least 80% of people)
- Precision >= 0.90 (at least 90% of drawn boxes are right)
- At most 1 false alarm per minute in 10 minutes of video with nobody in it
- A box is "right" if it overlaps your hand-drawn box by IoU >= 0.50
- Harder groups (lying down, hidden, dark, far) have no pass rule. Just report the result.

**How to do it:**
1. Build and deploy the dashboard's **evaluation capture mode** (not built yet; this is the blocker).
2. Capture 400 frames through the robot's own camera: 320 with a person (16 groups of
   posture / hidden or not / light / distance) and 80 with nobody.
3. Import each batch: `tools/eval/detector_import.py` (check it reports no problems).
4. Write down your drawing rule (for example "box the whole visible body"), then draw a
   box on every person in every frame with `detector_annotate.py`. Mark empty frames too.
5. Record 10+ minutes of video with nobody in it (for the false-alarm test).
6. Run `./detector_eval.py --strict --out results/detector_eval.md`
7. Put the numbers in Section 5.9 of the paper.

**Careful:** The code exists, but that is not the experiment. Until all 6 steps are done it stays pending.

---

### E16 - Media isolation

**Simple idea:** If the video/audio program (P2) freezes or is busy, do drive commands
(P1) still work on time? This proves the "separate processes" design.

**Pass rule:** In both `media-on` and `p2-frozen` conditions: 30 of 30 motor commands
confirmed, and the median motor-stop time within 50 ms of the `media-off` median.

**How to do it:**
1. Run on the Pi (loopback), three conditions x 30 trials: `media-off`, `media-on`, `p2-frozen`.
2. Use: `wslatency.py --probe motor --trials 30 --label <condition>`
3. For `p2-frozen`, pause the P2 process (for example with a stop signal) while trials run, then resume it.
4. Compare the median of each condition with `media-off`.

**Note:** E1-style numbers are rounded up to 700 ms, so this test only finds big blocking, not small effects.

---

### E5 - Video and audio delay (glass-to-glass)

**Simple idea:** How old is the picture on the dashboard? Point the robot camera at a
running stopwatch. Take one photo showing the real stopwatch and the dashboard video
together. The difference is the delay.

**Pass rule (condition `viewers-1`):** median video delay <= 500 ms, and median audio
delay <= 400 ms in each direction. `viewers-2` and `wifi-20m` are reported but do not decide.

**How to do it:**
1. Three conditions, 20 trials each: `viewers-1`, `viewers-2`, `wifi-20m`.
2. For each trial, photograph the real stopwatch and the video panel together.
3. Enter it: `./record.py glass2glass label=viewers-1 real_ms=12480 robot_ms=12190`
   (delay = real_ms - robot_ms).
4. Audio delay needs its own method for each direction (robot to operator, operator to robot). Decide the method and write it down before you start.

---

### E4 - Dead-man physical stop

**Simple idea:** When commands stop, does the Arduino firmware stop the wheels by itself,
without help from the Pi? You film the wheels to prove it.

**Pass rule:** Robot on the floor at PWM 180. Wheels stopped within 2.5 s of the last
command in **20 of 20** trials, and the PANIC DEADMAN line is in the log in **20 of 20**.

**How to do it:**
1. Film the wheels at 240 fps. Lay a tape measure along the path (also gives stopping distance).
2. Drive at PWM 180, then cut the command stream.
3. Count video frames from the last command to the wheels being still.
4. Check the PANIC DEADMAN line in `var/log/p1_events.log`.
5. Enter each trial: `./record.py deadman_physical speed_pwm=180 stop_s=2.1 panic_seen=1 distance_cm=6`
6. Do 20 trials.

**If it fails:** the paper may only claim "drive removed within 2042 ms" (from the log), not a physical stop.

**Do NOT use** `bench_motor.csv` as evidence. It was recorded with a wrong setup.

---

### E13 - Field trial (full rescue run)

**Simple idea:** A full practice rescue on an indoor corridor course. The operator drives,
finds a hidden person, talks with them using audio/video.

**A run passes only if all three are true:**
1. Operator finds the victim (victim visible in video) within **300 s**.
2. Operator asks 3 scripted questions, victim answers, operator writes all 3 answers
   correctly, and the victim repeats back 1 scripted instruction.
3. Nobody touches the robot during the run.

**Pass rule:** at least **9 of 10** runs pass.

**How to do it:**
1. Fix the course (for example a corridor with a turn, about 35 m) and write the rule down.
2. Run 10 times.
3. Enter each run: `./record.py field course="corridor-with-turn" course_m=35 time_to_victim_s=142 time_total_s=265 collisions=0 unplanned_stops=1 victim_heard_operator=1 victim_saw_operator=1 operator_heard_victim=1 operator_saw_victim=1 result=PASS operator=XX`
4. For any failed run, write the cause.

**Warning:** The old "100-run" number has no real data. Do not use it.

---

### E17 - Victim communication under degraded conditions (do LAST)

**Simple idea:** Can a victim who cannot speak still give information to the operator,
using the tap-to-answer screen or the repeating voice message?

**Design:** 15 participants x 3 modes (speech-only, voice-message, tap-to-answer) x
2 victim states (can speak / cannot speak) = 90 trials. Change the order between
participants (counterbalance).

**Pass rule (cannot-speak state):**
- Tap-to-answer: all 3 scripted items correct in at least **12 of 15** participants.
- Voice message: participant acts on 1 spoken instruction in at least **12 of 15**.
- Speech-only is expected to fail. Report whatever happens.
- Stats plan (fixed in advance): Cochran's Q, then exact McNemar with Holm correction.

**Blockers before you start:**
1. **Ethics approval** (one application can cover E13 and E17).
2. A **touch input on the robot display**. No tap-to-answer has ever been done on the robot.

**How to record:** `./record.py victim_comms participant=P3 order=2 mode=tap-to-answer victim_state=cannot-speak items_correct=3 time_to_contact_s=41 time_exchange_s=96 confidence=4 failure_mode=none question_ids="7;8;9"`
Cross-check tap timings with the P2 log lines QUESTION_ASK / QUESTION_ANSWER.

---

## 3. General rules for every experiment

- One trial is not a result. Always report n, mean and SD.
- Do all runs on a stable power supply. Check `under_voltage_ever`; if the supply sagged, rerun.
- Logs rotate. Copy the log window you use into `tools/eval/results/log_excerpts/`.
- After new data, rerun `tools/eval/section5_stats.py --out tools/eval/results/section5_stats.md`.
- Do not change a pass rule after seeing data.
- Failures go into the paper too. A failed test is still a result.
- Do not add E18, E17 or other unmeasured claims to the abstract, contributions or conclusion until data exist.
- Run `./summarize.py` any time to see what is still "Not yet measured".

---

## 4. Quick checklist

- [ ] E18 - build capture mode, capture 400 frames, annotate, score
- [ ] E16 - media isolation, 3 conditions x 30
- [ ] E5  - glass-to-glass delay, 3 conditions x 20
- [ ] E4  - dead-man physical stop, 20 trials at 240 fps
- [ ] E13 - field trial, 10 runs (needs a fixed course)
- [ ] E17 - victim communication, 90 trials (needs ethics + robot touch input)
