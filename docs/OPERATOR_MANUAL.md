# Rescue Robot — Operator Manual

This manual is for the person driving the robot from the dashboard. For how
to install and configure the system, see the [README](../README.md).

---

## 1. Before the mission

Work through this list before the robot is sent in.

**Robot**
- [ ] Battery charged and connected.
- [ ] Arduino, Raspberry Pi and the robot's mesh router powered on.
- [ ] Camera, speaker (3.5 mm jack) and robot display connected.
- [ ] Nothing loose on the chassis; wheels turn freely.

**Network**
- [ ] Relay routers placed and powered, forming a chain from you to the
      robot (you → relay → relay → robot).
- [ ] Your laptop is connected to the Wi-Fi network `robot-mesh-ap`.

**Laptop**
- [ ] Chrome is installed.
- [ ] To use your microphone and camera, the Chrome flag is set once:
      open `chrome://flags/#unsafely-treat-insecure-origin-as-secure`, add
      `http://192.168.10.10:8080`, enable it and restart Chrome. Without
      it, video from the robot, images and text messages still work.

---

## 2. Opening the dashboard

1. Wait about 30 seconds after powering the robot so all services start.
2. In Chrome, open **`http://192.168.10.10:8080`**.
3. Check the status bar at the top:

| Indicator | Good | Problem |
|---|---|---|
| Connection | `WS connected` (green) | `WS offline` (red): the dashboard can't reach the robot. It retries automatically. |
| Role | `role: controller` | `role: observer`: someone else is already controlling. You can watch but not drive. |
| Mission state | `READY` (green) | `STOP` (red): see [Section 4](#4-mission-states). |
| Serial | `serial ok` | `serial down`: the Pi can't talk to the Arduino. Motion is disabled. |
| GPS | `GPS fix` | `GPS no fix`: no location yet. Driving still works. It normally gets a fix within a few minutes outdoors. |

**Only one person can control the robot at a time.** The first dashboard to
connect becomes the controller; any others become observers. When the
controller closes their dashboard, the next one to connect takes over.

---

## 3. Dashboard layout

```
┌────────────────────────────────────────────────────────────────────┐
│ Status bar: connection · role · mission state · serial · GPS       │
├──────────────┬──────────────────────────────────┬──────────────────┤
│ Mission state│  Live video from robot           │ Sensor cards     │
│ Drive pad    │  Talk to victim panel            │ GPS card         │
│ Speed slider │  Map                             │ Alerts log       │
│ Camera pan/  │                                  │                  │
│   tilt       │                                  │                  │
│ EMERGENCY    │                                  │                  │
│   STOP       │                                  │                  │
└──────────────┴──────────────────────────────────┴──────────────────┘
```

---

## 4. Mission states

The large mission state on the left tells you whether it is safe to drive.

| State | Meaning | What to do |
|---|---|---|
| **READY** (green) | Everything working, robot idle. | Drive normally. |
| **DRIVING** (blue) | The robot is moving. | — |
| **DRIVING_LIMITED** (amber) | Video link from the robot lost. You can still drive, but you can't see. | Stop. Click **Retry video** on the video panel; if it fails, wait a few seconds for the media service to restart and try again. |
| **STOP** (red) | Connection lost, Arduino not responding, or no reply from the robot for over 3 seconds. Motion is disabled. | Stop and wait. See [Troubleshooting](#10-troubleshooting). |

---

## 5. Driving

You can drive with the on-screen pad or the keyboard.

| Action | On-screen | Keyboard |
|---|---|---|
| Forward | hold ▲ | hold `↑` or `W` |
| Reverse | hold ▼ | hold `↓` or `S` |
| Turn left | hold ◀ | hold `←` or `A` |
| Turn right | hold ▶ | hold `→` or `D` |
| Stop | click ■ | release the key |

- **The robot only moves while you hold the button or key.** Releasing it stops the robot.
- **Speed slider:** 0 to 180. The default is 120. Start low (around 80) in
  tight spaces and raise it once you're confident.
- Keyboard driving is ignored while you're typing in the message box, so
  typing a message won't move the robot.
- Watch the **Range** sensor card when driving forward. It turns amber
  under 30 cm and red under 20 cm from an obstacle.

### Built-in safety

- **Dead-man stop:** if the robot hears nothing from the dashboard for
  2 seconds (for example, the Wi-Fi drops), it stops the motors on its own.
  Once the connection returns, press a drive button again.
- The dashboard sends a heartbeat in the background, so the robot doesn't
  stop while you're simply idle and connected.

---

## 6. Camera (pan and tilt)

Use the **Pan** and **Tilt** sliders in the Camera section. Both range from
0° to 180°; 90° is centred. Pan and tilt are disabled when you're an observer
or disconnected.

---

## 7. Emergency stop

Click the red **EMERGENCY STOP** button (or the ■ on the drive pad).

- It stops all motors immediately.
- It always works, even when you're an observer.
- It isn't delayed or dropped by the checks that ordinary commands go through.

Use it whenever the robot does something unexpected. Driving works again as
soon as you press a drive button.

---

## 8. Sensors, map and alerts

**Sensor cards** (right side). A card turns **amber** at the warning level
and **red** at the critical level:

| Sensor | Warning | Critical |
|---|---|---|
| Temperature | above 50 °C | above 70 °C |
| Gas | above 450 | above 600 |
| Range (distance to obstacle) | below 30 cm | below 20 cm |
| Humidity | shown only, no alert | — |

The gas card is labelled "ppm", but the number is really the gas sensor's
raw reading (0–1023). The sensor hasn't been calibrated to true ppm. Use it
to tell whether gas is rising, not as an exact concentration.

**What a red card means for the mission:**
- **Temperature:** possible fire nearby. Back away and report it.
- **Gas:** hazardous air. Report it; rescuers need breathing protection.
- **Range:** the robot is about to hit something. Stop or reverse.

**GPS card and map:** show the robot's latitude and longitude, satellite
count and position on the map. Indoors or under rubble, GPS may show
`no fix`.

**Alerts log:** a timestamped list of events such as disconnections,
reconnections (`recovered N buffered telemetry frames`) and command errors.
The newest entry is at the bottom.

---

## 9. Talking to the victim

The **Talk to victim** panel (under the video) uses the robot's speaker and
display. The victim sees and hears you; you see and hear the victim through
the robot's camera and microphone.

**Before you start**, check the panel's top right shows
`robot screen online` (green). If it's amber, the robot's display isn't
running.

| To… | Do this |
|---|---|
| Speak | Click **🎤 Enable mic** once, then **hold 🎤 Hold to talk** while speaking. Release to stop. |
| Show your face | Click **My camera**. |
| Show a picture | Click **Image** and choose a file (for example, instructions or a photo of the rescue team). |
| Share your screen | Click **My screen**. |
| Show nothing | Click **Nothing**. |
| Send a text message | Type in the message box and click **Send**. When it appears on the robot, you'll see *"Message is on the robot screen ✓"*. |
| Remove the message | Click **Clear**. |

Useful things to tell the victim:
- Help is on the way.
- Stay still, and cover your nose and mouth if there is dust or gas.
- Tap or call out so rescuers can locate you.

**Only one operator can talk at a time.** If another operator is using the
screen, you'll see *"Another operator is talking to the victim"*. When you're
done, click **Release screen** so others can use it.

### Robot Display vs VNC mode

The **Robot display** buttons switch what the robot's screen shows:

- **🖥 Robot Display** (normal): the victim sees your video, images and messages.
- **💻 VNC Mode:** the robot screen shows the Pi desktop for maintenance.
  **The victim can't see anything you send.** A yellow warning appears
  while this mode is on.

Always switch back to **Robot Display** before a mission.

---

## 10. Troubleshooting

| Problem | Likely cause | What to do |
|---|---|---|
| Page won't load | Laptop not on the mesh, or robot still starting. | Check you're connected to `robot-mesh-ap`. Wait 30 s and reload. |
| `WS offline` | Wi-Fi link to the robot lost. | The dashboard reconnects on its own (retrying for up to 30 s). Move closer or add a relay. |
| `role: observer` | Another dashboard is the controller. | Close the other dashboard, then reload yours. |
| `serial down` / state `STOP` | Arduino disconnected or restarting. | The watchdog restarts services automatically; wait about 20 s. If it persists, check the Arduino USB cable. |
| Robot stops by itself while driving | Dead-man stop after a 2-second link drop. | Check the connection indicator, then press drive again. |
| No video | Media service restarting or weak link. | Wait a few seconds. Reload the page if it doesn't return. |
| "Hold to talk" / "My camera" greyed out | Chrome blocks the mic and camera on plain HTTP. | Set the Chrome flag in [Section 1](#1-before-the-mission). Images and text still work. |
| `robot screen offline` | The robot's display app isn't running, or the robot is in VNC mode. | Select **Robot Display**. If it stays offline, the robot display needs a restart. |
| Victim can't see messages | VNC mode is on. | Switch to **Robot Display**. |
| `GPS no fix` | Indoors or no sky view. | Normal indoors. Driving is unaffected. |

---

## 11. After the mission

1. Drive the robot back or wait for recovery.
2. Click **Release screen** if you were talking to the victim.
3. Close the dashboard so the controller role is freed.
4. Power off the robot and charge the battery.
5. Save the mission logs if needed. They are on the Pi in `/var/log/robot/`,
   and include telemetry and the GPS track.
