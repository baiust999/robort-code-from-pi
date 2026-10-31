"""Operator-to-victim path ("talk-to-victim"), methodology Section 16.

The operator's dashboard sends its microphone (push-to-talk), an optional
video source (laptop camera, a still image, or a shared screen), short
text messages and questions the victim answers by tapping a button, to P2
over its existing peer connection. P2 forwards all of it to the Robot Screen — a kiosk browser on the robot's own display and
speaker, connected to P2 over localhost.

Only the dashboard that is P1's current controller may use any of it (or
switch the robot display): the session must have presented the controller
key and come from the host P1 reports as its controller, so talking follows
P1's single-controller slot, takeovers included. Every other session is a
view-only observer that still receives the robot's own video and audio.
Only one session may drive the robot screen at a time (the "floor"): the
first to send anything claims it, and it is held until that session
releases it, disconnects, or stops being the controller. Everything here lives inside P2's failure domain; nothing
touches P1 or the motor path.

Operator media is decoded by aiortc on arrival and re-encoded for the
screen peer. ``ScreenVideoTrack`` and ``ScreenAudioTrack`` are the outbound
tracks on the screen connection: they are created once per screen session
and read whatever the floor holder is currently sending, falling back to
the last frame (video) or silence (audio) so the screen connection never
needs renegotiating when the operator starts or stops sending. Audio is
re-encoded here as 60 ms Opus packets rather than by aiortc (see
``ScreenAudioTrack``).
"""

from __future__ import annotations

import asyncio
import collections
import contextlib
import fractions
import io
import json
import time
from typing import Any, Protocol

import av
import numpy as np
from aiortc import VideoStreamTrack
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack

from common.logging_setup import EventLogger

from .media import AUDIO_PACKET_SAMPLES, encode_packet, opus_encoder

SCREEN_TEXT_MAX = 280
# A question the operator asks with tap-to-answer buttons on the robot screen,
# for a victim who can't speak. P2 owns it, including the timeout, so "no
# answer" holds even if the kiosk or the dashboard reconnects.
QUESTION_OPTIONS_MIN = 2
QUESTION_OPTIONS_MAX = 4
QUESTION_OPTION_MAX = 40
QUESTION_TIMEOUT_S = 300.0
VIDEO_SOURCES = ("none", "camera", "image", "screen")
# What the robot's display shows: the Robot Screen kiosk ("robot"), or the
# plain Pi desktop so an operator can work on the Pi over VNC ("vnc"), which
# mirrors that same display. The launcher closes the kiosk in "vnc" mode.
DISPLAY_MODES = ("robot", "vnc")

VIDEO_CLOCK_RATE = 90000
AUDIO_RATE = 48000
# Beyond this many queued 20 ms operator frames the oldest are dropped,
# capping the operator-to-speaker latency added by P2 at ~200 ms.
AUDIO_QUEUE_FRAMES = 10
# Audio to the Robot Screen goes out as one Opus packet per AUDIO_PACKET_MS (see
# ScreenAudioTrack). Later than this, the track resets its clock instead of
# catching up.
AUDIO_MAX_LATE_S = 0.1
AUDIO_BITRATE = 32000
# Voice buffered before playing (again) after running dry, and the most
# kept; beyond that the oldest is discarded to bound the delay.
AUDIO_CUSHION_SAMPLES = AUDIO_RATE * 120 // 1000
AUDIO_BUFFER_MAX_SAMPLES = AUDIO_RATE * 400 // 1000
# With no new operator frame for this long the screen track repeats the last
# one, so a static source (a still image, an idle shared screen) keeps the
# screen connection's encoder fed.
VIDEO_REPEAT_S = 1.0
IDLE_WIDTH = 640
IDLE_HEIGHT = 480
# A voice message the operator records and the robot repeats on its speaker
# until told to stop (e.g. while driving to a victim). P2 holds it in memory
# only and loops it itself, so it keeps playing if the dashboard's link drops.
# The dashboard stops recording at 30 s; the server allows a little slack.
VOICE_MAX_S = 35.0
VOICE_MAX_BYTES = 1_000_000
# Silence after each repeat, so the message isn't one run-on sentence.
VOICE_GAP_S = 1.5
# Recordings are peak-normalised to this fraction of full scale, but never
# amplified more than VOICE_MAX_GAIN (so a near-silent clip stays quiet hiss).
VOICE_PEAK = 0.9
VOICE_MAX_GAIN = 8.0
VOICE_COMMANDS = ("voice_loop_start", "voice_loop_stop", "voice_clear")
# After "Hold to talk" is released the loop waits this long before taking
# over again, so the operator's last words (still in flight) are not cut.
VOICE_RESUME_S = 0.5


