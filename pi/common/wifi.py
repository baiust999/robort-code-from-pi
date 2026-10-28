"""Wi-Fi link strength for the dashboard signal indicator.

Reads /proc/net/wireless (no subprocess, cheap enough for 1Hz) the same way
tools/eval/common.py:wifi_signal_dbm does. The difference is the operstate
check: after a disassociation /proc can keep reporting the last level, and a
stale good value on the dashboard is exactly what this feature must avoid.
None therefore means "no usable link", never "unknown but probably fine".
"""

from __future__ import annotations

from pathlib import Path

PROC_WIRELESS = Path("/proc/net/wireless")
SYS_NET = Path("/sys/class/net")


def parse_signal_dbm(text: str, iface: str) -> float | None:
    """Signal level column of /proc/net/wireless for ``iface``."""
    for line in text.splitlines():
        if line.strip().startswith(f"{iface}:"):
            try:
                return float(line.split()[3].rstrip("."))
            except (IndexError, ValueError):
                return None
    return None


def read_signal_dbm(
    iface: str = "wlan0",
    *,
    proc_path: Path = PROC_WIRELESS,
    sys_net: Path = SYS_NET,
) -> float | None:
    """Current RSSI in dBm, or None when the interface is down or absent."""
    try:
        if (sys_net / iface / "operstate").read_text(encoding="ascii").strip() != "up":
            return None
        return parse_signal_dbm(proc_path.read_text(encoding="ascii"), iface)
    except OSError:
        return None
