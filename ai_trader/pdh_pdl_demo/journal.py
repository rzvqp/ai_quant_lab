"""`PdhPdlAuditJournal` -- append-only persistence for `PdhPdlAuditEntry`, same `SqliteStateStore`
engine/convention already established (`live_signal_source.journal.LiveSignalJournal`,
`structural_observer.journal.StructuralObservationLog`)."""

from __future__ import annotations

import json

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry, PdhPdlAuditKind

_DEFAULT_LOG_NAME = "pdh_pdl_demo.audit"


def _serialize(entry: PdhPdlAuditEntry) -> str:
    return json.dumps({
        "symbol": entry.symbol, "as_of": entry.as_of, "kind": entry.kind.value, "detail": entry.detail,
    })


def _deserialize(payload: str) -> PdhPdlAuditEntry:
    data = json.loads(payload)
    return PdhPdlAuditEntry(
        symbol=data["symbol"], as_of=data["as_of"], kind=PdhPdlAuditKind(data["kind"]), detail=data["detail"],
    )


class PdhPdlAuditJournal:
    def __init__(self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[PdhPdlAuditEntry] = []
        else:
            self._entries = [_deserialize(p) for p in state_store.read_log_entries(log_name)]

    def record(self, entry: PdhPdlAuditEntry) -> None:
        self._entries.append(entry)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(entry))

    @property
    def entries(self) -> tuple[PdhPdlAuditEntry, ...]:
        return tuple(self._entries)
