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

**CEO prospective-learning safety patch (shadow-apprenticeship activation).** Two further gates,
added to `effective_general_episode_rows` alongside the ordering guard above, close a real gap the
ordering guard alone does not cover: it only fires once a scorecard row exists, so it cannot catch a
backfilled (pre-activation) episode reviewed before it is ever scored. Both gates below can only ever
downgrade an episode's effective eligibility from `YES` to `NO`, never upgrade a `NO` back to `YES` --
"must not rely on AI Trader remembering to exclude it".

1. **Activation-cutoff gate** (`evaluate_activation_cutoff_eligibility`): an episode's own
   `frozen_at_bar_ts` must be strictly after the shadow-apprenticeship activation record's own T0
   (`load_activation_cutoff_ts`, reading `GENUINELY_PROSPECTIVE_CUTOFF.M15_EPISODE_CUTOFF_EXCLUSIVE`
   from the authoritative activation JSON -- never a hardcoded/duplicated timestamp). Catches every
   backfilled first-tick episode, including one a future reviewer mistakenly completes BEFORE review
   for, even though no scorecard row will exist yet at that moment for the ordering guard to see.
2. **BEFORE-deadline gate** (`evaluate_before_deadline_eligibility`): once a BEFORE review record
   exists, its own `reviewed_at_utc` must be no later than `frozen_at_bar_ts + H1_WINDOW_SECONDS` --
   reusing `schemas.RESOLUTION_HORIZONS_M15[0]` (the already-frozen "H1 = 4 M15 bars" mapping) for the
   threshold itself, introducing no new timing constant. A late BEFORE stays on the durable record for
   qualitative/debugging purposes (never rewritten/deleted) but can never vote.

