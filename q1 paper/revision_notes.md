# Revision Notes: research paper/ -> q1 paper/manuscript.md

Date: 2026-11-01. Nothing in `research paper/` was modified. Nothing was
committed to git.

## 1. Files in this folder

| File | What it is |
|---|---|
| `manuscript.md` | The IEEE Access manuscript, with numbered citations [n] and the reference list. It is generated, so do not edit it by hand. |
| `build/00_front.md` ... `build/11_appendix.md` | The editable section sources, with pandoc `[@key]` citations |
| `build/build.py` | Assembles `manuscript.md`, numbers citations in order of first use, formats the reference list, and writes `references.bib`. Run `python3 build/build.py` after any edit. |
| `build/citation_order.txt` | The citation number -> bib key map |
| `references.bib` | The 67 cited entries, copied verbatim from `research paper/references.bib` (all verified there) |
| `figures/fig01..fig10_*.png` | The 10 figures, in order of citation |
| `figures/src/*.mmd` | Their Mermaid sources |
| `evidence_map.md` | Every quantitative claim -> file and line or command |

## 2. Structural changes from the source sections

| Change | Why |
|---|---|
| Body cut from about 53,000 words to about 11,900 words of prose (about 15,000 with tables) | IEEE Access length (agreed option 1). The audit narratives, the dated test-suite addenda (116 -> 187 tests) and the withdrawn-claim history are dropped from the paper; they remain in `research paper/` and the repository. |
| Sections renumbered I-VIII with lettered subsections; tables in Roman numerals (I-XVIII, plus A.I and B.I-B.III); figures Fig. 1-10; equations (1)-(5) | IEEE style |
| Source Sections 6.3 and 6.4 moved into VI-C and VI-D | The requested outline: Discussion includes limitations and threats |
| Section 7 cut from 18 directions in 6 themes to 6 short paragraphs; priority table dropped | Length; each kept direction is tied to a limitation in VI-C |
| Source Table 5.0 (evidence status), the planned-protocol blocks and the empty result tables for E2/E4/E5/E13/E14 replaced by Table XVII (one row per missing measurement) | Empty scaffolds do not belong in a journal paper. The protocols stay in the repository |
| Source Table 2.1 condensed from 10 to 6 columns (C1 and C2 merged; "text read" and code-availability columns dropped) | Width. No cell was changed in substance; the "This work" row uses the same figures |
| Victim-finding aids (source 3.11, about 2,100 words) cut to one paragraph (III-K) that states they are implemented and unevaluated | Project rule: they are out of the abstract, contributions and conclusion. Their endpoints and the dashboard details are not needed to judge the evaluated claims |
| Sections 3.3 pin and port details (Figs. 4-5, Tables 3-4 of the source) dropped; only the shared enable line (D4) kept | Not needed to judge the claims; Appendix B keeps the serial protocol |
| Figures dropped: source Figs. 4, 5, 6, 7, 11, 12, 16, 18, 19 and 20 | They duplicate text or tables. Kept: source 1, 2, 3, 8, 9, 10, 13, 14, 15 and 17 (now Fig. 1-10) |
| E1 dead-man results reorganized: the probe table (source 5.2a) folded into the Table IX text; the decomposition (5.2b) is Table IX | One table carries the main result |
| Native firmware test (source Table 5.5d) and simulated heartbeat model (5.5b, 5.5c) condensed into one paragraph and Table XI | They support the stop claim but are not physical measurements; their class is stated |

## 3. Content changes and corrections

