"""Value types for the Simulation Framework.

Mirrors ``SIMULATION_SCHEMA.json`` for every wire-shaped object (one frozen dataclass per schema
object, one ``str, Enum`` per closed vocabulary), exactly the pattern every prior module's own
``types.py`` used. Internal-only types (never serialized directly, no schema entry) are documented as
such -- ``Bar``, ``WorkingOrder``, ``SimAccount``/``Position`` (see ``portfolio_simulator.py``), and
``SimFillEvent`` are this module's own IMPLEMENTATION CHOICE shapes, the same class of gap-fill as
Risk Manager's ``PortfolioState``/``RiskContext`` or Execution Engine's ``BrokerCapabilities``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ai_trader.execution_engine.types import OrderType, TimeInForce
from ai_trader.signal_engine.types import Direction

# ---------------------------------------------------------------------- run lifecycle (SIMULATION_STATE_MACHINE.md A)


class RunState(str, Enum):
    """The 9 documented run-lifecycle states (``SIMULATION_STATE_MACHINE.md`` §A). No extra states
    are invented."""

    UNINITIALIZED = "UNINITIALIZED"
    CONFIGURED = "CONFIGURED"
    LOADING = "LOADING"
    WARMUP = "WARMUP"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


#: ``SIMULATION_STATE_MACHINE.md`` §A: "COMPLETED/FAILED/STOPPED are terminal for the run."
TERMINAL_RUN_STATES: frozenset[RunState] = frozenset({RunState.COMPLETED, RunState.FAILED, RunState.STOPPED})


class SimPhase(str, Enum):
    """``SIMULATION_CONTEXT.md`` §B: WARMUP bars never trade and are excluded from stats."""

    WARMUP = "WARMUP"
    RUNNING = "RUNNING"


class SimMode(str, Enum):
    """``SIMULATION_CONTEXT.md`` §C: the ONLY conceptual live/sim difference; ``LIVE`` is the future
    counterpart with the identical runtime-context shape."""

    SIMULATION = "SIMULATION"
    LIVE = "LIVE"


class PerBarSubState(str, Enum):
    """The per-bar cycle sub-states (``SIMULATION_STATE_MACHINE.md`` §B), in fixed order."""

    CLOCK_TICK = "CLOCK_TICK"
    CONTEXT_BUILD = "CONTEXT_BUILD"
    SIGNAL = "SIGNAL"
    SCORE = "SCORE"
    RISK = "RISK"
    ORDER = "ORDER"
    FILL = "FILL"
    ACCOUNT = "ACCOUNT"
    RECORD = "RECORD"
    ROLLUP = "ROLLUP"


class CloseAtEndPolicy(str, Enum):
    """``SIMULATION_CONTEXT.md`` §A.6."""

    CLOSE_AT_LAST = "close_at_last"
    HOLD_AND_MARK = "hold_and_mark"


# ---------------------------------------------------------------------- cost / fill models (SIMULATION_CONTEXT.md A.3)


class EntryTiming(str, Enum):
    """``SIMULATION_SCHEMA.json#/properties/context/properties/fill_model/properties/entry_timing``."""

    NEXT_OPEN = "next_open"
    CLOSE = "close"
    SIGNAL_CLOSE = "signal_close"


class IntrabarRule(str, Enum):
    """``SIMULATION_SCHEMA.json#/.../fill_model/properties/intrabar``."""

    STOP_BEFORE_TARGET = "stop_before_target"
    TARGET_BEFORE_STOP = "target_before_stop"
    PROPORTIONAL = "proportional"


class SlippageModelType(str, Enum):
    """``EXECUTION_SIMULATOR.md`` §4."""

    FIXED = "fixed"
    ATR_FRACTION = "atr_fraction"
    SEEDED_RANDOM = "seeded_random"


class PartialFillPolicy(str, Enum):
    """``EXECUTION_SIMULATOR.md`` §5. IMPLEMENTATION CHOICE (``IMPLEMENTATION_CHOICES.md`` §3):
    ``FULL_FILL`` is the documented v1 default ("full-fill for liquid instruments (default)");
    ``FIXED_FRACTION`` is a deterministic, config-driven alternative for exercising the partial-fill
    path, since no real liquidity/depth data exists in this repo."""

    FULL_FILL = "full_fill"
    FIXED_FRACTION = "fixed_fraction"


