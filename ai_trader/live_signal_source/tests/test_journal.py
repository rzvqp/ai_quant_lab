"""`LiveSignalJournal` tests -- append-only, no mutator besides `record()`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import LiveCandidate, LiveSignalJournalEntry
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction


def test_starts_empty() -> None:
    journal = LiveSignalJournal()
    assert journal.entries == ()


def test_record_appends_in_order() -> None:
    journal = LiveSignalJournal()
    first = LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None)
    second = LiveSignalJournalEntry(symbol="XAUUSD", as_of=200, candidate=None)

    journal.record(first)
    journal.record(second)

    assert journal.entries == (first, second)


def test_entries_is_a_tuple_not_the_backing_list() -> None:
    """Mutating the returned value must never affect the journal's own state -- confirms `entries` is
    a genuine snapshot, not a reference to internal mutable state."""
    journal = LiveSignalJournal()
    journal.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None))

    snapshot = journal.entries
    assert isinstance(snapshot, tuple)

    journal.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=200, candidate=None))
    assert len(snapshot) == 1  # the earlier snapshot is unaffected by the later record()
    assert len(journal.entries) == 2


def test_has_no_remove_or_clear_method() -> None:
    """Append-only by construction, not merely by convention."""
    journal = LiveSignalJournal()
    assert not hasattr(journal, "remove")
    assert not hasattr(journal, "clear")
    assert not hasattr(journal, "delete")


# -- Mandate 2 (2026-07-27): journal persistence -- a restart must not empty the observation history --


def test_history_survives_a_simulated_restart(tmp_path: Path) -> None:
    """The core acceptance proof: a brand-new `LiveSignalJournal` instance, given the SAME
    `SqliteStateStore`, must see every entry a prior instance recorded -- not start empty."""
    store = SqliteStateStore(tmp_path / "state.db")
    journal_before_restart = LiveSignalJournal(state_store=store)
    journal_before_restart.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None))
    journal_before_restart.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=200, candidate=None))

    # Simulated restart: a brand-new LiveSignalJournal object, same store.
    journal_after_restart = LiveSignalJournal(state_store=store)

    assert len(journal_after_restart.entries) == 2
    assert journal_after_restart.entries[0].as_of == 100
    assert journal_after_restart.entries[1].as_of == 200


def test_a_candidate_round_trips_through_persistence() -> None:
    """The richer row shape (a real candidate, not just `None`) must survive serialization intact --
    every field, including the `Direction` enum."""
    store = SqliteStateStore(":memory:")
    candidate = LiveCandidate(
        strategy_id="S1", symbol="XAUUSD", direction=Direction.LONG, entry=2000.0, stop=1995.0,
        target=2010.0, session="LONDON", magic_number=42, comment="test", as_of=500,
    )
    journal_before_restart = LiveSignalJournal(state_store=store)
    journal_before_restart.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=500, candidate=candidate))

    journal_after_restart = LiveSignalJournal(state_store=store)
    recovered = journal_after_restart.entries[0].candidate

    assert recovered == candidate


def test_new_records_after_restart_append_after_the_recovered_history(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    journal_before_restart = LiveSignalJournal(state_store=store)
    journal_before_restart.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None))

    journal_after_restart = LiveSignalJournal(state_store=store)
    journal_after_restart.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=200, candidate=None))

    assert [e.as_of for e in journal_after_restart.entries] == [100, 200]


def test_two_log_names_on_the_same_store_are_independent(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    journal_a = LiveSignalJournal(state_store=store, log_name="strategy_a")
    journal_b = LiveSignalJournal(state_store=store, log_name="strategy_b")

    journal_a.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None))

    assert len(journal_a.entries) == 1
    assert len(journal_b.entries) == 0


def test_without_a_state_store_nothing_is_persisted() -> None:
    """No `state_store` argument at all -- the exact prior, in-memory-only behavior -- remains the
    default; every other test in this file already proves this, this test names it explicitly."""
    journal = LiveSignalJournal()
    journal.record(LiveSignalJournalEntry(symbol="XAUUSD", as_of=100, candidate=None))
    assert len(journal.entries) == 1
