"""Strategy Research layer -- Phase 6.10 Implementation Checkpoint 4. Pure, read-only functions
producing a per-strategy DESCRIPTIVE research summary from a
:class:`~ai_trader.shadow_evidence.engine.ShadowEvidenceEngine`'s own already-recorded, public data.

**Scope discipline (CEO's own explicit boundary, Checkpoint 4)**: purely descriptive. No scoring, no
classification, no allocation, no optimization, no automatic disabling. Every number here is either
reused verbatim from :mod:`ai_trader.strategy_health.metrics`'s own frozen, unmodified
``compute_window_metrics()`` (total trades, win rate, profit factor, expectancy R, max drawdown,
average holding time, max consecutive losses -- Checkpoint 2's own precedent, extended, not
reinvented), or a new statistic of the SAME simple, transparent, single-number kind (Sharpe ratio,
best/worst month, long-vs-short split, longest winning streak) -- never a weighted composite, never a
percentile rank, never anything from :mod:`ai_trader.strategy_health.scoring`/``classifier``/
``evaluator`` (none of those three modules is imported here, exactly as Checkpoint 2 established for
:mod:`ai_trader.shadow_evidence.aggregation`).
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from ai_trader.shadow_evidence.aggregation import strategy_ids_observed, summary_for
from ai_trader.shadow_evidence.types import ShadowOpportunityRecord, ShadowRejectionRecord, ShadowTradeLegRecord
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import TradeRecord
from ai_trader.strategy_health.types import WINDOW_DAYS, WindowMetrics

_SECONDS_PER_DAY = 86400


def _month_key(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m")


def _trades_in_window(trades: Sequence[TradeRecord], window: str, as_of: int) -> list[TradeRecord]:
    """The same ``[as_of - window_days, as_of]`` rule ``strategy_health.metrics.trades_in_window``
    already uses (reusing its own public ``WINDOW_DAYS`` constant), applied directly to
    :class:`TradeRecord` (which carries ``direction``, unlike the ``ClosedTrade`` shape that function
    itself operates on) -- so every new statistic below is scoped to the SAME rolling window as the
    reused ``WindowMetrics``, not a different, inconsistent one."""
    span = WINDOW_DAYS[window] * _SECONDS_PER_DAY
    start = as_of - span
    return [t for t in trades if start <= t.exit_as_of <= as_of]


@dataclass(frozen=True, slots=True)
class DirectionStats:
    """Trade statistics for one direction only (LONG or SHORT) -- Checkpoint 4's own "Long vs Short"
    requirement. No existing type in this repository carries a direction-aware trade breakdown."""

    n_trades: int
    win_rate: float | None
    net_pnl: float


@dataclass(frozen=True, slots=True)
class StrategyResearchSummary:
    """One strategy's complete, purely descriptive research summary for one rolling window. Every
    field maps directly to one of the CEO's own named Checkpoint 4 metrics -- see the module docstring
    for which are reused verbatim from ``WindowMetrics`` vs. newly computed here:

    - Total trades / Win rate / Profit Factor / Expectancy (R) / Max Drawdown / Average holding time /
      Consecutive losses -> ``window_metrics`` (reused, unmodified computation).
    - Average R -> ``average_r`` (the SAME number as ``window_metrics.expectancy_r`` -- "average R per
      trade" IS this project's own established definition of expectancy-in-R, `strategy_health/
      metrics.py`'s own `expectancy_r` computation; exposed under both names because the CEO asked for
      both explicitly, not because they are two different statistics).
    - Sharpe Ratio / Best month / Worst month / Long vs Short / Consecutive wins -> newly computed
      fields below, genuinely new (no prior repository equivalent)."""

    strategy_id: str
    source: str
    window_metrics: WindowMetrics
    average_r: float | None
    sharpe_ratio: float | None
    best_month: str | None
    best_month_pnl: float | None
    worst_month: str | None
    worst_month_pnl: float | None
    long: DirectionStats
    short: DirectionStats
    max_consecutive_wins: int

    def __post_init__(self) -> None:
        if self.source != "shadow":
            raise ValueError(f"StrategyResearchSummary.source must be 'shadow', got {self.source!r}")
        if self.max_consecutive_wins < 0:
            raise ValueError("StrategyResearchSummary.max_consecutive_wins must be >= 0")


def _sharpe_ratio(r_values: Sequence[float]) -> float | None:
    """A simple, un-annualized Sharpe-style ratio -- mean(R) / population-stdev(R) across this
    strategy's own per-trade R-multiples in the window. IMPLEMENTATION CHOICE (no annualization: no
    established, non-arbitrary trading-periods-per-year convention exists for per-trade R-multiples
    at irregular holding times in this repository) -- documented, not silently assumed. ``None`` (never
    fabricated) with fewer than 2 R-valued trades or zero variance."""
    if len(r_values) < 2:
        return None
    stdev = statistics.pstdev(r_values)
    if stdev <= 0:
        return None
    return statistics.mean(r_values) / stdev


def _best_worst_month(trades: Sequence[TradeRecord]) -> tuple[str | None, float | None, str | None, float | None]:
    monthly: dict[str, float] = defaultdict(float)
    for trade in trades:
        monthly[_month_key(trade.exit_as_of)] += trade.net_pnl
    if not monthly:
        return None, None, None, None
    best = max(monthly, key=lambda m: (monthly[m], m))
    worst = min(monthly, key=lambda m: (monthly[m], m))
    return best, monthly[best], worst, monthly[worst]


def _direction_stats(trades: Sequence[TradeRecord], direction: Direction) -> DirectionStats:
    subset = [t for t in trades if t.direction is direction]
    n = len(subset)
    win_rate = (sum(1 for t in subset if t.net_pnl > 0) / n) if n else None
    return DirectionStats(n_trades=n, win_rate=win_rate, net_pnl=sum(t.net_pnl for t in subset))


def _max_consecutive_wins(ordered_trades: Sequence[TradeRecord]) -> int:
    """Mirrors ``strategy_health.metrics._max_losing_streak``'s own logic exactly, inverted for wins
    -- a new, equally simple function (that one is module-private, so re-derived here rather than
    reaching into another module's private internals)."""
    longest = current = 0
    for trade in ordered_trades:
        if trade.net_pnl > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def research_summary_for(
    strategy_id: str,
    window: str,
    as_of: int,
    opportunities: Sequence[ShadowOpportunityRecord],
    rejections: Sequence[ShadowRejectionRecord],
    trade_legs: Sequence[ShadowTradeLegRecord],
) -> StrategyResearchSummary:
    """One strategy's complete research summary. A strategy with zero trades in the window yields a
    valid, honest summary (every optional field ``None``, matching ``WindowMetrics``'s own "never
    fabricated" convention), never raises."""
    base = summary_for(strategy_id, window, as_of, opportunities, rejections, trade_legs)
    own_trades = sorted(
        (leg.leg for leg in trade_legs if leg.leg.strategy_id == strategy_id),
        key=lambda t: (t.exit_as_of, t.client_order_id),
    )
    windowed_trades = _trades_in_window(own_trades, window, as_of)
    r_values = [t.pnl_r for t in windowed_trades if t.pnl_r is not None]
    best_month, best_month_pnl, worst_month, worst_month_pnl = _best_worst_month(windowed_trades)
    return StrategyResearchSummary(
        strategy_id=strategy_id, source="shadow", window_metrics=base.window_metrics,
        average_r=base.window_metrics.expectancy_r, sharpe_ratio=_sharpe_ratio(r_values),
        best_month=best_month, best_month_pnl=best_month_pnl,
        worst_month=worst_month, worst_month_pnl=worst_month_pnl,
        long=_direction_stats(windowed_trades, Direction.LONG),
        short=_direction_stats(windowed_trades, Direction.SHORT),
        max_consecutive_wins=_max_consecutive_wins(windowed_trades),
    )


def all_research_summaries(
    window: str,
    as_of: int,
    opportunities: Sequence[ShadowOpportunityRecord],
    rejections: Sequence[ShadowRejectionRecord],
    trade_legs: Sequence[ShadowTradeLegRecord],
) -> dict[str, StrategyResearchSummary]:
    """Every currently-tracked strategy's own research summary, keyed by ``strategy_id`` -- generic
    over however many strategies are configured (1 to N, verified at N=43 by this checkpoint's own
    test suite), the strategy-id set derived entirely from the data (:func:`strategy_ids_observed`),
    never hardcoded."""
    return {
        strategy_id: research_summary_for(strategy_id, window, as_of, opportunities, rejections, trade_legs)
        for strategy_id in sorted(strategy_ids_observed(opportunities))
    }
