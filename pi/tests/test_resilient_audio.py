"""ResilientAudioTrack: a session's mic track that recovers when the mic comes and goes."""

import asyncio

import av
import numpy as np
import pytest
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack

from p2_media.media import AUDIO_PACKET_SAMPLES, AUDIO_SAMPLES_PER_FRAME, ResilientAudioTrack

# Mic frames per Opus packet.
PER_PACKET = AUDIO_PACKET_SAMPLES // AUDIO_SAMPLES_PER_FRAME
TONE = (8000 * np.sin(np.arange(AUDIO_SAMPLES_PER_FRAME) / 5)).astype(np.int16)


class FakeMic(MediaStreamTrack):
    """20 ms stereo s16 frames of a tone, like MediaPlayer, ending after ``frames``."""

    kind = "audio"

    def __init__(self, frames: int) -> None:
        super().__init__()
        self.left = frames

    async def recv(self) -> av.AudioFrame:
        if self.left == 0:
            self.stop()
            raise MediaStreamError
        self.left -= 1
        frame = av.AudioFrame.from_ndarray(
            np.repeat(TONE, 2).reshape(1, -1), format="s16", layout="stereo"
        )
        frame.sample_rate = 48000
        frame.pts = 123456  # the device's own clock, which must not leak out
        return frame


class Opener:
    """Fails ``failures`` times, then opens FakeMics of ``frames`` frames."""

    def __init__(self, failures: int, frames: int = 1000) -> None:
        self.failures = failures
        self.frames = frames
        self.opened: list[FakeMic] = []

    def __call__(self) -> FakeMic:
        if self.failures > 0:
            self.failures -= 1
            raise OSError("no ALSA capture device found")
        self.opened.append(FakeMic(self.frames))
        return self.opened[-1]


def loudness(packets: list[av.Packet]) -> list[int]:
    """Peak level of each decoded packet: ~0 for silence, thousands for the tone."""
    decoder = av.CodecContext.create("libopus", "r")
    return [int(np.abs(f.to_ndarray()).max()) for p in packets for f in decoder.decode(p)]


def test_silence_until_mic_appears_then_mic():
    asyncio.run(_silence_until_mic_appears_then_mic())


async def _silence_until_mic_appears_then_mic():
    events: list[str] = []
    # Two failed opens: two 20 ms silent frames before the mic comes through.
    opener = Opener(failures=2)
    track = ResilientAudioTrack(
        opener,
        on_lost=lambda exc: events.append("lost"),
        on_restored=lambda: events.append("restored"),
        retry_s=0,
    )
    packets = [await track.recv() for _ in range(3)]
    # One outage is reported once, however many retries it takes.
    assert events == ["lost", "restored"]
    # Silence and mic go out as one continuous stream of 60 ms packets.
    assert [p.pts for p in packets] == [i * AUDIO_PACKET_SAMPLES for i in range(3)]
    levels = loudness(packets)
    assert levels[-1] > 2000  # the tone
    track.stop()
    assert opener.opened[0].readyState == "ended"


def test_mic_lost_mid_session_falls_back_and_reopens():
    asyncio.run(_mic_lost_mid_session_falls_back_and_reopens())


async def _mic_lost_mid_session_falls_back_and_reopens():
    events: list[str] = []
    # Each mic ends after exactly one packet's worth of frames.
    opener = Opener(failures=0, frames=PER_PACKET)
    track = ResilientAudioTrack(
        opener,
        on_lost=lambda exc: events.append("lost"),
        on_restored=lambda: events.append("restored"),
        retry_s=0,
    )
    packets = [await track.recv()]
    opener.frames = 1000  # the reopened mic stays
    packets += [await track.recv() for _ in range(2)]
    # The first mic ends, 20 ms of silence goes out, and the retry reopens it.
    assert len(opener.opened) == 2
    assert events == ["lost", "restored"]
    assert [p.pts for p in packets] == [i * AUDIO_PACKET_SAMPLES for i in range(3)]
    assert loudness(packets)[-1] > 2000  # the reopened mic's tone
    track.stop()


def test_silence_is_paced_in_real_time():
    asyncio.run(_silence_is_paced_in_real_time())


async def _silence_is_paced_in_real_time():
    track = ResilientAudioTrack(Opener(failures=10**6), retry_s=60)
    loop = asyncio.get_running_loop()
    first = await track.recv()
    start = loop.time()
    second = await track.recv()
    # Each 60 ms packet of silence takes 60 ms to produce.
    assert loop.time() - start == pytest.approx(0.06, abs=0.03)
    assert max(loudness([first, second])) < 50  # silence, give or take codec noise
    track.stop()


def test_stopped_track_raises():
    asyncio.run(_stopped_track_raises())


async def _stopped_track_raises():
    track = ResilientAudioTrack(Opener(failures=0))
    track.stop()
    with pytest.raises(MediaStreamError):
        await track.recv()
