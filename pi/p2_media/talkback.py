"""Operator-to-victim path ("talk-to-victim"), methodology Section 16.

The operator's dashboard sends its microphone (push-to-talk), an optional
video source (laptop camera, a still image, or a shared screen) and short
text messages to P2 over its existing peer connection. P2 forwards all of
it to the Robot Screen — a kiosk browser on the robot's own display and
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
import json
import time
from typing import Any, Protocol

import av
from aiortc import VideoStreamTrack
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack

from common.logging_setup import EventLogger

from .media import AUDIO_PACKET_SAMPLES, encode_packet, opus_encoder

SCREEN_TEXT_MAX = 280
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
    if kind == "display_mode":
        mode = msg.get("mode")
        if mode not in DISPLAY_MODES:
            return None
        return {"type": "display_mode", "mode": mode}
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
        # Always "robot" after a P2 restart, so a reboot never leaves the
        # victim looking at the Pi desktop.
        self.display_mode = "robot"

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
        return {
            "screen_connected": self.screen_connected,
            "floor_held": self.floor_holder is not None,
            "display_mode": self.display_mode,
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
        """The next 60 ms of operator voice, or silence while (re)filling the cushion."""
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

        if not self._refilling and self._fifo.samples >= AUDIO_PACKET_SAMPLES:
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
