"""Telemetry CSV sink, Section 8.13.2.

Sampled at 1Hz rather than the 200ms broadcast rate: the full stream would be
~3.2MB/hour for data whose post-mission value is trend-level. Each line carries
the snapshot fields plus a packed alert bitfield so a reviewer can locate
threshold crossings without re-deriving them.

Rotation is handled by logrotate (deploy/logrotate/robot), not in-process.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

from common import protocol

CSV_COLUMNS: tuple[str, ...] = (
    "iso_ts",
    "seq",
    "temperature_c",
    "humidity_pct",
    "gas_ppm",
    "motion",
    "range_cm",
    "ir_left",
    "ir_right",
    "pan_angle",
    "tilt_angle",
    "fw_state",
    "uptime_ms",
    "lat",
    "lon",
    "gps_fix",
    "gps_sats",
    "serial_ok",
    "ws_clients",
    "turn_status",
    "alert_flags",
)


class TelemetryLog:
    """Append-only 1Hz CSV writer."""

    def __init__(
        self,
        path: Path,
        thresholds: dict[str, dict[str, float]],
        *,
        period_ms: int = protocol.TELEMETRY_LOG_PERIOD_MS,
        enabled: bool = True,
    ) -> None:
        self._path = path
        self._thresholds = thresholds
        self._period_s = period_ms / 1000.0
        self._enabled = enabled
        self._handle: TextIO | None = None
        self._last_write = 0.0

    def open(self) -> None:
        if not self._enabled:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not self._path.exists() or self._path.stat().st_size == 0
        self._handle = self._path.open("a", encoding="utf-8")
        if is_new:
            self._handle.write(",".join(CSV_COLUMNS) + "\n")
            self._handle.flush()

    def maybe_write(self, snapshot: dict[str, Any]) -> None:
        """Write at most once per period."""
        if self._handle is None:
            return
        now = time.monotonic()
        if now - self._last_write < self._period_s:
            return
        self._last_write = now
        self.write(snapshot)

    def write(self, snapshot: dict[str, Any]) -> None:
        if self._handle is None:
            return
        flags = protocol.compute_alert_flags(snapshot, self._thresholds)
        row = {
            **snapshot,
            "iso_ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "alert_flags": flags,
        }
        cells = [_render(row.get(column)) for column in CSV_COLUMNS]
        # One write per line keeps records atomic under concurrent readers.
        self._handle.write(",".join(cells) + "\n")
        self._handle.flush()

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None


def _render(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    text = str(value)
    return text.replace(",", ";")
