"""`send_after_dry_run_gate` -- CEO: "never send an order until the same intent's dry-run has passed."
Runs `execution_orchestrator.orchestrate(..., mode=DRY_RUN)` first, against its OWN, separate ledger/
journal; only if that run is `approved` AND its `order_result.state is ACKNOWLEDGED` does it then run
`orchestrate(..., mode=DEMO)` against a SEPARATE ledger/journal. Reusing the dry-run's own ledger for the
demo leg would hit the SAME deterministic `client_order_id`'s idempotency guard and silently short-
circuit the real attempt to the cached dry-run record -- a correctness requirement, not a style choice
(`MT5_DEMO_EXECUTION_PHASE10_DESIGN.md` §2)."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.execution_orchestrator.engine import orchestrate
from ai_trader.execution_orchestrator.types import (
    CandidateSignal,
    ExecutionMode,
    OrchestrationResult,
    OrchestratorConfig,
    OrchestratorDependencies,
)
from ai_trader.mt5_demo_execution import reason_codes as rc
from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.types import SafetyGuardReport
from ai_trader.strategy_runtime.context_access import MarketContext


@dataclass(frozen=True, slots=True)
class GatedDemoOutcome:
    dry_run_result: OrchestrationResult
    demo_result: OrchestrationResult | None
    safety_guard_report: SafetyGuardReport | None
    reason_codes: tuple[str, ...]

    @property
    def sent(self) -> bool:
        return self.demo_result is not None and self.demo_result.approved


def send_after_dry_run_gate(
    candidate: CandidateSignal, market_context: MarketContext, dry_run_deps: OrchestratorDependencies,
    demo_deps: OrchestratorDependencies, demo_adapter: MT5DemoBrokerAdapter,
    safety_guard_report: SafetyGuardReport, emergency_stop: bool = False,
    config: OrchestratorConfig | None = None,
) -> GatedDemoOutcome:
    """`dry_run_deps.adapter` MUST be a `DryRunBrokerAdapter`; `demo_deps.adapter` MUST be the SAME
    `demo_adapter` passed separately here (required as its own parameter so `verify_safety_guards`'s own
    caller and this gate's own caller are visibly the same object, never two adapters silently drifting
    apart). `dry_run_deps` and `demo_deps` MUST use different `ledger`/`order_journal` instances (see
    module docstring)."""
    dry_run_result = orchestrate(candidate, market_context, dry_run_deps, mode=ExecutionMode.DRY_RUN, emergency_stop=emergency_stop, config=config)

    dry_run_passed = (
        dry_run_result.approved and dry_run_result.order_result is not None
        and dry_run_result.order_result.state.value == "ACKNOWLEDGED"
    )
    if not dry_run_passed:
        return GatedDemoOutcome(
            dry_run_result=dry_run_result, demo_result=None, safety_guard_report=None,
            reason_codes=(rc.DRY_RUN_DID_NOT_PASS,),
        )

    if not safety_guard_report.all_passed:
        return GatedDemoOutcome(
            dry_run_result=dry_run_result, demo_result=None, safety_guard_report=safety_guard_report,
            reason_codes=(rc.SAFETY_GUARDS_FAILED,),
        )

    if id(demo_deps.adapter) != id(demo_adapter):
        raise ValueError("send_after_dry_run_gate: demo_deps.adapter must be the SAME object as demo_adapter")

    demo_result = orchestrate(candidate, market_context, demo_deps, mode=ExecutionMode.DEMO, emergency_stop=emergency_stop, config=config)
    return GatedDemoOutcome(
        dry_run_result=dry_run_result, demo_result=demo_result, safety_guard_report=safety_guard_report,
        reason_codes=demo_result.reason_codes,
    )
