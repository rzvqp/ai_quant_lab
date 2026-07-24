# Phase 4 — Portfolio Manager — Design

**CEO scope**: aggregated risk across existing positions, total/per-symbol/per-direction exposure,
aggregate risk, configurable limits, long/short conflicts, per-strategy/session/asset-class limits,
reserved capital, portfolio heat, daily state; returns a complete, auditable `PortfolioDecision`.
Position in the live pipeline (per the Phase 9 spec): **Risk Manager → Portfolio Manager → Order
Manager** — Portfolio Manager gates an already-Risk-Manager-APPROVED trade at the aggregate-book level
before Order Manager ever builds an order (CEO rule 8: no module may bypass Risk Manager OR Portfolio
Manager).

## 1. Investigation finding: `ai_trader/portfolio_architect/` is a different, non-overlapping concept

Confirmed by full read (`architect.py`, `types.py`, `PORTFOLIO_ARCHITECT_DESIGN.md`): it is a
pre-Risk-Manager opportunity RE-RANKER for the OLD, scoring-engine-coupled offline backtest pipeline
(`ai_trader/simulation/harness.py:737-745`), currently identity-PASSTHROUGH only, with zero
implementation of any Phase 4 concept and zero wiring to `risk_manager_live`. It is not extended here —
building on it would force this phase back onto `OpportunityScore`/the old `RiskDecision`, the same
scoring-engine coupling Phase 2 deliberately avoided. A genuinely new module is required, sitting above
`risk_manager_live/` the same way `risk_manager_live` itself sits above the frozen `risk_manager/`.

## 2. Reused vs. new

**Reused, unmodified**: `risk_manager.types.PortfolioState`/`OpenPosition` (the book), `risk_manager.
config.RiskConfig.correlation_group_for()` (avoids a second, duplicate correlation-group mapping),
`risk_manager_live.types.CalculationTraceStep` (same audit-trace shape as Phase 2, reused verbatim
rather than redefined).

**Genuinely new** (none of these concepts exist anywhere in the repo — confirmed by repo-wide search):
`PortfolioAuthorizationRequest` (the bridge type, built by a caller from an approved `TradeProposal` +
`LiveRiskDecision`, mirroring `order_manager.ApprovedTradeIntent`'s own pattern), `PortfolioDailyState`
(caller-owned, caller-persisted daily counters this pure module only evaluates — Portfolio Manager holds
no state itself, matching every prior module's "no state, no I/O" discipline), `ExposureSnapshot`,
`PortfolioDecision`, `PortfolioManagerConfig`.

## 3. Disclosed scope boundaries (no fabrication)

- **Per-session exposure of EXISTING open positions is not derivable**: `OpenPosition` (frozen,
  reused, never modified) has no session field. Session limits therefore apply only to the PENDING
  trade's own session against a caller-tracked cumulative counter (`PortfolioDailyState.
  session_heat_used_pct[session]`) — not a portfolio-wide per-session breakdown of the existing book.
  Disclosed, not silently approximated.
- **Asset class** has no existing taxonomy anywhere in the repo. `PortfolioManagerConfig.
  asset_class_map: dict[str, str]` is an operator-declared mapping (same pattern as `RiskConfig.
  correlation_groups`) — a symbol absent from the map is `"UNCLASSIFIED"`, never silently grouped.
- **Portfolio heat** has no existing precedent beyond `PortfolioState.portfolio_risk_pct` (sum of open
  positions' `risk_pct`) — the closest, and only, existing adjacent concept (confirmed by the Phase 4
  investigation). This module's own `portfolio_heat_pct` is that same sum, PLUS the pending trade's own
  risk, evaluated against a SEPARATE, distinctly-named, portfolio-level ceiling
  (`max_portfolio_heat_pct`) — not a fabricated alternative formula.
- **Long/short conflict** is evaluated per-symbol AND per-correlation-group (via the reused
  `RiskConfig.correlation_group_for`): any existing open position sharing a symbol or correlation group
  with the pending trade, whose `direction` opposes the pending trade's `direction`, is a conflict.
  Configurable (`allow_long_short_conflict`, default `False`).
- **Daily state** (trade count, daily/session heat used) is NOT computed or persisted by this module —
  it is a pure function of caller-supplied `PortfolioDailyState`, exactly mirroring every other module's
  "no wall-clock, no hidden state" discipline. A future Execution Orchestrator (Phase 9) owns tracking
  and resetting it.

## 4. Public entry point

```python
def evaluate_portfolio_authorization(
    request: PortfolioAuthorizationRequest, portfolio: PortfolioState, daily_state: PortfolioDailyState,
    risk_config: RiskConfig, config: PortfolioManagerConfig | None = None,
) -> PortfolioDecision: ...
```

Runs every check to completion (never short-circuits, matching Phase 2's own "never short-circuit"
discipline for a complete audit trail): total exposure + reserved capital, per-symbol exposure, per-
direction exposure, per-strategy exposure, per-session exposure (pending-trade-scoped), per-asset-class
exposure, long/short conflict, portfolio heat, daily trade count, daily heat. Fail-closed: any exception
in aggregation denies with `PORTFOLIO_STATE_UNAVAILABLE`, never raises.
