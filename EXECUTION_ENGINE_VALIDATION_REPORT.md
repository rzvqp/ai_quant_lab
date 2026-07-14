# Execution Engine v1 — Implementation & Validation Report (Phase 6.6)

**Date:** 2026-07-15. **Scope:** production implementation of the Execution Engine against the frozen
`ai_trader/execution_engine/*.md`/`ORDER_SCHEMA.json` specification, following the exact process and
quality bar established for Market Scanner v1 (Phase 6.1), Strategy Manager v1 (Phase 6.2), Signal
Engine v1 (Phase 6.3), Scoring Engine v1 (Phase 6.4), and Risk Manager v1 (Phase 6.5): implement → test
continuously → adversarial review → fix every real issue → report honestly.
**Verdict: READY.** (see §6)

---

## 1. What was built

14 production modules under `ai_trader/execution_engine/` (13 source `.py` files + `__init__.py`,
`py.typed`, `requirements.txt`), implementing every stage the architecture names:

| architecture component | module |
|---|---|
| Value types (mirrors `ORDER_SCHEMA.json` 1:1) + the abstract Broker Adapter contract's own shapes | `types.py` |
| Config / errors | `config.py`, `exceptions.py` |
| Schema loading + compiled validation | `schema_validation.py` |
| The abstract Broker Adapter `Protocol` | `broker_adapter.py` |
| Order Builder (decision/position → `OrderRequest`) | `builder.py` |
| Order Validator (mechanics + schema) | `validator.py` |
| Order Ledger (own record of live/terminal orders) | `ledger.py` |
| Lifecycle Tracker (broker events → order state) | `lifecycle.py` |
| Reconciler (query-before-any-resend, exception-safe boundary) | `reconciler.py` |
| The fixed per-decision pipeline (Intake → Build → Duplicate guard → Validate → Submit → Track) | `pipeline.py` |
| Result/Reporter | `reporter.py` |
| Public API facade + engine lifecycle/statistics/health | `engine.py` (`ExecutionEngine`) |

**198 tests** across 14 test files (unit tests per module covering every order-mechanics check, both
state machines, every documented failure mode, plus `test_engine_integration.py` against a REAL
`RiskDecision` produced by a real Scoring Engine + Risk Manager chain). `mypy --strict`: **0 errors**
across all 31 source files (14 production + its own `tests/` package). Coverage: **99%** (source only)
— the only remaining uncovered statements are `schema_validation.py`'s file-missing/corrupt-JSON/
compile-failure environment paths (6 lines, the same class of gap every prior module's own report left
uncovered), `lifecycle.py` line 92 (one specific transition-table branch), `validator.py` two lines
(defensive fallbacks), and `engine.py` lines 304-310 (the outermost safety net inside
`emergency_flatten`'s per-position loop for a `submit_built_order` failure that itself has no partial
Ledger record to report against — a doubly-defensive branch).

## 2. Design decisions worth recording (not redesign — filling gaps the spec leaves to the implementer)

`EXECUTION_ENGINE_ARCHITECTURE.md`/`ORDER_LIFECYCLE.md` name several mechanisms in prose without fixing
every numeric/policy/contract detail. Every such gap is filled with an explicit, documented default and
marked "IMPLEMENTATION CHOICE" in the source, per the established discipline:

- **Portfolio Manager gap** (flagged in `EXECUTION_ENGINE_HANDOFF.md` §2b before implementation began):
  no Portfolio Manager module exists. Resolved by reusing `ai_trader.risk_manager.types.PortfolioState`
  directly — Risk Manager is an allowed direct dependency per the interaction matrix, and its
  `PortfolioState` already has the exact shape (equity, open positions, computed exposure/leverage) a
  "read PortfolioState" consumer needs. `types.py`'s module docstring documents this as IMPLEMENTATION
  CHOICE #1.
- **Broker Adapter contract shape** (`broker_adapter.py`): the architecture describes submit/cancel/
  query/capabilities in prose without publishing an interface. Designed as a pull-based `Protocol`
  (`submit_order`, `cancel_order`, `query_status`, `query_open_orders`, `capabilities`) matching
  `EXECUTION_SEQUENCE.md`'s own `BA.query_status`/`BA.query_open_orders` calls exactly — nothing here
  pushes events into the engine, the Reconciler always pulls. A deterministic test double
  (`tests/fixtures/fake_broker.py`) implements it for the test suite; no real venue integration exists
  anywhere in this diff.
