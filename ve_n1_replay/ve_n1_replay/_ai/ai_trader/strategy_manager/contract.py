"""Typed representation of a Strategy Execution Contract.

Mirrors ``knowledge/interface/strategy_contract.v1.schema.json`` exactly — one frozen dataclass per
schema object, one ``StrEnum``-style ``str, Enum`` per closed vocabulary (``$defs`` enum). Nothing
here is invented: field names, nesting, and enum members are transcribed 1:1 from the frozen schema
(``knowledge/interface/STRATEGY_INTERFACE_v1.md`` is the read-only spec this mirrors).

:func:`parse_contract` assumes its input has ALREADY passed JSON-Schema validation
(:mod:`ai_trader.strategy_manager.schema_validation`) — it does not re-validate structure, only
converts the already-valid dict into a typed, immutable object graph. This module never reads
Research Lab artifacts; a contract is the Manager's ONLY view of a strategy (architecture §7
invariant 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ContractStatus(str, Enum):
    """``lifecycle.status`` (schema ``$defs/StrategyStatus``)."""

    IMPLEMENTED = "IMPLEMENTED"
    INVALID = "INVALID"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    DEPRECATED = "DEPRECATED"
    DISABLED = "DISABLED"


class Maturity(str, Enum):
    """``lifecycle.maturity`` (schema ``$defs/Maturity``) — the research validation ladder."""

    EXPLORATORY = "EXPLORATORY"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    PROMOTED = "PROMOTED"
    RETIRED = "RETIRED"


#: Ordinal rank of each maturity tier, lowest first — used for "maturity >= X" admission-policy and
#: gate comparisons (``STRATEGY_MANAGER_STATE_MACHINE.md`` transition table T4/T6-T9). RETIRED is
#: intentionally NOT part of the upward ladder (it is a terminal withdrawal, not a higher tier).
_MATURITY_LADDER: tuple[Maturity, ...] = (
    Maturity.EXPLORATORY, Maturity.CANDIDATE, Maturity.VALIDATED, Maturity.PROMOTED,
)


def maturity_rank(maturity: Maturity) -> int:
    """Ordinal rank on the upward ladder (higher = more mature). ``RETIRED`` ranks below
    ``EXPLORATORY`` (-1): it is a terminal withdrawal, never a comparison target for admission."""
    if maturity is Maturity.RETIRED:
        return -1
    return _MATURITY_LADDER.index(maturity)


class ContractHealth(str, Enum):
    """``lifecycle.current_health`` (schema ``$defs/Health``) — distinct from the Manager's own
    operational :class:`~ai_trader.strategy_manager.types.Health` enum; this is the contract's
    self-reported health."""

    OK = "OK"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    DISABLED = "DISABLED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(str, Enum):
    """``evidence.confidence.level`` (schema ``$defs/Confidence``)."""

    NONE = "NONE"
    NEGATIVE = "NEGATIVE"
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TestStatus(str, Enum):
    """Validation-ladder gate status (schema ``$defs/TestStatus``): walk-forward, matched-null,
    global-FDR."""

    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class Regime(str, Enum):
    """Market regime tag (schema ``$defs/Regime``)."""

    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE = "RANGE"
    HIGH_VOL = "HIGH_VOL"
    LOW_VOL = "LOW_VOL"
    SESSION_OPEN = "SESSION_OPEN"
    ANY = "ANY"


class LongShort(str, Enum):
    """``execution.long_short``."""

    LONG = "LONG"
    SHORT = "SHORT"
    BOTH = "BOTH"


class CooldownScope(str, Enum):
    """``execution.cooldown.scope``."""

    PER_STRATEGY = "PER_STRATEGY"
    PER_DIRECTION = "PER_DIRECTION"


class MatchedNullScope(str, Enum):
    """``evidence.matched_null_status.scope``."""

    NONE = "NONE"
    PILOT = "PILOT"
    WAVE1 = "WAVE1"
    FULL_UNIVERSE = "FULL_UNIVERSE"


class HoldoutStatus(str, Enum):
    """``provenance.holdout_status``."""

    SEALED = "SEALED"
    OPENED = "OPENED"


@dataclass(frozen=True, slots=True)
class Identity:
    id: str
    name: str
    slug: str
    version: str
    klass: str  # schema property name is "class"; renamed to avoid the Python keyword


@dataclass(frozen=True, slots=True)
class ContractLifecycle:
    status: ContractStatus
    maturity: Maturity
    current_health: ContractHealth
    last_review: str
    priority: int | None = None


@dataclass(frozen=True, slots=True)
class MarketRegimeSpec:
    applicable: tuple[Regime, ...]
    avoid: tuple[Regime, ...]


@dataclass(frozen=True, slots=True)
class RequiredDataSpec:
    """One entry of ``semantics.required_data`` — a single timeframe's data requirement."""

    timeframe: str
    fields: tuple[str, ...]
    lookback_bars: int
    htf: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class Semantics:
    mechanism: str
    signal_reason: str
    market_regime: MarketRegimeSpec
    required_data: tuple[RequiredDataSpec, ...]
    required_confirmations: tuple[str, ...]
    dependencies: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class RuleSpec:
    description: str
    trigger: str | None = None
    timing: str | None = None
    options: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class RiskModel:
    model: str
    risk_definition: str
    stop_floor: str
    costs: str


