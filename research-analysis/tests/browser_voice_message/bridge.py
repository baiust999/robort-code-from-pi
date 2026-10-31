"""Real ScreenHub behind a WebSocket (/op = dashboard data channel, /ctl = test
queries) plus a stub of P2's POST /voice that runs the real decode_voice_clip.
The HTTP side of /voice (key, controller host, 413/422) is covered by the
WebRTC test and the unit tests; here only the dashboard's use of it matters."""
import asyncio, json, logging, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, "/home/pi/robot/pi")
import websockets
from common.logging_setup import EventLogger
from p2_media.talkback import ScreenHub, decode_voice_clip

KEY = "browser-test-key"
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
hub = ScreenHub(EventLogger(logging.getLogger("bridge")))
hub.set_controller_host("h")
uploads, op_msgs = [], []
loop = None

class Screen:
    readyState = "open"
    def send(self, d): pass
hub.screen_attached(Screen())
n = 0

class Op:
    def __init__(self, ws): self.ws, self.readyState = ws, "open"
    def send(self, d):
        op_msgs.append(json.loads(d)); asyncio.ensure_future(self.ws.send(d))

class Voice(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if self.headers.get("X-Controller-Key") != KEY:
            code, out = 403, {"detail": "only the robot's controller may upload a voice message"}
        else:
            try:
                pcm = decode_voice_clip(body)
                dur = asyncio.run_coroutine_threadsafe(_set(pcm), loop).result()
                uploads.append({"type": self.headers.get("Content-Type"), "bytes": len(body), "duration_s": dur})
                code, out = 200, {"id": hub.voice_id, "duration_s": dur}
            except ValueError as e:
                code, out = 422, {"detail": str(e)}
        data = json.dumps(out).encode()
        self.send_response(code); self._cors(); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, *a): pass

async def _set(pcm):
    return hub.set_voice_clip(pcm, "browser")

async def handler(ws):
    global n
    if ws.request.path == "/op":
        n += 1; sid = f"s{n}"
        hub.grant_control(sid, "h"); hub.operator_connected(sid, Op(ws))
        try:
            async for m in ws: hub.handle_operator_message(sid, m)
        finally: hub.operator_closed(sid)
    else:
        async for m in ws:
            await ws.send(json.dumps({"playing": hub.voice_playing, "loaded": hub.voice_pcm is not None,
                                      "uploads": uploads, "op": [m for m in op_msgs if m["type"] != "talk_status"]}))

async def main():
    global loop
    loop = asyncio.get_running_loop()
    srv = ThreadingHTTPServer(("127.0.0.1", 18193), Voice)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with websockets.serve(handler, "127.0.0.1", 18190):
        await asyncio.Future()
asyncio.run(main())
