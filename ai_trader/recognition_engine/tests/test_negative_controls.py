"""The 9 CEO-mandated negative/synthetic controls for Recognition Engine Phase 1A
(`RECOGNITION_ENGINE_PHASE1_DESIGN.md` §7-8, CEO's own Phase 1A authorization "CONTROALE OBLIGATORII").
Control 7 (permanent mismatch regression fixtures) lives in `test_regression_fixtures.py`; control 9
(no-write) lives in `test_no_write_control.py`. This file covers controls 1, 2, 3, 4, 5, 6, 8.
"""

from __future__ import annotations

import inspect
import random
from pathlib import Path

from ai_trader.context_memory.enums import ContextVolatilityRegime, OutcomeKind
from ai_trader.recognition_engine.engine import _bucket_value, compute_conditional_statistics
from ai_trader.recognition_engine.types import ContextDimension
from ai_trader.recognition_engine.tests._fixtures import build_repository, make_snapshot


# ================================================================================================
# Control 1: self-match exclusion
# ================================================================================================
# Phase 1A computes AGGREGATE historical statistics over already-closed positions (a batch group-by),
# not a live per-decision retrieval query (that architecture, where "self-match" originally meant "a
# live query must not retrieve its own future," belongs to a DIFFERENT, not-yet-authorized design --
# RECOGNITION_ENGINE_DESIGN.md's own retrieval-based recognize()). For THIS architecture, the concrete,
# testable equivalent is two-fold: (a) bucket assignment is structurally a pure function of ContextSnapshot
# alone, so a record's own result can never influence which bucket IT ITSELF lands in (proven in Control 3
# below); (b) each record contributes to its own bucket's aggregate EXACTLY ONCE -- no duplication, no
# double-counting, no record silently excluded from or added twice to its own group.


def test_self_match_each_record_counted_exactly_once(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": float(i),
         "snapshot_overrides": {"session_state": "ny"}}
        for i in range(10)
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats[0].n == 10  # every record counted, none duplicated, none missing
    # sum of favorable/unfavorable/zero must equal n exactly (ConditionalStatistics.__post_init__ already
    # enforces this structurally; re-asserted here as an explicit self-match-exclusion proof)
    assert stats[0].favorable_count + stats[0].unfavorable_count + stats[0].zero_count == stats[0].n


# ================================================================================================
# Control 2: label-shuffle control
# ================================================================================================
# Direct methodological reuse of the Research Lab's own matched-null validation approach (proven, not
# invented for this design): if the true association between context and result is destroyed by shuffling
# which result belongs to which context, any apparent per-bucket difference must shrink toward the
# population-wide rate.


def test_label_shuffle_destroys_real_bucket_separation(tmp_path: Path) -> None:
    n_per_bucket = 30
    real_records = (
        [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
          "snapshot_overrides": {"session_state": "ny"}} for _ in range(n_per_bucket)]
        + [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": -1.0,
            "snapshot_overrides": {"session_state": "london"}} for _ in range(n_per_bucket)]
    )
    repo_real = build_repository(tmp_path / "real", real_records)
    stats_real = compute_conditional_statistics(repo_real, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    real_by_bucket = {s.context_bucket_value: s.favorable_rate for s in stats_real}
    assert real_by_bucket["ny"] is not None and real_by_bucket["london"] is not None  # n=30 >= threshold
    real_gap = abs(real_by_bucket["ny"] - real_by_bucket["london"])
    assert real_gap == 1.0  # ny is 100% favorable, london is 0% favorable -- a genuine, real pattern

    rng = random.Random(1234)
    results = [1.0] * n_per_bucket + [-1.0] * n_per_bucket
    rng.shuffle(results)
    shuffled_records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": results[i],
         "snapshot_overrides": {"session_state": "ny" if i < n_per_bucket else "london"}}
        for i in range(2 * n_per_bucket)
    ]
    repo_shuffled = build_repository(tmp_path / "shuffled", shuffled_records)
    stats_shuffled = compute_conditional_statistics(
        repo_shuffled, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION,
    )
    shuffled_by_bucket = {s.context_bucket_value: s.favorable_rate for s in stats_shuffled}
    assert shuffled_by_bucket["ny"] is not None and shuffled_by_bucket["london"] is not None
    shuffled_gap = abs(shuffled_by_bucket["ny"] - shuffled_by_bucket["london"])

    assert shuffled_gap < real_gap  # shuffling must shrink the apparent separation, with this fixed seed


# ================================================================================================
# Control 3: temporal reversal / temporal integrity control
# ================================================================================================
# No information from after the decision moment may enter the context used for bucketing.


