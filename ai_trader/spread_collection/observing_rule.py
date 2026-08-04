"""`SpreadCollectingNullRecognitionRule` -- the wiring point connecting this package to the live bar
flow, mirroring `structural_observer.observing_rule.ObservingNullRecognitionRule` exactly: satisfies the
`RecognitionRule` Protocol `CandidateSignalProducer` already expects, returns `None` unconditionally (no
candidate is ever produced, no order, no cost), with the side effect of forwarding the bar to
`SpreadCollector.collect()` first. Reuses the EXISTING, already-tested `CandidateSignalProducer`/
`LiveSignalLoop` infra instead of writing a new loop -- this package needs no per-bar hooks beyond what
`RecognitionRule.evaluate()` already provides."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.spread_collection.observer import SpreadCollector


class SpreadCollectingNullRecognitionRule:
    def __init__(self, collector: SpreadCollector) -> None:
        self._collector = collector

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self._collector.collect(bar)
        return None
