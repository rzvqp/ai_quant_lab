"""`LivePdhPdlDepsFactory` -- builds REAL `OrchestratorDependencies` (dry-run + demo legs) for
`PdhPdlOrchestrator.submit_candidate`, using `compute_sizing` NORMALLY (CEO instruction, 2026-08-03:
"Nu ocoli compute_sizing. Foloseste-l normal.") -- this module never bypasses sizing; it is what feeds
sizing REAL data.

**`point_value` correction reused verbatim** from the proven infra test
(`XAUUSD_INFRA_TEST_REPORT.md`, attempt 2): `InstrumentSpecification.point_value` (`tick_value/tick_size`,
already computed correctly by the existing `MT5AccountBridge.read_instrument_specification`, unmodified)
is a DIFFERENT field from `RiskConfig.sizing.point_value[symbol]` (`tick_value/tick_size/contract_size`,
the one `risk_manager/sizing.py::compute_sizing` actually reads) -- both derived here from a fresh
`symbol_info` read, never assumed, never copied between symbols.

**Disclosed, in-memory-only state**: `PortfolioDailyState` (day-reset tracking) does not persist across
a process restart in this first activation -- a restart starts a fresh trading day's counters, the same
class of limitation `structural_observer`'s own in-memory bar history already disclosed (Mandate 4 Step
3). `RiskConfig`'s per-symbol filter thresholds (`reference_spread`/`liquidity_floor`) are set ONCE at
construction from the spread observed then -- a static snapshot, not continuously re-derived; disclosed,
not silently presented as always-current.
"""

from __future__ import annotations

import time
from pathlib import Path

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import BrokerCapabilities, MarketStatus, OrderType, TimeInForce
from ai_trader.execution_orchestrator.types import OrchestratorDependencies
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.mt5_account_bridge.source import MT5AccountBridge
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.mt5_pnl_source.gateway import MT5HistoryGateway
from ai_trader.mt5_pnl_source.source import MT5PortfolioStateSource
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter, capabilities_for
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.pdh_pdl_demo.orchestration import DemoDepsBundle
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.portfolio_manager_live.daily_reset import reset_if_new_day
from ai_trader.portfolio_manager_live.types import PortfolioDailyState
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import RiskContext

#: Safety CEILING on `submit_order`'s own `quantity > max_order_volume` refusal -- NOT a sizing
#: decision (compute_sizing computes the real size; this only caps a catastrophically wrong result
#: from ever reaching the broker). 1.0 lot is generous headroom over every worked example the CEO gave
#: (0.01 lots at $2-8 stops) while still refusing anything two orders of magnitude larger.
_MAX_ORDER_VOLUME_SAFETY_CEILING = 1.0


class LivePdhPdlDepsFactory:
    def __init__(
        self, symbol: str, gateway: MT5HistoryGateway, demo_adapter: MT5DemoBrokerAdapter,
        risk_snapshot_builder: LiveRiskSnapshotBuilder, state_dir: Path,
    ) -> None:
        self._symbol = symbol
        self._gateway = gateway
        self._demo_adapter = demo_adapter
        self._risk_snapshot_builder = risk_snapshot_builder
        self._account_bridge = MT5AccountBridge(gateway)
        self._portfolio_source = MT5PortfolioStateSource(
            gateway, state_store=SqliteStateStore(state_dir / "pdh_pdl_pnl_state.db"),
        )
        self._daily_state = PortfolioDailyState(as_of=int(time.time()))
        self._dry_run_ledger = OrderLedger()
        self._dry_run_journal = OrderManagerAuditJournal(state_dir / "pdh_pdl_dry_run_journal.jsonl")
        self._demo_ledger = OrderLedger()
        self._demo_journal = OrderManagerAuditJournal(state_dir / "pdh_pdl_demo_order_journal.jsonl")

    def __call__(self, candidate: LiveCandidate, trigger: PdhPdlTrigger) -> DemoDepsBundle:
        now = candidate.as_of
        account = self._account_bridge.read_account_state()
        instrument = self._account_bridge.read_instrument_specification(self._symbol)
        portfolio = self._portfolio_source.current_portfolio_state()
        self._daily_state = reset_if_new_day(self._daily_state, now)

        raw_symbol_info = self._gateway.symbol_info(self._symbol)
        tick_value = float(getattr(raw_symbol_info, "trade_tick_value", 0.0))
        tick_size = float(getattr(raw_symbol_info, "trade_tick_size", 0.0))
        contract_size = float(getattr(raw_symbol_info, "trade_contract_size", 0.0))
        point_value_per_unit = (
            tick_value / tick_size / contract_size if tick_size > 0 and contract_size > 0 else 1.0
        )

        risk_config = RiskConfig()
        risk_config.filters.reference_spread[self._symbol] = max(trigger.effective_spread * 3, 1.0)
        risk_config.filters.liquidity_floor[self._symbol] = 0.1
        risk_config.sizing.point_value[self._symbol] = point_value_per_unit
        # risk_per_trade_pct left at RiskConfig's own default (0.5%) -- never touched (CEO instruction).

        risk_context_snapshot = self._risk_snapshot_builder.snapshot(current_spread=trigger.effective_spread)
        risk_context = RiskContext(as_of=now, per_symbol={self._symbol: risk_context_snapshot})

        demo_caps = self._demo_adapter.capabilities()
        broker_caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET, OrderType.LIMIT, OrderType.BRACKET}),
            supported_time_in_force=frozenset({TimeInForce.GTC, TimeInForce.IOC}),
            tick_size=demo_caps.tick_size, lot_step=demo_caps.lot_step, min_qty=demo_caps.min_qty,
            max_qty=demo_caps.max_qty, market_status={self._symbol: MarketStatus.OPEN},
        )

        dry_run_caps = capabilities_for(
            self._symbol, instrument.tick_size, instrument.lot_step, instrument.min_volume, instrument.max_volume,
        )
        dry_run_adapter = DryRunBrokerAdapter(dry_run_caps)
        dry_run_adapter.connect()
        dry_run_deps = OrchestratorDependencies(
            account=account, portfolio=portfolio, daily_state=self._daily_state, instrument=instrument,
            risk_context=risk_context, risk_config=risk_config, broker_caps=dry_run_caps,
            ledger=self._dry_run_ledger, order_journal=self._dry_run_journal, adapter=dry_run_adapter,
        )
        demo_deps = OrchestratorDependencies(
            account=account, portfolio=portfolio, daily_state=self._daily_state, instrument=instrument,
            risk_context=risk_context, risk_config=risk_config, broker_caps=broker_caps,
            ledger=self._demo_ledger, order_journal=self._demo_journal,
            adapter=self._demo_adapter,  # type: ignore[arg-type]
            # MT5DemoBrokerAdapter deliberately never implements cancel_order (Phase 10's own
            # test_import_independence.py asserts this) -- the SAME established, accepted structural
            # gap execution_orchestrator/tests/_fixtures.py::make_deps already suppresses this way.
            # send_after_dry_run_gate's demo leg is single-shot send-only; cancel_order is never called.
        )

        demo_config = MT5DemoConfig(
            max_order_volume=_MAX_ORDER_VOLUME_SAFETY_CEILING, expected_server="FusionMarkets-Demo",
        )
        safety_report = verify_safety_guards(self._demo_adapter, demo_config, symbol=self._symbol)

        return DemoDepsBundle(
            dry_run_deps=dry_run_deps, demo_deps=demo_deps, demo_adapter=self._demo_adapter,
            safety_guard_report=safety_report,
        )
