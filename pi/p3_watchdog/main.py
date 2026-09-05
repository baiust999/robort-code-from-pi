"""P3 entrypoint: supervises P1 and P2 as independent children, Section 8.8.3.

P3 is the only process systemd manages directly (see deploy/systemd); P1 and
P2 are spawned and monitored by P3 itself so that a crash in either one is
noticed and repaired without restarting the whole tree.
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys

import aiohttp

from common.config import P3Config
from common.logging_setup import setup_logging

from .supervisor import SupervisedProcess, run_supervised


async def _run(config: P3Config) -> int:
    log = setup_logging("P3", config.paths.log_dir, "p3_events.log")
    log.info("P3_START", "watchdog starting", enable_overlay=config.enable_overlay)

    env = dict(os.environ)
    children = [
        SupervisedProcess(
            name="P1", cmd=config.p1_cmd, health_url=config.p1_health_url, log=log, env=env
        ),
        SupervisedProcess(
            name="P2", cmd=config.p2_cmd, health_url=config.p2_health_url, log=log, env=env
        ),
    ]

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _handle_signal(sig_name: str) -> None:
        log.info("P3_SIGNAL", "shutdown signal received", signal=sig_name)
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _handle_signal, sig.name)
        except NotImplementedError:
            # Windows has no add_signal_handler for SIGTERM; SIGINT still
            # works via the default KeyboardInterrupt path in main().
            pass

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(run_supervised(child, session, stop_event))
            for child in children
        ]
        await stop_event.wait()
        for child in children:
            child.stop()
        await asyncio.gather(*tasks, return_exceptions=True)

    log.info("P3_STOP", "watchdog stopped")
    return 0


def main() -> int:
    config = P3Config.from_env()
    config.paths.ensure()
    try:
        return asyncio.run(_run(config))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
