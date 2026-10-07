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
- [ ] 5.4 Fault injection and automatic recovery (`faults.csv`)
- [ ] 5.4 Manually injected faults: health transitions (`fault_watch.csv`)
- [ ] 5.5 Resource utilisation on the Raspberry Pi 4 (per-process CPU is % of one core) (`resources.csv`)
- [ ] 5.6 Ultrasonic range error by true distance (`ultrasonic.csv`)
- [ ] 5.6 Temperature and humidity error vs reference instrument (`thermal.csv`)
- [ ] 5.6 Gas sensor response (raw ADC counts, uncalibrated) (`gas.csv`)
- [ ] 5.7 End-to-end rescue runs (`field.csv`)
- [ ] 5.8 Operator usability (System Usability Scale) (`sus.csv`)
- [ ] 4-5 Hardware and integration checklist (TEST_REPORT sections 4 and 5) (`checklist.csv`)

