#!/usr/bin/env python3
"""Guided E3 emergency-stop distance trials (paper Section 5.1, Table 5.4).

Drives the robot forward over the real control WebSocket and sends the same
`stop_all` message the dashboard EMERGENCY STOP button sends. The operator
supplies the two human parts of the protocol:

  1. press Enter the instant the reference mark on the robot crosses the line
     (this sends stop_all, exactly as pressing the dashboard button would);
  2. tape-measure line -> mark at rest and type the distance in cm.

Each trial is appended to results/estop.csv through record.py's own sheet
definition, so trial numbering and columns match the existing rows. Distances
are only ever typed by the operator; nothing is estimated here.

A motor command is refreshed inside the 2000 ms dead-man window and a stop_all
is guaranteed on exit, on a timeout (--max-drive) and on Ctrl-C.

    ROBOT_KEY=... ./estop_assist.py --speed 60 --trials 13 --tester SA
    ROBOT_KEY=... ./estop_assist.py --speed 120 --trials 11 --tester SA
    ROBOT_KEY=... ./estop_assist.py --speed 180 --trials 13 --tester SA --video

At the distance prompt: a number records the trial, `r` repeats it without
recording (bad run), `q` ends the session. --video also asks for stop_time_s.
Run it in your own terminal; it needs the keyboard.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso  # noqa: E402
from record import SHEETS, columns_for, next_index  # noqa: E402

try:
    from websockets.asyncio.client import connect
except ImportError:  # websockets < 14
    from websockets.client import connect  # type: ignore[no-redef]


async def ainput(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))


def log_trial(path: Path, args: argparse.Namespace, distance: float,
              stop_time: str) -> int:
    sheet = SHEETS["estop"]
    row = {"speed_pwm": args.speed, "surface": args.surface,
           "distance_cm": f"{distance:g}", "stop_time_s": stop_time,
           "tester": args.tester, "notes": ""}
    row["trial"] = next_index(sheet, path, row)
    row["iso_ts"] = now_iso()
    append_row(path, columns_for("estop", sheet), row)
    return row["trial"]


async def run(args: argparse.Namespace) -> int:
    key = os.environ.get("ROBOT_KEY", "")
    if not key and not args.no_robot:
        print("ROBOT_KEY not set", file=sys.stderr)
        return 2
    out = Path(args.out)
    done = 0

    if args.no_robot:
        socket = None
    else:
        socket = await connect(f"ws://{args.host}:{args.port}/control/ws", open_timeout=10)
        seq = 0

        async def send(msg: dict) -> None:
            nonlocal seq
            seq += 1
            await socket.send(json.dumps({**msg, "seq": seq}))

        await send({"type": "hello", "role": "controller", "key": key})
        ack = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
        if ack.get("role") != "controller":
            print(f"refused: role={ack.get('role')} auth={ack.get('auth')} "
                  "(close the dashboard controller session first)", file=sys.stderr)
            return 2

        async def reader() -> None:
            try:
                async for _ in socket:
                    pass
            except Exception:  # noqa: BLE001
                pass

        async def heartbeat() -> None:
            while True:
                await send({"type": "heartbeat"})
                await asyncio.sleep(0.5)

        background = [asyncio.create_task(reader()), asyncio.create_task(heartbeat())]

    async def drive_until_enter() -> None:
        """Drive forward until the operator presses Enter, then stop_all."""
        enter = asyncio.create_task(ainput("  driving... press ENTER as the mark crosses the line: "))
        loop = asyncio.get_running_loop()
        deadline = loop.time() + args.max_drive
        try:
            while not enter.done() and loop.time() < deadline:
                if socket:
                    await send({"type": "motor", "dir": "F", "speed": args.speed})
                await asyncio.wait({enter}, timeout=0.3)
        finally:
            if socket:
                await send({"type": "stop_all"})
        if not enter.done():
            print("\n  max-drive reached: stop_all sent automatically. Press ENTER.")
            await enter

    try:
        while done < args.trials:
            print(f"\nTrial {done + 1}/{args.trials}  PWM {args.speed}  ({args.surface})")
            reply = await ainput("  robot behind the line, clear path ahead. ENTER to start (q to quit): ")
            if reply.strip().lower() == "q":
                break
            await drive_until_enter()
            while True:
                reply = (await ainput("  distance line->mark at rest, cm (r=repeat, q=quit): ")).strip().lower()
                if reply in ("r", "q"):
                    break
                try:
                    distance = float(reply)
                except ValueError:
                    print("  enter a number")
                    continue
                stop_time = (await ainput("  stop_time_s (blank to skip): ")).strip() if args.video else ""
                trial = log_trial(out, args, distance, stop_time)
                done += 1
                print(f"  logged: PWM {args.speed} trial {trial} = {distance:g} cm")
                break
            if reply == "q":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        if socket:
            try:
                await send({"type": "stop_all"})
            except Exception:  # noqa: BLE001
                pass
            for task in background:
                task.cancel()
            await socket.close()
    print(f"\nlogged {done} trial(s) at PWM {args.speed} to {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--speed", type=int, required=True, choices=(60, 120, 180))
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--surface", default="concrete")
    parser.add_argument("--tester", default="")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--max-drive", type=float, default=6.0,
                        help="seconds before an automatic stop_all (default 6)")
    parser.add_argument("--video", action="store_true", help="also prompt for stop_time_s")
    parser.add_argument("--out", default=str(RESULTS_DIR / "estop.csv"))
    parser.add_argument("--no-robot", action="store_true",
                        help="do not connect or drive; test the logging only")
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
