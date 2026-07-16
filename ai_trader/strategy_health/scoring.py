"""Composite Health Score derivation -- explicitly NOT hand-tuned weights.

**Methodology (justified, not arbitrary):**

1. **Percentile-rank normalization.** Every scored metric is converted to a 0-100 percentile rank
   within the CROSS-SECTION of strategies that have at least one trade in the same window. This is
   scale-free and outlier-robust (unlike z-scores, which a single +21R trade would distort badly --
   exactly the kind of extreme value this system's own real trade history produces, per the Wave D
   audit's own S1 finding) and puts every metric on the same 0-100 footing the final Health Score
   itself uses.
2. **Credibility shrinkage** (Buhlmann-style, a standard actuarial technique for blending a small
   sample's own estimate with a neutral prior): each strategy's percentile is pulled toward the
   neutral midpoint (50) by a factor of `k / (n + k)`, where `n` is this window's own trade count and
   `k` is a fixed reference sample size (`CREDIBILITY_K = 10`, i.e. a strategy needs 10 trades in a
   window before its own evidence outweighs the neutral prior). This stops a single lucky/unlucky
   trade from swinging a strategy to the extreme of the scale.
3. **PCA-derived metric weights** (the actual "not hardcoded" answer): the 8 shrunk percentiles are
   assembled into a strategies x metrics matrix, its covariance matrix's dominant eigenvector is
   computed, and THAT eigenvector -- clipped to non-negative and renormalized to sum to 1 -- becomes
   the metric weight vector. This is the metrics' own first principal component: the linear
   combination that explains the most cross-strategy variance, i.e. the axis metrics MOST AGREE is
   "better." No metric is favored by manual judgment; the weights are a deterministic function of the
   population's own data. Falls back to equal weights only when the population is too small
   (`< MIN_POPULATION_FOR_PCA` strategies) for a covariance matrix to be meaningful -- disclosed, not
   hidden.
4. **Window combination**: 12m/6m/3m window scores are combined with FIXED, CEO-DIRECTED priority
   weights (`WINDOW_PRIORITY`) -- this is a distinct kind of choice from the metric weights above: an
   explicit business rule ("12-month is the primary decision window, shorter windows are supporting
   evidence"), not a discovered pattern, and is documented as such rather than presented as
   data-driven. A missing window's weight is redistributed proportionally among the windows that do
   have data.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from ai_trader.strategy_health.types import WindowMetrics, WindowScore

#: Buhlmann credibility reference sample size: at n=CREDIBILITY_K trades, a strategy's own evidence
#: and the neutral (50th percentile) prior are weighted equally.
CREDIBILITY_K = 10.0

#: Below this many strategies with data in a window, a covariance matrix is too noisy to trust;
#: fall back to equal weights (disclosed, not silently substituted).
MIN_POPULATION_FOR_PCA = 5

#: CEO-directed window-priority weights (a business rule, distinct from the PCA-derived metric
#: weights above) -- 12-month is the PRIMARY decision window; 6/3-month are supporting evidence.
WINDOW_PRIORITY: dict[str, float] = {"12m": 0.60, "6m": 0.25, "3m": 0.15}

#: (metric name, higher_is_better, none_meaning) -- none_meaning is "best" only for profit_factor
#: (None there means zero losing trades this window, unambiguously excellent) and "neutral"
#: everywhere else (None means the metric could not be computed, not that it was bad or good).
_METRIC_SPECS: tuple[tuple[str, bool, str], ...] = (
    ("expectancy_r", True, "neutral"),
    ("profit_factor", True, "best"),
    ("net_r", True, "neutral"),
    ("win_rate", True, "neutral"),
    ("monthly_consistency", True, "neutral"),
    ("equity_stability", True, "neutral"),
    ("max_drawdown", False, "neutral"),
    ("max_losing_streak", False, "neutral"),
)


def _raw_value(m: WindowMetrics, name: str) -> float | None:
    value = getattr(m, name)
    return None if value is None else float(value)


def percentile_rank(value: float | None, population: Sequence[float | None], none_meaning: str) -> float:
    """``value``'s percentile (0-100) within ``population`` (itself may contain ``None`` entries,
    each resolved via its own metric's ``none_meaning`` before ranking). ``None`` values in
    ``population`` are excluded from the comparison set entirely when they carry no informative
    value (there is nothing to compare a "best" sentinel against except other real numbers)."""
    if value is None:
        return 100.0 if none_meaning == "best" else 50.0
    resolved = [p for p in population if p is not None]
    if not resolved:
        return 50.0
    n = len(resolved)
    below = sum(1 for p in resolved if p < value)
    equal = sum(1 for p in resolved if p == value)
    # midpoint-of-ties convention: a value tied with k others sits at the CENTER of that tie block.
    return 100.0 * (below + 0.5 * equal) / n


def credibility_weight(n_trades: int, k: float = CREDIBILITY_K) -> float:
    return n_trades / (n_trades + k)


def _pca_weights(matrix: dict[str, list[float]]) -> dict[str, float]:
    names = list(matrix)
    data = np.array([matrix[name] for name in names], dtype=float)  # metrics x strategies
    if data.shape[1] < MIN_POPULATION_FOR_PCA:
        equal = 1.0 / len(names)
        return {name: equal for name in names}

    centered = data - data.mean(axis=1, keepdims=True)
    cov = np.cov(centered)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    top = eigenvectors[:, int(np.argmax(eigenvalues))]
    if top.sum() < 0:
        top = -top
    top = np.clip(top, 0.0, None)
    total = top.sum()
    if total <= 0:
        equal = 1.0 / len(names)
        return {name: equal for name in names}
    return {name: float(w / total) for name, w in zip(names, top)}


def score_window(
    strategy_metrics: WindowMetrics, population_metrics: Sequence[WindowMetrics],
) -> WindowScore:
    """The composite 0-100 score for one strategy's own metrics in one window, against the
    cross-section of every strategy with at least one trade in that same window."""
    window = strategy_metrics.window
    if strategy_metrics.n_trades == 0:
        return WindowScore(window=window, score=None, confidence=0.0, metric_weights={}, metric_percentiles={})

    percentiles: dict[str, float] = {}
    shrunk_matrix: dict[str, list[float]] = {}
    confidence = credibility_weight(strategy_metrics.n_trades)

    for name, higher_better, none_meaning in _METRIC_SPECS:
        own_raw = _raw_value(strategy_metrics, name)
        population_raw = [_raw_value(m, name) for m in population_metrics if m.n_trades > 0]
        oriented_own = own_raw if (own_raw is None or higher_better) else -own_raw
        oriented_population = [
            (p if (p is None or higher_better) else -p) for p in population_raw
        ]
        pct = percentile_rank(oriented_own, oriented_population, none_meaning)
        percentiles[name] = pct

        shrunk_row = []
        for m in population_metrics:
            if m.n_trades == 0:
                continue
            peer_raw = _raw_value(m, name)
            oriented_peer = peer_raw if (peer_raw is None or higher_better) else -peer_raw
            peer_pct = percentile_rank(oriented_peer, oriented_population, none_meaning)
            peer_conf = credibility_weight(m.n_trades)
            shrunk_row.append(peer_conf * peer_pct + (1 - peer_conf) * 50.0)
        shrunk_matrix[name] = shrunk_row

    weights = _pca_weights(shrunk_matrix)
    shrunk_own = {name: confidence * percentiles[name] + (1 - confidence) * 50.0 for name, *_ in _METRIC_SPECS}
    composite = sum(weights[name] * shrunk_own[name] for name in weights)

    return WindowScore(
        window=window, score=composite, confidence=confidence, metric_weights=weights,
        metric_percentiles=percentiles,
    )


def combine_windows(window_scores: Mapping[str, WindowScore]) -> tuple[float | None, float | None]:
    """Blend the 3 window scores into one overall Health Score using ``WINDOW_PRIORITY``,
    redistributing a missing window's weight proportionally among the windows that do have data.
    Returns ``(overall_score, trend_delta)`` -- ``trend_delta`` is ``3m score - 12m score`` when both
    exist (the regime-adaptation signal: strongly positive means recent performance has improved
    relative to the 12-month baseline; strongly negative means it has decayed), else ``None``.
    """
    available_scores = {w: s.score for w, s in window_scores.items() if s.score is not None}
    if not available_scores:
        return None, None

    total_priority = sum(WINDOW_PRIORITY[w] for w in available_scores)
    overall = sum(WINDOW_PRIORITY[w] * available_scores[w] for w in available_scores) / total_priority

    trend = None
    if "3m" in available_scores and "12m" in available_scores:
        trend = available_scores["3m"] - available_scores["12m"]
    return overall, trend
