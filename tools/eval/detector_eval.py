#!/usr/bin/env python3
"""E18: score the dashboard's person detector box-against-box, by IoU.

The dashboard runs MediaPipe EfficientDet-Lite0 in the operator's browser at a
score threshold of 0.4, restricted to the person class, at most five boxes per
frame, CPU delegate (Section 3.11,
dashboard/src/hooks/usePersonDetection.ts). This script does not run the
detector: it scores the boxes the deployed detector actually returned, as
exported from the dashboard and imported by detector_import.py, against boxes a
human drew by hand. Both sides are real records; nothing here simulates a
detection.

What changed, and why
---------------------
The first version of this script read one sheet, detector_frames.csv, with a
binary `detected` column, and called a frame a success when the detector
returned at least one person box anywhere in it. Three things were wrong with
that:

  * It measured frame-level classification, not detection. A box drawn around
    a chair, in a frame that also held a person, counted as a correct
    detection, and so did a box offset far enough to be useless to an
    operator.
  * Precision was computed as (frames with a person and a box) / (all frames
    with a box), so a wrong box in a frame containing a person could only ever
    raise precision, never lower it.
  * A frame with two people and one box scored the same as a frame with two
    people and two boxes.

This version matches predicted boxes to ground-truth boxes by intersection
over union, one to one, at a primary threshold of IoU 0.50, and counts true
positives, false positives and false negatives per box (detector_iou.py).
Precision, recall and F1 are computed from those counts.

The banner false-alarm measurement is unchanged and stays separate: it is a
property of the three-frames-to-raise logic on continuous video, not of any
single box, and its acceptance criterion (at most 1 false alarm per minute
over at least 10 min of person-free video, Table 4.2) is untouched.

    ./detector_eval.py                              # markdown to stdout
    ./detector_eval.py --out results/detector_eval.md
    ./detector_eval.py --iou 0.5 --strict            # non-zero exit on a data error
"""

from __future__ import annotations

import argparse
import statistics as st
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, percentile, read_rows  # noqa: E402
from detector_data import (  # noqa: E402
    BANNER_FILE,
    CONDITIONS,
    FRAMES_INDEX_FILE,
    GROUNDTRUTH_FILE,
    LEGACY_FRAMES_FILE,
    PREDICTIONS_FILE,
    RUNS_FILE,
    Dataset,
    Frame,
    load_dataset,
)
from detector_iou import (  # noqa: E402
    PRIMARY_IOU,
    SENSITIVITY_IOU,
    Metrics,
    aggregate,
    average_precision,
    match_frame,
)

#: Table 4.2's easiest stratum, where the pass criterion applies.
EASIEST = {"posture": "upright", "occlusion": "unoccluded", "light": "room", "distance_band": "near"}
RECALL_FLOOR = 0.80
PRECISION_FLOOR = 0.90
#: The dashboard turns detection off above this mean inference time (Section 3.11).
AUTO_OFF_MS = 150.0

out_lines: list[str] = []


def emit(line: str = "") -> None:
    out_lines.append(line)


def fmt(value: float, places: int = 2) -> str:
    return "-" if value != value else f"{value:.{places}f}"  # NaN != NaN


def fmt_ci(value: float, ci: tuple[float, float]) -> str:
    if value != value:
        return "-"
    lo, hi = ci
    return f"{value:.3f} ({lo:.3f} to {hi:.3f})"


def metrics_row(label: str, m: Metrics) -> str:
    stats = m.iou_stats()
    mean_iou = fmt(stats["mean"], 3) if stats else "-"
    return (
        f"| {label} | {m.n_gt} | {m.n_pred} | {m.tp} | {m.fp} | {m.fn} | "
        f"{fmt_ci(m.precision, m.precision_ci)} | {fmt_ci(m.recall, m.recall_ci)} | "
        f"{fmt(m.f1, 3)} | {mean_iou} |"
    )


