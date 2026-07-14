"""The final ``OpportunityScore`` construction step — composes a
:class:`~ai_trader.scoring_engine.pipeline.PartialScore` (+ its
:class:`~ai_trader.scoring_engine.conflict.ConflictResult`) into the schema-shaped, fully-stamped
object (versions, ``refs``, ``trade_context``, ``reason_codes``). Mirrors
:mod:`ai_trader.signal_engine.assembler`'s role in the prior module.

**Determinism note on ``timestamp``**: set to the signal's own ``as_of`` (never wall-clock) — there is
no dedicated wall-clock/timing field anywhere in ``SCORING_SCHEMA.json`` (unlike Signal Engine's
``evaluation_time_ms``), so this module contains no ``time`` import at all, matching ``SCORING_MODEL.md``
§8 literally: "No ML, no randomness, no wall-clock in the logic."
"""

from __future__ import annotations

from dataclasses import replace

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.scoring_engine import aggregator
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.conflict import ConflictResult
from ai_trader.scoring_engine.pipeline import PartialScore
from ai_trader.scoring_engine.types import (
    ComponentScores,
    OpportunityScore,
    Quality,
    Recommendation,
    Refs,
    ReasonCode,
    ScoreConfidence,
    TradeContext,
)
from ai_trader.signal_engine.types import Direction, SignalState, StrategySignal

#: JSON-Schema-valid placeholders for the pathological "not even a StrategySignal object" branch of
#: ``SCORE_INVALID`` -- never surfaced for a real signal (every real StrategySignal has genuine
#: values here); exist only so an emitted fallback score still validates against SCORING_SCHEMA.json.
_PLACEHOLDER_STRATEGY_ID = "S0"
_PLACEHOLDER_VERSION = "0.0.0"


def _fallback_refs() -> Refs:
    return Refs(
        strategy_version=None, signal_schema_version=_PLACEHOLDER_VERSION,
        interface_version=_PLACEHOLDER_VERSION, data_quality=DataQualityLevel.INSUFFICIENT,
    )


def assemble_invalid_score(signal: object, config: ScoringConfig) -> OpportunityScore:
    """``SCORE_INVALID`` (architecture §7: "signal fails to parse / schema mismatch"). ``signal`` is
    typed ``object`` deliberately -- this is the one path reachable even when the caller passed
    something that is not a genuine :class:`StrategySignal` at all, so every field is read
    defensively rather than assumed present."""
    if isinstance(signal, StrategySignal):
        strategy_id, symbol, as_of = signal.strategy_id, signal.symbol, signal.as_of
        signal_id, state = signal.signal_id, signal.state
        refs = Refs(
            strategy_version=signal.strategy_version, signal_schema_version=signal.signal_schema_version,
            interface_version=signal.context_ref.interface_version, data_quality=signal.context_ref.data_quality,
        )
    else:
        strategy_id, symbol, as_of = _PLACEHOLDER_STRATEGY_ID, "", 0
        signal_id, state = "", SignalState.INVALID
        refs = _fallback_refs()

    score_id = f"{strategy_id}|{symbol}|{as_of}"
    return OpportunityScore(
        scoring_schema_version=config.scoring_schema_version,
        scoring_engine_version=config.scoring_engine_version,
        scoring_model_version=config.scoring_model_version,
        score_id=score_id, signal_id=signal_id, strategy_id=strategy_id, symbol=symbol,
        timestamp=as_of, as_of=as_of, state=state, direction=Direction.NONE,
        total_score=0, component_scores=ComponentScores(), confidence=ScoreConfidence.NONE,
        quality=Quality.POOR, recommendation=Recommendation.INVALID, rank=1,
        reason_codes=(ReasonCode(code="SIGNAL_INVALID"),), refs=refs,
        base_quality=None, penalty_factor=None, trade_context=None,
    )


