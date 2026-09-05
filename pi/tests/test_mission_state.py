"""derive_mission_state first-match rules, Section 8.11.1.1."""

from common import protocol


def _base(**overrides) -> dict:
    params = dict(
        ws_connected=True,
        serial_ok=True,
        video_active=True,
        mesh_ok=True,
        last_cmd_ack_ms=0,
        command_active=False,
    )
    params.update(overrides)
    return params


def test_disconnected_ws_is_stop():
    assert protocol.derive_mission_state(**_base(ws_connected=False)) == protocol.MISSION_STOP


def test_serial_down_is_stop():
    assert protocol.derive_mission_state(**_base(serial_ok=False)) == protocol.MISSION_STOP


def test_stale_ack_is_stop():
    params = _base(last_cmd_ack_ms=protocol.COMMAND_ACK_TIMEOUT_MS + 1)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_STOP


def test_ack_at_exact_timeout_not_stop():
    params = _base(last_cmd_ack_ms=protocol.COMMAND_ACK_TIMEOUT_MS)
    assert protocol.derive_mission_state(**params) != protocol.MISSION_STOP


def test_stop_takes_priority_over_degraded_video():
    params = _base(ws_connected=False, video_active=False)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_STOP


def test_video_down_is_driving_limited():
    params = _base(video_active=False)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_DRIVING_LIMITED


def test_mesh_down_is_driving_limited():
    params = _base(mesh_ok=False)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_DRIVING_LIMITED


def test_nominal_idle_is_ready():
    assert protocol.derive_mission_state(**_base()) == protocol.MISSION_READY


def test_nominal_active_is_driving():
    params = _base(command_active=True)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_DRIVING


def test_driving_limited_ignores_command_active():
    """A degraded link caps the state at DRIVING_LIMITED regardless of command_active."""
    params = _base(video_active=False, command_active=True)
    assert protocol.derive_mission_state(**params) == protocol.MISSION_DRIVING_LIMITED
