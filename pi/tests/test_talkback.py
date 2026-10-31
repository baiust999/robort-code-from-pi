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
    QUESTION_OPTION_MAX,
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


CONTROLLER_HOST = "10.0.0.5"


def connect_controller(hub: ScreenHub, session_id: str, channel: FakeChannel) -> None:
    """Connect a keyed session from the host P1 says is the controller."""
    hub.set_controller_host(CONTROLLER_HOST)
    hub.grant_control(session_id, CONTROLLER_HOST)
    hub.operator_connected(session_id, channel)


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
    connect_controller(hub, "s1", a)
    connect_controller(hub, "s2", b)
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
    connect_controller(hub, "s1", a)
    connect_controller(hub, "s2", b)
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
    connect_controller(hub, "s1", FakeChannel())
    connect_controller(hub, "s2", FakeChannel())
    hub.handle_operator_message("s1", _msg(type="screen_clear"))
    hub.handle_operator_message("s2", _msg(type="floor_release"))
    assert hub.floor_holder == "s1"


# --- screen routing ---------------------------------------------------------


def test_messages_and_state_reach_screen(hub):
    op, screen = FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
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
    connect_controller(hub, "s1", FakeChannel())
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
    connect_controller(hub, "s1", op)
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
    connect_controller(hub, "s1", a)
    connect_controller(hub, "s2", b)
    assert hub.display_mode == "robot"
    assert a.of_type("talk_status")[-1]["display_mode"] == "robot"

    hub.handle_operator_message("s1", _msg(type="display_mode", mode="vnc"))
    assert hub.display_mode == "vnc"
    assert a.of_type("talk_status")[-1]["display_mode"] == "vnc"
    assert b.of_type("talk_status")[-1]["display_mode"] == "vnc"
    assert hub.health()["display_mode"] == "vnc"


def test_display_mode_does_not_need_or_claim_floor(hub):
    connect_controller(hub, "s1", FakeChannel())
    connect_controller(hub, "s2", FakeChannel())
    hub.handle_operator_message("s1", _msg(type="screen_clear"))
    assert hub.floor_holder == "s1"

    hub.handle_operator_message("s2", _msg(type="display_mode", mode="vnc"))
    assert hub.display_mode == "vnc"
    assert hub.floor_holder == "s1"


def test_local_switch_reaches_dashboards(hub):
    op = FakeChannel()
    connect_controller(hub, "s1", op)
    hub.set_display_mode("vnc", source="local")
    hub.set_display_mode("robot", source="local")
    assert [m["display_mode"] for m in op.of_type("talk_status")] == ["robot", "vnc", "robot"]
    with pytest.raises(ValueError):
        hub.set_display_mode("desktop", source="local")


# --- outbound tracks --------------------------------------------------------


# --- view-only observers ----------------------------------------------------


def test_observer_cannot_use_robot_screen(hub):
    screen, ctrl, obs = FakeChannel(), FakeChannel(), FakeChannel()
    hub.screen_attached(screen)
    connect_controller(hub, "s1", ctrl)
    hub.operator_connected("s2", obs)  # no key
    assert obs.of_type("talk_status")[-1]["can_control"] is False
    assert ctrl.of_type("talk_status")[-1]["can_control"] is True
    screen.sent.clear()

    for msg in (
        _msg(type="media_state", talking=True, video="camera"),
        _msg(type="screen_text", text="hello"),
        _msg(type="screen_clear"),
        _msg(type="display_mode", mode="vnc"),
        _msg(type="floor_release"),
    ):
        hub.handle_operator_message("s2", msg)

    assert len(obs.of_type("view_only")) == 5
    assert hub.floor_holder is None
    assert hub.display_mode == "robot"
    assert screen.sent == []

    # The controller is unaffected.
    hub.handle_operator_message("s1", _msg(type="screen_text", text="help is coming"))
    assert hub.floor_holder == "s1"


def test_observer_media_never_reaches_screen(hub):
    class FakeTrack:
        kind = "audio"

        def __init__(self) -> None:
            self.frames = [object(), object()]

        async def recv(self):
            if not self.frames:
                from aiortc.mediastreams import MediaStreamError

                raise MediaStreamError
            return self.frames.pop()

    async def run() -> None:
        hub.operator_connected("s2", FakeChannel())
        hub.attach_operator_track("s2", FakeTrack())
        await asyncio.sleep(0.01)

    asyncio.run(run())
    assert hub.next_audio_frame() is None


