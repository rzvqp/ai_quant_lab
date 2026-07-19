"""Deterministic historical-context retrieval -- Phase 7 Checkpoint 12.

Implements the fixed-priority **relaxation ladder** recommended by the accepted
``PHASE_7_CHECKPOINT_8_CONTEXT_MEMORY_DESIGN.md`` §8: a query is matched against historical `Episode`s
(Checkpoint 11) first on an EXACT match across all 14 categorical similarity dimensions; if that yields
no eligible episode, exactly one dimension is relaxed at a time, in the design doc's own disclosed
priority order, until either an episode is found or a hard floor (never "relax everything") is reached.
There is no weighted distance, no k-NN, no embedding, no clustering, no adaptive/learned ordering
anywhere in this module -- relaxation always proceeds in the SAME fixed, versioned order regardless of
query content, and the relaxation path itself IS the similarity explanation (no opaque numeric score).

**Relaxation order** (design doc §8's own proposed order, adopted verbatim -- "a reasoned starting
point, not final," per the design doc's own §17 disclosure; not re-litigated here):
``session_state -> expansion_state -> liquidity_state -> momentum_d1 -> momentum_h4 -> momentum_h1 ->
momentum_m15 -> trend_d1 -> trend_h4 -> trend_h1 -> trend_m15``. The floor (never relaxed) is
``instrument`` (a query-scope parameter, not a relaxed dimension -- retrieval never crosses instruments)
plus ``structure_state``, ``volatility_regime``, ``multi_timeframe_agreement`` -- the three dimensions
the design doc identifies as carrying the most information about whether a historical context resembles
the current one at all.

**Minimum-sample floor is deliberately NOT implemented here.** The design doc's own §17 leaves the exact
numeric threshold unresolved ("a reasoned starting point, not final"); Checkpoint 12's own mission
explicitly forbids inventing an arbitrary minimum-sample threshold and instead directs deferring
sufficiency classification to Checkpoint 13's own explicit, versioned policy object. The SMALLEST,
non-arbitrary, conservative choice made here: a tier is accepted as soon as it yields **at least one**
eligible episode (the smallest meaningful non-zero count) -- this is a "some evidence found" signal, not
a sufficiency judgment; ``SUCCESSFUL`` here says nothing about whether the evidence is enough to act on.

**Temporal safety**: every query requires an explicit ``as_of_cutoff``; only episodes whose
``end_as_of < as_of_cutoff`` are ever eligible (a strict, exclusive cutoff, matching Checkpoint 11's own
convention) -- the current context can never retrieve itself, which falls out structurally rather than
needing a separate self-exclusion check (same reasoning as design doc §9.5).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from ai_trader.context_memory.contracts import (
    MARKET_INTELLIGENCE_SCHEMA_VERSION,
    ContextSnapshot,
    ContextSnapshotId,
    SchemaVersion,
)
from ai_trader.context_memory.enums import ContextDataQualityState
from ai_trader.context_memory.episodes import Episode, EpisodeId, compute_episode_id
from ai_trader.context_memory.identities import compute_context_snapshot_id
from ai_trader.context_memory.index import HistoricalIndex
from ai_trader.context_memory.validation import ContextMemoryValidationError, require_non_empty_str, require_positive_int

RETRIEVAL_POLICY_VERSION = SchemaVersion("context_memory_retrieval", "cmr-v1")

# Fixed relaxation order -- design doc §8, adopted verbatim. Index 0 is relaxed first (Tier 1);
# index len-1 is relaxed last (the deepest non-floor tier).
RELAXATION_ORDER: tuple[str, ...] = (
    "session_state",
    "expansion_state",
    "liquidity_state",
    "momentum_d1",
    "momentum_h4",
    "momentum_h1",
    "momentum_m15",
    "trend_d1",
    "trend_h4",
    "trend_h1",
    "trend_m15",
)

# Never relaxed -- the floor. `instrument` is a query-scope gate, not a categorical similarity
# dimension, so it is checked separately from this tuple (never appears in RELAXATION_ORDER).
FLOOR_DIMENSIONS: tuple[str, ...] = ("structure_state", "volatility_regime", "multi_timeframe_agreement")


class RetrievalStatus(str, enum.Enum):
    SUCCESSFUL = "SUCCESSFUL"
    NO_ELIGIBLE_HISTORY = "NO_ELIGIBLE_HISTORY"
    NO_SUFFICIENTLY_SIMILAR = "NO_SUFFICIENTLY_SIMILAR"
    INCOMPATIBLE = "INCOMPATIBLE"
    DEGRADED_DATA = "DEGRADED_DATA"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"


@dataclass(frozen=True)
class RetrievalQuery:
    """Immutable query contract (Checkpoint 12 §A). ``context_snapshot`` supplies both the instrument
    scope and every categorical dimension value the ladder matches against; it need not itself be a
    stored `Observation` -- a live, as-yet-unpersisted snapshot is equally valid."""

    context_snapshot: ContextSnapshot
    as_of_cutoff: int
    edge_scope: tuple[str, ...] | None = None
    max_candidates: int | None = None
    retrieval_policy_version: SchemaVersion = field(default=RETRIEVAL_POLICY_VERSION)

    def __post_init__(self) -> None:
        if not isinstance(self.context_snapshot, ContextSnapshot):
            raise ContextMemoryValidationError("RetrievalQuery.context_snapshot must be a ContextSnapshot")
        require_positive_int(self.as_of_cutoff, "RetrievalQuery.as_of_cutoff")
        if self.edge_scope is not None:
            if len(self.edge_scope) == 0:
                raise ContextMemoryValidationError("RetrievalQuery.edge_scope must be None or non-empty")
            for strategy_id in self.edge_scope:
                require_non_empty_str(strategy_id, "RetrievalQuery.edge_scope entry")
        if self.max_candidates is not None:
            require_positive_int(self.max_candidates, "RetrievalQuery.max_candidates")
        if not isinstance(self.retrieval_policy_version, SchemaVersion):
            raise ContextMemoryValidationError("RetrievalQuery.retrieval_policy_version must be a SchemaVersion")


@dataclass(frozen=True)
class RetrievalMatch:
    """One retrieved historical episode plus its own similarity explanation -- no opaque numeric score;
    the tier reached and the exact dimensions matched/relaxed together ARE the explanation."""

    episode: Episode
    episode_id: EpisodeId
    matched_dimensions: tuple[str, ...]
    relaxed_dimensions: tuple[str, ...]
    unavailable_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalResult:
    """Immutable retrieval outcome (Checkpoint 12 §B). Always reports enough to audit itself -- query
    identity, both cutoffs, the tier reached, raw vs. episode-aware counts, and every exclusion reason --
    never a bare match list."""

    status: RetrievalStatus
    query_context_id: ContextSnapshotId
    retrieval_policy_version: SchemaVersion
    as_of_cutoff: int
    index_max_as_of: int | None
    selected_relaxation_tier: int | None
    raw_eligible_observation_count: int
    eligible_episode_count: int
    returned_count: int
    matches: tuple[RetrievalMatch, ...]
    exclusion_reasons: tuple[str, ...]
    limitations: tuple[str, ...]
    no_sufficient_history_reason: str | None


def _dimension_value(snapshot: ContextSnapshot, dimension: str) -> Any:
    return getattr(snapshot, dimension)


def _required_dimensions_at_tier(tier: int) -> tuple[str, ...]:
    """Tier 0 = every dimension required (exact match). Tier N (1 <= N <= len(RELAXATION_ORDER))
    additionally drops the first N entries of RELAXATION_ORDER from the requirement, in order."""
    still_required = RELAXATION_ORDER[tier:]
    return FLOOR_DIMENSIONS + still_required


def _episode_matches(episode: Episode, query_snapshot: ContextSnapshot, required_dimensions: tuple[str, ...]) -> bool:
    candidate = episode.representative_context_snapshot
    if candidate.instrument != query_snapshot.instrument:
        return False
    return all(_dimension_value(candidate, dim) == _dimension_value(query_snapshot, dim) for dim in required_dimensions)


def _match_sort_key(match: RetrievalMatch) -> tuple[int, str]:
    # Recency-weighted: most recent episode first (negated end_as_of sorts descending-recency
    # ascending), episode ID as the final fixed, disclosed tie-break on an exact recency tie.
    return (-match.episode.end_as_of, match.episode_id.value)


def retrieve(index: HistoricalIndex, query: RetrievalQuery) -> RetrievalResult:
    query_context_id = compute_context_snapshot_id(query.context_snapshot)
    all_observations = index.observations_matching()
    index_max_as_of = max((o.context_snapshot.as_of for o in all_observations), default=None)

    if query.retrieval_policy_version != RETRIEVAL_POLICY_VERSION:
        return RetrievalResult(
            status=RetrievalStatus.INCOMPATIBLE, query_context_id=query_context_id,
            retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
            index_max_as_of=index_max_as_of, selected_relaxation_tier=None,
            raw_eligible_observation_count=0, eligible_episode_count=0, returned_count=0, matches=(),
            exclusion_reasons=("retrieval_policy_version is not one this module supports",),
            limitations=(), no_sufficient_history_reason=None,
        )

    if query.context_snapshot.market_intelligence_schema_version != MARKET_INTELLIGENCE_SCHEMA_VERSION:
        return RetrievalResult(
            status=RetrievalStatus.UNSUPPORTED_VERSION, query_context_id=query_context_id,
            retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
            index_max_as_of=index_max_as_of, selected_relaxation_tier=None,
            raw_eligible_observation_count=0, eligible_episode_count=0, returned_count=0, matches=(),
            exclusion_reasons=("query context_snapshot's market_intelligence_schema_version is not supported by this retrieval module",),
            limitations=(), no_sufficient_history_reason=None,
        )

    if query.context_snapshot.data_quality_state is not ContextDataQualityState.OK:
        return RetrievalResult(
            status=RetrievalStatus.DEGRADED_DATA, query_context_id=query_context_id,
            retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
            index_max_as_of=index_max_as_of, selected_relaxation_tier=None,
            raw_eligible_observation_count=0, eligible_episode_count=0, returned_count=0, matches=(),
            exclusion_reasons=("query context_snapshot itself is not data_quality_state OK",),
            limitations=(), no_sufficient_history_reason=None,
        )

    eligible_episodes = [
        ep for ep in index.episodes(instrument=query.context_snapshot.instrument, as_of_before=query.as_of_cutoff)
        if ep.representative_context_snapshot.data_quality_state is ContextDataQualityState.OK
        and ep.representative_context_snapshot.market_intelligence_schema_version == MARKET_INTELLIGENCE_SCHEMA_VERSION
    ]
    if query.edge_scope is not None:
        eligible_episodes = [
            ep for ep in eligible_episodes if any(ref.strategy_id in query.edge_scope for ref in ep.present_edges)
        ]

    raw_eligible_observation_count = sum(len(ep.observation_ids) for ep in eligible_episodes)
    eligible_episode_count = len(eligible_episodes)

    if eligible_episode_count == 0:
        return RetrievalResult(
            status=RetrievalStatus.NO_ELIGIBLE_HISTORY, query_context_id=query_context_id,
            retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
            index_max_as_of=index_max_as_of, selected_relaxation_tier=None,
            raw_eligible_observation_count=0, eligible_episode_count=0, returned_count=0, matches=(),
            exclusion_reasons=(), limitations=(),
            no_sufficient_history_reason="no episode for this instrument, as-of cutoff, quality gate, and schema version passed even before similarity matching was applied",
        )

    max_tier = len(RELAXATION_ORDER)
    for tier in range(0, max_tier + 1):
        required_dimensions = _required_dimensions_at_tier(tier)
        tier_matches = [ep for ep in eligible_episodes if _episode_matches(ep, query.context_snapshot, required_dimensions)]
        if tier_matches:
            relaxed_dimensions = RELAXATION_ORDER[:tier]
            matched_dimensions = ("instrument",) + required_dimensions
            matches = tuple(
                RetrievalMatch(
                    episode=ep, episode_id=compute_episode_id(ep),
                    matched_dimensions=matched_dimensions, relaxed_dimensions=relaxed_dimensions,
                    unavailable_dimensions=(),
                )
                for ep in tier_matches
            )
            matches = tuple(sorted(matches, key=_match_sort_key))
            returned = matches if query.max_candidates is None else matches[: query.max_candidates]
            limitations = []
            if query.max_candidates is not None and len(matches) > len(returned):
                limitations.append(
                    f"{len(matches) - len(returned)} additional matching episode(s) at this tier were not returned due to max_candidates"
                )
            return RetrievalResult(
                status=RetrievalStatus.SUCCESSFUL, query_context_id=query_context_id,
                retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
                index_max_as_of=index_max_as_of, selected_relaxation_tier=tier,
                raw_eligible_observation_count=raw_eligible_observation_count,
                eligible_episode_count=eligible_episode_count, returned_count=len(returned), matches=returned,
                exclusion_reasons=(), limitations=tuple(limitations), no_sufficient_history_reason=None,
            )

    return RetrievalResult(
        status=RetrievalStatus.NO_SUFFICIENTLY_SIMILAR, query_context_id=query_context_id,
        retrieval_policy_version=query.retrieval_policy_version, as_of_cutoff=query.as_of_cutoff,
        index_max_as_of=index_max_as_of, selected_relaxation_tier=None,
        raw_eligible_observation_count=raw_eligible_observation_count,
        eligible_episode_count=eligible_episode_count, returned_count=0, matches=(),
        exclusion_reasons=(), limitations=(),
        no_sufficient_history_reason=(
            f"relaxation ladder exhausted at the floor ({', '.join(('instrument',) + FLOOR_DIMENSIONS)}) "
            f"without matching any of {eligible_episode_count} eligible episode(s)"
        ),
    )
