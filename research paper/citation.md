# Citation Ledger

Working notebook for every citation the paper needs. This file is the
human-readable companion to `references.bib`.

- `references.bib` is the machine-readable source that LaTeX compiles.
- This ledger records WHY each reference exists, WHERE it is cited, and
  its verification status.

## Rules (follow on every new citation)

1. When a new citation is needed, do BOTH in the same step:
   a. Add a VERIFIED entry to `references.bib`.
   b. Append a matching row to the table below.
2. A source that cannot be verified against an authoritative record
   (Crossref DOI, publisher page, RFC editor, or official datasheet) is
   logged here as `UNVERIFIED` and is NOT added to `references.bib`.
3. ASCII characters only. No Unicode symbols.
4. The BibKey in this table must match the key in `references.bib` exactly.

Status values: `VERIFIED` = in references.bib, safe to cite.
`UNVERIFIED` = lead only, do not cite yet.

## Master citation table

| BibKey | Section | Claim it supports | Source | DOI / Identifier | Status |
|--------|---------|-------------------|--------|------------------|--------|
| casper2003 | 2.2 | Field HRI findings from robot-assisted USAR at the World Trade Center | Casper and Murphy, IEEE Trans. SMC-B, 2003 | 10.1109/TSMCB.2003.811794 | VERIFIED |
| liu2013 | 2.1 | Survey of robotic urban search and rescue from the control perspective | Liu and Nejat, J. Intell. Robot. Syst., 2013 | 10.1007/s10846-013-9822-x | VERIFIED |
| pont2001 | 2.3, 3.5 | Time-triggered scheduling pattern for reliable embedded control | Pont, Addison-Wesley, 2001 | ISBN 0201331381 | VERIFIED |
| valin2012 | 2.5, 3.9.5 | Definition of the Opus low-latency audio codec | Valin, Vos, Terriberry, IETF RFC 6716, 2012 | 10.17487/RFC6716 | VERIFIED |
| shi2025webrtc | 2.5, 3.9 | WebRTC (Amazon KVS) remote dental-surgery robot; end-to-end latency below 50 ms | Shi et al., IEEE Access, 2025 | 10.1109/ACCESS.2025.3620994 | VERIFIED |
| ublox_neo6 | 3.10 | NEO-6 GPS module characteristics for localisation | u-blox AG Data Sheet, 2011 | GPS.G6-HW-09005 | VERIFIED |
| kareem2026 | 2.1 | Prior SAR review organised by a five-layer system architecture, 2016-2024 corpus | Kareem et al., IEEE Access, 2026 | 10.1109/ACCESS.2026.3660002 | VERIFIED |
| sinha2026 | 2.1 | Prior UGV reconnaissance review organised by research-method type | Sinha, Lee, Singh, Sensors, 2026 | 10.3390/s26051659 | VERIFIED |
| tong2024 | 2.1 | Earlier UAV/UGV software review of SAR in harsh environments | Tong et al., IEEE IV, 2024 | 10.1109/IV55156.2024.10588685 | VERIFIED |
| bakzadeh2026 | 2.1, 2.2 | Mine-rescue platform review; field predominantly teleoperated; autonomy excluded from scope | Bakzadeh et al., Front. Robot. AI, 2026 | 10.3389/frobt.2026.1857704 | VERIFIED (authors as initials, per Crossref) |
| daun2023 | 2.2 | Requirements for autonomy and assistance functions in ground rescue robots | Daun and von Stryk, IEEE SSRR, 2023 | 10.1109/SSRR59696.2023.10499930 | VERIFIED |
| megalingam2022 | 2.2 | Low-cost SAR robot platform evaluated at WRS 2020 | Megalingam et al., Advanced Robotics, 2022 | 10.1080/01691864.2022.2117575 | VERIFIED |
| verano2022 | 2.2 | Low-cost teleoperated explorer robot | Verano et al., IJACSA, 2022 | 10.14569/IJACSA.2022.01307104 | VERIFIED |
| cafolla2026 | 2.2 | Teleoperated universal SAR add-on platform (drone and quadruped) | Cafolla et al., Robot. Auton. Syst., 2026 | 10.1016/j.robot.2025.105237 | VERIFIED |
| jia2025 | 2.2 | Teleoperated terrestrial-aerial caged UAV; navigation autonomy deferred | Jia et al., Applied Sciences, 2025 | 10.3390/app15168792 | VERIFIED |
| liu2026hexapod | 2.2 | Teleoperated heavy-payload wheeled-hexapod rescue platform; navigation autonomy deferred | Liu et al., Mech. Mach. Theory, 2026 | 10.1016/j.mechmachtheory.2026.106472 | VERIFIED |
| raghavan2026 | 2.2 | Teleoperated UGV with YOLOv8 occluded-victim detection | Raghavan et al., Results in Engineering, 2026 | 10.1016/j.rineng.2026.110608 | VERIFIED |
| khattab2025 | 2.2, 2.4, 2.6 | Teleoperated earthquake rescue robot; multimodal detection validated in MATLAB simulation; victim speaker/microphone pending implementation (abstract) | Khattab et al., Scientific Reports, 2025 | 10.1038/s41598-025-16003-7 | VERIFIED |
| schrick2025 | 2.3 | Microservice control architecture for safety-critical mobile robots | Schrick et al., Robot. Auton. Syst., 2025 | 10.1016/j.robot.2024.104795 | VERIFIED |
| koczi2025 | 2.3 | Safety-engineering practice for robots operating near people | Koczi and Sarosi, Electronics, 2025 | 10.3390/electronics14234734 | VERIFIED |
| chen2007 | 2.4, 5 | Operator performance and interface design in teleoperation | Chen, Haas, Barnes, IEEE Trans. SMC-C, 2007 | 10.1109/TSMCC.2007.905819 | VERIFIED |
| bakzadeh2025 | 2.4 | Interface-design guidelines for mining emergency robots | Bakzadeh et al., Robotics, 2025 | 10.3390/robotics14110148 | VERIFIED |
| ruan2025 | 2.4 | Semantics-based situational awareness for operators of deployed robots | Ruan et al., Front. Robot. AI, 2025 | 10.3389/frobt.2025.1694123 | VERIFIED |
| akgun2023 | 2.4 | Affect (LED expressions) as a robot-to-rescue-worker communication channel; three online studies, N = 112, 223, 151 | Akgun et al., IEEE Trans. Affect. Comput., 2023 | 10.1109/TAFFC.2022.3221922 | VERIFIED |
| chitikena2023 | 2.4 | Ethical and design framework for SAR robots in the response phase | Chitikena, Sanfilippo, Ma, Applied Sciences, 2023 | 10.3390/app13031800 | VERIFIED |
| bachhuber2016 | 2.5, 5.2 | Glass-to-glass video delay measurement method | Bachhuber and Steinbach, IEEE ICIP, 2016 | 10.1109/ICIP.2016.7532735 | VERIFIED |

