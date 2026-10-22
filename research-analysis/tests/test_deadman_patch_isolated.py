"""Isolated tests for the PROPOSED dead-man patch (not applied to production).

These import `research_analysis.proposed_patch.mock_hardware_patched`
(a subclass that lives entirely under research-analysis/, never imported by
pi/ or the live robot-watchdog service) to prove the two-line fix described
in `research-analysis/proposed_patch/PATCH_production.diff` behaves as
intended, before that diff is applied anywhere. They do not modify, replace,
or run against `pi/common/mock_hardware.py` itself -- see
`research-analysis/proposed_patch/run_regression_check.py` (and its output,
reported alongside this file) for whether the real, unpatched historical
suite (`pi/tests/`) would still pass if the patch were applied there.

Safety: pure in-memory objects, deterministic fake clock, no serial device,
no socket, no systemd interaction.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROPOSED_PATCH_DIR = Path(__file__).resolve().parents[1] / "proposed_patch"
if str(PROPOSED_PATCH_DIR) not in sys.path:
    sys.path.insert(0, str(PROPOSED_PATCH_DIR))

PI_ROOT = Path(__file__).resolve().parents[2] / "pi"
if str(PI_ROOT) not in sys.path:
    sys.path.insert(0, str(PI_ROOT))

from common import mock_hardware, protocol  # noqa: E402
from mock_hardware_patched import PatchedMockArduino  # noqa: E402


class _FakeClock:
    def __init__(self, start_s: float = 1000.0) -> None:
        self.t = start_s

    def __call__(self) -> float:
        return self.t

    def advance_ms(self, ms: float) -> None:
        self.t += ms / 1000.0


def _patched_board_with_fake_clock(monkeypatch, seed: int = 1):
    clock = _FakeClock()
    monkeypatch.setattr(mock_hardware.time, "monotonic", clock)
    board = PatchedMockArduino(seed=seed)
    return board, clock


# --- Correction 1: boundary direction ---------------------------------------


def test_patched_deadman_trips_at_exactly_deadman_ms(monkeypatch):
    """Firmware (arduino.ino taskSafety): trips when elapsed >= DEADMAN_TIMEOUT_MS.
    The unpatched mock stays alive here (see
    test_deadman_boundaries.test_deadman_alive_at_exactly_deadman_ms); the
    patched mock must now trip, matching the firmware.
    """
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")
    assert board._deadman_tripped is False  # noqa: SLF001

    clock.advance_ms(protocol.DEADMAN_MS)  # elapsed == DEADMAN_MS exactly
    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


def test_patched_deadman_still_alive_one_ms_before_boundary(monkeypatch):
    """Immediately-before-boundary case: elapsed == DEADMAN_MS - 1 must still
    be alive on both the real firmware and the patched mock (this one line
    does not change relative to the unpatched mock).
    """
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS - 1)
    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001


def test_patched_deadman_trips_one_ms_past_boundary(monkeypatch):
    """Sanity check in the other direction: unchanged from the unpatched mock."""
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS + 1)
    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


# --- Correction 2: re-arming set ---------------------------------------------


def test_patched_pan_command_rearms_deadman(monkeypatch):
    """command_parser.cpp calls noteCommandReceived() for ANY opcode that
    passes validateArg(), including CMD_PAN. On the patched mock, a pan
    command sent right up to (and past) the original drive command's
    deadline must now mask the expiry, matching the firmware.
    """
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")
    assert board._deadman_tripped is False  # noqa: SLF001

    for _ in range(5):
        clock.advance_ms(protocol.DEADMAN_MS / 5)
        board.write(b"P90\n")
    clock.advance_ms(1)  # one ms past where the ORIGINAL F120 would have expired

    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001


def test_patched_tilt_and_status_rearm_deadman(monkeypatch):
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS - 50)
    board.write(b"T45\n")
    board.write(b"?\n")
    clock.advance_ms(60)  # now DEADMAN_MS + 10 since the original F120

    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001


def test_patched_pan_at_exact_new_arming_boundary_then_one_ms_before_expiry(monkeypatch):
    """Combines both corrections: pan arms (correction 2) at exactly
    DEADMAN_MS after the drive command (correction 1's own boundary is
    `< DEADMAN_MS` to stay alive, so this re-arming pan command itself
    lands exactly on the trip instant). Confirms the pan command's own
    arming is evaluated before _check_deadman would have tripped on the
    same tick, then checks the immediately-before-next-boundary instant.
    """
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS - 1)  # one ms before the original deadline
    board.write(b"P90\n")  # re-arms here, patched behaviour
    assert board._deadman_tripped is False  # noqa: SLF001

    clock.advance_ms(protocol.DEADMAN_MS - 1)  # one ms before the NEW deadline
    board.tick()
    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001

    clock.advance_ms(1)  # now exactly DEADMAN_MS since the pan re-arm
    board.tick()
    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


# --- Unchanged behaviour sanity checks ---------------------------------------


def test_patched_heartbeat_still_arms(monkeypatch):
    board, clock = _patched_board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")
    clock.advance_ms(protocol.DEADMAN_MS - 100)
    board.write(b"H\n")
    assert board._deadman_tripped is False  # noqa: SLF001
    board.tick()
    assert board._motors.speed == 120  # noqa: SLF001


def test_patched_boots_with_deadman_already_expired(monkeypatch):
    board, _clock = _patched_board_with_fake_clock(monkeypatch)
    board.tick()
    assert board._deadman_tripped is True  # noqa: SLF001
