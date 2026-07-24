# Phase 2 — Risk Manager (Live) — Design

**Status**: design-then-implement, per the CEO's own standing authorization for Phases 2-10 (no
per-phase approval gate this time — "Nu cere aprobarea mea după fiecare fază"). Written before
implementation, per the CEO's own "cerințe pentru fiecare fază" checklist.

## 1. What already exists — investigated first, per the CEO's own explicit rule

`ai_trader/risk_manager/` is a mature, frozen, 209-test package already covering almost everything Phase
2 asks for: `PortfolioState`/`OpenPosition`/`ClosedPosition` (exact match for the requested input),
`RiskConfig` (per-trade risk, daily/weekly loss, drawdown, position/exposure/leverage/correlation limits,
cooldowns, spread/volatility/liquidity/news/gap filters — all already implemented and tested),
`guards.py`/`limits.py`/`filters.py` (composable functions taking only `symbol`/`strategy_id`/
`PortfolioState`/`RiskContext`/`config` — genuinely reusable, NOT coupled to the scoring pipeline),
`sizing.py::compute_sizing` (fixed-fractional sizing, quality-scaled, exposure/correlation-clamped).

**What's genuinely missing, verified by reading every relevant signature, not assumed**:
- No `TradeProposal`/`AccountState`/`InstrumentSpecification` type exists anywhere in the repo.
- `RiskManager.evaluate()`/`allow_trade()` (the engine's own convenience entry points) take
  `OpportunityScore` — a scoring-pipeline-specific type (`total_score`, `component_scores`, `confidence`,
  `quality`, `recommendation`, `rank`) that a live `TradeProposal` (not yet scored by anything, Confidence
  Engine is Phase 8) cannot honestly construct without fabricating scoring internals.
- `compute_sizing` reads only `opportunity.trade_context` (entry/stop), `opportunity.symbol`, and
  `opportunity.quality` from the `OpportunityScore` it's given — confirmed by reading `sizing.py` in full.
- No volume-step (lot) rounding exists anywhere in `risk_manager` (only `execution_engine.types.
  BrokerCapabilities.lot_step` exists, unused by sizing).
- No free-margin concept exists in `risk_manager` at all (margin only lives in `simulation.
  portfolio_simulator.SimAccount`, backtest-internal, never exposed as a reusable live type).

## 2. Architectural decision

**Do not modify `ai_trader/risk_manager/` at all** (frozen, per the CEO's own rule 6). **Do not route
through `RiskManager.evaluate()`/`allow_trade()`** (scoring-coupled, wrong integration point). Instead:

**New, top-level package `ai_trader/risk_manager_live/`** — a live-oriented orchestration layer that:
1. Defines the 3 genuinely-missing types (`TradeProposal`, `AccountState`, `InstrumentSpecification`).
2. Calls the EXISTING, frozen, composable functions directly and unmodified:
   `guards.run_loss_drawdown_guards`, `guards.run_cooldowns`, `limits.run_portfolio_limits`,
   `filters.run_pre_trade_filters` — all take only `symbol`/`strategy_id`/`PortfolioState`/
   `RiskContext`/`RiskConfig`, satisfied directly and honestly by a live `TradeProposal`'s own fields.
3. For `compute_sizing`, constructs a genuine (not fabricated) `OpportunityScore`-shaped adapter object
   from the proposal's own real `symbol`/`direction`/`entry`/`stop`/`target`, with the scoring-only fields
   the sizing math doesn't use (`total_score`, `component_scores`, `confidence`, `recommendation`, `rank`)
   set to explicit, disclosed placeholders (documented in code, never silently invented) — and
   `quality` set from `TradeProposal.confidence_quality` (reusing `scoring_engine.types.Quality`
   unmodified) when supplied by a future Confidence Engine (Phase 8), or `Quality.MODERATE` (the
   existing config's own already-defined 0.5 neutral fallback, `RiskConfig.quality_factor_for`'s own
   `.get(quality, 0.5)` default) when not — never assumed favorable.
4. Adds exactly the two genuinely-missing checks as NEW, additive logic (never touching frozen files):
   **volume-step rounding/clamping** (units → lots via `InstrumentSpecification.contract_size`, rounded
   down to `lot_step`, clamped to `[min_volume, max_volume]`) and **free-margin sufficiency**
   (`margin_estimate <= account.margin_free`) — both run AFTER sizing succeeds, since both need a
   computed volume/notional to evaluate.
5. Also requires `RiskContext` (reused, unchanged) as a 5th input beyond the CEO's own named 4 — the
   existing spread/volatility/liquidity/gap/news filters need it and reinventing that data shape would
   be exactly the "needless duplication" the CEO's own rules forbid. Disclosed explicitly here, not
   silently added.
6. Fail-closed throughout (CEO rule 11): any missing/invalid input (no snapshot for the symbol, `equity
   <= 0`, invalid `tick_size`/`lot_step`, no `RiskContext` entry) produces an explicit DENY with a
   disclosed reason code — never an exception, never a default-approve.

## 3. New types (`risk_manager_live/types.py`)

```
TradeProposal: proposal_id, correlation_id, strategy_id, symbol, direction: Direction, entry, stop,
  target, as_of, confidence_quality: Quality | None = None  (reuses scoring_engine.types.Quality)

AccountState: as_of, currency, balance, equity, margin_used, margin_free, margin_level, leverage,
  is_demo: bool  (carried through for audit only -- Phase 2 itself never checks this; MT5-specific DEMO
  enforcement is the Broker Adapter's own job, Phase1, already done)

InstrumentSpecification: symbol, tick_size, lot_step, min_volume, max_volume, contract_size, point_value,
  margin_currency

CalculationTraceStep: stage, passed, detail=None, observed=None, limit=None  (one entry per gate run, in
  order -- guards, cooldowns, limits, filters, sizing, volume-step, margin)

LiveRiskDecision: approved, reason_codes: tuple[str,...], requested_risk, approved_risk,
  calculated_volume (lots, post-rounding), monetary_risk, stop_distance, margin_estimate,
  warnings: tuple[str,...], calculation_trace: tuple[CalculationTraceStep,...]
```

`LiveRiskDecision` is a deliberately NEW name, not a reuse of `risk_manager.types.RiskDecision` (which
has a different, incompatible field set) — avoids a same-name-different-shape collision; both are
importable side by side without ambiguity.

## 4. New reason codes (additive, never colliding with the existing vocabulary)

`VOLUME_STEP_ROUNDING_BELOW_MIN` (post-rounding volume fell below `min_volume`),
`INSUFFICIENT_FREE_MARGIN` (estimated margin exceeds `account.margin_free`), `PROPOSAL_DATA_INCOMPLETE`
(missing/invalid `TradeProposal`/`AccountState`/`InstrumentSpecification` field), `RISK_NOT_CALCULABLE`
(equity/point_value/tick_size/lot_step non-positive — risk arithmetic itself cannot run). Every EXISTING
reason code (`LOSS_DAILY`, `LIMIT_MAX_POSITIONS`, `FILTER_SPREAD`, `INVALID_STOP`, `SIZE_BELOW_MIN`, etc.)
is reused verbatim when the underlying, unmodified guard/limit/filter/sizing function returns it.

## 5. Public entry point

```
evaluate_trade_proposal(
    proposal: TradeProposal, account: AccountState, portfolio: PortfolioState,
    instrument: InstrumentSpecification, risk_context: RiskContext, config: RiskConfig | None = None,
) -> LiveRiskDecision
```

Pure function, no state, no I/O, no MT5 import (CEO rule 9 — verified by a static import-independence
test, matching the Broker Adapter package's own established precedent).

## 6. Testing plan

Unit tests per check (fail-closed on missing data, each existing guard/limit/filter reused correctly,
new volume-step/margin logic, `calculation_trace` completeness, reason-code correctness), plus
integration-style tests exercising full ALLOW and full DENY paths, plus a negative-data-completeness
suite (every required field missing, one at a time) and an import-independence test (no MT5, no
`execution_engine`, no `learning_feedback`, etc.).
