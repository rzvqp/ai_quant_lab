"""``ScoringEngine`` — the public facade implementing ``SCORING_API.md`` exactly.

Wires together the per-signal pipeline (:mod:`ai_trader.scoring_engine.pipeline`), the Conflict
Analyzer (:mod:`ai_trader.scoring_engine.conflict`), the Aggregator (:mod:`ai_trader.scoring_engine.
aggregator`), the Assembler (:mod:`ai_trader.scoring_engine.assembler`), the Ranker
(:mod:`ai_trader.scoring_engine.ranker`), and the Output Collector's validation
(:mod:`ai_trader.scoring_engine.validator`) into the documented, deterministic, fail-safe scoring
cycle. A pure opportunity-quality evaluator: no trading decision, no sizing, no risk, no execution, no
learning, no research access (``SCORING_ENGINE_ARCHITECTURE.md`` §2).

**Determinism note**: no module reached from this file imports ``time``/``random`` -- ``timestamp``
is always the scored signal's own ``as_of`` (``SCORING_MODEL.md`` §8: "No ML, no randomness, no
wall-clock in the logic"), unlike Signal Engine, which had one narrowly-scoped wall-clock exception
(``evaluation_time_ms``) for a field that has no equivalent anywhere in ``SCORING_SCHEMA.json``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ai_trader.scoring_engine import aggregator, assembler, conflict, ranker, validator
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.evidence import BoundEvidence, EvidenceCache, StrategyManagerLike
from ai_trader.scoring_engine.exceptions import EngineNotConfiguredError
from ai_trader.scoring_engine.pipeline import PartialScore, score_signal_stage1
from ai_trader.scoring_engine.types import (
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    NotFound,
    OpportunityScore,
    Quality,
    ReasonCode,
    Recommendation,
    ScoreBatch,
    ScoreExplanation,
    Statistics,
    ValidationResult,
    VersionInfo,
)
from ai_trader.signal_engine.types import StrategySignal

_NO_BATCH_CONTEXT = (ReasonCode(code="NO_BATCH_CONTEXT", component="conflict_penalty"),)


def _group_key(signal: object) -> tuple[str, int]:
    """``(symbol, as_of)`` grouping key for one signal -- conflict analysis and ranking are always
    scoped within a single symbol/as_of (``SCORING_MODEL.md`` §7). A signal that is not even a
    genuine :class:`StrategySignal` (the pathological ``SCORE_INVALID`` case) buckets into a fixed
    sentinel key -- it never participates in conflict analysis regardless (excluded by
    ``PartialScore.is_terminal``), so the exact bucket it lands in has no effect on any real result.
    """
    if isinstance(signal, StrategySignal):
        return (signal.symbol, signal.as_of)
    return ("", 0)


def _finalize_one(
    partial: PartialScore, conflict_result: conflict.ConflictResult, config: ScoringConfig,
    extra_reason_codes: tuple[ReasonCode, ...] = (),
) -> OpportunityScore:
    if partial.terminal_state == "SCORE_INVALID":
        score = assembler.assemble_invalid_score(partial.signal, config)
    elif partial.terminal_state == "SKIPPED":
        score = assembler.assemble_skipped_score(partial, config)
    else:
        score = assembler.assemble_score(partial, conflict_result, config, extra_reason_codes)

    result = validator.validate_score(score)
    if not result.valid:
        # fail-safe: a score that somehow still fails validation (e.g. a schema-boundary condition
        # this build didn't anticipate) is never emitted as-is -- reassemble as a classified INVALID,
        # preserving identity fields but disclosing the actual validation reasons, never a fabricated
        # passing score (SCORING_API.md "failure model").
        invalid_signal = partial.signal if isinstance(partial.signal, StrategySignal) else None
        mismatch_reasons = tuple(ReasonCode(code="SCHEMA_MISMATCH", detail=r) for r in result.reasons) or (
            ReasonCode(code="SCHEMA_MISMATCH"),
        )
        score = replace(assembler.assemble_invalid_score(invalid_signal, config), reason_codes=mismatch_reasons)

        # The reassembled score above copies identity fields (strategy_id, refs, ...) straight from
        # the ORIGINAL signal -- if that signal is itself what caused the schema failure (e.g. a
        # malformed strategy_version string), the "fixed" score can still be schema-invalid, and
        # would otherwise be emitted anyway since nothing re-checked it. Re-validate once more; if
        # STILL invalid, fall back to the fully placeholder-based score (signal=None), which is
        # schema-valid by construction and carries no unvalidated data from the offending signal.
        if not validator.validate_score(score).valid:
            score = replace(assembler.assemble_invalid_score(None, config), reason_codes=mismatch_reasons)
    return score


class ScoringEngine:
    """The Scoring Engine. See ``SCORING_API.md`` for the full contract."""

    def __init__(self, config: ScoringConfig | None = None) -> None:
        self._config = config or ScoringConfig()
        self._state = EngineLifecycleState.UNINITIALIZED
        self._manager: StrategyManagerLike | None = None
        self._degraded = True
        self._degraded_reasons: list[str] = []
        self._batches = 0
        self._scores_total = 0
        self._by_recommendation: dict[str, int] = {r.value: 0 for r in Recommendation}
        self._by_quality: dict[str, int] = {q.value: 0 for q in Quality}
        self._score_sum = 0
        self._invalids = 0
        self._last_scores_by_symbol: dict[str, ScoreBatch] = {}

    # ------------------------------------------------------------------ 0. configuration

    def configure(self, manager: StrategyManagerLike | None = None) -> None:
        """Idempotent full reset. ``manager`` is the read-only Strategy Manager evidence source
        (``SCORING_SEQUENCE.md`` §1: "handshake Strategy Manager (evidence availability)"); if absent,
        the engine starts ``DEGRADED`` and every score's ``historical_confidence``/``risk_penalty``
        falls back to their evidence-missing worst case -- it still scores, never fabricating."""
        self._manager = manager
        self._batches = 0
        self._scores_total = 0
        self._by_recommendation = {r.value: 0 for r in Recommendation}
        self._by_quality = {q.value: 0 for q in Quality}
        self._score_sum = 0
        self._invalids = 0
        self._last_scores_by_symbol = {}
        self._degraded_reasons = []
        if manager is None:
            self._degraded_reasons.append("no Strategy Manager configured; contract evidence unavailable")
            self._degraded = True
        else:
            self._degraded = False
        self._state = EngineLifecycleState.DEGRADED if self._degraded else EngineLifecycleState.READY

    def _require_configured(self) -> None:
        if self._state in (EngineLifecycleState.UNINITIALIZED, EngineLifecycleState.STOPPED):
            raise EngineNotConfiguredError("ScoringEngine.configure() must be called first")

    # ------------------------------------------------------------------ 1. scoring

    def score_signal(self, signal: StrategySignal, evidence: BoundEvidence | None = None) -> OpportunityScore:
        """Score a single signal (``SCORING_API.md`` §1). ``evidence``, if supplied, is used AS-IS
        instead of fetching from the configured Strategy Manager. Because ``conflict_penalty`` needs
        the whole batch, a lone call always scores with ``conflict_penalty=0`` and the reason code
        ``NO_BATCH_CONTEXT``, exactly as documented."""
        self._require_configured()
        self._state = EngineLifecycleState.SCORING
        try:
            cache: EvidenceCache = {}
            if evidence is not None:
                cache[getattr(signal, "strategy_id", "")] = evidence
            partial = score_signal_stage1(signal, self._manager, cache, self._config)
            conflict_result = conflict.ConflictResult(0.0, ())
            extra = () if partial.is_terminal else _NO_BATCH_CONTEXT
            score = _finalize_one(partial, conflict_result, self._config, extra)
            ranked = ranker.rank_scores([score])
            final = ranked[0]
            self._record_scores((final,))
            self._store_batch(ScoreBatch(
                as_of=final.as_of, symbol=final.symbol, scores=(final,),
                counts_by_recommendation={final.recommendation.value: 1}, generated_at=final.as_of,
            ))
            return final
        finally:
            self._state = EngineLifecycleState.DEGRADED if self._degraded else EngineLifecycleState.READY

    def score_batch(self, signals: Sequence[StrategySignal]) -> ScoreBatch:
        """Score a whole batch (``SCORING_API.md`` §1, the normal entry point): per-signal components
        + the cross-signal ``conflict_penalty`` + deterministic ranking, grouped by ``(symbol,
        as_of)`` (``SCORING_MODEL.md`` §7). Empty input -> empty batch (valid, per the API doc)."""
        self._require_configured()
        if not signals:
            batch = ScoreBatch(as_of=0, symbol=None, scores=(), counts_by_recommendation={}, generated_at=0)
            self._record_cycle(batch)
            return batch

        self._state = EngineLifecycleState.SCORING
        try:
            cache: EvidenceCache = {}
            partials = [score_signal_stage1(s, self._manager, cache, self._config) for s in signals]

            groups: dict[tuple[str, int], list[int]] = {}
            for i, p in enumerate(partials):
                groups.setdefault(_group_key(p.signal), []).append(i)

            all_scores: list[OpportunityScore] = []
            for idxs in groups.values():
                group_partials = [partials[i] for i in idxs]
                conflict_results = conflict.compute_conflict_penalties(group_partials)
                group_scores = [
                    _finalize_one(p, cres, self._config) for p, cres in zip(group_partials, conflict_results)
                ]
                all_scores.extend(ranker.rank_scores(group_scores))

            symbol, as_of = _batch_symbol_as_of(groups)
            batch = ScoreBatch(
                as_of=as_of, symbol=symbol, scores=tuple(all_scores),
                counts_by_recommendation=_counts_by_recommendation(all_scores), generated_at=as_of,
            )
            self._record_cycle(batch)
            return batch
        finally:
            self._state = EngineLifecycleState.DEGRADED if self._degraded else EngineLifecycleState.READY

    # ------------------------------------------------------------------ 2. explanation & validation

    def explain_score(self, score_id: str) -> ScoreExplanation | NotFound:
        for batch in self._last_scores_by_symbol.values():
            for score in batch.scores:
                if score.score_id == score_id:
                    return ScoreExplanation(
                        score_id=score.score_id, component_scores=score.component_scores,
                        base_quality=score.base_quality, penalty_factor=score.penalty_factor,
                        reason_codes=score.reason_codes, model_version=score.scoring_model_version,
                    )
        return NotFound(score_id)

    def validate(self, score: OpportunityScore) -> ValidationResult:
        return validator.validate_score(score)

    # ------------------------------------------------------------------ 3. introspection

    def statistics(self) -> Statistics:
        avg = self._score_sum / self._scores_total if self._scores_total else 0.0
        return Statistics(
            batches=self._batches, scores_total=self._scores_total,
            by_recommendation=dict(self._by_recommendation), by_quality=dict(self._by_quality),
            avg_score=avg, invalids=self._invalids,
        )

    def health(self) -> EngineHealth:
        if self._state in (EngineLifecycleState.UNINITIALIZED, EngineLifecycleState.STOPPED):
            overall = EngineOverallHealth.FAILED
        elif self._degraded_reasons:
            overall = EngineOverallHealth.DEGRADED
        else:
            overall = EngineOverallHealth.OK
        return EngineHealth(
            overall=overall, state=self._state, degraded_reasons=tuple(self._degraded_reasons),
            supported_versions={
                "signal_schema_major": self._config.supported_signal_schema_major,
                "interface_major": self._config.supported_interface_major,
            },
        )

    def versions(self) -> VersionInfo:
        return VersionInfo(
            scoring_engine_version=self._config.scoring_engine_version,
            scoring_schema_version=self._config.scoring_schema_version,
            scoring_model_version=self._config.scoring_model_version,
            supported_signal_schema_major=self._config.supported_signal_schema_major,
            supported_interface_major=self._config.supported_interface_major,
        )

    # ------------------------------------------------------------------ 4. shutdown

    def shutdown(self) -> EngineHealth:
        """Stop accepting new batches, release the batch + evidence cache (architecture §12: "hold no
        state")."""
        self._require_configured()
        final_health = self.health()  # captured BEFORE flipping state, same precedent as Signal
        # Engine's own shutdown() -- "stopped" must not be misreported as a synthetic FAILED.
        self._last_scores_by_symbol = {}
        self._state = EngineLifecycleState.STOPPED
        return final_health

    # ------------------------------------------------------------------ internals

    def _record_scores(self, scores: tuple[OpportunityScore, ...]) -> None:
        for score in scores:
            self._scores_total += 1
            self._by_recommendation[score.recommendation.value] = (
                self._by_recommendation.get(score.recommendation.value, 0) + 1
            )
            self._by_quality[score.quality.value] = self._by_quality.get(score.quality.value, 0) + 1
            self._score_sum += score.total_score
            if score.recommendation is Recommendation.INVALID:
                self._invalids += 1

    def _record_cycle(self, batch: ScoreBatch) -> None:
        self._batches += 1
        self._record_scores(batch.scores)
        self._store_batch(batch)

    def _store_batch(self, batch: ScoreBatch) -> None:
        if batch.symbol:
            self._last_scores_by_symbol[batch.symbol] = batch


def _counts_by_recommendation(scores: list[OpportunityScore]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for score in scores:
        counts[score.recommendation.value] = counts.get(score.recommendation.value, 0) + 1
    return counts


def _batch_symbol_as_of(groups: dict[tuple[str, int], list[int]]) -> tuple[str | None, int]:
    """The reported top-level ``(symbol, as_of)`` for a ``ScoreBatch``. Normal usage (per
    ``SCORING_SEQUENCE.md`` §3: "score_batch per symbol") always has exactly one group. A
    caller-contract violation (a mixed-symbol/as_of call) is handled defensively rather than crashing:
    the largest group's key is reported and ``symbol=None`` if more than one group exists, since a
    single ``ScoreBatch`` cannot faithfully summarize more than one ``(symbol, as_of)`` pair."""
    if len(groups) == 1:
        (symbol, as_of) = next(iter(groups))
        return symbol, as_of
    best_key = max(groups, key=lambda k: (len(groups[k]), k[0], k[1]))
    return None, best_key[1]
