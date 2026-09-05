"""HTTP health polling for supervised processes, Section 8.8.3.2.

P3 checks liveness two ways: the OS-level ``poll()`` on the child process
(fast, catches crashes) and an HTTP ``GET /health`` every 10s (catches a
process that is alive but wedged, e.g. deadlocked on the serial port).
Three consecutive missed health checks are treated as a hang and the
process is killed so the normal crash/respawn path picks it up.
"""

from __future__ import annotations

import asyncio

import aiohttp

HEALTH_POLL_INTERVAL_S = 10.0
HEALTH_MISS_LIMIT = 3
HEALTH_TIMEOUT_S = 5.0


async def check_health(session: aiohttp.ClientSession, url: str) -> bool:
    """Return True if the endpoint responded 200 within the timeout."""
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=HEALTH_TIMEOUT_S)
        ) as resp:
            return resp.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
        return False
