# Section 2 (Related Work) -- Pre-submission Audit, IEEE Access

Date: 2026-10-22
Target: research paper/section2_related_work.md (70 lines, approx. 3,890 words incl. table)
Also read: references.bib, citation.md, research paper.md (outline), section3_methodology.md
(Sections 3.0-3.10, focused on 3.2, 3.5, 3.7, 3.9), and Section 5.2/5.5/5.9 where Section 2
points to them.
Mode: REPORT ONLY. No file other than this report was changed.

## 0. How the verification was done

- Metadata: every key with a DOI (47 of 49) was resolved through api.crossref.org/works/<DOI>
  and compared field by field with references.bib (title, authors, venue, volume, issue,
  pages/article number, year). Script output kept in the session scratchpad.
- Retraction / correction: Crossref "updated-by"/"update-to" fields and OpenAlex
  "is_retracted" were checked for all 47 DOIs. All returned no update and is_retracted=false.
  A separate "<title> retraction" web search was NOT run for each of the 49 titles; the
  Crossref + OpenAlex flags are the retraction evidence used here.
- Content: abstracts were fetched from OpenAlex (api.openalex.org) or Crossref for 45 keys.
  Full text was read (Europe PMC / arXiv / RFC Editor) for: khattab2025 (PMC12660968),
  bakzadeh2026 (PMC13487453), bakzadeh2026b (PMC12932144), schneider2016 (arXiv:1912.04693),
  akgun2023 (arXiv:2208.09580), valin2012 (RFC 6716 text).
- Not reachable: Springer (cookie wall), ScienceDirect (HTTP 403), IEEE Xplore full text.
  These are listed in Part F.5.
- Gap-disproof and coverage searches: 7 web searches (Part C 2.6 and Part D.5).

Status legend (Part A): PASS = exists and bib matches the authoritative record;
FIX = exists but bib or usage needs a correction; UNVERIFIED = could not be checked online;
FAKE = does not exist (none found).

=====================================================================
## PART A -- CITATION EXISTENCE
=====================================================================

A.1 Key bookkeeping (mechanical check)

- All 49 Section 2 keys exist in references.bib. Missing keys: none.
- references.bib has 57 entries. The 8 not cited in Section 2 (adafruit_dht11, bangor2008,
  brooke1996, cred2026, rpi_docs, tabib2024, ublox_neo6, wilson1927) are each cited elsewhere
  in the paper (Sections 1/3/5). Uncited bib entries anywhere: none.
- All 49 keys have a row in citation.md.
- Duplicate entries for the same paper: none found (all 49 DOIs/identifiers distinct).
- avi2026review: not present in Section 2, references.bib, citation.md or the outline. It
  survives only in archive/section5_results_pre-audit_2026-10-22.md (archive copy, not
  submitted) -- no action needed.

A.2 Batch results. URL column: https://doi.org/<DOI> unless noted.

Batch 1 (1-10)

| # | key | in bib | found online | metadata errors | status |
|---|---|---|---|---|---|
| 1 | akgun2023 | yes | doi 10.1109/TAFFC.2022.3221922; preprint arXiv:2208.09580 | none (journal version correctly cited, not the preprint) | PASS |
| 2 | bachhuber2016 | yes | doi 10.1109/ICIP.2016.7532735 | none | PASS |
| 3 | bakzadeh2025 | yes | doi 10.3390/robotics14110148 | none | PASS |
| 4 | bakzadeh2026 | yes | doi 10.3389/frobt.2026.1857704; full text PMC13487453 | none (Crossref lists initials only; bib matches Crossref) | PASS |
| 5 | bakzadeh2026b | yes | doi 10.3389/frobt.2026.1698570; full text PMC12932144 | none | PASS |
| 6 | bethel2007 | yes | doi 10.1145/1228716.1228755 | none | PASS |
| 7 | cafolla2026 | yes | doi 10.1016/j.robot.2025.105237 | none (vol 196, art. 105237, Feb 2026) | PASS |
| 8 | candea2004 | yes | doi 10.1109/mc.2004.219 | none | PASS |
| 9 | cantizani2022 | yes | doi 10.1109/access.2022.3204272 | none | PASS |
| 10 | casper2003 | yes | doi 10.1109/TSMCB.2003.811794 | none | PASS |

Batch 2 (11-20)

| # | key | in bib | found online | metadata errors | status |
|---|---|---|---|---|---|
| 11 | chen2007 | yes | doi 10.1109/TSMCC.2007.905819 | none | PASS |
| 12 | chitikena2023 | yes | doi 10.3390/app13031800 | none | PASS |
| 13 | chung2023 | yes | doi 10.1146/annurev-control-062722-100728 | none | PASS |
| 14 | daun2023 | yes | doi 10.1109/SSRR59696.2023.10499930 | none | PASS |
| 15 | delmerico2019 | yes | doi 10.1002/rob.21887 | none (online Aug 2019, issue Oct 2019) | PASS |
| 16 | iec60204 | yes | IEC webstore pub. 26037: https://webstore.iec.ch/en/publication/26037 | Edition 6.0 (2016-10-13) exists, but the current valid IEC version is the consolidated IEC 60204-1:2016+AMD1:2021 CSV (Ed. 6.1). Ed. 7.0 is under development (forecast 2028). Normative clause text not read by anyone (bib comment says so). | FIX |
| 17 | jacoff2012 | yes | doi 10.1145/2393091.2393126 | none | PASS |
| 18 | jia2025 | yes | doi 10.3390/app15168792 | none | PASS |
| 19 | kareem2026 | yes | doi 10.1109/ACCESS.2026.3660002 | Author name split differs: Crossref family names are "Aqeel Kareem", "Jabbar Abid", "Abdulelah Al-Naji"; bib uses "Kareem, Abbas Aqeel" etc. Check IEEE Xplore author display so the printed initials match. | FIX (minor) |
| 20 | kawatsuma2012 | yes | doi 10.1108/01439911211249715 | none | PASS |

Batch 3 (21-30)

| # | key | in bib | found online | metadata errors | status |
|---|---|---|---|---|---|
| 21 | khattab2025 | yes | doi 10.1038/s41598-025-16003-7; full text PMC12660968 | none | PASS |
| 22 | kim2023 | yes | doi 10.3390/machines11030329 | none | PASS |
| 23 | koczi2025 | yes | doi 10.3390/electronics14234734 | none | PASS |
| 24 | liu2013 | yes | doi 10.1007/s10846-013-9822-x | none (online Mar 2013, issue Nov 2013). Abstract elided by publisher in OpenAlex and Semantic Scholar; Springer page not reachable. | PASS (metadata) |
| 25 | liu2026hexapod | yes | doi 10.1016/j.mechmachtheory.2026.106472 (Elsevier PII S0094114X26001229) | none in metadata. No abstract obtainable (OpenAlex none, Semantic Scholar not indexed, ScienceDirect 403). | PASS (metadata); content UNVERIFIED |
| 26 | luz2023 | yes | doi 10.1109/access.2023.3240307 | none | PASS |
| 27 | manuel2022 | yes | doi 10.1109/access.2022.3178437 | none | PASS |
| 28 | megalingam2022 | yes | doi 10.1080/01691864.2022.2117575 | none | PASS |
| 29 | militano2023 | yes | doi 10.3390/fi15020055 | none | PASS |
| 30 | murphy2004 | yes | doi 10.1109/MRA.2004.1337826 | none | PASS |

Batch 4 (31-40)

| # | key | in bib | found online | metadata errors | status |
|---|---|---|---|---|---|
| 31 | murphy2010 | yes | doi 10.1109/hri.2010.5453233 | none (2-page paper, pp. 127-128) | PASS |
| 32 | murphy2011 | yes | doi 10.1109/icra.2011.5979977 | none | PASS |
| 33 | nagatani2013 | yes | doi 10.1002/rob.21439 | none (online Oct 2012, issue Jan 2013; 2013 is correct for IEEE style) | PASS |
| 34 | narasimhan2024 | yes | doi 10.1109/lra.2023.3340525 | none | PASS |
| 35 | pont2001 | yes | ISBN 0201331381 via https://openlibrary.org/search.json?isbn=0201331381 | Title, author, year confirmed (OpenLibrary). Publisher/address (Addison-Wesley, Harlow) not shown by the fetched record. | PASS (publisher UNVERIFIED) |
| 36 | pramono2024 | yes | doi 10.25077/jnte.v13n1.1191.2024 -> http://jnte.ft.unand.ac.id/index.php/jnte/article/view/1191 | Crossref omits volume/issue; publisher page confirms Vol 13 No 1, pp. 51-59, Mar 2024. Bib correct. | PASS |
| 37 | raghavan2026 | yes | doi 10.1016/j.rineng.2026.110608 | Crossref splits "V, Berlin Hency"; bib has "Hency V, Berlin". Check printed name form. | FIX (minor) |
| 38 | ramesh2022 | yes | doi 10.1109/lra.2022.3192612 | none | PASS |
| 39 | ruan2025 | yes | doi 10.3389/frobt.2025.1694123 | none | PASS |
| 40 | schneider2016 | yes | doi 10.1109/carpathiancc.2016.7501177; arXiv:1912.04693 (journal-ref = this ICCC paper) | none | PASS |

