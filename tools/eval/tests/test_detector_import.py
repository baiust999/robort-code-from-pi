"""E18 import of the dashboard's detector export: validation and refusals.

Scope: tools/eval/detector_import.py. Each test builds an export directory and
a results directory under pytest's tmp_path, so nothing in tools/eval/results/
is read or written.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

EVAL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_DIR))

from common import read_rows  # noqa: E402
from detector_data import (  # noqa: E402
    FRAMES_INDEX_FILE,
    PREDICTIONS_FILE,
    RUNS_FILE,
    load_dataset,
)
from detector_import import EXPORT_SCHEMA  # noqa: E402

BATCH = [
    "--scene", "corridor-A", "--posture", "upright", "--occlusion", "unoccluded",
    "--light", "room", "--distance", "near", "--expected-persons", "1",
]


def record(frame_id="e18-20261103T184500123Z", predictions=None, **overrides):
    out = {
        "schema": EXPORT_SCHEMA,
        "frame_id": frame_id,
        "image_file": f"{frame_id}.jpg",
        "captured_utc": "2026-11-03T18:45:00.123Z",
        "video": {"width": 640, "height": 480, "current_time_s": 12.5},
        "detector": {
            "model_name": "efficientdet_lite0",
            "model_version": "mediapipe-tasks-vision 0.10.21",
            "delegate": "CPU",
            "score_threshold": 0.4,
            "max_results": 5,
            "category_allowlist": ["person"],
        },
        "infer_ms": 73.4,
        "n_boxes": 1,
        "predictions": [
            {"pred_id": "p1", "x_min": 100, "y_min": 80, "x_max": 210, "y_max": 330,
             "confidence": 0.8123},
        ] if predictions is None else predictions,
        "frame_written": True,
        "user_agent": "test",
    }
    out.update(overrides)
    return out


def export(directory: Path, data: dict, with_image=True) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{data['frame_id']}.json"
    path.write_text(json.dumps(data))
    if with_image:
        (directory / str(data["image_file"])).write_bytes(b"not-a-real-jpeg-but-hashable")
    return path


def run_import(source: Path, results: Path, *extra: str):
    return subprocess.run(
        [sys.executable, str(EVAL_DIR / "detector_import.py"), "--from", str(source),
         "--results-dir", str(results), *extra],
        capture_output=True, text=True, check=False,
    )


def test_a_valid_export_becomes_an_index_run_and_prediction_row(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record())
    done = run_import(source, results, *BATCH)
    assert done.returncode == 0, done.stderr

    index = read_rows(results / FRAMES_INDEX_FILE)
    assert len(index) == 1
    row = index[0]
    assert row["frame_id"] == "e18-20261103T184500123Z"
    assert row["posture"] == "upright" and row["distance_band"] == "near"
    assert row["image_width"] == "640"
    assert len(row["image_sha256"]) == 64
    assert row["capture_source"].endswith(f"({EXPORT_SCHEMA})")

    runs = read_rows(results / RUNS_FILE)
    assert runs[0]["model_name"] == "efficientdet_lite0"
    assert runs[0]["infer_ms"] == "73.4" and runs[0]["n_boxes"] == "1"

    preds = read_rows(results / PREDICTIONS_FILE)
    assert preds[0]["confidence"] == "0.8123"
    assert (preds[0]["x_min"], preds[0]["y_max"]) == ("100", "330")

    # The chain loads cleanly, and the frame waits for annotation.
    data = load_dataset(results)
    assert not data.errors
    frame = data.frames["e18-20261103T184500123Z"]
    assert frame.ran and not frame.annotated and len(frame.preds) == 1


def test_no_ground_truth_sheet_is_created(tmp_path):
    """Importing a prediction must never create an annotation."""
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record())
    run_import(source, results, *BATCH)
    assert not (results / "detector_groundtruth.csv").exists()


def test_a_frame_with_no_detections_still_records_the_run(tmp_path):
    """'The detector ran and found nobody' is a measurement; it must be kept."""
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record(predictions=[], n_boxes=0))
    assert run_import(source, results, *BATCH).returncode == 0
    assert read_rows(results / RUNS_FILE)[0]["n_boxes"] == "0"
    assert read_rows(results / PREDICTIONS_FILE) == []
    assert load_dataset(results).frames["e18-20261103T184500123Z"].ran


def test_dry_run_writes_nothing(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record())
    done = run_import(source, results, *BATCH, "--dry-run")
    assert done.returncode == 0
    assert "would import" in done.stdout
    assert not (results / FRAMES_INDEX_FILE).exists()


def test_a_second_import_of_the_same_frame_is_skipped(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record())
    run_import(source, results, *BATCH)
    done = run_import(source, results, *BATCH)
    assert "already in" in done.stdout
    assert len(read_rows(results / FRAMES_INDEX_FILE)) == 1
    assert len(read_rows(results / PREDICTIONS_FILE)) == 1


def test_a_foreign_schema_is_refused(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record(schema="something-else/9"))
    done = run_import(source, results, *BATCH)
    assert done.returncode == 1
    assert "is not" in done.stderr
    assert not (results / FRAMES_INDEX_FILE).exists()


@pytest.mark.parametrize("prediction", [
    {"pred_id": "p1", "x_min": 210, "y_min": 80, "x_max": 100, "y_max": 330, "confidence": 0.8},
    {"pred_id": "p1", "x_min": 100, "y_min": 80, "x_max": 900, "y_max": 330, "confidence": 0.8},
    {"pred_id": "p1", "x_min": 100, "y_min": 80, "x_max": 210, "y_max": 330, "confidence": 1.4},
    {"pred_id": "p1", "x_min": 100, "y_min": 80, "x_max": 210, "confidence": 0.8},
])
def test_an_unusable_prediction_stops_the_whole_record(tmp_path, prediction):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record(predictions=[prediction]))
    done = run_import(source, results, *BATCH)
    assert done.returncode == 1
    assert not (results / FRAMES_INDEX_FILE).exists()


def test_a_record_without_its_frame_is_skipped_by_default(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record(), with_image=False)
    done = run_import(source, results, *BATCH)
    assert done.returncode == 1
    assert "not found beside it" in done.stderr
    assert not (results / FRAMES_INDEX_FILE).exists()


def test_a_missing_frame_can_be_imported_but_is_marked_pending(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    export(source, record(), with_image=False)
    done = run_import(source, results, *BATCH, "--allow-missing-image")
    assert done.returncode == 1  # reported as a problem, and imported
    row = read_rows(results / FRAMES_INDEX_FILE)[0]
    assert row["image_sha256"] == ""
    assert "[PENDING MEASUREMENT: image SHA-256" in row["notes"]


def test_no_json_files_is_an_error_not_an_empty_import(tmp_path):
    source, results = tmp_path / "exports", tmp_path / "results"
    source.mkdir()
    done = run_import(source, results, *BATCH)
    assert done.returncode == 2
    assert "no .json export files" in done.stderr
