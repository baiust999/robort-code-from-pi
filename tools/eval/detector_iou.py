#!/usr/bin/env python3
"""Object-level detection scoring for E18: IoU matching and its metrics.

Pure functions, stdlib only, no file or network access, so the matching rule
and every metric in Section 5.9 can be unit tested on hand-built boxes
(tools/eval/tests/test_detector_iou.py).

Why this module exists
----------------------
The first version of E18 scored a frame as "detected" when the detector
returned at least one person box anywhere in it. That is a frame-level
classification, not a detection measurement: a box drawn around a chair in a
frame that also contains a person counted as a success, and a box in roughly
the right place counted the same as a box on the person. This module scores
boxes against boxes instead.

Coordinate convention
---------------------
All boxes are in the evaluated image's own pixel coordinates, x to the right,
y downward, origin at the top-left pixel, given as (x_min, y_min, x_max, y_max)
with x_max > x_min and y_max > y_min. The dashboard's detector reports
(originX, originY, width, height) in video pixels
(dashboard/src/hooks/usePersonDetection.ts), which `box_from_xywh` converts.

IoU
---
For boxes A and B,

    IoU(A, B) = area(A intersect B) / area(A union B)
              = inter / (area(A) + area(B) - inter)

with inter = max(0, min(x_max) - max(x_min)) * max(0, min(y_max) - max(y_min)).
IoU is 0 for disjoint boxes and 1 for identical boxes. The primary threshold
for E18 is 0.50 (`PRIMARY_IOU`).

Matching
--------
`match_frame` implements one-to-one greedy matching, the PASCAL VOC / COCO
rule, made fully deterministic:

1. Predictions are ordered by descending confidence. Ties are broken by the
   prediction's `key` (its pred_id, then its row order), ascending, so the
   result never depends on dict or file ordering.
2. Each prediction in that order takes the unmatched ground-truth box with
   the highest IoU, provided that IoU is >= the threshold. Ties on IoU are
   broken by the ground-truth box's `key`, ascending.
3. A matched pair is a true positive (TP). It consumes both boxes: neither can
   match again.
4. A prediction left unmatched is a false positive (FP).
5. A ground-truth box left unmatched is a false negative (FN).

Greedy confidence-ordered matching is not guaranteed to maximise the number of
matches (a maximum-weight bipartite matching could do better in contrived
overlapping cases). It is used because it is the convention the detection
literature reports against, and because the alternative would make these
numbers incomparable with any published figure.
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass, field
from typing import Iterable, Sequence

PRIMARY_IOU = 0.50
# Reported alongside the primary threshold as a sensitivity check only.
SENSITIVITY_IOU = (0.25, 0.50, 0.75)


class BoxError(ValueError):
    """An annotation or prediction whose coordinates cannot be scored."""


@dataclass(frozen=True)
class Box:
    """An axis-aligned box in image pixels, (x_min, y_min) to (x_max, y_max)."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float
    # Sort key for deterministic tie-breaking; never affects geometry.
    key: tuple = ()
    confidence: float | None = None
    source: str = ""

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def area(self) -> float:
        return self.width * self.height


def validate_box(
    x_min: float,
    y_min: float,
    x_max: float,
    y_max: float,
    *,
    where: str = "box",
    image_width: float | None = None,
    image_height: float | None = None,
) -> None:
    """Raise BoxError unless the four numbers describe a usable box.

    Rejects non-finite values, zero or negative width or height (x_max must be
    strictly greater than x_min), negative coordinates, and - when the image
    size is known - boxes that leave the image. A degenerate box has zero area,
    so every IoU against it would be 0 or undefined; silently scoring one would
    turn a typing mistake into a false negative.
    """
    values = {"x_min": x_min, "y_min": y_min, "x_max": x_max, "y_max": y_max}
    for name, value in values.items():
        if value is None or not math.isfinite(float(value)):
            raise BoxError(f"{where}: {name} is not a finite number ({value!r})")
        if float(value) < 0:
            raise BoxError(f"{where}: {name} is negative ({value})")
    if float(x_max) <= float(x_min):
        raise BoxError(f"{where}: x_max ({x_max}) must be greater than x_min ({x_min})")
    if float(y_max) <= float(y_min):
        raise BoxError(f"{where}: y_max ({y_max}) must be greater than y_min ({y_min})")
    if image_width is not None and float(x_max) > float(image_width):
        raise BoxError(f"{where}: x_max ({x_max}) is outside the image width ({image_width})")
    if image_height is not None and float(y_max) > float(image_height):
        raise BoxError(f"{where}: y_max ({y_max}) is outside the image height ({image_height})")