class LatencyModelType(str, Enum):
    """IMPLEMENTATION CHOICE (``IMPLEMENTATION_CHOICES.md`` §4): only ``NONE`` is implemented in v1."""

    NONE = "none"


# ---------------------------------------------------------------------- historical data (internal, no schema entry)


@dataclass(frozen=True, slots=True)
class Bar:
    """One OHLCV historical bar, as fed by the Replay Data Source. Internal type -- not part of
    ``SIMULATION_SCHEMA.json`` (no wire representation; bars are input data, never emitted)."""

    symbol: str
    timeframe: str
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


# ---------------------------------------------------------------------- Execution Simulator internals


class WorkingOrderState(str, Enum):
    """The Execution Simulator's own internal per-order state -- a superset mapped onto
    ``ai_trader.execution_engine.types.OrderState`` when reported via ``BrokerOrderState``
    (``ORDER_LIFECYCLE.md``'s 11 states; this simulator only ever reports the in-flight/terminal
    subset a real broker would, never the engine-internal pre-submit states, matching
    ``BrokerOrderState``'s own docstring)."""

    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


#: ``EXECUTION_SIMULATOR.md`` §7 order lifecycle emission -- terminal states, mirrors
#: ``execution_engine.types.TERMINAL_STATES`` for this module's own narrower vocabulary.
TERMINAL_WORKING_STATES: frozenset[WorkingOrderState] = frozenset({
    WorkingOrderState.FILLED, WorkingOrderState.CANCELLED,
    WorkingOrderState.REJECTED, WorkingOrderState.EXPIRED,
})


@dataclass(slots=True)
class WorkingOrder:
    """The Execution Simulator's own mutable per-order book entry. Internal type: never serialized,
    never crosses the ``BrokerAdapter`` boundary directly (``query_status``/``query_open_orders``
    project this onto ``BrokerOrderState`` instead, per ``IMPLEMENTATION_CHOICES.md`` §1)."""

    client_order_id: str
    symbol: str
    order_type: OrderType
    side_is_buy: bool
    direction: Direction
    quantity: float
    time_in_force: TimeInForce
    submitted_as_of: int
    strategy_id: str
    limit_price: float | None = None
    stop_price: float | None = None
    take_profit: float | None = None
    stop_loss: float | None = None
    reduce_only: bool = False
    max_slippage: float | None = None
    valid_until: int | None = None
    oco_group_id: str | None = None

    state: WorkingOrderState = WorkingOrderState.ACKNOWLEDGED
    filled_qty: float = 0.0
    avg_price: float | None = None
    reason: str | None = None
    #: True once this order has been eligible for at least one ``advance_bar`` match pass -- i.e. its
    #: ``submitted_as_of`` bar has fully elapsed. Never matched on the bar it was submitted on
    #: (``EXECUTION_SIMULATOR.md`` §3: "never the signal bar").
    activated_child_oco: str | None = None

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_WORKING_STATES

    @property
    def remaining_qty(self) -> float:
        return max(0.0, self.quantity - self.filled_qty)


@dataclass(frozen=True, slots=True)
class SimFillEvent:
    """One confirmed fill, as produced by the Execution Simulator and consumed directly by the
    Portfolio Simulator (``SIMULATION_ARCHITECTURE.md`` §4: "EXSIM.match ... -> fills / OrderStatus" ->
    "PSIM: apply(fills)"). Richer than ``execution_engine.types.Fill`` (which carries no commission) --
    this is the simulation-only, full-economics fill record; the Execution Simulator separately reports
    the leaner ``Fill``/``BrokerOrderState`` shapes to the Execution Engine via the ``BrokerAdapter``
    contract (``IMPLEMENTATION_CHOICES.md`` §1)."""

    client_order_id: str
    order_request_id: str
    strategy_id: str
    symbol: str
    direction: Direction
    intent_close: bool
    qty: float
    price: float
    spread_cost: float
    slippage_cost: float
    commission: float
    as_of: int
    reduce_only: bool = False


@dataclass(frozen=True, slots=True)
class RiskEventRecord:
    """One risk/account event for the Performance Analyzer's risk-event summary
    (``PERFORMANCE_ANALYZER.md`` §6). Internal type -- aggregated into ``report.risk_events`` by type."""

    type: str
    as_of: int
    detail: str | None = None
