"""Unit tests for :mod:`ai_trader.decision_intelligence.ranking`."""

from __future__ import annotations

from ai_trader.decision_intelligence.eligibility import evaluate_candidate
from ai_trader.decision_intelligence.ranking import comparison_notes, rank_candidates
from ai_trader.decision_intelligence.tests._fixtures import make_contract, make_reading, make_research_stats


def _accepted(strategy_id: str, maturity: str = "VALIDATED", confidence: str = "MEDIUM", **stats_kwargs):
    contract = make_contract(id=strategy_id, maturity=maturity, confidence_level=confidence)
    stats = make_research_stats(**stats_kwargs) if stats_kwargs else None
    candidate = evaluate_candidate(strategy_id, make_reading(strategy_id), contract, stats)
    return candidate, contract, stats


def test_higher_maturity_ranks_first() -> None:
    c1, contract1, _ = _accepted("S1", maturity="EXPLORATORY")
    c2, contract2, _ = _accepted("S2", maturity="PROMOTED")
    contracts = {"S1": contract1, "S2": contract2}
    ranked = rank_candidates((c1, c2), contracts, None)
    assert [c.strategy_id for c in ranked] == ["S2", "S1"]


def test_confidence_breaks_a_maturity_tie() -> None:
    c1, contract1, _ = _accepted("S1", maturity="VALIDATED", confidence="LOW")
    c2, contract2, _ = _accepted("S2", maturity="VALIDATED", confidence="HIGH")
    contracts = {"S1": contract1, "S2": contract2}
    ranked = rank_candidates((c1, c2), contracts, None)
    assert [c.strategy_id for c in ranked] == ["S2", "S1"]


def test_expectancy_breaks_a_maturity_and_confidence_tie() -> None:
    c1, contract1, stats1 = _accepted("S1", n_trades=10, expectancy_r=0.05, win_rate=0.4, sharpe_ratio=0.5)
    c2, contract2, stats2 = _accepted("S2", n_trades=10, expectancy_r=0.3, win_rate=0.6, sharpe_ratio=1.5)
    contracts = {"S1": contract1, "S2": contract2}
    research_stats = {"S1": stats1, "S2": stats2}
    ranked = rank_candidates((c1, c2), contracts, research_stats)
    assert [c.strategy_id for c in ranked] == ["S2", "S1"]


def test_strategy_id_is_the_final_tie_break() -> None:
    c1, contract1, _ = _accepted("S9")
    c2, contract2, _ = _accepted("S2")
    contracts = {"S9": contract1, "S2": contract2}
    ranked = rank_candidates((c1, c2), contracts, None)
    assert [c.strategy_id for c in ranked] == ["S2", "S9"]


def test_missing_research_stats_sorts_after_a_known_positive_expectancy() -> None:
    c1, contract1, stats1 = _accepted("S1", n_trades=10, expectancy_r=0.01, win_rate=0.4, sharpe_ratio=0.1)
    c2, contract2, _ = _accepted("S2")  # no research_stats entry at all
    contracts = {"S1": contract1, "S2": contract2}
    research_stats = {"S1": stats1}
    ranked = rank_candidates((c1, c2), contracts, research_stats)
    assert [c.strategy_id for c in ranked] == ["S1", "S2"]


def test_comparison_notes_cover_every_adjacent_pair() -> None:
    c1, contract1, _ = _accepted("S1", maturity="EXPLORATORY")
    c2, contract2, _ = _accepted("S2", maturity="VALIDATED")
    c3, contract3, _ = _accepted("S3", maturity="PROMOTED")
    contracts = {"S1": contract1, "S2": contract2, "S3": contract3}
    ranked = rank_candidates((c1, c2, c3), contracts, None)
    notes = comparison_notes(ranked, contracts, None)
    assert len(notes) == 2
    assert "S3 outranks S2" in notes[0]
    assert "S2 outranks S1" in notes[1]


def test_comparison_notes_differentiate_by_confidence_when_maturity_ties() -> None:
    c1, contract1, _ = _accepted("S1", maturity="VALIDATED", confidence="LOW")
    c2, contract2, _ = _accepted("S2", maturity="VALIDATED", confidence="HIGH")
    contracts = {"S1": contract1, "S2": contract2}
    ranked = rank_candidates((c1, c2), contracts, None)
    notes = comparison_notes(ranked, contracts, None)
    assert "S2 outranks S1: confidence=HIGH > LOW" in notes[0]


def test_comparison_notes_differentiate_by_expectancy_when_maturity_and_confidence_tie() -> None:
    c1, contract1, stats1 = _accepted("S1", n_trades=10, expectancy_r=0.05, win_rate=0.4, sharpe_ratio=0.5)
    c2, contract2, stats2 = _accepted("S2", n_trades=10, expectancy_r=0.3, win_rate=0.6, sharpe_ratio=1.5)
    contracts = {"S1": contract1, "S2": contract2}
    research_stats = {"S1": stats1, "S2": stats2}
    ranked = rank_candidates((c1, c2), contracts, research_stats)
    notes = comparison_notes(ranked, contracts, research_stats)
    assert "S2 outranks S1: research expectancy_r=0.3 > 0.05" in notes[0]


def test_comparison_notes_disclose_a_genuine_tie() -> None:
    c1, contract1, _ = _accepted("S1")
    c2, contract2, _ = _accepted("S9")
    contracts = {"S1": contract1, "S9": contract2}
    ranked = rank_candidates((c1, c2), contracts, None)
    notes = comparison_notes(ranked, contracts, None)
    assert "tied on maturity, confidence, and expectancy_r" in notes[0]


def test_ranking_is_deterministic() -> None:
    c1, contract1, _ = _accepted("S1", maturity="VALIDATED")
    c2, contract2, _ = _accepted("S2", maturity="PROMOTED")
    contracts = {"S1": contract1, "S2": contract2}
    assert rank_candidates((c1, c2), contracts, None) == rank_candidates((c1, c2), contracts, None)


def test_empty_accepted_yields_empty_ranking_and_no_notes() -> None:
    assert rank_candidates((), {}, None) == ()
    assert comparison_notes((), {}, None) == ()
