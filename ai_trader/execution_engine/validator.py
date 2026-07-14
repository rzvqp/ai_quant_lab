"""The Order Validator (``EXECUTION_ENGINE_ARCHITECTURE.md`` §8): mechanical, order-mechanics-only
validation of an already-built ``OrderRequest`` -- NEVER a risk re-decision (risk was already decided
by the Risk Manager). Runs WITHOUT submitting (``EXECUTION_API.md``'s ``validate_order``); duplicate-
prevention is a SEPARATE pipeline stage (the architecture's own stage 3 "Validate" vs. stage 4
"Duplicate guard" split, ``EXECUTION_ENGINE_ARCHITECTURE.md`` §6) and is handled by
:mod:`ai_trader.execution_engine.pipeline`, not here -- matching ``EXECUTION_API.md``'s own
``validate_order(order, caps, portfolio)`` signature, which carries no ledger/duplicate-lookup input.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from ai_trader.execution_engine.schema_validation import validate_order_dict
from ai_trader.execution_engine.types import (
    BrokerCapabilities,
    MarketStatus,
    OrderIntent,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
    ValidationResult,
)
from ai_trader.risk_manager.types import PortfolioState
from ai_trader.signal_engine.types import Direction

_TICK_TOLERANCE_FACTOR = 1e-6  # relative tolerance for float multiple-of checks after builder rounding


def order_to_dict(order: OrderRequest) -> dict[str, Any]:
    """Serialize an :class:`OrderRequest` to the exact ``ORDER_SCHEMA.json`` shape."""
    data: dict[str, Any] = {
        "order_schema_version": order.order_schema_version,
        "execution_engine_version": order.execution_engine_version,
        "order_request_id": order.order_request_id,
        "client_order_id": order.client_order_id,
        "decision_id": order.decision_id,
        "score_id": order.score_id,
        "signal_id": order.signal_id,
        "strategy_id": order.strategy_id,
        "symbol": order.symbol,
        "timestamp": order.timestamp,
        "as_of": order.as_of,
        "side": order.side.value,
        "direction": order.direction.value,
        "intent": order.intent.value,
        "order_type": order.order_type.value,
        "time_in_force": order.time_in_force.value,
        "quantity": order.quantity,
        "lots": order.lots,
        "limit_price": order.limit_price,
        "stop_price": order.stop_price,
        "bracket": (
            {"take_profit": order.bracket.take_profit, "stop_loss": order.bracket.stop_loss}
            if order.bracket is not None else None
        ),
        "oco_link": (
            {"group_id": order.oco_link.group_id, "role": order.oco_link.role.value}
            if order.oco_link is not None else None
        ),
        "constraints": {
            "max_slippage": order.constraints.max_slippage,
            "reduce_only": order.constraints.reduce_only,
            "post_only": order.constraints.post_only,
            "valid_until": order.constraints.valid_until,
            "allowed_session": order.constraints.allowed_session,
            "max_hold_bars": order.constraints.max_hold_bars,
        },
        "broker_capabilities_ref": (
            {
                "tick_size": order.broker_capabilities_ref.tick_size,
                "lot_step": order.broker_capabilities_ref.lot_step,
                "min_qty": order.broker_capabilities_ref.min_qty,
                "max_qty": order.broker_capabilities_ref.max_qty,
                "contract_version": order.broker_capabilities_ref.contract_version,
            } if order.broker_capabilities_ref is not None else None
        ),
        "refs": {
            "risk_schema_version": order.refs.risk_schema_version,
            "risk_policy_version": order.refs.risk_policy_version,
            "account": order.refs.account,
        },
    }
    return data


@dataclass(frozen=True, slots=True)
class _Check:
    ok: bool
    reason: str | None = None


def _is_multiple_of(value: float, increment: float) -> bool:
    if not math.isfinite(value):
        return False  # non-finite is never "a multiple of" anything -- caught here defensively even
        # though _check_price_validation independently flags it too (checks are never short-circuited,
        # so every check runs against every field regardless of what an earlier check already found).
    if increment <= 0:
        return True
    remainder = abs(value - round(value / increment) * increment)
    return remainder <= max(increment * _TICK_TOLERANCE_FACTOR, 1e-9)


def _check_direction(order: OrderRequest) -> _Check:
    expected_open_side = {Direction.LONG: OrderSide.BUY, Direction.SHORT: OrderSide.SELL}
    if order.intent in (OrderIntent.OPEN, OrderIntent.SCALE_IN):
        wanted = expected_open_side.get(order.direction)
        if wanted is None or order.side is not wanted:
            return _Check(False, f"DIRECTION_MISMATCH: {order.intent.value} with direction={order.direction.value} requires side={wanted}")
        return _Check(True)
    # CLOSE/REDUCE/SCALE_OUT trade against the position's direction.
    wanted_close_side = {Direction.LONG: OrderSide.SELL, Direction.SHORT: OrderSide.BUY}
    wanted = wanted_close_side.get(order.direction)
    if wanted is None or order.side is not wanted:
        return _Check(False, f"DIRECTION_MISMATCH: {order.intent.value} with direction={order.direction.value} requires side={wanted}")
    return _Check(True)


def _check_position_limit_consistency(order: OrderRequest, portfolio: PortfolioState) -> _Check:
    """Defensive consistency guard, NOT a risk re-decision (§8: "does not exceed what the RiskDecision
    authorized ... not opening a 2nd position the decision didn't authorize")."""
    if order.intent is not OrderIntent.OPEN:
        return _Check(True)
    already_open = any(
        p.symbol == order.symbol and p.strategy_id == order.strategy_id for p in portfolio.open_positions
    )
    if already_open:
        return _Check(False, "POSITION_LIMIT_CONSISTENCY: an OPEN order for a symbol/strategy that already has an open position")
    return _Check(True)


def _check_price_validation(order: OrderRequest) -> _Check:
    if order.order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT):
        if order.limit_price is None or not math.isfinite(order.limit_price) or order.limit_price <= 0:
            return _Check(False, f"PRICE_VALIDATION: {order.order_type.value} requires a finite, positive limit_price")
    if order.order_type in (OrderType.STOP, OrderType.STOP_LIMIT):
        if order.stop_price is None or not math.isfinite(order.stop_price) or order.stop_price <= 0:
            return _Check(False, f"PRICE_VALIDATION: {order.order_type.value} requires a finite, positive stop_price")
    if order.order_type is OrderType.BRACKET:
        if order.bracket is None:
            return _Check(False, "PRICE_VALIDATION: BRACKET requires bracket legs")
        for label, price in (("take_profit", order.bracket.take_profit), ("stop_loss", order.bracket.stop_loss)):
            if price is not None and not math.isfinite(price):
                return _Check(False, f"PRICE_VALIDATION: bracket.{label} is not finite")
        if order.limit_price is not None and not math.isfinite(order.limit_price):
            return _Check(False, "PRICE_VALIDATION: limit_price is not finite")
    return _Check(True)


