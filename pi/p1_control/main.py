"""P1 control server, Section 8.8.1.

Owns the Arduino UART and the GPS receiver, broadcasts telemetry at 200ms,
accepts validated motor/servo commands, and serves the health and ICE
configuration endpoints.

Exit codes are meaningful to the P3 watchdog (Section 8.8.3.2):
    0  clean exit, or lock held by a healthy peer -> cooldown, no alarm
    1  lock acquisition failed unexpectedly
    2  Arduino handshake failed -> treated as a crash
    3  configuration invalid -> non-restartable, prevents a crash loop
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import sys
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any

# Allow `python p1_control/main.py` as well as `python -m p1_control.main`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from common import protocol
from common.config import P1Config
from common.logging_setup import EventLogger, setup_logging
from p1_control.gps_reader import GPSReader
from p1_control.lockfile import LockAcquisitionError, ProcessLock
from p1_control.ring_buffer import RingBuffer
from p1_control.safety import CommandValidator
from p1_control.serial_bridge import HandshakeError, SerialBridge
from p1_control.telemetry_log import TelemetryLog
from p1_control.websocket_hub import Client, WebSocketHub

EXIT_LOCK_HELD = 0
EXIT_LOCK_ERROR = 1
EXIT_HANDSHAKE_FAILED = 2
EXIT_CONFIG_INVALID = 3

ICE_RATE_LIMIT = 5  # requests per minute per client, Section 8.8.1.1
ICE_RATE_WINDOW_S = 60.0


class ControlServer:
    """Application state and the 200ms telemetry loop."""

    def __init__(self, config: P1Config, log: EventLogger) -> None:
        self.config = config
        self.log = log
        self.session_id = str(uuid.uuid4())
        self.started_at = time.monotonic()

        self.serial = SerialBridge(config, log)
        self.gps = GPSReader(config, log)
        self.buffer = RingBuffer()
        self.hub = WebSocketHub(log)
        self.validator = CommandValidator()
        self.telemetry_log = TelemetryLog(
            config.paths.log_dir / "telemetry.log",
            config.thresholds,
            enabled=config.telemetry_log_enabled,
        )

        self._latest_frame: dict[str, Any] = {}
        self._seq = 0
        self._broadcast_task: asyncio.Task[None] | None = None
        self._ice_requests: dict[str, deque[float]] = {}
        self._last_command_ts = 0.0

    # --- lifecycle ----------------------------------------------------------

    async def start(self) -> None:
        self.config.paths.ensure()
        self.serial.set_handlers(self._on_telemetry_frame, None)
        await self.serial.open()
        self.serial.start_reader()
        self.gps.start()
        self.telemetry_log.open()
        self._broadcast_task = asyncio.create_task(
            self._broadcast_loop(), name="telemetry-broadcast"
        )
        self.log.info(
            "SESSION_OPEN",
            "control server ready",
            session=self.session_id,
            mock=self.config.mock_hardware,
        )

    async def stop(self) -> None:
        if self._broadcast_task is not None:
            self._broadcast_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._broadcast_task
            self._broadcast_task = None

        await self.serial.close()
        self.gps.write_geojson(self.session_id)
        self.gps.stop()
        self.telemetry_log.close()
        self.log.info("SESSION_CLOSE", "control server stopped", session=self.session_id)

    # --- telemetry ----------------------------------------------------------

    def _on_telemetry_frame(self, frame: dict[str, Any]) -> None:
        self._latest_frame = frame

    def build_snapshot(self) -> dict[str, Any]:
        """Merge the Arduino frame, GPS state, and server metadata."""
        self._seq += 1
        snapshot = protocol.TelemetrySnapshot(
            seq=self._seq,
            server_ts=int(time.time() * 1000),
            serial_ok=self.serial.connected,
            ws_clients=self.hub.client_count,
            turn_status=self._turn_status(),
        )
        payload = snapshot.to_message()
        payload.update(self._latest_frame)
        payload.update(self.gps.snapshot())
        # Fields owned by P1 win over anything a frame might carry.
        payload["seq"] = snapshot.seq
        payload["server_ts"] = snapshot.server_ts
        payload["serial_ok"] = snapshot.serial_ok
        payload["ws_clients"] = snapshot.ws_clients
        payload["type"] = protocol.MSG_TELEMETRY
        return payload

    def _turn_status(self) -> str:
        """Read the status file P3 maintains, Section 8.10.3.1."""
        if not self.config.paths.run_dir:
            return "unavailable"
        path = self.config.paths.run_dir / "turn_status"
        try:
            return path.read_text(encoding="utf-8").strip() or "unavailable"
        except OSError:
            return "unavailable"

    async def _broadcast_loop(self) -> None:
        period = protocol.TELEMETRY_PERIOD_MS / 1000.0
        next_tick = time.monotonic()
        while True:
            try:
                snapshot = self.build_snapshot()
                self.buffer.append(snapshot)
                self.telemetry_log.maybe_write(snapshot)
                await self.hub.broadcast(snapshot)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 - the cadence must not stop
                self.log.exception("BROADCAST_FAIL", "telemetry broadcast failed")

            # Absolute scheduling: a slow iteration is absorbed rather than
            # accumulating drift across the session.
            next_tick += period
            delay = next_tick - time.monotonic()
            if delay < 0:
                next_tick = time.monotonic()
                delay = 0
            await asyncio.sleep(delay)

    # --- command handling ---------------------------------------------------

    async def handle_client_message(self, client: Client, message: dict[str, Any]) -> None:
        msg_type = message.get("type")

        if msg_type == protocol.MSG_HELLO:
            role = self.hub.claim_role(client, str(message.get("role", protocol.ROLE_OBSERVER)))
            await self.hub.send(
                client,
                {
                    "type": protocol.MSG_ACK,
                    "of": protocol.MSG_HELLO,
                    "role": role,
                    "session": self.session_id,
                },
            )
            return

        if msg_type == protocol.MSG_RESUME_FROM:
            await self._handle_resume(client, message)
            return

        if msg_type not in protocol.CLIENT_MESSAGE_TYPES:
            await self._reject(client, f"unsupported type {msg_type!r}")
            return

        # Observers may keep the socket alive but not actuate anything.
        if not client.is_controller:
            await self._reject(client, "observer role cannot send commands")
            return

        result = self.validator.validate(
            message,
            client_id=client.id,
        )
        if not result.ok or result.opcode is None:
            await self._reject(client, result.reason or "rejected")
            return

        for warning in result.warnings:
            self.log.warning("CMD_CLAMP", warning, client=client.id)

        await self.serial.send(result.opcode, result.argument)
        self._last_command_ts = time.monotonic()

    async def _handle_resume(self, client: Client, message: dict[str, Any]) -> None:
        try:
            last_ts = int(message.get("last_ts", 0))
        except (TypeError, ValueError):
            await self._reject(client, "last_ts is not an integer")
            return

        entries = self.buffer.since(last_ts)
        await self.hub.send(
            client,
            {
                "type": protocol.MSG_RECOVERY_BATCH,
                "entries": entries,
                "gap_ms": self.buffer.gap_ms(last_ts),
            },
        )
        self.log.info(
            "WS_RECOVERY",
            "recovery batch sent",
            client=client.id,
            entries=len(entries),
        )

    async def _reject(self, client: Client, reason: str) -> None:
        await self.hub.send(
            client, {"type": protocol.MSG_ERROR, "code": "rejected", "message": reason}
        )

    # --- health -------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        return {
            "serial_connected": self.serial.connected,
            "ws_clients": self.hub.client_count,
            "gps_fix": bool(self.gps.snapshot().get("gps_fix")),
            "uptime_s": int(time.monotonic() - self.started_at),
        }

    def ice_config(self, client_key: str) -> dict[str, Any]:
        """Issue ICE servers, rate-limited per client, Section 8.8.1.1."""
        now = time.monotonic()
        history = self._ice_requests.setdefault(client_key, deque())
        while history and now - history[0] > ICE_RATE_WINDOW_S:
            history.popleft()
        if len(history) >= ICE_RATE_LIMIT:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
        history.append(now)

        # Local-mesh mode: STUN only. A TURN relay is issued by the internet
        # overlay when that mode is enabled (Section 8.10.2.1).
        return {
            "stun": self.config.stun_url,
            "iceServers": [{"urls": self.config.stun_url}],
            "policy": "all",
            "turn": None,
        }


def create_app(server: ControlServer) -> FastAPI:
    app = FastAPI(title="Rescue Robot Control (P1)", version="1.0.0")

    # The dashboard is served from Vite in development and from the CDN or the
    # Pi in the field, so its origin varies.
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

    @app.get("/api/ice-config")
    async def ice_config(request: Request) -> dict[str, Any]:
        client_key = request.client.host if request.client else "unknown"
        return server.ice_config(client_key)

    @app.get("/api/session")
    async def session() -> dict[str, Any]:
        return {
            "session_id": server.session_id,
            "mock_hardware": server.config.mock_hardware,
            "thresholds": server.config.thresholds,
            "telemetry_period_ms": protocol.TELEMETRY_PERIOD_MS,
            "heartbeat_period_ms": protocol.HEARTBEAT_PERIOD_MS,
        }

    @app.get("/api/gps-track")
    async def gps_track() -> dict[str, Any]:
        points = server.gps.track_points()
        return {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in points],
        }

    @app.websocket(protocol.WS_PATH)
    async def control_ws(socket: WebSocket) -> None:
        client = await server.hub.register(socket)
        try:
            # Prime the client with the current state so its first render is
            # immediate rather than up to 200ms late.
            await server.hub.send(client, server.build_snapshot())
            while True:
                raw = await socket.receive_text()
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError:
                    await server._reject(client, "malformed json")
                    continue
                if not isinstance(message, dict):
                    await server._reject(client, "message must be an object")
                    continue
                await server.handle_client_message(client, message)
        except WebSocketDisconnect:
            pass
        except Exception:  # noqa: BLE001
            server.log.exception("WS_ERROR", "websocket failed", client=client.id)
        finally:
            server.hub.unregister(client)
            server.validator.reset_client(client.id)
            # A disconnecting controller must not leave the robot moving. The
            # Arduino dead-man would also catch this within 2s; this is faster.
            if client.is_controller:
                with contextlib.suppress(Exception):
                    await server.serial.send_stop()

    if server.config.static_dir is not None:
        app.mount(
            "/",
            StaticFiles(directory=str(server.config.static_dir), html=True),
            name="dashboard",
        )
    else:

        @app.get("/")
        async def index() -> JSONResponse:
            return JSONResponse(
                {
                    "service": "p1-control",
                    "session": server.session_id,
                    "ws": protocol.WS_PATH,
                    "note": "dashboard bundle not mounted; set DASHBOARD_DIR",
                }
            )

    return app


async def _serve(config: P1Config, log: EventLogger) -> int:
    server = ControlServer(config, log)
    try:
        await server.start()
    except HandshakeError as exc:
        log.error("HANDSHAKE_FAIL", str(exc))
        await server.stop()
        return EXIT_HANDSHAKE_FAILED

    app = create_app(server)
    uvicorn_config = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        log_level="warning",
        access_log=False,
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
    )
    uvicorn_server = uvicorn.Server(uvicorn_config)
    try:
        await uvicorn_server.serve()
    finally:
        await server.stop()
    return 0


def main() -> int:
    try:
        config = P1Config.from_env()
    except Exception as exc:  # noqa: BLE001
        print(f"invalid configuration: {exc}", file=sys.stderr)
        return EXIT_CONFIG_INVALID

    config.paths.ensure()
    log = setup_logging("P1", config.paths.log_dir, "p1_events.log")

    lock = ProcessLock(config.lock_path)
    try:
        lock.acquire()
    except LockAcquisitionError as exc:
        # A healthy peer already owns the hardware. Exit cleanly so the
        # watchdog waits out its cooldown instead of counting a crash.
        log.warning("LOCK_HELD", str(exc), path=str(config.lock_path))
        return EXIT_LOCK_HELD
    except OSError as exc:
        log.error("LOCK_ERROR", f"cannot acquire lock: {exc}")
        return EXIT_LOCK_ERROR

    try:
        return asyncio.run(_serve(config, log))
    except KeyboardInterrupt:
        log.info("SIGINT", "interrupted")
        return 0
    finally:
        lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
