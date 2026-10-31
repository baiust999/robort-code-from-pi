"""End-to-end check of the repeating voice message over real WebRTC.

Starts an isolated P2 (MOCK_HARDWARE=1, own port, own key, own ROBOT_ROOT)
and a fake P1 that names 127.0.0.1 as the controller, then drives it with
aiortc peers standing in for the dashboard and for the Robot Screen kiosk.
Video is received but kept tiny (160x120 at 5 fps) to keep the Pi's load down.

The fake dashboard behaves like Chrome with the mic acquired: it always sends
audio, silence while not talking (a disabled track) and a 440 Hz tone while
"Hold to talk" is held. The voice message is a 1 kHz tone, so the kiosk's
received audio shows which source P2 is playing.

Usage: venv/bin/python run.py <scratch dir>
"""
import asyncio, fractions, io, json, os, subprocess, sys, time, urllib.request
import http.server, threading

import av
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import MediaStreamTrack

REPO = "/home/pi/robot"
P2_PORT, P1_PORT, KEY = 18443, 18180, "voice-test-key"
BASE = f"http://127.0.0.1:{P2_PORT}"
RATE = 48000
results = []


def check(name, ok, extra=""):
    results.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{extra}]" if extra else ""), flush=True)


# --- fake P1: only /api/controller, answering "127.0.0.1" ----------------------------
class P1(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"host": "127.0.0.1"}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass


# --- operator audio: silence, or 440 Hz while talking -----------------------------
class OperatorMic(MediaStreamTrack):
    kind = "audio"
    def __init__(self):
        super().__init__(); self.talking = False; self.n = 0; self.t0 = None
    async def recv(self):
        if self.t0 is None: self.t0 = time.monotonic()
        wait = self.t0 + self.n * 960 / RATE - time.monotonic()
        if wait > 0: await asyncio.sleep(wait)
        idx = np.arange(self.n * 960, (self.n + 1) * 960)
        pcm = (8000 * np.sin(2 * np.pi * 440 * idx / RATE)).astype(np.int16) if self.talking else np.zeros(960, np.int16)
        f = av.AudioFrame.from_ndarray(pcm.reshape(1, -1), format="s16", layout="mono")
        f.sample_rate = RATE; f.pts = self.n * 960; f.time_base = fractions.Fraction(1, RATE)
        self.n += 1
        return f


def tone_webm(seconds, freq=1000, amp=6000):
    buf = io.BytesIO()
    with av.open(buf, "w", format="webm") as out:
        st = out.add_stream("libopus", rate=RATE, layout="mono")
        n = int(seconds * RATE); pcm = (amp * np.sin(2 * np.pi * freq * np.arange(n) / RATE)).astype(np.int16)
        for s in range(0, n, 960):
            fr = av.AudioFrame.from_ndarray(pcm[s:s + 960].reshape(1, -1), format="s16", layout="mono")
            fr.sample_rate = RATE; fr.pts = s
            for p in st.encode(fr): out.mux(p)
        for p in st.encode(None): out.mux(p)
    return buf.getvalue()


def post(path, body, headers):
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, e.read().decode()


def health():
    return json.load(urllib.request.urlopen(BASE + "/health", timeout=5))


async def _drain(track):
    while True:
        try: await track.recv()
        except Exception: return


# --- kiosk: records what P2 sends to the robot speaker ------------------------------
class Kiosk:
    def __init__(self):
        # (monotonic, label, seconds) per received frame; P2 sends 60 ms packets.
        self.timeline = []  # label: "1k", "440", "silence" or "other"
        self.pc = RTCPeerConnection()
    async def start(self):
        self.pc.addTransceiver("video", direction="recvonly")
        self.pc.addTransceiver("audio", direction="recvonly")
        self.ch = self.pc.createDataChannel("screen")
        @self.pc.on("track")
        def on_track(track):
            if track.kind == "audio": asyncio.ensure_future(self._consume(track))
            else: asyncio.ensure_future(_drain(track))
        await self.pc.setLocalDescription(await self.pc.createOffer())
        st, ans = post("/webrtc/screen-offer", json.dumps({"sdp": self.pc.localDescription.sdp, "type": "offer"}).encode(),
                       {"Content-Type": "application/json"})
        assert st == 200, (st, ans)
        await self.pc.setRemoteDescription(RTCSessionDescription(ans["sdp"], ans["type"]))
    async def _consume(self, track):
        while True:
            try: f = await track.recv()
            except Exception: return
            x = f.to_ndarray().reshape(-1, len(f.layout.channels))[:, 0].astype(np.float32) if f.format.is_packed else f.to_ndarray()[0].astype(np.float32)
            rms = float(np.sqrt(np.mean(x * x)))
            if rms < 300: label = "silence"
            else:
                spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
                hz = np.argmax(spec) * f.sample_rate / len(x)
                label = "1k" if abs(hz - 1000) < 80 else "440" if abs(hz - 440) < 60 else "other"
            self.timeline.append((time.monotonic(), label, f.samples / f.sample_rate))
    def frames(self, t_from, t_to):
        return [(l, d) for t, l, d in self.timeline if t_from <= t < t_to]
    def share(self, t_from, t_to, label):
        fr = self.frames(t_from, t_to); total = sum(d for _, d in fr)
        return round(sum(d for l, d in fr if l == label) / total, 2) if total else 0.0
    def segments(self, t_from, t_to, label):
        """Lengths in seconds of runs of `label`, gaps of up to 100 ms bridged.
        The first and last run may be cut off by the window."""
        runs, cur, gap = [], 0.0, 0.0
        for l, d in self.frames(t_from, t_to):
            if l == label: cur += d + gap; gap = 0.0
            elif cur:
                gap += d
                if gap > 0.1: runs.append(round(cur, 2)); cur, gap = 0.0, 0.0
        if cur: runs.append(round(cur, 2))
        return runs