def test_keyed_session_that_is_not_p1_controller_is_view_only(hub):
    ctrl, other = FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", ctrl)
    # Right key, but P1 demoted this laptop (another one took over).
    hub.grant_control("s2", "10.0.0.6")
    hub.operator_connected("s2", other)
    assert other.of_type("talk_status")[-1]["can_control"] is False

    hub.handle_operator_message("s2", _msg(type="media_state", talking=True, video="none"))
    assert other.of_type("view_only")
    assert hub.floor_holder is None


def test_takeover_moves_talk_and_frees_the_floor(hub):
    screen, a, b = FakeChannel(), FakeChannel(), FakeChannel()
    hub.screen_attached(screen)
    connect_controller(hub, "s1", a)
    hub.grant_control("s2", "10.0.0.6")
    hub.operator_connected("s2", b)
    hub.handle_operator_message("s1", _msg(type="screen_text", text="stay calm"))
    assert hub.floor_holder == "s1"

    hub.set_controller_host("10.0.0.6")  # P1: laptop .6 took over
    assert hub.floor_holder is None
    assert screen.of_type("screen_clear")
    assert a.of_type("talk_status")[-1]["can_control"] is False
    assert b.of_type("talk_status")[-1]["can_control"] is True

    hub.handle_operator_message("s1", _msg(type="screen_text", text="again"))
    assert a.of_type("view_only")
    hub.handle_operator_message("s2", _msg(type="screen_text", text="hello"))
    assert hub.floor_holder == "s2"


def test_no_p1_controller_means_nobody_talks(hub):
    op = FakeChannel()
    connect_controller(hub, "s1", op)
    hub.set_controller_host(None)
    hub.handle_operator_message("s1", _msg(type="screen_text", text="hello"))
    assert op.of_type("view_only")


def test_closing_a_controller_session_revokes_it(hub):
    connect_controller(hub, "s1", FakeChannel())
    hub.operator_closed("s1")
    assert "s1" not in hub.controllers


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


# --- questions --------------------------------------------------------------


def _ask(text="Are you hurt?", options=("Yes", "No")) -> str:
    return _msg(type="question_ask", text=text, options=list(options))


def test_parse_question_trims_and_limits_options():
    msg = parse_operator_message(_ask("  Where?  ", ["  Head ", "", "Leg", "x" * 100]))
    assert msg == {"type": "question_ask", "text": "Where?", "options": ["Head", "Leg", "x" * QUESTION_OPTION_MAX]}
    assert parse_operator_message(_ask(options=["Yes"])) is None
    assert parse_operator_message(_ask(options=["Yes", " "])) is None
    assert parse_operator_message(_ask(options=["a", "b", "c", "d", "e"])) is None
    assert parse_operator_message(_ask(text=" ")) is None
    assert parse_operator_message(_msg(type="question_ask", text="Q", options="Yes,No")) is None
    assert parse_operator_message(_msg(type="question_ask", text="Q", options=["Yes", 2])) is None
    assert parse_operator_message(_msg(type="question_clear")) == {"type": "question_clear"}


def test_question_reaches_screen_and_answer_reaches_everyone(hub):
    op, viewer, screen = FakeChannel(), FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
    hub.operator_connected("s2", viewer)
    hub.screen_attached(screen)

    hub.handle_operator_message("s1", _ask())
    assert hub.floor_holder == "s1"
    shown = screen.of_type("question_show")[-1]
    assert shown == {"type": "question_show", "id": 1, "text": "Are you hurt?", "options": ["Yes", "No"]}
    assert op.of_type("question_status")[-1]["status"] == "waiting"

    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=0))
    for channel in (op, viewer):
        status = channel.of_type("question_status")[-1]
        assert (status["status"], status["answer"], status["remaining_s"]) == ("answered", 0, None)


def test_bad_late_or_repeated_answers_are_ignored(hub):
    op = FakeChannel()
    connect_controller(hub, "s1", op)
    hub.handle_operator_message("s1", _ask(options=["A", "B", "C"]))
    for qid, choice in [(2, 0), (1, 3), (1, -1), (1, True), (1, "0")]:
        hub.handle_screen_message(_msg(type="question_answer", id=qid, choice=choice))
        assert hub.question["status"] == "waiting"
    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=2))
    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=0))
    assert hub.question["answer"] == 2


