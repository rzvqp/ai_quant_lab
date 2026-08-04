"""`ZoneObservationLog` -- append-only persistence for `ZoneObservation`, same `SqliteStateStore`
engine and convention as `structural_observer.journal.StructuralObservationLog`."""

from __future__ import annotations

import json

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.zone_observer.types import ZoneEventKind, ZoneObservation

_DEFAULT_LOG_NAME = "zone_observer.observations"


def _serialize(observation: ZoneObservation) -> str:
    return json.dumps({
        "symbol": observation.symbol, "as_of": observation.as_of,
        "kind": observation.kind.value, "detail": observation.detail,
    })


def _deserialize(payload: str) -> ZoneObservation:
    data = json.loads(payload)
    return ZoneObservation(
        symbol=data["symbol"], as_of=data["as_of"],
        kind=ZoneEventKind(data["kind"]), detail=data["detail"],
    )


class ZoneObservationLog:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[ZoneObservation] = []
        else:
            self._entries = [
                _deserialize(payload) for payload in state_store.read_log_entries(log_name)
            ]

    def record(self, observation: ZoneObservation) -> None:
        self._entries.append(observation)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(observation))

    @property
    def entries(self) -> tuple[ZoneObservation, ...]:
        return tuple(self._entries)
