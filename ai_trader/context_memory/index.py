"""Deterministic derived historical index -- Phase 7 Checkpoint 11.

`HistoricalIndex` is a REBUILDABLE, in-memory structure derived entirely from an already-persisted
`ContextMemoryRepository` (Checkpoint 10) -- it never mutates the repository, is never itself written to
disk, and is never a second source of truth: deleting it and rebuilding from the same repository state
always reproduces byte-identical results (proven by test). It adds episode collapsing (`episodes.py`)
and a small set of structural query methods on top of the repository's own bare
append/get/iterate/verify API -- no similarity, no ranking, no statistics (Checkpoint 12/13's own job).

**Indexed dimensions** (Checkpoint 11 §A): every categorical `ContextSnapshot` field
(`session_state`, `trend_*`, `structure_state`, `momentum_*`, `volatility_regime`, `liquidity_state`,
`expansion_state`, `multi_timeframe_agreement`, `data_quality_state`), `instrument`, `as_of`, PRESENT
edge (`strategy_id`), and outcome `status`/horizon. **No `timeframe` dimension is indexed** -- there is
no such field on `ContextSnapshot` to index (Checkpoint 9's own disclosed design choice: MI's real
top-level snapshot carries no single "timeframe" either, only per-sub-reading values already captured as
the four `trend_*`/`momentum_*` dimensions) -- "do not index fields that are not actually present in the
approved contracts," applied literally.

**Deterministic filter intersection**: `observations_matching()` accepts many optional keyword filters;
a query with N filters returns exactly the observations satisfying ALL N (a plain, deterministic set
intersection over already-sorted, already-deduplicated candidate lists -- never a ranked/scored result).

**Temporal safety**: every query method accepts an explicit `as_of_cutoff` (or, for outcomes,
`resolution_visible_as_of`) and excludes anything the query should not yet be able to see -- §below.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.context_memory.contracts import (
    ContextSnapshot,
    Observation,
    ObservationId,
    Outcome,
)
from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
)
from ai_trader.context_memory.episodes import Episode, collapse_into_episodes
from ai_trader.context_memory.identities import compute_observation_id
from ai_trader.context_memory.repository import ContextMemoryRepository


def _observation_sort_key(observation: Observation) -> tuple[int, str, str]:
    # (as_of, instrument, id) -- fully deterministic even when two observations for DIFFERENT
    # instruments happen to share the exact same as_of (Checkpoint 11 §G's own "equal-timestamp
    # behavior is explicitly defined" requirement).
    return (
        observation.context_snapshot.as_of,
        observation.context_snapshot.instrument,
        compute_observation_id(observation).value,
    )


@dataclass(frozen=True)
class IndexStatistics:
    """Raw vs. episode-aware counts -- Checkpoint 11 §E. ``episode_count`` is a CONSERVATIVE
    effective-observation proxy, never claimed to be a mathematically exact effective sample size
    (that determination, if ever made, belongs to Checkpoint 13's own statistical-sufficiency layer)."""

    raw_observation_count: int
    episode_count: int
    resolved_outcome_count: int
    unresolved_outcome_count: int


class HistoricalIndex:
    """Built once from a `ContextMemoryRepository` snapshot in time; call `rebuild()` to re-derive from
    the repository's current on-disk state (e.g. after another writer has appended more records)."""

    def __init__(self, repository: ContextMemoryRepository) -> None:
        self._repository = repository
        self.rebuild()

    def rebuild(self) -> None:
        observations = sorted(self._repository.iter_observations(), key=_observation_sort_key)
        self._observations: tuple[Observation, ...] = tuple(observations)
        self._observation_ids: tuple[ObservationId, ...] = tuple(compute_observation_id(o) for o in observations)
        self._observations_by_id: dict[str, Observation] = dict(zip((oid.value for oid in self._observation_ids), observations))
        self._episodes: tuple[Episode, ...] = collapse_into_episodes(observations)

        outcomes = tuple(self._repository.iter_outcomes())
        self._outcomes_by_observation_id: dict[str, list[Outcome]] = {}
        for outcome in outcomes:
            self._outcomes_by_observation_id.setdefault(outcome.observation_id.value, []).append(outcome)
        self._outcome_count = len(outcomes)
        self._resolved_outcome_count = sum(1 for o in outcomes if o.status.value == "RESOLVED")
        self._unresolved_outcome_count = self._outcome_count - self._resolved_outcome_count

    # ------------------------------------------------------------------ observations

    def observations_matching(
        self,
        *,
        instrument: str | None = None,
        as_of_before: int | None = None,
        session_state: str | None = None,
        trend_m15: ContextTrendDirection | None = None,
        trend_h1: ContextTrendDirection | None = None,
        trend_h4: ContextTrendDirection | None = None,
        trend_d1: ContextTrendDirection | None = None,
        structure_state: ContextStructureState | None = None,
        momentum_m15: ContextMomentumState | None = None,
        momentum_h1: ContextMomentumState | None = None,
        momentum_h4: ContextMomentumState | None = None,
        momentum_d1: ContextMomentumState | None = None,
        volatility_regime: ContextVolatilityRegime | None = None,
        liquidity_state: ContextLiquidityState | None = None,
        expansion_state: ContextExpansionState | None = None,
        multi_timeframe_agreement: ContextAgreementLevel | None = None,
        data_quality_state: ContextDataQualityState | None = None,
        present_edge_strategy_id: str | None = None,
    ) -> tuple[Observation, ...]:
        """Deterministic AND-intersection of every non-``None`` filter, in ``(as_of, instrument, id)``
        order. Passing no filters returns every observation in the index."""
        filters: dict[str, object] = {
            "instrument": instrument, "session_state": session_state,
            "trend_m15": trend_m15, "trend_h1": trend_h1, "trend_h4": trend_h4, "trend_d1": trend_d1,
            "structure_state": structure_state,
            "momentum_m15": momentum_m15, "momentum_h1": momentum_h1,
            "momentum_h4": momentum_h4, "momentum_d1": momentum_d1,
            "volatility_regime": volatility_regime, "liquidity_state": liquidity_state,
            "expansion_state": expansion_state, "multi_timeframe_agreement": multi_timeframe_agreement,
            "data_quality_state": data_quality_state,
        }
        active_filters = {k: v for k, v in filters.items() if v is not None}

        result = []
        for obs in self._observations:
            if as_of_before is not None and not (obs.context_snapshot.as_of < as_of_before):
                continue
            if any(getattr(obs.context_snapshot, field_name) != value for field_name, value in active_filters.items()):
                continue
            if present_edge_strategy_id is not None and not any(
                ref.strategy_id == present_edge_strategy_id for ref in obs.present_edges
            ):
                continue
            result.append(obs)
        return tuple(result)

    def observation_by_id(self, observation_id: ObservationId) -> Observation | None:
        return self._observations_by_id.get(observation_id.value)

    # ------------------------------------------------------------------ episodes

    def episodes(self, *, instrument: str | None = None, as_of_before: int | None = None) -> tuple[Episode, ...]:
        result = []
        for ep in self._episodes:
            if instrument is not None and ep.instrument != instrument:
                continue
            if as_of_before is not None and not (ep.end_as_of < as_of_before):
                continue
            result.append(ep)
        return tuple(result)

    def episodes_with_edge(
        self, strategy_id: str, *, instrument: str | None = None, as_of_before: int | None = None,
    ) -> tuple[Episode, ...]:
        return tuple(
            ep for ep in self.episodes(instrument=instrument, as_of_before=as_of_before)
            if any(ref.strategy_id == strategy_id for ref in ep.present_edges)
        )

    # ------------------------------------------------------------------ outcomes

    def outcomes_for_observation(
        self, observation_id: ObservationId, *, visible_as_of: int | None = None,
    ) -> tuple[Outcome, ...]:
        """Outcomes for one observation. When ``visible_as_of`` is given, excludes any outcome whose
        own `resolution_as_of` is AFTER that cutoff -- a resolved outcome that hadn't resolved yet as of
        the query time must not be visible, never re-labeled as pending (Checkpoint 11 §G). Unresolved
        outcomes (``resolution_as_of is None``) are always visible -- they never leak a future numeric
        result, only the (already-true) fact that resolution is still pending."""
        candidates = self._outcomes_for_observation(observation_id)
        if visible_as_of is None:
            return candidates
        return tuple(
            o for o in candidates if o.resolution_as_of is None or o.resolution_as_of <= visible_as_of
        )

    def _outcomes_for_observation(self, observation_id: ObservationId) -> tuple[Outcome, ...]:
        return tuple(self._outcomes_by_observation_id.get(observation_id.value, ()))

    # ------------------------------------------------------------------ statistics

    def statistics(self) -> IndexStatistics:
        return IndexStatistics(
            raw_observation_count=len(self._observations),
            episode_count=len(self._episodes),
            resolved_outcome_count=self._resolved_outcome_count,
            unresolved_outcome_count=self._unresolved_outcome_count,
        )
