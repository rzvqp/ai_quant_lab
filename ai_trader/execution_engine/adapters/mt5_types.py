"""Data types for the MT5 read-only adapter (Layer B). Small, explicit, no hidden defaults."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AccountTradeMode(int, Enum):
    """Mirrors MT5's own `ACCOUNT_TRADE_MODE_*` integer constants exactly (confirmed empirically this
    session: the connected demo account reported `trade_mode == 0`,
    `MT5_CONNECTIVITY_PROBE_REPORT.md`)."""

    DEMO = 0
    CONTEST = 1
    REAL = 2


class AlgoTradingStatus(str, Enum):
    """The CEO's own explicit required reporting for the terminal-level AlgoTrading toggle -- a plain
    status value, never an exception; this read-only adapter never attempts to change it."""

    ENABLED = "ENABLED"
    TRADING_DISABLED_AT_TERMINAL = "TRADING_DISABLED_AT_TERMINAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class NormalizedMT5Error:
    """`mt5.last_error()` returns a `(code, description)` tuple whose shape/availability can vary by
    platform/build -- normalized here into one stable, always-present shape."""

    code: int
    description: str


@dataclass(frozen=True, slots=True)
class MT5SymbolCapabilities:
    """Per-symbol capability snapshot -- deliberately NOT the Protocol's own `BrokerCapabilities` type
    (that type's own `tick_size`/`lot_step`/`min_qty`/`max_qty` fields are single global scalars, not
    per-symbol -- a real mismatch with MT5's own per-symbol contract specs, disclosed rather than forced
    into a shape that doesn't fit)."""

    symbol: str
    tick_size: float
    lot_step: float
    min_qty: float
    max_qty: float
    digits: int
    spread: int
    trade_mode: int
    description: str


@dataclass(frozen=True, slots=True)
class MT5AdapterStatus:
    """The CEO's own explicit required exposed-status shape. Every field is `None`/`UNKNOWN` when not
    yet knowable (e.g. before the first successful `connect()`) -- never fabricated."""

    connected: bool
    terminal_connected: bool | None
    account_trade_mode: AccountTradeMode | None
    account_is_demo: bool | None
    account_trade_allowed: bool | None
    terminal_algo_trading_allowed: bool | None
    algo_trading_status: AlgoTradingStatus
    server: str | None
    terminal_build: int | None
    last_heartbeat: int | None
    last_error_normalized: NormalizedMT5Error | None
