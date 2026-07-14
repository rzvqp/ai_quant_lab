"""Feature Provider — the standardized, versioned M15 feature namespace
(``MARKET_SCANNER_ARCHITECTURE.md`` §4.5 / §10 parity requirement).

Computes, per symbol, exactly the flat feature names the frozen research engine exposes on its M15
frame (transcribed from ``code/mstrat.py:load``, ``code/s1.py:load_s1``, ``code/mtf.py:load_mtf`` —
read for reference only; this module imports none of that code, per the separation law):

``m_atr, m_ema20, m_ema50, m_rsi, m_sma, m_std, m_volrank, m_trend_up`` (M15-native indicators),
``atr_ma, compress`` (volatility regime), ``session, blk, bar_in_sess`` (session bookkeeping,
duplicated here for strategies that reference them as flat fields), ``rmax20, rmin20, rmax50,
rmin50`` (trailing swing extremes), ``sess_high, sess_low`` (developing session range),
``pdh, pdl, pd_open, pd_close, pd_mid`` (previous-day levels), ``pw_high, pw_low`` (previous-week
levels), ``or_high, or_low`` (opening range — see :mod:`~ai_trader.market_scanner.session` for the
lookahead-safe "formed" gating), ``prev_sess_high, prev_sess_low, prev_sess_close`` (previous
session), ``vwap, gap`` (session VWAP / session-open gap), ``fvg_bull, fvg_bear, disp, roc3,
bear_close, bull_close`` (bar-pattern primitives), and ``h4_trend_up, h4_volrank, h4_rsi,
h1_trend_up, h1_volrank, h1_rsi, d1_trend_up, d1_volrank, d1_rsi`` (higher-timeframe context, each
computed by its own :class:`~ai_trader.market_scanner.indicators.StreamingIndicatorEngine` instance
updated only at that timeframe's own bar closes — lookahead-safe by construction, architecture §9).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime

from ai_trader.market_scanner.calendar_engine import CalendarEngine, CalendarSnapshot
from ai_trader.market_scanner.config import DISPLACEMENT_ATR_MULT
from ai_trader.market_scanner.indicators import StreamingIndicatorEngine
from ai_trader.market_scanner.session import SessionEngine, SessionSnapshot
from ai_trader.market_scanner.types import RawBar

#: Trailing swing-extreme windows the Strategy Library's grammars reference (rmax20/rmin20/rmax50/rmin50).
SWING_WINDOWS: tuple[int, ...] = (20, 50)

#: The complete, versioned M15 flat feature namespace this module guarantees to populate (a key is
#: always present in the returned dict; its value is ``None`` until warmed up).
M15_FEATURE_NAMES: frozenset[str] = frozenset(
    {
        "m_atr", "m_ema20", "m_ema50", "m_rsi", "m_sma", "m_std", "m_volrank", "m_trend_up",
        "atr_ma", "compress",
        "session", "blk", "bar_in_sess",
        "rmax20", "rmin20", "rmax50", "rmin50",
        "sess_high", "sess_low",
        "pdh", "pdl", "pd_open", "pd_close", "pd_mid",
        "pw_high", "pw_low",
        "or_high", "or_low",
        "prev_sess_high", "prev_sess_low", "prev_sess_close",
        "vwap", "gap",
        "fvg_bull", "fvg_bear", "disp", "roc3", "bear_close", "bull_close",
        "h4_trend_up", "h4_volrank", "h4_rsi",
        "h1_trend_up", "h1_volrank", "h1_rsi",
        "d1_trend_up", "d1_volrank", "d1_rsi",
    }
)

#: Context timeframes whose own trend/volrank/rsi are folded into the M15 namespace under a prefix.
_HTF_PREFIXES: dict[str, str] = {"H1": "h1_", "H4": "h4_", "D1": "d1_"}


class TrailingExtreme:
    """Rolling max or min of the ``window`` bars STRICTLY BEFORE the current one (mirrors pandas
    ``rolling(window).max().shift(1)`` / ``.min().shift(1)`` — the current bar is never included).
    """

    __slots__ = ("_window", "_values", "_is_max")

    def __init__(self, window: int, is_max: bool) -> None:
        self._window = window
        self._values: deque[float] = deque(maxlen=window)
        self._is_max = is_max

    def update(self, value: float) -> float | None:
        """Return the trailing extreme (excluding ``value``), then fold ``value`` in."""
        result: float | None = None
        if len(self._values) == self._window:
            result = max(self._values) if self._is_max else min(self._values)
        self._values.append(value)
        return result


class WeeklyAggregator:
    """Tracks the previous COMPLETED ISO-calendar-week's D1 high/low, fed by D1 bar closes."""

    __slots__ = ("_current_week", "_current_high", "_current_low", "_prev_high", "_prev_low")

    def __init__(self) -> None:
        self._current_week: tuple[int, int] | None = None
        self._current_high: float | None = None
        self._current_low: float | None = None
        self._prev_high: float | None = None
        self._prev_low: float | None = None

    @property
    def prev_week_high(self) -> float | None:
        return self._prev_high

    @property
    def prev_week_low(self) -> float | None:
        return self._prev_low

    def update(self, d1_bar: RawBar) -> None:
        iso = datetime.fromtimestamp(d1_bar.ts_open, tz=UTC).isocalendar()
        week_key = (iso.year, iso.week)
        if self._current_week is None:
            self._current_week = week_key
            self._current_high = d1_bar.high
            self._current_low = d1_bar.low
            return
        if week_key != self._current_week:
            self._prev_high = self._current_high
            self._prev_low = self._current_low
            self._current_week = week_key
            self._current_high = d1_bar.high
            self._current_low = d1_bar.low
        else:
            self._current_high = d1_bar.high if self._current_high is None else max(self._current_high, d1_bar.high)
            self._current_low = d1_bar.low if self._current_low is None else min(self._current_low, d1_bar.low)


