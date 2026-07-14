"""Streaming (O(1)-ish, incremental) technical indicators shared by every timeframe.

One :class:`StreamingIndicatorEngine` instance is kept per (symbol, timeframe) that needs the
standardized indicator subset — the M15 base timeframe (full feature namespace, see
``features.py``) and each higher-context timeframe (H1/H4/D1, which only expose
``trend_up``/``volrank``/``rsi`` per ``MARKET_SCANNER_ARCHITECTURE.md`` §4.5).

Design note — parity vs streaming (architecture §10): these formulas mirror the frozen research
engine's ATR / RSI / SMA / STD / Parkinson-volatility-rank windows exactly (same window lengths,
same "any-missing-value blocks the window" semantics as pandas ``rolling(...).mean()``). EMA20/
EMA50 use the standard recursive exponential-moving-average recursion (``adjust=False`` form)
rather than pandas' default ``adjust=True`` (full-history-reweighted) form; the two are
numerically identical once warmed up and differ only in the first ``span`` bars. RSI uses the
textbook Wilder seed (a simple mean of the first ``RSI_WINDOW`` deltas) rather than pandas'
single-observation EWM seed; both apply the identical Wilder smoothing constant afterwards. Both
divergences are deliberate, documented engineering choices — full byte-for-byte conformance against
the frozen research engine is an explicit, separate, future task (architecture §10: "owed at build
time, not here"). This module contains no import of, or dependency on, Research Lab code.

Every computation here is a pure function of the bars fed to :meth:`StreamingIndicatorEngine.update`
in order — no wall-clock, no randomness, no hidden global state (determinism, architecture §4.6).
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from ai_trader.market_scanner.config import (
    ATR_MA_WINDOW,
    ATR_WINDOW,
    EMA_FAST_SPAN,
    EMA_SLOW_SPAN,
    RSI_WINDOW,
    SMA_WINDOW,
    STD_WINDOW,
    VOLRANK_WINDOW,
)


@dataclass(slots=True, frozen=True)
class IndicatorSnapshot:
    """The indicator values available *after* processing one bar close.

    Every field is ``None`` until its own warmup window has been satisfied — the scanner never
    fabricates an early, low-confidence reading (see module docstring; mirrors the "never invent"
    policy of ``MARKET_SCANNER_ARCHITECTURE.md`` §8).
    """

    atr: float | None
    atr_ma: float | None
    compress: bool | None
    ema_fast: float | None
    ema_slow: float | None
    trend_up: bool | None
    rsi: float | None
    sma: float | None
    std: float | None
    volrank: float | None


class StreamingIndicatorEngine:
    """Incremental ATR / EMA / RSI / SMA / STD / Parkinson-volrank engine for one bar series.

    Feed closed bars, in non-decreasing time order, via :meth:`update`. Each call returns the
    :class:`IndicatorSnapshot` valid as of that bar's close. Memory is O(window) — bounded deques,
    never the full history.
    """

    __slots__ = (
        "_bars_seen",
        "_prev_close",
        "_tr_window",
        "_atr_ma_window",
        "_ema_fast",
        "_ema_slow",
        "_avg_gain",
        "_avg_loss",
        "_seed_gains",
        "_seed_losses",
        "_close_window",
        "_park_window",
        "_pv_window",
        "_last_snapshot",
    )

    def __init__(self) -> None:
        self._bars_seen = 0
        self._prev_close: float | None = None
        self._tr_window: deque[float] = deque(maxlen=ATR_WINDOW)
        self._atr_ma_window: deque[float] = deque(maxlen=ATR_MA_WINDOW)
        self._ema_fast: float | None = None
        self._ema_slow: float | None = None
        self._avg_gain: float | None = None
        self._avg_loss: float | None = None
        self._seed_gains: deque[float] = deque(maxlen=RSI_WINDOW)
        self._seed_losses: deque[float] = deque(maxlen=RSI_WINDOW)
        self._close_window: deque[float] = deque(maxlen=SMA_WINDOW if SMA_WINDOW >= STD_WINDOW else STD_WINDOW)
        self._park_window: deque[float] = deque(maxlen=ATR_WINDOW)
        self._pv_window: deque[float] = deque(maxlen=VOLRANK_WINDOW)
        self._last_snapshot: IndicatorSnapshot | None = None

    def snapshot(self) -> IndicatorSnapshot | None:
        """The most recently computed :class:`IndicatorSnapshot`, or ``None`` before the first
        :meth:`update` call. Does not advance any state — safe to call any number of times."""
        return self._last_snapshot

    def update(self, high: float, low: float, close: float) -> IndicatorSnapshot:
        """Advance the engine by one closed bar and return the resulting snapshot.

        Args:
            high: the bar's high price.
            low: the bar's low price.
            close: the bar's close price.

        Returns:
            The :class:`IndicatorSnapshot` as of this bar's close.
        """
        self._bars_seen += 1

        # ---- True Range / ATR / ATR_MA / compress ----
        if self._prev_close is None:
            true_range: float | None = None  # matches a NaN first-bar True Range (no prior close)
        else:
            true_range = max(
                high - low,
                abs(high - self._prev_close),
                abs(low - self._prev_close),
            )
        atr = self._rolling_mean_with_gap(self._tr_window, true_range, ATR_WINDOW)
        atr_ma = self._rolling_mean_with_gap(self._atr_ma_window, atr, ATR_MA_WINDOW)
        compress: bool | None = None
        if atr is not None and atr_ma is not None:
            compress = bool(atr < 0.8 * atr_ma)

        # ---- EMA20 / EMA50 / trend_up ----
        alpha_fast = 2.0 / (EMA_FAST_SPAN + 1)
        alpha_slow = 2.0 / (EMA_SLOW_SPAN + 1)
        self._ema_fast = close if self._ema_fast is None else (alpha_fast * close + (1 - alpha_fast) * self._ema_fast)
        self._ema_slow = close if self._ema_slow is None else (alpha_slow * close + (1 - alpha_slow) * self._ema_slow)
        ema_fast_out = self._ema_fast if self._bars_seen >= EMA_FAST_SPAN else None
        ema_slow_out = self._ema_slow if self._bars_seen >= EMA_SLOW_SPAN else None
        trend_up = None if ema_fast_out is None or ema_slow_out is None else bool(ema_fast_out > ema_slow_out)

        # ---- RSI(14), Wilder-seeded ----
        rsi = self._update_rsi(close)

        # ---- SMA(20) / STD(20) ----
        self._close_window.append(close)
        sma = self._sma(SMA_WINDOW)
        std = self._std(STD_WINDOW, sma_window=SMA_WINDOW)

        # ---- Parkinson volatility + 60-bar rank ----
        volrank = self._update_volrank(high, low)

        self._prev_close = close
        snap = IndicatorSnapshot(
            atr=atr,
            atr_ma=atr_ma,
            compress=compress,
            ema_fast=ema_fast_out,
            ema_slow=ema_slow_out,
            trend_up=trend_up,
            rsi=rsi,
            sma=sma if self._bars_seen >= SMA_WINDOW else None,
            std=std if self._bars_seen >= STD_WINDOW else None,
            volrank=volrank,
        )
        self._last_snapshot = snap
        return snap

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _rolling_mean_with_gap(window: deque[float], new_value: float | None, size: int) -> float | None:
        """Append ``new_value`` to ``window`` (bounded to ``size``) and return the mean, or
        ``None`` if the window is not yet full or contains a ``None`` (mirrors pandas
        ``rolling(size).mean()`` with its default ``min_periods=size`` and NaN-propagation)."""
        window.append(new_value)  # type: ignore[arg-type]
        if len(window) < size:
            return None
        if any(v is None for v in window):
            return None
        return sum(window) / size

    def _update_rsi(self, close: float) -> float | None:
        if self._prev_close is None:
            return None
        delta = close - self._prev_close
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        if self._avg_gain is None:
            self._seed_gains.append(gain)
            self._seed_losses.append(loss)
            if len(self._seed_gains) < RSI_WINDOW:
                return None
            self._avg_gain = sum(self._seed_gains) / RSI_WINDOW
            self._avg_loss = sum(self._seed_losses) / RSI_WINDOW
        else:
            self._avg_gain = (self._avg_gain * (RSI_WINDOW - 1) + gain) / RSI_WINDOW
            self._avg_loss = (self._avg_loss * (RSI_WINDOW - 1) + loss) / RSI_WINDOW  # type: ignore[operator]
        if self._avg_loss == 0:
            return 100.0
        rs = self._avg_gain / self._avg_loss
        return 100.0 - 100.0 / (1.0 + rs)

    def _sma(self, size: int) -> float | None:
        if len(self._close_window) < size:
            return None
        tail = list(self._close_window)[-size:]
        return sum(tail) / size

    def _std(self, size: int, sma_window: int) -> float | None:
        if len(self._close_window) < size:
            return None
        tail = list(self._close_window)[-size:]
        mean = sum(tail) / size
        variance = sum((x - mean) ** 2 for x in tail) / (size - 1) if size > 1 else 0.0
        return math.sqrt(variance)

    def _update_volrank(self, high: float, low: float) -> float | None:
        park = math.log(high / low) ** 2 / (4.0 * math.log(2.0)) if high > 0 and low > 0 else 0.0
        self._park_window.append(park)
        if len(self._park_window) < ATR_WINDOW:
            return None
        pv = math.sqrt(sum(self._park_window) / ATR_WINDOW)
        self._pv_window.append(pv)
        if len(self._pv_window) < VOLRANK_WINDOW:
            return None
        prior = list(self._pv_window)[:-1]
        current = self._pv_window[-1]
        return sum(1 for p in prior if p < current) / len(prior)
