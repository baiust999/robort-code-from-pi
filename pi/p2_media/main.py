"""P2 entrypoint: WebRTC media server, Section 8.8.2.

Exposes ``POST /webrtc/offer`` (SDP offer in, SDP answer out) and
``GET /health``. Unlike P1, P2 does not own an exclusive hardware lock:
multiple simultaneous viewers are permitted, each with its own
PeerConnection and encoder, all fed from one shared camera and mic
(``SharedCapture``) since the devices themselves can only be opened once.

It also serves the Robot Screen (Section 16): ``GET /screen`` is the kiosk
page shown on the robot's own display, and ``POST /webrtc/screen-offer``
connects it — localhost only — so the operator's voice, video and messages
reach the victim. ``GET /screen/mode`` reports whether the display shows
the kiosk or the Pi desktop (for VNC); the kiosk launcher polls it, and the
kiosk page and desktop shortcut switch it with ``POST /screen/mode``
(localhost only; dashboards switch it over their data channel).
"""

from __future__ import annotations

import asyncio
import contextlib
import faulthandler
import itertools
import json
import sys
import urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from common import access, protocol
from common.config import P2Config
from common.logging_setup import EventLogger, setup_logging

from .media import (
    PrivateVideoTrack,
    ResilientAudioTrack,
    SharedCapture,
    open_camera_track,
    open_mic_track,
)
from .signaling import PeerSession, TrackFactory, default_track_factory, negotiate, negotiate_screen
from .talkback import DISPLAY_MODES, ScreenHub

EXIT_CONFIG_INVALID = 3
SCREEN_PAGE = Path(__file__).with_name("screen") / "index.html"
# Only the kiosk on the robot itself may become the Robot Screen; a remote
# host must not be able to hijack what the victim sees and hears.
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}
# How often P2 asks P1 which dashboard is the controller (talk follows it).
CONTROLLER_POLL_S = 1.0


class OfferRequest(BaseModel):
    sdp: str
    type: str
    # Controller key; without the right one the session is view-only.
    key: str | None = None


class AnswerResponse(BaseModel):
    sdp: str
    type: str
    role: str = protocol.ROLE_OBSERVER
    auth: str = access.NO_KEY
    retry_after_s: int | None = None


class DisplayMode(BaseModel):
    mode: str


class MediaServer:
    """Owns active peer sessions and the track factory for this process."""

    def __init__(self, config: P2Config, log: EventLogger) -> None:
        self.config = config
        self.log = log
        self.sessions: dict[str, PeerSession] = {}
        self._ids = itertools.count(1)
        self.track_factory = self._build_track_factory()
        self.hub = ScreenHub(log)
        self.gate = access.KeyGate(config.controller_key)
        self.screen_pc: RTCPeerConnection | None = None

    def _build_track_factory(self) -> TrackFactory:
        if self.config.mock_hardware:
            self.log.info("MOCK_HARDWARE", "using synthetic media tracks")
            return default_track_factory(
                self.config.width, self.config.height, self.config.framerate
            )

        camera = SharedCapture(
            lambda: open_camera_track(
                self.config.video_device,
                self.config.width,
                self.config.height,
                self.config.framerate,
            ),
            # Each viewer only needs the newest picture.
            buffered=False,
        )
        # Every audio frame matters, so each session gets its own queue.
        mic = SharedCapture(lambda: open_mic_track(self.config.audio_device), buffered=True)

        def make_video():
            try:
                # Each session's encoder gets frames of its own (see PrivateVideoTrack).
                return PrivateVideoTrack(camera.subscribe())
            except Exception as exc:  # noqa: BLE001 - fall back to synthetic on any capture failure
                self.log.warning("CAMERA_OPEN_FAIL", str(exc), device=self.config.video_device)
                from .media import SyntheticVideoTrack

                return SyntheticVideoTrack(
                    self.config.width, self.config.height, self.config.framerate
                )

        def make_audio():
            # Silence until the mic opens, and again if it drops off USB;
            # the track keeps retrying so no session is left silent for good.
            return ResilientAudioTrack(
                mic.subscribe,
                on_lost=lambda exc: self.log.warning(
                    "MIC_OPEN_FAIL", str(exc), device=self.config.audio_device
                ),
                on_restored=lambda: self.log.info(
                    "MIC_RESTORED", "microphone reopened", device=self.config.audio_device
                ),
            )

        return TrackFactory(make_video=make_video, make_audio=make_audio)

    async def offer(
        self, sdp: str, sdp_type: str, *, controller: bool, host: str
    ) -> RTCSessionDescription:
        session_id = f"s{next(self._ids)}"
        # Granted before negotiating so the session's first messages count.
        if controller:
            self.hub.grant_control(session_id, host)
        try:
            session, answer = await negotiate(
                sdp,
                sdp_type,
                track_factory=self.track_factory,
                session_id=session_id,
                log=self.log,
                hub=self.hub,
                on_closed=lambda sid: self.sessions.pop(sid, None),
            )
        except Exception:
            self.hub.operator_closed(session_id)
            raise
        self.sessions[session_id] = session
        return answer

    async def screen_offer(self, sdp: str, sdp_type: str) -> RTCSessionDescription:
        # A reconnecting kiosk replaces the old connection outright.
        if self.screen_pc is not None:
            await self.screen_pc.close()
        self.screen_pc, answer = await negotiate_screen(sdp, sdp_type, hub=self.hub, log=self.log)
        return answer

    def _fetch_controller_host(self) -> str | None:
        with urllib.request.urlopen(f"{self.config.p1_url}/api/controller", timeout=2) as resp:
            return json.load(resp).get("host")

    async def follow_controller(self) -> None:
        """Keep the hub's controller host in step with P1's controller slot.

        While P1 can't be reached nobody may talk: control is P1's to grant.
        """
        while True:
            try:
                host = await asyncio.to_thread(self._fetch_controller_host)
            except Exception:  # noqa: BLE001 - P1 restarting or not up yet
                host = None
            self.hub.set_controller_host(host)
            await asyncio.sleep(CONTROLLER_POLL_S)

    async def close_all(self) -> None:
        for session in list(self.sessions.values()):
            await session.close()
        self.sessions.clear()
        if self.screen_pc is not None:
            await self.screen_pc.close()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "camera_open": not self.config.mock_hardware,
            "active_streams": len(self.sessions),
            "mock_hardware": self.config.mock_hardware,
            **self.hub.health(),
        }


