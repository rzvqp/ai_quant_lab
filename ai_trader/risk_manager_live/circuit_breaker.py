"""`evaluate_circuit_state` -- the persistent loss/drawdown circuit breaker (Risk Audit #1 fix,
2026-07-25). Unifies the three previously-disconnected mechanisms that finding named:

1. `guards.py`'s `GuardResult.escalate_to` (`EngineState.SUSPENDED` on a daily/weekly-loss or
   max-drawdown breach) -- computed by the reused, frozen guards, previously discarded by the caller
   loop in `risk_manager_live/engine.py`.
2. The daily/weekly P&L + drawdown fields those guards read -- unchanged here; this module still takes
   whatever `PortfolioState` its injected `PortfolioStateSource` supplies (real or virtual, same
   interface, per the CEO's own instruction).
3. `execution_orchestrator`'s own `emergency_stop` override -- now persists into the same state object
   instead of being a single-call, ephemeral flag.

Pure function: no state, no I/O, no wall-clock (`as_of` is always caller-supplied). The caller persists
`TradingCircuitState` across calls -- the same discipline already established for `PortfolioDailyState`
(`portfolio_manager_live/types.py`). Reuses `risk_manager.guards.run_loss_drawdown_guards` (breach
detection) and deliberately reuses `risk_manager.engine._guard_breached` (recovery-eligibility) --
private, but the EXACT function the frozen batch engine's own `resume()`/`clear_emergency()` already use
for identical semantics; reimplementing the same three-line hysteresis condition here would risk silent
drift from that already-reviewed policy (in particular the asymmetric drawdown reset gap: breach at
`max_drawdown_pct`, recovery only below the tighter `drawdown_reset_threshold_pct`).
"""

from __future__ import annotations

from ai_trader.risk_manager import guards
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import _guard_breached  # noqa: SLF001 -- deliberate reuse, see
# module docstring: this is the exact recovery-eligibility condition the frozen engine's own
# resume()/clear_emergency() already use; duplicating it would risk silent drift.
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live import reason_codes as rc
from ai_trader.risk_manager_live.types import PortfolioStateSource, TradingCircuitState


def evaluate_circuit_state(
    current: TradingCircuitState, source: PortfolioStateSource, config: RiskConfig, as_of: int,
    emergency_stop_requested: bool = False,
) -> TradingCircuitState:
    """Returns the NEW `TradingCircuitState` the caller must persist for its next call. Order of
    precedence, fixed: (1) a fresh `emergency_stop_requested=True` always wins, overriding any other
    state; (2) an existing `EMERGENCY_STOP` is sticky -- it never auto-clears, matching the frozen
    engine's own guarded `clear_emergency()` precedent (no automatic recovery path exists for it here;
    a future explicit clear operation is a disclosed, separate gap, not silently assumed); (3) an
    existing `SUSPENDED` only clears if `source`'s current portfolio state is FULLY recovered (the same
    hysteresis-gated condition `_guard_breached` checks); (4) otherwise, run the loss/drawdown guards
    fresh against `source`'s current portfolio state and suspend on the first breach, in the guards'
    own fixed order."""
    if emergency_stop_requested:
        return TradingCircuitState(
            state=EngineState.EMERGENCY_STOP, reason_code=rc.CIRCUIT_EMERGENCY_STOP_REQUESTED, since=as_of,
        )

    if current.state is EngineState.EMERGENCY_STOP:
        return current

    portfolio = source.current_portfolio_state()

    if current.state is EngineState.SUSPENDED:
        if not _guard_breached(portfolio, config):
            return TradingCircuitState(state=EngineState.READY, reason_code=None, since=None)
        return current

    for _name, result in guards.run_loss_drawdown_guards(portfolio, config):
        if not result.passed and result.escalate_to is not None:
            reason = result.reason.code if result.reason is not None else rc.CIRCUIT_SUSPENDED
            return TradingCircuitState(state=result.escalate_to, reason_code=reason, since=as_of)

    return current