- **Order-type mapping policy** (`ORDER_LIFECYCLE.md` §6, implemented in `builder.py`): "entry ≈ current
  market → Market" cannot be evaluated in v1 — there is no live quote feed input (Market Scanner access
  is explicitly forbidden). The deterministic default is a marketable LIMIT at the decision's own entry
  price (never worse than approved entry) when an entry is given, falling back to MARKET only when the
  decision carries no entry at all. Since Risk Manager's own validator guarantees every ALLOW decision
  carries a `stop`, an opening order is BRACKET whenever `stop`/`target` is present (nearly always) —
  simplifying the mapping considerably and matching "attached as a Bracket ... so the position is
  protected on fill" from the same policy sentence.
- **Rounding/quantity-limit policy** (`config.py`): tick/lot rounding is round-half-up (arbitrary but
  deterministic, consistent with the Scoring Engine's own half-up choice elsewhere in this codebase);
  `max_qty` is clamped DOWN (never up — satisfies the hard boundary "never resize beyond the approved
  RiskDecision"), only rejecting if the clamp would then fall below `min_qty` (mirrors Risk Manager's own
  notional-cap-then-below-min precedent).
- **`emergency_flatten`'s synthesized closing orders** have no source `RiskDecision` (a flatten is a
  direct command, not a per-opportunity risk decision) — `builder.build_flatten_order()` is a
  deliberately separate, narrower builder: always MARKET + reduce_only + CLOSE, idempotent per
  `(strategy_id, symbol, as_of)`, using a documented placeholder `flatten_max_slippage` config default
  since there is no `RiskDecision.constraints.max_slippage` to read.
- **Fill price fallback** (`lifecycle.py`): a broker reporting new filled quantity without an
  `avg_price` (a malformed/incomplete report) falls back to the order's own `limit_price` rather than a
  fabricated `0.0` — a `0.0` "free trade" would be a worse lie than a reasonable reference price; `0.0`
  is used only when neither is available.
- **No wall-clock anywhere in this module.** `timestamp` is always the decision's own `as_of` (never
  read from a system clock), the identical precedent every downstream engine before this one has
  followed.

## 3. Independent adversarial review — 7 real issues found and fixed

Following the same technique that caught bugs in all five prior modules, a fresh-eyes review agent (no
memory of writing the code) read all 8 frozen spec documents plus `EXECUTION_ENGINE_HANDOFF.md` in full,
then all 13 source files and the test suite, hunting specifically for fail-safe violations, idempotency
violations, determinism violations, **sibling-entry-point inconsistency** (the newest lesson, explicitly
carried forward from the Risk Manager's own review — this module has five entry points that can each
touch the Ledger or the broker: `execute`, `cancel`, `reconcile`, `emergency_flatten`, `status`), and
state-machine correctness. It found 7 issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW); all were real and
fixed with regression tests.

