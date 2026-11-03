"""E18 object-level scoring: IoU, the matching rule, and the metrics from it.

Scope: tools/eval/detector_iou.py only. Pure in-memory boxes, no file, socket
or hardware access, and no measured data is read, so these tests verify the
arithmetic of the evaluation and nothing about the robot.

Every expected number below is worked out by hand in the test that uses it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from detector_iou import (  # noqa: E402
    PRIMARY_IOU,
    Box,
    BoxError,
    Metrics,
    aggregate,
    average_precision,
    box_from_xywh,
    confidence_order,
    f1_score,
    iou,
    make_box,
    match_frame,
    validate_box,
    wilson,
)


def gt(x_min, y_min, x_max, y_max, box_id="b1"):
    return make_box(x_min, y_min, x_max, y_max, key=("gt", box_id))


def pred(x_min, y_min, x_max, y_max, confidence, pred_id="p1"):
    return make_box(x_min, y_min, x_max, y_max, key=("pred", pred_id), confidence=confidence)


# --- IoU itself ------------------------------------------------------------


def test_identical_boxes_have_iou_one():
    box = gt(10, 10, 110, 210)
    assert iou(box, box) == pytest.approx(1.0)


def test_disjoint_boxes_have_iou_zero():
    assert iou(gt(0, 0, 10, 10), gt(100, 100, 110, 110)) == 0.0


def test_touching_edges_do_not_overlap():
    """Boxes that share only an edge have zero intersection area."""
    assert iou(gt(0, 0, 10, 10), gt(10, 0, 20, 10)) == 0.0


def test_iou_is_computed_by_hand():
    """Two 10x10 boxes offset by 5 in x: inter 5x10=50, union 100+100-50=150."""
    assert iou(gt(0, 0, 10, 10), gt(5, 0, 15, 10)) == pytest.approx(50 / 150)


def test_contained_box_iou_is_area_ratio():
    """A 10x10 box inside a 20x20 box: inter 100, union 400, IoU 0.25."""
    assert iou(gt(0, 0, 20, 20), gt(5, 5, 15, 15)) == pytest.approx(0.25)


def test_iou_is_symmetric():
    a, b = gt(0, 0, 10, 10), gt(3, 4, 14, 15)
    assert iou(a, b) == pytest.approx(iou(b, a))


def test_box_from_xywh_matches_the_detector_convention():
    """The dashboard reports originX, originY, width, height."""
    box = box_from_xywh(10, 20, 30, 40)
    assert (box.x_min, box.y_min, box.x_max, box.y_max) == (10, 20, 40, 60)
    assert box.area == 30 * 40


# --- invalid coordinates ---------------------------------------------------


@pytest.mark.parametrize(
    "coords",
    [
        (10, 10, 10, 20),      # zero width
        (10, 10, 20, 10),      # zero height
        (20, 10, 10, 20),      # x_max before x_min
        (10, 20, 20, 10),      # y_max before y_min
        (-1, 10, 20, 20),      # negative coordinate
        (10, 10, float("nan"), 20),
        (10, 10, float("inf"), 20),
    ],
)
def test_invalid_coordinates_are_rejected(coords):
    with pytest.raises(BoxError):
        validate_box(*coords)


def test_box_outside_the_image_is_rejected():
    with pytest.raises(BoxError):
        make_box(10, 10, 700, 100, image_width=640, image_height=480)
    with pytest.raises(BoxError):
        make_box(10, 10, 100, 500, image_width=640, image_height=480)


def test_box_on_the_image_edge_is_accepted():
    box = make_box(0, 0, 640, 480, image_width=640, image_height=480)
    assert box.area == 640 * 480


@pytest.mark.parametrize("confidence", [-0.1, 1.1, float("nan")])
def test_confidence_outside_zero_to_one_is_rejected(confidence):
    with pytest.raises(BoxError):
        make_box(0, 0, 10, 10, confidence=confidence)


# --- matching: the cases the old binary scoring could not tell apart -------


def test_perfect_match_is_one_true_positive():
    result = match_frame([pred(10, 10, 110, 210, 0.9)], [gt(10, 10, 110, 210)])
    assert (result.tp, result.fp, result.fn) == (1, 0, 0)
    assert result.matches[0].iou == pytest.approx(1.0)


def test_good_but_imperfect_overlap_still_matches():
    """90x200 prediction over a 100x200 ground truth: IoU 0.9, above 0.50."""
    result = match_frame([pred(10, 10, 100, 210, 0.8)], [gt(10, 10, 110, 210)])
    assert (result.tp, result.fp, result.fn) == (1, 0, 0)
    assert result.matches[0].iou == pytest.approx(0.9)


def test_partial_overlap_below_threshold_is_a_miss_and_a_false_alarm():
    """Offset by 5 on a 10-wide box: IoU 1/3, under 0.50, so no match at all.

    This is the case the frame-level scoring got wrong: the detector returned a
    box, the frame held a person, and it counted as a correct detection.
    """
    result = match_frame([pred(5, 0, 15, 10, 0.95)], [gt(0, 0, 10, 10)])
    assert (result.tp, result.fp, result.fn) == (0, 1, 1)
    assert iou(pred(5, 0, 15, 10, 0.95), gt(0, 0, 10, 10)) == pytest.approx(1 / 3)


def test_threshold_boundary_is_inclusive():
    """IoU exactly 0.50 counts as a match; just under it does not."""
    # 100x100 ground truth, prediction shifted so inter/union == 1/2 exactly:
    # inter = w*100, union = 20000 - w*100 -> w = 200/3 for IoU 0.5.
    shift = 100 - 200 / 3
    exact = match_frame([pred(shift, 0, shift + 100, 100, 0.9)], [gt(0, 0, 100, 100)])
    assert exact.tp == 1
    assert exact.matches[0].iou == pytest.approx(0.5)
    short = match_frame([pred(shift + 1, 0, shift + 101, 100, 0.9)], [gt(0, 0, 100, 100)])
    assert (short.tp, short.fp, short.fn) == (0, 1, 1)


def test_wrong_prediction_elsewhere_in_the_frame_is_a_false_positive():
    """A box on the furniture, in a frame that does hold a person.

    Frame-level scoring called this frame "detected" and counted the box
    towards precision. Here it is one FP and one FN.
    """
    result = match_frame([pred(400, 300, 500, 400, 0.6)], [gt(0, 0, 100, 200)])
    assert (result.tp, result.fp, result.fn) == (0, 1, 1)


def test_missing_prediction_is_a_false_negative_only():
    result = match_frame([], [gt(0, 0, 100, 200)])
    assert (result.tp, result.fp, result.fn) == (0, 0, 1)
    assert result.unmatched_gts == [0]


def test_empty_frame_with_a_false_detection_is_a_false_positive_only():
    result = match_frame([pred(0, 0, 50, 90, 0.52)], [])
    assert (result.tp, result.fp, result.fn) == (0, 1, 0)


def test_empty_frame_with_no_detection_contributes_nothing():
    result = match_frame([], [])
    assert (result.tp, result.fp, result.fn) == (0, 0, 0)


def test_two_people_both_found():
    gts = [gt(0, 0, 100, 200, "b1"), gt(300, 0, 400, 200, "b2")]
    preds = [pred(302, 2, 402, 202, 0.7, "p1"), pred(1, 1, 101, 201, 0.8, "p2")]
    result = match_frame(preds, gts)
    assert (result.tp, result.fp, result.fn) == (2, 0, 0)
    # Each ground-truth box took the prediction that lies on it, not the first one.
    assert sorted((m.gt_index, m.pred_index) for m in result.matches) == [(0, 1), (1, 0)]


def test_two_people_one_found():
    gts = [gt(0, 0, 100, 200, "b1"), gt(300, 0, 400, 200, "b2")]
    result = match_frame([pred(0, 0, 100, 200, 0.9)], gts)
    assert (result.tp, result.fp, result.fn) == (1, 0, 1)


def test_two_predictions_on_one_person_leave_one_false_positive():
    """Duplicate boxes are not free: one matches, the other is an FP."""
    gts = [gt(0, 0, 100, 200)]
    preds = [pred(0, 0, 100, 200, 0.9, "p1"), pred(2, 2, 102, 202, 0.8, "p2")]
    result = match_frame(preds, gts)
    assert (result.tp, result.fp, result.fn) == (1, 1, 0)
    # The higher-confidence box is the one kept.
    assert result.matches[0].pred_index == 0


def test_one_prediction_cannot_cover_two_people():
    """A single wide box over two adjacent people: at most one TP, one FN."""
    gts = [gt(0, 0, 100, 200, "b1"), gt(100, 0, 200, 200, "b2")]
    result = match_frame([pred(0, 0, 200, 200, 0.9)], gts, threshold=0.4)
    assert (result.tp, result.fp, result.fn) == (1, 0, 1)
    assert result.matches[0].iou == pytest.approx(0.5)


def test_confidence_order_decides_who_matches_first():
    """Both predictions clear the threshold on the same box; the stronger wins."""
    gts = [gt(0, 0, 100, 100)]
    preds = [pred(10, 10, 110, 110, 0.5, "p1"), pred(0, 0, 100, 100, 0.99, "p2")]
    result = match_frame(preds, gts)
    assert result.tp == 1
    assert result.matches[0].pred_index == 1
    assert result.unmatched_preds == [0]


def test_confidence_order_is_descending_with_a_deterministic_tie_break():
    preds = [
        pred(0, 0, 10, 10, 0.5, "p3"),
        pred(0, 0, 10, 10, 0.9, "p2"),
        pred(0, 0, 10, 10, 0.5, "p1"),
    ]
    # 0.9 first, then the two 0.5s by key: ("pred","p1") before ("pred","p3").
    assert confidence_order(preds) == [1, 2, 0]


def test_prediction_without_a_confidence_sorts_last():
    preds = [make_box(0, 0, 10, 10, key=("pred", "p1")), pred(0, 0, 10, 10, 0.1, "p2")]
    assert confidence_order(preds) == [1, 0]


def test_a_higher_iou_box_wins_over_a_more_confident_one_per_prediction():
    """Each prediction takes its own best ground-truth box, in confidence order."""
    gts = [gt(0, 0, 100, 100, "b1"), gt(50, 0, 150, 100, "b2")]
    # p1 (0.9) overlaps b2 best; p2 (0.8) then has to take b1.
    preds = [pred(55, 0, 155, 100, 0.9, "p1"), pred(0, 0, 100, 100, 0.8, "p2")]
    result = match_frame(preds, gts)
    assert (result.tp, result.fp, result.fn) == (2, 0, 0)
    assert sorted((m.gt_index, m.pred_index) for m in result.matches) == [(0, 1), (1, 0)]


def test_matching_is_order_independent():
    gts = [gt(0, 0, 100, 200, "b1"), gt(300, 0, 400, 200, "b2")]
    preds = [pred(1, 1, 101, 201, 0.8, "p1"), pred(301, 1, 401, 201, 0.7, "p2")]
    forward = match_frame(preds, gts)
    reversed_ = match_frame(list(reversed(preds)), list(reversed(gts)))
    assert (forward.tp, forward.fp, forward.fn) == (reversed_.tp, reversed_.fp, reversed_.fn)


# --- metrics ---------------------------------------------------------------


def test_metrics_arithmetic_by_hand():
    m = Metrics(tp=8, fp=2, fn=4)
    assert m.n_pred == 10 and m.n_gt == 12
    assert m.precision == pytest.approx(0.8)
    assert m.recall == pytest.approx(8 / 12)
    # F1 = 2 * 0.8 * 0.6667 / (0.8 + 0.6667)
    assert m.f1 == pytest.approx(2 * 0.8 * (8 / 12) / (0.8 + 8 / 12))


def test_perfect_and_empty_metrics():
    perfect = Metrics(tp=5, fp=0, fn=0)
    assert (perfect.precision, perfect.recall, perfect.f1) == (1.0, 1.0, 1.0)
    nothing = Metrics(tp=0, fp=0, fn=0)
    assert math.isnan(nothing.precision) and math.isnan(nothing.recall)


def test_f1_is_zero_when_precision_and_recall_are_zero():
    assert f1_score(0.0, 0.0) == 0.0
    assert math.isnan(f1_score(float("nan"), 0.5))


def test_no_predictions_leaves_precision_undefined_not_zero():
    """Zero predictions means precision has no denominator; it is not 0.0."""
    m = Metrics(tp=0, fp=0, fn=7)
    assert math.isnan(m.precision)
    assert m.recall == 0.0


def test_aggregate_sums_frames_and_micro_averages():
    frames = [
        # frame 1: one person, found
        match_frame([pred(0, 0, 100, 200, 0.9)], [gt(0, 0, 100, 200)]),
        # frame 2: two people, one found, one spurious box
        match_frame(
            [pred(0, 0, 100, 200, 0.9, "p1"), pred(500, 400, 600, 470, 0.5, "p2")],
            [gt(0, 0, 100, 200, "b1"), gt(300, 0, 400, 200, "b2")],
        ),
        # frame 3: person-free, one spurious box
        match_frame([pred(0, 0, 50, 90, 0.6)], []),
    ]
    m = aggregate(frames)
    assert (m.tp, m.fp, m.fn) == (2, 2, 1)
    assert m.precision == pytest.approx(0.5)      # 2 / 4 predictions
    assert m.recall == pytest.approx(2 / 3)       # 2 / 3 ground-truth boxes
    assert len(m.ious) == 2


def test_iou_stats_cover_matched_pairs_only():
    frames = [
        match_frame([pred(0, 0, 100, 100, 0.9)], [gt(0, 0, 100, 100)]),       # IoU 1.0
        match_frame([pred(0, 0, 90, 100, 0.9)], [gt(0, 0, 100, 100)]),        # IoU 0.9
        match_frame([pred(400, 0, 500, 100, 0.9)], [gt(0, 0, 100, 100)]),     # no match
    ]
    stats = aggregate(frames).iou_stats()
    assert stats["n"] == 2
    assert stats["mean"] == pytest.approx(0.95)
    assert stats["min"] == pytest.approx(0.9)
    assert stats["max"] == pytest.approx(1.0)


def test_iou_stats_are_none_without_a_match():
    assert Metrics(tp=0, fp=3, fn=2).iou_stats() is None


def test_wilson_interval_brackets_the_point_estimate():
    lo, hi = wilson(8, 10)
    assert 0 < lo < 0.8 < hi < 1
    # k = 0 and k = n stay inside [0, 1] and are not degenerate.
    zero_lo, zero_hi = wilson(0, 10)
    assert zero_lo <= 0 or zero_lo == pytest.approx(0, abs=1e-9)
    assert 0 < zero_hi < 1
    full_lo, full_hi = wilson(10, 10)
    assert 0 < full_lo < 1 and full_hi >= 1 - 1e-9
    assert all(math.isnan(v) for v in wilson(0, 0))


# --- average precision -----------------------------------------------------


def test_average_precision_is_one_when_every_box_is_found_cleanly():
    frames = [
        ([pred(0, 0, 100, 200, 0.9)], [gt(0, 0, 100, 200)]),
        ([pred(0, 0, 100, 200, 0.8)], [gt(0, 0, 100, 200)]),
    ]
    ap, n_gt = average_precision(frames)
    assert n_gt == 2
    assert ap == pytest.approx(1.0)


def test_average_precision_penalises_a_confident_false_positive():
    """The top-ranked prediction is wrong, so precision starts at 0."""
    frames = [
        ([pred(400, 400, 500, 500, 0.99, "p1")], []),
        ([pred(0, 0, 100, 200, 0.5, "p2")], [gt(0, 0, 100, 200)]),
    ]
    ap, n_gt = average_precision(frames)
    # Ranked: FP then TP. At recall 1.0 precision is 1/2, so AP = 0.5.
    assert n_gt == 1
    assert ap == pytest.approx(0.5)


def test_average_precision_is_nan_without_ground_truth():
    ap, n_gt = average_precision([([pred(0, 0, 10, 10, 0.9)], [])])
    assert math.isnan(ap) and n_gt == 0


def test_average_precision_counts_a_duplicate_box_as_a_false_positive():
    frames = [(
        [pred(0, 0, 100, 200, 0.9, "p1"), pred(1, 1, 101, 201, 0.8, "p2")],
        [gt(0, 0, 100, 200)],
    )]
    ap, n_gt = average_precision(frames)
    # Ranked: TP (precision 1.0 at recall 1.0), then FP, which cannot raise the
    # envelope at any recall already reached, so AP stays 1.0.
    assert n_gt == 1
    assert ap == pytest.approx(1.0)


# --- the primary threshold is the documented one ---------------------------


def test_primary_threshold_is_point_five():
    assert PRIMARY_IOU == 0.50


def test_box_is_immutable():
    box = Box(0, 0, 10, 10)
    with pytest.raises(Exception):
        box.x_min = 5  # type: ignore[misc]
