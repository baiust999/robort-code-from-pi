"""Shared helpers for the evaluation harness (tools/eval).

Stdlib only: this Pi has no psutil/numpy, and keeping the harness dependency
free means a reviewer can re-run it on a bare Raspberry Pi OS image.
"""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

RESULTS_DIR = Path(__file__).resolve().parent / "results"

P1_HEALTH = "http://127.0.0.1:8080/health"
P2_HEALTH = "http://127.0.0.1:8443/health"


def now_iso() -> str:
    """UTC timestamp with milliseconds; sorts lexically, pastes into a paper."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def append_row(path: Path, columns: Sequence[str], row: dict[str, Any]) -> None:
    """Append one row, writing the header if the file is new.

    Every sheet is append-only. A test run that crashes half way still leaves
    its completed trials on disk.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in columns})


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def http_json(url: str, timeout: float = 1.5) -> dict[str, Any] | None:
    """GET a /health endpoint. None on any failure: down is a measurement."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return None


def pids_for(pattern: str) -> list[int]:
    """PIDs whose cmdline contains `pattern`, excluding this process tree.

    pgrep -f would match the harness's own command line, so the match is done
    against /proc directly and self/parent are filtered out.
    """
    mine = {os.getpid(), os.getppid()}
    found: list[int] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid in mine:
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode()
        except OSError:
            continue
        if pattern in cmdline:
            found.append(pid)
    return sorted(found)


def one_pid(pattern: str) -> int | None:
    pids = pids_for(pattern)
    return pids[0] if pids else None


def cpu_temp_c() -> float | None:
    try:
        raw = Path("/sys/class/thermal/thermal_zone0/temp").read_text().strip()
        return round(int(raw) / 1000.0, 1)
    except (OSError, ValueError):
        return None


def throttled_flags() -> dict[str, Any]:
    """Decode `vcgencmd get_throttled`.

    Under-voltage or a frequency cap during a load test invalidates the CPU
    numbers, so this is recorded alongside them rather than assumed absent.
    """
    out: dict[str, Any] = {
        "throttled": "",
        "under_voltage_now": "",
        "freq_capped_now": "",
        "throttled_now": "",
        "under_voltage_ever": "",
    }
    try:
        text = subprocess.run(
            ["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=3
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return out
    if "=" not in text:
        return out
    value = int(text.split("=", 1)[1], 16)
    out["throttled"] = hex(value)
    out["under_voltage_now"] = int(bool(value & (1 << 0)))
    out["freq_capped_now"] = int(bool(value & (1 << 1)))
    out["throttled_now"] = int(bool(value & (1 << 2)))
    out["under_voltage_ever"] = int(bool(value & (1 << 16)))
    return out


def wifi_signal_dbm(iface: str = "wlan0") -> float | None:
    """RSSI from /proc/net/wireless (no subprocess, safe to sample at 1 Hz)."""
    try:
        for line in Path("/proc/net/wireless").read_text().splitlines():
            if line.strip().startswith(f"{iface}:"):
                fields = line.split()
                return float(fields[3].rstrip("."))
    except (OSError, IndexError, ValueError):
        return None
    return None


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle ground distance in metres (same formula as p1 gps_track)."""
    radius = 6371008.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def describe(values: Iterable[float]) -> dict[str, Any]:
    """n / mean / SD / min / max / median / p95, the set a reviewer expects.

    SD is the sample standard deviation (n-1); a single sample reports an
    empty SD rather than 0, which would overstate the precision.
    """
    data = sorted(float(v) for v in values)
    if not data:
        return {"n": 0}
    return {
        "n": len(data),
        "mean": round(statistics.fmean(data), 2),
        "sd": round(statistics.stdev(data), 2) if len(data) > 1 else "",
        "min": round(data[0], 2),
        "max": round(data[-1], 2),
        "median": round(statistics.median(data), 2),
        "p95": round(percentile(data, 95), 2),
    }


def percentile(sorted_data: Sequence[float], pct: float) -> float:
    """Linear-interpolation percentile on already-sorted data."""
    if len(sorted_data) == 1:
        return float(sorted_data[0])
    position = (len(sorted_data) - 1) * pct / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(sorted_data[low])
    return float(sorted_data[low] + (sorted_data[high] - sorted_data[low]) * (position - low))


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
