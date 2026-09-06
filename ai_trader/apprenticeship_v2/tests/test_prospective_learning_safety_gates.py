"""CEO mandate (prospective-learning safety patch, shadow-apprenticeship activation): two mechanical
gates in `before_review.effective_general_episode_rows`, closing a real defect where the
shadow-apprenticeship activation record was documentary only and never consulted by the learning
path -- the 27 backfilled first-tick episodes and 2 missed-move clusters could otherwise enter
canonical lesson evidence if ever (mistakenly) reviewed.

Gate 1 (activation-cutoff): an episode's own `frozen_at_bar_ts` must be STRICTLY AFTER the shadow-
apprenticeship activation record's own T0 to ever be prospective evidence.
Gate 2 (BEFORE-deadline): a BEFORE review completed more than H1 (60 minutes; reused from
`schemas.RESOLUTION_HORIZONS_M15[0]`, no new timing threshold) after the episode's own trigger is no
longer safely prospective.

Both gates can only ever downgrade `YES` to `NO`; neither ever reads `scored_at_utc` (scorecard
timing cannot influence either one); both are pure functions of already-persisted, restart-stable
facts, so a restart reproduces the identical verdict.
"""

from __future__ import annotations

import json

import pytest

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.general_observer import before_review
from ai_trader.apprenticeship_v2.general_observer.lesson_voting import select_canonical_episodes, tally_votes
from ai_trader.apprenticeship_v2.schemas import EpisodeRecord, ScorecardEntry

HYPOTHESIS = {"episode_type": "SWEEP_REJECTION", "directional_hypothesis": "BULLISH"}
CUTOFF_TS = 1_788_717_834  # matches the real production activation record's own M15_EPISODE_CUTOFF_EXCLUSIVE


@pytest.fixture(autouse=True)
def _isolated_durable_store(tmp_path, monkeypatch):
    """Must never read/write the real, live production files -- the real activation record, with this
    exact cutoff value, genuinely exists on this machine."""
    monkeypatch.setattr(durable_store, "SCORECARD_CSV", tmp_path / "AI_TRADER_SCORECARD.csv")
    monkeypatch.setattr(durable_store, "GENERAL_OBSERVER_PREDICTIONS_CSV", tmp_path / "AI_TRADER_GENERAL_OBSERVER_PREDICTIONS.csv")
    monkeypatch.setattr(before_review, "ACTIVATION_RECORD_JSON", tmp_path / "ACTIVATION.json")


def _write_activation_record(cutoff_ts: int = CUTOFF_TS) -> None:
    before_review.ACTIVATION_RECORD_JSON.parent.mkdir(parents=True, exist_ok=True)
    before_review.ACTIVATION_RECORD_JSON.write_text(
        json.dumps({"GENUINELY_PROSPECTIVE_CUTOFF": {"M15_EPISODE_CUTOFF_EXCLUSIVE": cutoff_ts}}), encoding="utf-8",
    )


def _ledger_row(frozen_at_bar_ts, *, episode_id="GO-1", eligible="YES", move_id="MOVE-1") -> dict:
    return {
        "episode_id": episode_id, "timestamp_utc": "t1", "episode_type": "SWEEP_REJECTION",
        "directional_hypothesis": "BULLISH", "underlying_move_id": move_id,
        "prospective_eligibility": eligible, "reference_levels_json": "{}",
        "frozen_at_bar_ts": frozen_at_bar_ts,
    }


def _episode(episode_id="GO-1", **overrides) -> EpisodeRecord:
    base = dict(
        episode_id=episode_id, timestamp_utc="2026-01-01T00:00:00+00:00", frozen_at_bar_ts=CUTOFF_TS + 10_000,
        episode_type="SWEEP_REJECTION", symbol="XAUUSD", current_price=1900.0, setup_direction=None,
        reference_levels={}, snapshot={"H4": [], "H1": [], "M15": [], "M5": []},
        directional_hypothesis="BULLISH", underlying_move_id="MOVE-1", prospective_eligibility="YES",
    )
    base.update(overrides)
    return EpisodeRecord(**base)


def _score_row(episode_id, scored_at_utc, verdict="YES"):
    return ScorecardEntry(
        episode_id=episode_id, review_horizon="H1", original_expectation="FOLLOW_THROUGH_LIKELY",
        original_confidence="HIGH", mechanical_outcome_summary="x", expectation_correct=verdict,
        partial_reason=None, scored_at_utc=scored_at_utc,
    )


# ---- Gate 1: activation-cutoff -------------------------------------------------------------------

def test_load_activation_cutoff_ts_none_when_record_absent():
    assert before_review.load_activation_cutoff_ts() is None


def test_load_activation_cutoff_ts_reads_the_authoritative_record():
    _write_activation_record(CUTOFF_TS)
    assert before_review.load_activation_cutoff_ts() == CUTOFF_TS


