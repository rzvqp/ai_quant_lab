"""`orchestrate` -- the Execution Orchestrator's single public entry point. Pure sequencing + bridging:
calls every downstream engine (Context Engine, Recognition Engine, Confidence Engine, Risk Manager,
Portfolio Manager, Order Manager) UNMODIFIED, in the CEO's own specified order, building only the bridge
objects each stage's own contract requires. Contains no risk/portfolio/order/recognition logic of its
own. Fail-closed throughout: any exception at any stage aborts the run, never propagates.
"""

from __future__ import annotations

from ai_trader.confidence_engine.engine import assess_confidence
from ai_trader.confidence_engine.types import ConfidenceAssessment
from ai_trader.context_engine.engine import build_context_snapshot
from ai_trader.context_engine.types import MarketContextSnapshot
from ai_trader.execution_engine.reconciler import reconcile_all_open
from ai_trader.execution_engine.types import Fill
from ai_trader.order_manager.engine import process_approved_intent
from ai_trader.order_manager.types import ApprovedTradeIntent
from ai_trader.execution_orchestrator import reason_codes as rc
from ai_trader.execution_orchestrator.types import (
    CalculationTraceStep,
    CandidateSignal,
    ExecutionMode,
    OrchestrationResult,
    OrchestratorConfig,
    OrchestratorDependencies,
)
from ai_trader.portfolio_manager_live.daily_reset import reset_if_new_day
from ai_trader.portfolio_manager_live.engine import evaluate_portfolio_authorization
from ai_trader.portfolio_manager_live.types import PortfolioAuthorizationRequest, PortfolioDailyState, PortfolioDecision
from ai_trader.recognition_engine_live.engine import recognize
from ai_trader.recognition_engine_live.types import RecognitionCandidate, RecognitionResult
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import evaluate_circuit_state
from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.types import LiveRiskDecision, PortfolioStateSource, TradeProposal, TradingCircuitState
from ai_trader.strategy_runtime.context_access import MarketContext
from ai_trader.strategy_runtime.context_access import as_of as market_context_as_of
from ai_trader.telegram_notifier.sender import notify_fire_and_forget
from ai_trader.telegram_notifier.types import NotificationEvent


def correlation_id_for(candidate: CandidateSignal) -> str:
    """Deterministic, no wall-clock, no randomness (`EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md` §3)."""
    return f"ORCH-{candidate.strategy_id}-{candidate.symbol}-{candidate.as_of}"


def _denied(
    candidate: CandidateSignal, correlation_id: str, mode: ExecutionMode, trace: list[CalculationTraceStep],
    reason_codes: list[str], context: MarketContextSnapshot | None = None,
    recognition: RecognitionResult | None = None, confidence: ConfidenceAssessment | None = None,
    risk_decision: LiveRiskDecision | None = None, portfolio_decision: PortfolioDecision | None = None,
    circuit_state_after: TradingCircuitState | None = None,
    daily_state_after: PortfolioDailyState | None = None,
) -> OrchestrationResult:
    return OrchestrationResult(
        correlation_id=correlation_id, strategy_id=candidate.strategy_id, symbol=candidate.symbol,
        as_of=candidate.as_of, mode=mode, approved=False, context=context, recognition=recognition,
        confidence=confidence, risk_decision=risk_decision, portfolio_decision=portfolio_decision,
        order_result=None, reason_codes=tuple(reason_codes), calculation_trace=tuple(trace),
        circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
    )


def _notify(deps: OrchestratorDependencies, event_type: str, summary: str, correlation_id: str, as_of: int) -> None:
    if deps.telegram_credentials is None:
        return
    notify_fire_and_forget(
        NotificationEvent(event_type=event_type, summary=summary, correlation_id=correlation_id, as_of=as_of),
        deps.telegram_credentials,
    )


