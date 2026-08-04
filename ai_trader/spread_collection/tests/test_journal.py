"""`SpreadObservationLog` tests -- persistence round-trip, same convention as every other journal in
this project."""

from __future__ import annotations

from pathlib import Path

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.journal import SpreadObservationLog
from ai_trader.spread_collection.types import SpreadObservation


def _observation(as_of: int = 1_705_356_000) -> SpreadObservation:
    return SpreadObservation(
        symbol="XAUUSD", as_of=as_of, bid=4054.55, ask=4054.62, spread=0.07, session="london",
        atr=2.3, day_boundary_label=1_705_356_000, is_level_touch=True, touch_level_kind="pdh",
    )


def test_record_and_read_back_in_memory() -> None:
    journal = SpreadObservationLog()
    obs = _observation()
    journal.record(obs)
    assert journal.entries == (obs,)


def test_persists_across_a_new_store_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "spread.db"
    store1 = SqliteStateStore(db_path)
    SpreadObservationLog(store1).record(_observation())
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        journal2 = SpreadObservationLog(store2)
        assert len(journal2.entries) == 1
        assert journal2.entries[0].symbol == "XAUUSD"
        assert journal2.entries[0].is_level_touch is True
        assert journal2.entries[0].touch_level_kind == "pdh"
    finally:
        store2.close()


def test_none_atr_and_none_touch_kind_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "spread.db"
    obs = SpreadObservation(
        symbol="XAUUSD", as_of=1_705_356_000, bid=4054.55, ask=4054.62, spread=0.07, session="asia",
        atr=None, day_boundary_label=1_705_356_000, is_level_touch=False, touch_level_kind=None,
    )
    store1 = SqliteStateStore(db_path)
    SpreadObservationLog(store1).record(obs)
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        journal2 = SpreadObservationLog(store2)
        assert journal2.entries[0].atr is None
        assert journal2.entries[0].touch_level_kind is None
    finally:
        store2.close()


def test_multiple_entries_append_in_order(tmp_path: Path) -> None:
    db_path = tmp_path / "spread.db"
    store = SqliteStateStore(db_path)
    try:
        journal = SpreadObservationLog(store)
        journal.record(_observation(as_of=1))
        journal.record(_observation(as_of=2))
        journal.record(_observation(as_of=3))
        assert [e.as_of for e in journal.entries] == [1, 2, 3]
    finally:
        store.close()