Batch 5 (41-49)

| # | key | in bib | found online | metadata errors | status |
|---|---|---|---|---|---|
| 41 | schrick2025 | yes | doi 10.1016/j.robot.2024.104795 | none | PASS |
| 42 | shi2025webrtc | yes | doi 10.1109/ACCESS.2025.3620994 | none | PASS |
| 43 | sinha2026 | yes | doi 10.3390/s26051659 | none | PASS |
| 44 | srinivasan2012 | yes | doi 10.1109/ssrr.2012.6523916 | none (2-page paper, pp. 1-2) | PASS |
| 45 | tiberkak2023 | yes | doi 10.1007/s41315-023-00281-3 | none | PASS |
| 46 | tong2024 | yes | doi 10.1109/IV55156.2024.10588685 | none | PASS |
| 47 | valin2012 | yes | doi 10.17487/RFC6716; text https://www.rfc-editor.org/rfc/rfc6716.txt | none (Crossref author record for Valin is malformed; RFC header confirms Valin, Vos, Terriberry) | PASS |
| 48 | verano2022 | yes | doi 10.14569/IJACSA.2022.01307104 | No pages in bib (IJACSA uses paper numbers; DOI suffix implies paper 104 of 13(7)); add "Paper 104" or pages if available. Venue-quality concern, see A.3. | FIX (minor) |
| 49 | yamauchi2022 | yes | doi 10.1186/s40648-022-00223-x | none (art. 8, vol 9) | PASS |

A.3 Venue / integrity flags

- Retractions: none (Crossref + OpenAlex flags, see Section 0).
- Preprint-instead-of-published: none. akgun2023 and schneider2016 have arXiv versions; the
  published versions are cited. The schneider2016 quote was read in the arXiv copy (bib
  comment says so); the ICCC text was not compared.
- Predatory / low-tier venues -- UNVERIFIED, flagged for author judgement:
  - verano2022, IJACSA (The Science and Information Organization). The publisher states
    Scopus indexing; I could not confirm its current Scopus status or quartile online. Some
    reviewers treat this venue with suspicion. It is used only as a platform example.
  - pramono2024, Jurnal Nasional Teknik Elektro (Indonesian national journal). Indexing
    (SINTA/Scopus/DOAJ) not confirmed from the article page.
  Neither is fake, but both carry weight in Table 2.1; consider whether they are needed.
- iec60204 (detail): bib cites IEC 60204-1:2016 Ed. 6.0. Recommend citing
  "IEC 60204-1:2016+AMD1:2021 CSV" (the current consolidated version) or stating Ed. 6.0
  deliberately. Clause relied on: 9.2.2 (stop categories 0/1/2); only category 0 is used.
  The wording "stopping by immediate removal of power to the machine actuators (i.e. an
  uncontrolled stop)" is the commonly quoted text (vendor guides), but the normative text was
  not read -- see Part B, row B-27, and Part C 2.3 for the larger problem.

=====================================================================
## PART B -- CITATION ACCURACY
=====================================================================

Verdicts: ACCURATE / OVERSTATED / WRONG / NOT SUPPORTED BY ABSTRACT / UNVERIFIED.
"Src" quotes are from the fetched abstract unless marked (FT) = full text.
Curly quotes and dashes in sources have been transcribed to ASCII.

### 2.1 (line 9 and 11)

B-1 | L9 | liu2013 | "Liu and Nejat surveyed robotic urban search and rescue from the control
perspective" | Src: title only; abstract elided by publisher. S2 TLDR: "efforts ... towards
developing low-level controllers for rescue robot autonomy in traversing uneven terrain and
stairs, and perception-based SLAM". | ACCURATE (title-level).

B-2 | L9 | delmerico2019 | "...observe that field-deployable rescue technology has requirements
for robustness, speed, versatility and ease of use that the state of the art ... may not meet"
| Src: "field-deployable technologies for rescue work have requirements for robustness, speed,
versatility, and ease of use that may not be matched by the state of the art in robotics
research" | ACCURATE.

B-3 | L9 | schneider2016 | "reviewed SAR robotics as an applied benchmark ... set out
SAR-specific requirements on each component" | Src: "SAR-specific demands and requirements on
the various components of a robotic system are pictured ... SAR applications as an applied
benchmark" | ACCURATE.

B-4 | L9 | kareem2026 | "analysed 74 papers published between 2016 and 2024 ... five-layer
architecture of HRI, Perception, Navigation, Control and Robot layers ... multi-robot
coordination, AI-based real-time decision-making and energy efficiency" | Src: identical
figures and list | ACCURATE.

B-5 | L9 | sinha2026 | "more than 190 studies from 2020 to 2025 restricted to UGVs ... energy
limitations, robustness in harsh conditions and the lack of standardised benchmarks" | Src:
"over 190 recent studies (2020-2025)", "focuses exclusively on UGVs", "energy limitations,
robustness in harsh conditions, and the lack of standardized benchmarks" | ACCURATE.

