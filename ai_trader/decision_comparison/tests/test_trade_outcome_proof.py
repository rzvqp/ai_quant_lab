"""Unit tests for :mod:`ai_trader.decision_comparison.trade_outcome_proof`."""

from __future__ import annotations

from ai_trader.decision_comparison.recommendation import compare_recommendations
from ai_trader.decision_comparison.trade_outcome_proof import prove_trade_outcome_equivalence
from ai_trader.decision_intelligence.types import DecisionReport
from ai_trader.decision_intelligence_v2.types import DecisionReportV2


def _v1(as_of: int, recommended: str | None) -> DecisionReport:
    return DecisionReport(symbol="XAUUSD", as_of=as_of, candidates=(), recommended_strategy_id=recommended, comparison_notes=())


def test_equivalence_holds_when_no_divergence() -> None:
    v1 = _v1(1, "S1")
    v2 = DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S1")
    comparison = compare_recommendations([(v1, v2)])
    proof = prove_trade_outcome_equivalence(comparison)
    assert proof.equivalence_holds is True
    assert "provably identical" in proof.rationale


def test_equivalence_fails_when_divergence_detected() -> None:
    v1 = _v1(1, "S1")
    v2 = DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S1")
    object.__setattr__(v2, "recommended_strategy_id", "S2")
    comparison = compare_recommendations([(v1, v2)])
    proof = prove_trade_outcome_equivalence(comparison)
    assert proof.equivalence_holds is False
    assert "diverged" in proof.rationale
