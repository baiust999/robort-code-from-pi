"""NEO-6M GPS reader, Section 8.10.4.

Runs on its own thread because pyserial reads are blocking and the fix rate
(1Hz) is unrelated to the 200ms telemetry cadence. The latest fix is published
into a dict guarded by a lock; the telemetry builder merges it each broadcast.

Parses GPRMC (position + validity) and GPGGA (fix quality + satellite count)
directly rather than depending on pynmea2, so the module works unchanged when
that package is absent on a dev host.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.config import P1Config
from common.logging_setup import EventLogger
from common.mock_hardware import MockGPS


class GPSReader:
    """Background NMEA reader publishing the most recent fix."""

    def __init__(self, config: P1Config, log: EventLogger) -> None:
        self._config = config
        self._log = log
        self._lock = threading.Lock()
        self._state: dict[str, Any] = {
            "lat": None,
            "lon": None,
            "gps_fix": False,
            "gps_sats": 0,
        }
        self._track: list[tuple[float, float]] = []
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="gps-reader", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def track_points(self) -> list[tuple[float, float]]:
        with self._lock:
            return list(self._track)

    # --- reader thread ------------------------------------------------------

    def _run(self) -> None:
        if self._config.mock_hardware:
            self._run_mock()
            return
        self._run_serial()

    def _run_mock(self) -> None:
        mock = MockGPS()
        while not self._stop.is_set():
            self._publish(mock.read_fix())
            time.sleep(1.0)

    def _run_serial(self) -> None:
        try:
            import serial
        except ImportError:
            self._log.error("GPS_NO_PYSERIAL", "pyserial missing; gps disabled")
            return

        while not self._stop.is_set():
            try:
                with serial.Serial(
                    self._config.gps_port, self._config.gps_baud, timeout=1.0
                ) as port:
                    self._log.info("GPS_OPEN", "gps port opened", port=self._config.gps_port)
                    while not self._stop.is_set():
                        raw = port.readline()
                        if not raw:
                            continue
                        sentence = raw.decode("ascii", errors="ignore").strip()
                        parsed = parse_nmea(sentence)
                        if parsed:
                            self._publish(parsed)
            except Exception:  # noqa: BLE001 - retry a flapping GPS forever
                self._log.exception("GPS_FAIL", "gps read failed; retrying")
                self._mark_no_fix()
                time.sleep(2.0)

    def _publish(self, update: dict[str, Any]) -> None:
        with self._lock:
            self._state.update(update)
            lat, lon = self._state.get("lat"), self._state.get("lon")
            if self._state.get("gps_fix") and lat is not None and lon is not None:
                # Only record a point once it differs from the previous one, so
                # a stationary robot does not inflate the track.
                if not self._track or self._track[-1] != (lat, lon):
                    self._track.append((lat, lon))

    def _mark_no_fix(self) -> None:
        with self._lock:
            self._state["gps_fix"] = False
            self._state["gps_sats"] = 0

    # --- persistence --------------------------------------------------------

    def write_geojson(self, session_id: str) -> Path | None:
        """Persist the session track as a GeoJSON LineString, Section 8.13.6."""
        points = self.track_points()
        if len(points) < 2:
            return None

        self._config.paths.gps_track_dir.mkdir(parents=True, exist_ok=True)
        path = self._config.paths.gps_track_dir / f"session_{session_id}.geojson"
        document = {
            "type": "Feature",
            "properties": {
                "session_id": session_id,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "point_count": len(points),
            },
            "geometry": {
                # GeoJSON is lon,lat ordered.
                "type": "LineString",
                "coordinates": [[lon, lat] for lat, lon in points],
            },
        }
        with path.open("w", encoding="utf-8") as handle:
            json.dump(document, handle)
        self._log.info("GPS_TRACK_SAVED", "gps track written", path=str(path))
        return path


def parse_nmea(sentence: str) -> dict[str, Any] | None:
    """Extract position/fix data from a GPRMC or GPGGA sentence."""
    if not sentence.startswith("$") or "," not in sentence:
        return None
    if not _checksum_ok(sentence):
        return None

    fields = sentence.split(",")
    talker = fields[0][3:]

    if talker == "RMC" and len(fields) >= 7:
        valid = fields[2] == "A"
        if not valid:
            return {"gps_fix": False}
        lat = _to_degrees(fields[3], fields[4])
        lon = _to_degrees(fields[5], fields[6])
        if lat is None or lon is None:
            return {"gps_fix": False}
        return {"lat": round(lat, 6), "lon": round(lon, 6), "gps_fix": True}

    if talker == "GGA" and len(fields) >= 8:
        try:
            quality = int(fields[6]) if fields[6] else 0
            sats = int(fields[7]) if fields[7] else 0
        except ValueError:
            return None
        update: dict[str, Any] = {"gps_sats": sats, "gps_fix": quality > 0}
        lat = _to_degrees(fields[2], fields[3])
        lon = _to_degrees(fields[4], fields[5])
        if quality > 0 and lat is not None and lon is not None:
            update["lat"] = round(lat, 6)
            update["lon"] = round(lon, 6)
        return update

    return None


def _to_degrees(value: str, hemisphere: str) -> float | None:
    """Convert NMEA ddmm.mmmm to signed decimal degrees."""
    if not value or not hemisphere:
        return None
    try:
        raw = float(value)
    except ValueError:
        return None
    degrees = int(raw // 100)
    minutes = raw - degrees * 100
    decimal = degrees + minutes / 60.0
    if hemisphere in {"S", "W"}:
        decimal = -decimal
    return decimal


def _checksum_ok(sentence: str) -> bool:
    if "*" not in sentence:
        return True  # some receivers omit it; don't discard on that alone
    body, _, checksum = sentence[1:].partition("*")
    try:
        expected = int(checksum[:2], 16)
    except ValueError:
        return False
    actual = 0
    for char in body:
        actual ^= ord(char)
    return actual == expected