def test_new_question_replaces_old_one(hub):
    screen = FakeChannel()
    connect_controller(hub, "s1", FakeChannel())
    hub.screen_attached(screen)
    hub.handle_operator_message("s1", _ask())
    hub.handle_operator_message("s1", _ask("How many with you?", ["1", "2", "More"]))
    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=0))
    assert hub.question["id"] == 2 and hub.question["status"] == "waiting"
    assert screen.of_type("question_show")[-1]["id"] == 2


def test_expiry_and_clear_take_question_off_screen(hub):
    op, screen = FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
    hub.screen_attached(screen)
    hub.handle_operator_message("s1", _ask())
    hub.expire_question(1)
    assert screen.of_type("question_hide") == [{"type": "question_hide", "id": 1}]
    assert op.of_type("question_status")[-1]["status"] == "expired"

    hub.handle_operator_message("s1", _ask())
    hub.handle_operator_message("s1", _msg(type="question_clear"))
    assert hub.question is None
    assert screen.of_type("question_hide")[-1]["id"] == 2
    assert op.of_type("question_dismissed")[-1] == {"type": "question_dismissed", "id": 2}


def test_clear_after_answer_removes_it_from_dashboards(hub):
    op, viewer = FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
    hub.operator_connected("s2", viewer)
    hub.handle_operator_message("s1", _ask())
    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=0))

    hub.handle_operator_message("s1", _msg(type="question_clear"))
    assert hub.question is None
    for channel in (op, viewer):
        assert channel.of_type("question_dismissed")[-1]["id"] == 1

    late = FakeChannel()
    hub.operator_connected("s3", late)
    assert not late.of_type("question_status")


def test_expiry_after_answer_changes_nothing(hub):
    connect_controller(hub, "s1", FakeChannel())
    hub.handle_operator_message("s1", _ask())
    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=1))
    hub.expire_question(1)
    assert (hub.question["status"], hub.question["answer"]) == ("answered", 1)


def test_releasing_floor_clears_question(hub):
    screen = FakeChannel()
    connect_controller(hub, "s1", FakeChannel())
    hub.screen_attached(screen)
    hub.handle_operator_message("s1", _ask())
    hub.operator_closed("s1")
    assert hub.question["status"] == "cleared"
    assert screen.of_type("question_hide")


def test_observer_cannot_ask_but_sees_status_on_connect(hub):
    op, viewer, screen = FakeChannel(), FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
    hub.operator_connected("s2", viewer)
    hub.screen_attached(screen)
    hub.handle_operator_message("s2", _ask())
    assert hub.question is None and not screen.of_type("question_show")

    hub.handle_operator_message("s1", _ask())
    late = FakeChannel()
    hub.operator_connected("s3", late)
    assert late.of_type("question_status")[-1]["id"] == 1


def test_reconnecting_screen_gets_waiting_question_only(hub):
    connect_controller(hub, "s1", FakeChannel())
    hub.handle_operator_message("s1", _ask())
    screen = FakeChannel()
    hub.screen_attached(screen)
    assert screen.of_type("question_show")[-1]["id"] == 1

    hub.handle_screen_message(_msg(type="question_answer", id=1, choice=0))
    again = FakeChannel()
    hub.screen_attached(again)
    assert not again.of_type("question_show")


def test_question_times_out_on_the_event_loop(monkeypatch):
    monkeypatch.setattr("p2_media.talkback.QUESTION_TIMEOUT_S", 0.05)

    async def run():
        hub = ScreenHub(EventLogger(logging.getLogger("test-talkback")))
        op = FakeChannel()
        connect_controller(hub, "s1", op)
        hub.handle_operator_message("s1", _ask())
        assert op.of_type("question_status")[-1]["remaining_s"] is not None
        await asyncio.sleep(0.1)
        return hub

    assert asyncio.run(run()).question["status"] == "expired"


# --- voice message loop -----------------------------------------------------


def _pcm(samples: int, value: int = 1000) -> bytes:
    return np.full(samples, value, np.int16).tobytes()


