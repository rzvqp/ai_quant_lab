"""Unit tests for :mod:`ai_trader.edge_intelligence.context`."""

from __future__ import annotations

import dataclasses

from ai_trader.edge_intelligence.context import (
    evaluate_context_confidence,
    evaluate_multi_timeframe_agreement,
    evaluate_volatility_regime,
)
from ai_trader.edge_intelligence.tests._fixtures import make_snapshot
from ai_trader.edge_intelligence.types import EvidenceContribution


def test_confidence_supports_in_good_conditions() -> None:
    snapshot = make_snapshot(m15_features={"m_trend_up": True, "h1_trend_up": True, "h4_trend_up": True, "d1_trend_up": True})
    item = evaluate_context_confidence(snapshot)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_confidence_contradicts_when_score_is_low() -> None:
    # Bad data quality + EXTREME volatility -> score = mean(0.0, 1-0.5) = 0.25, below the 0.5 threshold.
    snapshot = make_snapshot(
        m15_features={"m_atr": 5.0, "atr_ma": 1.0}, data_quality_level="STALE",
    )
    item = evaluate_context_confidence(snapshot)
    assert item.contribution is EvidenceContribution.CONTRADICTS


def test_confidence_unknown_when_score_is_none() -> None:
    # compute_context_confidence() itself never actually returns score=None (its own formula always
    # averages at least two components) -- but ContextConfidence.score's own type is `float | None`,
    # so this layer must still handle that honestly rather than assume the real pipeline's own
    # current behaviour is the only possible input.
    snapshot = make_snapshot(m15_features={"m_trend_up": True})
    degraded = dataclasses.replace(snapshot, confidence=dataclasses.replace(snapshot.confidence, score=None))
    item = evaluate_context_confidence(degraded)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_agreement_supports_when_strong() -> None:
    snapshot = make_snapshot(m15_features={"m_trend_up": True, "h1_trend_up": True, "h4_trend_up": True, "d1_trend_up": True})
    item = evaluate_multi_timeframe_agreement(snapshot)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_agreement_unknown_with_no_known_directions() -> None:
    snapshot = make_snapshot(m15_features={})
    item = evaluate_multi_timeframe_agreement(snapshot)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_agreement_neutral_when_moderate_or_weak() -> None:
    # 2 up, 2 down -> a 50/50 split -> WEAK, never a contradiction.
    snapshot = make_snapshot(m15_features={"m_trend_up": True, "h1_trend_up": True, "h4_trend_up": False, "d1_trend_up": False})
    item = evaluate_multi_timeframe_agreement(snapshot)
    assert item.contribution is EvidenceContribution.NEUTRAL


def test_volatility_supports_when_normal() -> None:
    snapshot = make_snapshot(m15_features={"m_atr": 1.0, "atr_ma": 1.0})
    item = evaluate_volatility_regime(snapshot)
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_volatility_unknown_with_no_data() -> None:
    snapshot = make_snapshot(m15_features={})
    item = evaluate_volatility_regime(snapshot)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_volatility_neutral_never_contradicts_on_its_own() -> None:
    snapshot = make_snapshot(m15_features={"m_atr": 5.0, "atr_ma": 1.0})  # EXTREME
    item = evaluate_volatility_regime(snapshot)
    assert item.contribution is EvidenceContribution.NEUTRAL


def test_all_three_are_deterministic() -> None:
    snapshot = make_snapshot(m15_features={"m_trend_up": True, "h1_trend_up": True, "m_atr": 1.0, "atr_ma": 1.0})
    assert evaluate_context_confidence(snapshot) == evaluate_context_confidence(snapshot)
    assert evaluate_multi_timeframe_agreement(snapshot) == evaluate_multi_timeframe_agreement(snapshot)
    assert evaluate_volatility_regime(snapshot) == evaluate_volatility_regime(snapshot)
