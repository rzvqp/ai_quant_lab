"""Mandate Section 26/27 (Lesson voting): canonical-episode selection (earliest-eligible-wins),
one-vote-per-underlying-move, frozen-horizon-only vote derivation, retrospective-events-never-vote,
and the exact CEO worked examples (7/3-at-N=10 eligible, 6/4 not eligible via ratio, 7-support/
9-voting not eligible via N<10 despite 7/9 > 0.70).
"""

from __future__ import annotations

from ai_trader.apprenticeship_v2.general_observer.lesson_voting import (
    classify_lesson_status, derive_vote, episode_matches_hypothesis, select_canonical_episodes, tally_votes,
)

HYPOTHESIS = {"episode_type": "SWEEP_REJECTION", "directional_hypothesis": "BULLISH"}


def _episode_row(move_id, ts_utc, *, episode_id=None, etype="SWEEP_REJECTION", direction="BULLISH", eligible="YES"):
    episode_id = episode_id or f"GO-{move_id}-{ts_utc}"
    return {
        "episode_id": episode_id, "timestamp_utc": ts_utc, "episode_type": etype,
        "directional_hypothesis": direction, "underlying_move_id": move_id,
        "prospective_eligibility": eligible, "reference_levels_json": "{}",
    }


def _score_row(episode_id, horizon, verdict):
    return {"episode_id": episode_id, "review_horizon": horizon, "expectation_correct": verdict}


def test_episode_matches_hypothesis_exact_field_match():
    row = _episode_row("M1", "t1", etype="SWEEP_REJECTION", direction="BULLISH")
    assert episode_matches_hypothesis(row, HYPOTHESIS) is True
    assert episode_matches_hypothesis(row, {**HYPOTHESIS, "directional_hypothesis": "BEARISH"}) is False


def test_canonical_episode_is_earliest_by_timestamp_within_a_move():
    later = _episode_row("M1", "2026-01-01T02:00:00+00:00", episode_id="LATER")
    earlier = _episode_row("M1", "2026-01-01T01:00:00+00:00", episode_id="EARLIER")
    canonical = select_canonical_episodes(HYPOTHESIS, [later, earlier])
    assert canonical["M1"]["episode_id"] == "EARLIER"


def test_non_matching_episode_type_excluded_from_canonical_selection():
    row = _episode_row("M1", "t1", etype="DISPLACEMENT")  # hypothesis requires SWEEP_REJECTION
    canonical = select_canonical_episodes(HYPOTHESIS, [row])
    assert "M1" not in canonical


def test_non_eligible_episode_excluded_from_canonical_selection():
    row = _episode_row("M1", "t1", eligible="NO")
    canonical = select_canonical_episodes(HYPOTHESIS, [row])
    assert "M1" not in canonical


def test_derive_vote_support_on_yes():
    ep = _episode_row("M1", "t1", episode_id="E1")
    scores = [_score_row("E1", "H1", "YES")]
    assert derive_vote(ep, "H1", scores) == "SUPPORT"


def test_derive_vote_counterexample_on_no():
    ep = _episode_row("M1", "t1", episode_id="E1")
    scores = [_score_row("E1", "H1", "NO")]
    assert derive_vote(ep, "H1", scores) == "COUNTEREXAMPLE"


def test_derive_vote_non_voting_on_partial_and_not_scorable():
    ep = _episode_row("M1", "t1", episode_id="E1")
    assert derive_vote(ep, "H1", [_score_row("E1", "H1", "PARTIAL")]) == "NON_VOTING"
    assert derive_vote(ep, "H1", [_score_row("E1", "H1", "NOT_SCORABLE")]) == "NON_VOTING"


def test_derive_vote_non_voting_when_horizon_not_yet_scored():
    ep = _episode_row("M1", "t1", episode_id="E1")
    assert derive_vote(ep, "H4", [_score_row("E1", "H1", "YES")]) == "NON_VOTING"  # wrong horizon


def test_derive_vote_never_uses_a_different_episode_or_horizon_from_the_same_move():
    """No multiple-horizon rescue, no multiple-episode rescue -- a YES at H4 must not count when the
    hypothesis's frozen horizon is H1."""
    ep = _episode_row("M1", "t1", episode_id="E1")
    scores = [_score_row("E1", "H4", "YES"), _score_row("SOME-OTHER-EPISODE", "H1", "YES")]
    assert derive_vote(ep, "H1", scores) == "NON_VOTING"


