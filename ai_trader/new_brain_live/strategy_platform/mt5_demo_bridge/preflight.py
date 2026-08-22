"""Consolidated broker preflight chain (mandate section 17). Every item is independently checked and
independently reported in `PreflightResult.reasons` -- no single failure hides another (same discipline
`SafetyGuardReport` itself already established). ANY unresolved failure -> the caller must treat this as
`NO_ORDER`; this module never partially proceeds."""

from __future__ import annotations

import dataclasses

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.safety import verify_safety_guards
from ai_trader.mt5_demo_execution.types import MT5DemoConfig, SafetyGuardReport
from ai_trader.new_brain_live.strategy_platform.ev_engine import EVDecision
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.mt5_execution_ledger import (
    RECONCILED_NEVER_ACCEPTED,
    MT5ExecutionLedger,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.order_identity import client_order_id_for
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis

NOT_CONNECTED = "PREFLIGHT_NOT_CONNECTED"
SAFETY_GUARDS_FAILED = "PREFLIGHT_SAFETY_GUARDS_FAILED"
DUPLICATE_IDENTITY = "PREFLIGHT_DUPLICATE_IDENTITY"
NO_TICK = "PREFLIGHT_NO_TICK"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PreflightResult:
    passed: bool
    reasons: tuple[str, ...]
    safety_guard_report: SafetyGuardReport | None = None
    tick_bid: float | None = None
    tick_ask: float | None = None
    client_order_id: str | None = None


def run_preflight(
    *, adapter: MT5DemoBrokerAdapter, config: MT5DemoConfig, symbol: str, ledger: MT5ExecutionLedger,
    hypothesis: TradeHypothesis, decision: EVDecision,
) -> PreflightResult:
    cid = client_order_id_for(hypothesis, decision)

    if not adapter.is_connected():
        return PreflightResult(passed=False, reasons=(NOT_CONNECTED,), client_order_id=cid)

    reasons: list[str] = []
    guard_report = verify_safety_guards(adapter, config, symbol=symbol)
    if not guard_report.all_passed:
        reasons.append(SAFETY_GUARDS_FAILED)

    existing = ledger.latest_state_for(cid)
    if existing is not None and existing.state != RECONCILED_NEVER_ACCEPTED:
        # this EXACT canonical event has already begun/completed a submission attempt -- never a second
        # one (mandate sections 12, 21, 25). The one deliberate exception: RECONCILED_NEVER_ACCEPTED is
        # reconciliation's own explicit "mechanically proven the prior attempt was never accepted by the
        # broker -- safe to retry" verdict (mandate section 24); everything else (including RECONCILED_
        # EXISTING, where a real broker position WAS found) still blocks.
        reasons.append(DUPLICATE_IDENTITY)

    tick = adapter.read_tick(symbol)
    bid = getattr(tick, "bid", None) if tick is not None else None
    ask = getattr(tick, "ask", None) if tick is not None else None
    if tick is None or bid is None or ask is None:
        reasons.append(NO_TICK)

    return PreflightResult(
        passed=not reasons, reasons=tuple(reasons), safety_guard_report=guard_report,
        tick_bid=bid, tick_ask=ask, client_order_id=cid,
    )
