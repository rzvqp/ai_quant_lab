"""Mandate 4 (2026-07-29): connects the vendored, frozen structural detectors
(`market_structure`/`imbalance_mechanics`/`market_state`/`order_flow`, pinned via git submodule at
`vendor/alpha_automation_detectors`) to an append-only journal, as a pure OBSERVER. Never produces a
signal, never evaluates -- see `observer.py`'s own module docstring for the full specification.

`liquidity_mechanics` and `institutional_levels` remain deliberately NOT wired -- both need a day/week
boundary derivation that exists only as an offline batch script, not a live-callable function (Step 2's
own Finding 3); not authorized to invent one here."""

from __future__ import annotations

from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.observer import StructuralObserver
from ai_trader.structural_observer.observing_rule import ObservingNullRecognitionRule
from ai_trader.structural_observer.types import StructuralEventKind, StructuralObservation

__all__ = [
    "ObservingNullRecognitionRule",
    "StructuralEventKind",
    "StructuralObservation",
    "StructuralObservationLog",
    "StructuralObserver",
]
