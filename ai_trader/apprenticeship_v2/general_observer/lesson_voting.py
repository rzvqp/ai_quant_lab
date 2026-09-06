"""Lesson vote aggregation (design doc Section 13/13a, CEO Addendum 2; ladder corrected by Section
19.7, Fifth Addendum). Governs how one `underlying_move_id` produces a single
`SUPPORT`/`COUNTEREXAMPLE`/non-voting outcome, and how the accumulated votes classify a
`LessonHypothesis`'s `lesson_status`.

Depends on `scorecard.py`'s `ScorecardEntry.expectation_correct` values -- now produced for real by
`scorecard.classify_expectation_correct` (patched per Section 19), so this module's own vote
aggregation is no longer blocked from real (non-test-fixture) data.

`MIN_INDEPENDENT_UNDERLYING_MOVES = 10`, `MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED = 0.70`,
`MAX_LESSON_VOTES_PER_UNDERLYING_MOVE = 1` -- all CEO-declared, Section 13/13a, applied verbatim,
unchanged by this patch.

`classify_lesson_status`'s ladder was corrected by Section 19.7 (Fifth Addendum): the prior
delivery's own disclosed `NEW_HYPOTHESIS`/`REPEATED_OBSERVATION` boundary default was found
`SEMANTICALLY_INCORRECT` against the frozen doc's own wording and is now `n_voting in {0,1}` /
`n_voting in [2,9]`; the prior `WEAKENED`/`REJECTED` collapse is now split at the mathematically
forced `0.5` majority midpoint (not a new CEO-calibrated constant). See `classify_lesson_status`'s
own docstring for the exact table.
"""

from __future__ import annotations

import json

MIN_INDEPENDENT_UNDERLYING_MOVES = 10
MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED = 0.70
MAX_LESSON_VOTES_PER_UNDERLYING_MOVE = 1


def episode_matches_hypothesis(episode_row: dict, hypothesis_eligibility_definition: dict) -> bool:
    """Every key in `hypothesis_eligibility_definition` must exactly match the episode row's own
    field, or (for a `"reference_levels"` sub-dict) a key inside its parsed `reference_levels_json`.
    Whether the definition itself only cites prospectively-available fields is a hypothesis-authoring-
    time concern (Section 13a's own constraint on the CEO/researcher who writes one) -- out of scope
    for this pure matcher, which only ever applies whatever criteria it is given."""
    for key, expected in hypothesis_eligibility_definition.items():
        if key == "reference_levels":
            if not isinstance(expected, dict):
                return False
            ref = json.loads(episode_row.get("reference_levels_json", "{}") or "{}")
            if any(ref.get(rk) != rv for rk, rv in expected.items()):
                return False
            continue
        if episode_row.get(key) != expected:
            return False
    return True


def select_canonical_episodes(
    hypothesis_eligibility_definition: dict, general_episode_rows: list[dict],
) -> dict[str, dict]:
    """Section 13a's exact mechanical rule: filter to `prospective_eligibility=YES`, filter to
    hypothesis-matching, group by `underlying_move_id`, sort ascending by `timestamp_utc` (the ledger
    field Section 7 aliases to `created_at_utc`) within each group -- the first is
    `CANONICAL_LESSON_EPISODE`; every later matching episode in the same move is simply absent from
    the returned mapping (never chosen by strength, confidence, cleanliness, outcome, or proximity to
    the eventual move -- `LESSON_VOTE_WEIGHT=0` is enforced by never being looked at again, not by an
    explicit zero-weight marker). Returns `{underlying_move_id: canonical_row}`."""
    matching = [
        row for row in general_episode_rows
        if row.get("prospective_eligibility") == "YES" and episode_matches_hypothesis(row, hypothesis_eligibility_definition)
    ]
    by_move: dict[str, list[dict]] = {}
    for row in matching:
        move_id = row.get("underlying_move_id")
        if not move_id:
            continue
        by_move.setdefault(move_id, []).append(row)
    canonical: dict[str, dict] = {}
    for move_id, rows in by_move.items():
        rows.sort(key=lambda r: r.get("timestamp_utc") or "")
        canonical[move_id] = rows[0]
    return canonical


