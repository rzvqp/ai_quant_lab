"""`ZoneObservingNullRecognitionRule` -- exact structural mirror of
`structural_observer.observing_rule.ObservingNullRecognitionRule`: satisfies the `RecognitionRule`
Protocol, always returns `None`, forwards each bar to `ZoneObserver.observe()` as a side effect. No
candidate is ever produced; no strategy logic lives here."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.zone_observer.observer import ZoneObserver


class ZoneObservingNullRecognitionRule:
    def __init__(self, observer: ZoneObserver) -> None:
        self._observer = observer

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self._observer.observe(bar)
        return None