def test_evaluate_activation_cutoff_pre_t0_is_no():
    assert before_review.evaluate_activation_cutoff_eligibility(CUTOFF_TS - 1, CUTOFF_TS) == "NO"


def test_evaluate_activation_cutoff_exactly_at_t0_is_no():
    assert before_review.evaluate_activation_cutoff_eligibility(CUTOFF_TS, CUTOFF_TS) == "NO"


def test_evaluate_activation_cutoff_post_t0_is_yes():
    assert before_review.evaluate_activation_cutoff_eligibility(CUTOFF_TS + 1, CUTOFF_TS) == "YES"


def test_pre_t0_episode_never_votes_end_to_end():
    """The real backfill shape: a raw ledger row, never reviewed (no prediction record at all), whose
    trigger is at-or-before T0 -- must never show YES, not merely happen to never vote because it
    lacks a scorecard row."""
    _write_activation_record(CUTOFF_TS)
    row = _ledger_row(CUTOFF_TS - 10_000)
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "NO"
    canonical = select_canonical_episodes(HYPOTHESIS, [row])
    assert canonical == {}
    n_voting, support, counter = tally_votes(HYPOTHESIS, "H1", [row], [_score_row("GO-1", "t", "YES")])
    assert (n_voting, support, counter) == (0, 0, 0)


def test_episode_exactly_at_t0_never_votes_end_to_end():
    _write_activation_record(CUTOFF_TS)
    row = _ledger_row(CUTOFF_TS)
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "NO"
    assert select_canonical_episodes(HYPOTHESIS, [row]) == {}


def test_post_t0_episode_may_remain_eligible_end_to_end():
    _write_activation_record(CUTOFF_TS)
    row = _ledger_row(CUTOFF_TS + 1)
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "YES"
    canonical = select_canonical_episodes(HYPOTHESIS, [row])
    assert "MOVE-1" in canonical


def test_activation_cutoff_gate_is_a_noop_when_no_activation_record_exists_yet():
    """Chicken-and-egg case: apprenticeship never activated -- no episodes should exist either, and
    the gate must not spuriously block a hand-built test row."""
    row = _ledger_row(123)
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "YES"


def test_backfilled_episode_forced_no_even_if_mistakenly_reviewed_before_any_scoring():
    """The exact gap the ordering guard alone does not cover: a backfilled (pre-T0) episode that a
    future reviewer mistakenly completes BEFORE review for, with NO scorecard row yet in existence at
    all -- `evaluate_prospective_eligibility` (the ordering guard) would say YES here (no early
    scorecard row to violate against), but the activation-cutoff gate must independently force NO."""
    _write_activation_record(CUTOFF_TS)
    ep = _episode("GO-BACKFILL", frozen_at_bar_ts=CUTOFF_TS - 5000)
    assert before_review.evaluate_prospective_eligibility("GO-BACKFILL", "2026-01-01T00:10:00+00:00") == "YES"
    completed = before_review.complete_before_review(ep, reviewed_at_utc="2026-01-01T00:10:00+00:00")
    assert completed.prospective_eligibility == "YES"  # the ordering guard alone was fooled
    durable_store.append_general_prediction(completed)

    row = _ledger_row(CUTOFF_TS - 5000, episode_id="GO-BACKFILL")
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "NO"  # the activation-cutoff gate catches it anyway
    assert select_canonical_episodes(HYPOTHESIS, [row]) == {}


def test_activation_cutoff_restart_preserves_exclusion():
    """Restart-safety: two independent evaluations against the same persisted facts (no reused
    objects, no in-memory cache) reproduce the identical verdict."""
    _write_activation_record(CUTOFF_TS)
    row = _ledger_row(CUTOFF_TS - 1)
    verdict_a = before_review.effective_general_episode_rows([row])[0]["prospective_eligibility"]
    verdict_b = before_review.effective_general_episode_rows([dict(row)])[0]["prospective_eligibility"]
    assert verdict_a == verdict_b == "NO"


# ---- Gate 2: BEFORE-deadline (H1) ------------------------------------------------------------------

def test_h1_window_seconds_reuses_the_frozen_horizon_no_new_constant():
    from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15
    assert before_review.H1_WINDOW_SECONDS == RESOLUTION_HORIZONS_M15[0] * 15 * 60 == 3600


def test_evaluate_before_deadline_within_h1_is_yes():
    trigger = 1_000_000
    reviewed = trigger + before_review.H1_WINDOW_SECONDS - 1
    reviewed_iso = _iso(reviewed)
    assert before_review.evaluate_before_deadline_eligibility(trigger, reviewed_iso) == "YES"


def test_evaluate_before_deadline_exactly_at_boundary_is_yes_inclusive():
    trigger = 1_000_000
    reviewed_iso = _iso(trigger + before_review.H1_WINDOW_SECONDS)
    assert before_review.evaluate_before_deadline_eligibility(trigger, reviewed_iso) == "YES"


