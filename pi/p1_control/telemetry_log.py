"""Telemetry CSV sink, Section 8.13.2.

Sampled at 1Hz rather than the 200ms broadcast rate: the full stream would be
~3.2MB/hour for data whose post-mission value is trend-level. Each line carries
the snapshot fields plus a packed alert bitfield so a reviewer can locate
threshold crossings without re-deriving them.

Rotation is handled by logrotate (deploy/logrotate/robot), not in-process.
That config rotates with ``copytruncate``: the content is copied away and this
file is truncated to zero underneath us while the handle stays open. The writer
therefore re-emits the header whenever it finds the file empty, so a rotated log
describes its own columns instead of starting mid-stream.
"""

from __future__ import annotations

import os
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
    "range_cm",
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
        self._handle = self._path.open("a", encoding="utf-8")
        self._write_header_if_empty()

    def _write_header_if_empty(self) -> None:
        """Emit the column header if the file currently holds nothing.

        Covers both a freshly created log and one that logrotate has just
        truncated with copytruncate while this handle stayed open. The size
        comes from fstat on the open descriptor rather than a path stat: it
        sees the truncation immediately and carries no TOCTOU window.
        """
        if self._handle is None:
            return
        try:
            if os.fstat(self._handle.fileno()).st_size:
                return
        except OSError:
            # A log we cannot stat is still worth writing rows to; losing the
            # header is better than dropping telemetry.
            return
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
        self._write_header_if_empty()
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