METRIC_HEADER = (
    "| group | GT boxes | predictions | TP | FP | FN | precision (95% CI) | "
    "recall (95% CI) | F1 | mean IoU of TP |"
)
METRIC_RULE = "|---|---|---|---|---|---|---|---|---|---|"


def score(frames: list[Frame], threshold: float) -> Metrics:
    return aggregate(match_frame(f.preds, f.gt, threshold) for f in frames)


def provenance_block(results_dir: Path, data: Dataset) -> None:
    emit("## Provenance of the scored data")
    emit()
    emit("| sheet | present | data rows | last modified (UTC) |")
    emit("|---|---|---|---|")
    for name in (FRAMES_INDEX_FILE, GROUNDTRUTH_FILE, RUNS_FILE, PREDICTIONS_FILE, BANNER_FILE):
        path = results_dir / name
        if path.exists():
            when = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(
                timespec="seconds"
            )
            rows = data.row_counts.get(name)
            count = str(rows) if rows is not None else str(len(read_rows(path)))
            emit(f"| `{name}` | yes | {count} | {when} |")
        else:
            emit(f"| `{name}` | no | - | - |")
    emit()
    emit(
        "Every scored box comes from one of these files. The predictions are the "
        "deployed detector's own output, exported from the dashboard and imported by "
        "`detector_import.py`, which records the export file in `export_source` and the "
        "frame's SHA-256 in the index. The ground truth is hand-drawn and names its "
        "annotator. This script writes nothing but its report."
    )
    emit()


def integrity_block(data: Dataset) -> None:
    if not data.errors and not data.warnings:
        return
    emit("## Data integrity")
    emit()
    if data.errors:
        emit(f"**{len(data.errors)} row(s) were rejected and are not scored.** The input "
             "files are not modified; fix them at the source and re-run.")
        emit()
        for message in data.errors:
            emit(f"- ERROR: {message}")
        emit()
    if data.warnings:
        for message in data.warnings:
            emit(f"- WARNING: {message}")
        emit()


def inventory_block(data: Dataset) -> None:
    frames = list(data.frames.values())
    scorable = data.scorable
    annotated = [f for f in frames if f.annotated]
    ran = [f for f in frames if f.ran]
    with_person = [f for f in scorable if f.gt]
    person_free = [f for f in scorable if f.person_free]
    gt_boxes = sum(len(f.gt) for f in scorable)
    pred_boxes = sum(len(f.preds) for f in scorable)
    annotators = sorted({a for f in annotated for a in f.annotators})

    emit("## Dataset inventory")
    emit()
    emit("| quantity | value |")
    emit("|---|---|")
    emit(f"| Frames in the index | {len(frames)} |")
    emit(f"| Frames annotated | {len(annotated)} |")
    emit(f"| Frames the detector was run on | {len(ran)} |")
    emit(f"| Frames scored (annotated and run) | {len(scorable)} |")
    emit(f"| &nbsp;&nbsp;of those, containing a person | {len(with_person)} |")
    emit(f"| &nbsp;&nbsp;of those, person-free | {len(person_free)} |")
    emit(f"| Ground-truth person boxes scored | {gt_boxes} |")
    emit(f"| Predicted boxes scored | {pred_boxes} |")
    emit(f"| Annotators | {', '.join(annotators) if annotators else '-'} |")
    models = sorted({f.model_label for f in ran if f.model_label})
    emit(f"| Detector | {'; '.join(models) if models else '-'} |")
    thresholds = sorted({
        f"{run['score_threshold']:g}"
        for f in ran for run in f.runs if run.get("score_threshold") is not None
    })
    emit(f"| Detector score threshold | {', '.join(thresholds) if thresholds else '-'} |")
    emit()
    excluded = data.excluded()
    if excluded:
        emit(f"{len(excluded)} frame(s) in the index are not scored:")
        emit()
        emit("| frame | reason |")
        emit("|---|---|")
        for frame, reason in excluded:
            emit(f"| {frame.frame_id} | {reason} |")
        emit()
        emit(
            "An unannotated frame is not a person-free frame, and a frame the detector "
            "has not been run on is not a missed detection. Neither is scored."
        )
        emit()


