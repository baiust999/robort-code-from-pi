# Bibliography verification (Phase 6)

Scope: independent re-verification of the 19 references.bib entries that are
NOT in citation.md's "Master citation table". That table already lists 6
entries as VERIFIED from a prior session (casper2003, liu2013, pont2001,
valin2012, shi2025webrtc, ublox_neo6); those were out of scope here and were
not rechecked.

Method: Crossref API (api.crossref.org/works/<DOI>) for every DOI entry,
compared field by field against references.bib. For the 4 non-DOI entries,
the actual source page/PDF was fetched or searched for directly. No entry
was added, changed, or removed in references.bib or citation.md; this file
is a read-only check.

## Summary

- 19 entries checked.
- 18 VERIFIED (title, authors, venue, year, and pages/volume/issue all match
  the cited source; 2 of the 18 carry a minor caveat noted below, not a
  mismatch).
- 1 UNVERIFIABLE-BY-DESIGN (avi2026review: unpublished manuscript, no DOI,
  cannot be checked against an external record by definition).
- 0 real MISMATCHES found (no wrong author, title, year, venue, or page
  range that would need correcting).

## Findings by entry

| BibKey | Verdict | What was checked | Notes / discrepancies | Source |
|---|---|---|---|---|
| daun2023 | VERIFIED | Title, authors, event, pages, year | Exact match | Crossref DOI 10.1109/SSRR59696.2023.10499930 |
| megalingam2022 | VERIFIED | Title, authors, journal, vol/issue/pages, year | Exact match | Crossref DOI 10.1080/01691864.2022.2117575 |
| akgun2023 | VERIFIED | Title, authors, journal, vol/issue/pages, year | Exact match | Crossref DOI 10.1109/TAFFC.2022.3221922 |
| chitikena2023 | VERIFIED | Title, authors, journal, vol/issue/article no, year | Exact match | Crossref DOI 10.3390/app13031800 |
| schrick2025 | VERIFIED | Title, authors, journal, vol/article no, year | Exact match | Crossref DOI 10.1016/j.robot.2024.104795 |
| koczi2025 | VERIFIED | Title, authors, journal, vol/issue/article no, year | Exact match | Crossref DOI 10.3390/electronics14234734 |
| verano2022 | VERIFIED | Title, authors, journal, vol/issue, year | Crossref's own author metadata splits each author oddly (e.g. given="Rafael Verano", family="M"), a Crossref-side formatting artifact for these double-surname names, not a bib error; the .bib's family names (Verano, Caceres, Arenas, Montoya, Guevara, Galdos, Talavera) correctly identify the authors and match the given-name halves of the Crossref record | Crossref DOI 10.14569/IJACSA.2022.01307104 |
| cred2026 | VERIFIED | Title, authors, institution, year | Report's full title is "2025 Disasters in Numbers: Earth, Wind & Fire"; the .bib title "2025 Disasters in Numbers" is the first half only, missing the subtitle. Not a wrong title, just incomplete -- worth a one-line fix before camera-ready. Author list (Delforge, Below, Wathelet, Tonnelier, Alonso, Speybroeck) and 2026/CRED/Brussels all confirmed via the report's own recommended-citation block (no DOI exists for this report; it is CRED's house report, correctly entered as @techreport) | WebSearch of files.emdat.be/reports/2025_EMDAT_report.pdf citation block + preventionweb.net listing; the PDF itself could not be text-extracted (compressed binary), so this rests on secondary citation records of the report, not a direct read of its title page |
| tabib2024 | VERIFIED | Title, all 18 authors, year | Exact match, including author order | arXiv abstract page 2410.08507 |
| kareem2026 | VERIFIED | Title, authors, journal, vol/pages, year | Exact match | Crossref DOI 10.1109/ACCESS.2026.3660002 |
| bakzadeh2026 | VERIFIED | Title, authors, journal, vol/article no, year | Exact match | Crossref DOI 10.3389/frobt.2026.1857704 |
| avi2026review | UNVERIFIABLE-BY-DESIGN | N/A | Self-reported unpublished/under-review manuscript by the paper's own authors, no DOI exists yet to check against. The existing .bib comment already flags this correctly and says to update or remove it before camera-ready once a DOI exists. No action needed now beyond leaving that flag in place | N/A (nothing external to check) |
| brooke1996 | VERIFIED (with caveat) | Title, book, publisher, year, ISBN, editors, pages of the CRC reissue | Crossref confirms: title "SUS: A Quick and Dirty Usability Scale", book "Usability Evaluation In Industry", publisher CRC Press, editors Jordan/Thomas/McClelland/Weerdmeester, ISBN 9780429157011, and pages 207-212 for the DOI's target (the CRC reissue) -- all matching the .bib note exactly. Crossref lists no chapter author for this record at all (not Brooke, not anyone), so the "Brooke, J." author and the original-1996-print pagination "189-194" remain attributed from a secondary source (bangor2008's reference list, per the existing .bib comment) and were not independently re-derived from a primary record of the 1996 print edition -- this is the same limitation the prior session's comment already disclosed, confirmed still accurate | Crossref DOI 10.1201/9781498710411-35 (chapter) and 10.1201/9781498710411 (parent book) |
| bangor2008 | VERIFIED | Title, authors, journal, vol/issue/pages, year | Exact match | Crossref DOI 10.1080/10447310802205776 |
| chen2007 | VERIFIED | Title, authors, journal, vol/issue/pages, year | Exact match | Crossref DOI 10.1109/TSMCC.2007.905819 |
| wilson1927 | VERIFIED | Title, author, journal, vol/issue/pages, year | Exact match | Crossref DOI 10.1080/01621459.1927.10502953 |
| bachhuber2016 | VERIFIED | Title, authors, event, pages, year | Exact match | Crossref DOI 10.1109/ICIP.2016.7532735 |
| rpi_docs | VERIFIED (with caveat) | get_throttled bit-pattern table | Directly confirmed on the current Raspberry Pi OS/vcgencmd documentation page: bit 0 under-voltage, bit 1 ARM frequency capped, bit 2 currently throttled, bit 3 soft temperature limit, bits 16-19 the "has happened since boot" flags for the same conditions -- matches the .bib note. The "between 80C and 85C...progressively throttled back" wording lives on a separate Raspberry Pi Hardware (frequency management/thermal) page, not the one fetched directly; its substance (80C soft throttle warning, 85C hard limit on ARM+GPU) was confirmed via search of Raspberry Pi's own documentation content rather than a direct re-fetch of that exact page, so this part is confirmed-in-substance rather than quote-verified against a freshly loaded page | Direct fetch of raspberrypi.com/documentation/computers/os.html (get_throttled) + WebSearch confirming the 80-85C thermal-throttling language exists in Raspberry Pi's documentation |
| adafruit_dht11 | VERIFIED | DHT11-specific humidity/temperature accuracy and sampling rate | Exact wording match: "Good for 20-80% humidity readings with 5% accuracy", "Good for 0-50C temperature readings +/-2C accuracy", "No more than 1 Hz sampling rate". The .bib's own caveat that this is a distributor-hosted page, not the original Aosong datasheet, is correct and preserved here, not treated as a defect | Direct fetch of learn.adafruit.com/dht |

