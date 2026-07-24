"""`DryRunBrokerAdapter` -- Order Manager's own live-context, zero-network `BrokerAdapter`. Mirrors
`execution_engine.adapters.null_adapter.NullBrokerAdapter`'s pattern (subclasses `RealBrokerAdapterBase`
for REUSED, unmodified connection-lifecycle/idempotency/retry machinery; ACKNOWLEDGE-only, never FILLS)
but is Order-Manager-owned and journal-integrated. Structurally incapable of reaching MT5: this module
imports nothing from `ai_trader.execution_engine.adapters.mt5_gateway`/`mt5_adapter`/`mt5_types`, and
never will (Phase 10's real MT5 wiring is a SEPARATE adapter this phase never touches) -- enforced by
`tests/test_import_independence.py`.
"""

from __future__ import annotations

from ai_trader.execution_engine.adapters.base import RealBrokerAdapterBase
from ai_trader.execution_engine.adapters.connection import ConnectionResult
from ai_trader.execution_engine.types import (
    TERMINAL_STATES,
    BrokerAck,
    BrokerCapabilities,
    BrokerOrderState,
    MarketStatus,
    OrderRequest,
    OrderState,
    OrderType,
    TimeInForce,
)


class DryRunBrokerAdapter(RealBrokerAdapterBase):
    """Every `submit_order` reaches `ACKNOWLEDGED` and stops there -- there is no market to fill
    against and no real venue to submit to. `capabilities()` is built from the same
    `InstrumentSpecification` Order Manager already validated the order against, so
    `validator.validate_order`'s tick/lot/quantity checks are validated against a CONSISTENT profile,
    not an arbitrary one."""

    def __init__(self, capabilities: BrokerCapabilities, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._capabilities = capabilities
        self._orders: dict[str, BrokerOrderState] = {}

    # ------------------------------------------------------------------ RealBrokerAdapterBase hooks

    def _do_connect(self) -> ConnectionResult:
        return ConnectionResult(accepted=True)  # nothing real to connect to; always succeeds

    def _do_disconnect(self) -> None:
        self._orders.clear()

    def _do_heartbeat_check(self) -> bool:
        return True

    # ------------------------------------------------------------------ BrokerAdapter (unmodified Protocol)

    def capabilities(self) -> BrokerCapabilities:
        return self._capabilities

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        if not self.is_connected():
            return BrokerAck(accepted=False, reason="NOT_CONNECTED")

        def _do_submit() -> BrokerAck:
            self._orders[order.client_order_id] = BrokerOrderState(
                client_order_id=order.client_order_id, state=OrderState.ACKNOWLEDGED,
            )
            return BrokerAck(accepted=True, broker_order_id=f"DRYRUN-{order.client_order_id}")

        return self._submit_with_idempotency(order, _do_submit)

    def cancel_order(self, client_order_id: str) -> BrokerAck:
        if not self.is_connected():
            return BrokerAck(accepted=False, reason="NOT_CONNECTED")
        existing = self._orders.get(client_order_id)
        if existing is None:
            return BrokerAck(accepted=False, reason="UNKNOWN_ORDER")
        self._orders[client_order_id] = BrokerOrderState(
            client_order_id=client_order_id, state=OrderState.CANCELLED,
        )
        return BrokerAck(accepted=True)

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        return self._orders.get(client_order_id)

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        return tuple(s for s in self._orders.values() if s.state not in TERMINAL_STATES)


def capabilities_for(
    symbol: str, tick_size: float, lot_step: float, min_volume: float, max_volume: float,
) -> BrokerCapabilities:
    """Builds a `BrokerCapabilities` profile consistent with an `InstrumentSpecification`. Explicitly
    marks `symbol` as `MarketStatus.OPEN` -- a symbol absent from `market_status` defaults to `UNKNOWN`
    (fail-safe in `execution_engine.types`), which `validator._check_market_status` would then reject;
    Order Manager's dry run always evaluates as if the ONE symbol it was given were tradable (a real
    market-status feed is out of scope this phase -- no live quote feed input exists anywhere in
    `execution_engine` v1 either, per its own documented IMPLEMENTATION CHOICE)."""
    return BrokerCapabilities(
        supported_order_types=frozenset({OrderType.MARKET, OrderType.LIMIT, OrderType.BRACKET}),
        supported_time_in_force=frozenset({TimeInForce.GTC, TimeInForce.IOC, TimeInForce.DAY, TimeInForce.FOK}),
        tick_size=tick_size, lot_step=lot_step, min_qty=min_volume, max_qty=max_volume,
        market_status={symbol: MarketStatus.OPEN},
    )
