"""The Replay Data Source (``SIMULATION_ARCHITECTURE.md`` §3): feeds the Market Scanner historical
bars in order. Reads the Research Lab's own already-produced, read-only CSV bar files under
``data/market/`` (``NEXT_SESSION.md``: "Data already present in ``data/market/``") -- it never imports
or calls Research Lab code, only reads its already-materialized output files, preserving the
Research-Lab-is-frozen boundary.

IMPLEMENTATION CHOICE: file naming convention is ``{PROVIDER}_{SYMBOL}_{TIMEFRAME}.csv`` (matching the
files actually present, e.g. ``OANDA_XAUUSD_M15.csv``) with columns ``time,open,high,low,close,volume``
(``time`` = UTC epoch seconds of the bar's OPEN). No prior "Replay Data Source" file convention exists
in this repo to mirror -- this is new, disclosed code.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ai_trader.market_scanner.scanner import MarketScanner
from ai_trader.market_scanner.timeframes import timeframe_seconds
from ai_trader.market_scanner.types import RawBar
from ai_trader.simulation.exceptions import DataLoadError
from ai_trader.simulation.types import Bar

#: Higher timeframes must be ingested at/before a base bar closing at the same timestamp
#: (``MarketScanner.ingest_bar`` docstring, architecture §9) -- descending size order guarantees that.
_TIMEFRAME_INGEST_ORDER = ("D1", "H4", "H1", "M15")


def _csv_path(data_dir: Path, provider: str, symbol: str, timeframe: str) -> Path:
    return data_dir / f"{provider}_{symbol}_{timeframe}.csv"


def _load_raw_bars(path: Path, symbol: str, timeframe: str) -> list[RawBar]:
    if not path.exists():
        raise DataLoadError(f"Replay data file not found: {path}")
    tf_seconds = timeframe_seconds(timeframe)
    bars: list[RawBar] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts_open = int(row["time"])
            bars.append(RawBar(
                symbol=symbol, timeframe=timeframe, ts_open=ts_open, ts_close=ts_open + tf_seconds,
                open=float(row["open"]), high=float(row["high"]), low=float(row["low"]),
                close=float(row["close"]), volume=float(row["volume"]) if row.get("volume") else None,
                complete=True,
            ))
    bars.sort(key=lambda b: b.ts_open)
    return bars


class ReplayDataSource:
    """Loads and serves historical bars for one run's ``symbols``/``timeframes``, in a fixed, lookahead-
    safe ingestion order. All data is loaded once at construction (bounded, read-only historical
    files -- no unbounded growth, ``SIMULATION_ARCHITECTURE.md`` §9)."""

    def __init__(
        self, symbols: tuple[str, ...], timeframes: tuple[str, ...], base_timeframe: str,
        data_dir: Path, provider: str = "OANDA",
    ) -> None:
        self.base_timeframe = base_timeframe
        self._bars_by_symbol_tf: dict[tuple[str, str], list[RawBar]] = {}
        for symbol in symbols:
            for tf in timeframes:
                self._bars_by_symbol_tf[(symbol, tf)] = _load_raw_bars(
                    _csv_path(data_dir, provider, symbol, tf), symbol, tf
                )
        self._symbols = symbols
        self._timeframes = tuple(tf for tf in _TIMEFRAME_INGEST_ORDER if tf in timeframes)
        self._next_index: dict[tuple[str, str], int] = {(s, tf): 0 for s in symbols for tf in timeframes}
        #: O(1) base-bar lookup by (symbol, ts_close) -- built once, avoiding an O(n) scan per replayed
        #: bar (``SIMULATION_HANDOFF.md`` §12: a multi-year replay is exactly the hot loop where a
        #: linear per-tick scan would be a measured bottleneck).
        self._base_bar_index: dict[tuple[str, int], Bar] = {
            (raw.symbol, raw.ts_close): Bar(
                symbol=raw.symbol, timeframe=raw.timeframe, ts_open=raw.ts_open, ts_close=raw.ts_close,
                open=raw.open, high=raw.high, low=raw.low, close=raw.close, volume=raw.volume,
            )
            for symbol in symbols
            for raw in self._bars_by_symbol_tf.get((symbol, base_timeframe), [])
        }

    def base_ticks_in_range(self, start: int, end: int, warmup_bars: int) -> tuple[int, ...]:
        """The sorted, deduplicated set of base-timeframe ``ts_close`` values across every configured
        symbol, extended ``warmup_bars`` bars before ``start`` (or as many as exist), capped at ``end``.
        Drives the Replay Clock -- ``warmup_ticks`` is the count of ticks strictly before ``start``.
        """
        all_close: set[int] = set()
        for symbol in self._symbols:
            for raw in self._bars_by_symbol_tf.get((symbol, self.base_timeframe), []):
                if raw.ts_close <= end:
                    all_close.add(raw.ts_close)
        ticks = sorted(all_close)
        start_idx = 0
        for i, ts in enumerate(ticks):
            if ts >= start:
                start_idx = i
                break
        else:
            start_idx = len(ticks)
        warmup_start_idx = max(0, start_idx - warmup_bars)
        return tuple(ticks[warmup_start_idx:])

    def feed_up_to(self, scanner: MarketScanner, as_of: int) -> None:
        """Ingest every not-yet-ingested bar (any configured timeframe, any symbol) whose
        ``ts_close <= as_of``, in a fixed cross-timeframe order (``_TIMEFRAME_INGEST_ORDER``) so a
        higher-timeframe bar closing at the same timestamp as a base bar is always ingested first."""
        for tf in self._timeframes:
            for symbol in self._symbols:
                key = (symbol, tf)
                bars = self._bars_by_symbol_tf.get(key, [])
                idx = self._next_index[key]
                while idx < len(bars) and bars[idx].ts_close <= as_of:
                    scanner.ingest_bar(bars[idx])
                    idx += 1
                self._next_index[key] = idx

    def base_bars_at(self, as_of: int) -> dict[str, Bar]:
        """The base-timeframe ``Bar`` (for the Execution Simulator / Portfolio Simulator) whose
        ``ts_close == as_of``, per symbol -- absent for a symbol with no bar at exactly this tick."""
        out: dict[str, Bar] = {}
        for symbol in self._symbols:
            bar = self._base_bar_index.get((symbol, as_of))
            if bar is not None:
                out[symbol] = bar
        return out
