"""Victim marks: stored on the robot without snapshots, stamped with P1's own GPS, controller only."""

import asyncio
import logging

import pytest
from fastapi import HTTPException

from common import protocol
from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.main import VICTIM_BODY_MAX_BYTES, ControlServer, VictimMarkRequest, read_body_limited
from p1_control.victim_log import VictimLog

KEY = "test-key"
HOST = "10.0.0.5"


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
    first = victims.add("under the stairs", {"lat": 23.45, "lon": 91.2})
    second = victims.add("", {"lat": None, "lon": None})

    assert [m["id"] for m in victims.list()] == [first["id"], second["id"]]
    assert victims.list()[0]["note"] == "under the stairs"
    assert [p.name for p in (tmp_path / "victims").iterdir()] == ["victims.jsonl"]


def test_list_is_empty_before_any_mark(tmp_path, log):
    assert VictimLog(tmp_path / "victims", log).list() == []


def test_corrupt_line_is_skipped(tmp_path, log):
    victims = VictimLog(tmp_path / "victims", log)
    victims.add("one", {})
    with (tmp_path / "victims" / "victims.jsonl").open("a") as fh:
        fh.write('{"id": "half-writ\n')
    victims.add("two", {})
    assert [m["note"] for m in victims.list()] == ["one", "two"]


# --- P1 add_victim ------------------------------------------------------------


def test_mark_is_stamped_with_p1_gps_and_broadcast(server):
    set_gps(server, lat=23.4536, lon=91.2028, gps_fix=True, gps_sats=7)
    server._latest_frame = {"pan_angle": 120, "tilt_angle": 80}

    result = mark(server, VictimMarkRequest(note=" lying by the wall ", ai_score=0.87))

    assert result["lat"] == 23.4536 and result["lon"] == 91.2028
    assert result["gps_fix"] is True and result["gps_sats"] == 7
    assert result["pan_angle"] == 120 and result["tilt_angle"] == 80
    assert result["note"] == "lying by the wall"
    assert result["ai_score"] == 0.87
    assert "snapshot" not in result
    assert server.victims.list() == [result]
    assert server.broadcasts == [{"type": protocol.MSG_VICTIM_MARK, "mark": result}]


def test_without_fix_position_is_null_and_last_fix_is_kept(server):
    set_gps(server, lat=23.0, lon=91.0, gps_fix=False, gps_sats=0)
    server.gps._track = [(23.4536, 91.2028), (23.4540, 91.2030)]

    result = mark(server, VictimMarkRequest())

    assert result["lat"] is None and result["lon"] is None
    assert result["gps_fix"] is False
    assert result["last_fix"] == [23.4540, 91.2030]


@pytest.mark.parametrize("key", [None, "", "wrong"])
def test_only_the_controller_key_may_mark(server, key):
    with pytest.raises(HTTPException) as exc:
        mark(server, VictimMarkRequest(note="x"), key=key)
    assert exc.value.status_code == 403
    assert server.victims.list() == []
    assert server.broadcasts == []


def test_long_note_is_refused(server):
    with pytest.raises(HTTPException) as exc:
        mark(server, VictimMarkRequest(note="x" * 281))
    assert exc.value.status_code == 400
    assert server.victims.list() == []


# --- request size limit ---------------------------------------------------------


async def _chunks(*parts: bytes):
    for part in parts:
        yield part


def read(content_length, *parts, limit=100):
    return asyncio.run(read_body_limited(content_length, _chunks(*parts), limit))


def test_body_within_limit_is_returned():
    assert read("10", b"0123456789") == b"0123456789"
    assert read(None, b"abc", b"def") == b"abcdef"


@pytest.mark.parametrize(
    "content_length, parts",
    [
        ("101", [b"x"]),  # refused on the header alone, before reading
        (None, [b"x" * 60, b"x" * 60]),  # chunked with no length: refused while reading
        ("10", [b"x" * 200]),  # a length header that lies
    ],
    ids=["declared", "chunked", "lying-header"],
)
def test_oversized_body_is_refused(content_length, parts):
    with pytest.raises(HTTPException) as exc:
        read(content_length, *parts)
    assert exc.value.status_code == 413


def test_bad_content_length_is_refused():
    with pytest.raises(HTTPException) as exc:
        read("lots", b"x")
    assert exc.value.status_code == 400


def test_limit_fits_a_full_note():
    body = VictimMarkRequest(note="\U0001f600" * 280, ai_score=0.99).model_dump_json()
    assert len(body) <= VICTIM_BODY_MAX_BYTES


def test_a_snapshot_sent_anyway_is_not_stored(server):
    body = VictimMarkRequest.model_validate_json('{"note": "x", "snapshot_b64": "/9j/AAAA"}')
    result = mark(server, body)
    assert "snapshot" not in result
    assert [p.name for p in server.config.paths.victims_dir.iterdir()] == ["victims.jsonl"]
