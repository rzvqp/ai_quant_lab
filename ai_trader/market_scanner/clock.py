"""The canonical clock controller behind :meth:`MarketScanner.advance_clock`.

Tracks, per (symbol, timeframe), the last bar-close already reported to the caller, and — when the
clock advances to a new ``as_of`` — returns every newly-closed bar in chronological order. The
clock itself never moves backward (architecture §4.6 determinism / §9 "one canonical clock").
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.market_scanner.bar_store import SymbolBarStore


@dataclass(slots=True, frozen=True)
class SymbolTimeframeClose:
    """One (symbol, timeframe) bar that closed at/before the ``as_of`` just advanced to."""

    symbol: str
    timeframe: str
    ts_close: int


class ClockController:
    """Global, monotonic canonical clock shared by every tracked symbol."""

    __slots__ = ("_as_of", "_last_reported")

    def __init__(self) -> None:
        self._as_of: int | None = None
        self._last_reported: dict[tuple[str, str], int] = {}

    @property
    def as_of(self) -> int | None:
        return self._as_of

    def advance(
        self, as_of: int, stores: dict[str, SymbolBarStore]
    ) -> list[SymbolTimeframeClose]:
        """Move the canonical clock to ``as_of`` and report every newly-closed bar.

        Args:
            as_of: the new canonical timestamp (UTC epoch seconds). Must be ``>=`` the current
                clock value.
            stores: the per-symbol bar stores to scan for newly-closed bars.

        Returns:
            Every ``(symbol, timeframe)`` bar whose close is in ``(previously reported, as_of]``,
            oldest first, deterministically ordered by ``(ts_close, symbol, timeframe)``.

        Raises:
            ValueError: if ``as_of`` would move the clock backward.
        """
        if self._as_of is not None and as_of < self._as_of:
            raise ValueError(
                f"clock cannot move backward: current as_of={self._as_of}, requested={as_of}"
            )
        self._as_of = as_of

        closes: list[SymbolTimeframeClose] = []
        for symbol, store in stores.items():
            for timeframe in store.timeframes():
                window = store.window(timeframe)
                if window is None:
                    continue
                key = (symbol, timeframe)
                last_reported = self._last_reported.get(key, -1)
                for bar in window.bars():
                    if last_reported < bar.ts_close <= as_of:
                        closes.append(SymbolTimeframeClose(symbol, timeframe, bar.ts_close))
                        last_reported = bar.ts_close
                self._last_reported[key] = last_reported
        closes.sort(key=lambda c: (c.ts_close, c.symbol, c.timeframe))
        return closes
