#!/bin/bash
# Robot Screen kiosk launcher, methodology Section 16.
#
# Shows P2's /screen page full-screen on the robot's own display so the
# victim sees and hears the operator. Started from the desktop session's
# autostart (installed by deploy/install.sh), because Chromium needs the
# logged-in graphical session, which system services don't have.
#
# Waits for P2 before launching and relaunches Chromium if it ever exits,
# so a browser crash costs the victim a few seconds of screen, not the mission.
set -u

P2_PORT="${P2_PORT:-8443}"
if [ -r /etc/robot/p2.env ]; then
  port=$(sed -n 's/^P2_PORT=//p' /etc/robot/p2.env | tail -n1)
  [ -n "$port" ] && P2_PORT="$port"
fi
SCREEN_URL="${SCREEN_URL:-http://localhost:${P2_PORT}/screen}"
HEALTH_URL="http://localhost:${P2_PORT}/health"
PROFILE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/robot-screen"
RESTART_DELAY_S=3

BROWSER=$(command -v chromium || command -v chromium-browser)
if [ -z "$BROWSER" ]; then
  echo "robot-screen: chromium not installed" >&2
  exit 1
fi

while true; do
  # P2 starts well after the desktop does; the page would also retry on its
  # own, but waiting here avoids flashing a browser error page at the victim.
  until curl -fs -o /dev/null --max-time 2 "$HEALTH_URL"; do
    sleep "$RESTART_DELAY_S"
  done

  "$BROWSER" \
    --kiosk "$SCREEN_URL" \
    --user-data-dir="$PROFILE_DIR" \
    --autoplay-policy=no-user-gesture-required \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --no-first-run \
    --password-store=basic \
    --check-for-update-interval=31536000

  echo "robot-screen: browser exited ($?), restarting in ${RESTART_DELAY_S}s" >&2
  sleep "$RESTART_DELAY_S"
done
