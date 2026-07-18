"""Unit tests for :mod:`ai_trader.market_intelligence.momentum`."""

from __future__ import annotations

from ai_trader.market_intelligence.momentum import analyze_momentum, analyze_momentum_m15
from ai_trader.market_intelligence.types import MomentumState
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_momentum_overbought() -> None:
    ctx = make_context(m15_features={"m_rsi": 75.0, "roc3": 0.02})
    reading = analyze_momentum_m15(ctx)
    assert reading.state is MomentumState.OVERBOUGHT
    assert reading.rsi == 75.0
    assert reading.rate_of_change == 0.02


def test_momentum_oversold() -> None:
    ctx = make_context(m15_features={"m_rsi": 25.0})
    assert analyze_momentum_m15(ctx).state is MomentumState.OVERSOLD


def test_momentum_neutral() -> None:
    ctx = make_context(m15_features={"m_rsi": 50.0})
    assert analyze_momentum_m15(ctx).state is MomentumState.NEUTRAL


def test_momentum_boundary_values_are_inclusive() -> None:
    assert analyze_momentum_m15(make_context(m15_features={"m_rsi": 70.0})).state is MomentumState.OVERBOUGHT
    assert analyze_momentum_m15(make_context(m15_features={"m_rsi": 30.0})).state is MomentumState.OVERSOLD


def test_momentum_unknown_when_missing() -> None:
    reading = analyze_momentum_m15(make_context(m15_features={}))
    assert reading.state is MomentumState.UNKNOWN
    assert reading.rsi is None


def test_momentum_higher_timeframes_have_no_rate_of_change() -> None:
    ctx = make_context(m15_features={"m_rsi": 50.0, "h1_rsi": 80.0, "h4_rsi": 20.0, "d1_rsi": 55.0})
    readings = analyze_momentum(ctx)
    assert readings["H1"].state is MomentumState.OVERBOUGHT
    assert readings["H1"].rate_of_change is None
    assert readings["H4"].state is MomentumState.OVERSOLD


def test_analyze_momentum_is_deterministic() -> None:
    ctx = make_context(m15_features={"m_rsi": 50.0, "h1_rsi": 80.0})
    assert analyze_momentum(ctx) == analyze_momentum(ctx)
