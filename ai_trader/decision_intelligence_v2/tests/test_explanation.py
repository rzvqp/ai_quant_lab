"""Unit tests for :mod:`ai_trader.decision_intelligence_v2.explanation`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory import RetrievalQuery, retrieve
from ai_trader.decision_intelligence_v2.explanation import explain_candidate, explain_evidence, explain_retrieval
from ai_trader.decision_intelligence_v2.tests._fixtures import AS_OF, build_populated_index, make_cm_snapshot
from ai_trader.context_memory import aggregate_evidence
from ai_trader.context_memory.retrieval import RetrievalStatus


def test_explain_retrieval_no_eligible_history(tmp_path: Path) -> None:
    from ai_trader.context_memory import ContextMemoryRepository, HistoricalIndex

    idx = HistoricalIndex(ContextMemoryRepository(tmp_path / "repo"))
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF + 1000), as_of_cutoff=AS_OF + 1000)
    result = retrieve(idx, query)
    lines = explain_retrieval(result)
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY
    assert len(lines) == 1
    assert "No historical context retrieved" in lines[0]
    assert "NO_ELIGIBLE_HISTORY" in lines[0]


def test_explain_retrieval_successful(tmp_path: Path) -> None:
    idx = build_populated_index(tmp_path, strategy_id="S1", n_episodes=5)
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF, edge_scope=("S1",))
    result = retrieve(idx, query)
    lines = explain_retrieval(result)
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert any("Historical context found" in line for line in lines)
    assert any("Best match" in line for line in lines)


def test_explain_evidence_sufficient(tmp_path: Path) -> None:
    idx = build_populated_index(tmp_path, strategy_id="S1", n_episodes=30, result=1.0)
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF, edge_scope=("S1",), max_candidates=30)
    result = retrieve(idx, query)
    evidence = aggregate_evidence(idx, result, "S1")
    lines = explain_evidence(evidence)
    assert any("Evidence status: SUFFICIENT" in line for line in lines)
    assert any("resolved episode" in line for line in lines)
    assert any("confidence interval" in line for line in lines)


def test_explain_evidence_unavailable_zero_resolved(tmp_path: Path) -> None:
    idx = build_populated_index(tmp_path, strategy_id="S1", n_episodes=1)
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF, edge_scope=("S7",))
    result = retrieve(idx, query)
    evidence = aggregate_evidence(idx, result, "S7")
    lines = explain_evidence(evidence)
    assert any("Evidence status: UNAVAILABLE" in line for line in lines)


def test_explain_candidate_combines_retrieval_and_evidence(tmp_path: Path) -> None:
    idx = build_populated_index(tmp_path, strategy_id="S1", n_episodes=5)
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF), as_of_cutoff=AS_OF, edge_scope=("S1",))
    result = retrieve(idx, query)
    evidence = aggregate_evidence(idx, result, "S1")
    lines = explain_candidate(result, evidence)
    assert any("Historical context found" in line for line in lines)
    assert any("Evidence status" in line for line in lines)


def test_explain_candidate_without_evidence(tmp_path: Path) -> None:
    from ai_trader.context_memory import ContextMemoryRepository, HistoricalIndex

    idx = HistoricalIndex(ContextMemoryRepository(tmp_path / "repo"))
    query = RetrievalQuery(context_snapshot=make_cm_snapshot(as_of=AS_OF + 1000), as_of_cutoff=AS_OF + 1000)
    result = retrieve(idx, query)
    lines = explain_candidate(result, evidence=None)
    assert lines == explain_retrieval(result)
