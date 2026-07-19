"""Deterministic episode collapsing -- Phase 7 Checkpoint 11.

An **Episode** is a maximal contiguous run of `Observation`s (sorted by ``as_of``, per instrument) that
share the SAME `state_fingerprint` (the categorical "shape" of the market, deliberately excluding
``as_of`` itself) AND the SAME PRESENT-edge set -- Checkpoint 8 design's own §9.3 definition, implemented
here faithfully, not reinvented. This is the single most load-bearing mechanism in the whole Context
Memory design: without it, a multi-hour persistent regime on a 15-minute base timeframe would be counted
as dozens of independent, highly autocorrelated "observations," silently inflating apparent sample size
(Checkpoint 8 design §1, §12).

**Collapsing rule (deterministic, no statistical learning, Checkpoint 11 §D)** -- an episode boundary
occurs the moment ANY of the following changes between two as_of-consecutive observations for one
instrument:
- the `state_fingerprint` (folds in instrument, so an instrument change is automatically a boundary --
  no separate instrument rule needed; folds in `session_state`, so a session change is automatically a
  boundary too -- no separate session rule needed);
- the PRESENT-edge set (Checkpoint 8 design §9.3's own explicit requirement -- a strategy becoming
  PRESENT or ceasing to be PRESENT always starts a new episode, never silently folded into the old one);
- `market_intelligence_schema_version` (mixing evidence produced under two different upstream schema
  versions inside one "episode" could be semantically wrong even if the categorical VALUES happen to
  print identically -- a disclosed, conservative choice);
- `data_quality_state` is not `OK` (a degraded/stale/insufficient snapshot never starts OR extends an
  episode -- it ends whatever episode preceded it and is itself never a member of any episode; it
  remains fully retrievable as a raw `Observation` via the index, §index.py, just never through episode
  membership).

**No maximum temporal gap is enforced** (Checkpoint 11 §C's own "if needed" hedge, resolved here as "not
needed yet"): `ContextSnapshot` carries no declared bar-interval/timeframe field (a disclosed Checkpoint
9 design choice, §9's own docstring), so there is no non-arbitrary way to define "too large a gap"
without inventing an unvalidated threshold number -- exactly what this whole design's own discipline
forbids (Checkpoint 8 design §17, "do not select arbitrary thresholds without justification"). Episode
continuity is defined ENTIRELY by fingerprint/edge-set/version/quality equality across
as_of-consecutive observations, never by elapsed wall-clock time. Disclosed limitation: a large real-
world data gap (e.g. an outage) with an identical fingerprint on both sides would currently be treated as
one continuous episode -- flagged as an open question for a future checkpoint, not silently assumed safe.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from ai_trader.context_memory.contracts import (
    CONTEXT_MEMORY_SCHEMA_VERSION,
    ContextSnapshot,
    Observation,
    ObservationId,
    PresentEdgeReference,
)
from ai_trader.context_memory.enums import ContextDataQualityState
from ai_trader.context_memory.identities import (
    canonical_context_snapshot,
    canonical_present_edge_reference,
    canonical_schema_version,
    compute_observation_id,
)
from ai_trader.context_memory.validation import ContextMemoryValidationError, require_non_empty_str


@dataclass(frozen=True)
class StateFingerprint:
    """The categorical "shape" of one `ContextSnapshot`, EXCLUDING ``as_of`` -- the key episode
    membership is grouped by. Two snapshots at different times with an identical fingerprint represent
    the market looking the same way; that is the entire point of computing this separately from
    `ContextSnapshotId` (Checkpoint 9's own identity, which DOES include ``as_of`` and is therefore
    unique per instance, never a grouping key)."""

    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "StateFingerprint.value")


@dataclass(frozen=True)
class EpisodeId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "EpisodeId.value")


def _canonical_state_fingerprint_payload(snapshot: ContextSnapshot, present_edge_ids: tuple[str, ...]) -> dict[str, Any]:
    # Deliberately excludes as_of (the whole point) AND context_confidence_score/data_quality_state
    # (both are QUALITY gates, not market-state dimensions -- Checkpoint 9 §3.2's own reasoning, reused
    # here rather than re-litigated).
    return {
        "record_type": "context_memory.state_fingerprint",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "instrument": snapshot.instrument,
        "session_state": snapshot.session_state,
        "trend_m15": snapshot.trend_m15.value,
        "trend_h1": snapshot.trend_h1.value,
        "trend_h4": snapshot.trend_h4.value,
        "trend_d1": snapshot.trend_d1.value,
        "structure_state": snapshot.structure_state.value,
        "momentum_m15": snapshot.momentum_m15.value,
        "momentum_h1": snapshot.momentum_h1.value,
        "momentum_h4": snapshot.momentum_h4.value,
        "momentum_d1": snapshot.momentum_d1.value,
        "volatility_regime": snapshot.volatility_regime.value,
        "liquidity_state": snapshot.liquidity_state.value,
        "expansion_state": snapshot.expansion_state.value,
        "multi_timeframe_agreement": snapshot.multi_timeframe_agreement.value,
        "market_intelligence_schema_version": canonical_schema_version(snapshot.market_intelligence_schema_version),
        "present_edge_ids": sorted(present_edge_ids),
    }


def _hash_payload(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_state_fingerprint(snapshot: ContextSnapshot, present_edge_ids: Sequence[str]) -> StateFingerprint:
    return StateFingerprint(_hash_payload(_canonical_state_fingerprint_payload(snapshot, tuple(present_edge_ids))))


@dataclass(frozen=True)
class Episode:
    """One collapsed, persistent market-context state, spanning one or more `Observation`s that all
    share the same `state_fingerprint` and PRESENT-edge set. ``representative_context_snapshot`` is the
    FIRST observation's own snapshot in the episode -- Checkpoint 8 design §9.3's own choice: "the
    episode's own resolution point for outcome measurement is the FIRST bar of the run (the moment the
    context first became this shape)"."""

    instrument: str
    state_fingerprint: StateFingerprint
    start_as_of: int
    end_as_of: int
    representative_context_snapshot: ContextSnapshot
    present_edges: tuple[PresentEdgeReference, ...]
    observation_ids: tuple[ObservationId, ...]

    def __post_init__(self) -> None:
        require_non_empty_str(self.instrument, "Episode.instrument")
        if not isinstance(self.state_fingerprint, StateFingerprint):
            raise ContextMemoryValidationError("Episode.state_fingerprint must be a StateFingerprint")
        if self.end_as_of < self.start_as_of:
            raise ContextMemoryValidationError(
                f"Episode.end_as_of ({self.end_as_of}) must not precede start_as_of ({self.start_as_of})"
            )
        if not self.observation_ids:
            raise ContextMemoryValidationError("Episode.observation_ids must contain at least one observation")


