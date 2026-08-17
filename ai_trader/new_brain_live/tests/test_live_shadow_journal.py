"""`LiveShadowJournal` tests -- classification, durability across restart, no P&L field."""

from __future__ import annotations

import dataclasses
from pathlib import Path

from ai_trader.new_brain_live.live_shadow_journal import LiveShadowCategory, LiveShadowJournal, LiveShadowRecord
from ai_trader.persistent_state.store import SqliteStateStore


def _record(category: LiveShadowCategory, trace_id: str = "t-1") -> LiveShadowRecord:
    return LiveShadowRecord(
        category=category, trace_id=trace_id, market_event_id="XAUUSD:M15:1700000000",
        strategy_id="trend_pullback", as_of=1_700_000_000, terminal_reason_code="MISSING_LEVEL_INPUT",
        decision=None,
    )


def test_record_and_read_back(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    journal = LiveShadowJournal(store)
    journal.record(_record(LiveShadowCategory.LIVE_SHADOW_NO_TRADE))
    assert len(journal.entries) == 1
    assert journal.entries[0].category is LiveShadowCategory.LIVE_SHADOW_NO_TRADE
    store.close()


def test_durable_across_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store_before = SqliteStateStore(db_path)
    journal_before = LiveShadowJournal(store_before)
    journal_before.record(_record(LiveShadowCategory.LIVE_SHADOW_CANDIDATE, trace_id="t-restart"))
    store_before.close()

    store_after = SqliteStateStore(db_path)
    journal_after = LiveShadowJournal(store_after)
    assert len(journal_after.entries) == 1
    assert journal_after.entries[0].trace_id == "t-restart"
    store_after.close()


def test_counts_by_category(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    journal = LiveShadowJournal(store)
    journal.record(_record(LiveShadowCategory.LIVE_SHADOW_NO_TRADE, "a"))
    journal.record(_record(LiveShadowCategory.LIVE_SHADOW_NO_TRADE, "b"))
    journal.record(_record(LiveShadowCategory.LIVE_SHADOW_CANDIDATE, "c"))
    counts = journal.counts_by_category()
    assert counts["LIVE_SHADOW_NO_TRADE"] == 2
    assert counts["LIVE_SHADOW_CANDIDATE"] == 1
    assert counts["LIVE_SHADOW_BLOCKED_AT_BROKER"] == 0
    store.close()


def test_blocked_at_broker_record_carries_broker_evidence(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    journal = LiveShadowJournal(store)
    record = LiveShadowRecord(
        category=LiveShadowCategory.LIVE_SHADOW_BLOCKED_AT_BROKER, trace_id="t-blocked",
        market_event_id="XAUUSD:M15:1700000000", strategy_id="trend_pullback", as_of=1_700_000_000,
        terminal_reason_code="TRADE_VALIDATED_EDGE", decision="TRADE", reached_broker_gate=True,
        broker_blocked=True, order_send_calls=0, orders_created=0, positions_created=0,
    )
    journal.record(record)
    read_back = journal.entries[0]
    assert read_back.reached_broker_gate is True
    assert read_back.broker_blocked is True
    assert read_back.order_send_calls == 0
    store.close()


def test_record_carries_no_pnl_field() -> None:
    """Structural, not conventional -- `LiveShadowRecord` has no field that could be misread as
    profit/edge (CEO's own explicit instruction, section 6)."""
    field_names = {f.name for f in dataclasses.fields(LiveShadowRecord)}
    forbidden = {"pnl", "profit", "edge", "expected_value", "return", "roi"}
    assert not (field_names & forbidden)
