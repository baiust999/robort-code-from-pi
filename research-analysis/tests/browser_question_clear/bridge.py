"""Real ScreenHub behind a WebSocket: /op = dashboard data channel, /ctl = test commands."""
import asyncio, json, logging, sys
sys.path.insert(0, "/home/pi/robot/pi")
import websockets
from common.logging_setup import EventLogger
from p2_media.talkback import ScreenHub

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
hub = ScreenHub(EventLogger(logging.getLogger("bridge")))
hub.set_controller_host("h")
screen_msgs, op_msgs = [], []

class Screen:
    readyState = "open"
    def send(self, d): screen_msgs.append(json.loads(d))
hub.screen_attached(Screen())
n = 0

class Op:
    def __init__(self, ws): self.ws, self.readyState = ws, "open"
    def send(self, d):
        op_msgs.append(json.loads(d)); asyncio.ensure_future(self.ws.send(d))

async def handler(ws):
    global n
    path = ws.request.path
    if path == "/op":
        n += 1; sid = f"s{n}"
        hub.grant_control(sid, "h"); hub.operator_connected(sid, Op(ws))
        try:
            async for m in ws: hub.handle_operator_message(sid, m)
        finally: hub.operator_closed(sid)
    else:
        async for m in ws:
            c = json.loads(m)
            if c["cmd"] == "answer":
                hub.handle_screen_message(json.dumps({"type": "question_answer", "id": hub.question["id"], "choice": c["choice"]}))
            await ws.send(json.dumps({"question": hub.question, "screen": screen_msgs, "op": op_msgs}))

async def main():
    async with websockets.serve(handler, "127.0.0.1", 18090):
        await asyncio.Future()
asyncio.run(main())
