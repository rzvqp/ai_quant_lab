"""Gated real-MT5-terminal integration test for Phase 10 -- mirrors Phase 1's own
`MT5_REAL_TERMINAL_TEST=1`-gated precedent exactly, but under its OWN, separate, more explicit env var
(`MT5_REAL_DEMO_ORDER_TEST=1`) so enabling Phase 1's read-only real-terminal tests never accidentally
enables an order-sending one.

**Exact flow, per the CEO's own explicit instruction (2026-07-25)**:
1. Connect to the real terminal, real gateway, real `MT5DemoBrokerAdapter`.
2. Verify DEMO account (the adapter's own `_do_connect`, inherited unmodified, already refuses non-DEMO
   -- this step re-confirms it independently, as `test_mt5_real_terminal_integration.py` already does
   for the read-only adapter).
3. Verify the symbol (`XAUUSD`) is available.
4. Verify the market is OPEN (`is_market_open_for_symbol`, tick-recency heuristic) -- if CLOSED, STOP
   here, before any `order_check`/`order_send` call, and report `PENDING_MARKET_OPEN`. Never bypassed.
5. Run the full `verify_safety_guards` chain (connected, DEMO, AlgoTrading enabled, server, volume,
   market open) -- if ANY guard fails, stop, never send.
6. Only if every guard passes: submit exactly ONE order, at the broker's own confirmed minimum volume
   (`0.01` lots, `MT5DemoConfig`'s own default), via `MT5DemoBrokerAdapter.submit_order` (which itself
   calls `order_check` before `order_send`, unmodified).
7. Disconnect in a `finally` block, mirroring the read-only test's own precedent.

Run: `MT5_REAL_DEMO_ORDER_TEST=1 pytest ai_trader/mt5_demo_execution/tests/test_mt5_demo_real_terminal_integration.py -v -s`
"""

from __future__ import annotations

import os

import pytest

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
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import is_market_open_for_symbol, verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.signal_engine.types import Direction

pytestmark = pytest.mark.skipif(
    os.environ.get("MT5_REAL_DEMO_ORDER_TEST") != "1",
    reason="Gated: set MT5_REAL_DEMO_ORDER_TEST=1 to run against a REAL, already-open, already-"
    "authenticated MT5 DEMO terminal. Never runs implicitly as part of standard regression.",
)

_SYMBOL = "XAUUSD"


def test_real_demo_single_minimum_volume_order_or_pending_market_open() -> None:
    config = MT5DemoConfig(max_order_volume=0.01)
    adapter = MT5DemoBrokerAdapter(config=config)
    try:
        connection = adapter.connect()
        assert connection.accepted is True, f"connect() refused: {connection.reason}"

        status = adapter.status()
        assert status.account_is_demo is True, "SAFETY: refusing to proceed on a non-DEMO account"

        capabilities = adapter.symbol_capabilities(_SYMBOL)
        assert capabilities is not None, f"{_SYMBOL} not available on this terminal"

        market_open = is_market_open_for_symbol(adapter, _SYMBOL, config)
        if not market_open:
            pytest.skip(f"PENDING_MARKET_OPEN: {_SYMBOL} market is closed (or undeterminable) -- stopping before any transmission")

        report = verify_safety_guards(adapter, config, symbol=_SYMBOL)
        if not report.all_passed:
            pytest.fail(
                f"safety guards did not all pass, refusing to send: connected={report.connected} "
                f"account_is_demo={report.account_is_demo} algo_trading_enabled={report.algo_trading_enabled} "
                f"server_matches_expected={report.server_matches_expected} "
                f"max_volume_configured={report.max_volume_configured} market_open={report.market_open}"
            )

        tick = adapter.read_tick(_SYMBOL)
        assert tick is not None
        entry = float(tick.ask)

        order = OrderRequest(
            order_schema_version="1.0.0", execution_engine_version="1.0.0",
            order_request_id="PHASE10-REAL-DEMO-TEST", client_order_id="PHASE10-REAL-DEMO-TEST",
            decision_id="PHASE10-REAL-DEMO-TEST", strategy_id="PHASE10_MANUAL_TEST", symbol=_SYMBOL,
            timestamp=0, as_of=0, side=OrderSide.BUY, direction=Direction.LONG, intent=OrderIntent.OPEN,
            order_type=OrderType.MARKET, time_in_force=TimeInForce.IOC, quantity=config.max_order_volume,
            limit_price=entry, bracket=BracketLegs(take_profit=None, stop_loss=None),
            constraints=OrderConstraints(max_slippage=None, reduce_only=False, post_only=False),
            refs=OrderRefs(risk_schema_version="1.0.0", risk_policy_version="1.0.0"),
        )

        ack = adapter.submit_order(order)
        print(f"submit_order result: accepted={ack.accepted} broker_order_id={ack.broker_order_id} reason={ack.reason}")
        assert ack.accepted is True, f"real DEMO order was refused: {ack.reason}"

        result_status = adapter.query_status(order.client_order_id)
        assert result_status is not None
        print(f"final status: {result_status.state.value}")
    finally:
        adapter.disconnect()
