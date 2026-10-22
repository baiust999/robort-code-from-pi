# Log excerpts cited by Section 5

The robot's own logs in `var/log/` rotate (telemetry.log daily, 7 kept; event
logs weekly, 8 kept), so the windows that Section 5 relies on are copied here
unchanged. Extracted on 2026-10-22 (UTC) from `/home/pi/robot/var/log/`.

| File | Source | Window (UTC) | Used for |
|---|---|---|---|
| telemetry_2026-09-29_E9_window.csv | telemetry.log.5.gz | 2026-09-29 15:19-17:29 | E9 static GPS (Table 5.13, 5.13a) |
| telemetry_2026-10-21_E10-E12_1830-1937.csv | telemetry.log.1 | 2026-10-21 18:30-19:37 | E10, E11, E12 cross-checks |
| telemetry_2026-10-22_F9_1200-1320.csv | telemetry.log | 2026-10-22 12:00-13:20 | F9 attempt, second GPS window |
| p1_events_2026-10-07_2100-2259.log.gz | p1_events.log.2.gz | 2026-10-07 21:00-22:59 | E7 F3 serial re-opens |
| p1_events_2026-10-21_1100-1400.log.gz | p1_events.log | 2026-10-21 11:00-13:59 | E1 dead-man (Table 5.2b), E3 drive commands |
| p1_events_2026-10-21_1940-1955.log.gz | p1_events.log | 2026-10-21 19:40-19:55 | F6, F7 (Table 5.9a) |
| p1_events_2026-10-22_1200-1402.log.gz | p1_events.log | 2026-10-22 12:00-14:02 | F9 GPS_FAIL matching, 14:01 heartbeat stalls |
| p3_events_2026-10-21_2020-2029.log | p3_events.log | 2026-10-21 20:20-20:29 | P2 restart between E8 bitrate runs |

Telemetry excerpts keep the file's header line and every row in the window.
Event-log excerpts keep every line that begins with a timestamp in the window;
the continuation lines of multi-line Python tracebacks are not included.
`gps_track_live_2026-10-22.geojson` (one level up) is the response of P1's
read-only `GET /api/gps-track` at 2026-10-22T14:08Z (P1 PID 924, started
2026-10-22T11:39:41Z); the in-memory track it holds is lost when P1 restarts.
