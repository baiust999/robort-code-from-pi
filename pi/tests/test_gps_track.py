"""GPS track: drift around a stationary robot is ignored, real movement is kept."""

import logging

from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.gps_reader import MIN_TRACK_STEP_M, GPSReader, distance_m

START = (23.4536, 91.2028)


def make_reader(monkeypatch, tmp_path) -> GPSReader:
    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    return GPSReader(P1Config.from_env(), EventLogger(logging.getLogger("test-gps")))


def fix(reader: GPSReader, lat: float, lon: float) -> None:
    reader._publish({"lat": lat, "lon": lon, "gps_fix": True})


def test_distance_m():
    # 0.0001 degrees of latitude is about 11 m anywhere.
    assert abs(distance_m(START, (START[0] + 0.0001, START[1])) - 11.1) < 0.1
    assert distance_m(START, START) == 0.0


def test_drift_while_stationary_adds_no_points(monkeypatch, tmp_path):
    reader = make_reader(monkeypatch, tmp_path)
    fix(reader, *START)
    # Jitter of up to ~8 m in every direction, as a 4-satellite fix does.
    for dlat, dlon in [(0.00005, 0), (-0.00007, 0.00003), (0, -0.00006), (0.00004, 0.00004)]:
        fix(reader, START[0] + dlat, START[1] + dlon)
    assert reader.track_points() == [START]


def test_driving_adds_a_point_per_step(monkeypatch, tmp_path):
    reader = make_reader(monkeypatch, tmp_path)
    # Drive north about 3 m per fix for 100 m.
    for i in range(34):
        fix(reader, START[0] + i * 0.000027, START[1])
    points = reader.track_points()
    assert 8 <= len(points) <= 11
    steps = [distance_m(a, b) for a, b in zip(points, points[1:])]
    assert all(step >= MIN_TRACK_STEP_M for step in steps)


def test_no_fix_adds_no_points(monkeypatch, tmp_path):
    reader = make_reader(monkeypatch, tmp_path)
    reader._publish({"lat": START[0], "lon": START[1], "gps_fix": False})
    assert reader.track_points() == []
