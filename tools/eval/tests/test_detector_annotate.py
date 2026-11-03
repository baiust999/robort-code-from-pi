"""E18 annotation entry: what it accepts, and what it refuses to write.

Scope: tools/eval/detector_annotate.py. Sheets live in pytest's tmp_path, so
tools/eval/results/ is neither read nor written.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL_DIR))

from common import read_rows  # noqa: E402
from detector_data import FRAMES_INDEX_COLUMNS, FRAMES_INDEX_FILE, GROUNDTRUTH_FILE  # noqa: E402


def index(results: Path, frames=("F1",)) -> None:
    results.mkdir(parents=True, exist_ok=True)
    with (results / FRAMES_INDEX_FILE).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FRAMES_INDEX_COLUMNS))
        writer.writeheader()
        for frame_id in frames:
            writer.writerow({
                **{c: "" for c in FRAMES_INDEX_COLUMNS},
                "frame_id": frame_id,
                "image_file": f"{frame_id}.jpg",
                "image_width": 640,
                "image_height": 480,
            })


def annotate(results: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(EVAL_DIR / "detector_annotate.py"), *args,
         "--results-dir", str(results)],
        capture_output=True, text=True, check=False,
    )


def test_a_box_is_appended_with_its_annotator_and_timestamp(tmp_path):
    index(tmp_path)
    done = annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=100", "y_min=80",
                    "x_max=210", "y_max=330", "annotator_id=AB", "notes=left arm hidden")
    assert done.returncode == 0, done.stderr
    row = read_rows(tmp_path / GROUNDTRUTH_FILE)[0]
    assert (row["frame_id"], row["box_id"], row["annotator_id"]) == ("F1", "b1", "AB")
    assert (row["x_min"], row["y_max"]) == ("100", "330")
    assert row["image_file"] == "F1.jpg"      # taken from the index, not retyped
    assert row["annotated_utc"].startswith("20")
    assert row["notes"] == "left arm hidden"


def test_two_people_are_two_rows(tmp_path):
    index(tmp_path)
    annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
             "x_max=110", "y_max=210", "annotator_id=AB")
    annotate(tmp_path, "box", "frame_id=F1", "box_id=b2", "x_min=300", "y_min=10",
             "x_max=400", "y_max=210", "annotator_id=AB")
    assert [r["box_id"] for r in read_rows(tmp_path / GROUNDTRUTH_FILE)] == ["b1", "b2"]


def test_a_person_free_frame_is_recorded_explicitly(tmp_path):
    index(tmp_path)
    assert annotate(tmp_path, "empty", "frame_id=F1", "annotator_id=AB").returncode == 0
    row = read_rows(tmp_path / GROUNDTRUTH_FILE)[0]
    assert row["box_id"] == "none"
    assert (row["x_min"], row["y_min"], row["x_max"], row["y_max"]) == ("", "", "", "")


def test_an_unknown_frame_is_refused(tmp_path):
    index(tmp_path)
    done = annotate(tmp_path, "box", "frame_id=NOPE", "box_id=b1", "x_min=10", "y_min=10",
                    "x_max=110", "y_max=210", "annotator_id=AB")
    assert done.returncode == 2
    assert "is not in" in done.stderr
    assert not (tmp_path / GROUNDTRUTH_FILE).exists()


def test_an_annotation_without_an_annotator_is_refused(tmp_path):
    index(tmp_path)
    done = annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
                    "x_max=110", "y_max=210")
    assert done.returncode == 2
    assert "annotator_id= is required" in done.stderr


def test_invalid_coordinates_are_refused(tmp_path):
    index(tmp_path)
    for coords in (("x_min=210", "y_min=10", "x_max=110", "y_max=210"),
                   ("x_min=10", "y_min=10", "x_max=900", "y_max=210"),
                   ("x_min=10", "y_min=10", "x_max=110", "y_max=10")):
        done = annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", *coords,
                        "annotator_id=AB")
        assert done.returncode == 2, coords
        assert "rejected:" in done.stderr
    assert not (tmp_path / GROUNDTRUTH_FILE).exists()


def test_a_box_cannot_contradict_a_person_free_record(tmp_path):
    index(tmp_path)
    annotate(tmp_path, "empty", "frame_id=F1", "annotator_id=AB")
    done = annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
                    "x_max=110", "y_max=210", "annotator_id=AB")
    assert done.returncode == 2
    assert "recorded as person-free" in done.stderr
    assert len(read_rows(tmp_path / GROUNDTRUTH_FILE)) == 1


def test_empty_cannot_contradict_an_annotated_box(tmp_path):
    index(tmp_path)
    annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
             "x_max=110", "y_max=210", "annotator_id=AB")
    done = annotate(tmp_path, "empty", "frame_id=F1", "annotator_id=AB")
    assert done.returncode == 2
    assert "would contradict" in done.stderr


def test_a_duplicate_box_id_is_refused(tmp_path):
    index(tmp_path)
    annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
             "x_max=110", "y_max=210", "annotator_id=AB")
    done = annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=12", "y_min=12",
                    "x_max=112", "y_max=212", "annotator_id=AB")
    assert done.returncode == 2
    assert "already has a box" in done.stderr


def test_the_reserved_box_id_is_refused_for_a_box(tmp_path):
    index(tmp_path)
    done = annotate(tmp_path, "box", "frame_id=F1", "box_id=none", "x_min=10", "y_min=10",
                    "x_max=110", "y_max=210", "annotator_id=AB")
    assert done.returncode == 2
    assert "reserved" in done.stderr


def test_list_unannotated_names_the_frames_still_to_do(tmp_path):
    index(tmp_path, frames=("F1", "F2"))
    annotate(tmp_path, "empty", "frame_id=F1", "annotator_id=AB")
    done = annotate(tmp_path, "--list-unannotated")
    assert done.returncode == 0
    assert "1 of 2 frame(s) are not annotated yet" in done.stdout
    assert "F2" in done.stdout and "F1" not in done.stdout


def test_show_reports_what_has_been_entered(tmp_path):
    index(tmp_path)
    annotate(tmp_path, "box", "frame_id=F1", "box_id=b1", "x_min=10", "y_min=10",
             "x_max=110", "y_max=210", "annotator_id=AB")
    done = annotate(tmp_path, "--show", "frame_id=F1")
    assert "1 box(es)" in done.stdout
    assert "detector NOT RUN" in done.stdout
