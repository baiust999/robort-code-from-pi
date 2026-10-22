"""Isolated proof-of-concept for the proposed dead-man patch. NOT production
code and not imported by anything under pi/ or by the live robot-watchdog
service.

This subclasses the real, unmodified `pi.common.mock_hardware.MockArduino`
(imported read-only) and overrides exactly the two behaviours the proposed
patch (see PATCH_production.diff in this directory) would change in
`pi/common/mock_hardware.py` and `pi/common/protocol.py`:

1. Timeout boundary: the firmware's `taskSafety()` trips on
   `elapsed >= DEADMAN_TIMEOUT_MS` (arduino/arduino.ino:79). The shipped
   mock's `_check_deadman` stays alive on `elapsed <= DEADMAN_MS`, i.e. it
   is alive at the exact boundary where the firmware already trips. This
   subclass changes the comparison to `elapsed < DEADMAN_MS` to match.
2. Re-arming set: the firmware's `handleLine()` calls `noteCommandReceived()`
   for any opcode that passes `validateArg()` -- i.e. every opcode in
   `ALL_COMMANDS`, including CMD_PAN/CMD_TILT/CMD_STATUS
   (arduino/command_parser.cpp:87-89, validateArg at lines 102-144). The
   shipped mock only arms on `protocol.DEADMAN_ARMING_COMMANDS`, which
   excludes pan/tilt/status. This subclass arms on `PATCHED_ARMING_COMMANDS`
   (== `protocol.ALL_COMMANDS`) instead.

Everything else (framing, argument clamping, motor execution, telemetry) is
inherited unchanged from the real MockArduino.
"""

from __future__ import annotations

import sys
from pathlib import Path

PI_ROOT = Path(__file__).resolve().parents[2] / "pi"
if str(PI_ROOT) not in sys.path:
    sys.path.insert(0, str(PI_ROOT))

from common import protocol  # noqa: E402
from common.mock_hardware import MockArduino, _MotorState  # noqa: E402

# arduino/command_parser.cpp:87-89: "Any well-formed command counts as comms
# activity for the dead-man timer, even a query or heartbeat." Well-formed
# here means it passed validateArg(), i.e. it is one of ALL_COMMANDS.
PATCHED_ARMING_COMMANDS = protocol.ALL_COMMANDS


class PatchedMockArduino(MockArduino):
    """MockArduino with the two dead-man corrections applied, isolated."""

    def _check_deadman(self, now: float) -> None:
        if now - self._last_command_ms < protocol.DEADMAN_MS:  # was: <=
            return
        if self._deadman_tripped:
            return
        self._deadman_tripped = True
        self._motors = _MotorState()
        if self._fw_state != protocol.FW_STATE_STOPPED:
            self._fw_state = protocol.FW_STATE_ARMED

    def _handle_line(self, line: str) -> None:
        # Identical to MockArduino._handle_line except the arming-set check
        # below uses PATCHED_ARMING_COMMANDS instead of
        # protocol.DEADMAN_ARMING_COMMANDS. Everything else is unchanged.
        if not line:
            return

        if len(line) > protocol.MAX_COMMAND_CHARS:
            self._respond("ERR_LEN")
            return

        opcode = line[0]

        if opcode not in protocol.ALL_COMMANDS:
            self._respond("ERR_TOK")
            return

        argument = 0
        tail = line[1:]
        if tail:
            if tail.isdigit():
                argument = int(tail)
                if argument > protocol.MAX_PWM:
                    argument = protocol.MAX_PWM
                    self._respond("WARN_CLAMP")
            else:
                argument = 0
                self._respond("WARN_CLAMP")

        now_ms = _now_ms()

        if opcode in PATCHED_ARMING_COMMANDS:  # <-- the one changed line
            self._arm(now_ms)

        self._execute(opcode, argument, now_ms)


def _now_ms() -> float:
    import time

    return time.monotonic() * 1000.0
