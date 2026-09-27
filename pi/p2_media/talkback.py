"""Operator-to-victim path ("talk-to-victim"), methodology Section 16.

The operator's dashboard sends its microphone (push-to-talk), an optional
video source (laptop camera, a still image, or a shared screen) and short
text messages to P2 over its existing peer connection. P2 forwards all of
it to the Robot Screen — a kiosk browser on the robot's own display and
speaker, connected to P2 over localhost.

Only one operator session may drive the robot screen at a time (the
"floor"), mirroring P1's single-controller slot: the first session to send
anything claims it, and it is held until that session releases it or
disconnects. Everything here lives inside P2's failure domain; nothing
touches P1 or the motor path.

Operator media is decoded by aiortc on arrival and re-encoded for the
screen peer. ``ScreenVideoTrack`` and ``ScreenAudioTrack`` are the outbound
tracks on the screen connection: they are created once per screen session
and read whatever the floor holder is currently sending, falling back to
the last frame (video) or silence (audio) so the screen connection never
needs renegotiating when the operator starts or stops sending.
"""

from __future__ import annotations

import asyncio
import collections
import contextlib
import fractions
import json
import time
from typing import Any, Protocol

import av
from aiortc import AudioStreamTrack, VideoStreamTrack
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack

from common.logging_setup import EventLogger

SCREEN_TEXT_MAX = 280
VIDEO_SOURCES = ("none", "camera", "image", "screen")

VIDEO_CLOCK_RATE = 90000
AUDIO_RATE = 48000
AUDIO_FRAME_SAMPLES = 960  # 20 ms, the Opus frame size browsers send
# Beyond this many queued 20 ms frames the oldest are dropped, capping the
# operator-to-speaker latency added by P2 at ~200 ms.
AUDIO_QUEUE_FRAMES = 10
# With no new operator frame for this long the screen track repeats the last
# one, so a static source (a still image, an idle shared screen) keeps the
# screen connection's encoder fed.
VIDEO_REPEAT_S = 1.0
IDLE_WIDTH = 640
IDLE_HEIGHT = 480


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
    if kind == "media_state":
        video = msg.get("video", "none")
        if video not in VIDEO_SOURCES:
            return None
        return {"type": "media_state", "talking": bool(msg.get("talking")), "video": video}
    if kind == "floor_release":
        return {"type": "floor_release"}
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
        self.screen_channel: Channel | None = None
        self.screen_connected = False
        self.media_state: dict[str, Any] = {"talking": False, "video": "none"}
        self.current_text: str | None = None

        self._video_latest: av.VideoFrame | None = None
        self._video_event = asyncio.Event()
        self._audio_queue: collections.deque[av.AudioFrame] = collections.deque(
            maxlen=AUDIO_QUEUE_FRAMES
        )
        self._pumps: set[asyncio.Task[None]] = set()

    # --- operator sessions -------------------------------------------------

    def operator_connected(self, session_id: str, channel: Channel) -> None:
        self.operators[session_id] = channel
        self._send_status(session_id)

    def operator_closed(self, session_id: str) -> None:
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

        if msg["type"] == "floor_release":
            if self.floor_holder == session_id:
                self._release_floor()
            return

        if not self._claim_floor(session_id):
            _send(self.operators.get(session_id), {"type": "floor_denied"})
            return

        if msg["type"] == "media_state":
            self.media_state = {"talking": msg["talking"], "video": msg["video"]}
            self._send_screen_state()
        elif msg["type"] == "screen_text":
            self.current_text = msg["text"]
            _send(self.screen_channel, msg)
            self.log.info("SCREEN_TEXT", "message sent to robot screen", session=session_id)
        elif msg["type"] == "screen_clear":
            self.current_text = None
            _send(self.screen_channel, {"type": "screen_clear"})

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
            {"type": "talk_status", "screen_online": self.screen_connected, "floor": floor},
        )

    def _broadcast_status(self) -> None:
        for session_id in list(self.operators):
            self._send_status(session_id)

    # --- robot screen ------------------------------------------------------

    def screen_attached(self, channel: Channel) -> None:
        """A (new) Robot Screen connected; it replaces any previous one."""
        self.screen_channel = channel
        self.screen_connected = True
        self._send_screen_state()
        if self.current_text is not None:
            _send(channel, {"type": "screen_text", "text": self.current_text, "ts": None})
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
        if isinstance(msg, dict) and msg.get("type") == "screen_ack" and self.floor_holder:
            _send(self.operators.get(self.floor_holder), {"type": "screen_ack", "ts": msg.get("ts")})

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
        return {"screen_connected": self.screen_connected, "floor_held": self.floor_holder is not None}


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


class ScreenAudioTrack(AudioStreamTrack):
    """Outbound audio to the Robot Screen: operator voice, or silence, at a steady 20 ms pace."""

    kind = "audio"

    def __init__(self, hub: ScreenHub) -> None:
        super().__init__()
        self.hub = hub
        self._start: float | None = None
        self._samples = 0

    async def recv(self) -> av.AudioFrame:
        if self._start is None:
            self._start = time.monotonic()
        else:
            wait = self._start + self._samples / AUDIO_RATE - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)

        frame = self.hub.next_audio_frame()
        if frame is None:
            # Stereo s16 at 48 kHz matches what aiortc's Opus decoder
            # produces, so the encoder's resampler never switches format.
            frame = av.AudioFrame(format="s16", layout="stereo", samples=AUDIO_FRAME_SAMPLES)
            for plane in frame.planes:
                plane.update(bytes(plane.buffer_size))
            frame.sample_rate = AUDIO_RATE

        frame.pts = self._samples
        frame.time_base = fractions.Fraction(1, AUDIO_RATE)
        self._samples += int(frame.samples * AUDIO_RATE / (frame.sample_rate or AUDIO_RATE))
        return frame