class Dashboard:
    def __init__(self, key):
        self.key = key; self.pc = RTCPeerConnection(); self.mic = OperatorMic(); self.msgs = []
    async def start(self):
        self.pc.addTransceiver("video", direction="recvonly")
        self.pc.addTransceiver(self.mic, direction="sendrecv")
        self.ch = self.pc.createDataChannel("screen")
        opened = asyncio.Event()
        self.ch.on("open", opened.set)
        self.ch.on("message", lambda m: self.msgs.append(json.loads(m)))
        self.pc.on("track", lambda track: asyncio.ensure_future(_drain(track)))
        await self.pc.setLocalDescription(await self.pc.createOffer())
        st, ans = post("/webrtc/offer", json.dumps({"sdp": self.pc.localDescription.sdp, "type": "offer", "key": self.key}).encode(),
                       {"Content-Type": "application/json"})
        assert st == 200, (st, ans)
        await self.pc.setRemoteDescription(RTCSessionDescription(ans["sdp"], ans["type"]))
        await asyncio.wait_for(opened.wait(), 15)
        return ans["role"]
    def send(self, **m): self.ch.send(json.dumps(m))
    def last(self, kind):
        return next((m for m in reversed(self.msgs) if m["type"] == kind), None)


async def main(scratch):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", P1_PORT), P1)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    env = dict(os.environ, MOCK_HARDWARE="1", P2_PORT=str(P2_PORT), P2_HOST="127.0.0.1", P1_PORT=str(P1_PORT),
               CONTROLLER_KEY=KEY, ROBOT_ROOT=scratch, VIDEO_WIDTH="160", VIDEO_HEIGHT="120", VIDEO_FPS="5", PYTHONPATH=f"{REPO}/pi")
    log = open(f"{scratch}/p2_stdout.txt", "w")
    p2 = subprocess.Popen([f"{REPO}/venv/bin/python", "-m", "p2_media.main"], cwd=f"{REPO}/pi", env=env, stdout=log, stderr=log)
    print(f"test P2 pid {p2.pid} on :{P2_PORT}", flush=True)
    try:
        for _ in range(60):
            try: health(); break
            except Exception: await asyncio.sleep(0.5)
        await asyncio.sleep(1.5)  # first controller poll of the fake P1

        kiosk = Kiosk(); await kiosk.start()
        dash = Dashboard(KEY); role = await dash.start()
        check("dashboard with key is controller", role == "controller", role)
        await asyncio.sleep(2)
        got = sum(d for _, _, d in kiosk.timeline)
        check("kiosk receives audio from P2 in real time", got > 1.2, f"{got:.2f} s of audio in ~2 s")
        check("new dashboard gets voice_status (no clip)", (dash.last("voice_status") or {}).get("has_clip") is False)

        st, body = post("/voice", tone_webm(1.0), {"Content-Type": "audio/webm", "X-Controller-Key": "wrong"})
        check("upload with wrong key refused (403)", st == 403, st)
        st, body = post("/voice", b"not audio" * 50, {"Content-Type": "audio/webm", "X-Controller-Key": KEY})
        check("unreadable upload refused (422)", st == 422, st)
        st, body = post("/voice", tone_webm(1.0), {"Content-Type": "audio/webm", "X-Controller-Key": KEY})
        check("upload accepted", st == 200 and abs(body["duration_s"] - 1.0) < 0.15, body)
        await asyncio.sleep(1.5)
        check("dashboard told a clip is stored", (dash.last("voice_status") or {}).get("has_clip") is True,
              [m for m in dash.msgs if m["type"] == "voice_status"])

        # 1. Loop plays with gaps, before the operator ever talked.
        dash.send(type="voice_loop_start"); t = time.monotonic(); await asyncio.sleep(8.0)
        runs = kiosk.segments(t + 0.5, time.monotonic(), "1k"); inner = runs[1:-1]
        check("loop: 1 kHz repeats (>= 2 whole tones in 7.5 s)", len(inner) >= 2, runs)
        check("loop: each whole tone ~1 s (0.85-1.15)", inner and all(0.85 <= r <= 1.15 for r in inner), runs)
        sh = kiosk.share(t + 0.5, time.monotonic(), "1k")
        check("loop: tone share ~40% (1 s on, 1.5 s gap)", 0.3 <= sh <= 0.5, sh)
        check("health says playing", health()["voice_playing"] is True and health()["floor_held"] is False)

        # 2. Hold to talk: live voice replaces the loop.
        dash.mic.talking = True; dash.send(type="media_state", talking=True, video="none")
        t = time.monotonic(); await asyncio.sleep(2.5)
        check("talking: operator 440 Hz heard", kiosk.share(t + 0.5, time.monotonic(), "440") > 0.6, kiosk.share(t + 0.5, time.monotonic(), "440"))
        check("talking: no 1 kHz loop while talking", kiosk.share(t + 0.5, time.monotonic(), "1k") == 0, kiosk.share(t + 0.5, time.monotonic(), "1k"))

        # 3. Release: floor still held, mic sends silence (as Chrome does); the loop must come back.
        dash.mic.talking = False; dash.send(type="media_state", talking=False, video="none")
        t = time.monotonic(); await asyncio.sleep(8.5)
        check("after release: floor still held by the dashboard", health()["floor_held"] is True)
        first = next((tt for tt, l, _ in kiosk.timeline if tt > t and l == "1k"), None)
        # It resumes where it paused, so up to the 1.5 s gap can come first.
        check("after release: loop back within 2.2 s", first is not None and first - t < 2.2,
              None if first is None else round(first - t, 2))
        runs = kiosk.segments(t, time.monotonic(), "1k"); inner = runs[1:-1]
        check("after release: whole tones again, not chopped (0.85-1.15 s)", len(inner) >= 2 and all(0.85 <= r <= 1.15 for r in inner), runs)
        sh = kiosk.share(t + 2.2, time.monotonic(), "1k")
        check("after release: tone share ~40% despite the silent mic", 0.3 <= sh <= 0.5, sh)

        # 4. Operator's link goes away: loop keeps playing.
        await dash.pc.close(); t = time.monotonic(); await asyncio.sleep(6.0)
        h = health()
        check("dashboard gone: floor released, loop still playing", h["floor_held"] is False and h["voice_playing"] is True,
              {k: h[k] for k in ("floor_held", "voice_playing")})
        sh = kiosk.share(t + 1.0, time.monotonic(), "1k")
        check("dashboard gone: loop still on the speaker (~40%)", 0.3 <= sh <= 0.5, sh)

        # 5. Reconnect: told it is playing; observer can't stop it; controller stops and clears.
        dash2 = Dashboard(KEY); await dash2.start(); await asyncio.sleep(1)
        vs = dash2.last("voice_status") or {}
        check("reconnected dashboard sees playing", vs.get("playing") is True and vs.get("has_clip") is True, vs)
        obs = Dashboard(None); orole = await obs.start(); await asyncio.sleep(0.5)
        obs.send(type="voice_loop_stop"); await asyncio.sleep(1)
        check("observer is view-only and can't stop it", orole == "observer" and obs.last("view_only") is not None and health()["voice_playing"] is True)
        dash2.send(type="voice_loop_stop"); t = time.monotonic(); await asyncio.sleep(2.5)
        sh = kiosk.share(t + 0.5, time.monotonic(), "1k")
        check("Stop Play: speaker silent", sh == 0 and health()["voice_playing"] is False, sh)
        dash2.send(type="voice_clear"); await asyncio.sleep(1)
        vs = dash2.last("voice_status") or {}
        check("Clear Voice: clip gone on P2 and dashboard told", health()["voice_loaded"] is False and vs.get("has_clip") is False, vs)
        dash2.send(type="voice_loop_start"); await asyncio.sleep(0.5)
        check("Start with nothing stored does nothing", health()["voice_playing"] is False)
        for pc in (dash2.pc, obs.pc, kiosk.pc): await pc.close()
    finally:
        p2.terminate()
        try: p2.wait(10)
        except subprocess.TimeoutExpired: p2.kill()
        srv.shutdown()
    logf = next((os.path.join(d, "p2_events.log") for d, _, fs in os.walk(scratch) if "p2_events.log" in fs), None)
    events = [l.split("][")[3] for l in open(logf) if "][VOICE" in l] if logf else []
    print("P2 voice events:", " ".join(events))
    print(f"\n{sum(results)}/{len(results)} passed")
    return all(results)

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main(sys.argv[1])) else 1)
