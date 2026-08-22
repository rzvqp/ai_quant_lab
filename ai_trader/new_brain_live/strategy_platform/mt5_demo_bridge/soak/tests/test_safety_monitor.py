from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.safety_monitor import (
    ACCOUNT_NOT_DEMO,
    RISK_EXCEEDS_5_PERCENT,
    SafetyMonitor,
)
from ai_trader.persistent_state.store import SqliteStateStore


def _monitor(tmp_path: Path, name: str = "safety.db") -> tuple[SafetyMonitor, SqliteStateStore]:
    store = SqliteStateStore(tmp_path / name)
    return SafetyMonitor(store), store


def test_starts_unblocked(tmp_path: Path) -> None:
    monitor, store = _monitor(tmp_path)
    assert monitor.is_blocked() is False
    assert monitor.current_block() is None
    store.close()


def test_trip_blocks_and_records_condition(tmp_path: Path) -> None:
    monitor, store = _monitor(tmp_path)
    monitor.trip(ACCOUNT_NOT_DEMO, "account switched to REAL", at=100)
    assert monitor.is_blocked() is True
    block = monitor.current_block()
    assert block is not None
    assert block.condition == ACCOUNT_NOT_DEMO
    store.close()


def test_unknown_condition_rejected(tmp_path: Path) -> None:
    monitor, store = _monitor(tmp_path)
    with pytest.raises(ValueError):
        monitor.trip("NOT_A_REAL_CONDITION", "x", at=0)
    store.close()


def test_second_trip_does_not_overwrite_first(tmp_path: Path) -> None:
    monitor, store = _monitor(tmp_path)
    monitor.trip(ACCOUNT_NOT_DEMO, "first", at=100)
    monitor.trip(RISK_EXCEEDS_5_PERCENT, "second", at=200)
    block = monitor.current_block()
    assert block is not None
    assert block.condition == ACCOUNT_NOT_DEMO  # the first trip is the one of record
    store.close()


def test_clear_unblocks_and_persists(tmp_path: Path) -> None:
    monitor, store = _monitor(tmp_path)
    monitor.trip(ACCOUNT_NOT_DEMO, "x", at=100)
    assert monitor.is_blocked() is True
    monitor.clear(note="investigated, false alarm", at=200)
    assert monitor.is_blocked() is False
    store.close()


def test_block_state_survives_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "restart.db"
    store1 = SqliteStateStore(db_path)
    SafetyMonitor(store1).trip(ACCOUNT_NOT_DEMO, "x", at=100)
    store1.close()

    store2 = SqliteStateStore(db_path)
    monitor2 = SafetyMonitor(store2)
    assert monitor2.is_blocked() is True
    store2.close()
