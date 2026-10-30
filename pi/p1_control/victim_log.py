"""Victim marks: where the operator found someone.

Each mark is one JSON line in ``victims.jsonl`` in the robot's log folder, so
it survives a dashboard reload or a laptop crash and stays with the mission
logs. The snapshot is never sent here: the dashboard saves it on the
operator's device.
"""

from __future__ import annotations

import json
import secrets
import threading
import time
from pathlib import Path
from typing import Any

from common.logging_setup import EventLogger

NOTE_MAX = 280


class VictimLog:
    def __init__(self, directory: Path, log: EventLogger) -> None:
        self.directory = directory
        self.log = log
        self._index = directory / "victims.jsonl"
        self._lock = threading.Lock()

    def add(self, note: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Store one mark; ``fields`` are the server-side readings (GPS, servos)."""
        now = time.time()
        mark_id = f"{time.strftime('%Y%m%d-%H%M%S', time.localtime(now))}-{secrets.token_hex(2)}"
        mark: dict[str, Any] = {
            "id": mark_id,
            "ts": int(now * 1000),
            "note": note[:NOTE_MAX],
            **fields,
        }
        with self._lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            with self._index.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(mark) + "\n")
        return mark

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            try:
                lines = self._index.read_text(encoding="utf-8").splitlines()
            except FileNotFoundError:
                return []
        marks = []
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                mark = json.loads(line)
            except json.JSONDecodeError:
                self.log.warning("VICTIM_LOG_BAD_LINE", "skipped unreadable victim mark", line=number)
                continue
            if isinstance(mark, dict):
                marks.append(mark)
        return marks
