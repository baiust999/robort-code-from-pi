# Browser check: repeating voice message (2026-10-31)

Runs the real dashboard `TalkPanel` (with `VoiceMessagePanel`,
`useVoiceMessage` and `useTalkback`) in headless Chromium against the real P2
`ScreenHub` (`pi/p2_media/talkback.py`). The WebRTC data channel is replaced
by a WebSocket (`bridge.py`), and P2's `POST /voice` by a stub in the same
script that runs the real `decode_voice_clip`. Chromium's fake mic supplies
the recording. The WebRTC path, the real HTTP endpoint and what reaches the
speaker are covered by `../voice_loop_webrtc/run.py`.

To run (from a scratch copy of this folder, with `node_modules` symlinked to
`dashboard/node_modules`):

1. `VITE_ROBOT_HOST=127.0.0.1 VITE_P2_PORT=18193 vite build --config vite.config.ts --outDir out`
2. `python bridge.py &` (WebSocket 18190, /voice stub 18193)
3. `python -m http.server 18191 --bind 127.0.0.1 --directory out &`
4. `chromium --headless=new --remote-debugging-port=18192 --use-fake-device-for-media-stream --use-fake-ui-for-media-stream --autoplay-policy=no-user-gesture-required --user-data-dir=<tmp> about:blank &`
5. `python drive.py <dir for screenshots>`
