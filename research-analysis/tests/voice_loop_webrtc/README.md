# End-to-end check: repeating voice message over WebRTC (2026-10-31)

`run.py` starts an isolated P2 (`MOCK_HARDWARE=1`, port 18443, its own
controller key and `ROBOT_ROOT`, video shrunk to 160x120 at 5 fps to keep
the Pi's load down) and a fake P1 on port 18180 that names 127.0.0.1 as
the controller. aiortc peers stand in for the dashboard and for the Robot
Screen kiosk. The live robot is not touched.

The fake dashboard sends audio the whole time, like Chrome with the mic
open: silence while not talking (a disabled track) and a 440 Hz tone while
"Hold to talk" is held. The uploaded voice message is a 1 s, 1 kHz tone,
so the kiosk can tell from what it receives which source P2 is playing.

Covered: wrong key (403) and unreadable clip (422) on `POST /voice`;
repeats of about 1 s with the 1.5 s gap; live voice replacing the loop
while talking; the loop coming back whole after release, with the floor
still held and the muted mic still sending silence; the loop surviving the
dashboard's disconnect; a reconnecting dashboard told it is playing; an
observer unable to stop it; Stop, Clear, Start with nothing stored; the
`VOICE_*` events in P2's log.

Run (takes about 45 s):

    /home/pi/robot/venv/bin/python run.py <empty scratch dir>

Output of the 2026-10-31 runs, before and after the muted-mic fix
(TEST_REPORT Issue 13): `research-analysis/output/e2e_voice_loop_webrtc_2026-10-31.txt`.
Not covered: the real speaker, a real operator mic, Chrome's own WebRTC
stack. The dashboard panel is checked separately in `../browser_voice_message/`.
