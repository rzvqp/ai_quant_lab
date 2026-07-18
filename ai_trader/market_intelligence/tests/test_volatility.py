"""Unit tests for :mod:`ai_trader.market_intelligence.volatility`."""

from __future__ import annotations

from ai_trader.market_intelligence.volatility import analyze_volatility
from ai_trader.market_intelligence.types import VolatilityRegime
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_volatility_normal() -> None:
    ctx = make_context(m15_features={"m_atr": 1.0, "atr_ma": 1.0, "m_volrank": 0.5})
    reading = analyze_volatility(ctx)
    assert reading.atr_ratio == 1.0
    assert reading.regime is VolatilityRegime.NORMAL
    assert reading.volatility_rank == 0.5


def test_volatility_low() -> None:
    ctx = make_context(m15_features={"m_atr": 0.5, "atr_ma": 1.0})
    assert analyze_volatility(ctx).regime is VolatilityRegime.LOW


def test_volatility_high() -> None:
    ctx = make_context(m15_features={"m_atr": 1.5, "atr_ma": 1.0})
    assert analyze_volatility(ctx).regime is VolatilityRegime.HIGH


def test_volatility_extreme_low_side() -> None:
    ctx = make_context(m15_features={"m_atr": 0.1, "atr_ma": 1.0})
    assert analyze_volatility(ctx).regime is VolatilityRegime.EXTREME


def test_volatility_extreme_high_side() -> None:
    ctx = make_context(m15_features={"m_atr": 5.0, "atr_ma": 1.0})
    assert analyze_volatility(ctx).regime is VolatilityRegime.EXTREME


def test_volatility_unknown_when_missing() -> None:
    reading = analyze_volatility(make_context(m15_features={}))
    assert reading.regime is VolatilityRegime.UNKNOWN
    assert reading.atr_ratio is None


def test_volatility_unknown_when_atr_ma_is_zero() -> None:
    reading = analyze_volatility(make_context(m15_features={"m_atr": 1.0, "atr_ma": 0.0}))
    assert reading.atr_ratio is None
    assert reading.regime is VolatilityRegime.UNKNOWN


def test_analyze_volatility_is_deterministic() -> None:
    ctx = make_context(m15_features={"m_atr": 1.0, "atr_ma": 1.0})
    assert analyze_volatility(ctx) == analyze_volatility(ctx)