## Pending / needed citations

(Claims in the draft that still need a source. Move a row up to the
master table once its entry is verified and added to references.bib.)

| Section | Claim needing a source | Candidate source | Status |
|---------|------------------------|------------------|--------|
| 3.2 | "an 802.11n cell on the 2.4 GHz band" - the WLAN standard the link runs on | IEEE Std 802.11-2020 (or 802.11n-2009 amendment) | UNVERIFIED |
| 3.2 | "Browsers allow microphone and camera capture only in a secure context" | W3C Secure Contexts; W3C Media Capture and Streams (getUserMedia) | UNVERIFIED |
| 3.8, 3.9.2 | "WebRTC's own SRTP/DTLS"; "DTLS handshake, then SRTP media" | RFC 5764 (DTLS-SRTP); RFC 3711 (SRTP) | UNVERIFIED |
| 3.9 | WebRTC as the two-way media platform (the standard itself) | W3C WebRTC 1.0 Recommendation; RFC 8825 (WebRTC overview) | UNVERIFIED |
| 3.9.2 | "no trickle ICE", "host candidates", "ICE connectivity checks" | RFC 8445 (ICE) | UNVERIFIED |
| 3.9.2 | "SDP offer ... the answer" (offer/answer model) | RFC 8866 (SDP); RFC 3264 (offer/answer) | UNVERIFIED |
| 3.9.2 | "a deployment that would need STUN"; "issue a TURN server" | RFC 8489 (STUN); RFC 8656 (TURN) | UNVERIFIED |
| 3.9.3 | "reliable, ordered data channel ... over ... DTLS" (SCTP data channel) | RFC 8831 (WebRTC data channels); RFC 8832 (DCEP) | UNVERIFIED |
| 3.9.1, 3.9 (Fig 17), Table 12 | Video "encoded ... as VP8 or H.264" | RFC 6386 (VP8); ITU-T Rec. H.264 | UNVERIFIED |
| 3.8 | "permissive CORS" / cross-origin request handling | WHATWG Fetch Standard (CORS) | UNVERIFIED |
| 3.10 | "equirectangular approximation ... against the haversine formula" | Standard geodesy reference (e.g. Sinnott 1984, haversine) | UNVERIFIED |
| 2.6, Table 2.1 | Every "NR" cell in Table 2.1 (based on abstracts and the review summary, not full text); liu2026hexapod validation cell | Full text of each tabulated paper | UNVERIFIED |

## Software / tools (footnote or cite depending on venue policy)

These are implementation dependencies, not claims. IEEE often lists them as
footnoted URLs rather than numbered references; decide per journal policy.

| Section | Tool | Note |
|---------|------|------|
| 3.4, 3.9.1 | aiortc | Python WebRTC/ORTC implementation |
| 3.4, 3.9.1 | PyAV / FFmpeg | capture, decode, encode |
| 3.4 | FastAPI, uvicorn, aiohttp | P1/P2/P3 web stack |
| 3.4 | React 19, Vite, Tailwind CSS | dashboard frontend |
| 3.4, 3.10 | Leaflet, PMTiles | offline map rendering |
| 3.3, Table 3 | ServoTimer2Plus (Arduino) | servo PWM on Timer2 |
