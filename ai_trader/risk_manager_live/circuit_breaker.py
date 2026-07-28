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

**Mandate 3, Element 2 (2026-07-27), circuit-state persistence + the EMERGENCY_STOP reset path**:
`persist_circuit_state`/`load_persisted_circuit_state` make `TradingCircuitState` itself survive a
process restart -- this was NOT part of Mandate 2's three components (bar-feed watermark, journal,
equity high-water mark); verified, not assumed, before writing anything here, since the CEO's own
required test ("proces suspendat, repornire, disjunctorul inca activ") cannot pass without it.
`evaluate_circuit_state` itself is UNCHANGED -- still pure, still takes `current` as an explicit
parameter -- restart-survival is achieved entirely by the CALLER loading the persisted state instead of
defaulting to `READY_CIRCUIT_STATE` on startup, then persisting whatever this function (or
`reset_emergency_stop`) returns.

`reset_emergency_stop` is the ONLY function in this codebase that transitions OUT of `EMERGENCY_STOP` --
deliberate and explicit by construction (CEO specification, closing Step 1's own disclosed gap): it
reads the CURRENTLY PERSISTED state (never a possibly-stale in-memory value), requires it to actually be
`EMERGENCY_STOP` (a caller resetting anything else is an error, not a silent no-op), and journals the
reset with a reason and timestamp on its own dedicated log BEFORE persisting the new `READY` state --
never automatic, never a side effect of loading the state after a restart (`test_emergency_stop_
survives_a_simulated_restart_without_any_automatic_reset` proves this directly).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager import guards
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.engine import _guard_breached  # noqa: SLF001 -- deliberate reuse, see
# module docstring: this is the exact recovery-eligibility condition the frozen engine's own
# resume()/clear_emergency() already use; duplicating it would risk silent drift.
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live import reason_codes as rc
from ai_trader.risk_manager_live.types import READY_CIRCUIT_STATE, PortfolioStateSource, TradingCircuitState

_CIRCUIT_STATE_LOG = "risk_manager_live.circuit_state"
_EMERGENCY_STOP_RESET_LOG = "risk_manager_live.circuit_state.emergency_stop_resets"


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


@dataclass(frozen=True, slots=True)
class EmergencyStopResetRecord:
    """One row of the EMERGENCY_STOP reset audit trail -- `reason` and `as_of` are exactly what the
    CEO's specification requires every reset to carry; `previous_reason_code` records what was being
    cleared, for anyone auditing the history later."""

    reason: str
    as_of: int
    previous_reason_code: str | None


def _serialize_circuit_state(circuit_state: TradingCircuitState, as_of: int) -> str:
    return json.dumps({
        "state": circuit_state.state.value, "reason_code": circuit_state.reason_code,
        "since": circuit_state.since, "as_of": as_of,
    })


def _deserialize_circuit_state(payload: str) -> TradingCircuitState:
    data = json.loads(payload)
    return TradingCircuitState(
        state=EngineState(data["state"]), reason_code=data["reason_code"], since=data["since"],
    )


def persist_circuit_state(state_store: SqliteStateStore, circuit_state: TradingCircuitState, as_of: int) -> None:
    """The caller must call this after every `evaluate_circuit_state`/`reset_emergency_stop` call whose
    result should survive a restart -- this module never calls it on its own (matching
    `evaluate_circuit_state`'s own "no I/O" design; only `reset_emergency_stop` below is impure, and
    deliberately so)."""
    state_store.append_log_entry(_CIRCUIT_STATE_LOG, _serialize_circuit_state(circuit_state, as_of))


def load_persisted_circuit_state(state_store: SqliteStateStore) -> TradingCircuitState:
    """Returns the LAST persisted circuit state, or `READY_CIRCUIT_STATE` if nothing has ever been
    persisted (a brand-new deployment -- not a prior SUSPENDED/EMERGENCY_STOP being silently discarded;
    those cases always have at least one prior `persist_circuit_state` call to read back). Loading never
    mutates anything -- it is not a reset, confirmed directly by
    `test_emergency_stop_survives_a_simulated_restart_without_any_automatic_reset`."""
    entries = state_store.read_log_entries(_CIRCUIT_STATE_LOG)
    if not entries:
        return READY_CIRCUIT_STATE
    return _deserialize_circuit_state(entries[-1])


def _serialize_reset(record: EmergencyStopResetRecord) -> str:
    return json.dumps({
        "reason": record.reason, "as_of": record.as_of,
        "previous_reason_code": record.previous_reason_code,
    })


def _deserialize_reset(payload: str) -> EmergencyStopResetRecord:
    data = json.loads(payload)
    return EmergencyStopResetRecord(
        reason=data["reason"], as_of=data["as_of"], previous_reason_code=data["previous_reason_code"],
    )


def emergency_stop_resets(state_store: SqliteStateStore) -> tuple[EmergencyStopResetRecord, ...]:
    """The full, append-only audit trail of every deliberate EMERGENCY_STOP reset ever performed
    against this store."""
    return tuple(_deserialize_reset(payload) for payload in state_store.read_log_entries(_EMERGENCY_STOP_RESET_LOG))


def reset_emergency_stop(state_store: SqliteStateStore, reason: str, as_of: int) -> TradingCircuitState:
    """The ONLY function in this codebase that transitions OUT of `EMERGENCY_STOP` -- see this module's
    own docstring for the full specification. Raises `ValueError` if the currently PERSISTED state is
    not `EMERGENCY_STOP` (resetting anything else is a caller error, not a no-op) or if `reason` is
    empty (every reset is journaled WITH a reason -- an empty one is not acceptable input, not merely an
    omission). Journals the reset before persisting the new state, so a reset is never recorded without
    a reason and never partially applied."""
    current = load_persisted_circuit_state(state_store)
    if current.state is not EngineState.EMERGENCY_STOP:
        raise ValueError(
            f"reset_emergency_stop: current persisted state must be EMERGENCY_STOP, got {current.state!r}"
        )
    if not reason:
        raise ValueError("reset_emergency_stop: reason must not be empty")

    state_store.append_log_entry(
        _EMERGENCY_STOP_RESET_LOG,
        _serialize_reset(EmergencyStopResetRecord(
            reason=reason, as_of=as_of, previous_reason_code=current.reason_code,
        )),
    )
    new_state = TradingCircuitState(state=EngineState.READY, reason_code=None, since=None)
    persist_circuit_state(state_store, new_state, as_of)
    return new_state
