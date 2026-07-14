"""Value types for the Execution Engine.

``OrderRequest`` and its nested objects mirror ``ORDER_SCHEMA.json`` exactly -- one frozen dataclass
per schema object, one ``str, Enum`` per closed vocabulary. Reuses the already-published, stable
``Direction`` from Signal Engine (the Execution Engine never redefines it).

The Broker Adapter is abstract-only in v1 (``README.md``: "v1 defines the contract, not an
integration"). ``BrokerCapabilities``/``BrokerAck``/``BrokerOrderState`` are this module's own
designed shapes for that contract -- the architecture docs name the CONCEPTS (supported order types/
TIF, tick size, lot step, min/max quantity, market status; submit/cancel/query semantics) in prose
without publishing a schema for them, so this is a documented IMPLEMENTATION CHOICE, exactly the same
class of gap-fill as Risk Manager's own ``RiskContext``/``PortfolioState`` (see
``EXECUTION_ENGINE_VALIDATION_REPORT.md`` for the full rationale). A future real Broker Adapter would
need to satisfy this exact contract (or a frozen evolution of it) to plug in unmodified.

Portfolio Manager gap: no such module exists (``EXECUTION_ENGINE_HANDOFF.md`` §2b). This module reuses
``ai_trader.risk_manager.types.PortfolioState``/``OpenPosition`` directly -- Risk Manager is an allowed
direct dependency per the interaction matrix, and its ``PortfolioState`` already has the exact shape
(equity, open positions, computed exposure/leverage/drawdown) a "read PortfolioState" consumer needs.
This is IMPLEMENTATION CHOICE #1, documented in the validation report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ai_trader.signal_engine.types import Direction

# ---------------------------------------------------------------------- closed vocabularies


class OrderSide(str, Enum):
    """``ORDER_SCHEMA.json#/properties/side``."""

    BUY = "BUY"
    SELL = "SELL"


class OrderIntent(str, Enum):
    """``ORDER_SCHEMA.json#/properties/intent``."""

    OPEN = "OPEN"
    CLOSE = "CLOSE"
    REDUCE = "REDUCE"
    SCALE_IN = "SCALE_IN"
    SCALE_OUT = "SCALE_OUT"


class OrderType(str, Enum):
    """``ORDER_SCHEMA.json#/properties/order_type`` (``ORDER_LIFECYCLE.md`` §4)."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    OCO = "OCO"
    BRACKET = "BRACKET"


class TimeInForce(str, Enum):
    """``ORDER_SCHEMA.json#/properties/time_in_force`` (``ORDER_LIFECYCLE.md`` §5)."""

    IOC = "IOC"
    FOK = "FOK"
    GTC = "GTC"
    DAY = "DAY"


