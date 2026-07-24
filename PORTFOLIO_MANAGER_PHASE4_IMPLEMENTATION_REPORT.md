# Phase 4 — Portfolio Manager — Implementation Report

**Scope executed**: exactly the CEO's own Phase 4 specification from the "Phases 2–10" sweeping
authorization (2026-07-24), building on `PORTFOLIO_MANAGER_PHASE4_DESIGN.md`. Phases 1–3 were not
repeated or modified.

---

## 1. Files created

New package `ai_trader/portfolio_manager_live/` -- 11 production/test files:

```
portfolio_manager_live/__init__.py           -- public exports
portfolio_manager_live/types.py              -- PortfolioAuthorizationRequest, PortfolioDailyState,
                                                 ExposureSnapshot, CalculationTraceStep, PortfolioDecision,
                                                 PortfolioManagerConfig
portfolio_manager_live/reason_codes.py       -- 11 new PORTFOLIO_* reason codes
portfolio_manager_live/aggregation.py        -- build_exposure_snapshot(), find_long_short_conflicts()
portfolio_manager_live/engine.py             -- evaluate_portfolio_authorization() public entry point
portfolio_manager_live/tests/__init__.py
portfolio_manager_live/tests/_fixtures.py
portfolio_manager_live/tests/test_types.py             -- 9 tests
portfolio_manager_live/tests/test_aggregation.py       -- 7 tests
portfolio_manager_live/tests/test_engine.py            -- 16 tests
portfolio_manager_live/tests/test_import_independence.py -- 5 tests
```

## 2. Critical investigation finding: `ai_trader/portfolio_architect/` is a different, non-overlapping concept

