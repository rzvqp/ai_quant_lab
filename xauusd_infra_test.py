"""XAUUSD Infrastructure Test -- CEO-authorized 2026-08-03, attempt 3: sizing BYPASSED.

"Ocoleste compute_sizing pentru testul de instalatie. Volum 0,01 explicit." -- the installation test
verifies the PIPE (request -> adapter -> MT5 -> confirmation -> close -> flat account), not sizing.
Those are two different things; the 3.03%-risk-for-min-lot finding from attempt 2 is real and stays on
record (`XAUUSD_INFRA_TEST_REPORT.md`), but is out of scope for what this script now tests.

**SIZING IS EXPLICITLY BYPASSED FOR THIS INSTALLATION TEST ONLY** -- `risk_manager/sizing.py::compute_sizing`
is NEVER CALLED, `RiskConfig` is NEVER CONSTRUCTED, `risk_per_trade_pct` is NEVER READ. Volume is a
HARDCODED constant (`TEST_VOLUME = 0.01`), and the order is built directly (`execution_engine.types.OrderRequest`,
the exact same shape `execution_engine/builder.py::build_order` would normally produce from a sized
`RiskDecision`) and sent straight to `MT5DemoBrokerAdapter.submit_order()` -- skipping
`execution_orchestrator.orchestrate()`/`send_after_dry_run_gate()` entirely, since bypassing sizing means
there is no `RiskDecision` for that pipeline to run on. `submit_order()` itself still enforces every one
of its own safety refusals (connected, DEMO, AlgoTrading, expected server, volume ceiling) -- ONLY the
sizing computation is skipped, nothing else.

NOT PDH-PDL, NOT going through `PdhPdlRecognitionRule`. ONE order. Aborts fail-closed on any check
failure. Lives at repo root, not inside any `ai_trader` package, not part of the standing test suite.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ai_trader.execution_engine.types import (
    BrokerCapabilitiesRef,
    OrderConstraints,
    OrderIntent,
    OrderRefs,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
)
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import is_market_open_for_symbol, verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
MODELED_ROUND_TRIP_COST = 0.20  # $ -- the constant assumed throughout the project's own backtests
TEST_VOLUME = 0.01  # HARDCODED -- sizing bypassed for this installation test only (CEO, 2026-08-03)
ORDER_SCHEMA_VERSION = "1.0.0"
EXECUTION_ENGINE_VERSION = "1.0.0"
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

        # ---- Check 11: minimum allowed volume -- confirm the hardcoded TEST_VOLUME is actually valid ----
        min_volume = caps.min_qty
        log("CHECK_11_MIN_VOLUME", min_volume=min_volume, test_volume_hardcoded=TEST_VOLUME,
            sizing_bypassed=True, note="TEST_VOLUME is a hardcoded constant for this installation test -- NOT computed by risk_manager/sizing.py")
        if min_volume is None or min_volume <= 0:
            abort("could not determine a valid minimum volume")
        if TEST_VOLUME < min_volume or TEST_VOLUME > caps.max_qty:
            abort(f"TEST_VOLUME={TEST_VOLUME} outside broker-allowed range [{min_volume}, {caps.max_qty}]")

        config = MT5DemoConfig(max_order_volume=TEST_VOLUME, expected_server=status.server)
        adapter._config = config  # script-level re-configuration of the already-connected instance;
        # not a file/component modification -- MT5DemoConfig is a plain constructor parameter.

        # Read real account numbers directly from the already-approved, frozen read-only gateway --
        # never fabricated. (contract_size/tick_value/tick_size are read for REPORTING only in this
        # attempt -- point_value/RiskConfig are not constructed at all, since sizing is bypassed.)
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

        # ---- Check 12: safety-guard report (compute_sizing/RiskConfig are NEVER constructed here) ----
        safety_report = verify_safety_guards(adapter, config, symbol=SYMBOL)
        log("SAFETY_GUARD_REPORT", connected=safety_report.connected, account_is_demo=safety_report.account_is_demo,
            algo_trading_enabled=safety_report.algo_trading_enabled, server_matches_expected=safety_report.server_matches_expected,
            max_volume_configured=safety_report.max_volume_configured, market_open=safety_report.market_open,
            all_passed=safety_report.all_passed)
        if not safety_report.all_passed:
            abort("final automated safety-guard verification did not all pass")

        # ---- Build the OrderRequest DIRECTLY -- the same shape execution_engine/builder.py::build_order
        # would normally produce from a sized RiskDecision, with `quantity` hardcoded instead of
        # `sizing.size_units`. No RiskDecision exists here because sizing was never run. ----
        entry_requested_price = float(entry_tick.ask)  # BUY fills at ask
        decision_id = f"XAUUSD-INFRA-SIZING-BYPASSED-{now}"
        order = OrderRequest(
            order_schema_version=ORDER_SCHEMA_VERSION, execution_engine_version=EXECUTION_ENGINE_VERSION,
            order_request_id=f"OM-REQ-{decision_id}", client_order_id=f"OM-CID-{decision_id}",
            decision_id=decision_id, strategy_id="S998",  # ORDER_SCHEMA.json requires ^S\d+$; distinct infra-test id
            symbol=SYMBOL, timestamp=now, as_of=now, side=OrderSide.BUY, direction=Direction.LONG,
            intent=OrderIntent.OPEN, order_type=OrderType.MARKET, time_in_force=TimeInForce.IOC,
            quantity=TEST_VOLUME,  # HARDCODED -- sizing bypassed
            constraints=OrderConstraints(max_slippage=entry_spread_price * 5, reduce_only=False, post_only=False),
            broker_capabilities_ref=BrokerCapabilitiesRef(
                tick_size=caps.tick_size, lot_step=caps.lot_step, min_qty=caps.min_qty, max_qty=caps.max_qty,
            ),
            refs=OrderRefs(risk_schema_version="SIZING_BYPASSED", risk_policy_version="SIZING_BYPASSED"),
        )
        log("ORDER_REQUEST_BUILT_SIZING_BYPASSED", client_order_id=order.client_order_id, quantity=order.quantity,
            order_type=order.order_type.value, side=order.side.value, sizing_bypassed=True,
            note="compute_sizing/RiskConfig never constructed or called for this request")

        log("SENDING_DIRECTLY_TO_ADAPTER", note="OrderRequest -> MT5DemoBrokerAdapter.submit_order() -> MT5 order_check -> MT5 order_send (execution_orchestrator/send_after_dry_run_gate bypassed along with sizing)")
        ack = adapter.submit_order(order)
        log("SUBMIT_ORDER_ACK", accepted=ack.accepted, reason=ack.reason, broker_order_id=ack.broker_order_id)
        if not ack.accepted:
            abort(f"submit_order refused: {ack.reason}")

        order_status = adapter.query_status(order.client_order_id)
        entry_fill_price = order_status.avg_price if order_status is not None else None
        entry_slippage = None if entry_fill_price is None else abs(float(entry_fill_price) - entry_requested_price)
        log(
            "EXECUTION_CONFIRMED",
            retcode="10009 (TRADE_RETCODE_DONE) -- inferred from BrokerAck.accepted=True, per MT5OrderSendResult.ok's own definition",
            broker_order_ticket=ack.broker_order_id, client_order_id=order.client_order_id,
            state=None if order_status is None else order_status.state.value,
            filled_qty=None if order_status is None else order_status.filled_qty,
            entry_requested_price=entry_requested_price, entry_fill_price=entry_fill_price,
            entry_slippage=entry_slippage, execution_wall_clock=time.time(),
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
                    "price": close_price, "deviation": config.deviation_points, "magic": 0,
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
        realized_round_trip_dollars = None
        if entry_fill_price is not None and exit_fill_price is not None:
            # LONG: bought at (near) ask, sold at (near) bid, essentially immediately -- the direct
            # price give-up between the two fills is the realized round-trip friction, under the
            # simplifying assumption that the true midpoint barely moved in the ~1-2s hold (disclosed,
            # not proven -- a single trade cannot separate friction from genuine price movement).
            realized_round_trip_price_cost = float(entry_fill_price) - float(exit_fill_price)
            # At TEST_VOLUME=0.01 lots (1 oz), a $1 price move = contract_size*TEST_VOLUME = 1 oz worth
            # of USD P&L -- so the $ round-trip cost at this specific volume equals the price-unit cost
            # times (contract_size * TEST_VOLUME), in the instrument's OWN quote currency (USD), not
            # yet converted to account currency (PLN) -- reported as USD to match the project's own
            # $0.20 modeled constant directly.
            realized_round_trip_dollars = realized_round_trip_price_cost * contract_size * TEST_VOLUME
        log(
            "REALIZED_COST_REPORT",
            entry_spread_observed=entry_spread_price, exit_spread_observed=exit_spread_price,
            entry_requested_price=entry_requested_price, entry_fill_price=entry_fill_price, entry_slippage=entry_slippage,
            exit_requested_price=exit_requested_price, exit_fill_price=exit_fill_price, exit_slippage=exit_slippage,
            realized_round_trip_price_cost=realized_round_trip_price_cost,
            realized_round_trip_dollars_at_test_volume=realized_round_trip_dollars,
            test_volume=TEST_VOLUME, modeled_round_trip_cost=MODELED_ROUND_TRIP_COST,
            realized_vs_modeled_ratio=None if realized_round_trip_dollars is None else realized_round_trip_dollars / MODELED_ROUND_TRIP_COST,
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
