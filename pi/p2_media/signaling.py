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

from aiortc import RTCPeerConnection, RTCSessionDescription

from common.logging_setup import EventLogger

from .media import AudioStreamTrack, SilentAudioTrack, SyntheticVideoTrack, VideoStreamTrack


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
) -> tuple[PeerSession, RTCSessionDescription]:
    """Create a peer connection, attach outbound tracks, and answer the offer."""
    pc = RTCPeerConnection()

    video_track = track_factory.make_video()
    audio_track = track_factory.make_audio()
    pc.addTrack(video_track)
    pc.addTrack(audio_track)

    @pc.on("connectionstatechange")
    async def _on_state_change() -> None:
        log.info(
            "WEBRTC_STATE",
            "peer connection state changed",
            session=session_id,
            state=pc.connectionState,
        )
        if pc.connectionState in ("failed", "closed"):
            await pc.close()

    offer = RTCSessionDescription(sdp=offer_sdp, type=offer_type)
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    log.info("WEBRTC_OFFER", "negotiated peer connection", session=session_id)
    return PeerSession(pc, session_id), pc.localDescription
