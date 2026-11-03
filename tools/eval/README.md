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
| `wslatency.py` | 5.1 | H7, N6 | Command -> telemetry confirmation, and the firmware dead-man trip, over the real WebSocket path. Automated, high n. Records the dead-man trip twice: `deadman_trip` (fw_state in telemetry, quantised) and `deadman_panic` (the firmware's immediate PANIC notice, read from P1's event log, so it needs to run on the Pi). |
| `record.py latency_video` | 5.1 | N6 | True key-press-to-wheel latency from 240 fps video. |
| `record.py deadman_physical` | 5.1 | H7 | Time until the wheels actually stop. |
| `record.py glass2glass` | 5.2 | N7 | End-to-end video delay. |
| `netsweep.py` | 5.3 | N1-N5 | Latency, jitter, loss, RSSI and negotiated rate per position. |
| `faultinject.py run` | 5.4 | F3-F5 | Kills a supervised process and times the automatic recovery. |
| `faultinject.py watch` | 5.4 | F1-F2, F6-F10 | Times hand-injected faults by logging health transitions at 10 Hz. |
| `reslog.py` | 5.5 | - | CPU, memory, temperature, throttling, throughput per load condition. |
| `gpsdrift.py` | 5.6 | H14, I17c | Static GPS scatter: mean, SD, RMS, CEP50, CEP95. |
| `record.py field` | 5.7 | section 8 | One row per complete rescue run. |
| `record.py victim_comms` | 5.8 | - | E17: one row per victim-communication trial (3 modes x 2 victim states per participant); cross-check the tap-mode timings against P2's QUESTION_ASK / QUESTION_ANSWER lines. |
| `detector_import.py` | 5.9 | - | E18: imports the dashboard's own exported detector output (boxes, confidences, inference time) into the prediction sheets. Never writes ground truth. |
| `detector_annotate.py` | 5.9 | - | E18: typed entry of hand-drawn ground-truth person boxes, one row per person, plus an explicit record for a person-free frame. |
| `detector_eval.py` | 5.9 | - | E18: scores predicted boxes against ground-truth boxes by IoU (primary threshold 0.50), one-to-one: TP/FP/FN, precision, recall, F1, IoU statistics, AP@0.50, per-condition tables, banner false alarms and inference time. |
| `record.py sus` | - | - | Per-participant SUS items and task metrics; scores them. |
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

Dead-man physical stop, 20 trials. Film the wheels at 240 fps; with a tape
laid along the path, the same film also gives the distance covered after the
last command:

    ./record.py deadman_physical speed_pwm=180 stop_s=2.1 panic_seen=1 distance_cm=6

### Victim communication and the detector test set

E17 needs ethics approval and a touch input on the robot display (no answer has
ever been given on the robot itself). One row per trial, entered during the
session, three modes x two victim states per participant:

    ./record.py victim_comms participant=P3 order=2 mode=tap-to-answer \
        victim_state=cannot-speak items_correct=3 time_to_contact_s=41 \
        time_exchange_s=96 confidence=4 failure_mode=none question_ids="7;8;9"

E18 needs no ethics approval and no purchase. It is scored box against box by
IoU; the whole procedure is in **E18: the person-detector evaluation** below.

### Day 2: streaming and resources

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

## E18: the person-detector evaluation

E18 measures how well the operator's person detector finds a person **in the
right place** in the video the operator actually sees (paper Section 5.9).
Status: [PENDING MEASUREMENT]. The tools below are in place and tested; no
frame has been annotated and no prediction has been collected, so no detection
figure exists yet.

### What this measures, and what it replaced

The first version of `detector_eval.py` read one sheet with a binary
`detected` column and scored a frame as a success when the detector returned at
least one person box anywhere in it. That is frame-level classification, not
detection, and it was wrong in three ways:

- a box drawn around a chair in a frame that also held a person counted as a
  correct detection, and so did a box offset far enough to be useless;
- precision was (frames with a person and a box) / (all frames with a box), so
  a wrong box in a frame containing a person could only raise precision;
- a frame with two people and one box scored the same as a frame with two
  people and two boxes.

The evaluation now matches predicted boxes to hand-drawn boxes one to one by
intersection over union. Classification accuracy is not reported at all: it is
not an object-detection metric.

### The four sheets

All under `results/`, all append-only CSV, all written by the tools below.
`detector_data.py` holds the column lists and the loader.

