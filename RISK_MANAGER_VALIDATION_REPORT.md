# Risk Manager v1 — Implementation & Validation Report (Phase 6.5)

**Date:** 2026-07-15. **Scope:** production implementation of the Risk Manager against the frozen
`ai_trader/risk_manager/*.md`/`*.json` specification, following the exact process and quality bar
established for Market Scanner v1 (Phase 6.1), Strategy Manager v1 (Phase 6.2), Signal Engine v1
(Phase 6.3), and Scoring Engine v1 (Phase 6.4): implement → test continuously → adversarial review →
fix every real issue → report honestly.
**Verdict: READY.** (see §6)

---

## 1. What was built

13 production modules under `ai_trader/risk_manager/` (`py.typed` + `requirements.txt` in addition),
implementing every stage the architecture names:

| architecture component | module |
|---|---|
| Value types (mirrors `RISK_SCHEMA.json` 1:1) + module-owned input types (`RiskContext`/`PortfolioState`/...) | `types.py` |
| Config / errors | `config.py`, `exceptions.py` |
| Schema loading + compiled validation | `schema_validation.py` |
| Pre-Trade Filters (stage 3) | `filters.py` |
| Portfolio Limits (stage 4) | `limits.py` |
| Loss & Drawdown Guards + Cooldowns (stages 5–6) | `guards.py` |
| Position Sizer (stage 7) | `sizing.py` |
| Constraint Builder (stage 8) | `constraints.py` |
| The fixed, per-opportunity gate chain (stages 0–8) | `pipeline.py` |
| Decision Assembler | `assembler.py` |
| Output Collector (schema + semantic validation) | `validator.py` |
| Public API facade + lifecycle/statistics/health | `engine.py` (`RiskManager`) |

**209 tests** across 14 test files (unit tests per module covering every filter/limit/guard/cooldown/
sizing branch, the fixed 9-stage pipeline order, decision assembly/validation, and every operational-
control/lifecycle transition), including `test_engine_integration.py` against real `OpportunityScore`
objects produced by the real Scoring Engine. `mypy --strict`: **0 errors** across all 32 source files
(13 production + its own `tests/` package). Coverage: **99%** (source only) — the only remaining
uncovered statements are in `pipeline.py` (2 lines, an unreachable branch of `_valid_stop_side` for a
`Direction` other than `LONG`/`SHORT`, matching `Direction.NONE`'s own documented non-actionable
semantics) and `schema_validation.py` (6 lines, file-missing/corrupt-JSON/compile-failure environment
paths) — the same class of defensive-only gap every prior module's own report left uncovered, for the
same reason. `engine.py` itself is **100%** covered.

## 2. Design decisions worth recording (not redesign — filling gaps the spec leaves to the implementer)

The Risk Manager has no upstream Portfolio Manager module or schema yet — `RISK_MANAGER_ARCHITECTURE.md`
names `PortfolioState`/`RiskContext` as required inputs without publishing their shape. Every such gap
is filled with an explicit, documented default and marked "IMPLEMENTATION CHOICE" in the source, matching
the precedent set by every prior module:

- **`RiskContext`/`SymbolRiskSnapshot`/`PortfolioState`/`OpenPosition`/`ClosedPosition`** are the
  module's own designed input types (`types.py`), built from what the architecture/policy docs name
  (ATR, spread, liquidity, event timing, weekend/gap flags, equity, open positions, recent closed
  positions, daily/weekly P&L) without a canonical schema to mirror. `PortfolioState.drawdown_pct` /
  `daily_pnl_pct` / `weekly_pnl_pct` / `portfolio_risk_pct` / `leverage` are always DERIVED computed
  properties (from equity/high-water-mark/open positions), never stored fields — eliminates an entire
  class of "stale stored derived value" bug by construction.
- **`correlation_groups: dict[str, str]`** (config.py) fills `RISK_POLICY.md` §2's "groups by mechanism
  class / instrument correlation" — the Risk Manager has no access to a strategy's contract (forbidden
  dependency, architecture §13), so grouping is an operator-configured `symbol -> group` mapping. A
  symbol absent from the mapping is its own singleton group — the conservative default when no grouping
  has been declared.
