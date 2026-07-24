"""Recognition Engine (live wiring, Phase 7 -- `RECOGNITION_ENGINE_PHASE7_DESIGN.md`). Wraps the
existing, already-approved `recognition_engine` (Phase 1A) batch statistics library with an authorized/
versioned pattern catalog and a live per-candidate query. Never decides risk, never sends an order,
never invents a pattern, never imports the MT5 terminal API (verified by dedicated static tests)."""

from __future__ import annotations

from ai_trader.recognition_engine_live.engine import recognize
from ai_trader.recognition_engine_live.patterns import AUTHORIZED_PATTERNS, pattern_for_id
from ai_trader.recognition_engine_live.types import (
    CalculationTraceStep,
    RecognitionCandidate,
    RecognitionPattern,
    RecognitionResult,
)

__all__ = [
    "recognize",
    "AUTHORIZED_PATTERNS",
    "pattern_for_id",
    "RecognitionCandidate",
    "RecognitionPattern",
    "RecognitionResult",
    "CalculationTraceStep",
]
