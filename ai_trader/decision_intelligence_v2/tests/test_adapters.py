"""Unit tests for :mod:`ai_trader.decision_intelligence_v2.adapters`."""

from __future__ import annotations

import pytest

from ai_trader.context_memory.enums import (
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
)
from ai_trader.decision_intelligence_v2.adapters import build_context_snapshot, build_present_edge_reference
from ai_trader.decision_intelligence_v2.tests._fixtures import AS_OF, make_mi_snapshot
from ai_trader.edge_intelligence.tests._fixtures import make_contract as make_edge_contract
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.market_intelligence.types import ContextConfidence, MomentumState, StructureState, TrendDirection, VolatilityRegime


def test_build_context_snapshot_maps_every_dimension() -> None:
    mi = make_mi_snapshot(symbol="XAUUSD", as_of=AS_OF)
    snap = build_context_snapshot(mi)

    assert snap.instrument == "XAUUSD"
    assert snap.as_of == AS_OF
    assert snap.session_state == "LONDON"
    assert snap.trend_m15 is ContextTrendDirection.UP
    assert snap.structure_state is ContextStructureState.BULLISH_BOS
    assert snap.momentum_m15 is ContextMomentumState.NEUTRAL
    assert snap.volatility_regime is ContextVolatilityRegime.NORMAL
    assert snap.context_confidence_score == 0.8


def test_build_context_snapshot_maps_data_quality_ok_true() -> None:
    mi = make_mi_snapshot(confidence=ContextConfidence(score=0.9, data_quality_ok=True, agreement_component=1.0, volatility_penalty=0.0))
    snap = build_context_snapshot(mi)
    assert snap.data_quality_state is ContextDataQualityState.OK


def test_build_context_snapshot_maps_data_quality_ok_false_to_degraded() -> None:
    mi = make_mi_snapshot(confidence=ContextConfidence(score=0.2, data_quality_ok=False, agreement_component=0.1, volatility_penalty=0.5))
    snap = build_context_snapshot(mi)
    assert snap.data_quality_state is ContextDataQualityState.DEGRADED


def test_build_context_snapshot_per_timeframe_trend_and_momentum_independent() -> None:
    from ai_trader.market_intelligence.types import MomentumReading, TrendReading

    mi = make_mi_snapshot()
    trend = dict(mi.trend)
    trend["D1"] = TrendReading(timeframe="D1", direction=TrendDirection.DOWN, strength=None)
    momentum = dict(mi.momentum)
    momentum["H4"] = MomentumReading(timeframe="H4", rsi=80.0, state=MomentumState.OVERBOUGHT, rate_of_change=None)
    mi2 = make_mi_snapshot(trend=trend, momentum=momentum)

    snap = build_context_snapshot(mi2)
    assert snap.trend_d1 is ContextTrendDirection.DOWN
    assert snap.trend_m15 is ContextTrendDirection.UP  # unaffected
    assert snap.momentum_h4 is ContextMomentumState.OVERBOUGHT
    assert snap.momentum_m15 is ContextMomentumState.NEUTRAL  # unaffected


def test_build_present_edge_reference() -> None:
    contract = make_edge_contract(id="S1")
    ref = build_present_edge_reference("S1", contract, EdgeState.PRESENT)
    assert ref.strategy_id == "S1"
    assert ref.declared_status is ContextEdgeStatus.PRESENT
    assert ref.contract_version.namespace == "strategy_contract"


def test_build_present_edge_reference_preserves_possible_state() -> None:
    # Fidelity correction (Learning/Research Feedback Phase E, CEO decision): the real edge_state must
    # be preserved, never silently upgraded to PRESENT.
    contract = make_edge_contract(id="S1")
    ref = build_present_edge_reference("S1", contract, EdgeState.POSSIBLE)
    assert ref.declared_status is ContextEdgeStatus.POSSIBLE
    assert ref.strategy_id == "S1"


def test_build_present_edge_reference_rejects_absent_state() -> None:
    contract = make_edge_contract(id="S1")
    with pytest.raises(ValueError):
        build_present_edge_reference("S1", contract, EdgeState.ABSENT)
