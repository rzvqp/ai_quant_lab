"""BEFORE mechanical episode-shell construction (design doc Section 8, steps 1-5). Composes the 4
detector contracts (`detectors.py`) + eligible major levels (`major_levels.py`) + dedup/underlying-
move-id (`dedup.py`) + frozen snapshot/hash (`snapshot.py`) into fully-formed, `PENDING_LLM_REVIEW`
`EpisodeRecord`s -- the mechanical half of the BEFORE contract (step 6, the LLM pass that fills
qualitative fields, is explicitly out of scope here and everywhere else in this delivery).

Persistence itself (`durable_store.append_general_episode_to_ledger`) is the CALLER's responsibility
-- mirrors `loop.py::tick()`'s own convention of calling that append function itself rather than
bundling persistence into episode construction. This module stays a pure function set: given causal
bars in, `EpisodeRecord`s out, no I/O.

SESSION_TRANSITION_REVERSAL composition (Section 4D + Section 8 rule 3): the design doc's own
"Reference levels saved" for this class is "...reference to the child episode's `episode_id`..." --
which requires the child (`SWEEP_REJECTION`/`STRUCTURAL_BREAK`) to exist as its OWN persisted row,
not be replaced/subsumed by the reversal. This module always emits BOTH when a reversal fires: the
child as its own normal episode, and the reversal as a SEPARATE episode carrying
`reference_levels["child_episode_id"]`. Section 4D also states the two "always share the same
`underlying_move_id` by construction" -- enforced here by literally reusing the child's own already-
computed `underlying_move_id` for the reversal, rather than recomputing it a second time (a second,
independent `compute_underlying_move_id` call could in principle mint a different fallback family id
on the two calls; reuse removes that risk entirely rather than relying on the two calls happening to
agree).

One VE interpretive decision, not settled verbatim by the frozen text, is disclosed here (and again
in the implementation report): when BOTH a `SWEEP_REJECTION` and a `STRUCTURAL_BREAK` independently
fire on the same session-transition bar (against two different eligible levels), `SWEEP_REJECTION` is
preferred as the reversal's `child` -- an arbitrary but deterministic tie-break. Neither observation
is lost either way: both are still persisted as their own standalone episodes; the choice only
affects which ONE of them additionally receives a `SESSION_TRANSITION_REVERSAL` companion row.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import uuid
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2.general_observer.dedup import compute_underlying_move_id, is_duplicate
from ai_trader.apprenticeship_v2.general_observer.detectors import (
    DetectedEvent, detect_displacement, detect_session_transition_reversal, detect_structural_break,
    detect_sweep_rejection, session_closing_direction,
)
from ai_trader.apprenticeship_v2.general_observer.major_levels import MajorLevel, compute_eligible_major_levels
from ai_trader.apprenticeship_v2.general_observer.primitives import session_for_ts
from ai_trader.apprenticeship_v2.general_observer.snapshot import build_snapshot, compute_snapshot_hash
from ai_trader.apprenticeship_v2.schemas import EpisodeRecord

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _preceding_session_bars(m15_bars: "list[ReadOnlyBar]", new_session_start_index: int) -> "list[ReadOnlyBar]":
    """All consecutive M15 bars, in chronological order, belonging to the SAME session as
    `m15_bars[new_session_start_index - 1]` -- the session immediately preceding the one
    `m15_bars[new_session_start_index]` opens (design doc Section 4D's "immediately preceding
    session" input). Backward-walk, same technique `major_levels.previous_session_high_low` already
    uses for H1 -- gap-tolerant, does not assume a fixed bar count per session."""
    if new_session_start_index <= 0:
        return []
    prior_session = session_for_ts(m15_bars[new_session_start_index - 1].ts_open)
    out: list[ReadOnlyBar] = []
    i = new_session_start_index - 1
    while i >= 0 and session_for_ts(m15_bars[i].ts_open) == prior_session:
        out.append(m15_bars[i])
        i -= 1
    out.reverse()
    return out


@dataclasses.dataclass(frozen=True, slots=True)
class DetectionResult:
    base_events: tuple[DetectedEvent, ...]
    session_reversal: DetectedEvent | None
    session_child: DetectedEvent | None
    """The specific member of `base_events` (`is`-identical) that `session_reversal` attached to, if
    any -- `None` whenever `session_reversal` is `None`."""


def detect_all_events_for_bar(
    bar: "ReadOnlyBar", m15_causal_bars_up_to_and_including_bar: "list[ReadOnlyBar]", levels: list[MajorLevel],
) -> DetectionResult:
    """Evaluates all 4 frozen contracts for one newly-closed causal M15 bar (design doc Section 8
    step 1's "mechanical detector fires"). Multiple base classes CAN co-fire on the same bar (e.g. a
    sweep of one level and a displacement, independent conditions over different inputs) -- each
    becomes its own episode, later joined under a shared `underlying_move_id`, never collapsed into
    one row (Section 8's family/dedup model exists precisely to represent several observations of
    one underlying move)."""
    bar_index = len(m15_causal_bars_up_to_and_including_bar) - 1
    assert m15_causal_bars_up_to_and_including_bar[bar_index] is bar or m15_causal_bars_up_to_and_including_bar[bar_index] == bar
    prior_bar = m15_causal_bars_up_to_and_including_bar[bar_index - 1] if bar_index >= 1 else None

    sweep = detect_sweep_rejection(bar, levels)
    brk = detect_structural_break(prior_bar, bar, levels) if prior_bar is not None else None
    disp = detect_displacement(bar, m15_causal_bars_up_to_and_including_bar)

    session_reversal: DetectedEvent | None = None
    session_child: DetectedEvent | None = None
    if prior_bar is not None:
        new_session = session_for_ts(bar.ts_open)
        prior_session = session_for_ts(prior_bar.ts_open)
        if new_session != prior_session:
            candidate_child = sweep if sweep is not None else brk  # VE tie-break -- see module docstring
            if candidate_child is not None:
                preceding_bars = _preceding_session_bars(m15_causal_bars_up_to_and_including_bar, bar_index)
                preceding_direction = session_closing_direction(preceding_bars)
                fired = detect_session_transition_reversal(
                    candidate_child, preceding_session_name=prior_session,
                    preceding_session_direction=preceding_direction, new_session_name=new_session,
                )
                if fired is not None:
                    session_reversal = fired
                    session_child = candidate_child

    base_events = tuple(e for e in (sweep, brk, disp) if e is not None)
    return DetectionResult(base_events=base_events, session_reversal=session_reversal, session_child=session_child)


def _make_episode_id(event: DetectedEvent) -> str:
    return f"GO-{event.episode_type}-{event.trigger_bar_ts_close}-{uuid.uuid4().hex[:8]}"


def build_episode_record(
    event: DetectedEvent, *, symbol: str, current_price: float,
    h4: "list[ReadOnlyBar]", h1: "list[ReadOnlyBar]", m15: "list[ReadOnlyBar]", m5: "list[ReadOnlyBar]",
    underlying_move_id: str, extra_reference_levels: dict[str, object] | None = None,
) -> EpisodeRecord:
    """Design doc Section 8 steps 1-5: shell -> snapshot -> freeze -> hash -> `PENDING_LLM_REVIEW`
    (the dataclass's own default). `setup_direction` is deliberately never set (S5 isolation, Section
    15) -- `directional_hypothesis` carries direction instead, as the plain "BULLISH"/"BEARISH"
    string `DetectedEvent.direction` already is (never `str(some_enum)` -- the live `Direction.LONG`
    serialization defect, mandate Section 24, is deliberately not repeated here)."""
    snapshot = build_snapshot(h4, h1, m15, m5)
    reference_levels = dict(event.reference_levels)
    if extra_reference_levels:
        reference_levels.update(extra_reference_levels)
    return EpisodeRecord(
        episode_id=_make_episode_id(event),
        timestamp_utc=_now_iso(),
        frozen_at_bar_ts=event.trigger_bar_ts_close,
        episode_type=event.episode_type,
        symbol=symbol,
        current_price=current_price,
        setup_direction=None,
        reference_levels=reference_levels,
        snapshot=snapshot,
        trigger_timeframe="M15",
        what_triggered_observation=event.what_triggered_observation,
        directional_hypothesis=event.direction,
        frozen_snapshot_hash=compute_snapshot_hash(snapshot),
        prospective_eligibility="YES",
        # Design doc Section 8 step 8 / step 7's `NO` case (BEFORE fields filled after outcome
        # information was visible) is a QUALITATIVE-review-time concern -- this mechanical shell is,
        # by construction, built only from already-causal `fetch_causal_closed_bars` inputs and is
        # never itself the point where a later ordering violation could occur, so `YES` is correct
        # at construction time. A restart-recovery path that might re-freeze a partially-built shell
        # is not yet implemented (disclosed as an open item in the implementation report).
        underlying_move_id=underlying_move_id,
    )


def _record_to_pseudo_row(record: EpisodeRecord) -> dict[str, object]:
    """A same-tick, not-yet-persisted `EpisodeRecord` shaped like a ledger CSV row, so a SECOND event
    on the SAME bar (e.g. sweep + displacement together) can correctly dedup/chain against the FIRST
    one without a real CSV round-trip mid-tick. Field shape matches
    `durable_store.append_general_episode_to_ledger`'s own row dict."""
    return {
        "episode_type": record.episode_type, "frozen_at_bar_ts": str(record.frozen_at_bar_ts),
        "directional_hypothesis": record.directional_hypothesis,
        "reference_levels_json": json.dumps(record.reference_levels),
        "underlying_move_id": record.underlying_move_id,
    }


def build_episodes_for_bar(
    bar: "ReadOnlyBar", *, symbol: str, h4: "list[ReadOnlyBar]", h1: "list[ReadOnlyBar]",
    m15_causal_bars_up_to_and_including_bar: "list[ReadOnlyBar]", m5: "list[ReadOnlyBar]",
    existing_general_episode_rows: list[dict],
) -> list[EpisodeRecord]:
    """Top-level per-bar orchestrator (design doc Section 8, full pipeline): major levels -> all 4
    contracts -> dedup + underlying-move-id -> snapshot/hash -> `PENDING_LLM_REVIEW` shells. Returns
    already-deduplicated episodes ready for the caller to persist via
    `durable_store.append_general_episode_to_ledger` (one call per returned record) -- this function
    never writes to the ledger itself.

    `m15_causal_bars_up_to_and_including_bar` must end with `bar` itself and should cover at least
    the last `UNDERLYING_MOVE_WINDOW_M15_BARS` (32) bars for `compute_underlying_move_id` to see
    every real chaining candidate; an under-provisioned list fails SAFE (fewer/no candidates found ->
    a new family started rather than an incorrect join), per `dedup.py`'s own documented contract.
    `existing_general_episode_rows` must be the durable ledger's rows from BEFORE this bar (e.g.
    `durable_store.read_all_general_episode_rows()`), never mutated by the caller mid-call."""
    levels = compute_eligible_major_levels(h1, as_of_ts_close=bar.ts_close)
    detection = detect_all_events_for_bar(bar, m15_causal_bars_up_to_and_including_bar, levels)

    out: list[EpisodeRecord] = []
    rows_so_far = list(existing_general_episode_rows)
    child_episode_id: str | None = None
    child_move_id: str | None = None
    session_reversal_suppressed = False

    for event in detection.base_events:
        move_id = compute_underlying_move_id(
            event, existing_general_episode_rows=rows_so_far,
            m15_bars_since_earliest_candidate=m15_causal_bars_up_to_and_including_bar,
        )
        if is_duplicate(event, underlying_move_id=move_id, existing_general_episode_rows=rows_so_far):
            if event is detection.session_child:
                # Section 6: SESSION_TRANSITION_REVERSAL "inherits its materiality entirely from its
                # child" -- a duplicate (non-material-as-new) child means no reversal either.
                session_reversal_suppressed = True
            continue
        record = build_episode_record(
            event, symbol=symbol, current_price=bar.close, h4=h4, h1=h1,
            m15=m15_causal_bars_up_to_and_including_bar, m5=m5, underlying_move_id=move_id,
        )
        out.append(record)
        rows_so_far.append(_record_to_pseudo_row(record))
        if event is detection.session_child:
            child_episode_id = record.episode_id
            child_move_id = move_id

    if detection.session_reversal is not None and not session_reversal_suppressed and child_episode_id is not None:
        assert child_move_id is not None
        record = build_episode_record(
            detection.session_reversal, symbol=symbol, current_price=bar.close, h4=h4, h1=h1,
            m15=m15_causal_bars_up_to_and_including_bar, m5=m5, underlying_move_id=child_move_id,
            extra_reference_levels={"child_episode_id": child_episode_id},
        )
        out.append(record)

    return out
