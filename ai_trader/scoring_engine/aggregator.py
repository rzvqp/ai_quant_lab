"""The Aggregator (``SCORING_ENGINE_ARCHITECTURE.md`` §5): the fixed 0-100 formula
(``SCORING_MODEL.md`` §5) plus the derived-field banding (§6). Pure arithmetic — no signal/evidence
objects touched here, only the already-computed numeric components, keeping this module trivially
testable and obviously deterministic.
"""

from __future__ import annotations

import math

from ai_trader.scoring_engine.config import ConfidenceBands, QualityBands, RecommendationBands
from ai_trader.scoring_engine.components import clamp
from ai_trader.scoring_engine.types import ACTIONABLE_STATES, READY_STATES, Quality, Recommendation, ScoreConfidence
from ai_trader.signal_engine.types import SignalState


def round_half_up(value: float) -> int:
    """``SCORING_MODEL.md`` §5: "deterministic rounding: half-up". Python's builtin ``round()`` uses
    round-half-to-even (banker's rounding) -- NOT half-up (``round(2.5) == 2``, not 3) -- so it cannot
    be used here without silently violating the spec. ``value`` is always in [0, 100] (a product of
    two [0,1] factors times 100), so a plain ``floor(value + 0.5)`` is correct and exact."""
    return math.floor(value + 0.5)


def aggregate(base_quality: float, risk_penalty: float, conflict_penalty: float) -> tuple[float, int]:
    """``SCORING_MODEL.md`` §5: ``penalty_factor = (1-risk_penalty)*(1-conflict_penalty)``;
    ``total_score = round(100 * base_quality * penalty_factor)``. Returns ``(penalty_factor,
    total_score)``."""
    penalty_factor = clamp((1.0 - risk_penalty) * (1.0 - conflict_penalty), 0.0, 1.0)
    total_score = round_half_up(100.0 * base_quality * penalty_factor)
    return penalty_factor, max(0, min(100, total_score))


def confidence_band(historical_confidence: float, bands: ConfidenceBands) -> ScoreConfidence:
    """``SCORING_MODEL.md`` §6: ``confidence`` from the ``historical_confidence`` tier."""
    if historical_confidence <= 0.0:
        return ScoreConfidence.NONE
    if historical_confidence < bands.low_min:
        return ScoreConfidence.VERY_LOW
    if historical_confidence < bands.medium_min:
        return ScoreConfidence.LOW
    if historical_confidence < bands.high_min:
        return ScoreConfidence.MEDIUM
    return ScoreConfidence.HIGH


def quality_band(total_score: int, bands: QualityBands) -> Quality:
    """``SCORING_MODEL.md`` §6, exact: PREMIUM >=80, STRONG 65-79, MODERATE 45-64, WEAK 25-44, POOR <25."""
    if total_score >= bands.premium_min:
        return Quality.PREMIUM
    if total_score >= bands.strong_min:
        return Quality.STRONG
    if total_score >= bands.moderate_min:
        return Quality.MODERATE
    if total_score >= bands.weak_min:
        return Quality.WEAK
    return Quality.POOR


def recommendation_for(state: SignalState, total_score: int, bands: RecommendationBands) -> Recommendation:
    """``SCORING_MODEL.md`` §6. Only called for non-terminal (non-SKIPPED/SCORE_INVALID) signals --
    those two terminal cases set their ``recommendation`` directly (``SKIP``/``INVALID``) without
    reaching aggregation at all (``pipeline.py``'s own module docstring)."""
    if state in ACTIONABLE_STATES:
        if total_score >= bands.strong_min:
            return Recommendation.STRONG_OPPORTUNITY
        if total_score >= bands.moderate_min:
            return Recommendation.MODERATE_OPPORTUNITY
        if total_score >= bands.weak_min:
            return Recommendation.WEAK_OPPORTUNITY
        return Recommendation.SKIP  # actionable but too low a score to call an "opportunity"
    if state in READY_STATES or state is SignalState.WAIT_CONFIRMATION:
        # SCORING_MODEL.md's prose says "WATCH/ARM" but SCORING_SCHEMA.json's own recommendation
        # enum has no "ARM" value -- the schema is the binding, machine-validated contract (the same
        # precedent set by every prior AI Trader module), so both READY and WAIT_CONFIRMATION map to
        # the one schema-valid non-actionable-but-live tier, WATCH. Flagged in the validation report.
        return Recommendation.WATCH
    return Recommendation.SKIP
