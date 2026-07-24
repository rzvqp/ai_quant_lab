"""Order Manager's own append-only audit journal. Mirrors the established
`ai_trader.context_memory.repository` convention (one `.jsonl` stream, envelope = deterministic
content-hash id + sequence, fsync-on-append, idempotent-duplicate vs conflicting-duplicate distinction,
integrity re-verification on read) at a scope matching this package's single record type -- it does not
import `context_memory` (a different, multi-type-generic package this one has no need to depend on;
reusing the PATTERN, not the module, exactly as disclosed in the design doc)."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class JournalCorruptionError(Exception):
    """Raised when a line's stored `event_id` does not match the hash of its own payload."""


class ConflictingDuplicateAuditEventError(Exception):
    """Raised when an `event_id` collision carries a DIFFERENT payload than the one already
    journaled -- never silently resolved (same discipline as `context_memory.repository`)."""


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_audit_event_id(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class OrderAuditEvent:
    """One journaled Order Manager event. `event_id` is the caller-visible identity; recomputed and
    verified on every read (never trusted from disk alone)."""

    stage: str
    client_order_id: str
    correlation_id: str
    as_of: int
    detail: dict[str, Any] = field(default_factory=dict)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "client_order_id": self.client_order_id,
            "correlation_id": self.correlation_id,
            "as_of": self.as_of,
            "detail": self.detail,
        }


class OrderManagerAuditJournal:
    """Single-writer-process, append-only. The file (never the in-memory index) is the source of
    truth; the index is rebuilt from disk on construction, matching `context_memory.repository`'s own
    rebuild-on-read discipline."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._by_id: dict[str, dict[str, Any]] = {}
        self._sequence = 0
        self._rebuild()

    def _rebuild(self) -> None:
        self._by_id.clear()
        self._sequence = 0
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                envelope = json.loads(line)
                self._ingest_envelope(envelope)

    def _ingest_envelope(self, envelope: dict[str, Any]) -> None:
        event_id = envelope["event_id"]
        payload = envelope["payload"]
        recomputed = compute_audit_event_id(payload)
        if recomputed != event_id:
            raise JournalCorruptionError(
                f"audit journal line has event_id={event_id!r} but payload hashes to {recomputed!r}"
            )
        self._by_id[event_id] = payload
        self._sequence = max(self._sequence, envelope["sequence"])

    def append(self, event: OrderAuditEvent) -> str:
        """Idempotent: appending the identical event twice (same `event_id`) is a no-op. A DIFFERENT
        payload colliding on `event_id` (astronomically unlikely with sha256, but never silently
        accepted) raises."""
        payload = event.canonical_payload()
        event_id = compute_audit_event_id(payload)
        with self._lock:
            existing = self._by_id.get(event_id)
            if existing is not None:
                if existing != payload:
                    raise ConflictingDuplicateAuditEventError(
                        f"event_id={event_id!r} already journaled with a different payload"
                    )
                return event_id  # idempotent no-op
            self._sequence += 1
            envelope = {"event_id": event_id, "sequence": self._sequence, "payload": payload}
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(_canonical_json(envelope) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._by_id[event_id] = payload
            return event_id

    def get(self, event_id: str) -> dict[str, Any] | None:
        return self._by_id.get(event_id)

    def events_for_order(self, client_order_id: str) -> tuple[dict[str, Any], ...]:
        return tuple(
            p for p in self._by_id.values() if p.get("client_order_id") == client_order_id
        )

    def __len__(self) -> int:
        return len(self._by_id)

    def verify_integrity(self) -> bool:
        """Re-derives every event_id from its stored payload -- raises via `_rebuild`/`_ingest_envelope`
        on any mismatch, so a clean return simply confirms no exception was raised."""
        self._rebuild()
        return True