@dataclass(slots=True)
class BaseCloseResult:
    """Everything produced by folding in one closed base (M15) bar."""

    session: SessionSnapshot
    calendar: CalendarSnapshot
    features: dict[str, float | bool | str | int | None]


class FeatureProvider:
    """Per-symbol feature computation: session/calendar bookkeeping + the full M15 namespace."""

    __slots__ = (
        "session_engine",
        "calendar_engine",
        "_m15_indicators",
        "_htf_indicators",
        "_weekly_agg",
        "_swing_high",
        "_swing_low",
        "_fvg_high2",
        "_fvg_low2",
        "_roc_close3",
        "_event_flag_window_seconds",
    )

    def __init__(self, context_timeframes: frozenset[str], event_flag_window_seconds: int) -> None:
        self.session_engine = SessionEngine()
        self.calendar_engine = CalendarEngine()
        self._m15_indicators = StreamingIndicatorEngine()
        self._htf_indicators: dict[str, StreamingIndicatorEngine] = {
            tf: StreamingIndicatorEngine() for tf in context_timeframes if tf in _HTF_PREFIXES
        }
        self._weekly_agg = WeeklyAggregator()
        self._swing_high = {w: TrailingExtreme(w, is_max=True) for w in SWING_WINDOWS}
        self._swing_low = {w: TrailingExtreme(w, is_max=False) for w in SWING_WINDOWS}
        self._fvg_high2: deque[float] = deque(maxlen=2)
        self._fvg_low2: deque[float] = deque(maxlen=2)
        self._roc_close3: deque[float] = deque(maxlen=3)
        self._event_flag_window_seconds = event_flag_window_seconds

    def htf_feature_snapshot(self, timeframe: str) -> dict[str, float | bool | None]:
        """The minimal ``{trend_up, volrank, rsi}`` snapshot for one context timeframe's own
        ``TimeframeContext.features`` entry (mirrors exactly what the research engine's
        ``_htf_feat`` forwards for H1/H4/D1 — no extra, strategy-specific computation)."""
        engine = self._htf_indicators.get(timeframe)
        snap = engine.snapshot() if engine is not None else None
        return {
            "trend_up": snap.trend_up if snap else None,
            "volrank": snap.volrank if snap else None,
            "rsi": snap.rsi if snap else None,
        }

    def on_context_close(self, timeframe: str, bar: RawBar) -> None:
        """Feed a newly-closed higher-context-timeframe bar (H1/H4/D1/W1)."""
        engine = self._htf_indicators.get(timeframe)
        if engine is not None:
            engine.update(bar.high, bar.low, bar.close)
        if timeframe == "D1":
            self._weekly_agg.update(bar)

    def on_base_close(self, bar: RawBar, latest_d1_bar: RawBar | None) -> BaseCloseResult:
        """Feed a newly-closed base (M15) bar and return the session/calendar snapshots plus the
        complete, versioned M15 feature dict.

        Args:
            bar: the closed base-timeframe bar.
            latest_d1_bar: the last D1 bar whose ``available_at <= as_of`` (selected by the caller
                via :mod:`~ai_trader.market_scanner.timeframe_sync`), or ``None`` if none is
                available yet — used for ``pdh/pdl/pd_open/pd_close/pd_mid``.
        """
        session = self.session_engine.update(bar.ts_open, bar.high, bar.low, bar.close, bar.volume)
        calendar = self.calendar_engine.update(bar.ts_open, self._event_flag_window_seconds)

        ind = self._m15_indicators.update(bar.high, bar.low, bar.close)

        rmax20 = self._swing_high[20].update(bar.high)
        rmin20 = self._swing_low[20].update(bar.low)
        rmax50 = self._swing_high[50].update(bar.high)
        rmin50 = self._swing_low[50].update(bar.low)

        fvg_bull: bool | None = None
        fvg_bear: bool | None = None
        if len(self._fvg_high2) == 2:
            two_ago_high = self._fvg_high2[0]
            two_ago_low = self._fvg_low2[0]
            fvg_bull = bar.low > two_ago_high
            fvg_bear = bar.high < two_ago_low
        self._fvg_high2.append(bar.high)
        self._fvg_low2.append(bar.low)

        roc3: float | None = None
        if len(self._roc_close3) == 3:
            close_3_ago = self._roc_close3[0]
            roc3 = (bar.close / close_3_ago - 1.0) if close_3_ago != 0 else None
        self._roc_close3.append(bar.close)

        disp: bool | None = None
        if ind.atr is not None:
            disp = (bar.high - bar.low) > DISPLACEMENT_ATR_MULT * ind.atr

        pdh = pdl = pd_open = pd_close = pd_mid = None
        if latest_d1_bar is not None:
            pdh, pdl = latest_d1_bar.high, latest_d1_bar.low
            pd_open, pd_close = latest_d1_bar.open, latest_d1_bar.close
            pd_mid = (pdh + pdl) / 2.0

        gap: float | None = None
        if session.bar_in_session == 0 and session.prev_session_close is not None:
            gap = bar.open - session.prev_session_close

        features: dict[str, float | bool | str | int | None] = {
            "m_atr": ind.atr, "m_ema20": ind.ema_fast, "m_ema50": ind.ema_slow, "m_rsi": ind.rsi,
            "m_sma": ind.sma, "m_std": ind.std, "m_volrank": ind.volrank, "m_trend_up": ind.trend_up,
            "atr_ma": ind.atr_ma, "compress": ind.compress,
            "session": session.name.value, "blk": session.block_id, "bar_in_sess": session.bar_in_session,
            "rmax20": rmax20, "rmin20": rmin20, "rmax50": rmax50, "rmin50": rmin50,
            "sess_high": session.session_high, "sess_low": session.session_low,
            "pdh": pdh, "pdl": pdl, "pd_open": pd_open, "pd_close": pd_close, "pd_mid": pd_mid,
            "pw_high": self._weekly_agg.prev_week_high, "pw_low": self._weekly_agg.prev_week_low,
            "or_high": session.opening_range.high, "or_low": session.opening_range.low,
            "prev_sess_high": session.prev_session_high, "prev_sess_low": session.prev_session_low,
            "prev_sess_close": session.prev_session_close,
            "vwap": session.vwap, "gap": gap,
            "fvg_bull": fvg_bull, "fvg_bear": fvg_bear, "disp": disp, "roc3": roc3,
            "bear_close": bar.close < bar.open, "bull_close": bar.close > bar.open,
        }
        for tf, prefix in _HTF_PREFIXES.items():
            engine = self._htf_indicators.get(tf)
            snap = engine.snapshot() if engine is not None else None
            features[f"{prefix}trend_up"] = snap.trend_up if snap else None
            features[f"{prefix}volrank"] = snap.volrank if snap else None
            features[f"{prefix}rsi"] = snap.rsi if snap else None

        assert set(features) == M15_FEATURE_NAMES, "feature namespace drift detected"
        return BaseCloseResult(session=session, calendar=calendar, features=features)