| # | issue | file | severity | fix |
|---|---|---|---|---|
| 1 | The pipeline validated an order BEFORE checking the duplicate guard. A retry of an ALREADY-TERMINAL (e.g. FILLED) order, evaluated against a `PortfolioState` that had since changed (e.g. now shows the position that same order just created), could fail `POSITION_LIMIT_CONSISTENCY` and have its Ledger record OVERWRITTEN with a bogus REJECTED — corrupting the record of an order that had genuinely filled, unrecoverably (the Reconciler treats a terminal record as already resolved) | `pipeline.py` | **CRITICAL** | The duplicate guard now runs FIRST, before `validate_order` is even called — an already-known `client_order_id` returns the existing record untouched, with no re-validation against a possibly-different portfolio. |
| 2 | `reconciler.py`'s `reconcile_one`/`reconcile_all_open`/`rebuild_from_broker`, and `engine.py`'s `cancel()` (which called `adapter.cancel_order` directly) had NO exception handling around Broker Adapter calls — unlike `pipeline._validate_and_submit`, which explicitly wraps the equivalent calls. A single flaky broker call during `reconcile_all_open` aborted reconciling every OTHER open order; a broker exception during `shutdown()`'s `DRAINING` reconciliation propagated out of `shutdown()` entirely, violating `EXECUTION_API.md` §1's explicit contract ("expected failures return terminal OrderStatus/typed results, never thrown across the boundary") | `reconciler.py`, `engine.py` | **CRITICAL** | Every Broker Adapter call in `reconciler.py` is now wrapped (`_safe_query_status`, `_safe_query_open_orders`, `_safe_cancel`) — an exception degrades to "treat as unresolved/not-found", never propagates. Added `reconciler.request_cancel()` as the one exception-safe boundary `engine.cancel()` now uses instead of calling the adapter directly. |
| 3 | `emergency_flatten()` silently no-ops (empty report, no degraded signal) when called before any `execute()` call has ever populated `_last_portfolio` — unlike `execute()`'s explicit, disclosed handling of the identical underlying condition (`PORTFOLIO_UNAVAILABLE`). For a method that exists specifically as an emergency safety mechanism, silently doing nothing while reporting "success" is dangerous | `engine.py` | **HIGH** | `emergency_flatten()` now marks the engine DEGRADED with an explicit reason when no `PortfolioState` has ever been observed, matching `execute()`'s own disclosure discipline. |
| 4 | The Order Validator had no check for §8's named "time restrictions" requirement at all — not a weakened check, an entirely missing function | `validator.py` | **MEDIUM** | Added `_check_time_restrictions()`, documented as IMPLEMENTATION CHOICE: v1 has no wall-clock to evaluate `allowed_session`/`valid_until` against (deferred to a future clock-having consumer), but the one structurally-enforceable sub-check — a reduce-only order must not use GTC (it would linger instead of resolving promptly) — is now implemented. |
| 5 | `lifecycle.py::is_valid_broker_transition()` was dead code — written, documented as "used by the Reconciler", but never actually called anywhere | `lifecycle.py` | **MEDIUM** | Wired into `apply_broker_update()` as an advisory warning log (the update is still applied — the broker is always the source of truth for its own order — but an unexpected transition is now surfaced for operator visibility instead of silently possible). Docstring corrected to describe its real caller. |
| 6 | `emergency_flatten()`'s BUILD stage (`builder.build_flatten_order()`) had no exception safety net, unlike its submit stage (`pipeline.submit_built_order`, already wrapped) — an unexpected exception while building ONE position's closing order would abort flattening every OTHER position, the exact "one malformed order cannot abort the batch" violation the submit stage was already protected against | `engine.py` | **MEDIUM** | The build call is now wrapped in its own `try/except` inside the per-position loop, logging and continuing to the next position rather than propagating. |
| 7 | A broker reporting new filled quantity without an `avg_price` (a malformed/incomplete report) had its fill price silently fabricated as `0.0` — a "free trade," which is a worse and more misleading fabrication than a reasonable fallback, for any future downstream P&L consumer | `lifecycle.py` | **LOW** | Falls back to the order's own `limit_price` when available; `0.0` only as the very last resort when no reference price exists at all. |

All 7 fixed issues got dedicated regression tests proving the fix (e.g.
`test_retrying_a_filled_order_against_a_now_invalid_portfolio_does_not_corrupt_the_ledger`,
`test_reconcile_all_open_continues_past_one_broker_exception`,
`test_shutdown_with_a_flaky_broker_still_reaches_stopped`,
`test_cancel_with_a_raising_broker_never_propagates`,
`test_no_portfolio_yet_flatten_is_disclosed_as_degraded_not_a_silent_no_op`,
`test_reduce_only_with_gtc_is_invalid`, `test_unexpected_transition_is_still_applied`,
`test_build_exception_during_flatten_does_not_abort_flattening_the_rest`,
`test_fill_without_avg_price_falls_back_to_the_orders_own_limit_price`). The review found **no** issues
with the order-mechanics validation formulas themselves (tick/lot rounding, quantity bounds, direction
derivation), the per-order or engine lifecycle state machines' OWN transition logic (only the missing
advisory-logging wire-up, finding #5), the idempotent `client_order_id` derivation, or the boundary
rules (no Research Lab/Knowledge Base/Strategy Library/Market Scanner/Signal Engine/Scoring Engine
access anywhere; no real broker/MT5 code anywhere) — all matched the frozen specification exactly.

## 4. Final numbers (after all fixes)

