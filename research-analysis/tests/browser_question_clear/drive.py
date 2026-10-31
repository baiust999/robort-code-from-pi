import asyncio, base64, json, sys, urllib.request
import websockets

S = sys.argv[1]
results = []
def check(name, ok, extra=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  [{extra}]" if extra else ""))

async def main():
    tabs = json.load(urllib.request.urlopen("http://127.0.0.1:18092/json"))
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=None) as cdp, \
               websockets.connect("ws://127.0.0.1:18090/ctl") as ctl:
        i = 0
        async def call(method, **params):
            nonlocal i; i += 1; await cdp.send(json.dumps({"id": i, "method": method, "params": params}))
            while True:
                r = json.loads(await asyncio.wait_for(cdp.recv(), 10))
                if r.get("id") == i: return r.get("result", {})
        async def js(expr):
            r = await call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
            return r.get("result", {}).get("value")
        async def bridge(**cmd):
            await ctl.send(json.dumps({"cmd": "state", **cmd})); return json.loads(await ctl.recv())
        async def shot(name):
            r = await call("Page.captureScreenshot")
            open(f"{S}/{name}.png", "wb").write(base64.b64decode(r["data"]))
        panel = "document.querySelector('form').innerText"
        clear_disabled = "[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Clear').disabled"
        fill = """(() => { const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
          const ins = document.querySelectorAll('form input'); const vals = %s;
          vals.forEach((v,k)=>{ set.call(ins[k], v); ins[k].dispatchEvent(new Event('input',{bubbles:true})); }); })()"""
        click = "[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===%r).click()"

        await call("Emulation.setDeviceMetricsOverride", width=420, height=360, deviceScaleFactor=1, mobile=False)
        await call("Page.navigate", url="http://127.0.0.1:18091/"); await asyncio.sleep(4)
        check("fresh page: Clear disabled, no result", await js(clear_disabled) and "Answer:" not in await js(panel))

        # 1. The reported bug: answered question, then Clear.
        await js(fill % json.dumps(["can you", "yes", "no"])); await asyncio.sleep(0.5)
        await js(click % "Send question"); await asyncio.sleep(1)
        st = await bridge()
        check("question reaches robot screen", st["screen"][-1]["type"] == "question_show" and st["screen"][-1]["text"] == "can you")
        check("dashboard shows waiting", "Waiting for answer" in await js(panel))
        await ctl.send(json.dumps({"cmd": "answer", "choice": 0})); await ctl.recv(); await asyncio.sleep(1)
        txt = await js(panel)
        check("dashboard shows 'Answer: yes'", "Answer: yes" in txt)
        check("Clear ENABLED after answer (was the bug)", await js(clear_disabled) is False)
        await shot("1-answered")
        await js(click % "Clear"); await asyncio.sleep(1)
        txt = await js(panel); st = await bridge()
        check("after Clear: answer gone from dashboard", "Answer:" not in txt and "can you" not in txt, txt.replace("\n", " | ")[-80:])
        check("after Clear: Clear disabled again", await js(clear_disabled) is True)
        check("P2 forgot the question", st["question"] is None)
        check("P2 sent question_dismissed", any(m["type"] == "question_dismissed" for m in st["op"]))
        await shot("2-cleared")
        await call("Page.reload"); await asyncio.sleep(4)
        check("after reload: answer does not come back", "Answer:" not in await js(panel) and await js(clear_disabled) is True)

        # 2. Clearing a question still waiting still takes it off the robot screen.
        await js(fill % json.dumps(["are you hurt", "yes", "no"])); await asyncio.sleep(0.5)
        await js(click % "Send question"); await asyncio.sleep(1)
        check("waiting: Clear enabled", await js(clear_disabled) is False)
        await js(click % "Clear"); await asyncio.sleep(1)
        st = await bridge()
        check("waiting + Clear: robot screen got question_hide", st["screen"][-1]["type"] == "question_hide")
        check("waiting + Clear: dashboard empty", "are you hurt" not in await js(panel) and st["question"] is None)
        print(f"\n{sum(results)}/{len(results)} passed")

asyncio.run(main())
