"""Outbound media tracks, Section 8.8.2 / 8.10.2.

In mock mode (or whenever the real capture device can't be opened) P2 falls
back to a synthetic video track so the WebRTC path — SDP negotiation, ICE,
encoding, packetisation — can be exercised without a camera. Real capture
uses PyAV to pull frames from the V4L2 device / ALSA mic on the Pi.
"""

from __future__ import annotations

import fractions
import os
import time
from collections.abc import Callable
from pathlib import Path

import av
import numpy as np
from aiortc import AudioStreamTrack, VideoStreamTrack
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack

VIDEO_CLOCK_RATE = 90000
AUDIO_CLOCK_RATE = 48000
AUDIO_SAMPLES_PER_FRAME = 960  # 20ms @ 48kHz
# P2's own audio tracks hand aiortc ready-made Opus packets of this length
# (see ResilientAudioTrack); aiortc would otherwise encode every 20 ms frame
# on its thread pool, which a busy Pi can't keep up with.
AUDIO_PACKET_MS = 60
AUDIO_PACKET_SAMPLES = AUDIO_CLOCK_RATE * AUDIO_PACKET_MS // 1000
MIC_BITRATE = 32000


class SyntheticVideoTrack(VideoStreamTrack):
    """A moving test pattern with a timestamp overlay, used when no camera is present."""

    kind = "video"

    def __init__(self, width: int = 640, height: int = 480, framerate: int = 10) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self._frame_interval = 1.0 / framerate
        self._frame_index = 0
        self._start = time.monotonic()

    async def recv(self) -> av.VideoFrame:
        pts, time_base = await self._next_timestamp()

        elapsed = time.monotonic() - self._start
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # A bar sweeping left-to-right so motion is visually obvious over WebRTC.
        bar_x = int((elapsed * 120) % self.width)
        img[:, max(0, bar_x - 4) : bar_x + 4] = (0, 200, 255)

        # Colour cycles slowly so a static screenshot still proves liveness.
        hue_shift = int(elapsed * 20) % 255
        img[:, :, 0] = hue_shift // 2
        img[:, :, 1] = 40

        # Coarse digit-free "clock": a block whose width encodes seconds
        # elapsed, so frame-to-frame progress is visible without font
        # rendering (avoids a fontconfig dependency for a mock-only track).
        seconds_width = int((elapsed % 60) / 60 * self.width)
        img[0:10, 0:seconds_width] = (255, 255, 255)

        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        frame.pts = pts
        frame.time_base = time_base
        self._frame_index += 1
        return frame

    async def _next_timestamp(self) -> tuple[int, fractions.Fraction]:
        if hasattr(self, "_timestamp"):
            self._timestamp += int(self._frame_interval * VIDEO_CLOCK_RATE)
            wait = self._start + self._frame_index * self._frame_interval - time.monotonic()
            if wait > 0:
                import asyncio

                await asyncio.sleep(wait)
        else:
            self._timestamp = 0
            self._start = time.monotonic()
        return self._timestamp, fractions.Fraction(1, VIDEO_CLOCK_RATE)


class SilentAudioTrack(AudioStreamTrack):
    """Silence at the standard Opus frame size, used when no mic is present."""

    kind = "audio"

    def __init__(self) -> None:
        super().__init__()
        self._timestamp = 0
        self._start: float | None = None

    async def recv(self) -> av.AudioFrame:
        import asyncio

        if self._start is None:
            self._start = time.monotonic()
        else:
            target = self._start + (self._timestamp / AUDIO_CLOCK_RATE)
            wait = target - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)

        frame = av.AudioFrame(format="s16", layout="mono", samples=AUDIO_SAMPLES_PER_FRAME)
        for plane in frame.planes:
            plane.update(bytes(plane.buffer_size))
        frame.pts = self._timestamp
        frame.sample_rate = AUDIO_CLOCK_RATE
        frame.time_base = fractions.Fraction(1, AUDIO_CLOCK_RATE)
        self._timestamp += AUDIO_SAMPLES_PER_FRAME
        return frame


def open_camera_track(device: str, width: int, height: int, framerate: int) -> VideoStreamTrack:
    """Open the Pi camera via PyAV/V4L2, raising if unavailable.

    Callers should catch the exception and fall back to SyntheticVideoTrack;
    this keeps the "no camera present" path identical for mock mode and for
    a real Pi whose camera happens to be disconnected.
    """
    from aiortc.contrib.media import MediaPlayer

    player = MediaPlayer(
        device,
        format="v4l2",
        options={
            "video_size": f"{width}x{height}",
            "framerate": str(framerate),
        },
    )
    if player.video is None:
        raise MediaStreamError("camera device produced no video track")
    return player.video


