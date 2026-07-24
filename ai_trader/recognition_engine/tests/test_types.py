"""Validation tests for `ConditionalStatistics`'s own `__post_init__` invariants."""

from __future__ import annotations

import pytest

from ai_trader.recognition_engine.types import ConditionalStatistics, ContextDimension, Sufficiency


def _stats(**overrides: object) -> ConditionalStatistics:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "outcome_kind": "STRATEGY", "context_dimension": ContextDimension.SESSION,
        "context_bucket_value": "ny", "n": 3, "favorable_count": 1, "unfavorable_count": 1,
        "zero_count": 1, "favorable_rate": 1 / 3, "unfavorable_rate": 1 / 3, "mean_result": 0.0,
        "median_result": 0.0, "stdev_result": 1.0, "min_result": -1.0, "max_result": 1.0,
        "sufficiency": Sufficiency.INSUFFICIENT_EVIDENCE, "min_observations_threshold": 25,
        "data_provenance": "test",
    }
    kwargs.update(overrides)
    return ConditionalStatistics(**kwargs)  # type: ignore[arg-type]


def test_construction_happy_path() -> None:
    s = _stats()
    assert s.n == 3


def test_rejects_negative_n() -> None:
    with pytest.raises(ValueError, match="n must be >= 0"):
        _stats(n=-1)


def test_rejects_count_mismatch() -> None:
    with pytest.raises(ValueError, match="must equal n"):
        _stats(favorable_count=2)  # 2 + 1 + 1 = 4 != n=3


def test_rejects_zero_n_without_insufficient_evidence() -> None:
    with pytest.raises(ValueError, match="INSUFFICIENT_EVIDENCE"):
        _stats(n=0, favorable_count=0, unfavorable_count=0, zero_count=0, sufficiency=Sufficiency.SUFFICIENT)


def test_zero_n_with_insufficient_evidence_is_valid() -> None:
    s = _stats(
        n=0, favorable_count=0, unfavorable_count=0, zero_count=0,
        favorable_rate=None, unfavorable_rate=None, mean_result=None, median_result=None,
        stdev_result=None, min_result=None, max_result=None, sufficiency=Sufficiency.INSUFFICIENT_EVIDENCE,
    )
    assert s.n == 0
