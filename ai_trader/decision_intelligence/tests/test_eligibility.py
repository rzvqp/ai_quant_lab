"""Unit tests for :mod:`ai_trader.decision_intelligence.eligibility`."""

from __future__ import annotations

from ai_trader.decision_intelligence.eligibility import evaluate_candidate
from ai_trader.decision_intelligence.tests._fixtures import make_contract, make_reading, make_research_stats
from ai_trader.decision_intelligence.types import DecisionOutcome


def test_accepts_a_clean_implemented_present_candidate() -> None:
    contract = make_contract(status="IMPLEMENTED", maturity="VALIDATED", confidence_level="MEDIUM")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.ACCEPT
    assert candidate.confidence == "MEDIUM"


def test_rejects_non_implemented_status() -> None:
    contract = make_contract(status="DISABLED")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.REJECT
    assert "DISABLED" in candidate.explanation


def test_rejects_retired_maturity() -> None:
    contract = make_contract(maturity="RETIRED")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.REJECT
    assert "RETIRED" in candidate.explanation


def test_rejects_none_confidence() -> None:
    contract = make_contract(confidence_level="NONE")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.REJECT


def test_rejects_negative_confidence() -> None:
    contract = make_contract(confidence_level="NEGATIVE")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.REJECT


def test_accepts_very_low_confidence() -> None:
    contract = make_contract(confidence_level="VERY_LOW")
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert candidate.outcome is DecisionOutcome.ACCEPT


def test_rejects_non_positive_research_expectancy() -> None:
    contract = make_contract(confidence_level="HIGH")
    stats = make_research_stats(n_trades=20, expectancy_r=-0.1)
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, stats)
    assert candidate.outcome is DecisionOutcome.REJECT
    assert "expectancy_r" in candidate.explanation


def test_accepts_positive_research_expectancy() -> None:
    contract = make_contract(confidence_level="HIGH")
    stats = make_research_stats(n_trades=20, expectancy_r=0.15)
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, stats)
    assert candidate.outcome is DecisionOutcome.ACCEPT


def test_zero_trade_research_stats_does_not_block_acceptance() -> None:
    # n_trades == 0 means the expectancy check never fires (there is no track record to judge, not a
    # negative one) -- the eligibility gate must not fabricate a rejection from absent data.
    contract = make_contract(confidence_level="HIGH")
    stats = make_research_stats(n_trades=0, expectancy_r=None)
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, stats)
    assert candidate.outcome is DecisionOutcome.ACCEPT


def test_evidence_is_never_empty() -> None:
    contract = make_contract()
    candidate = evaluate_candidate("S1", make_reading("S1"), contract, None)
    assert len(candidate.evidence) > 0


def test_is_deterministic() -> None:
    contract = make_contract(confidence_level="HIGH")
    reading = make_reading("S1")
    assert evaluate_candidate("S1", reading, contract, None) == evaluate_candidate("S1", reading, contract, None)