def create_app(server: MediaServer) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        task = asyncio.create_task(server.follow_controller(), name="follow-controller")
        yield
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    app = FastAPI(lifespan=lifespan)

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
    async def webrtc_offer(offer: OfferRequest, request: Request) -> AnswerResponse:
        host = request.client.host if request.client else "unknown"
        auth = server.gate.check(host, offer.key)
        controller = auth == access.OK
        role = protocol.ROLE_CONTROLLER if controller else protocol.ROLE_OBSERVER
        log = server.log.warning if auth in (access.BAD_KEY, access.LOCKED) else server.log.info
        log("WEBRTC_ROLE", f"viewer from {host} is {role}", host=host, role=role, auth=auth)
        try:
            answer = await server.offer(offer.sdp, offer.type, controller=controller, host=host)
        except Exception as exc:  # noqa: BLE001
            server.log.error("WEBRTC_NEGOTIATE_FAIL", str(exc))
            raise HTTPException(status_code=500, detail="negotiation failed") from exc
        return AnswerResponse(
            sdp=answer.sdp,
            type=answer.type,
            role=role,
            auth=auth,
            retry_after_s=server.gate.retry_after(host) if auth == access.LOCKED else None,
        )

    @app.post("/webrtc/screen-offer", response_model=AnswerResponse)
    async def webrtc_screen_offer(offer: OfferRequest, request: Request) -> AnswerResponse:
        if request.client is None or request.client.host not in LOCAL_HOSTS:
            raise HTTPException(status_code=403, detail="robot screen must connect from localhost")
        try:
            answer = await server.screen_offer(offer.sdp, offer.type)
        except Exception as exc:  # noqa: BLE001
            server.log.error("SCREEN_NEGOTIATE_FAIL", str(exc))
            raise HTTPException(status_code=500, detail="negotiation failed") from exc
        return AnswerResponse(sdp=answer.sdp, type=answer.type)

    @app.get("/screen")
    async def screen_page() -> FileResponse:
        return FileResponse(SCREEN_PAGE, media_type="text/html")

    @app.get("/screen/mode", response_model=DisplayMode)
    async def get_display_mode() -> DisplayMode:
        return DisplayMode(mode=server.hub.display_mode)

    @app.post("/screen/mode", response_model=DisplayMode)
    async def set_display_mode(body: DisplayMode, request: Request) -> DisplayMode:
        if request.client is None or request.client.host not in LOCAL_HOSTS:
            raise HTTPException(status_code=403, detail="display mode is set locally or via the dashboard")
        if body.mode not in DISPLAY_MODES:
            raise HTTPException(status_code=422, detail=f"mode must be one of {DISPLAY_MODES}")
        # The kiosk page (a browser) and the launcher/shortcut (curl) both
        # switch locally; name which one so a surprise switch can be traced.
        agent = request.headers.get("user-agent", "")
        via = "kiosk" if "Mozilla" in agent else (agent.split("/", 1)[0] or "unknown")
        server.hub.set_display_mode(body.mode, source=f"local:{request.client.host}:{via}")
        return DisplayMode(mode=server.hub.display_mode)

    return app


def main() -> int:
    # PyAV/FFmpeg run native code; on a segfault, dump every thread's
    # Python stack to stderr (the journal) instead of dying silently.
    faulthandler.enable()
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
    if not server.gate.enabled:
        log.warning("NO_CONTROLLER_KEY", "CONTROLLER_KEY is not set; nobody can talk to the victim")
    uvicorn.run(app, host=config.host, port=config.port, log_level="warning", access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
