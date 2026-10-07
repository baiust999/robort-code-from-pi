#!/usr/bin/env python3
"""Resource utilisation logger for paper Section 5.5.

Samples the Pi once a second under a named load condition and writes one CSV
row per sample: total and per-process CPU, RSS, SoC temperature, throttling
flags, Wi-Fi RSSI, interface throughput, and the live /health counters that
say what the robot was actually doing at that moment.

Per-process CPU is a percentage of ONE core (top's convention), so the
four-core Pi 4 saturates at 400. Total CPU is a percentage of all cores.

Run one capture per condition, with the robot genuinely in that state:

    ./reslog.py --condition idle            --duration 1800
    ./reslog.py --condition one-viewer      --duration 1800
    ./reslog.py --condition two-viewers     --duration 1800
    ./reslog.py --condition drive-talk-view --duration 1800
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    P1_HEALTH,
    P2_HEALTH,
    RESULTS_DIR,
    append_row,
    cpu_temp_c,
    http_json,
    now_iso,
    one_pid,
    throttled_flags,
    wifi_signal_dbm,
)

CLK_TCK = os.sysconf("SC_CLK_TCK")
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

PROCESSES = {"p1": "p1_control.main", "p2": "p2_media.main", "p3": "p3_watchdog.main"}

COLUMNS = (
    "iso_ts", "t_s", "condition",
    "cpu_pct", "p1_cpu_pct", "p2_cpu_pct", "p3_cpu_pct",
    "mem_used_mb", "mem_avail_mb", "p1_rss_mb", "p2_rss_mb", "p3_rss_mb",
    "temp_c", "throttled", "under_voltage_now", "freq_capped_now",
    "throttled_now", "under_voltage_ever",
    "load1", "rx_kbps", "tx_kbps", "signal_dbm",
    "ws_clients", "active_streams", "serial_ok", "camera_open", "gps_fix",
    # The robot display runs either a Chromium kiosk or VNC, and the two cost
    # very different amounts of CPU, so a capture is only comparable to
    # another in the same mode.
    "display_mode", "screen_connected",
)


def total_cpu_jiffies() -> tuple[int, int]:
    """(busy+idle, idle) from /proc/stat; idle includes iowait."""
    fields = Path("/proc/stat").read_text().split("\n", 1)[0].split()[1:]
    values = [int(v) for v in fields]
    return sum(values), values[3] + values[4]


def proc_cpu_jiffies(pid: int) -> int | None:
    """utime+stime for a PID. /proc/<pid>/stat field 2 may contain spaces, so
    the fixed-position fields are read after the final ')'."""
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    try:
        tail = raw[raw.rindex(")") + 2:].split()
        return int(tail[11]) + int(tail[12])
    except (ValueError, IndexError):
        return None


def proc_rss_mb(pid: int) -> float | None:
    try:
        resident_pages = int(Path(f"/proc/{pid}/statm").read_text().split()[1])
    except (OSError, ValueError, IndexError):
        return None
    return round(resident_pages * PAGE_SIZE / 1048576, 1)


def meminfo_mb() -> tuple[float, float]:
    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, _, rest = line.partition(":")
        values[key] = int(rest.split()[0])
    total = values.get("MemTotal", 0) / 1024
    available = values.get("MemAvailable", 0) / 1024
    return round(total - available, 1), round(available, 1)


def net_bytes(iface: str) -> tuple[int, int]:
    for line in Path("/proc/net/dev").read_text().splitlines():
        name, _, rest = line.partition(":")
        if name.strip() == iface:
            fields = rest.split()
            return int(fields[0]), int(fields[8])
    return 0, 0


def load1() -> float:
    return float(Path("/proc/loadavg").read_text().split()[0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--condition", required=True, help="load label, e.g. idle / two-viewers")
    parser.add_argument("--duration", type=float, default=1800, help="seconds (default 1800 = 30 min)")
    parser.add_argument("--interval", type=float, default=1.0, help="sample period in seconds")
    parser.add_argument("--iface", default="wlan0")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR / "resources.csv")
    args = parser.parse_args()

    pids = {name: one_pid(pattern) for name, pattern in PROCESSES.items()}
    missing = [name for name, pid in pids.items() if pid is None]
    if missing:
        print(f"warning: not running: {', '.join(missing)} (columns will be blank)", file=sys.stderr)

    prev_total, prev_idle = total_cpu_jiffies()
    prev_proc = {name: (proc_cpu_jiffies(pid) if pid else None) for name, pid in pids.items()}
    prev_rx, prev_tx = net_bytes(args.iface)
    start = time.monotonic()
    prev_wall = start
    time.sleep(args.interval)

    samples = 0
    print(f"logging '{args.condition}' for {args.duration:.0f}s -> {args.out}  (Ctrl-C to stop early)")
    try:
        while time.monotonic() - start < args.duration:
            wall = time.monotonic()
            elapsed = wall - prev_wall
            total, idle = total_cpu_jiffies()
            d_total = total - prev_total
            cpu_pct = round(100.0 * (1 - (idle - prev_idle) / d_total), 1) if d_total > 0 else ""

            row: dict[str, object] = {
                "iso_ts": now_iso(),
                "t_s": round(wall - start, 1),
                "condition": args.condition,
                "cpu_pct": cpu_pct,
            }

            # A process restarted by P3 gets a new PID; re-resolve it so the
            # series continues instead of going blank for the rest of the run.
            for name, pattern in PROCESSES.items():
                pid = pids[name]
                jiffies = proc_cpu_jiffies(pid) if pid else None
                if jiffies is None:
                    pids[name] = pid = one_pid(pattern)
                    jiffies = proc_cpu_jiffies(pid) if pid else None
                    prev_proc[name] = jiffies
                before = prev_proc[name]
                if jiffies is not None and before is not None and elapsed > 0:
                    row[f"{name}_cpu_pct"] = round(100.0 * (jiffies - before) / (elapsed * CLK_TCK), 1)
                prev_proc[name] = jiffies
                if pid:
                    row[f"{name}_rss_mb"] = proc_rss_mb(pid)

            used, available = meminfo_mb()
            rx, tx = net_bytes(args.iface)
            row.update(
                mem_used_mb=used,
                mem_avail_mb=available,
                temp_c=cpu_temp_c(),
                load1=load1(),
                rx_kbps=round((rx - prev_rx) * 8 / 1000 / elapsed, 1) if elapsed > 0 else "",
                tx_kbps=round((tx - prev_tx) * 8 / 1000 / elapsed, 1) if elapsed > 0 else "",
                signal_dbm=wifi_signal_dbm(args.iface),
                **throttled_flags(),
            )

            p1 = http_json(P1_HEALTH, timeout=1.0)
            if p1:
                row.update(
                    ws_clients=p1.get("ws_clients"),
                    serial_ok=int(bool(p1.get("serial_connected"))),
                    gps_fix=int(bool(p1.get("gps_fix"))),
                )
            p2 = http_json(P2_HEALTH, timeout=1.0)
            if p2:
                row.update(
                    active_streams=p2.get("active_streams"),
                    camera_open=int(bool(p2.get("camera_open"))),
                    display_mode=p2.get("display_mode"),
                    screen_connected=int(bool(p2.get("screen_connected"))),
                )

            append_row(args.out, COLUMNS, row)
            samples += 1
            if samples % 60 == 0:
                print(f"  {row['t_s']:.0f}s  cpu {cpu_pct}%  temp {row['temp_c']}C  "
                      f"streams {row.get('active_streams', '-')}")

            prev_total, prev_idle = total, idle
            prev_rx, prev_tx = rx, tx
            prev_wall = wall
            time.sleep(max(0.0, args.interval - (time.monotonic() - wall)))
    except KeyboardInterrupt:
        print("\nstopped early")

    print(f"{samples} samples written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
