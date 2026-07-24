"""Order Manager's own, narrow `OrderRequest` builder -- mirrors the established
`execution_engine.builder.build_flatten_order` precedent (a separate builder for a non-`RiskDecision`
source is already this codebase's own convention, not a new pattern here). Performs PRICE normalization
only (round entry/stop/target to `instrument.tick_size`) -- volume/lot normalization already happened in
`risk_manager_live.engine` (Phase 2); `ApprovedTradeIntent.volume` arrives pre-rounded."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ai_trader.execution_engine.config import BROKER_ADAPTER_CONTRACT_VERSION, EXECUTION_ENGINE_VERSION, ORDER_SCHEMA_VERSION
from ai_trader.execution_engine.types import (
    BracketLegs,
    BrokerCapabilitiesRef,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.order_manager import reason_codes as rc
from ai_trader.order_manager.types import ApprovedTradeIntent, OrderManagerConfig
from ai_trader.risk_manager_live.types import InstrumentSpecification
from ai_trader.signal_engine.types import Direction

_SIDE_FOR_DIRECTION = {Direction.LONG: OrderSide.BUY, Direction.SHORT: OrderSide.SELL}


@dataclass(frozen=True, slots=True)
class BuildOutcome:
    success: bool
    order: OrderRequest | None = None
    reason: str | None = None


def _round_to_tick(value: float, tick_size: float) -> float:
    """Round-half-up to the nearest multiple of `tick_size` -- same rounding DIRECTION as
    `execution_engine.builder`'s own `RoundingPolicy` (round-half-up), reimplemented here (not
    imported) because the source is a private, underscore-prefixed function in a sibling package;
    the arithmetic itself is a trivial, standard rounding rule, not a duplicated design decision."""
    if tick_size <= 0:
        return value
    return math.floor(value / tick_size + 0.5) * tick_size


def build_order_request(
    intent: ApprovedTradeIntent, instrument: InstrumentSpecification, config: OrderManagerConfig | None = None,
) -> BuildOutcome:
    """Deterministically construct (never submit) an `OrderRequest` from an `ApprovedTradeIntent`.
    Always builds a BRACKET order: `TradeProposal.stop` (the source of `intent.stop`) is a required,
    always-present field in `risk_manager_live`, so there is always at least a stop leg -- never a bare
    MARKET order. `intent.entry` is always used as `limit_price` -- never marketable, so no
    `max_slippage` is required (mirrors the entry-always-present branch of
    `execution_engine.builder.build_order`)."""
    resolved_config = config if config is not None else OrderManagerConfig()

    if instrument.symbol != intent.symbol:
        return BuildOutcome(False, reason=rc.INSTRUMENT_SYMBOL_MISMATCH)
    if intent.direction not in _SIDE_FOR_DIRECTION:
        return BuildOutcome(False, reason=f"{rc.INVALID_DIRECTION}: intent carries no concrete direction")

    entry = _round_to_tick(intent.entry, instrument.tick_size)
    stop = _round_to_tick(intent.stop, instrument.tick_size)
    target = _round_to_tick(intent.target, instrument.tick_size) if intent.target is not None else None
    for label, price in (("entry", entry), ("stop", stop), ("target", target)):
        if price is not None and not math.isfinite(price):
            return BuildOutcome(False, reason=f"{rc.PRICE_NORMALIZATION_FAILED}: {label} is not finite")

    decision_id = f"LIVE-{intent.proposal_id}"
    order = OrderRequest(
        order_schema_version=ORDER_SCHEMA_VERSION,
        execution_engine_version=EXECUTION_ENGINE_VERSION,
        order_request_id=f"{resolved_config.order_request_id_prefix}-{decision_id}",
        client_order_id=f"{resolved_config.client_order_id_prefix}-{decision_id}",
        decision_id=decision_id,
        strategy_id=intent.strategy_id,
        symbol=intent.symbol,
        timestamp=intent.as_of,
        as_of=intent.as_of,
        side=_SIDE_FOR_DIRECTION[intent.direction],
        direction=intent.direction,
        intent=OrderIntent.OPEN,
        order_type=OrderType.BRACKET,
        time_in_force=TimeInForce.GTC,
        quantity=intent.volume,
        limit_price=entry,
        stop_price=None,
        bracket=BracketLegs(take_profit=target, stop_loss=stop),
        oco_link=None,
        constraints=OrderConstraints(max_slippage=None, reduce_only=False, post_only=False),
        broker_capabilities_ref=BrokerCapabilitiesRef(
            tick_size=instrument.tick_size, lot_step=instrument.lot_step, min_qty=instrument.min_volume,
            max_qty=instrument.max_volume, contract_version=BROKER_ADAPTER_CONTRACT_VERSION,
        ),
        refs=OrderRefs(
            risk_schema_version=resolved_config.risk_lineage_ref,
            risk_policy_version=resolved_config.risk_lineage_ref,
        ),
    )
    return BuildOutcome(True, order=order)
