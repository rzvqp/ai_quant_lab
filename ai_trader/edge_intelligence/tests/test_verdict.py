"""Unit tests for :mod:`ai_trader.edge_intelligence.verdict`."""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EdgeState, EvidenceContribution
from ai_trader.edge_intelligence.verdict import determine_edge_state


def _item(contribution: EvidenceContribution) -> EdgeEvidenceItem:
    return EdgeEvidenceItem(dimension="test", contribution=contribution, explanation="test")


def test_any_contradicts_is_absent_regardless_of_others() -> None:
    evidence = (_item(EvidenceContribution.SUPPORTS), _item(EvidenceContribution.CONTRADICTS), _item(EvidenceContribution.SUPPORTS))
    assert determine_edge_state(evidence) is EdgeState.ABSENT


def test_unknown_with_no_contradiction_is_possible() -> None:
    evidence = (_item(EvidenceContribution.SUPPORTS), _item(EvidenceContribution.UNKNOWN))
    assert determine_edge_state(evidence) is EdgeState.POSSIBLE


def test_all_supports_or_neutral_with_at_least_one_supports_is_present() -> None:
    evidence = (_item(EvidenceContribution.SUPPORTS), _item(EvidenceContribution.NEUTRAL))
    assert determine_edge_state(evidence) is EdgeState.PRESENT


def test_all_neutral_is_possible_not_present() -> None:
    evidence = (_item(EvidenceContribution.NEUTRAL), _item(EvidenceContribution.NEUTRAL))
    assert determine_edge_state(evidence) is EdgeState.POSSIBLE


def test_is_deterministic() -> None:
    evidence = (_item(EvidenceContribution.SUPPORTS), _item(EvidenceContribution.NEUTRAL))
    assert determine_edge_state(evidence) == determine_edge_state(evidence)
