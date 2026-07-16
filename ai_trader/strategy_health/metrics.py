"""Per-rolling-window metric computation -- pure functions over a strategy's own closed trades.
Every metric the CEO asked for (``expectancy``, ``profit factor``, ``net R``, ``win rate``,
``drawdown``, ``number of trades``, ``monthly consistency``, ``equity stability``, ``maximum losing
streak``, ``average R per trade``, ``average holding time``) is computed here, from real trade data
only -- nothing estimated, nothing carried over from a different window.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime

from ai_trader.strategy_health.types import WINDOW_DAYS, ClosedTrade, WindowMetrics

_SECONDS_PER_DAY = 86400


def _month_key(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m")


def trades_in_window(trades: Sequence[ClosedTrade], window: str, as_of: int) -> list[ClosedTrade]:
    """Trades whose own ``exit_as_of`` falls within ``[as_of - window_days, as_of]`` (inclusive) --
    the trade's CLOSE is what counts as "this window's own evidence" (an entry from before the
    window that is still open, or that closed after ``as_of``, tells us nothing about performance
    realized inside the window)."""
    span = WINDOW_DAYS[window] * _SECONDS_PER_DAY
    start = as_of - span
    return [t for t in trades if t.strategy_id and start <= t.exit_as_of <= as_of]


def _max_losing_streak(ordered: Sequence[ClosedTrade]) -> int:
    longest = current = 0
    for t in ordered:
        if t.net_pnl <= 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _isolated_max_drawdown(ordered: Sequence[ClosedTrade]) -> float:
    """Peak-to-trough of THIS strategy's own cumulative net-PnL curve, in its own trades' exit
    order -- a proxy (real drawdown is shared across the whole portfolio's one capital account), not
    a portfolio-attributed number; documented at every call site that surfaces it."""
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for t in ordered:
        cum += t.net_pnl
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
    return max_dd


def compute_window_metrics(trades: Sequence[ClosedTrade], window: str, as_of: int) -> WindowMetrics:
    """Compute every metric for one rolling window. Returns a ``WindowMetrics`` with ``n_trades=0``
    and every other field ``None``/``0.0`` when the strategy has no trades in this window -- the
    caller (``scoring.py``) is responsible for treating a zero-trade window as "no evidence", not
    this function fabricating a neutral-looking result."""
    windowed = sorted(trades_in_window(trades, window, as_of), key=lambda t: t.exit_as_of)
    n = len(windowed)
    if n == 0:
        return WindowMetrics(
            window=window, as_of=as_of, n_trades=0, win_rate=None, profit_factor=None,
            expectancy_currency=None, expectancy_r=None, net_r=None, net_pnl=0.0, max_drawdown=0.0,
            monthly_consistency=None, equity_stability=None, max_losing_streak=0, avg_holding_bars=None,
        )

    wins = [t for t in windowed if t.net_pnl > 0]
    losses = [t for t in windowed if t.net_pnl <= 0]
    win_rate = len(wins) / n
    gross_win = sum(t.net_pnl for t in wins)
    gross_loss = -sum(t.net_pnl for t in losses)
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else None
    net_pnl = sum(t.net_pnl for t in windowed)
    expectancy_currency = net_pnl / n

    r_values = [t.pnl_r for t in windowed if t.pnl_r is not None]
    expectancy_r = (sum(r_values) / len(r_values)) if r_values else None
    net_r = sum(r_values) if r_values else None

    monthly_pnl: dict[str, float] = defaultdict(float)
    for t in windowed:
        monthly_pnl[_month_key(t.exit_as_of)] += t.net_pnl
    months = sorted(monthly_pnl)
    monthly_consistency = (sum(1 for m in months if monthly_pnl[m] > 0) / len(months)) if months else None
    if len(months) >= 2:
        values = [monthly_pnl[m] for m in months]
        stdev = statistics.pstdev(values)
        equity_stability = (statistics.mean(values) / stdev) if stdev > 0 else None
    else:
        equity_stability = None

    holding = [float(t.holding_bars) for t in windowed]
    avg_holding_bars = statistics.mean(holding) if holding else None

    return WindowMetrics(
        window=window, as_of=as_of, n_trades=n, win_rate=win_rate, profit_factor=profit_factor,
        expectancy_currency=expectancy_currency, expectancy_r=expectancy_r, net_r=net_r,
        net_pnl=net_pnl, max_drawdown=_isolated_max_drawdown(windowed),
        monthly_consistency=monthly_consistency, equity_stability=equity_stability,
        max_losing_streak=_max_losing_streak(windowed), avg_holding_bars=avg_holding_bars,
    )
