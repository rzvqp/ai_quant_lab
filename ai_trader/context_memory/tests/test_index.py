"""Unit tests for :mod:`ai_trader.context_memory.index`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory.contracts import Observation, Outcome, SchemaVersion
from ai_trader.context_memory.enums import (
    ContextTrendDirection,
    HorizonUnit,
    OutcomeKind,
    OutcomeStatus,
    SourceType,
)
from ai_trader.context_memory.index import HistoricalIndex
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.context_memory.tests._fixtures import AS_OF, make_edge_reference, make_snapshot


def _repo_with(tmp_path: Path, snapshots: list) -> tuple[ContextMemoryRepository, list]:
    repo = ContextMemoryRepository(tmp_path / "repo")
    ref = make_edge_reference("S1")
    obs_ids = []
    for snap in snapshots:
        obs = Observation(context_snapshot=snap, present_edges=(ref,))
        obs_ids.append(repo.append_observation(obs))
    return repo, obs_ids


# ------------------------------------------------------------------ rebuild / determinism


def test_deterministic_index_rebuild(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + i * 900) for i in range(3)])
    idx1 = HistoricalIndex(repo)
    idx2 = HistoricalIndex(repo)
    assert idx1.statistics() == idx2.statistics()
    assert idx1.observations_matching() == idx2.observations_matching()


def test_rebuild_equivalence_after_repository_reopen(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + i * 900) for i in range(3)])
    idx1 = HistoricalIndex(repo)

    repo2 = ContextMemoryRepository(tmp_path / "repo")  # fresh instance, same path
    idx2 = HistoricalIndex(repo2)

    assert idx1.statistics() == idx2.statistics()
    assert idx1.observations_matching() == idx2.observations_matching()


def test_rebuild_reflects_new_appends(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    idx = HistoricalIndex(repo)
    assert idx.statistics().raw_observation_count == 1

    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF + 900), present_edges=(make_edge_reference("S1"),)))
    idx.rebuild()
    assert idx.statistics().raw_observation_count == 2


# ------------------------------------------------------------------ filtering


def test_exact_filter_behavior(tmp_path: Path) -> None:
    repo, _ = _repo_with(
        tmp_path,
        [
            make_snapshot(as_of=AS_OF, trend_m15=ContextTrendDirection.UP),
            make_snapshot(as_of=AS_OF + 900, trend_m15=ContextTrendDirection.DOWN),
        ],
    )
    idx = HistoricalIndex(repo)
    up = idx.observations_matching(trend_m15=ContextTrendDirection.UP)
    assert len(up) == 1
    assert up[0].context_snapshot.trend_m15 is ContextTrendDirection.UP


def test_multi_filter_intersection(tmp_path: Path) -> None:
    from ai_trader.context_memory.enums import ContextVolatilityRegime

    repo, _ = _repo_with(
        tmp_path,
        [
            make_snapshot(as_of=AS_OF, trend_m15=ContextTrendDirection.UP, volatility_regime=ContextVolatilityRegime.HIGH),
            make_snapshot(as_of=AS_OF + 900, trend_m15=ContextTrendDirection.UP, volatility_regime=ContextVolatilityRegime.NORMAL),
            make_snapshot(as_of=AS_OF + 1800, trend_m15=ContextTrendDirection.DOWN, volatility_regime=ContextVolatilityRegime.HIGH),
        ],
    )
    idx = HistoricalIndex(repo)
    result = idx.observations_matching(trend_m15=ContextTrendDirection.UP, volatility_regime=ContextVolatilityRegime.HIGH)
    assert len(result) == 1
    assert result[0].context_snapshot.as_of == AS_OF


def test_present_edge_filter(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF), present_edges=(make_edge_reference("S1"),)))
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF + 900), present_edges=(make_edge_reference("S7"),)))
    idx = HistoricalIndex(repo)
    assert len(idx.observations_matching(present_edge_strategy_id="S1")) == 1
    assert len(idx.observations_matching(present_edge_strategy_id="S9")) == 0


def test_no_filters_returns_everything(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + i * 900) for i in range(4)])
    idx = HistoricalIndex(repo)
    assert len(idx.observations_matching()) == 4


# ------------------------------------------------------------------ as-of cutoff / temporal safety


def test_as_of_cutoff_excludes_future_observations(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + i * 900) for i in range(5)])
    idx = HistoricalIndex(repo)
    result = idx.observations_matching(as_of_before=AS_OF + 1800)
    assert [o.context_snapshot.as_of for o in result] == [AS_OF, AS_OF + 900]


def test_as_of_cutoff_is_strict_exclusive(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    idx = HistoricalIndex(repo)
    # a cutoff EQUAL to the observation's own as_of must exclude it -- the current query moment cannot
    # retroactively become its own history.
    assert idx.observations_matching(as_of_before=AS_OF) == ()
    assert len(idx.observations_matching(as_of_before=AS_OF + 1)) == 1


def test_future_outcome_resolution_excluded_when_not_yet_visible(tmp_path: Path) -> None:
    repo, obs_ids = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    outcome = Outcome(
        observation_id=obs_ids[0], strategy_id="S1", horizon=20, horizon_unit=HorizonUnit.BARS,
        outcome_definition_version=SchemaVersion("outcome_definition", "od-v1"), status=OutcomeStatus.RESOLVED,
        observation_as_of=AS_OF, normalized_result=0.3, resolution_as_of=AS_OF + 5000,
        cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.SHADOW_EVIDENCE_ADAPTER,
        outcome_kind=OutcomeKind.STRATEGY, unavailable_reason=None,
    )
    repo.append_outcome(outcome)
    idx = HistoricalIndex(repo)

    assert idx.outcomes_for_observation(obs_ids[0], visible_as_of=AS_OF + 1000) == ()
    assert idx.outcomes_for_observation(obs_ids[0], visible_as_of=AS_OF + 5000) == (outcome,)
    assert idx.outcomes_for_observation(obs_ids[0]) == (outcome,)  # no cutoff -> everything visible


def test_pending_outcome_always_visible_regardless_of_cutoff(tmp_path: Path) -> None:
    repo, obs_ids = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    outcome = Outcome(
        observation_id=obs_ids[0], strategy_id="S1", horizon=20, horizon_unit=HorizonUnit.BARS,
        outcome_definition_version=SchemaVersion("outcome_definition", "od-v1"), status=OutcomeStatus.PENDING,
        observation_as_of=AS_OF, normalized_result=None, resolution_as_of=None,
        cost_model_ref="GROSS_NO_COSTS", source_type=SourceType.SHADOW_EVIDENCE_ADAPTER,
        outcome_kind=OutcomeKind.STRATEGY, unavailable_reason=None,
    )
    repo.append_outcome(outcome)
    idx = HistoricalIndex(repo)
    assert idx.outcomes_for_observation(obs_ids[0], visible_as_of=AS_OF) == (outcome,)


# ------------------------------------------------------------------ episodes via index


def test_episodes_query(tmp_path: Path) -> None:
    repo, _ = _repo_with(
        tmp_path,
        [
            make_snapshot(as_of=AS_OF, trend_m15=ContextTrendDirection.UP),
            make_snapshot(as_of=AS_OF + 900, trend_m15=ContextTrendDirection.UP),
            make_snapshot(as_of=AS_OF + 1800, trend_m15=ContextTrendDirection.DOWN),
        ],
    )
    idx = HistoricalIndex(repo)
    assert len(idx.episodes()) == 2
    assert idx.statistics().episode_count == 2
    assert idx.statistics().raw_observation_count == 3


def test_episodes_with_edge(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF), present_edges=(make_edge_reference("S1"),)))
    idx = HistoricalIndex(repo)
    assert len(idx.episodes_with_edge("S1")) == 1
    assert len(idx.episodes_with_edge("S9")) == 0


def test_episodes_instrument_filter(tmp_path: Path) -> None:
    repo = ContextMemoryRepository(tmp_path / "repo")
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF, instrument="XAUUSD"), present_edges=(make_edge_reference("S1"),)))
    repo.append_observation(Observation(context_snapshot=make_snapshot(as_of=AS_OF + 900, instrument="EURUSD"), present_edges=(make_edge_reference("S1"),)))
    idx = HistoricalIndex(repo)
    xau_only = idx.episodes(instrument="XAUUSD")
    assert len(xau_only) == 1
    assert xau_only[0].instrument == "XAUUSD"


def test_episodes_as_of_cutoff(tmp_path: Path) -> None:
    repo, _ = _repo_with(
        tmp_path,
        [
            make_snapshot(as_of=AS_OF, trend_m15=ContextTrendDirection.UP),
            make_snapshot(as_of=AS_OF + 1800, trend_m15=ContextTrendDirection.DOWN),
        ],
    )
    idx = HistoricalIndex(repo)
    assert len(idx.episodes(as_of_before=AS_OF + 900)) == 1
    assert len(idx.episodes()) == 2


# ------------------------------------------------------------------ observation_by_id / source unchanged


def test_observation_by_id(tmp_path: Path) -> None:
    repo, obs_ids = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF)])
    idx = HistoricalIndex(repo)
    result = idx.observation_by_id(obs_ids[0])
    assert result is not None
    assert result.context_snapshot.as_of == AS_OF


def test_source_repository_remains_unchanged_after_indexing(tmp_path: Path) -> None:
    repo, _ = _repo_with(tmp_path, [make_snapshot(as_of=AS_OF + i * 900) for i in range(3)])
    count_before = repo.count_observations()
    HistoricalIndex(repo)
    assert repo.count_observations() == count_before
    assert repo.verify_integrity().ok
