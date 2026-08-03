"""XAUUSD Infrastructure Test -- CEO-authorized 2026-08-03. "Exact ca testul BTCUSD din commit a3ef1c7,
dar pe XAUUSD."

NOT a strategy test, NOT PDH-PDL. NOT going through PdhPdlRecognitionRule (explicit instruction: "NU
treci prin regula de recunoastere"). Validates EXCLUSIVELY the execution infrastructure path: AI Trader
-> Execution Orchestrator -> Order Manager -> Broker Adapter -> MT5 order_check -> MT5 order_send ->
confirmation -> controlled close -> report. Mirrors `btcusd_phase10_operational_test.py` line for line
in structure; the only substantive differences are the symbol and the additional realized-cost/spread
reporting the CEO specifically requested this time.

ONE order only. Aborts fail-closed on any check failure -- no order sent on abort. Lives at repo root
(mirroring `mt5_connectivity_probe.py`/`btcusd_phase10_operational_test.py`'s own precedent), not inside
any `ai_trader` package, not part of the standing automated test suite.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ai_trader.confidence_engine.types import ConfidenceEngineConfig
from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import BrokerCapabilities, MarketStatus, OrderType, TimeInForce
from ai_trader.execution_orchestrator.types import CandidateSignal, ExecutionMode, OrchestratorConfig, OrchestratorDependencies
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.gating import send_after_dry_run_gate
from ai_trader.mt5_demo_execution.safety import is_market_open_for_symbol, verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.portfolio_manager_live.types import PortfolioDailyState
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
MODELED_ROUND_TRIP_COST = 0.20  # $ -- the constant assumed throughout the project's own backtests
JOURNAL_PATH = Path(__file__).parent / "xauusd_infra_test_journal.jsonl"

journal: list[dict[str, object]] = []


def log(stage: str, **detail: object) -> None:
    entry = {"stage": stage, "wall_clock": time.time(), **detail}
    journal.append(entry)
    print(f"[{stage}] {json.dumps(detail, default=str)}")


def abort(reason: str) -> None:
    log("ABORT_FAIL_CLOSED", reason=reason)
    _flush_journal()
    raise SystemExit(1)


def _flush_journal() -> None:
    with JOURNAL_PATH.open("w", encoding="utf-8") as f:
        for entry in journal:
            f.write(json.dumps(entry, default=str) + "\n")


def main() -> None:
    now = int(time.time())
    config = MT5DemoConfig()  # corrected below once the real minimum volume is known
    adapter = MT5DemoBrokerAdapter(config=config)

    try:
        # ---- Check 1: terminal connected ----
        connection = adapter.connect()
        log("CHECK_1_CONNECTED", accepted=connection.accepted, reason=connection.reason)
        if not connection.accepted:
            abort(f"connect() refused: {connection.reason}")

        status = adapter.status()

        # ---- Check 2: account is DEMO ----
        log("CHECK_2_ACCOUNT_IS_DEMO", account_is_demo=status.account_is_demo, trade_mode=str(status.account_trade_mode), server=status.server)
        if status.account_is_demo is not True:
            abort("account is not DEMO -- refusing (structural: no LIVE/CONTEST account will ever be used)")
        if status.server != "FusionMarkets-Demo":
            abort(f"unexpected server {status.server!r} -- expected FusionMarkets-Demo, refusing")

        # ---- Check 3: AlgoTrading enabled ----
        log("CHECK_3_ALGO_TRADING_ENABLED", algo_trading_status=status.algo_trading_status.value)
        if status.algo_trading_status.value != "ENABLED":
            abort(f"AlgoTrading not enabled at terminal: {status.algo_trading_status.value} -- never auto-activated")

        # ---- Check 4: terminal_info().trade_allowed ----
        log("CHECK_4_TERMINAL_TRADE_ALLOWED", terminal_algo_trading_allowed=status.terminal_algo_trading_allowed)
        if status.terminal_algo_trading_allowed is not True:
            abort("terminal_info().trade_allowed is not True")

        # ---- Check 5: account_info().trade_allowed ----
        log("CHECK_5_ACCOUNT_TRADE_ALLOWED", account_trade_allowed=status.account_trade_allowed)
        if status.account_trade_allowed is not True:
            abort("account_info().trade_allowed is not True")

        # ---- Check 6+7: symbol exists, selected/visible, properties readable ----
        caps = adapter.symbol_capabilities(SYMBOL)
        log("CHECK_6_7_SYMBOL_CAPABILITIES", symbol=SYMBOL, caps=None if caps is None else {
            "tick_size": caps.tick_size, "lot_step": caps.lot_step, "min_qty": caps.min_qty,
            "max_qty": caps.max_qty, "digits": caps.digits, "spread": caps.spread, "trade_mode": caps.trade_mode,
        })
        if caps is None:
            abort(f"{SYMBOL} not available / not selectable on this terminal")

        # ---- Check 8: tick is current (market open) ----
        entry_tick = adapter.read_tick(SYMBOL)
        log("CHECK_8_TICK", tick_present=entry_tick is not None, bid=getattr(entry_tick, "bid", None), ask=getattr(entry_tick, "ask", None), tick_time=getattr(entry_tick, "time", None))
        if entry_tick is None:
            abort("no tick data available for XAUUSD")

        market_open = is_market_open_for_symbol(adapter, SYMBOL, config)
        log("CHECK_8B_MARKET_OPEN", market_open=market_open)
        if not market_open:
            log("PENDING_MARKET_OPEN", reason="market closed or undeterminable -- stopping before any transmission, per explicit instruction never to bypass this")
            _flush_journal()
            return

        # ---- Check 9+10: properties + spread available (THE COMPARISON THAT MATTERS) ----
        entry_spread_price = float(entry_tick.ask) - float(entry_tick.bid)
        log("CHECK_9_10_SPREAD_AT_ENTRY", bid=entry_tick.bid, ask=entry_tick.ask, spread_price=entry_spread_price,
            broker_reported_spread_points=caps.spread, modeled_round_trip_cost=MODELED_ROUND_TRIP_COST,
            spread_vs_modeled_ratio=entry_spread_price / MODELED_ROUND_TRIP_COST)
        if entry_spread_price <= 0:
            abort("spread is not a positive, sane value")

        # ---- Check 11: minimum allowed volume ----
        min_volume = caps.min_qty
        log("CHECK_11_MIN_VOLUME", min_volume=min_volume)
        if min_volume is None or min_volume <= 0:
            abort("could not determine a valid minimum volume")

        config = MT5DemoConfig(max_order_volume=min_volume, expected_server=status.server)
        adapter._config = config  # script-level re-configuration of the already-connected instance;
        # not a file/component modification -- MT5DemoConfig is a plain constructor parameter, supplied
        # here only once the real minimum volume is known from the terminal itself.

        # Read real account numbers directly from the already-approved, frozen read-only gateway --
        # never fabricated.
        raw_account = adapter._demo_gateway.account_info()
        raw_symbol_info = adapter._demo_gateway.symbol_info(SYMBOL)
        contract_size = float(getattr(raw_symbol_info, "trade_contract_size", 1.0))
        log("ACCOUNT_SNAPSHOT", balance=raw_account.balance, equity=raw_account.equity, currency=raw_account.currency,
            leverage=raw_account.leverage, margin_free=raw_account.margin_free, contract_size=contract_size)

        # Verify no pre-existing XAUUSD position before we start.
        pre_positions = adapter._demo_gateway.positions_get(SYMBOL) or ()
        log("PRE_EXISTING_POSITIONS_CHECK", count=len(pre_positions))
        if len(pre_positions) > 0:
            abort(f"{len(pre_positions)} pre-existing XAUUSD position(s) found before the test even started -- refusing to add ambiguity")

        # ---- Build the full AI Trader dependency set, using REAL queried values wherever available ----
        entry_requested_price = float(entry_tick.ask)  # BUY fills at ask
        candidate = CandidateSignal(
            strategy_id="S998", symbol=SYMBOL, direction=Direction.LONG,  # ORDER_SCHEMA.json requires ^S\d+$; S998, distinct from BTCUSD's own S999 infra-test id and PDH-PDL's S9001, never a real registered strategy
            entry=entry_requested_price, stop=entry_requested_price * 0.98, target=entry_requested_price * 1.02,
            session="INFRA_TEST", magic_number=900011, comment="XAUUSD-INFRA-TEST", as_of=now,
        )
        market_context = {
            "meta": {"as_of": now, "symbol": SYMBOL},
            "timeframes": {"M15": {"bars": [], "features": {}, "feature_history": []}},
            "data_quality": {"level": "OK"},
        }
        account = AccountState(
            as_of=now, currency=str(raw_account.currency), balance=float(raw_account.balance),
            equity=float(raw_account.equity), margin_used=float(raw_account.balance) - float(raw_account.margin_free),
            margin_free=float(raw_account.margin_free), margin_level=None, leverage=float(raw_account.leverage),
            is_demo=True,
        )
        portfolio = PortfolioState(as_of=now, equity=float(raw_account.equity), equity_high_water_mark=float(raw_account.equity))
        daily_state = PortfolioDailyState(as_of=now)
        instrument = InstrumentSpecification(
            symbol=SYMBOL, tick_size=caps.tick_size, lot_step=caps.lot_step, min_volume=caps.min_qty,
            max_volume=caps.max_qty, contract_size=contract_size, point_value=1.0,
            margin_currency=str(raw_account.currency),
        )
        risk_config = RiskConfig()
        risk_config.filters.reference_spread[SYMBOL] = max(entry_spread_price * 3, 1.0)
        risk_config.filters.liquidity_floor[SYMBOL] = 0.1
        risk_config.sizing.point_value[SYMBOL] = 1.0
        risk_context = RiskContext(as_of=now, per_symbol={SYMBOL: SymbolRiskSnapshot(
            atr=entry_spread_price * 20, atr_rolling_median=entry_spread_price * 20, current_spread=entry_spread_price,
            liquidity_proxy=1.0, is_weekend_gap=False, bars_since_gap=100, is_past_friday_cutoff=False,
            is_near_session_close=False, minutes_to_high_impact_event=999.0, data_quality=DataQualityLevel.OK,
        )})
        broker_caps = BrokerCapabilities(
            supported_order_types=frozenset({OrderType.MARKET, OrderType.LIMIT, OrderType.BRACKET}),
            supported_time_in_force=frozenset({TimeInForce.GTC, TimeInForce.IOC}),
            tick_size=caps.tick_size, lot_step=caps.lot_step, min_qty=caps.min_qty, max_qty=min_volume,
            market_status={SYMBOL: MarketStatus.OPEN},
        )

        dry_run_ledger = OrderLedger()
        dry_run_journal = OrderManagerAuditJournal(Path(__file__).parent / "xauusd_infra_test_dry_run_journal.jsonl")
        dry_run_adapter = DryRunBrokerAdapter(broker_caps)
        dry_run_adapter.connect()
        dry_run_deps = OrchestratorDependencies(
            account=account, portfolio=portfolio, daily_state=daily_state, instrument=instrument,
            risk_context=risk_context, risk_config=risk_config, broker_caps=broker_caps, ledger=dry_run_ledger,
            order_journal=dry_run_journal, adapter=dry_run_adapter,
        )
        demo_ledger = OrderLedger()
        demo_journal = OrderManagerAuditJournal(Path(__file__).parent / "xauusd_infra_test_demo_order_journal.jsonl")
        demo_deps = OrchestratorDependencies(
            account=account, portfolio=portfolio, daily_state=daily_state, instrument=instrument,
            risk_context=risk_context, risk_config=risk_config, broker_caps=broker_caps, ledger=demo_ledger,
            order_journal=demo_journal, adapter=adapter,
        )

        orchestrator_config = OrchestratorConfig(
            recognition_pattern_id=None,  # infra test -- recognition is out of scope, optional input
            confidence_config=ConfidenceEngineConfig(require_data_quality_ok=True, require_not_stale=True),
        )

        # ---- Check 12: run the full safety-guard report + require the identical dry-run to pass first ----
        safety_report = verify_safety_guards(adapter, config, symbol=SYMBOL)
        log("SAFETY_GUARD_REPORT", connected=safety_report.connected, account_is_demo=safety_report.account_is_demo,
            algo_trading_enabled=safety_report.algo_trading_enabled, server_matches_expected=safety_report.server_matches_expected,
            max_volume_configured=safety_report.max_volume_configured, market_open=safety_report.market_open,
            all_passed=safety_report.all_passed)
        if not safety_report.all_passed:
            abort("final automated safety-guard verification did not all pass")

        log("SENDING_THROUGH_FULL_AI_TRADER_PIPELINE", note="Execution Orchestrator -> Order Manager -> Broker Adapter -> MT5 order_check -> MT5 order_send")
        outcome = send_after_dry_run_gate(
            candidate, market_context, dry_run_deps, demo_deps, adapter, safety_report,
            config=orchestrator_config,
        )

        log("CHECK_12_DRY_RUN_RESULT", approved=outcome.dry_run_result.approved,
            order_state=None if outcome.dry_run_result.order_result is None else outcome.dry_run_result.order_result.state.value,
            reason_codes=outcome.dry_run_result.reason_codes)
        if not (outcome.dry_run_result.approved and outcome.dry_run_result.order_result is not None and outcome.dry_run_result.order_result.state.value == "ACKNOWLEDGED"):
            abort("the identical dry-run did not pass completely -- refusing to send")

        log("DEMO_RESULT", sent=outcome.sent, reason_codes=outcome.reason_codes)
        if not outcome.sent or outcome.demo_result is None or outcome.demo_result.order_result is None:
            abort(f"demo send did not succeed: {outcome.reason_codes}")

        order_result = outcome.demo_result.order_result
        demo_ledger_record = demo_ledger.get(order_result.client_order_id)
        broker_order_ticket = demo_ledger_record.broker_order_id if demo_ledger_record is not None else None
        entry_fill_price = order_result.avg_price
        entry_slippage = None if entry_fill_price is None else abs(float(entry_fill_price) - entry_requested_price)
        log(
            "EXECUTION_CONFIRMED",
            retcode="10009 (TRADE_RETCODE_DONE) -- inferred from BrokerAck.accepted=True, per MT5OrderSendResult.ok's own definition; the adapter does not expose the raw numeric retcode on BrokerAck (unmodified, out of scope to change)",
            broker_order_ticket=broker_order_ticket, client_order_id=order_result.client_order_id,
            state=order_result.state.value, filled_qty=order_result.filled_qty,
            entry_requested_price=entry_requested_price, entry_fill_price=entry_fill_price,
            entry_slippage=entry_slippage, dry_run=order_result.dry_run, execution_wall_clock=time.time(),
        )

        # ---- Controlled close: query the real position, then close it referencing its own ticket ----
        time.sleep(1.0)  # let the broker settle the fill before querying real position state
        open_positions = adapter._demo_gateway.positions_get(SYMBOL) or ()
        log("POST_SEND_POSITIONS", count=len(open_positions), positions=[
            {"ticket": getattr(p, "ticket", None), "volume": getattr(p, "volume", None), "type": getattr(p, "type", None)}
            for p in open_positions
        ])

        exit_requested_price: float | None = None
        exit_fill_price: float | None = None
        exit_spread_price: float | None = None

        if len(open_positions) == 0:
            log("NO_POSITION_TO_CLOSE", note="order may have been rejected at the position level, or this account nets differently than expected -- nothing further to close")
        else:
            for position in open_positions:
                ticket = int(getattr(position, "ticket"))
                volume = float(getattr(position, "volume"))
                pos_type = int(getattr(position, "type"))  # 0 = BUY, 1 = SELL
                close_type = 1 if pos_type == 0 else 0
                close_tick = adapter.read_tick(SYMBOL)
                exit_spread_price = float(close_tick.ask) - float(close_tick.bid)
                close_price = float(close_tick.bid) if close_type == 1 else float(close_tick.ask)
                exit_requested_price = close_price
                close_request = {
                    "action": 1, "symbol": SYMBOL, "volume": volume, "type": close_type, "position": ticket,
                    "price": close_price, "deviation": config.deviation_points, "magic": candidate.magic_number,
                    "comment": "XAUUSD-INFRA-TEST-CLOSE", "type_time": 0, "type_filling": 1,
                }
                check_result = adapter._demo_gateway.order_check(close_request)
                log("CLOSE_ORDER_CHECK", ticket=ticket, retcode=getattr(check_result, "retcode", None), comment=getattr(check_result, "comment", None))
                if getattr(check_result, "retcode", -1) != 0:
                    log("CLOSE_ORDER_CHECK_FAILED", ticket=ticket)
                    continue
                send_result = adapter._demo_gateway.order_send(close_request)
                exit_fill_price = getattr(send_result, "price", None)
                log("CLOSE_ORDER_SEND", ticket=ticket, retcode=getattr(send_result, "retcode", None),
                    comment=getattr(send_result, "comment", None), close_price=exit_fill_price,
                    close_volume=getattr(send_result, "volume", None))

        exit_slippage = None
        if exit_fill_price is not None and exit_requested_price is not None:
            exit_slippage = abs(float(exit_fill_price) - exit_requested_price)

        # ---- Realized cost report -- the comparison that matters ----
        realized_round_trip_price_cost = None
        if entry_fill_price is not None and exit_fill_price is not None:
            # LONG: bought at (near) ask, sold at (near) bid, essentially immediately -- the direct
            # price give-up between the two fills is the realized round-trip friction, under the
            # simplifying assumption that the true midpoint barely moved in the ~1-2s hold (disclosed,
            # not proven -- a single trade cannot separate friction from genuine price movement).
            realized_round_trip_price_cost = float(entry_fill_price) - float(exit_fill_price)
        log(
            "REALIZED_COST_REPORT",
            entry_spread_observed=entry_spread_price, exit_spread_observed=exit_spread_price,
            entry_requested_price=entry_requested_price, entry_fill_price=entry_fill_price, entry_slippage=entry_slippage,
            exit_requested_price=exit_requested_price, exit_fill_price=exit_fill_price, exit_slippage=exit_slippage,
            realized_round_trip_price_cost=realized_round_trip_price_cost,
            modeled_round_trip_cost=MODELED_ROUND_TRIP_COST,
            realized_vs_modeled_ratio=None if realized_round_trip_price_cost is None else realized_round_trip_price_cost / MODELED_ROUND_TRIP_COST,
            note="realized_round_trip_price_cost assumes negligible mid-price movement during the ~1-2s "
                 "hold -- disclosed simplifying assumption, not proven by one trade. entry/exit spreads "
                 "observed independently are the assumption-free comparison against the modeled constant.",
        )

        time.sleep(1.0)
        final_positions = adapter._demo_gateway.positions_get(SYMBOL) or ()
        final_orders = adapter._demo_gateway.orders_get(SYMBOL) or ()
        final_account = adapter._demo_gateway.account_info()
        log("FINAL_CLEANUP_VERIFICATION", open_positions=len(final_positions), open_orders=len(final_orders),
            final_balance=getattr(final_account, "balance", None), final_equity=getattr(final_account, "equity", None),
            starting_balance=raw_account.balance)
        if len(final_positions) > 0 or len(final_orders) > 0:
            log("CLEANUP_INCOMPLETE_WARNING", open_positions=len(final_positions), open_orders=len(final_orders))
        else:
            log("CLEANUP_CONFIRMED_FLAT", note="no positions or orders remain open from this test")

        log("TEST_COMPLETE", overall="SUCCESS" if len(final_positions) == 0 and len(final_orders) == 0 else "SUCCESS_WITH_CLEANUP_WARNING")

    finally:
        adapter.disconnect()
        _flush_journal()


if __name__ == "__main__":
    main()