def decode_voice_clip(data: bytes) -> bytes:
    """Decode an uploaded recording to the loop's PCM: 48 kHz mono s16.

    Any container/codec FFmpeg reads is accepted (the dashboard sends
    WebM/Opus). The result is peak-normalised and ends in VOICE_GAP_S of
    silence. Raises ValueError for an unreadable, silent-length or too-long clip.
    """
    if not data:
        raise ValueError("empty recording")
    if len(data) > VOICE_MAX_BYTES:
        raise ValueError("recording too large")
    resampler = av.AudioResampler(format="s16", layout="mono", rate=AUDIO_RATE)
    chunks: list[np.ndarray] = []
    total = 0
    max_samples = int(VOICE_MAX_S * AUDIO_RATE)
    try:
        with av.open(io.BytesIO(data)) as container:
            if not container.streams.audio:
                raise ValueError("recording has no audio")
            for frame in container.decode(audio=0):
                frame.pts = None
                for mono in resampler.resample(frame):
                    chunk = mono.to_ndarray().reshape(-1)
                    chunks.append(chunk)
                    total += chunk.size
                if total > max_samples:
                    raise ValueError(f"recording longer than {VOICE_MAX_S:.0f} s")
            for mono in resampler.resample(None):
                chunks.append(mono.to_ndarray().reshape(-1))
    except av.FFmpegError as exc:
        raise ValueError(f"unreadable recording: {exc}") from exc
    pcm = np.concatenate(chunks).astype(np.int16) if chunks else np.zeros(0, np.int16)
    if pcm.size < AUDIO_PACKET_SAMPLES:
        raise ValueError("recording too short")
    if pcm.size > max_samples:
        raise ValueError(f"recording longer than {VOICE_MAX_S:.0f} s")
    peak = int(np.abs(pcm.astype(np.int32)).max())
    if peak > 0:
        gain = min(VOICE_MAX_GAIN, VOICE_PEAK * 32767 / peak)
        pcm = np.clip(pcm.astype(np.float32) * gain, -32768, 32767).astype(np.int16)
    gap = np.zeros(int(VOICE_GAP_S * AUDIO_RATE), np.int16)
    return np.concatenate([pcm, gap]).tobytes()


class Channel(Protocol):
    """The subset of ``RTCDataChannel`` the hub uses (lets tests pass fakes)."""

    readyState: str

    def send(self, data: str) -> None: ...


def parse_operator_message(raw: Any) -> dict[str, Any] | None:
    """Validate one data-channel message from a dashboard.

    Returns a normalised message, or None if it is malformed or unknown.
    Text is trimmed and capped at SCREEN_TEXT_MAX characters rather than
    rejected, matching the firmware's clamp-don't-discard policy.
    """
    if not isinstance(raw, str):
        return None
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(msg, dict):
        return None

    kind = msg.get("type")
    if kind == "screen_text":
        text = msg.get("text")
        if not isinstance(text, str):
            return None
        text = text.strip()[:SCREEN_TEXT_MAX]
        if not text:
            return None
        ts = msg.get("ts")
        return {"type": "screen_text", "text": text, "ts": ts if isinstance(ts, (int, float)) else None}
    if kind == "screen_clear":
        return {"type": "screen_clear"}
    if kind == "question_ask":
        text = msg.get("text")
        options = msg.get("options")
        if not isinstance(text, str) or not isinstance(options, list):
            return None
        text = text.strip()[:SCREEN_TEXT_MAX]
        if not text or not all(isinstance(o, str) for o in options):
            return None
        cleaned = [o.strip()[:QUESTION_OPTION_MAX] for o in options]
        cleaned = [o for o in cleaned if o]
        if not QUESTION_OPTIONS_MIN <= len(cleaned) <= QUESTION_OPTIONS_MAX:
            return None
        return {"type": "question_ask", "text": text, "options": cleaned}
    if kind == "question_clear":
        return {"type": "question_clear"}
    if kind == "media_state":
        video = msg.get("video", "none")
        if video not in VIDEO_SOURCES:
            return None
        return {"type": "media_state", "talking": bool(msg.get("talking")), "video": video}
    if kind == "floor_release":
        return {"type": "floor_release"}
    if kind == "display_mode":
        mode = msg.get("mode")
        if mode not in DISPLAY_MODES:
            return None
        return {"type": "display_mode", "mode": mode}
    if kind in VOICE_COMMANDS:
        return {"type": kind}
    return None


