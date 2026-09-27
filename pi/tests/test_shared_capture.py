"""SharedCapture: one capture device shared by every P2 session."""

import asyncio

import pytest
from aiortc.mediastreams import MediaStreamTrack

from p2_media.media import SharedCapture


class FakeDevice(MediaStreamTrack):
    kind = "audio"

    def __init__(self) -> None:
        super().__init__()
        self.n = 0

    async def recv(self):
        await asyncio.sleep(0.001)
        self.n += 1
        return self.n


def make_capture():
    opened: list[FakeDevice] = []

    def open_track() -> FakeDevice:
        opened.append(FakeDevice())
        return opened[-1]

    return SharedCapture(open_track, buffered=True), opened


def test_sessions_share_one_open_device():
    asyncio.run(_sessions_share_one_open_device())


async def _sessions_share_one_open_device():
    capture, opened = make_capture()
    a = capture.subscribe()
    b = capture.subscribe()
    assert len(opened) == 1
    # Both sessions receive frames from the same device at the same time.
    assert isinstance(await a.recv(), int)
    assert isinstance(await b.recv(), int)
    a.stop()
    b.stop()


def test_device_closes_after_last_session_and_reopens():
    asyncio.run(_device_closes_after_last_session_and_reopens())


async def _device_closes_after_last_session_and_reopens():
    capture, opened = make_capture()
    a = capture.subscribe()
    b = capture.subscribe()
    a.stop()
    assert opened[0].readyState == "live"  # b still uses it
    b.stop()
    assert opened[0].readyState == "ended"

    c = capture.subscribe()
    assert len(opened) == 2 and opened[1].readyState == "live"
    c.stop()


def test_open_failure_propagates():
    def broken():
        raise OSError("busy")

    with pytest.raises(OSError):
        SharedCapture(broken, buffered=False).subscribe()
