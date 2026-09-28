"""Controller key, lockout and observer restrictions."""

import asyncio
import logging

import pytest

from common import access, protocol
from common.config import P1Config
from common.logging_setup import EventLogger
from p1_control.main import ControlServer
from p1_control.websocket_hub import Client

KEY = "test-key"


# --- KeyGate ----------------------------------------------------------------


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def gate(clock) -> access.KeyGate:
    return access.KeyGate(KEY, max_failures=5, lockout_s=300, clock=clock)


def test_right_key_passes_and_missing_key_is_no_guess(gate):
    assert gate.check("10.0.0.5", KEY) == access.OK
    for _ in range(10):
        assert gate.check("10.0.0.5", None) == access.NO_KEY
        assert gate.check("10.0.0.5", "") == access.NO_KEY
    assert gate.check("10.0.0.5", KEY) == access.OK


def test_wrong_key(gate):
    assert gate.check("10.0.0.5", "123") == access.BAD_KEY
    assert gate.check("10.0.0.5", "test-key2") == access.BAD_KEY


def test_fifth_wrong_key_locks_out_even_the_right_key(gate, clock):
    for _ in range(4):
        assert gate.check("10.0.0.5", "000") == access.BAD_KEY
    assert gate.check("10.0.0.5", "001") == access.LOCKED
    assert gate.check("10.0.0.5", KEY) == access.LOCKED
    assert gate.retry_after("10.0.0.5") == 300
    # Joining without a key is still allowed (as an observer).
    assert gate.check("10.0.0.5", None) == access.NO_KEY

    # Other hosts are unaffected.
    assert gate.check("10.0.0.6", KEY) == access.OK

    clock.now += 299
    assert gate.check("10.0.0.5", KEY) == access.LOCKED
    clock.now += 1
    assert gate.check("10.0.0.5", KEY) == access.OK
    assert gate.retry_after("10.0.0.5") == 0


def test_success_resets_the_failure_count(gate):
    for _ in range(4):
        gate.check("10.0.0.5", "000")
    assert gate.check("10.0.0.5", KEY) == access.OK
    for _ in range(4):
        assert gate.check("10.0.0.5", "000") == access.BAD_KEY


def test_old_failures_expire(gate, clock):
    for _ in range(4):
        gate.check("10.0.0.5", "000")
    clock.now += 301
    assert gate.check("10.0.0.5", "000") == access.BAD_KEY


def test_no_configured_key_lets_nobody_control():
    gate = access.KeyGate("")
    assert not gate.enabled
    assert gate.check("10.0.0.5", "") == access.NO_KEY
    assert gate.check("10.0.0.5", "anything") == access.DISABLED


# --- P1 roles ---------------------------------------------------------------


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_json(self, message: dict) -> None:
        self.sent.append(message)


class FakeSerial:
    def __init__(self) -> None:
        self.sent: list[tuple] = []
        self.stops = 0

    async def send(self, opcode, argument) -> None:
        self.sent.append((opcode, argument))

    async def send_stop(self) -> None:
        self.stops += 1


@pytest.fixture
def server(monkeypatch, tmp_path) -> ControlServer:
    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    monkeypatch.setenv("CONTROLLER_KEY", KEY)
    srv = ControlServer(P1Config.from_env(), EventLogger(logging.getLogger("test-access")))
    srv.serial = FakeSerial()
    return srv


def connect(server: ControlServer, cid: str, host: str) -> Client:
    client = Client(id=cid, socket=FakeSocket(), host=host)
    server.hub._clients[cid] = client
    return client


def hello(server: ControlServer, client: Client, key: str | None) -> dict:
    message = {"type": protocol.MSG_HELLO, "role": protocol.ROLE_CONTROLLER}
    if key is not None:
        message["key"] = key
    asyncio.run(server.handle_client_message(client, message))
    return client.socket.sent[-1]


def send(server: ControlServer, client: Client, message: dict) -> None:
    asyncio.run(server.handle_client_message(client, message))


def test_right_key_becomes_controller(server):
    c1 = connect(server, "c1", "10.0.0.5")
    ack = hello(server, c1, KEY)
    assert ack["role"] == protocol.ROLE_CONTROLLER
    assert ack["auth"] == access.OK
    assert server.hub.controller_id == "c1"


@pytest.mark.parametrize("key", [None, "", "123"])
def test_no_or_wrong_key_is_observer(server, key):
    c1 = connect(server, "c1", "10.0.0.5")
    ack = hello(server, c1, key)
    assert ack["role"] == protocol.ROLE_OBSERVER
    assert server.hub.controller_id is None


def test_first_connection_without_key_does_not_block_operator(server):
    stranger = connect(server, "c1", "10.0.0.7")
    hello(server, stranger, None)
    operator = connect(server, "c2", "10.0.0.5")
    assert hello(server, operator, KEY)["role"] == protocol.ROLE_CONTROLLER


def test_takeover_demotes_and_tells_old_controller_and_stops(server):
    old = connect(server, "c1", "10.0.0.5")
    hello(server, old, KEY)
    new = connect(server, "c2", "10.0.0.6")
    assert hello(server, new, KEY)["role"] == protocol.ROLE_CONTROLLER

    assert server.hub.controller_id == "c2"
    assert old.role == protocol.ROLE_OBSERVER
    assert old.socket.sent[-1] == {
        "type": protocol.MSG_ROLE,
        "role": protocol.ROLE_OBSERVER,
        "reason": "taken_over",
    }
    assert server.serial.stops == 1

    # The demoted client's commands are now refused.
    send(server, old, {"type": protocol.MSG_MOTOR, "dir": "F", "speed": 100, "seq": 1})
    assert old.socket.sent[-1]["type"] == protocol.MSG_ERROR
    assert server.serial.sent == []