def _canonical_episode_payload(episode: Episode) -> dict[str, Any]:
    return {
        "record_type": "context_memory.episode",
        "context_memory_schema_version": canonical_schema_version(CONTEXT_MEMORY_SCHEMA_VERSION),
        "instrument": episode.instrument,
        "state_fingerprint": episode.state_fingerprint.value,
        "start_as_of": episode.start_as_of,
        "end_as_of": episode.end_as_of,
        "representative_context_snapshot": canonical_context_snapshot(episode.representative_context_snapshot),
        "present_edges": [canonical_present_edge_reference(ref) for ref in episode.present_edges],
        "observation_ids": [oid.value for oid in episode.observation_ids],  # already as_of-ordered by construction
    }


def compute_episode_id(episode: Episode) -> EpisodeId:
    return EpisodeId(_hash_payload(_canonical_episode_payload(episode)))


def collapse_into_episodes(observations: Sequence[Observation]) -> tuple[Episode, ...]:
    """The deterministic collapsing algorithm (Checkpoint 11 §D). Groups ``observations`` (any order --
    canonically re-sorted here by ``(as_of, instrument, context_snapshot_id)`` before processing, so
    caller-supplied order never changes the result) into maximal contiguous, same-fingerprint,
    same-edge-set, same-schema-version, `OK`-data-quality runs, one per instrument. Observations with
    `data_quality_state != OK` are excluded from every episode (they neither start nor extend one) but
    do end whatever episode preceded them for that instrument."""
    ordered = sorted(
        observations,
        key=lambda o: (o.context_snapshot.as_of, o.context_snapshot.instrument, compute_observation_id(o).value),
    )

    by_instrument: dict[str, list[Observation]] = {}
    for obs in ordered:
        by_instrument.setdefault(obs.context_snapshot.instrument, []).append(obs)

    episodes: list[Episode] = []
    for instrument in sorted(by_instrument):
        episodes.extend(_collapse_one_instrument(by_instrument[instrument]))
    return tuple(episodes)


def _collapse_one_instrument(observations: list[Observation]) -> list[Episode]:
    episodes: list[Episode] = []
    current: list[Observation] = []
    current_fingerprint: StateFingerprint | None = None
    current_mi_version: str | None = None

    def _flush() -> None:
        if not current:
            return
        first, last = current[0], current[-1]
        assert current_fingerprint is not None
        episodes.append(
            Episode(
                instrument=first.context_snapshot.instrument,
                state_fingerprint=current_fingerprint,
                start_as_of=first.context_snapshot.as_of,
                end_as_of=last.context_snapshot.as_of,
                representative_context_snapshot=first.context_snapshot,
                present_edges=first.present_edges,
                observation_ids=tuple(compute_observation_id(o) for o in current),
            )
        )

    for obs in observations:
        snapshot = obs.context_snapshot
        if snapshot.data_quality_state is not ContextDataQualityState.OK:
            _flush()
            current, current_fingerprint, current_mi_version = [], None, None
            continue

        edge_ids = tuple(sorted(ref.strategy_id for ref in obs.present_edges))
        fingerprint = compute_state_fingerprint(snapshot, edge_ids)
        mi_version = f"{snapshot.market_intelligence_schema_version.namespace}:{snapshot.market_intelligence_schema_version.version}"

        if current and (fingerprint != current_fingerprint or mi_version != current_mi_version):
            _flush()
            current = []

        current.append(obs)
        current_fingerprint = fingerprint
        current_mi_version = mi_version

    _flush()
    return episodes
