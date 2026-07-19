"""Deterministic per-edge Contextual Evidence Aggregation -- Phase 7 Checkpoint 13.

Aggregates a Checkpoint 12 `RetrievalResult` (already-matched historical `Episode`s) plus their
resolved `Outcome`s into one immutable, explainable `ContextualEvidenceReport` per `(strategy_id,
retrieval)` pair. This module produces EVIDENCE REPORTS ONLY -- it never emits BUY/SELL, entry, stop,
target, size, or a final recommendation; it never ranks edges against each other; and it never modifies
Decision Intelligence eligibility, ranking, or NO TRADE behavior (none of those types are even imported
here, verified by `test_import_independence.py`).

**Episode-level counting (no overlapping-sample inflation).** An episode's own outcome evidence is drawn
EXCLUSIVELY from the outcome attached to its FIRST member observation (`episode.observation_ids[0]`) --
the same "episode's own resolution point is the first bar of the run" convention Checkpoint 8 design
§9.3 and Checkpoint 11's own `Episode.representative_context_snapshot` already establish. This makes the
episode-aware count structurally at-most-one-per-episode by construction, never needing a separate
de-duplication pass. `raw_outcome_count` additionally reports the naive count across EVERY member
observation's own outcome, for transparency only -- every statistic in this report is computed from the
episode-collapsed set exclusively, never from the raw one.

**Sufficiency policy -- grounded in an ALREADY-VALIDATED Research Layer convention, not invented.** The
accepted Checkpoint 8 design doc's own §17 leaves the numeric evidence-sufficiency threshold explicitly
unresolved. Per Checkpoint 13's own mission ("inspect existing Research Layer statistical conventions
before deciding"), this module's own `EvidencePolicy` default reuses `code/alpha_lab.py`'s own
`MINTR = 25` constant -- this project's own already-live minimum-trade-count gate, used unmodified for
years across `alpha_lab.py`/`mstrat.py`/`mtf.py`/`s1.py`/`campaign.py` -- as `min_episodes_sufficient`.
The policy is an explicit, versioned, caller-overridable object (never a hidden module constant) and
appears verbatim in every report's `evidence_policy_version` field, satisfying "explicit, versioned,
sensitivity-testable."

**CONTRADICTORY -- reusing the project's own established convention, not a new rule.** `PROJECT_AUDIT.md`
§28 already documents a live "min-trades + UNRESOLVED-if-CI-straddles" rule for exactly this situation
(small-n strategies whose confidence interval straddles zero). This module reuses that same rule
verbatim: `CONTRADICTORY` fires when a 95%, NORMAL-APPROXIMATION confidence interval (computed via
stdlib `statistics.NormalDist` -- no third-party dependency) straddles zero. This CI is explicitly
DESCRIPTIVE, not a validated significance test -- `PROJECT_AUDIT.md` D1 already documents that this
project's own analytic normal-approximation p-values can be badly miscalibrated on heavy-tailed R
distributions; the same caveat is disclosed verbatim in every report's `limitations` field. This module
never claims causal edge validation, never labels evidence as strategy proof, and never computes a
p-value.

**STALE -- deliberately left unresolved rather than invented.** No existing Research Layer convention
defines a staleness threshold for contextual evidence age (as opposed to trade-count sufficiency). Per
the same "do not invent arbitrary thresholds" discipline, `EvidencePolicy.staleness_threshold_seconds`
defaults to `None` -- when absent, evidence is simply never classified `STALE`, and `evidence_freshness_*`
is still reported raw so a caller can apply their own judgment; supplying an explicit value activates the
check.
"""

from __future__ import annotations

import enum
import statistics
from dataclasses import dataclass, field

from ai_trader.context_memory.contracts import ContextSnapshotId, Outcome, ObservationId, SchemaVersion
from ai_trader.context_memory.enums import OutcomeStatus
from ai_trader.context_memory.episodes import Episode, EpisodeId, compute_episode_id
from ai_trader.context_memory.index import HistoricalIndex
from ai_trader.context_memory.retrieval import RetrievalResult, RetrievalStatus
from ai_trader.context_memory.validation import ContextMemoryValidationError, require_non_empty_str, require_positive_int

