"""P2 entrypoint: WebRTC media server, Section 8.8.2.

Exposes ``POST /webrtc/offer`` (SDP offer in, SDP answer out) and
``GET /health``. Unlike P1, P2 does not own an exclusive hardware lock: the
camera/mic devices are opened per-session and multiple simultaneous viewers
are permitted (each gets its own PeerConnection and encoder).
"""

from __future__ import annotations

import itertools
import sys
from typing import Any

import uvicorn
from aiortc import RTCSessionDescription
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from common.config import P2Config
from common.logging_setup import EventLogger, setup_logging

from .media import open_camera_track, open_mic_track
from .signaling import PeerSession, TrackFactory, default_track_factory, negotiate

EXIT_CONFIG_INVALID = 3


class OfferRequest(BaseModel):
    sdp: str
    type: str


class AnswerResponse(BaseModel):
    sdp: str
    type: str


class MediaServer:
    """Owns active peer sessions and the track factory for this process."""

    def __init__(self, config: P2Config, log: EventLogger) -> None:
        self.config = config
        self.log = log
        self.sessions: dict[str, PeerSession] = {}
        self._ids = itertools.count(1)
        self.track_factory = self._build_track_factory()

    def _build_track_factory(self) -> TrackFactory:
        if self.config.mock_hardware:
            self.log.info("MOCK_HARDWARE", "using synthetic media tracks")
            return default_track_factory(
                self.config.width, self.config.height, self.config.framerate
            )

        def make_video():
            try:
                return open_camera_track(
                    self.config.video_device,
                    self.config.width,
                    self.config.height,
                    self.config.framerate,
                )
            except Exception as exc:  # noqa: BLE001 - fall back to synthetic on any capture failure
                self.log.warning("CAMERA_OPEN_FAIL", str(exc), device=self.config.video_device)
                from .media import SyntheticVideoTrack

                return SyntheticVideoTrack(
                    self.config.width, self.config.height, self.config.framerate
                )

        def make_audio():
            try:
                return open_mic_track(self.config.audio_device)
            except Exception as exc:  # noqa: BLE001
                self.log.warning("MIC_OPEN_FAIL", str(exc), device=self.config.audio_device)
                from .media import SilentAudioTrack

                return SilentAudioTrack()

        return TrackFactory(make_video=make_video, make_audio=make_audio)

    async def offer(self, sdp: str, sdp_type: str) -> RTCSessionDescription:
        session_id = f"s{next(self._ids)}"
        session, answer = await negotiate(
            sdp,
            sdp_type,
            track_factory=self.track_factory,
            session_id=session_id,
            log=self.log,
        )
        self.sessions[session_id] = session
        return answer

    async def close_all(self) -> None:
        for session in list(self.sessions.values()):
            await session.close()
        self.sessions.clear()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "camera_open": not self.config.mock_hardware,
            "active_streams": len(self.sessions),
            "mock_hardware": self.config.mock_hardware,
        }


def create_app(server: MediaServer) -> FastAPI:
    app = FastAPI()

    # The dashboard's origin varies (Vite dev server, the Pi's own static
    # mount, or a CDN), same rationale as P1's CORS setup.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return server.health()

    @app.post("/webrtc/offer", response_model=AnswerResponse)
    async def webrtc_offer(offer: OfferRequest) -> AnswerResponse:
        try:
            answer = await server.offer(offer.sdp, offer.type)
        except Exception as exc:  # noqa: BLE001
            server.log.error("WEBRTC_NEGOTIATE_FAIL", str(exc))
            raise HTTPException(status_code=500, detail="negotiation failed") from exc
        return AnswerResponse(sdp=answer.sdp, type=answer.type)

    return app


def main() -> int:
    try:
        config = P2Config.from_env()
    except Exception as exc:  # noqa: BLE001
        print(f"invalid configuration: {exc}", file=sys.stderr)
        return EXIT_CONFIG_INVALID

    config.paths.ensure()
    log = setup_logging("P2", config.paths.log_dir, "p2_events.log")
    server = MediaServer(config, log)
    app = create_app(server)

    log.info("P2_START", "media server starting", mock=config.mock_hardware, port=config.port)
    uvicorn.run(app, host=config.host, port=config.port, log_level="warning", access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
