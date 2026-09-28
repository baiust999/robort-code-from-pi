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


# --- PrivateVideoTrack --------------------------------------------------------


class FakeCamera(MediaStreamTrack):
    kind = "video"

    def __init__(self, fmt: str) -> None:
        super().__init__()
        self.fmt = fmt
        self.n = 0

    async def recv(self):
        import fractions

        import av
        import numpy as np

        await asyncio.sleep(0.001)
        shape = (48, 64, 2) if self.fmt == "yuyv422" else (72, 64)
        frame = av.VideoFrame.from_ndarray(np.full(shape, self.n % 255, np.uint8), format=self.fmt)
        frame.pts, frame.time_base = self.n * 9000, fractions.Fraction(1, 90000)
        self.n += 1
        return frame


@pytest.mark.parametrize("fmt", ["yuyv422", "yuv420p"])
def test_each_session_gets_its_own_yuv420p_frames(fmt):
    asyncio.run(_each_session_gets_its_own_frames(fmt))


async def _each_session_gets_its_own_frames(fmt):
    from p2_media.media import PrivateVideoTrack

    opened: list[FakeCamera] = []

    def open_camera() -> FakeCamera:
        opened.append(FakeCamera(fmt))
        return opened[-1]

    # Newest-frame-only, as P2 shares the real camera.
    capture = SharedCapture(open_camera, buffered=False)
    a = PrivateVideoTrack(capture.subscribe())
    b = PrivateVideoTrack(capture.subscribe())
    fa, fb = await asyncio.gather(a.recv(), b.recv())

    # Never the same object: encoder threads must not share a frame.
    assert fa is not fb
    for frame in (fa, fb):
        assert frame.format.name == "yuv420p"
        assert (frame.width, frame.height) == (64, 48 if fmt == "yuyv422" else 48)
        assert frame.time_base is not None and frame.pts is not None

    # Stopping both sessions closes the shared camera.
    a.stop()
    b.stop()
    await asyncio.sleep(0.01)
    assert len(opened) == 1 and opened[0].readyState == "ended"
