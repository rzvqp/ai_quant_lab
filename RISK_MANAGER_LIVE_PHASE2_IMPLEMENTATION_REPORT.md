# Phase 2 — Risk Manager (Live) — Implementation Report

**Scope executed**: exactly the CEO's own Phase 2 specification from the "Phases 2–10" sweeping
authorization (2026-07-24), building on `RISK_MANAGER_LIVE_PHASE2_DESIGN.md`. Independent of MT5 — no
broker connectivity, no order submission, no state, no I/O. **Phase 1 (MT5 Broker Adapter Read-Only,
Layers A+B) was not touched, per the CEO's explicit instruction not to repeat or modify already-approved
components.**

---

## 1. Files created

New package `ai_trader/risk_manager_live/` — 11 production/test files, zero existing file modified
outside this new package and this report/design pair:

```
risk_manager_live/__init__.py           -- public exports
risk_manager_live/types.py              -- TradeProposal, AccountState, InstrumentSpecification,
                                            CalculationTraceStep, LiveRiskDecision
risk_manager_live/reason_codes.py       -- PROPOSAL_DATA_INCOMPLETE, RISK_NOT_CALCULABLE,
                                            VOLUME_STEP_ROUNDING_BELOW_MIN, INSUFFICIENT_FREE_MARGIN
risk_manager_live/engine.py             -- evaluate_trade_proposal() public entry point
risk_manager_live/tests/__init__.py
risk_manager_live/tests/_fixtures.py            -- make_proposal/make_account/make_portfolio/
                                                    make_instrument/make_snapshot/make_risk_context/
                                                    make_config
risk_manager_live/tests/test_types.py           -- 8 tests (type validation, invariants)
risk_manager_live/tests/test_fail_closed.py     -- 8 tests (fail-closed edge cases)
risk_manager_live/tests/test_reused_controls.py -- 9 tests (proof every frozen control fires)
risk_manager_live/tests/test_sizing_volume_margin.py -- 7 tests (ALLOW path, volume/margin logic)
risk_manager_live/tests/test_import_independence.py  -- 5 tests (static import-boundary proof)
```

**Confirmed unchanged** (`git diff --stat -- ai_trader/risk_manager/ ai_trader/execution_engine/`, empty):
the entire frozen `ai_trader/risk_manager/` package and the entire, already-approved
`ai_trader/execution_engine/` package (including the Phase 1 Broker Adapter). Repository status
(`git status --short`) shows only two new, untracked paths: this report's sibling design doc and the new
package itself.

## 2. Architectural decision (from the design doc, now proven in code)

`evaluate_trade_proposal()` does **not** route through `RiskManager.evaluate()` / `allow_trade()` — those
are scoring-engine-coupled and the wrong integration point for a live proposal that was never scored.
Instead it calls the frozen `risk_manager` package's own lower-level, composable functions directly and
unmodified:

- `guards.run_loss_drawdown_guards`, `guards.run_cooldowns`
- `limits.run_portfolio_limits`
- `filters.run_pre_trade_filters`
- `sizing.compute_sizing` — the one function requiring an `OpportunityScore`, satisfied via a disclosed,
  non-fabricated adapter (`_build_sizing_adapter`) that only populates the 3 fields `compute_sizing`
  actually reads (`trade_context`, `symbol`, `quality`); every other field is an explicitly-commented,
  inert placeholder (`total_score=0`, `confidence=ScoreConfidence.NONE`, `recommendation=Recommendation.WATCH`,
  etc.) — never presented as real scoring output.

Two genuinely new checks were added additively, since neither has any equivalent in the frozen
`risk_manager` package (only ever existed inside `simulation.portfolio_simulator.SimAccount`,
backtest-internal):

- **Volume-step rounding**: converts `compute_sizing`'s risk-based `size_units` into broker lots via
  `InstrumentSpecification.contract_size`, rounds **down** to `lot_step` (never up — never grants more
  size than was risk-approved), clamps to `[min_volume, max_volume]`, denies `VOLUME_STEP_ROUNDING_BELOW_MIN`
  if the rounded volume falls below `min_volume`.
- **Free-margin sufficiency**: `margin_estimate = (volume_lots * contract_size * entry) / account.leverage`;
  denies `INSUFFICIENT_FREE_MARGIN` if it exceeds `account.margin_free`.

All four stages (loss/drawdown guards, cooldowns, portfolio limits, pre-trade filters) run to completion
every time — never short-circuited — so `LiveRiskDecision.calculation_trace` always carries the full,
auditable record, matching CEO rule 12 (every decision carries reason codes and a complete trace).

## 3. Public contract

```python
def evaluate_trade_proposal(
    proposal: TradeProposal, account: AccountState, portfolio: PortfolioState,
    instrument: InstrumentSpecification, risk_context: RiskContext, config: RiskConfig | None = None,
) -> LiveRiskDecision: ...
```

