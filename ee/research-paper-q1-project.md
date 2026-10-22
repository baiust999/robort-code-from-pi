---
name: research-paper-q1-project
description: "Goal, venue, and integrity rules for completing the rescue-robot research paper to Q1"
metadata:
  node_type: memory
  type: project
  originSessionId: d8117ead-295e-48de-a385-5752ae3e34de
  modified: 2026-10-18T11:36:09.146Z
---

Completing `research paper/` into a submission-ready **IEEE Access (Q1)** paper:
"A Low-Cost, Fail-Safe Teleoperated Rescue Robot...". Decided 2026-10-18.

State at start: `research paper.md` = title + TOC only; `section3_methodology.md`
= full Methodology (only section written). All other sections empty.

**Integrity boundary (non-negotiable):** only the bench data in
`tools/eval/results/` is real (latency, faults, resources, GPS static). Per its
`summary.md` "Not yet measured" list, Sections 5.2 (streaming), 5.3 (Wi-Fi
range), 5.7 (field trial), 5.8 (usability/SUS), and parts of 5.1/5.6 have NO
data. User chose: scaffold those with `[PENDING MEASUREMENT]` + protocol + empty
tables; never fabricate numbers. Every Section 5 number must trace to a real CSV
row or sit inside a PENDING block.

**Citations:** use pandoc `[@key]` syntax in the Markdown master; keep
`research paper/references.bib`. NEVER add a bib entry until verified against
Crossref/RFC/official datasheet (Semantic Scholar + DBLP were rate-limited/
blocked; Crossref API worked). Verified so far: casper2003, liu2013, pont2001,
valin2012 (RFC 6716), ublox_neo6.

**Hardware specs user will supply:** DC motor V/RPM/stall/gear; servo model +
torque; battery capacity Ah + continuous discharge A. Tagged `[NEEDS SPEC: ...]`
in Section 3 Table 2.

Constraints: ASCII-only (see [[research-paper-ascii-only]]); Mermaid figure rules
(see [[mermaid-figures-no-back-edges]]). Final packaging = IEEEtran LaTeX from the
Markdown master, Mermaid exported to images/TikZ.

Phase plan in `/home/pi/.claude/plans/gleaming-baking-mccarthy.md`. Phase A
(Section 3 VERIFY repair) done except RQ labels (await Section 1.3) + one
WebRTC-teleop cite.
