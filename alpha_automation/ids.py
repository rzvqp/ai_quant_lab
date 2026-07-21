"""Monotonic ID allocator -- pure stdlib, file-backed, never reuses an ID.

Provides the queryable/atomic ID service the current markdown-prose registries lack. Counters
persist to a single JSON file under the state directory. IDs are zero-padded and namespaced:

    INV-000001   an internal investigation record
    DC-0001      a frozen Discovery Candidate (reserved on creation, never reused -- Phase 3)

Allocation is append-then-flush on every call so a crash cannot hand out the same ID twice.
Run IDs are timestamp-based (human-readable, sortable) and take the clock explicitly so tests
are deterministic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional


class IdAllocator:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._counters = self._read()

    def _read(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                # Fail-closed: never silently reset a corrupt counter file -- surface it.
                raise
        return {}

    def _write(self) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._counters, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)  # atomic on same filesystem

    def _next(self, namespace: str) -> int:
        n = int(self._counters.get(namespace, 0)) + 1
        self._counters[namespace] = n
        self._write()
        return n

    def next_investigation_id(self) -> str:
        return f"INV-{self._next('INV'):06d}"

    def next_candidate_id(self) -> str:
        # Reserved for Phase 3 freeze; kept here so the whole namespace has one allocator.
        return f"DC-{self._next('DC'):04d}"

    def peek(self, namespace: str) -> int:
        return int(self._counters.get(namespace, 0))


def make_run_id(clock: Optional[Callable[[], str]] = None, suffix: str = "") -> str:
    """Human-readable, sortable run id. `clock` returns an ISO-ish stamp; injectable for tests."""
    from datetime import datetime, timezone

    stamp = (clock or (lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))()
    stamp = stamp.replace(":", "").replace("-", "")
    return f"R-{stamp}{('-' + suffix) if suffix else ''}"
