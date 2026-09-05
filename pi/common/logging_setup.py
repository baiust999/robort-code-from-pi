"""Structured event logging in the format of Section 8.13.3.

Every line is ``[TS][PROC][LEVEL][EVENT_CODE][MSG]{k=v ...}`` written in append
mode, one line per write, so concurrent processes never interleave partial
records.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EventFormatter(logging.Formatter):
    """Render records as the bracketed five-field event format."""

    def __init__(self, process_name: str) -> None:
        super().__init__()
        self.process_name = process_name

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
            timespec="milliseconds"
        )
        event_code = getattr(record, "event_code", "GENERIC")
        message = record.getMessage()
        line = (
            f"[{timestamp}][{self.process_name}][{record.levelname}]"
            f"[{event_code}][{message}]"
        )
        fields = getattr(record, "fields", None)
        if fields:
            rendered = " ".join(f"{key}={_render(value)}" for key, value in fields.items())
            line = f"{line}{{{rendered}}}"
        if record.exc_info:
            line = f"{line} {self.formatException(record.exc_info)}"
        return line


def _render(value: Any) -> str:
    text = str(value)
    return f'"{text}"' if " " in text else text


class EventLogger:
    """Thin wrapper that keeps ``event_code`` and ``fields`` ergonomic."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _emit(self, level: int, code: str, message: str, **fields: Any) -> None:
        self._logger.log(level, message, extra={"event_code": code, "fields": fields})

    def debug(self, code: str, message: str, **fields: Any) -> None:
        self._emit(logging.DEBUG, code, message, **fields)

    def info(self, code: str, message: str, **fields: Any) -> None:
        self._emit(logging.INFO, code, message, **fields)

    def warning(self, code: str, message: str, **fields: Any) -> None:
        self._emit(logging.WARNING, code, message, **fields)

    def error(self, code: str, message: str, **fields: Any) -> None:
        self._emit(logging.ERROR, code, message, **fields)

    def critical(self, code: str, message: str, **fields: Any) -> None:
        self._emit(logging.CRITICAL, code, message, **fields)

    def exception(self, code: str, message: str, **fields: Any) -> None:
        self._logger.exception(message, extra={"event_code": code, "fields": fields})


def setup_logging(process_name: str, log_dir: Path, filename: str, level: int = logging.INFO) -> EventLogger:
    """Attach file + stderr handlers and return the event logger."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(process_name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()

    formatter = EventFormatter(process_name)

    file_handler = logging.FileHandler(log_dir / filename, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return EventLogger(logger)
