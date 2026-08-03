"""Mandate 4 (2026-07-30): the actual live entrypoint -- CEO directive "Porneste observarea live. Fara
ordine." Wires the REAL `RealMT5Gateway` (read-only by construction -- no order-capable method exists on
`MT5Gateway`/`RealMT5Gateway` at all) to the already-built, already-tested live pipeline: `LiveBarFeed` →
`ObservingNullRecognitionRule` (forwards every bar to `StructuralObserver`, always returns `None`) →
`CandidateSignalProducer` → `LiveSignalLoop`. Every persisted state (bar-feed watermark, signal journal,
structural observation journal) shares ONE `SqliteStateStore`, matching Mandate 2's own "one persistence
solution" rule.

Zero new detection logic. Zero new trading capability. `NullRecognitionRule`'s replacement
(`ObservingNullRecognitionRule`) still returns `None` unconditionally for every bar -- the only change from
Step 3 is that this package actually CONSTRUCTS the pipeline against a real gateway and calls
`run_forever()`, instead of only proving the wiring correct in tests."""

from __future__ import annotations

from ai_trader.live_observation.entrypoint import build_loop

__all__ = ["build_loop"]
