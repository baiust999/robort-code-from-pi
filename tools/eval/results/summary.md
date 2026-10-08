# Measured results

Generated from `/home/pi/robot/tools/eval/results` by tools/eval/summarize.py. Every figure below is a measurement on the assembled robot.

## Section 5.1

### Command confirmation latency over the real control path (upper bound: 200 ms telemetry quantisation)

Source: `latency.csv`, 240 raw rows.

| metric | label | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| deadman_trip | on-pi | latency (ms) | 30 | 2409.13 | 115.07 | 2200.9 | 2598.4 | 2409.7 | 2584.05 |
| hello_rtt | on-pi | latency (ms) | 30 | 46.83 | 24.57 | 19.6 | 116.9 | 41.0 | 75.78 |
| motor_start | on-pi | latency (ms) | 30 | 328.22 | 136.09 | 156.8 | 761.1 | 306.3 | 573.51 |
| motor_start | on-pi-phaselocked | latency (ms) | 30 | 407.09 | 62.82 | 266.2 | 504.9 | 393.9 | 496.0 |
| motor_stop | on-pi | latency (ms) | 30 | 314.35 | 79.97 | 207.9 | 606.7 | 300.0 | 393.92 |
| motor_stop | on-pi-phaselocked | latency (ms) | 30 | 403.3 | 19.89 | 392.6 | 507.2 | 400.7 | 405.65 |
| pan_echo | on-pi | latency (ms) | 30 | 387.72 | 60.4 | 285.9 | 495.0 | 381.1 | 480.79 |
| pan_echo | on-pi-phaselocked | latency (ms) | 30 | 492.08 | 82.9 | 150.3 | 609.8 | 500.25 | 607.02 |

## Section 5.4

### Fault injection and automatic recovery

Source: `faults.csv`, 30 raw rows.

| test_id | fault | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| F3 | p1 | recovery (ms) | 10 | 16026.7 | 140.62 | 15804.4 | 16254.8 | 15989.95 | 16223.7 |
| F3 | p1 | detection (ms) | 10 | 91.11 | 34.8 | 59.2 | 182.8 | 80.7 | 145.32 |
| F4 | p2 | recovery (ms) | 10 | 14450.44 | 961.17 | 12966.8 | 15914.9 | 14758.35 | 15600.89 |
| F4 | p2 | detection (ms) | 10 | 123.24 | 46.12 | 59.8 | 175.0 | 147.1 | 168.56 |
| F5 | p3 | recovery (ms) | 10 | 12828.97 | 903.34 | 10428.5 | 13841.4 | 12997.95 | 13619.24 |
| F5 | p3 | detection (ms) | 10 | 156.97 | 40.29 | 61.3 | 216.0 | 156.55 | 205.47 |

- recovered [F3 / p1]: **10/10**
- recovered [F4 / p2]: **10/10**
- recovered [F5 / p3]: **10/10**

## Section 5.5

### Resource utilisation on the Raspberry Pi 4 (per-process CPU is % of one core)

Source: `resources.csv`, 2402 raw rows.

| condition | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|
| idle | total CPU (%) | 1799 | 14.44 | 15.67 | 1.0 | 91.4 | 10.2 | 46.11 |
| idle | P1 CPU (%) | 1799 | 2.89 | 1.09 | 1.0 | 8.0 | 3.0 | 5.0 |
| idle | P2 CPU (%) | 1799 | 0.9 | 0.54 | 0.0 | 3.0 | 1.0 | 2.0 |
| idle | P3 CPU (%) | 1799 | 0.12 | 0.33 | 0.0 | 2.0 | 0.0 | 1.0 |
| idle | memory used (MB) | 1799 | 1906.94 | 97.25 | 1785.2 | 2134.7 | 1896.0 | 2081.02 |
| idle | SoC temp (C) | 1799 | 45.21 | 1.81 | 41.4 | 52.1 | 45.3 | 48.2 |
| idle | uplink (kbps) | 1799 | 535.33 | 1122.29 | 0.0 | 10707.1 | 6.6 | 2656.2 |
| idle-partial-10min | total CPU (%) | 603 | 33.47 | 20.05 | 1.5 | 95.9 | 30.4 | 88.18 |
| idle-partial-10min | P1 CPU (%) | 603 | 4.62 | 1.66 | 1.0 | 11.0 | 5.0 | 8.0 |
| idle-partial-10min | P2 CPU (%) | 603 | 26.64 | 29.47 | 0.0 | 97.0 | 10.0 | 83.81 |
| idle-partial-10min | P3 CPU (%) | 603 | 0.16 | 0.4 | 0.0 | 2.0 | 0.0 | 1.0 |
| idle-partial-10min | memory used (MB) | 603 | 2341.81 | 171.15 | 2023.2 | 2520.1 | 2471.1 | 2507.88 |
| idle-partial-10min | SoC temp (C) | 603 | 47.2 | 1.69 | 43.8 | 52.6 | 47.2 | 51.05 |
| idle-partial-10min | uplink (kbps) | 603 | 803.32 | 1539.03 | 0.5 | 8473.9 | 127.0 | 5349.24 |

- under-voltage seen [idle]: 0/1799 samples
- under-voltage seen [idle-partial-10min]: 0/603 samples

- throttled samples [idle]: 0/1799 samples
- throttled samples [idle-partial-10min]: 0/603 samples

## Section 5.6

### Static GPS accuracy

Source: `gps_static.csv`, 1 raw row.

| label | n_samples | duration_min | ref_mode | mean_m | sd_m | rms_m | cep50_m | cep95_m | max_m | mean_sats |
|---|---|---|---|---|---|---|---|---|---|---|
| archive-2026-09-29 | 6888 | 129.1 | centroid | 14.14 | 10.45 | 17.58 | 8.9 | 30.46 | 120.4 | 4.8 |

## Not yet measured

- [ ] 5.1 Control latency, 240 fps video (key press -> wheel motion) (`latency_video.csv`)
- [ ] 5.1 Emergency-stop stopping distance (`estop.csv`)
- [ ] 5.1 Dead-man wheel-stop time (expected 2.0 s) (`deadman_physical.csv`)
- [ ] 5.2 End-to-end video delay (`glass2glass.csv`)
- [ ] 5.3 Wi-Fi range and link degradation (`network.csv`)
- [ ] 5.4 Manually injected faults: health transitions (`fault_watch.csv`)
- [ ] 5.6 Ultrasonic range error by true distance (`ultrasonic.csv`)
- [ ] 5.6 Temperature and humidity error vs reference instrument (`thermal.csv`)
- [ ] 5.6 Gas sensor response (raw ADC counts, uncalibrated) (`gas.csv`)
- [ ] 5.7 End-to-end rescue runs (`field.csv`)
- [ ] 5.8 Operator usability (System Usability Scale) (`sus.csv`)
- [ ] 4-5 Hardware and integration checklist (TEST_REPORT sections 4 and 5) (`checklist.csv`)

