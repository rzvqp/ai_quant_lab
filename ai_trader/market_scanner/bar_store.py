"""Bar Store — bounded rolling windows of complete bars per (symbol, timeframe), plus mechanical
gap detection (``MARKET_SCANNER_ARCHITECTURE.md`` §3 "Per-Symbol State" / §8 "never invent prices;
always disclose").

A :class:`TimeframeWindow` holds only *complete, closed* bars in its rolling window — the "current"
still-forming bar is tracked separately and is never exposed to feature/strategy consumers
(architecture §8: "strategies see only completed bars"). Ingest is idempotent-ish for genuinely
late/out-of-order data: a bar whose period has already closed is dropped and counted, never used to
rewrite history (architecture §8 "Out-of-order / late ticks").
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta

from ai_trader.market_scanner.timeframes import snap_to_grid, timeframe_seconds
from ai_trader.market_scanner.types import RawBar


@dataclass(slots=True, frozen=True)
class Gap:
    """A detected hole in the expected bar grid for one (symbol, timeframe)."""

    from_ts: int
    to_ts: int
    bars_missing: int
    cause: str | None = None


def infer_gap_cause(from_ts: int, to_ts: int) -> str | None:
    """Classify a gap as an expected weekend closure, or leave it unexplained (``None``).

    Any calendar day strictly between ``from_ts`` and ``to_ts`` (UTC) that falls on a Saturday or
    Sunday marks the gap ``"weekend"``. This is a mechanical, self-contained check (no dependency
    on :mod:`~ai_trader.market_scanner.calendar_engine`) so the Bar Store never needs to know about
    session/calendar state to classify its own gaps.
    """
    start_day = datetime.fromtimestamp(from_ts, tz=UTC).date()
    end_day = datetime.fromtimestamp(to_ts, tz=UTC).date()
    day = start_day
    while day <= end_day:
        if day.weekday() >= 5:  # Saturday=5, Sunday=6
            return "weekend"
        day = day + timedelta(days=1)
    return None


class TimeframeWindow:
    """A bounded rolling window of complete bars for one (symbol, timeframe) pair."""

    __slots__ = ("symbol", "timeframe", "_tf_seconds", "_max_len", "_bars", "_forming", "_gaps", "late_dropped")

    def __init__(self, timeframe: str, max_len: int, symbol: str = "") -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self._tf_seconds = timeframe_seconds(timeframe)
        self._max_len = max_len
        self._bars: deque[RawBar] = deque(maxlen=max_len)
        self._forming: RawBar | None = None
        self._gaps: deque[Gap] = deque(maxlen=50)
        self.late_dropped = 0

    @property
    def last_ingested_close(self) -> int | None:
        return self._bars[-1].ts_close if self._bars else None

    @property
    def forming(self) -> RawBar | None:
        return self._forming

    def bars(self) -> list[RawBar]:
        """The rolling window of complete bars, oldest first."""
        return list(self._bars)

    def gaps(self) -> list[Gap]:
        return list(self._gaps)

    def ingest_bar(self, bar: RawBar) -> Gap | None:
        """Ingest a normalized bar (complete or forming) for this timeframe.

        Returns:
            A :class:`Gap` if this ingestion revealed a hole in the grid, else ``None``.
        """
        if not bar.complete:
            if self._forming is None or bar.ts_open >= self._forming.ts_open:
                self._forming = bar
            else:
                self.late_dropped += 1
            return None

        last_close = self.last_ingested_close
        if last_close is not None and bar.ts_open < last_close:
            # this period already closed in our history; never rewrite the past.
            self.late_dropped += 1
            return None

        gap: Gap | None = None
        if last_close is not None and bar.ts_open > last_close:
            bars_missing = (bar.ts_open - last_close) // self._tf_seconds
            if bars_missing > 0:
                gap = Gap(
                    from_ts=last_close,
                    to_ts=bar.ts_open,
                    bars_missing=int(bars_missing),
                    cause=infer_gap_cause(last_close, bar.ts_open),
                )
                self._gaps.append(gap)

        self._bars.append(bar)
        if self._forming is not None and self._forming.ts_open <= bar.ts_open:
            self._forming = None
        return gap

    def apply_tick(self, ts: int, price: float, volume: float | None) -> None:
        """Fold a tick price into the forming bar for this timeframe (base timeframe only)."""
        grid_open = snap_to_grid(ts, self.timeframe)
        last_close = self.last_ingested_close
        if last_close is not None and grid_open < last_close:
            self.late_dropped += 1
            return
        if self._forming is None or self._forming.ts_open != grid_open:
            self._forming = RawBar(
                symbol=self.symbol,
                timeframe=self.timeframe,
                ts_open=grid_open,
                ts_close=grid_open + self._tf_seconds,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=volume,
                complete=False,
            )
        else:
            f = self._forming
            new_volume = None
            if f.volume is not None or volume is not None:
                new_volume = (f.volume or 0.0) + (volume or 0.0)
            self._forming = replace(
                f,
                high=max(f.high, price),
                low=min(f.low, price),
                close=price,
                volume=new_volume,
            )


class SymbolBarStore:
    """All tracked timeframe windows for one symbol."""

    __slots__ = ("symbol", "_windows", "_max_len_by_tf")

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self._windows: dict[str, TimeframeWindow] = {}
        self._max_len_by_tf: dict[str, int] = {}

    def ensure_timeframe(self, timeframe: str, max_len: int) -> TimeframeWindow:
        """Get (creating if needed) the :class:`TimeframeWindow` for ``timeframe``."""
        existing = self._windows.get(timeframe)
        if existing is not None:
            if max_len > self._max_len_by_tf[timeframe]:
                # widen the window (e.g. a strategy with a larger lookback registered later)
                widened = TimeframeWindow(timeframe, max_len, symbol=self.symbol)
                for b in existing.bars():
                    widened.ingest_bar(b)
                if existing.forming is not None:
                    widened.ingest_bar(existing.forming)
                widened.late_dropped = existing.late_dropped
                self._windows[timeframe] = widened
                self._max_len_by_tf[timeframe] = max_len
                return widened
            return existing
        window = TimeframeWindow(timeframe, max_len, symbol=self.symbol)
        self._windows[timeframe] = window
        self._max_len_by_tf[timeframe] = max_len
        return window

    def timeframes(self) -> list[str]:
        return list(self._windows.keys())

    def window(self, timeframe: str) -> TimeframeWindow | None:
        return self._windows.get(timeframe)