| Item | Source said | Manuscript says | Reason |
|---|---|---|---|
| Title | "...on Edge Hardware: Design, Implementation and Experimental Evaluation" | "A Low-Cost Fail-Safe Teleoperated Rescue Robot with Two-Way Victim Audio and Video: Firmware-Bounded Stop, Supervised Recovery and Measured Resource Cost" | States the combination and what was measured. [AUTHOR DECISION: keep or revert] |
| Contribution 1 wording | "A firmware dead-man timer with a ramp stop" | "...that removes drive without help from the Pi" | The dead-man stop is not ramped (PWM 0 and enable low at once; `arduino.ino:79-86`). Only the ordinary S command ramps. The old wording mixed the two |
| motor_stop, 2026-10-07 mean | 314.3 ms (source Table 5.1) | 314.4 ms | Raw mean from `latency.csv` is 314.35 ms; `section5_stats.md` gives 314.4 |
| OpenAlex hit counts (446, 272, 56, 1, 1,204, 34, 61, 11, 14, 65, 970) | In Section 2 | Removed; queries described without counts | The query results are not saved in the repository, so the counts cannot be traced (integrity rule). [AUTHOR ACTION: save the query exports if you want the counts back] |
| "No study of a dead-man or command-timeout stop for a teleoperated rescue robot was found among the results screened" | Section 2 intro | Removed | Without saved screening records it reads as an unsupported absence claim |
| Intro sentence on hand-entered data | "Sections 5 and 6.2" cross-check | "three of the four hand-entered data sets (stopping distance, ultrasonic range and the temperature-error figures) failed that check" | Consistency with Discussion VI-B |
| Speed cap justification | "keeping the 14.8 V battery under the motor's ~12 V rating" | Adds "180/255 x 14.8 V = 10.4 V (CALCULATED)" | Makes the claim checkable |
| SoC temperature of the throttled capture | Not given | 48.2 deg C max (Table XIV) | Computed from `resources.csv` so the table has no blank cell |
| E10 values absent from the session log | Source text lists 75, 150, 284, 389 cm | Same (first draft of the manuscript omitted 150; fixed) | Matches `section5_stats.md:166` |
| Network detail | Pi IP address, router address, SSID | Removed | Not needed; identifying detail |
| CRED economic loss (USD 169.68 billion) | In Section 1.1 | Removed | Length; not used by any argument |
| Dead-man re-arming by camera commands | Described in Section 3.5.2 | Also stated as a consequence in VI-A (a dashboard sending only pan or status commands keeps the robot armed) | Follows directly from the firmware rule confirmed by the native test; a reviewer will ask |

The required statements are all present:

- E3, E10 and the E11 error columns are reported as [VERIFICATION REQUIRED] and support no claim.
- E8 states that `driving+media` is two spliced logger runs and that the 16 kbit/s run is confounded by a P2 restart (20:23 UTC, exit -15 in `log_excerpts/p3_events_2026-10-21_2020-2029.log`) and by an uncommitted configuration change.
- GPS results are stated as limited by the 4-dp logging resolution.
- The 5.7 "100-run" table is absent.
- No crash or uptime count from P3 logs is reported, so the deliberate restarts and test-load kills need no exclusion. If one is added later, exclude them (see `evidence_map.md` Section 5).
- Cost is given as about USD 310 (37,158 BDT at 120 BDT per USD) and the battery as 4S3P 4.5 Ah.
- `avi2026review` is not cited.
- The research gap is framed as a combination (Sections I-A, II-F, VI-A and VIII), never as a first.

## 4. Citations

- 67 entries are cited. All come from `research paper/references.bib`, which the ledger (`research paper/citation.md`) marks VERIFIED. No new reference was added, so no online lookup was needed.
- Every description of a cited paper is carried over from the source sections, whose descriptions were checked against abstracts or full text (ledger). No paper was given a new description, so no new abstract check was needed. Wording was shortened, not changed in meaning.
- Five source entries are no longer cited and are absent from `q1 paper/references.bib`:
  - `adafruit_dht11`: the DHT11 tolerance sentence was dropped.
  - `bangor2008`: the SUS benchmarking protocol was dropped with E14's scaffold.
  - `koczi2025`: the humanoid-safety review sentence was dropped.
  - `tan2020efficientdet` and `lin2014coco`: the detector details were dropped with Section 3.11.
- The reference list is formatted by `build.py` from the .bib fields. Before submission, typeset it with IEEEtran.bst, because the Markdown formatting is approximate. In particular, booktitle abbreviations and the misc entries `[2]`, `[10]` and the `rpi_docs` entry need a manual look.

## 5. Figures

