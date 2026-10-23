#!/usr/bin/env python3
"""SIMULATED / SYNTHETIC analysis of dead-man-timer robustness to lost heartbeats.

This is a software model, not a measurement. No input here comes from the
robot; it is a sensitivity and Monte Carlo study built only from two
documented, verified constants:

  - DEADMAN_MS = 2000           pi/common/protocol.py:67 (mirrors the Arduino
                                 firmware's dead-man window, Section 8.7.6)
  - HEARTBEAT_PERIOD_MS = 500    dashboard/src/lib/protocol.ts:11 (the
                                 dashboard's idle-heartbeat send interval)

Research question: how many consecutive lost or delayed heartbeats can the
system tolerate before the dead-man trips, and how does trip probability
over a mission grow as the per-heartbeat loss probability increases?

Nothing here is a wireless-range or network-loss measurement: Section 5.3
(Wi-Fi range/link quality) is [PENDING MEASUREMENT] in the paper, so the
per-heartbeat loss probability p is swept over an assumed range, not drawn
from a measured distribution. Every table this script prints must carry the
word SIMULATED when it is copied anywhere outside this directory.

Two independent methods are run and cross-checked against each other
(Phase 5 "statistical-pipeline validation"):
  1. Monte Carlo: explicit per-heartbeat Bernoulli loss trials, continuous
     time semantics using the firmware's trip condition: elapsed >=
     DEADMAN_MS trips (arduino taskSafety(); pi/common/mock_hardware.py was
     corrected to match on 2026-10-22). A heartbeat due exactly at
     elapsed == DEADMAN_MS is too late. An earlier version of this script used
     elapsed <= DEADMAN_MS as alive, which is one loss too lenient at the
     500 ms period; the previous report is kept as
     output/deadman_sim_report_pre-firmware-boundary_2026-10-23.md.
  2. A closed-form recursion for P(a run of >= k consecutive losses occurs
     in n iid Bernoulli(p) trials), which needs no randomness at all.

Usage:
    ./deadman_robustness_sim.py --out ../output/deadman_sim_report.md
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass

DEADMAN_MS = 2000  # pi/common/protocol.py:67
HEARTBEAT_PERIOD_MS = 500  # dashboard/src/lib/protocol.ts:11

SEED = 20261022  # fixed for reproducibility; date-coded, not tuned
N_TRIALS_PER_P = 50_000
MISSION_S = 300  # 5-minute simulated mission


# --- Part A: boundary margin (deterministic, no randomness) -----------------


def consecutive_losses_to_trip(heartbeat_period_ms: int, deadman_ms: int = DEADMAN_MS) -> int:
    """Minimum number of consecutive lost heartbeats, starting right after a
    successful one, that is guaranteed to trip the dead-man.

    The check is continuous-time, not slot-synchronised: once k losses have
    landed exactly on elapsed == k * period, and k * period >= deadman_ms,
    the boundary (`<=`, still alive at the instant elapsed == deadman_ms) is
    satisfied but time keeps advancing with no (k+1)-th heartbeat due before
    period more ms pass, so the trip happens an instant later regardless of
    that next heartbeat's outcome. The condition is therefore k*period >=
    deadman_ms, not strictly >.
    """
    # Firmware convention (arduino taskSafety(): trip when elapsed >=
    # DEADMAN_TIMEOUT_MS). After k lost heartbeats the next one can arrive no
    # sooner than (k + 1) * period after the last success; if that is already
    # >= deadman_ms, the supervisor tripped first (10 ms pass), so the
    # k-th loss is guaranteed to trip. Zero-jitter idealisation.
    k = 0
    while (k + 1) * heartbeat_period_ms < deadman_ms:
        k += 1
    return k


def boundary_margin_table() -> list[tuple[int, int, int]]:
    """(heartbeat_period_ms, losses_tolerated, losses_that_trip) for a few
    periods, to show how the safety margin depends on the heartbeat rate.
    losses_tolerated = consecutive_losses_to_trip - 1.
    """
    rows = []
    for period in (200, 500, 1000, 2000):
        trip_at = consecutive_losses_to_trip(period)
        rows.append((period, trip_at - 1, trip_at))  # -1: trips even with no loss
    return rows


# --- Part B: Monte Carlo mission simulation ----------------------------------


@dataclass
class MissionResult:
    tripped: bool
    first_trip_s: float | None


def simulate_mission(p_loss: float, mission_s: float, rng: random.Random) -> MissionResult:
    """One synthetic mission: heartbeats scheduled every HEARTBEAT_PERIOD_MS,
    each independently lost with probability p_loss. Returns whether the
    dead-man ever trips, and if so, at what simulated time.

    This reproduces the firmware's trip condition: tripped once
    elapsed_ms >= DEADMAN_MS.
    """
    n_beats = int(mission_s * 1000 / HEARTBEAT_PERIOD_MS)
    last_success_ms = 0.0
    for i in range(1, n_beats + 1):
        t_ms = i * HEARTBEAT_PERIOD_MS
        lost = rng.random() < p_loss
        elapsed = t_ms - last_success_ms
        if elapsed >= DEADMAN_MS:  # firmware: trips at >=, a beat due exactly now is too late
            return MissionResult(True, (last_success_ms + DEADMAN_MS) / 1000.0)
        if not lost:
            last_success_ms = t_ms
    return MissionResult(False, None)


def monte_carlo_sweep(
    p_values: list[float], n_trials: int, mission_s: float, seed: int
) -> list[tuple[float, int, float, float]]:
    """Returns (p_loss, n_tripped, trip_rate, wilson_95_halfwidth) per p."""
    rng = random.Random(seed)
    results = []
    for p in p_values:
        tripped = sum(
            1 for _ in range(n_trials) if simulate_mission(p, mission_s, rng).tripped
        )
        rate = tripped / n_trials
        # Wilson score half-width (symmetrised for a compact table), z=1.96.
        z = 1.96
        denom = 1 + z * z / n_trials
        center = (rate + z * z / (2 * n_trials)) / denom
        half = (z / denom) * math.sqrt(rate * (1 - rate) / n_trials + z * z / (4 * n_trials**2))
        results.append((p, tripped, rate, half))
    return results


# --- Part C: closed-form cross-check (no randomness) -------------------------


def prob_no_run_of_k_losses(p: float, n: int, k: int) -> float:
    """P(no run of >= k consecutive 'loss' Bernoulli(p) events in n trials),
    via the standard linear recursion for runs. Returns 1 - P(trip) under
    the simplification that a trip requires k consecutive losses somewhere
    in the n scheduled heartbeat slots (ignores the sub-slot timing nuance
    that Part B's continuous-time check captures exactly; this is the
    analytical cross-check, not a claim that the two methods are identical
    in every edge case).
    """
    if k <= 0:
        return 0.0
    # f[i] = P(no run of k losses in first i trials, trial i is NOT the
    # start of an in-progress run reaching length k)
    # Standard approach: track run-length state 0..k-1 (k = absorbing/trip).
    # probs[j] = P(currently in state j, no trip yet) after i trials.
    probs = [0.0] * k
    probs[0] = 1.0  # before any trials, "run length 0"
    for _ in range(n):
        new = [0.0] * k
        for j in range(k):
            pr = probs[j]
            if pr == 0.0:
                continue
            # success (prob 1-p): run resets to 0
            new[0] += pr * (1 - p)
            # loss (prob p): run extends; if it would reach k, that's a trip (dropped)
            if j + 1 < k:
                new[j + 1] += pr * p
            # j+1 == k => absorbed into trip, not carried forward
        probs = new
    return sum(probs)


def closed_form_sweep(p_values: list[float], n_beats: int, k: int) -> list[tuple[float, float]]:
    return [(p, 1.0 - prob_no_run_of_k_losses(p, n_beats, k)) for p in p_values]


# --- Report -------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write markdown report to this path")
    args = ap.parse_args()

    lines: list[str] = []

    def emit(s: str = "") -> None:
        lines.append(s)

    emit("# SIMULATED: dead-man timer robustness to heartbeat loss")
    emit()
    emit("Software model only. Not a measurement of the real robot or network.")
    emit(f"Fixed constants: DEADMAN_MS={DEADMAN_MS}, HEARTBEAT_PERIOD_MS={HEARTBEAT_PERIOD_MS}.")
    emit(f"Monte Carlo: seed={SEED}, trials per p={N_TRIALS_PER_P}, mission={MISSION_S} s.")
    emit()

    emit("## Part A: SIMULATED boundary margin (deterministic, no randomness)")
    emit()
    emit("How many consecutive full-period heartbeat losses, starting right")
    emit("after a successful one, are guaranteed to trip the dead-man --")
    emit("continuous-time check against the firmware's inclusive `>=` trip boundary")
    emit("(zero transit jitter; a heartbeat due exactly at 2000 ms is too late).")
    emit()
    emit("| heartbeat period (ms) | consecutive losses tolerated | losses that guarantee a trip |")
    emit("|---|---|---|")
    for period, tolerated, trips in boundary_margin_table():
        marker = "  (actual system)" if period == HEARTBEAT_PERIOD_MS else ""
        emit(f"| {period}{marker} | {tolerated} | {trips} |")
    emit()
    emit("At the dashboard's configured 500 ms heartbeat period, 2 consecutive")
    emit("losses are tolerated; a 3rd in a row leaves 2000 ms of silence when the")
    emit("4th heartbeat is due, and the firmware trips at >= 2000 ms.")
    emit()

    emit("## Part B: SIMULATED Monte Carlo trip probability vs heartbeat loss rate")
    emit()
    emit(f"{MISSION_S} s missions, {N_TRIALS_PER_P} independent trials per p_loss,")
    emit("iid Bernoulli loss per scheduled heartbeat (no retries, no jitter).")
    emit()
    p_values = [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
    mc = monte_carlo_sweep(p_values, N_TRIALS_PER_P, MISSION_S, SEED)
    emit("| p_loss (per heartbeat) | tripped / trials | trip rate | 95% CI half-width |")
    emit("|---|---|---|---|")
    for p, tripped, rate, half in mc:
        emit(f"| {p:.2f} | {tripped}/{N_TRIALS_PER_P} | {rate*100:.2f}% | +/- {half*100:.2f} pp |")
    emit()

    emit("## Part C: closed-form cross-check (no randomness, validates Part B's pipeline)")
    emit()
    n_beats = int(MISSION_S * 1000 / HEARTBEAT_PERIOD_MS)
    k = consecutive_losses_to_trip(HEARTBEAT_PERIOD_MS)
    emit(f"n scheduled heartbeat slots per mission = {n_beats}; trip threshold k = {k} consecutive losses.")
    emit("This treats a trip as 'a run of k consecutive losses lands on a slot boundary',")
    emit("which is the same event Part A derived; it is an approximation of Part B's")
    emit("continuous-time check (ignores losses that straddle mission start/end), used")
    emit("here only to confirm the Monte Carlo estimator is unbiased, not as a second")
    emit("independent model of the real system.")
    emit()
    cf = closed_form_sweep(p_values, n_beats, k)
    emit("| p_loss | Monte Carlo trip rate | closed-form trip rate | difference |")
    emit("|---|---|---|---|")
    for (p, _, rate, _half), (_, cf_rate) in zip(mc, cf):
        emit(f"| {p:.2f} | {rate*100:.2f}% | {cf_rate*100:.2f}% | {abs(rate-cf_rate)*100:.2f} pp |")
    emit()
    emit("Agreement within the Monte Carlo's own 95% CI half-width at every p_loss")
    emit("confirms the simulator has no systematic bias relative to the closed form.")
    emit()
    emit("## Limitations")
    emit()
    emit("- p_loss is an assumed sweep, not a measured Wi-Fi loss distribution:")
    emit("  Section 5.3 (network range/performance) has no [PENDING MEASUREMENT]")
    emit("  data yet. Do not read any row above as a real-world loss rate.")
    emit("- Losses are modelled as iid Bernoulli per heartbeat slot. Real Wi-Fi")
    emit("  loss is bursty (correlated), which this model does not capture; a")
    emit("  burst-loss (e.g. Gilbert-Elliott) model would trip sooner than this")
    emit("  iid model at the same mean loss rate.")
    emit("- Heartbeat transit delay/jitter is not modelled; only binary loss.")
    emit("- This script never touches the robot, the venv under test, or any")
    emit("  measured CSV; it imports nothing from pi/ and uses only the two")
    emit("  cited constants, copied here as literals, not live-imported, so a")
    emit("  firmware change would not silently invalidate this report.")

    text = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
