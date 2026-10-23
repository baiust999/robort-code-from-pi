Check and fix the inconsistencies between Section 3 and Section 5 of my research paper.

1. **Heartbeat rate:** Check the dashboard, Raspberry Pi, and Arduino code. Correct Section 5.4 to match the actual 500 ms controller heartbeat and distinguish it from the Arduino's separate 1000 ms status heartbeat. Verify Table 5.5b against the actual dead-man timeout logic.

2. **Dead-man arming:** Fix the contradictory statements in Section 5.1a about whether pan, tilt, and status commands re-arm the dead-man timer. Check the actual Arduino firmware and corrected mock implementation.

3. **Placeholders:** Resolve `[VERIFY: RQ labels]` and `[NEEDS SPEC]` using the actual research questions and reliable battery specifications. Never invent missing information.

4. **RQ4 mapping:** Check the research questions and available results. Correct the Section 3.0 mapping so it references only relevant evidence. Keep unmeasured video/audio performance explicitly marked as pending.

5. **240 fps claim:** Correct Section 3.5.2 because physical wheel-stop filming has not been completed. Clearly distinguish analytical timing, firmware logs, and pending physical measurements.

Inspect the actual source code, manuscript, and evaluation records before editing. Fix related inconsistencies throughout Sections 3 and 5.

Preserve valid results, citations, tables, and the existing paper structure. Do not fabricate data, claim pending experiments are complete, or modify unrelated files.

After editing, check for remaining contradictions and show me a summary of the changes. Do not commit or push anything.