B-6 | L9 | bakzadeh2026 | "reviewed the coal-mine rescue robots documented over three decades
... comprehensive guidelines ... have not been established" | Src: "comprehensive guidelines
for the design and deployment of robots in harsh underground environments have not been
established ... documented CMRRs of the last 3 decades" | ACCURATE as far as it goes, BUT
SELECTIVE: the same paper (FT) states "Two-way voice capabilities are also a fundamental
functionality of most of the reviewed MRRs", "two-way audio is a common functionality for most
mine rescue robots", and lists ANDROS Wolverine V2 ("two-way voice communication systems"),
CUMT-V ("intrinsically safe two-way audio systems") and Inuktun VGTV ("microphone, a
speaker"). Section 2 cites this review but omits the finding that most directly bears on C3.
See REJECT-RISK issue #1.

B-7 | L9 | tong2024 | "emphasis on deficiencies in perception systems" | Src: "highlights
deficiencies in both software and hardware, particularly focusing on perception systems" |
ACCURATE.

B-8 | L9 | (synthesis) "the safety of the control path and the interaction between robot and
trapped person are not their organising concerns" | kareem2026 is titled "Safe Search and
Rescue Operations ..." and has an HRI layer; bakzadeh2026 treats two-way voice as a core
requirement. "Not organising concerns" is defensible for most, but a reviewer will read it
against those two titles. | OVERSTATED (soften: "neither is the axis along which they
organise the field").

B-9 | L11 | daun2023 | "drawing on reports of past deployments and workshops with first
responders, state that rescue robots are typically teleoperated in actual disasters" | Src:
"they are typically teleoperated in actual disasters ... reports of past deployments ...
insights from workshops with first responders" | ACCURATE.

B-10 | L11 | chen2007 | "teleoperation will remain an important default mode even for
autonomous and semi-autonomous systems" | Src: "Even for autonomous and semiautonomous systems,
teleoperation will be an important default mode" | ACCURATE.

B-11 | L11 | (no citation) four levels of operator involvement | No source cited for the
taxonomy; "Shared-Collaborative Control" is not a standard term. | NOT SUPPORTED (missing
reference). Note: schneider2016 (FT, already cited) says SAR robots "in practice ... are
either tele-operated or semi-autonomous" and calls semi-autonomous operation "supervisory
control" -- usable support. A standard LOA reference is proposed in Part D.5.

### 2.2 (lines 15-23)

B-12 | L15 | murphy2004 | "WTC collapse in September 2001 is the first known use of robots
for urban search and rescue; ... mobility, sensors, control, communications and power" | Src:
"this is the first known use of robots for urban search and rescue (USAR) ... components
(mobility, sensors, control, communications, and power)" | ACCURATE. Dates (11-21 Sept 2001)
correct.

B-13 | L15 | casper2003 | "the first study of HRI during an unstaged rescue, produced 17
findings and 11 recommendations, including calls for ... perceptual and assistive interfaces
and for formal models of the robot's state" | Src: "study the HRI during a real unstaged rescue
for the first time ... 17 findings ... Eleven recommendations ... more research into
perceptual and assistive interfaces, and formal models of the state of the robot" | ACCURATE.

B-14 | L15 | nagatani2013 | "tests in a comparable plant indicated that robust wireless
communication would not be possible inside the reactor buildings, so the deployed robots were
fitted with a wired communication device" | Src: "performed at the Hamaoka ... similar to the
target environment ... robust wireless communication would not be possible in the reactor
buildings ... a wired communication device would need to be installed" | ACCURATE (minor:
"the deployed robots" -- abstract says "one of the robots was delivered"; say "the deployed
robot").

B-15 | L15 | kawatsuma2012 | "organisation, operation scheme and systemisation as the major
lessons" | Src: "organization and operation scheme, and systemization were major lessons
learned" | ACCURATE.

B-16 | L15 | daun2023 | "identify a need for approaches that combine the complementary
capabilities of human operators and robotic assistance functions" | Src: "need for an
increased research focus on novel approaches combining the complementary capabilities of human
operators and robotic assistance functions" | ACCURATE, but misplaced: it sits in the
"field deployments" paragraph and is followed by "Loss or degradation of the link ... is
therefore an expected operating condition". Daun's point is about assistance functions, not
links; the "therefore" rests on nagatani2013 alone. | LOGIC GAP (see issue #9).

B-17 | L17 | jacoff2012 | "Standard test methods for response robots have been developed and
refined through competitions" | Src: "Competitions are an effective aid to the development
... of standard test methods ... rapid iterative refinement of the test methods" | ACCURATE.

B-18 | L17 | chung2023 | "DARPA Subterranean Challenge (2018-2021) evaluated integrated
systems for complex underground environments in physical and simulated contests" | Src:
"multiyear (2018-2021) ... integrated technologies for operating in complex underground
environments ... physical and simulated contests" | ACCURATE. The follow-on claim "at platform
budgets far above that of a single-board robot" has no citation. | NOT SUPPORTED (add source
or drop).

B-19 | L19 | megalingam2022 | "tracked robot with four assistive flippers and a 4-DoF
manipulator, built on ROS ... best-in-class dexterity award" | Src: matches ("tracks and four
assistive flippers", "4-DoF robotic manipulator", "ROS framework", "best-in-class dexterity
award at the WRS 2020") | ACCURATE.

B-20 | L19 | verano2022 | "low-cost tracked explorer with a camera, gas sensors and a
real-time data display, which a human operator monitors and controls remotely; tested on
uneven surfaces in a simulated disaster environment" | Src: matches | ACCURATE.

B-21 | L19 | pramono2024 | "report Bluetooth communication up to 10 m and video transmission
up to 12 m in field experiments" | Src: "Rigorous lab tests validated ... Bluetooth
communication ranges up to 10 meters ... Further field experiments showcased ... video signals
over distances up to 12 meters" | OVERSTATED (Bluetooth figure is from lab tests, not field
experiments; Table 2.1 already says "10 m lab"). Minor.

B-22 | L19 | khattab2025 | "SERR, a robot controlled from a smartphone application, which fuses
visual, thermal and audio data in a CNN-LSTM survivor detector validated by MATLAB simulation
on USGS-PAGER data" | Src: matches | ACCURATE.

B-23 | L19 | manuel2022 | "LoRa LPWAN architecture ... Rescuer, monitored and controlled from
a remote base station in Gazebo simulation and a laboratory test setup" | Src: matches |
ACCURATE.

B-24 | L19 | cafolla2026 | "connects to any robot accepting text commands ... voice-guided
control, 3D reconstruction and person tracking, tested on a drone and a quadruped in wind of
23 km/h and noise up to 100 dB" | Src: "any robotic platform ... that supports text-based
command communication via network or cable ... high-wind (23 km/h) and noisy environments
(70-100 dB for the Drone, 65-99.6 dB for the Quadruped)" | ACCURATE.

B-25 | L21 | jia2025 | "separation-cage structure removes the sensor occlusion of earlier caged
drones, with a 1.2 kg prototype reaching 40 min endurance at full 1 kg payload" | Src:
"addresses the occlusion issue of sensing components in traditional caged UAVs ... 1.2 kg with
a 1 kg payload capacity, achieves a 40 min maximum endurance under full payload" | Numbers
ACCURATE; "removes" OVERSTATED vs "addresses". Minor.

B-26 | L21 | liu2026hexapod | "present the mechanical structure and a locomotion control
framework for a wheeled hexapod rescue device" | Src: title only; no abstract obtainable. |
UNVERIFIED (title-level paraphrase only).

B-26a | L21 | yamauchi2022 | "80 distributed sensors including IMUs, microphones, speakers and
vibration sensors ... survivor search in simulated rubble at the Fukushima Robot Test Field" |
Src: matches | ACCURATE.

B-26b | L21 | kim2023 | "low-cost sensing and control architecture ... thermal infrared sensor
array ... approaches them along a generated trajectory" | Src: matches | ACCURATE.

B-26c | L21 | raghavan2026 | "fine-tuned a YOLOv8 model ... (93.1% mean average precision) ...
Jetson Nano ... mobile robotic vehicle with cloud-based alerting" | Src: "mean average
precision of 93.1% ... low-cost NVIDIA Jetson Nano, which is integrated with a mobile robotic
vehicle ... cloud-based alert transmission" | ACCURATE.

B-26d | L21 | cantizani2022 | "Bluetooth Low Energy wearables can be detected by terrestrial
and aerial robots up to 15 m away" | Src: "the tested devices can be reliably detected up to 15
meters away when using transmission power values typical of a smartphone" | OVERSTATED (the
15 m figure is conditional on smartphone-level transmit power; wearables transmit less).
Minor -- add the condition.

B-26e | L23 | verano2022, pramono2024, kim2023, raghavan2026, sinha2026 (affordability
sentence) | Each paraphrase matches its abstract ("low-cost", "affordable", "inexpensive,
commonly available parts", "low-cost NVIDIA Jetson Nano", "MCU-based control, LoRa
communication, DC motors") | ACCURATE. The conclusion "none of the platforms in Table 2.1
states a numeric build cost" is CONFIRMED in full text only for khattab2025 (no figure for
SERR); for the other 11 rows it is NOT SUPPORTED BY ABSTRACT alone (absence claims need full
text). The table caption itself admits this.

### 2.3 (lines 27-29)

B-27 | L27 | iec60204 | "category 0 is stopping by immediate removal of power to the machine
actuators, an uncontrolled stop" | Src: standard not read; same wording in secondary sources
(vendor guides). | UNVERIFIED (wording); likely correct. The follow-on sentence "a category-0
stop that is independent of the Linux processes above it (C1)" -- see issue #3: the firmware
removes drive by setting PWM to zero and pulling a driver-enable GPIO low on a
non-safety-rated microcontroller. That is analogous to a category-0 stop in behaviour, but
calling it "a category-0 stop" invites the reviewer to apply the standard's requirements for
safety-related control (and, for emergency stop, the requirement that final power removal be
by electromechanical components, as quoted in secondary sources). | OVERSTATED.

B-28 | L27 | pont2001 | "design patterns for time-triggered embedded systems, in which tasks
are released by a periodic timer rather than by asynchronous events" | Src: book not fetched;
title confirms the topic. | UNVERIFIED (content). Separate concern: "The firmware of Section
3.5 follows this pattern" -- Section 3.5.1 describes a main-loop scheduler polling millis()
with blocking reads of 25 ms and about 20 ms (J about 50 ms). Pont's time-triggered
co-operative pattern assumes short, non-blocking tasks. "Follows this pattern" is
OVERSTATED; "is inspired by" or "uses a co-operative, time-based scheduler in the style of"
is safer.

B-29 | L27 | narasimhan2024 | "run-time monitor that restricts a networked robot to actions
that remain safe under delayed sensory observations, given the expected and maximum network
latency, ... F1/10th vehicle over congested Wi-Fi" | Src: "construct a shield, i.e., a run-time
monitor, that provides a list of safe actions for any delayed sensory observation, given the
expected and maximum network latency ... F1/10th ... congested WiFi links" | ACCURATE.

B-30 | L29 | candea2004 | "building systems to recover fast may be more productive than aiming
for systems that never fail ... multiple lines of defence" | Src: verbatim match | ACCURATE.

B-31 | L29 | schrick2025 | "microservices and a hierarchical finite-state machine that reduces
centralised logic and so increases concurrency, interruptibility and fail-safety ... delivery
robot operated in public space" | Src: matches | ACCURATE.

B-32 | L29 | ramesh2022 | "'robot vitals', lower-level metrics combined into a single 'robot
health' estimate, to detect performance degradation of remote mobile robots at run time so
that a human supervisor can intervene" | Src: matches | ACCURATE.

B-33 | L29 | koczi2025 | "most work concentrates on physical safety, including fault-tolerant
control, while software robustness, secure real-time communication and standardisation receive
less attention" | Src: "most work concentrates on physical safety, while cybersecurity,
standardization, and socio-ethical aspects are addressed less frequently" and, separately,
"studies increasingly address ... secure real-time communication". | OVERSTATED / partly
WRONG: the abstract names "cybersecurity" (not "software robustness" or "secure real-time
communication") as under-addressed, and describes secure real-time communication as an
increasing trend. Rephrase to the abstract's wording. Relevance also weak (humanoids in
everyday life).

B-34 | L29 | (synthesis) "These works concern platforms and budgets well above a single-board
rescue robot" | candea2004 is about Internet services; koczi2025 is a review; no source gives
budgets. | NOT SUPPORTED. Rephrase ("none of these targets a single-board rescue robot").

B-35 | L29 | "Among the rescue platforms of Table 2.1, none reports a hardware-level stop
guarantee or supervised process recovery." | Checked in full text for khattab2025: no
fail-safe, watchdog or emergency-stop mechanism for SERR found. Others: abstract only. |
NOT SUPPORTED BY ABSTRACT for 10 of 11 rows (absence claim). See issue #6.

### 2.4 (lines 33-39)

B-36 | L33 | chen2007 | "more than 150 papers ... performance decrements caused by limited
video bandwidth, time lags, low frame rates, lack of proprioception and two-dimensional views"
| Src: matches | ACCURATE.

