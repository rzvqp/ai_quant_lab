"""Confidence-calibration measurement -- Phase 7 Checkpoint 15. Whether Context Memory's own point
estimate carries any measured predictive skill against REAL realized outcomes. Pure, general,
stdlib-only machinery -- never fabricates a correlation from zero real data; `n_samples == 0` is a
first-class, honest result."""

from __future__ import annotations

import math
from collections.abc import Sequence

from ai_trader.decision_comparison.types import CalibrationResult, CalibrationSample


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _pearson_correlation(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    variance_y = sum((y - mean_y) ** 2 for y in ys)
    if variance_x == 0.0 or variance_y == 0.0:
        return None
    return covariance / math.sqrt(variance_x * variance_y)


def evaluate_calibration(samples: Sequence[CalibrationSample]) -> CalibrationResult:
    n = len(samples)
    if n == 0:
        return CalibrationResult(
            n_samples=0, sign_agreement_rate=None, pearson_correlation=None,
            rationale=(
                "No real historical outcome data supplied -- Context Memory's repository is not yet "
                "populated with real AI Trader observations (Checkpoint 14's own disclosed limitation), "
                "so predictive skill cannot be measured yet; this function's own machinery is built and "
                "tested with synthetic data, ready to run once real paired data exists."
            ),
        )

    predicted_means: list[float] = [s.predicted_mean for s in samples if s.predicted_mean is not None]
    realized_where_predicted: list[float] = [s.realized_result for s in samples if s.predicted_mean is not None]

    sign_agreement_rate = None
    if predicted_means:
        agreements = sum(1 for p, r in zip(predicted_means, realized_where_predicted) if _sign(p) == _sign(r))
        sign_agreement_rate = agreements / len(predicted_means)

    pearson = _pearson_correlation(predicted_means, realized_where_predicted)

    return CalibrationResult(
        n_samples=n, sign_agreement_rate=sign_agreement_rate, pearson_correlation=pearson,
        rationale=f"{n} sample(s) evaluated; {len(predicted_means)} carried a Context Memory point estimate.",
    )
