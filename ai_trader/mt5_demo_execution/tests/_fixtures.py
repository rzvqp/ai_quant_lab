"""Shared fixture builders for `mt5_demo_execution` tests. A local copy of the established per-package
"own local test fixtures" convention (`execution_engine/adapters/tests/_fixtures.py`'s own `FakeMT5Gateway`
docstring), extended with order_check/order_send faking (no scaffold existed for this -- confirmed by
this phase's own investigation)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ai_trader.execution_engine.types import (
    BracketLegs,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000


class FakeMT5DemoGateway:
    """Fakes every `MT5DemoGateway` method: the 13 read-only ones (mirroring `FakeMT5Gateway`'s own
    defaults exactly -- healthy connected DEMO account, `FusionMarkets-Demo`, `XAUUSD`) plus the two new
    `order_check`/`order_send`, both scripted via constructor overrides, both recording every call."""

    def __init__(
        self, *, algo_trading_enabled: bool = True, account_trade_mode: int = 0, is_demo_server: str = "FusionMarkets-Demo",
        tick_time: float = AS_OF, order_check_result: object | None = None, order_send_result: object | None = None,
    ) -> None:
        self.terminal_info_result = SimpleNamespace(connected=True, trade_allowed=algo_trading_enabled, build=5836)
        self.account_info_result = SimpleNamespace(trade_mode=account_trade_mode, trade_allowed=True, server=is_demo_server)
        self._symbols = ("XAUUSD", "EURUSD")
        self._symbol_info = {
            "XAUUSD": SimpleNamespace(
                trade_tick_size=0.01, volume_step=0.01, volume_min=0.01, volume_max=100.0, digits=2,
                spread=7, trade_mode=4, description="Gold vs US Dollar",
            ),
        }
        self._tick = SimpleNamespace(bid=4054.55, ask=4054.62, time=tick_time)
        self._order_check_result = order_check_result if order_check_result is not None else SimpleNamespace(retcode=0, comment="Done", balance=200_000.0, margin=10.0, margin_free=199_990.0)
        self._order_send_result = order_send_result if order_send_result is not None else SimpleNamespace(retcode=10009, comment="Request completed", order=123456, deal=654321, volume=0.01, price=2000.0)
        self.order_check_calls: list[dict[str, object]] = []
        self.order_send_calls: list[dict[str, object]] = []

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def terminal_info(self) -> Any:
        return self.terminal_info_result

    def account_info(self) -> Any:
        return self.account_info_result

    def symbols_get(self) -> Any:
        return tuple(SimpleNamespace(name=s) for s in self._symbols)

    def symbol_info(self, symbol: str) -> Any:
        return self._symbol_info.get(symbol)

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return symbol in self._symbols

    def symbol_info_tick(self, symbol: str) -> Any:
        return self._tick if symbol in self._symbols else None

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        return None

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def positions_get(self, symbol: str | None = None) -> Any:
        return ()

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")

    def order_check(self, request: dict[str, object]) -> Any:
        self.order_check_calls.append(request)
        return self._order_check_result

    def order_send(self, request: dict[str, object]) -> Any:
        self.order_send_calls.append(request)
        return self._order_send_result


def make_order_request(**overrides: object) -> OrderRequest:
    kwargs: dict[str, object] = {
        "order_schema_version": "1.0.0", "execution_engine_version": "1.0.0", "order_request_id": "REQ-1",
        "client_order_id": "CID-1", "decision_id": "DEC-1", "strategy_id": "S1", "symbol": "XAUUSD",
        "timestamp": AS_OF, "as_of": AS_OF, "side": OrderSide.BUY, "direction": Direction.LONG,
        "intent": OrderIntent.OPEN, "order_type": OrderType.MARKET, "time_in_force": TimeInForce.IOC,
        "quantity": 0.01, "limit_price": 2000.0, "bracket": BracketLegs(take_profit=2020.0, stop_loss=1990.0),
        "constraints": OrderConstraints(max_slippage=None, reduce_only=False, post_only=False),
        "refs": OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
    }
    kwargs.update(overrides)
    return OrderRequest(**kwargs)  # type: ignore[arg-type]
