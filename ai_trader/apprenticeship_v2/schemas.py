"""Plain, JSON-serializable dataclasses for the apprenticeship V2 durable artifacts. No behavior,
no I/O -- pure data shape, matching the mandate's Section 10/11/12/14/15/16 field lists exactly."""

from __future__ import annotations

import dataclasses

ALLOWED_EXPECTATIONS = (
    "FOLLOW_THROUGH_LIKELY", "FAILURE_LIKELY", "REVERSAL_LIKELY", "ROUND_TRIP_LIKELY", "UNCLEAR",
)
ALLOWED_CONFIDENCE = ("HIGH", "MEDIUM", "LOW")
ALLOWED_SHADOW_DECISION = ("TAKE", "SKIP", "UNCLEAR")
RESOLUTION_HORIZONS_M15 = (4, 8, 16, 32)


@dataclasses.dataclass
class EpisodeRecord:
    """One frozen, pre-outcome episode. `qualitative_review_status` starts `PENDING_LLM_REVIEW` --
    the mechanical loop that creates this record never fills the qualitative fields (Section 8-10
    requires genuine reasoning, not a formula). The embedded `snapshot` is the ONLY data a later
    qualitative-review pass may use to fill those fields -- it must never re-query live bars for an
    already-frozen episode, which would contaminate a "pre-outcome" record with newer information."""

    episode_id: str
    timestamp_utc: str
    frozen_at_bar_ts: int
    episode_type: str  # e.g. "S5_OCCURRENCE"
    symbol: str
    current_price: float
    setup_direction: str | None
    reference_levels: dict[str, float]
    snapshot: dict[str, list[dict[str, object]]]  # {"H4": [...], "H1": [...], "M15": [...], "M5": [...]}

    # Section 10 fields -- None until a qualitative-review pass fills them.
    h4_context: str | None = None
    h1_context: str | None = None
    m15_context: str | None = None
    m5_context: str | None = None
    market_structure_state: str | None = None
    approach_description: str | None = None
    pressure_state: str | None = None
    pullback_state: str | None = None
    participation_state: str | None = None
    acceptance_rejection_state: str | None = None
    level_defense_weakening_state: str | None = None
    liquidity_context: str | None = None
    conflicting_evidence: str | None = None
    supporting_evidence: str | None = None
    ai_trader_expectation: str | None = None  # one of ALLOWED_EXPECTATIONS
    confidence: str | None = None  # one of ALLOWED_CONFIDENCE
    expected_failure_mode: str | None = None
    expected_confirmation_behavior: str | None = None
    expected_invalidation_behavior: str | None = None

    # Section 22 -- shadow only, never an order.
    shadow_decision: str | None = None  # one of ALLOWED_SHADOW_DECISION

    qualitative_review_status: str = "PENDING_LLM_REVIEW"  # -> "FROZEN" once the LLM pass completes
    reviewed_at_utc: str | None = None

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class HorizonMetrics:
    forward_return: float
    mfe: float
    mae: float
    max_up_move: float
    max_down_move: float
    close_location: float  # (close - low) / (high - low) over the horizon window, 0..1
    directional_follow_through: bool | None  # None if setup_direction was None (no directional claim)
    round_trip_magnitude: float  # how much of the initial move was given back, as a fraction

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class S5StructuralResolution:
    """S5-specific mechanical resolution (Section 15) -- computed by replaying S5's own frozen
    STOP/TARGET/MAX_HOLD rules forward against causally-revealed bars, exactly the technique already
    used throughout the completed Q4 causal replay. Only populated when `episode_type ==
    'S5_OCCURRENCE'` and reference_levels carries entry/stop/target."""

    exit_bar_ts: int
    exit_reason: str  # "STOP" | "TARGET" | "MAX_HOLD"
    exit_price: float
    r_multiple: float

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ResolvedEpisode:
    episode_id: str
    resolved_at_utc: str
    atr_at_episode_start: float | None
    horizons: dict[str, dict[str, object]]  # {"4": HorizonMetrics.to_json_dict(), ...}
    structural_resolution: dict[str, object] | None  # S5StructuralResolution.to_json_dict() or None

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ScorecardEntry:
    """Section 16 -- append-only, never overwrites an original prediction."""

    episode_id: str
    original_expectation: str
    original_confidence: str
    mechanical_outcome_summary: str
    expectation_correct: str  # "YES" | "NO" | "PARTIAL" | "NOT_SCORABLE"
    partial_reason: str | None
    scored_at_utc: str

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)