def primary_block(scorable: list[Frame], threshold: float) -> Metrics:
    m = score(scorable, threshold)
    emit(f"## Object-level detection at IoU {threshold:.2f} (primary result)")
    emit()
    emit(METRIC_HEADER)
    emit(METRIC_RULE)
    emit(metrics_row("**all scored frames**", m))
    emit()
    emit(
        f"A true positive is a predicted box matched one-to-one to a ground-truth box at "
        f"IoU >= {threshold:.2f}, predictions taken in descending confidence order, each "
        "matched to the highest-IoU unmatched ground-truth box (`detector_iou.match_frame`). "
        "An unmatched prediction is a false positive; an unmatched ground-truth box is a "
        "false negative."
    )
    emit()
    emit(
        f"Precision = TP / (TP + FP) = {m.tp} / {m.n_pred} = {fmt(m.precision, 3)}; "
        f"recall = TP / (TP + FN) = {m.tp} / {m.n_gt} = {fmt(m.recall, 3)}; "
        f"F1 = {fmt(m.f1, 3)}."
    )
    emit()
    stats = m.iou_stats()
    if stats:
        emit(
            f"IoU of the {stats['n']} matched pairs: mean {stats['mean']:.3f}, median "
            f"{stats['median']:.3f}, min {stats['min']:.3f}, max {stats['max']:.3f}, SD "
            f"{fmt(stats['sd'], 3)}. This is localisation quality among the boxes that "
            "matched; it says nothing about the ones that did not."
        )
        emit()
    emit(
        "The 95% intervals are Wilson score intervals on TP out of the prediction count "
        "(precision) and out of the ground-truth count (recall). They assume the boxes are "
        "independent Bernoulli trials, which boxes from consecutive frames of one scene are "
        "not, so they understate the true uncertainty. Read them as an indication of how "
        "little a small test set can settle, not as an exact coverage statement."
    )
    emit()
    return m


def sensitivity_block(scorable: list[Frame], primary: float) -> None:
    thresholds = sorted(set(SENSITIVITY_IOU) | {primary})
    emit("## Sensitivity to the IoU threshold")
    emit()
    emit("| IoU threshold | TP | FP | FN | precision | recall | F1 |")
    emit("|---|---|---|---|---|---|---|")
    for threshold in thresholds:
        m = score(scorable, threshold)
        mark = " (primary)" if threshold == primary else ""
        emit(
            f"| {threshold:.2f}{mark} | {m.tp} | {m.fp} | {m.fn} | {fmt(m.precision, 3)} | "
            f"{fmt(m.recall, 3)} | {fmt(m.f1, 3)} |"
        )
    emit()
    emit(
        "Only the primary row is the E18 result. The others show how much of the result is "
        "a localisation effect rather than a detection effect: a large gap between 0.25 and "
        "0.75 means the detector finds people but boxes them loosely."
    )
    emit()


def ap_block(scorable: list[Frame], threshold: float) -> None:
    pairs = [(f.preds, f.gt) for f in scorable]
    ap, n_gt = average_precision(pairs, threshold)
    if n_gt == 0:
        return
    emit(f"## Average precision at IoU {threshold:.2f}")
    emit()
    emit(f"AP@{threshold:.2f} = {fmt(ap, 3)} over {n_gt} ground-truth boxes, all-point "
         "interpolation of the precision-recall curve obtained by ranking every prediction "
         "in the set by confidence.")
    emit()
    emit(
        "**This is AP, not mAP.** There is one class (person), so nothing is averaged over "
        "classes, and no average over IoU thresholds is taken. It is also a lower bound "
        "rather than the model's AP: the only predictions that exist are those the shipped "
        "detector emitted above its own 0.4 score threshold, so the recall axis is "
        "truncated at whatever that threshold reaches and the curve has no low-confidence "
        "tail. Do not compare it with a COCO mAP figure."
    )
    emit()


