# Evaluation harness

Everything in paper Section 5 has to be measured on the assembled robot. The
111 unit tests in `docs/TEST_REPORT.md` section 3 run against
`pi/common/mock_hardware.py` and prove the software logic only; no reviewer
will accept them as validation of the system.

These scripts produce the raw data for Section 5 and fill in the empty result
columns of `docs/TEST_REPORT.md` sections 4-8. Each one appends to a CSV in
`results/`, and `summarize.py` turns those CSVs into n / mean / SD / min / max
/ median / p95 tables ready to paste into the paper.

Stdlib only, apart from `websockets` (already in `venv`). Run the Python
scripts with the project venv:

    cd /home/pi/robot/tools/eval
    ../../venv/bin/python wslatency.py --help     # websockets needed
    ./reslog.py --help                            # or directly, stdlib only

The controller key the drive probes need lives in a root-only drop-in:

    sudo grep CONTROLLER_KEY /etc/systemd/system/robot-watchdog.service.d/controller-key.conf

## What each script measures

| Script | Paper | TEST_REPORT | Measures |
|---|---|---|---|
| `wslatency.py` | 5.1 | H7, N6 | Command -> telemetry confirmation, and the firmware dead-man trip, over the real WebSocket path. Automated, high n. |
| `record.py latency_video` | 5.1 | N6 | True key-press-to-wheel latency from 240 fps video. |
| `record.py estop` | 5.1 | I6 | Emergency-stop stopping distance. |
| `record.py deadman_physical` | 5.1 | H7 | Time until the wheels actually stop. |
| `record.py glass2glass` | 5.2 | N7 | End-to-end video delay. |
| `netsweep.py` | 5.3 | N1-N5 | Latency, jitter, loss, RSSI and negotiated rate per position. |
| `faultinject.py run` | 5.4 | F3-F5 | Kills a supervised process and times the automatic recovery. |
| `faultinject.py watch` | 5.4 | F1-F2, F6-F10 | Times hand-injected faults by logging health transitions at 10 Hz. |
| `reslog.py` | 5.5 | - | CPU, memory, temperature, throttling, throughput per load condition. |
| `record.py ultrasonic/thermal/gas` | 5.6 | H11-H13 | Sensor error against reference instruments. |
| `gpsdrift.py` | 5.6 | H14, I17c | Static GPS scatter: mean, SD, RMS, CEP50, CEP95. |
| `record.py field` | 5.7 | section 8 | One row per complete rescue run. |
| `record.py sus` | 5.8 | - | Per-participant SUS items and task metrics; scores them. |
| `record.py checklist` | - | H1-H15, I1-I19 | Pass/fail rows for the plain checklist tests. |

## Running the campaign

### Day 1, bench: hardware and integration checklist

The robot can be on blocks. Work through `docs/TEST_REPORT.md` sections 4 and
5 and record each row:

    ./record.py checklist test_id=H1 result=PASS measured="READY RESCUE-UNO 1.0.0" tester=XX
    ./record.py checklist test_id=I8b result=PASS notes="locked out 5 min as designed"

Anything that fails goes in TEST_REPORT section 9 with a severity.

### Day 1, bench: latency and the dead-man timer

Wheels clear of the ground, or the robot in open space.

    KEY=$(sudo grep -oP 'CONTROLLER_KEY=\K.*' \
          /etc/systemd/system/robot-watchdog.service.d/controller-key.conf)

    # on the robot: internal path only
    ../../venv/bin/python wslatency.py --key "$KEY" --probe all --trials 30 --label on-pi
    # from the operator laptop: adds Wi-Fi
    ../../venv/bin/python wslatency.py --host <pi-ip> --key "$KEY" --probe all \
                                       --trials 30 --label wifi-5m

Then the camera measurements, which are the ones that go in the abstract.
Film the dashboard and the wheels in one frame at 240 fps, press a drive key,
count frames to first wheel movement, and do it 30 times:

    ./record.py latency_video fps=240 frames=19 label=wifi-5m

Emergency stop, 20 trials at each of three speeds, tape measure on the floor:

    ./record.py estop speed_pwm=180 distance_cm=42 surface=concrete

Dead-man physical stop, 20 trials:

    ./record.py deadman_physical speed_pwm=150 stop_s=2.1 panic_seen=1

### Day 2: streaming, resources, sensors

Video delay, 20 trials per viewer count. Point the camera at a running
stopwatch and photograph the real stopwatch and the video panel together:

    ./record.py glass2glass label=viewers-1 real_ms=12480 robot_ms=12190

Resource utilisation, one 30-minute capture per condition, with the robot
genuinely in that state:

    ./reslog.py --condition idle            --duration 1800
    ./reslog.py --condition one-viewer      --duration 1800
    ./reslog.py --condition two-viewers     --duration 1800
    ./reslog.py --condition drive-talk-view --duration 1800

Check `under_voltage_ever` in the output: if the supply sags, the CPU figures
describe a throttled Pi and the condition has to be re-run.

Sensors, against reference instruments:

    ./record.py ultrasonic true_cm=20 reading_cm=21      # 10 readings at each of 5 distances
    ./record.py thermal ref_c=28.4 sensor_c=29.1 ref_rh=62 sensor_rh=58
    ./record.py gas source=unlit-lighter-20cm baseline_adc=310 peak_adc=790 trip_s=4.2

### Day 2: fault injection

Automated, 10 repeats each. `--settle` must stay above P3's 10 s restart
cooldown; 30 s is the default:

    ./faultinject.py run all --repeats 10

