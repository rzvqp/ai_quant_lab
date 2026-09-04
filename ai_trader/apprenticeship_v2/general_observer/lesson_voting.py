"""Lesson vote aggregation (design doc Section 13/13a, CEO Addendum 2). Governs how one
`underlying_move_id` produces a single `SUPPORT`/`COUNTEREXAMPLE`/non-voting outcome, and how the
accumulated votes classify a `LessonHypothesis`'s `lesson_status`.

Depends on `scorecard.py`'s `ScorecardEntry.expectation_correct` values, which -- per that module's
own disclosed `VE_SEMANTIC_GAP_FOUND` -- are not currently produced by any working code path
(`classify_expectation_correct` raises rather than guesses). Every function below is fully
implemented and independently testable against manually-constructed scorecard rows; there is
currently no real caller path that produces those rows in production -- an honest, disclosed
consequence of the upstream gap, not a second, independent gap in this file.

`MIN_INDEPENDENT_UNDERLYING_MOVES = 10`, `MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED = 0.70`,
`MAX_LESSON_VOTES_PER_UNDERLYING_MOVE = 1` -- all CEO-declared, Section 13/13a, applied verbatim.

**Two narrow disclosed gaps in `classify_lesson_status`** (see its own docstring for detail): (1) the
exact vote-count boundary between `NEW_HYPOTHESIS` and `REPEATED_OBSERVATION` is not stated
numerically; (2) the frozen stage table gives `PROSPECTIVELY_WEAKENED`/`PROSPECTIVELY_REJECTED` as
one undifferentiated row with no criterion separating them. Both are resolved here with a disclosed,
conservative default -- distinct from the exact, fully-specified `N>=10`/`ratio>=0.70` threshold
itself, which is applied verbatim with zero interpretation.
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
    """Section 13's stage table, applied to `(n_voting_independent_moves, support_moves)`.

    The `N>=10` / `ratio>=0.70` threshold ITSELF is exact and applied verbatim -- reproduces every
    one of the CEO's worked examples exactly (7-support/10-voting through 10-support/10-voting ->
    `PROSPECTIVELY_SUPPORTED`; 6-support/10-voting -> not eligible via ratio; 7-support/9-voting ->
    not eligible via `N<10` despite `7/9 > 0.70`, Section 13a's own explicit example).

    Two narrower points are NOT stated numerically/distinctly anywhere in the frozen text, and are
    resolved here with a disclosed default rather than silently guessed:
    (1) `NEW_HYPOTHESIS` vs `REPEATED_OBSERVATION` boundary -- "First prospectively-eligible...
        observation" (singular) could mean `n_voting==0` (just created, no vote yet) or `n_voting==1`
        (one vote already in, with `REPEATED_OBSERVATION` then meaning 2-9). This function uses
        `n_voting==0 -> NEW_HYPOTHESIS`, `1..9 -> REPEATED_OBSERVATION` -- the reading that keeps the
        full `0..9` range contiguous, with no gap and no double-count.
    (2) `PROSPECTIVELY_WEAKENED` vs `PROSPECTIVELY_REJECTED` -- the frozen table gives one combined
        row ("`PROSPECTIVELY_WEAKENED / PROSPECTIVELY_REJECTED | >=10 ... <70% support`") with no
        further criterion anywhere distinguishing them. This function always returns
        `PROSPECTIVELY_WEAKENED` for that condition -- the more conservative-sounding of the two
        undifferentiated names, not a discovered rule."""
    if n_voting == 0:
        return "NEW_HYPOTHESIS"
    if n_voting < MIN_INDEPENDENT_UNDERLYING_MOVES:
        return "REPEATED_OBSERVATION"
    ratio = support / n_voting
    if ratio >= MIN_SUPPORT_RATIO_FOR_PROSPECTIVELY_SUPPORTED:
        return "PROSPECTIVELY_SUPPORTED"
    return "PROSPECTIVELY_WEAKENED"
