"""``RiskManager`` -- the public facade implementing ``RISK_API.md`` exactly.

Wires together the per-opportunity pipeline (:mod:`ai_trader.risk_manager.pipeline`), the Position
Sizer (:mod:`ai_trader.risk_manager.sizing`), the Assembler (:mod:`ai_trader.risk_manager.assembler`),
and the Output Collector's validation (:mod:`ai_trader.risk_manager.validator`) into the documented,
deterministic, fail-safe risk-decision cycle. A pure decision function: no signal, no score, no
learning, no execution, no research access (``RISK_MANAGER_ARCHITECTURE.md`` §2).

**Determinism note**: no module reached from this file imports ``time``/``random`` -- ``timestamp``
is always the evaluated opportunity's own ``as_of``. Opportunities within one ``evaluate()`` batch are
always processed in ascending ``rank`` order regardless of the order the caller supplies them in,
guaranteeing the "running portfolio view" (architecture §5/§9) is reproducible from the batch content
alone, never from incidental list ordering.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ai_trader.risk_manager import assembler, pipeline, validator
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.exceptions import EngineNotConfiguredError
from ai_trader.risk_manager.sizing import compute_sizing
from ai_trader.risk_manager.types import (
    Decision,
    DeniedReason,
    EngineHealth,
    EngineLifecycleState,
    EngineOverallHealth,
    EngineState,
    LimitsReport,
    OpenPosition,
    PortfolioState,
    RiskContext,
    RiskDecision,
    RiskDecisionBatch,
    Sizing,
    SizingMethod,
    SizingResult,
    Statistics,
    ValidationResult,
    VersionInfo,
)
from ai_trader.scoring_engine.types import OpportunityScore

_LIFECYCLE_TO_GLOBAL: dict[EngineLifecycleState, EngineState] = {
    EngineLifecycleState.READY: EngineState.READY,
    EngineLifecycleState.EVALUATING: EngineState.READY,
    EngineLifecycleState.SUSPENDED: EngineState.SUSPENDED,
    EngineLifecycleState.EMERGENCY_STOP: EngineState.EMERGENCY_STOP,
}

_ZERO_SIZING = Sizing(
    method=SizingMethod.FIXED_FRACTIONAL, risk_per_trade_pct=0.0, risk_R=0.0,
    size_units=0.0, min_size=0.0, max_size=0.0,
)


def _global_state(lifecycle: EngineLifecycleState) -> EngineState:
    return _LIFECYCLE_TO_GLOBAL.get(lifecycle, EngineState.EMERGENCY_STOP)


def _guard_breached(portfolio: PortfolioState, config: RiskConfig) -> bool:
    """Whether ANY loss/drawdown guard is currently tripped against ``portfolio`` -- the recovery
    guard condition shared by :meth:`RiskManager.resume`/:meth:`RiskManager.clear_emergency` and
    startup reconciliation (``RISK_POLICY.md`` §9: recovery "requires ... drawdown recovered")."""
    daily_breach = portfolio.daily_pnl_pct <= -config.loss_drawdown.max_daily_loss_pct
    weekly_breach = portfolio.weekly_pnl_pct <= -config.loss_drawdown.max_weekly_loss_pct
    drawdown_breach = portfolio.drawdown_pct >= config.loss_drawdown.drawdown_reset_threshold_pct
    return daily_breach or weekly_breach or drawdown_breach


def _finalize_decision(
    opportunity: OpportunityScore, outcome: pipeline.PipelineOutcome, engine_state: EngineState,
    config: RiskConfig, portfolio_after: PortfolioState | None,
) -> RiskDecision:
    """Assemble + validate a decision, with a safe fallback if it fails its OWN validation.

    Regression note: the first reassembly (``assemble_invalid_decision(opportunity, ...)``) copies
    identity fields (``strategy_id``, ``refs``, ...) straight from the SAME opportunity that may have
    caused the original schema failure -- if that field was itself the problem (e.g. a malformed
    ``strategy_id``), the "fixed" decision can still be schema-invalid. Re-validating and falling back
    to the fully placeholder-based decision (``opportunity=None``) if it is STILL invalid guarantees a
    genuinely conformant decision is always emitted, mirroring the identical fix applied to the
    Scoring Engine's own ``_finalize_one`` for the same class of bug.
    """
    decision = assembler.assemble_decision(opportunity, outcome, engine_state, config, portfolio_after=portfolio_after)
    result = validator.validate_decision(decision)
    if not result.valid:
        detail = "; ".join(result.reasons)
        decision = assembler.assemble_invalid_decision(opportunity, config, detail=detail, engine_state=engine_state)
        if not validator.validate_decision(decision).valid:
            decision = assembler.assemble_invalid_decision(None, config, detail=detail, engine_state=engine_state)
    return decision


def _evaluate_one(
    opportunity: OpportunityScore, risk_context: RiskContext, portfolio: PortfolioState, config: RiskConfig,
    engine_state: EngineState, state_reason_code: str,
) -> tuple[RiskDecision, PortfolioState, EngineState | None]:
    """Runs the fixed pipeline for ONE opportunity against ``portfolio``, applies any ALLOW to the
    running view, and finalizes/validates the decision -- catching ANY exception anywhere in that
    chain and degrading to a classified ``DENY(INTERNAL_ERROR)`` instead of ever propagating
    (README.md: "one bad opportunity never affects the evaluation of the others"; architecture §7:
    "internal/sizing/validation error -> DENY(INTERNAL_*); batch continues"). ``pipeline.py``'s own
    module docstring claims its logic is "exception-free by construction", but that only holds if
    every upstream field is well-typed at runtime -- which a Python dataclass does not enforce -- so
    this boundary exists precisely for the case that assumption doesn't hold.

    Returns ``(decision, portfolio_after, escalate_to)`` -- ``portfolio_after`` equals the input
    ``portfolio`` unchanged if the opportunity was denied or an exception was caught.
    """
    try:
        outcome = pipeline.evaluate_opportunity(
            opportunity, risk_context, portfolio, config, engine_state, state_reason_code,
        )
        portfolio_after = portfolio
        if outcome.allowed and outcome.sizing is not None:
            portfolio_after = _apply_allow_to_portfolio(portfolio, opportunity, outcome.sizing, config)
        decision = _finalize_decision(opportunity, outcome, engine_state, config, portfolio_after)
        return decision, portfolio_after, outcome.escalate_to
    except Exception:  # noqa: BLE001 -- any failure anywhere in this opportunity's own evaluation
        # is classified and isolated here, never propagated to crash the rest of the batch/call.
        decision = assembler.assemble_invalid_decision(
            opportunity, config, reason_code="INTERNAL_ERROR",
            detail="unexpected exception during evaluation", engine_state=engine_state,
        )
        if not validator.validate_decision(decision).valid:
            decision = assembler.assemble_invalid_decision(
                None, config, reason_code="INTERNAL_ERROR", engine_state=engine_state,
            )
        return decision, portfolio, None


def _apply_allow_to_portfolio(
    portfolio: PortfolioState, opportunity: OpportunityScore, sizing: Sizing, config: RiskConfig,
) -> PortfolioState:
    """The running-portfolio-view update after an ALLOW (architecture §5: "an ALLOW earlier in the
    ranked batch consumes budget/slots for later ones") -- a synthetic new open position + updated
    aggregate notional, so later opportunities in the same batch see the effect."""
    new_position = OpenPosition(
        symbol=opportunity.symbol, strategy_id=opportunity.strategy_id, direction=opportunity.direction,
        size_units=sizing.size_units,
        entry_price=(opportunity.trade_context.entry or 0.0) if opportunity.trade_context else 0.0,
        opened_bars_ago=0, risk_pct=sizing.risk_per_trade_pct, notional=sizing.notional or 0.0,
        correlation_group=config.correlation_group_for(opportunity.symbol),
    )
    return replace(
        portfolio,
        open_positions=portfolio.open_positions + (new_position,),
        gross_notional=portfolio.gross_notional + (sizing.notional or 0.0),
    )


class RiskManager:
    """The Risk Manager. See ``RISK_API.md`` for the full contract."""

    def __init__(self, config: RiskConfig | None = None) -> None:
        self._config = config or RiskConfig()
        self._lifecycle_state = EngineLifecycleState.IDLE
        self._state_reason_code = "READY"
        self._degraded = False
        self._degraded_reasons: list[str] = []
        self._last_portfolio: PortfolioState | None = None
        self._batches = 0
        self._decisions_total = 0
        self._allow = 0
        self._deny = 0
        self._by_reason: dict[str, int] = {}

    # ------------------------------------------------------------------ 0. configuration

    def configure(self, portfolio: PortfolioState | None = None) -> None:
        """Idempotent full reset. Reconciles the initial global state from ``portfolio``
        (``RISK_SEQUENCE.md`` §1: "daily/weekly loss or drawdown already breached -> SUSPENDED").
        ``portfolio=None`` starts the engine DEGRADED (the Portfolio Manager handshake "failed") --
        it still reaches READY-lifecycle so introspection works, but every ``evaluate()`` denies with
        ``PORTFOLIO_UNAVAILABLE`` until a real snapshot arrives."""
        self._batches = 0
        self._decisions_total = 0
        self._allow = 0
        self._deny = 0
        self._by_reason = {}
        self._degraded_reasons = []
        self._last_portfolio = portfolio

        if portfolio is None or portfolio.is_stale:
            self._degraded = True
            self._degraded_reasons.append("no PortfolioState available at configure()")
            self._lifecycle_state = EngineLifecycleState.READY
            self._state_reason_code = "READY"
            return

        self._degraded = False
        if _guard_breached(portfolio, self._config):
            self._lifecycle_state = EngineLifecycleState.SUSPENDED
            self._state_reason_code = "LOSS_DAILY" if portfolio.daily_pnl_pct <= -self._config.loss_drawdown.max_daily_loss_pct else (
                "LOSS_WEEKLY" if portfolio.weekly_pnl_pct <= -self._config.loss_drawdown.max_weekly_loss_pct else "DRAWDOWN_MAX"
            )
        else:
            self._lifecycle_state = EngineLifecycleState.READY
            self._state_reason_code = "READY"

    def _require_configured(self) -> None:
        if self._lifecycle_state in (EngineLifecycleState.IDLE, EngineLifecycleState.SHUTDOWN):
            raise EngineNotConfiguredError("RiskManager.configure() must be called first")

    # ------------------------------------------------------------------ 1. decision

    def evaluate(
        self, opportunities: Sequence[OpportunityScore], risk_context: RiskContext,
        portfolio: PortfolioState | None,
    ) -> RiskDecisionBatch:
        """The normal entry point (``RISK_API.md`` §1). Empty input -> empty batch (valid)."""
        self._require_configured()
        if not opportunities:
            batch = RiskDecisionBatch(
                as_of=risk_context.as_of, decisions=(), counts_by_decision={},
                engine_state=_global_state(self._lifecycle_state), generated_at=risk_context.as_of,
            )
            self._record_batch(batch)
            return batch

        if portfolio is None or portfolio.is_stale:
            self._degraded = True
            if "PortfolioState unavailable/stale at evaluate()" not in self._degraded_reasons:
                self._degraded_reasons.append("PortfolioState unavailable/stale at evaluate()")
            engine_state = _global_state(self._lifecycle_state)
            unavailable_decisions = tuple(
                _finalize_decision(
                    opp, pipeline.PipelineOutcome(
                        allowed=False, applied_rules=(), denied_reasons=(DeniedReason(code="PORTFOLIO_UNAVAILABLE"),),
                    ),
                    engine_state, self._config, None,
                )
                for opp in sorted(opportunities, key=lambda o: o.rank)
            )
            batch = RiskDecisionBatch(
                as_of=risk_context.as_of, decisions=unavailable_decisions,
                counts_by_decision=_counts(unavailable_decisions),
                engine_state=engine_state, generated_at=risk_context.as_of,
            )
            self._record_batch(batch)
            return batch

        self._last_portfolio = portfolio
        # A fresh, non-stale PortfolioState arriving here means the Portfolio Manager handshake is
        # healthy again -- clear any previously recorded portfolio-availability degradation so
        # health() recovers to OK once evaluate() sees good data (RISK_SEQUENCE.md §8: "recovers to
        # normal ... once PortfolioState is fresh again"), rather than staying DEGRADED forever.
        self._degraded_reasons = [r for r in self._degraded_reasons if "PortfolioState" not in r]
        self._degraded = bool(self._degraded_reasons)
        if self._lifecycle_state is EngineLifecycleState.READY:
            # EVALUATING is a transient sub-state of READY (RISK_STATE_MACHINE.md §A) -- a batch
            # that starts SUSPENDED/EMERGENCY_STOP must stay in that state throughout (never
            # silently downgraded to a state that reads as READY to the per-opportunity Global
            # State Gate below), so every opportunity is correctly denied for the real reason.
            self._lifecycle_state = EngineLifecycleState.EVALUATING
        running_portfolio = portfolio
        decisions: list[RiskDecision] = []
        state_reason = self._state_reason_code

        for opp in sorted(opportunities, key=lambda o: o.rank):
            engine_state = _global_state(self._lifecycle_state)
            decision, running_portfolio, escalate_to = _evaluate_one(
                opp, risk_context, running_portfolio, self._config, engine_state, state_reason,
            )

            if escalate_to is not None:
                self._lifecycle_state = EngineLifecycleState(escalate_to.value)
                self._state_reason_code = decision.denied_reasons[0].code if decision.denied_reasons else "SUSPENDED"
                state_reason = self._state_reason_code

            decisions.append(decision)

        self._lifecycle_state = (
            self._lifecycle_state if self._lifecycle_state in (EngineLifecycleState.SUSPENDED, EngineLifecycleState.EMERGENCY_STOP)
            else EngineLifecycleState.READY
        )
        self._last_portfolio = running_portfolio
        batch = RiskDecisionBatch(
            as_of=risk_context.as_of, decisions=tuple(decisions), counts_by_decision=_counts(tuple(decisions)),
            engine_state=_global_state(self._lifecycle_state), generated_at=risk_context.as_of,
        )
        self._record_batch(batch)
        return batch

    def allow_trade(
        self, opportunity: OpportunityScore, risk_context: RiskContext, portfolio: PortfolioState | None,
    ) -> RiskDecision:
        """Evaluate a single opportunity (``RISK_API.md`` §1) -- the running-portfolio effect of a
        batch is NOT applied/persisted."""
        self._require_configured()
        engine_state = _global_state(self._lifecycle_state)
        if portfolio is None or portfolio.is_stale:
            outcome = pipeline.PipelineOutcome(
                allowed=False, applied_rules=(), denied_reasons=(DeniedReason(code="PORTFOLIO_UNAVAILABLE"),),
            )
            decision = _finalize_decision(opportunity, outcome, engine_state, self._config, None)
        else:
            # Routes through the same exception-safe helper used by evaluate() so a single-opportunity
            # call gets identical crash protection, AND so this decision's own portfolio_impact
            # reflects its own ALLOW effect (previously it reported the pre-trade portfolio unchanged,
            # inconsistent with what evaluate() reports for the identical opportunity).
            decision, _portfolio_after, _escalate_to = _evaluate_one(
                opportunity, risk_context, portfolio, self._config, engine_state, self._state_reason_code,
            )
        self._record_scores((decision,))
        return decision

    def position_size(
        self, opportunity: OpportunityScore, portfolio: PortfolioState, risk_context: RiskContext,
    ) -> SizingResult:
        """Compute the deterministic size assuming the opportunity is allowed -- does not apply the
        policy gates (``RISK_API.md`` §1)."""
        outcome = compute_sizing(opportunity, portfolio, self._config)
        if outcome.valid and outcome.sizing is not None:
            return SizingResult(sizing=outcome.sizing, valid=True)
        reason = outcome.deny_reason.code if outcome.deny_reason else "SIZE_BELOW_MIN"
        return SizingResult(sizing=_ZERO_SIZING, valid=False, reason=reason)

    # ------------------------------------------------------------------ 2. portfolio limits & introspection

    def portfolio_limits(self, portfolio: PortfolioState) -> LimitsReport:
        pl = self._config.portfolio_limits
        limits_map = {
            "max_positions": float(pl.max_positions), "max_per_symbol": float(pl.max_per_symbol),
            "max_correlated": float(pl.max_correlated), "max_exposure_pct": pl.max_exposure_pct,
            "max_leverage": pl.max_leverage, "max_overnight_exposure_pct": pl.max_overnight_exposure_pct,
        }
        utilization = {
            "open_positions": float(len(portfolio.open_positions)),
            "portfolio_risk_pct": portfolio.portfolio_risk_pct, "leverage": portfolio.leverage,
            "daily_pnl_pct": portfolio.daily_pnl_pct, "weekly_pnl_pct": portfolio.weekly_pnl_pct,
            "drawdown_pct": portfolio.drawdown_pct,
        }
        breaches: list[str] = []
        if len(portfolio.open_positions) >= pl.max_positions:
            breaches.append("LIMIT_MAX_POSITIONS")
        if portfolio.portfolio_risk_pct >= pl.max_exposure_pct:
            breaches.append("LIMIT_MAX_EXPOSURE")
        if portfolio.leverage >= pl.max_leverage:
            breaches.append("LIMIT_MAX_LEVERAGE")
        if portfolio.daily_pnl_pct <= -self._config.loss_drawdown.max_daily_loss_pct:
            breaches.append("LOSS_DAILY")
        if portfolio.weekly_pnl_pct <= -self._config.loss_drawdown.max_weekly_loss_pct:
            breaches.append("LOSS_WEEKLY")
        if portfolio.drawdown_pct >= self._config.loss_drawdown.max_drawdown_pct:
            breaches.append("DRAWDOWN_MAX")
        return LimitsReport(
            engine_state=_global_state(self._lifecycle_state), limits=limits_map,
            current_utilization=utilization, breaches=tuple(breaches),
        )

    def validate(self, decision: RiskDecision) -> ValidationResult:
        return validator.validate_decision(decision)

    def statistics(self) -> Statistics:
        return Statistics(
            batches=self._batches, decisions_total=self._decisions_total, allow=self._allow, deny=self._deny,
            by_reason=dict(self._by_reason), avg_eval_ms=0.0,
        )

    def health(self) -> EngineHealth:
        if self._lifecycle_state in (EngineLifecycleState.IDLE, EngineLifecycleState.SHUTDOWN):
            overall = EngineOverallHealth.FAILED
        elif self._degraded_reasons:
            overall = EngineOverallHealth.DEGRADED
        else:
            overall = EngineOverallHealth.OK
        return EngineHealth(
            overall=overall, state=self._lifecycle_state, degraded_reasons=tuple(self._degraded_reasons),
            supported_versions={
                "scoring_schema_major": self._config.supported_scoring_schema_major,
                "interface_major": self._config.supported_interface_major,
            },
        )

    def versions(self) -> VersionInfo:
        return VersionInfo(
            risk_engine_version=self._config.risk_engine_version,
            risk_schema_version=self._config.risk_schema_version,
            risk_policy_version=self._config.risk_policy_version,
            supported_scoring_schema_major=self._config.supported_scoring_schema_major,
            supported_interface_major=self._config.supported_interface_major,
        )

    # ------------------------------------------------------------------ 3. operational controls

    def suspend(self, reason: str) -> EngineHealth:
        self._require_configured()
        self._lifecycle_state = EngineLifecycleState.SUSPENDED
        self._state_reason_code = "SUSPENDED"
        return self.health()

    def resume(self) -> EngineHealth:
        """Guarded: only resumes if no guard is currently tripped against the last known
        ``PortfolioState`` (``RISK_POLICY.md`` §9). Fail-safe: remains SUSPENDED if unguarded."""
        self._require_configured()
        if self._lifecycle_state is EngineLifecycleState.SUSPENDED:
            if self._last_portfolio is not None and not _guard_breached(self._last_portfolio, self._config):
                self._lifecycle_state = EngineLifecycleState.READY
                self._state_reason_code = "READY"
        return self.health()

    def emergency_stop(self, reason: str, is_kill_switch: bool = False) -> EngineHealth:
        self._require_configured()
        self._lifecycle_state = EngineLifecycleState.EMERGENCY_STOP
        self._state_reason_code = "KILL_SWITCH" if is_kill_switch else "EMERGENCY_STOP"
        return self.health()

    def clear_emergency(self) -> EngineHealth:
        """Guarded: requires ``PortfolioState`` reconciled AND no guard tripped
        (``RISK_POLICY.md`` §9). Fail-safe: remains EMERGENCY_STOP if unguarded or no snapshot."""
        self._require_configured()
        if self._lifecycle_state is EngineLifecycleState.EMERGENCY_STOP:
            if self._last_portfolio is not None and not self._last_portfolio.is_stale and not _guard_breached(self._last_portfolio, self._config):
                self._lifecycle_state = EngineLifecycleState.READY
                self._state_reason_code = "READY"
        return self.health()

    # ------------------------------------------------------------------ 4. shutdown

    def shutdown(self) -> EngineHealth:
        """Stop accepting new evaluations; release snapshots (architecture §12: "hold no truth of
        fills")."""
        self._require_configured()
        final_health = self.health()  # captured BEFORE flipping state, same precedent as every
        # prior module's own shutdown() -- "stopped" must not be misreported as a synthetic FAILED.
        self._last_portfolio = None
        self._lifecycle_state = EngineLifecycleState.SHUTDOWN
        return final_health

    # ------------------------------------------------------------------ internals

    def _record_batch(self, batch: RiskDecisionBatch) -> None:
        self._batches += 1
        self._record_scores(batch.decisions)

    def _record_scores(self, decisions: tuple[RiskDecision, ...]) -> None:
        for decision in decisions:
            self._decisions_total += 1
            if decision.decision is Decision.ALLOW:
                self._allow += 1
            else:
                self._deny += 1
                for reason in decision.denied_reasons:
                    self._by_reason[reason.code] = self._by_reason.get(reason.code, 0) + 1


def _counts(decisions: tuple[RiskDecision, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for decision in decisions:
        counts[decision.decision.value] = counts.get(decision.decision.value, 0) + 1
    return counts