`LiveRiskDecision` fields: `approved`, `reason_codes`, `requested_risk`, `approved_risk`,
`calculated_volume`, `monetary_risk`, `stop_distance`, `margin_estimate`, `warnings`,
`calculation_trace` — exactly the CEO-specified field list. `__post_init__` enforces the invariant that an
approved decision always carries a non-empty trace and a denied decision always carries at least one
reason code; denied decisions never carry volume/monetary_risk/margin_estimate (proven in
`test_fail_closed.py`).

`PortfolioState` and `RiskContext` are reused verbatim from the frozen `risk_manager.types` module — no
duplicate portfolio/context type was created.

## 4. Test results

```
pytest ai_trader/risk_manager_live -q          -> 37 passed
pytest ai_trader/risk_manager ai_trader/risk_manager_live -q  -> 246 passed  (209 frozen + 37 new)
```

Coverage by file: `test_types.py` (8), `test_fail_closed.py` (8), `test_reused_controls.py` (9, one per
CEO-required control: daily loss, drawdown, max positions, max per symbol, max leverage, consecutive-loss
cooldown, spread filter, plus the frozen sizing module's own `SIZE_BELOW_MIN` guard reached via
`dataclasses.replace()` on the frozen `SizingLimits`/`RiskConfig`), `test_sizing_volume_margin.py` (7: full
ALLOW path field population, lot-step rounding, volume-below-min-after-rounding DENY, volume clamped to
max, insufficient-free-margin DENY, margin_estimate reflects leverage, determinism), 
`test_import_independence.py` (5: no MT5 terminal API import anywhere in this package, no forbidden
package imports, dependency allow-list, no "harness" reference, no order-submission vocabulary).

## 5. mypy strict

```
mypy --strict ai_trader/risk_manager_live
-> Success: no issues found in 11 source files
```

One real issue was caught and fixed during this pass (not a false positive): three `for name, result in
...` loops over `guards`/`limits`/`filters` result lists reused the same loop-variable name across
functions returning `GuardResult`/`LimitResult`/`FilterResult` respectively — mypy strict correctly flagged
the narrowed-type reassignment as unsound. Fixed by giving each loop its own distinctly-named variable
(`limit_name`/`limit_result`, `filter_name`/`filter_result`); no behavior change.

## 6. Static safety proof (CEO rules 8, 9, 12)

- `test_no_metatrader5_import_anywhere` — passes; this package never imports the MT5 terminal API (only
  `ai_trader/execution_engine/adapters/mt5_gateway.py` may, per Phase 1).
- `test_no_forbidden_imports_in_any_production_module` / `test_only_depends_on_allowed_ai_trader_packages`
  — passes; this package only imports from `risk_manager`, `scoring_engine`, `signal_engine`,
  `market_scanner` — never `execution_engine`, `simulation`, or any downstream module, so it cannot itself
  be bypassed by or bypass anything downstream.
- `test_no_order_submission_vocabulary` — passes; no `submit_order`/`order_send`/`order_check`/
  `cancel_order`/`close_position` token appears anywhere in this package (this is a risk-authorization
  layer, not an execution layer — Order Manager, Phase 3, and Broker Adapter, Phase 1/10, own that).

**Known, non-blocking pattern encountered twice more this phase** (same class of false positive already
seen in Phase 1): docstrings explaining "this package does not import the MT5 terminal API" originally
used the literal substring `MetaTrader5`, which the blunt substring-check static test correctly flagged.
Fixed in both `__init__.py`, `engine.py`, and `types.py` by rewording to "MT5 terminal API" — no production
logic changed.

## 7. Known limitations / disclosed scope boundaries

- `AccountState.is_demo` is carried through for future-phase auditing only; **Phase 2 itself does not gate
  on it** — DEMO-only enforcement is Phase 10's / Broker Adapter's responsibility (already implemented
  there for read operations; order-submission-time enforcement is a Phase 10 item).
- The sizing adapter's placeholder `OpportunityScore` fields (`total_score`, `component_scores`,
  `confidence`, `recommendation`, `rank`, `reason_codes`) are inert and explicitly commented as such in
  `engine.py` — a future Confidence Engine (Phase 8) integration must not read them as if they were real
  scores.
- No margin-call / stop-out simulation exists in this phase (only a static pre-trade margin-sufficiency
  check) — matches the CEO's own Phase 2 field list (`margin_estimate`), nothing beyond it was invented.

## 8. Repository state at close of Phase 2

- Working tree: only `RISK_MANAGER_LIVE_PHASE2_DESIGN.md`, this report, and `ai_trader/risk_manager_live/`
  are new/untracked; everything else byte-identical to the post-Phase-1 commit.
  Committed separately as the Phase 2 commit (design + implementation + tests + this report).
- Frozen `ai_trader/risk_manager/` package: zero diff.
- Phase 1 `ai_trader/execution_engine/` package: zero diff.

**Stop conditions from the sweeping authorization were not triggered**: no architecture change was
required beyond what the design doc already proposed, and no safety guard failed to be demonstrated.
Proceeding to Phase 3 (Order Manager Dry-Run) next, per the standing authorization covering phases 2–10.
