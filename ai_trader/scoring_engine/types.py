"""Value types for the Scoring Engine.

Mirrors ``SCORING_SCHEMA.json`` exactly — one frozen dataclass per schema object, one ``str, Enum``
per closed vocabulary. Reuses already-published, stable-upstream types from Signal Engine
(``SignalState``, ``Direction``) and Market Scanner (``DataQualityLevel``) rather than redefining
them — legitimate, documented dependencies (``SCORING_ENGINE_ARCHITECTURE.md`` §"Dependencies").
``ConfidenceLevel`` is NOT reused from Strategy Manager: that enum includes ``NEGATIVE``, a value
``SCORING_SCHEMA.json#/properties/confidence`` does not permit — a fresh, schema-exact
:class:`ScoreConfidence` is defined instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.signal_engine.types import Direction, SignalState

#: States the model treats as immediately tradeable ("actionable"), mirroring
#: ``ai_trader.signal_engine.types.ACTIONABLE_STATES``.
ACTIONABLE_STATES: frozenset[SignalState] = frozenset({SignalState.BUY, SignalState.SELL})
#: "Armed, awaiting trigger" states -> ``WATCH``.
READY_STATES: frozenset[SignalState] = frozenset({SignalState.LONG_READY, SignalState.SHORT_READY})
#: Non-actionable states the schema's own ``allOf`` rule constrains to ``recommendation`` in
#: ``{SKIP, INVALID}`` and ``direction=NONE`` (``SCORING_SCHEMA.json`` ``allOf``, verbatim list).
NON_ACTIONABLE_STATES: frozenset[SignalState] = frozenset({
    SignalState.NEED_CONTEXT, SignalState.BLOCKED, SignalState.INVALID, SignalState.NO_SIGNAL,
})


class ScoreConfidence(str, Enum):
    """``SCORING_SCHEMA.json#/properties/confidence`` — derived from ``historical_confidence``
    (``SCORING_MODEL.md`` §6); NOT the same enum as the contract's own ``evidence.confidence.level``
    (which additionally allows ``NEGATIVE``, not valid here)."""

    NONE = "NONE"
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Quality(str, Enum):
    """``SCORING_SCHEMA.json#/properties/quality`` — ``total_score`` band (``SCORING_MODEL.md`` §6)."""

    PREMIUM = "PREMIUM"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    POOR = "POOR"


class Recommendation(str, Enum):
    """``SCORING_SCHEMA.json#/properties/recommendation``."""

    STRONG_OPPORTUNITY = "STRONG_OPPORTUNITY"
    MODERATE_OPPORTUNITY = "MODERATE_OPPORTUNITY"
    WEAK_OPPORTUNITY = "WEAK_OPPORTUNITY"
    WATCH = "WATCH"
    SKIP = "SKIP"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class ComponentScores:
    """``SCORING_SCHEMA.json#/properties/component_scores`` — all nine components, each in [0,1]
    (``SCORING_MODEL.md`` §2), always fully populated so any score is decomposable."""

    signal_strength: float = 0.0
    historical_confidence: float = 0.0
    market_alignment: float = 0.0
    regime_alignment: float = 0.0
    confirmation_quality: float = 0.0
    data_quality: float = 0.0
    execution_readiness: float = 0.0
    risk_penalty: float = 0.0
    conflict_penalty: float = 0.0


@dataclass(frozen=True, slots=True)
class ReasonCode:
    """``SCORING_SCHEMA.json#/properties/reason_codes`` item."""

    code: str
    component: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class Refs:
    """``SCORING_SCHEMA.json#/properties/refs``."""

    strategy_version: str | None
    signal_schema_version: str
    interface_version: str
    data_quality: DataQualityLevel


@dataclass(frozen=True, slots=True)
class TradeContext:
    """``SCORING_SCHEMA.json#/properties/trade_context`` — prices carried through for the Risk
    Manager; no sizing here."""

    entry: float | None
    stop: float | None
    target: float | None
    risk_R: float | None


@dataclass(frozen=True, slots=True)
class OpportunityScore:
    """``SCORING_SCHEMA.json`` root object — the canonical output of one signal's scoring."""

    scoring_schema_version: str
    scoring_engine_version: str
    scoring_model_version: str
    score_id: str
    signal_id: str
    strategy_id: str
    symbol: str
    timestamp: int
    as_of: int
    state: SignalState
    direction: Direction
    total_score: int
    component_scores: ComponentScores
    confidence: ScoreConfidence
    quality: Quality
    recommendation: Recommendation
    rank: int
    reason_codes: tuple[ReasonCode, ...]
    refs: Refs
    base_quality: float | None = None
    penalty_factor: float | None = None
    trade_context: TradeContext | None = None


@dataclass(frozen=True, slots=True)
class ScoreBatch:
    """``SCORING_API.md`` §0."""

    as_of: int
    symbol: str | None
    scores: tuple[OpportunityScore, ...]
    counts_by_recommendation: dict[str, int]
    generated_at: int


@dataclass(frozen=True, slots=True)
class ScoreExplanation:
    """``SCORING_API.md`` §2 ``explain_score()`` result."""

    score_id: str
    component_scores: ComponentScores
    base_quality: float | None
    penalty_factor: float | None
    reason_codes: tuple[ReasonCode, ...]
    model_version: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Statistics:
    """``SCORING_API.md`` §3."""

    batches: int
    scores_total: int
    by_recommendation: dict[str, int]
    by_quality: dict[str, int]
    avg_score: float
    invalids: int


class EngineOverallHealth(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class EngineLifecycleState(str, Enum):
    """Engine lifecycle (``SCORING_STATE_MACHINE.md`` §A)."""

    UNINITIALIZED = "UNINITIALIZED"
    CONFIGURING = "CONFIGURING"
    READY = "READY"
    SCORING = "SCORING"
    DEGRADED = "DEGRADED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    STOPPED = "STOPPED"


@dataclass(frozen=True, slots=True)
class EngineHealth:
    overall: EngineOverallHealth
    state: EngineLifecycleState
    degraded_reasons: tuple[str, ...] = ()
    supported_versions: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VersionInfo:
    scoring_engine_version: str
    scoring_schema_version: str
    scoring_model_version: str
    supported_signal_schema_major: int
    supported_interface_major: int


@dataclass(frozen=True, slots=True)
class NotFound:
    """Typed "not found" result (``SCORING_API.md`` §2) — never an exception."""

    key: str


#: Structural alias -- ``StrategySignal`` is imported directly where needed rather than aliased here,
#: matching Signal Engine's ``MarketContext = dict[str, Any]`` precedent of naming the exact upstream
#: type instead of a vague ``Any``.
JsonDict = dict[str, Any]
