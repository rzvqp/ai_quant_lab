"""Basic correctness for Recognition Engine Phase 1A -- grouping, counting, descriptive statistics,
sufficiency-threshold boundary behavior."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.recognition_engine.engine import compute_conditional_statistics
from ai_trader.recognition_engine.policy import SufficiencyPolicy
from ai_trader.recognition_engine.types import ContextDimension, Sufficiency
from ai_trader.recognition_engine.tests._fixtures import build_repository


def test_single_bucket_basic_counts(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": -1.0,
         "snapshot_overrides": {"session_state": "ny"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 0.0,
         "snapshot_overrides": {"session_state": "ny"}},
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert len(stats) == 1
    bucket = stats[0]
    assert bucket.context_bucket_value == "ny"
    assert bucket.n == 3
    assert bucket.favorable_count == 1
    assert bucket.unfavorable_count == 1
    assert bucket.zero_count == 1
    assert bucket.mean_result == 0.0
    assert bucket.sufficiency is Sufficiency.INSUFFICIENT_EVIDENCE  # 3 < default 25


def test_two_distinct_buckets_are_separated(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 5.0,
         "snapshot_overrides": {"session_state": "ny"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": -5.0,
         "snapshot_overrides": {"session_state": "london"}},
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert {s.context_bucket_value for s in stats} == {"ny", "london"}
    by_bucket = {s.context_bucket_value: s for s in stats}
    assert by_bucket["ny"].mean_result == 5.0
    assert by_bucket["london"].mean_result == -5.0


def test_sufficiency_threshold_boundary_24_vs_25(tmp_path: Path) -> None:
    records_24 = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}}
        for _ in range(24)
    ]
    repo_24 = build_repository(tmp_path / "a", records_24)
    stats_24 = compute_conditional_statistics(repo_24, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats_24[0].n == 24
    assert stats_24[0].sufficiency is Sufficiency.INSUFFICIENT_EVIDENCE

    records_25 = records_24 + [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}}
    ]
    repo_25 = build_repository(tmp_path / "b", records_25)
    stats_25 = compute_conditional_statistics(repo_25, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats_25[0].n == 25
    assert stats_25[0].sufficiency is Sufficiency.SUFFICIENT


def test_custom_sufficiency_policy_is_honored(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}}
        for _ in range(5)
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(
        repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION, policy=SufficiencyPolicy(min_observations=5),
    )
    assert stats[0].sufficiency is Sufficiency.SUFFICIENT


def test_different_dimension_produces_different_bucketing(tmp_path: Path) -> None:
    from ai_trader.context_memory.enums import ContextVolatilityRegime

    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny", "volatility_regime": ContextVolatilityRegime.HIGH}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "london", "volatility_regime": ContextVolatilityRegime.HIGH}},
    ]
    repo = build_repository(tmp_path, records)
    by_session = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    by_vol = compute_conditional_statistics(
        repo, "S1", OutcomeKind.STRATEGY, ContextDimension.VOLATILITY_REGIME,
    )
    assert len(by_session) == 2  # ny, london
    assert len(by_vol) == 1  # both HIGH -> merged into one bucket
    assert by_vol[0].n == 2


def test_results_sorted_by_bucket_value_deterministically(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "late"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "asia"}},
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert [s.context_bucket_value for s in stats] == sorted(s.context_bucket_value for s in stats)
