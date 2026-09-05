#!/bin/bash
# Raspberry Pi provisioning script, Section 8.14.4.
#
# Run on the Pi as a user with sudo, from inside the cloned repo, e.g.:
#   git clone <repo-url> /opt/robot-src
#   cd /opt/robot-src && sudo ./deploy/install.sh
#
# Idempotent: safe to re-run after a code update to refresh the venv and
# service units without disturbing /etc/robot config the operator has
# already customised.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT=/opt/robot
ROBOT_USER=robot

if [ "$(id -u)" -ne 0 ]; then
  echo "run as root (sudo ./deploy/install.sh)" >&2
  exit 1
fi

echo "== stage 1: system packages =="
apt-get update
apt-get install -y \
  python3 python3-pip python3-venv \
  libatlas-base-dev \
  ffmpeg libavcodec-dev libavformat-dev \
  gpsd gpsd-clients \
  logrotate

echo "== stage 2: robot user and directories =="
id -u "$ROBOT_USER" >/dev/null 2>&1 || useradd -r -m -G dialout,video,audio "$ROBOT_USER"
mkdir -p "$INSTALL_ROOT" /etc/robot /var/log/robot/gps_track /run/robot
chown -R "$ROBOT_USER:$ROBOT_USER" "$INSTALL_ROOT" /var/log/robot /run/robot

echo "== stage 3: application code =="
rsync -a --delete \
  --exclude '.git' --exclude 'node_modules' --exclude '__pycache__' \
  "$REPO_ROOT"/pi "$INSTALL_ROOT"/
if [ -d "$REPO_ROOT/dashboard/dist" ]; then
  rsync -a --delete "$REPO_ROOT"/dashboard/dist/ "$INSTALL_ROOT"/dashboard/dist/
else
  echo "note: dashboard/dist not built yet; run 'npm run build' in dashboard/ and re-run this script" >&2
fi

echo "== stage 4: python virtualenv =="
python3 -m venv "$INSTALL_ROOT/venv"
"$INSTALL_ROOT/venv/bin/pip" install --upgrade pip
"$INSTALL_ROOT/venv/bin/pip" install -r "$INSTALL_ROOT/pi/requirements.txt"
"$INSTALL_ROOT/venv/bin/pip" install -r "$INSTALL_ROOT/pi/requirements-media.txt"
chown -R "$ROBOT_USER:$ROBOT_USER" "$INSTALL_ROOT"

echo "== stage 5: config templates (won't overwrite existing) =="
for f in p1.env p2.env p3.env thresholds.json mesh.conf; do
  if [ ! -f "/etc/robot/$f" ]; then
    cp "$REPO_ROOT/deploy/etc-robot/$f" "/etc/robot/$f"
  fi
done

echo "== stage 6: systemd service =="
cp "$REPO_ROOT/deploy/systemd/robot-watchdog.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable robot-watchdog.service

echo "== stage 7: logrotate =="
cp "$REPO_ROOT/deploy/logrotate/robot" /etc/logrotate.d/robot

echo "== stage 8: hardware interfaces (manual verification required) =="
cat <<'EOF'
Remaining manual steps (Section 8.14.4, Stage 5):
  1. Enable the GPS UART:
       sudo raspi-config nonint do_serial_hw 0
       sudo raspi-config nonint do_serial_cons 1
  2. Verify GPS: minicom -D /dev/serial0 -b 9600
  3. Verify Arduino USB: ls /dev/ttyUSB*
  4. Set the Ethernet static IP in /etc/dhcpcd.conf:
       interface eth0
       static ip_address=192.168.10.10/24
       static routers=192.168.10.1
       static domain_name_servers=8.8.8.8
     then: sudo systemctl restart dhcpcd
  5. Flash and provision the three mesh routers with deploy/mesh/*.sh
     (Section 8.14.5.1).

Then start the stack:
  sudo systemctl start robot-watchdog.service
  sudo systemctl status robot-watchdog.service
EOF