All 20 PNGs in `research paper/figures/` are identical blank 200x150 grey placeholders, so none could be copied. The 10 figures used here were rendered from the Mermaid blocks in `research paper/section3_methodology.md`, using Mermaid 11.17.2 (`mermaid.min.js`, already on disk in a Claude plugin's vendor folder) and the system Chromium in headless mode. The npx download of mermaid-cli was blocked by the sandbox. The output is 2x scale on a white background. Re-render with:

```
cp <path to mermaid.min.js> /some/workdir/
python3 -I "q1 paper/build/render_figures.py" "q1 paper/figures/src" "q1 paper/figures" /some/workdir
```

Known figure issues, to fix before submission:

- Fig. 1: re-laid out top-to-bottom, with the node order changed and the "supervises" labels dropped in favour of dashed lines explained in the caption. The left-to-right source layout overlapped its labels. The WebRTC label still sits close to the GPS line. All edges keep their direction, with no back-edges.
- Fig. 3: the "PWM, enable out" and "servo pulses out" labels overlap near the Arduino. Redraw by hand or in TikZ.
- Figs. 5 and 10 are very wide (aspect ratio about 7:1 and 11:1). At IEEE column width they will be small. Consider a top-to-bottom layout or a two-column figure.
- IEEE Access wants figures at 300 dpi or more in the final upload. The PNGs are 2x screen resolution, so export to vector (SVG or PDF) for the final version.

## 6. Open [PENDING MEASUREMENT] items (Table XVII)

1. E2: true control latency over Wi-Fi, key press to wheel motion at 240 fps.
2. E4: wheel-stop time after a dead-man trip, at 240 fps.
3. E3: stopping distance, repeated with each stop logged by P1 and filmed (current data [VERIFICATION REQUIRED]).
4. E5: glass-to-glass video delay, audio delay each way, frame rate and packet loss, for 1 and 2 viewers and at 20 m.
5. E6: usable-range upper bound, obstructed links, and repeated bursts at a fixed station.
6. E9: static precision at six-decimal resolution against a surveyed point, and a controlled track test.
7. E10: ultrasonic accuracy (current data [VERIFICATION REQUIRED]).
8. E11: DHT11 at further set-points against a reference of stated accuracy (current error figures [VERIFICATION REQUIRED]).
9. E13: field trial with a role-played victim, 5-10 runs.
10. E14: usability study, 8-12 operators.
11. Ablations: dead-man disabled, watchdog disabled, single process.
12. F9: GPS loss and recovery with a single reader on the port.
13. Opus 16 kbit/s ablation: a clean rerun with a committed configuration and no P2 restart, plus the audio-quality side.

## 7. [AUTHOR INPUT REQUIRED] items in the manuscript

1. Author-name spelling and order, affiliations, corresponding author, ORCID.
2. Ethics-committee decision or waiver with reference and date (Section IV-F).
3. Repository URL and archived DOI; choose and add a licence (none exists).
4. Deposit or describe the procurement receipt record.
5. Confirm the BDT -> USD rate and date; price the webcam, the speaker, the Pi power bank and its replacement.
6. CRediT contributions.
7. Funding statement.
8. Conflict-of-interest declaration.
9. Acknowledgments, including the IEEE-required disclosure of AI-assisted writing (sections and tool). Word this yourselves.

IEEE Access also requires author biographies and photographs at submission. They are not drafted here.

## 8. Self-review against the skill's Q1 checklist (Phase 4)

| Check | Result |
|---|---|
| Every number traces to a source | Yes. See `evidence_map.md`, 91 rows. Table X heartbeat intervals and the 121/25 test counts trace to the source text, not to a re-run; recompute Table X from `p1_events.log` excerpts before submission |
| Every citation supports its sentence | Descriptions carried over unchanged in meaning from ledger-checked source text |
| Every reference exists | All 67 are in the verified source .bib |
| Acronyms expanded at first use | Fixed in review: HRI, RTOS, PWM, BMS, ICE, SDP, CEP, SoC, SUS. Common terms (Wi-Fi, USB, CPU, GPS, UDP, TCP, HTTP) are left unexpanded per IEEE practice. [AUTHOR CHECK] |
| Every figure and table cited in text, self-contained caption | Yes, after review. Tables V, XV and XVIII lacked a text citation and were fixed |
| Equation variables defined | Yes, (1)-(5) |
| Methods describe what was done | Yes. The ablations are stated as not run, and E8 as a single capture per condition |
| Results vs discussion separated | Interpretation is kept to short sentences in V; the main interpretation is in VI |
| Conclusions within evidence | Yes. The conclusion repeats measured figures only and lists what remains to be measured |
| Limitations and pending tests visible | VI-C, Table XVII, abstract last sentence |
| ASCII only | `grep -P '[^\x00-\x7F]'` finds 0 hits in `manuscript.md`, `references.bib` and `evidence_map.md` |
| Anti-AI scan | 0 banned words in body prose. Remaining grep hits: "first" as an enumerator (First, ... Second, ...) and in the cited historical fact about the WTC response; "Novel" only inside quoted reference titles. No sentence starts with Furthermore, Moreover or Additionally, and there are no dash asides |
| Abstract length | 246 words (limit 250) |
| Unverifiable statements removed | OpenAlex counts and the absence claim were removed (Section 3 above) |

Residual risks a reviewer may raise:

- n = 10 per fault target and one robot.
- No end-to-end or human-subject data.
- No ablation evidence for the process split.
- The plain-HTTP control key.
- The two range sessions that disagree by 17 dB.
- The C3 contribution is a processor cost only.

These are stated in the paper, not hidden.
