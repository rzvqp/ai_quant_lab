"""`LiveSignalJournal` tests -- append-only, no mutator besides `record()`."""

from __future__ import annotations

from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import LiveSignalJournalEntry


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