def test_derive_vote_non_voting_when_canonical_not_prospectively_eligible():
    ep = _episode_row("M1", "t1", episode_id="E1", eligible="NO")
    assert derive_vote(ep, "H1", [_score_row("E1", "H1", "YES")]) == "NON_VOTING"


def test_retrospective_records_never_enter_canonical_selection_or_voting():
    """A RETROSPECTIVELY_IDENTIFIED_MISSED_EVENT row is structurally distinct (missing
    directional_hypothesis/episode_type values matching any of the 4 classes) -- it can never match
    a hypothesis built from prospective fields, so it can never vote, by construction."""
    retro = {
        "episode_id": "RETRO-1", "timestamp_utc": "t0", "episode_type": "RETROSPECTIVELY_IDENTIFIED_MISSED_EVENT",
        "directional_hypothesis": None, "underlying_move_id": None, "prospective_eligibility": None,
        "reference_levels_json": "{}",
    }
    canonical = select_canonical_episodes(HYPOTHESIS, [retro])
    assert canonical == {}


def test_one_vote_per_underlying_move_even_with_multiple_matching_episodes():
    e1 = _episode_row("M1", "2026-01-01T01:00:00+00:00", episode_id="E1")
    e2 = _episode_row("M1", "2026-01-01T02:00:00+00:00", episode_id="E2")  # later episode, same move
    scores = [_score_row("E1", "H1", "YES"), _score_row("E2", "H1", "YES")]  # even if E2 also scored
    n_voting, support, counter = tally_votes(HYPOTHESIS, "H1", [e1, e2], scores)
    assert n_voting == 1  # one move, one vote -- E2's own score is never consulted (E1 is canonical)
    assert support == 1


def test_tally_worked_example_7_of_10_eligible():
    rows = [_episode_row(f"M{i}", f"t{i}", episode_id=f"E{i}") for i in range(10)]
    scores = [_score_row(f"E{i}", "H1", "YES" if i < 7 else "NO") for i in range(10)]
    n_voting, support, _ = tally_votes(HYPOTHESIS, "H1", rows, scores)
    assert (n_voting, support) == (10, 7)
    assert classify_lesson_status(n_voting, support) == "PROSPECTIVELY_SUPPORTED"


def test_tally_worked_example_6_of_10_not_eligible_via_ratio():
    rows = [_episode_row(f"M{i}", f"t{i}", episode_id=f"E{i}") for i in range(10)]
    scores = [_score_row(f"E{i}", "H1", "YES" if i < 6 else "NO") for i in range(10)]
    n_voting, support, _ = tally_votes(HYPOTHESIS, "H1", rows, scores)
    assert (n_voting, support) == (10, 6)
    assert classify_lesson_status(n_voting, support) == "PROSPECTIVELY_WEAKENED"


def test_tally_worked_example_7_of_9_not_eligible_via_n_below_10_despite_high_ratio():
    """Section 13a's own explicit example: 7 supporting matches out of 9 total VOTING moves --
    7/9 ~ 0.778 > 0.70, but N=9 < 10, so not eligible regardless of the good ratio."""
    rows = [_episode_row(f"M{i}", f"t{i}", episode_id=f"E{i}") for i in range(9)]
    scores = [_score_row(f"E{i}", "H1", "YES" if i < 7 else "NO") for i in range(9)]
    n_voting, support, _ = tally_votes(HYPOTHESIS, "H1", rows, scores)
    assert (n_voting, support) == (9, 7)
    assert n_voting < 10
    assert classify_lesson_status(n_voting, support) == "REPEATED_OBSERVATION"


def test_non_voting_moves_never_counted_in_denominator():
    rows = [_episode_row(f"M{i}", f"t{i}", episode_id=f"E{i}") for i in range(5)]
    # 3 determinate (2 YES, 1 NO) + 2 non-voting (PARTIAL / unscored).
    scores = [
        _score_row("E0", "H1", "YES"), _score_row("E1", "H1", "YES"), _score_row("E2", "H1", "NO"),
        _score_row("E3", "H1", "PARTIAL"),
        # E4 intentionally has no scorecard row at all -- unresolved, non-voting.
    ]
    n_voting, support, counter = tally_votes(HYPOTHESIS, "H1", rows, scores)
    assert (n_voting, support, counter) == (3, 2, 1)