Both gates are pure functions of already-persisted, restart-stable facts (an episode's own
`frozen_at_bar_ts`, its prediction row's `reviewed_at_utc`, and the static activation JSON) -- no
in-memory state, so a restart reproduces the identical verdict, and neither gate ever reads
`scored_at_utc`, so no scorecard-timing manipulation can influence either one.
"""

from __future__ import annotations

import datetime
import dataclasses
import json
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.schemas import EpisodeRecord

ACTIVATION_RECORD_JSON = durable_store.LIVE_STATE_DIR / "AI_TRADER_GENERAL_OBSERVER_SHADOW_APPRENTICESHIP_ACTIVATION.json"

_M15_BAR_SECONDS = 15 * 60
"""Physical duration of one M15 bar -- the same fact `mt5_read_only_source.BAR_SECONDS[TIMEFRAME_M15]`
and `tests/conftest.py::M15_SECONDS` each separately encode. Duplicated here as a plain int (not an
MT5 import) to keep this module importable without MetaTrader5 installed, matching this package's
established `TYPE_CHECKING`-guard convention elsewhere (e.g. `primitives.py`, `snapshot.py`,
`resolution.py`). This is unit conversion only, not a policy threshold -- the actual threshold being
reused is `schemas.RESOLUTION_HORIZONS_M15[0]` below."""

H1_WINDOW_SECONDS = RESOLUTION_HORIZONS_M15[0] * _M15_BAR_SECONDS
"""60 minutes -- `schemas.RESOLUTION_HORIZONS_M15[0]` (4 M15 bars = the frozen "H1" horizon) converted
to seconds. No new timing threshold: this reuses the exact same frozen horizon-count `scorecard.py`'s
own `due_horizons_for_episode` already scores against."""


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(ts)


def load_activation_cutoff_ts() -> int | None:
    """Reads T0 from the authoritative shadow-apprenticeship activation record (CEO mandate: "Use the
    existing activation record as the authoritative T0 source") -- never a value duplicated/hardcoded
    elsewhere. Returns `None` when the record does not exist yet: the apprenticeship has not been
    activated, so no general-observer episode exists yet to gate, and the activation-cutoff gate is
    correctly a no-op rather than blocking everything closed."""
    if not ACTIVATION_RECORD_JSON.exists():
        return None
    data = json.loads(ACTIVATION_RECORD_JSON.read_text(encoding="utf-8"))
    return int(data["GENUINELY_PROSPECTIVE_CUTOFF"]["M15_EPISODE_CUTOFF_EXCLUSIVE"])


def evaluate_activation_cutoff_eligibility(frozen_at_bar_ts: int | str, activation_cutoff_ts: int) -> str:
    """`"NO"` when `frozen_at_bar_ts` is at or before the official activation cutoff (the backfilled
    first-tick episodes, and any episode exactly at T0 -- only STRICTLY after T0 counts as genuinely
    prospective); `"YES"` otherwise."""
    return "NO" if int(frozen_at_bar_ts) <= int(activation_cutoff_ts) else "YES"


def evaluate_before_deadline_eligibility(frozen_at_bar_ts: int | str, reviewed_at_utc: str) -> str:
    """`"NO"` when the BEFORE review completed strictly after `frozen_at_bar_ts + H1_WINDOW_SECONDS`;
    `"YES"` otherwise. Exactly-at-the-boundary is treated as still eligible -- consistent with this
    package's existing inclusive-horizon convention (e.g. `scorecard.due_horizons_for_episode`'s own
    `len(forward) < horizon_bars` -- a horizon is already due at exactly N bars, not only after)."""
    reviewed_epoch = _parse_iso(reviewed_at_utc).timestamp()
    deadline = int(frozen_at_bar_ts) + H1_WINDOW_SECONDS
    return "NO" if reviewed_epoch > deadline else "YES"


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
    completion record yet (BEFORE review has not happened for it) keeps its existing value unchanged,
    subject to the two further gates below. Restart-safe: always a fresh
    `durable_store.read_all_general_predictions` call.

    This is the enforcement point for design doc Section 8 step 8's "such an episode cannot enter
    prospective lesson evidence" -- `lesson_voting.select_canonical_episodes` calls this
    unconditionally on its own input, so no future caller can accidentally bypass the override by
    forgetting to apply it themselves.

    **CEO prospective-learning safety patch**: after the ordering-guard overlay above, two further
    mechanical gates are applied, each only capable of downgrading `YES` to `NO`, never the reverse:

    1. Activation-cutoff (`evaluate_activation_cutoff_eligibility`): applied even when NO completion
       record exists at all, against the row's own raw `frozen_at_bar_ts` -- a backfilled episode that
       is never reviewed must still never show `YES` here, not merely happen to never vote because it
       lacks a scorecard row. Skipped (no-op) only when the activation record itself does not exist
       yet (`load_activation_cutoff_ts` returns `None`) or the row carries no `frozen_at_bar_ts`.
    2. BEFORE-deadline (`evaluate_before_deadline_eligibility`): applied only once a completion record
       exists and carries a `reviewed_at_utc` -- meaningless before a BEFORE review has actually
       happened, and that case is already excluded from voting upstream (no prediction/scorecard row
       can exist for an unreviewed episode)."""
    predictions_by_id = {
        row["episode_id"]: row for row in durable_store.read_all_general_predictions() if row.get("episode_id")
    }
    activation_cutoff_ts = load_activation_cutoff_ts()
    if not predictions_by_id and activation_cutoff_ts is None:
        return general_episode_rows
    out = []
    for row in general_episode_rows:
        episode_id = row.get("episode_id")
        prediction = predictions_by_id.get(episode_id)
        eligibility = prediction["prospective_eligibility"] if prediction is not None else row.get("prospective_eligibility")
        frozen_at_bar_ts = row.get("frozen_at_bar_ts")

        if eligibility == "YES" and activation_cutoff_ts is not None and frozen_at_bar_ts not in (None, ""):
            if evaluate_activation_cutoff_eligibility(frozen_at_bar_ts, activation_cutoff_ts) == "NO":
                eligibility = "NO"

        reviewed_at_utc = prediction.get("reviewed_at_utc") if prediction is not None else None
        if eligibility == "YES" and reviewed_at_utc and frozen_at_bar_ts not in (None, ""):
            if evaluate_before_deadline_eligibility(frozen_at_bar_ts, reviewed_at_utc) == "NO":
                eligibility = "NO"

        if eligibility != row.get("prospective_eligibility"):
            row = dict(row)
            row["prospective_eligibility"] = eligibility
        out.append(row)
    return out
