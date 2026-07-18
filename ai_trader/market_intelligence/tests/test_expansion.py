"""Unit tests for :mod:`ai_trader.market_intelligence.expansion`."""

from __future__ import annotations

from ai_trader.market_intelligence.expansion import analyze_expansion
from ai_trader.market_intelligence.types import ExpansionState
from ai_trader.market_intelligence.tests._fixtures import make_context


def test_expansion_compressed() -> None:
    ctx = make_context(m15_features={"compress": True, "disp": False})
    assert analyze_expansion(ctx).state is ExpansionState.COMPRESSED


def test_expansion_expanding() -> None:
    ctx = make_context(m15_features={"compress": False, "disp": True})
    assert analyze_expansion(ctx).state is ExpansionState.EXPANDING


def test_expansion_normal() -> None:
    ctx = make_context(m15_features={"compress": False, "disp": False})
    assert analyze_expansion(ctx).state is ExpansionState.NORMAL


def test_expansion_displacement_takes_priority_over_compression() -> None:
    ctx = make_context(m15_features={"compress": True, "disp": True})
    assert analyze_expansion(ctx).state is ExpansionState.EXPANDING


def test_expansion_unknown_when_missing() -> None:
    reading = analyze_expansion(make_context(m15_features={}))
    assert reading.state is ExpansionState.UNKNOWN
    assert reading.is_compressed is None
    assert reading.is_displacement is None


def test_expansion_is_deterministic() -> None:
    ctx = make_context(m15_features={"compress": True, "disp": False})
    assert analyze_expansion(ctx) == analyze_expansion(ctx)