def _opus_webm(seconds: float, amplitude: int = 4000) -> bytes:
    """A WebM/Opus recording like the dashboard's MediaRecorder makes."""
    import io

    buf = io.BytesIO()
    with av.open(buf, "w", format="webm") as out:
        stream = out.add_stream("libopus", rate=48000, layout="mono")
        n = int(seconds * 48000)
        tone = (amplitude * np.sin(np.arange(n) / 8)).astype(np.int16)
        for start in range(0, n, 960):
            chunk = tone[start:start + 960]
            frame = av.AudioFrame.from_ndarray(chunk.reshape(1, -1), format="s16", layout="mono")
            frame.sample_rate = 48000
            frame.pts = start
            for packet in stream.encode(frame):
                out.mux(packet)
        for packet in stream.encode(None):
            out.mux(packet)
    return buf.getvalue()


def test_parse_voice_commands():
    for kind in ("voice_loop_start", "voice_loop_stop", "voice_clear"):
        assert parse_operator_message(_msg(type=kind, junk=1)) == {"type": kind}
    assert parse_operator_message(_msg(type="voice_loop")) is None


def test_decode_voice_clip_normalises_and_appends_gap():
    from p2_media.talkback import VOICE_GAP_S, decode_voice_clip

    pcm = np.frombuffer(decode_voice_clip(_opus_webm(1.0, amplitude=6000)), np.int16)
    gap = int(VOICE_GAP_S * 48000)
    assert abs(pcm.size - (48000 + gap)) < 2000  # codec padding, give or take
    assert np.abs(pcm[-gap:]).max() == 0
    assert np.abs(pcm[:-gap].astype(np.int32)).max() > 25000  # boosted towards 0.9 FS
    # A faint clip is boosted at most VOICE_MAX_GAIN times, not to full scale.
    faint = np.frombuffer(decode_voice_clip(_opus_webm(1.0, amplitude=500)), np.int16)
    assert np.abs(faint.astype(np.int32)).max() < 6000


def test_decode_voice_clip_rejects_bad_clips(monkeypatch):
    from p2_media import talkback

    with pytest.raises(ValueError):
        talkback.decode_voice_clip(b"")
    with pytest.raises(ValueError):
        talkback.decode_voice_clip(b"not audio at all" * 10)
    monkeypatch.setattr(talkback, "VOICE_MAX_S", 0.5)
    with pytest.raises(ValueError, match="longer"):
        talkback.decode_voice_clip(_opus_webm(1.0))


def test_voice_loop_needs_controller_but_not_floor(hub):
    op, viewer = FakeChannel(), FakeChannel()
    connect_controller(hub, "s1", op)
    hub.operator_connected("s2", viewer)
    hub.set_voice_clip(_pcm(10000))
    assert op.of_type("voice_status")[-1]["has_clip"] is True

    hub.handle_operator_message("s2", _msg(type="voice_loop_start"))
    assert viewer.of_type("view_only") and not hub.voice_playing

    hub.handle_operator_message("s1", _msg(type="voice_loop_start"))
    assert hub.voice_playing and hub.floor_holder is None
    assert viewer.of_type("voice_status")[-1]["playing"] is True


def test_voice_loop_survives_floor_release_and_disconnect(hub):
    op = FakeChannel()
    connect_controller(hub, "s1", op)
    hub.set_voice_clip(_pcm(10000))
    hub.handle_operator_message("s1", _msg(type="voice_loop_start"))
    hub.handle_operator_message("s1", _msg(type="screen_text", text="hi"))  # claims the floor
    hub.handle_operator_message("s1", _msg(type="floor_release"))
    hub.operator_closed("s1")
    assert hub.voice_playing

    again = FakeChannel()
    connect_controller(hub, "s3", again)
    status = again.of_type("voice_status")[-1]
    assert (status["has_clip"], status["playing"]) == (True, True)

    hub.handle_operator_message("s3", _msg(type="voice_loop_stop"))
    assert not hub.voice_playing and hub.voice_pcm is not None
    hub.handle_operator_message("s3", _msg(type="voice_clear"))
    assert hub.voice_pcm is None
    assert again.of_type("voice_status")[-1] == {
        "type": "voice_status", "id": None, "has_clip": False, "playing": False, "duration_s": None,
    }


def test_start_without_clip_is_a_noop(hub):
    op = FakeChannel()
    connect_controller(hub, "s1", op)
    hub.handle_operator_message("s1", _msg(type="voice_loop_start"))
    assert not hub.voice_playing
    assert op.of_type("voice_status")[-1]["playing"] is False


