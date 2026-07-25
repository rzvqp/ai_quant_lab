"""`MT5AccountBridge` -- projects a raw `MT5Gateway`'s `account_info()`/`symbol_info()` into
`risk_manager_live.types.AccountState`/`InstrumentSpecification`. Uses the ALREADY-frozen Phase 1
`MT5Gateway` Protocol directly (unlike `mt5_pnl_source`, no subclassed gateway extension is needed here
-- `account_info`/`symbol_select`/`symbol_info` were already part of it).

Fail-closed on every incomplete read (`AccountDataUnavailableError`, matching `mt5_pnl_source`'s own
`PortfolioDataUnavailableError` precedent and rationale) and **never caches**: every call re-reads the
gateway from scratch. A value that cannot currently be read must never be served as though it were
current -- whether that means defaulting to 0.0 (Risk Audit #1) or returning an earlier, now-stale read
(this package's own added constraint).
"""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.execution_engine.adapters.mt5_types import AccountTradeMode
from ai_trader.mt5_account_bridge.types import AccountDataUnavailableError
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification


def _default_clock() -> int:
    return int(time.time())


class MT5AccountBridge:
    """No inheritance from any Protocol required (structural typing, matching this codebase's own
    established convention for real/fake gateway implementations)."""

    def __init__(self, gateway: MT5Gateway, clock: Callable[[], int] = _default_clock) -> None:
        self._gateway = gateway
        self._clock = clock

    def read_account_state(self) -> AccountState:
        account = self._gateway.account_info()
        if account is None:
            raise AccountDataUnavailableError("account_info() returned None")

        trade_mode = getattr(account, "trade_mode", None)
        currency = getattr(account, "currency", None)
        balance = getattr(account, "balance", None)
        equity = getattr(account, "equity", None)
        margin = getattr(account, "margin", None)
        margin_free = getattr(account, "margin_free", None)
        margin_level = getattr(account, "margin_level", None)
        leverage = getattr(account, "leverage", None)

        if (
            trade_mode is None or currency is None or balance is None or equity is None
            or margin is None or margin_free is None or leverage is None
        ):
            raise AccountDataUnavailableError("account_info() result is missing a required field")

        return AccountState(
            as_of=self._clock(),
            currency=str(currency),
            balance=float(balance),
            equity=float(equity),
            margin_used=float(margin),
            margin_free=float(margin_free),
            margin_level=float(margin_level) if margin_level is not None else None,
            leverage=float(leverage),
            is_demo=int(trade_mode) != int(AccountTradeMode.REAL),
        )

    def read_instrument_specification(self, symbol: str) -> InstrumentSpecification:
        # Select before reading -- a symbol not already on the terminal's own Market Watch list can
        # otherwise report stale/missing data (established precedent: the read-only adapter's own
        # symbol-capabilities lookup, in execution_engine/adapters/mt5_adapter.py).
        self._gateway.symbol_select(symbol, True)
        info = self._gateway.symbol_info(symbol)
        if info is None:
            raise AccountDataUnavailableError(f"symbol_info({symbol!r}) returned None")

        tick_size = getattr(info, "trade_tick_size", None)
        lot_step = getattr(info, "volume_step", None)
        min_volume = getattr(info, "volume_min", None)
        max_volume = getattr(info, "volume_max", None)
        contract_size = getattr(info, "trade_contract_size", None)
        tick_value = getattr(info, "trade_tick_value", None)
        margin_currency = getattr(info, "currency_margin", None)

        if (
            tick_size is None or lot_step is None or min_volume is None or max_volume is None
            or contract_size is None or tick_value is None or margin_currency is None
        ):
            raise AccountDataUnavailableError(f"symbol_info({symbol!r}) result is missing a required field")
        if float(tick_size) == 0:
            raise AccountDataUnavailableError(f"symbol_info({symbol!r}).trade_tick_size is zero")

        return InstrumentSpecification(
            symbol=symbol,
            tick_size=float(tick_size),
            lot_step=float(lot_step),
            min_volume=float(min_volume),
            max_volume=float(max_volume),
            contract_size=float(contract_size),
            point_value=float(tick_value) / float(tick_size),
            margin_currency=str(margin_currency),
        )
