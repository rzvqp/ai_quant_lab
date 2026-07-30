"""`ObservingNullRecognitionRule` -- the actual wiring point connecting this package to the live bar
flow, per the CEO's "Dupa punte, cableaza ca OBSERVATOR" instruction.

**Why the wiring point is `RecognitionRule`, not `producer.py`**: `CandidateSignalProducer.run_once()`
calls `self._rule.evaluate(bar)` for every newly closed bar exactly once (Piesa 2's own design -- the
recognition rule is already an INJECTED dependency, precisely so alternate implementations can be
substituted without touching the producer itself). Modifying `producer.py` to add a second, parallel
observer parameter was considered and rejected: `live_signal_source` currently has zero dependency on
the vendor submodule, and a module-level import of `structural_observer` from `producer.py` would force
that dependency onto every user of `CandidateSignalProducer` at IMPORT time (not merely when an observer
is actually supplied) -- a real increase in that already-audited, execution-independent package's
fragility surface for no behavioral gain, since the exact same effect is achievable through the seam
that already exists.

**Behavior**: identical to `NullRecognitionRule` from the producer's own point of view -- returns `None`
unconditionally, for every bar, no exceptions (CEO: "producatorul ramane cu NullRecognitionRule"). The
ONLY difference is the side effect of forwarding the bar to `StructuralObserver.observe()` first. No
candidate is ever produced by this class; no strategy logic lives here.

**Not yet activated by any entrypoint**: this codebase has no real deployment/entrypoint script that
constructs `CandidateSignalProducer`/`LiveSignalLoop` together for an actual live run -- only tests do,
for either class, today. Substituting this class in place of a bare `NullRecognitionRule()` at whatever
future entrypoint eventually constructs the live system is what would make structural observation
actually run against real bars; that entrypoint does not exist yet as a decision this mandate made, so
this file makes the wiring *possible*, not yet *active*."""

from __future__ import annotations

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.structural_observer.observer import StructuralObserver


class ObservingNullRecognitionRule:
    """Satisfies the `RecognitionRule` Protocol (structural typing -- no inheritance required, matching
    this codebase's established convention for injected real/fake/null implementations)."""

    def __init__(self, observer: StructuralObserver) -> None:
        self._observer = observer

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self._observer.observe(bar)
        return None
