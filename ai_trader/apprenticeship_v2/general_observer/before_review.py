"""BEFORE ordering-violation protection (final closure mandate item 2; design doc Section 8 step 8:
"If, for any reason, the BEFORE fields are filled after outcome information has already become
visible to the reviewer... prospective_eligibility = NO. The row is kept for diagnostic purposes
only and is explicitly excluded from prediction-accuracy scoring, lesson support counting, and Alpha
handoff evidence -- never silently included.").

**Why this needed new plumbing, not just a check.** The qualitative-review pass itself (the LLM step
that fills BEFORE fields) is explicitly out of scope for this delivery (design doc Section 8 step 6;
Section 16's own ownership table: "BEFORE qualitative judgment | AI Trader runtime LLM") -- so no
code anywhere transitions a general-observer episode's `qualitative_review_status` away from
`PENDING_LLM_REVIEW`, and `GENERAL_OBSERVER_LEDGER_CSV` (append-only) has no column to even hold a
REVISED `prospective_eligibility` value after the fact. This module provides the MECHANICAL GUARD a
future qualitative-review-completion caller must invoke (`complete_before_review`), plus the
persistence path that guard's result needs (`durable_store.append_general_prediction` /
`GENERAL_OBSERVER_PREDICTIONS_CSV`) and the read-side overlay that makes the corrected value
authoritative for lesson evidence (`effective_general_episode_rows`) -- so the protection is real,
tested, and wired end-to-end into `lesson_voting.py`, ready for that future caller, rather than a
theoretical function nothing ever calls.

**The mechanical proxy for "future/outcome information had already become visible."** An LLM's own
context/awareness is not a variable mechanical code can inspect. The MECHANICALLY CHECKABLE
equivalent this module uses: has ANY scorecard (AFTER) row for this same episode already been
written (`scored_at_utc`) BEFORE the moment BEFORE review completes (`reviewed_at_utc`)? If so, the
system had ALREADY mechanically computed an outcome for this episode before the BEFORE fields were
even frozen -- the durable ordering guarantee is violated regardless of whether a reviewer looked at
it, so `prospective_eligibility` is forced to `NO`. This is a real, restart-safe, fully mechanical
check: always a fresh read of the durable scorecard ledger, never an in-memory sequence flag.
"""

from __future__ import annotations

import datetime
import dataclasses
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2 import durable_store

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.schemas import EpisodeRecord


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(ts)


def evaluate_prospective_eligibility(episode_id: str, reviewed_at_utc: str) -> str:
    """Returns `"NO"` if any scorecard row for `episode_id` was `scored_at_utc` strictly before
    `reviewed_at_utc` (future/outcome information mechanically available before BEFORE was frozen);
    `"YES"` otherwise. Restart-safe: always a fresh `durable_store.read_scorecard_rows` call, never a
    cached/in-memory result -- a restart that re-runs this check reproduces the identical verdict."""
    reviewed_at = _parse_iso(reviewed_at_utc)
    for row in durable_store.read_scorecard_rows(episode_id):
        scored_at_raw = row.get("scored_at_utc")
        if not scored_at_raw:
            continue
        if _parse_iso(scored_at_raw) < reviewed_at:
            return "NO"
    return "YES"


def complete_before_review(episode: "EpisodeRecord", *, reviewed_at_utc: str | None = None) -> "EpisodeRecord":
    """Finalizes a qualitatively-reviewed episode's mechanical `prospective_eligibility` gate.
    Callers (the future qualitative-review-completion process) must call this exactly once per
    episode and persist the RETURNED record via `durable_store.append_general_prediction` --
    `qualitative_review_status` transitions to `"FROZEN"` here, matching design doc Section 8 step 7
    (`prospective_eligibility = YES` in the non-violated case) and step 8 (`NO` in the violated one).
    Never re-evaluates an already-completed episode (the append-only `GENERAL_OBSERVER_PREDICTIONS_
    CSV` this produces a row for is itself the single-write record -- callers must not call this
    twice for the same episode, mirroring `append_prediction()`'s own existing "called once" contract)."""
    reviewed_at_utc = reviewed_at_utc or _now_iso()
    eligibility = evaluate_prospective_eligibility(episode.episode_id, reviewed_at_utc)
    return dataclasses.replace(
        episode, reviewed_at_utc=reviewed_at_utc, prospective_eligibility=eligibility,
        qualitative_review_status="FROZEN",
    )


def effective_general_episode_rows(general_episode_rows: list[dict]) -> list[dict]:
    """Overlays each row's `prospective_eligibility` with its BEFORE-review-completion record's own
    value, when one exists -- the review-time-computed, AUTHORITATIVE value (this module's own
    `complete_before_review`) takes precedence over the mechanical shell's always-`"YES"` default
    written at episode-construction time (`episode_builder.build_episode_record`). A row with no
    completion record yet (BEFORE review has not happened for it) keeps its existing value unchanged.
    Restart-safe: always a fresh `durable_store.read_all_general_predictions` call.

    This is the enforcement point for design doc Section 8 step 8's "such an episode cannot enter
    prospective lesson evidence" -- `lesson_voting.select_canonical_episodes` calls this
    unconditionally on its own input, so no future caller can accidentally bypass the override by
    forgetting to apply it themselves."""
    overrides = {
        row["episode_id"]: row.get("prospective_eligibility")
        for row in durable_store.read_all_general_predictions()
        if row.get("episode_id")
    }
    if not overrides:
        return general_episode_rows
    out = []
    for row in general_episode_rows:
        episode_id = row.get("episode_id")
        if episode_id in overrides:
            row = dict(row)
            row["prospective_eligibility"] = overrides[episode_id]
        out.append(row)
    return out