def condition_blocks(scorable: list[Frame], threshold: float) -> None:
    with_labels = [f for f in scorable if any(f.conditions.get(c) for c in CONDITIONS)]
    if not with_labels:
        return
    emit(f"## Per-condition results at IoU {threshold:.2f}")
    emit()
    for name in CONDITIONS:
        groups: dict[str, list[Frame]] = {}
        for frame in with_labels:
            value = frame.conditions.get(name, "")
            if value:
                groups.setdefault(value, []).append(frame)
        if not groups:
            continue
        emit(f"### By {name}")
        emit()
        emit(METRIC_HEADER)
        emit(METRIC_RULE)
        for value in sorted(groups):
            emit(metrics_row(value, score(groups[value], threshold)))
        emit()
    cells: dict[tuple, list[Frame]] = {}
    for frame in with_labels:
        cells.setdefault(frame.condition_key, []).append(frame)
    emit("### By full condition cell")
    emit()
    emit("| " + " | ".join(CONDITIONS) + " | frames | GT boxes | predictions | TP | FP | FN | "
         "precision (95% CI) | recall (95% CI) | F1 | mean IoU of TP |")
    # 4 condition columns + frames, GT, preds, TP, FP, FN, precision, recall, F1, IoU
    emit("|" + "---|" * (len(CONDITIONS) + 10))
    for key in sorted(cells):
        group = cells[key]
        m = score(group, threshold)
        stats = m.iou_stats()
        emit(
            "| " + " | ".join(v or "-" for v in key) + f" | {len(group)} | {m.n_gt} | "
            f"{m.n_pred} | {m.tp} | {m.fp} | {m.fn} | {fmt_ci(m.precision, m.precision_ci)} | "
            f"{fmt_ci(m.recall, m.recall_ci)} | {fmt(m.f1, 3)} | "
            + (fmt(stats["mean"], 3) if stats else "-") + " |"
        )
    emit()
    emit(
        "A cell's recall is the measured failure region for that condition. No floor is set "
        "for the harder cells (Table 4.2): whatever they read is the result."
    )
    emit()


def criterion_block(scorable: list[Frame], threshold: float) -> None:
    easiest = [
        f for f in scorable
        if all(f.conditions.get(k) == v for k, v in EASIEST.items())
    ]
    emit("## Pass criterion for the detector (Table 4.2)")
    emit()
    if not easiest:
        emit(
            "[PENDING MEASUREMENT] No scored frame carries the easiest stratum "
            + ", ".join(f"{k}={v}" for k, v in EASIEST.items())
            + ", so the criterion cannot be evaluated."
        )
        emit()
        return
    m = score(easiest, threshold)
    emit(
        f"Easiest stratum ({', '.join(f'{k}={v}' for k, v in EASIEST.items())}): "
        f"{len(easiest)} frames, {m.n_gt} ground-truth boxes."
    )
    emit()
    emit("| limit | required | measured | verdict |")
    emit("|---|---|---|---|")
    for label, value, floor in (
        ("recall", m.recall, RECALL_FLOOR),
        ("precision", m.precision, PRECISION_FLOOR),
    ):
        if value != value:
            verdict = "cannot be evaluated"
        else:
            verdict = "met" if value >= floor else "**not met**"
        emit(f"| {label} | >= {floor:.2f} | {fmt(value, 3)} | {verdict} |")
    emit()
    emit(
        f"Both limits were fixed before capture (Table 4.2) on the frame-level definition "
        f"the first version of this script used. They are evaluated here at box level, "
        f"matched at IoU {threshold:.2f}, which is a strictly harder test: a box in the "
        f"wrong place now counts against precision instead of for it. State the box-level "
        f"definition and the IoU threshold wherever the criterion is quoted, so the "
        f"comparison is not read as the frame-level one."
    )
    emit()


