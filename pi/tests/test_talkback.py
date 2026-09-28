"""Talk-to-victim floor control and message routing, Section 16."""

import asyncio
import json
import logging
import time

import av
import numpy as np

import pytest

from common.logging_setup import EventLogger
from p2_media.talkback import (
    SCREEN_TEXT_MAX,
    ScreenAudioTrack,
    ScreenHub,
    ScreenVideoTrack,
    parse_operator_message,
)


class FakeChannel:
    def __init__(self) -> None:
        self.readyState = "open"
        self.sent: list[dict] = []

    def send(self, data: str) -> None:
        self.sent.append(json.loads(data))

    def of_type(self, kind: str) -> list[dict]:
        return [m for m in self.sent if m["type"] == kind]


@pytest.fixture
def hub() -> ScreenHub:
    return ScreenHub(EventLogger(logging.getLogger("test-talkback")))


def _msg(**fields) -> str:
    return json.dumps(fields)


# --- parse_operator_message -------------------------------------------------


def test_parse_rejects_malformed():
    assert parse_operator_message("not json") is None
    assert parse_operator_message("[1, 2]") is None
    assert parse_operator_message(b"{}") is None
    assert parse_operator_message(_msg(type="unknown")) is None
    assert parse_operator_message(_msg(type="screen_text", text=5)) is None
    assert parse_operator_message(_msg(type="screen_text", text="   ")) is None
    assert parse_operator_message(_msg(type="media_state", video="webcam")) is None


def test_parse_trims_and_caps_text():
    msg = parse_operator_message(_msg(type="screen_text", text="  " + "x" * 500 + "  ", ts=7))
    assert msg == {"type": "screen_text", "text": "x" * SCREEN_TEXT_MAX, "ts": 7}


def test_parse_media_state_defaults():
    assert parse_operator_message(_msg(type="media_state")) == {
        "type": "media_state",
        "talking": False,
        "video": "none",
    }


# --- floor control ----------------------------------------------------------


def test_first_sender_claims_floor_and_others_are_denied(hub):
    a, b = FakeChannel(), FakeChannel()
    hub.operator_connected("s1", a)
    hub.operator_connected("s2", b)
    assert a.of_type("talk_status")[-1]["floor"] == "free"

    hub.handle_operator_message("s1", _msg(type="media_state", talking=True, video="none"))
    assert hub.floor_holder == "s1"
    assert a.of_type("talk_status")[-1]["floor"] == "you"
    assert b.of_type("talk_status")[-1]["floor"] == "other"

    hub.handle_operator_message("s2", _msg(type="screen_text", text="hello"))
    assert hub.floor_holder == "s1"
    assert b.of_type("floor_denied")
    assert hub.current_text is None


def test_release_and_disconnect_free_the_floor(hub):
    a, b, screen = FakeChannel(), FakeChannel(), FakeChannel()
    hub.operator_connected("s1", a)
    hub.operator_connected("s2", b)
    hub.screen_attached(screen)

    hub.handle_operator_message("s1", _msg(type="screen_text", text="stay calm"))
    hub.handle_operator_message("s1", _msg(type="floor_release"))
    assert hub.floor_holder is None
    assert hub.current_text is None
    assert screen.sent[-1]["type"] == "screen_state" and screen.sent[-1]["operator"] is False

    hub.handle_operator_message("s2", _msg(type="media_state", video="camera"))
    assert hub.floor_holder == "s2"
    hub.operator_closed("s2")
    assert hub.floor_holder is None
    assert a.of_type("talk_status")[-1]["floor"] == "free"


def test_release_by_non_holder_is_ignored(hub):
    hub.operator_connected("s1", FakeChannel())
    hub.operator_connected("s2", FakeChannel())
    hub.handle_operator_message("s1", _msg(type="screen_clear"))
    hub.handle_operator_message("s2", _msg(type="floor_release"))
    assert hub.floor_holder == "s1"


# --- screen routing ---------------------------------------------------------


def test_messages_and_state_reach_screen(hub):
    op, screen = FakeChannel(), FakeChannel()
    hub.operator_connected("s1", op)
    hub.screen_attached(screen)
    assert op.of_type("talk_status")[-1]["screen_online"] is True

    hub.handle_operator_message("s1", _msg(type="media_state", talking=True, video="image"))
    assert screen.of_type("screen_state")[-1] == {
        "type": "screen_state",
        "operator": True,
        "talking": True,
        "video": "image",
    }

    hub.handle_operator_message("s1", _msg(type="screen_text", text="Help is coming", ts=42))
    assert screen.of_type("screen_text")[-1]["text"] == "Help is coming"

    hub.handle_screen_message(_msg(type="screen_ack", ts=42))
    assert op.of_type("screen_ack") == [{"type": "screen_ack", "ts": 42}]


