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
| casper2003 | 2.1, 2.2 | Field HRI findings from robot-assisted USAR at the World Trade Center | Casper and Murphy, IEEE Trans. SMC-B, 2003 | 10.1109/TSMCB.2003.811794 | VERIFIED |
| liu2013 | 2.1 | Survey of robotic urban search and rescue from the control perspective | Liu and Nejat, J. Intell. Robot. Syst., 2013 | 10.1007/s10846-013-9822-x | VERIFIED |
| pont2001 | 2.4, 3.5 | Time-triggered scheduling pattern for reliable embedded control | Pont, Addison-Wesley, 2001 | ISBN 0201331381 | VERIFIED |
| valin2012 | 3.9.5 | Definition of the Opus low-latency audio codec | Valin, Vos, Terriberry, IETF RFC 6716, 2012 | 10.17487/RFC6716 | VERIFIED |
| shi2025webrtc | 2.3, 3.9 | Latency and reliability of a WebRTC-based real-time teleoperation link | Shi et al., IEEE Access, 2025 | 10.1109/ACCESS.2025.3620994 | VERIFIED |
| ublox_neo6 | 3.10 | NEO-6 GPS module characteristics for localisation | u-blox AG Data Sheet, 2011 | GPS.G6-HW-09005 | VERIFIED |

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
