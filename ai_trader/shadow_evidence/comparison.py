"""Strategy comparison/ranking utilities -- Phase 6.10 Implementation Checkpoint 4. Pure, deterministic
functions over :class:`~ai_trader.shadow_evidence.research.StrategyResearchSummary` objects.

**Scope discipline**: every ranking here sorts by exactly ONE already-computed, named metric at a
time -- never a weighted composite across metrics. That is Strategy Health's own separate, unselected
scoring methodology (percentile rank + Bühlmann shrinkage + PCA-derived weights,
`PHASE_6_10_SHADOW_EVIDENCE_ARCHITECTURE_DESIGN.md` §11) -- untouched, unreferenced, out of scope for
this purely descriptive layer. Ties are broken by ``strategy_id`` (ascending) so every ranking/
leaderboard is byte-identical across repeated calls on the identical input, satisfying "rankings are
deterministic" without relying on Python dict/sort implementation details alone.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass

from ai_trader.shadow_evidence.research import StrategyResearchSummary

#: metric name -> pure extractor function. The single source of truth for "every metric" (Checkpoint
#: 4's own "rank by every metric" requirement) -- adding a new metric here is the only change needed
#: for it to appear in rankings/comparisons/leaderboards, never a duplicated switch statement.
_METRIC_EXTRACTORS: dict[str, Callable[[StrategyResearchSummary], float | None]] = {
    "total_trades": lambda s: float(s.window_metrics.n_trades),
    "win_rate": lambda s: s.window_metrics.win_rate,
    "profit_factor": lambda s: s.window_metrics.profit_factor,
    "expectancy_r": lambda s: s.window_metrics.expectancy_r,
    "average_r": lambda s: s.average_r,
    "net_pnl": lambda s: s.window_metrics.net_pnl,
    "max_drawdown": lambda s: s.window_metrics.max_drawdown,
    "sharpe_ratio": lambda s: s.sharpe_ratio,
    "avg_holding_bars": lambda s: s.window_metrics.avg_holding_bars,
    "max_consecutive_wins": lambda s: float(s.max_consecutive_wins),
    "max_consecutive_losses": lambda s: float(s.window_metrics.max_losing_streak),
    "long_net_pnl": lambda s: s.long.net_pnl,
    "short_net_pnl": lambda s: s.short.net_pnl,
}


def available_metrics() -> tuple[str, ...]:
    """Every metric name usable with :func:`rank_by`/:func:`leaderboard`, sorted for a stable,
    deterministic listing."""
    return tuple(sorted(_METRIC_EXTRACTORS))


def _metric_value(summary: StrategyResearchSummary, metric: str) -> float | None:
    if metric not in _METRIC_EXTRACTORS:
        raise ValueError(f"unknown metric {metric!r}; available: {available_metrics()}")
    return _METRIC_EXTRACTORS[metric](summary)


def rank_by(
    summaries: Mapping[str, StrategyResearchSummary], metric: str, descending: bool = True,
) -> list[tuple[str, float | None]]:
    """Every strategy in ``summaries``, sorted by one named metric. Strategies with no evidence for
    this metric (``None``) always sort LAST, regardless of ``descending`` -- "no evidence" must never
    outrank "evidence," in either direction. Ties (equal metric value, or both ``None``) break by
    ``strategy_id`` ascending -- deterministic across repeated calls on the identical input."""
    rows = [(strategy_id, _metric_value(summary, metric)) for strategy_id, summary in summaries.items()]

    def _sort_key(row: tuple[str, float | None]) -> tuple[bool, float, str]:
        strategy_id, value = row
        if value is None:
            return (True, 0.0, strategy_id)
        ordered_value = -value if descending else value
        return (False, ordered_value, strategy_id)

    return sorted(rows, key=_sort_key)


@dataclass(frozen=True, slots=True)
class ComparisonRow:
    """One metric's own side-by-side comparison between two strategies."""

    metric: str
    value_a: float | None
    value_b: float | None
    difference: float | None  # value_a - value_b; None if either value is None


@dataclass(frozen=True, slots=True)
class StrategyComparison:
    """A complete, deterministic, metric-by-metric comparison of exactly two strategies -- Checkpoint
    4's own "compare any two strategies" requirement. ``rows`` is always in ``available_metrics()``'s
    own sorted order, never dependent on dict iteration order."""

    strategy_a: str
    strategy_b: str
    rows: tuple[ComparisonRow, ...]


def compare(summary_a: StrategyResearchSummary, summary_b: StrategyResearchSummary) -> StrategyComparison:
    rows = []
    for metric in available_metrics():
        value_a = _metric_value(summary_a, metric)
        value_b = _metric_value(summary_b, metric)
        difference = (value_a - value_b) if value_a is not None and value_b is not None else None
        rows.append(ComparisonRow(metric=metric, value_a=value_a, value_b=value_b, difference=difference))
    return StrategyComparison(strategy_a=summary_a.strategy_id, strategy_b=summary_b.strategy_id, rows=tuple(rows))


def export_summary(summary: StrategyResearchSummary) -> dict[str, object]:
    """A complete, plain-dict export of one strategy's research summary -- Checkpoint 4's own "export
    complete strategy summaries" requirement. A thin wrapper over ``dataclasses.asdict`` (nested
    dataclasses, e.g. ``window_metrics``/``long``/``short``, are recursively expanded automatically) --
    no new serialization logic."""
    return asdict(summary)


def leaderboard(
    summaries: Mapping[str, StrategyResearchSummary], primary_metric: str = "net_pnl", descending: bool = True,
) -> list[dict[str, object]]:
    """A global leaderboard: every strategy, ranked by ``primary_metric``, with every OTHER available
    metric attached to each row too (Checkpoint 4's own "global leaderboard" requirement) -- a single,
    deterministic table, not just one metric's own ranking in isolation."""
    ranked = rank_by(summaries, primary_metric, descending=descending)
    return [
        {
            "rank": position + 1, "strategy_id": strategy_id,
            **{metric: _metric_value(summaries[strategy_id], metric) for metric in available_metrics()},
        }
        for position, (strategy_id, _value) in enumerate(ranked)
    ]
