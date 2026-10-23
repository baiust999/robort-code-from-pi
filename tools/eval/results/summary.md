# Measured results

Generated from `/home/pi/robot/tools/eval/results` by tools/eval/summarize.py. Every figure below is a measurement on the assembled robot.

## Section 5.1

### Command confirmation latency over the real control path (telemetry-confirmed metrics are upper bounds: 700 ms quantisation; deadman_panic is not)

Source: `latency.csv`, 420 raw rows.

| metric | label | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| deadman_panic | on-pi-2026-10-21 | latency (ms) | 30 | 2079.12 | 27.94 | 2022.3 | 2122.3 | 2076.45 | 2120.82 |
| deadman_trip | on-pi | latency (ms) | 30 | 2409.13 | 115.07 | 2200.9 | 2598.4 | 2409.7 | 2584.05 |
| deadman_trip | on-pi-2026-10-21 | latency (ms) | 30 | 2435.89 | 110.8 | 2197.5 | 2593.2 | 2467.45 | 2582.8 |
| hello_rtt | on-pi | latency (ms) | 30 | 46.83 | 24.57 | 19.6 | 116.9 | 41.0 | 75.78 |
| hello_rtt | on-pi-2026-10-21 | latency (ms) | 30 | 137.99 | 59.67 | 30.1 | 255.9 | 115.9 | 247.66 |
| motor_start | on-pi | latency (ms) | 30 | 328.22 | 136.09 | 156.8 | 761.1 | 306.3 | 573.51 |
| motor_start | on-pi-2026-10-21 | latency (ms) | 30 | 275.43 | 62.9 | 180.1 | 434.1 | 264.3 | 383.34 |
| motor_start | on-pi-phaselocked | latency (ms) | 30 | 407.09 | 62.82 | 266.2 | 504.9 | 393.9 | 496.0 |
| motor_stop | on-pi | latency (ms) | 30 | 314.35 | 79.97 | 207.9 | 606.7 | 300.0 | 393.92 |
| motor_stop | on-pi-2026-10-21 | latency (ms) | 30 | 302.91 | 57.64 | 195.5 | 385.6 | 312.25 | 381.4 |
| motor_stop | on-pi-phaselocked | latency (ms) | 30 | 403.3 | 19.89 | 392.6 | 507.2 | 400.7 | 405.65 |
| pan_echo | on-pi | latency (ms) | 30 | 387.72 | 60.4 | 285.9 | 495.0 | 381.1 | 480.79 |
| pan_echo | on-pi-2026-10-21 | latency (ms) | 30 | 389.61 | 79.72 | 265.6 | 637.1 | 378.2 | 481.69 |
| pan_echo | on-pi-phaselocked | latency (ms) | 30 | 492.08 | 82.9 | 150.3 | 609.8 | 500.25 | 607.02 |

### Emergency-stop stopping distance

Source: `estop.csv`, 23 raw rows.

| speed_pwm | surface | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|---|
| 120 | concrete | distance (cm) | 9 | 75.89 | 18.68 | 34.0 | 92.0 | 78.0 | 91.2 |
| 180 | concrete | distance (cm) | 7 | 91.29 | 6.65 | 78.0 | 98.0 | 92.0 | 97.7 |
| 60 | concrete | distance (cm) | 7 | 42.71 | 6.78 | 34.0 | 54.0 | 41.0 | 52.2 |

## Section 5.3

### Wi-Fi range and link degradation

Source: `network.csv`, 6 raw rows.

| label | distance_m | obstacles | loss_pct | rtt_avg_ms | rtt_max_ms | rtt_mdev_ms | signal_dbm_start | tx_bitrate_mbps |
|---|---|---|---|---|---|---|---|---|
| N1 | 5 | none | 0.0 | 3.373 | 17.981 | 3.608 | -41.0 | 72.2 |
| N2 | 10 | none | 0.0 | 5.342 | 30.884 | 6.172 | -39.0 | 72.2 |
| N3 | 15 | none | 0.0 | 5.738 | 41.687 | 8.206 | -41.0 | 65.0 |
| N4 | 20 | none | 0.0 | 5.276 | 37.101 | 6.701 | -40.0 | 72.2 |
| N5 | 25 | none | 0.0 | 4.77 | 31.714 | 6.531 | -42.0 | 72.2 |
| N6 | 50 | none | 0.0 | 3.467 | 25.388 | 3.869 | -41.0 | 72.2 |

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

