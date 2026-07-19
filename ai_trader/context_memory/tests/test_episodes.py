"""Unit tests for :mod:`ai_trader.context_memory.episodes`."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.context_memory.enums import ContextDataQualityState, ContextTrendDirection
from ai_trader.context_memory.episodes import (
    Episode,
    collapse_into_episodes,
    compute_episode_id,
    compute_state_fingerprint,
)
from ai_trader.context_memory.tests._fixtures import AS_OF, make_edge_reference, make_observation, make_snapshot
from ai_trader.context_memory.validation import ContextMemoryValidationError


def _obs_at(as_of: int, **snapshot_overrides: object) -> object:
    return make_observation(context_snapshot=make_snapshot(as_of=as_of, **snapshot_overrides))


# ------------------------------------------------------------------ state fingerprint


def test_fingerprint_excludes_as_of() -> None:
    a = compute_state_fingerprint(make_snapshot(as_of=AS_OF), ["S1"])
    b = compute_state_fingerprint(make_snapshot(as_of=AS_OF + 900), ["S1"])
    assert a == b


def test_fingerprint_differs_on_trend() -> None:
    a = compute_state_fingerprint(make_snapshot(trend_m15=ContextTrendDirection.UP), ["S1"])
    b = compute_state_fingerprint(make_snapshot(trend_m15=ContextTrendDirection.DOWN), ["S1"])
    assert a != b


def test_fingerprint_differs_on_instrument() -> None:
    a = compute_state_fingerprint(make_snapshot(instrument="XAUUSD"), ["S1"])
    b = compute_state_fingerprint(make_snapshot(instrument="EURUSD"), ["S1"])
    assert a != b


def test_fingerprint_differs_on_present_edges() -> None:
    a = compute_state_fingerprint(make_snapshot(), ["S1"])
    b = compute_state_fingerprint(make_snapshot(), ["S1", "S2"])
    assert a != b


def test_fingerprint_ignores_present_edge_order() -> None:
    a = compute_state_fingerprint(make_snapshot(), ["S1", "S2"])
    b = compute_state_fingerprint(make_snapshot(), ["S2", "S1"])
    assert a == b


def test_fingerprint_ignores_confidence_and_quality() -> None:
    a = compute_state_fingerprint(make_snapshot(context_confidence_score=0.9, data_quality_state=ContextDataQualityState.OK), ["S1"])
    b = compute_state_fingerprint(make_snapshot(context_confidence_score=0.1, data_quality_state=ContextDataQualityState.OK), ["S1"])
    assert a == b


# ------------------------------------------------------------------ Episode contract


def test_episode_rejects_end_before_start() -> None:
    snap = make_snapshot()
    fp = compute_state_fingerprint(snap, [])
    with pytest.raises(ContextMemoryValidationError):
        Episode(
            instrument="XAUUSD", state_fingerprint=fp, start_as_of=AS_OF + 100, end_as_of=AS_OF,
            representative_context_snapshot=snap, present_edges=(), observation_ids=(),
        )


def test_episode_rejects_empty_observation_ids() -> None:
    snap = make_snapshot()
    fp = compute_state_fingerprint(snap, [])
    with pytest.raises(ContextMemoryValidationError):
        Episode(
            instrument="XAUUSD", state_fingerprint=fp, start_as_of=AS_OF, end_as_of=AS_OF,
            representative_context_snapshot=snap, present_edges=(), observation_ids=(),
        )


def test_episode_rejects_non_state_fingerprint_type() -> None:
    from ai_trader.context_memory.contracts import ObservationId

    snap = make_snapshot()
    with pytest.raises(ContextMemoryValidationError):
        Episode(
            instrument="XAUUSD", state_fingerprint="not-a-fingerprint",  # type: ignore[arg-type]
            start_as_of=AS_OF, end_as_of=AS_OF,
            representative_context_snapshot=snap, present_edges=(), observation_ids=(ObservationId("x" * 64),),
        )


def test_episode_immutable() -> None:
    from ai_trader.context_memory.contracts import ObservationId

    snap = make_snapshot()
    fp = compute_state_fingerprint(snap, [])
    ep = Episode(
        instrument="XAUUSD", state_fingerprint=fp, start_as_of=AS_OF, end_as_of=AS_OF,
        representative_context_snapshot=snap, present_edges=(), observation_ids=(ObservationId("x" * 64),),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        ep.instrument = "EURUSD"  # type: ignore[misc]


# ------------------------------------------------------------------ collapse_into_episodes


def test_single_persistent_regime_collapses_to_one_episode() -> None:
    obs = [_obs_at(AS_OF + i * 900) for i in range(5)]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 1
    assert len(episodes[0].observation_ids) == 5
    assert episodes[0].start_as_of == AS_OF
    assert episodes[0].end_as_of == AS_OF + 4 * 900


def test_context_change_splits_episode() -> None:
    obs = [
        _obs_at(AS_OF, trend_m15=ContextTrendDirection.UP),
        _obs_at(AS_OF + 900, trend_m15=ContextTrendDirection.UP),
        _obs_at(AS_OF + 1800, trend_m15=ContextTrendDirection.DOWN),
        _obs_at(AS_OF + 2700, trend_m15=ContextTrendDirection.DOWN),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 2
    assert [len(e.observation_ids) for e in episodes] == [2, 2]


def test_session_change_splits_episode_via_fingerprint() -> None:
    # No separate session rule exists -- session_state is itself part of the fingerprint.
    obs = [
        _obs_at(AS_OF, session_state="LONDON"),
        _obs_at(AS_OF + 900, session_state="NY"),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 2


def test_instrument_isolation() -> None:
    obs = [
        _obs_at(AS_OF, instrument="XAUUSD"),
        _obs_at(AS_OF + 900, instrument="EURUSD"),
        _obs_at(AS_OF + 1800, instrument="XAUUSD"),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    # instrument-sorted processing -- 2 XAUUSD episodes are NOT reunited across the EURUSD one, and
    # each instrument is processed as its own independent as_of-ordered sequence.
    instruments = {e.instrument for e in episodes}
    assert instruments == {"XAUUSD", "EURUSD"}
    xau_episodes = [e for e in episodes if e.instrument == "XAUUSD"]
    assert len(xau_episodes) == 1  # both XAUUSD observations DO collapse together (same fingerprint,
    # instrument-partitioned before ordering -- the EURUSD observation in between never breaks them)


def test_present_edge_set_change_splits_episode() -> None:
    ref_s1 = make_edge_reference("S1")
    ref_s2 = make_edge_reference("S2")
    snap1 = make_snapshot(as_of=AS_OF)
    snap2 = make_snapshot(as_of=AS_OF + 900)
    obs = [
        make_observation(context_snapshot=snap1, present_edges=(ref_s1,)),
        make_observation(context_snapshot=snap2, present_edges=(ref_s1, ref_s2)),
    ]
    episodes = collapse_into_episodes(obs)
    assert len(episodes) == 2


def test_market_intelligence_schema_version_change_splits_episode() -> None:
    obs = [
        _obs_at(AS_OF, market_intelligence_schema_version=SchemaVersion("market_intelligence", "mi-v1")),
        _obs_at(AS_OF + 900, market_intelligence_schema_version=SchemaVersion("market_intelligence", "mi-v2")),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 2


def test_degraded_data_quality_excludes_observation_and_splits() -> None:
    obs = [
        _obs_at(AS_OF, data_quality_state=ContextDataQualityState.OK),
        _obs_at(AS_OF + 900, data_quality_state=ContextDataQualityState.STALE),
        _obs_at(AS_OF + 1800, data_quality_state=ContextDataQualityState.OK),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 2  # the STALE observation belongs to neither
    total_observations_in_episodes = sum(len(e.observation_ids) for e in episodes)
    assert total_observations_in_episodes == 2  # the STALE one is excluded entirely


def test_degraded_data_quality_as_final_observation_yields_no_trailing_empty_episode() -> None:
    # The trailing STALE observation triggers a flush of the preceding run and resets `current` to
    # empty; the loop then ends with nothing further appended, so the unconditional final `_flush()`
    # call must be a no-op rather than emitting a bogus empty episode.
    obs = [
        _obs_at(AS_OF, data_quality_state=ContextDataQualityState.OK),
        _obs_at(AS_OF + 900, data_quality_state=ContextDataQualityState.STALE),
    ]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 1
    assert len(episodes[0].observation_ids) == 1


def test_no_gap_based_split_disclosed_limitation() -> None:
    # A large real-world time gap with an IDENTICAL fingerprint on both sides is currently treated as
    # ONE continuous episode -- the disclosed limitation from this module's own docstring, verified here
    # so a future change to this behavior is a deliberate, visible decision, not an accidental one.
    obs = [_obs_at(AS_OF), _obs_at(AS_OF + 10_000_000)]  # ~116 days apart
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert len(episodes) == 1


def test_caller_order_does_not_affect_result() -> None:
    obs = [_obs_at(AS_OF + i * 900, trend_m15=ContextTrendDirection.UP if i < 3 else ContextTrendDirection.DOWN) for i in range(6)]
    forward = collapse_into_episodes(obs)  # type: ignore[arg-type]
    backward = collapse_into_episodes(list(reversed(obs)))  # type: ignore[arg-type]
    assert [(e.start_as_of, e.end_as_of) for e in forward] == [(e.start_as_of, e.end_as_of) for e in backward]


def test_empty_input_yields_no_episodes() -> None:
    assert collapse_into_episodes([]) == ()


# ------------------------------------------------------------------ episode identity


def test_episode_id_is_deterministic() -> None:
    obs = [_obs_at(AS_OF), _obs_at(AS_OF + 900)]
    a = collapse_into_episodes(obs)  # type: ignore[arg-type]
    b = collapse_into_episodes(obs)  # type: ignore[arg-type]
    assert compute_episode_id(a[0]) == compute_episode_id(b[0])


def test_episode_id_differs_on_content() -> None:
    obs_a = [_obs_at(AS_OF, trend_m15=ContextTrendDirection.UP)]
    obs_b = [_obs_at(AS_OF, trend_m15=ContextTrendDirection.DOWN)]
    a = collapse_into_episodes(obs_a)  # type: ignore[arg-type]
    b = collapse_into_episodes(obs_b)  # type: ignore[arg-type]
    assert compute_episode_id(a[0]) != compute_episode_id(b[0])


def test_episode_id_fixed_expected_value() -> None:
    # A hardcoded, independently-computed expected hash (not self-referential) -- computed once via a
    # standalone script before this test was written, same discipline as every prior checkpoint's own
    # "fixed expected identity value" test.
    obs = [_obs_at(AS_OF), _obs_at(AS_OF + 900)]
    episodes = collapse_into_episodes(obs)  # type: ignore[arg-type]
    result = compute_episode_id(episodes[0])
    assert result.value == "a952a63c76c5ac603e328f08ea946d7165df221eb1bfb427fd742d76d4f97d4e"
