#!/usr/bin/env python3
"""Static GPS accuracy from telemetry.log, for paper Section 5.6.

Leave the robot stationary outdoors with a fix for 30 minutes, then point this
at the telemetry log. It takes the fixed samples in the window, treats their
centroid as the reference position, and reports the radial error distribution:
mean, SD, RMS, CEP50 and CEP95. CEP50 is the circle containing half the fixes
and is the figure GNSS papers quote.

    ./gpsdrift.py --minutes 30
    ./gpsdrift.py --log var/log/telemetry.log --from 2026-10-08T09:00 --to 2026-10-08T09:30

With --ref-lat/--ref-lon (a surveyed point, or an averaged phone fix) the error
is measured against that instead of the centroid, which also captures bias
rather than scatter alone. Scatter around the centroid is precision; distance
from a known point is accuracy. Say which one the paper reports.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import RESULTS_DIR, append_row, haversine_m, now_iso, percentile, to_float  # noqa: E402

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "var" / "log" / "telemetry.log"
COLUMNS = ("iso_ts", "label", "n_samples", "duration_min", "window_from", "window_to",
           "ref_mode", "ref_lat", "ref_lon", "mean_m", "sd_m", "rms_m",
           "cep50_m", "cep95_m", "max_m", "mean_sats")


def parse_time(text: str) -> datetime:
    stamp = datetime.fromisoformat(text)
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


# telemetry.log writes its header once, when the file is created, and logrotate
# is what starts a new one. A log that predates a change to
# p1_control/telemetry_log.py:CSV_COLUMNS therefore carries a header that no
# longer describes its own rows -- csv.DictReader maps by position and would
# read lat/lon/gps_fix out of whatever now sits in those columns. Rows are
# mapped by field count instead, and a mismatch is reported rather than
# silently mis-parsed.
CURRENT_COLUMNS: tuple[str, ...] = (
    "iso_ts", "seq", "temperature_c", "humidity_pct", "gas_ppm", "range_cm",
    "pan_angle", "tilt_angle", "fw_state", "uptime_ms", "lat", "lon",
    "gps_fix", "gps_sats", "serial_ok", "ws_clients", "turn_status", "alert_flags",
)

# The two earlier layouts this log has carried, from git history of
# telemetry_log.py: 51962a2 (initial, with motion + ir_left/ir_right) and
# b497cb4 (ir sensors dropped). 3a537de dropped motion, giving CURRENT_COLUMNS.
LEGACY_COLUMNS: tuple[tuple[str, ...], ...] = (
    (
        "iso_ts", "seq", "temperature_c", "humidity_pct", "gas_ppm", "motion",
        "range_cm", "ir_left", "ir_right", "pan_angle", "tilt_angle", "fw_state",
        "uptime_ms", "lat", "lon", "gps_fix", "gps_sats", "serial_ok",
        "ws_clients", "turn_status", "alert_flags",
    ),
    (
        "iso_ts", "seq", "temperature_c", "humidity_pct", "gas_ppm", "motion",
        "range_cm", "pan_angle", "tilt_angle", "fw_state", "uptime_ms", "lat",
        "lon", "gps_fix", "gps_sats", "serial_ok", "ws_clients", "turn_status",
        "alert_flags",
    ),
)


def row_mapper(header: list[str]) -> tuple[dict[int, tuple[str, ...]], bool]:
    """Layouts keyed by field count, and whether the file's header is stale."""
    layouts = {len(columns): columns for columns in LEGACY_COLUMNS}
    layouts[len(CURRENT_COLUMNS)] = CURRENT_COLUMNS
    stale = len(header) != len(CURRENT_COLUMNS)
    if stale:
        layouts.setdefault(len(header), tuple(header))
    return layouts, stale