class OcoRole(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"


class OrderState(str, Enum):
    """The 11 order states (``ORDER_LIFECYCLE.md`` §1). No extra states are invented."""

    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


#: ``ORDER_LIFECYCLE.md`` §1: "Terminal states: FILLED, CANCELLED, REJECTED, EXPIRED, FAILED."
TERMINAL_STATES: frozenset[OrderState] = frozenset({
    OrderState.FILLED, OrderState.CANCELLED, OrderState.REJECTED, OrderState.EXPIRED, OrderState.FAILED,
})

#: The pre-submit states (``ORDER_LIFECYCLE.md`` §1) -- a rejection here means nothing was ever sent
#: to the (future) venue.
PRE_SUBMIT_STATES: frozenset[OrderState] = frozenset({
    OrderState.CREATED, OrderState.VALIDATED, OrderState.QUEUED,
})


class EngineLifecycleState(str, Enum):
    """The engine lifecycle (``EXECUTION_STATE_MACHINE.md`` §A). Exactly the 7 documented states --
    no extras invented."""

    IDLE = "IDLE"
    RECONCILING = "RECONCILING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    EMERGENCY_FLATTEN = "EMERGENCY_FLATTEN"
    DRAINING = "DRAINING"
    STOPPED = "STOPPED"


class EngineOverallHealth(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class MarketStatus(str, Enum):
    """Part of the abstract ``BrokerCapabilities`` contract (IMPLEMENTATION CHOICE, see module
    docstring). ``UNKNOWN`` is the fail-safe default for a symbol the capabilities profile never
    declared -- "cannot confirm tradable," never "assume open," mirroring every prior module's
    fail-safe-on-unverifiable-state precedent."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------- OrderRequest (ORDER_SCHEMA.json)


@dataclass(frozen=True, slots=True)
class BracketLegs:
    """``ORDER_SCHEMA.json#/properties/bracket``."""

    take_profit: float | None = None
    stop_loss: float | None = None


@dataclass(frozen=True, slots=True)
class OcoLink:
    """``ORDER_SCHEMA.json#/properties/oco_link``."""

    group_id: str
    role: OcoRole


@dataclass(frozen=True, slots=True)
class OrderConstraints:
    """``ORDER_SCHEMA.json#/properties/constraints``. ``max_slippage``/``reduce_only``/``post_only``
    are schema-required (``post_only`` and ``reduce_only`` default False -- explicit, never implicit)."""

    max_slippage: float | None
    reduce_only: bool
    post_only: bool
    valid_until: str | int | None = None
    allowed_session: str | None = None
    max_hold_bars: int | None = None


@dataclass(frozen=True, slots=True)
class BrokerCapabilitiesRef:
    """``ORDER_SCHEMA.json#/properties/broker_capabilities_ref`` -- the capability profile an order
    was validated against, echoed onto the order for audit."""

    tick_size: float | None = None
    lot_step: float | None = None
    min_qty: float | None = None
    max_qty: float | None = None
    contract_version: str | None = None


@dataclass(frozen=True, slots=True)
class OrderRefs:
    """``ORDER_SCHEMA.json#/properties/refs``."""

    risk_schema_version: str
    risk_policy_version: str
    account: str | None = None


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """``ORDER_SCHEMA.json`` root object -- the fully-specified, idempotent order built from an
    approved ``RiskDecision``. Carries no fills and performs no execution; it is the request."""

    order_schema_version: str
    execution_engine_version: str
    order_request_id: str
    client_order_id: str
    decision_id: str
    strategy_id: str
    symbol: str
    timestamp: int
    as_of: int
    side: OrderSide
    direction: Direction
    intent: OrderIntent
    order_type: OrderType
    time_in_force: TimeInForce
    quantity: float
    constraints: OrderConstraints
    refs: OrderRefs
    score_id: str | None = None
    signal_id: str | None = None
    lots: float | None = None
    limit_price: float | None = None
    stop_price: float | None = None
    bracket: BracketLegs | None = None
    oco_link: OcoLink | None = None
    broker_capabilities_ref: BrokerCapabilitiesRef | None = None


# ---------------------------------------------------------------------- API summary types (EXECUTION_API.md §0)


@dataclass(frozen=True, slots=True)
class OrderStatus:
    order_request_id: str
    client_order_id: str
    state: OrderState
    filled_qty: float = 0.0
    remaining_qty: float = 0.0
    avg_price: float | None = None
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    order_request_id: str
    client_order_id: str
    terminal_state: OrderState
    filled_qty: float = 0.0
    avg_price: float | None = None
    fees: float = 0.0
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Fill:
    """One confirmed fill event, reported to the Portfolio Manager as it occurs
    (``EXECUTION_FAILURE_POLICY.md`` §4)."""

    client_order_id: str
    symbol: str
    direction: Direction
    qty: float
    price: float
    as_of: int


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    as_of: int
    results: tuple[ExecutionResult, ...] = ()
    fills: tuple[Fill, ...] = ()
    counts_by_state: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Statistics:
    orders_total: int
    by_state: dict[str, int]
    fills: int
    rejects: int
    failures: int
    avg_submit_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class EngineHealth:
    overall: EngineOverallHealth
    state: EngineLifecycleState
    degraded_reasons: tuple[str, ...] = ()
    broker_available: bool = True
    supported_versions: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VersionInfo:
    execution_engine_version: str
    order_schema_version: str
    broker_adapter_contract_version: str
    supported_risk_schema_major: int


@dataclass(frozen=True, slots=True)
class NotFound:
    requested_id: str


@dataclass(frozen=True, slots=True)
class FlattenScope:
    """The scope of an ``emergency_flatten`` command (``EXECUTION_API.md`` §3). IMPLEMENTATION CHOICE:
    the architecture names ``scope`` without fixing its shape. ``symbols=None`` means "every open
    position" (the conservative default -- a full flatten, matching "refuse new opening orders" being
    the DEFAULT posture of ``EMERGENCY_FLATTEN`` state); a non-``None`` frozenset restricts the flatten
    to those symbols only."""

    symbols: frozenset[str] | None = None


# ---------------------------------------------------------------------- Broker Adapter contract (abstract, IMPLEMENTATION CHOICE)


@dataclass(frozen=True, slots=True)
class BrokerCapabilities:
    """The abstract capability profile (``EXECUTION_ENGINE_ARCHITECTURE.md`` §3) -- a DECLARED
    capability set in v1, never a live integration. A symbol absent from ``market_status`` is
    ``MarketStatus.UNKNOWN`` (fail-safe: never assume a market is open)."""

    supported_order_types: frozenset[OrderType]
    supported_time_in_force: frozenset[TimeInForce]
    tick_size: float
    lot_step: float
    min_qty: float
    max_qty: float
    contract_version: str = "1.0.0"
    market_status: dict[str, MarketStatus] = field(default_factory=dict)

    def status_for(self, symbol: str) -> MarketStatus:
        return self.market_status.get(symbol, MarketStatus.UNKNOWN)


@dataclass(frozen=True, slots=True)
class BrokerAck:
    """The broker's immediate response to a submit/cancel call (``EXECUTION_SEQUENCE.md`` §2/§5)."""

    accepted: bool
    broker_order_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class BrokerOrderState:
    """The broker's current view of one order, as returned by ``query_status``/``query_open_orders``
    (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5's Reconciler: "query the broker for the order's true
    state"). ``state`` is one of the in-flight/terminal :class:`OrderState` values -- a broker never
    reports the engine-internal pre-submit states (``CREATED``/``VALIDATED``/``QUEUED``)."""

    client_order_id: str
    state: OrderState
    filled_qty: float = 0.0
    avg_price: float | None = None
    reason: str | None = None