def _check_tick_size(order: OrderRequest, caps: BrokerCapabilities) -> _Check:
    prices = [order.limit_price, order.stop_price]
    if order.bracket is not None:
        prices += [order.bracket.take_profit, order.bracket.stop_loss]
    for price in prices:
        if price is not None and not _is_multiple_of(price, caps.tick_size):
            return _Check(False, f"TICK_SIZE: {price!r} is not a multiple of tick_size {caps.tick_size!r}")
    return _Check(True)


def _check_lot_size(order: OrderRequest, caps: BrokerCapabilities) -> _Check:
    if not _is_multiple_of(order.quantity, caps.lot_step):
        return _Check(False, f"LOT_SIZE: quantity {order.quantity!r} is not a multiple of lot_step {caps.lot_step!r}")
    return _Check(True)


def _check_quantity_bounds(order: OrderRequest, caps: BrokerCapabilities) -> _Check:
    if order.quantity < caps.min_qty:
        return _Check(False, f"MIN_QTY: quantity {order.quantity!r} below min_qty {caps.min_qty!r}")
    if caps.max_qty > 0 and order.quantity > caps.max_qty:
        return _Check(False, f"MAX_QTY: quantity {order.quantity!r} above max_qty {caps.max_qty!r}")
    return _Check(True)


def _check_slippage(order: OrderRequest) -> _Check:
    is_marketable = order.limit_price is None
    if is_marketable and (order.constraints.max_slippage is None or order.constraints.max_slippage < 0):
        return _Check(False, "SLIPPAGE_LIMITS: a marketable order requires a non-negative max_slippage")
    return _Check(True)


def _check_time_restrictions(order: OrderRequest) -> _Check:
    """§8's "time restrictions: within allowed_session; respect valid_until/expire_time; TIF
    consistent". IMPLEMENTATION CHOICE (documented, not a silent omission): v1 has no wall-clock in its
    business logic (the standing rule followed by every AI Trader module) and therefore no "now" to
    compare ``allowed_session``/``valid_until`` against -- those two sub-checks cannot be evaluated
    here without violating that rule, and are deferred to whatever consumes ``OrderStatus`` over time
    (a future Execution Simulator, which DOES have a clock). What CAN be checked without a clock is
    structural TIF consistency: a reduce-only (closing/flatten) order using GTC would sit open
    indefinitely rather than resolving promptly, which contradicts the purpose of a reduce-only order
    (exit quickly, don't linger) -- flagged here as the one enforceable "TIF consistent" sub-check.
    """
    if order.constraints.reduce_only and order.time_in_force is TimeInForce.GTC:
        return _Check(False, "TIME_RESTRICTIONS: a reduce_only order should not use GTC (would linger instead of resolving promptly)")
    return _Check(True)


def _check_market_status(order: OrderRequest, caps: BrokerCapabilities) -> _Check:
    status = caps.status_for(order.symbol)
    if status is not MarketStatus.OPEN:
        return _Check(False, f"MARKET_STATUS: {order.symbol} market status is {status.value}, not OPEN")
    return _Check(True)


def _check_supported_capabilities(order: OrderRequest, caps: BrokerCapabilities) -> _Check:
    if order.order_type not in caps.supported_order_types:
        return _Check(False, f"UNSUPPORTED_ORDER_TYPE: {order.order_type.value}")
    if order.time_in_force not in caps.supported_time_in_force:
        return _Check(False, f"UNSUPPORTED_TIME_IN_FORCE: {order.time_in_force.value}")
    return _Check(True)


def validate_order(order: OrderRequest, caps: BrokerCapabilities, portfolio: PortfolioState) -> ValidationResult:
    """Run schema validation (against ``ORDER_SCHEMA.json``) plus the full §8 mechanics suite. Pure;
    never mutates anything; never raises for ordinary (malformed-order) conditions -- an unexpected
    exception here is the caller's job to catch (see :mod:`ai_trader.execution_engine.pipeline`)."""
    reasons: list[str] = list(validate_order_dict(order_to_dict(order)))
    checks = (
        _check_direction(order),
        _check_position_limit_consistency(order, portfolio),
        _check_price_validation(order),
        _check_tick_size(order, caps),
        _check_lot_size(order, caps),
        _check_quantity_bounds(order, caps),
        _check_slippage(order),
        _check_time_restrictions(order),
        _check_market_status(order, caps),
        _check_supported_capabilities(order, caps),
    )
    reasons.extend(c.reason for c in checks if not c.ok and c.reason is not None)
    return ValidationResult(valid=not reasons, reasons=tuple(reasons))
