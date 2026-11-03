#!/usr/bin/env python3
"""E18: score the dashboard's person detector against a labelled frame set.

The dashboard runs MediaPipe EfficientDet-Lite0 on the operator's computer at
a score threshold of 0.4 (Section 3.11 of the paper). This script does not run
the detector: it scores what the detector produced against hand-entered
labels, so the numbers in Section 5.9 are reproducible from two CSV files.

Inputs, both under results/:

  detector_frames.csv   one row per captured frame
      frame            frame identifier (file name of the captured still)
      posture          upright / lying-down / none      ("none" = person-free frame)
      occlusion        unoccluded / partly-covered / -
      light            room / low
      distance_band    near / far
      person_present   1/0, the ground truth label
      detected         1/0, whether the detector returned at least one person box
      best_score       the highest person score on that frame (blank if none)
      infer_ms         the inference time the dashboard measured for that frame
      notes

  detector_banner.csv   one row per continuous person-free video segment
      segment          label
      person_free_s    length of the segment in seconds
      banner_raises    times the "possible person" banner was raised
      notes

A frame counts as detected when the detector returned at least one person box,
which is what raises the operator's box overlay and, after three consecutive
frames, the banner (Section 3.11). Recall, precision and F1 carry 95% Wilson
intervals; no hypothesis test is reported, in line with Section 5.

    ./detector_eval.py                         # print markdown
    ./detector_eval.py --out results/detector_eval.md
"""

from __future__ import annotations

import argparse
import math
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS_DIR, read_rows  # noqa: E402

STRATA = ("posture", "occlusion", "light", "distance_band")

out_lines: list[str] = []


def emit(line: str = "") -> None:
    out_lines.append(line)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval; stays informative when k is 0 or n."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def rate(k: int, n: int) -> str:
    if n == 0:
        return "-"
    lo, hi = wilson(k, n)
    return f"{k / n:.2f} ({lo:.2f} to {hi:.2f})"


def truthy(value: str) -> bool:
    return str(value).strip() in ("1", "true", "True", "yes")


def scores(rows: list[dict], key: str) -> list[float]:
    out = []
    for r in rows:
        v = str(r.get(key, "")).strip()
        if v:
            try:
                out.append(float(v))
            except ValueError:
                pass
    return out


def frames_block(rows: list[dict]) -> None:
    present = [r for r in rows if truthy(r["person_present"])]
    absent = [r for r in rows if not truthy(r["person_present"])]
    emit("## E18 frame-level detection by stratum (detector_frames.csv)")
    emit()
    emit(f"{len(rows)} frames: {len(present)} with a person, {len(absent)} person-free.")
    emit()
    emit("| posture | occlusion | light | distance | frames | detected | recall (95% CI) | median best score |")
    emit("|---|---|---|---|---|---|---|---|")
    cells: dict[tuple, list[dict]] = {}
    for r in present:
        cells.setdefault(tuple(r[k] for k in STRATA), []).append(r)
    for key in sorted(cells):
        group = cells[key]
        hit = [r for r in group if truthy(r["detected"])]
        sc = scores(hit, "best_score")
        emit("| " + " | ".join(key) + f" | {len(group)} | {len(hit)} | {rate(len(hit), len(group))} | "
             + (f"{st.median(sc):.2f}" if sc else "-") + " |")
    tp = [r for r in present if truthy(r["detected"])]
    fp = [r for r in absent if truthy(r["detected"])]
    emit(f"| **all with a person** | | | | **{len(present)}** | **{len(tp)}** | "
         f"**{rate(len(tp), len(present))}** | |")
    emit(f"| person-free | | | | {len(absent)} | {len(fp)} | - | |")
    emit()
    prec_k, prec_n = len(tp), len(tp) + len(fp)
    recall = len(tp) / len(present) if present else float("nan")
    precision = prec_k / prec_n if prec_n else float("nan")
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else float("nan")
    emit(f"Pooled recall {rate(len(tp), len(present))}; pooled precision {rate(prec_k, prec_n)}; "
         f"F1 {f1:.2f}.")
    emit()
    hit_sc, miss_sc = scores(tp, "best_score"), scores(fp, "best_score")
    if hit_sc:
        emit(f"Best score on true detections: median {st.median(hit_sc):.2f}, "
             f"min {min(hit_sc):.2f}, max {max(hit_sc):.2f} (n {len(hit_sc)}).")
    if miss_sc:
        emit(f"Best score on false detections: median {st.median(miss_sc):.2f}, "
             f"min {min(miss_sc):.2f}, max {max(miss_sc):.2f} (n {len(miss_sc)}).")
    inf = scores(rows, "infer_ms")
    if inf:
        inf.sort()
        p95 = inf[min(len(inf) - 1, int(round(0.95 * (len(inf) - 1))))]
        over = sum(1 for v in inf if v > 150)
        emit(f"Inference time: median {st.median(inf):.0f} ms, p95 {p95:.0f} ms, "
             f"n {len(inf)}; {over} frame{'' if over == 1 else 's'} above the dashboard's "
             f"150 ms auto-off level (it switches off on the mean of five, Section 3.11).")
    emit()


def banner_block(rows: list[dict]) -> None:
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--out", type=Path, help="write markdown here instead of stdout")
    args = ap.parse_args()

    emit("# E18 person-detector evaluation")
    emit()
    emit("Generated by tools/eval/detector_eval.py from the labelled frame set. "
         "Derived figures only; no input file is modified.")
    emit()
    any_input = False
    frames = args.results_dir / "detector_frames.csv"
    banner = args.results_dir / "detector_banner.csv"
    if frames.exists():
        rows = read_rows(frames)
        if rows:
            frames_block(rows)
            any_input = True
    else:
        emit(f"(skipped: {frames.name} not present yet)")
        emit()
    if banner.exists():
        rows = read_rows(banner)
        if rows:
            banner_block(rows)
            any_input = True
    else:
        emit(f"(skipped: {banner.name} not present yet)")
        emit()
    if not any_input:
        emit("E18 is [PENDING MEASUREMENT]: no labelled frames have been captured. "
             "The protocol and the pass criterion are in Section 5.9 and Table 4.2.")
        emit()
    text = "\n".join(out_lines) + "\n"
    if args.out:
        args.out.write_text(text)
        print(f"written to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
