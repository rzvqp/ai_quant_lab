"""`SqliteStateStore` tests -- including the core proof this whole mandate rests on: state written by
one store instance is read back correctly by a SEPARATE instance opened on the same file, simulating a
process restart without actually restarting a process."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.persistent_state.types import PersistenceError


def test_get_value_returns_none_when_key_absent(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    assert store.get_value("missing") is None


def test_set_then_get_value_round_trips(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    store.set_value("equity_hwm", 12_345.5)
    assert store.get_value("equity_hwm") == 12_345.5


def test_set_value_overwrites_existing_key(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    store.set_value("k", 1.0)
    store.set_value("k", 2.0)
    assert store.get_value("k") == 2.0


def test_value_persists_across_separate_store_instances_same_file(tmp_path: Path) -> None:
    """The core restart-determinism proof for the key-value side: a brand-new `SqliteStateStore`
    object, pointed at the same file, sees exactly what the previous one wrote -- nothing reset."""
    db_path = tmp_path / "state.db"
    first = SqliteStateStore(db_path)
    first.set_value("watermark:XAUUSD:M15", 1_700_000_000.0)
    first.close()

    second = SqliteStateStore(db_path)
    assert second.get_value("watermark:XAUUSD:M15") == 1_700_000_000.0


def test_append_log_entry_and_read_back_in_order(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    store.append_log_entry("journal", "first")
    store.append_log_entry("journal", "second")
    store.append_log_entry("journal", "third")

    assert store.read_log_entries("journal") == ("first", "second", "third")


def test_log_entries_persist_across_separate_store_instances_same_file(tmp_path: Path) -> None:
    """The core restart-determinism proof for the append-log side: no entries lost, no entries
    duplicated, when a fresh store instance reopens the same file."""
    db_path = tmp_path / "state.db"
    first = SqliteStateStore(db_path)
    first.append_log_entry("journal", "a")
    first.append_log_entry("journal", "b")
    first.close()

    second = SqliteStateStore(db_path)
    assert second.read_log_entries("journal") == ("a", "b")

    second.append_log_entry("journal", "c")
    assert second.read_log_entries("journal") == ("a", "b", "c")


def test_two_log_names_are_independent(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    store.append_log_entry("journal_a", "x")
    store.append_log_entry("journal_b", "y")

    assert store.read_log_entries("journal_a") == ("x",)
    assert store.read_log_entries("journal_b") == ("y",)


def test_read_log_entries_empty_for_unknown_log_name(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    assert store.read_log_entries("never_written") == ()


def test_verify_integrity_true_for_a_fresh_store(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    assert store.verify_integrity() is True


def test_raises_persistence_error_on_a_corrupt_file(tmp_path: Path) -> None:
    corrupt_path = tmp_path / "corrupt.db"
    corrupt_path.write_bytes(b"this is not a sqlite database file, just garbage bytes")

    with pytest.raises(PersistenceError):
        SqliteStateStore(corrupt_path)