def orchestrate(
    candidate: CandidateSignal, market_context: MarketContext, deps: OrchestratorDependencies,
    mode: ExecutionMode = ExecutionMode.DRY_RUN, emergency_stop: bool = False,
    config: OrchestratorConfig | None = None,
    circuit_state: TradingCircuitState | None = None,
    pnl_source: PortfolioStateSource | None = None,
) -> OrchestrationResult:
    resolved_config = config if config is not None else OrchestratorConfig()
    correlation_id = correlation_id_for(candidate)
    trace: list[CalculationTraceStep] = []

    # Demo Readiness precondition #11 fix (2026-07-25): `PortfolioDailyState`'s own docstring named a
    # Phase-9 owner that was never built. Computed unconditionally (unlike circuit tracking, this isn't
    # opt-in -- it's a bug fix to existing, always-active behavior) and threaded through every return
    # path so the caller always knows what to persist forward, the same discipline as `circuit_state_after`.
    daily_state_after = reset_if_new_day(deps.daily_state, candidate.as_of)
    trace.append(CalculationTraceStep(
        "DAILY_STATE_RESET_CHECKED", daily_state_after is deps.daily_state,
        detail="same day" if daily_state_after is deps.daily_state else "new UTC day, state reset",
    ))

    # Risk Audit #1 fix (2026-07-25): a caller that opts in by supplying BOTH `circuit_state` and
    # `pnl_source` gets the unified, persistent circuit breaker -- `emergency_stop` folds into it
    # (`emergency_stop_requested`) instead of being a separate, single-call-only override. A caller
    # that supplies neither sees the OLD, unchanged, single-call `emergency_stop` check -- byte
    # -identical behavior, so every existing caller is unaffected.
    circuit_state_after: TradingCircuitState | None = None
    if circuit_state is not None and pnl_source is not None:
        # Step 2 of #2 (2026-07-25): the injected `pnl_source` can now be a REAL, I/O-backed
        # implementation that raises when account/position/deal data is missing or incomplete
        # (`PortfolioDataUnavailableError`, `mt5_pnl_source`) -- fail-closed: absence of data is a
        # reason NOT to trade, never silently treated as "no losses" by letting the exception escape
        # this function's own documented "never propagates" contract.
        try:
            circuit_state_after = evaluate_circuit_state(
                circuit_state, pnl_source, deps.risk_config, candidate.as_of,
                emergency_stop_requested=emergency_stop,
            )
        except Exception as exc:  # noqa: BLE001 -- fail-closed, matching every other stage in this function.
            trace.append(CalculationTraceStep(
                "CIRCUIT_STATE_CHECKED", False, detail=f"{type(exc).__name__}: {exc}",
            ))
            result = _denied(
                candidate, correlation_id, mode, trace, [rc.CIRCUIT_DATA_UNAVAILABLE],
                circuit_state_after=circuit_state, daily_state_after=daily_state_after,
            )
            _notify(
                deps, "ORCHESTRATION_DENIED", "circuit data unavailable", correlation_id, candidate.as_of,
            )
            return result
        trace.append(CalculationTraceStep(
            "CIRCUIT_STATE_CHECKED", circuit_state_after.state is EngineState.READY,
            detail=circuit_state_after.state.value,
        ))
        if circuit_state_after.state is not EngineState.READY:
            reason = circuit_state_after.reason_code or rc.TRADING_SUSPENDED
            result = _denied(
                candidate, correlation_id, mode, trace, [rc.TRADING_SUSPENDED, reason],
                circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
            )
            _notify(
                deps, "ORCHESTRATION_DENIED", f"circuit {circuit_state_after.state.value}: {reason}",
                correlation_id, candidate.as_of,
            )
            return result
    else:
        trace.append(CalculationTraceStep("EMERGENCY_STOP_CHECKED", not emergency_stop))
        if emergency_stop:
            result = _denied(
                candidate, correlation_id, mode, trace, [rc.EMERGENCY_STOP_ACTIVE],
                daily_state_after=daily_state_after,
            )
            _notify(deps, "ORCHESTRATION_DENIED", "emergency stop active", correlation_id, candidate.as_of)
            return result

    trace.append(CalculationTraceStep("MODE_CHECKED", mode is not ExecutionMode.LIVE, detail=mode.value))
    if mode is ExecutionMode.LIVE:
        result = _denied(
            candidate, correlation_id, mode, trace, [rc.LIVE_TRADING_NOT_AUTHORIZED],
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )
        _notify(deps, "ORCHESTRATION_DENIED", "LIVE trading is not authorized", correlation_id, candidate.as_of)
        return result

    if mode is ExecutionMode.DEMO:
        demo_ok = deps.account.is_demo
        trace.append(CalculationTraceStep("DEMO_ACCOUNT_CHECKED", demo_ok))
        if not demo_ok:
            return _denied(
                candidate, correlation_id, mode, trace, [rc.NON_DEMO_ACCOUNT_REFUSED],
                circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
            )

    context_as_of = market_context_as_of(market_context)
    staleness_ok = abs(candidate.as_of - context_as_of) <= resolved_config.max_staleness_seconds
    trace.append(CalculationTraceStep(
        "FRESHNESS_CHECKED", staleness_ok, detail=f"candidate.as_of={candidate.as_of} context.as_of={context_as_of}",
    ))
    if not staleness_ok:
        return _denied(
            candidate, correlation_id, mode, trace, [rc.STALE_CANDIDATE],
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    try:
        context = build_context_snapshot(market_context, deps.strategy_library_path)
        trace.append(CalculationTraceStep("CONTEXT_ENGINE_CALLED", True))
    except Exception as exc:  # noqa: BLE001 -- fail-closed: any stage exception aborts the run here.
        trace.append(CalculationTraceStep("CONTEXT_ENGINE_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _denied(
            candidate, correlation_id, mode, trace, [rc.CONTEXT_BUILD_FAILED],
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    recognition: RecognitionResult | None = None
    if resolved_config.recognition_pattern_id is not None and context.market_intelligence is not None and deps.repository is not None:
        try:
            recognition_candidate = RecognitionCandidate(
                strategy_id=candidate.strategy_id, pattern_id=resolved_config.recognition_pattern_id,
                as_of=candidate.as_of, correlation_id=correlation_id,
            )
            recognition = recognize(
                recognition_candidate, context.market_intelligence, deps.repository, resolved_config.recognition_policy,
            )
            trace.append(CalculationTraceStep("RECOGNITION_ENGINE_CALLED", True))
        except Exception as exc:  # noqa: BLE001 -- non-fatal: Confidence Engine handles a missing
            # RecognitionResult explicitly (it is optional input, Phase 8's own design).
            trace.append(CalculationTraceStep("RECOGNITION_ENGINE_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
    else:
        trace.append(CalculationTraceStep("RECOGNITION_ENGINE_SKIPPED", True))

    try:
        confidence = assess_confidence(
            candidate.strategy_id, correlation_id, context, recognition, resolved_config.confidence_config,
        )
        trace.append(CalculationTraceStep("CONFIDENCE_ENGINE_CALLED", True, detail=confidence.grade.value))
    except Exception as exc:  # noqa: BLE001 -- fail-closed.
        trace.append(CalculationTraceStep("CONFIDENCE_ENGINE_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _denied(
            candidate, correlation_id, mode, trace, [rc.CONFIDENCE_ASSESSMENT_FAILED], context, recognition,
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    trace.append(CalculationTraceStep("ELIGIBILITY_CHECKED", confidence.eligible_for_risk_evaluation))
    if not confidence.eligible_for_risk_evaluation:
        result = _denied(
            candidate, correlation_id, mode, trace, [rc.NOT_ELIGIBLE_FOR_RISK_EVALUATION, *confidence.reason_codes],
            context, recognition, confidence, circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )
        _notify(deps, "ORCHESTRATION_DENIED", f"not eligible, grade={confidence.grade.value}", correlation_id, candidate.as_of)
        return result

    proposal = TradeProposal(
        proposal_id=correlation_id, correlation_id=correlation_id, strategy_id=candidate.strategy_id,
        symbol=candidate.symbol, direction=candidate.direction, entry=candidate.entry, stop=candidate.stop,
        target=candidate.target, as_of=candidate.as_of, confidence_quality=confidence.quality,
    )
    try:
        risk_decision = evaluate_trade_proposal(
            proposal, deps.account, deps.portfolio, deps.instrument, deps.risk_context, deps.risk_config,
        )
        trace.append(CalculationTraceStep("RISK_MANAGER_CALLED", True, detail=str(risk_decision.approved)))
    except Exception as exc:  # noqa: BLE001 -- fail-closed.
        trace.append(CalculationTraceStep("RISK_MANAGER_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _denied(
            candidate, correlation_id, mode, trace, [rc.RISK_EVALUATION_FAILED], context, recognition, confidence,
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    if not risk_decision.approved:
        result = _denied(
            candidate, correlation_id, mode, trace, [rc.RISK_DENIED, *risk_decision.reason_codes],
            context, recognition, confidence, risk_decision, circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )
        _notify(deps, "ORCHESTRATION_DENIED", "denied by Risk Manager", correlation_id, candidate.as_of)
        return result

    assert risk_decision.calculated_volume is not None and risk_decision.monetary_risk is not None
    assert risk_decision.approved_risk is not None

    portfolio_request = PortfolioAuthorizationRequest(
        proposal_id=correlation_id, correlation_id=correlation_id, strategy_id=candidate.strategy_id,
        symbol=candidate.symbol, direction=candidate.direction, session=candidate.session,
        monetary_risk=risk_decision.monetary_risk, approved_risk_pct=risk_decision.approved_risk,
        as_of=candidate.as_of,
    )
    try:
        portfolio_decision = evaluate_portfolio_authorization(
            portfolio_request, deps.portfolio, daily_state_after, deps.risk_config, resolved_config.portfolio_config,
        )
        trace.append(CalculationTraceStep("PORTFOLIO_MANAGER_CALLED", True, detail=str(portfolio_decision.approved)))
    except Exception as exc:  # noqa: BLE001 -- fail-closed.
        trace.append(CalculationTraceStep("PORTFOLIO_MANAGER_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _denied(
            candidate, correlation_id, mode, trace, [rc.PORTFOLIO_EVALUATION_FAILED],
            context, recognition, confidence, risk_decision, circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    if not portfolio_decision.approved:
        result = _denied(
            candidate, correlation_id, mode, trace, [rc.PORTFOLIO_DENIED, *portfolio_decision.reason_codes],
            context, recognition, confidence, risk_decision, portfolio_decision,
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )
        _notify(deps, "ORCHESTRATION_DENIED", "denied by Portfolio Manager", correlation_id, candidate.as_of)
        return result

    intent = ApprovedTradeIntent(
        proposal_id=correlation_id, correlation_id=correlation_id, strategy_id=candidate.strategy_id,
        symbol=candidate.symbol, direction=candidate.direction, entry=candidate.entry, stop=candidate.stop,
        target=candidate.target, as_of=candidate.as_of, volume=risk_decision.calculated_volume,
        monetary_risk=risk_decision.monetary_risk, magic_number=candidate.magic_number, comment=candidate.comment,
    )
    try:
        order_result = process_approved_intent(
            intent, deps.instrument, deps.portfolio, deps.broker_caps, deps.ledger, deps.order_journal,
            deps.adapter, resolved_config.order_manager_config,
        )
        trace.append(CalculationTraceStep("ORDER_MANAGER_CALLED", True, detail=order_result.state.value))
    except Exception as exc:  # noqa: BLE001 -- fail-closed.
        trace.append(CalculationTraceStep("ORDER_MANAGER_CALLED", False, detail=f"{type(exc).__name__}: {exc}"))
        return _denied(
            candidate, correlation_id, mode, trace, [rc.ORDER_MANAGER_FAILED],
            context, recognition, confidence, risk_decision, portfolio_decision,
            circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
        )

    _notify(deps, "ORCHESTRATION_APPROVED", f"order state={order_result.state.value}", correlation_id, candidate.as_of)
    return OrchestrationResult(
        correlation_id=correlation_id, strategy_id=candidate.strategy_id, symbol=candidate.symbol,
        as_of=candidate.as_of, mode=mode, approved=True, context=context, recognition=recognition,
        confidence=confidence, risk_decision=risk_decision, portfolio_decision=portfolio_decision,
        order_result=order_result, reason_codes=(), calculation_trace=tuple(trace),
        circuit_state_after=circuit_state_after, daily_state_after=daily_state_after,
    )


def reconcile_orchestrated_orders(deps: OrchestratorDependencies) -> tuple[Fill, ...]:
    """Thin wrapper over `execution_engine.reconciler.reconcile_all_open`, unmodified
    (`EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md` §9)."""
    return reconcile_all_open(deps.ledger, deps.adapter)
