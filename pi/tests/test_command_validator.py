"""CommandValidator four-stage pipeline, Section 8.10.1.3."""

from p1_control.safety import CommandValidator


def test_valid_forward_command():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": 120}, client_id="c1", range_cm=100)
    assert result.ok
    assert result.opcode == "F"
    assert result.argument == 120
    assert result.wire == "F120\n"


def test_unknown_direction_rejected():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "X", "speed": 100}, client_id="c1", range_cm=100)
    assert not result.ok
    assert "unknown direction" in result.reason


def test_speed_clamped_to_max_pwm():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": 999}, client_id="c1", range_cm=100)
    assert result.ok
    assert result.argument == 180
    assert any("clamped" in w for w in result.warnings)


def test_speed_clamped_to_min_pwm():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": -50}, client_id="c1", range_cm=100)
    assert result.ok
    assert result.argument == 0


def test_forward_blocked_by_obstacle_at_or_below_threshold():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": 100}, client_id="c1", range_cm=20)
    assert not result.ok
    assert "obstacle" in result.reason


def test_forward_allowed_just_above_obstacle_threshold():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": 100}, client_id="c1", range_cm=21)
    assert result.ok


def test_reverse_not_blocked_by_close_obstacle():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "R", "speed": 100}, client_id="c1", range_cm=5)
    assert result.ok


def test_zero_speed_forward_not_blocked_by_obstacle():
    v = CommandValidator()
    result = v.validate({"type": "motor", "dir": "F", "speed": 0}, client_id="c1", range_cm=5)
    assert result.ok


def test_servo_pan_and_tilt():
    v = CommandValidator()
    pan = v.validate({"type": "servo", "axis": "pan", "angle": 45}, client_id="c1", range_cm=None)
    tilt = v.validate({"type": "servo", "axis": "tilt", "angle": 200}, client_id="c1", range_cm=None)
    assert pan.ok and pan.opcode == "P" and pan.argument == 45
    assert tilt.ok and tilt.argument == 180  # clamped


def test_unknown_servo_axis_rejected():
    v = CommandValidator()
    result = v.validate({"type": "servo", "axis": "yaw", "angle": 10}, client_id="c1", range_cm=None)
    assert not result.ok


def test_heartbeat_always_ok():
    v = CommandValidator()
    result = v.validate({"type": "heartbeat"}, client_id="c1", range_cm=5)
    assert result.ok
    assert result.opcode == "H"


def test_stop_all_bypasses_sequence_check():
    v = CommandValidator()
    v.validate({"type": "motor", "dir": "F", "speed": 1, "seq": 10}, client_id="c1", range_cm=100)
    # A stale seq would normally be rejected, but stop_all doesn't check seq at all.
    result = v.validate({"type": "stop_all", "seq": 1}, client_id="c1", range_cm=100)
    assert result.ok
    assert result.opcode == "S"


def test_stale_sequence_rejected():
    v = CommandValidator()
    first = v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 5}, client_id="c1", range_cm=100)
    second = v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 5}, client_id="c1", range_cm=100)
    assert first.ok
    assert not second.ok
    assert "stale seq" in second.reason


def test_sequence_tracked_per_client():
    v = CommandValidator()
    a = v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 5}, client_id="client-a", range_cm=100)
    b = v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 5}, client_id="client-b", range_cm=100)
    assert a.ok
    assert b.ok  # independent sequence counters per client


def test_reset_client_clears_sequence_state():
    v = CommandValidator()
    v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 5}, client_id="c1", range_cm=100)
    v.reset_client("c1")
    result = v.validate({"type": "motor", "dir": "F", "speed": 10, "seq": 1}, client_id="c1", range_cm=100)
    assert result.ok


def test_missing_seq_skips_sequence_check():
    v = CommandValidator()
    a = v.validate({"type": "motor", "dir": "F", "speed": 10}, client_id="c1", range_cm=100)
    b = v.validate({"type": "motor", "dir": "F", "speed": 10}, client_id="c1", range_cm=100)
    assert a.ok and b.ok


def test_unsupported_message_type_rejected():
    v = CommandValidator()
    result = v.validate({"type": "bogus"}, client_id="c1", range_cm=100)
    assert not result.ok
