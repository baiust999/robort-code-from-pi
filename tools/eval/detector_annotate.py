#!/usr/bin/env python3
"""E18: enter hand-drawn ground-truth person boxes for frames in the test set.

Ground truth is a human judgement, so it is typed in here rather than derived
from anything. One row per person visible in the frame, in the frame's own
pixel coordinates, (x_min, y_min) at the top-left corner of the box and
(x_max, y_max) at the bottom-right, read off any image viewer that shows pixel
coordinates (GIMP's pointer window, `feh`'s title bar, a browser's developer
tools on the opened JPEG).

    # one person in the frame
    ./detector_annotate.py box frame_id=e18-20261103T184500123Z box_id=b1 \
        x_min=412 y_min=96 x_max=505 y_max=348 annotator_id=AB

    # two people: one row each
    ./detector_annotate.py box frame_id=F12 box_id=b1 x_min=120 y_min=80  x_max=210 y_max=330 annotator_id=AB
    ./detector_annotate.py box frame_id=F12 box_id=b2 x_min=460 y_min=102 x_max=548 y_max=352 annotator_id=AB

    # nobody in the frame: still a record, so the frame counts as annotated
    ./detector_annotate.py empty frame_id=F80 annotator_id=AB notes="chairs only"

    ./detector_annotate.py --list-unannotated      # what is still to do
    ./detector_annotate.py --show frame_id=F12     # what has been entered

A frame with no row here is an unannotated frame, not a person-free frame, and
detector_eval.py excludes it from every metric. That distinction is the point
of the `empty` command: it records that a human looked and saw nobody.

The frame must already be in results/detector_frames_index.csv, which
detector_import.py writes when the dashboard's export is imported. This script
appends to results/detector_groundtruth.csv and changes nothing else. To
correct a box, append a new row with a new box_id and say in its notes which
box it replaces; the superseded row stays on disk, and the correction is
visible.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402
from detector_data import (  # noqa: E402
    EMPTY_BOX_ID,
    FRAMES_INDEX_FILE,
    GROUNDTRUTH_COLUMNS,
    GROUNDTRUTH_FILE,
    load_dataset,
)
from detector_iou import BoxError, validate_box  # noqa: E402

COORDS = ("x_min", "y_min", "x_max", "y_max")


def parse_pairs(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"expected key=value, got {item!r}")
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", choices=("box", "empty"),
                    help="`box` adds one person box; `empty` records a person-free frame")
    ap.add_argument("pairs", nargs="*", help="key=value fields")
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--fields", action="store_true", help="list the fields and exit")
    ap.add_argument("--list-unannotated", action="store_true",
                    help="frames in the index with no annotation record yet")
    ap.add_argument("--show", nargs="*", metavar="frame_id=ID",
                    help="print what has been annotated, for one frame or all")
    args = ap.parse_args()

    if args.fields:
        print("box:   " + " ".join(f"{c}=" for c in
                                   ("frame_id", "box_id", *COORDS, "annotator_id", "notes")))
        print("empty: " + " ".join(f"{c}=" for c in ("frame_id", "annotator_id", "notes")))
        print(f"\nCoordinates are pixels in the frame's own space; box_id "
              f"{EMPTY_BOX_ID!r} is reserved for `empty`.")
        return 0

    data = load_dataset(args.results_dir)
    for message in data.errors:
        print(f"EXISTING DATA ERROR: {message}", file=sys.stderr)

    if args.list_unannotated:
        todo = [f for f in data.frames.values() if not f.annotated]
        if not data.frames:
            print(f"{FRAMES_INDEX_FILE} holds no frames yet: import a dashboard export "
                  "first (detector_import.py). [PENDING MEASUREMENT: E18 test set]")
            return 0
        if not todo:
            print(f"all {len(data.frames)} frame(s) in the index are annotated")
            return 0
        print(f"{len(todo)} of {len(data.frames)} frame(s) are not annotated yet:")
        for frame in sorted(todo, key=lambda f: f.frame_id):
            size = (f"{frame.image_width:g}x{frame.image_height:g}"
                    if frame.image_width and frame.image_height else "size unknown")
            print(f"  {frame.frame_id}  {frame.image_file}  {size}  "
                  f"[{', '.join(v for v in frame.condition_key if v)}]")
        return 0

    if args.show is not None:
        wanted = parse_pairs(args.show).get("frame_id")
        frames = [f for f in data.frames.values() if wanted is None or f.frame_id == wanted]
        if not frames:
            print(f"no such frame in {FRAMES_INDEX_FILE}: {wanted!r}", file=sys.stderr)
            return 2
        for frame in sorted(frames, key=lambda f: f.frame_id):
            state = "person-free (annotated)" if frame.person_free else (
                f"{len(frame.gt)} box(es)" if frame.annotated else "NOT ANNOTATED")
            print(f"{frame.frame_id}: {state}; detector "
                  f"{'ran' if frame.ran else 'NOT RUN'}, {len(frame.preds)} prediction(s)"
                  + (f"; annotators {', '.join(sorted(frame.annotators))}" if frame.annotators else ""))
            for box in frame.gt:
                print(f"    {box.source}: ({box.x_min:g}, {box.y_min:g}) to "
                      f"({box.x_max:g}, {box.y_max:g})")
        return 0

    if args.command is None:
        ap.error("give a command (box or empty), or --list-unannotated / --show / --fields")

    row = parse_pairs(args.pairs)
    frame_id = row.get("frame_id", "")
    if not frame_id:
        print("frame_id= is required", file=sys.stderr)
        return 2
    frame = data.frames.get(frame_id)
    if frame is None:
        print(f"frame_id {frame_id!r} is not in {FRAMES_INDEX_FILE}. Import the dashboard's "
              f"export first (detector_import.py); a frame is never created here.",
              file=sys.stderr)
        return 2
    annotator = row.get("annotator_id", "")
    if not annotator:
        print("annotator_id= is required: every annotation names who drew it", file=sys.stderr)
        return 2

    existing = {box.key[1] for box in frame.gt}
    if args.command == "empty":
        if frame.gt:
            print(f"{frame_id} already has {len(frame.gt)} annotated box(es); `empty` would "
                  "contradict them. Nothing written.", file=sys.stderr)
            return 2
        if frame.annotated:
            print(f"{frame_id} is already recorded as person-free. Nothing written.")
            return 0
        out = {
            "frame_id": frame_id,
            "image_file": frame.image_file,
            "box_id": EMPTY_BOX_ID,
            "annotator_id": annotator,
            "annotated_utc": now_iso(),
            "notes": row.get("notes", ""),
        }
    else:
        if frame.person_free:
            print(f"{frame_id} is recorded as person-free ({EMPTY_BOX_ID} row); a box would "
                  "contradict that. Fix the sheet at the source. Nothing written.",
                  file=sys.stderr)
            return 2
        box_id = row.get("box_id", "")
        if not box_id:
            box_id = f"b{len(frame.gt) + 1}"
        if box_id == EMPTY_BOX_ID:
            print(f"box_id {EMPTY_BOX_ID!r} is reserved for the `empty` command",
                  file=sys.stderr)
            return 2
        if box_id in existing:
            print(f"{frame_id} already has a box {box_id!r}; use a new box_id", file=sys.stderr)
            return 2
        missing = [c for c in COORDS if not row.get(c)]
        if missing:
            print(f"missing coordinate(s): {', '.join(missing)}", file=sys.stderr)
            return 2
        try:
            values = [float(row[c]) for c in COORDS]
            validate_box(*values, where=f"{frame_id}/{box_id}",
                         image_width=frame.image_width, image_height=frame.image_height)
        except ValueError as err:
            print(f"rejected: {err}", file=sys.stderr)
            return 2
        except BoxError as err:
            print(f"rejected: {err}", file=sys.stderr)
            return 2
        out = {
            "frame_id": frame_id,
            "image_file": frame.image_file,
            "box_id": box_id,
            **{c: row[c] for c in COORDS},
            "annotator_id": annotator,
            "annotated_utc": now_iso(),
            "notes": row.get("notes", ""),
        }

    append_row(args.results_dir / GROUNDTRUTH_FILE, GROUNDTRUTH_COLUMNS, out)
    what = "person-free record" if args.command == "empty" else f"box {out['box_id']}"
    print(f"appended {what} for {frame_id} to {GROUNDTRUTH_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