def test_evaluate_before_deadline_after_h1_is_no():
    trigger = 1_000_000
    reviewed_iso = _iso(trigger + before_review.H1_WINDOW_SECONDS + 1)
    assert before_review.evaluate_before_deadline_eligibility(trigger, reviewed_iso) == "NO"


def _iso(epoch_seconds: int) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(epoch_seconds, tz=datetime.timezone.utc).isoformat()


def test_before_within_h1_eligible_subject_to_other_gates_end_to_end():
    _write_activation_record(CUTOFF_TS)
    trigger = CUTOFF_TS + 100_000
    ep = _episode("GO-2", frozen_at_bar_ts=trigger)
    completed = before_review.complete_before_review(ep, reviewed_at_utc=_iso(trigger + 60))  # 1 minute later
    durable_store.append_general_prediction(completed)
    row = _ledger_row(trigger, episode_id="GO-2")
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "YES"


def test_before_after_h1_forced_non_prospective_end_to_end():
    """A late BEFORE stays on the durable record (never rewritten/deleted) but can never vote."""
    _write_activation_record(CUTOFF_TS)
    trigger = CUTOFF_TS + 100_000
    ep = _episode("GO-3", frozen_at_bar_ts=trigger)
    late_reviewed = _iso(trigger + before_review.H1_WINDOW_SECONDS + 1)
    completed = before_review.complete_before_review(ep, reviewed_at_utc=late_reviewed)
    assert completed.prospective_eligibility == "YES"  # ordering guard alone: no violation
    durable_store.append_general_prediction(completed)

    # The record itself is untouched -- still there, still readable, for qualitative/debugging use.
    persisted = durable_store.read_general_prediction("GO-3")
    assert persisted is not None
    assert persisted["reviewed_at_utc"] == late_reviewed

    row = _ledger_row(trigger, episode_id="GO-3")
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "NO"  # but it can never vote
    assert select_canonical_episodes(HYPOTHESIS, [row]) == {}


def test_before_deadline_restart_cannot_bypass_the_gate():
    _write_activation_record(CUTOFF_TS)
    trigger = CUTOFF_TS + 100_000
    ep = _episode("GO-4", frozen_at_bar_ts=trigger)
    completed = before_review.complete_before_review(
        ep, reviewed_at_utc=_iso(trigger + before_review.H1_WINDOW_SECONDS + 1),
    )
    durable_store.append_general_prediction(completed)
    row = _ledger_row(trigger, episode_id="GO-4")

    verdict_a = before_review.effective_general_episode_rows([row])[0]["prospective_eligibility"]
    verdict_b = before_review.effective_general_episode_rows([dict(row)])[0]["prospective_eligibility"]
    assert verdict_a == verdict_b == "NO"


def test_no_scorecard_timing_manipulation_can_restore_eligibility():
    """Neither an early NOR a late scorecard row -- nor the complete absence of one -- can flip a
    late-BEFORE verdict back to YES. The gate reads only frozen_at_bar_ts/reviewed_at_utc, never
    scored_at_utc."""
    _write_activation_record(CUTOFF_TS)
    trigger = CUTOFF_TS + 100_000
    late_reviewed = _iso(trigger + before_review.H1_WINDOW_SECONDS + 1)
    ep = _episode("GO-5", frozen_at_bar_ts=trigger)
    completed = before_review.complete_before_review(ep, reviewed_at_utc=late_reviewed)
    durable_store.append_general_prediction(completed)
    row = _ledger_row(trigger, episode_id="GO-5")

    # No scorecard row at all.
    assert before_review.effective_general_episode_rows([row])[0]["prospective_eligibility"] == "NO"

    # A deceptively EARLY scored_at_utc (would satisfy the ordering guard trivially) changes nothing.
    durable_store.append_scorecard(_score_row("GO-5", _iso(trigger - 1000)))
    assert before_review.effective_general_episode_rows([row])[0]["prospective_eligibility"] == "NO"

    # A genuinely later scored_at_utc changes nothing either.
    durable_store.append_scorecard(_score_row("GO-5", _iso(trigger + 999_999)))
    assert before_review.effective_general_episode_rows([row])[0]["prospective_eligibility"] == "NO"


def test_before_deadline_gate_is_a_noop_before_any_review_happens():
    """An episode still PENDING_LLM_REVIEW (no prediction row, hence no reviewed_at_utc) is not
    touched by gate 2 -- meaningless before a BEFORE review has actually happened, and it already
    cannot vote upstream (no prediction/scorecard row can exist for it)."""
    _write_activation_record(CUTOFF_TS)
    row = _ledger_row(CUTOFF_TS + 100_000, episode_id="GO-6")
    effective = before_review.effective_general_episode_rows([row])
    assert effective[0]["prospective_eligibility"] == "YES"
