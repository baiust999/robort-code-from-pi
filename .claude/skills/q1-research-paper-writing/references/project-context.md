# Project context: low-cost teleoperated rescue robot (firmware-enforced stop)

Facts below were current on 2026-11-03. They are a summary, not the source of
truth. Always inspect the files named here before relying on a fact, and
update this file when a fact changes.

## Target and manuscript files

- Target journal: IEEE Access (Q1 at time of decision, 2026-10-18; re-check).
- Title (decided 2026-11-03): "Firmware-Enforced Stop, Supervised Recovery, and Two-Way Victim Audio and Video on a Teleoperated Rescue Robot"
- Manuscript folder: `research paper/`
  - `section1_introduction.md` ... `section8_conclusion.md` are the sources.
  - `RESEARCH PAPER.md` is the assembled master: front matter + the eight
    section files verbatim + back matter, joined by a single newline. Edit the
    section files, then rebuild the master by concatenation. Never hand-edit
    only the master. Verify the master contains every section file verbatim.
  - `references.bib` (pandoc `[@key]` citations in the Markdown).
  - `archive/` holds pre-rewrite copies and audit notes.
  - `review_paper_v34_final.md` is reference material only (see Citations).
- Final packaging: IEEEtran LaTeX from the Markdown master; Mermaid figures
  exported to images or TikZ.

## Formatting constraints

- ASCII only in `research paper/`. Use `-`, `->`, `Section`, `deg`, `>=`, `<=`,
  `~`, `x`. Check with `grep -P '[^\x00-\x7F]'` before finishing.
- Mermaid figures: all edges leave the hub node in one direction; no reverse
  edges; declare nodes before edges; use `A <-- "label" --> B` for two-way
  links and state direction in the label for input-only pins. Figure 1 is the
  layout reference.

## Evidence base

- Real measurements: `tools/eval/results/` (CSV files, `summary.md`,
  `section5_stats.md`, `log_excerpts/`).
- Corroborating logs: `var/log/p1_events.log` (every Arduino TX/RX, ms
  timestamps), `var/log/telemetry.log` (~1 Hz; lat/lon at 4 dp, so GPS stats
  are resolution-limited), `var/log/p3_events.log` (watchdog). Logs rotate;
  copy any window a claim relies on into `tools/eval/results/log_excerpts/`.
- Hand-entered `record.py` rows carry entry time, not measurement time; only
  the logs can corroborate them.
- After any data change, rerun
  `tools/eval/section5_stats.py --out tools/eval/results/section5_stats.md`
  and the cell-by-cell checker
  `research-analysis/scripts/audit_section5_2026-10-23.py`.

## Measurement status (check Section 5 Table 5.0 for the current state)

- Nine experiments: E1, E4-E9, E15, E16. Every reported result is
  machine-logged; no [VERIFICATION REQUIRED] mark is left in the paper.
- Machine-logged / usable: E1, E7, E8 (all conditions complete after the
  2026-10-21 supply upgrade; driving+media is two spliced logger runs; the
  16 kbps run is confounded by a P2 restart), E6 (16 line-of-sight stations,
  5-250 m, no failure point reached), E9 (resolution-limited), E15 (receipts).
- [PENDING MEASUREMENT] (the experiments still planned, in run order):
  E16 (media isolation, C2), E5 (glass-to-glass media delay, C3), E4 (240 fps
  physical wheel stop, C1; the tape in frame also gives the distance covered
  after drive is removed, with no criterion on it). Each has a claim and pass
  criterion fixed in advance in Section 4 Table 4.2 (q1 Table XVII); never
  change a criterion after its data is seen. Procedures: `experiment.md` and
  `tools/eval/README.md`.
- Deleted 2026-11-23 at the author's request: E13 (field trial), E17 (victim
  communication, 15 participants; its Cochran's Q / McNemar plan is gone too)
  and E18 (person detector, IoU 0.50). None had been run; E13 and E17 needed
  ethics approval and participants; none tests a contribution C1-C4. They were
  removed from `research paper/`, `q1 paper/`, `docs/`, `experiment.md` and
  `tools/eval/README.md` (marked "not in the paper"). The tools stay in the code
  for future work (`detector_*.py`, their tests, `record.py victim_comms` and
  `field`); their evaluation is future work (research paper Section 7.5.2 and
  7.6.4; q1 Section VII). The paper now reports no human-subject experiments
  and has no ethics section or ethics author-input marker. Do not re-add these
  experiments unless the author asks.
