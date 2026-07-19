"""Unit tests for :mod:`ai_trader.context_memory.enums` -- fixed expected values, since these must
match Market Intelligence's/Edge Intelligence's/market_scanner's own real enum values exactly (verified
against the real source files before writing these, not assumed)."""

from __future__ import annotations

from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    HorizonUnit,
    OutcomeStatus,
    SourceType,
)


def test_trend_direction_values() -> None:
    assert {m.value for m in ContextTrendDirection} == {"UP", "DOWN", "FLAT", "UNKNOWN"}


def test_structure_state_values() -> None:
    assert {m.value for m in ContextStructureState} == {
        "BULLISH_BOS", "BEARISH_BOS", "BULLISH_CHOCH", "BEARISH_CHOCH", "RANGING", "UNKNOWN",
    }


def test_momentum_state_values() -> None:
    assert {m.value for m in ContextMomentumState} == {"OVERBOUGHT", "OVERSOLD", "NEUTRAL", "UNKNOWN"}


def test_volatility_regime_values() -> None:
    assert {m.value for m in ContextVolatilityRegime} == {"LOW", "NORMAL", "HIGH", "EXTREME", "UNKNOWN"}


def test_liquidity_state_values() -> None:
    assert {m.value for m in ContextLiquidityState} == {"THIN", "NORMAL", "THICK", "UNKNOWN"}


def test_expansion_state_values() -> None:
    assert {m.value for m in ContextExpansionState} == {"COMPRESSED", "EXPANDING", "NORMAL", "UNKNOWN"}


def test_agreement_level_values() -> None:
    assert {m.value for m in ContextAgreementLevel} == {"STRONG", "MODERATE", "WEAK", "UNKNOWN"}


def test_data_quality_state_values() -> None:
    assert {m.value for m in ContextDataQualityState} == {"OK", "DEGRADED", "STALE", "INSUFFICIENT"}


def test_edge_status_values() -> None:
    assert {m.value for m in ContextEdgeStatus} == {"PRESENT", "POSSIBLE", "ABSENT"}


def test_outcome_status_values() -> None:
    assert {m.value for m in OutcomeStatus} == {"PENDING", "RESOLVED", "INVALID", "UNAVAILABLE"}


def test_source_type_values() -> None:
    assert {m.value for m in SourceType} == {"PRICE_ONLY", "SHADOW_EVIDENCE_ADAPTER"}


def test_horizon_unit_values() -> None:
    assert {m.value for m in HorizonUnit} == {"BARS"}