- **`per_strategy_cooldown_bars: dict[str, int]`** (config.py) fills `COOLDOWN_STRATEGY`'s "honor the
  strategy contract's `execution.cooldown`" the same way, for the same forbidden-dependency reason. A
  strategy absent from the mapping has no configured cooldown (0 bars) — "no unconfigured restriction,"
  not a silent assumption of safety.
- **`ConstraintDefaults`'s numeric placeholders** (`max_hold_bars`, `max_slippage_pct`, `valid_for_bars`)
  fill `RISK_MANAGER_ARCHITECTURE.md`'s naming of the Constraint Builder's outputs without fixing values
  for any of them — conservative, documented placeholders, matching `RISK_POLICY.md` §0's own framing
  for every other v1 default ("conservative placeholders for design review, not tuned values").
- **`QUALITY_FACTOR`'s MODERATE/PREMIUM bands** (config.py) — `POSITION_SIZING.md` §2 names the two
  endpoints only (POOR/WEAK→0.5, STRONG→1.0); MODERATE is the documented linear interpolation (0.75),
  PREMIUM stays capped at the same ceiling as STRONG (the spec gives no reason a strictly-higher band
  should exceed the [0.5, 1.0] range it itself fixes).
- **No wall-clock anywhere in this module.** `RISK_SCHEMA.json` has no informational timing field
  (unlike Signal Engine's `evaluation_time_ms`), so `timestamp` is always the opportunity's own `as_of`,
  and no module reached from `engine.py` imports `time`.

## 3. Independent adversarial review — 8 real issues found and fixed

Following the same technique that caught bugs in all four prior modules, a fresh-eyes review agent (no
memory of writing the code) read every frozen spec document in full, then all 13 source files, hunting
specifically for policy/formula deviations, fail-safe violations, determinism violations, and batch/
running-portfolio-view correctness. It found 8 issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW); all were
real and fixed with regression tests.