def test_lockout_keeps_guesser_an_observer(server):
    c1 = connect(server, "c1", "10.0.0.9")
    for guess in ("000", "001", "002", "003"):
        assert hello(server, c1, guess)["auth"] == access.BAD_KEY
    ack = hello(server, c1, "004")
    assert ack["auth"] == access.LOCKED
    assert ack["retry_after_s"] == 300
    ack = hello(server, c1, KEY)
    assert ack["auth"] == access.LOCKED
    assert ack["role"] == protocol.ROLE_OBSERVER


@pytest.mark.parametrize(
    "message",
    [
        {"type": protocol.MSG_MOTOR, "dir": "F", "speed": 100, "seq": 1},
        {"type": protocol.MSG_SERVO, "axis": "pan", "angle": 90, "seq": 1},
        {"type": protocol.MSG_STOP_ALL},
    ],
)
def test_observer_commands_rejected_including_stop(server, message):
    obs = connect(server, "c1", "10.0.0.5")
    hello(server, obs, None)
    send(server, obs, message)
    assert obs.socket.sent[-1]["type"] == protocol.MSG_ERROR
    assert server.serial.sent == []
    assert server.serial.stops == 0


def test_observer_heartbeat_dropped_quietly(server):
    obs = connect(server, "c1", "10.0.0.5")
    hello(server, obs, None)
    before = len(obs.socket.sent)
    send(server, obs, {"type": protocol.MSG_HEARTBEAT})
    assert len(obs.socket.sent) == before
    assert server.serial.sent == []


def test_controller_stop_all_still_works(server):
    ctrl = connect(server, "c1", "10.0.0.5")
    hello(server, ctrl, KEY)
    send(server, ctrl, {"type": protocol.MSG_STOP_ALL})
    assert server.serial.sent  # reached the Arduino


def test_unset_key_means_nobody_controls(server, monkeypatch):
    server.gate = access.KeyGate("")
    c1 = connect(server, "c1", "10.0.0.5")
    ack = hello(server, c1, KEY)
    assert ack["role"] == protocol.ROLE_OBSERVER
    assert ack["auth"] == access.DISABLED


# --- P2 offer ---------------------------------------------------------------


class FakeRequest:
    def __init__(self, host: str) -> None:
        self.client = type("Addr", (), {"host": host})()


@pytest.fixture
def media(monkeypatch, tmp_path):
    from common.config import P2Config
    from p2_media.main import MediaServer, create_app

    monkeypatch.setenv("ROBOT_ROOT", str(tmp_path))
    monkeypatch.setenv("MOCK_HARDWARE", "1")
    monkeypatch.setenv("CONTROLLER_KEY", KEY)
    srv = MediaServer(P2Config.from_env(), EventLogger(logging.getLogger("test-access-p2")))
    granted: list[bool] = []

    async def fake_offer(sdp, sdp_type, *, controller, host):
        granted.append(controller)
        return type("Answer", (), {"sdp": "answer", "type": "answer"})()

    srv.offer = fake_offer
    app = create_app(srv)
    endpoint = next(r.endpoint for r in app.routes if getattr(r, "path", "") == "/webrtc/offer")
    return endpoint, granted


def offer(media, host: str, key: str | None):
    from p2_media.main import OfferRequest

    endpoint, _ = media
    return asyncio.run(endpoint(OfferRequest(sdp="x", type="offer", key=key), FakeRequest(host)))


def test_p2_offer_with_key_is_controller(media):
    answer = offer(media, "10.0.0.5", KEY)
    assert answer.role == protocol.ROLE_CONTROLLER
    assert answer.auth == access.OK
    assert media[1] == [True]


@pytest.mark.parametrize("key", [None, "123"])
def test_p2_offer_without_key_is_view_only(media, key):
    answer = offer(media, "10.0.0.5", key)
    assert answer.role == protocol.ROLE_OBSERVER
    assert media[1] == [False]  # still negotiated: observers watch the video


def test_p2_offer_lockout(media):
    for guess in ("000", "001", "002", "003", "004"):
        answer = offer(media, "10.0.0.9", guess)
    assert answer.auth == access.LOCKED
    assert answer.retry_after_s == 300
    assert offer(media, "10.0.0.9", KEY).role == protocol.ROLE_OBSERVER


def test_p1_reports_controller_host(server):
    c1 = connect(server, "c1", "10.0.0.5")
    assert server.hub.controller_host is None
    hello(server, c1, KEY)
    assert server.hub.controller_host == "10.0.0.5"
    c2 = connect(server, "c2", "10.0.0.6")
    hello(server, c2, KEY)
    assert server.hub.controller_host == "10.0.0.6"
    server.hub.unregister(c2)
    assert server.hub.controller_host is None


def test_p1_controller_endpoint_is_local_only(server):
    from fastapi import HTTPException

    from p1_control.main import create_app

    app = create_app(server)
    endpoint = next(r.endpoint for r in app.routes if getattr(r, "path", "") == "/api/controller")
    c1 = connect(server, "c1", "10.0.0.5")
    hello(server, c1, KEY)
    assert asyncio.run(endpoint(FakeRequest("127.0.0.1"))) == {"host": "10.0.0.5"}
    with pytest.raises(HTTPException):
        asyncio.run(endpoint(FakeRequest("10.0.0.7")))