def test_horizon_is_a_respected_input_never_silently_ignored_or_mutable():
    """Mandate Section 27's explicit adversarial requirement (horizon changed after hypothesis
    creation must not be tolerated): `lesson_evaluation_horizon` is frozen at hypothesis creation and
    is passed into `derive_vote`/`tally_votes` as a plain parameter on every call -- neither function
    stores or mutates it internally, so there is no code path by which it could silently drift after
    creation. Demonstrated here: the SAME underlying scorecard data, read at two different frozen
    horizons, produces genuinely different verdicts -- proof the horizon is load-bearing, not a
    decoration a caller could vary after the fact without consequence."""
    ep = _episode_row("M1", "t1", episode_id="E1")
    scores = [_score_row("E1", "H1", "YES"), _score_row("E1", "H4", "NO")]
    assert derive_vote(ep, "H1", scores) == "SUPPORT"
    assert derive_vote(ep, "H4", scores) == "COUNTEREXAMPLE"
    # A hypothesis frozen at H1 must never be re-scored by silently reading the H4 row instead.
    assert derive_vote(ep, "H1", scores) != derive_vote(ep, "H4", scores)


def test_classify_lesson_status_new_hypothesis_at_zero_and_one_votes():
    """Section 19.7 correction: NEW_HYPOTHESIS = n_voting in {0, 1} (the frozen doc's own "First...
    observation" is singular, i.e. n==1, not n==0 alone -- the prior delivery's n==0-only default
    was SEMANTICALLY_INCORRECT per Section 19.1's own audit)."""
    assert classify_lesson_status(0, 0) == "NEW_HYPOTHESIS"
    assert classify_lesson_status(1, 1) == "NEW_HYPOTHESIS"
    assert classify_lesson_status(1, 0) == "NEW_HYPOTHESIS"


def test_classify_lesson_status_repeated_observation_range():
    """REPEATED_OBSERVATION = n_voting in [2, 9] -- corrected boundary starts at 2, not 1."""
    assert classify_lesson_status(2, 2) == "REPEATED_OBSERVATION"
    assert classify_lesson_status(9, 9) == "REPEATED_OBSERVATION"
    assert classify_lesson_status(9, 0) == "REPEATED_OBSERVATION"


def test_classify_lesson_status_weakened_rejected_0_5_boundary():
    """Section 19.7/mandate Section 20: the WEAKENED/REJECTED split at the mathematically forced 0.5
    majority midpoint, inclusive on the WEAKENED side -- exact equality boundary tests as required."""
    assert classify_lesson_status(10, 7) == "PROSPECTIVELY_SUPPORTED"  # 0.70 exact boundary
    assert classify_lesson_status(10, 5) == "PROSPECTIVELY_WEAKENED"  # 0.5 exact boundary, inclusive
    assert classify_lesson_status(10, 4) == "PROSPECTIVELY_REJECTED"  # just below 0.5
    assert classify_lesson_status(10, 6) == "PROSPECTIVELY_WEAKENED"  # strictly between 0.5 and 0.70
    assert classify_lesson_status(10, 0) == "PROSPECTIVELY_REJECTED"  # 0.0, well below 0.5
    assert classify_lesson_status(10, 10) == "PROSPECTIVELY_SUPPORTED"  # 1.0, well above 0.70


def test_classify_lesson_status_deterioration_and_recovery_are_pure_recomputation():
    """Section 19.7: no special-case code is needed for deterioration/recovery -- classify_lesson_
    status is a pure function of the CURRENT (n_voting, support) totals, so recomputing it after new
    evidence arrives automatically reflects a stage change either direction."""
    assert classify_lesson_status(10, 7) == "PROSPECTIVELY_SUPPORTED"
    # A new counterexample arrives (support unchanged, n_voting +1) -- ratio drops, recompute:
    assert classify_lesson_status(11, 7) == "PROSPECTIVELY_WEAKENED"  # 7/11 ~ 0.636 -- deteriorated
    # Evidence recovers (another support arrives):
    assert classify_lesson_status(12, 9) == "PROSPECTIVELY_SUPPORTED"  # 9/12 = 0.75 -- recovered
