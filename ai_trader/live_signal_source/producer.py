"""`CandidateSignalProducer` (Piesa 2): drives one `LiveBarFeed` poll cycle through an injected
`RecognitionRule`, journaling every bar processed (Piesa 3) and returning zero or more `LiveCandidate`s.

Never constructed with, and never imports, any execution-capable adapter -- `types.py`'s own module
docstring explains why `execution_orchestrator` itself is not imported here at all. Statically confirmed
by `tests/test_import_independence.py`. The ONLY behavior in this file is "ask the injected rule, pass
through whatever it returns, journal the bar either way" -- no strategy logic lives here (CEO
prohibition, 2026-07-26: "fara strategie scrisa in cod").
"""

from __future__ import annotations

from ai_trader.live_signal_source.bar_feed import LiveBarFeed
from ai_trader.live_signal_source.journal import LiveSignalJournal
from ai_trader.live_signal_source.types import LiveCandidate, LiveSignalJournalEntry, RecognitionRule


class CandidateSignalProducer:
    def __init__(self, feed: LiveBarFeed, rule: RecognitionRule, journal: LiveSignalJournal) -> None:
        self._feed = feed
        self._rule = rule
        self._journal = journal

    def run_once(self) -> tuple[LiveCandidate, ...]:
        """Polls the feed once, evaluates every newly closed bar through the injected rule, journals
        each bar (candidate-or-none), and returns whatever candidates were produced, oldest first."""
        candidates: list[LiveCandidate] = []
        for bar in self._feed.poll():
            candidate = self._rule.evaluate(bar)
            self._journal.record(
                LiveSignalJournalEntry(symbol=bar.symbol, as_of=bar.ts_close, candidate=candidate)
            )
            if candidate is not None:
                candidates.append(candidate)
        return tuple(candidates)
