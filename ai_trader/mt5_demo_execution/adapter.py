"""`MT5DemoBrokerAdapter` -- a SUBCLASS of the already-approved, frozen `MT5ReadOnlyBrokerAdapter`
(Phase 1), adding `submit_order`/`capabilities`/`query_status`/`query_open_orders` on top of the
parent's own, unmodified DEMO/server verification performed at connection-establishment time. This
subclass never overrides the parent's own connection-establishment hook -- every existing safety
refusal (non-DEMO, unexpected server, terminal not connected, unreadable account/terminal data) applies
unchanged. `cancel_order` is deliberately NOT implemented this phase (disclosed,
`MT5_DEMO_EXECUTION_PHASE10_DESIGN.md` §2)."""

from __future__ import annotations

from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.mt5_types import AlgoTradingStatus
from ai_trader.execution_engine.types import (
    TERMINAL_STATES,
    BrokerAck,
    BrokerCapabilities,
    BrokerOrderState,
    OrderRequest,
    OrderSide,
    OrderState,
    OrderType,
    TimeInForce,
)
from ai_trader.mt5_demo_execution import reason_codes as rc
from ai_trader.mt5_demo_execution.gateway import MT5DemoGateway, RealMT5DemoGateway
from ai_trader.mt5_demo_execution.request_builder import build_mt5_request
from ai_trader.mt5_demo_execution.types import MT5DemoConfig, MT5OrderCheckResult, MT5OrderSendResult

_MT5_ORDER_TYPE_BY_SIDE = {OrderSide.BUY: 0, OrderSide.SELL: 1}  # ORDER_TYPE_BUY / ORDER_TYPE_SELL
_TRADE_ACTION_DEAL = 1  # mt5.TRADE_ACTION_DEAL -- immediate market execution
_TRADE_RETCODE_DONE = 10009


def _normalize_check(result: object) -> MT5OrderCheckResult:
    if result is None:
        return MT5OrderCheckResult(retcode=-1, comment="order_check returned None")
    return MT5OrderCheckResult(
        retcode=int(getattr(result, "retcode", -1)), comment=str(getattr(result, "comment", "")),
        balance=getattr(result, "balance", None), margin=getattr(result, "margin", None),
        margin_free=getattr(result, "margin_free", None),
    )


def _normalize_send(result: object) -> MT5OrderSendResult:
    if result is None:
        return MT5OrderSendResult(retcode=-1, comment="order_send returned None")
    return MT5OrderSendResult(
        retcode=int(getattr(result, "retcode", -1)), comment=str(getattr(result, "comment", "")),
        order=getattr(result, "order", None), deal=getattr(result, "deal", None),
        volume=getattr(result, "volume", None), price=getattr(result, "price", None),
    )


class MT5DemoBrokerAdapter(MT5ReadOnlyBrokerAdapter):
    def __init__(
        self, *, gateway: MT5DemoGateway | None = None, config: MT5DemoConfig | None = None,
        **kwargs: object,
    ) -> None:
        resolved_gateway = gateway if gateway is not None else RealMT5DemoGateway()
        super().__init__(gateway=resolved_gateway, **kwargs)
        self._demo_gateway: MT5DemoGateway = resolved_gateway
        self._config = config if config is not None else MT5DemoConfig()
        self._orders: dict[str, BrokerOrderState] = {}

    def capabilities(self) -> BrokerCapabilities:
        return BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET}),
            supported_time_in_force=frozenset({TimeInForce.IOC}),
            tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=self._config.max_order_volume,
            market_status={},  # every symbol defaults to MarketStatus.UNKNOWN -- no live feed owned here
        )

    def submit_order(self, order: OrderRequest) -> BrokerAck:
        if not self.is_connected():
            return BrokerAck(accepted=False, reason=rc.NOT_CONNECTED)

        status = self.status()
        if status.algo_trading_status is not AlgoTradingStatus.ENABLED:
            return BrokerAck(accepted=False, reason=rc.TRADING_DISABLED_AT_TERMINAL)
        if status.account_is_demo is not True:
            return BrokerAck(accepted=False, reason=rc.NON_DEMO_ACCOUNT_REFUSED)
        if self._config.expected_server is not None and status.server != self._config.expected_server:
            return BrokerAck(accepted=False, reason=rc.UNEXPECTED_SERVER)
        if order.quantity > self._config.max_order_volume:
            return BrokerAck(accepted=False, reason=rc.VOLUME_EXCEEDS_CONFIGURED_MAXIMUM)

        def _do_submit() -> BrokerAck:
            request = build_mt5_request(
                order, action=_TRADE_ACTION_DEAL, mt5_order_type=_MT5_ORDER_TYPE_BY_SIDE[order.side],
                deviation_points=self._config.deviation_points,
            )
            check_result = _normalize_check(self._demo_gateway.order_check(request))
            if not check_result.ok:
                return BrokerAck(accepted=False, reason=f"{rc.ORDER_CHECK_FAILED}: ({check_result.retcode}) {check_result.comment}")

            send_result = _normalize_send(self._demo_gateway.order_send(request))
            if not send_result.ok:
                return BrokerAck(accepted=False, reason=f"{rc.ORDER_SEND_FAILED}: ({send_result.retcode}) {send_result.comment}")

            self._orders[order.client_order_id] = BrokerOrderState(
                client_order_id=order.client_order_id, state=OrderState.ACKNOWLEDGED,
                filled_qty=send_result.volume or 0.0, avg_price=send_result.price,
            )
            return BrokerAck(accepted=True, broker_order_id=str(send_result.order) if send_result.order else None)

        return self._submit_with_idempotency(order, _do_submit)

    def query_status(self, client_order_id: str) -> BrokerOrderState | None:
        return self._orders.get(client_order_id)

    def query_open_orders(self) -> tuple[BrokerOrderState, ...]:
        return tuple(s for s in self._orders.values() if s.state not in TERMINAL_STATES)