| # | issue | file | severity | fix |
|---|---|---|---|---|
| 1 | `pipeline.py`'s own module docstring claimed its logic was "exception-free by construction" — but a runtime-malformed `OpportunityScore` field (e.g. `total_score=None`, reachable via `dataclasses.replace` bypassing the type system) raises a `TypeError` out of a plain comparison, and nothing anywhere in the call chain caught it — one bad opportunity could crash the WHOLE `evaluate()` batch, not just deny that one opportunity | `pipeline.py`, `engine.py` | **CRITICAL** | Added a new `_evaluate_one()` helper in `engine.py` that wraps the pipeline call + portfolio update + decision finalization in `try/except Exception`, degrading to a classified `DENY(INTERNAL_ERROR)` (with its own re-validated, placeholder-based fallback if even that reassembly is schema-invalid) instead of ever propagating. `evaluate()`'s per-opportunity loop and `allow_trade()` both now route through it. Corrected `pipeline.py`'s docstring to accurately describe this boundary instead of falsely claiming its own exception-freedom. |
| 2 | `evaluate()`'s `PORTFOLIO_UNAVAILABLE` branch called `assembler.assemble_decision()` directly, bypassing `_finalize_decision`'s validation/reassembly entirely — a decision built from a schema-invalid opportunity (e.g. a malformed `strategy_id`) could be emitted unvalidated even though the identical opportunity going through the NORMAL path would have been caught and reassembled | `engine.py` | **CRITICAL** | The `PORTFOLIO_UNAVAILABLE` branch now routes every decision through `_finalize_decision`, exactly like the normal per-opportunity loop. |
| 3 | `POSITION_SIZING.md` §3's second sentence (trades in the same correlation group share a smaller, deterministic sub-budget of the aggregate exposure cap) was never implemented — `sizing.py` only clamped to the AGGREGATE portfolio exposure budget, so two heavily-correlated trades could each independently consume up to the full aggregate budget | `sizing.py` | **HIGH** | Added a group-level clamp: `group_budget_pct = max_exposure_pct / max_correlated` (an even, deterministic split across the max number of correlated positions `LIMIT_MAX_CORRELATED` ever allows open at once), then clamps `effective_risk_pct` to whatever of that group budget remains after summing the `risk_pct` of already-open positions sharing the same correlation group — mirroring `limits.py::check_max_correlated`'s own group-membership logic so both gates agree on what "the same group" means. |
| 4 | `allow_trade()`'s `portfolio_impact` for its own ALLOW decision reported the PRE-trade portfolio unchanged (`portfolio_after = portfolio if outcome.allowed else None`) instead of the position it just decided to allow — inconsistent with what `evaluate()` reports for the identical opportunity | `engine.py` | **MEDIUM** | `allow_trade()` now routes through the same `_evaluate_one()` helper as `evaluate()`, which applies `_apply_allow_to_portfolio()` before finalizing — its `portfolio_impact` now reflects its own effect. |
| 5 | `health()`'s `DEGRADED` status, once set by a stale/missing-portfolio `evaluate()` call, never cleared even after a LATER `evaluate()` call received a fresh, valid portfolio — only a full `configure()` reset it, contradicting `RISK_SEQUENCE.md` §8's "recovers to normal ... once PortfolioState is fresh again" | `engine.py` | **MEDIUM** | `evaluate()` now clears any previously recorded portfolio-availability degraded reason as soon as it receives a fresh, non-stale portfolio, recomputing `self._degraded` from what remains. |
| 6 | `limits.py`'s module docstring implied the fine-grained sizing-time clamp (`POSITION_SIZING.md` §3) applies to `LIMIT_MAX_EXPOSURE`/`LIMIT_MAX_LEVERAGE`/`LIMIT_MAX_OVERNIGHT` collectively — but the spec only actually defines that mechanism for exposure; leverage/overnight are coarse "is there room at all" checks only, with no sizing-time counterpart. Documentation-accuracy only; the spec itself never asks for leverage/overnight sizing-time clamps, so no functional gap exists | `limits.py` | **MEDIUM** | Reworded the docstring to state explicitly that only `LIMIT_MAX_EXPOSURE` has a matching fine-grained sizing clamp, and that leverage/overnight are never subsequently narrowed by sizing. |
| 7 | `assemble_invalid_decision()` hardcoded `engine_state=EngineState.READY` regardless of the actual global state at fallback time — a fallback `DENY` produced while the engine is SUSPENDED/EMERGENCY_STOP would misreport itself as READY, inconsistent with the batch-level `RiskDecisionBatch.engine_state` | `assembler.py`, `engine.py` | **LOW** | Added an `engine_state` parameter to `assemble_invalid_decision()` (default `READY` only for callers with no better information); `_finalize_decision()`'s two call sites now pass the actual current `engine_state` through. |
| 8 | `filters.py::run_pre_trade_filters()` always evaluated `DATA_DEGRADED` FIRST, but `RISK_POLICY.md` §5's own table lists Volatility, Spread, Liquidity, News, THEN Data-quality — since the pipeline stops at the first failure, this changed which single reason code surfaces when multiple filters fail simultaneously | `filters.py` | **LOW** | Reordered the fixed filter chain to match the policy table exactly: Volatility → Spread → Liquidity → News → Data-quality → Weekend → Gap. |

