"""E18 dataset loader and report: the integrity rules, on throwaway CSVs.

Scope: tools/eval/detector_data.py and the report in tools/eval/detector_eval.py.
Every sheet here is written into a pytest tmp_path, so no test reads or writes
anything in tools/eval/results/ and no measured record is touched.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

EVAL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_DIR))

from detector_data import (  # noqa: E402
    FRAMES_INDEX_COLUMNS,
    FRAMES_INDEX_FILE,
    GROUNDTRUTH_COLUMNS,
    GROUNDTRUTH_FILE,
    PREDICTIONS_COLUMNS,
    PREDICTIONS_FILE,
    RUNS_COLUMNS,
    RUNS_FILE,
    load_dataset,
)
from detector_iou import match_frame  # noqa: E402

MODEL = {"model_name": "efficientdet_lite0", "model_version": "mediapipe-tasks-vision 0.10.21"}


def write(path: Path, columns, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})


def frame_row(frame_id, **kwargs):
    row = {
        "frame_id": frame_id,
        "image_file": f"{frame_id}.jpg",
        "image_width": 640,
        "image_height": 480,
        "posture": "upright",
        "occlusion": "unoccluded",
        "light": "room",
        "distance_band": "near",
    }
    row.update(kwargs)
    return row


def gt_row(frame_id, box_id, coords=None, annotator="AB", **kwargs):
    row = {
        "frame_id": frame_id,
        "image_file": f"{frame_id}.jpg",
        "box_id": box_id,
        "annotator_id": annotator,
    }
    if coords:
        row.update(dict(zip(("x_min", "y_min", "x_max", "y_max"), coords)))
    row.update(kwargs)
    return row


def run_row(frame_id, infer_ms=70, n_boxes=1, **kwargs):
    row = {
        "frame_id": frame_id,
        **MODEL,
        "delegate": "CPU",
        "score_threshold": 0.4,
        "max_results": 5,
        "infer_ms": infer_ms,
        "n_boxes": n_boxes,
    }
    row.update(kwargs)
    return row


def pred_row(frame_id, pred_id, coords, confidence=0.9, **kwargs):
    row = {
        "frame_id": frame_id,
        "image_file": f"{frame_id}.jpg",
        "pred_id": pred_id,
        **dict(zip(("x_min", "y_min", "x_max", "y_max"), coords)),
        "confidence": confidence,
        **MODEL,
        "infer_ms": 70,
    }
    row.update(kwargs)
    return row


def build(results: Path, frames=(), gts=(), runs=(), preds=()):
    write(results / FRAMES_INDEX_FILE, FRAMES_INDEX_COLUMNS, frames)
    write(results / GROUNDTRUTH_FILE, GROUNDTRUTH_COLUMNS, gts)
    write(results / RUNS_FILE, RUNS_COLUMNS, runs)
    write(results / PREDICTIONS_FILE, PREDICTIONS_COLUMNS, preds)
    return load_dataset(results)


# --- joining the four sheets ----------------------------------------------


def test_a_fully_recorded_frame_is_scored(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1", expected_person_count=1)],
        gts=[gt_row("F1", "b1", (100, 100, 200, 300))],
        runs=[run_row("F1")],
        preds=[pred_row("F1", "p1", (102, 101, 202, 301))],
    )
    assert not data.errors and not data.warnings
    frame = data.frames["F1"]
    assert frame.scorable and frame.annotated and frame.ran
    assert len(frame.gt) == 1 and len(frame.preds) == 1
    assert match_frame(frame.preds, frame.gt).tp == 1


def test_an_unannotated_frame_is_not_treated_as_person_free(tmp_path):
    """The failure this guards against invents false positives out of nothing."""
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        runs=[run_row("F1", n_boxes=1)],
        preds=[pred_row("F1", "p1", (10, 10, 60, 120))],
    )
    frame = data.frames["F1"]
    assert frame.ran and not frame.annotated
    assert not frame.scorable and not frame.person_free
    assert data.scorable == []
    reasons = dict((f.frame_id, why) for f, why in data.excluded())
    assert "not annotated" in reasons["F1"]


def test_a_frame_the_detector_never_ran_on_is_not_a_missed_detection(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (100, 100, 200, 300))],
    )
    frame = data.frames["F1"]
    assert frame.annotated and not frame.ran and not frame.scorable
    reasons = dict((f.frame_id, why) for f, why in data.excluded())
    assert "detector not run" in reasons["F1"]


def test_a_person_free_frame_needs_an_explicit_record(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F80", posture="none", occlusion="-", expected_person_count=0)],
        gts=[gt_row("F80", "none", notes="chairs only")],
        runs=[run_row("F80", n_boxes=0)],
    )
    frame = data.frames["F80"]
    assert not data.errors
    assert frame.annotated and frame.person_free and frame.gt == []
    assert frame.scorable


def test_the_empty_marker_may_not_carry_coordinates(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F80")],
        gts=[gt_row("F80", "none", (1, 2, 3, 4))],
    )
    assert any("must have blank coordinates" in e for e in data.errors)
    assert not data.frames["F80"].annotated


def test_an_unknown_frame_id_is_rejected_not_created(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F2", "b1", (10, 10, 50, 90))],
        runs=[run_row("F3")],
        preds=[pred_row("F4", "p1", (10, 10, 50, 90))],
    )
    assert list(data.frames) == ["F1"]
    assert sum("is not in" in e for e in data.errors) == 3


def test_image_file_disagreeing_with_the_index_is_rejected(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (10, 10, 50, 90), image_file="someone-elses-frame.jpg")],
    )
    assert any("disagrees with the index" in e for e in data.errors)
    assert not data.frames["F1"].annotated


def test_an_annotation_without_an_annotator_is_rejected(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (10, 10, 50, 90), annotator="")],
    )
    assert any("no annotator_id" in e for e in data.errors)
    assert not data.frames["F1"].annotated


def test_duplicate_ids_are_rejected(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1"), frame_row("F1", scene="second")],
        gts=[gt_row("F1", "b1", (10, 10, 50, 90)), gt_row("F1", "b1", (11, 11, 51, 91))],
        runs=[run_row("F1")],
        preds=[pred_row("F1", "p1", (10, 10, 50, 90)), pred_row("F1", "p1", (12, 12, 52, 92))],
    )
    assert sum("duplicate" in e for e in data.errors) == 3
    assert len(data.frames["F1"].gt) == 1
    assert len(data.frames["F1"].preds) == 1


def test_a_prediction_without_a_run_record_is_rejected(tmp_path):
    """The run record is what names the detector that made the prediction."""
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (10, 10, 50, 90))],
        preds=[pred_row("F1", "p1", (10, 10, 50, 90))],
    )
    assert any(f"no row in {RUNS_FILE}" in e for e in data.errors)
    assert data.frames["F1"].preds == []


def test_a_run_record_without_a_model_is_rejected(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        runs=[{"frame_id": "F1", "infer_ms": 70, "n_boxes": 0}],
    )
    assert any("no model_name or model_version" in e for e in data.errors)
    assert not data.frames["F1"].ran


def test_invalid_coordinates_are_rejected_at_load(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[
            gt_row("F1", "b1", (200, 100, 100, 300)),    # x_max before x_min
            gt_row("F1", "b2", (10, 10, 900, 300)),      # outside the 640 px width
            gt_row("F1", "b3", (10, 10, 60, 10)),        # zero height
            gt_row("F1", "b4", (10, 10, 60, 120)),       # the one usable box
        ],
        runs=[run_row("F1")],
    )
    assert len(data.errors) == 3
    assert [box.key[1] for box in data.frames["F1"].gt] == ["b4"]


def test_an_incomplete_coordinate_row_is_rejected(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[{"frame_id": "F1", "box_id": "b1", "x_min": 10, "y_min": 10, "annotator_id": "AB"}],
    )
    assert any("incomplete coordinates" in e for e in data.errors)


def test_expected_person_count_disagreement_is_warned_about(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1", expected_person_count=2)],
        gts=[gt_row("F1", "b1", (10, 10, 60, 120))],
        runs=[run_row("F1", n_boxes=0)],
    )
    assert any("expected_person_count=2" in w for w in data.warnings)
    # It is a warning, not a rejection: the annotation is still scored.
    assert data.frames["F1"].scorable


def test_n_boxes_disagreement_is_warned_about(tmp_path):
    data = build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (10, 10, 60, 120))],
        runs=[run_row("F1", n_boxes=3)],
        preds=[pred_row("F1", "p1", (10, 10, 60, 120))],
    )
    assert any("n_boxes=3" in w for w in data.warnings)


def test_missing_sheets_load_as_an_empty_dataset(tmp_path):
    data = load_dataset(tmp_path)
    assert data.frames == {} and not data.errors and not data.any_input
    assert all(present is False for present in data.present.values())


# --- the report ------------------------------------------------------------


def report(results_dir: Path, *extra: str) -> str:
    done = subprocess.run(
        [sys.executable, str(EVAL_DIR / "detector_eval.py"), "--results-dir", str(results_dir),
         *extra],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode in (0, 1), done.stderr
    return done.stdout


def test_report_on_an_empty_results_dir_is_pending(tmp_path):
    text = report(tmp_path)
    assert "[PENDING MEASUREMENT: E18 person detection.]" in text
    assert "at most 1 false alarm per minute over at least 10 min" in text


def test_report_counts_a_hand_built_set_correctly(tmp_path):
    """Three frames worked out by hand: TP 2, FP 2, FN 1."""
    build(
        tmp_path,
        frames=[
            frame_row("F1", expected_person_count=1),
            frame_row("F2", expected_person_count=2),
            frame_row("F3", posture="none", occlusion="-", expected_person_count=0),
        ],
        gts=[
            gt_row("F1", "b1", (100, 100, 200, 300)),
            gt_row("F2", "b1", (10, 10, 110, 210)),
            gt_row("F2", "b2", (300, 10, 400, 210)),
            gt_row("F3", "none"),
        ],
        runs=[run_row("F1", 60, 1), run_row("F2", 80, 2), run_row("F3", 70, 1)],
        preds=[
            pred_row("F1", "p1", (101, 101, 201, 301), 0.95),   # TP
            pred_row("F2", "p1", (12, 12, 112, 212), 0.90),     # TP
            pred_row("F2", "p2", (500, 400, 600, 470), 0.55),   # FP (b2 missed -> FN)
            pred_row("F3", "p1", (20, 20, 120, 220), 0.60),     # FP on a person-free frame
        ],
    )
    text = report(tmp_path)
    assert "| **all scored frames** | 3 | 4 | 2 | 2 | 1 |" in text
    assert "Precision = TP / (TP + FP) = 2 / 4 = 0.500" in text
    assert "recall = TP / (TP + FN) = 2 / 3 = 0.667" in text
    assert "| Frames scored (annotated and run) | 3 |" in text
    # The person-free frame's false positive is reported separately as well.
    assert "1 false-positive box(es) on 1 frame(s)" in text
    # Inference times come from the run sheet: median of 60, 70, 80.
    assert "median 70 ms" in text


def test_report_excludes_an_unannotated_frame_and_says_so(tmp_path):
    build(
        tmp_path,
        frames=[frame_row("F1"), frame_row("F2")],
        gts=[gt_row("F1", "b1", (100, 100, 200, 300))],
        runs=[run_row("F1"), run_row("F2", n_boxes=1)],
        preds=[
            pred_row("F1", "p1", (100, 100, 200, 300)),
            pred_row("F2", "p1", (10, 10, 60, 120)),
        ],
    )
    text = report(tmp_path)
    assert "| Frames scored (annotated and run) | 1 |" in text
    assert "| F2 | detector run, not annotated" in text
    # F2's box is not counted as a false positive.
    assert "| **all scored frames** | 1 | 1 | 1 | 0 | 0 |" in text


def test_report_evaluates_the_pass_criterion_in_the_easiest_stratum(tmp_path):
    build(
        tmp_path,
        frames=[frame_row(f"F{n}") for n in range(1, 4)],
        gts=[gt_row(f"F{n}", "b1", (100, 100, 200, 300)) for n in range(1, 4)],
        runs=[run_row(f"F{n}") for n in range(1, 4)],
        preds=[
            pred_row("F1", "p1", (100, 100, 200, 300)),
            pred_row("F2", "p1", (101, 101, 201, 301)),
            # F3: a box in the wrong place, so recall 2/3 and precision 2/3.
            pred_row("F3", "p1", (10, 10, 60, 120)),
        ],
    )
    text = report(tmp_path)
    assert "| recall | >= 0.80 | 0.667 | **not met** |" in text
    assert "| precision | >= 0.90 | 0.667 | **not met** |" in text


def test_report_marks_rejected_rows_and_strict_exits_non_zero(tmp_path):
    build(
        tmp_path,
        frames=[frame_row("F1")],
        gts=[gt_row("F1", "b1", (200, 100, 100, 300))],
        runs=[run_row("F1", n_boxes=0)],
    )
    text = report(tmp_path)
    assert "row(s) were rejected and are not scored" in text
    done = subprocess.run(
        [sys.executable, str(EVAL_DIR / "detector_eval.py"), "--results-dir", str(tmp_path),
         "--strict"],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 1


def test_report_keeps_the_banner_measurement_separate(tmp_path):
    write(
        tmp_path / "detector_banner.csv",
        ("segment", "person_free_s", "banner_raises", "notes"),
        [{"segment": "corridor-A", "person_free_s": 600, "banner_raises": 3, "notes": ""}],
    )
    text = report(tmp_path)
    assert "| corridor-A | 10.0 | 3 | 0.30 |" in text
    assert "| **all** | **10.0** | **3** | **0.30** |" in text
    assert "shares no counts with them" in text
    # Nothing from the banner sheet reaches the box-level metrics.
    assert "[PENDING MEASUREMENT: E18 person detection.]" in text


def test_report_flags_too_little_person_free_video(tmp_path):
    write(
        tmp_path / "detector_banner.csv",
        ("segment", "person_free_s", "banner_raises", "notes"),
        [{"segment": "short", "person_free_s": 120, "banner_raises": 0, "notes": ""}],
    )
    text = report(tmp_path)
    assert "Only 2.0 min of person-free video has been scored" in text


def test_report_never_scores_the_legacy_frame_level_sheet(tmp_path):
    write(
        tmp_path / "detector_frames.csv",
        ("frame", "posture", "person_present", "detected", "best_score", "infer_ms"),
        [{"frame": "old1", "posture": "upright", "person_present": 1, "detected": 1,
          "best_score": 0.81, "infer_ms": 70}],
    )
    text = report(tmp_path)
    assert "Legacy sheet `detector_frames.csv` (not scored)" in text
    assert "cannot be converted into an object-level measurement" in text
    assert "[PENDING MEASUREMENT: E18 person detection.]" in text


@pytest.mark.parametrize("threshold", ["0", "1.5", "-0.2"])
def test_report_rejects_an_impossible_iou_threshold(tmp_path, threshold):
    done = subprocess.run(
        [sys.executable, str(EVAL_DIR / "detector_eval.py"), "--results-dir", str(tmp_path),
         "--iou", threshold],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 2