### Manually injected faults: health transitions

Source: `fault_watch.csv`, 94 raw rows.

| label | t_s | field | from_value | to_value | held_s |
|---|---|---|---|---|---|
| F6-arduino-unplug | 4.70 | serial_connected | 1 | 0 | 4.70 |
| F7-wifi-drop | 26.85 | ws_clients | 1 | 0 | 26.85 |
| F7-wifi-drop | 28.76 | ws_clients | 0 | 1 | 1.91 |
| F9-gps-loss | 65.23 | ws_clients | 1 | 0 | 65.23 |
| F9-gps-loss | 65.23 | active_streams | 1 | 0 | 65.23 |
| F9-gps-loss | 66.09 | ws_clients | 0 | 1 | 0.87 |
| F9-gps-loss | 66.34 | active_streams | 0 | 1 | 1.11 |
| F9-gps-loss | 317.58 | active_streams | 1 | 0 | 251.24 |
| F9-gps-loss | 318.45 | active_streams | 0 | 1 | 0.87 |
| F9-gps-loss | 478.22 | active_streams | 1 | 0 | 159.78 |
| F9-gps-loss | 479.06 | active_streams | 0 | 1 | 0.83 |
| F9-gps-loss | 834.42 | active_streams | 1 | 0 | 355.36 |
| F9-gps-loss | 834.59 | active_streams | 0 | 1 | 0.17 |
| F9-gps-loss | 1306.57 | gps_fix | 0 | 1 | 1306.57 |
| F9-gps-loss | 1316.48 | gps_fix | 1 | 0 | 9.91 |
| F9-gps-loss | 1322.88 | gps_fix | 0 | 1 | 6.4 |
| F9-gps-loss | 1349.57 | gps_fix | 1 | 0 | 26.69 |
| F9-gps-loss | 1355.59 | gps_fix | 0 | 1 | 6.02 |
| F9-gps-loss | 1360.59 | gps_fix | 1 | 0 | 5.0 |
| F9-gps-loss | 1368.6 | gps_fix | 0 | 1 | 8.01 |
| F9-gps-loss | 1413.6 | gps_fix | 1 | 0 | 45.0 |
| F9-gps-loss | 1509.55 | gps_fix | 0 | 1 | 95.95 |
| F9-gps-loss | 1546.82 | gps_fix | 1 | 0 | 37.27 |
| F9-gps-loss | 1551.56 | gps_fix | 0 | 1 | 4.73 |
| F9-gps-loss | 1578.61 | gps_fix | 1 | 0 | 27.06 |
| F9-gps-loss | 1592.64 | gps_fix | 0 | 1 | 14.03 |
| F9-gps-loss | 1606.56 | gps_fix | 1 | 0 | 13.92 |
| F9-gps-loss | 1610.8 | gps_fix | 0 | 1 | 4.24 |
| F9-gps-loss-run2 | 0.39 | gps_fix | 0 | 1 | 0.39 |
| F9-gps-loss-run2 | 1.78 | gps_fix | 1 | 0 | 1.39 |
| F9-gps-loss-run2 | 16.43 | gps_fix | 0 | 1 | 14.65 |
| F9-gps-loss-run2 | 21.31 | gps_fix | 1 | 0 | 4.89 |
| F9-gps-loss-run2 | 27.45 | gps_fix | 0 | 1 | 6.13 |
| F9-gps-loss-run2 | 42.65 | gps_fix | 1 | 0 | 15.2 |
| F9-gps-loss-run2 | 49.39 | gps_fix | 0 | 1 | 6.74 |
| F9-gps-loss-run2 | 90.75 | gps_fix | 1 | 0 | 41.37 |
| F9-gps-loss-run2 | 95.39 | gps_fix | 0 | 1 | 4.64 |
| F9-gps-loss-run2 | 120.83 | gps_fix | 1 | 0 | 25.44 |
| F9-gps-loss-run2 | 125.46 | gps_fix | 0 | 1 | 4.63 |
| F9-gps-loss-run2 | 148.9 | gps_fix | 1 | 0 | 23.44 |
| F9-gps-loss-run2 | 153.66 | gps_fix | 0 | 1 | 4.75 |
| F9-gps-loss-run2 | 185.33 | gps_fix | 1 | 0 | 31.68 |
| F9-gps-loss-run2 | 190.34 | gps_fix | 0 | 1 | 5.01 |
| F9-gps-loss-run2 | 191.35 | gps_fix | 1 | 0 | 1.01 |
| F9-gps-loss-run2 | 194.35 | gps_fix | 0 | 1 | 3.01 |
| F9-gps-loss-run2 | 233.32 | gps_fix | 1 | 0 | 38.97 |
| F9-gps-loss-run2 | 238.34 | gps_fix | 0 | 1 | 5.01 |
| F9-gps-loss-run2 | 249.36 | gps_fix | 1 | 0 | 11.03 |
| F9-gps-loss-run2 | 261.39 | gps_fix | 0 | 1 | 12.03 |
| F9-gps-loss-run2 | 307.29 | gps_fix | 1 | 0 | 45.89 |
| F9-gps-loss-run2 | 311.54 | gps_fix | 0 | 1 | 4.25 |
| F9-gps-loss-run2 | 327.83 | gps_fix | 1 | 0 | 16.28 |
| F9-gps-loss-run2 | 332.46 | gps_fix | 0 | 1 | 4.63 |
| F9-gps-loss-run2 | 351.54 | gps_fix | 1 | 0 | 19.08 |
| F9-gps-loss-run2 | 355.52 | gps_fix | 0 | 1 | 3.98 |
| F9-gps-loss-run2 | 465.38 | gps_fix | 1 | 0 | 109.86 |
| F9-gps-loss-run2 | 469.53 | gps_fix | 0 | 1 | 4.16 |
| F9-gps-loss-run2 | 488.54 | gps_fix | 1 | 0 | 19.01 |
| F9-gps-loss-run2 | 493.43 | gps_fix | 0 | 1 | 4.89 |
| F9-gps-loss-run2 | 512.34 | gps_fix | 1 | 0 | 18.91 |
| F9-gps-loss-run2 | 516.51 | gps_fix | 0 | 1 | 4.17 |
| F9-gps-loss-run2 | 1234.33 | gps_fix | 1 | 0 | 717.82 |
| F9-gps-loss-run2 | 1244.35 | gps_fix | 0 | 1 | 10.02 |
| F9-gps-loss-run2 | 1246.36 | gps_fix | 1 | 0 | 2.01 |
| F9-gps-loss-run2 | 1250.37 | gps_fix | 0 | 1 | 4.01 |
| F9-indoor | 45.84 | gps_fix | 1 | 0 | 45.84 |
| F9-indoor | 136.81 | gps_fix | 0 | 1 | 90.97 |
| F9-indoor | 157.76 | gps_fix | 1 | 0 | 20.95 |
| F9-indoor | 173.79 | gps_fix | 0 | 1 | 16.03 |
| F9-indoor | 198.97 | gps_fix | 1 | 0 | 25.18 |
| F9-indoor | 216.88 | gps_fix | 0 | 1 | 17.91 |
| F9-indoor | 330.76 | gps_fix | 1 | 0 | 113.88 |
| F9-indoor | 331.89 | gps_fix | 0 | 1 | 1.13 |
| F9-indoor | 333.77 | gps_fix | 1 | 0 | 1.88 |
| F9-indoor | 415.86 | gps_fix | 0 | 1 | 82.09 |
| F9-indoor | 954.76 | gps_fix | 1 | 0 | 538.89 |
| F9-indoor | 956.88 | gps_fix | 0 | 1 | 2.13 |
| F9-indoor | 958.77 | gps_fix | 1 | 0 | 1.88 |
| F9-indoor | 3781.88 | p1_up | 1 | 0 | 3781.88 |
| F9-indoor | 3781.88 | serial_connected | 1 |  | 3781.88 |
| F9-indoor | 3781.88 | gps_fix | 0 |  | 2823.11 |
| F9-indoor | 3781.88 | ws_clients | 1 |  | 3781.88 |
| F9-indoor | 3782.23 | p1_up | 0 | 1 | 0.35 |
| F9-indoor | 3782.23 | serial_connected |  | 1 | 0.35 |
| F9-indoor | 3782.23 | gps_fix |  | 0 | 0.35 |
| F9-indoor | 3782.23 | ws_clients |  | 1 | 0.35 |
| F9-indoor | 3790.64 | p1_up | 1 | 0 | 8.41 |
| F9-indoor | 3790.64 | serial_connected | 1 |  | 8.41 |
| F9-indoor | 3790.64 | gps_fix | 0 |  | 8.41 |
| F9-indoor | 3790.64 | ws_clients | 1 |  | 8.41 |
| F9-indoor | 3791.42 | p1_up | 0 | 1 | 0.78 |
| F9-indoor | 3791.42 | serial_connected |  | 1 | 0.78 |
| F9-indoor | 3791.42 | gps_fix |  | 0 | 0.78 |
| F9-indoor | 3791.42 | ws_clients |  | 1 | 0.78 |

