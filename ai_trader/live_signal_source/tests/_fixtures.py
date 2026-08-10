"""Shared fake gateway for `live_signal_source` tests -- implements the FULL `MT5Gateway` Protocol
surface (matching the established precedent, `mt5_pnl_source`/`mt5_account_bridge`'s own fixtures)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_UNSET: Any = object()


@dataclass
class FakeTick:
    """Minimal stand-in for MT5's real tick namedtuple -- only the `.time` field `make_broker_clock`
    reads. `bid`/`ask` default to 0.0 since no test using this needs them; construct a richer fake
    directly where a test needs real quote values."""

    time: int
    bid: float = 0.0
    ask: float = 0.0


@dataclass
class RawRate:
    """One raw MT5 `copy_rates_from` record -- field names match the real MetaTrader5 rate tuple
    exactly (`time`, `open`, `high`, `low`, `close`, `tick_volume`)."""

    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


class FakeMT5Gateway:
    def __init__(self, rates: Any = _UNSET, range_rates: Any = _UNSET, tick_time: int | None = None) -> None:
        self.rates: Any = [] if rates is _UNSET else rates
        """Returned by `copy_rates_from` (the steady-state, small-lookback path)."""
        self.range_rates: Any = [] if range_rates is _UNSET else range_rates
        """Returned by `copy_rates_range` (the backfill, full-missing-window path) -- separate from
        `rates` so a test can assert exactly which fetch path `LiveBarFeed` chose."""
        self.tick_time: int | None = tick_time
        """Backs `symbol_info_tick(...).time` -- `make_broker_clock`'s only read. Defaults to `None`
        (matching the pre-broker-clock behavior, `symbol_info_tick` returning `None`) since most tests
        in this package inject their own `clock=` lambda directly and never touch this at all; a test
        exercising `make_broker_clock` (or a `build_loop` composition that now wires one) must set this
        explicitly to a value at or after the bars' own `ts_close`, or every bar will look "still
        forming"."""
        self.copy_rates_from_calls: list[tuple[str, int, int, int]] = []
        self.copy_rates_range_calls: list[tuple[str, int, int, int]] = []

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
        self.copy_rates_from_calls.append((symbol, timeframe, date_from, count))
        if self.rates is None:
            return None
        return tuple(self.rates)

    # -- the rest of `MT5Gateway`, unused here, stubbed to satisfy the Protocol structurally --

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        return None

    def terminal_info(self) -> Any | None:
        return None

    def account_info(self) -> Any | None:
        return None

    def symbols_get(self) -> tuple[Any, ...] | None:
        return None

    def symbol_info(self, symbol: str) -> Any | None:
        return None

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any | None:
        return None if self.tick_time is None else FakeTick(time=self.tick_time)

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any | None:
        self.copy_rates_range_calls.append((symbol, timeframe, date_from, date_to))
        if self.range_rates is None:
            return None
        return tuple(self.range_rates)

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any | None:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any | None:
        return None

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return None

    def orders_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return None

    def last_error(self) -> tuple[int, str]:
        return (0, "no error")
