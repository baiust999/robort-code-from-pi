"""Server-side command validation, Section 8.10.1.3.

P1 repeats the checks the firmware already performs. This is deliberate
defence-in-depth: the Arduino enforces safety for its own sake and cannot be
bypassed, while these checks reject bad input before it consumes UART
bandwidth and give the operator an immediate reason string.

Pipeline: speed clamp -> proximity gate -> sequence monotonicity -> encode.
"""

from __future__ import annotations

from typing import Any

from common import protocol
from common.protocol import ValidationResult


class CommandValidator:
    """Validates dashboard messages into Arduino wire commands."""

    def __init__(self) -> None:
        self._last_seq: dict[str, int] = {}

    def reset_client(self, client_id: str) -> None:
        self._last_seq.pop(client_id, None)

    def validate(
        self,
        message: dict[str, Any],
        *,
        client_id: str,
        range_cm: int | None,
    ) -> ValidationResult:
        msg_type = message.get("type")

        if msg_type == protocol.MSG_MOTOR:
            return self._validate_motor(message, client_id=client_id, range_cm=range_cm)
        if msg_type == protocol.MSG_SERVO:
            return self._validate_servo(message, client_id=client_id)
        if msg_type == protocol.MSG_HEARTBEAT:
            return ValidationResult(
                ok=True,
                opcode=protocol.CMD_HEARTBEAT,
                wire=protocol.encode_command(protocol.CMD_HEARTBEAT),
            )
        if msg_type == protocol.MSG_STOP_ALL:
            # Emergency stop bypasses sequence checking entirely: a stop must
            # never be dropped because a counter arrived out of order.
            return ValidationResult(
                ok=True,
                opcode=protocol.CMD_STOP,
                wire=protocol.encode_command(protocol.CMD_STOP),
            )

        return ValidationResult(ok=False, reason=f"unsupported type {msg_type!r}")

    def _validate_motor(
        self, message: dict[str, Any], *, client_id: str, range_cm: int | None
    ) -> ValidationResult:
        direction = message.get("dir")
        opcode = protocol.DIRECTION_TO_OPCODE.get(str(direction))
        if opcode is None:
            return ValidationResult(ok=False, reason=f"unknown direction {direction!r}")

        speed, warnings = _clamp_int(
            message.get("speed"), protocol.MIN_PWM, protocol.MAX_PWM, "speed"
        )
        if speed is None:
            return ValidationResult(ok=False, reason="speed is not a number")

        if opcode == protocol.CMD_FORWARD and speed > 0:
            if range_cm is not None and range_cm <= protocol.OBSTACLE_BLOCK_CM:
                return ValidationResult(
                    ok=False,
                    reason=f"obstacle at {range_cm}cm blocks forward motion",
                )

        seq_error = self._check_sequence(message, client_id)
        if seq_error is not None:
            return ValidationResult(ok=False, reason=seq_error)

        return ValidationResult(
            ok=True,
            opcode=opcode,
            argument=speed,
            wire=protocol.encode_command(opcode, speed),
            warnings=warnings,
        )

    def _validate_servo(
        self, message: dict[str, Any], *, client_id: str
    ) -> ValidationResult:
        axis = message.get("axis")
        if axis == "pan":
            opcode = protocol.CMD_PAN
        elif axis == "tilt":
            opcode = protocol.CMD_TILT
        else:
            return ValidationResult(ok=False, reason=f"unknown servo axis {axis!r}")

        angle, warnings = _clamp_int(
            message.get("angle"),
            protocol.SERVO_MIN_ANGLE,
            protocol.SERVO_MAX_ANGLE,
            "angle",
        )
        if angle is None:
            return ValidationResult(ok=False, reason="angle is not a number")

        seq_error = self._check_sequence(message, client_id)
        if seq_error is not None:
            return ValidationResult(ok=False, reason=seq_error)

        return ValidationResult(
            ok=True,
            opcode=opcode,
            argument=angle,
            wire=protocol.encode_command(opcode, angle),
            warnings=warnings,
        )

    def _check_sequence(self, message: dict[str, Any], client_id: str) -> str | None:
        """Reject replayed or reordered commands, Section 8.10.1.3.

        Messages without a seq are accepted: the field is optional and its
        absence simply forgoes the protection.
        """
        raw = message.get("seq")
        if raw is None:
            return None
        try:
            seq = int(raw)
        except (TypeError, ValueError):
            return "seq is not an integer"

        last = self._last_seq.get(client_id)
        if last is not None and seq <= last:
            return f"stale seq {seq} (last {last})"
        self._last_seq[client_id] = seq
        return None


def _clamp_int(
    raw: Any, low: int, high: int, name: str
) -> tuple[int | None, list[str]]:
    warnings: list[str] = []
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None, warnings
    if value < low:
        warnings.append(f"{name} clamped {value}->{low}")
        value = low
    elif value > high:
        warnings.append(f"{name} clamped {value}->{high}")
        value = high
    return value, warnings
