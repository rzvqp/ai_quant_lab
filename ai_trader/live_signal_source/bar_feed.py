"""`LiveBarFeed` (Piesa 1): emits a `Bar` only at candle CLOSE, never a forming/in-progress bar.

Motivated by a concrete failure the data-acquisition division found today (CEO, 2026-07-26): the
TradingView replay cursor's own bar carries a PROVISIONAL close/volume while still active, which
corrupted 1,186 of 355,716 bars in one historical file. The same error class live -- reading a bar
before its close time has actually passed -- would produce signals on values that can still change
after being read.

`poll()` computes each candidate bar's own close time (`ts_open + bar_seconds`) and compares it against
the injected clock; a bar whose close time has not yet passed is filtered out, silently -- this is not
an error, it simply is not closed yet. Dedup against `_last_emitted_ts_open` ensures a bar already
returned by a prior `poll()` is never returned twice.

**Mandate 2 (2026-07-27), persistence**: an optional injected `SqliteStateStore` makes the watermark
survive a process restart -- without one, behavior is byte-for-byte the prior in-memory-only version
(every pre-Mandate-2 test still passes unmodified). With one, the watermark is loaded from the store at
construction (instead of starting at `None`) and written through on every `poll()` that emits new bars,
keyed per `(symbol, mt5_timeframe)` so two feeds sharing one store never collide.
"""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.execution_engine.adapters.mt5_gateway import MT5Gateway
from ai_trader.live_signal_source.types import Bar, BarFeedError
from ai_trader.persistent_state.store import SqliteStateStore


def _default_clock() -> int:
    return int(time.time())


class LiveBarFeed:
    def __init__(
        self, gateway: MT5Gateway, symbol: str, mt5_timeframe: int, bar_seconds: int,
        lookback_count: int = 10, clock: Callable[[], int] = _default_clock,
        state_store: SqliteStateStore | None = None,
    ) -> None:
        if bar_seconds <= 0:
            raise ValueError(f"LiveBarFeed: bar_seconds must be > 0, got {bar_seconds!r}")
        if lookback_count <= 0:
            raise ValueError(f"LiveBarFeed: lookback_count must be > 0, got {lookback_count!r}")
        self._gateway = gateway
        self._symbol = symbol
        self._mt5_timeframe = mt5_timeframe
        self._bar_seconds = bar_seconds
        self._lookback_count = lookback_count
        self._clock = clock
        self._state_store = state_store
        self._watermark_key = f"live_signal_source.bar_feed:{symbol}:{mt5_timeframe}"
        self._last_emitted_ts_open: int | None = (
            None if state_store is None else self._load_persisted_watermark(state_store)
        )

    def _load_persisted_watermark(self, state_store: SqliteStateStore) -> int | None:
        persisted = state_store.get_value(self._watermark_key)
        return None if persisted is None else int(persisted)

    def poll(self) -> tuple[Bar, ...]:
        """Returns every newly CLOSED bar since the previous `poll()` call, oldest first. Never returns
        the currently-forming bar. Raises `BarFeedError` on a genuine gateway failure -- never returns a
        stale/partial result silently."""
        now = self._clock()
        rates = self._gateway.copy_rates_from(self._symbol, self._mt5_timeframe, now, self._lookback_count)
        if rates is None:
            raise BarFeedError(f"copy_rates_from({self._symbol!r}) returned None")

        closed_bars: list[Bar] = []
        for rate in rates:
            ts_open = getattr(rate, "time", None)
            open_ = getattr(rate, "open", None)
            high = getattr(rate, "high", None)
            low = getattr(rate, "low", None)
            close = getattr(rate, "close", None)
            volume = getattr(rate, "tick_volume", None)
            if ts_open is None or open_ is None or high is None or low is None or close is None:
                raise BarFeedError(
                    f"copy_rates_from({self._symbol!r}) returned a rate missing an OHLC field"
                )

            ts_open = int(ts_open)
            ts_close = ts_open + self._bar_seconds
            if ts_close > now:
                continue  # still forming -- never emitted; not an error
            if self._last_emitted_ts_open is not None and ts_open <= self._last_emitted_ts_open:
                continue  # already emitted in a prior poll() -- dedup

            closed_bars.append(Bar(
                symbol=self._symbol, ts_open=ts_open, ts_close=ts_close,
                open=float(open_), high=float(high), low=float(low), close=float(close),
                volume=float(volume) if volume is not None else None,
            ))

        closed_bars.sort(key=lambda b: b.ts_open)
        if closed_bars:
            self._last_emitted_ts_open = closed_bars[-1].ts_open
            if self._state_store is not None:
                self._state_store.set_value(self._watermark_key, float(self._last_emitted_ts_open))
        return tuple(closed_bars)
