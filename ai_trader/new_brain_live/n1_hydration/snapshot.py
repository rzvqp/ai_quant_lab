"""`N1Snapshot`/`N1SnapshotStore` -- overwrite-latest persistence for N1 hydration state, mirroring
`upstream_context.py`'s own established `SqliteStateStore.set_text`/`get_text` pattern exactly (a snapshot
represents CURRENT hydration state, never a history log).

**Bounded size, by design**: a snapshot NEVER carries more than `identity.required_bar_count()` bars --
the trailing window every vendored detector this builder actually consults. `RawAxesBuilder` itself
accumulates forever (never resets, per its own docstring), so a snapshot restricted to the trailing
window is a DISCLOSED scope boundary, not an oversight: structure/direction detection over a truncated
window can only see breaks within that window, and will correctly report `UNCERTAIN` for an older
still-active break that falls outside it -- exactly the honest "not identifiable yet" behavior `RawAxes`
already reports for a genuinely empty history (never a fabricated regime), and the CEO's own instruction
explicitly permits ("regimul nu este forțat; UNCERTAIN rămâne permis"). A full since-inception replay is
out of scope for hydration; that is what a genuine cold rebuild is for."""

from __future__ import annotations

import dataclasses
import json

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.n1_hydration.identity import N1SnapshotIdentity
from ai_trader.persistent_state.store import SqliteStateStore

_DEFAULT_SNAPSHOT_KEY = "new_brain_live.n1_hydration.snapshot"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1Snapshot:
    identity: N1SnapshotIdentity
    bars: tuple[Bar, ...]


def _serialize(snapshot: N1Snapshot) -> str:
    identity = snapshot.identity
    return json.dumps({
        "identity": {
            "n1_contract_version": identity.n1_contract_version, "router_version": identity.router_version,
            "implementation_commit": identity.implementation_commit,
            "detector_configuration_fingerprint": identity.detector_configuration_fingerprint,
            "symbol": identity.symbol, "timeframe": identity.timeframe,
            "snapshot_schema_version": identity.snapshot_schema_version,
            "first_bar_ts_open": identity.first_bar_ts_open, "last_bar_ts_close": identity.last_bar_ts_close,
            "bar_content_identity": identity.bar_content_identity, "watermark_ts_open": identity.watermark_ts_open,
        },
        "bars": [
            {
                "symbol": b.symbol, "ts_open": b.ts_open, "ts_close": b.ts_close, "open": b.open,
                "high": b.high, "low": b.low, "close": b.close, "volume": b.volume,
                "is_backfilled": b.is_backfilled,
            }
            for b in snapshot.bars
        ],
    })


def _deserialize(raw: str) -> N1Snapshot:
    data = json.loads(raw)
    identity_data = data["identity"]
    identity = N1SnapshotIdentity(
        n1_contract_version=identity_data["n1_contract_version"], router_version=identity_data["router_version"],
        implementation_commit=identity_data["implementation_commit"],
        detector_configuration_fingerprint=identity_data["detector_configuration_fingerprint"],
        symbol=identity_data["symbol"], timeframe=identity_data["timeframe"],
        snapshot_schema_version=identity_data["snapshot_schema_version"],
        first_bar_ts_open=identity_data["first_bar_ts_open"], last_bar_ts_close=identity_data["last_bar_ts_close"],
        bar_content_identity=identity_data["bar_content_identity"], watermark_ts_open=identity_data["watermark_ts_open"],
    )
    bars = tuple(
        Bar(
            symbol=b["symbol"], ts_open=b["ts_open"], ts_close=b["ts_close"], open=b["open"], high=b["high"],
            low=b["low"], close=b["close"], volume=b["volume"], is_backfilled=b["is_backfilled"],
        )
        for b in data["bars"]
    )
    return N1Snapshot(identity=identity, bars=bars)


class N1SnapshotStore:
    def __init__(self, state_store: SqliteStateStore, key: str = _DEFAULT_SNAPSHOT_KEY) -> None:
        self._state_store = state_store
        self._key = key

    def latest(self) -> N1Snapshot | None:
        raw = self._state_store.get_text(self._key)
        return None if raw is None else _deserialize(raw)

    def record(self, snapshot: N1Snapshot) -> None:
        self._state_store.set_text(self._key, _serialize(snapshot))