def test_bucket_value_signature_takes_only_context_snapshot() -> None:
    params = list(inspect.signature(_bucket_value).parameters)
    assert params == ["context_snapshot", "dimension"]  # structurally cannot receive a PositionOutcome/result


def test_identical_context_different_result_same_bucket(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 100.0,
         "snapshot_overrides": {"session_state": "ny"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": -100.0,
         "snapshot_overrides": {"session_state": "ny"}},
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert len(stats) == 1  # same context (session=ny) -> same bucket, regardless of wildly different results
    assert stats[0].n == 2


def test_different_context_same_result_different_bucket(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}},
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "london"}},
    ]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert len(stats) == 2  # identical result, different context -> different buckets


def test_bucket_value_ignores_position_outcome_entirely() -> None:
    snap = make_snapshot(session_state="asia")
    # _bucket_value never receives a PositionOutcome at all -- calling it twice with the same snapshot
    # and different (nonexistent) "future" context is not even expressible; this documents the invariant.
    assert _bucket_value(snap, ContextDimension.SESSION) == "asia"
    assert _bucket_value(snap, ContextDimension.SESSION) == "asia"  # deterministic, no hidden state


# ================================================================================================
# Control 4: empty-input control
# ================================================================================================


def test_empty_repository_returns_empty_tuple_never_raises(tmp_path: Path) -> None:
    repo = build_repository(tmp_path, [])
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats == ()


def test_strategy_with_no_records_returns_empty_tuple(tmp_path: Path) -> None:
    records = [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0}]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S999-NEVER-TRADED", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats == ()


def test_outcome_kind_with_no_records_returns_empty_tuple(tmp_path: Path) -> None:
    records = [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0}]
    repo = build_repository(tmp_path, records)
    stats = compute_conditional_statistics(repo, "S1", OutcomeKind.PORTFOLIO, ContextDimension.SESSION)
    assert stats == ()  # S1 has STRATEGY-kind records only -- PORTFOLIO-kind query must return empty, not raise


# ================================================================================================
# Control 5: strategy isolation control
# ================================================================================================


def test_strategy_isolation_s1_never_sees_s2_data(tmp_path: Path) -> None:
    records = (
        [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
          "snapshot_overrides": {"session_state": "ny"}} for _ in range(5)]
        + [{"strategy_id": "S2", "outcome_kind": OutcomeKind.STRATEGY, "result": -1.0,
            "snapshot_overrides": {"session_state": "ny"}} for _ in range(5)]
    )
    repo = build_repository(tmp_path, records)
    s1_stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    s2_stats = compute_conditional_statistics(repo, "S2", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert s1_stats[0].n == 5 and s1_stats[0].mean_result == 1.0
    assert s2_stats[0].n == 5 and s2_stats[0].mean_result == -1.0
    assert all(s.strategy_id == "S1" for s in s1_stats)
    assert all(s.strategy_id == "S2" for s in s2_stats)


# ================================================================================================
# Control 6: outcome-kind isolation control
# ================================================================================================


def test_outcome_kind_isolation_strategy_and_portfolio_never_blend(tmp_path: Path) -> None:
    records = (
        [{"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
          "snapshot_overrides": {"session_state": "ny"}} for _ in range(5)]
        + [{"strategy_id": "S1", "outcome_kind": OutcomeKind.PORTFOLIO, "result": -1.0,
            "snapshot_overrides": {"session_state": "ny"}} for _ in range(5)]
    )
    repo = build_repository(tmp_path, records)
    strat_stats = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    port_stats = compute_conditional_statistics(repo, "S1", OutcomeKind.PORTFOLIO, ContextDimension.SESSION)
    assert strat_stats[0].n == 5 and strat_stats[0].mean_result == 1.0
    assert port_stats[0].n == 5 and port_stats[0].mean_result == -1.0
    assert strat_stats[0].outcome_kind == "STRATEGY"
    assert port_stats[0].outcome_kind == "PORTFOLIO"


# ================================================================================================
# Control 8: determinism
# ================================================================================================


def test_determinism_same_input_same_output(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": float(i % 3 - 1),
         "snapshot_overrides": {
             "session_state": ["ny", "london", "asia"][i % 3],
             "volatility_regime": [ContextVolatilityRegime.HIGH, ContextVolatilityRegime.NORMAL][i % 2],
         }}
        for i in range(20)
    ]
    repo = build_repository(tmp_path, records)
    stats_a = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    stats_b = compute_conditional_statistics(repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats_a == stats_b  # frozen dataclasses -> structural equality; identical input, identical output
