"""`LiveSignalJournal` (Piesa 3): the append-only observation record for the live signal pipeline. See
`types.py`'s own docstring (`LiveSignalJournalEntry`) for why none of `shadow_evidence.types`'s six
record dataclasses were reused verbatim, and what "reuse" concretely means here instead.

Append-only by construction: the only mutator is `record()` -- there is no remove/clear/replace method
anywhere on this class, and `entries` is exposed as an immutable `tuple`, never the backing list.

**Mandate 2 (2026-07-27), persistence**: an optional injected `SqliteStateStore` makes the full
observation history survive a process restart -- without one, behavior is byte-for-byte the prior
in-memory-only version (every pre-Mandate-2 test still passes unmodified). With one, every entry ever
recorded is loaded back at construction (not just what this instance itself has seen), and every new
`record()` call writes through immediately. `log_name` scopes multiple journals sharing one store, the
same way `LiveBarFeed`'s watermark key scopes per `(symbol, mt5_timeframe)`.

**Mandate 3, Element 1 (2026-07-27), gaps are journaled too**: `record_gap()`/`gaps` follow the exact
same shape and persistence discipline as `record()`/`entries`, on a SEPARATE log (`f"{log_name}.gaps"`)
so a `GapRecord` row is never confused with a `LiveSignalJournalEntry` row. This is what makes all three
classifications (MAINTENANCE/WEEKEND/UNEXPECTED) durably visible -- CEO: "un consumator care citeste
jurnalul peste sase luni nu poate distinge un shadow sanatos de unul cu pierderi" without them.
"""

from __future__ import annotations

import json

from ai_trader.live_signal_source.types import (
    GapClassification,
    GapRecord,
    LiveCandidate,
    LiveSignalJournalEntry,
)
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction

_DEFAULT_LOG_NAME = "live_signal_source.journal"


def _serialize_entry(entry: LiveSignalJournalEntry) -> str:
    candidate_payload: dict[str, object] | None = None
    if entry.candidate is not None:
        c = entry.candidate
        candidate_payload = {
            "strategy_id": c.strategy_id, "symbol": c.symbol, "direction": c.direction.value,
            "entry": c.entry, "stop": c.stop, "target": c.target, "session": c.session,
            "magic_number": c.magic_number, "comment": c.comment, "as_of": c.as_of,
        }
    return json.dumps({"symbol": entry.symbol, "as_of": entry.as_of, "candidate": candidate_payload})


def _deserialize_entry(payload: str) -> LiveSignalJournalEntry:
    data = json.loads(payload)
    candidate: LiveCandidate | None = None
    raw_candidate = data["candidate"]
    if raw_candidate is not None:
        candidate = LiveCandidate(
            strategy_id=raw_candidate["strategy_id"], symbol=raw_candidate["symbol"],
            direction=Direction(raw_candidate["direction"]), entry=raw_candidate["entry"],
            stop=raw_candidate["stop"], target=raw_candidate["target"],
            session=raw_candidate["session"], magic_number=raw_candidate["magic_number"],
            comment=raw_candidate["comment"], as_of=raw_candidate["as_of"],
        )
    return LiveSignalJournalEntry(symbol=data["symbol"], as_of=data["as_of"], candidate=candidate)


def _serialize_gap(gap: GapRecord) -> str:
    return json.dumps({
        "symbol": gap.symbol, "gap_start": gap.gap_start, "gap_end": gap.gap_end,
        "duration_seconds": gap.duration_seconds, "classification": gap.classification.value,
    })


def _deserialize_gap(payload: str) -> GapRecord:
    data = json.loads(payload)
    return GapRecord(
        symbol=data["symbol"], gap_start=data["gap_start"], gap_end=data["gap_end"],
        duration_seconds=data["duration_seconds"],
        classification=GapClassification(data["classification"]),
    )


class LiveSignalJournal:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        self._gap_log_name = f"{log_name}.gaps"
        if state_store is None:
            self._entries: list[LiveSignalJournalEntry] = []
            self._gaps: list[GapRecord] = []
        else:
            self._entries = [
                _deserialize_entry(payload) for payload in state_store.read_log_entries(log_name)
            ]
            self._gaps = [
                _deserialize_gap(payload)
                for payload in state_store.read_log_entries(self._gap_log_name)
            ]

    def record(self, entry: LiveSignalJournalEntry) -> None:
        self._entries.append(entry)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize_entry(entry))

    def record_gap(self, gap: GapRecord) -> None:
        self._gaps.append(gap)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._gap_log_name, _serialize_gap(gap))

    @property
    def entries(self) -> tuple[LiveSignalJournalEntry, ...]:
        return tuple(self._entries)

    @property
    def gaps(self) -> tuple[GapRecord, ...]:
        return tuple(self._gaps)
