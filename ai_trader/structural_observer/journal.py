"""`StructuralObservationLog` -- append-only persistence for `StructuralObservation`, same
`SqliteStateStore` engine and same convention as `live_signal_source.journal.LiveSignalJournal`
(serialize to JSON, one append-only log per instance, `entries` loaded in full at construction so a
restart sees the complete history)."""

from __future__ import annotations

import json

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.types import StructuralEventKind, StructuralObservation

_DEFAULT_LOG_NAME = "structural_observer.observations"


def _serialize(observation: StructuralObservation) -> str:
    return json.dumps({
        "symbol": observation.symbol, "as_of": observation.as_of,
        "kind": observation.kind.value, "detail": observation.detail,
    })


def _deserialize(payload: str) -> StructuralObservation:
    data = json.loads(payload)
    return StructuralObservation(
        symbol=data["symbol"], as_of=data["as_of"],
        kind=StructuralEventKind(data["kind"]), detail=data["detail"],
    )


class StructuralObservationLog:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[StructuralObservation] = []
        else:
            self._entries = [
                _deserialize(payload) for payload in state_store.read_log_entries(log_name)
            ]

    def record(self, observation: StructuralObservation) -> None:
        self._entries.append(observation)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(observation))

    @property
    def entries(self) -> tuple[StructuralObservation, ...]:
        return tuple(self._entries)
