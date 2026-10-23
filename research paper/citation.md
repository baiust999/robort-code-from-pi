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
| bakzadeh2026 | 1, 2.1, 2.4, 2.6 | Mine-rescue platform review over three decades; design guidelines not established; two-way voice a fundamental functionality of most reviewed MRRs (full text PMC13487453) | Bakzadeh et al., Front. Robot. AI, 2026 | 10.3389/frobt.2026.1857704 | VERIFIED (authors as initials, per Crossref) |
| daun2023 | 1, 2.2 | Requirements for autonomy and assistance functions in ground rescue robots | Daun and von Stryk, IEEE SSRR, 2023 | 10.1109/SSRR59696.2023.10499930 | VERIFIED |
| megalingam2022 | 2.2 | Low-cost SAR robot platform evaluated at WRS 2020 | Megalingam et al., Advanced Robotics, 2022 | 10.1080/01691864.2022.2117575 | VERIFIED |
| verano2022 | 2.2 | Low-cost teleoperated explorer robot | Verano et al., IJACSA, 2022 | 10.14569/IJACSA.2022.01307104 | VERIFIED |
| cafolla2026 | 2.2, 2.5, 2.6 | Universal add-on SAR controller (voice control, 3D reconstruction, person following) on drone and quadruped; cloud-based connectivity | Cafolla et al., Robot. Auton. Syst., 2026 | 10.1016/j.robot.2025.105237 | VERIFIED |
| jia2025 | 2.2, 2.6 | Ground-air amphibious UAV, separation cage; 1.2 kg, 40 min endurance at 1 kg payload; control mode not stated in abstract | Jia et al., Applied Sciences, 2025 | 10.3390/app15168792 | VERIFIED |
| raghavan2026 | 2.2, 2.4, 2.5, 2.6 | YOLOv8 victim detection on a Jetson Nano mobile robotic vehicle with cloud alerts; control mode not stated in abstract | Raghavan et al., Results in Engineering, 2026 | 10.1016/j.rineng.2026.110608 | VERIFIED |
| khattab2025 | 2.2, 2.4, 2.6 | Teleoperated earthquake rescue robot; multimodal detection validated in MATLAB simulation; victim speaker/microphone pending implementation (abstract) | Khattab et al., Scientific Reports, 2025 | 10.1038/s41598-025-16003-7 | VERIFIED |
| schrick2025 | 2.3 | Microservice control architecture for safety-critical mobile robots | Schrick et al., Robot. Auton. Syst., 2025 | 10.1016/j.robot.2024.104795 | VERIFIED |
| koczi2025 | 2.3 | Humanoid safety scoping review: most work on physical safety; cybersecurity, standardisation, socio-ethical aspects addressed less frequently | Koczi and Sarosi, Electronics, 2025 | 10.3390/electronics14234734 | VERIFIED |
| chen2007 | 1, 2.4, 5 | Operator performance and interface design in teleoperation | Chen, Haas, Barnes, IEEE Trans. SMC-C, 2007 | 10.1109/TSMCC.2007.905819 | VERIFIED |
| bakzadeh2025 | 2.4 | Interface-design guidelines for mining emergency robots | Bakzadeh et al., Robotics, 2025 | 10.3390/robotics14110148 | VERIFIED |
| ruan2025 | 2.4 | Semantics-based situational awareness for operators of deployed robots | Ruan et al., Front. Robot. AI, 2025 | 10.3389/frobt.2025.1694123 | VERIFIED |
| akgun2023 | 2.4 | Affect (LED expressions) as a robot-to-rescue-worker communication channel; three online studies, N = 112, 223, 151 | Akgun et al., IEEE Trans. Affect. Comput., 2023 | 10.1109/TAFFC.2022.3221922 | VERIFIED |
| chitikena2023 | 2.1 | Ethical and design framework for SAR robots in the response phase | Chitikena, Sanfilippo, Ma, Applied Sciences, 2023 | 10.3390/app13031800 | VERIFIED |
| bachhuber2016 | 2.5, 5.2 | Glass-to-glass video delay measurement method | Bachhuber and Steinbach, IEEE ICIP, 2016 | 10.1109/ICIP.2016.7532735 | VERIFIED |
| delmerico2019 | 2.1, 2.6 | Survey of rescue robotics against first-responder needs; robustness, speed, versatility, ease of use not yet met | Delmerico et al., J. Field Robot., 2019 | 10.1002/rob.21887 | VERIFIED |
| schneider2016 | 1, 2.1, 2.4, 2.6 | SAR requirements; robot should provide audio-visual communication between operator and trapped persons (quote read in arXiv:1912.04693 version) | Schneider and Wildermuth, ICCC, 2016 | 10.1109/carpathiancc.2016.7501177 | VERIFIED |
| murphy2004 | 1, 2.2, 2.6 | WTC 2001, first known use of robots for USAR; performance by mobility, sensors, control, communications, power | Murphy, IEEE Robot. Autom. Mag., 2004 | 10.1109/MRA.2004.1337826 | VERIFIED |
| nagatani2013 | 1, 2.2, 2.5, 2.6 | Fukushima: robust wireless not possible in reactor buildings, wired communication device installed | Nagatani et al., J. Field Robot., 2013 | 10.1002/rob.21439 | VERIFIED |
| kawatsuma2012 | 2.2 | Fukushima robot response lessons: organisation, operation scheme, systemisation | Kawatsuma, Fukushima, Okada, Industrial Robot, 2012 | 10.1108/01439911211249715 | VERIFIED |
| jacoff2012 | 2.2, 2.6 | Standard test methods for response robots developed through competitions | Jacoff et al., PerMIS, 2012 | 10.1145/2393091.2393126 | VERIFIED |
| chung2023 | 2.2, 2.6 | DARPA Subterranean Challenge 2018-2021 analysis and lessons | Chung, Orekhov, Maio, Annu. Rev. Control Robot. Auton. Syst., 2023 | 10.1146/annurev-control-062722-100728 | VERIFIED |
| pramono2024 | 2.2, 2.4, 2.6 | 3D-printed IoT disaster robot: video, GPS, lighting; Bluetooth 10 m, video 12 m; "affordable" | Pramono, Al Hakim, Alfianto, J. Nas. Tek. Elektro, 2024 | 10.25077/jnte.v13n1.1191.2024 | VERIFIED |
| manuel2022 | 2.2, 2.5, 2.6 | LoRa LPWAN SAR communication architecture; Rescuer robot, Gazebo and lab tests | Manuel, Faied, Krishnan, IEEE Access, 2022 | 10.1109/access.2022.3178437 | VERIFIED |
| yamauchi2022 | 2.2, 2.4, 2.6 | Active scope camera with 80 distributed sensors incl. microphones and speakers; Fukushima Robot Test Field | Yamauchi et al., ROBOMECH J., 2022 | 10.1186/s40648-022-00223-x | VERIFIED |
| kim2023 | 2.2, 2.4, 2.6 | Low-cost thermal-IR survivor localisation and approach for a SAR assistant robot | Kim et al., Machines, 2023 | 10.3390/machines11030329 | VERIFIED |
| cantizani2022 | 2.2, 2.4 | BLE wearables detected by SAR robots up to 15 m | Cantizani-Estepa et al., IEEE Access, 2022 | 10.1109/access.2022.3204272 | VERIFIED |
| iec60204 | 1, 2.3, 2.6 | Stop category 0: immediate removal of power to machine actuators (uncontrolled stop); used as a behavioural analogy only, no compliance claim | IEC 60204-1:2016+AMD1:2021 CSV, Ed. 6.1 | IEC webstore publication 26037 | VERIFIED (metadata on IEC webstore; clause 9.2.2 wording via vendor documents, normative text not read) |
| narasimhan2024 | 2.3 | Run-time shield for networked robots under stochastic latency; F1/10th over congested Wi-Fi | Narasimhan, Bhat, Chinchali, IEEE RA-L, 2024 | 10.1109/lra.2023.3340525 | VERIFIED |
| candea2004 | 1, 2.3, 2.6 | Recovery-oriented computing: recover fast, multiple lines of defence | Candea et al., Computer, 2004 | 10.1109/mc.2004.219 | VERIFIED |
| ramesh2022 | 2.3 | Robot vitals / robot health: run-time degradation detection for human takeover | Ramesh, Stolkin, Chiou, IEEE RA-L, 2022 | 10.1109/lra.2022.3192612 | VERIFIED |
| luz2023 | 2.4 | Latency compromises robot safety, overshoot, workload; interfaces for 3 s latency | Luz, Silva, Ventura, IEEE Access, 2023 | 10.1109/access.2023.3240307 | VERIFIED |
| bakzadeh2026b | 2.4 | Interviews with ten mine-rescue personnel: real-time situational data, communication, reliability | Bakzadeh et al., Front. Robot. AI, 2026 | 10.3389/frobt.2026.1698570 | VERIFIED |
| bethel2007 | 2.4, 2.6 | Non-facial/non-verbal affect for robot-assisted victim assessment within about 3 m | Bethel and Murphy, ACM/IEEE HRI, 2007 | 10.1145/1228716.1228755 | VERIFIED |
| murphy2010 | 2.4, 2.6 | Survivor Buddy: 4-DoF head, touch-screen face, social medium between trapped survivors and outside world | Murphy et al., ACM/IEEE HRI, 2010 | 10.1109/hri.2010.5453233 | VERIFIED | Full text read 2026-10-23 (fulltext/Survivor Buddy and SciGirls...md): 4-DoF head, MIMO 740 touch screen, "permit the survivor to videoconference with responders (or family)"; v1.0 prototype teleoperated; study with four middle-school girls and friends, "neither statistically significant nor rigorously controlled".
| murphy2011 | 2.2, 2.4, 2.6 | Survivor Buddy 2.0: abstract 50% less expensive, 78% lighter, up to 700% faster than 1.0; Table II (p. 705): weight 7.8 kg vs 1.72 kg, cost USD 3,600 vs USD 1,800, design time 6 months each; v1.0 mounted on an ATRV-jr base; joints network-controllable and tether permitted as design criteria | Murphy et al., IEEE ICRA, 2011; full text read 2026-10-23 (Zenodo copy, 6 pages; Table II read from the rendered page) | 10.1109/icra.2011.5979977 | VERIFIED (full text). The paper's conclusion contains a typo ("more cost-effective (50% lighter)"); Table II and the abstract give 50% cheaper |
| srinivasan2012 | 1, 2.4, 2.6 | 4-10 h from victim discovery to extrication; robot stays with victim; simulated US&R studies | Srinivasan, Henkel, Murphy, IEEE SSRR, 2012 | 10.1109/ssrr.2012.6523916 | VERIFIED |
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
| 2.6, Table 2.1 | Full-text status of rows (rechecked 2026-10-23): full texts of Rescuer, Universal Platform, Paripreksya 2.0, active scope camera, ERS and both Murphy Survivor Buddy papers were read for the cells in Table 2.1 and several cells were corrected (Rescuer audio and video, Universal Platform and active scope camera speakers, ERS evidence, Survivor Buddy cost and evidence); srinivasan2012 rests on its abstract | fulltext/*.md; Zenodo copy of murphy2011 | VERIFIED (full text) except srinivasan2012 (abstract) |
| bangor2008 | 5.8 | Empirical distribution of SUS scores to position the E14 mean against | Bangor, Kortum, Miller, Int. J. Hum.-Comput. Interact. 24(6), 2008; Crossref record and abstract ("nearly 10 years' worth" of SUS data on numerous products) checked 2026-10-23; full text not read | 10.1080/10447310802205776 | VERIFIED (abstract only). E14 is pending, so the comparison is a plan, not a result |
| brooke1996 | 5.8 | SUS instrument and scoring: odd items minus 1, even items 5 minus response, sum times 2.5 | Brooke, SUS - A quick and dirty usability scale, in Usability Evaluation in Industry, 1996; scoring paragraph read in a reproduction of the chapter text (hell.meiert.org/core/pdf/sus.pdf); Crossref lists pp. 207-212 for the CRC reissue, bib gives the 1996 print pages 189-194 and says so | 10.1201/9781498710411-35 | VERIFIED (chapter text via reproduction, not the print edition) |
| wilson1927 | 1, 5 (methods), 5.7 | 95% Wilson score interval for success proportions | Wilson, J. Am. Stat. Assoc. 22(158), 1927; Crossref record checked 2026-10-23; full text not read. The property cited ("informative when every trial succeeds") was reproduced by computation: 10 of 10 gives 72.2% to 100%, 30 of 30 gives 88.6% to 100% | 10.1080/01621459.1927.10502953 | VERIFIED (metadata; property by computation) |
| rpi_docs | 5.5 | get_throttled bit meanings (bit 0 under-voltage detected, bit 2 currently throttled, bit 16 under-voltage has occurred, bit 18 throttling has occurred); Arm cores progressively throttled between 80 and 85 deg C | Raspberry Pi Documentation, os.html (vcgencmd) and raspberry-pi.html (frequency management and thermal control), accessed 2026-10-23 | https://www.raspberrypi.com/documentation/computers/ | VERIFIED (official documentation; both quotations found: "When the core temperature is between 80C and 85C, the Arm cores will be progressively throttled back") |
| adafruit_dht11 | 5.6.3 | DHT11 tolerance: 20-80% RH at 5%, 0-50 deg C at +/-2 deg C, no more than 1 Hz | Adafruit Learn guide "DHT11, DHT22 and AM2302 Sensors", accessed 2026-10-23; page does not name the manufacturer (Aosong) | https://learn.adafruit.com/dht | VERIFIED as a distributor page (all three quotations found), not the manufacturer datasheet |
| cred2026 | 1.1 | 2025 disaster burden: 358 disasters, 16,607 deaths, 110.2 million affected, USD 169.68 billion losses (EM-DAT) | Delforge et al., CRED, "2025 Disasters in Numbers: Earth, Wind & Fire", compiled by the six listed authors; PDF text read 2026-10-23 | https://files.emdat.be/reports/2025_EMDAT_report.pdf | VERIFIED. Section 1.1 cites it for the four figures only; all four re-found in the downloaded PDF text on 2026-10-23 (358 disasters, 16,607 fatalities, 110.2 million affected, US$169.68B losses) |
| tabib2024 | 1.1 | Rapid SAR is critical to maximizing survival rates after natural disasters, and communications infrastructure is unreliable in such efforts (arXiv abstract, re-read via the arXiv API 2026-10-23; the abstract does not use the term "golden window") | Tabib et al., arXiv:2410.08507 (v1 11 Oct 2024, v2 10 Jun 2025; comment "accepted at ISER 2025") | arXiv:2410.08507 | VERIFIED as a preprint (abstract only) for the two statements above. Section 1.1 does not use the term "golden window", which this source does not name; bib lists 2024 and no venue |
| deshmukh2025 | 2.2, 2.6 | ROS quadruped on Raspberry Pi 4B + Pico, joystick control, Wi-Fi video to rescue team, 200 m control range and packet loss under 1 percent in field evaluation; no fail-safe, watchdog, victim audio, cost figure or code release described (code on request) | Deshmukh et al., IAES IJRA 14(4), 2025; full text read (PDF) | 10.11591/ijra.v14i4.pp539-550 | VERIFIED (OpenAlex lists a wrong DOI, ijra.v14i3.pp387-398; Crossref and the PDF give v14i4.pp539-550) |
| gehlot2025 | 2.2, 2.6 | Arduino Uno + LoRa command link, ESP32-CAM video over Wi-Fi, Blynk cloud dashboard; states 15 km open / 5 km urban range, 1.5 s video latency; stop is an operator command; no link-loss stop, victim audio or cost figure found; abstract and text call it "aerial"/"drone" although the hardware is a two-DC-motor ground vehicle | Gehlot et al., IAES IJRA 14(3), 2025; full text read (PDF) | 10.11591/ijra.v14i3.pp311-321 | VERIFIED |
| sharma2022 | 2.4 | Robots examine video feed with audio and stream detected survivor location to a cloud server (survivor treated as detection target) | Sharma et al., Drones 6(8), 2022; abstract only (MDPI full text blocked) | 10.3390/drones6080219 | VERIFIED (abstract only) |
| isaacs2022 | 2.1 | Teleoperation used as baseline for comparison with autonomous solutions in DARPA SubT Urban Circuit; communication constraints in underground domains | Isaacs et al., Field Robotics 2, 2022; abstract only (publisher PDF blocked) | 10.55417/fr.2022039 | VERIFIED (abstract only) |
| murray2022 | 2.3 | Industrial trend of moving safety functions from physical hardware (safety relays, interlocks) into software, which motivates formal verification | Murray et al., Sci. Comput. Program. 216, 2022; abstract only (ScienceDirect blocked) | 10.1016/j.scico.2021.102766 | VERIFIED (abstract only) |
| madhushankara2024 | 1, 2.3 | Hardware watchdog timer for drone processors: reset if the timer is not serviced within an interval; designed and verified in SystemVerilog, implemented in 15 nm technology (processor-hang watchdog, not a command-timeout dead-man) | Madhushankara et al., JESTR 17(6), 2024; full text read (PDF), introduction and abstract | 10.25103/jestr.176.08 | VERIFIED |
| ardupilot_rover_failsafe | 1, 2.3, 2.6 | Rover autopilot documentation: radio failsafe when the transmitter link is lost for FS_TIMEOUT (default 1 s); GCS failsafe when no MAVLink heartbeat arrives within FS_GCS_TIMEOUT (default 5 s); actions include Hold. Replaces khrystyuk2025 (two-page abstract-only paper, removed 2026-10-23) | ArduPilot Dev Team, Rover documentation page, accessed 2026-10-23; page shows only "Copyright 2024" | https://ardupilot.org/rover/docs/rover-failsafes.html | VERIFIED (official documentation; no version or date on the page; the documentation does not report measured stop times) |
| kamtam2024 | 2.4 | Survey: network latency in teleoperation of connected and autonomous vehicles affects uplink/downlink and operators' real-time perception and decision-making | Kamtam et al., Sensors 24(12), 2024; abstract only | 10.3390/s24123957 | VERIFIED (abstract only) |
| sini2022 | 2.3 | FMEA/FMEDA-based simulation of software detection and mitigation of random sensor and actuator hardware failures; benchmark is a Mars-exploration assistance rover mobility system | Sini et al., Sensors 22(13), 2022; full text read (Europe PMC PMC9269304) | 10.3390/s22134665 | VERIFIED |

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

## Section 7 re-check (2026-10-23)

Full-text or abstract re-check of the keys cited in `section7_future_work.md`. Only what Section 7 states was checked.

| BibKey | Statement in Section 7 | Checked against | Result |
|--------|------------------------|-----------------|--------|
| schneider2016 | 1, 2.1, 2.4, 2.6 | Full text (arXiv 1912.04693, section "Communication", "Autonomy and Tele-Operation", audio-visual requirement in the requirements section) | Supported in full text |
| valin2012 | Opus operates over a wide, dynamically adjustable bitrate range | RFC 6716 Abstract and Sections 2, 2.1 (first 100,000 characters) | Supported: 6 to 510 kbit/s, controls changeable during operation |
| beer2014 | Levels of robot autonomy from teleoperation to full autonomy | Abstract (via Semantic Scholar) | Supported (abstract); full text not read |
| queralta2020 | Multi-robot SAR survey; open questions include heterogeneous coordination and interoperability | Abstract (Semantic Scholar record, IEEE Access title matches `references.bib`) | Supported (abstract); full text not read |
| koczi2025 | Cybersecurity addressed less often than physical safety, in a humanoid-robot review | Abstract (Semantic Scholar) | Supported (abstract); scope is humanoids, not rescue robots |
| manuel2022 | LoRa SAR architecture tested in Gazebo and a lab; low-rate packets | Full text (fulltext/LoRa_LPWAN_Communication_Search_Rescue.md) | Supported in full text: Gazebo phase plus indoor lab phase with a Pioneer P3DX; packets carry destination, position and enable bits; 1.86 s packet delay at SF10, 250 kHz, CR 4/5 at 600 m; video is recorded on the robot, not shown streamed. NOTE: the file fulltext/Development_of_a_continuum_robot_...md is a duplicate of this paper, not a different paper |
| jacoff2012 | Standard test methods for response robots developed through competitions | NIST/Curtin record summary | Supported (summary); full text not read |
| bachhuber2016 | Method for measuring glass-to-glass video delay | Full text (fulltext/Glass_to_Glass_Delay_Measurement.md) | Supported in full text: an LED and phototransistor system for capture-to-display (glass-to-glass) delay with 0.5 ms precision. Its method differs from the clock-photograph method of Section 5.2, which Section 7 does not claim to follow |
| nagatani2013 | 1, 2.2, 2.5, 2.6 | Full text (fulltext/Fukushima_Daiichi_Quince_Rescue_Robots.md, Sections 3, 4.2, 4.3) | Supported in full text: Hamaoka tests showed the high-power 2.4 GHz devices would not work in reactor buildings; 200 m and 500 m twisted-pair cable with VDSL was used; cameras ran over the LAN. The paper also mentions a hybrid wired and wireless mesh network from an earlier NEDO project |
| raghavan2026 | Rubble-scene human detection with YOLOv8-s on a Jetson Nano, alerts to a mobile app | Full text (fulltext/Earthquake_Response_AI_Human_Detection.md) | Supported in full text: YOLOv8-s, Jetson Nano, Logitech C270, Firebase real-time database and MIT App Inventor alert app. The authors state their own boundary conditions on the dataset. Accuracy and latency figures not extracted |
| wilson1927 | Wilson interval, 30 of 30 gives lower bound 88.6% | Full text (fulltext/Wilson_Probable_Inference.md) and computation | Supported: the 1927 paper gives the interval for an observed rate; the 88.6% figure was reproduced by computation |
