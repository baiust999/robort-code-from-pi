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
| bakzadeh2026 | 2.1, 2.4, 2.6 | Mine-rescue platform review over three decades; design guidelines not established; two-way voice a fundamental functionality of most reviewed MRRs (full text PMC13487453) | Bakzadeh et al., Front. Robot. AI, 2026 | 10.3389/frobt.2026.1857704 | VERIFIED (authors as initials, per Crossref) |
| daun2023 | 2.2 | Requirements for autonomy and assistance functions in ground rescue robots | Daun and von Stryk, IEEE SSRR, 2023 | 10.1109/SSRR59696.2023.10499930 | VERIFIED |
| megalingam2022 | 2.2 | Low-cost SAR robot platform evaluated at WRS 2020 | Megalingam et al., Advanced Robotics, 2022 | 10.1080/01691864.2022.2117575 | VERIFIED |
| verano2022 | 2.2 | Low-cost teleoperated explorer robot | Verano et al., IJACSA, 2022 | 10.14569/IJACSA.2022.01307104 | VERIFIED |
| cafolla2026 | 2.2, 2.5, 2.6 | Universal add-on SAR controller (voice control, 3D reconstruction, person following) on drone and quadruped; cloud-based connectivity | Cafolla et al., Robot. Auton. Syst., 2026 | 10.1016/j.robot.2025.105237 | VERIFIED |
| jia2025 | 2.2, 2.6 | Ground-air amphibious UAV, separation cage; 1.2 kg, 40 min endurance at 1 kg payload; control mode not stated in abstract | Jia et al., Applied Sciences, 2025 | 10.3390/app15168792 | VERIFIED |
| raghavan2026 | 2.2, 2.4, 2.5, 2.6 | YOLOv8 victim detection on a Jetson Nano mobile robotic vehicle with cloud alerts; control mode not stated in abstract | Raghavan et al., Results in Engineering, 2026 | 10.1016/j.rineng.2026.110608 | VERIFIED |
| khattab2025 | 2.2, 2.4, 2.6 | Teleoperated earthquake rescue robot; multimodal detection validated in MATLAB simulation; victim speaker/microphone pending implementation (abstract) | Khattab et al., Scientific Reports, 2025 | 10.1038/s41598-025-16003-7 | VERIFIED |
| schrick2025 | 2.3 | Microservice control architecture for safety-critical mobile robots | Schrick et al., Robot. Auton. Syst., 2025 | 10.1016/j.robot.2024.104795 | VERIFIED |
| koczi2025 | 2.3 | Humanoid safety scoping review: most work on physical safety; cybersecurity, standardisation, socio-ethical aspects addressed less frequently | Koczi and Sarosi, Electronics, 2025 | 10.3390/electronics14234734 | VERIFIED |
| chen2007 | 2.4, 5 | Operator performance and interface design in teleoperation | Chen, Haas, Barnes, IEEE Trans. SMC-C, 2007 | 10.1109/TSMCC.2007.905819 | VERIFIED |
| bakzadeh2025 | 2.4 | Interface-design guidelines for mining emergency robots | Bakzadeh et al., Robotics, 2025 | 10.3390/robotics14110148 | VERIFIED |
| ruan2025 | 2.4 | Semantics-based situational awareness for operators of deployed robots | Ruan et al., Front. Robot. AI, 2025 | 10.3389/frobt.2025.1694123 | VERIFIED |
| akgun2023 | 2.4 | Affect (LED expressions) as a robot-to-rescue-worker communication channel; three online studies, N = 112, 223, 151 | Akgun et al., IEEE Trans. Affect. Comput., 2023 | 10.1109/TAFFC.2022.3221922 | VERIFIED |
| chitikena2023 | 2.1 | Ethical and design framework for SAR robots in the response phase | Chitikena, Sanfilippo, Ma, Applied Sciences, 2023 | 10.3390/app13031800 | VERIFIED |
| bachhuber2016 | 2.5, 5.2 | Glass-to-glass video delay measurement method | Bachhuber and Steinbach, IEEE ICIP, 2016 | 10.1109/ICIP.2016.7532735 | VERIFIED |
| delmerico2019 | 2.1, 2.6 | Survey of rescue robotics against first-responder needs; robustness, speed, versatility, ease of use not yet met | Delmerico et al., J. Field Robot., 2019 | 10.1002/rob.21887 | VERIFIED |
| schneider2016 | 2.1, 2.4, 2.6 | SAR requirements; robot should provide audio-visual communication between operator and trapped persons (quote read in arXiv:1912.04693 version) | Schneider and Wildermuth, ICCC, 2016 | 10.1109/carpathiancc.2016.7501177 | VERIFIED |
| murphy2004 | 2.2, 2.6 | WTC 2001, first known use of robots for USAR; performance by mobility, sensors, control, communications, power | Murphy, IEEE Robot. Autom. Mag., 2004 | 10.1109/MRA.2004.1337826 | VERIFIED |
| nagatani2013 | 2.2, 2.5, 2.6 | Fukushima: robust wireless not possible in reactor buildings, wired communication device installed | Nagatani et al., J. Field Robot., 2013 | 10.1002/rob.21439 | VERIFIED |
| kawatsuma2012 | 2.2 | Fukushima robot response lessons: organisation, operation scheme, systemisation | Kawatsuma, Fukushima, Okada, Industrial Robot, 2012 | 10.1108/01439911211249715 | VERIFIED |
| jacoff2012 | 2.2, 2.6 | Standard test methods for response robots developed through competitions | Jacoff et al., PerMIS, 2012 | 10.1145/2393091.2393126 | VERIFIED |
| chung2023 | 2.2, 2.6 | DARPA Subterranean Challenge 2018-2021 analysis and lessons | Chung, Orekhov, Maio, Annu. Rev. Control Robot. Auton. Syst., 2023 | 10.1146/annurev-control-062722-100728 | VERIFIED |
| pramono2024 | 2.2, 2.4, 2.6 | 3D-printed IoT disaster robot: video, GPS, lighting; Bluetooth 10 m, video 12 m; "affordable" | Pramono, Al Hakim, Alfianto, J. Nas. Tek. Elektro, 2024 | 10.25077/jnte.v13n1.1191.2024 | VERIFIED |
| manuel2022 | 2.2, 2.5, 2.6 | LoRa LPWAN SAR communication architecture; Rescuer robot, Gazebo and lab tests | Manuel, Faied, Krishnan, IEEE Access, 2022 | 10.1109/access.2022.3178437 | VERIFIED |
| yamauchi2022 | 2.2, 2.4, 2.6 | Active scope camera with 80 distributed sensors incl. microphones and speakers; Fukushima Robot Test Field | Yamauchi et al., ROBOMECH J., 2022 | 10.1186/s40648-022-00223-x | VERIFIED |
| kim2023 | 2.2, 2.4, 2.6 | Low-cost thermal-IR survivor localisation and approach for a SAR assistant robot | Kim et al., Machines, 2023 | 10.3390/machines11030329 | VERIFIED |
| cantizani2022 | 2.2, 2.4 | BLE wearables detected by SAR robots up to 15 m | Cantizani-Estepa et al., IEEE Access, 2022 | 10.1109/access.2022.3204272 | VERIFIED |
| iec60204 | 2.3, 2.6 | Stop category 0: immediate removal of power to machine actuators (uncontrolled stop); used as a behavioural analogy only, no compliance claim | IEC 60204-1:2016+AMD1:2021 CSV, Ed. 6.1 | IEC webstore publication 26037 | VERIFIED (metadata on IEC webstore; clause 9.2.2 wording via vendor documents, normative text not read) |
| narasimhan2024 | 2.3 | Run-time shield for networked robots under stochastic latency; F1/10th over congested Wi-Fi | Narasimhan, Bhat, Chinchali, IEEE RA-L, 2024 | 10.1109/lra.2023.3340525 | VERIFIED |
| candea2004 | 2.3, 2.6 | Recovery-oriented computing: recover fast, multiple lines of defence | Candea et al., Computer, 2004 | 10.1109/mc.2004.219 | VERIFIED |
| ramesh2022 | 2.3 | Robot vitals / robot health: run-time degradation detection for human takeover | Ramesh, Stolkin, Chiou, IEEE RA-L, 2022 | 10.1109/lra.2022.3192612 | VERIFIED |
| luz2023 | 2.4 | Latency compromises robot safety, overshoot, workload; interfaces for 3 s latency | Luz, Silva, Ventura, IEEE Access, 2023 | 10.1109/access.2023.3240307 | VERIFIED |
| bakzadeh2026b | 2.4 | Interviews with ten mine-rescue personnel: real-time situational data, communication, reliability | Bakzadeh et al., Front. Robot. AI, 2026 | 10.3389/frobt.2026.1698570 | VERIFIED |
| bethel2007 | 2.4, 2.6 | Non-facial/non-verbal affect for robot-assisted victim assessment within about 3 m | Bethel and Murphy, ACM/IEEE HRI, 2007 | 10.1145/1228716.1228755 | VERIFIED |
| murphy2010 | 2.4, 2.6 | Survivor Buddy: 4-DoF head, touch-screen face, social medium between trapped survivors and outside world | Murphy et al., ACM/IEEE HRI, 2010 | 10.1109/hri.2010.5453233 | VERIFIED |
| murphy2011 | 2.4, 2.6 | Survivor Buddy 2.0: 50% cheaper, 78% lighter, up to 700% faster than 1.0 | Murphy et al., IEEE ICRA, 2011 | 10.1109/icra.2011.5979977 | VERIFIED |
| srinivasan2012 | 2.4, 2.6 | 4-10 h from victim discovery to extrication; robot stays with victim; simulated US&R studies | Srinivasan, Henkel, Murphy, IEEE SSRR, 2012 | 10.1109/ssrr.2012.6523916 | VERIFIED |
| tiberkak2023 | 2.5 | WebRTC multi-operator remote control platform with priority system and chat | Tiberkak, Hentout, Belkhir, Int. J. Intell. Robot. Appl., 2023 | 10.1007/s41315-023-00281-3 | VERIFIED |
| militano2023 | 2.5 | Cloud-to-edge-to-IoT continuum for SAR low-delay requirements; open challenge | Militano et al., Future Internet, 2023 | 10.3390/fi15020055 | VERIFIED |
| murphy2004hri | 2.1, 2.6 | Rescue-HRI tutorial; domain theory of robot-assisted search (workflow and information-flow models) from eight years of USAR HRI | Murphy, IEEE Trans. SMC-C, 2004 | 10.1109/TSMCC.2004.826267 | VERIFIED |
| queralta2020 | 2.1, 2.6 | Review of multi-robot SAR systems: coordination and perception algorithms | Queralta et al., IEEE Access, 2020 | 10.1109/ACCESS.2020.3030190 | VERIFIED |
| beer2014 | 2.1 | Levels of robot autonomy range from teleoperation to full autonomy | Beer, Fisk, Rogers, J. Human-Robot Interaction, 2014 | 10.5898/JHRI.3.2.Beer | VERIFIED (pages 74-99 per Scholar Commons record) |
| kruijff2016 | 2.2, 2.6 | Amatrice (Italy) August 2016 earthquake: ground and aerial robots collected data for 3D models of two damaged churches | Kruijff-Korbayova et al., IEEE SSRR, 2016 | 10.1109/SSRR.2016.7784314 | VERIFIED |
| endsley1995 | 2.4 | Theory of situation awareness and its role in dynamic decision making | Endsley, Human Factors, 1995 | 10.1518/001872095779049543 | VERIFIED |

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
| 2.2 | liu2026hexapod (Liu et al., Mech. Mach. Theory 225:106472, 2026, doi 10.1016/j.mechmachtheory.2026.106472): wheeled hexapod rescue device. Removed from Section 2 and references.bib on 2026-10-22 because neither abstract nor full text could be read | Full text | UNVERIFIED |
| 2.6, Table 2.1 | "NR*" cells of the six Table 2.1 rows still based on abstracts (full text blocked or paywalled when tried 2026-10-22; Zenodo copy of murphy2011 is listed but could not be downloaded): murphy2010/murphy2011 (Survivor Buddy), megalingam2022, manuel2022, cafolla2026, yamauchi2022, raghavan2026. Rows checked against full text on 2026-10-22: verano2022, pramono2024, khattab2025, kim2023, jia2025 | Full text of each listed paper (paywalled or bot-blocked when tried) | UNVERIFIED |

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
