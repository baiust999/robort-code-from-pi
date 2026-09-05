"""Outbound media tracks, Section 8.8.2 / 8.10.2.

In mock mode (or whenever the real capture device can't be opened) P2 falls
back to a synthetic video track so the WebRTC path — SDP negotiation, ICE,
encoding, packetisation — can be exercised without a camera. Real capture
uses PyAV to pull frames from the V4L2 device / ALSA mic on the Pi.
"""

from __future__ import annotations

import fractions
import time

import av
import numpy as np
from aiortc import AudioStreamTrack, VideoStreamTrack
from aiortc.mediastreams import MediaStreamError

VIDEO_CLOCK_RATE = 90000
AUDIO_CLOCK_RATE = 48000
AUDIO_SAMPLES_PER_FRAME = 960  # 20ms @ 48kHz


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


def open_mic_track(device: str) -> AudioStreamTrack:
    """Open the Pi microphone via PyAV/ALSA, raising if unavailable."""
    from aiortc.contrib.media import MediaPlayer

    player = MediaPlayer(device, format="alsa")
    if player.audio is None:
        raise MediaStreamError("audio device produced no audio track")
    return player.audio
