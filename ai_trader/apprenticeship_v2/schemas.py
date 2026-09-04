"""Plain, JSON-serializable dataclasses for the apprenticeship V2 durable artifacts. No behavior,
no I/O -- pure data shape, matching the mandate's Section 10/11/12/14/15/16 field lists exactly."""

from __future__ import annotations

import dataclasses

ALLOWED_EXPECTATIONS = (
    "FOLLOW_THROUGH_LIKELY", "FAILURE_LIKELY", "REVERSAL_LIKELY", "ROUND_TRIP_LIKELY", "RANGE_LIKELY",
    "UNCLEAR",
)
"""`RANGE_LIKELY` added by General Observer V1.1 (design doc Section 9) -- closes the gap V1 left
open. Adding a 6th value to this existing tuple is additive and does not change the meaning of the
5 pre-existing values S5 already writes/reads."""
ALLOWED_CONFIDENCE = ("HIGH", "MEDIUM", "LOW")
ALLOWED_SHADOW_DECISION = ("TAKE", "SKIP", "UNCLEAR")
RESOLUTION_HORIZONS_M15 = (4, 8, 16, 32)

# ---- General Observer V1.1 additions (design doc Section 7/9/10/13a) ----------------------------

GENERAL_OBSERVER_EVENT_TYPES = (
    "SWEEP_REJECTION", "STRUCTURAL_BREAK", "DISPLACEMENT", "SESSION_TRANSITION_REVERSAL",
)
"""Exactly the four locked classes (design doc Section 3) -- no fifth class, ever."""

