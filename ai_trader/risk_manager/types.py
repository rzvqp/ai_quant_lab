"""Value types for the Risk Manager.

``RiskDecision`` and its nested objects mirror ``RISK_SCHEMA.json`` exactly — one frozen dataclass
per schema object, one ``str, Enum`` per closed vocabulary. Reuses the already-published, stable-
upstream ``Direction`` from Signal Engine and ``DataQualityLevel`` from Market Scanner.

``RiskContext`` and ``PortfolioState`` (this module's own INPUT types) are NOT defined by any frozen
JSON Schema -- no Portfolio Manager module exists yet to publish one, and ``RISK_SCHEMA.json`` only
defines the OUTPUT (``RiskDecision``). ``RISK_MANAGER_ARCHITECTURE.md`` §3 names their required
content in prose ("open positions (symbol, direction, size, entry, age, correlation group), aggregate
exposure, leverage, realized/unrealized P&L (intraday/daily/weekly), equity high-water mark, current
drawdown" for ``PortfolioState``; "volatility/ATR, spread, liquidity proxy, session, weekend/gap
flags, calendar/news flags, data_quality, as_of" for ``RiskContext``) — every field below traces
directly to that prose. This is a documented, necessary gap-fill (IMPLEMENTATION CHOICE), not an
invented redesign: a future real Portfolio Manager module would need to satisfy this exact shape (or
a schema-frozen evolution of it) to plug into this Risk Manager unmodified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.signal_engine.types import Direction


class Decision(str, Enum):
    """``RISK_SCHEMA.json#/properties/decision``."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class EngineState(str, Enum):
    """``RISK_SCHEMA.json#/properties/engine_state`` -- the GLOBAL risk state gating every decision
    (``RISK_STATE_MACHINE.md`` §A). Distinct from :class:`EngineLifecycleState`, which additionally
    covers the module's own construction/shutdown bookkeeping states (``IDLE``/``EVALUATING``/
    ``SHUTDOWN``) that never appear in an emitted ``RiskDecision``."""

    READY = "READY"
    SUSPENDED = "SUSPENDED"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class EngineLifecycleState(str, Enum):
    """The full module lifecycle (``RISK_STATE_MACHINE.md`` §A) -- a superset of :class:`EngineState`
    used internally; ``IDLE``/``EVALUATING``/``SHUTDOWN`` collapse to the nearest :class:`EngineState`
    when stamped onto an emitted ``RiskDecision`` (``EVALUATING`` -> ``READY``)."""

    IDLE = "IDLE"
    READY = "READY"
    EVALUATING = "EVALUATING"
    SUSPENDED = "SUSPENDED"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SHUTDOWN = "SHUTDOWN"


