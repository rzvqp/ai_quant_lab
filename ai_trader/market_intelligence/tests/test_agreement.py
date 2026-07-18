"""Unit tests for :mod:`ai_trader.market_intelligence.agreement`."""

from __future__ import annotations

from ai_trader.market_intelligence.agreement import analyze_multi_timeframe_agreement
from ai_trader.market_intelligence.types import AgreementLevel, TrendDirection, TrendReading


def _reading(direction: TrendDirection, timeframe: str = "M15") -> TrendReading:
    return TrendReading(timeframe=timeframe, direction=direction, strength=None)


def test_agreement_strong_when_all_aligned() -> None:
    readings = {tf: _reading(TrendDirection.UP, tf) for tf in ("M15", "H1", "H4", "D1")}
    result = analyze_multi_timeframe_agreement(readings)
    assert result.agreement_score == 1.0
    assert result.level is AgreementLevel.STRONG


def test_agreement_weak_when_evenly_split() -> None:
    readings = {
        "M15": _reading(TrendDirection.UP), "H1": _reading(TrendDirection.UP),
        "H4": _reading(TrendDirection.DOWN), "D1": _reading(TrendDirection.DOWN),
    }
    result = analyze_multi_timeframe_agreement(readings)
    assert result.agreement_score == 0.5
    assert result.level is AgreementLevel.WEAK


def test_agreement_moderate_when_majority_but_not_all() -> None:
    readings = {
        "M15": _reading(TrendDirection.UP), "H1": _reading(TrendDirection.UP),
        "H4": _reading(TrendDirection.UP), "D1": _reading(TrendDirection.DOWN),
    }
    result = analyze_multi_timeframe_agreement(readings)
    assert result.agreement_score == 0.75
    assert result.level is AgreementLevel.MODERATE


def test_agreement_ignores_flat_and_unknown_readings() -> None:
    readings = {
        "M15": _reading(TrendDirection.FLAT), "H1": _reading(TrendDirection.UP),
        "H4": _reading(TrendDirection.UP), "D1": _reading(TrendDirection.UNKNOWN),
    }
    result = analyze_multi_timeframe_agreement(readings)
    assert result.agreement_score == 1.0  # only H1/H4 count, both UP
    assert result.level is AgreementLevel.STRONG


def test_agreement_unknown_when_nothing_known() -> None:
    readings = {"M15": _reading(TrendDirection.UNKNOWN), "H1": _reading(TrendDirection.FLAT)}
    result = analyze_multi_timeframe_agreement(readings)
    assert result.agreement_score is None
    assert result.level is AgreementLevel.UNKNOWN


def test_agreement_is_deterministic() -> None:
    readings = {tf: _reading(TrendDirection.UP, tf) for tf in ("M15", "H1")}
    assert analyze_multi_timeframe_agreement(readings) == analyze_multi_timeframe_agreement(readings)