def load_fixes(log: Path, start: datetime | None, end: datetime | None) -> list[tuple[datetime, float, float, float]]:
    """Fixed samples in the window, mapped by field count (see above)."""
    fixes: list[tuple[datetime, float, float, float]] = []
    skipped = 0
    with log.open(newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return fixes
        layouts, stale = row_mapper(header)
        if stale:
            print(f"warning: {log} has a {len(header)}-column header but the current "
                  f"format has {len(CURRENT_COLUMNS)}. Rows are being mapped by field "
                  f"count. Rotate the log (`sudo logrotate -f /etc/logrotate.d/robot`) "
                  f"so new data gets a correct header.", file=sys.stderr)
        for fields in reader:
            columns = layouts.get(len(fields))
            if columns is None:
                skipped += 1
                continue
            row = dict(zip(columns, fields))
            if str(row.get("gps_fix", "")).strip() not in ("1", "true", "True"):
                continue
            lat, lon = to_float(row.get("lat")), to_float(row.get("lon"))
            if lat is None or lon is None or (lat == 0 and lon == 0):
                continue
            try:
                stamp = parse_time(row["iso_ts"])
            except (KeyError, ValueError):
                continue
            if start and stamp < start:
                continue
            if end and stamp > end:
                continue
            fixes.append((stamp, lat, lon, to_float(row.get("gps_sats")) or 0.0))
    if skipped:
        print(f"warning: skipped {skipped} rows whose field count matched no known "
              f"layout", file=sys.stderr)
    return fixes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--minutes", type=float, help="use the last N minutes of the log")
    parser.add_argument("--from", dest="start", help="ISO start of the static window")
    parser.add_argument("--to", dest="end", help="ISO end of the static window")
    parser.add_argument("--ref-lat", type=float, help="known reference latitude")
    parser.add_argument("--ref-lon", type=float, help="known reference longitude")
    parser.add_argument("--label", default="static-30min")
    parser.add_argument("--out", type=Path, default=RESULTS_DIR / "gps_static.csv")
    args = parser.parse_args()

    if not args.log.exists():
        print(f"no such log: {args.log}", file=sys.stderr)
        return 2

    start = parse_time(args.start) if args.start else None
    end = parse_time(args.end) if args.end else None
    if args.minutes:
        start = datetime.now(timezone.utc) - timedelta(minutes=args.minutes)

    fixes = load_fixes(args.log, start, end)
    if len(fixes) < 2:
        print(f"only {len(fixes)} fixed samples in the window. The robot needs a GPS fix "
              f"outdoors; check gps_fix in {args.log}.", file=sys.stderr)
        return 1

    if args.ref_lat is not None and args.ref_lon is not None:
        ref_lat, ref_lon, mode = args.ref_lat, args.ref_lon, "known-point"
    else:
        ref_lat = statistics.fmean(lat for _, lat, _, _ in fixes)
        ref_lon = statistics.fmean(lon for _, _, lon, _ in fixes)
        mode = "centroid"

    errors = sorted(haversine_m(ref_lat, ref_lon, lat, lon) for _, lat, lon, _ in fixes)
    duration = (fixes[-1][0] - fixes[0][0]).total_seconds() / 60
    row = {
        "iso_ts": now_iso(), "label": args.label, "n_samples": len(fixes),
        "duration_min": round(duration, 1),
        "window_from": fixes[0][0].isoformat(timespec="seconds"),
        "window_to": fixes[-1][0].isoformat(timespec="seconds"),
        "ref_mode": mode, "ref_lat": round(ref_lat, 7), "ref_lon": round(ref_lon, 7),
        "mean_m": round(statistics.fmean(errors), 2),
        "sd_m": round(statistics.stdev(errors), 2) if len(errors) > 1 else "",
        "rms_m": round((sum(e * e for e in errors) / len(errors)) ** 0.5, 2),
        "cep50_m": round(percentile(errors, 50), 2),
        "cep95_m": round(percentile(errors, 95), 2),
        "max_m": round(errors[-1], 2),
        "mean_sats": round(statistics.fmean(f[3] for f in fixes), 1),
    }
    append_row(args.out, COLUMNS, row)

    print(f"{row['n_samples']} fixes over {row['duration_min']} min, reference: {mode}")
    print(f"  mean {row['mean_m']} m   SD {row['sd_m']} m   RMS {row['rms_m']} m")
    print(f"  CEP50 {row['cep50_m']} m   CEP95 {row['cep95_m']} m   max {row['max_m']} m")
    print(f"  mean satellites {row['mean_sats']}")
    print(f"  appended to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