All 8 fixed issues got dedicated regression tests proving the fix (e.g.
`test_a_malformed_opportunity_field_never_crashes_the_batch`,
`test_portfolio_unavailable_decisions_are_schema_valid_even_for_a_malformed_opportunity`,
`test_correlated_positions_share_a_budget_smaller_than_aggregate`,
`test_allow_trade_portfolio_impact_reflects_its_own_effect`,
`test_health_recovers_after_a_fresh_portfolio_arrives`,
`test_fallback_decision_engine_state_matches_actual_global_state_when_suspended`,
`test_stale_data_and_bad_volatility_together_surface_volatility_first`). The review found **no** issues
with the fixed-fractional sizing formula itself, the quality-scaling band, the notional cap, the
loss/drawdown guard thresholds, the cooldown logic, the deterministic rank-ordered running-portfolio-
view processing, or the operational-control state machine (`suspend`/`resume`/`emergency_stop`/
`clear_emergency`'s guard conditions) — all matched the frozen specification exactly.

One additional test-design issue was found and fixed during the module's own initial test-writing pass
(before the formal adversarial review): tuning `signal_strength` alone (with no Strategy Manager
configured) cannot reliably produce a below-floor `total_score` through the real Scoring Engine, because
its `EVIDENCE_MISSING` fallback defaults `risk_penalty`/`regime_alignment` to a neutral 0.5 rather than
0 — a structural floor of the Scoring Engine's own formula under those inputs, not a Risk Manager
concern. Resolved with a dedicated fixture, `make_below_floor_opportunity()`, that forces the needed
fields directly via `dataclasses.replace` rather than relying on that cross-engine arithmetic
coincidence. A related "proportional scaling" property was also documented and tested: since sizing
expresses risk as a percentage of equity, scaling equity or `quality_factor` down alone can never trigger
`SIZE_BELOW_MIN` under the default config (numerator and denominator scale together) — the genuine
trigger is exposure/group-budget exhaustion or the notional-cap interaction.

## 4. Final numbers (after all fixes)

```
pytest ai_trader/risk_manager/tests/ -q
209 passed in 0.72s

mypy --strict ai_trader/risk_manager
Success: no issues found in 32 source files

coverage run --source=ai_trader/risk_manager -m pytest ai_trader/risk_manager/tests/ -q
coverage report --omit="*/tests/*"
TOTAL   926 stmts   8 miss   99%   (engine.py: 100%)

pytest ai_trader/ -q   (Market Scanner + Strategy Manager + Signal Engine + Scoring Engine + Risk Manager together)
967 passed in 4.28s
```

`mypy --strict` was also run across the entire `ai_trader/` tree; it reports pre-existing errors in
Strategy Manager's and Market Scanner's own TEST files (98 errors in 16 files, all `union-attr`/
`type-arg`/`no-untyped-def` in files this task did not touch) — unrelated to Risk Manager and out of
scope for this task, which is scoped exclusively to the Risk Manager module per the CEO's directive.
`ai_trader/risk_manager/` itself remains independently clean, as shown above.

## 5. Protected invariants — confirmed untouched

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; zero files modified.
- **Market Scanner**, **Strategy Manager**, **Signal Engine**, **Scoring Engine** implementations —
  zero files modified. The Risk Manager only *imports* already-published types (`OpportunityScore`/
  `Quality`/`Recommendation` from Scoring Engine, `Direction` from Signal Engine, `DataQualityLevel`
  from Market Scanner) — never touches their source, never calls a mutating method.
- **No broker code, no MT5, no live trading, no Execution Engine, no Simulation, no Learning Engine, no
  ML** — none exist anywhere in this diff, per the CEO directive's explicit exclusion list.
- **The Risk Manager never generates signals, never scores, never executes** (`RiskDecision` is a pure
  ALLOW/DENY + sizing/constraints recommendation, never a placed order); **never learns or adapts** (all
  thresholds are fixed `RiskConfig` constants, never trained); **never touches the Research Lab or a
  strategy's contract** — verified by the module's own scope (a pure `(opportunity, context, portfolio)
  → RiskDecision` function chain, no side effects beyond internal statistics bookkeeping) and confirmed
  by the adversarial review.
- **Determinism preserved**: opportunities within one `evaluate()` batch are always processed in
  ascending `rank` order regardless of input order; no module reached from `engine.py` imports `time`/
  `random`; identical inputs produce byte-identical `RiskDecisionBatch` output (`TestDeterminism` in
  both `test_pipeline.py` and `test_engine_unit.py`).

## 6. Verdict

**Risk Manager v1 is READY.**

- Implementation: every architecture component built, matching the frozen spec exactly (no redesign —
  every design decision in §2 fills a genuine spec gap, never contradicts documented behavior).
- Tests: 209/209 passing, covering every filter/limit/guard/cooldown/sizing branch, the fixed 9-stage
  pipeline order, decision assembly/validation, every operational-control transition, and a real-
  Scoring-Engine integration test.
- Types: `mypy --strict` clean across all 32 source files (13 production + test package).
- Coverage: 99% (engine.py 100%); remaining gaps are documented defensive/environment-only or
  structurally-unreachable-by-construction branches.
- Independent adversarial review: completed, found 8 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW),
  all fixed and regression-tested, no outstanding findings.
- Protected invariants: confirmed untouched. Full `ai_trader/` suite (967 tests) green with no
  regressions in Market Scanner, Strategy Manager, Signal Engine, or Scoring Engine.

Per the standing "stop between every phase" directive and the CEO's explicit instruction for this task:
**this verdict does not itself authorize starting Execution Engine, Simulation, Learning Engine, Broker
Adapter, or MT5 integration.** That requires an explicit new CEO go-ahead.
