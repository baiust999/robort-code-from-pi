"""Per-child supervision state machine, Section 8.8.3.1.

Each supervised process (P1, P2) is independent: SPAWN -> MONITOR, and on
crash or a health-check hang, MONITOR -> CRASH -> a 10s cooldown -> SPAWN
again. A process that exits with EXIT_LOCK_HELD (0) is not restarted on the
usual crash path immediately - it means a healthy peer already owns the
hardware lock, most likely this supervisor's own previous instance during a
restart race, so the cooldown still applies but the event is logged
distinctly from a real crash.
"""

from __future__ import annotations

import asyncio
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum

import aiohttp

from common.logging_setup import EventLogger

from .health import HEALTH_MISS_LIMIT, HEALTH_POLL_INTERVAL_S, check_health

COOLDOWN_S = 10.0
POLL_INTERVAL_S = 1.0

# Exit codes a supervised process may use to signal "do not respawn me
# frantically" conditions. Mirrors p1_control.main / p2_media.main.
EXIT_LOCK_HELD = 0
EXIT_CONFIG_INVALID = 3
NON_CRASH_EXIT_CODES = {EXIT_CONFIG_INVALID}


class ChildState(str, Enum):
    SPAWNING = "spawning"
    MONITORING = "monitoring"
    COOLDOWN = "cooldown"
    STOPPED = "stopped"


@dataclass
class SupervisedProcess:
    """Owns the lifecycle of one child process (P1 or P2)."""

    name: str
    cmd: list[str]
    health_url: str
    log: EventLogger
    env: dict[str, str] | None = None

    state: ChildState = ChildState.STOPPED
    proc: subprocess.Popen | None = None
    health_misses: int = 0
    restart_count: int = 0
    last_exit_code: int | None = None
    _stopping: bool = field(default=False, init=False)

    def is_alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def spawn(self) -> None:
        self.proc = subprocess.Popen(self.cmd, env=self.env)
        self.state = ChildState.MONITORING
        self.health_misses = 0
        self.log.info(
            "PROC_SPAWN", "process started", name=self.name, pid=self.proc.pid, cmd=" ".join(self.cmd)
        )

    def adopt(self, pid: int) -> None:
        """Attach to an already-running orphan instead of spawning a new one.

        Section 8.8.3.1: if P3 itself restarts (e.g. after an update), P1/P2
        may still be running from before. Killing and respawning them would
        drop the Arduino connection unnecessarily, so P3 first checks for a
        live PID recorded from a prior run and adopts it via /health instead
        of starting a duplicate.
        """
        self.state = ChildState.MONITORING
        self.health_misses = 0
        self.log.info("PROC_ADOPT", "adopted orphan process", name=self.name, pid=pid)

    def mark_crashed(self, exit_code: int | None) -> None:
        self.last_exit_code = exit_code
        self.state = ChildState.COOLDOWN
        self.proc = None
        if exit_code in NON_CRASH_EXIT_CODES:
            self.log.error(
                "PROC_CONFIG_INVALID",
                "process exited due to invalid config; will still retry after cooldown",
                name=self.name,
                exit_code=exit_code,
            )
        elif exit_code == EXIT_LOCK_HELD:
            self.log.warning(
                "PROC_LOCK_HELD", "process exited: lock already held", name=self.name
            )
        else:
            self.restart_count += 1
            self.log.error(
                "PROC_CRASH",
                "process exited unexpectedly",
                name=self.name,
                exit_code=exit_code,
                restart_count=self.restart_count,
            )

    def kill(self, reason: str) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.log.warning("PROC_KILL", reason, name=self.name, pid=self.proc.pid)
            self.proc.kill()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    def stop(self) -> None:
        self._stopping = True
        self.kill("supervisor shutting down")
        self.state = ChildState.STOPPED


async def run_supervised(
    child: SupervisedProcess, session: aiohttp.ClientSession, stop_event: asyncio.Event
) -> None:
    """Own the SPAWN -> MONITOR -> CRASH -> COOLDOWN loop for one child."""
    last_health_check = 0.0
    child.spawn()

    while not stop_event.is_set():
        await asyncio.sleep(POLL_INTERVAL_S)

        if child.state == ChildState.COOLDOWN:
            await asyncio.sleep(COOLDOWN_S)
            if stop_event.is_set():
                break
            child.spawn()
            last_health_check = 0.0
            continue

        if not child.is_alive():
            exit_code = child.proc.returncode if child.proc else None
            child.mark_crashed(exit_code)
            continue

        now = time.monotonic()
        if now - last_health_check >= HEALTH_POLL_INTERVAL_S:
            last_health_check = now
            healthy = await check_health(session, child.health_url)
            if healthy:
                child.health_misses = 0
            else:
                child.health_misses += 1
                child.log.warning(
                    "HEALTH_MISS",
                    "health check failed",
                    name=child.name,
                    misses=child.health_misses,
                )
                if child.health_misses >= HEALTH_MISS_LIMIT:
                    child.kill("health check hang: killing for respawn")
                    child.mark_crashed(None)

    child.stop()
