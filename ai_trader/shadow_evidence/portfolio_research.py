"""Portfolio-level, cross-strategy research -- Phase 6.10 Implementation Checkpoint 4. Purely
descriptive: correlation matrix, trade overlap, simultaneous exposure, diversification aggregates.

**Scope discipline**: no allocation decisions, no optimization, no eigen-decomposition/PCA anywhere in
this module -- PCA-derived weighting is part of Strategy Health's own scoring methodology (Design §11),
deliberately not reused or approximated here. Diversification is reported as simple, transparent
aggregates of the correlation matrix (mean, a disclosed threshold count) -- never a single composite
"diversification score."
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from ai_trader.shadow_evidence.types import ShadowPositionRecord, ShadowTradeLegRecord


def _month_key(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m")


def monthly_pnl_by_strategy(trade_legs: Sequence[ShadowTradeLegRecord]) -> dict[str, dict[str, float]]:
    """Every strategy's own monthly net PnL -- the shared building block for the correlation matrix
    below (and directly inspectable on its own, e.g. for a research report's own monthly-PnL table)."""
    out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for leg in trade_legs:
        out[leg.leg.strategy_id][_month_key(leg.leg.exit_as_of)] += leg.leg.net_pnl
    return {strategy_id: dict(months) for strategy_id, months in out.items()}


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Population Pearson correlation coefficient. ``None`` (never fabricated) with fewer than 2
    common points or zero variance in either series."""
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    stdev_x, stdev_y = statistics.pstdev(xs), statistics.pstdev(ys)
    if stdev_x <= 0 or stdev_y <= 0:
        return None
    mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / len(xs)
    return covariance / (stdev_x * stdev_y)


def correlation_matrix(trade_legs: Sequence[ShadowTradeLegRecord]) -> dict[tuple[str, str], float | None]:
    """Pearson correlation of monthly net PnL between every pair of strategies with at least one
    recorded trade leg -- Checkpoint 4's own "correlation matrix" requirement. Symmetric
    (``matrix[(a, b)] == matrix[(b, a)]``); ``matrix[(a, a)] == 1.0`` always.

    IMPLEMENTATION CHOICE, disclosed: a month in which a strategy recorded zero shadow trades is
    zero-filled (a genuine zero contribution to that month's return), not treated as missing data --
    the union of every month ANY strategy traded in becomes the common timeline every strategy's own
    series is measured against."""
    monthly = monthly_pnl_by_strategy(trade_legs)
    strategy_ids = sorted(monthly)
    all_months = sorted({month for per_strategy in monthly.values() for month in per_strategy})
    series = {
        strategy_id: [monthly[strategy_id].get(month, 0.0) for month in all_months]
        for strategy_id in strategy_ids
    }
    result: dict[tuple[str, str], float | None] = {}
    for i, strategy_a in enumerate(strategy_ids):
        for strategy_b in strategy_ids[i:]:
            correlation = 1.0 if strategy_a == strategy_b else _pearson(series[strategy_a], series[strategy_b])
            result[(strategy_a, strategy_b)] = correlation
            result[(strategy_b, strategy_a)] = correlation
    return result


@dataclass(frozen=True, slots=True)
class OverlapStats:
    """How often two DIFFERENT strategies' own shadow positions were open at overlapping times --
    Checkpoint 4's own "trade overlap statistics" requirement. Counts CLOSED positions only (an
    OPEN position at query time has no fixed end yet to compare against)."""

    strategy_a: str
    strategy_b: str
    n_overlapping_position_pairs: int


def trade_overlap_stats(positions: Sequence[ShadowPositionRecord]) -> tuple[OverlapStats, ...]:
    closed = [p for p in positions if p.status == "CLOSED" and p.full_exit_as_of is not None]
    by_strategy: dict[str, list[ShadowPositionRecord]] = defaultdict(list)
    for position in closed:
        by_strategy[position.strategy_id].append(position)
    strategy_ids = sorted(by_strategy)
    out = []
    for i, strategy_a in enumerate(strategy_ids):
        for strategy_b in strategy_ids[i + 1:]:
            count = sum(
                1
                for pos_a in by_strategy[strategy_a]
                for pos_b in by_strategy[strategy_b]
                if pos_a.entry_as_of <= (pos_b.full_exit_as_of or pos_b.entry_as_of)
                and pos_b.entry_as_of <= (pos_a.full_exit_as_of or pos_a.entry_as_of)
            )
            out.append(OverlapStats(strategy_a=strategy_a, strategy_b=strategy_b, n_overlapping_position_pairs=count))
    return tuple(out)


@dataclass(frozen=True, slots=True)
class ExposureStats:
    """How many DIFFERENT strategies held a shadow position simultaneously, at the busiest moment --
    Checkpoint 4's own "simultaneous exposure" requirement. Computed by a standard sweep-line count
    over every closed position's own ``[entry_as_of, full_exit_as_of]`` interval, entries processed
    before exits at an identical timestamp (an entry and an exit at the same instant are not treated
    as reducing concurrency below what it already was)."""

    max_concurrent_positions: int
    n_strategies_with_any_closed_position: int


def simultaneous_exposure(positions: Sequence[ShadowPositionRecord]) -> ExposureStats:
    closed = [p for p in positions if p.status == "CLOSED" and p.full_exit_as_of is not None]
    events: list[tuple[int, int]] = []
    for position in closed:
        events.append((position.entry_as_of, 1))
        assert position.full_exit_as_of is not None
        events.append((position.full_exit_as_of, -1))
    events.sort(key=lambda event: (event[0], -event[1]))  # opens before closes at an identical timestamp
    concurrent = 0
    max_concurrent = 0
    for _as_of, delta in events:
        concurrent += delta
        max_concurrent = max(max_concurrent, concurrent)
    n_strategies = len({p.strategy_id for p in closed})
    return ExposureStats(max_concurrent_positions=max_concurrent, n_strategies_with_any_closed_position=n_strategies)


@dataclass(frozen=True, slots=True)
class DiversificationStats:
    """Simple, transparent aggregates of the correlation matrix -- Checkpoint 4's own "diversification
    metrics" requirement. Deliberately NOT a single composite "diversification score" -- two disclosed
    descriptive numbers instead."""

    n_strategy_pairs: int
    avg_pairwise_correlation: float | None
    n_pairs_highly_correlated: int  # |correlation| > threshold


def diversification_metrics(
    correlation: dict[tuple[str, str], float | None], threshold: float = 0.7,
) -> DiversificationStats:
    """``threshold`` (default 0.7, a documented, disclosed, conservative "highly correlated" cutoff --
    never tuned against results, matching this codebase's own ``IMPLEMENTATION_CHOICES.md`` convention
    for undocumented numeric defaults) is explicit and overridable, never hidden."""
    pairs = {
        (a, b): value for (a, b), value in correlation.items() if a < b and value is not None
    }
    values = list(pairs.values())
    avg = statistics.mean(values) if values else None
    n_high = sum(1 for value in values if abs(value) > threshold)
    return DiversificationStats(
        n_strategy_pairs=len(pairs), avg_pairwise_correlation=avg, n_pairs_highly_correlated=n_high,
    )
