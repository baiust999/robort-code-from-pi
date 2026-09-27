"""WebRTC SDP offer/answer exchange, Section 8.10.2.1.

P2 speaks a minimal signaling protocol: the dashboard POSTs its SDP offer to
``/webrtc/offer`` and receives an SDP answer in the same response — there is
no separate signaling channel or trickle ICE round-trip, which keeps the
local-mesh deployment simple (no STUN/TURN needed for the answer itself; the
STUN server from P1's ``/api/ice-config`` is only used for candidate
gathering inside the browser).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aiortc import RTCPeerConnection, RTCSessionDescription

from common.logging_setup import EventLogger

from .media import AudioStreamTrack, SilentAudioTrack, SyntheticVideoTrack, VideoStreamTrack
from .talkback import ScreenAudioTrack, ScreenHub, ScreenVideoTrack

# Label of the data channel both the dashboard and the Robot Screen open.
SCREEN_CHANNEL_LABEL = "screen"


@dataclass
class TrackFactory:
    """Produces the outbound tracks for one peer connection."""

    make_video: "callable[[], VideoStreamTrack]"
    make_audio: "callable[[], AudioStreamTrack]"


def default_track_factory(width: int, height: int, framerate: int) -> TrackFactory:
    return TrackFactory(
        make_video=lambda: SyntheticVideoTrack(width, height, framerate),
        make_audio=lambda: SilentAudioTrack(),
    )


class PeerSession:
    """One negotiated WebRTC connection to a dashboard."""

    def __init__(self, pc: RTCPeerConnection, session_id: str) -> None:
        self.pc = pc
        self.session_id = session_id

    async def close(self) -> None:
        await self.pc.close()


async def negotiate(
    offer_sdp: str,
    offer_type: str,
    *,
    track_factory: TrackFactory,
    session_id: str,
    log: EventLogger,
    hub: ScreenHub | None = None,
    on_closed: Callable[[str], None] | None = None,
) -> tuple[PeerSession, RTCSessionDescription]:
    """Create a peer connection, attach outbound tracks, and answer the offer.

    When the dashboard offers sendrecv transceivers and a ``screen`` data
    channel, the operator's inbound media and messages are handed to
    ``hub`` for the Robot Screen (Section 16). A recv-only offer still works
    and simply never sends anything back.
    """
    pc = RTCPeerConnection()
    closed = False

    video_track = track_factory.make_video()
    audio_track = track_factory.make_audio()
    pc.addTrack(video_track)
    pc.addTrack(audio_track)

    def _closed() -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        if hub is not None:
            hub.operator_closed(session_id)
        if on_closed is not None:
            on_closed(session_id)

    if hub is not None:

        @pc.on("track")
        def _on_track(track) -> None:
            log.info("WEBRTC_TRACK_IN", "operator track received", session=session_id, kind=track.kind)
            hub.attach_operator_track(session_id, track)

        @pc.on("datachannel")
        def _on_datachannel(channel) -> None:
            if channel.label != SCREEN_CHANNEL_LABEL:
                return

            @channel.on("message")
            def _on_message(message) -> None:
                hub.handle_operator_message(session_id, message)

            @channel.on("open")
            def _on_open() -> None:
                hub.operator_connected(session_id, channel)

            @channel.on("close")
            def _on_close() -> None:
                hub.operator_closed(session_id)

            hub.operator_connected(session_id, channel)

    @pc.on("connectionstatechange")
    async def _on_state_change() -> None:
        log.info(
            "WEBRTC_STATE",
            "peer connection state changed",
            session=session_id,
            state=pc.connectionState,
        )
        if pc.connectionState in ("failed", "closed"):
            _closed()
            await pc.close()

    offer = RTCSessionDescription(sdp=offer_sdp, type=offer_type)
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    log.info("WEBRTC_OFFER", "negotiated peer connection", session=session_id)
    return PeerSession(pc, session_id), pc.localDescription


async def negotiate_screen(
    offer_sdp: str,
    offer_type: str,
    *,
    hub: ScreenHub,
    log: EventLogger,
) -> tuple[RTCPeerConnection, RTCSessionDescription]:
    """Answer the Robot Screen kiosk's recv-only offer with the operator relay tracks."""
    pc = RTCPeerConnection()
    pc.addTrack(ScreenVideoTrack(hub))
    pc.addTrack(ScreenAudioTrack(hub))
    screen_channel = None

    @pc.on("datachannel")
    def _on_datachannel(channel) -> None:
        nonlocal screen_channel
        if channel.label != SCREEN_CHANNEL_LABEL:
            return
        screen_channel = channel

        @channel.on("open")
        def _on_open() -> None:
            hub.screen_attached(channel)

        @channel.on("message")
        def _on_message(message) -> None:
            hub.handle_screen_message(message)

        @channel.on("close")
        def _on_close() -> None:
            hub.screen_detached(channel)

        # aiortc usually delivers the channel already open, in which case
        # the "open" event never fires.
        if channel.readyState == "open":
            hub.screen_attached(channel)

    @pc.on("connectionstatechange")
    async def _on_state_change() -> None:
        log.info("SCREEN_STATE", "robot screen connection changed", state=pc.connectionState)
        if pc.connectionState in ("failed", "closed"):
            if screen_channel is not None:
                hub.screen_detached(screen_channel)
            await pc.close()

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type=offer_type))
    await pc.setLocalDescription(await pc.createAnswer())
    log.info("SCREEN_OFFER", "robot screen connected")
    return pc, pc.localDescription
