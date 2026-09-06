"""AFTER scorecard: per-horizon incremental scoring (design doc Section 9), restructured from the
existing all-at-once `resolution.py`/`loop.py` gate into independent per-`(episode_id,
review_horizon)` rows -- additive alongside (never replacing) that existing all-at-once path. S5's
own resolution behavior is unchanged: `resolution.py` itself is not modified by this file, only
called, exactly as Section 15 (S5 isolation) requires.

**`classify_expectation_correct` -- patched per design doc Section 19 (Fifth Addendum,
`SCORECARD_DEFINITIONAL_LOCK = PASS`).** The prior delivery correctly identified that Sections 9/13a
described the `HorizonMetrics -> expectation_correct` mapping as "forced"/"not a new invention"
without ever actually stating it, and left the classifier raising `NotImplementedError` rather than
guess a threshold. Section 19 closes that gap by writing the mapping down explicitly, built entirely
from `directional_follow_through` (boolean, mathematically forced) and `round_trip_magnitude`'s own
already-existing `0.0`/`1.0` boundaries plus a direct `mae`-vs-`mfe` comparison (scale-invariant --
sidesteps the `atr=None` raw-price question noted in Section 19.1's own audit). No new numeric
constant is introduced anywhere in this classifier; `classify_expectation_correct` below is a direct
transcription of Section 19.14's own required pseudocode.
"""

from __future__ import annotations

import dataclasses
import datetime
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.resolution import compute_horizon_metrics
from ai_trader.apprenticeship_v2.schemas import (
    ALLOWED_EXPECTATIONS, RESOLUTION_HORIZONS_M15, HorizonMetrics, ScorecardEntry,
)

if TYPE_CHECKING:
    from ai_trader.apprenticeship_v2.mt5_read_only_source import ReadOnlyBar

_HORIZON_NAMES = ("H1", "H2", "H4", "H8")  # 1:1 with RESOLUTION_HORIZONS_M15 = (4, 8, 16, 32)

_DIRECTION_TO_S5_VOCABULARY = {"BULLISH": "LONG", "BEARISH": "SHORT"}
"""`resolution.compute_horizon_metrics` is S5's own pre-existing, byte-unchanged function and speaks
S5's own `setup_direction` vocabulary (confirmed by reading its source directly: `if setup_direction
== "LONG": ... elif setup_direction == "SHORT": ... else: <direction-unknown symmetric fallback>`).
General-observer's own frozen direction vocabulary is "BULLISH"/"BEARISH" (Section 4). Passing
"BULLISH"/"BEARISH" straight through would silently hit that unknown-direction fallback for every
single general-observer episode -- `directional_follow_through` always `None`, `mfe`/`mae` always the
symmetric max/min rather than the correctly-signed pair. This local, call-site-only translation is
required for `compute_horizon_metrics`'s own EXISTING, unmodified semantics to work correctly for a
general-observer caller; `resolution.py` itself is never touched, so S5's own calls are unaffected."""


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def already_scored(episode_id: str, review_horizon: str) -> bool:
    """Restart-safe by construction -- always a fresh ledger read (Section 9's append-only,
    never-double-scored requirement), never an in-memory flag."""
    rows = durable_store.read_scorecard_rows(episode_id)
    return any(r.get("review_horizon") == review_horizon for r in rows)


def mechanical_outcome_summary(metrics: HorizonMetrics) -> str:
    """Purely descriptive restatement of `HorizonMetrics` -- Section 9: "derived purely from
    resolution.py's existing HorizonMetrics... no subjective content." No interpretation, no
    classification, just the numbers."""
    return (
        f"forward_return={metrics.forward_return}, mfe={metrics.mfe}, mae={metrics.mae}, "
        f"max_up_move={metrics.max_up_move}, max_down_move={metrics.max_down_move}, "
        f"close_location={metrics.close_location}, "
        f"directional_follow_through={metrics.directional_follow_through}, "
        f"round_trip_magnitude={metrics.round_trip_magnitude}"
    )


def due_horizons_for_episode(
    episode_row: dict, m15_bars: "list[ReadOnlyBar]",
) -> list[tuple[str, HorizonMetrics]]:
    """Fully mechanical: which `(review_horizon, HorizonMetrics)` pairs are due to be scored right
    now for this episode -- not already scored (fresh ledger read) AND enough causal forward bars
    exist. A horizon without enough bars yet is simply absent from the result, staying pending for a
    later tick (Section 9's own "unresolved horizons remain pending"), never scored early against a
    truncated window."""
    frozen_bar_ts = int(episode_row["frozen_at_bar_ts"])
    forward = sorted((b for b in m15_bars if b.ts_close > frozen_bar_ts), key=lambda b: b.ts_close)
    direction = episode_row.get("directional_hypothesis") or None
    s5_direction = _DIRECTION_TO_S5_VOCABULARY.get(direction) if direction else None

    due: list[tuple[str, HorizonMetrics]] = []
    for horizon_bars, horizon_name in zip(RESOLUTION_HORIZONS_M15, _HORIZON_NAMES):
        if already_scored(episode_row["episode_id"], horizon_name):
            continue
        if len(forward) < horizon_bars:
            continue
        metrics = compute_horizon_metrics(
            entry_price=float(episode_row["current_price"]), setup_direction=s5_direction,
            forward_bars=forward, horizon_n=horizon_bars, atr=None,
        )
        due.append((horizon_name, metrics))
    return due


