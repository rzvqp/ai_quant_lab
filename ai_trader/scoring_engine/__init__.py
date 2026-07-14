"""Scoring Engine v1 — public package surface.

Only the documented API (``SCORING_API.md``) is exported here; internal modules
(:mod:`ai_trader.scoring_engine.pipeline`, :mod:`ai_trader.scoring_engine.components`, etc.) are
implementation details, not part of the public surface.
"""

from __future__ import annotations

from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.engine import ScoringEngine
from ai_trader.scoring_engine.evidence import StrategyManagerLike
from ai_trader.scoring_engine.exceptions import EngineNotConfiguredError, SchemaLoadError, ScoringEngineError
from ai_trader.scoring_engine.types import (
    ComponentScores,
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    NotFound,
    OpportunityScore,
    Quality,
    ReasonCode,
    Recommendation,
    Refs,
    ScoreBatch,
    ScoreConfidence,
    ScoreExplanation,
    Statistics,
    TradeContext,
    ValidationResult,
    VersionInfo,
)

__all__ = [
    "ScoringEngine",
    "ScoringConfig",
    "StrategyManagerLike",
    "ScoringEngineError",
    "EngineNotConfiguredError",
    "SchemaLoadError",
    "OpportunityScore",
    "ComponentScores",
    "ReasonCode",
    "Refs",
    "TradeContext",
    "ScoreBatch",
    "ScoreExplanation",
    "ValidationResult",
    "Statistics",
    "EngineHealth",
    "EngineOverallHealth",
    "EngineLifecycleState",
    "VersionInfo",
    "NotFound",
    "ScoreConfidence",
    "Quality",
    "Recommendation",
]
