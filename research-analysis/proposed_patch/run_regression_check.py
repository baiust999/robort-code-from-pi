"""Checks whether applying the proposed patch would break the protected,
historical pi/tests/ suite -- WITHOUT writing to any file under pi/.

Does this by monkeypatching the two targeted behaviours on the imported
module objects, in this process's memory only, then running the real
pi/tests/ suite against the patched objects. Nothing on disk is touched;
the patch is undone the moment this process exits. Run with:

    /home/pi/robot/venv/bin/python research-analysis/proposed_patch/run_regression_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PI_ROOT = REPO_ROOT / "pi"
sys.path.insert(0, str(PI_ROOT))

import pytest  # noqa: E402

from common import mock_hardware, protocol  # noqa: E402
from common.mock_hardware import _MotorState  # noqa: E402


def _patched_check_deadman(self, now: float) -> None:
    if now - self._last_command_ms < protocol.DEADMAN_MS:  # was: <=
        return
    if self._deadman_tripped:
        return
    self._deadman_tripped = True
    self._motors = _MotorState()
    if self._fw_state != protocol.FW_STATE_STOPPED:
        self._fw_state = protocol.FW_STATE_ARMED


def main() -> int:
    original_check_deadman = mock_hardware.MockArduino._check_deadman
    original_arming = protocol.DEADMAN_ARMING_COMMANDS

    mock_hardware.MockArduino._check_deadman = _patched_check_deadman
    protocol.DEADMAN_ARMING_COMMANDS = protocol.ALL_COMMANDS
    try:
        print("=== Running pi/tests/ with the proposed patch applied in-memory only ===")
        return pytest.main(["-v", str(PI_ROOT / "tests")])
    finally:
        mock_hardware.MockArduino._check_deadman = original_check_deadman
        protocol.DEADMAN_ARMING_COMMANDS = original_arming
        print("=== In-memory patch reverted; pi/ source files were never modified ===")


if __name__ == "__main__":
    raise SystemExit(main())
