# Experiments: What Is Done and What Is Left

This file explains the experiments of the rescue robot project in simple English.
Last checked: 2026-11-23. Sources: `research paper/section5_results.md` (Table 5.0),
`research paper/section4_experimental_setup.md` (Table 4.2) and `tools/eval/README.md`.

Important rule: **never change a pass rule after you see the data.** Each pass rule
below was fixed before the test. If the robot fails, you report the failure.

---

## 1. Experiments that are DONE

| Experiment | What it measured | Status |
|---|---|---|
| E1 | Delay between a command and the robot confirming it (WebSocket), and the dead-man interval | Done. Latencies are upper bounds (up to 700 ms extra, because telemetry is slow). Dead-man interval: mean 2022.5 ms, max 2042 ms. |
| E6 | Wi-Fi range | Done (partial design). 16 line-of-sight stations, 5-250 m, one ping burst each. No failure point was reached and no obstacles were tested. |
| E7 | Fault tests (kill a process, watchdog restarts it) | Done. 30 of 30 SIGKILL trials recovered. Manual faults F6 (USB unplug) and F7 (Wi-Fi drop) run once each. |
| E8 | CPU / resource use (idle, driving, driving + media) | Done. The 16 kbps Opus run is confounded by a P2 restart; it is not used for any claim. |
| E9 | GPS drift | Done, but weak: GPS in the log has only 4 decimal places. |
| E15 | Cost | Done. 37,158 BDT, about USD 310. Webcam, speaker and Pi power bank are not itemised. |

Also done (supporting evidence, not numbered experiments): the Pi unit-test suite, the
native firmware dead-man test, and the Monte Carlo heartbeat-loss simulation.

---

## 2. Experiments NOT done yet (3 of them)

These three are kept because each one tests a contribution of the paper directly:
E4 tests C1 (firmware stop), E16 tests C2 (process split), E5 tests C3 (media path).

Recommended order: **E16, E5, then E4.**

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

## 3. Experiments removed from the paper

| Experiment | Why it was removed |
|---|---|
| E13 Field trial | Not run. Needs ethics approval and a second person. Removed 2026-11-23. |
| E17 Victim communication study (15 participants) | Not run. Needs ethics approval, 15 participants and a robot touch screen. It tests operator aids that are outside the paper's contributions. Removed 2026-11-23. |
| E18 Person detector test | Not run. Outside the paper's contributions. Removed 2026-11-23. |
| E2 Wi-Fi latency (240 fps), E14 SUS usability, dead-man/watchdog-off ablations | Removed 2026-11-01. |
| E3 E-stop distance, E10 ultrasonic, E11 DHT11, E12 gas | Removed 2026-11-03 (hand-entered sheets, not backed by logs). |

The features behind E17 and E18 (person detector, voice message, tap-to-answer
questions) still exist in the code. Evaluating them is **future work**, not part of this
paper. The detector scoring tools (`tools/eval/detector_*.py`) are kept for that later work.
The old result files (`bench_motor.csv`, `estop*.csv`, `ultrasonic.csv`, `dht11_environmental.csv`,
`gas.csv`) are kept as a record but are not cited.

---

## 4. General rules for every experiment

- One trial is not a result. Always report n, mean and SD.
- Do all runs on a stable power supply. Check `under_voltage_ever`; if the supply sagged, rerun.
- Logs rotate. Copy the log window you use into `tools/eval/results/log_excerpts/`.
- After new data, rerun `tools/eval/section5_stats.py --out tools/eval/results/section5_stats.md`.
- Do not change a pass rule after seeing data.
- Failures go into the paper too. A failed test is still a result.
- Do not add unmeasured claims to the abstract, contributions or conclusion until data exist.
- Run `./summarize.py` any time to see what is still "Not yet measured".

---

## 5. Quick checklist

- [ ] E16 - media isolation, 3 conditions x 30
- [ ] E5  - glass-to-glass delay, 3 conditions x 20
- [ ] E4  - dead-man physical stop, 20 trials at 240 fps
