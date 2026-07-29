"""Mandate 4 (2026-07-28), Item #7: the unattended loop. Orchestrates `LiveBarFeed`/
`CandidateSignalProducer`/`LiveSignalJournal` (Step 5) and the persisted circuit breaker
(Mandate 3, Element 2) at interval-based scheduling -- the last infrastructure piece before shadow mode.

Every underlying capability (restart-correct watermark, gap detection/journaling, circuit-state
persistence) was already independently built and proven in Mandates 2 and 3; this package adds only
scheduling and circuit-breaker consultation. No real orders. No execution adapter. The producer this
loop drives is still constructed with `NullRecognitionRule` -- nothing here changes what candidates get
produced, only whether/how often the pipeline runs."""

from __future__ import annotations

from ai_trader.live_loop.loop import LiveSignalLoop

__all__ = ["LiveSignalLoop"]