def assemble_skipped_score(partial: PartialScore, config: ScoringConfig) -> OpportunityScore:
    """``SKIPPED`` (non-actionable state, ``SCORING_STATE_MACHINE.md`` §B) -- ``EVIDENCE_BOUND``/
    ``COMPONENTS_SCORED`` never ran for this signal, so ``component_scores`` stays the
    never-computed default and ``base_quality``/``penalty_factor`` stay ``None`` (both are optional
    in the schema precisely for this early-exit terminal)."""
    signal = partial.signal
    score_id = f"{signal.strategy_id}|{signal.symbol}|{signal.as_of}"
    refs = Refs(
        strategy_version=signal.strategy_version, signal_schema_version=signal.signal_schema_version,
        interface_version=signal.context_ref.interface_version, data_quality=signal.context_ref.data_quality,
    )
    trade_context = _trade_context(signal)
    return OpportunityScore(
        scoring_schema_version=config.scoring_schema_version,
        scoring_engine_version=config.scoring_engine_version,
        scoring_model_version=config.scoring_model_version,
        score_id=score_id, signal_id=signal.signal_id, strategy_id=signal.strategy_id, symbol=signal.symbol,
        timestamp=signal.as_of, as_of=signal.as_of, state=signal.state, direction=Direction.NONE,
        total_score=0, component_scores=ComponentScores(), confidence=ScoreConfidence.NONE,
        quality=Quality.POOR, recommendation=Recommendation.SKIP, rank=1,
        reason_codes=(ReasonCode(code="NOT_ACTIONABLE"), ReasonCode(code=signal.state.value)),
        refs=refs, base_quality=None, penalty_factor=None, trade_context=trade_context,
    )


def _trade_context(signal: StrategySignal) -> TradeContext | None:
    tp = signal.trade_params
    if tp is None:
        return None
    return TradeContext(entry=tp.entry, stop=tp.stop, target=tp.target, risk_R=tp.risk_R)


def assemble_score(
    partial: PartialScore, conflict: ConflictResult, config: ScoringConfig,
    extra_reason_codes: tuple[ReasonCode, ...] = (),
) -> OpportunityScore:
    """The normal path: a signal that passed Intake & Filter and had its components fully scored.
    ``rank`` is a placeholder (1) — :mod:`ai_trader.scoring_engine.ranker` stamps the real value
    after every score in the batch has been assembled."""
    signal = partial.signal
    comp = replace(partial.components, conflict_penalty=conflict.conflict_penalty)
    penalty_factor, total_score = aggregator.aggregate(
        partial.base_quality_pre_conflict, comp.risk_penalty, comp.conflict_penalty,
    )
    confidence = aggregator.confidence_band(comp.historical_confidence, config.confidence_bands)
    quality = aggregator.quality_band(total_score, config.quality_bands)
    recommendation = aggregator.recommendation_for(signal.state, total_score, config.recommendation_bands)

    reason_codes = partial.reason_codes + conflict.reason_codes + extra_reason_codes
    if not reason_codes:
        # SCORING_SCHEMA.json requires reason_codes to be non-empty; a clean score with no
        # negative/degraded/conflicting condition still needs a disclosed, structured reason.
        reason_codes = (ReasonCode(code="SCORED_CLEAN"),)

    score_id = f"{signal.strategy_id}|{signal.symbol}|{signal.as_of}"
    refs = Refs(
        strategy_version=signal.strategy_version, signal_schema_version=signal.signal_schema_version,
        interface_version=signal.context_ref.interface_version, data_quality=signal.context_ref.data_quality,
    )

    return OpportunityScore(
        scoring_schema_version=config.scoring_schema_version,
        scoring_engine_version=config.scoring_engine_version,
        scoring_model_version=config.scoring_model_version,
        score_id=score_id, signal_id=signal.signal_id, strategy_id=signal.strategy_id, symbol=signal.symbol,
        timestamp=signal.as_of, as_of=signal.as_of, state=signal.state, direction=signal.direction,
        total_score=total_score, component_scores=comp, confidence=confidence, quality=quality,
        recommendation=recommendation, rank=1, reason_codes=reason_codes, refs=refs,
        base_quality=partial.base_quality_pre_conflict, penalty_factor=penalty_factor,
        trade_context=_trade_context(signal),
    )
