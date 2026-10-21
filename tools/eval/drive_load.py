#!/usr/bin/env python3
"""Sustained drive load over the real control WebSocket, for the E8
pure-driving resource condition (no media stream connected).

Models wslatency.py's controller session exactly: hello handshake, a 500 ms
heartbeat, incrementing seq on every frame. It keeps a motor command refreshed
well inside the 2000 ms dead-man window so the robot drives continuously for
the duration, alternating direction periodically, then guarantees a stop_all on
exit (normal, exception or signal). The key is read from the ROBOT_KEY env var
so it never appears in an argument list.

    ROBOT_KEY=... drive_load.py --duration 300 --speed 150
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
import time

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]


async def drive(host: str, port: int, key: str, duration: float,
                speed: int, flip_s: float, refresh_s: float) -> int:
    url = f"ws://{host}:{port}/control/ws"
    seq = 0

    def nxt(msg: dict) -> str:
        nonlocal seq
        seq += 1
        return json.dumps({**msg, "seq": seq})

    async with connect(url, open_timeout=10) as socket:
        await socket.send(nxt({"type": "hello", "role": "controller", "key": key}))
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
        if ack.get("role") != "controller":
            print(f"refused: role={ack.get('role')} auth={ack.get('auth')} "
                  "(is the dashboard still holding the controller role?)",
                  file=sys.stderr)
            return 2
        print(f"controller session up; driving {duration:.0f}s at PWM {speed}, "
              f"flip every {flip_s:.0f}s", flush=True)

        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop.set)
            except (NotImplementedError, RuntimeError):
                pass

        async def reader() -> None:
            try:
                async for _ in socket:
                    pass
            except Exception:  # noqa: BLE001
                pass

        async def heartbeat() -> None:
            while not stop.is_set():
                await socket.send(nxt({"type": "heartbeat"}))
                await asyncio.sleep(0.5)

        reader_task = asyncio.create_task(reader())
        heartbeat_task = asyncio.create_task(heartbeat())
        start = time.monotonic()
        direction = "F"
        last_flip = start
        sent = 0
        try:
            while time.monotonic() - start < duration and not stop.is_set():
                now = time.monotonic()
                if now - last_flip >= flip_s:
                    direction = "B" if direction == "F" else "F"
                    last_flip = now
                await socket.send(nxt({"type": "motor", "dir": direction, "speed": speed}))
                sent += 1
                if sent % 30 == 0:
                    print(f"  {now - start:.0f}s driving ({direction})", flush=True)
                await asyncio.sleep(refresh_s)
        finally:
            # Guaranteed stop, whatever happened above.
            try:
                await asyncio.wait_for(socket.send(nxt({"type": "stop_all"})), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass
            heartbeat_task.cancel()
            reader_task.cancel()
            for task in (heartbeat_task, reader_task):
                try:
                    await task
                except (asyncio.CancelledError, Exception):  # noqa: BLE001
                    pass
        elapsed = time.monotonic() - start
        print(f"done: {sent} motor frames over {elapsed:.0f}s; stop_all sent", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--duration", type=float, default=300)
    parser.add_argument("--speed", type=int, default=150)
    parser.add_argument("--flip-s", type=float, default=5.0)
    parser.add_argument("--refresh-s", type=float, default=0.3)
    args = parser.parse_args()
    key = os.environ.get("ROBOT_KEY", "")
    if not key:
        print("ROBOT_KEY not set", file=sys.stderr)
        return 2
    try:
        return asyncio.run(drive(args.host, args.port, key, args.duration,
                                 args.speed, args.flip_s, args.refresh_s))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