def test_next_voice_frame_wraps_around(hub):
    from p2_media.media import AUDIO_PACKET_SAMPLES

    assert hub.next_voice_frame() is None
    clip = np.arange(AUDIO_PACKET_SAMPLES + 100, dtype=np.int16)
    hub.set_voice_clip(clip.tobytes())
    assert hub.next_voice_frame() is None  # loaded but not playing
    hub.voice_playing = True
    first = hub.next_voice_frame().to_ndarray().ravel()
    second = hub.next_voice_frame().to_ndarray().ravel()
    assert first.size == second.size == AUDIO_PACKET_SAMPLES
    assert np.array_equal(first, clip[:AUDIO_PACKET_SAMPLES])
    assert np.array_equal(second[:100], clip[AUDIO_PACKET_SAMPLES:])
    assert np.array_equal(second[100:], clip[: AUDIO_PACKET_SAMPLES - 100])


def test_screen_audio_plays_loop_and_pauses_for_live_talk(hub):
    from p2_media.media import AUDIO_PACKET_SAMPLES

    # A tone, not a constant: Opus filters out DC.
    tone = (8000 * np.sin(np.arange(AUDIO_PACKET_SAMPLES * 10) / 5)).astype(np.int16)
    hub.set_voice_clip(tone.tobytes())
    hub.voice_playing = True
    decoder = av.CodecContext.create("libopus", "r")

    def loud(packet) -> bool:
        return np.abs(np.concatenate([f.to_ndarray().ravel() for f in decoder.decode(packet)])).max() > 2000

    async def run():
        track = ScreenAudioTrack(hub)
        playing = [loud(await track.recv()) for _ in range(3)]
        pos = hub._voice_pos
        hub.media_state = {"talking": True, "video": "none"}
        paused = [loud(await track.recv()) for _ in range(3)]
        assert hub._voice_pos == pos  # not advanced while talking
        hub.media_state = {"talking": False, "video": "none"}
        resumed = [loud(await track.recv()) for _ in range(2)]
        return playing, paused, resumed

    playing, paused, resumed = asyncio.run(run())
    assert all(playing[1:]) and not any(paused[1:]) and all(resumed[1:])


def test_loop_is_not_chopped_by_a_muted_mic(hub, monkeypatch):
    """A floor holder's open-but-muted mic still sends silence; while the
    loop plays that must not displace it. Right after Hold to talk is
    released, live audio still wins for VOICE_RESUME_S."""
    from p2_media.media import AUDIO_PACKET_SAMPLES

    op = FakeChannel()
    connect_controller(hub, "s1", op)
    tone = (8000 * np.sin(np.arange(AUDIO_PACKET_SAMPLES * 10) / 5)).astype(np.int16)
    hub.set_voice_clip(tone.tobytes())
    hub.handle_operator_message("s1", _msg(type="voice_loop_start"))
    hub.handle_operator_message("s1", _msg(type="media_state", talking=True, video="none"))
    hub.handle_operator_message("s1", _msg(type="media_state", talking=False, video="none"))
    assert hub.floor_holder == "s1"

    def silent_frame():
        f = av.AudioFrame.from_ndarray(np.zeros((1, 1920), np.int16), format="s16", layout="stereo")
        f.sample_rate = 48000
        return f

    decoder = av.CodecContext.create("libopus", "r")

    def loud(packet) -> bool:
        return np.abs(np.concatenate([f.to_ndarray().ravel() for f in decoder.decode(packet)])).max() > 2000

    async def run():
        track = ScreenAudioTrack(hub)
        assert hub.live_voice_active()  # within the hangover after release
        pos = hub._voice_pos
        for _ in range(7):
            hub._audio_queue.append(silent_frame())
        await track.recv()
        assert hub._voice_pos == pos  # hangover: the loop waits
        monkeypatch.setattr("p2_media.talkback.VOICE_RESUME_S", 0.0)
        out = []
        for _ in range(6):
            for _ in range(3):  # the muted mic keeps sending, 20 ms a frame
                hub._audio_queue.append(silent_frame())
            out.append(loud(await track.recv()))
        return out

    out = asyncio.run(run())
    assert all(out[1:]), out
