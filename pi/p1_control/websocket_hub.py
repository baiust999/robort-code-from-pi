"""WebSocket client registry and broadcast fan-out, Section 8.10.1.

Multiple dashboards may connect, but only one holds the controller role; the
rest are observers whose motor and servo commands are rejected. The controller
slot is claimed by the first client to send a ``hello`` with role=controller and
is released when that client disconnects.
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

    def has_controller(self) -> bool:
        return self._controller_id is not None

    async def register(self, socket: WebSocket) -> Client:
        await socket.accept()
        client = Client(id=f"c{next(self._ids)}", socket=socket)
        self._clients[client.id] = client
        self._log.info(
            "WS_CONNECT", "client connected", client=client.id, total=len(self._clients)
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

    def claim_role(self, client: Client, requested: str) -> str:
        """Assign a role, granting controller only if the slot is free."""
        if requested != protocol.ROLE_CONTROLLER:
            client.role = protocol.ROLE_OBSERVER
        elif self._controller_id in (None, client.id):
            self._controller_id = client.id
            client.role = protocol.ROLE_CONTROLLER
        else:
            client.role = protocol.ROLE_OBSERVER
            self._log.info(
                "WS_CONTROLLER_BUSY",
                "controller slot taken; assigned observer",
                client=client.id,
                holder=self._controller_id,
            )
        return client.role

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
