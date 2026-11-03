#!/usr/bin/env python3
"""E18 dataset: the four CSV sheets, their schemas, and a strict loader.

Four sheets under tools/eval/results/, all append-only, all plain CSV:

  detector_frames_index.csv   one row per frame in the test set (the manifest)
  detector_groundtruth.csv    one row per hand-annotated person box
  detector_runs.csv           one row per frame the deployed detector ran on
  detector_predictions.csv    one row per box the deployed detector returned

A fifth sheet, detector_banner.csv, is unchanged and is not read here: the
banner false-alarm test is a separate measurement on continuous video and is
scored by detector_eval.py on its own.

Why four sheets and not one
---------------------------
Boxes are one-to-many with frames in two directions at once (several people,
several predictions), so a one-row-per-frame sheet cannot hold them. The split
also keeps three facts apart that the old binary sheet conflated:

  * a frame exists in the test set            -> a row in the index
  * a human has looked at it and annotated it -> at least one row in
                                                 detector_groundtruth.csv
  * the detector has been run on it           -> a row in detector_runs.csv

Those have to be distinguishable. A frame with no ground-truth rows is not a
person-free frame, it is an unannotated frame, and scoring it as person-free
would invent false positives. A frame with no run row has no measurement at
all, and scoring it would invent false negatives. Only frames that are both
annotated and run are scored; everything else is listed as excluded, with the
reason, in the report.

A frame that genuinely contains nobody is recorded explicitly: one
detector_groundtruth.csv row with box_id `none` and all four coordinates
blank. That is the annotator asserting "I looked, there is no person here",
which is a measurement. Zero ground-truth boxes, one annotation record.

Integrity rules this loader enforces
------------------------------------
  * Every ground-truth, run and prediction row must name a frame_id that is in
    the index. An unknown frame_id is an error, not a new frame.
  * image_file must agree with the index wherever a row repeats it.
  * Coordinates are validated (detector_iou.validate_box) and are rejected if
    they leave the frame's declared image size.
  * frame_id and box_id / pred_id must be unique within their sheet.
  * expected_person_count, when given, is cross-checked against the number of
    annotated boxes and any disagreement is reported.
  * Nothing is ever written, inferred or defaulted into a measurement. Rows
    that fail a check are reported and dropped from the scored set, never
    repaired.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import read_rows  # noqa: E402
from detector_iou import Box, BoxError, make_box  # noqa: E402

FRAMES_INDEX_FILE = "detector_frames_index.csv"
GROUNDTRUTH_FILE = "detector_groundtruth.csv"
RUNS_FILE = "detector_runs.csv"
PREDICTIONS_FILE = "detector_predictions.csv"
BANNER_FILE = "detector_banner.csv"
LEGACY_FRAMES_FILE = "detector_frames.csv"

#: Marker in detector_groundtruth.csv box_id for "annotated, nobody in frame".
EMPTY_BOX_ID = "none"

CONDITIONS = ("posture", "occlusion", "light", "distance_band")

FRAMES_INDEX_COLUMNS = (
    "frame_id",          # stable identifier, unique in the set
    "image_file",        # file name of the still, on the operator's computer
    "image_sha256",      # hash of that file, so a frame cannot be swapped silently
    "image_width",       # pixels; the coordinate space of every box for this frame
    "image_height",
    "scene",             # which scene/setup the frame came from
    "posture",           # upright / lying-down / none
    "occlusion",         # unoccluded / partly-covered / -
    "light",             # room / low
    "distance_band",     # near / far
    "lux",               # measured illumination, if taken
    "expected_person_count",  # how many people the capture notes say are in frame
    "capture_utc",       # when the frame was captured
    "capture_source",    # provenance: export file, session, operator
    "notes",
)

GROUNDTRUTH_COLUMNS = (
    "frame_id",
    "image_file",
    "box_id",            # unique within the frame; `none` = annotated, no person
    "x_min",
    "y_min",
    "x_max",
    "y_max",
    "annotator_id",
    "annotated_utc",
    "notes",
)

RUNS_COLUMNS = (
    "frame_id",
    "model_name",        # e.g. efficientdet_lite0
    "model_version",     # e.g. mediapipe-tasks-vision 0.10.21
    "delegate",          # CPU / GPU
    "score_threshold",   # the detector's own threshold (shipped: 0.4)
    "max_results",
    "infer_ms",          # the dashboard's own per-frame measurement
    "n_boxes",           # boxes the detector returned on this frame
    "image_width",
    "image_height",
    "export_utc",
    "export_source",     # the export file this row was imported from
    "notes",
)

PREDICTIONS_COLUMNS = (
    "frame_id",
    "image_file",
    "pred_id",           # unique within the frame
    "x_min",
    "y_min",
    "x_max",
    "y_max",
    "confidence",        # the detector's score, 0 to 1
    "model_name",
    "model_version",
    "infer_ms",
    "export_utc",
    "export_source",
    "notes",
)


def _text(row: dict, key: str) -> str:
    return str(row.get(key, "") or "").strip()


def _number(row: dict, key: str) -> float | None:
    raw = _text(row, key)
    if not raw:
        return None
    return float(raw)


@dataclass
class Frame:
    """One frame of the test set, with whatever has been recorded about it."""

    frame_id: str
    image_file: str = ""
    image_width: float | None = None
    image_height: float | None = None
    scene: str = ""
    conditions: dict[str, str] = field(default_factory=dict)
    lux: str = ""
    expected_person_count: int | None = None
    capture_utc: str = ""
    capture_source: str = ""
    notes: str = ""

    annotated: bool = False
    annotators: set[str] = field(default_factory=set)
    gt: list[Box] = field(default_factory=list)

    ran: bool = False
    runs: list[dict] = field(default_factory=list)
    preds: list[Box] = field(default_factory=list)

    @property
    def scorable(self) -> bool:
        """Only a frame that was both annotated and run contributes a metric."""
        return self.annotated and self.ran

    @property
    def person_free(self) -> bool:
        return self.annotated and not self.gt

    @property
    def condition_key(self) -> tuple[str, ...]:
        return tuple(self.conditions.get(name, "") for name in CONDITIONS)

    @property
    def infer_ms(self) -> float | None:
        values = [r["infer_ms"] for r in self.runs if r.get("infer_ms") is not None]
        return values[-1] if values else None

    @property
    def model_label(self) -> str:
        for run in self.runs:
            name = run.get("model_name", "")
            version = run.get("model_version", "")
            if name or version:
                return f"{name} {version}".strip()
        return ""


@dataclass
class Dataset:
    frames: dict[str, Frame] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    present: dict[str, bool] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)

    @property
    def scorable(self) -> list[Frame]:
        return [f for f in self.frames.values() if f.scorable]

    @property
    def any_input(self) -> bool:
        return bool(self.frames)

    def excluded(self) -> list[tuple[Frame, str]]:
        out = []
        for frame in self.frames.values():
            if frame.scorable:
                continue
            if not frame.annotated and not frame.ran:
                reason = "not annotated and detector not run"
            elif not frame.annotated:
                reason = "detector run, not annotated [PENDING MEASUREMENT: annotation]"
            else:
                reason = "annotated, detector not run [PENDING MEASUREMENT: prediction]"
            out.append((frame, reason))
        return sorted(out, key=lambda pair: pair[0].frame_id)


def load_dataset(results_dir: Path) -> Dataset:
    """Read the four sheets, validate them against each other, and join them."""
    data = Dataset()
    paths = {
        FRAMES_INDEX_FILE: results_dir / FRAMES_INDEX_FILE,
        GROUNDTRUTH_FILE: results_dir / GROUNDTRUTH_FILE,
        RUNS_FILE: results_dir / RUNS_FILE,
        PREDICTIONS_FILE: results_dir / PREDICTIONS_FILE,
    }
    for name, path in paths.items():
        data.present[name] = path.exists()

    _load_index(read_rows(paths[FRAMES_INDEX_FILE]), data)
    data.row_counts[FRAMES_INDEX_FILE] = len(data.frames)
    gt_rows = read_rows(paths[GROUNDTRUTH_FILE])
    run_rows = read_rows(paths[RUNS_FILE])
    pred_rows = read_rows(paths[PREDICTIONS_FILE])
    data.row_counts[GROUNDTRUTH_FILE] = len(gt_rows)
    data.row_counts[RUNS_FILE] = len(run_rows)
    data.row_counts[PREDICTIONS_FILE] = len(pred_rows)
    _load_groundtruth(gt_rows, data)
    _load_runs(run_rows, data)
    _load_predictions(pred_rows, data)
    _cross_check(data)
    return data


def _frame_of(data: Dataset, row: dict, sheet: str, line: int) -> Frame | None:
    frame_id = _text(row, "frame_id")
    if not frame_id:
        data.errors.append(f"{sheet} line {line}: empty frame_id; row dropped")
        return None
    frame = data.frames.get(frame_id)
    if frame is None:
        data.errors.append(
            f"{sheet} line {line}: frame_id {frame_id!r} is not in {FRAMES_INDEX_FILE}; "
            "row dropped (a frame is added to the test set only through the index)"
        )
        return None
    declared = _text(row, "image_file")
    if declared and frame.image_file and declared != frame.image_file:
        data.errors.append(
            f"{sheet} line {line}: image_file {declared!r} disagrees with the index "
            f"({frame.image_file!r}) for frame {frame_id}; row dropped"
        )
        return None
    return frame


def _load_index(rows: list[dict], data: Dataset) -> None:
    for line, row in enumerate(rows, start=2):
        frame_id = _text(row, "frame_id")
        if not frame_id:
            data.errors.append(f"{FRAMES_INDEX_FILE} line {line}: empty frame_id; row dropped")
            continue
        if frame_id in data.frames:
            data.errors.append(
                f"{FRAMES_INDEX_FILE} line {line}: duplicate frame_id {frame_id!r}; row dropped"
            )
            continue
        try:
            width = _number(row, "image_width")
            height = _number(row, "image_height")
            expected = _number(row, "expected_person_count")
        except ValueError as err:
            data.errors.append(f"{FRAMES_INDEX_FILE} line {line}: {err}; row dropped")
            continue
        data.frames[frame_id] = Frame(
            frame_id=frame_id,
            image_file=_text(row, "image_file"),
            image_width=width,
            image_height=height,
            scene=_text(row, "scene"),
            conditions={name: _text(row, name) for name in CONDITIONS},
            lux=_text(row, "lux"),
            expected_person_count=int(expected) if expected is not None else None,
            capture_utc=_text(row, "capture_utc"),
            capture_source=_text(row, "capture_source"),
            notes=_text(row, "notes"),
        )


def _load_groundtruth(rows: list[dict], data: Dataset) -> None:
    seen: set[tuple[str, str]] = set()
    for line, row in enumerate(rows, start=2):
        frame = _frame_of(data, row, GROUNDTRUTH_FILE, line)
        if frame is None:
            continue
        box_id = _text(row, "box_id")
        if not box_id:
            data.errors.append(f"{GROUNDTRUTH_FILE} line {line}: empty box_id; row dropped")
            continue
        if (frame.frame_id, box_id) in seen:
            data.errors.append(
                f"{GROUNDTRUTH_FILE} line {line}: duplicate box_id {box_id!r} "
                f"on frame {frame.frame_id}; row dropped"
            )
            continue
        coords = [_text(row, k) for k in ("x_min", "y_min", "x_max", "y_max")]
        annotator = _text(row, "annotator_id")
        if not annotator:
            data.errors.append(
                f"{GROUNDTRUTH_FILE} line {line}: no annotator_id on frame "
                f"{frame.frame_id}; row dropped (every annotation names its annotator)"
            )
            continue
        if box_id == EMPTY_BOX_ID:
            if any(coords):
                data.errors.append(
                    f"{GROUNDTRUTH_FILE} line {line}: box_id {EMPTY_BOX_ID!r} means "
                    "'no person in this frame' and must have blank coordinates; row dropped"
                )
                continue
            seen.add((frame.frame_id, box_id))
            frame.annotated = True
            frame.annotators.add(annotator)
            continue
        if not all(coords):
            data.errors.append(
                f"{GROUNDTRUTH_FILE} line {line}: incomplete coordinates on frame "
                f"{frame.frame_id} box {box_id} (use box_id {EMPTY_BOX_ID!r} for a "
                "person-free frame); row dropped"
            )
            continue
        try:
            box = make_box(
                *(float(v) for v in coords),
                where=f"{GROUNDTRUTH_FILE} line {line} ({frame.frame_id}/{box_id})",
                key=("gt", box_id),
                source=f"{frame.frame_id}/{box_id}",
                image_width=frame.image_width,
                image_height=frame.image_height,
            )
        except (BoxError, ValueError) as err:
            data.errors.append(f"{err}; row dropped")
            continue
        seen.add((frame.frame_id, box_id))
        frame.annotated = True
        frame.annotators.add(annotator)
        frame.gt.append(box)


def _load_runs(rows: list[dict], data: Dataset) -> None:
    for line, row in enumerate(rows, start=2):
        frame = _frame_of(data, row, RUNS_FILE, line)
        if frame is None:
            continue
        try:
            record = {
                "model_name": _text(row, "model_name"),
                "model_version": _text(row, "model_version"),
                "delegate": _text(row, "delegate"),
                "score_threshold": _number(row, "score_threshold"),
                "max_results": _number(row, "max_results"),
                "infer_ms": _number(row, "infer_ms"),
                "n_boxes": _number(row, "n_boxes"),
                "export_utc": _text(row, "export_utc"),
                "export_source": _text(row, "export_source"),
                "notes": _text(row, "notes"),
            }
        except ValueError as err:
            data.errors.append(f"{RUNS_FILE} line {line}: {err}; row dropped")
            continue
        if not record["model_name"] and not record["model_version"]:
            data.errors.append(
                f"{RUNS_FILE} line {line}: no model_name or model_version on frame "
                f"{frame.frame_id}; row dropped (a prediction has to say which detector made it)"
            )
            continue
        if frame.runs:
            data.warnings.append(
                f"{RUNS_FILE} line {line}: frame {frame.frame_id} already has a detector "
                "run; both are kept in the sheet, and the metrics use the predictions "
                "as recorded. Re-running the detector on a frame needs a new frame_id."
            )
        frame.ran = True
        frame.runs.append(record)


def _load_predictions(rows: list[dict], data: Dataset) -> None:
    seen: set[tuple[str, str]] = set()
    for line, row in enumerate(rows, start=2):
        frame = _frame_of(data, row, PREDICTIONS_FILE, line)
        if frame is None:
            continue
        pred_id = _text(row, "pred_id")
        if not pred_id:
            data.errors.append(f"{PREDICTIONS_FILE} line {line}: empty pred_id; row dropped")
            continue
        if (frame.frame_id, pred_id) in seen:
            data.errors.append(
                f"{PREDICTIONS_FILE} line {line}: duplicate pred_id {pred_id!r} "
                f"on frame {frame.frame_id}; row dropped"
            )
            continue
        if not frame.ran:
            data.errors.append(
                f"{PREDICTIONS_FILE} line {line}: frame {frame.frame_id} has a predicted "
                f"box but no row in {RUNS_FILE}; row dropped (the run record is what says "
                "which detector produced it)"
            )
            continue
        try:
            box = make_box(
                float(_text(row, "x_min")),
                float(_text(row, "y_min")),
                float(_text(row, "x_max")),
                float(_text(row, "y_max")),
                where=f"{PREDICTIONS_FILE} line {line} ({frame.frame_id}/{pred_id})",
                key=("pred", pred_id),
                confidence=_number(row, "confidence"),
                source=f"{frame.frame_id}/{pred_id}",
                image_width=frame.image_width,
                image_height=frame.image_height,
            )
        except (BoxError, ValueError) as err:
            data.errors.append(f"{err}; row dropped")
            continue
        if box.confidence is None:
            data.warnings.append(
                f"{PREDICTIONS_FILE} line {line}: frame {frame.frame_id} box {pred_id} "
                "has no confidence; it sorts last in the matching order and is excluded "
                "from the score distribution"
            )
        seen.add((frame.frame_id, pred_id))
        frame.preds.append(box)


def _cross_check(data: Dataset) -> None:
    for frame in data.frames.values():
        if frame.annotated and frame.expected_person_count is not None:
            if len(frame.gt) != frame.expected_person_count:
                data.warnings.append(
                    f"frame {frame.frame_id}: {len(frame.gt)} annotated box(es) but the index "
                    f"declares expected_person_count={frame.expected_person_count}; "
                    "check the annotation against the capture notes"
                )
        for run in frame.runs:
            declared = run.get("n_boxes")
            if declared is not None and len(frame.preds) != declared:
                data.warnings.append(
                    f"frame {frame.frame_id}: {len(frame.preds)} prediction row(s) but the "
                    f"run record declares n_boxes={declared:g}; the export may be incomplete"
                )
        if frame.scorable and not any(frame.conditions.get(c) for c in CONDITIONS):
            data.warnings.append(
                f"frame {frame.frame_id}: no condition labels, so it appears only in the "
                "pooled metrics, not in the per-condition tables"
            )
