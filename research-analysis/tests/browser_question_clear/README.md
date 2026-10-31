# Browser check: question Clear (2026-10-31)

Runs the real dashboard `QuestionPanel` and `useTalkback` hook in headless
Chromium against the real P2 `ScreenHub` (`pi/p2_media/talkback.py`). The
WebRTC data channel is replaced by a WebSocket (`bridge.py`) and the robot
screen by a stub that records what P2 sends it, so it tests the message
logic, not WebRTC or the physical display. Absolute paths assume the repo is
at `/home/pi/robot`. Output of the 2026-10-31 run:
`research-analysis/output/browser_question_clear_2026-10-31.txt`.

To run (from a scratch copy of this folder, with `node_modules` symlinked to
`dashboard/node_modules`):

1. `vite build --config vite.config.ts --outDir out`
2. `python bridge.py &` (port 18090)
3. `python -m http.server 18091 --bind 127.0.0.1 --directory out &`
4. `chromium --headless=new --remote-debugging-port=18092 --user-data-dir=<tmp> about:blank &`
5. `python drive.py <dir for screenshots>`

Use a static build: headless Chromium on the Pi did not load the Vite dev
server.
