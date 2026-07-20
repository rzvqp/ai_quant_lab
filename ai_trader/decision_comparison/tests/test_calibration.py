"""Unit tests for :mod:`ai_trader.decision_comparison.calibration`."""

from __future__ import annotations

from ai_trader.decision_comparison.calibration import evaluate_calibration
from ai_trader.decision_comparison.types import CalibrationSample


def test_zero_samples_is_honest_first_class_result() -> None:
    result = evaluate_calibration([])
    assert result.n_samples == 0
    assert result.sign_agreement_rate is None
    assert result.pearson_correlation is None
    assert "not yet populated" in result.rationale


def test_perfect_sign_agreement() -> None:
    samples = [
        CalibrationSample(predicted_mean=0.5, predicted_status="SUFFICIENT", realized_result=0.3),
        CalibrationSample(predicted_mean=-0.5, predicted_status="SUFFICIENT", realized_result=-0.2),
        CalibrationSample(predicted_mean=0.1, predicted_status="LIMITED", realized_result=0.9),
    ]
    result = evaluate_calibration(samples)
    assert result.n_samples == 3
    assert result.sign_agreement_rate == 1.0


def test_zero_sign_agreement() -> None:
    samples = [
        CalibrationSample(predicted_mean=0.5, predicted_status="SUFFICIENT", realized_result=-0.3),
        CalibrationSample(predicted_mean=-0.5, predicted_status="SUFFICIENT", realized_result=0.2),
    ]
    result = evaluate_calibration(samples)
    assert result.sign_agreement_rate == 0.0


def test_zero_sign_is_its_own_bucket() -> None:
    samples = [CalibrationSample(predicted_mean=0.0, predicted_status="SUFFICIENT", realized_result=0.0)]
    result = evaluate_calibration(samples)
    assert result.sign_agreement_rate == 1.0  # sign(0) == sign(0)


def test_missing_predicted_mean_excluded_from_sign_agreement() -> None:
    samples = [CalibrationSample(predicted_mean=None, predicted_status="UNAVAILABLE", realized_result=0.3)]
    result = evaluate_calibration(samples)
    assert result.n_samples == 1
    assert result.sign_agreement_rate is None
    assert result.pearson_correlation is None


def test_pearson_correlation_perfect_positive() -> None:
    samples = [
        CalibrationSample(predicted_mean=float(i), predicted_status="SUFFICIENT", realized_result=float(i) * 2.0)
        for i in range(1, 6)
    ]
    result = evaluate_calibration(samples)
    assert result.pearson_correlation is not None
    assert result.pearson_correlation == 1.0


def test_pearson_correlation_none_when_fewer_than_two_predicted() -> None:
    samples = [CalibrationSample(predicted_mean=0.5, predicted_status="SUFFICIENT", realized_result=0.1)]
    result = evaluate_calibration(samples)
    assert result.pearson_correlation is None


def test_pearson_correlation_none_when_zero_variance() -> None:
    samples = [
        CalibrationSample(predicted_mean=0.5, predicted_status="SUFFICIENT", realized_result=0.1),
        CalibrationSample(predicted_mean=0.5, predicted_status="SUFFICIENT", realized_result=0.9),
    ]
    result = evaluate_calibration(samples)
    assert result.pearson_correlation is None
