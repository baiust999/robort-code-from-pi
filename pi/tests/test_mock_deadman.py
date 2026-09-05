"""MockArduino dead-man timer and obstacle gate, mirrors robot_state.cpp/command_parser.cpp."""

import time

from common import protocol
from common.mock_hardware import MockArduino


def _read_lines(board: MockArduino) -> list[str]:
    raw = board.read_all()
    return [line for line in raw.decode().splitlines() if line]


def test_boots_with_deadman_already_expired():
    """stateInit() starts lastCommandTime expired, Section 8.7.7 safe-boot order."""
    board = MockArduino(seed=1)
    board.tick()
    # No motion should be possible from a cold boot with no command sent yet.
    assert board._deadman_tripped is True  # noqa: SLF001


def test_forward_command_arms_deadman_and_drives():
    board = MockArduino(seed=1)
    board.write(b"F120\n")
    assert board._deadman_tripped is False  # noqa: SLF001
    assert board._fw_state == protocol.FW_STATE_DRIVING  # noqa: SLF001


def test_deadman_trips_after_timeout_and_stops_motors():
    board = MockArduino(seed=1)
    board.write(b"F120\n")
    assert board._motors.speed == 120  # noqa: SLF001

    # Simulate time passing beyond DEADMAN_MS without another command by
    # rewinding last_command_ms directly rather than sleeping 2s in a test.
    board._last_command_ms -= protocol.DEADMAN_MS + 1  # noqa: SLF001
    board.tick()

    assert board._deadman_tripped is True  # noqa: SLF001
    assert board._motors.speed == 0  # noqa: SLF001


def test_heartbeat_rearms_deadman_without_moving():
    board = MockArduino(seed=1)
    board.write(b"F120\n")
    board._last_command_ms -= protocol.DEADMAN_MS - 100  # noqa: SLF001  close to timeout
    board.write(b"H\n")
    assert board._deadman_tripped is False  # noqa: SLF001

    board.tick()
    assert board._motors.speed == 120  # noqa: SLF001, heartbeat doesn't change motor state


def test_obstacle_blocks_forward_and_still_arms_deadman():
    board = MockArduino(seed=1)
    board._range_cm = 10  # noqa: SLF001, within OBSTACLE_BLOCK_CM
    board.write(b"F120\n")
    lines = _read_lines(board)

    assert protocol.ALERT_OBSTACLE_TOKEN in lines
    assert board._motors.speed == 0  # noqa: SLF001, forward suppressed
    # Re-arming on a suppressed forward means holding forward against a wall
    # doesn't trip the deadman while the operator is still actively driving.
    assert board._deadman_tripped is False  # noqa: SLF001


def test_obstacle_gate_does_not_block_reverse():
    board = MockArduino(seed=1)
    board._range_cm = 10  # noqa: SLF001
    board.write(b"R120\n")
    assert board._motors.speed == 120  # noqa: SLF001
    assert board._motors.direction == protocol.CMD_REVERSE  # noqa: SLF001


def test_stop_command_resets_motors_and_arms_state():
    board = MockArduino(seed=1)
    board.write(b"F120\n")
    board.write(b"S\n")
    assert board._motors.speed == 0  # noqa: SLF001
    assert board._fw_state == protocol.FW_STATE_ARMED  # noqa: SLF001


def test_oversized_command_rejected():
    board = MockArduino(seed=1)
    board.write(b"F1234567890\n")  # exceeds MAX_COMMAND_CHARS
    lines = _read_lines(board)
    assert "ERR_LEN" in lines


def test_unknown_opcode_rejected():
    board = MockArduino(seed=1)
    board.write(b"Z\n")
    lines = _read_lines(board)
    assert "ERR_TOK" in lines


def test_non_numeric_argument_clamped_to_zero_with_warning():
    board = MockArduino(seed=1)
    board.write(b"Fxx\n")
    lines = _read_lines(board)
    assert "WARN_CLAMP" in lines
    assert board._motors.speed == 0  # noqa: SLF001


def test_pwm_argument_clamped_to_max():
    board = MockArduino(seed=1)
    board.write(b"F999\n")
    lines = _read_lines(board)
    assert "WARN_CLAMP" in lines
    assert board._motors.speed == protocol.MAX_PWM  # noqa: SLF001


def test_telemetry_emitted_at_expected_cadence():
    board = MockArduino(seed=1)
    board.read_all()  # drain the initial READY token
    time.sleep(protocol.TELEMETRY_PERIOD_MS / 1000 + 0.05)
    lines = _read_lines(board)
    assert any(protocol.parse_telemetry_line(line) is not None for line in lines)