| Sheet | One row per | Written by |
|---|---|---|
| `detector_frames_index.csv` | frame in the test set (the manifest) | `detector_import.py` |
| `detector_groundtruth.csv` | hand-drawn person box, or one "person-free" record | `detector_annotate.py` |
| `detector_runs.csv` | frame the deployed detector was run on | `detector_import.py` |
| `detector_predictions.csv` | box the deployed detector returned | `detector_import.py` |

`detector_banner.csv` is a fifth, unchanged sheet for the banner test and is
scored separately (below).

**`detector_frames_index.csv`** - `frame_id`, `image_file`, `image_sha256`,
`image_width`, `image_height`, `scene`, `posture`, `occlusion`, `light`,
`distance_band`, `lux`, `expected_person_count`, `capture_utc`,
`capture_source`, `notes`. The four condition columns carry the 2x2x2x2 strata
of Section 5.9 and belong to the frame; a box inherits its frame's conditions.
`image_width` / `image_height` define the coordinate space every box for that
frame is in. `image_sha256` is the hash of the frame file, so a frame cannot be
substituted without the hash changing.

**`detector_groundtruth.csv`** - `frame_id`, `image_file`, `box_id`, `x_min`,
`y_min`, `x_max`, `y_max`, `annotator_id`, `annotated_utc`, `notes`. One row per
person visible in the frame, so several people in one frame are several rows.
A frame that contains nobody gets exactly one row with `box_id` = `none` and
all four coordinates blank: zero ground-truth boxes, but an explicit record
that a human looked and saw nobody.

**`detector_runs.csv`** - `frame_id`, `model_name`, `model_version`,
`delegate`, `score_threshold`, `max_results`, `infer_ms`, `n_boxes`,
`image_width`, `image_height`, `export_utc`, `export_source`, `notes`. One row
per frame the detector ran on, whether or not it returned anything.

**`detector_predictions.csv`** - `frame_id`, `image_file`, `pred_id`, `x_min`,
`y_min`, `x_max`, `y_max`, `confidence`, `model_name`, `model_version`,
`infer_ms`, `export_utc`, `export_source`, `notes`. One row per returned box,
so several boxes in one frame are several rows and a frame with no detection
has none.

Coordinates are pixels in the frame's own space: x to the right, y downward,
origin at the top-left pixel, `(x_min, y_min)` the top-left corner of the box
and `(x_max, y_max)` the bottom-right, with `x_max > x_min` and
`y_max > y_min`.

### Why three facts are kept in three sheets

A frame being in the index, a human having annotated it, and the detector
having been run on it are three different facts, and the loader keeps them
apart on purpose:

- A frame with **no ground-truth row** is an unannotated frame, **not** a
  person-free frame. Scoring it as person-free would invent false positives.
- A frame with **no run row** has no measurement at all. Scoring it would
  invent false negatives.

Only a frame that is both annotated and run is scored. Everything else is
listed in the report under "Dataset inventory" with the reason, and those
reasons carry `[PENDING MEASUREMENT]`.

### Collecting the predictions

The detector runs in the operator's browser (`usePersonDetection.ts`), so its
real output exists nowhere else, and the predictions have to come from there.
Running a second copy of the model offline would be a different measurement of
a different system.

Capture mode is off for an operator. Turn it on once per browser by opening the
dashboard with `?evalcapture=1` (it is then remembered in that browser's
`localStorage` under `robot.evalCapture`; set it to anything else, or clear site
data, to turn it off). A **Capture eval frame** button then appears next to the
AI button while detection is running. It saves two files per press to the
browser's Downloads folder:

    e18-20261103T184500123Z.jpg     the frame, with no boxes drawn on it
    e18-20261103T184500123Z.json    the boxes that detector returned on it

The capture happens **inside** the detection pass, so the JPEG is the frame
those boxes were produced from, not a later one. The JPEG carries no overlay,
because the annotator has to draw ground truth on a clean frame: a frame with
the detector's own boxes burnt in would tell them the answer. The JSON records
the model name and version, the delegate, the score threshold, `max_results`,
the measured `infer_ms` and each box with its confidence.

