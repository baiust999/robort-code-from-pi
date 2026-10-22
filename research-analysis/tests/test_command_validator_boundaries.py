"""New exact-boundary tests for CommandValidator.

The existing suite (pi/tests/test_command_validator.py) exercises clamping
with far out-of-range values (999, -50), which cannot distinguish a correct
`> high` / `< low` comparison from an off-by-one error at the boundary
itself. These tests probe the exact boundary values and the strict
monotonicity of the sequence check.

Source under test: pi/p1_control/safety.py (CommandValidator, _clamp_int).
Safety: pure object-level unit tests, no I/O, no hardware, no network.
"""

from __future__ import annotations

import sys
from pathlib import Path

PI_ROOT = Path(__file__).resolve().parents[2] / "pi"
if str(PI_ROOT) not in sys.path:
    sys.path.insert(0, str(PI_ROOT))

from common import protocol  # noqa: E402
from p1_control.safety import CommandValidator  # noqa: E402


def test_speed_at_max_pwm_is_not_flagged_as_clamped():
    v = CommandValidator()
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": protocol.MAX_PWM}, client_id="c1"
    )
    assert result.ok
    assert result.argument == protocol.MAX_PWM
    assert result.warnings == []


def test_speed_one_above_max_pwm_is_clamped():
    v = CommandValidator()
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": protocol.MAX_PWM + 1}, client_id="c1"
    )
    assert result.ok
    assert result.argument == protocol.MAX_PWM
    assert any("clamped" in w for w in result.warnings)


def test_speed_at_min_pwm_is_not_flagged_as_clamped():
    v = CommandValidator()
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": protocol.MIN_PWM}, client_id="c1"
    )
    assert result.ok
    assert result.argument == protocol.MIN_PWM
    assert result.warnings == []


def test_speed_one_below_min_pwm_is_clamped():
    v = CommandValidator()
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": protocol.MIN_PWM - 1}, client_id="c1"
    )
    assert result.ok
    assert result.argument == protocol.MIN_PWM
    assert any("clamped" in w for w in result.warnings)


def test_servo_angle_boundaries_not_flagged():
    v = CommandValidator()
    low = v.validate(
        {"type": "servo", "axis": "pan", "angle": protocol.SERVO_MIN_ANGLE},
        client_id="c1",
    )
    high = v.validate(
        {"type": "servo", "axis": "tilt", "angle": protocol.SERVO_MAX_ANGLE},
        client_id="c1",
    )
    assert low.ok and low.argument == protocol.SERVO_MIN_ANGLE and low.warnings == []
    assert high.ok and high.argument == protocol.SERVO_MAX_ANGLE and high.warnings == []


def test_servo_angle_one_past_each_boundary_is_clamped():
    v = CommandValidator()
    below = v.validate(
        {"type": "servo", "axis": "pan", "angle": protocol.SERVO_MIN_ANGLE - 1},
        client_id="c1",
    )
    above = v.validate(
        {"type": "servo", "axis": "tilt", "angle": protocol.SERVO_MAX_ANGLE + 1},
        client_id="c1",
    )
    assert below.ok and below.argument == protocol.SERVO_MIN_ANGLE
    assert above.ok and above.argument == protocol.SERVO_MAX_ANGLE
    assert any("clamped" in w for w in below.warnings)
    assert any("clamped" in w for w in above.warnings)


def test_sequence_exactly_one_less_than_last_is_stale():
    v = CommandValidator()
    v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 10}, client_id="c1")
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": 10, "seq": 9}, client_id="c1"
    )
    assert not result.ok
    assert "stale seq" in result.reason


def test_sequence_exactly_one_more_than_last_is_accepted():
    v = CommandValidator()
    v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 10}, client_id="c1")
    result = v.validate(
        {"type": "motor", "dir": "F", "speed": 10, "seq": 11}, client_id="c1"
    )
    assert result.ok


def test_sequence_zero_then_negative_is_rejected():
    """seq is not restricted to positive values by validate(); the ordering
    check must still hold for zero and negative sequence numbers.
    """
    v = CommandValidator()
    first = v.validate(
        {"type": "motor", "dir": "F", "speed": 10, "seq": 0}, client_id="c1"
    )
    second = v.validate(
        {"type": "motor", "dir": "F", "speed": 10, "seq": -1}, client_id="c1"
    )
    assert first.ok
    assert not second.ok
    assert "stale seq" in second.reason