REVIEW_HORIZONS = ("H1", "H2", "H4", "H8", "STRUCTURAL_FINAL")
"""Section 9 -- the exact horizon set a `ScorecardEntry` row's `review_horizon` may take. `H1..H8`
correspond 1:1 to `RESOLUTION_HORIZONS_M15` (4, 8, 16, 32 M15 bars); `STRUCTURAL_FINAL` is reserved
for a class whose resolution is structural (e.g. S5's own STOP/TARGET/MAX_HOLD) rather than a fixed
M15-bar-count horizon -- not produced by any code in this delivery, reserved by the frozen contract
for future use, never invented content here."""


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
    reference_levels: dict[str, object]
    """`dict[str, float]` was this field's original (S5-only) type -- widened to `dict[str, object]`
    for General Observer V1.1, whose own reference_levels dicts legitimately carry strings too
    (level types, session names, reason codes), not just floats. Type-annotation-only change: never
    checked at runtime (this module uses `from __future__ import annotations`), and strictly widens
    what is accepted, so every existing S5 call site (which only ever passes floats) remains valid
    unchanged."""
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

    # ---- General Observer V1.1 additions (design doc Section 7) -- all additive/defaulted, so
    # every existing S5_OCCURRENCE construction site (loop.py) is unaffected byte-for-byte. ----
    trigger_timeframe: str | None = None
    """Always "M15" for a general-observer episode (design doc Section 3); left `None` for
    S5_OCCURRENCE rows, which never set this field -- S5 stays behaviorally unchanged, not
    retroactively backfilled."""
    what_triggered_observation: str | None = None
    """A short, deterministic, code-generated description of the mechanical trigger (e.g. "M15 close
    swept PREVIOUS_DAY_LOW then reclaimed"). Distinct from `approach_description`, which is a
    broader, LLM-written concept (design doc Section 7 table) -- this field is filled by the
    mechanical detector itself, before any qualitative pass."""
    directional_hypothesis: str | None = None
    """Genuinely separate from `setup_direction` (S5 isolation, design doc Section 15) -- never a
    rename or reuse. One of "BULLISH" / "BEARISH" (never `str(some_enum)` -- see the live
    `setup_direction` serialization defect this field deliberately does not repeat)."""
    what_to_watch_next: str | None = None
    """LLM-written during BEFORE review (design doc Section 8 step 6) -- mechanically `None` at
    episode-shell creation time, exactly like the existing qualitative fields above."""
    frozen_snapshot_hash: str | None = None
    """SHA-256 of the frozen snapshot's canonical JSON serialization (design doc Section 8 step 4) --
    computed mechanically, once, at freeze time. `None` only before the snapshot is computed (never
    true for a fully-constructed EpisodeRecord in this delivery's own code paths)."""
    prospective_eligibility: str | None = None
    """"YES" / "NO" (design doc Section 8 step 7/8) -- `None` until a qualitative-review pass sets
    it; general-observer code that only builds the mechanical shell never sets this itself."""
    underlying_move_id: str | None = None
    """Design doc Section 8's family-grouping key -- computed mechanically at episode-creation time
    (unlike the other new fields above, this one IS set by the mechanical detector, not by a later
    qualitative pass, since dedup must happen before an episode is even written to the ledger)."""

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class RetrospectiveMissedMoveCluster:
    """Design doc Section 10 -- `RETROSPECTIVE_MISSED_MOVE_CLUSTER`. Structurally distinct from
    `EpisodeRecord`: never carries BEFORE-shaped fields, prospective confidence, or a
    `directional_hypothesis` -- enforced by simply not having those fields at all, not by a runtime
    check on a shared shape. Never counts toward lesson evidence (Section 10's own explicit lock)."""

    cluster_id: str
    record_class: str = dataclasses.field(default="RETROSPECTIVELY_IDENTIFIED_MISSED_EVENT", init=False)
    direction: str = ""  # "BULLISH" | "BEARISH"
    canonical_window_start_ts: int = 0
    canonical_window_end_ts: int = 0
    canonical_magnitude: float = 0.0
    canonical_atr_reference: float = 0.0
    canonical_normalized_magnitude: float = 0.0
    qualifying_window_count: int = 1
    cluster_terminated_at_ts: int | None = None
    """`None` while the cluster is still active (its most recent candidate was still a qualifying
    continuation and no terminating candidate has been seen yet)."""

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
    """Section 16 -- append-only, never overwrites an original prediction. Pre-existing dataclass,
    confirmed unused anywhere in the codebase before this delivery (no `append_scorecard()`, no
    `SCORECARD_CSV`, zero construction sites) -- General Observer V1.1 Section 9 requires one row
    per `(episode_id, review_horizon)`, so `review_horizon` is added as a REQUIRED field (safe:
    there are no existing call sites to break) rather than an optional one, exactly matching the
    frozen contract's own "never one row per episode" requirement."""

    episode_id: str
    review_horizon: str  # one of schemas.REVIEW_HORIZONS -- "H1"/"H2"/"H4"/"H8"/"STRUCTURAL_FINAL"
    original_expectation: str
    original_confidence: str
    mechanical_outcome_summary: str
    expectation_correct: str  # "YES" | "NO" | "PARTIAL" | "NOT_SCORABLE"
    partial_reason: str | None
    scored_at_utc: str
    after_market_interpretation: str | None = None
    """LLM-written (design doc Section 9) -- mechanically `None` when a scorecard row is written by
    code alone; filled by a later qualitative pass, exactly like `EpisodeRecord`'s own qualitative
    fields."""
    lesson_candidate_effect: str | None = None
    """LLM-written (design doc Section 9) -- same defer-to-qualitative-pass convention."""

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class LessonHypothesis:
    """Design doc Section 13a -- the minimum required representation for
    `hypothesis_eligibility_definition` + `lesson_evaluation_horizon`, specified here because no
    equivalent field exists anywhere in the current register (confirmed: `AI_TRADER_LESSON_REGISTER.md`
    has no per-entry field schema at all, only prose). Both fields are immutable once written
    (Section 13a: "never widened or narrowed after counterexamples appear" / "never altered
    afterward") -- enforced by convention (this is a plain dataclass, not a frozen one, only because
    `lesson_status` below legitimately changes over the hypothesis's life; the two eligibility/horizon
    fields themselves are simply never reassigned anywhere in this delivery's own code once
    constructed)."""

    hypothesis_id: str
    created_at_utc: str
    hypothesis_eligibility_definition: dict[str, object]
    """Expressed only in terms of prospectively-available fields (episode_type,
    directional_hypothesis, reference_levels level-type, trigger_timeframe, etc.) -- never an
    outcome/scorecard field (Section 13a's own explicit constraint). A plain dict of those filter
    criteria; validated by `lesson_voting.episode_matches_hypothesis()`, not by this dataclass
    itself (keeping this a pure data shape, matching every other dataclass in this module)."""
    lesson_evaluation_horizon: str  # one of schemas.REVIEW_HORIZONS -- frozen at creation, never altered
    lesson_status: str = "NEW_HYPOTHESIS"
    """One of NEW_HYPOTHESIS / REPEATED_OBSERVATION / PROSPECTIVELY_SUPPORTED /
    PROSPECTIVELY_WEAKENED / PROSPECTIVELY_REJECTED (design doc Section 13/18) -- the only field on
    this dataclass that legitimately changes over time, recomputed by
    `lesson_voting.classify_lesson_status()`, never hand-set."""

    def to_json_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)