## Section 5.5

### Resource utilisation on the Raspberry Pi 4 (per-process CPU is % of one core)

Source: `resources.csv`, 3608 raw rows.

| condition | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|
| driving | total CPU (%) | 309 | 20.7 | 8.66 | 9.7 | 61.2 | 18.5 | 40.98 |
| driving | P1 CPU (%) | 309 | 3.74 | 0.96 | 2.0 | 8.0 | 4.0 | 5.0 |
| driving | P2 CPU (%) | 309 | 1.12 | 1.37 | 0.0 | 8.0 | 1.0 | 2.0 |
| driving | P3 CPU (%) | 309 | 0.12 | 0.34 | 0.0 | 2.0 | 0.0 | 1.0 |
| driving | memory used (MB) | 309 | 2429.29 | 31.48 | 2355.8 | 2508.5 | 2434.8 | 2478.24 |
| driving | SoC temp (C) | 309 | 48.04 | 0.83 | 45.8 | 51.6 | 48.2 | 49.2 |
| driving | uplink (kbps) | 309 | 923.71 | 506.87 | 97.4 | 2499.9 | 1152.2 | 1528.44 |
| driving+media | total CPU (%) | 299 | 20.76 | 3.89 | 15.9 | 45.4 | 19.6 | 28.04 |
| driving+media | P1 CPU (%) | 299 | 3.81 | 0.64 | 2.0 | 6.0 | 4.0 | 5.0 |
| driving+media | P2 CPU (%) | 299 | 62.92 | 3.91 | 58.9 | 92.0 | 62.0 | 71.0 |
| driving+media | P3 CPU (%) | 299 | 0.1 | 0.3 | 0.0 | 1.0 | 0.0 | 1.0 |
| driving+media | memory used (MB) | 299 | 2271.73 | 26.72 | 2231.2 | 2304.6 | 2286.6 | 2303.3 |
| driving+media | SoC temp (C) | 299 | 49.53 | 0.56 | 48.2 | 51.6 | 49.7 | 50.1 |
| driving+media | uplink (kbps) | 299 | 1124.61 | 18.38 | 1074.4 | 1193.0 | 1127.1 | 1147.45 |
| driving+media-16kbps | total CPU (%) | 299 | 22.98 | 8.35 | 15.9 | 73.9 | 20.5 | 42.02 |
| driving+media-16kbps | P1 CPU (%) | 299 | 3.85 | 0.94 | 2.0 | 8.0 | 4.0 | 5.0 |
| driving+media-16kbps | P2 CPU (%) | 299 | 64.51 | 4.33 | 59.0 | 85.0 | 63.0 | 74.0 |
| driving+media-16kbps | P3 CPU (%) | 299 | 0.11 | 0.31 | 0.0 | 1.0 | 0.0 | 1.0 |
| driving+media-16kbps | memory used (MB) | 299 | 1962.02 | 29.69 | 1932.8 | 2061.9 | 1947.4 | 2032.1 |
| driving+media-16kbps | SoC temp (C) | 299 | 49.22 | 0.78 | 47.7 | 52.6 | 49.2 | 50.6 |
| driving+media-16kbps | uplink (kbps) | 299 | 1195.19 | 559.87 | 1050.7 | 6396.0 | 1104.2 | 1180.58 |
| driving+media-throttled | total CPU (%) | 299 | 68.46 | 7.69 | 51.6 | 96.7 | 66.9 | 85.4 |
| driving+media-throttled | P1 CPU (%) | 299 | 8.79 | 0.91 | 6.0 | 11.0 | 9.0 | 10.0 |
| driving+media-throttled | P2 CPU (%) | 299 | 118.1 | 7.59 | 81.9 | 131.0 | 120.0 | 125.37 |
| driving+media-throttled | P3 CPU (%) | 299 | 0.22 | 0.45 | 0.0 | 2.0 | 0.0 | 1.0 |
| driving+media-throttled | memory used (MB) | 299 | 2223.2 | 24.88 | 2154.4 | 2269.0 | 2227.0 | 2261.45 |
| driving+media-throttled | SoC temp (C) | 299 | 46.43 | 0.59 | 44.8 | 48.2 | 46.3 | 47.2 |
| driving+media-throttled | uplink (kbps) | 299 | 1367.06 | 93.69 | 1140.6 | 1705.7 | 1366.3 | 1515.28 |
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

