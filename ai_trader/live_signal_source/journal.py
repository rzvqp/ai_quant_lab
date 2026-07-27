"""`LiveSignalJournal` (Piesa 3): the append-only observation record for the live signal pipeline. See
`types.py`'s own docstring (`LiveSignalJournalEntry`) for why none of `shadow_evidence.types`'s six
record dataclasses were reused verbatim, and what "reuse" concretely means here instead.

Append-only by construction: the only mutator is `record()` -- there is no remove/clear/replace method
anywhere on this class, and `entries` is exposed as an immutable `tuple`, never the backing list.

**Scope, disclosed**: in-memory only this step. No disk/database persistence was authorized or built --
a restarted process starts with an empty journal. Nothing in the CEO's Step 5 specification named
persistence as a requirement (unlike Step 1's suspension state, which explicitly needed to survive a
restart); if the CEO wants that guarantee, it is a separate, not-yet-authorized decision.
"""

from __future__ import annotations

from ai_trader.live_signal_source.types import LiveSignalJournalEntry


class LiveSignalJournal:
    def __init__(self) -> None:
        self._entries: list[LiveSignalJournalEntry] = []

    def record(self, entry: LiveSignalJournalEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> tuple[LiveSignalJournalEntry, ...]:
        return tuple(self._entries)
