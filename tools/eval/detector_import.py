#!/usr/bin/env python3
"""E18: import the dashboard's own detector output into the evaluation sheets.

The detector runs in the operator's browser (Section 3.11), so its real output
exists nowhere else. In E18 capture mode the dashboard writes two files per
frame to the operator's Downloads folder (dashboard/src/lib/detectorExport.ts):

    e18-20261103T184500123Z.jpg    the frame, with no boxes drawn on it
    e18-20261103T184500123Z.json   the boxes that detector returned on it

This script reads those JSON records and appends them to

    results/detector_frames_index.csv    the frame manifest
    results/detector_runs.csv            one row per frame the detector ran on
    results/detector_predictions.csv      one row per predicted box

It never writes a ground-truth box: annotation is a separate, human step
(detector_annotate.py). It never invents a prediction, and a record it cannot
validate is reported and skipped rather than repaired.

**The frames themselves are not copied into the repository.** They show people,
and no image of a person is stored on the robot (Section 4.1 and Section 3.11).
The index records the file name and its SHA-256 so a frame cannot be swapped
for another one without the hash changing; the images stay on the operator's
computer.

One capture batch is one condition cell, so the stratum labels are given on the
command line and apply to every record in the run:

    ./detector_import.py --from ~/Downloads/e18-batch-01 \
        --scene corridor-A --posture upright --occlusion unoccluded \
        --light room --distance near --lux 320 --expected-persons 1

    ./detector_import.py --from ~/Downloads/e18-personfree \
        --scene corridor-A --posture none --occlusion - \
        --light room --distance near --expected-persons 0

    ./detector_import.py --from ~/Downloads/e18-batch-01 --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso, read_rows  # noqa: E402
from detector_data import (  # noqa: E402
    FRAMES_INDEX_COLUMNS,
    FRAMES_INDEX_FILE,
    PREDICTIONS_COLUMNS,
    PREDICTIONS_FILE,
    RUNS_COLUMNS,
    RUNS_FILE,
)
from detector_iou import BoxError, validate_box  # noqa: E402

EXPORT_SCHEMA = "robot-e18-detector-export/1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(problems: list[str], message: str) -> None:
    problems.append(message)


def read_record(path: Path, problems: list[str]) -> dict | None:
    """Parse and validate one exported JSON record. None if unusable."""
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as err:
        fail(problems, f"{path.name}: cannot be read as JSON ({err})")
        return None
    if not isinstance(record, dict):
        fail(problems, f"{path.name}: top level is not an object")
        return None
    schema = str(record.get("schema", ""))
    if schema != EXPORT_SCHEMA:
        fail(problems, f"{path.name}: schema {schema!r} is not {EXPORT_SCHEMA!r}")
        return None
    for key in ("frame_id", "image_file", "captured_utc", "detector", "predictions"):
        if key not in record:
            fail(problems, f"{path.name}: no {key!r} field")
            return None
    if not isinstance(record["predictions"], list):
        fail(problems, f"{path.name}: predictions is not a list")
        return None
    video = record.get("video") or {}
    width, height = video.get("width"), video.get("height")
    if not width or not height:
        fail(problems, f"{path.name}: no video width/height, so no coordinate space")
        return None
    for index, pred in enumerate(record["predictions"], start=1):
        where = f"{path.name} prediction {index}"
        if not isinstance(pred, dict):
            fail(problems, f"{where}: not an object")
            return None
        try:
            validate_box(
                float(pred["x_min"]), float(pred["y_min"]),
                float(pred["x_max"]), float(pred["y_max"]),
                where=where, image_width=float(width), image_height=float(height),
            )
            confidence = float(pred["confidence"])
        except (KeyError, TypeError, ValueError) as err:
            fail(problems, f"{where}: bad coordinates or confidence ({err})")
            return None
        except BoxError as err:
            fail(problems, str(err))
            return None
        if not 0.0 <= confidence <= 1.0:
            fail(problems, f"{where}: confidence {confidence} is outside [0, 1]")
            return None
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="source", type=Path, required=True,
                    help="directory holding the dashboard's exported .json (and .jpg) files")
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--scene", default="", help="which scene/setup this batch was captured in")
    ap.add_argument("--posture", default="", help="upright / lying-down / none")
    ap.add_argument("--occlusion", default="", help="unoccluded / partly-covered / -")
    ap.add_argument("--light", default="", help="room / low")
    ap.add_argument("--distance", default="", help="near / far")
    ap.add_argument("--lux", default="", help="measured illumination, if taken")
    ap.add_argument("--expected-persons", type=int, default=None,
                    help="how many people the capture notes say are in every frame of this batch")
    ap.add_argument("--notes", default="")
    ap.add_argument("--allow-missing-image", action="store_true",
                    help="import a record whose .jpg is not in the directory; the index then "
                         "carries no SHA-256 for that frame and the gap is recorded in notes")
    ap.add_argument("--dry-run", action="store_true", help="validate and report, write nothing")
    args = ap.parse_args()

    if not args.source.is_dir():
        print(f"not a directory: {args.source}", file=sys.stderr)
        return 2

    index_path = args.results_dir / FRAMES_INDEX_FILE
    runs_path = args.results_dir / RUNS_FILE
    preds_path = args.results_dir / PREDICTIONS_FILE
    known = {row["frame_id"] for row in read_rows(index_path) if row.get("frame_id")}

    files = sorted(args.source.glob("*.json"))
    if not files:
        print(f"no .json export files in {args.source}", file=sys.stderr)
        return 2

    problems: list[str] = []
    imported = skipped = boxes = 0
    for path in files:
        record = read_record(path, problems)
        if record is None:
            continue
        frame_id = str(record["frame_id"])
        if frame_id in known:
            print(f"skip {path.name}: frame_id {frame_id} is already in {FRAMES_INDEX_FILE}")
            skipped += 1
            continue
        image = args.source / str(record["image_file"])
        if image.exists():
            digest = sha256(image)
            image_note = args.notes
        elif args.allow_missing_image:
            digest = ""
            image_note = " ".join(
                part for part in (args.notes, "[PENDING MEASUREMENT: image SHA-256; the "
                                  "frame file was not beside its record at import]") if part
            )
            problems.append(
                f"{path.name}: {record['image_file']} not found; imported without a hash"
            )
        else:
            fail(problems, f"{path.name}: {record['image_file']} not found beside it; "
                           "skipped (pass --allow-missing-image to import anyway)")
            continue

        detector = record.get("detector") or {}
        video = record["video"]
        predictions = record["predictions"]
        source_label = f"{path.name} ({EXPORT_SCHEMA})"

        index_row = {
            "frame_id": frame_id,
            "image_file": record["image_file"],
            "image_sha256": digest,
            "image_width": video["width"],
            "image_height": video["height"],
            "scene": args.scene,
            "posture": args.posture,
            "occlusion": args.occlusion,
            "light": args.light,
            "distance_band": args.distance,
            "lux": args.lux,
            "expected_person_count": "" if args.expected_persons is None else args.expected_persons,
            "capture_utc": record["captured_utc"],
            "capture_source": source_label,
            "notes": image_note,
        }
        run_row = {
            "frame_id": frame_id,
            "model_name": detector.get("model_name", ""),
            "model_version": detector.get("model_version", ""),
            "delegate": detector.get("delegate", ""),
            "score_threshold": detector.get("score_threshold", ""),
            "max_results": detector.get("max_results", ""),
            "infer_ms": record.get("infer_ms", ""),
            "n_boxes": len(predictions),
            "image_width": video["width"],
            "image_height": video["height"],
            "export_utc": record["captured_utc"],
            "export_source": source_label,
            "notes": f"imported {now_iso()}",
        }
        pred_rows = [
            {
                "frame_id": frame_id,
                "image_file": record["image_file"],
                "pred_id": pred.get("pred_id", f"p{n}"),
                "x_min": pred["x_min"],
                "y_min": pred["y_min"],
                "x_max": pred["x_max"],
                "y_max": pred["y_max"],
                "confidence": pred["confidence"],
                "model_name": detector.get("model_name", ""),
                "model_version": detector.get("model_version", ""),
                "infer_ms": record.get("infer_ms", ""),
                "export_utc": record["captured_utc"],
                "export_source": source_label,
                "notes": "",
            }
            for n, pred in enumerate(predictions, start=1)
        ]

        if not args.dry_run:
            append_row(index_path, FRAMES_INDEX_COLUMNS, index_row)
            append_row(runs_path, RUNS_COLUMNS, run_row)
            for row in pred_rows:
                append_row(preds_path, PREDICTIONS_COLUMNS, row)
        known.add(frame_id)
        imported += 1
        boxes += len(pred_rows)
        print(f"{'would import' if args.dry_run else 'imported'} {frame_id}: "
              f"{len(pred_rows)} predicted box(es), infer {record.get('infer_ms', '-')} ms")

    for message in problems:
        print(f"PROBLEM: {message}", file=sys.stderr)
    verb = "would be imported" if args.dry_run else "imported"
    print(f"\n{imported} frame(s) {verb}, {boxes} predicted box(es), {skipped} already present, "
          f"{len(problems)} problem(s).")
    if imported and not args.dry_run:
        print(f"Next: annotate them. ./detector_annotate.py --list-unannotated")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