B-37 | L33 | luz2023 | "even small amounts of latency can compromise robot safety, cause goal
overshoot and raise cognitive workload, and evaluate augmented interfaces for a robot operated
under 3 s of latency" | Src: matches | ACCURATE. Context omitted: planetary exploration in a
virtual environment. Add "for planetary rovers, in simulation" so the reader does not assume
SAR.

B-38 | L33 | bakzadeh2025 | "map cognitive load, situational awareness, trust and attentional
control to interface design principles and recommend layered feedback, multimodal
communication and adaptive interfaces" | Src: matches | ACCURATE.

B-39 | L33 | bakzadeh2026b | "interviews with ten mine-rescue personnel and SMEs ... need for
real-time situational data and customisable interfaces, with communication capabilities and
system reliability among the recurring themes" | Src: "ten mine rescue personnel and subject
matter experts ... functional aspects ... communication capabilities, system reliability ...
need for real-time situational data and customizable human-robot interfaces" | ACCURATE.

B-40 | L33 | ruan2025 | "semantic indicators, including signs of human activity, that
summarise how information-rich a scene is and so when it requires the expert operator's
attention, tested on a Jackal robot in a mock-up disaster environment" | Src: matches |
ACCURATE.

B-41 | L35 | akgun2023 | "across three online studies with 112, 223 and 151 participants,
LED-based affective expressions on an appearance-constrained field robot improved the
situational awareness of participants acting as rescue workers" | Src (abstract): three
studies; LEDs used in the third; (FT, arXiv) "participants who saw a rescue robot with an
ability to express emotions had a better situational awareness". | ACCURATE in substance;
wording attributes the LED result to all three studies. Minor: "In the third of three online
studies (N = 112, 223, 151), LED-based ...".

B-42 | L35 | chitikena2023 | "ethical and design issues ... response phase of SAR, with
emphasis on snake robots for confined spaces" | Src: matches | ACCURATE, but placed under
"Robot to rescue team", which it is not about. Move or drop.

B-43 | L37 | schneider2016 | "a SAR robot should be able to provide audio-visual communication
between the operator and trapped persons that allows basic diagnosis by an emergency
responder" | Src (FT, arXiv:1912.04693): "The robot should be able to provide audio-visual
communication between operator and trapped persons that allows for basic diagnosis by an
emergency responder." | ACCURATE (verbatim).

B-44 | L37 | srinivasan2012 | "on average, four to ten hours pass between the discovery of a
victim and extrication, during which a rescue robot remains with the victim ... socially
appropriate way to keep the victim calm and engaged" | Src: matches | ACCURATE. Note: Srinivasan
cites this figure to its own refs [2], [5]; a reviewer may ask for the primary source.

B-45 | L37 | bethel2007 | "robot operates within about three metres of a victim" | Src:
"places a robot approximately three meters or less from a victim" | ACCURATE.

B-46 | L37 | murphy2010 | "four-degree-of-freedom robot head whose face is a multimedia
touch-screen monitor ... social media ... intermediaries between trapped survivors and the
outside world, including doctors, rescuers and family members" | Src: matches | ACCURATE.

B-47 | L37 | murphy2011 | "50% less expensive, 78% lighter and up to 700% faster" | Src:
verbatim | ACCURATE.

B-48 | L37 | murphy2010; srinivasan2012 | "evaluated in an informal public study and in
simulated urban search and rescue scenarios" | Src: murphy2010 was a PBS "SciGirls" episode
with four middle-school girls, "neither statistically significant nor rigorously
controlled"; srinivasan2012: "two large scale simulated US&R scenario studies" of "an
affective robot" (not named as Survivor Buddy in the abstract). | ACCURATE in substance;
"informal public study" is generous. Table 2.1 attributes srinivasan2012 to Survivor Buddy --
UNVERIFIED from the abstract.

B-49 | L39 | raghavan2026, khattab2025, kim2023, cantizani2022 | "Victims are detected by
vision, thermal sensing, radio beacons or multimodal fusion" | Src: each matches |
ACCURATE.

B-50 | L39 | megalingam2022, verano2022, pramono2024, cafolla2026, jia2025 | "the platform
reports no victim-facing channel at all" | Abstract-only; full text not read for any of the
five. | NOT SUPPORTED BY ABSTRACT (absence claim). cafolla2026 tracks and identifies persons
("person face identification, 3D tracking, and following") -- not a channel, but check full
text for any speaker use.

B-51 | L39 | yamauchi2022 | "its abstract presents them as information-gathering sensors for
survivor search rather than as a conversation channel" | Src: "multiple small sensors ...
multiple information-gathering functions ... microphones, speakers" | ACCURATE about the
abstract, but the sentence openly argues from the abstract. Full text (Springer) not
reachable in this audit. A web-indexed table of the paper lists "19 speakers". What the
speakers are used for is UNVERIFIED. A reviewer will not accept "its abstract presents".

B-52 | L39 | khattab2025 | "The one recent system that provisions a speaker and microphone for
communication with victims reports that this capability is pending implementation in its
prototype" | Src (abstract): "provisions for communication via built-in speakers and
microphones, although these audio communication capabilities are pending implementation";
(FT) "the two-way audio communication feature ... is not yet implemented or functional in the
current prototype". | Pending status ACCURATE (confirmed in full text). "The one recent
system" is WRONG unless scoped: khattab2025's own related work cites Raspberry Pi/Arduino
rescue robots with speaker and microphone (its refs [39], [44] "Scouting Owl"), and
bakzadeh2026 lists fielded robots with two-way audio. Scope it to "the one platform in Table
2.1".

B-53 | L39 | (synthesis) "Two-way victim communication is therefore an established requirement
with a substantial HRI literature, but no recent low-cost platform in Table 2.1 demonstrates
it" | True only as scoped to Table 2.1, and the table's inclusion rule (peer-reviewed,
2022+) excludes the fielded robots that do have two-way voice (bakzadeh2026 FT). | OVERSTATED
by omission. See issue #1.

### 2.5 (lines 43-45)

B-54 | L43 | shi2025webrtc | "optimised Amazon KVS WebRTC framework with two video and two
data channels and report end-to-end latency below 50 ms, 34.2% lower than their baseline" |
Src: "two video channels and two data channels ... end-to-end latency under 50 ms, reducing
delay by 34.2% compared with baseline configurations" | ACCURATE.

B-55 | L43 | tiberkak2023 | "several operators control a mobile manipulator simultaneously,
with a priority system for parallel tasks and a chat channel between operators, validated on
an emulator of the robot over the Internet" | Src: matches | ACCURATE.

B-56 | L43 | shi2025webrtc, tiberkak2023 | "Both systems rely on Internet or cloud services for
signalling and connectivity" | shi: uses Amazon KVS WebRTC (a cloud-managed service), so a
cloud dependency is a fair inference but not stated in the abstract. tiberkak: "telerobotics
via the Internet" and validation "over the Internet"; signalling architecture not described in
the abstract; full text (Springer) unreachable. | NOT SUPPORTED BY ABSTRACT for "signalling".
Rephrase: "Both were deployed over the Internet or a cloud service".

B-57 | L43 | valin2012 | "Opus ... designed for interactive speech and audio and supports
frame sizes from 2.5 ms to 60 ms" | Src (RFC 6716, Sec. 2.1.4): "Opus can encode frames of 2.5,
5, 10, 20, 40, or 60 ms. It can also combine multiple frames into packets of up to 120 ms." |
ACCURATE. "instead of the usual 20 ms" is supported by the same section: "20 ms frames are a
good choice for most applications" -- cite that clause.

B-58 | L43 | bachhuber2016 | "glass-to-glass delay measurement system with 0.5 ms precision at
a 2 kHz sampling rate" | Src: "G2G measurement precision of 0.5 milliseconds with a sampling
rate of 2kHz" | ACCURATE. BUT "Section 5.2 reports the same glass-to-glass metric, measured
with a simpler clock-photograph procedure" is WRONG on two counts: (a) Section 5.2 reports no
data ("No valid streaming measurement exists; the experiment is entirely pending"); (b)
Section 5.2 calls the clock-photograph method "the established camera-to-display delay method
[@bachhuber2016]", which contradicts Section 2's (correct) statement that it is a simpler,
different procedure. Bachhuber's system is not a clock-photograph method. See issue #5.

B-59 | L45 | militano2023 | "cloud-to-edge-to-IoT continuum as a way to meet the low-delay
requirements of SAR operations, while noting that building such a continuum is still an open
challenge" | Src: matches | ACCURATE.

B-60 | L45 | raghavan2026, cafolla2026 | cloud alerting / "cloud-based connectivity for
streaming and data flow" | Src: matches | ACCURATE.

B-61 | L45 | manuel2022, nagatani2013 | infrastructure-free LoRa; wired link at Fukushima |
ACCURATE.

### 2.6 (lines 49-69) and Table 2.1 cells

B-62 | L49 | murphy2004 ... delmerico2019 | "are not single platforms" | ACCURATE.

B-63 | Table, Survivor Buddy row | "Version 2.0 50% cheaper than 1.0; no figure" ACCURATE;
"simulated US&R scenario studies [@srinivasan2012]" -- robot not named in abstract,
UNVERIFIED.