class SharedCapture:
    """One capture device fanned out to every session through a MediaRelay.

    ALSA and V4L2 devices can only be opened once, so opening them per
    session left every session after the first (a second viewer, or a page
    reload that arrives before the old connection has timed out) with a
    busy device and a silent/synthetic fallback. The device is opened on
    first use and closed again when the last session's track ends.
    """

    def __init__(self, open_track: Callable[[], MediaStreamTrack], buffered: bool) -> None:
        from aiortc.contrib.media import MediaRelay

        self._open = open_track
        self._buffered = buffered
        self._relay = MediaRelay()
        self._source: MediaStreamTrack | None = None
        self._users = 0

    def subscribe(self) -> MediaStreamTrack:
        """A new consumer track; raises if the device can't be opened."""
        if self._source is None or self._source.readyState != "live":
            self._source = self._open()
            self._users = 0
        source = self._source
        proxy = self._relay.subscribe(source, buffered=self._buffered)
        self._users += 1

        @proxy.on("ended")
        def _ended() -> None:
            if source is not self._source:
                return  # a consumer of a source that was already replaced
            self._users -= 1
            if self._users <= 0:
                self._source = None
                source.stop()

        return proxy


class PrivateVideoTrack(MediaStreamTrack):
    """A session's own yuv420p copy of every frame from a shared video track.

    The camera frames that ``SharedCapture`` fans out are one object shared
    by every session, and each session's VP8 encoder runs on its own thread.
    Given a YUYV camera frame, each encoder called ``frame.reformat()``,
    which PyAV runs through a converter cached on the frame itself with the
    GIL released, so two viewers converted the same frame through the same
    converter at once and P2 died with a segmentation fault. Converting here,
    on the event loop, hands each encoder a frame nobody else touches, already
    in the format it needs.
    """

    kind = "video"

    def __init__(self, source: MediaStreamTrack) -> None:
        from av.video.reformatter import VideoReformatter

        super().__init__()
        self._source = source
        self._reformatter = VideoReformatter()

    async def recv(self) -> av.VideoFrame:
        frame = await self._source.recv()
        private = self._reformatter.reformat(frame, format="yuv420p")
        if private is frame:
            # Already yuv420p: reformat hands back the shared frame itself.
            private = av.VideoFrame.from_ndarray(frame.to_ndarray(), format="yuv420p")
            private.pts = frame.pts
            private.time_base = frame.time_base
        return private

    def stop(self) -> None:
        super().stop()
        self._source.stop()


ALSA_CONF = Path(__file__).with_name("alsa.conf")


def opus_encoder(bitrate: int) -> av.CodecContext:
    """A mono voice Opus encoder that emits one packet per AUDIO_PACKET_MS frame."""
    encoder = av.CodecContext.create("libopus", "w")
    encoder.sample_rate = AUDIO_CLOCK_RATE
    encoder.format = "s16"
    encoder.layout = "mono"
    encoder.bit_rate = bitrate
    encoder.options = {"application": "voip", "frame_duration": str(AUDIO_PACKET_MS)}
    encoder.time_base = fractions.Fraction(1, AUDIO_CLOCK_RATE)
    return encoder


def encode_packet(encoder: av.CodecContext, frame: av.AudioFrame) -> av.Packet:
    """Encode exactly one AUDIO_PACKET_MS frame, keeping the frame's timestamp."""
    # libopus emits exactly one packet per full frame of frame_duration.
    packet = encoder.encode(frame)[0]
    packet.pts = frame.pts
    packet.time_base = frame.time_base
    return packet


