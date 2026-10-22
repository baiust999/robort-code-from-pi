---
name: section5-data-audit
description: 2026-10-22 cross-check of Section 5 CSVs against robot logs; which results are contradicted and how to verify new data
metadata:
  node_type: memory
  type: project
  originSessionId: 2e2650e3-c0c2-4ea0-a8f9-cbe9215ecdd8
  modified: 2026-10-22T17:48:35.925Z
---

On 2026-10-22 every `tools/eval/results/` CSV was cross-checked against the robot's own logs (`var/log/p1_events.log` logs every Arduino TX/RX with ms timestamps; `var/log/telemetry.log` stores telemetry at ~1 Hz). Findings, now written into Section 5 (Table 5.0):

- E10 ultrasonic: 150/284/389 cm readings never occur in any telemetry; marked [VERIFICATION REQUIRED].
- E3 e-stop: no `F60` drive command in any P1 log; distances are >10x what the 0.20 m/s drive and 120 ms ramp allow; marked [VERIFICATION REQUIRED].
- 5.7 field trial: the 100-run aggregate (commit 10de336) has no per-run data; moved into an HTML comment, PENDING restored. Do not restore it without field.csv rows.
- E11 thermal and E12 gas agree with telemetry. E1, E7 and E8 are machine-logged.
- E8 driving+media is two overlapping reslog runs (196 s wall time); the 16 kbps run is confounded by a P2 restart at 20:23, and its bitrate change was never committed.
- telemetry.log writes lat/lon to 4 dp (~11 x 10 m grid), so the E9 GPS stats are resolution-limited.
- Dead-man interval from the P1 log: TX to PANIC max 2042 ms (n=30). F7 Wi-Fi drop tripped the dead-man after 2.02 s.

**Why:** hand-entered `record.py` rows carry entry time, not measurement time, so only the logs can corroborate them.

**How to apply:** check any new Section 5 data against p1_events.log and telemetry.log before writing it up. Logs rotate (telemetry daily, 7 kept), so copy the windows a claim relies on into `tools/eval/results/log_excerpts/`, which the script reads. Rerun `tools/eval/section5_stats.py --out tools/eval/results/section5_stats.md` after any data change. Verify Section 5 tables with a cell-by-cell checker against the CSVs; 485 cells passed on 2026-10-22. The pre-audit text is in `research paper/archive/`.

Follow-up, 2026-10-22:
- P1's live GPS track (`/api/gps-track`, saved as `gps_track_live_2026-10-22.geojson`) held 130 points and 1609 m of path while the robot was not driven, so the 10 m filter admits drift. Section 3.10 is corrected to say so.
- Section 4.2 now states 15 experiments in 9 groups.
- The `fault_watch.csv` 14:01 rows are unplanned P1 heartbeat stalls; a 2.080 s gap tripped the dead-man.
- `New Text Document.txt` is the user's prompt hand-off file: it is uploaded via the GitHub web UI, pulled, then deleted locally. Leave it alone.

Follow-up, 2026-10-22 (later same day): the robot has no thermal camera / IR
imaging hardware, only a DHT11 (ambient temperature + relative humidity).
`tools/eval/results/thermal.csv` was renamed to `dht11_environmental.csv`
(git mv) after confirming its columns (`ref_c/sensor_c/ref_rh/sensor_rh`) are
DHT11 readings, not thermal-imaging data; the `record.py` sheet key changed
`"thermal"` -> `"dht11"` to match. Updated: `tools/eval/record.py`,
`tools/eval/summarize.py`, `tools/eval/README.md`,
`research paper/section4_experimental_setup.md` (E11 row),
`research paper/section5_results.md` (Table 5.0 row + Table 5.15 caption),
and regenerated `tools/eval/results/summary.md`. No thermal-camera/imaging or
victim-detection-by-thermal claims existed anywhere in the manuscript as
current capability (one "Future Work" bullet already correctly lists
"thermal or gas sensing for victim detection" as a deferred hardware
extension, not implemented — left as is). `research-analysis/*.md` (an
earlier same-day audit's output, which had already independently flagged
E11's `error_c==0.0`/E10's `reading_cm==true_cm` non-independent-reading
problem and recommended exactly this [VERIFICATION REQUIRED] framing and
rename) were left unchanged as a dated historical record rather than
rewritten to the new filename. No synthetic data was generated: real DHT11
measurements already exist (flagged [VERIFICATION REQUIRED] for the error
columns, not missing), so fabricating a synthetic replacement was not
warranted. 121/121 `pi/tests` pass after the rename; no hardware touched; no
commit made.

**Why:** the filename "thermal.csv" invited exactly the misreading the user
caught (sounds like thermal-imaging data) even though the prose around it was
already accurate; renaming it removes that trap for future readers/reviewers.

**How to apply:** always refer to E11 as "DHT11 ambient temperature/humidity,"
never "thermal imaging/camera." If more real reference-vs-sensor trials are
recorded, use `record.py dht11 ...` (not `thermal`) and it writes to
`dht11_environmental.csv`.

Related: [[research-paper-q1-project]] [[e8-resource-supply-blocker]].