Before writing any code, the existing `ai_trader/portfolio_architect/` package (mentioned in this
session's task history) was fully read to check for reuse. Confirmed: it is a pre-Risk-Manager
`OpportunityScore` re-ranker for the OLD, scoring-engine-coupled offline backtest pipeline
(`ai_trader/simulation/harness.py:737-745`), currently identity-PASSTHROUGH only (`architect.py:45-49`),
explicitly forbidden by its own design doc from ever emitting an ALLOW/DENY verdict
(`PORTFOLIO_ARCHITECT_DESIGN.md:167-168`), and with zero wiring to `risk_manager_live`. It implements
none of the CEO's Phase 4 requirements. Building on it would have forced Phase 4 back onto
`OpportunityScore`, the same scoring-engine coupling Phase 2 deliberately avoided for the same reason.
Phase 4 is therefore a genuinely new module, sitting above `risk_manager_live/` the same way
`risk_manager_live` itself sits above the frozen `risk_manager/` -- not an extension of
`portfolio_architect/`. `portfolio_architect/` was not touched.

## 3. What already existed vs. what's genuinely new

A repo-wide search (before writing code) confirmed **zero existing definitions anywhere** for: portfolio
heat, reserved capital, asset class, per-strategy/session portfolio limits, or long/short conflict
detection against live positions. `risk_manager.limits.run_portfolio_limits` (already reused unmodified
inside Phase 2) covers only: position count, per-symbol position count, a static correlation-group cap,
aggregate exposure, leverage, and overnight exposure -- none of the direction-aware, strategy/session/
asset-class-scoped, capital-reservation, or heat concepts Phase 4 needs. The only reusable precedent
found was `PortfolioState.portfolio_risk_pct` (sum of open positions' `risk_pct`) as the closest existing
analog to "portfolio heat," and `RiskConfig.correlation_group_for()` as the existing, reusable
correlation-grouping mechanism (reused unmodified rather than duplicated).

## 4. Reused vs. new (mirrors the design doc's own account)

| CEO requirement | Source |
|---|---|
| aggregated risk / existing positions | REUSED (`risk_manager.types.PortfolioState.open_positions`) |
| total exposure | NEW aggregation, using REUSED `PortfolioState.portfolio_risk_pct` as the base |
| per-symbol / per-direction / per-strategy exposure | NEW (`aggregation.build_exposure_snapshot`) |
| configurable limits | NEW (`PortfolioManagerConfig`) |
| long/short conflicts | NEW (`aggregation.find_long_short_conflicts`), using REUSED `RiskConfig.correlation_group_for` |
| per-session / per-asset-class limits | NEW (asset class has no repo-wide precedent; session is pending-trade-scoped, disclosed in §3 of the design doc) |
| reserved capital | NEW |
| portfolio heat | NEW metric name, same formula as total exposure (disclosed, not fabricated) |
| daily state | NEW, caller-owned/caller-persisted (`PortfolioDailyState`) -- this module holds no state itself |
| `PortfolioDecision` | NEW (no prior type of this shape existed; `risk_manager.types.PortfolioImpact` is a much narrower, single-decision audit fragment, not reusable as-is) |

## 5. Public contract

```python
def evaluate_portfolio_authorization(
    request: PortfolioAuthorizationRequest, portfolio: PortfolioState, daily_state: PortfolioDailyState,
    risk_config: RiskConfig, config: PortfolioManagerConfig | None = None,
) -> PortfolioDecision: ...
```

Runs 10 checks to completion every time -- total exposure, reserved capital, direction exposure,
strategy exposure, session exposure, asset-class exposure, long/short conflict, portfolio heat, daily
trade count, daily heat -- never short-circuited, for a complete audit trail (`test_multiple_breaches_
all_collected_never_short_circuited`, `test_denied_decision_carries_full_trace_and_snapshot`). Fail-
closed: any aggregation exception (verified with a deliberately malformed `PortfolioState`) denies with
`PORTFOLIO_STATE_UNAVAILABLE`, never raises.

## 6. Test results

```
pytest ai_trader/portfolio_manager_live -q
-> 37 passed

pytest ai_trader/risk_manager ai_trader/risk_manager_live ai_trader/execution_engine ai_trader/order_manager ai_trader/portfolio_manager_live -q
-> 581 passed, 1 skipped   (the 1 skip is Phase 1's own gated real-MT5-terminal integration test)
```

## 7. mypy strict

```
mypy --strict ai_trader/portfolio_manager_live
-> Success: no issues found in 11 source files
```

Clean on the first pass -- no fixes needed to frozen modules this phase.

## 8. Static safety proof (CEO rules 8, 9, 12)

- `test_no_metatrader5_import_anywhere` -- passes.
- `test_no_forbidden_imports_in_any_production_module` -- passes; explicitly forbids `execution_engine`
  and `order_manager` (Portfolio Manager sits ABOVE both in the pipeline and must never depend on
  anything downstream of it, or it could be bypassed).
- `test_only_depends_on_allowed_ai_trader_packages` -- passes; allow-list is `portfolio_manager_live`,
  `risk_manager`, `signal_engine` only.
- `test_no_order_submission_vocabulary` -- passes; this is an authorization layer, never an execution one.

## 9. Known limitations / disclosed scope boundaries

- Per-session exposure of the EXISTING open book is not derivable (`OpenPosition` has no session field,
  and was not modified to add one) -- the session check is scoped to the pending trade's own cumulative
  session heat, tracked by the caller in `PortfolioDailyState.session_heat_used_pct`.
- `portfolio_heat_pct` is literally the same value as `total_exposure_pct`, evaluated against a
  separately-named, separately-configurable ceiling -- disclosed as reusing the one existing adjacent
  concept (`portfolio_risk_pct`) rather than inventing a new, unproven correlation-weighted formula.
- `asset_class_map`/`session` have no automatic detector -- both are operator/caller-declared inputs,
  matching the existing `RiskConfig.correlation_groups` precedent for "no fabricated inference."

## 10. Repository state at close of Phase 4

- Working tree: `PORTFOLIO_MANAGER_PHASE4_DESIGN.md`, this report, and `ai_trader/portfolio_manager_live/`
  are new; everything else byte-identical to the post-Phase-3 commit. Committed separately as the Phase
  4 commit.
- All previously-approved packages (`risk_manager`, `risk_manager_live`, `execution_engine`,
  `order_manager`): zero diff.

**Stop conditions from the sweeping authorization were not triggered.** Proceeding to Phase 5 (Telegram
Notification Service) next, per the standing authorization covering phases 2–10.
