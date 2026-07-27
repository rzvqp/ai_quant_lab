"""Live signal source (Phase 2A Step 5 authorization, 2026-07-26): the three pieces the CEO named --
Piesa 1 `LiveBarFeed` (bar-close-only, never a forming bar), Piesa 2 `CandidateSignalProducer` (an
injected `RecognitionRule`, shipped only with `NullRecognitionRule`, which never returns a candidate),
Piesa 3 `LiveSignalJournal` (append-only observation record).

Not wired into `execution_orchestrator` or any other caller -- this step builds the three pieces and
their end-to-end zero-candidates acceptance test only. The producer never receives, and this package
never imports, any execution-capable adapter (see `types.py`'s own module docstring for the transitive-
import reasoning). No strategy logic anywhere in this package. No order submission anywhere in this
package."""

from __future__ import annotations

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.live_signal_source.types import (
    Bar,
    BarFeedError,
    LiveCandidate,
    LiveSignalJournalEntry,
    NullRecognitionRule,
    RecognitionRule,
)

__all__ = [
    "Bar",
    "BarFeedError",
    "CandidateSignalProducer",
    "LiveBarFeed",
    "LiveCandidate",
    "LiveSignalJournal",
    "LiveSignalJournalEntry",
    "NullRecognitionRule",
    "RecognitionRule",
]
