"""Result/state contracts for CSV_CAUSAL_REPLAY_ADAPTER_V1 (mandate sections 5-9).

`Bar`/`GapRecord`/`GapClassification` below are DELIBERATELY redeclared with the same field shape
as `ai_trader.live_signal_source.types` rather than imported from it -- confirmed by trying the
import first, not assumed: that package's own `__init__.py` unconditionally pulls in
`bar_feed` -> `execution_engine` -> `signal_engine` -> `market_scanner.schema_validation` ->
`fastjsonschema` (not installed in this environment, and none of it is CSV-replay-related in the
first place). This mirrors the exact precedent `live_signal_source.types.Bar`'s own docstring
already sets for `ai_trader.simulation.types.Bar` ("Structurally similar OHLCV shape by design,
redeclared rather than imported") -- same reasoning, applied one level up, to avoid this package
(whose entire job is reading a CSV file) transitively depending on MT5/broker/schema-validation
machinery it never calls."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Literal

from ai_trader.csv_causal_replay.identity import SourceIdentity


@dataclasses.dataclass(frozen=True, slots=True)
class Bar:
    """Same field shape as `ai_trader.live_signal_source.types.Bar` -- see this module's own
    docstring for why it is redeclared here rather than imported."""

    symbol: str
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    is_backfilled: bool = False

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("Bar.symbol must not be empty")
        if self.ts_close <= self.ts_open:
            raise ValueError(
                f"Bar.ts_close must be after ts_open, got ts_open={self.ts_open!r} ts_close={self.ts_close!r}"
            )


class GapClassification(str, Enum):
    """Same four categories as `ai_trader.live_signal_source.types.GapClassification` -- see this
    module's own docstring for why redeclared. `sealed_reader.classify_gap` reproduces
    `live_signal_source.gap_classification.classify_gap`'s exact logic (same CEO-specified
    MAINTENANCE formula, same empirically-measured 72h WEEKEND/EXTENDED_PAUSE threshold), not a
    reinterpretation."""

    MAINTENANCE = "MAINTENANCE"
    WEEKEND = "WEEKEND"
    EXTENDED_PAUSE = "EXTENDED_PAUSE"
    UNEXPECTED = "UNEXPECTED"


@dataclasses.dataclass(frozen=True, slots=True)
class GapRecord:
    symbol: str
    gap_start: int
    gap_end: int
    duration_seconds: int
    classification: GapClassification

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("GapRecord.symbol must not be empty")
        if self.gap_end <= self.gap_start:
            raise ValueError(
                f"GapRecord.gap_end must be after gap_start, got gap_start={self.gap_start!r} "
                f"gap_end={self.gap_end!r}"
            )
        if self.duration_seconds != self.gap_end - self.gap_start:
            raise ValueError(
                f"GapRecord.duration_seconds must equal gap_end - gap_start, got "
                f"duration_seconds={self.duration_seconds!r}, "
                f"gap_end - gap_start={self.gap_end - self.gap_start!r}"
            )

DecisionType = Literal[
    "ROUTINE_NO_EVENT",
    "TRADE_CONTRACT",
    "P007_PRECLASSIFICATION",
    "P007_RESOLUTION",
    "MGMT004_TRIGGER",
    "NO_TRADE_ACTIONABLE",
]

REQUIRED_EVENT_FIELDS: dict[str, tuple[str, ...]] = {
    "ROUTINE_NO_EVENT": (),
    "TRADE_CONTRACT": (
        "entry", "direction", "initial_stop", "structural_target", "baseline_management",
        "thesis", "invalidation",
    ),
    "P007_PRECLASSIFICATION": ("trigger_bar_id", "preclassification"),
    "P007_RESOLUTION": ("trigger_bar_id", "resolution"),
    "MGMT004_TRIGGER": ("trade_bar_id", "r_multiple_reached"),
    "NO_TRADE_ACTIONABLE": ("setup_description", "rationale"),
}
"""Identical decision-type vocabulary and required-field sets to `causal_replay.js`'s own
`REQUIRED_EVENT_FIELDS` (the mandate's named conceptual reference) -- ported, not redesigned, so a
reasoning layer already familiar with the TradingView-backed accelerator's handshake needs to learn
nothing new to use this CSV-backed one."""

MECHANICAL_EVENT_GATES: tuple[str, ...] = (
    "STRUCTURAL_LEVEL_TOUCH", "MATERIAL_VOLATILITY_TRANSITION", "GAP_OR_INTEGRITY_ANOMALY",
)
"""Only these three of the mandate's full event taxonomy are mechanically evaluable without
inventing new market intelligence -- the same honestly-disclosed limitation as
`causal_replay.js`'s `EVENT_GATE_DEFS` (`CAUSAL_REPLAY_ACCELERATOR_V1_IMPLEMENTATION.md` section 5).
Not expanded here: doing so would require reimplementing parts of P007/MGMT-004 detection logic that
belong to AI Trader's own reasoning, which mandate section 15 explicitly places out of scope
("retune P007", "retune MGMT-004")."""

MAX_HEARTBEAT_BARS = 8
"""Same ceiling as `causal_replay.js`'s `MAX_HEARTBEAT_BARS` -- kept identical rather than
re-derived, since nothing about switching the data source changes the apprenticeship-quality
information-loss trade-off `CAUSAL_REPLAY_ACCELERATOR_V1_DESIGN.md` originally reasoned through for
this ceiling."""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PendingDecision:
    """A bar has been revealed and is awaiting `causal_commit_decision` before the next bar can be
    revealed. Mirrors `causal_replay.js`'s in-memory `_pendingCommit`, but persisted (mandate
    section 7: unlike the live-TradingView variant, this adapter has no live browser pointer to fall
    back on as ground truth, so the pending-commit flag itself must survive a restart)."""

    bar_id: int
    """The pending bar's `ts_open` -- the same integer used everywhere else in this package (and by
    `causal_replay.js`'s own `_pendingCommit.bar_id`) to name a bar unambiguously. TIMESTAMP-valued,
    not an index -- `commit_decision(bar_id=...)` callers pass this same value."""
    bar_timestamp: int
    """Equal to `bar_id` for this adapter (CSV rows are keyed by `ts_open`) -- kept as a separate,
    equally-named field only for readability at call sites and parity with the mandate's own
    `LAST_COMMITTED_TIMESTAMP` field name; never allowed to diverge from `bar_id` (enforced in
    `__post_init__`)."""
    bar_index: int
    """The pending bar's 1-based Q4 index (`AI_TRADER_Q4_M15_LOG.md`'s own `BAR N` numbering) --
    INDEX-valued, deliberately a separate field from `bar_id`/`bar_timestamp` rather than conflated
    with them (an earlier draft compared a timestamp against an index-arithmetic expression in
    `DurableState.__post_init__` and could never validate correctly -- caught by
    `tests/test_engine.py`'s own commit-handshake tests failing during development, fixed by adding
    this field instead of re-deriving one unit from the other)."""

    def __post_init__(self) -> None:
        if self.bar_timestamp != self.bar_id:
            raise ValueError(
                f"PendingDecision.bar_timestamp ({self.bar_timestamp}) must equal bar_id ({self.bar_id})"
            )


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DurableState:
    """Minimum durable state mandate section 7 requires, persisted as JSON by
    `persistence.DurablePointerStore` between calls/process restarts. Frozen + reconstructed on
    every mutation (never mutated in place) so a half-applied change can never be observed --
    `persistence.save` either writes a complete, valid new state atomically or raises, leaving the
    on-disk file exactly as it was."""

    source_identity: SourceIdentity
    session_id: str
    last_committed_bar: int | None
    """`None` only in the freshly-seeded state before the seed bar (bar 378) has itself been
    (re)committed -- see `engine.seed_from_known_state`. Every real call site after seeding has this
    populated."""
    last_committed_timestamp: int | None
    next_bar: int
    pending_decision: PendingDecision | None
    open_event_state_reference: str | None
    """E.g. `"Q4-P007-003:OPEN"` -- mandate section 7's `OPEN_EVENT_STATE_REFERENCE`. Non-null is
    exactly the condition `engine.run_until_gate` (HYBRID mode) refuses under, per mandate section 9
    ("the future AI Trader session must resume initially in ATOMIC mode... HYBRID may only become
    eligible after the active reasoning-dependent event no longer requires strict per-bar
    supervision")."""
    adapter_version: str

    def __post_init__(self) -> None:
        if self.pending_decision is not None and self.pending_decision.bar_index != self.next_bar:
            raise ValueError(
                "DurableState: pending_decision.bar_index must equal next_bar (next_bar stays "
                "pinned to the pending bar's own index until it is committed -- it does not "
                "advance to index+1 until commit_decision() runs); got "
                f"pending_decision.bar_index={self.pending_decision.bar_index}, next_bar={self.next_bar}"
            )


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RevealedBar:
    """One bar revealed by `engine.step` -- the CSV-backed equivalent of `causal_step_snapshot`'s
    return value. Deliberately carries only the current bar plus gap context about how it was
    reached, never anything about the bar after it."""

    bar: Bar
    bar_index: int
    """1-based Q4 bar index, matching `AI_TRADER_Q4_M15_LOG.md`'s own `BAR N` numbering exactly (see
    `identity.SourceIdentity.sealed_through_bar_index`)."""
    gap_before: GapRecord | None
    """Set iff this bar's `ts_open` is not exactly `bar_interval_seconds` after the previously
    committed bar's `ts_open` -- classified via `ai_trader.live_signal_source.gap_classification.
    classify_gap`, reused verbatim rather than reimplemented (mandate section 15: REUSE > REBUILD)."""
    source_identity_fingerprint: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class EventGateFiring:
    gate: str
    detail: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RunUntilGateResult:
    """CSV-backed equivalent of `causal_run_until_gate`'s return value."""

    bars_processed: tuple[RevealedBar, ...]
    stopped_reason: Literal["EVENT_GATE", "HEARTBEAT_CEILING"]
    firing: EventGateFiring | None


def gap_classification_str(gap: GapRecord | None) -> str:
    if gap is None:
        return "NONE"
    assert isinstance(gap.classification, GapClassification)
    return gap.classification.value
