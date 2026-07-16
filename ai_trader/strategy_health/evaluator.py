"""Top-level orchestrator: given every strategy's own closed-trade history and an ``as_of``
timestamp, produce one :class:`StrategyHealthReport` per strategy id. Designed to be called
repeatedly (the CEO's own stated "Future Direction": periodic re-evaluation) -- every call recomputes
everything from scratch from the trades passed in; nothing is cached or carried over between calls.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ai_trader.strategy_health.classifier import classify
from ai_trader.strategy_health.metrics import compute_window_metrics
from ai_trader.strategy_health.scoring import combine_windows, score_window
from ai_trader.strategy_health.types import ClosedTrade, StrategyHealthReport, WindowMetrics, WindowScore

WINDOWS: tuple[str, ...] = ("3m", "6m", "12m")


def _rationale(strategy_id: str, overall: float | None, trend: float | None, reason: str) -> str:
    parts = [f"{strategy_id}: {reason}."]
    if trend is not None:
        parts.append(f"3m-vs-12m trend delta: {trend:+.1f}.")
    if overall is None:
        parts.append("No trades in the 3/6/12-month windows -- nothing to score.")
    return " ".join(parts)


def evaluate_strategy_health(
    trades_by_strategy: Mapping[str, Sequence[ClosedTrade]], as_of: int,
) -> dict[str, StrategyHealthReport]:
    """Evaluate every strategy id present in ``trades_by_strategy`` (including ids with an empty
    trade list -- they still get a report, classified WATCHLIST for lack of evidence)."""
    strategy_ids = list(trades_by_strategy)

    metrics_by_window: dict[str, dict[str, WindowMetrics]] = {
        window: {
            sid: compute_window_metrics(trades_by_strategy[sid], window, as_of) for sid in strategy_ids
        }
        for window in WINDOWS
    }

    reports: dict[str, StrategyHealthReport] = {}
    for sid in strategy_ids:
        window_metrics = {window: metrics_by_window[window][sid] for window in WINDOWS}
        window_scores: dict[str, WindowScore] = {}
        for window in WINDOWS:
            own = metrics_by_window[window][sid]
            population = [m for m in metrics_by_window[window].values() if m.n_trades > 0]
            window_scores[window] = score_window(own, population)

        overall, trend = combine_windows(window_scores)
        state, reason = classify(overall, trend)

        reports[sid] = StrategyHealthReport(
            strategy_id=sid, as_of=as_of, window_metrics=window_metrics, window_scores=window_scores,
            overall_score=overall, trend_delta=trend, state=state,
            rationale=_rationale(sid, overall, trend, reason),
        )
    return reports
