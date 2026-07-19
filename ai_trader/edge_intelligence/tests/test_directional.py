"""Unit tests for :mod:`ai_trader.edge_intelligence.directional`."""

from __future__ import annotations

from ai_trader.edge_intelligence.directional import evaluate_directional_alignment
from ai_trader.edge_intelligence.tests._fixtures import make_contract, make_snapshot
from ai_trader.edge_intelligence.types import EvidenceContribution


def test_both_is_neutral_regardless_of_trend() -> None:
    contract = make_contract(long_short="BOTH")
    snapshot = make_snapshot(m15_features={"m_trend_up": True})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.NEUTRAL


def test_long_supports_when_trend_is_up() -> None:
    contract = make_contract(long_short="LONG", timeframe="M15")
    snapshot = make_snapshot(m15_features={"m_trend_up": True})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_long_contradicts_when_trend_is_down() -> None:
    contract = make_contract(long_short="LONG", timeframe="M15")
    snapshot = make_snapshot(m15_features={"m_trend_up": False})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.CONTRADICTS


def test_short_supports_when_trend_is_down() -> None:
    contract = make_contract(long_short="SHORT", timeframe="H1")
    snapshot = make_snapshot(m15_features={"h1_trend_up": False})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_short_contradicts_when_trend_is_up() -> None:
    contract = make_contract(long_short="SHORT", timeframe="H4")
    snapshot = make_snapshot(m15_features={"h4_trend_up": True})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.CONTRADICTS


def test_unknown_when_no_trend_flag_present() -> None:
    contract = make_contract(long_short="LONG", timeframe="D1")
    snapshot = make_snapshot(m15_features={})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_unknown_when_execution_timeframe_not_tracked_by_market_intelligence() -> None:
    contract = make_contract(long_short="LONG", timeframe="M5")
    snapshot = make_snapshot(m15_features={"m_trend_up": True})
    item = evaluate_directional_alignment(contract, snapshot)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_is_deterministic() -> None:
    contract = make_contract(long_short="LONG", timeframe="M15")
    snapshot = make_snapshot(m15_features={"m_trend_up": True})
    assert evaluate_directional_alignment(contract, snapshot) == evaluate_directional_alignment(contract, snapshot)