```
pytest ai_trader/execution_engine/tests/ -q
198 passed in 0.93s

mypy --strict ai_trader/execution_engine
Success: no issues found in 31 source files

coverage run --source=ai_trader/execution_engine -m pytest ai_trader/execution_engine/tests/ -q
coverage report --omit="*/tests/*"
TOTAL   912 stmts   11 miss   99%   (builder.py/pipeline.py/reconciler.py: 100%)

pytest ai_trader/ -q   (Market Scanner + Strategy Manager + Signal Engine + Scoring Engine + Risk Manager + Execution Engine together)
1165 passed in 4.37s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine --exclude 'tests/'
Success: no issues found in 89 source files   (no regression in any prior module)
```

## 5. Protected invariants — confirmed untouched

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; `git diff cef57c1~1 HEAD -- code/
  results/ knowledge/` returns empty, confirming 0-diff across the entire Phase 6.1–6.6 implementation
  span.
- **Market Scanner**, **Strategy Manager**, **Signal Engine**, **Scoring Engine**, **Risk Manager**
  implementations — zero files modified. The Execution Engine only *imports* already-published types
  (`RiskDecision`/`PortfolioState`/`OpenPosition`/`Decision` from Risk Manager, `Direction` from Signal
  Engine) — never touches their source, never calls a mutating method.
- **No broker code, no MT5, no live trading, no Simulation Framework, no Learning Engine, no ML** — none
  exist anywhere in this diff, per the CEO directive's explicit exclusion list. The Broker Adapter is a
  `Protocol` (an interface definition) plus a test-only fake; no real venue integration was written.
- **The Execution Engine never generates signals, scores, or re-decides risk** (it executes the Risk
  Manager's own `sizing`/`constraints` exactly, clamping quantity only DOWN, never up); **never learns
  or adapts** (all policy is fixed `ExecConfig` constants); **never accesses Research Lab / Knowledge
  Base / Strategy Library / Market Scanner / Signal Engine / Scoring Engine** — verified by the module's
  own import graph (only `ai_trader.risk_manager` and `ai_trader.signal_engine.types.Direction` are
  reached from outside this package) and confirmed by the adversarial review.
- **Determinism preserved**: no module reached from `engine.py` imports `time`/`random`; `OrderRequest`
  construction/validation are deterministic given identical `(decision, portfolio, caps, config)`
  (`TestDeterminism` in both `test_builder.py` and `test_pipeline.py`); `client_order_id`/
  `order_request_id` are pure functions of `decision_id`, guaranteeing a retry never creates a duplicate
  order regardless of when it happens.

## 6. Verdict

**Execution Engine v1 is READY.**

- Implementation: every architecture component built, matching the frozen spec exactly (no redesign —
  every design decision in §2 fills a genuine spec gap, several explicitly pre-flagged in
  `EXECUTION_ENGINE_HANDOFF.md` before implementation began, never contradicts documented behavior).
- Tests: 198/198 passing, covering the full order-mechanics validation suite, both state machines (11
  order states + 7 engine lifecycle states), every documented failure mode (broker unavailable, timeout,
  network fault, rejection, partial fill, cancel, duplicate, validation failure, internal error,
  portfolio-unavailable, emergency flatten), idempotent retries, batch/malformed-input isolation,
  determinism, shutdown-with-pending-orders, and a real-Risk-Manager/real-Scoring-Engine integration
  test.
- Types: `mypy --strict` clean across all 31 source files (14 production + test package).
- Coverage: 99%, remaining gaps are documented defensive/environment-only or structurally
  doubly-defensive branches.
- Independent adversarial review: completed, found 7 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW),
  all fixed and regression-tested, no outstanding findings.
- Protected invariants: confirmed untouched. Full `ai_trader/` suite (1165 tests, 89 source files across
  6 modules) green with no regressions in Market Scanner, Strategy Manager, Signal Engine, Scoring
  Engine, or Risk Manager.

Per the standing "stop between every phase" directive and the CEO's explicit instruction for this task:
**this verdict does not itself authorize starting Simulation Framework, Portfolio Simulator, Execution
Simulator, Performance Analyzer, Learning Engine, Broker Adapter (a real one), or MT5 integration.** That
requires an explicit new CEO go-ahead.
