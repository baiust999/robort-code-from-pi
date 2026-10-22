"""Exact-boundary test for the MAX_COMMAND_CHARS length check.

pi/tests/test_mock_deadman.py::test_oversized_command_rejected sends an
11-character line, which proves oversized commands are rejected but not
where the cutoff actually sits. This checks the boundary itself: a line of
exactly MAX_COMMAND_CHARS must pass stage 1, and one character more must
not.

Source under test: pi/common/mock_hardware.py MockArduino._handle_line,
pi/common/protocol.py MAX_COMMAND_CHARS. Safety: in-memory object only.
"""

from __future__ import annotations

import sys
from pathlib import Path

PI_ROOT = Path(__file__).resolve().parents[2] / "pi"
if str(PI_ROOT) not in sys.path:
    sys.path.insert(0, str(PI_ROOT))

from common import protocol  # noqa: E402
from common.mock_hardware import MockArduino  # noqa: E402


def _read_lines(board: MockArduino) -> list[str]:
    raw = board.read_all()
    return [line for line in raw.decode().splitlines() if line]


def test_line_at_exactly_max_command_chars_is_accepted():
    n_digits = protocol.MAX_COMMAND_CHARS - 1  # 1 char for the opcode
    line = "F" + "1" * n_digits
    assert len(line) == protocol.MAX_COMMAND_CHARS

    board = MockArduino(seed=1)
    board.write((line + "\n").encode())
    lines = _read_lines(board)

    assert "ERR_LEN" not in lines


def test_line_one_char_past_max_command_chars_is_rejected():
    n_digits = protocol.MAX_COMMAND_CHARS  # opcode + this many digits = +1 over
    line = "F" + "1" * n_digits
    assert len(line) == protocol.MAX_COMMAND_CHARS + 1

    board = MockArduino(seed=1)
    board.write((line + "\n").encode())
    lines = _read_lines(board)

    assert "ERR_LEN" in lines
