"""Builds the structured ``Explanation`` (``SIGNAL_EXPLANATION_SCHEMA.json``) from a
:class:`~ai_trader.signal_engine.pipeline.PipelineOutcome` plus the strategy's contract and the
``MarketContext`` used. Structured fields only -- no free-text generation
(``SIGNAL_ENGINE_ARCHITECTURE.md`` §6): every human string here is either copied verbatim from the
contract (``mechanism``) or a stable condition code, never composed prose.
"""

from __future__ import annotations

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.signal_engine.pipeline import PipelineOutcome
from ai_trader.signal_engine.types import (
    ConditionRecord,
    ContextSummary,
    Explanation,
    MarketContext,
    StrategyRef,
    TriggeringMechanism,
)
from ai_trader.strategy_manager.contract import Contract, Regime


def build_explanation(
    outcome: PipelineOutcome, contract: Contract, context: MarketContext, explanation_schema_version: str,
) -> Explanation:
    """Assemble the structured ``Explanation`` for one evaluation outcome."""
    required_records = tuple(
        ConditionRecord(code=name, satisfied=name in outcome.confirmations_detail.met)
        for name in outcome.confirmations_detail.required
    ) or outcome.required_condition_records

    session_block = context.get("session", {})
    dq = context.get("data_quality", {})
    dq_overall = dq.get("overall", "OK") if isinstance(dq, dict) else "OK"
    try:
        # A strategy's generate_signal() response is never schema-validated for its 'regime' string
        # (pipeline.py takes it as-is) -- an unrecognized value must degrade to "unknown", never
        # crash the whole evaluation cycle (this mirrors assembler.py's own defensive handling of
        # the same outcome.regime field for the top-level StrategySignal.regime).
        regime = Regime(outcome.regime) if outcome.regime else None
    except ValueError:
        regime = None
    context_summary = ContextSummary(
        symbol=context.get("meta", {}).get("symbol", ""),
        as_of=context.get("meta", {}).get("as_of", 0),
        session=session_block.get("name") if isinstance(session_block, dict) else None,
        data_quality=DataQualityLevel(dq_overall),
        regime=regime,
        timeframes_used=tuple(sorted(context.get("timeframes", {}).keys())) or None,
    )

    return Explanation(
        explanation_schema_version=explanation_schema_version,
        strategy_ref=StrategyRef(id=contract.identity.id, version=contract.identity.version),
        state=outcome.state,
        triggering_mechanism=TriggeringMechanism(mechanism_text=contract.semantics.mechanism),
        why_exists=outcome.why_exists,
        why_failed=outcome.why_failed,
        required_conditions=required_records,
        missing_conditions=tuple(
            ConditionRecord(code=m, satisfied=False) for m in outcome.missing_context
        ),
        invalid_conditions=tuple(
            ConditionRecord(code=c, satisfied=False) for c in outcome.invalid_conditions
        ),
        confirmations=outcome.confirmations_detail,
        context_summary=context_summary,
    )
