"""Victim marks: stored on the robot, stamped with P1's own GPS, controller only."""

import asyncio
import base64
import logging

import pytest
from fastapi import HTTPException

from common import protocol
from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.main import ControlServer, VictimMarkRequest
from p1_control.victim_log import SNAPSHOT_MAX_BYTES, VictimLog

KEY = "test-key"
HOST = "10.0.0.5"
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


@pytest.fixture
def log() -> EventLogger:
    return EventLogger(logging.getLogger("test-victims"))


@pytest.fixture
def server(monkeypatch, tmp_path) -> ControlServer:
    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    monkeypatch.setenv("CONTROLLER_KEY", KEY)
    srv = ControlServer(P1Config.from_env(), EventLogger(logging.getLogger("test-victims")))
    srv.broadcasts = []

    async def broadcast(message):
        srv.broadcasts.append(message)

    srv.hub.broadcast = broadcast
    return srv


def mark(server, body: VictimMarkRequest, key: str | None = KEY) -> dict:
    return asyncio.run(server.add_victim(HOST, key, body))


def set_gps(server, **state) -> None:
    server.gps._state.update(state)


# --- VictimLog ----------------------------------------------------------------


def test_add_and_list_round_trip(tmp_path, log):
    victims = VictimLog(tmp_path / "victims", log)
    first = victims.add("under the stairs", JPEG, {"lat": 23.45, "lon": 91.2})
    second = victims.add("", None, {"lat": None, "lon": None})

    assert [m["id"] for m in victims.list()] == [first["id"], second["id"]]
    assert victims.list()[0]["note"] == "under the stairs"
    assert first["snapshot"] is True and second["snapshot"] is False
    assert victims.snapshot_path(first["id"]).read_bytes() == JPEG
    assert victims.snapshot_path(second["id"]) is None


def test_list_is_empty_before_any_mark(tmp_path, log):
    assert VictimLog(tmp_path / "victims", log).list() == []


def test_corrupt_line_is_skipped(tmp_path, log):
    victims = VictimLog(tmp_path / "victims", log)
    victims.add("one", None, {})
    with (tmp_path / "victims" / "victims.jsonl").open("a") as fh:
        fh.write('{"id": "half-writ\n')
    victims.add("two", None, {})
    assert [m["note"] for m in victims.list()] == ["one", "two"]


@pytest.mark.parametrize("bad", ["../etc/passwd", "x", "20261029-101010-zzzz", "20261029-101010-abcd/.."])
def test_bad_snapshot_ids_are_refused(tmp_path, log, bad):
    assert VictimLog(tmp_path / "victims", log).snapshot_path(bad) is None


# --- P1 add_victim ------------------------------------------------------------


def test_mark_is_stamped_with_p1_gps_and_broadcast(server):
    set_gps(server, lat=23.4536, lon=91.2028, gps_fix=True, gps_sats=7)
    server._latest_frame = {"pan_angle": 120, "tilt_angle": 80}

    result = mark(server, VictimMarkRequest(note=" lying by the wall ", ai_score=0.87, snapshot_b64=b64(JPEG)))

    assert result["lat"] == 23.4536 and result["lon"] == 91.2028
    assert result["gps_fix"] is True and result["gps_sats"] == 7
    assert result["pan_angle"] == 120 and result["tilt_angle"] == 80
    assert result["note"] == "lying by the wall"
    assert result["ai_score"] == 0.87
    assert server.victims.snapshot_path(result["id"]).read_bytes() == JPEG
    assert server.victims.list() == [result]
    assert server.broadcasts == [{"type": protocol.MSG_VICTIM_MARK, "mark": result}]


def test_without_fix_position_is_null_and_last_fix_is_kept(server):
    set_gps(server, lat=23.0, lon=91.0, gps_fix=False, gps_sats=0)
    server.gps._track = [(23.4536, 91.2028), (23.4540, 91.2030)]

    result = mark(server, VictimMarkRequest())

    assert result["lat"] is None and result["lon"] is None
    assert result["gps_fix"] is False
    assert result["last_fix"] == [23.4540, 91.2030]
    assert result["snapshot"] is False


@pytest.mark.parametrize("key", [None, "", "wrong"])
def test_only_the_controller_key_may_mark(server, key):
    with pytest.raises(HTTPException) as exc:
        mark(server, VictimMarkRequest(note="x"), key=key)
    assert exc.value.status_code == 403
    assert server.victims.list() == []
    assert server.broadcasts == []


@pytest.mark.parametrize(
    "body",
    [
        VictimMarkRequest(snapshot_b64=b64(b"GIF89a....")),
        VictimMarkRequest(snapshot_b64="not base64!!"),
        VictimMarkRequest(snapshot_b64=b64(JPEG + b"\x00" * SNAPSHOT_MAX_BYTES)),
        VictimMarkRequest(note="x" * 281),
    ],
    ids=["not-jpeg", "not-base64", "too-big", "long-note"],
)
def test_bad_requests_are_refused(server, body):
    with pytest.raises(HTTPException) as exc:
        mark(server, body)
    assert exc.value.status_code == 400
    assert server.victims.list() == []
