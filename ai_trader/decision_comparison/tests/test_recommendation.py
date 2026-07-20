"""Unit tests for :mod:`ai_trader.decision_comparison.recommendation`."""

from __future__ import annotations

from ai_trader.decision_comparison.recommendation import compare_recommendations
from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome, DecisionReport
from ai_trader.decision_intelligence_v2.types import DecisionCandidateV2, DecisionReportV2


def _candidate(strategy_id: str) -> DecisionCandidate:
    return DecisionCandidate(strategy_id=strategy_id, outcome=DecisionOutcome.ACCEPT, confidence="LOW", evidence=("e",), explanation="x")


def _v1(as_of: int, recommended: str | None) -> DecisionReport:
    return DecisionReport(symbol="XAUUSD", as_of=as_of, candidates=(), recommended_strategy_id=recommended, comparison_notes=())


def _v2(v1: DecisionReport) -> DecisionReportV2:
    return DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id=v1.recommended_strategy_id)


def test_compare_recommendations_empty_input() -> None:
    result = compare_recommendations([])
    assert result.n_compared == 0
    assert result.divergence_rate == 0.0
    assert result.no_trade_frequency_v1 == 0.0


def test_compare_recommendations_all_agree() -> None:
    pairs = [(_v1(1, "S1"), _v2(_v1(1, "S1"))), (_v1(2, None), _v2(_v1(2, None))), (_v1(3, "S2"), _v2(_v1(3, "S2")))]
    result = compare_recommendations(pairs)
    assert result.n_compared == 3
    assert result.divergences == 0
    assert result.divergence_rate == 0.0
    assert result.no_trade_count_v1 == 1
    assert result.no_trade_count_v2 == 1
    assert result.edge_selection_counts_v1 == {"S1": 1, "S2": 1}
    assert result.edge_selection_agreement_rate == 1.0
    assert result.divergent_as_of == ()


def test_compare_recommendations_detects_real_divergence() -> None:
    v1 = _v1(1, "S1")
    v2 = DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S1")
    # construct a v2 whose OWN recommended_strategy_id field differs from what compare_recommendations
    # will read as v2's -- simulate via object.__setattr__ since the type itself forbids this via
    # __post_init__; here we bypass construction validation deliberately to prove the comparator itself
    # detects the mismatch rather than assuming agreement.
    object.__setattr__(v2, "recommended_strategy_id", "S2")
    result = compare_recommendations([(v1, v2)])
    assert result.divergences == 1
    assert result.divergence_rate == 1.0
    assert result.divergent_as_of == (1,)
