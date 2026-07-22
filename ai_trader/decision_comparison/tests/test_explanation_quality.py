"""Unit tests for :mod:`ai_trader.decision_comparison.explanation_quality`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory import (
    ContextMemoryRepository,
    HistoricalIndex,
    OutcomeKind,
    RetrievalQuery,
    RetrievalStatus,
    aggregate_evidence,
    retrieve,
)
from ai_trader.decision_comparison.explanation_quality import score_explanation_quality
from ai_trader.decision_intelligence.types import DecisionReport
from ai_trader.decision_intelligence_v2.explanation import explain_candidate
from ai_trader.decision_intelligence_v2.tests._fixtures import AS_OF, build_populated_index, make_cm_snapshot
from ai_trader.decision_intelligence_v2.types import CandidateEvidence, DecisionCandidateV2, DecisionReportV2
from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome


def _v1_candidate(strategy_id: str) -> DecisionCandidate:
    return DecisionCandidate(strategy_id=strategy_id, outcome=DecisionOutcome.ACCEPT, confidence="LOW", evidence=("e",), explanation="x")


def test_no_context_evidence_yields_zero_counts() -> None:
    v1 = DecisionReport(symbol="XAUUSD", as_of=AS_OF, candidates=(_v1_candidate("S1"),), recommended_strategy_id="S1", comparison_notes=())
    v2 = DecisionReportV2(
        v1_report=v1, candidates=(DecisionCandidateV2(candidate=_v1_candidate("S1"), context_evidence=None),),
        recommended_strategy_id="S1",
    )
    result = score_explanation_quality([v2])
    assert result.n_candidates_with_context_evidence == 0
    assert result.v2_strictly_more_explanatory_content is False


def test_context_evidence_with_failed_retrieval_and_no_evidence_report(tmp_path: Path) -> None:
    idx = HistoricalIndex(ContextMemoryRepository(tmp_path / "repo"))
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF)
    retrieval = retrieve(idx, query)
    assert retrieval.status is RetrievalStatus.NO_ELIGIBLE_HISTORY

    v1 = DecisionReport(symbol="XAUUSD", as_of=AS_OF, candidates=(_v1_candidate("S1"),), recommended_strategy_id="S1", comparison_notes=())
    v2 = DecisionReportV2(
        v1_report=v1,
        candidates=(DecisionCandidateV2(
            candidate=_v1_candidate("S1"),
            context_evidence=CandidateEvidence(retrieval_status=retrieval.status, evidence=None, explanation=("no history",)),
        ),),
        recommended_strategy_id="S1",
    )
    result = score_explanation_quality([v2])
    assert result.n_candidates_with_context_evidence == 1
    assert result.n_candidates_disclosing_limitations_when_present == 1  # vacuously satisfied
    assert result.v2_strictly_more_explanatory_content is True


def test_populated_context_evidence_discloses_all_categories(tmp_path: Path) -> None:
    idx = build_populated_index(tmp_path, strategy_id="S1", n_episodes=30, result=1.0)
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF, edge_scope=("S1",), max_candidates=30)
    retrieval = retrieve(idx, query)
    evidence = aggregate_evidence(idx, retrieval, "S1", OutcomeKind.STRATEGY)
    explanation = explain_candidate(retrieval, evidence)

    v1 = DecisionReport(symbol="XAUUSD", as_of=AS_OF, candidates=(_v1_candidate("S1"),), recommended_strategy_id="S1", comparison_notes=())
    v2 = DecisionReportV2(
        v1_report=v1,
        candidates=(DecisionCandidateV2(
            candidate=_v1_candidate("S1"),
            context_evidence=CandidateEvidence(retrieval_status=retrieval.status, evidence=evidence, explanation=explanation),
        ),),
        recommended_strategy_id="S1",
    )
    result = score_explanation_quality([v2])
    assert result.n_candidates_with_context_evidence == 1
    assert result.n_candidates_disclosing_why_found == 1
    assert result.n_candidates_disclosing_evidence == 1
    assert result.n_candidates_disclosing_status_reason == 1
    assert result.n_candidates_disclosing_limitations_when_present == 1
    assert result.v2_strictly_more_explanatory_content is True