def make_box(
    x_min: float,
    y_min: float,
    x_max: float,
    y_max: float,
    *,
    where: str = "box",
    key: tuple = (),
    confidence: float | None = None,
    source: str = "",
    image_width: float | None = None,
    image_height: float | None = None,
) -> Box:
    """A validated Box. The only constructor the loaders use."""
    validate_box(
        x_min, y_min, x_max, y_max,
        where=where, image_width=image_width, image_height=image_height,
    )
    if confidence is not None:
        conf = float(confidence)
        if not math.isfinite(conf) or not 0.0 <= conf <= 1.0:
            raise BoxError(f"{where}: confidence must be in [0, 1] ({confidence!r})")
        confidence = conf
    return Box(float(x_min), float(y_min), float(x_max), float(y_max), key, confidence, source)


def box_from_xywh(
    x: float, y: float, width: float, height: float, **kwargs
) -> Box:
    """A validated Box from the detector's (originX, originY, width, height)."""
    return make_box(x, y, float(x) + float(width), float(y) + float(height), **kwargs)


def iou(a: Box, b: Box) -> float:
    """Intersection over union of two boxes; 0 when they do not overlap."""
    inter_w = min(a.x_max, b.x_max) - max(a.x_min, b.x_min)
    inter_h = min(a.y_max, b.y_max) - max(a.y_min, b.y_min)
    if inter_w <= 0 or inter_h <= 0:
        return 0.0
    inter = inter_w * inter_h
    union = a.area + b.area - inter
    if union <= 0:
        return 0.0
    return inter / union


@dataclass
class Match:
    pred_index: int
    gt_index: int
    iou: float


@dataclass
class FrameResult:
    """One frame's matching outcome at one IoU threshold."""

    matches: list[Match] = field(default_factory=list)
    unmatched_preds: list[int] = field(default_factory=list)
    unmatched_gts: list[int] = field(default_factory=list)

    @property
    def tp(self) -> int:
        return len(self.matches)

    @property
    def fp(self) -> int:
        return len(self.unmatched_preds)

    @property
    def fn(self) -> int:
        return len(self.unmatched_gts)


def confidence_order(preds: Sequence[Box]) -> list[int]:
    """Prediction indices, highest confidence first, ties by key then index.

    A prediction with no confidence sorts last (treated as -inf), which only
    happens for hand-entered rows that omitted the score.
    """
    return sorted(
        range(len(preds)),
        key=lambda i: (
            -(preds[i].confidence if preds[i].confidence is not None else -math.inf),
            preds[i].key,
            i,
        ),
    )


def match_frame(
    preds: Sequence[Box], gts: Sequence[Box], threshold: float = PRIMARY_IOU
) -> FrameResult:
    """One-to-one greedy IoU matching for a single frame; see module docstring."""
    taken: set[int] = set()
    result = FrameResult()
    for pred_index in confidence_order(preds):
        best_gt: int | None = None
        best_iou = 0.0
        best_key: tuple = ()
        for gt_index, gt in enumerate(gts):
            if gt_index in taken:
                continue
            value = iou(preds[pred_index], gt)
            if value < threshold:
                continue
            gt_key = (gt.key, gt_index)
            if best_gt is None or value > best_iou or (value == best_iou and gt_key < best_key):
                best_gt, best_iou, best_key = gt_index, value, gt_key
        if best_gt is None:
            result.unmatched_preds.append(pred_index)
        else:
            taken.add(best_gt)
            result.matches.append(Match(pred_index, best_gt, best_iou))
    result.unmatched_gts = [i for i in range(len(gts)) if i not in taken]
    # Stable output order, independent of the confidence walk above.
    result.matches.sort(key=lambda m: (m.gt_index, m.pred_index))
    result.unmatched_preds.sort()
    return result


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval; stays informative when k is 0 or n."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def f1_score(precision: float, recall: float) -> float:
    """Harmonic mean; 0.0 when both are 0 (no predictions and no ground truth)."""
    if not math.isfinite(precision) or not math.isfinite(recall):
        return float("nan")
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


