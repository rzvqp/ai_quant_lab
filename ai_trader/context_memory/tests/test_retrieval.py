"""Unit tests for :mod:`ai_trader.context_memory.retrieval`."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.context_memory.contracts import Observation, SchemaVersion
from ai_trader.context_memory.enums import (
    ContextDataQualityState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
)
from ai_trader.context_memory.index import HistoricalIndex
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.retrieval import (
    RETRIEVAL_POLICY_VERSION,
    RetrievalQuery,
    RetrievalStatus,
    retrieve,
)
from ai_trader.context_memory.tests._fixtures import AS_OF, make_edge_reference, make_snapshot
from ai_trader.context_memory.validation import ContextMemoryValidationError


def _repo_with(tmp_path: Path, snapshots: list, *, edge: str = "S1") -> HistoricalIndex:
    repo = ContextMemoryRepository(tmp_path / "repo")
    ref = make_edge_reference(edge)
    for snap in snapshots:
        repo.append_observation(Observation(context_snapshot=snap, present_edges=(ref,)))
    return HistoricalIndex(repo)


def _query(snapshot, as_of_cutoff, **overrides) -> RetrievalQuery:
    kwargs = {"context_snapshot": snapshot, "as_of_cutoff": as_of_cutoff}
    kwargs.update(overrides)
    return RetrievalQuery(**kwargs)


# ------------------------------------------------------------------ query contract validation


def test_query_rejects_non_positive_cutoff() -> None:
    with pytest.raises(ContextMemoryValidationError):
        RetrievalQuery(context_snapshot=make_snapshot(), as_of_cutoff=0)


def test_query_rejects_empty_edge_scope_tuple() -> None:
    with pytest.raises(ContextMemoryValidationError):
        RetrievalQuery(context_snapshot=make_snapshot(), as_of_cutoff=AS_OF + 1, edge_scope=())


def test_query_rejects_non_positive_max_candidates() -> None:
    with pytest.raises(ContextMemoryValidationError):
        RetrievalQuery(context_snapshot=make_snapshot(), as_of_cutoff=AS_OF + 1, max_candidates=0)


def test_query_rejects_non_context_snapshot_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        RetrievalQuery(context_snapshot="not-a-snapshot", as_of_cutoff=AS_OF + 1)  # type: ignore[arg-type]


def test_query_rejects_non_schema_version_retrieval_policy_version() -> None:
    with pytest.raises(ContextMemoryValidationError):
        RetrievalQuery(context_snapshot=make_snapshot(), as_of_cutoff=AS_OF + 1, retrieval_policy_version="not-a-version")  # type: ignore[arg-type]


# ------------------------------------------------------------------ tier 0 exact match


def test_tier_0_exact_match(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.selected_relaxation_tier == 0
    assert result.returned_count == 1
    assert result.matches[0].relaxed_dimensions == ()


# ------------------------------------------------------------------ relaxation stepping


def test_relaxation_order_stepping(tmp_path: Path) -> None:
    # Candidate differs only in session_state -> must match at tier 1 (session_state is first in
    # RELAXATION_ORDER), never require deeper relaxation.
    candidate = make_snapshot(as_of=AS_OF, session_state="NY")
    idx = _repo_with(tmp_path, [candidate])
    query_snap = make_snapshot(as_of=AS_OF + 1000, session_state="LONDON")
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.selected_relaxation_tier == 1
    assert result.matches[0].relaxed_dimensions == ("session_state",)


def test_relaxation_reaches_deeper_tier_when_multiple_dimensions_differ(tmp_path: Path) -> None:
    from ai_trader.context_memory.enums import ContextExpansionState

    candidate = make_snapshot(as_of=AS_OF, session_state="NY", expansion_state=ContextExpansionState.COMPRESSED)
    idx = _repo_with(tmp_path, [candidate])
    query_snap = make_snapshot(as_of=AS_OF + 1000, session_state="LONDON", expansion_state=ContextExpansionState.NORMAL)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.selected_relaxation_tier == 2
    assert result.matches[0].relaxed_dimensions == ("session_state", "expansion_state")


# ------------------------------------------------------------------ floor / no-similar-match


def test_floor_reached_without_match_is_no_sufficiently_similar(tmp_path: Path) -> None:
    # Candidate differs on a FLOOR dimension (structure_state) -- never relaxed, so even the deepest
    # tier cannot match it. This also proves the relaxation order is enforced, not just documented
    # (design doc §14's own "synthetic false-neighbor" test).
    candidate = make_snapshot(as_of=AS_OF, structure_state=ContextStructureState.RANGING)
    idx = _repo_with(tmp_path, [candidate])
    query_snap = make_snapshot(as_of=AS_OF + 1000, structure_state=ContextStructureState.BULLISH_BOS)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.NO_SUFFICIENTLY_SIMILAR
    assert result.returned_count == 0
    assert result.no_sufficient_history_reason is not None
    assert result.eligible_episode_count == 1  # it WAS eligible, just never matched


def test_no_eligible_history_when_index_empty(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY
    assert result.eligible_episode_count == 0


def test_no_eligible_history_when_only_wrong_instrument_present(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF, instrument="EURUSD")])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000, instrument="XAUUSD"), AS_OF + 1000))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY


# ------------------------------------------------------------------ temporal safety / self-retrieval


def test_as_of_cutoff_excludes_future_and_self(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    # cutoff EQUAL to the only stored observation's own as_of must exclude it -- self-retrieval is
    # impossible, structurally, via the strict `<` cutoff (design doc §9.5).
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF), AS_OF))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY

    result2 = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1), AS_OF + 1))
    assert result2.status is RetrievalStatus.SUCCESSFUL


def test_future_observation_never_retrieved(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + 5000)])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF), AS_OF))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY


# ------------------------------------------------------------------ instrument scope never crossed


def test_never_crosses_instruments(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF, instrument="EURUSD")])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000, instrument="XAUUSD"), AS_OF + 1000))
    assert result.status is not RetrievalStatus.SUCCESSFUL


# ------------------------------------------------------------------ edge scope


def test_edge_scope_filters_candidates(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)], edge="S7")
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000, edge_scope=("S1",)))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY

    result2 = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000, edge_scope=("S7",)))
    assert result2.status is RetrievalStatus.SUCCESSFUL


# ------------------------------------------------------------------ max_candidates cap


def test_max_candidates_caps_returned_but_not_counts(tmp_path: Path) -> None:
    snaps = [make_snapshot(as_of=AS_OF + i * 10_000_000, momentum_h1=ContextMomentumState.OVERBOUGHT if i % 2 else ContextMomentumState.NEUTRAL) for i in range(3)]
    # Force each into its own episode via alternating momentum_h1 (a relaxable, non-floor dimension) --
    # tier reached will vary, but the point here is the cap, not the tier.
    idx = _repo_with(tmp_path, snaps)
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 40_000_000), AS_OF + 40_000_000, max_candidates=1))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.returned_count == 1
    assert len(result.limitations) == 1


# ------------------------------------------------------------------ deterministic ordering


def test_deterministic_recency_ordering(tmp_path: Path) -> None:
    idx = _repo_with(
        tmp_path,
        [
            make_snapshot(as_of=AS_OF, session_state="LONDON"),
            make_snapshot(as_of=AS_OF + 20_000_000, session_state="NY"),
        ],
    )
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 40_000_000, session_state="TOKYO"), AS_OF + 40_000_000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.returned_count == 2
    # more recent episode (the NY one) must sort first
    assert result.matches[0].episode.end_as_of == AS_OF + 20_000_000
    assert result.matches[1].episode.end_as_of == AS_OF


def test_retrieval_is_deterministic_across_repeated_calls(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF), make_snapshot(as_of=AS_OF + 900, session_state="NY")])
    query = _query(make_snapshot(as_of=AS_OF + 40_000_000), AS_OF + 40_000_000)
    r1 = retrieve(idx, query)
    r2 = retrieve(idx, query)
    assert r1.status == r2.status
    assert [m.episode_id.value for m in r1.matches] == [m.episode_id.value for m in r2.matches]


# ------------------------------------------------------------------ version / quality gates


def test_retrieval_policy_version_mismatch_is_incompatible(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    bad_version = SchemaVersion("context_memory_retrieval", "cmr-v999")
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000, retrieval_policy_version=bad_version))
    assert result.status is RetrievalStatus.INCOMPATIBLE


def test_unsupported_market_intelligence_schema_version(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    bad_mi = SchemaVersion("market_intelligence", "mi-v999")
    query_snap = make_snapshot(as_of=AS_OF + 1000, market_intelligence_schema_version=bad_mi)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.UNSUPPORTED_VERSION


def test_degraded_query_data_quality(tmp_path: Path) -> None:
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    query_snap = make_snapshot(as_of=AS_OF + 1000, data_quality_state=ContextDataQualityState.STALE)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.DEGRADED_DATA


def test_degraded_candidate_is_excluded_by_quality_gate(tmp_path: Path) -> None:
    # A STALE observation is excluded from episode membership entirely by Checkpoint 11's own
    # collapsing rule, so it can never surface as a retrievable episode -- verified end-to-end here.
    idx = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF, data_quality_state=ContextDataQualityState.STALE)])
    result = retrieve(idx, _query(make_snapshot(as_of=AS_OF + 1000), AS_OF + 1000))
    assert result.status is RetrievalStatus.NO_ELIGIBLE_HISTORY


# ------------------------------------------------------------------ match explanation correctness


def test_match_explanation_reports_matched_and_relaxed(tmp_path: Path) -> None:
    candidate = make_snapshot(as_of=AS_OF, liquidity_state=ContextLiquidityState.THIN)
    idx = _repo_with(tmp_path, [candidate])
    query_snap = make_snapshot(as_of=AS_OF + 1000, liquidity_state=ContextLiquidityState.NORMAL)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    match = result.matches[0]
    assert "liquidity_state" in match.relaxed_dimensions
    assert "instrument" in match.matched_dimensions
    assert "structure_state" in match.matched_dimensions
    assert match.unavailable_dimensions == ()


# ------------------------------------------------------------------ trend direction relaxes independently of momentum


# ------------------------------------------------------------------ internal defense-in-depth


def test_episode_matches_helper_rejects_instrument_mismatch_directly() -> None:
    # White-box test of the internal guard: HistoricalIndex.episodes(instrument=...) already filters by
    # instrument before candidates reach _episode_matches, so this branch is otherwise unreachable
    # through the public retrieve() API -- exercised directly for defense-in-depth, same convention as
    # Checkpoint 10's own white-box ConflictingDuplicateError test.
    from ai_trader.context_memory.retrieval import FLOOR_DIMENSIONS, _episode_matches
    from ai_trader.context_memory.episodes import collapse_into_episodes
    from ai_trader.context_memory.tests._fixtures import make_observation

    episode = collapse_into_episodes([make_observation(context_snapshot=make_snapshot(instrument="EURUSD"))])[0]
    query_snap = make_snapshot(instrument="XAUUSD")
    assert _episode_matches(episode, query_snap, FLOOR_DIMENSIONS) is False


def test_trend_d1_requires_relaxing_every_earlier_ladder_entry_too(tmp_path: Path) -> None:
    # Relaxation is CUMULATIVE in the fixed ladder order (never a sparse "only the differing
    # dimensions" set) -- trend_d1 sits at index 7, so matching a candidate that differs ONLY on
    # trend_d1 still requires relaxing every dimension ahead of it in the ladder (even though the
    # candidate agrees with the query on all of them), landing at tier 8.
    from ai_trader.context_memory.retrieval import RELAXATION_ORDER

    candidate = make_snapshot(as_of=AS_OF, trend_d1=ContextTrendDirection.DOWN)
    idx = _repo_with(tmp_path, [candidate])
    query_snap = make_snapshot(as_of=AS_OF + 1000, trend_d1=ContextTrendDirection.UP)
    result = retrieve(idx, _query(query_snap, AS_OF + 1000))
    assert result.status is RetrievalStatus.SUCCESSFUL
    assert result.selected_relaxation_tier == RELAXATION_ORDER.index("trend_d1") + 1
    assert result.matches[0].relaxed_dimensions == RELAXATION_ORDER[: RELAXATION_ORDER.index("trend_d1") + 1]