- under-voltage seen [driving]: 0/309 samples
- under-voltage seen [driving+media]: 0/299 samples
- under-voltage seen [driving+media-16kbps]: 0/299 samples
- under-voltage seen [driving+media-throttled]: 299/299 samples
- under-voltage seen [idle]: 0/1799 samples
- under-voltage seen [idle-partial-10min]: 0/603 samples

- throttled samples [driving]: 0/309 samples
- throttled samples [driving+media]: 0/299 samples
- throttled samples [driving+media-16kbps]: 0/299 samples
- throttled samples [driving+media-throttled]: 276/299 samples
- throttled samples [idle]: 0/1799 samples
- throttled samples [idle-partial-10min]: 0/603 samples

## Section 5.6

### Ultrasonic range error by true distance

Source: `ultrasonic.csv`, 50 raw rows.

| true_cm | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|
| 150 | error (cm) | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 150 | reading (cm) | 10 | 150.0 | 0.0 | 150.0 | 150.0 | 150.0 | 150.0 |
| 20 | error (cm) | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 20 | reading (cm) | 10 | 20.0 | 0.0 | 20.0 | 20.0 | 20.0 | 20.0 |
| 284 | error (cm) | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 284 | reading (cm) | 10 | 284.0 | 0.0 | 284.0 | 284.0 | 284.0 | 284.0 |
| 389 | error (cm) | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 389 | reading (cm) | 10 | 389.0 | 0.0 | 389.0 | 389.0 | 389.0 | 389.0 |
| 75 | error (cm) | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 75 | reading (cm) | 10 | 75.0 | 0.0 | 75.0 | 75.0 | 75.0 | 75.0 |

