"""`recognize` -- Recognition Engine (live)'s single public entry point. Never decides risk, never
sends an order, never invents a pattern: only a `pattern_id` already present in
`patterns.AUTHORIZED_PATTERNS` can ever be queried. Always returns descriptive statistics (or an
explicit, disclosed absence of them) -- never a trading recommendation."""

from __future__ import annotations

from ai_trader.context_memory import ContextMemoryRepository
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.recognition_engine import ConditionalStatistics, Sufficiency, compute_conditional_statistics
from ai_trader.recognition_engine.engine import _bucket_value  # noqa: SLF001 -- deliberate reuse of the
# EXACT same bucket-assignment function used for the historical group-by, so live/historical bucketing
# can never silently drift apart (see design doc §1).
from ai_trader.recognition_engine.policy import SufficiencyPolicy
from ai_trader.recognition_engine_live import reason_codes as rc
from ai_trader.recognition_engine_live.adapters import build_context_snapshot
from ai_trader.recognition_engine_live.patterns import pattern_for_id
from ai_trader.recognition_engine_live.types import CalculationTraceStep, RecognitionCandidate, RecognitionResult


def _result(
    candidate: RecognitionCandidate, trace: list[CalculationTraceStep], reason_codes: list[str],
    pattern_authorized: bool, pattern_version: str | None = None, context_bucket_value: str | None = None,
    statistics: ConditionalStatistics | None = None, sufficiency: Sufficiency = Sufficiency.INSUFFICIENT_EVIDENCE,
) -> RecognitionResult:
    return RecognitionResult(
        strategy_id=candidate.strategy_id, pattern_id=candidate.pattern_id, pattern_version=pattern_version,
        as_of=candidate.as_of, correlation_id=candidate.correlation_id, context_bucket_value=context_bucket_value,
        statistics=statistics, sufficiency=sufficiency, pattern_authorized=pattern_authorized,
        reason_codes=tuple(reason_codes), calculation_trace=tuple(trace),
    )


def recognize(
    candidate: RecognitionCandidate, mi_snapshot: MarketIntelligenceSnapshot,
    repository: ContextMemoryRepository, policy: SufficiencyPolicy | None = None,
) -> RecognitionResult:
    trace: list[CalculationTraceStep] = []

    pattern = pattern_for_id(candidate.pattern_id)
    trace.append(CalculationTraceStep(
        "PATTERN_AUTHORIZED", pattern is not None,
        detail=None if pattern is not None else f"pattern_id={candidate.pattern_id!r} not in the authorized catalog",
    ))
    if pattern is None:
        return _result(candidate, trace, [rc.UNAUTHORIZED_PATTERN], pattern_authorized=False)

    try:
        context_snapshot = build_context_snapshot(mi_snapshot)
        bucket_value = _bucket_value(context_snapshot, pattern.dimension)
        trace.append(CalculationTraceStep("BUCKET_VALUE_RESOLVED", True, detail=f"bucket={bucket_value}"))
    except Exception as exc:  # noqa: BLE001 -- fail-closed: a read-only query must never raise past its
        # own boundary.
        trace.append(CalculationTraceStep("BUCKET_VALUE_RESOLVED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _result(candidate, trace, [rc.QUERY_FAILED], pattern_authorized=True, pattern_version=pattern.pattern_version)

    try:
        rows = compute_conditional_statistics(repository, candidate.strategy_id, pattern.outcome_kind, pattern.dimension, policy)
        trace.append(CalculationTraceStep("STATISTICS_QUERIED", True, detail=f"{len(rows)} bucket(s) in history"))
    except Exception as exc:  # noqa: BLE001 -- same fail-closed discipline as above.
        trace.append(CalculationTraceStep("STATISTICS_QUERIED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _result(
            candidate, trace, [rc.QUERY_FAILED], pattern_authorized=True, pattern_version=pattern.pattern_version,
            context_bucket_value=bucket_value,
        )

    matching = next((row for row in rows if row.context_bucket_value == bucket_value), None)
    trace.append(CalculationTraceStep("HISTORICAL_BUCKET_MATCHED", matching is not None))
    if matching is None:
        return _result(
            candidate, trace, [rc.NO_HISTORICAL_BUCKET_MATCH], pattern_authorized=True,
            pattern_version=pattern.pattern_version, context_bucket_value=bucket_value,
        )

    reason_codes: list[str] = []
    if matching.sufficiency is Sufficiency.INSUFFICIENT_EVIDENCE:
        reason_codes.append(rc.INSUFFICIENT_EVIDENCE)
    trace.append(CalculationTraceStep("SUFFICIENCY_CHECKED", matching.sufficiency is Sufficiency.SUFFICIENT, detail=matching.sufficiency.value))

    return _result(
        candidate, trace, reason_codes, pattern_authorized=True, pattern_version=pattern.pattern_version,
        context_bucket_value=bucket_value, statistics=matching, sufficiency=matching.sufficiency,
    )
