"""`NewBrainLiveDepsFactory` -- builds the REAL, non-fixture `account`/`portfolio`/`instrument`/
`risk_context`/`risk_config` arguments `risk_gate.submit_new_brain_candidate` needs, for LIVE_SHADOW.
Reuses exactly the same real classes `pdh_pdl_demo.live_deps.LivePdhPdlDepsFactory` already established
and proved against a live MT5 terminal (`MT5AccountBridge`, `MT5PortfolioStateSource`,
`LiveRiskSnapshotBuilder`, `LiveMT5TickReader`) -- no new account/portfolio/instrument-reading primitive.

**Deliberately narrower than `LivePdhPdlDepsFactory`**: this factory builds NOTHING order-capable --
no `OrchestratorDependencies`, no `BrokerCapabilities`, no `OrderLedger`, no broker adapter of any kind.
`risk_gate.submit_new_brain_candidate` only needs the five arguments below; `execution_shadow.
attempt_shadow_execution`'s own default `BrokerOrderSubmissionGate()` needs nothing from this factory at
all. There is structurally no path from this module to `order_send` -- it never imports anything that
could call it."""

from __future__ import annotations

from pathlib import Path

from ai_trader.live_signal_source.types import Bar, GapRecord
from ai_trader.mt5_account_bridge.source import MT5AccountBridge
from ai_trader.mt5_pnl_source.gateway import MT5HistoryGateway
from ai_trader.mt5_pnl_source.source import MT5PortfolioStateSource
from ai_trader.pdh_pdl_demo.live_tick_reader import LiveMT5TickReader
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification

_FALLBACK_SPREAD_ON_UNREADABLE_TICK = 1.0
"""Only used if `symbol_info_tick` genuinely returns nothing this cycle (a transient real-feed gap) --
a conservative, disclosed, non-zero placeholder so `RiskContext`'s own filters stay in a fail-safe
direction (a spread of 0.0 would UNDERSTATE cost, the wrong direction to fail toward) rather than crash
the tick. Never presented as a real measured spread; the honest source is `LiveMT5TickReader`."""


class NewBrainLiveDepsFactory:
    def __init__(self, symbol: str, gateway: MT5HistoryGateway, state_dir: Path) -> None:
        self._symbol = symbol
        self._gateway = gateway
        self._account_bridge = MT5AccountBridge(gateway)
        self._portfolio_source = MT5PortfolioStateSource(
            gateway, state_store=SqliteStateStore(state_dir / "new_brain_live_pnl_state.db"),
        )
        self._tick_reader = LiveMT5TickReader(gateway)
        self._risk_snapshot_builder = LiveRiskSnapshotBuilder()

    def update_on_bar(self, bar: Bar, gaps_this_poll: tuple[GapRecord, ...]) -> None:
        """Feeds the risk-snapshot builder's own indicator/volume/gap state -- call once per closed bar,
        before building deps for any candidate that bar produced (mirrors `LivePdhPdlDepsFactory`'s own
        `PortfolioDailyState`-per-cycle discipline)."""
        self._risk_snapshot_builder.update(bar, gaps_this_poll)

    def _current_spread(self) -> float:
        tick = self._tick_reader.read(self._symbol)
        if tick is None:
            return _FALLBACK_SPREAD_ON_UNREADABLE_TICK
        return tick.ask - tick.bid

    def account(self) -> AccountState:
        return self._account_bridge.read_account_state()

    def instrument(self) -> InstrumentSpecification:
        return self._account_bridge.read_instrument_specification(self._symbol)

    def portfolio(self) -> PortfolioState:
        return self._portfolio_source.current_portfolio_state()

    def risk_config(self) -> RiskConfig:
        current_spread = self._current_spread()
        config = RiskConfig()
        config.filters.reference_spread[self._symbol] = max(current_spread * 3, 1.0)
        config.filters.liquidity_floor[self._symbol] = 0.1
        raw_symbol_info = self._gateway.symbol_info(self._symbol)
        tick_value = float(getattr(raw_symbol_info, "trade_tick_value", 0.0))
        tick_size = float(getattr(raw_symbol_info, "trade_tick_size", 0.0))
        contract_size = float(getattr(raw_symbol_info, "trade_contract_size", 0.0))
        config.sizing.point_value[self._symbol] = (
            tick_value / tick_size / contract_size if tick_size > 0 and contract_size > 0 else 1.0
        )
        return config

    def risk_context(self, *, as_of: int) -> RiskContext:
        snapshot = self._risk_snapshot_builder.snapshot(current_spread=self._current_spread())
        return RiskContext(as_of=as_of, per_symbol={self._symbol: snapshot})
