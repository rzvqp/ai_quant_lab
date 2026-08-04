"""`SpreadObservationLog` -- append-only persistence for `SpreadObservation`, same `SqliteStateStore`
engine and convention as every other journal in this project (`live_signal_source.journal.LiveSignalJournal`,
`structural_observer.journal.StructuralObservationLog`, `pdh_pdl_demo.journal.PdhPdlAuditJournal`)."""

from __future__ import annotations

import json

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.types import SpreadObservation

_DEFAULT_LOG_NAME = "spread_collection.observations"


def _serialize(observation: SpreadObservation) -> str:
    return json.dumps({
        "symbol": observation.symbol, "as_of": observation.as_of, "bid": observation.bid,
        "ask": observation.ask, "spread": observation.spread, "session": observation.session,
        "atr": observation.atr, "day_boundary_label": observation.day_boundary_label,
        "is_level_touch": observation.is_level_touch, "touch_level_kind": observation.touch_level_kind,
    })


def _deserialize(payload: str) -> SpreadObservation:
    data = json.loads(payload)
    return SpreadObservation(
        symbol=data["symbol"], as_of=data["as_of"], bid=data["bid"], ask=data["ask"],
        spread=data["spread"], session=data["session"], atr=data["atr"],
        day_boundary_label=data["day_boundary_label"], is_level_touch=data["is_level_touch"],
        touch_level_kind=data["touch_level_kind"],
    )


class SpreadObservationLog:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[SpreadObservation] = []
        else:
            self._entries = [
                _deserialize(payload) for payload in state_store.read_log_entries(log_name)
            ]

    def record(self, observation: SpreadObservation) -> None:
        self._entries.append(observation)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(observation))

    @property
    def entries(self) -> tuple[SpreadObservation, ...]:
        return tuple(self._entries)
