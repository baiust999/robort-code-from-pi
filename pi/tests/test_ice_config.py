"""ICE configuration served by P1, Section 8.8.1.1.

The local-network mode evaluated in this work needs no STUN server: both peers
sit on one subnet and offer host candidates only. STUN_URL is therefore
optional, and an unset STUN_URL must not advertise a server that does not
exist.
"""

import logging

import pytest
from fastapi import HTTPException

from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.main import ICE_RATE_LIMIT, ControlServer


def build(monkeypatch, tmp_path, stun: str | None) -> ControlServer:
    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    if stun is None:
        monkeypatch.delenv("STUN_URL", raising=False)
    else:
        monkeypatch.setenv("STUN_URL", stun)
    return ControlServer(P1Config.from_env(), EventLogger(logging.getLogger("test-ice")))


def test_no_stun_configured_advertises_no_ice_server(monkeypatch, tmp_path) -> None:
    server = build(monkeypatch, tmp_path, None)
    assert server.config.stun_url == ""
    body = server.ice_config("10.0.0.1")
    assert body["iceServers"] == []
    assert body["stun"] == ""


def test_configured_stun_is_advertised(monkeypatch, tmp_path) -> None:
    server = build(monkeypatch, tmp_path, "stun:stun.example.org:3478")
    body = server.ice_config("10.0.0.1")
    assert body["stun"] == "stun:stun.example.org:3478"
    assert body["iceServers"] == [{"urls": "stun:stun.example.org:3478"}]


@pytest.mark.parametrize("stun", [None, "stun:stun.example.org:3478"])
def test_no_turn_relay_in_local_mode(monkeypatch, tmp_path, stun) -> None:
    body = build(monkeypatch, tmp_path, stun).ice_config("10.0.0.1")
    assert body["turn"] is None
    assert body["policy"] == "all"


def test_rate_limited_per_client(monkeypatch, tmp_path) -> None:
    server = build(monkeypatch, tmp_path, None)
    for _ in range(ICE_RATE_LIMIT):
        server.ice_config("10.0.0.1")
    with pytest.raises(HTTPException) as excinfo:
        server.ice_config("10.0.0.1")
    assert excinfo.value.status_code == 429
    # A different client keeps its own budget.
    assert server.ice_config("10.0.0.2")["iceServers"] == []
