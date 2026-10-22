---
name: live-service-runs-from-repo
description: robot-watchdog.service runs directly from /home/pi/robot (not /opt/robot); /etc/robot does not exist
metadata:
  node_type: memory
  type: project
  originSessionId: 25c50f35-b1d8-44c6-9644-d026cdad741b
  modified: 2026-10-01T20:15:33.388Z
---

The installed robot-watchdog.service on this Pi runs P1/P2/P3 straight from the working tree:
WorkingDirectory=/home/pi/robot/pi, venv /home/pi/robot/venv, ROBOT_ROOT=/home/pi/robot/var,
DASHBOARD_DIR=/home/pi/robot/dashboard/dist. Settings are Environment= lines in the unit; there is no /etc/robot.

**Why:** The checked-out branch is what the robot runs on its next process restart, and `npm run build` overwrites the live dashboard.

**How to apply:** Treat branch switches and edits in pi/ as live changes. For a test build, write it into a scratch folder (`npx tsc -b && npx vite build --outDir <scratch>`) so the live dist isn't touched. Run smoke tests on a spare port (e.g. P1_PORT=18080) with their own ROBOT_ROOT.
