"""parse_telemetry_line / format_telemetry_line round-trip and rejection, Section 8.7.5."""

from common import protocol


def _valid_values() -> dict:
    return {
        "temperature_c": 24.5,
        "humidity_pct": 55.0,
        "gas_ppm": 3,
        "motion": 0,
        "range_cm": 180,
        "pan_angle": 90,
        "tilt_angle": 45,
        "fw_state": protocol.FW_STATE_ARMED,
        "uptime_ms": 123456,
    }


def test_round_trip():
    values = _valid_values()
    line = protocol.format_telemetry_line(values)
    parsed = protocol.parse_telemetry_line(line)
    assert parsed == values


def test_wrong_field_count_rejected():
    line = "24.5,55.0,3,0,180,90,45,1"  # missing uptime_ms
    assert protocol.parse_telemetry_line(line) is None


def test_extra_field_rejected():
    line = protocol.format_telemetry_line(_valid_values()) + ",99"
    assert protocol.parse_telemetry_line(line) is None


def test_non_numeric_field_rejected():
    line = "abc,55.0,3,0,180,90,45,1,123456"
    assert protocol.parse_telemetry_line(line) is None


def test_out_of_range_field_rejected():
    values = _valid_values()
    values["fw_state"] = 99  # valid range is 1-3
    line = protocol.format_telemetry_line(values)
    assert protocol.parse_telemetry_line(line) is None


def test_empty_line_rejected():
    assert protocol.parse_telemetry_line("") is None
    assert protocol.parse_telemetry_line("   ") is None


def test_oversized_line_rejected():
    line = "1" * (protocol.TELEMETRY_MAX_CHARS + 1)
    assert protocol.parse_telemetry_line(line) is None


def test_trailing_newline_and_whitespace_tolerated():
    line = protocol.format_telemetry_line(_valid_values()) + "\r\n"
    assert protocol.parse_telemetry_line(line) == _valid_values()
