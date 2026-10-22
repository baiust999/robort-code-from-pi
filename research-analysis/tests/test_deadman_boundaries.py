"""New boundary tests for the MockArduino dead-man timer.

Scope: these import pi/common (read-only) from an isolated test directory.
They do not modify, replace, or duplicate anything in pi/tests/; they probe
exact-boundary and non-arming-command behaviour that the existing suite
(pi/tests/test_mock_deadman.py) does not assert.

Source under test: pi/common/mock_hardware.py (MockArduino._check_deadman,
_handle_line) and pi/common/protocol.py (DEADMAN_MS, DEADMAN_ARMING_COMMANDS).

Safety: pure in-memory objects, MOCK_HARDWARE semantics only. No serial
device, no network socket, no systemd interaction. Clock is controlled by
monkeypatching time.monotonic inside the mock_hardware module, so no test
sleeps or depends on wall-clock scheduling.
"""

from __future__ import annotations

import sys
from pathlib import Path

PI_ROOT = Path(__file__).resolve().parents[2] / "pi"
if str(PI_ROOT) not in sys.path:
    sys.path.insert(0, str(PI_ROOT))

from common import mock_hardware, protocol  # noqa: E402
from common.mock_hardware import MockArduino  # noqa: E402


class _FakeClock:
    """Deterministic stand-in for time.monotonic(), in seconds."""

    def __init__(self, start_s: float = 1000.0) -> None:
        self.t = start_s

    def __call__(self) -> float:
        return self.t

    def advance_ms(self, ms: float) -> None:
        self.t += ms / 1000.0


def _board_with_fake_clock(monkeypatch, seed: int = 1) -> tuple[MockArduino, _FakeClock]:
    clock = _FakeClock()
    monkeypatch.setattr(mock_hardware.time, "monotonic", clock)
    board = MockArduino(seed=seed)
    return board, clock


def test_deadman_alive_at_exactly_deadman_ms(monkeypatch):
    """_check_deadman uses `<=`, so elapsed == DEADMAN_MS must still be alive."""
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")
    assert board._deadman_tripped is False  # noqa: SLF001

    clock.advance_ms(protocol.DEADMAN_MS)  # elapsed == DEADMAN_MS exactly
    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001


def test_deadman_trips_one_ms_past_boundary(monkeypatch):
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS + 1)  # elapsed == DEADMAN_MS + 1
    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


def test_deadman_still_alive_one_ms_before_boundary(monkeypatch):
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS - 1)
    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001


def test_pan_command_does_not_rearm_deadman(monkeypatch):
    """CMD_PAN is in ALL_COMMANDS but deliberately excluded from
    DEADMAN_ARMING_COMMANDS (protocol.py line 45-46). Continuously panning
    the camera must NOT mask an expired drive command: the motors still
    have to stop on schedule.
    """
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")
    assert board._deadman_tripped is False  # noqa: SLF001

    # Walk the clock forward in small steps, sending a pan command at each
    # step, right up to the original drive command's deadline, then step
    # one more ms past it so the elapsed time strictly exceeds DEADMAN_MS
    # (the boundary itself is inclusive/alive, per
    # test_deadman_alive_at_exactly_deadman_ms).
    for _ in range(5):
        clock.advance_ms(protocol.DEADMAN_MS / 5)
        board.write(b"P90\n")
    clock.advance_ms(1)

    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


def test_tilt_and_status_also_do_not_rearm_deadman(monkeypatch):
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS - 50)
    board.write(b"T45\n")
    board.write(b"?\n")
    clock.advance_ms(60)  # now DEADMAN_MS + 10 since the original F120
    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


def test_heartbeat_at_exact_boundary_rearms(monkeypatch):
    """Sanity check in the other direction: an arming command sent exactly
    at the boundary must reset the window from that instant.
    """
    board, clock = _board_with_fake_clock(monkeypatch)
    board.write(b"F120\n")

    clock.advance_ms(protocol.DEADMAN_MS)  # right at the edge, still alive
    board.write(b"H\n")  # heartbeat re-arms

    clock.advance_ms(protocol.DEADMAN_MS - 1)  # one ms short of the new deadline
    board.tick()

    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._motors.speed == 120  # noqa: SLF001