- Deleted 2026-11-01 at the author's request: E2, E14 (usability), ablations
  1-2, and the optional E6/E9/E11/F9 extensions.
- Deleted 2026-11-03 at the author's request: E3 (e-stop distance), E10
  (ultrasonic), E11 (DHT11) and E12 (gas) - the four hand-entered sheets -
  from `research paper/`, `q1 paper/` and `tools/eval/` (record.py sheets,
  section5_stats.py and summarize.py blocks; estop_assist.py and estop_auto.py
  deleted). Raw CSVs and the dated `research-analysis/` records were kept
  deliberately and are no longer cited by the paper. E numbers are NOT
  renumbered (gaps E2, E3, E10-E12, E14 are intentional). Source Section
  5.6 is GPS only; Section 5 tables were renumbered to close the gaps (old
  5.4-5.12 -> 5.3-5.11, old 5.16 -> 5.12, old 5.17/5.18 -> 5.13/5.14, then
  the cost tables again to 5.15/5.16 when 5.8 and 5.9 were inserted, and
  to 5.12/5.13 when 5.7-5.9 were deleted on 2026-11-23).
  Section 5 subsections now: 5.1 latency, 5.2 media, 5.3 range, 5.4 faults,
  5.5 resources, 5.6 GPS, 5.7 cost, 5.8 summary. q1 paper: V-G cost,
  V-H experiments without data.
- The old "100-run" field-trial aggregate has no per-run data. Do not restore
  it without real field rows.
- `bench_motor.csv` (60 rows) was collected with the robot on the floor under
  a false "wheels elevated" premise. Never cite it as stationary bench data or
  as a stopping-distance result. Operator confirmations are not independent
  verification.
- E15 cost: receipt-backed 37,158 BDT ~= USD 310 at indicative 1 USD = 120 BDT
  (Oct 2026), parts + build materials only. Webcam, speaker and Pi power bank
  are not itemised. Confirm FX rate/date before submission.
- Battery: 4S3P Li-ion, twelve 18650 cells x 1500 mAh = 4.5 Ah at 14.8 V,
  40 A BMS; separate 50000 mAh USB power bank for the Pi.
- Crash/uptime counts from P3 logs must exclude the deliberate deploy restarts
  and test-load events recorded in the project memory.
- Section 6 "146 unit tests" means 121 (pi/tests) + 25 (research-analysis
  tests), not the full-suite count.

## Claims and framing

- The research gap is a combination on low-cost hardware with measured
  resource cost, never a "first". Two-way voice is common on fielded, costly
  robots (bakzadeh2026); the C3 claim is low-cost single-board two-way audio +
  video with measured resource cost.
- Describe the firmware stop as behaviourally analogous to an IEC 60204-1
  category-0 stop, not as compliant with it.
- Victim-finding aids (Section 3.11: person detection, repeating voice
  message, marks, session recording, tap-to-answer questions) are implemented
  but unevaluated. Keep them out of the abstract, contributions (1.3) and
  conclusion (8.2) until evaluation data exist. The call-out button and reply
  cue were removed; do not re-add them.
- Victim images are stored on the operator device, never on the Pi.

## Citations

- Add a .bib entry only after verifying it against Crossref, an RFC, or an
  official datasheet (Crossref API works; Semantic Scholar/DBLP were blocked).
- Read the abstract (e.g. api.openalex.org/works/doi:...) before describing a
  paper; mark abstract-only table cells [VERIFY AGAINST FULL TEXT]. Past
  mis-descriptions: akgun2023 (rescue-worker affect, not victims),
  shi2025webrtc (WebRTC dental-surgery robot, not SAR).
- Do not cite avi2026review (the authors' own review without a DOI) or its
  corpus statistics. Ask before re-adding it if it gets a DOI.

## Open author inputs

Affiliation, author-name spelling, CRediT contributions, data/code URL + DOI,
acknowledgments, FX rate confirmation, prices of
the three unitemised parts.