@dataclass
class Metrics:
    """TP / FP / FN and the rates derived from them, with intervals."""

    tp: int
    fp: int
    fn: int
    ious: list[float] = field(default_factory=list)

    @property
    def n_pred(self) -> int:
        return self.tp + self.fp

    @property
    def n_gt(self) -> int:
        return self.tp + self.fn

    @property
    def precision(self) -> float:
        return self.tp / self.n_pred if self.n_pred else float("nan")

    @property
    def recall(self) -> float:
        return self.tp / self.n_gt if self.n_gt else float("nan")

    @property
    def f1(self) -> float:
        return f1_score(self.precision, self.recall)

    @property
    def precision_ci(self) -> tuple[float, float]:
        return wilson(self.tp, self.n_pred)

    @property
    def recall_ci(self) -> tuple[float, float]:
        return wilson(self.tp, self.n_gt)

    def iou_stats(self) -> dict[str, float] | None:
        """Mean / median / min / max IoU over matched pairs only."""
        if not self.ious:
            return None
        return {
            "n": len(self.ious),
            "mean": st.fmean(self.ious),
            "median": st.median(self.ious),
            "min": min(self.ious),
            "max": max(self.ious),
            "sd": st.stdev(self.ious) if len(self.ious) > 1 else float("nan"),
        }


def aggregate(results: Iterable[FrameResult]) -> Metrics:
    """Sum per-frame outcomes into one Metrics.

    Summing TP, FP and FN over frames and dividing once (micro-averaging) is
    the convention for detection: every box carries the same weight, so a frame
    with three people is not given the same weight as a frame with one.
    """
    tp = fp = fn = 0
    ious: list[float] = []
    for result in results:
        tp += result.tp
        fp += result.fp
        fn += result.fn
        ious.extend(m.iou for m in result.matches)
    return Metrics(tp, fp, fn, ious)


def average_precision(
    frames: Sequence[tuple[Sequence[Box], Sequence[Box]]], threshold: float = PRIMARY_IOU
) -> tuple[float, int]:
    """All-point-interpolated AP at one IoU threshold, and the ground-truth count.

    Single class (person), so this is AP, never mAP: there is no second class
    to average over, and no average over IoU thresholds is taken. The
    predictions available are only those the shipped detector emitted above its
    own 0.4 score threshold, so the recall axis is truncated at whatever recall
    that threshold reaches; the value is therefore a lower bound on the AP the
    model would score with an unthresholded output, and is not comparable with
    a COCO mAP. Returns (nan, 0) when there is no ground truth.

    The scored pairs come from one pass over all predictions ranked by
    confidence across the whole set, each matched within its own frame against
    the ground-truth boxes not yet taken in that frame, which is the standard
    construction.
    """
    ranked: list[tuple[float, tuple, int, int]] = []  # (-conf, key, frame, pred index)
    n_gt = 0
    for frame_index, (preds, gts) in enumerate(frames):
        n_gt += len(gts)
        for pred_index in range(len(preds)):
            conf = preds[pred_index].confidence
            ranked.append((
                -(conf if conf is not None else -math.inf),
                preds[pred_index].key,
                frame_index,
                pred_index,
            ))
    if n_gt == 0:
        return float("nan"), 0
    ranked.sort()
    taken: dict[int, set[int]] = {}
    tp_cum = fp_cum = 0
    points: list[tuple[float, float]] = []  # (recall, precision)
    for _, _, frame_index, pred_index in ranked:
        preds, gts = frames[frame_index]
        used = taken.setdefault(frame_index, set())
        best_gt, best_iou, best_key = None, 0.0, ()
        for gt_index, gt in enumerate(gts):
            if gt_index in used:
                continue
            value = iou(preds[pred_index], gt)
            if value < threshold:
                continue
            gt_key = (gt.key, gt_index)
            if best_gt is None or value > best_iou or (value == best_iou and gt_key < best_key):
                best_gt, best_iou, best_key = gt_index, value, gt_key
        if best_gt is None:
            fp_cum += 1
        else:
            used.add(best_gt)
            tp_cum += 1
        points.append((tp_cum / n_gt, tp_cum / (tp_cum + fp_cum)))
    if not points:
        return 0.0, n_gt
    # All-point interpolation: precision is replaced by the maximum precision
    # at any recall at least as high, then the area under the step curve.
    best_right = 0.0
    envelope: list[tuple[float, float]] = []
    for recall, precision in reversed(points):
        best_right = max(best_right, precision)
        envelope.append((recall, best_right))
    envelope.reverse()
    area = 0.0
    previous_recall = 0.0
    for recall, precision in envelope:
        area += (recall - previous_recall) * precision
        previous_recall = recall
    return area, n_gt
