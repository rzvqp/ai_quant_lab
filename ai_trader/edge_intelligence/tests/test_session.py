"""Unit tests for :mod:`ai_trader.edge_intelligence.session`."""

from __future__ import annotations

from ai_trader.edge_intelligence.session import evaluate_session_suitability
from ai_trader.edge_intelligence.types import EvidenceContribution


def test_all_sessions_is_neutral() -> None:
    item = evaluate_session_suitability("All sessions", "LONDON")
    assert item.contribution is EvidenceContribution.NEUTRAL


def test_matching_session_supports() -> None:
    item = evaluate_session_suitability("London KZ 07-10 UTC | NY KZ 12-15 UTC", "LONDON")
    assert item.contribution is EvidenceContribution.SUPPORTS


def test_non_matching_session_contradicts() -> None:
    item = evaluate_session_suitability("London KZ 07-10 UTC | NY KZ 12-15 UTC", "ASIA")
    assert item.contribution is EvidenceContribution.CONTRADICTS


def test_unparseable_declaration_is_unknown_never_guessed() -> None:
    item = evaluate_session_suitability("Monday open only", "LONDON")
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_unknown_when_current_session_is_none() -> None:
    item = evaluate_session_suitability("London KZ 07-10 UTC", None)
    assert item.contribution is EvidenceContribution.UNKNOWN


def test_is_deterministic() -> None:
    args = ("London KZ 07-10 UTC", "LONDON")
    assert evaluate_session_suitability(*args) == evaluate_session_suitability(*args)
