"""Offline map mount: /maps is served only when the map folder exists."""

import logging

from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.main import ControlServer, create_app


def make_app(monkeypatch, tmp_path, map_dir):
    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    monkeypatch.setenv("MAP_DIR", str(map_dir))
    dashboard = tmp_path / "dist"
    dashboard.mkdir()
    monkeypatch.setenv("DASHBOARD_DIR", str(dashboard))
    config = P1Config.from_env()
    return config, create_app(ControlServer(config, EventLogger(logging.getLogger("test-map"))))


def paths(app) -> list[str]:
    return [getattr(route, "path", "") for route in app.routes]


def test_map_folder_is_served_before_dashboard(monkeypatch, tmp_path):
    maps = tmp_path / "maps"
    maps.mkdir()
    (maps / "area.pmtiles").write_bytes(b"PMTiles")
    config, app = make_app(monkeypatch, tmp_path, maps)
    assert config.map_dir == maps
    routes = paths(app)
    # The dashboard mounted at "/" would swallow /maps if it came first.
    assert routes.index("/maps") < routes.index("")


def test_missing_map_folder_changes_nothing(monkeypatch, tmp_path):
    config, app = make_app(monkeypatch, tmp_path, tmp_path / "no-such-dir")
    assert config.map_dir is None
    assert "/maps" not in paths(app)