def derive_vote(canonical_episode_row: dict, lesson_evaluation_horizon: str, scorecard_rows: list[dict]) -> str:
    """Returns `"SUPPORT"` | `"COUNTEREXAMPLE"` | `"NON_VOTING"`. Reads exactly one scorecard row --
    `(episode_id=canonical, review_horizon=lesson_evaluation_horizon)` -- never any other horizon or
    episode from the same move (Section 13a: "No other horizon and no other episode from the same
    move participates"). `expectation_correct=YES -> SUPPORT`, `NO -> COUNTEREXAMPLE`,
    `{PARTIAL, NOT_SCORABLE} -> NON_VOTING`, an unresolved (not-yet-scored) horizon -> `NON_VOTING`,
    and a canonical episode that itself is not prospectively eligible -> `NON_VOTING` -- all per
    Section 13a's own exhaustive non-voting-case list."""
    if canonical_episode_row.get("prospective_eligibility") != "YES":
        return "NON_VOTING"
    matches = [
        r for r in scorecard_rows
        if r.get("episode_id") == canonical_episode_row.get("episode_id") and r.get("review_horizon") == lesson_evaluation_horizon
    ]
    if not matches:
        return "NON_VOTING"  # not yet resolved at this horizon
    verdict = matches[0].get("expectation_correct")
    if verdict == "YES":
        return "SUPPORT"
    if verdict == "NO":
        return "COUNTEREXAMPLE"
    return "NON_VOTING"  # PARTIAL / NOT_SCORABLE / anything else unrecognized


def tally_votes(
    hypothesis_eligibility_definition: dict, lesson_evaluation_horizon: str,
    general_episode_rows: list[dict], scorecard_rows: list[dict],
) -> tuple[int, int, int]:
    """Returns `(n_voting_independent_moves, support_moves, counterexample_moves)`. Section 13a's
    exact denominator: only moves with a determinate (`SUPPORT`/`COUNTEREXAMPLE`) vote count toward
    `N`; non-voting moves are excluded entirely, never imputed. `MAX_LESSON_VOTES_PER_UNDERLYING_
    MOVE=1` holds by construction: exactly one canonical episode, hence at most one vote, per move."""
    canonical = select_canonical_episodes(hypothesis_eligibility_definition, general_episode_rows)
    support = 0
    counterexample = 0
    for row in canonical.values():
        vote = derive_vote(row, lesson_evaluation_horizon, scorecard_rows)
        if vote == "SUPPORT":
            support += 1
        elif vote == "COUNTEREXAMPLE":
            counterexample += 1
    return support + counterexample, support, counterexample


def classify_lesson_status(n_voting: int, support: int) -> str:
    """Design doc Section 19.7 (Fifth Addendum) -- the corrected, complete stage table, applied to
    `(n_voting_independent_moves, support_moves)`.

    `NEW_HYPOTHESIS` = `n_voting in {0, 1}`; `REPEATED_OBSERVATION` = `n_voting in [2, 9]`;
    `PROSPECTIVELY_SUPPORTED` = `n_voting >= 10 and ratio >= 0.70`; `PROSPECTIVELY_WEAKENED` =
    `n_voting >= 10 and 0.5 <= ratio < 0.70`; `PROSPECTIVELY_REJECTED` = `n_voting >= 10 and ratio <
    0.5`.

    This corrects the prior delivery's own disclosed default (`n_voting==0 -> NEW_HYPOTHESIS`,
    `1..9 -> REPEATED_OBSERVATION`), which Section 19's own audit (19.1) found
    `SEMANTICALLY_INCORRECT` against the frozen doc's literal "First... observation" (singular, i.e.
    `n==1`) / "2-9" wording. It also resolves the prior `WEAKENED`/`REJECTED` collapse using the
    `0.5` majority midpoint -- mathematically forced (the boundary between "more supporting than
    contradicting evidence" and the reverse, for a two-outcome vote), not a new CEO-calibrated
    constant, per Section 19.7's own reasoning.

    `N>=10` / `0.70` / `0.5` reproduce every CEO worked example exactly, including `7-support/
    9-voting -> REPEATED_OBSERVATION` (`N<10` overrides the ratio even though `7/9 > 0.70`, Section
    13a's own explicit example) and the new `n_voting=10, support=5 -> WEAKENED` (`0.5` boundary,
    inclusive) / `support=4 -> REJECTED` (just below `0.5`) vectors (Section 19.15)."""
    if n_voting <= 1:
        return "NEW_HYPOTHESIS"
    if n_voting < MIN_INDEPENDENT_UNDERLYING_MOVES:
        return "REPEATED_OBSERVATION"
    ratio = support / n_voting
    if ratio >= MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED:
        return "PROSPECTIVELY_SUPPORTED"
    if ratio >= 0.5:
        return "PROSPECTIVELY_WEAKENED"
    return "PROSPECTIVELY_REJECTED"
