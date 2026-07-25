# Phase 2A, Step 1 — Persistent Suspension State — Implementation Report

**Scope**: exclusively the defect documented as Risk Audit #1 (`AI_TRADER_RISK_AUDIT.md` §1) and restated
as Demo Readiness precondition #1 (`AI_TRADER_DEMO_READINESS_AUDIT.md`). No refactor, no improvement, no
optimization beyond this one fix. No live signal source built. No Phase 1-10 code touched outside the two
files the finding itself named (`risk_manager_live/engine.py`, `execution_orchestrator/engine.py`) plus
their own `types.py`/`reason_codes.py`/`__init__.py`. No 5%-sizing logic implemented.

## What the defect was

Three mechanisms existed to "stop trading," uncoordinated:
1. `guards.py`'s `GuardResult.escalate_to` (`EngineState.SUSPENDED` on a daily/weekly-loss or
   max-drawdown breach) — computed, then discarded by the loop in `risk_manager_live/engine.py:123`.
2. The P&L fields those guards read — raw, caller-supplied, no persistence across calls.
3. `execution_orchestrator`'s `emergency_stop: bool` (`engine.py:69`) — a single-call override with no
   relationship to the other two.

Net effect: a real breach denied one proposal and left no trace that trading should stay halted.

## What was built

- **`risk_manager_live/types.py`**: `LiveRiskDecision.escalate_to: EngineState | None = None` (additive
  field — surfaces what guards already compute); `TradingCircuitState` (frozen, caller-persisted, mirrors
  `PortfolioDailyState`'s own "pure data, caller owns it" discipline); `READY_CIRCUIT_STATE` (the named
  starting value); `PortfolioStateSource` (`Protocol`, one method, `current_portfolio_state() ->
  PortfolioState` — the injected P&L source the CEO required, real or virtual, same interface, no two
  parallel implementations).
- **`risk_manager_live/circuit_breaker.py`** (new file): `evaluate_circuit_state(current, source, config,
  as_of, emergency_stop_requested=False) -> TradingCircuitState`, pure function. Reuses
  `guards.run_loss_drawdown_guards` (breach detection, unmodified) and deliberately reuses the private
  `risk_manager.engine._guard_breached` (recovery-eligibility — the exact hysteresis condition the frozen
  engine's own `resume()`/`clear_emergency()` already use: breach at `max_drawdown_pct` 12%, recovery only
  below the tighter `drawdown_reset_threshold_pct` 8%, same asymmetric gap for daily/weekly loss at their
  own thresholds). `emergency_stop_requested=True` always wins; an existing `EMERGENCY_STOP` is sticky
  (never auto-clears — no clear operation exists yet, disclosed, not silently assumed); an existing
  `SUSPENDED` only clears on full recovery; otherwise a fresh breach check runs.
