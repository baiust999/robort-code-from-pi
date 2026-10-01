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
# The user who logs in to the Pi desktop; the Robot Screen kiosk runs in
# their graphical session (Section 16).
DESKTOP_USER="${DESKTOP_USER:-${SUDO_USER:-pi}}"

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
  logrotate \
  curl
# Robot Screen kiosk. Raspberry Pi OS ships Chromium as chromium-browser
# (Bookworm) or chromium (later releases).
if ! command -v chromium >/dev/null && ! command -v chromium-browser >/dev/null; then
  apt-get install -y chromium-browser || apt-get install -y chromium
fi

echo "== stage 2: robot user and directories =="
id -u "$ROBOT_USER" >/dev/null 2>&1 || useradd -r -m -G dialout,video,audio "$ROBOT_USER"
mkdir -p "$INSTALL_ROOT" /etc/robot /var/log/robot/gps_track /run/robot
chown -R "$ROBOT_USER:$ROBOT_USER" "$INSTALL_ROOT" /var/log/robot /run/robot

echo "== stage 3: application code =="
rsync -a --delete \
  --exclude '.git' --exclude 'node_modules' --exclude '__pycache__' \
  "$REPO_ROOT"/pi "$INSTALL_ROOT"/
mkdir -p "$INSTALL_ROOT/deploy"
rsync -a --delete "$REPO_ROOT"/deploy/robot-screen "$INSTALL_ROOT"/deploy/
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
for f in p1.env p2.env p3.env thresholds.json; do
  if [ ! -f "/etc/robot/$f" ]; then
    cp "$REPO_ROOT/deploy/etc-robot/$f" "/etc/robot/$f"
  fi
done

echo "== stage 6: systemd service =="
cp "$REPO_ROOT/deploy/systemd/robot-watchdog.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable robot-watchdog.service

if id -u "$DESKTOP_USER" >/dev/null 2>&1; then
  desktop_home="$(getent passwd "$DESKTOP_USER" | cut -d: -f6)"
  autostart_dir="$desktop_home/.config/autostart"
  install -d -o "$DESKTOP_USER" -g "$DESKTOP_USER" "$autostart_dir"
  install -m 644 -o "$DESKTOP_USER" -g "$DESKTOP_USER" \
    "$REPO_ROOT/deploy/robot-screen/robot-screen.desktop" "$autostart_dir/robot-screen.desktop"
  # "Show Robot Screen" in the app menu and on the desktop: the way back
  # from VNC mode when working on the Pi itself.
  apps_dir="$desktop_home/.local/share/applications"
  install -d -o "$DESKTOP_USER" -g "$DESKTOP_USER" "$apps_dir"
  install -m 644 -o "$DESKTOP_USER" -g "$DESKTOP_USER" \
    "$REPO_ROOT/deploy/robot-screen/robot-screen-show.desktop" "$apps_dir/robot-screen-show.desktop"
  if [ -d "$desktop_home/Desktop" ]; then
    install -m 755 -o "$DESKTOP_USER" -g "$DESKTOP_USER" \
      "$REPO_ROOT/deploy/robot-screen/robot-screen-show.desktop" "$desktop_home/Desktop/robot-screen-show.desktop"
  fi
  echo "Robot Screen kiosk will start in $DESKTOP_USER's desktop session"
else
  echo "note: desktop user '$DESKTOP_USER' not found; set DESKTOP_USER to enable the Robot Screen kiosk" >&2
fi

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
  4. Robot Screen (talk-to-victim, Section 16):
       - Enable desktop autologin so the kiosk starts at boot:
           sudo raspi-config nonint do_boot_behaviour B4
       - VNC shows the same display as the kiosk. To use the Pi desktop,
         hold the kiosk's corner "Hold 3 s for VNC" button, or pick VNC
         on the dashboard; "Show Robot Screen" in the app menu switches back.
       - Connect the robot display (HDMI 0) and the speaker (3.5 mm jack),
         then make the jack the default audio output:
           wpctl status            # find the "Built-in Audio" sink id
           wpctl set-default <id>
       - Operator laptops need a secure context for mic/camera: open Chrome
         with chrome://flags/#unsafely-treat-insecure-origin-as-secure set to
         http://<pi-ip>:8080 (images and text messages work without it).
         Give the Pi a fixed address in your Wi-Fi router's settings so this
         does not change.

Then start the stack:
  sudo systemctl start robot-watchdog.service
  sudo systemctl status robot-watchdog.service
EOF
