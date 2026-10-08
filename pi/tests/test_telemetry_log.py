"""Telemetry CSV sink: the header survives a logrotate copytruncate.

deploy/logrotate/robot rotates telemetry.log with copytruncate, which empties
the file while P1 keeps writing through the same open handle. Without a
re-emitted header the live log would carry bare rows until the next restart,
and a reader would have to guess the column order.
"""

from pathlib import Path

from common import protocol
from p1_control.telemetry_log import CSV_COLUMNS, TelemetryLog

SNAPSHOT = {
    "seq": 7,
    "temperature_c": 31.0,
    "humidity_pct": 79.0,
    "gas_ppm": 46,
    "range_cm": 90,
    "pan_angle": 90,
    "tilt_angle": 90,
    "fw_state": protocol.FW_STATE_ARMED,
    "uptime_ms": 519604,
    "lat": None,
    "lon": None,
    "gps_fix": False,
    "gps_sats": 0,
    "serial_ok": True,
    "ws_clients": 1,
    "turn_status": "unavailable",
}


def make_log(tmp_path: Path) -> tuple[TelemetryLog, Path]:
    path = tmp_path / "telemetry.log"
    log = TelemetryLog(path, protocol.DEFAULT_THRESHOLDS, period_ms=0)
    log.open()
    return log, path


def header() -> str:
    return ",".join(CSV_COLUMNS)


def test_new_log_starts_with_the_header(tmp_path):
    log, path = make_log(tmp_path)
    log.write(SNAPSHOT)
    log.close()

    lines = path.read_text().splitlines()
    assert lines[0] == header()
    assert len(lines) == 2


def test_header_is_not_repeated_on_reopen(tmp_path):
    log, path = make_log(tmp_path)
    log.write(SNAPSHOT)
    log.close()

    reopened = TelemetryLog(path, protocol.DEFAULT_THRESHOLDS, period_ms=0)
    reopened.open()
    reopened.write(SNAPSHOT)
    reopened.close()

    lines = path.read_text().splitlines()
    assert lines.count(header()) == 1
    assert len(lines) == 3


def test_copytruncate_rotation_re_emits_the_header(tmp_path):
    log, path = make_log(tmp_path)
    log.write(SNAPSHOT)

    # What logrotate's copytruncate does: the content is copied elsewhere and
    # the original truncated to zero, while this handle stays open.
    rotated = tmp_path / "telemetry.log.1"
    rotated.write_text(path.read_text())
    with path.open("r+") as handle:
        handle.truncate(0)
    assert path.stat().st_size == 0

    log.write(SNAPSHOT)
    log.close()

    lines = path.read_text().splitlines()
    assert lines[0] == header(), "rotated log must describe its own columns"
    assert len(lines) == 2
    # The archived copy keeps its own header and the pre-rotation row.
    assert rotated.read_text().splitlines()[0] == header()


def test_rows_stay_aligned_with_the_header_after_rotation(tmp_path):
    log, path = make_log(tmp_path)
    log.write(SNAPSHOT)
    with path.open("r+") as handle:
        handle.truncate(0)
    log.write(SNAPSHOT)
    log.close()

    columns, row = path.read_text().splitlines()
    assert len(row.split(",")) == len(columns.split(","))
    fields = dict(zip(columns.split(","), row.split(",")))
    assert fields["seq"] == "7"
    assert fields["serial_ok"] == "1"
    assert fields["lat"] == ""


def test_disabled_log_writes_nothing(tmp_path):
    path = tmp_path / "telemetry.log"
    log = TelemetryLog(path, protocol.DEFAULT_THRESHOLDS, period_ms=0, enabled=False)
    log.open()
    log.write(SNAPSHOT)
    log.close()
    assert not path.exists()
