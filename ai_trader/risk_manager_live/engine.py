"""`evaluate_trade_proposal` -- the live Risk Manager's single public entry point (`RISK_MANAGER_LIVE_
PHASE2_DESIGN.md`). Pure function: no state, no I/O, no MT5 terminal API import (verified by
`tests/test_import_independence.py`). Reuses the existing, frozen `ai_trader/risk_manager/` package's
own composable guard/limit/filter/sizing functions completely unmodified -- never routes through
`RiskManager.evaluate()`/`allow_trade()` (scoring-engine-coupled, wrong integration point for a live
proposal that has not been scored by anything).

Fail-closed throughout (every unhandled/ambiguous condition is a DENY, never an approve).
"""

from __future__ import annotations

import math

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager import guards, limits
from ai_trader.risk_manager import filters as risk_filters
from ai_trader.risk_manager import sizing as risk_sizing
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import DeniedReason, EngineState, PortfolioState, RiskContext
from ai_trader.risk_manager_live import reason_codes as rc
from ai_trader.risk_manager_live.types import (
    AccountState,
    CalculationTraceStep,
    InstrumentSpecification,
    LiveRiskDecision,
    TradeProposal,
)
from ai_trader.scoring_engine.types import (
    ComponentScores,
    OpportunityScore,
    Quality,
    Recommendation,
    Refs,
    ScoreConfidence,
    TradeContext,
)
from ai_trader.signal_engine.types import Direction, SignalState

_SIGNAL_STATE_BY_DIRECTION = {Direction.LONG: SignalState.BUY, Direction.SHORT: SignalState.SELL}


def _deny(
    reason_codes: list[str], trace: list[CalculationTraceStep], warnings: list[str] | None = None,
    escalate_to: EngineState | None = None,
) -> LiveRiskDecision:
    return LiveRiskDecision(
        approved=False, reason_codes=tuple(reason_codes), requested_risk=None, approved_risk=None,
        calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None,
        warnings=tuple(warnings or ()), calculation_trace=tuple(trace), escalate_to=escalate_to,
    )


def _trace_from_result(stage: str, passed: bool, reason: DeniedReason | None) -> CalculationTraceStep:
    if reason is None:
        return CalculationTraceStep(stage=stage, passed=passed)
    return CalculationTraceStep(
        stage=stage, passed=passed, detail=reason.detail, observed=reason.observed, limit=reason.limit,
    )


def _build_sizing_adapter(proposal: TradeProposal, config: RiskConfig) -> OpportunityScore:
    """Constructs a genuine (never fabricated-as-meaningful) `OpportunityScore` satisfying
    `compute_sizing`'s own type signature. `compute_sizing` (read in full before writing this function)
    only ever reads `.trade_context` (entry/stop), `.symbol`, and `.quality` from this object -- every
    OTHER field below is a disclosed, inert placeholder the sizing arithmetic never touches, not invented
    data presented as real. `state`/`direction` are the one place a genuine, non-placeholder mapping
    exists (the proposal's own real trading direction)."""
    quality = proposal.confidence_quality if proposal.confidence_quality is not None else Quality.MODERATE
    return OpportunityScore(
        scoring_schema_version="live-shim-1.0.0", scoring_engine_version="live-shim-1.0.0",
        scoring_model_version="live-shim-1.0.0", score_id=f"LIVE-{proposal.proposal_id}",
        signal_id=f"LIVE-{proposal.proposal_id}", strategy_id=proposal.strategy_id, symbol=proposal.symbol,
        timestamp=proposal.as_of, as_of=proposal.as_of,
        state=_SIGNAL_STATE_BY_DIRECTION[proposal.direction], direction=proposal.direction,
        total_score=0,  # placeholder, unused by compute_sizing
        component_scores=ComponentScores(),  # all-zero, placeholder, unused by compute_sizing
        confidence=ScoreConfidence.NONE,  # placeholder, unused by compute_sizing
        quality=quality,  # REAL: proposal's own confidence_quality, or the disclosed neutral default
        recommendation=Recommendation.WATCH,  # placeholder, deliberately non-committal, unused by compute_sizing
        rank=0,  # placeholder, unused by compute_sizing
        reason_codes=(),  # placeholder, unused by compute_sizing
        refs=Refs(
            strategy_version=None, signal_schema_version="live-shim-1.0.0",
            interface_version="live-shim-1.0.0",
            data_quality=DataQualityLevel.OK,  # placeholder, unused by compute_sizing
        ),
        trade_context=TradeContext(
            entry=proposal.entry, stop=proposal.stop, target=proposal.target, risk_R=None,
        ),
    )


