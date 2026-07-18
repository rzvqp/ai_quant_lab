"""Unit tests for :mod:`ai_trader.market_intelligence.confidence`."""

from __future__ import annotations

from ai_trader.market_intelligence.confidence import compute_context_confidence
from ai_trader.market_intelligence.types import (
    AgreementLevel, MultiTimeframeAgreement, VolatilityReading, VolatilityRegime,
)


def _agreement(score: float | None) -> MultiTimeframeAgreement:
    return MultiTimeframeAgreement(directions_by_timeframe={}, agreement_score=score, level=AgreementLevel.UNKNOWN)


def _volatility(regime: VolatilityRegime) -> VolatilityReading:
    return VolatilityReading(atr=1.0, atr_ma=1.0, atr_ratio=1.0, volatility_rank=0.5, regime=regime)


def test_confidence_perfect_conditions() -> None:
    result = compute_context_confidence("OK", _agreement(1.0), _volatility(VolatilityRegime.NORMAL))
    assert result.score == 1.0
    assert result.data_quality_ok is True
    assert result.volatility_penalty == 0.0


def test_confidence_degraded_data_quality_lowers_score() -> None:
    result = compute_context_confidence("STALE", _agreement(1.0), _volatility(VolatilityRegime.NORMAL))
    assert result.data_quality_ok is False
    assert result.score is not None and result.score < 1.0


def test_confidence_extreme_volatility_applies_penalty() -> None:
    result = compute_context_confidence("OK", _agreement(1.0), _volatility(VolatilityRegime.EXTREME))
    assert result.volatility_penalty == 0.5
    assert result.score is not None and result.score < 1.0


def test_confidence_still_computes_without_a_known_agreement_score() -> None:
    result = compute_context_confidence("OK", _agreement(None), _volatility(VolatilityRegime.NORMAL))
    assert result.agreement_component is None
    assert result.score is not None  # averages over the 2 remaining components, never crashes


def test_confidence_is_deterministic() -> None:
    args = ("OK", _agreement(0.75), _volatility(VolatilityRegime.HIGH))
    assert compute_context_confidence(*args) == compute_context_confidence(*args)
