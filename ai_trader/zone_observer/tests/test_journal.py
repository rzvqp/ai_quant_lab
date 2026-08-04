"""`ZoneObservationLog` tests -- persistence round-trip, same convention as every other journal."""

from __future__ import annotations

from pathlib import Path

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.zone_observer.journal import ZoneObservationLog
from ai_trader.zone_observer.types import ZoneEventKind, ZoneObservation


def _observation(as_of: int = 1_705_356_000, kind: ZoneEventKind = ZoneEventKind.SESSION_LEVEL_FORMED) -> ZoneObservation:
    return ZoneObservation(
        symbol="XAUUSD", as_of=as_of, kind=kind,
        detail={"level_kind": "session_high", "price": 4055.0, "session_label": "london"},
    )


def test_record_and_read_back_in_memory() -> None:
    journal = ZoneObservationLog()
    obs = _observation()
    journal.record(obs)
    assert journal.entries == (obs,)


def test_persists_across_a_new_store_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "zone.db"
    store1 = SqliteStateStore(db_path)
    ZoneObservationLog(store1).record(_observation())
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        journal2 = ZoneObservationLog(store2)
        assert len(journal2.entries) == 1
        assert journal2.entries[0].kind is ZoneEventKind.SESSION_LEVEL_FORMED
        assert journal2.entries[0].detail["level_kind"] == "session_high"
    finally:
        store2.close()


def test_every_event_kind_round_trips(tmp_path: Path) -> None:
    db_path = tmp_path / "zone.db"
    store = SqliteStateStore(db_path)
    try:
        journal = ZoneObservationLog(store)
        for kind in ZoneEventKind:
            journal.record(_observation(kind=kind))
        assert [e.kind for e in journal.entries] == list(ZoneEventKind)
    finally:
        store.close()


def test_multiple_entries_append_in_order() -> None:
    journal = ZoneObservationLog()
    journal.record(_observation(as_of=1))
    journal.record(_observation(as_of=2))
    journal.record(_observation(as_of=3))
    assert [e.as_of for e in journal.entries] == [1, 2, 3]
