"""Drives the real TalkPanel / VoiceMessagePanel over CDP. Chromium's fake mic
(--use-fake-device-for-media-stream) supplies the recording."""
import asyncio, base64, json, sys, urllib.request
import websockets

S = sys.argv[1]
results = []
def check(name, ok, extra=""):
    results.append(bool(ok)); print(("PASS " if ok else "FAIL ") + name + (f"  [{extra}]" if extra else ""), flush=True)

async def main():
    tabs = json.load(urllib.request.urlopen("http://127.0.0.1:18192/json"))
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as cdp, \
               websockets.connect("ws://127.0.0.1:18190/ctl") as ctl:
        i = 0
        async def call(method, **params):
            nonlocal i; i += 1; await cdp.send(json.dumps({"id": i, "method": method, "params": params}))
            while True:
                r = json.loads(await asyncio.wait_for(cdp.recv(), 15))
                if r.get("id") == i: return r.get("result", {})
        async def js(expr):
            r = await call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
            return r.get("result", {}).get("value")
        async def hub():
            await ctl.send("{}"); return json.loads(await ctl.recv())
        async def shot(name):
            r = await call("Page.captureScreenshot")
            open(f"{S}/{name}.png", "wb").write(base64.b64decode(r["data"]))
        btn = "[...document.querySelectorAll('button')].find(b=>b.textContent.includes(%r))"
        async def has_btn(label): return await js(f"!!({btn % label})")
        async def disabled(label): return await js(f"({btn % label})?.disabled")
        async def click(label): await js(f"({btn % label}).click()")
        text = "document.body.innerText"

        await call("Emulation.setDeviceMetricsOverride", width=420, height=900, deviceScaleFactor=1, mobile=False)
        await call("Page.navigate", url="http://127.0.0.1:18191/"); await asyncio.sleep(4)
        body = await js(text)
        check("Call out button is gone", "Call out" not in body and "call-out" not in body.lower(), )
        check("voice message box is shown", "Voice message (repeats on robot)" in body)
        check("fresh: Record enabled, Start Play and Clear disabled",
              await disabled("Record Voice") is False and await disabled("Start Play") is True and await disabled("Clear Voice") is True)
        await shot("1-fresh")

        # Record ~2.5 s from the fake mic.
        await click("Record Voice"); await asyncio.sleep(2.7)
        check("recording: button shows Stop with a timer", await has_btn("Stop 0:0"), await js(f"({btn % 'Stop 0:0'})?.textContent"))
        check("recording: Start Play disabled", await disabled("Start Play") is True)
        await shot("2-recording")
        await click("Stop 0:0"); await asyncio.sleep(1)
        check("recorded: preview player shown", await js("!!document.querySelector('audio[controls]')"))
        check("recorded: hint says listen, then Start Play", "Listen above, then Start Play" in await js(text))
        check("recorded: nothing uploaded yet", (await hub())["uploads"] == [])

        await click("Start Play"); await asyncio.sleep(2)
        h = await hub()
        up = h["uploads"][-1] if h["uploads"] else {}
        check("Start Play: recording uploaded once and decoded (~2.5 s)", len(h["uploads"]) == 1 and 2.0 <= up.get("duration_s", 0) <= 3.2, up)
        check("Start Play: uploaded as WebM/Opus", "webm" in str(up.get("type")), up.get("type"))
        check("Start Play: P2 is looping", h["playing"] is True)
        body = await js(text)
        check("playing: Stop Play shown and 'Repeating on robot speaker'", await has_btn("Stop Play") and "Repeating on robot speaker" in body)
        check("playing: Record disabled", await disabled("Record Voice") is True)
        await shot("3-playing")

        await call("Page.reload"); await asyncio.sleep(4)
        body = await js(text)
        check("after reload: still shows playing (state from P2)", await has_btn("Stop Play") and "Repeating on robot speaker" in body)
        await click("Stop Play"); await asyncio.sleep(1)
        h = await hub()
        check("Stop Play: P2 stopped, clip kept", h["playing"] is False and h["loaded"] is True)
        body = await js(text)
        check("after reload + stop: 'Robot has a message loaded', Start Play enabled",
              "Robot has a message loaded" in body and await disabled("Start Play") is False)
        await click("Start Play"); await asyncio.sleep(1.5)
        h = await hub()
        check("Start Play with no local recording replays the robot's copy, no new upload",
              h["playing"] is True and len(h["uploads"]) == 1)
        await click("Stop Play"); await asyncio.sleep(1)
        await click("Clear Voice"); await asyncio.sleep(1)
        h = await hub(); body = await js(text)
        check("Clear Voice: deleted on P2, Start Play disabled again",
              h["loaded"] is False and await disabled("Start Play") is True and "Record a message" in body)
        await shot("4-cleared")

        # Recording stops by itself at 30 s.
        await click("Record Voice"); await asyncio.sleep(32)
        check("recording stops by itself at 30 s", await has_btn("Record Voice") and await js("!!document.querySelector('audio[controls]')"))
        await click("Start Play"); await asyncio.sleep(3)
        h = await hub(); up = h["uploads"][-1]
        check("30 s recording accepted by P2's decoder (29-31 s)", 29 <= up["duration_s"] <= 31.5 and h["playing"], up)
        await click("Stop Play"); await asyncio.sleep(1)
        errs = await js("[...document.querySelectorAll('.text-red-400')].map(e=>e.textContent).join(' | ')")
        check("no error shown on the panel", not errs, errs)
        print(f"\n{sum(results)}/{len(results)} passed")

asyncio.run(main())