### Temperature and humidity error vs reference instrument (DHT11)

Source: `dht11_environmental.csv`, 5 raw rows.

| measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|
| temp error (C) | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| humidity error (%RH) | 5 | 0.4 | 0.55 | 0.0 | 1.0 | 0.0 | 1.0 |

### Gas sensor response (raw ADC counts, uncalibrated)

Source: `gas.csv`, 5 raw rows.

| source | measure | n | mean | sd | min | max | median | p95 |
|---|---|---|---|---|---|---|---|---|
| butane-lighter-5cm | rise (ADC) | 5 | 697.2 | 72.94 | 616.0 | 809.0 | 684.0 | 791.0 |
| butane-lighter-5cm | time to warn (s) | 5 | 2.2 | 1.1 | 1.0 | 4.0 | 2.0 | 3.6 |

### Static GPS accuracy

Source: `gps_static.csv`, 1 raw row.

| label | n_samples | duration_min | ref_mode | mean_m | sd_m | rms_m | cep50_m | cep95_m | max_m | mean_sats |
|---|---|---|---|---|---|---|---|---|---|---|
| archive-2026-09-29 | 6888 | 129.1 | centroid | 14.14 | 10.45 | 17.58 | 8.9 | 30.46 | 120.4 | 4.8 |

## Not yet measured

- [ ] 5.1 Control latency, 240 fps video (key press -> wheel motion) (`latency_video.csv`)
- [ ] 5.1 Dead-man wheel-stop time (bound about 2.06 s: 2000 ms window + 10 ms supervisor period + one loop pass) (`deadman_physical.csv`)
- [ ] 5.2 End-to-end video delay (`glass2glass.csv`)
- [ ] 5.7 End-to-end rescue runs (`field.csv`)
- [ ] 5.8 Operator usability (System Usability Scale) (`sus.csv`)
- [ ] 4-5 Hardware and integration checklist (TEST_REPORT sections 4 and 5) (`checklist.csv`)