def person_free_block(scorable: list[Frame], threshold: float) -> None:
    person_free = [f for f in scorable if f.person_free]
    if not person_free:
        return
    m = score(person_free, threshold)
    frames_with_fp = sum(1 for f in person_free if f.preds)
    emit("## Person-free frames")
    emit()
    emit(
        f"{len(person_free)} scored frames contain no person, so they hold no ground-truth "
        f"box and can only produce false positives. They produced {m.fp} false-positive "
        f"box(es) on {frames_with_fp} frame(s), {m.fp / len(person_free):.2f} per frame."
    )
    emit()
    emit(
        "These false positives are already included in the pooled precision above; this "
        "block only separates out where they came from. The banner false-alarm measurement "
        "below is a different test on continuous video and shares none of these counts."
    )
    emit()


def confidence_block(scorable: list[Frame], threshold: float) -> None:
    tp_scores: list[float] = []
    fp_scores: list[float] = []
    for frame in scorable:
        result = match_frame(frame.preds, frame.gt, threshold)
        matched = {m.pred_index for m in result.matches}
        for index, box in enumerate(frame.preds):
            if box.confidence is None:
                continue
            (tp_scores if index in matched else fp_scores).append(box.confidence)
    if not tp_scores and not fp_scores:
        return
    emit("## Confidence of matched and unmatched predictions")
    emit()
    emit("| predictions | n | median | min | max |")
    emit("|---|---|---|---|---|")
    for label, values in (("matched (TP)", tp_scores), ("unmatched (FP)", fp_scores)):
        if values:
            emit(f"| {label} | {len(values)} | {st.median(values):.2f} | "
                 f"{min(values):.2f} | {max(values):.2f} |")
        else:
            emit(f"| {label} | 0 | - | - | - |")
    emit()
    emit(
        "Scores below the detector's own 0.4 threshold cannot appear: the detector never "
        "emits them. Nothing here is a threshold sweep, and no threshold other than the "
        "shipped one was run."
    )
    emit()


def timing_block(scorable: list[Frame]) -> None:
    values = sorted(v for v in (f.infer_ms for f in scorable) if v is not None)
    if not values:
        emit("Inference time: [PENDING MEASUREMENT] no `infer_ms` recorded in "
             f"`{RUNS_FILE}`.")
        emit()
        return
    p95 = percentile(values, 95)
    over = sum(1 for v in values if v > AUTO_OFF_MS)
    emit("## Inference time")
    emit()
    emit(
        f"n {len(values)} frames: median {st.median(values):.0f} ms, mean "
        f"{st.fmean(values):.0f} ms, p95 {p95:.0f} ms, min {min(values):.0f} ms, max "
        f"{max(values):.0f} ms. {over} frame{'' if over == 1 else 's'} above the "
        f"dashboard's {AUTO_OFF_MS:.0f} ms auto-off level, which it applies to the mean of "
        "five consecutive frames rather than to a single frame (Section 3.11)."
    )
    emit()


def banner_block(rows: list[dict]) -> None:
    """Unchanged from the first version of this script: see the module docstring."""
    emit("## E18 banner false alarms on person-free video (detector_banner.csv)")
    emit()
    emit("| segment | person-free (min) | banner raises | false alarms per minute |")
    emit("|---|---|---|---|")
    total_s = total_raises = 0.0
    for r in rows:
        secs = float(r["person_free_s"])
        raises = float(r["banner_raises"])
        total_s += secs
        total_raises += raises
        mins = secs / 60
        emit(f"| {r['segment']} | {mins:.1f} | {raises:.0f} | "
             + (f"{raises / mins:.2f}" if mins else "-") + " |")
    mins = total_s / 60
    per_min = f"**{total_raises / mins:.2f}**" if mins else "-"
    emit(f"| **all** | **{mins:.1f}** | **{total_raises:.0f}** | {per_min} |")
    emit()
    emit("Pass criterion (Table 4.2, adopted): at most 1 false alarm per minute over at "
         "least 10 min of person-free video.")
    emit()
    if mins < 10:
        emit(f"[PENDING MEASUREMENT] Only {mins:.1f} min of person-free video has been "
             "scored; the criterion needs at least 10 min.")
        emit()
    emit(
        "This is a measurement of the raise logic (three consecutive frames with a box to "
        "raise, five without to clear) on continuous video. It is deliberately kept apart "
        "from the box-level metrics above and shares no counts with them."
    )
    emit()


