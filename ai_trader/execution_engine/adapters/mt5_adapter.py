"""`MT5ReadOnlyBrokerAdapter` -- Layer B (`BROKER_ADAPTER_DESIGN.md` + CEO's own Layer B authorization,
2026-07-24). A REAL adapter for a real MT5 terminal, strictly read-only.

**Deliberately does NOT implement the `BrokerAdapter` Protocol's `submit_order`/`cancel_order` methods AT
ALL** -- not a stub that refuses, not a placeholder: the methods do not exist on this class. This is a
stronger safety guarantee than a refusing stub would be (there is no method to accidentally call, and no
method a future edit could carelessly "complete"). `capabilities()`/`query_status()`/`query_open_orders()`
are ALSO not implemented in this phase -- disclosed as an explicit, deliberate scope-narrowing decision
(`symbol_capabilities()` below covers "read capabilities for XAUUSD," the one thing actually required by
the CEO's own mandatory test list; nothing today needs `query_status`/`query_open_orders` for
reconciliation, since Execution Integration -- the only consumer that would -- has not begun).

**Only the CEO's own authorized read-only operations are called, exclusively through `MT5Gateway`**
(never a direct import of the real MT5 package here): `initialize`, `shutdown`, `terminal_info`, `account_info`,
`symbols_get`, `symbol_info`, `symbol_select` (only when reading a symbol's own info/tick requires it),
`symbol_info_tick`. `copy_rates_*`/`copy_ticks_*`/`positions_get`/`orders_get` are available on
`MT5Gateway` but not called by this class yet (no scope currently needs them); available for a
future, separately-scoped read-only reconciliation need.

**Mandatory safety refusals** (CEO's own explicit list, enforced in `_do_connect`, never retried, never
auto-corrected): non-DEMO account, unexpected server (only if `BrokerCredentials.expected_server` is
set), terminal not connected, account/terminal data unreadable. No automatic fallback to any other
account is ever attempted -- a refusal is the end of that `connect()` call, full stop.
"""

from __future__ import annotations

from typing import Any

from ai_trader.execution_engine.adapters.base import RealBrokerAdapterBase, TransientOperationError
from ai_trader.execution_engine.adapters.connection import ConnectionResult
from ai_trader.execution_engine.adapters.exceptions import (
    AccountValidationError,
    NonDemoAccountError,
    TerminalNotConnectedError,
    UnexpectedServerError,
)
from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway, RealMT5Gateway
from ai_trader.execution_engine.adapters.mt5_types import (
    AccountTradeMode,
    AlgoTradingStatus,
    MT5AdapterStatus,
    MT5SymbolCapabilities,
    NormalizedMT5Error,
)


class MT5ReadOnlyBrokerAdapter(RealBrokerAdapterBase):
    def __init__(self, *, gateway: MT5Gateway | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._gateway: MT5Gateway = gateway if gateway is not None else RealMT5Gateway()

    # ------------------------------------------------------------------ RealBrokerAdapterBase hooks

    def _do_connect(self) -> ConnectionResult:
        initialized = self._gateway.initialize(
            path=self._credentials.path, login=self._credentials.login,
            password=self._credentials.password, server=self._credentials.server,
        )
        if not initialized:
            code, description = self._gateway.last_error()
            raise TransientOperationError(f"mt5.initialize() failed: ({code}) {description}")

        terminal = self._gateway.terminal_info()
        if terminal is None:
            raise AccountValidationError("terminal_info() returned None -- cannot validate terminal state")
        if not bool(terminal.connected):
            raise TerminalNotConnectedError("terminal_info().connected is False")

        account = self._gateway.account_info()
        if account is None:
            raise AccountValidationError("account_info() returned None -- cannot validate account state")

        if account.trade_mode != AccountTradeMode.DEMO.value:
            raise NonDemoAccountError(
                f"account trade_mode={account.trade_mode!r} is not DEMO "
                f"({AccountTradeMode.DEMO.value!r}) -- refusing, no automatic fallback attempted"
            )

        if (
            self._credentials.expected_server is not None
            and account.server != self._credentials.expected_server
        ):
            raise UnexpectedServerError(
                f"connected server={account.server!r} != "
                f"expected_server={self._credentials.expected_server!r}"
            )

        return ConnectionResult(accepted=True)

    def _do_disconnect(self) -> None:
        self._gateway.shutdown()

    def _do_heartbeat_check(self) -> bool:
        terminal = self._gateway.terminal_info()
        return terminal is not None and bool(terminal.connected)

    # ------------------------------------------------------------------ read-only status/data surface

    def status(self) -> MT5AdapterStatus:
        """Always safe to call, connected or not -- every field degrades to `None`/`UNKNOWN` rather
        than raising or fabricating a value."""
        terminal = self._gateway.terminal_info()
        account = self._gateway.account_info()
        error_code, error_description = self._gateway.last_error()
        normalized_error = (
            NormalizedMT5Error(code=error_code, description=error_description) if error_code != 0 else None
        )

        terminal_connected = bool(terminal.connected) if terminal is not None else None
        terminal_algo_allowed = bool(terminal.trade_allowed) if terminal is not None else None
        if terminal_algo_allowed is None:
            algo_status = AlgoTradingStatus.UNKNOWN
        elif terminal_algo_allowed:
            algo_status = AlgoTradingStatus.ENABLED
        else:
            algo_status = AlgoTradingStatus.TRADING_DISABLED_AT_TERMINAL

        trade_mode = AccountTradeMode(account.trade_mode) if account is not None else None

        return MT5AdapterStatus(
            connected=self.is_connected(),
            terminal_connected=terminal_connected,
            account_trade_mode=trade_mode,
            account_is_demo=(trade_mode is AccountTradeMode.DEMO) if trade_mode is not None else None,
            account_trade_allowed=bool(account.trade_allowed) if account is not None else None,
            terminal_algo_trading_allowed=terminal_algo_allowed,
            algo_trading_status=algo_status,
            server=account.server if account is not None else None,
            terminal_build=terminal.build if terminal is not None else None,
            last_heartbeat=self.last_heartbeat_as_of(),
            last_error_normalized=normalized_error,
        )

    def symbol_capabilities(self, symbol: str) -> MT5SymbolCapabilities | None:
        """Read-only per-symbol capability snapshot. Calls `symbol_select` only because a symbol not
        already present on the terminal's own Market Watch list can otherwise report stale/no data for
        `symbol_info`/`symbol_info_tick` -- CEO's own explicit "only if necessary for reading" condition."""
        if not self.is_connected():
            return None
        self._gateway.symbol_select(symbol, True)
        info = self._gateway.symbol_info(symbol)
        if info is None:
            return None
        return MT5SymbolCapabilities(
            symbol=symbol, tick_size=float(info.trade_tick_size), lot_step=float(info.volume_step),
            min_qty=float(info.volume_min), max_qty=float(info.volume_max), digits=int(info.digits),
            spread=int(info.spread), trade_mode=int(info.trade_mode), description=str(info.description),
        )

    def read_tick(self, symbol: str) -> Any | None:
        """Read-only, no side effects beyond the gateway's own already-established connection."""
        if not self.is_connected():
            return None
        return self._gateway.symbol_info_tick(symbol)

    def list_symbols(self) -> tuple[str, ...] | None:
        if not self.is_connected():
            return None
        symbols = self._gateway.symbols_get()
        return tuple(s.name for s in symbols) if symbols is not None else None