@dataclasses.dataclass(frozen=True, slots=True)
class EpisodeContext:
    """Design doc Section 19.14's own `episode_context` parameter -- carries exactly the fields the
    classifier's universal preconditions need, kept separate from `HorizonMetrics` (which is purely
    the numeric outcome, not eligibility/horizon-identity state)."""

    prospective_eligibility: str | None
    review_horizon: str
    structural_resolution_state: str | None = None
    """One of `"CONFIRMATION"` / `"INVALIDATION"` / `"UNRESOLVED_AT_H8"` / `None` -- only consulted
    when `review_horizon == "STRUCTURAL_FINAL"`. No caller in this delivery ever produces a
    `STRUCTURAL_FINAL` row today (`due_horizons_for_episode` only emits H1/H2/H4/H8) -- the
    structural-resolution computation itself for general-observer episodes remains a disclosed,
    separate, not-yet-built engineering gap (design doc Section 19.11); this classifier's own
    STRUCTURAL_FINAL branch is defined and tested regardless, ready for that future caller."""


def classify_expectation_correct(expectation: str, metrics: HorizonMetrics, episode_context: EpisodeContext) -> str:
    """Design doc Section 19.5/19.13/19.14 (Fifth Addendum) -- the now-frozen mapping. Transcribed
    directly from Section 19.14's own required pseudocode; no threshold introduced beyond what that
    section itself declares mathematically forced. Mutual exclusivity and exhaustiveness proved in
    Section 19.16 (every reachable state maps to exactly one verdict, by construction of the
    if/return branches below -- verified independently by this module's own tests, not merely
    asserted)."""
    # --- Universal preconditions (Section 19.4), checked in this exact order ---
    if expectation == "UNCLEAR":
        return "NOT_SCORABLE"
    if expectation not in ALLOWED_EXPECTATIONS:
        return "NOT_SCORABLE"
    if episode_context.prospective_eligibility != "YES":
        return "NOT_SCORABLE"

    if episode_context.review_horizon == "STRUCTURAL_FINAL":
        state = episode_context.structural_resolution_state
        if state is None or state == "UNRESOLVED_AT_H8":
            return "NOT_SCORABLE"
        dft: bool | None = state == "CONFIRMATION"
        rtm = 0.0 if dft else 1.0  # CONFIRMATION behaves as the "YES" pole, INVALIDATION as the "NO" pole
        mae_gt_mfe = state == "INVALIDATION"
    else:
        dft = metrics.directional_follow_through
        rtm = metrics.round_trip_magnitude
        mae_gt_mfe = metrics.mae > metrics.mfe
        if dft is None:
            return "NOT_SCORABLE"

    # --- Per-expectation contract (Section 19.5 / 19.13) ---
    if expectation == "FOLLOW_THROUGH_LIKELY":
        return "YES" if (dft is True and rtm < 1.0) else "NO"
    if expectation == "FAILURE_LIKELY":
        return "YES" if (dft is False or rtm >= 1.0) else "NO"
    if expectation == "REVERSAL_LIKELY":
        return "YES" if (dft is False and mae_gt_mfe) else "NO"
    if expectation == "RANGE_LIKELY":
        return "YES" if (dft is False and not mae_gt_mfe) else "NO"
    if expectation == "ROUND_TRIP_LIKELY":
        if rtm >= 1.0:
            return "YES"
        if rtm > 0.0:
            return "PARTIAL"
        return "NO"

    return "NOT_SCORABLE"  # unreachable given the precondition check above; defensive only


def score_due_horizons_for_episode(
    episode_row: dict, prediction_row: dict, m15_bars: "list[ReadOnlyBar]",
) -> list[ScorecardEntry]:
    """Builds one `ScorecardEntry` per due horizon (`due_horizons_for_episode`). Only meaningful for
    episodes whose `qualitative_review_status == "FROZEN"` (the caller's responsibility -- checked by
    the caller, not here, since gating on review status is an orchestration concern, not a scoring
    one). `original_expectation`/`original_confidence` are copied verbatim from the BEFORE prediction
    record, never re-derived (Section 9). `partial_reason` stays `None` -- Section 19 does not
    request populating it, and `mechanical_outcome_summary` already carries full numeric
    auditability for the `PARTIAL` (`ROUND_TRIP_LIKELY` only) case."""
    entries: list[ScorecardEntry] = []
    for horizon_name, metrics in due_horizons_for_episode(episode_row, m15_bars):
        expectation = prediction_row.get("ai_trader_expectation", "")
        episode_context = EpisodeContext(
            prospective_eligibility=episode_row.get("prospective_eligibility"), review_horizon=horizon_name,
        )
        expectation_correct = classify_expectation_correct(expectation, metrics, episode_context)
        entries.append(ScorecardEntry(
            episode_id=episode_row["episode_id"], review_horizon=horizon_name,
            original_expectation=expectation, original_confidence=prediction_row.get("confidence", ""),
            mechanical_outcome_summary=mechanical_outcome_summary(metrics),
            expectation_correct=expectation_correct, partial_reason=None, scored_at_utc=_now_iso(),
        ))
    return entries
