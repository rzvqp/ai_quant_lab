"""MT5 Connectivity Probe (CEO directive, 2026-07-24). READ-ONLY verification only -- the terminal is
already open and authenticated on a DEMO account. This script is a throwaway diagnostic (matching this
project's own established "diagnostic script, not a permanent library change" precedent), never imported
by any `ai_trader/` production code.

**Authorized**: terminal detection, connecting to the local MetaTrader5 API, verifying connection status,
reading terminal info, reading demo account info, reading available symbols, reading one tick/market data
point.

**Explicitly FORBIDDEN, and NOT called anywhere in this file**: `order_send`, `order_check`,
`order_calc_margin`, `order_calc_profit`, `positions_get`/`positions_total` (position state was not on the
CEO's own authorized list), any order/position modification, any terminal/settings modification. This
script performs zero write operations of any kind against the terminal or the account.
"""

from __future__ import annotations

import json

import MetaTrader5 as mt5

PROBE_SYMBOL = "XAUUSD"


def main() -> None:
    report: dict[str, object] = {}

    initialized = mt5.initialize()
    report["initialize_succeeded"] = initialized
    if not initialized:
        report["initialize_error"] = mt5.last_error()
        print(json.dumps(report, indent=2, default=str))
        return

    try:
        terminal_info = mt5.terminal_info()
        report["terminal_info"] = terminal_info._asdict() if terminal_info is not None else None
        report["terminal_connected"] = bool(terminal_info.connected) if terminal_info is not None else None

        account_info = mt5.account_info()
        if account_info is not None:
            account_dict = account_info._asdict()
            # Redact anything resembling a login identifier out of an abundance of caution, even on a
            # demo account -- this script's own output may be pasted into a report/log.
            account_dict.pop("login", None)
            report["account_info"] = account_dict
            report["account_is_demo_trade_mode"] = account_dict.get("trade_mode")
        else:
            report["account_info"] = None
            report["account_info_error"] = mt5.last_error()

        symbols = mt5.symbols_get()
        report["symbols_total_count"] = len(symbols) if symbols is not None else None
        report["symbols_sample_first_10"] = (
            [s.name for s in symbols[:10]] if symbols is not None else None
        )
        report["probe_symbol_present"] = (
            any(s.name == PROBE_SYMBOL for s in symbols) if symbols is not None else None
        )

        tick = mt5.symbol_info_tick(PROBE_SYMBOL)
        report["probe_symbol"] = PROBE_SYMBOL
        report["tick"] = tick._asdict() if tick is not None else None
        if tick is None:
            report["tick_error"] = mt5.last_error()

        symbol_info = mt5.symbol_info(PROBE_SYMBOL)
        report["symbol_info"] = symbol_info._asdict() if symbol_info is not None else None

    finally:
        mt5.shutdown()
        report["shutdown_called"] = True

    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
