"""Structured JSONL logging -- pure stdlib.

Matches the lab convention (append-only JSONL audit trails). Every event is one JSON line
with a UTC timestamp, level, event name, and arbitrary structured fields. Logs go to both a
run-scoped file and (optionally) stdout. There is no external logging dependency.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TextIO


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonlLogger:
    def __init__(
        self,
        path: Optional[Path] = None,
        echo: bool = True,
        stream: Optional[TextIO] = None,
        clock=None,
    ):
        self.path = Path(path) if path else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.echo = echo
        self.stream = stream if stream is not None else sys.stdout
        self._clock = clock or _utc_now_iso

    def log(self, level: str, event: str, **fields) -> dict:
        rec = {"ts": self._clock(), "level": level, "event": event}
        rec.update(fields)
        line = json.dumps(rec, ensure_ascii=False, default=str)
        if self.path:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        if self.echo and self.stream is not None:
            self.stream.write(line + "\n")
            self.stream.flush()
        return rec

    def info(self, event: str, **f):
        return self.log("INFO", event, **f)

    def warn(self, event: str, **f):
        return self.log("WARN", event, **f)

    def error(self, event: str, **f):
        return self.log("ERROR", event, **f)

    def debug(self, event: str, **f):
        return self.log("DEBUG", event, **f)
