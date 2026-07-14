"""Signal Assembler (``SIGNAL_ENGINE_ARCHITECTURE.md`` §2) — composes the final ``StrategySignal``
from a :class:`~ai_trader.signal_engine.pipeline.PipelineOutcome`, stamping versions and the context
reference (architecture §11: "everything explainable + versioned").
"""

from __future__ import annotations

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.explanation import build_explanation
from ai_trader.signal_engine.pipeline import PipelineOutcome
from ai_trader.signal_engine.types import (
    ContextRef,
    MarketContext,
    QualityFlag,
    StrategySignal,
)
from ai_trader.strategy_manager.contract import ConfidenceLevel, Contract, Regime


def assemble_signal(
    strategy_id: str,
    contract: Contract | None,
    outcome: PipelineOutcome,
    context: MarketContext,
    evaluation_time_ms: float,
    config: EngineConfig,
    now_ts: int,
    extra_quality_flags: tuple[QualityFlag, ...] = (),
) -> StrategySignal:
    """Build the final, schema-shaped :class:`StrategySignal`. ``contract`` is ``None`` only for the
    ``CORRUPTED_OUTPUT``/``EVAL_TIMEOUT`` fallback path (the strategy's own response could not be
    trusted enough to even read its contract fields safely) -- everything defaults to the safest,
    most conservative values in that case (architecture §7 fail-safe policy).
    """
    meta = context.get("meta", {})
    as_of = meta.get("as_of", 0)
    symbol = meta.get("symbol", "")
    base_timeframe = meta.get("base_timeframe", "")
    dq = context.get("data_quality", {})
    dq_overall = dq.get("overall", "OK") if isinstance(dq, dict) else "OK"

    context_ref = ContextRef(
        context_schema_version=meta.get("context_schema_version", "1.0.0"),
        feature_dictionary_version=meta.get("feature_dictionary_version", "1.0.0"),
        interface_version=meta.get("interface_version", "1.0.0"),
        data_quality=DataQualityLevel(dq_overall),
    )

    explanation_version = config.explanation_schema_version
    if contract is not None:
        explanation = build_explanation(outcome, contract, context, explanation_version)
        mechanism_text = contract.semantics.mechanism
        strategy_version = contract.identity.version
    else:
        from ai_trader.signal_engine.types import (
            ConditionRecord,
            Confirmations,
            ContextSummary,
            Explanation,
            StrategyRef,
            TriggeringMechanism,
        )

        explanation = Explanation(
            explanation_schema_version=explanation_version,
            strategy_ref=StrategyRef(id=strategy_id, version=None),
            state=outcome.state,
            triggering_mechanism=TriggeringMechanism(mechanism_text="unavailable: strategy output could not be read"),
            why_exists=(),
            why_failed=tuple(ConditionRecord(code=f.value, satisfied=False) for f in extra_quality_flags),
            required_conditions=(),
            missing_conditions=(),
            invalid_conditions=(),
            confirmations=Confirmations(),
            context_summary=ContextSummary(
                symbol=symbol, as_of=as_of, session=None, data_quality=DataQualityLevel(dq_overall),
            ),
        )
        mechanism_text = "unavailable: strategy output could not be read"
        strategy_version = None

    try:
        confidence = ConfidenceLevel(outcome.confidence)
    except ValueError:
        confidence = ConfidenceLevel.NONE

    quality_flags: tuple[QualityFlag, ...] = extra_quality_flags or (QualityFlag.OK,)

    signal_id = f"{strategy_id}|{symbol}|{as_of}"

    regime: Regime | None
    try:
        regime = Regime(outcome.regime) if outcome.regime else None
    except ValueError:
        regime = None
    session_block = context.get("session", {})
    session_name = session_block.get("name") if isinstance(session_block, dict) else None

    return StrategySignal(
        signal_schema_version=config.signal_schema_version,
        signal_engine_version=config.signal_engine_version,
        signal_id=signal_id,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        timestamp=now_ts,
        as_of=as_of,
        symbol=symbol,
        timeframe=base_timeframe,
        state=outcome.state,
        direction=outcome.direction,
        signal_strength=outcome.signal_strength,
        confidence=confidence,
        mechanism=mechanism_text,
        required_confirmations=outcome.required_confirmations,
        confirmations_met=outcome.confirmations_met,
        missing_context=outcome.missing_context,
        invalid_conditions=outcome.invalid_conditions,
        quality_flags=quality_flags,
        context_ref=context_ref,
        explanation=explanation,
        evaluation_time_ms=evaluation_time_ms,
        trade_params=outcome.trade_params,
        regime=regime,
        session=session_name,
    )
