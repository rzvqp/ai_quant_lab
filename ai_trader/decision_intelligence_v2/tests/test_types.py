"""Unit tests for :mod:`ai_trader.decision_intelligence_v2.types`."""

from __future__ import annotations

import pytest

from ai_trader.context_memory import RetrievalStatus
from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome, DecisionReport
from ai_trader.decision_intelligence_v2.types import CandidateEvidence, DecisionCandidateV2, DecisionReportV2


def _v1_candidate(strategy_id: str = "S1", outcome: DecisionOutcome = DecisionOutcome.ACCEPT) -> DecisionCandidate:
    return DecisionCandidate(strategy_id=strategy_id, outcome=outcome, confidence="LOW", evidence=("test evidence",), explanation="test")


def _v1_report(recommended: str | None) -> DecisionReport:
    return DecisionReport(
        symbol="XAUUSD", as_of=1_700_000_000, candidates=(_v1_candidate(),),
        recommended_strategy_id=recommended, comparison_notes=("only candidate",),
    )


def test_candidate_evidence_rejects_empty_explanation() -> None:
    with pytest.raises(ValueError):
        CandidateEvidence(retrieval_status=RetrievalStatus.NO_ELIGIBLE_HISTORY, evidence=None, explanation=())


def test_candidate_evidence_accepts_non_empty_explanation() -> None:
    ce = CandidateEvidence(retrieval_status=RetrievalStatus.NO_ELIGIBLE_HISTORY, evidence=None, explanation=("no history",))
    assert ce.explanation == ("no history",)


def test_decision_report_v2_accepts_matching_recommendation() -> None:
    v1 = _v1_report("S1")
    v2 = DecisionReportV2(
        v1_report=v1, candidates=(DecisionCandidateV2(candidate=_v1_candidate(), context_evidence=None),),
        recommended_strategy_id="S1",
    )
    assert v2.recommended_strategy_id == v1.recommended_strategy_id


def test_decision_report_v2_accepts_matching_no_trade() -> None:
    v1 = _v1_report(None)
    v2 = DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id=None)
    assert v2.recommended_strategy_id is None


def test_decision_report_v2_rejects_mismatched_recommendation() -> None:
    v1 = _v1_report("S1")
    with pytest.raises(ValueError):
        DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S2")


def test_decision_report_v2_rejects_recommendation_when_v1_says_no_trade() -> None:
    v1 = _v1_report(None)
    with pytest.raises(ValueError):
        DecisionReportV2(v1_report=v1, candidates=(), recommended_strategy_id="S1")
