"""Unit tests for :mod:`ai_trader.edge_intelligence.data_availability`."""

from __future__ import annotations

from ai_trader.edge_intelligence.data_availability import evaluate_data_availability
from ai_trader.edge_intelligence.tests._fixtures import make_contract, make_context
from ai_trader.edge_intelligence.types import EvidenceContribution
from ai_trader.market_intelligence.tests._fixtures import make_bar


def test_supports_when_all_required_timeframes_have_bars() -> None:
    contract = make_contract(timeframe="M15")
    context = make_context(m15_bars=[make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)])
    item = evaluate_data_availability(contract, context)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_contradicts_when_execution_timeframe_has_no_bars() -> None:
    contract = make_contract(timeframe="M15")
    context = make_context(m15_bars=[])
    item = evaluate_data_availability(contract, context)
    assert item.contribution is EvidenceContribution.CONTRADICTS


def test_contradicts_when_a_declared_htf_requirement_has_no_bars() -> None:
    contract = make_contract(
        timeframe="M15",
        required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 20, "htf": ["H4"]}],
    )
    context = make_context(m15_bars=[make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)])
    item = evaluate_data_availability(contract, context)
    assert item.contribution is EvidenceContribution.CONTRADICTS
    assert "H4" in item.explanation


def test_supports_when_declared_htf_requirement_has_bars() -> None:
    contract = make_contract(
        timeframe="M15",
        required_data=[{"timeframe": "M15", "fields": ["m_atr"], "lookback_bars": 20, "htf": ["H4"]}],
    )
    context = make_context(
        m15_bars=[make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)],
        other_timeframes={"H4": {"bars": [make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)], "features": {}, "feature_history": []}},
    )
    item = evaluate_data_availability(contract, context)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_is_deterministic() -> None:
    contract = make_contract(timeframe="M15")
    context = make_context(m15_bars=[make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)])
    assert evaluate_data_availability(contract, context) == evaluate_data_availability(contract, context)
