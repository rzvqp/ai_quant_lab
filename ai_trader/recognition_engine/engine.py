"""Recognition Engine Phase 1A -- single-dimension conditional statistics
(`RECOGNITION_ENGINE_PHASE1_DESIGN.md`, CEO verdict CONDITIONAL GO). Read-only: this module never calls
any `append_*`/write method on `ContextMemoryRepository` -- verified by
`tests/test_no_write_control.py`. Never imports `learning_feedback`, `shadow_evidence`,
`decision_intelligence`, `decision_intelligence_v2`, `risk_manager`, or `execution_engine` (Phase 1
Design Sec4/Sec10's own standing isolation rule).

**Unit of learning** (Phase 1 Design Sec1, CEO decision 1): the pair (decision-time `ContextSnapshot`,
terminal `PositionOutcome`). `result` throughout this module means `PositionOutcome.total_net_pnl` --
NEVER the terminal, per-fill `Outcome.normalized_result` (CEO decision 5; the dataset audit's own 4/688
sign-mismatch finding proved the latter is unsafe as a position's own truth for multi-partial exits).

**Strict isolation** (CEO decisions 2-4): every statistic is computed for exactly one
`(strategy_id, outcome_kind)` pair at a time -- callers must never merge results across strategies or
across `STRATEGY`/`PORTFOLIO` kind themselves; this module enforces the isolation on its OWN read side
(the repository query is filtered to the requested pair before any bucketing happens) but the CALLER
remains responsible for not merging separately-returned results.

**Single dimension only** (CEO's own explicit Phase 1A scope limit): `compute_conditional_statistics`
takes exactly one `ContextDimension` per call. No multi-dimensional joint conditioning, no similarity
matching, no relaxation ladder -- a direct, deterministic group-by over the already-closed dataset, not a
live per-query retrieval (`retrieval.py`/`evidence.py`, Context Memory's own Checkpoint 12/13 machinery,
are deliberately NOT used here -- reusing them would implicitly combine multiple `ContextSnapshot`
dimensions across relaxation tiers, exactly what this phase's own authorization excludes).
"""

from __future__ import annotations

import statistics
from collections import defaultdict

from ai_trader.context_memory.contracts import ContextSnapshot, PositionOutcome
from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.recognition_engine.policy import SufficiencyPolicy
from ai_trader.recognition_engine.types import ConditionalStatistics, ContextDimension, Sufficiency


def _bucket_value(context_snapshot: ContextSnapshot, dimension: ContextDimension) -> str:
    """Pure function of `ContextSnapshot` ONLY -- never takes a `PositionOutcome`/result value as an
    argument. This signature IS the temporal-integrity guarantee: which bucket a position falls into can
    structurally never depend on how that position eventually resolved (verified directly by
    `tests/test_negative_controls.py::test_temporal_integrity_bucket_assignment_ignores_outcome`)."""
    if dimension is ContextDimension.SESSION:
        return context_snapshot.session_state or "UNKNOWN"
    if dimension is ContextDimension.TREND_M15:
        return context_snapshot.trend_m15.value
    if dimension is ContextDimension.TREND_H1:
        return context_snapshot.trend_h1.value
    if dimension is ContextDimension.TREND_H4:
        return context_snapshot.trend_h4.value
    if dimension is ContextDimension.TREND_D1:
        return context_snapshot.trend_d1.value
    if dimension is ContextDimension.STRUCTURE_STATE:
        return context_snapshot.structure_state.value
    if dimension is ContextDimension.MOMENTUM_M15:
        return context_snapshot.momentum_m15.value
    if dimension is ContextDimension.MOMENTUM_H1:
        return context_snapshot.momentum_h1.value
    if dimension is ContextDimension.MOMENTUM_H4:
        return context_snapshot.momentum_h4.value
    if dimension is ContextDimension.MOMENTUM_D1:
        return context_snapshot.momentum_d1.value
    if dimension is ContextDimension.VOLATILITY_REGIME:
        return context_snapshot.volatility_regime.value
    if dimension is ContextDimension.LIQUIDITY_STATE:
        return context_snapshot.liquidity_state.value
    if dimension is ContextDimension.EXPANSION_STATE:
        return context_snapshot.expansion_state.value
    if dimension is ContextDimension.MULTI_TIMEFRAME_AGREEMENT:
        return context_snapshot.multi_timeframe_agreement.value
    if dimension is ContextDimension.DATA_QUALITY_STATE:
        return context_snapshot.data_quality_state.value
    raise ValueError(f"Unhandled ContextDimension: {dimension!r}")  # pragma: no cover -- exhaustive above


