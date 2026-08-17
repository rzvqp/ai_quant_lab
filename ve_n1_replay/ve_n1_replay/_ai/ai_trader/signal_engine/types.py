"""Value types for the Signal Engine.

Mirrors ``SIGNAL_SCHEMA.json`` and ``SIGNAL_EXPLANATION_SCHEMA.json`` exactly — one frozen dataclass
per schema object, one ``str, Enum`` per closed vocabulary. Reuses already-published, stable-upstream
enums from Market Scanner (``DataQualityLevel``) and Strategy Manager (``ConfidenceLevel``,
``Regime``) rather than redefining them — both are legitimate, documented dependencies
(``SIGNAL_ENGINE_ARCHITECTURE.md`` §"Dependencies").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.strategy_manager.contract import ConfidenceLevel, Regime


class SignalState(str, Enum):
    """The nine signal states (``SIGNAL_ENGINE_STATE_MACHINE.md`` §1)."""

    BUY = "BUY"
    SELL = "SELL"
    LONG_READY = "LONG_READY"
    SHORT_READY = "SHORT_READY"
    WAIT_CONFIRMATION = "WAIT_CONFIRMATION"
    NEED_CONTEXT = "NEED_CONTEXT"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"
    NO_SIGNAL = "NO_SIGNAL"


#: "Enter now" states.
ACTIONABLE_STATES: frozenset[SignalState] = frozenset({SignalState.BUY, SignalState.SELL})
#: "Armed, awaiting trigger" states.
READY_STATES: frozenset[SignalState] = frozenset({SignalState.LONG_READY, SignalState.SHORT_READY})
#: States that must carry ``direction=NONE`` (schema ``allOf``).
NON_ACTIONABLE_STATES: frozenset[SignalState] = frozenset({
    SignalState.WAIT_CONFIRMATION, SignalState.NEED_CONTEXT, SignalState.BLOCKED,
    SignalState.INVALID, SignalState.NO_SIGNAL,
})


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class QualityFlag(str, Enum):
    """``SIGNAL_SCHEMA.json#/properties/quality_flags``."""

    OK = "OK"
    EVAL_TIMEOUT = "EVAL_TIMEOUT"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    INVALID_DIRECTION = "INVALID_DIRECTION"
    MISSING_TIMESTAMP = "MISSING_TIMESTAMP"
    UNKNOWN_STRATEGY = "UNKNOWN_STRATEGY"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    INVALID_CONFIDENCE = "INVALID_CONFIDENCE"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"
    CORRUPTED_OUTPUT = "CORRUPTED_OUTPUT"
    DEGRADED_CONTEXT = "DEGRADED_CONTEXT"
    DEPRECATED_FIELD = "DEPRECATED_FIELD"


class EngineOverallHealth(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ContextRef:
    """``SIGNAL_SCHEMA.json#/properties/context_ref``."""

    context_schema_version: str
    feature_dictionary_version: str
    interface_version: str
    data_quality: DataQualityLevel
    context_hash: str | None = None


@dataclass(frozen=True, slots=True)
class TradeParams:
    """``SIGNAL_SCHEMA.json#/properties/trade_params`` — present only for actionable/ready states."""

    entry: float | None
    stop: float | None
    target: float | None
    risk_R: float | None
    valid_until: str | int | None = None


@dataclass(frozen=True, slots=True)
class ConditionRecord:
    """``SIGNAL_EXPLANATION_SCHEMA.json#/$defs/ConditionRecord``."""

    code: str
    satisfied: bool
    label: str | None = None
    observed: float | str | bool | None = None
    expected: float | str | bool | None = None


@dataclass(frozen=True, slots=True)
class TriggeringMechanism:
    mechanism_text: str
    mechanism_code: str | None = None


@dataclass(frozen=True, slots=True)
class Confirmations:
    required: tuple[str, ...] = ()
    met: tuple[str, ...] = ()
    pending: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ContextSummary:
    symbol: str
    as_of: int
    session: str | None
    data_quality: DataQualityLevel
    regime: Regime | None = None
    timeframes_used: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class StrategyRef:
    id: str
    version: str | None = None


@dataclass(frozen=True, slots=True)
class Explanation:
    """``SIGNAL_EXPLANATION_SCHEMA.json`` root object."""

    explanation_schema_version: str
    strategy_ref: StrategyRef
    state: SignalState
    triggering_mechanism: TriggeringMechanism
    why_exists: tuple[ConditionRecord, ...]
    why_failed: tuple[ConditionRecord, ...]
    required_conditions: tuple[ConditionRecord, ...]
    missing_conditions: tuple[ConditionRecord, ...]
    invalid_conditions: tuple[ConditionRecord, ...]
    confirmations: Confirmations
    context_summary: ContextSummary


@dataclass(frozen=True, slots=True)
class StrategySignal:
    """``SIGNAL_SCHEMA.json`` root object — the canonical output of one (strategy, symbol, as_of)
    evaluation."""

    signal_schema_version: str
    signal_engine_version: str
    signal_id: str
    strategy_id: str
    strategy_version: str | None
    timestamp: int
    as_of: int
    symbol: str
    timeframe: str
    state: SignalState
    direction: Direction
    signal_strength: float
    confidence: ConfidenceLevel
    mechanism: str
    required_confirmations: tuple[str, ...]
    confirmations_met: bool
    missing_context: tuple[str, ...]
    invalid_conditions: tuple[str, ...]
    quality_flags: tuple[QualityFlag, ...]
    context_ref: ContextRef
    explanation: Explanation
    evaluation_time_ms: float
    trade_params: TradeParams | None = None
    regime: Regime | None = None
    session: str | None = None


@dataclass(frozen=True, slots=True)
class SignalBatch:
    """``SIGNAL_ENGINE_API.md`` §0."""

    as_of: int
    symbol: str | None
    signals: tuple[StrategySignal, ...]
    counts_by_state: dict[str, int]
    generated_at: int


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reasons: tuple[str, ...] = ()
    quality_flags: tuple[QualityFlag, ...] = ()


@dataclass(frozen=True, slots=True)
class Statistics:
    cycles: int
    signals_total: int
    by_state: dict[str, int]
    avg_eval_ms: float
    timeouts: int
    invalids: int


@dataclass(frozen=True, slots=True)
class EngineHealth:
    overall: EngineOverallHealth
    last_cycle_ok: bool
    degraded_reasons: tuple[str, ...] = ()
    supported_versions: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VersionInfo:
    signal_engine_version: str
    signal_schema_version: str
    explanation_schema_version: str
    supported_interface_major: int
    supported_context_schema_major: int


@dataclass(frozen=True, slots=True)
class NotFound:
    """Typed "not found" result (``SIGNAL_ENGINE_API.md`` §2/§3) — never an exception."""

    key: str


#: Structural alias for a MarketContext -- a plain JSON-serializable dict, matching Market Scanner's
#: own representation (``MarketContext`` is deliberately a ``dict[str, Any]``, not a dataclass mirror
#: -- see ``ai_trader.market_scanner.scanner.MarketScanner.build_context``'s own docstring rationale,
#: reused here for the same reason: the schema IS the canonical contract).
MarketContext = dict[str, Any]
