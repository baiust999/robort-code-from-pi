# Evidence Map for manuscript.md

Every quantitative claim in `manuscript.md`, the file and line (or command)
it comes from, its evidence class and its status. Paths are relative to the
repository root (`/home/pi/robot`).

Conventions

- `S5STATS:n` = line n of `tools/eval/results/section5_stats.md`. That file
  is the output of `python3 tools/eval/section5_stats.py --out
  tools/eval/results/section5_stats.md`. It was regenerated on 2026-11-03,
  after the stopping-distance and bench-sensor blocks were removed from the
  script, and every figure used here was reproduced unchanged; the line
  numbers below are those of that version.
- `SUMMARY:n` = line n of `tools/eval/results/summary.md`.
- CSV `row k` = data row k (file line k+1, after the header).
- Classes: MEASURED, CALCULATED, PREDICTED, SIMULATED, SOFTWARE-TEST,
  PUBLISHED (from a cited source; checked against `research paper/citation.md`),
  DESIGN (a constant in the code), RECEIPT (authors' procurement record).
- Status: VERIFIED (traced to the raw file in this pass), FLAGGED (reported
  with [VERIFICATION REQUIRED]), AUTHOR (needs author input), PENDING.

## 1. Abstract, Introduction and Conclusion

| # | Claim | Value | Source | Class | Status |
|---|---|---|---|---|---|
| 1 | Drive removed within this time of the last command, 30 of 30 trials | max 2042 ms, mean 2022.5 ms | S5STATS:26, S5STATS:30; raw: `var/log/p1_events.log.1` window preserved in `tools/eval/results/log_excerpts/p1_events_2026-10-21_1100-1400.log.gz` matched to `tools/eval/results/latency.csv` rows with label `on-pi-2026-10-21` | CALCULATED from MEASURED | VERIFIED |
| 2 | Analytical stop bound | about 2060 ms | Eq. (1): `arduino/config.h:34` (2000 ms), `arduino/config.h:39` (10 ms), J about 50 ms from `arduino/config.h:37,38,92` and the DHT11 start pulse (Section III-E) | CALCULATED | VERIFIED |
| 3 | SIGKILL recovery 30 of 30; pooled Wilson lower bound | 30/30; 88.6% | S5STATS:39-42; raw `tools/eval/results/faults.csv` rows 1-30 | MEASURED / CALCULATED | VERIFIED |
| 4 | Mean recovery range | 12.8 to 16.0 s | S5STATS:39 (F3 16.03 s), S5STATS:41 (F5 12.83 s) | MEASURED | VERIFIED |
| 5 | P2 CPU with one operator media session | 62.92% of one core (abstract 62.9%, about 63%) | S5STATS:86; raw `tools/eval/results/resources.csv`, condition `driving+media` | MEASURED | VERIFIED |
| 6 | P1 CPU stays below 4% (near 4%) | 3.74% and 3.81%; upper CI 3.93% and 3.92% | S5STATS:81, S5STATS:85 | MEASURED | VERIFIED |
| 7 | Original power bank under-volted | 276 of 299 samples | Command: count of `under_voltage_now` in `resources.csv` condition `driving+media-throttled` (run 2026-11-01: 276/299; other conditions 0) | MEASURED | VERIFIED |
| 8 | Cost | 37,158 BDT, about USD 310 at 120 BDT/USD | `research paper/section5_results.md` Table 5.15 (authors' receipts, not in the repository) | RECEIPT | AUTHOR (deposit receipts; confirm FX rate and date) |
| 9 | EM-DAT 2025 | 358 disasters, 16,607 deaths, 110.2 million affected | [cred2026]; `research paper/citation.md` | PUBLISHED | VERIFIED (ledger) |
| 10 | Time from discovery to extrication | 4 to 10 h | [srinivasan2012] | PUBLISHED | VERIFIED (ledger) |
| 11 | Control-path upper bounds (Conclusion) | 275 to 390 ms | S5STATS:14-21 (means 275.4 to 389.6) | MEASURED | VERIFIED |
| 12 | Link usable by judgement to at least this distance | 250 m | `tools/eval/results/network.csv` row 10 (N10) | MEASURED (operator judgement) | VERIFIED |
| 13 | Wi-Fi stop during injected outage | 2.02 s | S5STATS:119-120 | MEASURED | VERIFIED |

## 2. Section II (literature figures)

| # | Claim | Value | Source | Class | Status |
|---|---|---|---|---|---|
| 14 | Kareem review corpus | 74 papers, 2016-2024 | [kareem2026]; citation.md | PUBLISHED | VERIFIED (ledger) |
| 15 | Sinha review corpus | more than 190 studies | [sinha2026]; citation.md | PUBLISHED | VERIFIED (ledger) |
| 16 | QUADRESCUE control range | 200 m | [deshmukh2025] | PUBLISHED | VERIFIED (ledger) |
| 17 | Platforms described as low-cost without a figure | 5 | [verano2022; pramono2024; kim2023; raghavan2026; deshmukh2025]; source Section 2.2 | PUBLISHED | VERIFIED (source text) |
| 18 | Survivor Buddy cost | USD 3,600 (v1.0), USD 1,800 (v2.0) | [murphy2011] Table II | PUBLISHED | VERIFIED (ledger) |
| 19 | Survivor Buddy v2 | 50% less expensive, 78% lighter | [murphy2011] | PUBLISHED | VERIFIED (ledger) |
| 20 | ArduPilot failsafe defaults | 1 s radio, 5 s GCS | [ardupilot_rover_failsafe] | PUBLISHED | VERIFIED (ledger) |
| 21 | Victim assessment distance | about 3 m | [bethel2007] | PUBLISHED | VERIFIED (ledger) |
| 22 | WebRTC dental robot latency | below 50 ms | [shi2025webrtc] | PUBLISHED | VERIFIED (ledger) |
| 23 | Opus frame sizes | 2.5 to 60 ms; 20 ms recommended | [valin2012] RFC 6716 | PUBLISHED | VERIFIED |
| 24 | IEC 60204-1 category 0 | immediate removal of power | [iec60204] | PUBLISHED | VERIFIED (ledger) |

## 3. Section III (design constants)

| # | Claim | Value | Source | Class | Status |
|---|---|---|---|---|---|
| 25 | Dead-man window, inclusive trip | 2000 ms, `>=` | `arduino/config.h:34`; `arduino/arduino.ino:79` | DESIGN | VERIFIED |
| 26 | Supervisor and motor service period | 10 ms | `arduino/config.h:39`; `arduino/arduino.ino:122-123` | DESIGN | VERIFIED |
| 27 | Telemetry and status-line periods | 500 ms, 1000 ms | `arduino/config.h:35-36` | DESIGN | VERIFIED |
| 28 | Fast and slow sensor periods; echo timeout | 50 ms, 2000 ms; 25 ms | `arduino/config.h:37-38, 92` | DESIGN | VERIFIED |
| 29 | Ramp step; ramp time from 180 | 15; 120 ms | `arduino/config.h:61`; Eq. (2) | DESIGN / CALCULATED | VERIFIED |
| 30 | Serial baud; receive buffer; max command length | 115200; 32 B; 31 chars | `arduino/config.h:27-28` | DESIGN | VERIFIED |
| 31 | P1 speed cap | 180 of 255 | `pi/common/protocol.py:62` | DESIGN | VERIFIED |
| 32 | Average motor voltage at the cap | 10.4 V (180/255 x 14.8 V) | Arithmetic from #31 and the 14.8 V nominal pack | CALCULATED | VERIFIED |
| 33 | Dashboard heartbeat period | 500 ms | `dashboard/src/lib/protocol.ts:11` | DESIGN | VERIFIED |
| 34 | Operator telemetry timeout | 3000 ms | `pi/common/protocol.py:136`; `dashboard/src/lib/protocol.ts:12` | DESIGN | VERIFIED |
| 35 | P1 broadcast period; ring buffer; replay depth | 200 ms; 300; 60 s | `pi/common/protocol.py:120, 132`; Eq. (3) | DESIGN / CALCULATED | VERIFIED |
| 36 | Confirmation delay | up to 700 ms, about 350 ms mean | 500 + 200 ms (#27, #35); mean as half of each period | CALCULATED | VERIFIED |
| 37 | WebSocket keep-alive | 20 s ping, 20 s timeout | `pi/p1_control/main.py:595-596` | DESIGN | VERIFIED |
| 38 | P1 start-up handshake | 2.0 s wait, 3 x S at 0.2 s, 5 s timeout | `pi/common/protocol.py:22-25` | DESIGN | VERIFIED |
| 39 | P3 exit poll; cooldown | 1 s; 10 s | `pi/p3_watchdog/supervisor.py:26-27` | DESIGN | VERIFIED |
| 40 | Health check interval, timeout, miss limit | 10 s, 5 s, 3 | `pi/p3_watchdog/health.py:16-18` | DESIGN | VERIFIED |
| 41 | systemd restart delay for P3 | 5 s | `deploy/systemd/robot-watchdog.service:19` | DESIGN | VERIFIED |
| 42 | Recovery model window for P1 | 14.6 to 19.6 s | Eq. (4) from #38-#40 | PREDICTED | VERIFIED |
| 43 | Key lockout | 5 failures in 300 s, refused 300 s | `pi/common/access.py:27-28` | DESIGN | VERIFIED |
| 44 | Signal warning thresholds | -70 dBm, -80 dBm | `dashboard/src/lib/signal.ts:41-42` | DESIGN | VERIFIED |
| 45 | Opus bitrate, packet length, capture period | 32 kbit/s, 60 ms, 960 frames | `pi/p2_media/media.py:24, 28, 30` | DESIGN | VERIFIED |
| 46 | Packet rate reduction | 50 to 16.7 packets/s | 1000/20 and 1000/60 | CALCULATED | VERIFIED |
| 47 | Video parameters | 640x480, 10 fps, 500 kbit/s | `research paper/section3_methodology.md` Table 12 (P2 config) | DESIGN | VERIFIED (source); not re-read from code in this pass |
| 48 | GPS track step | 10 m | `pi/p1_control/gps_reader.py:29` | DESIGN | VERIFIED |
| 49 | Telemetry log GPS precision | 4 decimal places | `pi/p1_control/telemetry_log.py:131` | DESIGN | VERIFIED |
| 50 | NEO-6M datasheet CEP | 2.5 m (24 h static, -130 dBm) | [ublox_neo6] | PUBLISHED | VERIFIED |
| 51 | Battery | 4S3P, 12 x 18650 x 1500 mAh, 14.8 V, 4.5 Ah, 40 A BMS | `research paper/section3_methodology.md` Table 2; project memory `paper-master-cost-battery` | DESIGN | VERIFIED (source) |
| 52 | Motor rating | 60 RPM no-load, 12 V, 65 mm wheels | `research paper/section3_methodology.md` Table 2 | DESIGN | VERIFIED (source) |
| 53 | Throttling threshold | 80 deg C | [rpi_docs] | PUBLISHED | VERIFIED (ledger) |

## 4. Section V (results)

| # | Claim | Value | Source | Class | Status |
|---|---|---|---|---|---|
| 54 | Table IX row 1 | 2022.5 / 2019.7-2025.3 / 7.5 / 2009.0 / 2024.0 / 2042.0 ms | S5STATS:30 | CALCULATED | VERIFIED |
| 55 | Table IX row 2 | 2002.0 / 1998.7-2005.2 / 8.7 / 1986.0 / 2002.5 / 2022.0 ms | S5STATS:31 | CALCULATED | VERIFIED |
| 56 | Table IX row 3 | 20.5 / 18.8-22.2 / 4.6 / 6.0 / 21.0 / 29.0 ms | S5STATS:32 | CALCULATED | VERIFIED |
| 57 | E1 dead-man session speed | PWM 150 | `research paper/section5_results.md` Table 5.2a caption; `latency.csv` rows `on-pi-2026-10-21` | MEASURED | VERIFIED (source) |
| 58 | Telemetry-confirmed trip mean, SD; difference | 2435.9 ms, SD 110.8; 356.8 ms | S5STATS:11 (2435.9); SD from `research paper/section5_results.md` Table 5.2a; 2435.9 - 2079.1 = 356.8 (S5STATS:9) | MEASURED / CALCULATED | VERIFIED |
| 59 | Timestamp jitter of the method | about 15 ms | Spread 1986-2022 ms, S5STATS:31 | CALCULATED | VERIFIED |
| 60 | F7 times | last heartbeat 19:52:48.530; PANIC +2.02 s; close +23.16 s; reconnect +1.91 s | S5STATS:119-122; `log_excerpts/p1_events_2026-10-21_1940-1955.log.gz` | MEASURED | VERIFIED |
| 61 | Heartbeat gaps | 1.902, 1.988 s no trip; 2.080 s PANIC at 14:01:17.616 | S5STATS:128-130; `log_excerpts/p1_events_2026-10-22_1200-1402.log.gz` | MEASURED | VERIFIED |
| 62 | Table X heartbeat intervals | 5308/0.501; 84/0.997; 192/0.502; 80/1.000 and percentiles | `research paper/section5_results.md` Table 5.7d, from `var/log/p1_events.log.1` | MEASURED | VERIFIED (source); not in S5STATS. Recompute before submission |
| 63 | Native firmware test | 10 functions, 27 checks, all pass | `research-analysis/output/native_deadman_tests_2026-10-22.txt`; rerun `native_deadman_tests_rerun_2026-11-01.txt` | SOFTWARE-TEST | VERIFIED |
| 64 | Pi suite and supplementary tests | 121 and 25 | `research paper/section5_results.md` Table 5.3a; `research-analysis/test_inventory.md` | SOFTWARE-TEST | VERIFIED (source). The full suite is now 187 (2026-10-31); the manuscript cites 121 + 25 only |
| 65 | Table XI | tolerated losses 8/2/0/none; trip 0.05%, 6.84%, 42.04%, 82.34% | `research-analysis/sim/deadman_robustness_sim.py`; `research-analysis/output/deadman_sim_report.md`; source Tables 5.5b, 5.5c | SIMULATED | VERIFIED (source) |
| 66 | Table XII latencies | 8 means with CIs | S5STATS:12-21; motor_stop 2026-10-07 raw mean 314.35 ms (latency.csv), reported 314.4 as in S5STATS (source Table 5.1 had 314.3) | MEASURED | VERIFIED |
| 67 | Phase-locked motor_stop | median 400.7 ms; SD 19.9 vs 80.0 | S5STATS:19; SDs from source Tables 5.1 and 5.2 | MEASURED | VERIFIED |
| 68 | Table XIII | detection means, recovery means, CIs, SDs | S5STATS:39-41; SDs from source Table 5.6 | MEASURED | VERIFIED |
| 69 | Detection range | 59 to 216 ms | source Table 5.8 (min 59.2, max 216.0) from `faults.csv` | MEASURED | VERIFIED (source) |
| 70 | Ten serial re-opens during F3 | 10 | source Section 5.4; `log_excerpts/p1_events_2026-10-07_2100-2259.log.gz` | MEASURED | VERIFIED (source) |
| 71 | Failure probability bound | below 11.4% | 100% - 88.6% (S5STATS:42) | CALCULATED | VERIFIED |
| 72 | F6 | 0.11 s from first read failure to flag | S5STATS:117-118 | MEASURED | VERIFIED |
| 73 | Table XIV CPU means and CIs | all cells | S5STATS:72-90 | MEASURED / CALCULATED | VERIFIED |
| 74 | Table XIV SoC max | 52.1, 51.6, 51.6, 52.6, 48.2 deg C | SUMMARY (per-condition max); throttled 48.2 from `resources.csv` (command run 2026-11-01) | MEASURED | VERIFIED |
| 75 | Rows per condition; under-voltage | 1799, 309, 299, 299, 299; 0 or 276 | S5STATS:50-55; #7 | MEASURED | VERIFIED |
| 76 | Splice of driving+media | 2 runs 94 s apart; 196 s span; 103 s doubled; P2 means 63.01 and 62.87 | S5STATS:54, 69-70 | CALCULATED | VERIFIED |
| 77 | Memory use range | 1.9 to 2.5 GB | source Table 5.9 (1906.9 to 2429.3 MB means; max 2520.1) | MEASURED | VERIFIED (source) |
| 78 | P2 restart between 32 and 16 kbit/s captures | 20:23 UTC | `tools/eval/results/log_excerpts/p3_events_2026-10-21_2020-2029.log` | MEASURED | VERIFIED |
| 79 | Table XV range sweep | all cells | `tools/eval/results/network.csv` rows 1-16 (N1-N6, N7-N10, R1-R6 in file order) | MEASURED | VERIFIED |
| 80 | 17 dB difference at 5 m | -41 vs -58 dBm | `network.csv` rows 1 and 11 | CALCULATED | VERIFIED |
| 81 | Table XVI GPS | 6888 fixes, 129.1 min, 4.76 sats, 14.14/17.58/8.90/30.46/120.4 m, 53.1%, 61 | S5STATS:97; `log_excerpts/telemetry_2026-09-29_E9_window.csv` | MEASURED | VERIFIED (resolution-limited) |
| 82 | GPS grid and rounding RMS | 11.12 x 10.20 m; 4.36 m | S5STATS:101 | CALCULATED | VERIFIED |
| 83 | Track filter | 130 points, 1609 m, median 26.2 m; 2431 samples | S5STATS:134-135; `tools/eval/results/gps_track_live_2026-10-22.geojson` | MEASURED / CALCULATED | VERIFIED |
| 84 | BOM subsystem lines | 20,861 / 6,802 / 4,007 / 3,946 / 782 / 700 / 60 BDT | `research paper/section5_results.md` Table 5.19 | RECEIPT | AUTHOR (receipts not in repo) |
| 85 | Pi plus display share; motor drive share | about USD 174; about USD 57 | 20,861/120; 6,802/120 | CALCULATED | VERIFIED |

## 5. Claims deliberately not made

| Item | Reason |
|---|---|
| 5.7 "100-run" field-trial aggregate | No per-run data exist (no `field.csv`); kept out entirely. E13 is [PENDING MEASUREMENT] |
| Crash or uptime counts from P3 logs | Not reported. Any future count must exclude the deliberate deploy restarts (2026-10-29 to 10-31) and the 2026-10-30 16:04-16:14 UTC test-load kills listed in project memory |
| `bench_motor.csv` (60 rows) | Run on the floor under a false "wheels elevated" premise; not cited anywhere |
| Victim-finding aid performance | No measurement yet. E17 (victim channel) and E18 (detector) are [PENDING MEASUREMENT] with criteria fixed in Table XVII; victim marks and the session recording stay unevaluated. No figure in the manuscript rests on any of them |
| Wheel-stop time and the distance after it (E4), media quality (E5), media isolation (E16), field trial (E13), victim communication (E17), detector accuracy (E18) | Pending, each with a pass criterion fixed in advance (Table XVII). Wi-Fi control latency and usability: not evaluated (limitations) |
| `avi2026review` and its corpus statistics | Not cited (project rule) |
| OpenAlex hit counts from source Section 2 | Removed; the query results were not saved in the repository, so the counts cannot be traced |