EVIDENCE_POLICY_VERSION = SchemaVersion("context_memory_evidence", "cme-v1")

# Reused verbatim from code/alpha_lab.py's own live MINTR=25 -- this project's own already-validated
# minimum-trade-count gate, not a value invented for this checkpoint.
_RESEARCH_LAYER_MINTR = 25

_Z_975 = statistics.NormalDist(0.0, 1.0).inv_cdf(0.975)  # ~1.959963985 -- standard 95% two-sided z


class EvidenceStatus(str, enum.Enum):
    SUFFICIENT = "SUFFICIENT"
    LIMITED = "LIMITED"
    CONTRADICTORY = "CONTRADICTORY"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    INCOMPATIBLE = "INCOMPATIBLE"


@dataclass(frozen=True)
class EvidencePolicy:
    """Explicit, versioned, caller-overridable sufficiency policy -- never a hidden constant."""

    policy_version: SchemaVersion = field(default=EVIDENCE_POLICY_VERSION)
    min_episodes_sufficient: int = _RESEARCH_LAYER_MINTR
    min_episodes_limited: int = 1
    staleness_threshold_seconds: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, SchemaVersion):
            raise ContextMemoryValidationError("EvidencePolicy.policy_version must be a SchemaVersion")
        require_positive_int(self.min_episodes_sufficient, "EvidencePolicy.min_episodes_sufficient")
        require_positive_int(self.min_episodes_limited, "EvidencePolicy.min_episodes_limited")
        if self.min_episodes_limited > self.min_episodes_sufficient:
            raise ContextMemoryValidationError(
                "EvidencePolicy.min_episodes_limited must not exceed min_episodes_sufficient"
            )
        if self.staleness_threshold_seconds is not None:
            require_positive_int(self.staleness_threshold_seconds, "EvidencePolicy.staleness_threshold_seconds")


@dataclass(frozen=True)
class ContextualEvidenceReport:
    """Immutable, per-`(strategy_id, retrieval)` evidence report -- see Checkpoint 13 §B. Only metrics
    supported by the real `Outcome` contract are computed; nothing here is a BUY/SELL/entry/stop/target/
    size/execution recommendation."""

    query_context_id: ContextSnapshotId
    target_strategy_id: str
    retrieval_policy_version: SchemaVersion
    evidence_policy_version: SchemaVersion
    as_of_cutoff: int
    selected_relaxation_tier: int | None

    raw_outcome_count: int
    episode_count: int
    resolved_outcome_count: int
    unresolved_outcome_count: int
    invalid_outcome_count: int
    excluded_incompatible_outcome_count: int

    outcome_definition_version: SchemaVersion | None
    horizon: int | None
    cost_model_ref: str | None

    evidence_freshness_newest_age: int | None
    evidence_freshness_oldest_age: int | None
    time_coverage_span: int | None

    contextual_win_rate: float | None
    mean_normalized_result: float | None
    median_normalized_result: float | None
    result_dispersion_stdev: float | None
    confidence_interval_95: tuple[float, float] | None
    positive_sign_count: int
    negative_sign_count: int
    zero_sign_count: int
    evidence_consistency: float | None

    evidence_status: EvidenceStatus
    evidence_status_reason: str
    limitations: tuple[str, ...]

    source_episode_ids: tuple[EpisodeId, ...]
    source_observation_ids: tuple[ObservationId, ...]