def test_reconnecting_screen_gets_current_text(hub):
    hub.operator_connected("s1", FakeChannel())
    hub.handle_operator_message("s1", _msg(type="screen_text", text="We see you"))
    screen = FakeChannel()
    hub.screen_attached(screen)
    assert screen.of_type("screen_text")[-1]["text"] == "We see you"


def test_stale_screen_close_does_not_detach_new_screen(hub):
    old, new = FakeChannel(), FakeChannel()
    hub.screen_attached(old)
    hub.screen_attached(new)
    hub.screen_detached(old)
    assert hub.screen_connected is True
    hub.screen_detached(new)
    assert hub.screen_connected is False


def test_closed_channel_is_not_written(hub):
    op = FakeChannel()
    op.readyState = "closing"
    hub.operator_connected("s1", op)
    assert op.sent == []


# --- display mode -----------------------------------------------------------


def test_parse_display_mode():
    assert parse_operator_message(_msg(type="display_mode", mode="vnc")) == {
        "type": "display_mode",
        "mode": "vnc",
    }
    assert parse_operator_message(_msg(type="display_mode", mode="desktop")) is None
    assert parse_operator_message(_msg(type="display_mode")) is None


def test_display_mode_starts_robot_and_is_broadcast(hub):
    a, b = FakeChannel(), FakeChannel()
    hub.operator_connected("s1", a)
    hub.operator_connected("s2", b)
    assert hub.display_mode == "robot"
    assert a.of_type("talk_status")[-1]["display_mode"] == "robot"

    hub.handle_operator_message("s1", _msg(type="display_mode", mode="vnc"))
    assert hub.display_mode == "vnc"
    assert a.of_type("talk_status")[-1]["display_mode"] == "vnc"
    assert b.of_type("talk_status")[-1]["display_mode"] == "vnc"
    assert hub.health()["display_mode"] == "vnc"


def test_display_mode_does_not_need_or_claim_floor(hub):
    hub.operator_connected("s1", FakeChannel())
    hub.operator_connected("s2", FakeChannel())
    hub.handle_operator_message("s1", _msg(type="screen_clear"))
    assert hub.floor_holder == "s1"

    hub.handle_operator_message("s2", _msg(type="display_mode", mode="vnc"))
    assert hub.display_mode == "vnc"
    assert hub.floor_holder == "s1"


def test_local_switch_reaches_dashboards(hub):
    op = FakeChannel()
    hub.operator_connected("s1", op)
    hub.set_display_mode("vnc", source="local")
    hub.set_display_mode("robot", source="local")
    assert [m["display_mode"] for m in op.of_type("talk_status")] == ["robot", "vnc", "robot"]
    with pytest.raises(ValueError):
        hub.set_display_mode("desktop", source="local")


# --- outbound tracks --------------------------------------------------------


def test_idle_tracks_produce_black_video_and_silence(hub, monkeypatch):
    monkeypatch.setattr("p2_media.talkback.VIDEO_REPEAT_S", 0.01)

    async def run():
        video = await ScreenVideoTrack(hub).recv()
        audio_track = ScreenAudioTrack(hub)
        a1 = await audio_track.recv()
        a2 = await audio_track.recv()
        return video, a1, a2

    video, a1, a2 = asyncio.run(run())
    assert (video.width, video.height) == (640, 480)
    # Audio leaves as one 60 ms Opus packet at a time.
    assert a2.pts - a1.pts == 2880
    decoder = av.CodecContext.create("libopus", "r")
    decoded = [f for p in (a1, a2) for f in decoder.decode(p)]
    assert sum(f.samples for f in decoded) == 2 * 2880
    assert abs(decoded[-1].to_ndarray()).max() < 50  # silence, give or take codec noise


def test_screen_audio_carries_operator_voice_and_never_bursts(hub, monkeypatch):
    """Operator frames come out intact; a late track resets its clock rather than bursting."""
    hub.floor_holder = "s1"
    tone = (8000 * np.sin(np.arange(960) / 5)).astype(np.int16)

    def operator_frame():
        f = av.AudioFrame.from_ndarray(np.repeat(tone, 2).reshape(1, -1), format="s16", layout="stereo")
        f.sample_rate = 48000
        return f

    async def run():
        track = ScreenAudioTrack(hub)
        # 140 ms: enough to fill the 120 ms cushion.
        for _ in range(7):
            hub._audio_queue.append(operator_frame())
        voiced = await track.recv()
        # Simulate the event loop stalling for a second.
        track._start -= 1.0
        t = time.monotonic()
        await track.recv()
        await track.recv()
        return voiced, time.monotonic() - t

    voiced, elapsed = asyncio.run(run())
    decoder = av.CodecContext.create("libopus", "r")
    samples = np.concatenate([f.to_ndarray().ravel() for f in decoder.decode(voiced)])
    assert np.abs(samples).max() > 2000  # the tone, not silence
    # After the stall the next packet goes out at once, but the one after
    # waits its 60 ms instead of following in a burst.
    assert elapsed >= 0.05