B-64 | Table, Pramono row | "Bluetooth (10 m lab), video up to 12 m" | ACCURATE.

B-65 | Table, SERR row | "Speaker and microphone provisioned; pending implementation" |
ACCURATE (FT). Link cell "Smartphone app, live video": FT also mentions an RF module; fine.

B-66 | Table, Universal Platform row | "Network or cable; cloud-based connectivity" | ACCURATE.

B-67 | Table, Jia row | "Onboard real-time object detection" | ACCURATE.

B-68 | Table, Wheeled hexapod row | every cell NR plus "[VERIFY]" | UNVERIFIED. No abstract
obtainable. A row whose content nobody has read should not be in a comparison table.

B-69 | Table, ERS row | "Detector evaluated on a 6,837-image dataset" | Src: "applies a dataset
of 6,837 images to fine-tune a pretrained YOLOv8" | OVERSTATED wording: the dataset was used
to fine-tune (with some split for evaluation). Say "fine-tuned and evaluated on".

B-70 | Table, all NR cells in C1, C2, C3, C4 columns | Absence claims based on abstracts
(caption admits it). | NOT SUPPORTED BY ABSTRACT, except SERR (FT checked: C3 pending, C1/C2
nothing found, C4 no figure).

B-71 | Table, This work row | "drive removed within 2042 ms of the last command in 30 of 30
logged trials" | Consistent with Section 5.1 (max 2042.0 ms, P1 send to PANIC receipt, mean
2022.5 ms). "USD 320, ESTIMATE" consistent with Table 5.19. "streaming metrics pending"
consistent with Section 5.2. | ACCURATE.