def _send(channel: Channel | None, payload: dict[str, Any]) -> None:
    if channel is None or channel.readyState != "open":
        return
    with contextlib.suppress(Exception):
        channel.send(json.dumps(payload))


class ScreenHub:
    """Floor control and routing between operator sessions and the Robot Screen."""

    def __init__(self, log: EventLogger) -> None:
        self.log = log
        self.floor_holder: str | None = None
        self.operators: dict[str, Channel | None] = {}
        # Sessions that presented the controller key, with the host each came
        # from; only those from P1's controller host may act.
        self.controllers: dict[str, str] = {}
        self.controller_host: str | None = None
        self.screen_channel: Channel | None = None
        self.screen_connected = False
        self.media_state: dict[str, Any] = {"talking": False, "video": "none"}
        self.current_text: str | None = None
        # The current question: id, text, options, status ("waiting",
        # "answered", "expired" or "cleared") and the chosen option's index.
        self.question: dict[str, Any] | None = None
        self._question_ids = 0
        self._question_deadline: float | None = None
        self._question_timer: asyncio.TimerHandle | None = None
        # Always "robot" after a P2 restart, so a reboot never leaves the
        # victim looking at the Pi desktop.
        self.display_mode = "robot"
        # The looping voice message: 48 kHz mono s16 PCM (gap included), the
        # read position, and an id bumped per upload so a dashboard can tell
        # whether the robot holds the clip it recorded. Robot-owned: neither
        # releasing the floor nor an operator disconnecting stops it.
        self.voice_pcm: bytes | None = None
        self.voice_id = 0
        self.voice_playing = False
        self._voice_pos = 0
        self._talk_ended_at = float("-inf")

        self._video_latest: av.VideoFrame | None = None
        self._video_event = asyncio.Event()
        self._audio_queue: collections.deque[av.AudioFrame] = collections.deque(
            maxlen=AUDIO_QUEUE_FRAMES
        )
        self._pumps: set[asyncio.Task[None]] = set()

    # --- operator sessions -------------------------------------------------

    def grant_control(self, session_id: str, host: str) -> None:
        self.controllers[session_id] = host

    def can_control(self, session_id: str) -> bool:
        host = self.controllers.get(session_id)
        return host is not None and host == self.controller_host

    def set_controller_host(self, host: str | None) -> None:
        """Follow P1's controller; a floor holder that lost control loses the floor."""
        if host == self.controller_host:
            return
        self.log.info("TALK_CONTROLLER", "talk now follows P1 controller", host=host)
        self.controller_host = host
        if self.floor_holder is not None and not self.can_control(self.floor_holder):
            self._release_floor()  # also broadcasts
        else:
            self._broadcast_status()

    def operator_connected(self, session_id: str, channel: Channel) -> None:
        self.operators[session_id] = channel
        self._send_status(session_id)
        if self.question is not None:
            _send(channel, self._question_status())
        _send(channel, self._voice_status())

    def operator_closed(self, session_id: str) -> None:
        self.controllers.pop(session_id, None)
        if session_id not in self.operators and self.floor_holder != session_id:
            return
        self.operators.pop(session_id, None)
        if self.floor_holder == session_id:
            self._release_floor()

    def handle_operator_message(self, session_id: str, raw: Any) -> None:
        msg = parse_operator_message(raw)
        if msg is None:
            self.log.warning("TALK_BAD_MSG", "ignored malformed operator message", session=session_id)
            return

        if not self.can_control(session_id):
            self.log.warning(
                "TALK_VIEW_ONLY", "observer session tried to use the robot screen",
                session=session_id, kind=msg["type"],
            )
            _send(self.operators.get(session_id), {"type": "view_only"})
            return

        if msg["type"] == "floor_release":
            if self.floor_holder == session_id:
                self._release_floor()
            return

        # Switching the display is a maintenance action, not talking to the
        # victim, so it neither needs nor claims the floor.
        if msg["type"] == "display_mode":
            self.set_display_mode(msg["mode"], source=session_id)
            return

        # The voice loop is the robot's, not a conversation: it neither needs
        # nor claims the floor, so it can keep going after the operator leaves.
        if msg["type"] in VOICE_COMMANDS:
            self._voice_command(msg["type"], session_id)
            return

        if not self._claim_floor(session_id):
            _send(self.operators.get(session_id), {"type": "floor_denied"})
            return

        if msg["type"] == "media_state":
            if self.media_state["talking"] and not msg["talking"]:
                self._talk_ended_at = time.monotonic()
            self.media_state = {"talking": msg["talking"], "video": msg["video"]}
            self._send_screen_state()
        elif msg["type"] == "screen_text":
            self.current_text = msg["text"]
            _send(self.screen_channel, msg)
            self.log.info("SCREEN_TEXT", "message sent to robot screen", session=session_id)
        elif msg["type"] == "screen_clear":
            self.current_text = None
            _send(self.screen_channel, {"type": "screen_clear"})
        elif msg["type"] == "question_ask":
            self._ask_question(msg["text"], msg["options"], session_id)
        elif msg["type"] == "question_clear":
            self._clear_question()

    def _claim_floor(self, session_id: str) -> bool:
        if self.floor_holder == session_id:
            return True
        if self.floor_holder is not None:
            return False
        self.floor_holder = session_id
        self.log.info("FLOOR_CLAIM", "operator took the robot screen", session=session_id)
        self._broadcast_status()
        return True

    def _release_floor(self) -> None:
        self.log.info("FLOOR_RELEASE", "robot screen released", session=self.floor_holder)
        self.floor_holder = None
        self.media_state = {"talking": False, "video": "none"}
        self.current_text = None
        self._video_latest = None
        self._audio_queue.clear()
        _send(self.screen_channel, {"type": "screen_clear"})
        self._end_question("cleared")
        self._send_screen_state()
        self._broadcast_status()

    def _send_status(self, session_id: str) -> None:
        if self.floor_holder is None:
            floor = "free"
        elif self.floor_holder == session_id:
            floor = "you"
        else:
            floor = "other"
        _send(
            self.operators.get(session_id),
            {
                "type": "talk_status",
                "screen_online": self.screen_connected,
                "floor": floor,
                "display_mode": self.display_mode,
                "can_control": self.can_control(session_id),
            },
        )

    def _broadcast_status(self) -> None:
        for session_id in list(self.operators):
            self._send_status(session_id)

    def set_display_mode(self, mode: str, source: str) -> None:
        """Switch the robot display between the kiosk and the Pi desktop."""
        if mode not in DISPLAY_MODES:
            raise ValueError(f"unknown display mode: {mode}")
        if mode == self.display_mode:
            return
        self.display_mode = mode
        self.log.info("DISPLAY_MODE", f"robot display switched to {mode}", source=source)
        self._broadcast_status()

    # --- questions ---------------------------------------------------------

    def _ask_question(self, text: str, options: list[str], session_id: str) -> None:
        """Show a new question, replacing any current one."""
        self._cancel_question_timer()
        self._question_ids += 1
        qid = self._question_ids
        self.question = {"id": qid, "text": text, "options": options, "status": "waiting", "answer": None}
        self._question_deadline = time.monotonic() + QUESTION_TIMEOUT_S
        # Handlers run on P2's event loop; unit tests without one call
        # expire_question themselves.
        with contextlib.suppress(RuntimeError):
            self._question_timer = asyncio.get_running_loop().call_later(
                QUESTION_TIMEOUT_S, self.expire_question, qid
            )
        self._show_question(self.screen_channel)
        self.log.info("QUESTION_ASK", "question sent to robot screen",
                      session=session_id, id=qid, options=len(options))
        self._broadcast_question()

    def expire_question(self, qid: int) -> None:
        """Nobody answered in time: take the question off the screen."""
        if self.question is not None and self.question["id"] == qid:
            self._end_question("expired")

    def _end_question(self, status: str) -> None:
        if self.question is None or self.question["status"] != "waiting":
            return
        self._cancel_question_timer()
        self.question["status"] = status
        _send(self.screen_channel, {"type": "question_hide", "id": self.question["id"]})
        event = "QUESTION_EXPIRE" if status == "expired" else "QUESTION_CLEAR"
        self.log.info(event, f"question {status}", id=self.question["id"])
        self._broadcast_question()

    def _clear_question(self) -> None:
        """Operator's Clear: take a waiting question off the screen, then
        forget the question (answered or not) so no dashboard shows it again."""
        if self.question is None:
            return
        self._end_question("cleared")  # no-op unless still waiting
        qid = self.question["id"]
        self.question = None
        self.log.info("QUESTION_DISMISS", "question removed from dashboards", id=qid)
        for channel in list(self.operators.values()):
            _send(channel, {"type": "question_dismissed", "id": qid})

    def _answer_question(self, qid: Any, choice: Any) -> None:
        q = self.question
        # bool is an int; a stray true must not count as option 1.
        if (
            q is None or q["status"] != "waiting" or qid != q["id"]
            or not isinstance(choice, int) or isinstance(choice, bool)
            or not 0 <= choice < len(q["options"])
        ):
            return  # a late, repeated or malformed tap
        self._cancel_question_timer()
        q["status"] = "answered"
        q["answer"] = choice
        self.log.info("QUESTION_ANSWER", "victim answered the question", id=qid, choice=choice)
        self._broadcast_question()

    def _cancel_question_timer(self) -> None:
        if self._question_timer is not None:
            self._question_timer.cancel()
            self._question_timer = None
        self._question_deadline = None

    def _show_question(self, channel: Channel | None) -> None:
        q = self.question
        if q is not None and q["status"] == "waiting":
            _send(channel, {"type": "question_show", "id": q["id"], "text": q["text"], "options": q["options"]})

    def _question_status(self) -> dict[str, Any]:
        q = self.question
        assert q is not None
        remaining = None
        if self._question_deadline is not None:
            remaining = max(0.0, round(self._question_deadline - time.monotonic(), 1))
        return {"type": "question_status", **q, "remaining_s": remaining}

    def _broadcast_question(self) -> None:
        status = self._question_status()
        for channel in list(self.operators.values()):
            _send(channel, status)

    # --- voice message loop ------------------------------------------------

    def set_voice_clip(self, pcm: bytes, session_id: str | None = None) -> float:
        """Store a decoded recording (see decode_voice_clip), replacing any
        previous one and stopping playback. Returns its length in seconds."""
        self.voice_pcm = pcm
        self.voice_id += 1
        self.voice_playing = False
        self._voice_pos = 0
        duration = self._voice_duration()
        self.log.info("VOICE_SET", "voice message stored for looping",
                      session=session_id, id=self.voice_id, duration_s=duration)
        self._broadcast_voice()
        return duration

    def _voice_command(self, kind: str, session_id: str) -> None:
        if kind == "voice_loop_start":
            if self.voice_pcm is not None and not self.voice_playing:
                self.voice_playing = True
                self._voice_pos = 0
                self.log.info("VOICE_LOOP_START", "voice message looping on robot speaker",
                              session=session_id, id=self.voice_id)
        elif kind == "voice_loop_stop":
            if self.voice_playing:
                self.voice_playing = False
                self.log.info("VOICE_LOOP_STOP", "voice message loop stopped",
                              session=session_id, id=self.voice_id)
        elif kind == "voice_clear":
            if self.voice_pcm is not None:
                self.voice_pcm = None
                self.voice_playing = False
                self._voice_pos = 0
                self.log.info("VOICE_CLEAR", "voice message deleted",
                              session=session_id, id=self.voice_id)
        # Always answer, so a dashboard with a stale view is corrected.
        self._broadcast_voice()

    def live_voice_active(self) -> bool:
        """The operator is talking, or let go less than VOICE_RESUME_S ago."""
        return self.media_state["talking"] or time.monotonic() - self._talk_ended_at < VOICE_RESUME_S

    def next_voice_frame(self) -> av.AudioFrame | None:
        """The next AUDIO_PACKET_SAMPLES of the looping message, wrapping
        around at its end; None unless it is playing."""
        pcm = self.voice_pcm
        if not self.voice_playing or not pcm:
            return None
        need = AUDIO_PACKET_SAMPLES * 2  # s16: two bytes a sample
        pos = self._voice_pos % len(pcm)
        out = bytearray()
        while len(out) < need:
            take = pcm[pos:pos + need - len(out)]
            out += take
            pos = (pos + len(take)) % len(pcm)
        self._voice_pos = pos
        samples = np.frombuffer(bytes(out), np.int16).reshape(1, -1)
        frame = av.AudioFrame.from_ndarray(samples, format="s16", layout="mono")
        frame.sample_rate = AUDIO_RATE
        return frame

    def _voice_duration(self) -> float | None:
        if self.voice_pcm is None:
            return None
        return round(len(self.voice_pcm) / 2 / AUDIO_RATE - VOICE_GAP_S, 1)

    def _voice_status(self) -> dict[str, Any]:
        return {
            "type": "voice_status",
            "id": self.voice_id if self.voice_pcm is not None else None,
            "has_clip": self.voice_pcm is not None,
            "playing": self.voice_playing,
            "duration_s": self._voice_duration(),
        }

    def _broadcast_voice(self) -> None:
        status = self._voice_status()
        for channel in list(self.operators.values()):
            _send(channel, status)

    # --- robot screen ------------------------------------------------------

    def screen_attached(self, channel: Channel) -> None:
        """A (new) Robot Screen connected; it replaces any previous one."""
        self.screen_channel = channel
        self.screen_connected = True
        self._send_screen_state()
        if self.current_text is not None:
            _send(channel, {"type": "screen_text", "text": self.current_text, "ts": None})
        self._show_question(channel)
        self._broadcast_status()

    def screen_detached(self, channel: Channel | None = None) -> None:
        if channel is not None and channel is not self.screen_channel:
            return  # an old screen connection closing after its replacement arrived
        self.screen_channel = None
        self.screen_connected = False
        self._broadcast_status()

    def handle_screen_message(self, raw: Any) -> None:
        try:
            msg = json.loads(raw) if isinstance(raw, str) else None
        except json.JSONDecodeError:
            return
        if not isinstance(msg, dict):
            return
        if msg.get("type") == "screen_ack" and self.floor_holder:
            _send(self.operators.get(self.floor_holder), {"type": "screen_ack", "ts": msg.get("ts")})
        elif msg.get("type") == "question_answer":
            self._answer_question(msg.get("id"), msg.get("choice"))

    def _send_screen_state(self) -> None:
        _send(
            self.screen_channel,
            {
                "type": "screen_state",
                "operator": self.floor_holder is not None,
                "talking": self.media_state["talking"],
                "video": self.media_state["video"],
            },
        )

    # --- media -------------------------------------------------------------

    def attach_operator_track(self, session_id: str, track: MediaStreamTrack) -> None:
        """Drain an operator's inbound track for its whole life.

        aiortc queues decoded frames on the track whether or not anyone
        reads them, so every inbound track is consumed here; frames are
        forwarded only while their session holds the floor.
        """
        task = asyncio.ensure_future(self._pump(session_id, track))
        self._pumps.add(task)
        task.add_done_callback(self._pumps.discard)

    async def _pump(self, session_id: str, track: MediaStreamTrack) -> None:
        while True:
            try:
                frame = await track.recv()
            except MediaStreamError:
                return
            if self.floor_holder != session_id:
                continue
            if track.kind == "video":
                self._video_latest = frame
                self._video_event.set()
            else:
                self._audio_queue.append(frame)

    async def next_video_frame(self) -> av.VideoFrame | None:
        """The newest operator frame, or the previous one after VIDEO_REPEAT_S."""
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._video_event.wait(), VIDEO_REPEAT_S)
        self._video_event.clear()
        return self._video_latest

    def next_audio_frame(self) -> av.AudioFrame | None:
        return self._audio_queue.popleft() if self._audio_queue else None

    def health(self) -> dict[str, Any]:
        return {
            "screen_connected": self.screen_connected,
            "floor_held": self.floor_holder is not None,
            "display_mode": self.display_mode,
            "voice_loaded": self.voice_pcm is not None,
            "voice_playing": self.voice_playing,
        }