@dataclass(frozen=True, slots=True)
class CapitalLimit:
    max_risk_per_trade_R: float | None = None
    max_strategy_allocation_pct: float | None = None


@dataclass(frozen=True, slots=True)
class ExpectedFrequency:
    trades_per_year: float | None
    basis: str


@dataclass(frozen=True, slots=True)
class Cooldown:
    bars: int
    scope: CooldownScope


@dataclass(frozen=True, slots=True)
class Execution:
    timeframe: str
    sessions: str
    long_short: LongShort
    entry: RuleSpec
    exit: RuleSpec
    stop: RuleSpec
    risk_model: RiskModel
    position_sizing: dict[str, Any]
    max_concurrent_positions: int
    expected_frequency: ExpectedFrequency
    cooldown: Cooldown
    invalid_conditions: tuple[str, ...]
    target: RuleSpec | None = None
    capital_limit: CapitalLimit | None = None


@dataclass(frozen=True, slots=True)
class Confidence:
    level: ConfidenceLevel
    rationale: str
    score: float | None = None


@dataclass(frozen=True, slots=True)
class Metrics:
    segment: str
    n: int | None = None
    expectancy_R: float | None = None
    profit_factor: float | None = None
    drawdown_R: float | None = None
    win_rate: float | None = None
    pos_months: int | None = None
    months: int | None = None
    top1_share: float | None = None


@dataclass(frozen=True, slots=True)
class MatchedNullStatus:
    status: TestStatus
    scope: MatchedNullScope
    note: str
    p: float | None = None
    adjusted_p: float | None = None


@dataclass(frozen=True, slots=True)
class Evidence:
    confidence: Confidence
    historical_metrics: Metrics
    oos_metrics: Metrics
    walk_forward_status: TestStatus
    matched_null_status: MatchedNullStatus
    global_fdr_status: TestStatus
    validation_status: str
    known_limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Provenance:
    engine: str
    generated_from: str
    holdout_status: HoldoutStatus
    source_ref: str | None = None


@dataclass(frozen=True, slots=True)
class Contract:
    """The full, typed Strategy Execution Contract (schema root object)."""

    interface_version: str
    identity: Identity
    lifecycle: ContractLifecycle
    semantics: Semantics
    execution: Execution
    evidence: Evidence
    provenance: Provenance


def _tuple_or_none(value: Any) -> tuple[Any, ...] | None:
    return None if value is None else tuple(value)