class ResilientAudioTrack(MediaStreamTrack):
    """A session's mic track that survives the mic being missing or going away.

    Opening the mic once per session and falling back to silence for good
    left a dashboard silent until reloaded whenever the mic wasn't there at
    connect time — and the robot's USB webcam/mic does drop off the bus and
    come back (e.g. right after P2 restarts). Instead this sends silence
    while the mic is unavailable, retries every ``retry_s``, and switches to
    the mic as soon as it opens; if the mic ends mid-session it goes back to
    silence and retries.

    It sends ready-made mono Opus packets of AUDIO_PACKET_MS, stamped on one
    counter so the receiver sees a single continuous stream across those
    switches. Left to itself, aiortc encodes each 20 ms mic frame on its
    thread pool, behind every viewer's video encoding; on a busy Pi that
    sent only ~37 of the 50 packets a second, and the dashboard played the
    robot's audio choppy.
    """

    kind = "audio"

    def __init__(
        self,
        open_track: Callable[[], MediaStreamTrack],
        on_lost: Callable[[Exception], None] | None = None,
        on_restored: Callable[[], None] | None = None,
        retry_s: float = 2.0,
    ) -> None:
        super().__init__()
        self._open = open_track
        self._on_lost = on_lost
        self._on_restored = on_restored
        self._retry_s = retry_s
        self._source: MediaStreamTrack | None = None
        self._next_retry = 0.0
        self._lost = False
        self._next_silence: float | None = None
        self._samples = 0
        # The mic is mono, but MediaPlayer hands over stereo.
        self._resampler = av.AudioResampler(format="s16", layout="mono", rate=AUDIO_CLOCK_RATE)
        self._fifo = av.AudioFifo()
        self._encoder = opus_encoder(MIC_BITRATE)

    async def recv(self) -> av.Packet:
        if self.readyState != "live":
            raise MediaStreamError
        while self._fifo.samples < AUDIO_PACKET_SAMPLES:
            source_frame = await self._next_frame()
            source_frame.pts = None  # mic and silence carry unrelated clocks
            for mono in self._resampler.resample(source_frame):
                mono.pts = None
                self._fifo.write(mono)
        frame = self._fifo.read(AUDIO_PACKET_SAMPLES)
        frame.pts = self._samples
        frame.time_base = fractions.Fraction(1, AUDIO_CLOCK_RATE)
        self._samples += AUDIO_PACKET_SAMPLES
        return encode_packet(self._encoder, frame)

    async def _next_frame(self) -> av.AudioFrame:
        """The next mic frame, or 20 ms of silence while the mic is unavailable."""
        if self._source is None and time.monotonic() >= self._next_retry:
            self._try_open()

        frame = None
        if self._source is not None:
            try:
                frame = await self._source.recv()
            except MediaStreamError:
                self._source = None
                self._mark_lost(MediaStreamError("mic stream ended"))
        if frame is None:
            return await self._silence()
        self._next_silence = None  # the device paces live frames
        return frame

    def stop(self) -> None:
        super().stop()
        if self._source is not None:
            self._source.stop()
            self._source = None

    def _try_open(self) -> None:
        try:
            self._source = self._open()
        except Exception as exc:  # noqa: BLE001 - any failure means "try again later"
            self._mark_lost(exc)
            return
        if self._lost and self._on_restored is not None:
            self._on_restored()
        self._lost = False

    def _mark_lost(self, exc: Exception) -> None:
        self._next_retry = time.monotonic() + self._retry_s
        if not self._lost and self._on_lost is not None:
            self._on_lost(exc)  # once per outage, not once per retry
        self._lost = True

    async def _silence(self) -> av.AudioFrame:
        import asyncio

        # 20 ms of silence in the same format the mic delivers (MediaPlayer
        # resamples to stereo s16), since the resampler rejects a change of
        # layout mid-stream.
        now = time.monotonic()
        if self._next_silence is None or self._next_silence < now - 0.1:
            self._next_silence = now
        wait = self._next_silence - now
        if wait > 0:
            await asyncio.sleep(wait)
        self._next_silence += AUDIO_SAMPLES_PER_FRAME / AUDIO_CLOCK_RATE

        frame = av.AudioFrame(format="s16", layout="stereo", samples=AUDIO_SAMPLES_PER_FRAME)
        for plane in frame.planes:
            plane.update(bytes(plane.buffer_size))
        frame.sample_rate = AUDIO_CLOCK_RATE
        return frame


def _first_capture_card() -> str | None:
    """The ALSA id (e.g. "U20") of the first card that can record, if any."""
    try:
        lines = Path("/proc/asound/pcm").read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        if "capture" in line:
            card = int(line.split("-", 1)[0])
            return Path(f"/proc/asound/card{card}/id").read_text().strip()
    return None


def resolve_mic_device(device: str) -> str:
    """Map AUDIO_DEVICE onto a name PyAV's bundled ALSA can open.

    "default" means the PipeWire/PulseAudio default on a desktop, which P2
    can't reach (see alsa.conf), so it picks the first capture card instead.
    """
    if device != "default":
        return device
    card = _first_capture_card()
    if card is None:
        raise MediaStreamError("no ALSA capture device found")
    return f"mic:CARD={card},DEV=0"


def open_mic_track(device: str) -> AudioStreamTrack:
    """Open the Pi microphone via PyAV/ALSA, raising if unavailable."""
    from aiortc.contrib.media import MediaPlayer

    os.environ.setdefault("ALSA_CONFIG_PATH", str(ALSA_CONF))
    player = MediaPlayer(resolve_mic_device(device), format="alsa")
    if player.audio is None:
        raise MediaStreamError("audio device produced no audio track")
    return player.audio