B-72 | L69 | daun2023, chen2007, nagatani2013, iec60204, candea2004, schneider2016, bethel2007,
murphy2010, srinivasan2012, khattab2025 | Each restates an already-checked claim. | ACCURATE,
except the inherited problems: "A category-0 stop on loss of commands is standard machinery
practice [@iec60204]" (IEC 60204-1 defines stop categories; it does not, as far as the
secondary sources show, mandate a stop on loss of command signals -- that is an inference;
UNVERIFIED), and the C3 clause (issue #1).

Extra-scrutiny summary (as requested): akgun2023 ACCURATE (minor wording); shi2025webrtc
ACCURATE except the "signalling" inference; bakzadeh2026 accurate but SELECTIVE (omits
two-way-audio finding: REJECT-RISK); bakzadeh2026b ACCURATE; bakzadeh2025 ACCURATE.
2025-2026 papers: kareem2026, sinha2026, cafolla2026, raghavan2026, khattab2025, ruan2025,
schrick2025, jia2025 ACCURATE; koczi2025 OVERSTATED/partly wrong; liu2026hexapod UNVERIFIED.

Cross-section finding (outside Section 2, found while checking the gap -> method link):
section3_methodology.md:367 cites liu2013 for "this dead-man (watchdog) pattern ... is a
standard fail-safe for teleoperated mobile robots". liu2013's available summary is about
terrain-traversal control and SLAM; nothing found supports a dead-man claim. UNVERIFIED and
likely a mis-citation. section3_methodology.md:17 also cites casper2003 and liu2013 for "the
layered style of prior teleoperated search-and-rescue systems" -- not supported by either
abstract.

=====================================================================
## PART C -- SUBSECTION REVIEW
=====================================================================

Opening (L3-5). Clear roadmap. L5 claims a Crossref/OpenAlex search protocol but gives no
counts (records found, screened, included); an IEEE Access reviewer may ask for them or for a
PRISMA-style sentence. L5 still contains "[AUTHORS: confirm ...]" -- must go before
submission.

2.1 Prior Reviews and Levels of Operator Involvement (428 words)
- Purpose clear; the closing sentence of L9 synthesises. L9 itself is a 286-word list
  ("X surveyed ... Y reviewed ...").
- Murphy line: casper2003 and murphy2004 are cited in 2.2, but Murphy's own HRI-in-rescue
  review (Murphy 2004, IEEE T-SMC-C, verified in D.5) is missing; it is the standard citation
  for rescue HRI and is the most likely "why not cited?" comment.
- Delmerico 2019: present and correct.
- Missing major review: Queralta et al. 2020 (IEEE Access, multi-robot SAR) -- verified in
  D.5.
- Levels of autonomy: four levels are defined WITHOUT a reference (issue #7). Add Beer et
  al. 2014 (verified in D.5) and use schneider2016's own statement that SAR robots in
  practice are tele-operated or semi-autonomous.
- avi2026review: absent (correct).
- The claim that safety of the control path and victim interaction are "not their organising
  concerns" must be softened (B-8), and the bakzadeh2026 sentence must mention two-way voice
  (B-6).

2.2 Field Deployments, Benchmarks and Recent Platforms (826 words -- longest body
subsection)
- Deployments: WTC (Sept 2001) and Fukushima (2011) correct. No earthquake deployment is
  cited although the paper's motivation is building collapse/earthquakes; Amatrice 2016
  (TRADR) is verified in D.5.
- "Link loss is an expected operating condition" rests on Fukushima only; daun2023 is
  inserted between evidence and conclusion (B-16). Add WTC communication evidence from
  murphy2004/casper2003 (needs their full text) or soften.
- Benchmarks: jacoff2012 used correctly; the budget claim is unsupported (B-18). Honest
  statement that Section 5 does not use standard apparatus is good practice.
- Platforms: two consecutive laundry-list paragraphs (L19, L21), one sentence per paper.
  Group them by what the reader needs (control path / link / victim interaction / cost).
- Comparison table: present (Table 2.1) but (a) columns C1/C2 are defined by this paper's own
  features, so every other row is "NR" -- reviewers call this a straw-man table; (b) no
  open-source column (requested in the brief); (c) liu2026hexapod row unverified; (d) all NR
  cells abstract-based; (e) fielded robots with two-way voice are excluded by the inclusion
  rule without saying so.

2.3 Fail-Safe and Fault-Tolerant Architectures (492 words)
- Candea used accurately. Pont: "follows this pattern" overstated (B-28).
- IEC 60204-1: stop-category definition fine (wording unverified); calling the firmware stop
  "a category-0 stop" is an overclaim (issue #3). The standard covers the electrical equipment
  of machines; a hobby-grade MCU GPIO disabling an H-bridge is not a safety-rated function.
  Write "behaves like a category-0 stop (immediate removal of drive, no ramp); it is not a
  safety-rated implementation" and keep compliance language out.
- Missing directly relevant prior work: Birk and Kenn 2003, "A Rescue Robot Control
  Architecture Ensuring Safe Semi-autonomous Operation" (verified in D.5) addresses a rescue
  robot's behaviour when the network breaks down -- the C1/C2 problem.
- Recent (2022-2026) fail-safe work on low-cost robots: my searches found no peer-reviewed
  item worth adding (only practitioner blogs and a 2026 arXiv humanoid study). Say so in the
  text rather than leaving it implicit.
- koczi2025 misparaphrased and weakly relevant (B-33).

2.4 HRI: Operator and Victim (645 words)
- Victim-side works (Bethel, Survivor Buddy, Srinivasan, Schneider) are described correctly.
- REJECT-RISK: the narrative that victim communication exists essentially only in the
  Survivor Buddy line and in one pending prototype is contradicted by bakzadeh2026 (already
  cited) and by fielded robots (bakzadeh2026 lists Inuktun Micro-VGTV with microphone and
  speaker, ANDROS Wolverine V2 and CUMT-V; whether the Inuktun units used at WTC carried audio
  was not verified here). C3 must be reframed as: two-way voice is
  common on fielded (expensive, tethered or mine-permissible) robots; what is not reported is
  two-way audio AND video on a low-cost single-board robot, with its CPU/power/bandwidth cost.
- Operator SA: discussed (Akgun, Ruan, Bakzadeh) but no foundational SA reference; Endsley
  1995 (verified in D.5) is the expected one.
- "Robot to rescue team" mixes Akgun (on topic) with Chitikena (ethics) -- move Chitikena.

2.5 Real-Time Media and Edge Computing (368 words)
- Latency numbers attributed correctly (Shi < 50 ms, -34.2%; Bachhuber 0.5 ms / 2 kHz).
- "Section 5.2 reports the same glass-to-glass metric" is wrong while 5.2 is pending, and
  Section 5.2 mis-attributes the clock-photograph method to Bachhuber (issue #5).
- "signalling" claim for Shi/Tiberkak not supported (B-56).
- Missing recent WebRTC-for-robotics: my search found no peer-reviewed 2023-2026 WebRTC
  mobile-robot latency study to recommend (practitioner measurements only). The current two
  WebRTC citations (surgery robot, emulator) are thin for a paper whose media path is WebRTC;
  a reviewer will notice. This remains an open search item (Part F.5).

2.6 Research Gap (929 words incl. table; gap paragraph 202 words)
- The gap is explicit and is correctly framed as a combination: "none of its parts is
  claimed as a first". No "novel", "unique", "to the best of our knowledge" or "no prior
  work" wording anywhere in Section 2.
- Absolute wording present, all scoped to Table 2.1: L23 "none of the platforms in Table 2.1
  states", L29 "none reports", L39 "no recent low-cost platform in Table 2.1 demonstrates it,
  and none reports", L69 "no recent rescue platform in Table 2.1 reports", "none reports the
  resource cost". L39 "The one recent system" is NOT scoped (B-52). Each scoped "none" is
  only as strong as the full-text check behind the NR cells, which has not been done.
- Mapping to contributions: the brief refers to "contributions C1-C3", but the paper's
  outline uses C1-C4 as CHALLENGES (Section 1.2) and Section 1.3 (contributions) is not yet
  written. Section 2 maps the gap 1:1 to challenges C1-C4, and Section 3 delivers each (C1:
  3.5 dead-man; C2: 3.7 P3 watchdog; C3: 3.9 WebRTC; C4: Table 5.19). The 1:1 mapping to
  contributions cannot be confirmed until Section 1.3 exists.
- Gap -> method link: supported by Section 3 (3.2 local network, 3.5.2 dead-man and bound,
  3.7 supervision, 3.9 two-way media, 3.9.5 60 ms Opus). Consistent.

Gap-disproof searches (5 run):
1. "low-cost search and rescue robot Raspberry Pi two-way audio video communication with
   trapped victim WebRTC" -- found no peer-reviewed paper with the combination. Closest:
   student/hobby projects with Raspberry Pi + speaker + microphone and NO fail-safe
   evaluation: Cornell "Scouting Owl" (2021,
   https://courses.ece.cornell.edu/ece5990/ECE5725_Spring2021_Projects/May_19/Scouting%20Owl/Th_lh479_pss242-1/index.html),
   GitHub "C.A.T.S." (https://github.com/adormeojoshua/cats-search-and-rescue-robot, two-way
   audio, MJPEG not WebRTC). Not citable as peer-reviewed, but they show that "Raspberry Pi
   rescue robot with two-way audio" is not new in itself -- reinforcing the combination
   framing.
2. "teleoperated rescue robot dead-man watchdog communication loss fail-safe ..." -- no
   peer-reviewed low-cost match; found Birk and Kenn 2003 (relevant prior work, D.5).
3. "Scouting Owl" (to check khattab2025's ref [44]) -- confirmed as the Cornell project above.
4. "rescue robot two-way voice communication with trapped survivor ... 2023-2025" -- only
   khattab2025 (pending); commercial Sarcos Guardian S is described in trade press as having
   two-way voice (not peer-reviewed); EU SMURF press item mentions microphones and speakers.
5. bakzadeh2026 full text (already cited) -- two-way voice is "a fundamental functionality of
   most of the reviewed MRRs".
Conclusion: no paper found that already combines a firmware dead-man with a bounded stop
time, supervised process recovery and two-way audio/video on a low-cost single-board rescue
robot. The combination gap survives; the "victim communication is rare" sub-claim does not.

=====================================================================
## PART D -- COVERAGE, RECENCY, BALANCE
=====================================================================

D.1 Year histogram (49 keys)

| Year | n |   | Year | n |
|---|---|---|---|---|
| 2001 | 1 |   | 2016 | 3 |
| 2003 | 1 |   | 2019 | 1 |
| 2004 | 2 |   | 2022 | 6 |
| 2007 | 2 |   | 2023 | 8 |
| 2010 | 1 |   | 2024 | 3 |
| 2011 | 1 |   | 2025 | 7 |
| 2012 | 4 |   | 2026 | 7 |
| 2013 | 2 |   |      |   |

2021-2026: 31 of 49 = 63.3%. Recency is adequate for IEEE Access. The 2014-2021 window is
almost empty (schneider2016, delmerico2019 only), which is where most of the classic SAR
reviews and deployments sit (e.g. Queralta 2020, Amatrice 2016) -- a gap a domain reviewer
will notice more than the 2001-2013 items.

D.2 Source types: journal articles 37; conference papers 9 (bachhuber2016 ICIP, bethel2007
HRI, daun2023 SSRR, jacoff2012 PerMIS, murphy2010 HRI, murphy2011 ICRA, schneider2016 ICCC,
srinivasan2012 SSRR, tong2024 IV); standards/RFC 2 (iec60204, valin2012); book 1 (pont2001);
web 0. Two of the conference items (murphy2010, srinivasan2012) are 2-page papers, and they
carry the Survivor Buddy validation claims.

D.3 Venue quality (quartiles NOT verified in this audit; journal names only):
- Top robotics/HRI venues: IEEE RA-L x2, J. Field Robotics x2, IEEE T-SMC x2, IEEE T-AFFC,
  Annu. Rev. Control Robot. Auton. Syst., Robotics and Autonomous Systems x2, IEEE RAM, IEEE
  Computer; conferences ICRA x1, HRI x2, SSRR x2.
- IEEE Access x5 (the target venue -- good).
- MDPI x7 (Sensors, Applied Sciences x2, Electronics, Machines, Robotics, Future Internet),
  Frontiers Robot. AI x3, Sci. Rep., Results in Engineering, Mech. Mach. Theory, Advanced
  Robotics, ROBOMECH J., JIRS, Industrial Robot, Int. J. Intell. Robot. Appl.
- Questionable/low-tier: IJACSA (verano2022), JNTE (pramono2024) -- see A.3.
- No RSS or IROS paper is cited.

D.4 Clustering
- Murphy group: 6 keys (casper2003, murphy2004, bethel2007, murphy2010, murphy2011,
  srinivasan2012). Justified -- it is the main victim-HRI line -- but Murphy's best-known
  rescue-HRI review (2004 T-SMC-C) is the one missing.
- Roghanchi/Bakzadeh group (Univ. of Alabama/NMT mine rescue): 3 keys (bakzadeh2025,
  bakzadeh2026, bakzadeh2026b), all 2025-2026. Borderline clustering; acceptable because they
  serve three different purposes, but use bakzadeh2026 for its two-way-voice finding or the
  cluster looks decorative.
- Chiou/Stolkin (Birmingham): 2 keys (ramesh2022, ruan2025). Fine.
- Self-citation: none identifiable (author list of this paper not in the files read).

D.5 Recommended additions (max 8; each DOI resolved via Crossref, abstract via OpenAlex).
None of the 2023-2026 targeted searches produced a peer-reviewed item I could verify as
clearly better than what is already cited; I did not pad the list with unverified recent
papers.

| # | Reference (verified) | DOI / URL | Evidence of relevance (abstract snippet) | Why | Subsection |
|---|---|---|---|---|---|
| 1 | Murphy, R. R., "Human-Robot Interaction in Rescue Robotics", IEEE T-SMC Part C, 34(2):138-153, 2004 | https://doi.org/10.1109/TSMCC.2004.826267 | "provides a short tutorial on how robots are currently used in urban search and rescue (USAR) and discusses the HRI issues encountered over the past eight years" | Canonical rescue-HRI review; its absence is the likeliest reviewer comment | 2.1 / 2.4 |
| 2 | Queralta, J. P., et al., "Collaborative Multi-Robot Search and Rescue: Planning, Coordination, Perception, and Active Vision", IEEE Access, 8:191617-191643, 2020 | https://doi.org/10.1109/ACCESS.2020.3030190 | "SAR operations can take significant advantage from supporting autonomous or teleoperated robots ... establishing communication networks, or searching for victims" | Major, highly cited review in the target journal; fills the 2014-2021 hole | 2.1 |
| 3 | Beer, J. M., Fisk, A. D., Rogers, W. A., "Toward a Framework for Levels of Robot Autonomy in Human-Robot Interaction", J. Human-Robot Interaction, 3(2):74, 2014 | https://doi.org/10.5898/JHRI.3.2.Beer | "Levels of robot autonomy (LORA), ranging from teleoperation to fully autonomous systems, influence the way in which humans and robots may interact" | Standard reference for the four-level taxonomy that is currently uncited | 2.1 |
| 4 | Birk, A., Kenn, H., "A Rescue Robot Control Architecture Ensuring Safe Semi-autonomous Operation", RoboCup 2002, LNCS 2752, pp. 254-262, 2003 | https://doi.org/10.1007/978-3-540-45135-8_19 | No abstract in OpenAlex; text indexed by search engine (ResearchGate copy): "the robots need quite some autonomous functionality ensuring FSG and QoS as the network performance is unknown and can even break completely down" (snippet seen via search, full text not read) | Direct prior work on safe rescue-robot behaviour when the link fails (C1/C2). Read the full text before citing | 2.3 |
| 5 | Kruijff-Korbayova, I., et al., "Deployment of ground and aerial robots in earthquake-struck Amatrice in Italy (brief report)", IEEE SSRR 2016, pp. 278-279 | https://doi.org/10.1109/SSRR.2016.7784314 | "TRADR project deployment of ground and aerial robots in Amatrice, Italy, after the major earthquake in August 2016" | Earthquake field deployment, currently missing; matches the paper's building-collapse motivation | 2.2 |
| 6 | Endsley, M. R., "Toward a Theory of Situation Awareness in Dynamic Systems", Human Factors, 37(1):32-64, 1995 | https://doi.org/10.1518/001872095779049543 | "presents a theoretical model of situation awareness based on its role in dynamic human decision making" | SA is used in 2.4 (Akgun, Ruan, Bakzadeh) without its foundational definition | 2.4 |

(No item 7-8: the WebRTC-for-robotics, Raspberry Pi + MCU architecture, and recent fail-safe
searches returned no peer-reviewed paper I could verify; see F.5.)

=====================================================================
## PART E -- WRITING, STYLE, FORMAT
=====================================================================

E.1 ASCII: `grep -nP '[^\x00-\x7F]' section2_related_work.md` returned no lines. PASS.

E.2 IEEE style
- Citations: pandoc [@key] form, numeric at build. OK.
- Person: third person throughout ("This paper uses"). OK.
- Tense: mixed past ("surveyed", "reviewed", "built") and present ("observe", "identify",
  "argue") for describing literature. IEEE Access accepts either; pick one (present for what
  a paper states, past for what authors did) and apply consistently.
- Spelling: British (organise, synthesised, characterised, defence). Consistent within
  Section 2 and with Section 3. OK, but check the rest of the paper.
- Terminology consistent: "teleoperated", "fail-safe", "dead-man", "two-way". "US&R" (Table
  2.1, L55) vs "urban search and rescue" (L15, L37) vs "USAR" (none) -- pick one acronym.
- Acronyms not expanded at first use in Section 2 (they may be defined in Section 1, which is
  not yet written -- check after drafting): DoF (L19), ROS (L19), CNN-LSTM, USGS-PAGER (L19),
  LoRa, LPWAN (L19), WebRTC (L3/L43), IoT (L45), PWM (L27), CPU (L39), IR (Table), WRS
  (Table, though "World Robot Summit" appears in L19), P3 (Table, defined only in Section 3).
- Placeholders that must not reach submission: L5 "[AUTHORS: confirm ...]", L51 "[VERIFY
  AGAINST FULL TEXT ...]", L65 "[VERIFY]".

E.3 Paragraph quality
- Paragraphs over 200 words: L9 (286), L15 (207), L19 (252), L27 (240), L29 (252), L37 (225),
  L43 (234), L69 (202).
- Laundry-list paragraphs: L9 (reviews), L19 and L21 (platforms), L29 (first four sentences).
- Repeated points: teleoperation-is-default (L11 and L69, same two citations); link loss
  (L15, L45, L69); cloud dependence of raghavan2026/cafolla2026 (L19/L21, L45, Table);
  khattab2025 pending audio (L39, L69, Table); affordability-without-figure (L23, L69,
  Table).

E.4 Length
| Part | Words |
|---|---|
| Opening (L1-5) | 202 |
| 2.1 | 428 |
| 2.2 | 826 |
| 2.3 | 492 |
| 2.4 | 645 |
| 2.5 | 368 |
| 2.6 (incl. table) | 929 |
| Total | approx. 3,890 |
IEEE Access related-work sections are typically 1-2 journal pages (roughly 1,000-2,000
words). Section 2 is about twice that. Target: cut to approx. 2,000-2,300 words plus the
table, mainly by merging L19/L21 into the table, removing repeats (E.3) and shortening L9.

E.5 Grammar / clarity / hedging
- L15 "the deployed robots were fitted" -> only one robot was delivered (B-14).
- L21 "removes the sensor occlusion" -> "addresses" (B-25).
- L23 "Affordability is claimed more often than it is quantified" -- good, keep.
- L27 "The dead-man principle is therefore not new" -- "therefore" does not follow from the
  IEC definition; use "The dead-man principle is not new".
- L39 "its abstract presents them" -- never argue from an abstract in the paper text.
- L49 "Survivor Buddy is included although it predates 2022, because it is the closest prior
  work on C3" -- after the C3 reframing (issue #1) this justification must change.
- No informal phrases found.

E.6 Figures/tables
- Table 2.1: numbered, captioned, referenced in text (L3, L23, L29, L39, L49, L69). OK.
- Numbering scheme inconsistent across the paper: "Table 2.1" here, "Table 1 ... Table 14"
  in Section 3, "Table 5.x" in Section 5. IEEE uses TABLE I, II, ... -- unify before
  submission.
- Table 2.1 has 9 columns; it will not fit an IEEE two-column page in portrait without a
  full-width float and small font. Consider dropping "Ref." (merge into Platform) and
  shortening cells.
- No Mermaid figures in Section 2 (back-edge rule not applicable).

=====================================================================
## PART F -- FINAL VERDICT
=====================================================================

F.1 Severity-ranked issues

| # | Severity | Line | Issue | Evidence URL | Fix |
|---|---|---|---|---|---|
| 1 | REJECT-RISK | 9, 37-39, 49, 69 | C3 narrative implies victim two-way communication exists only in Survivor Buddy and one pending prototype; our own cited review states two-way voice is a fundamental feature of most mine rescue robots (ANDROS Wolverine V2, CUMT-V, Inuktun VGTV) | https://doi.org/10.3389/frobt.2026.1857704 (FT: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13487453/fullTextXML) | State that two-way voice is common on fielded (costly, tethered/permissible) rescue robots [bakzadeh2026]; narrow C3 to two-way audio+video on a low-cost single-board robot with measured resource cost; update Table 2.1 inclusion note |
| 2 | REJECT-RISK | 51-66 | Comparison table rests on abstracts: all NR cells unverified, one row (liu2026hexapod) entirely unread, caption carries a [VERIFY] placeholder | https://doi.org/10.1016/j.mechmachtheory.2026.106472 | Read full text of all 11 comparison papers and fill cells, or drop rows that cannot be read; delete placeholders |
| 3 | MAJOR | 27, 69 | Firmware stop called "a category-0 stop"; IEC 60204-1 classifies stops but a non-safety-rated MCU GPIO path is not a compliant category-0 implementation; edition superseded by 2016+AMD1:2021; normative text never read | https://webstore.iec.ch/en/publication/26037 | "behaves like a stop category 0 (immediate removal of drive, no ramp), without a safety-rated implementation"; cite the consolidated edition; read clause 9.2.2 |
| 4 | MAJOR | 21, 29, 39, 69 | Absence claims ("none reports", "no victim-facing channel") made from abstracts | (per-paper DOIs, Part A) | Full-text check, or rephrase as "does not report in [the paper]" only after reading |
| 5 | MAJOR | 43 (and section5 L215) | "Section 5.2 reports the same glass-to-glass metric" while 5.2 is entirely pending; Section 5.2 attributes the clock-photograph method to Bachhuber, contradicting Section 2 | https://doi.org/10.1109/ICIP.2016.7532735 | "Section 5.2 will report..." until data exist; in 5.2 cite Bachhuber as the reference metric, not as the method used |
| 6 | MAJOR | 29 | Missing direct prior work on safe rescue-robot behaviour under network breakdown (Birk and Kenn 2003) | https://doi.org/10.1007/978-3-540-45135-8_19 | Read and cite in 2.3 |
| 7 | MAJOR | 11 | Four levels of operator involvement defined with no reference; "Shared-Collaborative Control" non-standard | https://doi.org/10.5898/JHRI.3.2.Beer | Cite Beer et al. 2014 and schneider2016 (FT supports teleop/semi-autonomous in practice) |
| 8 | MAJOR | whole section | Length approx. 3,890 words, about twice typical; 8 paragraphs over 200 words; laundry lists; repeats | - | Cut to approx. 2,000-2,300 words (E.3, E.4) |
| 9 | MAJOR | 15 | "Link loss ... therefore an expected operating condition" generalised from one site; daun2023 sentence interposed | https://doi.org/10.1002/rob.21439 | Move daun2023; add WTC comms evidence (after reading murphy2004/casper2003 full text) or soften to "can be" |
| 10 | MAJOR | 9, 33 | Missing canonical references: Murphy 2004 HRI in rescue robotics; Queralta 2020; Endsley 1995; no earthquake deployment (Amatrice 2016) | DOIs in D.5 | Add (D.5 #1, #2, #5, #6) |
| 11 | MAJOR | 43 | Only two WebRTC citations (surgery robot; emulator) for a WebRTC-based paper; "signalling" claim unsupported | https://doi.org/10.1007/s41315-023-00281-3 | Rephrase B-56; further search for WebRTC robotics evaluations |
| 12 | MAJOR | sec3 L367, L17 | (Cross-section) liu2013 cited for "dead-man is a standard fail-safe" and for "layered style"; not supported by available summary | https://doi.org/10.1007/s10846-013-9822-x | Replace with a source that states it, or remove the claim |
| 13 | MINOR | 39 | "The one recent system" unscoped; student Raspberry Pi robots with speaker+mic exist (cited by khattab2025) | https://doi.org/10.1038/s41598-025-16003-7 | "the one platform in Table 2.1" |
| 14 | MINOR | 29 | koczi2025 paraphrase does not match abstract; weak relevance | https://doi.org/10.3390/electronics14234734 | Use abstract wording or drop |
| 15 | MINOR | 27 | "follows this pattern" (Pont) despite blocking reads; content of book unverified | ISBN 0201331381 | "uses a co-operative, time-based scheduler in the style of Pont" |
| 16 | MINOR | 9 | "not their organising concerns" vs kareem2026 ("Safe SAR ...", HRI layer) | https://doi.org/10.1109/ACCESS.2026.3660002 | Soften |
| 17 | MINOR | 17, 29 | Unsupported budget claims ("budgets far above") | - | Drop or cite |
| 18 | MINOR | 19, 21, 35 | pramono lab vs field; jia "removes"; cantizani 15 m condition; akgun LED attributed to all studies; ERS "evaluated on" | DOIs in Part A | Wording fixes (B-21, B-25, B-26d, B-41, B-69) |
| 19 | MINOR | 35 | chitikena2023 under "Robot to rescue team" | https://doi.org/10.3390/app13031800 | Move/drop |
| 20 | MINOR | 33 | luz2023 context (planetary, virtual) omitted | https://doi.org/10.1109/access.2023.3240307 | Add context |
| 21 | MINOR | 37 | 4-10 h figure is secondary (srinivasan2012 cites its refs [2],[5]); 2-page papers carry Survivor Buddy validation | https://doi.org/10.1109/ssrr.2012.6523916 | Cite primary source if available |
| 22 | MINOR | bib | kareem2026, raghavan2026 name splits; verano2022 no paper number; IJACSA/JNTE venue quality | Part A | Bib fixes; consider whether low-tier venues are needed |
| 23 | MINOR | 5, 51, 65 | Placeholders [AUTHORS: confirm], [VERIFY ...] | - | Resolve and delete |
| 24 | MINOR | various | Acronyms undefined (DoF, ROS, LoRa, LPWAN, WebRTC, IoT, PWM, CPU, P3); US&R vs USAR; tense mix; table numbering scheme | - | Style pass |

F.2 Readiness score: 5 / 10

Reviewer-style justification: The section is unusually careful for a systems paper -- every
citation resolves, metadata are clean, the large majority of paraphrases match their sources
(I found no fabricated paper, number or quote), and the gap is explicitly framed as a
combination rather than a first. That is a strong base. It is held back by one substantive
problem and one evidential one. Substantively, the C3 narrative understates prior art: the
authors' own cited mine-rescue review states that two-way voice is a fundamental feature of
most fielded rescue robots, so the claim that victim communication is essentially absent
outside one academic project would be rejected by any reviewer from the rescue-robotics
community. Evidentially, the comparison table and every "none reports" statement rest on
abstracts, which the manuscript itself admits in a [VERIFY] note. Add to this a stop-category
claim that reads as a safety-standard compliance claim, a section about twice the usual
length, and several missing canonical references (Murphy 2004, levels of autonomy, an
earthquake deployment), and the section would draw a major-revision request. With issues 1-8
fixed it would be at 7-8.

F.3 Simulated reviewer comments

Reviewer 1 (domain expert, rescue robotics):
"1. The authors present two-way communication with trapped victims as nearly unexplored,
citing only Survivor Buddy and a prototype whose audio is not implemented. This is not
correct. Two-way audio is common on fielded rescue robots -- the mine-rescue review the
authors cite [bakzadeh2026] lists the Inuktun Micro-VGTV (microphone and speaker) and states that two-way voice is a fundamental functionality of most
mine rescue robots. Please reposition the contribution: what is new here is not two-way
communication but its realisation, with video, on a low-cost single-board platform together
with a bounded stop.
2. The firmware dead-man is described as 'a category-0 stop' per IEC 60204-1. An Arduino GPIO
disabling a motor driver is not a safety-rated stop function. Please avoid language that
implies compliance, or provide the safety analysis.
3. The levels of operator involvement need a reference (e.g. Beer et al.), and Murphy's 2004
review of HRI in rescue robotics should be discussed. No earthquake deployment is cited,
although the motivation is building collapse.
4. Table 2.1 marks almost every competing platform 'NR' in columns defined by the authors' own
features. Please add columns that let other platforms show their strengths (e.g. mobility,
sensing, open-source availability) and confirm every NR from the full papers.
5. Related work is too long; the platform paragraphs read as a list."

Reviewer 2 (methodology and integrity):
"1. The table caption states that entries are 'based on abstracts' and must be verified
against full text. A comparison table in a journal article must be based on the full papers.
The same applies to the statements 'none reports ...' in Sections 2.3, 2.4 and 2.6, and to
the active-scope-camera sentence that explicitly argues from an abstract.
2. One row (wheeled hexapod) has no content beyond the title and a [VERIFY] mark. Remove it or
complete it.
3. Section 2.5 says Section 5.2 reports glass-to-glass delay; Section 5.2 contains no data.
Section 5.2 also cites Bachhuber and Steinbach as the source of a clock-photograph method,
which is not what that paper describes.
4. The literature-search paragraph claims a Crossref/OpenAlex protocol but gives no numbers;
please report records identified, screened and included, or describe the search as
non-systematic.
5. Several paraphrases are stronger than their sources (Koczi and Sarosi; Cantizani-Estepa et
al. 15 m condition; Pramono et al. lab vs field). Two venues (IJACSA, JNTE) are of uncertain
standing; consider whether they are needed."

F.4 Top 5 fixes, in order of impact on acceptance
1. Reframe C3 (issue #1): acknowledge two-way voice on fielded robots via bakzadeh2026;
   narrow the claim to low-cost single-board two-way audio+video with measured resource cost;
   fix "The one recent system"; revise the Survivor Buddy inclusion sentence and L69.
2. Full-text verification of Table 2.1 and every absence claim (issues #2, #4); drop
   liu2026hexapod unless read; add an open-source column; remove [VERIFY] placeholders.
3. Rewrite the IEC 60204-1 sentences as behavioural analogy, not compliance; cite the
   consolidated 2016+AMD1:2021 edition (issue #3). Fix the liu2013 dead-man citation in
   Section 3 (issue #12).
4. Add the verified missing references: Beer 2014 (levels), Murphy 2004 (rescue HRI), Birk
   and Kenn 2003 (safe operation under link loss), Queralta 2020, Kruijff-Korbayova 2016,
   Endsley 1995 (issues #6, #7, #10).
5. Cut Section 2 to about 2,000-2,300 words: fold L19/L21 into the table, remove repeats,
   split/shorten the 8 long paragraphs; fix the 5.2 cross-reference (issues #5, #8).

F.5 Could NOT verify, and why
- liu2026hexapod content: no abstract in OpenAlex/Crossref, not in Semantic Scholar,
  ScienceDirect returned HTTP 403.
- liu2013 content: abstract elided by publisher in OpenAlex and Semantic Scholar; Springer
  behind a cookie wall. Only title and Semantic Scholar TLDR seen.
- yamauchi2022 full text (use of the 19 speakers): Springer cookie wall; abstract only.
- tiberkak2023 full text (signalling architecture): Springer cookie wall.
- Full text of megalingam2022, verano2022, pramono2024, manuel2022, cafolla2026, kim2023,
  jia2025, raghavan2026 (needed for NR cells): not attempted for all; several are paywalled
  (Elsevier, Taylor & Francis). Only khattab2025 was checked in full.
- iec60204 normative text (clause 9.2.2 wording; any requirement on loss of control
  signals): standard is paywalled; only the IEC webstore record and secondary sources seen.
- pont2001 content and publisher: OpenLibrary confirms title/author/year only.
- srinivasan2012: whether the "affective robot" is Survivor Buddy (abstract does not name it).
- schneider2016: quote verified in the arXiv version; the IEEE ICCC version was not compared.
- Venue standing of IJACSA and JNTE (Scopus status/quartile): not confirmed online.
- Journal quartiles for D.3: not checked.
- Birk and Kenn 2003 (suggested addition): DOI and metadata verified via Crossref; text only
  seen as a search-engine snippet -- read before citing.
- Recent (2023-2026) peer-reviewed WebRTC-for-mobile-robot latency studies and low-cost
  fail-safe teleoperation papers: searches returned none I could verify; absence of evidence,
  not evidence of absence.
- Per-title "<title> retraction" web searches were not run; retraction status relies on
  Crossref update metadata and OpenAlex is_retracted for the 47 DOIs (both clean).

F.6 All 49 citation keys checked: YES
(49/49 present in references.bib and citation.md; 47/47 DOIs resolved against Crossref with
abstracts from OpenAlex/Crossref for 45; iec60204 checked on the IEC webstore; pont2001 checked
via OpenLibrary; content of liu2013 and liu2026hexapod could not be read -- see F.5.)

Sources used (beyond the per-key DOIs above):
- https://webstore.iec.ch/en/publication/26037
- https://www.rfc-editor.org/rfc/rfc6716.txt
- https://arxiv.org/abs/1912.04693 and https://arxiv.org/pdf/1912.04693
- https://arxiv.org/pdf/2208.09580
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12660968/fullTextXML (khattab2025)
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13487453/fullTextXML (bakzadeh2026)
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12932144/fullTextXML (bakzadeh2026b)
- http://jnte.ft.unand.ac.id/index.php/jnte/article/view/1191
- https://openlibrary.org/search.json?isbn=0201331381
- https://courses.ece.cornell.edu/ece5990/ECE5725_Spring2021_Projects/May_19/Scouting%20Owl/Th_lh479_pss242-1/index.html
- https://github.com/adormeojoshua/cats-search-and-rescue-robot
- https://thesai.org/Publications/GIDP
