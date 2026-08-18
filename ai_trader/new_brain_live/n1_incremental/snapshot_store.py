"""Overwrite-latest persistence for the incremental N1 snapshot -- same `SqliteStateStore.set_text`/
`get_text` pattern already established (`heartbeat.py`, `dual_clock.upstream_context.py`,
`n1_hydration.snapshot.py`). The blob itself is opaque (pickled inside the isolated worker, see
`worker_script.py`'s own docstring for why) -- this store never parses it, only round-trips it."""

from __future__ import annotations

import dataclasses
import json

from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_KEY = "new_brain_live.n1_incremental.snapshot"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class StoredN1IncrementalSnapshot:
    snapshot_blob: str
    identity_fingerprint: str
    symbol: str
    timeframe: str
    last_bar_ts_open: int
    last_bar_ts_close: int


class N1IncrementalSnapshotStore:
    def __init__(self, state_store: SqliteStateStore, key: str = _DEFAULT_KEY) -> None:
        self._state_store = state_store
        self._key = key

    def latest(self) -> StoredN1IncrementalSnapshot | None:
        raw = self._state_store.get_text(self._key)
        if raw is None:
            return None
        data = json.loads(raw)
        return StoredN1IncrementalSnapshot(
            snapshot_blob=data["snapshot_blob"], identity_fingerprint=data["identity_fingerprint"],
            symbol=data["symbol"], timeframe=data["timeframe"], last_bar_ts_open=data["last_bar_ts_open"],
            last_bar_ts_close=data["last_bar_ts_close"],
        )

    def record(self, snapshot: StoredN1IncrementalSnapshot) -> None:
        self._state_store.set_text(self._key, json.dumps({
            "snapshot_blob": snapshot.snapshot_blob, "identity_fingerprint": snapshot.identity_fingerprint,
            "symbol": snapshot.symbol, "timeframe": snapshot.timeframe,
            "last_bar_ts_open": snapshot.last_bar_ts_open, "last_bar_ts_close": snapshot.last_bar_ts_close,
        }))