def legacy_block(path: Path) -> None:
    rows = read_rows(path)
    emit(f"## Legacy sheet `{LEGACY_FRAMES_FILE}` (not scored)")
    emit()
    emit(
        f"{len(rows)} row(s) are present in `{LEGACY_FRAMES_FILE}`, the frame-level sheet "
        "this script used before the IoU rewrite. They are left on disk untouched and are "
        "**not** included in any metric above."
    )
    emit()
    emit(
        "The sheet records only whether the detector returned at least one box per frame, "
        "with no box coordinates on either side, so it cannot be converted into an "
        "object-level measurement: the information a conversion would need was never "
        "recorded. Treating its `detected` column as a box-level true positive would be "
        "fabrication. Any frame in it that is to count towards E18 has to be re-exported "
        "with its boxes and re-annotated."
    )
    emit()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--out", type=Path, help="write markdown here instead of stdout")
    ap.add_argument("--iou", type=float, default=PRIMARY_IOU,
                    help=f"primary IoU threshold (default {PRIMARY_IOU})")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any input row was rejected")
    args = ap.parse_args()
    if not 0 < args.iou <= 1:
        ap.error("--iou must be in (0, 1]")

    data = load_dataset(args.results_dir)
    scorable = sorted(data.scorable, key=lambda f: f.frame_id)

    emit("# E18 person-detector evaluation (object-level, IoU matched)")
    emit()
    emit(
        f"Generated by `tools/eval/detector_eval.py` at "
        f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} from the sheets listed "
        f"below, at a primary threshold of IoU {args.iou:.2f}. Derived figures only: no "
        "input file is read for anything but its rows, and none is modified."
    )
    emit()

    provenance_block(args.results_dir, data)
    integrity_block(data)

    if data.any_input:
        inventory_block(data)
    if scorable:
        primary_block(scorable, args.iou)
        sensitivity_block(scorable, args.iou)
        ap_block(scorable, args.iou)
        condition_blocks(scorable, args.iou)
        criterion_block(scorable, args.iou)
        person_free_block(scorable, args.iou)
        confidence_block(scorable, args.iou)
        timing_block(scorable)
    else:
        emit("## Object-level detection")
        emit()
        emit(
            "[PENDING MEASUREMENT: E18 person detection.] No frame is both annotated and "
            "scored by the deployed detector, so no precision, recall, F1 or IoU figure "
            "exists. The protocol is in Section 5.9, the pass criterion in Table 4.2, and "
            "the procedure for collecting the data in `tools/eval/README.md`."
        )
        emit()

    banner = args.results_dir / BANNER_FILE
    banner_rows = read_rows(banner) if banner.exists() else []
    if banner_rows:
        banner_block(banner_rows)
    else:
        emit("## E18 banner false alarms on person-free video")
        emit()
        emit(f"[PENDING MEASUREMENT] `{BANNER_FILE}` holds no segments. Criterion "
             "(Table 4.2, adopted): at most 1 false alarm per minute over at least 10 min "
             "of person-free video.")
        emit()

    legacy = args.results_dir / LEGACY_FRAMES_FILE
    if legacy.exists():
        legacy_block(legacy)

    text = "\n".join(out_lines) + "\n"
    if args.out:
        args.out.write_text(text)
        print(f"written to {args.out}")
    else:
        sys.stdout.write(text)
    if args.strict and data.errors:
        print(f"{len(data.errors)} input row(s) rejected; see the report", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
