"""WebSocket client registry and broadcast fan-out, Section 8.10.1.

Multiple dashboards may connect, but only one holds the controller role; the
rest are observers whose commands (motor, servo and stop alike) are rejected.
Only a client that presented the controller key may hold the slot. The most
recent such client takes it over, demoting the previous holder to observer,
and it is released when its holder disconnects.
"""

from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from common import protocol
from common.logging_setup import EventLogger


@dataclass
class Client:
    """One connected dashboard."""

    id: str
    socket: WebSocket
    host: str = "unknown"
    role: str = protocol.ROLE_OBSERVER
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=32))

    @property
    def is_controller(self) -> bool:
        return self.role == protocol.ROLE_CONTROLLER


class WebSocketHub:
    """Owns connected clients and the outbound broadcast path."""

    def __init__(self, log: EventLogger) -> None:
        self._log = log
        self._clients: dict[str, Client] = {}
        self._controller_id: str | None = None
        self._ids = itertools.count(1)

    @property
    def client_count(self) -> int:
        return len(self._clients)

    @property
    def controller_id(self) -> str | None:
        return self._controller_id

    @property
    def controller_host(self) -> str | None:
        client = self._clients.get(self._controller_id) if self._controller_id else None
        return client.host if client is not None else None

    def has_controller(self) -> bool:
        return self._controller_id is not None

    async def register(self, socket: WebSocket) -> Client:
        await socket.accept()
        host = socket.client.host if socket.client else "unknown"
        client = Client(id=f"c{next(self._ids)}", socket=socket, host=host)
        self._clients[client.id] = client
        self._log.info(
            "WS_CONNECT",
            "client connected",
            client=client.id,
            host=host,
            total=len(self._clients),
        )
        return client

    def unregister(self, client: Client) -> None:
        self._clients.pop(client.id, None)
        if self._controller_id == client.id:
            self._controller_id = None
            self._log.info("WS_CONTROLLER_RELEASED", "controller slot free", client=client.id)
        self._log.info(
            "WS_DISCONNECT", "client disconnected", client=client.id, total=len(self._clients)
        )

    def claim_role(self, client: Client, requested: str, authorized: bool) -> Client | None:
        """Assign ``client`` its role; controller needs ``authorized`` (the right key).

        An authorized claim always wins, taking the slot over from any other
        holder. Returns the client demoted by that takeover, if any, so the
        caller can tell it.
        """
        if requested != protocol.ROLE_CONTROLLER or not authorized:
            if self._controller_id == client.id:
                self._controller_id = None
            client.role = protocol.ROLE_OBSERVER
            return None

        previous = None
        if self._controller_id not in (None, client.id):
            previous = self._clients.get(self._controller_id)
            if previous is not None:
                previous.role = protocol.ROLE_OBSERVER
            self._log.info(
                "WS_TAKEOVER",
                "controller taken over",
                client=client.id,
                host=client.host,
                previous=self._controller_id,
            )
        self._controller_id = client.id
        client.role = protocol.ROLE_CONTROLLER
        return previous

    async def send(self, client: Client, message: dict[str, Any]) -> None:
        try:
            await client.socket.send_json(message)
        except Exception:  # noqa: BLE001 - disconnect races are expected
            self._log.debug("WS_SEND_FAIL", "send failed", client=client.id)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Fan a message out to every client concurrently.

        A slow or half-dead socket must not delay the 200ms cadence for the
        others, so sends are gathered and their failures swallowed.
        """
        if not self._clients:
            return
        await asyncio.gather(
            *(self.send(client, message) for client in list(self._clients.values())),
            return_exceptions=True,
        )
