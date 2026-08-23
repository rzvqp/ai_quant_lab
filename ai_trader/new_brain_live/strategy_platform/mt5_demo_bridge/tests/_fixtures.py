"""Shared fixture builders for `mt5_demo_bridge` tests. `FakeMT5BridgeGateway` mirrors `mt5_demo_execution.
tests._fixtures.FakeMT5DemoGateway`'s own defaults (healthy connected DEMO account, `FusionMarkets-Demo`,
`XAUUSD`) -- extended with `order_calc_profit`/`history_deals_get` (the two new primitives this bridge
adds) and scriptable `positions_get`/`orders_get`/`history_deals_get` for reconciliation tests. No real
MT5 terminal or `MetaTrader5` package is required to run any test in this suite."""

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any

from ai_trader.execution_engine.adapters.connection import BrokerCredentials
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.ev_engine import NO_TRADE, TRADE_DECISION, EVDecision
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import MT5ExecutionLedger
from ai_trader.new_brain_live.strategy_platform.s5_ev_evidence import S5_REAL_EV_EVIDENCE_V1
from ai_trader.new_brain_live.strategy_platform.s5_opening_range_breakout import (
    CONFIG_FINGERPRINT,
    STRATEGY_ID,
    STRATEGY_VERSION,
    S5OpeningRangeBreakoutLong,
    catalog_entry_for_s5,
)
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000
SYMBOL = "XAUUSD"


class FakeMT5BridgeGateway:
    def __init__(
        self, *, algo_trading_enabled: bool = True, account_trade_mode: int = 0,
        is_demo_server: str = "FusionMarkets-Demo", tick_time: float | None = None,
        order_check_result: object | None = None, order_send_result: object | None = None,
        order_calc_profit_result: float | None = -50.0, equity: float = 10_000.0,
    ) -> None:
        now = tick_time if tick_time is not None else time.time()
        self.terminal_info_result: Any = SimpleNamespace(connected=True, trade_allowed=algo_trading_enabled, build=6090)
        self.account_info_result: Any = SimpleNamespace(trade_mode=account_trade_mode, trade_allowed=True, server=is_demo_server, equity=equity, login=10000001, currency="USD")
        self._symbols = ("XAUUSD", "EURUSD")
        self._symbol_info = {
            "XAUUSD": SimpleNamespace(
                trade_tick_size=0.01, volume_step=0.01, volume_min=0.01, volume_max=100.0, digits=2,
                spread=7, trade_mode=4, description="Gold vs US Dollar",
            ),
        }
        self._tick: Any = SimpleNamespace(bid=4054.55, ask=4054.62, time=now)
        self._order_check_result = order_check_result if order_check_result is not None else SimpleNamespace(retcode=0, comment="Done", balance=200_000.0, margin=10.0, margin_free=199_990.0)
        self._order_send_result = order_send_result if order_send_result is not None else SimpleNamespace(retcode=10009, comment="Request completed", order=123456, deal=654321, volume=0.01, price=2000.0)
        self._order_calc_profit_result = order_calc_profit_result
        self.order_check_calls: list[dict[str, object]] = []
        self.order_send_calls: list[dict[str, object]] = []
        self.order_calc_profit_calls: list[tuple[object, ...]] = []
        self._positions: tuple[Any, ...] = ()
        self._orders: tuple[Any, ...] = ()
        self._deals: tuple[Any, ...] = ()
        self._rates: Any = None
        self.copy_rates_from_calls: list[tuple[object, ...]] = []

    # -- read-only surface --
    def initialize(self, path: str | None = None, login: int | None = None, password: str | None = None, server: str | None = None) -> bool:
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
        self.copy_rates_from_calls.append((symbol, timeframe, date_from, count))
        return self._rates

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def positions_get(self, symbol: str | None = None) -> Any:
        return self._positions

    def orders_get(self, symbol: str | None = None) -> Any:
        return self._orders

    def history_deals_get(self, date_from: int, date_to: int) -> Any:
        return self._deals

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")

    # -- order surface --
    def order_check(self, request: dict[str, object]) -> Any:
        self.order_check_calls.append(request)
        return self._order_check_result

    def order_send(self, request: dict[str, object]) -> Any:
        self.order_send_calls.append(request)
        return self._order_send_result

    def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float | None:
        self.order_calc_profit_calls.append((action, symbol, volume, price_open, price_close))
        return self._order_calc_profit_result if self._order_calc_profit_result is None else self._order_calc_profit_result * volume


def make_connected_demo_adapter(gateway: FakeMT5BridgeGateway, *, config: MT5DemoConfig | None = None) -> MT5DemoBrokerAdapter:
    adapter = MT5DemoBrokerAdapter(gateway=gateway, config=config or MT5DemoConfig(max_order_volume=1.0), credentials=BrokerCredentials())
    result = adapter.connect()
    assert result.accepted, result.reason
    return adapter


def make_ledger(tmp_path: Any, name: str = "mt5_bridge_ledger.db") -> tuple[MT5ExecutionLedger, SqliteStateStore]:
    store = SqliteStateStore(tmp_path / name)
    return MT5ExecutionLedger(store), store


def real_s5_catalog_entry() -> tuple[S5OpeningRangeBreakoutLong, CatalogEntry]:
    strategy = S5OpeningRangeBreakoutLong()
    return strategy, catalog_entry_for_s5(strategy)


def make_s5_hypothesis(*, market_state_identity: str = "ms-1", signal_timestamp: int = AS_OF, entry: float = 2052.0, sl: float = 2039.98) -> TradeHypothesis:
    return TradeHypothesis(
        strategy_id=STRATEGY_ID, strategy_version=STRATEGY_VERSION, instrument=SYMBOL, direction=Direction.LONG,
        signal_timestamp=signal_timestamp, eligible_entry_timestamp=signal_timestamp, entry_type="MARKET",
        intended_entry=entry, invalidation=sl, exit_specification="rr:3.0", max_hold=48,
        expected_edge=S5_REAL_EV_EVIDENCE_V1.to_expected_edge(), reason_codes=("S5_OPENING_RANGE_BREAKOUT",),
        market_state_identity=market_state_identity, strategy_config_fingerprint=CONFIG_FINGERPRINT,
        research_validation_identity="test-only", provenance="test-fixture",
    )


def make_trade_decision(hypothesis: TradeHypothesis) -> EVDecision:
    return EVDecision(hypothesis=hypothesis, decision=TRADE_DECISION, reason_codes=("REAL_EV_VALIDATED_EDGE",), evidence_fingerprint=S5_REAL_EV_EVIDENCE_V1.evidence_fingerprint)


def make_no_trade_decision(hypothesis: TradeHypothesis) -> EVDecision:
    return EVDecision(hypothesis=hypothesis, decision=NO_TRADE, reason_codes=("EV_BELOW_THRESHOLD",))
