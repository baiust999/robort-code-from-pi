#!/usr/bin/env python3
"""Wi-Fi range and link-degradation sweep for paper Section 5.3 (N1-N5).

Run this ON THE ROBOT at each measurement position, pinging the operator
laptop (or the router). It records latency, jitter, loss and the local RSSI
together, so the paper can plot loss against both distance and signal
strength rather than distance alone -- RSSI is what actually explains the
cliff, and it is only readable on the Pi.

    ./netsweep.py --target 192.168.0.14 --label N1 --distance-m 5  --obstacles none
    ./netsweep.py --target 192.168.0.14 --label N4 --distance-m 15 --obstacles 2-walls \
                  --video choppy --control degraded

Video quality and control responsiveness are the operator's judgement, so they
are passed in as flags; everything else is measured. Add --iperf to also run a
throughput test (needs iperf3 on both ends: `sudo apt install iperf3`, and
`iperf3 -s` on the laptop).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, now_iso, wifi_signal_dbm  # noqa: E402

COLUMNS = (
    "iso_ts", "label", "distance_m", "obstacles", "target",
    "sent", "received", "loss_pct",
    "rtt_min_ms", "rtt_avg_ms", "rtt_max_ms", "rtt_mdev_ms",
    "signal_dbm_start", "signal_dbm_end", "tx_bitrate_mbps", "iperf_mbps",
    "video", "control", "notes",
)


def run_ping(target: str, count: int, interval: float, iface: str) -> dict[str, object]:
    command = ["ping", "-n", "-c", str(count), "-i", str(interval), "-I", iface, target]
    completed = subprocess.run(command, capture_output=True, text=True,
                               timeout=count * interval + 30)
    text = completed.stdout
    row: dict[str, object] = {}

    stats = re.search(r"(\d+) packets transmitted, (\d+) received.*?([\d.]+)% packet loss", text, re.S)
    if stats:
        row["sent"] = int(stats.group(1))
        row["received"] = int(stats.group(2))
        row["loss_pct"] = float(stats.group(3))
    else:
        # 100% loss on some builds prints no "received" clause at all.
        row["sent"] = count
        row["received"] = 0
        row["loss_pct"] = 100.0

    rtt = re.search(r"min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", text)
    if rtt:
        row["rtt_min_ms"] = float(rtt.group(1))
        row["rtt_avg_ms"] = float(rtt.group(2))
        row["rtt_max_ms"] = float(rtt.group(3))
        row["rtt_mdev_ms"] = float(rtt.group(4))
    return row


def tx_bitrate_mbps(iface: str) -> float | None:
    """Negotiated Wi-Fi rate; it drops before packets start being lost."""
    if not shutil.which("iw"):
        return None
    try:
        text = subprocess.run(["iw", "dev", iface, "link"], capture_output=True,
                              text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"tx bitrate:\s*([\d.]+)\s*MBit/s", text)
    return float(match.group(1)) if match else None


def run_iperf(target: str, seconds: int) -> float | None:
    if not shutil.which("iperf3"):
        print("iperf3 not installed, skipping throughput (sudo apt install iperf3)", file=sys.stderr)
        return None
    try:
        completed = subprocess.run(
            ["iperf3", "-c", target, "-t", str(seconds), "-J"],
            capture_output=True, text=True, timeout=seconds + 30,
        )
        data = json.loads(completed.stdout)
        return round(data["end"]["sum_sent"]["bits_per_second"] / 1e6, 2)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, KeyError) as error:
        print(f"iperf3 failed: {error}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True, help="operator laptop or router IP")
    parser.add_argument("--label", required=True, help="test ID, e.g. N1")
    parser.add_argument("--distance-m", required=True)
    parser.add_argument("--obstacles", default="none", help="e.g. none / 1-wall / 2-walls")
    parser.add_argument("--count", type=int, default=100, help="ping packets (default 100)")
    parser.add_argument("--interval", type=float, default=0.2, help="ping interval (default 0.2s)")
    parser.add_argument("--iface", default="wlan0")
    parser.add_argument("--video", default="", choices=["", "good", "choppy", "lost"])
    parser.add_argument("--control", default="", choices=["", "yes", "degraded", "no"])
    parser.add_argument("--iperf", action="store_true", help="also run an iperf3 throughput test")
    parser.add_argument("--iperf-seconds", type=int, default=10)
    parser.add_argument("--notes", default="")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR / "network.csv")
    args = parser.parse_args()

    print(f"{args.label}: {args.count} pings to {args.target} at {args.distance_m} m ({args.obstacles})")
    signal_start = wifi_signal_dbm(args.iface)
    row = run_ping(args.target, args.count, args.interval, args.iface)
    signal_end = wifi_signal_dbm(args.iface)

    row.update(
        iso_ts=now_iso(), label=args.label, distance_m=args.distance_m,
        obstacles=args.obstacles, target=args.target,
        signal_dbm_start=signal_start, signal_dbm_end=signal_end,
        tx_bitrate_mbps=tx_bitrate_mbps(args.iface),
        video=args.video, control=args.control, notes=args.notes,
    )
    if args.iperf:
        row["iperf_mbps"] = run_iperf(args.target, args.iperf_seconds)

    append_row(args.out, COLUMNS, row)
    print(f"  loss {row.get('loss_pct')}%  rtt avg {row.get('rtt_avg_ms')} ms  "
          f"max {row.get('rtt_max_ms')} ms  rssi {signal_start} dBm")
    print(f"  appended to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
