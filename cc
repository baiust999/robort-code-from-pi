Task: Upgrade E18 Person Detector Evaluation Using IoU

Work on my rescue robot research repository

1. Objective

Improve the existing E18 person detector evaluation so that it measures actual bounding-box detection performance rather than only checking whether a person was detected in a frame.

The current evaluation script is:

tools/eval/detector_eval.py

Read the complete script, evaluation README, existing data formats, and relevant dashboard detector implementation before making changes.

2. Existing problem

The current evaluation uses a binary detected field.

It considers a frame successfully detected whenever at least one person detection exists.

It does not compare predicted bounding boxes with manually annotated ground-truth bounding boxes.

Its precision calculation also has a limitation: a wrong detection in a frame containing a real person may be counted as a successful detection.

Therefore, the existing method does not properly measure object-level detection performance.

3. Required improvements

A. Ground-truth annotation

Create a data format for manually annotated person bounding boxes.

Each annotation must contain:

Image/frame ID

Image filename

Person bounding-box coordinates (x_min, y_min, x_max, y_max)

Annotator ID

Annotation notes, if necessary

Support multiple people in one frame.

Frames containing no person must have zero ground-truth boxes.

B. Predicted detections

Store the actual detector outputs for each evaluated frame:

Image/frame ID

Predicted bounding-box coordinates

Confidence score

Model name/version

Inference time

Support multiple predicted boxes in one frame.

Use predictions from the actual deployed detector. Do not invent or simulate detection outputs.

C. IoU matching

Implement Intersection over Union (IoU) between predicted and ground-truth bounding boxes.

Use an IoU threshold of 0.50 as the primary evaluation threshold.

Apply one-to-one matching:

One prediction can match only one ground-truth box.

One ground-truth box can match only one prediction.

A valid match is a True Positive (TP).

An unmatched prediction is a False Positive (FP).

An unmatched ground-truth box is a False Negative (FN).

Use a documented, deterministic matching procedure. Process predictions in descending confidence order and match each to the highest-IoU unmatched ground-truth box that meets the threshold.

D. Evaluation metrics

Calculate:

Precision

Recall

F1-score

TP, FP and FN

IoU statistics for matched detections

Per-condition results for posture, occlusion, lighting and distance

95% confidence intervals where statistically appropriate

Do not claim mAP unless a proper average-precision calculation across confidence thresholds is implemented.

Do not use classification accuracy as the main object detection metric.

E. Banner evaluation

Preserve the existing person-free banner false-alarm evaluation.

Keep it separate from bounding-box detection metrics.

Retain the existing acceptance criterion of no more than one false alarm per minute over at least 10 minutes of person-free video, unless the research protocol is explicitly revised.

4. Data integrity

Important:

Never fabricate annotations, predictions or measurements.

Never modify existing raw experimental records silently.

Do not treat illustrative data as real experimental data.

Preserve the original dataset.

Record the source of every evaluated frame and prediction.

Mark missing measurements as PENDING MEASUREMENT.

Make the evaluation reproducible.

If existing CSV files are incompatible, create a documented migration or new schema. Do not silently reinterpret old records as bounding-box measurements.

5. Research documentation

Update the relevant documentation in tools/eval/README.md.

Explain:

The annotation procedure.

The prediction collection procedure.

The IoU formula and threshold.

The matching algorithm.

The evaluation metrics.

How to execute the evaluation.

How to interpret the generated report.

Generate a reproducible Markdown evaluation report.

6. Testing

Add tests for:

Perfect predicted and ground-truth box matches.

Partial overlap below IoU 0.50.

Incorrect predictions.

Missing predictions.

Multiple people in one frame.

Multiple predictions for one person.

Empty frames with false detections.

Multiple ground-truth boxes with one prediction.

Invalid bounding-box coordinates.

Confidence-score ordering.

Verify that TP, FP, FN, precision, recall and F1 are calculated correctly.

7. Constraints

Do not rewrite the robot architecture.

Do not change motor control, safety mechanisms, networking or unrelated dashboard functions.

Preserve the existing banner evaluation.

Keep changes limited to E18 evaluation and the minimum required detector-output integration.

Do not claim that the experiment is completed after implementing the code.

The experiment remains PENDING MEASUREMENT until real frames are annotated and real detector predictions are collected.

8. Final report

Before finishing, provide:

Files inspected.

Files changed.

Explanation of the original problem.

Explanation of the new evaluation method.

Dataset schema.

Test results.

Exact commands to collect data and run evaluation.

Remaining work before E18 can be reported in the research paper.

Do not modify unrelated files.
