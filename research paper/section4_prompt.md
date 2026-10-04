Write **Section 4 (Methodology)** of my research paper and save it as
`research paper/section4_methodology.md`.

## Read these first (all of them, fully)

Paper context:
- `research paper/research paper.md` — the paper's TOC. Section 4 must follow its
  4.1–4.9 headings and subheadings exactly (same numbers, same titles).
- `research paper/section3_system_architecture.md` — the finished Section 3. Match
  its style and tone, and do NOT repeat what it already says; refer back to it
  ("see §3.2", "Table 1") instead. Read its "Author notes" at the end and respect them.
- `research paper/methodology_diagrams.md` — existing Mermaid figures and tables.
  Reuse or adapt them where they fit instead of drawing from scratch.

Source documents in `docs/` (every file):
- `docs/ARCHITECTURE.md` — context/container/component views, scheduler, state
  machines, sequences, data model, failure modes → recovery, victim communication.
- `docs/SOFTWARE_ARCHITECTURE.md` — drivers, component views of firmware/P1/P2/P3/
  dashboard, protocol contract, runtime views, safety architecture, decision record.
- `docs/CAPSTONE_METHODOLOGY_FINAL.md` — full methodology detail (timings, thresholds,
  invariants, protocols). Long: read all of it.
- `docs/high level software architure diagram.md` — high-level software diagram.
- `docs/OPERATOR_MANUAL.md` — mission states, safety behaviour, victim talk, display modes.
- `docs/TEST_REPORT.md` — use only for 4.1.5 (emulation-based verification). Do not
  put results here; results belong to Section 6.

When the docs disagree with each other, the code wins. Check numbers (timeouts,
periods, baud rate, thresholds, ports, pins, PWM limits) against the source in
`arduino/`, `pi/` (p1_control, p2_media, p3_watchdog, common) and `dashboard/src`.
List every contradiction you find in an "Author notes (remove before submission)"
block at the end, like Section 3 does.

## Style: MORE DIAGRAMS, LESS TEXT (most important rule)

I want this section to be mostly diagrams and tables, with very little prose.
The diagrams and tables must carry the explanation; the text only introduces them.

- Each subsection = 1–3 sentences (max ~50 words), then the figure(s)/table(s).
  If something can be shown in a diagram or table, show it there instead of
  writing it as text.
- Every subsection (4.x.y) must have at least one diagram; add a table too where
  there are numbers, parameters or comparisons. Several subsections should have
  two diagrams.
- Overall aim: **30+ figures and 15+ tables**. Prose should be well under half
  the section.
- Before finishing, re-read every paragraph and cut any sentence that only
  repeats what a figure or table already shows.
- No bullet-point walls, no repeated explanations, no marketing words.
- Formulas (stop-time bound, recovery-time model, PWM–voltage, haversine/
  equirectangular distance, drift threshold) as LaTeX `$$ … $$` with a one-line
  variable definition table.
- Academic third person, past/present tense, same voice as Section 3.

## Diagrams

- All diagrams in Mermaid (` ```mermaid `), must render on mermaid.live.
- Pick the right type: `sequenceDiagram` for flows/handshakes/heartbeats/WebRTC
  signalling; `stateDiagram-v2` for firmware modes, mission state, display mode,
  floor control; `flowchart` for validation pipelines, supervision, drift filter,
  decision logic; `gantt` or timeline-style flowchart for scheduler task periods and
  fault-detection/recovery timing.
- Keep each diagram small (≤ ~15 nodes) and readable in print; split if larger.
- Put real values on edges/nodes (ms, Hz, ports, thresholds).

Suggested diagrams/tables (adapt as needed):
- 4.1: failure-domain diagram; drivers → structural consequence table; protocol
  contract message table (type, direction, fields, rate); end-to-end command/
  telemetry/media sequence; emulation test setup diagram.
- 4.2: scheduler task table (task, period, priority, max blocking); timer/pin
  allocation table; 4-stage validation flowchart; firmware mode state machine;
  differential-drive mixing + PWM ramp table.
- 4.3: defense-in-depth layer diagram (dashboard → P1 → firmware); edge validation
  checks table; heartbeat/dead-man timing sequence + stop-time bound formula;
  disconnect stop sequence; E-STOP priority path; gas panic-stop flowchart;
  ultrasonic advisory zones table.
- 4.4: telemetry pipeline flowchart; startup handshake sequence; single-writer
  enforcement table; frame format table; 200 ms broadcast cycle; server-owned vs
  firmware-owned fields table; ring buffer/session-resume sequence; alert thresholds
  table + bit-packed log layout.
- 4.5: supervision hierarchy (systemd → P3 → P1/P2); liveness checks table;
  exit-code → restart policy table; detection + recovery time model; degradation
  modes table (what fails / what still works).
- 4.6: mission-state first-match function as a decision flowchart + truth table;
  reconnection policy table (control vs media: backoff, limits).
- 4.7: WebRTC architecture diagram; signalling sequence; capture fan-out diagram;
  Opus packetisation/playout parameters table; capture fallback state machine;
  floor control / push-to-talk state machine; display-mode arbitration diagram.
- 4.8: role/permission matrix; controller-key takeover sequence; lockout parameters
  table; cross-process role consistency diagram.
- 4.9: NMEA parse + checksum flowchart; distance formula; drift-suppression flowchart
  with thresholds; offline map serving (HTTP range) sequence.

## Numbering and references

- Section 3 ends at Table 6 and Figure 6. Start Section 4 at **Table 7** and
  **Figure 7** and count up.
- Captions as in Section 3: `**Figure N.** Caption.` / `**Table N.** Caption.`
  placed directly above the figure/table, and reference each one in the text.
- Cross-reference other sections with `§` (e.g. §3.4.2, §6.4).

## Rules

- Use only facts from the docs and code. Never invent measurements; anything not
  measured is labelled "design value" or "configured value".
- Do not modify any other file.
- When done, give me: the file path, a count of figures and tables, and the list
  of author notes/contradictions.
