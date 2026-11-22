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

### E5 - Video and audio delay `[NOT RUN]`

- **Idea:** How old is the picture on the dashboard? Point the camera at a running stopwatch. Photograph the real stopwatch and the dashboard together.
- **Pass rule (only `viewers-1` decides):** median video delay <= 500 ms; median audio delay <= 400 ms each direction.
- **How:** 3 conditions x 20 trials: `viewers-1`, `viewers-2`, `wifi-20m`. `./record.py glass2glass label=viewers-1 real_ms=12480 robot_ms=12190`.
- **Open points:**
  - No method exists yet for **audio** delay (robot to operator, operator to robot). Decide first.
  - The 400 ms audio limit is "adopted". If you cite ITU-T G.114 as its basis, add and verify that reference first.
  - Frame rate and packet loss are also listed as outputs. No tool for them is described.
- **Paper place:** Tables 5.4 and 5.4a (empty).

### E4 - Dead-man physical stop `[NOT RUN]`

- **Idea:** Cut the command stream. Does the Arduino stop the wheels alone? Prove it on film.
- **Pass rule:** Robot on floor, PWM 180. Wheels still within 2.5 s of the last command in 20 of 20 trials. PANIC DEADMAN logged in 20 of 20.
- **How:** Film wheels at 240 fps with a tape measure on the floor. `./record.py deadman_physical speed_pwm=180 stop_s=2.1 panic_seen=1 distance_cm=6`. Count frames from last command to wheels still.
- **What exists already:** log result only: dead-man interval mean 2022.5 ms, max 2042 ms (this is when drive is removed, NOT when wheels stop).
- **If it fails:** paper can only claim "drive removed within 2042 ms".
- **Paper place:** Table 5.3 (empty).

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

## 9. Quick checklist

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