class ScreenVideoTrack(VideoStreamTrack):
    """Outbound video to the Robot Screen: the floor holder's video, restamped."""

    kind = "video"

    def __init__(self, hub: ScreenHub) -> None:
        super().__init__()
        self.hub = hub
        self._start = time.monotonic()
        self._last_pts = -1

    async def recv(self) -> av.VideoFrame:
        frame = await self.hub.next_video_frame()
        if frame is None:
            frame = av.VideoFrame(IDLE_WIDTH, IDLE_HEIGHT, "yuv420p")
            for plane in frame.planes:
                plane.update(bytes(plane.buffer_size))
        # Operator frames carry the operator's RTP clock, and repeated or idle
        # frames carry none; restamp everything on one monotonic clock.
        pts = max(int((time.monotonic() - self._start) * VIDEO_CLOCK_RATE), self._last_pts + 1)
        self._last_pts = pts
        frame.pts = pts
        frame.time_base = fractions.Fraction(1, VIDEO_CLOCK_RATE)
        return frame


class ScreenAudioTrack(MediaStreamTrack):
    """Outbound audio to the Robot Screen: operator voice, or silence, as 60 ms Opus packets.

    The track encodes its own Opus packets instead of handing aiortc 20 ms
    frames. On a busy Pi, P2's event loop can run tens of milliseconds late,
    and aiortc's sender needs a trip through the loop per frame, so a 20 ms
    pace could not be kept: the track fell seconds behind, then sent in
    bursts faster than real time, and the operator frames that piled up in
    the meantime overflowed the queue and were dropped. The kiosk played
    that as speech with pieces missing — too fast. A 60 ms packet needs a
    third as many trips, and a late packet is never followed by a burst.
    """

    kind = "audio"

    def __init__(self, hub: ScreenHub) -> None:
        super().__init__()
        self.hub = hub
        self._start: float | None = None
        self._samples = 0
        # Operator voice is mono; aiortc's decoder hands over stereo.
        self._resampler = av.AudioResampler(format="s16", layout="mono", rate=AUDIO_RATE)
        self._fifo = av.AudioFifo()
        self._refilling = True
        self._encoder = opus_encoder(AUDIO_BITRATE)

    async def recv(self) -> av.Packet:
        if self.readyState != "live":
            raise MediaStreamError
        now = time.monotonic()
        if self._start is None:
            self._start = now
        else:
            wait = self._start + self._samples / AUDIO_RATE - now
            if wait > 0:
                await asyncio.sleep(wait)
            elif wait < -AUDIO_MAX_LATE_S:
                # Running late (the Pi was busy): carry on from now rather
                # than bursting to catch up, which the kiosk's jitter buffer
                # would play back sped up.
                self._start = now - self._samples / AUDIO_RATE

        return encode_packet(self._encoder, self._next_frame())

    def _next_frame(self) -> av.AudioFrame:
        """The next 60 ms of operator voice, else the looping voice message,
        else silence while (re)filling the cushion."""
        while (operator := self.hub.next_audio_frame()) is not None:
            operator.pts = None
            for mono in self._resampler.resample(operator):
                mono.pts = None
                self._fifo.write(mono)
        # Operator audio reaches P2 in bursts when the Pi is busy. Keep a
        # small cushion so a late burst doesn't cut words into pieces, but
        # never let the backlog (and so the delay) grow past a cap.
        excess = self._fifo.samples - AUDIO_BUFFER_MAX_SAMPLES
        if excess > 0:
            self._fifo.read(excess)
        if self._refilling and self._fifo.samples >= AUDIO_CUSHION_SAMPLES:
            self._refilling = False

        # The looping voice message, unless the operator is talking (then it
        # is not read, so it pauses and resumes where it was). While it plays,
        # what the floor holder sends between presses is dropped: a dashboard
        # whose mic is open but muted still sends silence, and treating that
        # as live voice would chop the loop into pieces (found 2026-10-31).
        voice = None if self.hub.live_voice_active() else self.hub.next_voice_frame()
        if voice is not None:
            if self._fifo.samples:
                self._fifo.read(self._fifo.samples)
            self._refilling = True  # live voice that starts later gets its cushion first
            frame = voice
        elif not self._refilling and self._fifo.samples >= AUDIO_PACKET_SAMPLES:
            frame = self._fifo.read(AUDIO_PACKET_SAMPLES)
        else:
            # Ran dry (the operator is silent, or their audio is late): send
            # silence and keep what has arrived until the cushion is full
            # again, so speech resumes intact rather than in 60 ms scraps.
            self._refilling = True
            frame = av.AudioFrame(format="s16", layout="mono", samples=AUDIO_PACKET_SAMPLES)
            for plane in frame.planes:
                plane.update(bytes(plane.buffer_size))
        frame.sample_rate = AUDIO_RATE
        frame.pts = self._samples
        frame.time_base = fractions.Fraction(1, AUDIO_RATE)
        self._samples += AUDIO_PACKET_SAMPLES
        return frame
