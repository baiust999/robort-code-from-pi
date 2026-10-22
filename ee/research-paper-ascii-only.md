---
name: research-paper-ascii-only
description: Files in /home/pi/robot/research paper/ must be plain ASCII - no em dashes, arrows, §, ✓, °, ≥ etc.
metadata:
  type: feedback
---

Write only plain ASCII in the research paper folder. Use `-`, `->`, `Section`, `Yes`/`No`, `deg`, `>=`, `<=`, `~`, `x` and `|` in place of the Unicode symbols.

**Why:** the user's viewer shows non-ASCII characters as the � sign, and they asked never to use it (2026-10-04).
**How to apply:** check any new or edited research paper text with `grep -P '[^\x00-\x7F]'` before finishing.