- **`risk_manager_live/engine.py`**: the guard loop now captures `result.escalate_to` (first non-None,
  matching the guards' own fixed order) and surfaces it on `LiveRiskDecision.escalate_to` — additive, zero
  change to any existing field or behavior.
- **`execution_orchestrator/types.py`**: `OrchestrationResult.circuit_state_after: TradingCircuitState |
  None = None` (additive, trailing, default `None`).
- **`execution_orchestrator/engine.py`**: `orchestrate()` gains two new optional parameters,
  `circuit_state`/`pnl_source`. When BOTH are supplied, the new unified check runs first (folding
  `emergency_stop` into `emergency_stop_requested` — it now persists instead of being single-call-only)
  and denies immediately with `TRADING_SUSPENDED` if not READY. When NEITHER is supplied, the exact
  original `emergency_stop` check runs unchanged — every existing caller is unaffected. `circuit_state_
  after` is threaded through every return path (all `_denied` call sites plus the success path) so a
  tracking caller always knows what to persist for its next call.

## Reuse investigated and applied

The frozen batch `RiskManager` class (`risk_manager/engine.py`) already implements essentially this exact
concept — `EngineLifecycleState`/`EngineState`, `configure()`/`resume()`/`emergency_stop()`/
`clear_emergency()`, and `_guard_breached()`'s hysteresis-gated recovery condition. Its own
`evaluate()`/`allow_trade()` were correctly NOT reused (Phase 2's own established reason: scoring-engine
-coupled, wrong integration point for a live proposal). Its **types and recovery-eligibility logic** were
reused deliberately (`EngineState` imported verbatim; `_guard_breached` imported directly, same pattern
already established elsewhere in this codebase for `recognition_engine_live` reusing
`recognition_engine.engine._bucket_value`) rather than reimplemented, so the new live circuit breaker's
recovery semantics can never silently drift from the already-reviewed batch-engine policy.

## Test discipline: fails before, passes after

Three separate proofs, each verified directly, not asserted:

1. **`circuit_breaker.py` itself**: `tests/test_circuit_breaker.py` written first — collection failed
   (`ModuleNotFoundError`, the module didn't exist) — then implemented — 8/8 pass, including the exact
   hysteresis scenario (suspended on a daily-loss breach, next call's daily P&L alone looks recovered but
   drawdown is still above the reset threshold — stays suspended; only fully recovers when ALL three
   conditions clear).
2. **`escalate_to` surfacing**: `tests/test_escalate_to.py` written first — ran red (`AssertionError:
   assert None is EngineState.SUSPENDED`, i.e. the actual pre-fix bug reproduced, not just an import
   error) — then `engine.py` fixed — 4/4 pass.
3. **Orchestrator-level integration** (the CEO's own scenario, restated precisely): a drawdown breach
   suspends the account; the next call's portfolio has recovered to 10% drawdown — below the 12% breach
   line, so a system with no memory would re-approve — but still above the 8% reset line, so it must stay
   blocked. `tests/test_circuit_breaker_integration.py` written, confirmed to PASS against the finished
   code, then verified to genuinely FAIL against the pre-fix code by temporarily stashing
   `execution_orchestrator/{engine,types,reason_codes}.py` via git, re-running (3/3 failed:
   `TypeError: orchestrate() got an unexpected keyword argument 'circuit_state'`,
   `AttributeError: 'OrchestrationResult' object has no attribute 'circuit_state_after'`), then restoring
   the fix via `git stash pop` (3/3 passed again). A third test in the same file pins that a caller
   supplying neither `circuit_state` nor `pnl_source` sees `circuit_state_after is None` and otherwise
   identical behavior.

## Validation

```
pytest ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution \
  ai_trader/order_manager ai_trader/execution_engine ai_trader/risk_manager ai_trader/portfolio_manager_live -q
-> 656 passed, 2 skipped (the two gated real-terminal tests, unaffected), 0 failed

mypy --strict ai_trader/risk_manager_live ai_trader/execution_orchestrator ai_trader/mt5_demo_execution ai_trader/order_manager
-> Success: no issues found in 57 source files
```

## Exact diff surface

```
 ai_trader/execution_orchestrator/engine.py       | 84 ++++++++++++++++++-----
 ai_trader/execution_orchestrator/reason_codes.py |  6 ++
 ai_trader/execution_orchestrator/types.py        |  7 +-
 ai_trader/risk_manager_live/__init__.py          |  8 +++
 ai_trader/risk_manager_live/engine.py            | 13 +++-
 ai_trader/risk_manager_live/reason_codes.py      |  6 ++
 ai_trader/risk_manager_live/types.py             | 47 +++++++++++++
 7 files changed, 152 insertions(+), 19 deletions(-)
```
Plus 4 new files (`risk_manager_live/circuit_breaker.py` and three test files). Nothing outside these two
packages was touched — matching the narrow scope Risk Audit #1 itself defined. No file listed in the
Decision Logic or Demo Readiness audits as unrelated was modified.

## What this does NOT do (disclosed, not silently deferred)

- No live signal source was built (Demo Readiness precondition #6, untouched).
- No real (`PortfolioStateSource`) or virtual/shadow implementation was built — only the interface both
  will satisfy. That is precondition #2 (P&L computation) and the shadow P&L work, both later steps in
  the CEO-approved order.
- `EMERGENCY_STOP` has no clear/resume operation yet — once entered (by explicit request), it is
  permanent until a future explicit mechanism is added. Disclosed, not silently assumed away; the same
  conservative default the frozen batch engine's own guarded `clear_emergency()` reflects.
- The two-argument `circuit_state`/`pnl_source` opt-in means existing callers (all 18 pre-existing
  `execution_orchestrator` tests, `mt5_demo_execution`'s gating) are structurally incapable of exercising
  the new persistence — this is intentional additive scope, not a gap.

**Stopping here per instruction.** Report and commit only; awaiting approval before the next step
(`#10, #11` — direction/stop validation and `PortfolioDailyState` ownership/reset, per the approved
order).
