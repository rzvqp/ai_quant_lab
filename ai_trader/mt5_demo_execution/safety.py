"""`verify_safety_guards`/`is_market_open_for_symbol` -- the final automated safety-guard verification
CEO requires before the very first real DEMO trade attempt. Every guard is individually inspectable
(`SafetyGuardReport`) -- if any fails, `all_passed` is `False` and the caller must not send."""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.execution_engine.adapters.mt5_types import AlgoTradingStatus
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import MT5DemoConfig, SafetyGuardReport


def is_market_open_for_symbol(
    adapter: MT5DemoBrokerAdapter, symbol: str, config: MT5DemoConfig, clock: Callable[[], float] | None = None,
) -> bool | None:
    """Heuristic: a symbol whose most recent tick is older than
    `config.market_staleness_threshold_seconds` is treated as closed -- broker/timezone-agnostic (no
    day-of-week/session-hours table is fabricated). `None` (undeterminable, no tick data at all) is
    treated as NOT open by every caller of this function -- fail-closed, never fail-open."""
    resolved_clock = clock if clock is not None else time.time
    tick = adapter.read_tick(symbol)
    if tick is None:
        return None
    tick_time = getattr(tick, "time", None)
    if tick_time is None:
        return None
    age_seconds = resolved_clock() - float(tick_time)
    return age_seconds <= config.market_staleness_threshold_seconds


def verify_safety_guards(
    adapter: MT5DemoBrokerAdapter, config: MT5DemoConfig, symbol: str | None = None,
    clock: Callable[[], float] | None = None,
) -> SafetyGuardReport:
    if not adapter.is_connected():
        return SafetyGuardReport(
            connected=False, account_is_demo=False, algo_trading_enabled=False,
            server_matches_expected=False, max_volume_configured=config.max_order_volume > 0,
            market_open=None,
        )

    status = adapter.status()
    market_open = is_market_open_for_symbol(adapter, symbol, config, clock) if symbol is not None else None

    return SafetyGuardReport(
        connected=True,
        account_is_demo=status.account_is_demo is True,
        algo_trading_enabled=status.algo_trading_status is AlgoTradingStatus.ENABLED,
        server_matches_expected=(config.expected_server is None or status.server == config.expected_server),
        max_volume_configured=config.max_order_volume > 0,
        market_open=market_open,
    )
