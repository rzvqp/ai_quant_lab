"""Mandate item 2 (BEFORE ordering-violation protection, design doc Section 8 step 8): the
mechanical guard forcing `prospective_eligibility = NO` when outcome/future information was already
mechanically available before BEFORE review completed, its persistence path, the read-side overlay
that makes it authoritative for lesson evidence, and the required explicit adversarial tests.
"""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer import before_review
from ai_trader.apprenticeship_v2.general_observer.lesson_voting import select_canonical_episodes
from ai_trader.apprenticeship_v2.schemas import EpisodeRecord, ScorecardEntry


@pytest.fixture(autouse=True)
def _isolated_durable_store(tmp_path, monkeypatch):
    """These tests must never read or write the real, live production files. Includes
    `before_review.ACTIVATION_RECORD_JSON`: the real shadow-apprenticeship activation record already
    exists on this machine (production data), so leaving it unisolated would make these tests silently
    depend on live state -- pointed at a nonexistent path by default (`load_activation_cutoff_ts()`
    returns `None`, the documented no-activation-yet behavior) unless a test writes its own fixture
    file there."""
    monkeypatch.setattr(durable_store, "SCORECARD_CSV", tmp_path / "AI_TRADER_SCORECARD.csv")
    monkeypatch.setattr(durable_store, "GENERAL_OBSERVER_PREDICTIONS_CSV", tmp_path / "AI_TRADER_GENERAL_OBSERVER_PREDICTIONS.csv")
    monkeypatch.setattr(before_review, "ACTIVATION_RECORD_JSON", tmp_path / "AI_TRADER_GENERAL_OBSERVER_SHADOW_APPRENTICESHIP_ACTIVATION.json")


def _episode(episode_id="GO-1", **overrides) -> EpisodeRecord:
    base = dict(
        episode_id=episode_id, timestamp_utc="2026-01-01T00:00:00+00:00", frozen_at_bar_ts=1000,
        episode_type="SWEEP_REJECTION", symbol="XAUUSD", current_price=1900.0, setup_direction=None,
        reference_levels={}, snapshot={"H4": [], "H1": [], "M15": [], "M5": []},
        directional_hypothesis="BULLISH", underlying_move_id="MOVE-1", prospective_eligibility="YES",
    )
    base.update(overrides)
    return EpisodeRecord(**base)


def _score_row(episode_id, scored_at_utc):
    return ScorecardEntry(
        episode_id=episode_id, review_horizon="H1", original_expectation="FOLLOW_THROUGH_LIKELY",
        original_confidence="HIGH", mechanical_outcome_summary="x", expectation_correct="YES",
        partial_reason=None, scored_at_utc=scored_at_utc,
    )


def test_no_violation_when_no_scorecard_row_exists_yet():
    assert before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00") == "YES"


def test_no_violation_when_scorecard_row_was_written_after_review_completed():
    """Normal, expected ordering: BEFORE freezes at T0, outcome is scored later at T1 > T0 -- no
    violation."""
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T01:00:00+00:00"))
    assert before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00") == "YES"


def test_violation_forces_no_when_scorecard_row_predates_review_completion():
    """The explicit adversarial case: an outcome was already mechanically computed BEFORE the BEFORE
    review completed -- future/outcome information was available first."""
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:05:00+00:00"))
    assert before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00") == "NO"


def test_violation_detected_even_with_multiple_scorecard_rows_only_one_early():
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T02:00:00+00:00"))  # after -- fine on its own
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:01:00+00:00"))  # before -- violates
    assert before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00") == "NO"


def test_complete_before_review_sets_no_and_frozen_on_violation():
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:05:00+00:00"))
    ep = _episode("GO-1")
    completed = before_review.complete_before_review(ep, reviewed_at_utc="2026-01-01T00:10:00+00:00")
    assert completed.prospective_eligibility == "NO"
    assert completed.qualitative_review_status == "FROZEN"
    assert completed.reviewed_at_utc == "2026-01-01T00:10:00+00:00"
    # Original episode object is untouched (immutable dataclasses.replace, not a mutation).
    assert ep.prospective_eligibility == "YES"


def test_complete_before_review_sets_yes_when_no_violation():
    ep = _episode("GO-2")
    completed = before_review.complete_before_review(ep, reviewed_at_utc="2026-01-01T00:10:00+00:00")
    assert completed.prospective_eligibility == "YES"
    assert completed.qualitative_review_status == "FROZEN"


def test_effective_rows_overrides_ledger_default_when_completion_record_says_no():
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:05:00+00:00"))
    ep = _episode("GO-1")
    completed = before_review.complete_before_review(ep, reviewed_at_utc="2026-01-01T00:10:00+00:00")
    durable_store.append_general_prediction(completed)

    ledger_row = {"episode_id": "GO-1", "prospective_eligibility": "YES"}  # stale mechanical default
    effective = before_review.effective_general_episode_rows([ledger_row])
    assert effective[0]["prospective_eligibility"] == "NO"
    assert ledger_row["prospective_eligibility"] == "YES"  # original dict never mutated in place


def test_effective_rows_unchanged_when_no_completion_record_exists():
    ledger_row = {"episode_id": "GO-3", "prospective_eligibility": "YES"}
    effective = before_review.effective_general_episode_rows([ledger_row])
    assert effective[0]["prospective_eligibility"] == "YES"


def test_lesson_evidence_excludes_episode_whose_before_review_was_violated():
    """End-to-end adversarial proof (mandate item 2's own required behavior): an episode whose
    ledger row still says prospective_eligibility=YES (the stale, mechanical-shell-creation-time
    value) is nonetheless EXCLUDED from lesson evidence once its BEFORE-review-completion record
    says NO -- "such an episode cannot enter prospective lesson evidence"."""
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:05:00+00:00"))
    ep = _episode("GO-1")
    completed = before_review.complete_before_review(ep, reviewed_at_utc="2026-01-01T00:10:00+00:00")
    durable_store.append_general_prediction(completed)

    ledger_rows = [{
        "episode_id": "GO-1", "timestamp_utc": "t1", "episode_type": "SWEEP_REJECTION",
        "directional_hypothesis": "BULLISH", "underlying_move_id": "MOVE-1",
        "prospective_eligibility": "YES",  # stale ledger value -- must not be trusted directly
        "reference_levels_json": "{}",
    }]
    hypothesis = {"episode_type": "SWEEP_REJECTION", "directional_hypothesis": "BULLISH"}
    canonical = select_canonical_episodes(hypothesis, ledger_rows)
    assert canonical == {}  # excluded -- the violation was caught despite the stale YES on the row itself


def test_restart_reproduces_identical_violation_verdict():
    """Restart-safety: freshly-constructed inputs (simulating a process restart -- no reused Python
    objects, no in-memory cache) reproduce the identical violation verdict."""
    durable_store.append_scorecard(_score_row("GO-1", "2026-01-01T00:05:00+00:00"))
    verdict_a = before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00")
    # Simulate restart: re-read from the same durable file fresh, independently.
    verdict_b = before_review.evaluate_prospective_eligibility("GO-1", "2026-01-01T00:10:00+00:00")
    assert verdict_a == verdict_b == "NO"
