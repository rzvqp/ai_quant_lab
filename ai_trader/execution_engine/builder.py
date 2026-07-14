"""The Order Builder (``EXECUTION_ENGINE_ARCHITECTURE.md`` §5/§6 stage 2): deterministically maps an
approved ``RiskDecision`` + the running ``PortfolioState`` + the abstract ``BrokerCapabilities`` into
an ``OrderRequest`` -- never submits, never mutates state. See ``ORDER_LIFECYCLE.md`` §6 for the
default type-mapping policy this implements, and ``config.py``'s ``OrderTypeMappingPolicy``/
``RoundingPolicy``/``QuantityLimitPolicy`` docstrings for every IMPLEMENTATION CHOICE made here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ai_trader.execution_engine.config import ExecConfig
from ai_trader.execution_engine.types import (
    BracketLegs,
    BrokerCapabilities,
    BrokerCapabilitiesRef,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.risk_manager.types import OpenPosition, PortfolioState, RiskDecision
from ai_trader.signal_engine.types import Direction


@dataclass(frozen=True, slots=True)
class BuildOutcome:
    success: bool
    order: OrderRequest | None = None
    reason: str | None = None


def _round_to_increment(value: float, increment: float) -> float:
    """Round-half-up to the nearest multiple of ``increment`` (IMPLEMENTATION CHOICE, see
    ``config.py::RoundingPolicy``). ``increment <= 0`` means "no configured increment" -- the value
    passes through unrounded (nothing to round to)."""
    if increment <= 0:
        return value
    return math.floor(value / increment + 0.5) * increment


def _side_for(direction: Direction, reduce_only: bool) -> OrderSide | None:
    """Opening/scaling orders trade WITH the decision's direction (LONG->BUY, SHORT->SELL, matching
    ``ORDER_SCHEMA.json``'s own conditional requirement); reduce/close orders trade AGAINST it (a
    closing sale exits a LONG, a closing buy exits a SHORT)."""
    if direction is Direction.LONG:
        return OrderSide.SELL if reduce_only else OrderSide.BUY
    if direction is Direction.SHORT:
        return OrderSide.BUY if reduce_only else OrderSide.SELL
    return None


def _intent_for(decision: RiskDecision, portfolio: PortfolioState, reduce_only: bool) -> OrderIntent:
    if not reduce_only:
        return OrderIntent.OPEN
    matching = next(
        (p for p in portfolio.open_positions
         if p.symbol == decision.symbol and p.strategy_id == decision.strategy_id),
        None,
    )
    sizing = decision.sizing
    if matching is None or sizing is None or sizing.size_units >= matching.size_units:
        return OrderIntent.CLOSE
    return OrderIntent.REDUCE


def build_order(
    decision: RiskDecision, portfolio: PortfolioState, caps: BrokerCapabilities, config: ExecConfig,
) -> BuildOutcome:
    """Deterministically construct (never submit) an ``OrderRequest`` from an approved decision.

    **Determinism note on ``timestamp``**: set to the decision's own ``as_of`` (never wall-clock) --
    the identical precedent every downstream engine before this one has followed (Signal/Scoring/Risk
    Manager's own ``timestamp`` fields), since there is no other deterministic time source available
    without violating "no wall-clock in business logic." ``ORDER_SCHEMA.json`` names ``timestamp`` and
    ``as_of`` as two fields with different prose descriptions, but no other module has ever had a
    genuine second time source to give them different values, so neither does this one.
    """
    if decision.direction is Direction.NONE:
        return BuildOutcome(False, reason="INVALID_DIRECTION: decision carries no concrete direction")

    sizing = decision.sizing
    constraints = decision.constraints
    if sizing is None or constraints is None:
        return BuildOutcome(False, reason="MISSING_SIZING_OR_CONSTRAINTS: only ALLOW decisions can be built")

    reduce_only = bool(constraints.reduce_only)
    side = _side_for(decision.direction, reduce_only)
    if side is None:
        return BuildOutcome(False, reason="INVALID_DIRECTION: could not derive an order side")
    intent = _intent_for(decision, portfolio, reduce_only)

    quantity = sizing.size_units
    if config.rounding.round_quantity:
        quantity = _round_to_increment(quantity, caps.lot_step)
    if config.quantity_limits.clamp_to_max_qty and caps.max_qty > 0:
        quantity = min(quantity, caps.max_qty)
    if quantity < caps.min_qty or quantity <= 0:
        return BuildOutcome(
            False, reason=f"QTY_BELOW_MIN: {quantity!r} below broker min_qty {caps.min_qty!r}",
        )

    entry = constraints.entry
    stop = constraints.stop
    target = constraints.target
    if config.rounding.round_prices:
        if entry is not None:
            entry = _round_to_increment(entry, caps.tick_size)
        if stop is not None:
            stop = _round_to_increment(stop, caps.tick_size)
        if target is not None:
            target = _round_to_increment(target, caps.tick_size)

    limit_price: float | None = None
    bracket: BracketLegs | None = None
    if reduce_only:
        order_type = OrderType.MARKET
        time_in_force = config.order_mapping.close_time_in_force
    elif stop is not None or target is not None:
        order_type = OrderType.BRACKET
        limit_price = entry
        bracket = BracketLegs(take_profit=target, stop_loss=stop)
        time_in_force = config.order_mapping.open_time_in_force
    elif entry is not None:
        order_type = OrderType.LIMIT
        limit_price = entry
        time_in_force = config.order_mapping.open_time_in_force
    else:
        order_type = OrderType.MARKET
        time_in_force = config.order_mapping.open_time_in_force

    is_marketable = limit_price is None  # MARKET, or a BRACKET whose parent entry has no limit_price
    max_slippage = constraints.max_slippage
    if is_marketable and max_slippage is None:
        return BuildOutcome(
            False, reason="MISSING_MAX_SLIPPAGE: a marketable order requires a max_slippage constraint",
        )

    if order_type not in caps.supported_order_types:
        return BuildOutcome(False, reason=f"UNSUPPORTED_ORDER_TYPE: {order_type.value} not in broker capabilities")
    if time_in_force not in caps.supported_time_in_force:
        return BuildOutcome(False, reason=f"UNSUPPORTED_TIME_IN_FORCE: {time_in_force.value} not in broker capabilities")

    decision_id = decision.decision_id
    order = OrderRequest(
        order_schema_version=config.order_schema_version,
        execution_engine_version=config.execution_engine_version,
        order_request_id=f"{config.order_request_id_prefix}-{decision_id}",
        client_order_id=f"{config.client_order_id_prefix}-{decision_id}",
        decision_id=decision_id,
        score_id=decision.score_id or None,
        signal_id=decision.signal_id or None,
        strategy_id=decision.strategy_id,
        symbol=decision.symbol,
        timestamp=decision.as_of,
        as_of=decision.as_of,
        side=side,
        direction=decision.direction,
        intent=intent,
        order_type=order_type,
        time_in_force=time_in_force,
        quantity=quantity,
        limit_price=limit_price,
        stop_price=None,
        bracket=bracket,
        oco_link=None,
        constraints=OrderConstraints(
            max_slippage=max_slippage,
            reduce_only=reduce_only,
            post_only=False,
            valid_until=constraints.valid_until,
            allowed_session=constraints.allowed_session,
            max_hold_bars=constraints.max_hold_bars,
        ),
        broker_capabilities_ref=BrokerCapabilitiesRef(
            tick_size=caps.tick_size, lot_step=caps.lot_step, min_qty=caps.min_qty,
            max_qty=caps.max_qty, contract_version=caps.contract_version,
        ),
        refs=OrderRefs(
            risk_schema_version=decision.risk_schema_version,
            risk_policy_version=decision.risk_policy_version,
        ),
    )
    return BuildOutcome(True, order=order)


def build_flatten_order(
    position: OpenPosition, caps: BrokerCapabilities, config: ExecConfig, as_of: int,
    risk_schema_version: str, risk_policy_version: str,
) -> BuildOutcome:
    """Build a reduce-only closing ``OrderRequest`` directly from an ``OpenPosition`` -- used ONLY by
    ``ExecutionEngine.emergency_flatten`` (``EXECUTION_SEQUENCE.md`` §8: "for each in-scope open
    position: build reduce_only closing order"). There is no ``RiskDecision`` for a flatten command (it
    is issued directly by the Risk Manager, ``EXECUTION_API.md`` §3), so this is a deliberately
    separate, narrower builder: always MARKET + reduce_only + CLOSE, no bracket (a closing order does
    not need its own protective legs), idempotent per ``(strategy_id, symbol, as_of)`` so a repeated
    flatten command for the same position at the same ``as_of`` never double-submits.
    """
    if position.direction is Direction.NONE:
        return BuildOutcome(False, reason="INVALID_DIRECTION: position carries no concrete direction")
    side = OrderSide.SELL if position.direction is Direction.LONG else OrderSide.BUY

    quantity = position.size_units
    if config.rounding.round_quantity:
        quantity = _round_to_increment(quantity, caps.lot_step)
    if quantity < caps.min_qty or quantity <= 0:
        return BuildOutcome(False, reason=f"QTY_BELOW_MIN: {quantity!r} below broker min_qty {caps.min_qty!r}")

    if OrderType.MARKET not in caps.supported_order_types:
        return BuildOutcome(False, reason="UNSUPPORTED_ORDER_TYPE: MARKET not in broker capabilities")
    time_in_force = config.order_mapping.close_time_in_force
    if time_in_force not in caps.supported_time_in_force:
        return BuildOutcome(False, reason=f"UNSUPPORTED_TIME_IN_FORCE: {time_in_force.value} not in broker capabilities")

    flatten_id = f"FLATTEN-{position.strategy_id}-{position.symbol}-{as_of}"
    order = OrderRequest(
        order_schema_version=config.order_schema_version,
        execution_engine_version=config.execution_engine_version,
        order_request_id=f"{config.order_request_id_prefix}-{flatten_id}",
        client_order_id=f"{config.client_order_id_prefix}-{flatten_id}",
        decision_id=flatten_id,
        strategy_id=position.strategy_id,
        symbol=position.symbol,
        timestamp=as_of,
        as_of=as_of,
        side=side,
        direction=position.direction,
        intent=OrderIntent.CLOSE,
        order_type=OrderType.MARKET,
        time_in_force=time_in_force,
        quantity=quantity,
        limit_price=None,
        stop_price=None,
        bracket=None,
        oco_link=None,
        constraints=OrderConstraints(
            max_slippage=config.flatten_max_slippage, reduce_only=True, post_only=False,
        ),
        broker_capabilities_ref=BrokerCapabilitiesRef(
            tick_size=caps.tick_size, lot_step=caps.lot_step, min_qty=caps.min_qty,
            max_qty=caps.max_qty, contract_version=caps.contract_version,
        ),
        refs=OrderRefs(risk_schema_version=risk_schema_version, risk_policy_version=risk_policy_version),
    )
    return BuildOutcome(True, order=order)
