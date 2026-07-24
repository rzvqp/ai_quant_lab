"""Confidence Engine (Phase 8 -- `CONFIDENCE_ENGINE_PHASE8_DESIGN.md`). Combines Context Engine's
`ContextConfidence` and Recognition Engine's `ConditionalStatistics` into a disclosed A/B/C/D grade with
configurable thresholds. Grades A/B may become eligible for risk evaluation -- never automatically
executable: this package never imports `execution_engine`/`order_manager` and never constructs or
submits anything (verified by dedicated static tests)."""

from __future__ import annotations

from ai_trader.confidence_engine.engine import assess_confidence
from ai_trader.confidence_engine.types import (
    GRADE_TO_QUALITY,
    CalculationTraceStep,
    ConfidenceAssessment,
    ConfidenceEngineConfig,
    Grade,
    GradeBands,
    ScoreComponents,
)

__all__ = [
    "assess_confidence",
    "Grade",
    "GradeBands",
    "ConfidenceEngineConfig",
    "ScoreComponents",
    "ConfidenceAssessment",
    "CalculationTraceStep",
    "GRADE_TO_QUALITY",
]
