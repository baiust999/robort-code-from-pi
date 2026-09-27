#!/bin/bash
# Robot Screen kiosk launcher, methodology Section 16.
#
# Shows P2's /screen page full-screen on the robot's own display so the
# victim sees and hears the operator. Started from the desktop session's
# autostart (installed by deploy/install.sh), because Chromium needs the
# logged-in graphical session, which system services don't have.
#
# VNC (wayvnc) mirrors this same display, so a full-screen kiosk also covers
# the operator's VNC session. P2 therefore holds a display mode — "robot"
# (kiosk shown) or "vnc" (kiosk closed, Pi desktop usable) — switched from
# the dashboard, the radio buttons on the kiosk page, or this script:
#
#   robot-screen.sh          run the launcher loop (autostart does this)
#   robot-screen.sh robot    show the Robot Screen (desktop/menu shortcut)
#   robot-screen.sh vnc      hide it and use the Pi desktop
#
# The loop polls the mode and opens or closes Chromium to match. It waits
# for P2 before the first launch and relaunches Chromium if it crashes, so a
# browser crash costs the victim a few seconds of screen, not the mission.
# Closing the kiosk by hand (Alt+F4) counts as switching to "vnc", so the
# dashboard keeps showing what is really on the display.
set -u

P2_PORT="${P2_PORT:-8443}"
if [ -r /etc/robot/p2.env ]; then
  port=$(sed -n 's/^P2_PORT=//p' /etc/robot/p2.env | tail -n1)
  [ -n "$port" ] && P2_PORT="$port"
fi
SCREEN_URL="${SCREEN_URL:-http://localhost:${P2_PORT}/screen}"
MODE_URL="http://localhost:${P2_PORT}/screen/mode"
PROFILE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/robot-screen"
LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/robot-screen.lock"
POLL_S=1
RESTART_DELAY_S=3

# Prints "robot" or "vnc", or nothing while P2 is unreachable.
get_mode() {
  curl -fs --max-time 2 "$MODE_URL" | sed -n 's/.*"mode" *: *"\([a-z]*\)".*/\1/p'
}

set_mode() {
  curl -fs --max-time 2 -o /dev/null -X POST -H 'Content-Type: application/json' \
    -d "{\"mode\":\"$1\"}" "$MODE_URL"
}

case "${1:-}" in
  robot|vnc)
    if ! set_mode "$1"; then
      echo "robot-screen: P2 is not reachable at $MODE_URL" >&2
      exit 1
    fi
    # The shortcut should work even if the launcher isn't running (e.g.
    # autostart disabled): start it, detached, when nobody holds the lock.
    if [ "$1" = robot ] && flock -n "$LOCK_FILE" true; then
      setsid "$0" </dev/null >/dev/null 2>&1 &
    fi
    exit 0
    ;;
  "") ;;
  *)
    echo "usage: $0 [robot|vnc]" >&2
    exit 2
    ;;
esac

# One launcher per session.
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "robot-screen: already running" >&2
  exit 0
fi

BROWSER=$(command -v chromium || command -v chromium-browser)
if [ -z "$BROWSER" ]; then
  echo "robot-screen: chromium not installed" >&2
  exit 1
fi

# A kiosk left over from a previous launcher would make ours hand off to it
# and exit straight away.
pkill -f -- "--user-data-dir=$PROFILE_DIR" 2>/dev/null

browser_pid=""

launch() {
  "$BROWSER" \
    --kiosk "$SCREEN_URL" \
    --user-data-dir="$PROFILE_DIR" \
    --autoplay-policy=no-user-gesture-required \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --no-first-run \
    --password-store=basic \
    --check-for-update-interval=31536000 &
  browser_pid=$!
}

close_browser() {
  kill "$browser_pid" 2>/dev/null
  wait "$browser_pid" 2>/dev/null
  browser_pid=""
}

trap '[ -n "$browser_pid" ] && close_browser; exit 0' TERM INT

while true; do
  mode=$(get_mode)

  # The browser went away without us closing it.
  if [ -n "$browser_pid" ] && ! kill -0 "$browser_pid" 2>/dev/null; then
    wait "$browser_pid"
    status=$?
    browser_pid=""
    if [ "$status" -eq 0 ] && [ "$mode" = robot ]; then
      echo "robot-screen: kiosk closed by hand, switching to vnc" >&2
      set_mode vnc && mode=vnc
    else
      echo "robot-screen: browser exited ($status), restarting in ${RESTART_DELAY_S}s" >&2
      sleep "$RESTART_DELAY_S"
      continue
    fi
  fi

  # With P2 unreachable (mode empty) nothing changes: at boot we wait for
  # it rather than flash a browser error page at the victim, and an open
  # kiosk page reconnects on its own when P2 comes back.
  case "$mode" in
    robot) [ -z "$browser_pid" ] && launch ;;
    vnc) [ -n "$browser_pid" ] && close_browser ;;
  esac
  sleep "$POLL_S"
done