def _sign_bucket(result: float) -> str:
    if result > 0:
        return "favorable"
    if result < 0:
        return "unfavorable"
    return "zero"


def compute_conditional_statistics(
    repository: ContextMemoryRepository, strategy_id: str, outcome_kind: OutcomeKind,
    dimension: ContextDimension, policy: SufficiencyPolicy | None = None,
) -> tuple[ConditionalStatistics, ...]:
    """Purely descriptive, read-only. Returns one `ConditionalStatistics` per distinct value of
    `dimension` actually observed among `(strategy_id, outcome_kind)`'s own `PositionOutcome` records --
    never a fabricated bucket for a value that never occurred. Returns `()` (empty, never raises) if the
    strategy/kind combination has zero `PositionOutcome` records at all (the empty-input control).

    `result` used throughout = `PositionOutcome.total_net_pnl` (never the terminal `Outcome`). Strategy
    and outcome-kind isolation are enforced by this function's own read filter, applied before any
    bucketing or aggregation.
    """
    resolved_policy = policy if policy is not None else SufficiencyPolicy()

    matching: list[PositionOutcome] = [
        po for po in repository.iter_position_outcomes()
        if po.strategy_id == strategy_id and po.outcome_kind is outcome_kind
    ]
    if not matching:
        return ()

    by_bucket: dict[str, list[float]] = defaultdict(list)
    for po in matching:
        observation = repository.get_observation(po.observation_id)
        if observation is None:  # pragma: no cover -- structurally unreachable, repository integrity
            # already verified (LEARNING_FEEDBACK_DATASET_AUDIT.md Sec1: 0 broken observation_id links);
            # defensive, not asserted away.
            continue
        bucket = _bucket_value(observation.context_snapshot, dimension)
        by_bucket[bucket].append(po.total_net_pnl)

    provenance = f"{repository.root_path} (strategy_id={strategy_id}, outcome_kind={outcome_kind.value})"
    results: list[ConditionalStatistics] = []
    for bucket_value in sorted(by_bucket):
        values = by_bucket[bucket_value]
        n = len(values)
        favorable = sum(1 for v in values if _sign_bucket(v) == "favorable")
        unfavorable = sum(1 for v in values if _sign_bucket(v) == "unfavorable")
        zero = n - favorable - unfavorable
        sufficiency = (
            Sufficiency.SUFFICIENT if n >= resolved_policy.min_observations
            else Sufficiency.INSUFFICIENT_EVIDENCE
        )
        results.append(ConditionalStatistics(
            strategy_id=strategy_id, outcome_kind=outcome_kind.value, context_dimension=dimension,
            context_bucket_value=bucket_value,
            n=n, favorable_count=favorable, unfavorable_count=unfavorable, zero_count=zero,
            favorable_rate=(favorable / n) if n > 0 else None,
            unfavorable_rate=(unfavorable / n) if n > 0 else None,
            mean_result=statistics.fmean(values) if n > 0 else None,
            median_result=statistics.median(values) if n > 0 else None,
            stdev_result=statistics.stdev(values) if n > 1 else None,
            min_result=min(values) if n > 0 else None,
            max_result=max(values) if n > 0 else None,
            sufficiency=sufficiency, min_observations_threshold=resolved_policy.min_observations,
            data_provenance=provenance,
        ))
    return tuple(results)