def evaluate_trade_proposal(
    proposal: TradeProposal, account: AccountState, portfolio: PortfolioState,
    instrument: InstrumentSpecification, risk_context: RiskContext, config: RiskConfig | None = None,
) -> LiveRiskDecision:
    resolved_config = config if config is not None else RiskConfig()
    trace: list[CalculationTraceStep] = []
    reason_codes: list[str] = []
    warnings: list[str] = []

    # 1. Data-completeness / risk-not-calculable gates -- fail-closed, before anything else runs.
    if instrument.symbol != proposal.symbol:
        trace.append(CalculationTraceStep(
            "DATA_COMPLETENESS", False, detail="instrument.symbol does not match proposal.symbol",
        ))
        return _deny([rc.PROPOSAL_DATA_INCOMPLETE], trace)

    stop_distance = abs(proposal.entry - proposal.stop)
    calculable = (
        stop_distance > 0 and instrument.point_value > 0 and instrument.tick_size > 0
        and instrument.lot_step > 0 and instrument.contract_size > 0 and account.equity > 0
    )
    trace.append(CalculationTraceStep(
        "RISK_CALCULABLE", calculable,
        detail=None if calculable else "non-positive stop_distance/point_value/tick_size/lot_step/"
        "contract_size/equity",
    ))
    if not calculable:
        return _deny([rc.RISK_NOT_CALCULABLE], trace)

    # 2. Loss/drawdown guards (existing, frozen, unmodified) -- run in full, never short-circuited here.
    # Risk Audit #1 fix: `result.escalate_to` is now captured, not discarded -- the caller (the future
    # persistent circuit breaker, `risk_manager_live.circuit_breaker`) needs it to remember a breach
    # across calls, which this function itself never does (still pure, still no state of its own).
    escalate_to: EngineState | None = None
    for name, result in guards.run_loss_drawdown_guards(portfolio, resolved_config):
        trace.append(_trace_from_result(name, result.passed, result.reason))
        if not result.passed and result.reason is not None:
            reason_codes.append(result.reason.code)
            if result.escalate_to is not None and escalate_to is None:
                escalate_to = result.escalate_to

    # 3. Cooldowns (existing, frozen, unmodified).
    for name, result in guards.run_cooldowns(proposal.symbol, proposal.strategy_id, portfolio, resolved_config):
        trace.append(_trace_from_result(name, result.passed, result.reason))
        if not result.passed and result.reason is not None:
            reason_codes.append(result.reason.code)

    # 4. Portfolio limits (existing, frozen, unmodified).
    snapshot = risk_context.for_symbol(proposal.symbol)
    for limit_name, limit_result in limits.run_portfolio_limits(
        proposal.symbol, snapshot, portfolio, resolved_config,
    ):
        trace.append(_trace_from_result(limit_name, limit_result.passed, limit_result.reason))
        if not limit_result.passed and limit_result.reason is not None:
            reason_codes.append(limit_result.reason.code)

    # 5. Pre-trade filters (existing, frozen, unmodified) -- includes data-quality/spread/volatility/
    # liquidity/news/weekend/gap, all already implemented and tested.
    for filter_name, filter_result in risk_filters.run_pre_trade_filters(
        proposal.symbol, risk_context, resolved_config,
    ):
        trace.append(_trace_from_result(filter_name, filter_result.passed, filter_result.reason))
        if not filter_result.passed and filter_result.reason is not None:
            reason_codes.append(filter_result.reason.code)

    if reason_codes:
        return _deny(reason_codes, trace, warnings, escalate_to=escalate_to)

    # 6. Sizing (existing, frozen, unmodified) -- via a genuine, disclosed adapter (see docstring above).
    opportunity = _build_sizing_adapter(proposal, resolved_config)
    sizing_outcome = risk_sizing.compute_sizing(opportunity, portfolio, resolved_config)
    trace.append(CalculationTraceStep(
        "SIZING", sizing_outcome.valid,
        detail=sizing_outcome.deny_reason.detail if sizing_outcome.deny_reason else None,
        observed=sizing_outcome.deny_reason.observed if sizing_outcome.deny_reason else None,
        limit=sizing_outcome.deny_reason.limit if sizing_outcome.deny_reason else None,
    ))
    if not sizing_outcome.valid or sizing_outcome.sizing is None:
        code = sizing_outcome.deny_reason.code if sizing_outcome.deny_reason else rc.RISK_NOT_CALCULABLE
        return _deny([code], trace)

    sizing_result = sizing_outcome.sizing
    requested_risk = resolved_config.sizing.risk_per_trade_pct
    approved_risk = sizing_result.risk_per_trade_pct

    # 7. Volume-step rounding/clamping -- NEW, additive (never in the frozen sizing.py). Converts base
    # units (e.g. troy ounces) into broker lots via InstrumentSpecification.contract_size, rounds DOWN to
    # the nearest lot_step (never up -- never grants more size than was risk-approved), clamps to
    # [min_volume, max_volume].
    volume_units = sizing_result.size_units
    volume_lots_raw = volume_units / instrument.contract_size
    volume_lots = math.floor(volume_lots_raw / instrument.lot_step) * instrument.lot_step
    volume_lots = min(volume_lots, instrument.max_volume)
    volume_ok = volume_lots >= instrument.min_volume
    trace.append(CalculationTraceStep(
        "VOLUME_STEP_ROUNDING", volume_ok, observed=volume_lots, limit=instrument.min_volume,
    ))
    if not volume_ok:
        return _deny([rc.VOLUME_STEP_ROUNDING_BELOW_MIN], trace)
    if volume_lots < volume_lots_raw:
        warnings.append(
            f"volume rounded down from {volume_lots_raw:.6f} to {volume_lots:.6f} lots "
            f"(lot_step={instrument.lot_step})"
        )

    # 8. Free-margin sufficiency -- NEW, additive (margin has no equivalent anywhere in the frozen
    # risk_manager package; only ever existed inside simulation.portfolio_simulator.SimAccount).
    notional = volume_lots * instrument.contract_size * proposal.entry
    margin_estimate = notional / account.leverage
    margin_ok = margin_estimate <= account.margin_free
    trace.append(CalculationTraceStep(
        "FREE_MARGIN", margin_ok, observed=margin_estimate, limit=account.margin_free,
    ))
    if not margin_ok:
        return _deny([rc.INSUFFICIENT_FREE_MARGIN], trace)

    return LiveRiskDecision(
        approved=True, reason_codes=(), requested_risk=requested_risk, approved_risk=approved_risk,
        calculated_volume=volume_lots, monetary_risk=sizing_result.risk_budget_currency,
        stop_distance=stop_distance, margin_estimate=margin_estimate, warnings=tuple(warnings),
        calculation_trace=tuple(trace),
    )