class EngineOverallHealth(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class SizingMethod(str, Enum):
    FIXED_FRACTIONAL = "FIXED_FRACTIONAL"
    VOL_SCALED = "VOL_SCALED"
    ATR_SCALED = "ATR_SCALED"


# ---------------------------------------------------------------------- RiskDecision (output)

@dataclass(frozen=True, slots=True)
class DeniedReason:
    """``RISK_SCHEMA.json#/properties/denied_reasons`` item."""

    code: str
    detail: str | None = None
    observed: float | str | bool | None = None
    limit: float | str | bool | None = None


@dataclass(frozen=True, slots=True)
class AppliedRule:
    """``RISK_SCHEMA.json#/properties/applied_rules`` item -- one per pipeline gate evaluated, for
    audit (``RISK_MANAGER_ARCHITECTURE.md`` §6)."""

    rule: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class PartialExitPlanEntry:
    at_R: float
    fraction: float


@dataclass(frozen=True, slots=True)
class Sizing:
    """``RISK_SCHEMA.json#/properties/sizing`` (``POSITION_SIZING.md`` §10) -- present only for
    ``ALLOW`` decisions."""

    method: SizingMethod
    risk_per_trade_pct: float
    risk_R: float
    size_units: float
    min_size: float
    max_size: float
    quality_factor: float | None = None
    risk_budget_currency: float | None = None
    stop_distance: float | None = None
    size_lots: float | None = None
    notional: float | None = None
    leverage: float | None = None
    partial_exit_plan: tuple[PartialExitPlanEntry, ...] | None = None


@dataclass(frozen=True, slots=True)
class Constraints:
    """``RISK_SCHEMA.json#/properties/constraints`` -- present only for ``ALLOW`` decisions."""

    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    max_hold_bars: int | None = None
    valid_until: str | int | None = None
    max_slippage: float | None = None
    allowed_session: str | None = None
    reduce_only: bool | None = None


@dataclass(frozen=True, slots=True)
class PortfolioImpact:
    """``RISK_SCHEMA.json#/properties/portfolio_impact`` -- the running portfolio view AFTER this
    decision, for the next opportunity in the same batch (``RISK_MANAGER_ARCHITECTURE.md`` §5)."""

    open_positions_after: int | None = None
    portfolio_risk_pct_after: float | None = None
    leverage_after: float | None = None
    correlation_group: str | None = None


@dataclass(frozen=True, slots=True)
class RiskRefs:
    """``RISK_SCHEMA.json#/properties/refs``."""

    scoring_schema_version: str
    interface_version: str
    account_equity: float | None = None
    data_quality: DataQualityLevel | None = None


@dataclass(frozen=True, slots=True)
class RiskDecision:
    """``RISK_SCHEMA.json`` root object -- the canonical output of one opportunity's risk evaluation."""

    risk_schema_version: str
    risk_engine_version: str
    risk_policy_version: str
    decision_id: str
    score_id: str
    signal_id: str
    strategy_id: str
    symbol: str
    timestamp: int
    as_of: int
    engine_state: EngineState
    decision: Decision
    direction: Direction
    applied_rules: tuple[AppliedRule, ...]
    refs: RiskRefs
    denied_reasons: tuple[DeniedReason, ...] = ()
    sizing: Sizing | None = None
    constraints: Constraints | None = None
    portfolio_impact: PortfolioImpact | None = None


@dataclass(frozen=True, slots=True)
class RiskDecisionBatch:
    """``RISK_API.md`` §0."""

    as_of: int
    decisions: tuple[RiskDecision, ...]
    counts_by_decision: dict[str, int]
    engine_state: EngineState
    generated_at: int


@dataclass(frozen=True, slots=True)
class SizingResult:
    """``RISK_API.md`` §0 ``position_size()`` result -- ``sizing`` plus a validity flag/reason for
    the "does not itself apply the policy gates" contract (a zero/invalid result is still returned,
    never raised)."""

    sizing: Sizing
    valid: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class LimitsReport:
    """``RISK_API.md`` §2 ``portfolio_limits()`` result."""

    engine_state: EngineState
    limits: dict[str, float]
    current_utilization: dict[str, float]
    breaches: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Statistics:
    batches: int
    decisions_total: int
    allow: int
    deny: int
    by_reason: dict[str, int]
    avg_eval_ms: float


@dataclass(frozen=True, slots=True)
class EngineHealth:
    overall: EngineOverallHealth
    state: EngineLifecycleState
    degraded_reasons: tuple[str, ...] = ()
    supported_versions: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VersionInfo:
    risk_engine_version: str
    risk_schema_version: str
    risk_policy_version: str
    supported_scoring_schema_major: int
    supported_interface_major: int


@dataclass(frozen=True, slots=True)
class NotFound:
    """Typed "not found" result -- never an exception."""

    key: str


# ---------------------------------------------------------------------- RiskContext (input, own design)

@dataclass(frozen=True, slots=True)
class SymbolRiskSnapshot:
    """One symbol's live market-risk facts within a :class:`RiskContext` (``RISK_MANAGER_ARCHITECTURE.md``
    §3, ``RISK_POLICY.md`` §5/§6). Every field here is an OBSERVED fact (changes bar to bar);
    thresholds/assumptions it is compared against live in ``RiskConfig`` instead."""

    atr: float | None = None
    atr_rolling_median: float | None = None
    current_spread: float | None = None
    liquidity_proxy: float | None = None
    is_weekend_gap: bool = False
    bars_since_gap: int | None = None
    is_past_friday_cutoff: bool = False
    is_near_session_close: bool = False
    minutes_to_high_impact_event: float | None = None
    data_quality: DataQualityLevel = DataQualityLevel.OK


@dataclass(frozen=True, slots=True)
class RiskContext:
    """Passed-in market-risk snapshot (``RISK_MANAGER_ARCHITECTURE.md`` §3: "assembled upstream, NOT
    fetched"). ``per_symbol`` may omit a symbol -- treated as worst-case/unknown by the filters
    (fail-safe: never assume a symbol is safe when no data was supplied for it)."""

    as_of: int
    per_symbol: dict[str, SymbolRiskSnapshot] = field(default_factory=dict)
    data_quality: DataQualityLevel = DataQualityLevel.OK

    def for_symbol(self, symbol: str) -> SymbolRiskSnapshot:
        return self.per_symbol.get(symbol, SymbolRiskSnapshot(data_quality=DataQualityLevel.INSUFFICIENT))


# ---------------------------------------------------------------------- PortfolioState (input, own design)

@dataclass(frozen=True, slots=True)
class OpenPosition:
    """One currently-open position (``RISK_MANAGER_ARCHITECTURE.md`` §3: "symbol, direction, size,
    entry, age, correlation group"). ``risk_pct`` is this position's own risk-at-open (fraction of
    equity), needed to reconstruct ``LIMIT_MAX_EXPOSURE``'s "sum of open-position risk in R x
    R-value" without re-deriving it from stop distances the Risk Manager no longer has access to."""

    symbol: str
    strategy_id: str
    direction: Direction
    size_units: float
    entry_price: float
    opened_bars_ago: int
    risk_pct: float = 0.0
    notional: float = 0.0
    correlation_group: str | None = None


@dataclass(frozen=True, slots=True)
class ClosedPosition:
    """One recently-closed position, the cooldown-clock source (``RISK_POLICY.md`` §4: "Cooldown
    clocks are read from the Ledger/PortfolioState (realized exits)")."""

    symbol: str
    strategy_id: str
    was_loss: bool
    bars_since_close: int


@dataclass(frozen=True, slots=True)
class PortfolioState:
    """Read-only portfolio/account snapshot from the Portfolio Manager (``RISK_MANAGER_ARCHITECTURE.md``
    §3). ``current_drawdown`` is deliberately NOT a stored field -- it is always derived from
    ``equity``/``equity_high_water_mark`` internally (a fail-safe choice: never trust a redundant
    precomputed number that could silently disagree with the two inputs it should be derived from).
    """

    as_of: int
    equity: float
    equity_high_water_mark: float
    open_positions: tuple[OpenPosition, ...] = ()
    recent_closed_positions: tuple[ClosedPosition, ...] = ()
    realized_pnl_pct_daily: float = 0.0
    unrealized_pnl_pct_daily: float = 0.0
    realized_pnl_pct_weekly: float = 0.0
    unrealized_pnl_pct_weekly: float = 0.0
    gross_notional: float = 0.0
    consecutive_losses: int = 0
    minutes_since_last_loss: float | None = None
    is_stale: bool = False

    @property
    def daily_pnl_pct(self) -> float:
        return self.realized_pnl_pct_daily + self.unrealized_pnl_pct_daily

    @property
    def weekly_pnl_pct(self) -> float:
        return self.realized_pnl_pct_weekly + self.unrealized_pnl_pct_weekly

    @property
    def drawdown_pct(self) -> float:
        if self.equity_high_water_mark <= 0:
            return 0.0
        return max(0.0, (self.equity_high_water_mark - self.equity) / self.equity_high_water_mark)

    @property
    def portfolio_risk_pct(self) -> float:
        return sum(p.risk_pct for p in self.open_positions)

    @property
    def leverage(self) -> float:
        if self.equity <= 0:
            return 0.0
        return self.gross_notional / self.equity


#: Structural alias, matching Signal/Scoring Engine's own "name the exact upstream type" precedent.
JsonDict = dict[str, Any]
