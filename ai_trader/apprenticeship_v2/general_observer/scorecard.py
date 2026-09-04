"""AFTER scorecard: per-horizon incremental scoring (design doc Section 9), restructured from the
existing all-at-once `resolution.py`/`loop.py` gate into independent per-`(episode_id,
review_horizon)` rows -- additive alongside (never replacing) that existing all-at-once path. S5's
own resolution behavior is unchanged: `resolution.py` itself is not modified by this file, only
called, exactly as Section 15 (S5 isolation) requires.

**Disclosed gap (`VE_SEMANTIC_GAP_FOUND`, narrow scope -- see `classify_expectation_correct` below).**
Section 9 states the six `ai_trader_expectation` values are "mutually distinguishable using only...
forward_return sign, round_trip_magnitude, directional_follow_through -- the mechanical scorer needs
no new computation" and Section 13a calls the resulting `expectation_correct` value "an unambiguous,
forced mapping... not a new invention." Having read the full 799-line frozen document, that mapping
itself is never actually stated anywhere -- no threshold says how large a `forward_return` must be to
count as genuine "follow-through" versus a "range," and no threshold says how much of `mfe` must be
given back (`round_trip_magnitude`) to count as a full versus partial round-trip. Every one of the
three named metrics is continuous; forcing a YES/NO/PARTIAL boundary without CEO input means inventing
an uncalibrated numeric cutoff -- exactly the class of unjustified parameter this mandate forbids VE
from introducing on its own (Section 6 applies this exact discipline to the 4 event contracts; no
equivalent pass was ever applied to this specific mapping anywhere in the document). Per this
mandate's own instruction ("VE implements frozen semantics exactly and must STOP with
VE_SEMANTIC_GAP_FOUND if any undefined semantic decision is needed -- never improvise"),
`classify_expectation_correct()` is deliberately left unimplemented (raises `NotImplementedError`)
rather than guessing. Everything upstream of it -- HorizonMetrics computation (via the existing,
unmodified `resolution.compute_horizon_metrics`), the BULLISH/BEARISH -> LONG/SHORT vocabulary
bridge it requires, `mechanical_outcome_summary`, per-horizon due/pending gating, and restart-safe
persistence -- is fully mechanical, fully specified, and fully implemented and tested below.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from ai_trader.apprenticeship_v2 import durable_store
from ai_trader.apprenticeship_v2.resolution import compute_horizon_metrics
from ai_trader.apprenticeship_v2.schemas import RESOLUTION_HORIZONS_M15, HorizonMetrics, ScorecardEntry

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


def classify_expectation_correct(ai_trader_expectation: str, metrics: HorizonMetrics) -> str:
    """NOT IMPLEMENTED -- see module docstring (`VE_SEMANTIC_GAP_FOUND`, disclosed in the
    implementation report). Raising here, rather than guessing an uncalibrated threshold, is the
    correct application of this mandate's own "never improvise a semantic decision" rule."""
    raise NotImplementedError(
        "classify_expectation_correct: VE_SEMANTIC_GAP_FOUND -- the design doc does not specify the "
        "HorizonMetrics -> {YES,NO,PARTIAL,NOT_SCORABLE} threshold mapping despite describing it as "
        "'forced'/'not a new invention' (Sections 9, 13a). See scorecard.py module docstring."
    )


def score_due_horizons_for_episode(
    episode_row: dict, prediction_row: dict, m15_bars: "list[ReadOnlyBar]",
) -> list[ScorecardEntry]:
    """Builds one `ScorecardEntry` per due horizon (`due_horizons_for_episode`). Only meaningful for
    episodes whose `qualitative_review_status == "FROZEN"` (the caller's responsibility -- checked by
    the caller, not here, since gating on review status is an orchestration concern, not a scoring
    one). `original_expectation`/`original_confidence` are copied verbatim from the BEFORE prediction
    record, never re-derived (Section 9).

    Currently always raises via `classify_expectation_correct` as soon as any horizon is due -- the
    gap is upstream-only-except-for-that-one-step (see module docstring); this function does not
    swallow the exception, so the gap can never be silently hidden behind a fabricated verdict.
    Callers must not call this until the classification gap is resolved; `due_horizons_for_episode`
    remains safely callable and independently useful in the meantime (e.g. to observe how many
    horizons are pending, without scoring any of them)."""
    entries: list[ScorecardEntry] = []
    for horizon_name, metrics in due_horizons_for_episode(episode_row, m15_bars):
        expectation = prediction_row.get("ai_trader_expectation", "")
        expectation_correct = classify_expectation_correct(expectation, metrics)  # raises
        entries.append(ScorecardEntry(
            episode_id=episode_row["episode_id"], review_horizon=horizon_name,
            original_expectation=expectation, original_confidence=prediction_row.get("confidence", ""),
            mechanical_outcome_summary=mechanical_outcome_summary(metrics),
            expectation_correct=expectation_correct, partial_reason=None, scored_at_utc=_now_iso(),
        ))
    return entries