def parse_contract(data: dict[str, Any]) -> Contract:
    """Convert an already schema-validated contract dict into a typed :class:`Contract`.

    Assumes ``data`` already passed :func:`ai_trader.strategy_manager.schema_validation.
    validate_contract` — required fields are trusted to be present with the correct shape, since
    re-deriving that here would duplicate the schema. A malformed enum value not covered by the
    schema's own ``enum``/``const`` constraints would raise ``ValueError`` from the ``Enum``
    constructor, which the caller (the Loader) treats as a load failure, never a crash.
    """
    identity = data["identity"]
    lifecycle = data["lifecycle"]
    semantics = data["semantics"]
    execution = data["execution"]
    evidence = data["evidence"]
    provenance = data["provenance"]

    market_regime = semantics["market_regime"]
    required_data = tuple(
        RequiredDataSpec(
            timeframe=rd["timeframe"],
            fields=tuple(rd["fields"]),
            lookback_bars=rd["lookback_bars"],
            htf=_tuple_or_none(rd.get("htf")),
        )
        for rd in semantics["required_data"]
    )

    def _rule_spec(raw: dict[str, Any] | None) -> RuleSpec | None:
        if raw is None:
            return None
        return RuleSpec(
            description=raw["description"],
            trigger=raw.get("trigger"),
            timing=raw.get("timing"),
            options=_tuple_or_none(raw.get("options")),
        )

    entry_rule = _rule_spec(execution["entry"])
    exit_rule = _rule_spec(execution["exit"])
    stop_rule = _rule_spec(execution["stop"])
    assert entry_rule is not None and exit_rule is not None and stop_rule is not None  # required by schema

    risk_model_raw = execution["risk_model"]
    capital_limit_raw = execution.get("capital_limit")
    expected_frequency_raw = execution["expected_frequency"]
    cooldown_raw = execution["cooldown"]

    confidence_raw = evidence["confidence"]
    matched_null_raw = evidence["matched_null_status"]

    def _metrics(raw: dict[str, Any]) -> Metrics:
        return Metrics(
            segment=raw["segment"], n=raw.get("n"), expectancy_R=raw.get("expectancy_R"),
            profit_factor=raw.get("profit_factor"), drawdown_R=raw.get("drawdown_R"),
            win_rate=raw.get("win_rate"), pos_months=raw.get("pos_months"),
            months=raw.get("months"), top1_share=raw.get("top1_share"),
        )

    return Contract(
        interface_version=data["interface_version"],
        identity=Identity(
            id=identity["id"], name=identity["name"], slug=identity["slug"],
            version=identity["version"], klass=identity["class"],
        ),
        lifecycle=ContractLifecycle(
            status=ContractStatus(lifecycle["status"]),
            maturity=Maturity(lifecycle["maturity"]),
            current_health=ContractHealth(lifecycle["current_health"]),
            last_review=lifecycle["last_review"],
            priority=lifecycle.get("priority"),
        ),
        semantics=Semantics(
            mechanism=semantics["mechanism"],
            signal_reason=semantics["signal_reason"],
            market_regime=MarketRegimeSpec(
                applicable=tuple(Regime(r) for r in market_regime["applicable"]),
                avoid=tuple(Regime(r) for r in market_regime["avoid"]),
            ),
            required_data=required_data,
            required_confirmations=tuple(semantics["required_confirmations"]),
            dependencies=_tuple_or_none(semantics.get("dependencies")),
        ),
        execution=Execution(
            timeframe=execution["timeframe"],
            sessions=execution["sessions"],
            long_short=LongShort(execution["long_short"]),
            entry=entry_rule, exit=exit_rule, stop=stop_rule,
            target=_rule_spec(execution.get("target")),
            risk_model=RiskModel(
                model=risk_model_raw["model"], risk_definition=risk_model_raw["risk_definition"],
                stop_floor=risk_model_raw["stop_floor"], costs=risk_model_raw["costs"],
            ),
            position_sizing=dict(execution["position_sizing"]),
            capital_limit=(
                None if not capital_limit_raw else CapitalLimit(
                    max_risk_per_trade_R=capital_limit_raw.get("max_risk_per_trade_R"),
                    max_strategy_allocation_pct=capital_limit_raw.get("max_strategy_allocation_pct"),
                )
            ),
            max_concurrent_positions=execution["max_concurrent_positions"],
            expected_frequency=ExpectedFrequency(
                trades_per_year=expected_frequency_raw["trades_per_year"],
                basis=expected_frequency_raw["basis"],
            ),
            cooldown=Cooldown(bars=cooldown_raw["bars"], scope=CooldownScope(cooldown_raw["scope"])),
            invalid_conditions=tuple(execution["invalid_conditions"]),
        ),
        evidence=Evidence(
            confidence=Confidence(
                level=ConfidenceLevel(confidence_raw["level"]), rationale=confidence_raw["rationale"],
                score=confidence_raw.get("score"),
            ),
            historical_metrics=_metrics(evidence["historical_metrics"]),
            oos_metrics=_metrics(evidence["oos_metrics"]),
            walk_forward_status=TestStatus(evidence["walk_forward_status"]),
            matched_null_status=MatchedNullStatus(
                status=TestStatus(matched_null_raw["status"]),
                scope=MatchedNullScope(matched_null_raw["scope"]), note=matched_null_raw["note"],
                p=matched_null_raw.get("p"), adjusted_p=matched_null_raw.get("adjusted_p"),
            ),
            global_fdr_status=TestStatus(evidence["global_fdr_status"]),
            validation_status=evidence["validation_status"],
            known_limitations=tuple(evidence["known_limitations"]),
        ),
        provenance=Provenance(
            engine=provenance["engine"], generated_from=provenance["generated_from"],
            holdout_status=HoldoutStatus(provenance["holdout_status"]),
            source_ref=provenance.get("source_ref"),
        ),
    )
