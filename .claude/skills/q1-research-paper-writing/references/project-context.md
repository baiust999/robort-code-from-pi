# Project context: low-cost fail-safe teleoperated rescue robot

Facts below were current on 2026-11-01. They are a summary, not the source of
truth. Always inspect the files named here before relying on a fact, and
update this file when a fact changes.

## Target and manuscript files

- Target journal: IEEE Access (Q1 at time of decision, 2026-10-18; re-check).
- Working title: "A Low-Cost, Fail-Safe Teleoperated Rescue Robot..."
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

- Machine-logged / usable: E1, E7, E8 (all conditions complete after the
  2026-10-21 supply upgrade; driving+media is two spliced logger runs; the
  16 kbps run is confounded by a P2 restart), E11 DHT11 and E12 gas agree with
  telemetry.
- [VERIFICATION REQUIRED]: E3 e-stop distances (contradicted by P1 logs),
  E10 ultrasonic (values never appear in telemetry), E11 error columns.
- [PENDING MEASUREMENT] (the only experiments still planned): E3 and E10
  repeats, E5, E4, E16 (media isolation, Table 5.8e), E13. Each has a claim
  and pass criterion fixed in advance in Section 4 Table 4.2 (q1 Table XVII);
  never change a criterion after its data is seen.
- Deleted 2026-11-01 at the author's request: E2, E14 (usability), ablations
  1-2, and the optional E6/E9/E11/F9 extensions. E numbers are NOT
  renumbered (gaps E2, E14 are intentional). Source Sections 5.8 = Cost,
  5.9 = Summary; source Tables 5.3-5.18 were renumbered after deleting old 5.3.
- The 5.7 "100-run" aggregate has no per-run data. Do not restore it without
  real field rows.
- `bench_motor.csv` (60 rows) was collected with the robot on the floor under
  a false "wheels elevated" premise. Never cite it as stationary bench data or
  as E3 data. Operator confirmations are not independent verification.
- E11 is DHT11 ambient temperature/humidity. The robot has no thermal camera.
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
acknowledgments, ethics-approval reference, FX rate confirmation, prices of
the three unitemised parts.
