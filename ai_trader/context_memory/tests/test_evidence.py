"""Unit tests for :mod:`ai_trader.context_memory.evidence`."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import Observation, Outcome, SchemaVersion
from ai_trader.context_memory.enums import HorizonUnit, OutcomeStatus, SourceType
from ai_trader.context_memory.evidence import (
    EVIDENCE_POLICY_VERSION,
    EvidencePolicy,
    EvidenceStatus,
    aggregate_all_present_edges,
    aggregate_evidence,
)
from ai_trader.context_memory.index import HistoricalIndex
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.retrieval import RetrievalQuery, retrieve
from ai_trader.context_memory.tests._fixtures import AS_OF, make_edge_reference, make_snapshot
from ai_trader.context_memory.validation import ContextMemoryValidationError

OUTCOME_VERSION = SchemaVersion("outcome_definition", "od-v1")


def _build(
    tmp_path: Path, count: int, *, results: list[float] | None = None, edge: str = "S1",
    status: OutcomeStatus = OutcomeStatus.RESOLVED, spacing: int = 20_000_000,
) -> tuple[HistoricalIndex, list]:
    # Each observation gets a UNIQUE session_state so every observation becomes its own separate
    # episode (a distinct state_fingerprint each time -- identical categorical values across
    # consecutive observations would instead collapse into ONE episode, per Checkpoint 11's own
    # collapsing rule). session_state is also the FIRST entry in the relaxation ladder, so every
    # resulting episode still matches a default query snapshot (session_state="LONDON") at the same
    # single relaxed tier (tier 1) -- keeping every built episode returned by one retrieve() call.
    repo = ContextMemoryRepository(tmp_path / "repo")
    ref = make_edge_reference(edge)
    obs_ids = []
    for i in range(count):
        snap = make_snapshot(as_of=AS_OF + i * spacing, session_state=f"SESSION_{i}")
        obs_id = repo.append_observation(Observation(context_snapshot=snap, present_edges=(ref,)))
        obs_ids.append(obs_id)
        result = None
        resolution = None
        if status is OutcomeStatus.RESOLVED:
            result = results[i] if results is not None else 0.5
            resolution = AS_OF + i * spacing + 100
        elif status in (OutcomeStatus.INVALID, OutcomeStatus.UNAVAILABLE):
            resolution = AS_OF + i * spacing + 100
        repo.append_outcome(
            Outcome(
                observation_id=obs_id, strategy_id=edge, horizon=20, horizon_unit=HorizonUnit.BARS,
                outcome_definition_version=OUTCOME_VERSION, status=status,
                observation_as_of=AS_OF + i * spacing, normalized_result=result, resolution_as_of=resolution,
                cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.PRICE_ONLY,
            )
        )
    return HistoricalIndex(repo), obs_ids


def _retrieve(index: HistoricalIndex, cutoff: int, **kwargs):
    query = RetrievalQuery(context_snapshot=make_snapshot(as_of=cutoff), as_of_cutoff=cutoff, **kwargs)
    return retrieve(index, query)


# ------------------------------------------------------------------ EvidencePolicy validation


def test_policy_default_uses_research_layer_mintr() -> None:
    policy = EvidencePolicy()
    assert policy.min_episodes_sufficient == 25
    assert policy.policy_version == EVIDENCE_POLICY_VERSION


def test_policy_rejects_limited_above_sufficient() -> None:
    with pytest.raises(ContextMemoryValidationError):
        EvidencePolicy(min_episodes_sufficient=5, min_episodes_limited=10)


def test_policy_rejects_non_positive_staleness_threshold() -> None:
    with pytest.raises(ContextMemoryValidationError):
        EvidencePolicy(staleness_threshold_seconds=0)


def test_policy_rejects_non_schema_version() -> None:
    with pytest.raises(ContextMemoryValidationError):
        EvidencePolicy(policy_version="not-a-version")  # type: ignore[arg-type]


# ------------------------------------------------------------------ input boundary / failure outputs


def test_incompatible_retrieval_yields_incompatible_evidence(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 1)
    bad_version = SchemaVersion("context_memory_retrieval", "cmr-v999")
    result = _retrieve(idx, AS_OF + 1000, retrieval_policy_version=bad_version)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.INCOMPATIBLE


def test_no_eligible_history_yields_unavailable(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 0)
    result = _retrieve(idx, AS_OF + 1000)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.UNAVAILABLE
    assert report.episode_count == 0


def test_edge_not_present_in_retrieved_episodes_yields_unavailable(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 3, edge="S7")
    result = _retrieve(idx, AS_OF + 100_000_000)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.UNAVAILABLE


def test_only_pending_outcomes_yields_unavailable(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 3, status=OutcomeStatus.PENDING)
    result = _retrieve(idx, AS_OF + 100_000_000)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.UNAVAILABLE
    assert report.unresolved_outcome_count == 3
    assert report.resolved_outcome_count == 0


def test_aggregate_evidence_rejects_empty_strategy_id(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 1)
    result = _retrieve(idx, AS_OF + 1000)
    with pytest.raises(ContextMemoryValidationError):
        aggregate_evidence(idx, result, "")


def test_edge_present_with_zero_outcomes_recorded_at_all_yields_unavailable(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF), present_edges=(make_edge_reference("S1"),)))
    idx = HistoricalIndex(repo)
    result = _retrieve(idx, AS_OF + 1000)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.UNAVAILABLE
    assert report.raw_outcome_count == 0


# ------------------------------------------------------------------ internal defense-in-depth


def test_classify_helper_rejects_zero_n_directly() -> None:
    # White-box: through aggregate_evidence, `_classify` is only ever called after confirming at least
    # one RESOLVED, dominant-triple outcome exists, so n==0 is structurally unreachable via the public
    # API. Exercised directly for defense-in-depth, matching Checkpoint 10/12's own convention.
    from ai_trader.context_memory.evidence import _classify

    status, reason = _classify(0, None, EvidencePolicy(), None)
    assert status is EvidenceStatus.UNAVAILABLE


# ------------------------------------------------------------------ sufficiency classification


def test_sufficient_status_at_or_above_research_layer_threshold(tmp_path: Path) -> None:
    # 25 episodes, all with a strongly positive, low-dispersion result -> CI well clear of zero.
    idx, _ = _build(tmp_path, 30, results=[1.0] * 30, spacing=1000)
    result = _retrieve(idx, AS_OF + 40_000, edge_scope=("S1",), max_candidates=30)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.SUFFICIENT
    assert report.resolved_outcome_count >= 25
    assert report.confidence_interval_95 is not None
    assert report.confidence_interval_95[0] > 0


def test_limited_status_below_threshold(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 5, results=[1.0] * 5, spacing=1000)
    result = _retrieve(idx, AS_OF + 10_000, max_candidates=5)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.LIMITED
    assert report.resolved_outcome_count == 5


def test_contradictory_status_when_ci_straddles_zero(tmp_path: Path) -> None:
    # Alternating +1/-1 results -> mean ~0, CI straddles zero.
    results = [1.0 if i % 2 == 0 else -1.0 for i in range(10)]
    idx, _ = _build(tmp_path, 10, results=results, spacing=1000)
    result = _retrieve(idx, AS_OF + 20_000, max_candidates=10)
    report = aggregate_evidence(idx, result, "S1")
    assert report.evidence_status is EvidenceStatus.CONTRADICTORY
    assert report.confidence_interval_95 is not None
    assert report.confidence_interval_95[0] <= 0.0 <= report.confidence_interval_95[1]


def test_stale_status_when_policy_threshold_configured_and_exceeded(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 1, results=[1.0])
    result = _retrieve(idx, AS_OF + 10_000_000)
    policy = EvidencePolicy(staleness_threshold_seconds=100)
    report = aggregate_evidence(idx, result, "S1", policy)
    assert report.evidence_status is EvidenceStatus.STALE


def test_no_staleness_check_when_threshold_not_configured(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 1, results=[1.0])
    result = _retrieve(idx, AS_OF + 10_000_000)
    report = aggregate_evidence(idx, result, "S1")  # default policy, staleness disabled
    assert report.evidence_status is not EvidenceStatus.STALE
    assert report.evidence_freshness_newest_age is not None


# ------------------------------------------------------------------ episode-level counting (no inflation)


def test_episode_aware_count_never_exceeds_episode_count(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 8, results=[0.5] * 8, spacing=1000)
    result = _retrieve(idx, AS_OF + 20_000, max_candidates=8)
    report = aggregate_evidence(idx, result, "S1")
    assert report.resolved_outcome_count <= report.episode_count
    assert report.raw_outcome_count >= report.resolved_outcome_count


# ------------------------------------------------------------------ statistical safety fields


def test_win_rate_and_sign_counts(tmp_path: Path) -> None:
    results = [1.0, 1.0, 1.0, -1.0, 0.0]
    idx, _ = _build(tmp_path, 5, results=results, spacing=1000)
    result = _retrieve(idx, AS_OF + 10_000, max_candidates=5)
    report = aggregate_evidence(idx, result, "S1")
    assert report.positive_sign_count == 3
    assert report.negative_sign_count == 1
    assert report.zero_sign_count == 1
    assert report.contextual_win_rate == pytest.approx(3 / 5)


def test_median_resistant_to_single_outlier(tmp_path: Path) -> None:
    results = [1.0, 1.1, 0.9, 1.0, 100.0]
    idx, _ = _build(tmp_path, 5, results=results, spacing=1000)
    result = _retrieve(idx, AS_OF + 10_000, max_candidates=5)
    report = aggregate_evidence(idx, result, "S1")
    assert report.median_normalized_result is not None
    assert report.mean_normalized_result is not None
    assert report.median_normalized_result < report.mean_normalized_result


def test_limitations_always_disclose_normal_approximation_caveat(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 3, results=[1.0, 1.0, 1.0], spacing=1000)
    result = _retrieve(idx, AS_OF + 5_000, max_candidates=3)
    report = aggregate_evidence(idx, result, "S1")
    assert any("NORMAL-APPROXIMATION" in lim for lim in report.limitations)


# ------------------------------------------------------------------ outcome compatibility partitioning


def test_incompatible_outcome_definition_version_is_excluded_and_disclosed(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    ref = make_edge_reference("S1")
    other_version = SchemaVersion("outcome_definition", "od-v2")
    obs_ids = []
    for i in range(3):
        snap = make_snapshot(as_of=AS_OF + i * 1000, session_state=f"SESSION_{i}")
        obs_id = repo.append_observation(Observation(context_snapshot=snap, present_edges=(ref,)))
        obs_ids.append(obs_id)
        version = OUTCOME_VERSION if i < 2 else other_version
        repo.append_outcome(
            Outcome(
                observation_id=obs_id, strategy_id="S1", horizon=20, horizon_unit=HorizonUnit.BARS,
                outcome_definition_version=version, status=OutcomeStatus.RESOLVED,
                observation_as_of=AS_OF + i * 1000, normalized_result=1.0, resolution_as_of=AS_OF + i * 1000 + 10,
                cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.PRICE_ONLY,
            )
        )
    idx = HistoricalIndex(repo)
    result = _retrieve(idx, AS_OF + 5_000, max_candidates=3)
    report = aggregate_evidence(idx, result, "S1")
    assert report.resolved_outcome_count == 2
    assert report.excluded_incompatible_outcome_count == 1
    assert any("outcome_definition_version" in lim for lim in report.limitations)


# ------------------------------------------------------------------ multi-edge aggregation, no ranking


def test_aggregate_all_present_edges_is_sorted_and_independent(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    snap = make_snapshot(as_of=AS_OF)
    ref_a = make_edge_reference("S9")
    ref_b = make_edge_reference("S2")
    obs_id = repo.append_observation(Observation(context_snapshot=snap, present_edges=(ref_a, ref_b)))
    for sid in ("S9", "S2"):
        repo.append_outcome(
            Outcome(
                observation_id=obs_id, strategy_id=sid, horizon=20, horizon_unit=HorizonUnit.BARS,
                outcome_definition_version=OUTCOME_VERSION, status=OutcomeStatus.RESOLVED,
                observation_as_of=AS_OF, normalized_result=1.0, resolution_as_of=AS_OF + 10,
                cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.PRICE_ONLY,
            )
        )
    idx = HistoricalIndex(repo)
    result = _retrieve(idx, AS_OF + 1000)
    reports = aggregate_all_present_edges(idx, result)
    assert [r.target_strategy_id for r in reports] == ["S2", "S9"]  # deterministic sort, never a ranking


# ------------------------------------------------------------------ determinism


def test_aggregation_is_deterministic(tmp_path: Path) -> None:
    idx, _ = _build(tmp_path, 6, results=[0.2, 0.4, -0.1, 0.3, 0.5, -0.2], spacing=1000)
    result = _retrieve(idx, AS_OF + 10_000, max_candidates=6)
    r1 = aggregate_evidence(idx, result, "S1")
    r2 = aggregate_evidence(idx, result, "S1")
    assert r1 == r2