def _unavailable_report(
    query_context_id: ContextSnapshotId, strategy_id: str, retrieval: RetrievalResult, policy: EvidencePolicy,
    status: EvidenceStatus, reason: str, limitations: tuple[str, ...] = (),
) -> ContextualEvidenceReport:
    return ContextualEvidenceReport(
        query_context_id=query_context_id, target_strategy_id=strategy_id,
        retrieval_policy_version=retrieval.retrieval_policy_version, evidence_policy_version=policy.policy_version,
        as_of_cutoff=retrieval.as_of_cutoff, selected_relaxation_tier=retrieval.selected_relaxation_tier,
        raw_outcome_count=0, episode_count=0, resolved_outcome_count=0, unresolved_outcome_count=0,
        invalid_outcome_count=0, excluded_incompatible_outcome_count=0,
        outcome_definition_version=None, horizon=None, cost_model_ref=None,
        evidence_freshness_newest_age=None, evidence_freshness_oldest_age=None, time_coverage_span=None,
        contextual_win_rate=None, mean_normalized_result=None, median_normalized_result=None,
        result_dispersion_stdev=None, confidence_interval_95=None,
        positive_sign_count=0, negative_sign_count=0, zero_sign_count=0, evidence_consistency=None,
        evidence_status=status, evidence_status_reason=reason, limitations=limitations,
        source_episode_ids=(), source_observation_ids=(),
    )


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def aggregate_evidence(
    index: HistoricalIndex, retrieval: RetrievalResult, strategy_id: str, policy: EvidencePolicy | None = None,
) -> ContextualEvidenceReport:
    """Build one `ContextualEvidenceReport` for `strategy_id` from an already-computed Checkpoint 12
    `RetrievalResult`. Never re-runs retrieval, never queries live market data, never imports Decision
    Intelligence."""
    require_non_empty_str(strategy_id, "aggregate_evidence strategy_id")
    resolved_policy = policy if policy is not None else EvidencePolicy()

    if retrieval.status in (RetrievalStatus.INCOMPATIBLE, RetrievalStatus.UNSUPPORTED_VERSION, RetrievalStatus.DEGRADED_DATA):
        return _unavailable_report(
            retrieval.query_context_id, strategy_id, retrieval, resolved_policy, EvidenceStatus.INCOMPATIBLE,
            f"underlying retrieval was not SUCCESSFUL (status={retrieval.status.value}) -- no evidence can be aggregated",
        )
    if retrieval.status in (RetrievalStatus.NO_ELIGIBLE_HISTORY, RetrievalStatus.NO_SUFFICIENTLY_SIMILAR):
        return _unavailable_report(
            retrieval.query_context_id, strategy_id, retrieval, resolved_policy, EvidenceStatus.UNAVAILABLE,
            retrieval.no_sufficient_history_reason or "retrieval found no eligible or sufficiently similar history",
        )

    edge_episodes: list[Episode] = [
        m.episode for m in retrieval.matches if any(ref.strategy_id == strategy_id for ref in m.episode.present_edges)
    ]
    if not edge_episodes:
        return _unavailable_report(
            retrieval.query_context_id, strategy_id, retrieval, resolved_policy, EvidenceStatus.UNAVAILABLE,
            f"strategy_id={strategy_id!r} was not PRESENT in any retrieved episode",
        )

    raw_outcome_count = 0
    per_episode_outcome: dict[str, Outcome] = {}
    for ep in edge_episodes:
        for obs_id in ep.observation_ids:
            raw_outcome_count += len(
                [o for o in index.outcomes_for_observation(obs_id, visible_as_of=retrieval.as_of_cutoff) if o.strategy_id == strategy_id]
            )
        representative_id = ep.observation_ids[0]
        candidates = [
            o for o in index.outcomes_for_observation(representative_id, visible_as_of=retrieval.as_of_cutoff)
            if o.strategy_id == strategy_id
        ]
        if candidates:
            per_episode_outcome[compute_episode_id(ep).value] = sorted(
                candidates, key=lambda o: (o.status.value, o.outcome_definition_version.version, o.horizon)
            )[0]

    if not per_episode_outcome:
        return _unavailable_report(
            retrieval.query_context_id, strategy_id, retrieval, resolved_policy, EvidenceStatus.UNAVAILABLE,
            f"strategy_id={strategy_id!r} was PRESENT but no episode's representative observation has a recorded outcome",
            limitations=(f"raw_outcome_count={raw_outcome_count} at non-representative observations was not used",),
        )

    resolved = [(eid, o) for eid, o in per_episode_outcome.items() if o.status is OutcomeStatus.RESOLVED]
    unresolved_count = sum(1 for o in per_episode_outcome.values() if o.status is OutcomeStatus.PENDING)
    invalid_count = sum(1 for o in per_episode_outcome.values() if o.status in (OutcomeStatus.INVALID, OutcomeStatus.UNAVAILABLE))

    if not resolved:
        return ContextualEvidenceReport(
            query_context_id=retrieval.query_context_id, target_strategy_id=strategy_id,
            retrieval_policy_version=retrieval.retrieval_policy_version, evidence_policy_version=resolved_policy.policy_version,
            as_of_cutoff=retrieval.as_of_cutoff, selected_relaxation_tier=retrieval.selected_relaxation_tier,
            raw_outcome_count=raw_outcome_count, episode_count=len(edge_episodes),
            resolved_outcome_count=0, unresolved_outcome_count=unresolved_count, invalid_outcome_count=invalid_count,
            excluded_incompatible_outcome_count=0,
            outcome_definition_version=None, horizon=None, cost_model_ref=None,
            evidence_freshness_newest_age=None, evidence_freshness_oldest_age=None, time_coverage_span=None,
            contextual_win_rate=None, mean_normalized_result=None, median_normalized_result=None,
            result_dispersion_stdev=None, confidence_interval_95=None,
            positive_sign_count=0, negative_sign_count=0, zero_sign_count=0, evidence_consistency=None,
            evidence_status=EvidenceStatus.UNAVAILABLE,
            evidence_status_reason="episodes exist but none has a RESOLVED outcome yet -- only PENDING/INVALID/UNAVAILABLE",
            limitations=(), source_episode_ids=(), source_observation_ids=(),
        )

    # Dominant (outcome_definition_version, horizon, cost_model_ref) triple, chosen deterministically
    # (most-common, ties broken by version/horizon string ordering) -- outcomes under any other triple
    # are excluded and disclosed rather than silently pooled (Checkpoint 13 §I).
    triples = [(o.outcome_definition_version, o.horizon, o.cost_model_ref) for _, o in resolved]
    triple_counts: dict[tuple[str, str, int, str], int] = {}
    for v, h, c in triples:
        key = (v.namespace, v.version, h, c)
        triple_counts[key] = triple_counts.get(key, 0) + 1
    dominant_key = sorted(triple_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    matching = [
        (eid, o) for eid, o in resolved
        if (o.outcome_definition_version.namespace, o.outcome_definition_version.version, o.horizon, o.cost_model_ref) == dominant_key
    ]
    excluded_incompatible = len(resolved) - len(matching)

    values = [o.normalized_result for _, o in matching if o.normalized_result is not None]
    n = len(values)
    mean_v = statistics.mean(values)
    median_v = statistics.median(values)
    stdev_v = statistics.stdev(values) if n >= 2 else None
    ci: tuple[float, float] | None = None
    if stdev_v is not None and n >= 2:
        margin = _Z_975 * (stdev_v / (n ** 0.5))
        ci = (mean_v - margin, mean_v + margin)

    signs = [_sign(v) for v in values]
    positive_count = sum(1 for s in signs if s > 0)
    negative_count = sum(1 for s in signs if s < 0)
    zero_count = sum(1 for s in signs if s == 0)
    win_rate = positive_count / n if n > 0 else None

    pooled_sign = _sign(mean_v)
    evidence_consistency = (sum(1 for s in signs if s == pooled_sign) / n) if n > 0 and pooled_sign != 0 else None

    matched_episode_end_as_of = [ep.end_as_of for ep in edge_episodes if compute_episode_id(ep).value in dict(matching)]
    newest_age = min(retrieval.as_of_cutoff - e for e in matched_episode_end_as_of) if matched_episode_end_as_of else None
    oldest_age = max(retrieval.as_of_cutoff - e for e in matched_episode_end_as_of) if matched_episode_end_as_of else None
    time_coverage_span = (oldest_age - newest_age) if (newest_age is not None and oldest_age is not None) else None

    limitations: list[str] = [
        "confidence_interval_95 is a NORMAL-APPROXIMATION interval (stdlib statistics.NormalDist), not a "
        "validated bootstrap -- PROJECT_AUDIT.md D1 already documents this approximation can be unreliable "
        "on heavy-tailed distributions; treat as descriptive only, never as a validated significance test.",
    ]
    if excluded_incompatible:
        limitations.append(
            f"{excluded_incompatible} resolved outcome(s) under a different outcome_definition_version/"
            "horizon/cost_model_ref were excluded rather than silently pooled"
        )
    if n < resolved_policy.min_episodes_sufficient:
        limitations.append(
            f"only {n} resolved, dominant-triple episode(s) -- below the SUFFICIENT threshold "
            f"({resolved_policy.min_episodes_sufficient}, reused from code/alpha_lab.py's own MINTR)"
        )

    dominant_version = next(o.outcome_definition_version for _, o in matching)
    dominant_horizon = next(o.horizon for _, o in matching)
    dominant_cost_ref = next(o.cost_model_ref for _, o in matching)

    status, reason = _classify(n, ci, resolved_policy, newest_age)

    return ContextualEvidenceReport(
        query_context_id=retrieval.query_context_id, target_strategy_id=strategy_id,
        retrieval_policy_version=retrieval.retrieval_policy_version, evidence_policy_version=resolved_policy.policy_version,
        as_of_cutoff=retrieval.as_of_cutoff, selected_relaxation_tier=retrieval.selected_relaxation_tier,
        raw_outcome_count=raw_outcome_count, episode_count=len(edge_episodes),
        resolved_outcome_count=n, unresolved_outcome_count=unresolved_count, invalid_outcome_count=invalid_count,
        excluded_incompatible_outcome_count=excluded_incompatible,
        outcome_definition_version=dominant_version, horizon=dominant_horizon, cost_model_ref=dominant_cost_ref,
        evidence_freshness_newest_age=newest_age, evidence_freshness_oldest_age=oldest_age,
        time_coverage_span=time_coverage_span,
        contextual_win_rate=win_rate, mean_normalized_result=mean_v, median_normalized_result=median_v,
        result_dispersion_stdev=stdev_v, confidence_interval_95=ci,
        positive_sign_count=positive_count, negative_sign_count=negative_count, zero_sign_count=zero_count,
        evidence_consistency=evidence_consistency,
        evidence_status=status, evidence_status_reason=reason, limitations=tuple(limitations),
        source_episode_ids=tuple(EpisodeId(k) for k in dict(matching).keys()),
        source_observation_ids=tuple(sorted({obs_id for ep in edge_episodes for obs_id in ep.observation_ids}, key=lambda x: x.value)),
    )


def _classify(
    n: int, ci: tuple[float, float] | None, policy: EvidencePolicy, newest_age: int | None,
) -> tuple[EvidenceStatus, str]:
    if n < policy.min_episodes_limited:
        return EvidenceStatus.UNAVAILABLE, "no resolved outcome under the dominant outcome-definition triple"
    if policy.staleness_threshold_seconds is not None and newest_age is not None and newest_age > policy.staleness_threshold_seconds:
        return (
            EvidenceStatus.STALE,
            f"newest contributing episode is {newest_age}s old, exceeding the configured staleness threshold "
            f"of {policy.staleness_threshold_seconds}s",
        )
    if ci is not None and ci[0] <= 0.0 <= ci[1]:
        return (
            EvidenceStatus.CONTRADICTORY,
            "the 95% confidence interval straddles zero -- reusing this project's own established "
            "UNRESOLVED-if-CI-straddles convention (PROJECT_AUDIT.md)",
        )
    if n < policy.min_episodes_sufficient:
        return EvidenceStatus.LIMITED, f"{n} resolved episode(s) is below the SUFFICIENT threshold ({policy.min_episodes_sufficient})"
    return EvidenceStatus.SUFFICIENT, f"{n} resolved episode(s) meets the SUFFICIENT threshold ({policy.min_episodes_sufficient})"


def aggregate_all_present_edges(
    index: HistoricalIndex, retrieval: RetrievalResult, policy: EvidencePolicy | None = None,
) -> tuple[ContextualEvidenceReport, ...]:
    """Deterministic, sorted-by-`strategy_id` collection of one report per distinct PRESENT edge across
    every retrieved episode -- never a ranked comparison between edges (Checkpoint 13 §F: "do not rank
    edges")."""
    strategy_ids = sorted({ref.strategy_id for m in retrieval.matches for ref in m.episode.present_edges})
    return tuple(aggregate_evidence(index, retrieval, sid, policy) for sid in strategy_ids)