## What this does not cover

- The 6 entries already verified in citation.md's master table were not
  rechecked here (out of scope, per this task's directive).
- Whether each citation is used to support the correct claim in the
  manuscript text (i.e. citation-to-claim fit) was not assessed; this file
  only checks that the bibliographic record itself is real and accurately
  transcribed.
- cred2026's PDF title page could not be read directly (binary/compressed
  text); the verification rests on the report's own recommended-citation
  block as reproduced by two independent secondary sources (PreventionWeb
  and the UCLouvain institutional repository), not a direct read of page 1.

## Update 2026-10-22: avi2026review removed

At the authors' request, avi2026review was deleted from references.bib, citation.md, the paper outline, Section 2 and Section 5.7. Claims that rested only on it (2025-2026 corpus statistics, the review's mode classification of individual papers) were removed; the remaining Section 2 claims are sourced to the primary papers. The entry above is kept as a historical record only.

## Section 2 Q1 revision (2026-10-22)

24 entries added to references.bib for the Section 2 rewrite. Each was
generated directly from its Crossref record (api.crossref.org/works/<DOI>),
so title, authors, venue, volume, issue, pages and year are Crossref's own
values, and each claim made about it in Section 2 was checked against the
abstract (OpenAlex abstract_inverted_index).

| BibKey | Verdict | Notes |
|---|---|---|
| delmerico2019, nagatani2013, kawatsuma2012, murphy2004, jacoff2012, chung2023, murphy2010, murphy2011, bethel2007, srinivasan2012, candea2004, kim2023, manuel2022, yamauchi2022, cantizani2022, militano2023, tiberkak2023, narasimhan2024, ramesh2022, luz2023, bakzadeh2026b | VERIFIED | Crossref record + abstract |
| pramono2024 | VERIFIED (caveat) | Crossref gives no volume/issue; volume 13, number 1 taken from the DOI suffix (v13n1) |
| schneider2016 | VERIFIED (caveat) | Crossref record for the ICCC 2016 paper; the quoted requirement (audio-visual communication between operator and trapped persons) was read in the authors' arXiv version 1912.04693, whose journal-ref is this paper |
| iec60204 | VERIFIED (caveat) | Title, edition 6.0, date 2016-10-13 from IEC webstore publication 26037; the stop-category-0 wording (clause 9.2.2) comes from vendor documents quoting the clause (ABB), not from the normative text |

Not added (found but not needed, or not verifiable from an abstract):
kruijff2015 TRADR (10.1007/s13218-015-0352-5, no abstract available),
Murphy, Disaster Robotics, MIT Press 2014 (10.7551/mitpress/9407.001.0001,
no abstract), crick2017 rosbridge (no abstract).