For the faults that need hands (unplug the Arduino, unplug the camera, switch
off the router, reboot the Pi), start the watcher, inject, restore, Ctrl-C.
It timestamps every health transition at 10 Hz so no stopwatch is involved:

    ./faultinject.py watch --label F6-arduino-unplug
    ./faultinject.py watch --label F1-wifi-off
    ./faultinject.py watch --label F9-pi-reboot

### Day 3, outdoors: GPS

Leave the robot stationary with a fix for 30 minutes, then:

    ./gpsdrift.py --minutes 30 --label static-30min

Scatter around the centroid is *precision*. For *accuracy*, average a phone
fix at the same spot (or use a surveyed point) and pass it in:

    ./gpsdrift.py --minutes 30 --label static-vs-known --ref-lat 23.8103 --ref-lon 90.4125

Say in the paper which of the two the quoted figure is.

### Day 3, outdoors: Wi-Fi range

Run on the robot, with `iperf3 -s` on the laptop if you want throughput too.
One call per position; keep going until control is unusable, and record that
distance as the maximum working range:

    ./netsweep.py --target <laptop-ip> --label N1 --distance-m 5  --obstacles none    --video good   --control yes
    ./netsweep.py --target <laptop-ip> --label N3 --distance-m 30 --obstacles none    --video choppy --control degraded
    ./netsweep.py --target <laptop-ip> --label N4 --distance-m 15 --obstacles 2-walls --video lost   --control no

### Day 4: field trial

5 to 10 complete runs of the scenario in TEST_REPORT section 8, not one:

    ./record.py field course="corridor-with-turn" course_m=35 time_to_victim_s=142 \
                time_total_s=265 collisions=0 unplanned_stops=1 \
                victim_heard_operator=1 victim_saw_operator=1 \
                operator_heard_victim=1 operator_saw_victim=1 result=PASS operator=XX

### Scheduled separately: usability study

8-12 operators who did not build the robot. Each drives the same course to the
victim; record completion, time, errors, then the 10 SUS items on 1-5. Check
whether your institution requires ethics approval for human participants
before you start, and get it if so -- a reviewer may ask.

    ./record.py sus participant=P3 q1=4 q2=2 q3=5 q4=1 q5=4 q6=2 q7=5 q8=1 q9=4 q10=2 \
                task_time_s=96 completed=1 errors=0 prior_experience=none

## Producing the tables

    ./summarize.py                               # everything, to the terminal
    ./summarize.py --only 5.4                    # one section
    ./summarize.py --out results/summary.md      # markdown file

Sheets with no data are listed under "Not yet measured", so this doubles as a
progress check on the campaign.

## Reporting rules this harness assumes

- Every figure gets n, mean and SD. A single trial is not a result.
- `wslatency.py` figures carry up to one 200 ms telemetry period of
  quantisation error (`protocol.TELEMETRY_PERIOD_MS`) and are upper bounds.
  Quote the 240 fps video figure as the control latency and this as the
  high-n confirmation of it; say so explicitly.
- Keep the CSVs in `results/` and cite them in the paper's Data and Code
  Availability statement. They are the evidence that the tests were run.
- A failed test is a result. Record it, write it up in TEST_REPORT section 9,
  and discuss it in Section 6.3 Limitations.

## Measured baselines, 2026-10-07

First real run on the assembled robot, 30 trials each, robot on blocks,
`--label on-pi` (loopback, so no Wi-Fi in the path):

| Metric | mean | SD | min | max |
|---|---|---|---|---|
| `motor_start` | 328 ms | 136 | 157 | 761 |
| `motor_stop` | 314 ms | 80 | 208 | 607 |
| `pan_echo` | 388 ms | 60 | 286 | 495 |
| `deadman_trip` | 2409 ms | 115 | 2201 | 2598 |
| `hello_rtt` | 47 ms | 25 | 20 | 117 |

Reading these:

- The **minimum** is the tightest upper bound on true latency, not the mean.
  Quantisation adds a uniform 0-400 ms (one Arduino frame period plus one P1
  rebroadcast period), so the mean sits about 200 ms above the truth while the
  minimum is the closest any trial got to it.
- `deadman_trip` of 2409 ms against a 2000 ms firmware timer (`DEADMAN_MS`) is
  that same ~400 ms of pipeline, not a late timer. No trial exceeded 2.6 s.
- `pan_echo` includes servo travel, so it is not comparable to the motor
  figures.
- The `on-pi-phaselocked` rows in `latency.csv` are the same probes run before
  `--jitter` existed: `motor_stop` read 403 +/- 20 ms, a distribution tight
  enough to look precise and be wrong. Useful as a methodology example.

## Known starting points

- `arduino/command_parser.cpp:195` returns ACTIVE to **READY (fw_state 1)** on
  a stop command. `fw_state 3` is BOOT, ESTOP or PANIC only
  (`arduino/telemetry.cpp:62`), which is why the dead-man probe waits for 3 and
  the motor probe waits for 1. Getting this backwards stalls the probe after
  one trial.
- A dead-man PANIC clears itself once any command refreshes the timer
  (`arduino/arduino.ino:99`), which is why repeated dead-man trials need no
  manual reset.
- `var/log/telemetry.log` carries four column layouts under one stale header,
  because logrotate was never installed and `deploy/logrotate/robot` points at
  `/var/log/robot/` rather than the live `/home/pi/robot/var/log/`.
  `gpsdrift.py` maps rows by field count to cope. Fix the paths before citing
  the log as data.
- `/health` on both processes is the harness's only view of robot state, so it
  cannot see motor current, wheel motion or sound. Those stay camera- and
  ear-measured.