Capture one condition cell per batch, so a whole batch shares its strata, then
import it (on the operator's computer, where the frames are):

    ./detector_import.py --from ~/Downloads/e18-batch-01 --dry-run \
        --scene corridor-A --posture upright --occlusion unoccluded \
        --light room --distance near --lux 320 --expected-persons 1

    ./detector_import.py --from ~/Downloads/e18-batch-01 \
        --scene corridor-A --posture upright --occlusion unoccluded \
        --light room --distance near --lux 320 --expected-persons 1

Person-free frames are a batch like any other:

    ./detector_import.py --from ~/Downloads/e18-personfree \
        --scene corridor-A --posture none --occlusion - \
        --light room --distance near --expected-persons 0

The importer validates every record, skips a frame it has already imported,
and reports anything it refuses rather than repairing it. It writes the three
prediction-side sheets and never a ground-truth row.

**The frames are not copied into the repository.** They show people, and no
image of a person is stored on the robot (paper Sections 3.11 and 4.1). The
index records the file name and the SHA-256 only; the images stay on the
operator's computer, and the CSVs are what comes back to the repo.

### Annotating the ground truth

Open the clean JPEG in any viewer that shows pixel coordinates (GIMP's pointer
window, a browser's developer tools on the opened file) and read off the
corners of a tight box around each visible person. One row per person:

    ./detector_annotate.py --list-unannotated

    ./detector_annotate.py box frame_id=e18-20261103T184500123Z box_id=b1 \
        x_min=412 y_min=96 x_max=505 y_max=348 annotator_id=AB

    # two people in one frame
    ./detector_annotate.py box frame_id=F12 box_id=b1 x_min=120 y_min=80 \
        x_max=210 y_max=330 annotator_id=AB
    ./detector_annotate.py box frame_id=F12 box_id=b2 x_min=460 y_min=102 \
        x_max=548 y_max=352 annotator_id=AB

    # nobody in the frame: still a record
    ./detector_annotate.py empty frame_id=F80 annotator_id=AB notes="chairs only"

    ./detector_annotate.py --show frame_id=F12

Rules the tool enforces: the frame must already be in the index (a frame is
never created here), `annotator_id` is required on every row, coordinates must
describe a real box inside the frame, a box may not contradict a person-free
record or the other way round, and `box_id` must be new. Annotate without
looking at the predictions first; knowing the detector's answer changes where a
human draws a box.

Decide and write down the annotation rule before starting, because it decides
the measurement: annotate the whole visible extent of the person including
limbs, exclude a person who is entirely hidden, and for a partly covered person
box the visible part only. Whatever is chosen, record it in the paper's
Section 5.9 and keep it the same for every frame. `notes` is the place for a
frame where the rule was hard to apply.

### IoU, and the matching rule

For a predicted box P and a ground-truth box G,

    IoU(P, G) = area(P and G) / area(P or G)
              = inter / (area(P) + area(G) - inter)

    inter = max(0, min(x_max) - max(x_min)) * max(0, min(y_max) - max(y_min))

IoU is 0 for boxes that do not overlap and 1 for identical boxes. **The primary
threshold for E18 is IoU 0.50**, inclusive: exactly 0.50 counts as a match.

Matching is one-to-one, per frame, and deterministic
(`detector_iou.match_frame`):

1. Predictions are taken in **descending confidence** order. Ties are broken by
   `pred_id` and then row order, ascending, so the result never depends on file
   or dict ordering.
2. Each prediction takes the **unmatched** ground-truth box it has the highest
   IoU with, provided that IoU is at least the threshold. Ties on IoU are
   broken by `box_id`, ascending.
3. A matched pair is a **true positive (TP)** and consumes both boxes; neither
   can match again.
4. A prediction left unmatched is a **false positive (FP)**.
5. A ground-truth box left unmatched is a **false negative (FN)**.

So a duplicate box on one person is one TP and one FP, one wide box over two
adjacent people is at most one TP and one FN, and a box in the wrong place in a
frame that does hold a person is one FP and one FN rather than a success.

Greedy confidence-ordered matching does not always maximise the number of
matches; a maximum-weight assignment could do better in contrived overlapping
cases. It is used because it is the convention the detection literature reports
against, and a different rule would make these numbers incomparable with any
published figure.

### Metrics

Computed over boxes, micro-averaged (every box weighs the same, so a frame with
three people is not given the weight of a frame with one):

| Metric | Definition |
|---|---|
| TP, FP, FN | counts of matched predictions, unmatched predictions and unmatched ground-truth boxes |
| Precision | TP / (TP + FP); undefined, and printed as `-`, with no predictions |
| Recall | TP / (TP + FN); undefined with no ground truth |
| F1 | 2PR / (P + R), and 0 when both are 0 |
| IoU statistics | mean, median, min, max and SD over matched pairs only |
| AP@0.50 | all-point-interpolated average precision, one class |
| Per condition | all of the above by posture, occlusion, light and distance, and by full 2x2x2x2 cell |
| Inference time | median, mean, p95, min, max from `infer_ms`, and the count above the dashboard's 150 ms auto-off level |

Three cautions the report also prints:

- The 95% intervals are **Wilson score intervals** on TP out of the prediction
  count (precision) and out of the ground-truth count (recall). They assume
  independent Bernoulli trials, which boxes from consecutive frames of one
  scene are not, so they understate the true uncertainty. Quote them as an
  indication of how little a small test set settles, not as exact coverage.
- `AP@0.50` is **AP, not mAP**: one class, one IoU threshold, nothing averaged
  over either. It is also a lower bound, because the only predictions that
  exist are those the shipped detector emitted above its own 0.4 score
  threshold, so the recall axis is truncated and the curve has no
  low-confidence tail. It is not comparable with a COCO mAP.
- **Classification accuracy is not reported.** On a set with far more
  background than people it is close to meaningless, and it is not an
  object-detection metric.

The IoU sensitivity table (0.25 / 0.50 / 0.75) is a diagnostic, not the result:
a large gap between 0.25 and 0.75 means the detector finds people but boxes
them loosely. Only the 0.50 row is the E18 figure.

### The banner test (unchanged, and kept separate)

The banner is raised after three consecutive frames with a box and cleared
after five without (Section 3.11), so it is a property of continuous video, not
of a single box. It is measured on its own, and the box-level metrics and the
banner metrics share no counts.

Play at least ten minutes of person-free video through the same path with
detection on, count every raise, and record one row per continuous segment in
`results/detector_banner.csv` (`segment`, `person_free_s`, `banner_raises`,
`notes`). The acceptance criterion is unchanged: **at most 1 false alarm per
minute over at least 10 minutes of person-free video** (Table 4.2, adopted).
The report flags a total under 10 minutes as `[PENDING MEASUREMENT]`.

### Running the evaluation

    ./detector_eval.py                                  # markdown to stdout
    ./detector_eval.py --out results/detector_eval.md   # the report for the paper
    ./detector_eval.py --iou 0.5 --strict                # exit 1 if any row was rejected

`--strict` is the one to use in a check: it exits non-zero if any input row was
rejected, so a typo in a sheet cannot pass unnoticed. The script reads the
sheets and writes only its report; it never runs the detector, so a reviewer
with the CSVs reproduces every number in it.

### Reading the report

1. **Provenance** - which sheets exist, how many rows each has, when each was
   last modified. Every scored box comes from one of them.
2. **Data integrity** - rejected rows (`ERROR`, dropped from every metric) and
   `WARNING` lines, including a disagreement between `expected_person_count`
   and the annotation, or between `n_boxes` and the imported predictions. A
   report with errors is not a result; fix the sheet at the source and re-run.
3. **Dataset inventory** - frames in the index, annotated, run, and scored,
   with the ground-truth and prediction box counts, the annotators, the model
   and its threshold. Then the frames that are **not** scored, with the reason.
   Check this first: the headline numbers describe the scored subset only.
4. **Object-level detection at IoU 0.50** - the primary result. TP, FP, FN,
   precision, recall, F1 and the mean IoU of matched pairs.
5. **Sensitivity, AP, per-condition tables** - diagnostics and the failure
   region per stratum. A cell's recall is the measured failure region; no floor
   is set for the harder cells, so whatever they read is the result.
6. **Pass criterion** - the Table 4.2 limits (recall >= 0.80, precision >= 0.90
   in the easiest stratum) evaluated on the scored frames of that stratum. The
   limits were fixed before capture on the frame-level definition; they are
   evaluated here at box level, which is strictly harder. Say so wherever the
   criterion is quoted.
7. **Person-free frames, confidence, inference time** - where the false
   positives came from, how confident matched and unmatched predictions were,
   and the per-frame cost on the operator's computer.
8. **Banner** - the separate continuous-video measurement.
9. **Legacy sheet** - printed only if `detector_frames.csv` exists, to say it
   was not scored.

### Migrating from the old `detector_frames.csv`

There is nothing to migrate: no `detector_frames.csv` was ever collected, and
`results/` has never held one. The schema is documented here as a schema
change, not a data change.

The sheet **cannot** be converted even if one appears. It records only whether
the detector returned at least one box per frame, with no coordinates on either
side, so the information an object-level score needs was never in it. Reading
its `detected` column as a box-level true positive would be fabrication. If one
turns up, `detector_eval.py` lists it in a "Legacy sheet (not scored)" block,
leaves it untouched on disk, and excludes it from every metric; any frame in it
that is to count towards E18 has to be re-exported with its boxes and
re-annotated.

### Tests

    cd /home/pi/robot && venv/bin/python -m pytest tools/eval/tests/ -q

102 tests over the IoU arithmetic, the matching rule, the metrics, the loader's
integrity rules, the importer and the annotation tool. They use hand-built
boxes and `tmp_path` sheets only: no test reads or writes anything in
`results/`, and none of them is evidence about the robot - they verify the
evaluation's arithmetic, nothing more.

### What is still needed before E18 can be reported

1. Capture the frame set through the robot's own video path, in capture mode,
   one batch per condition cell (Section 5.9 plans 400 frames: 320 with a
   person over 16 cells, 80 person-free).
2. Import every batch with its strata, and check the importer reported no
   problems.
3. Write down the annotation rule, then annotate every frame, person-free
   frames included.
4. Record at least 10 minutes of person-free video for the banner test.
5. Run `./detector_eval.py --strict --out results/detector_eval.md` and carry
   the numbers into Section 5.9.

Until all five are done, E18 stays `[PENDING MEASUREMENT]`. The code existing
is not the experiment having been run.

## Producing the tables

    ./summarize.py                               # everything, to the terminal
    ./summarize.py --only 5.4                    # one section
    ./summarize.py --out results/summary.md      # markdown file

Sheets with no data are listed under "Not yet measured", so this doubles as a
progress check on the campaign.

## Reporting rules this harness assumes

- Every figure gets n, mean and SD. A single trial is not a result.
- `wslatency.py` figures confirmed through a telemetry field carry up to
  700 ms of quantisation error and are upper bounds: one firmware frame period
  (500 ms, `arduino/config.h TELEMETRY_PERIOD_MS`) plus one P1 rebroadcast
  period (200 ms, `protocol.TELEMETRY_PERIOD_MS`). Quote the 240 fps video
  figure as the control latency and this as the high-n confirmation of it; say
  so explicitly. `deadman_panic` is the one exception: it is timed from P1's
  own log line, so its resolution is the log's millisecond timestamp.
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
  Quantisation adds 0-700 ms (one 500 ms Arduino frame period plus one 200 ms
  P1 rebroadcast period), so the mean sits about 350 ms above the truth while
  the minimum is the closest any trial got to it.
- `deadman_trip` of 2409 ms is not a late timer. The motors stop at about
  2060 ms (2000 ms `DEADMAN_MS` + 10 ms supervisor period + one loop pass);
  the rest is that reporting pipeline. No trial exceeded 2.6 s.
- These rows predate the `deadman_panic` metric and the corrected
  `resolution_ms` column, so they carry 200 in it. The `deadman_trip`
  definition itself is unchanged, so the values remain comparable with later
  runs.
- Caveat on the spread of `deadman_trip`: the jitter is 0-200 ms, one P1
  period, which cannot decorrelate a trial from the 500 ms firmware cycle.
  Phase is sampled incompletely, which is why the minimum sits near 2201 ms
  rather than near the 2060 ms stop bound, and why the SD understates the true
  quantisation spread. `deadman_panic` is free of this, being unquantised.
- `pan_echo` includes servo travel, so it is not comparable to the motor
  figures.
- The `on-pi-phaselocked` rows in `latency.csv` are the same probes run before
  `--jitter` existed: `motor_stop` read 403 +/- 20 ms, a distribution tight
  enough to look precise and be wrong. Useful as a methodology example.

## Data caveat, 2026-10-22: bench_motor.csv

The 60 rows in `results/bench_motor.csv` (`bench_motor.py`, PWM 60/120/180 x
F/R/L/G, 5 reps each) were run on the stated premise that the robot was
securely elevated with every wheel clear of the ground, so the drive
commands could not move it. That premise was wrong: the robot was actually
on the floor for all 60 trials. No collision or damage resulted (operator
confirmed after the fact), but the trials were real, undocumented floor
travel with no clear-path check, run under the belief that none was needed.

No tape measurement was taken, trial duration was a fixed 1 s rather than
"drive until operator marks the line", and no surface/traction condition was
recorded, so the rows support no stopping-distance figure. They remain only
firmware-timing data (`cmd_to_driving_s_*`,
`stop_to_ready_s_*`), as `bench_motor.py`'s docstring already says, and nothing
here changes that -- it just removes the "never left the ground" framing the
rows were originally logged under. Re-confirm wheel contact visually (not by
asking "is it elevated") before trusting that premise again.

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
