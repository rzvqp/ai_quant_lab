# Simulation Framework v1 — Implementation & Validation Report (Phase 6.7)

**Date:** 2026-07-15. **Scope:** production implementation of the Simulation Framework against the
frozen `ai_trader/simulation/*.md`/`SIMULATION_SCHEMA.json` specification and `SIMULATION_HANDOFF.md`,
following the exact process and quality bar established for Phases 6.1–6.6 (Market Scanner → Execution
Engine): resolve the documented open gaps → implement → test continuously → adversarial review → fix
every real issue → report honestly.
**Verdict: READY.** (see §7)

---

## 1. What was built

13 production modules under `ai_trader/simulation/` (12 source `.py` files + `__init__.py`, `py.typed`),
implementing every component `SIMULATION_ARCHITECTURE.md` §3 names:

| architecture component | module |
|---|---|
| Value types (mirrors `SIMULATION_SCHEMA.json`; internal-only shapes for `Bar`/`WorkingOrder`/`SimFillEvent`) | `types.py` |
| `SimulationContext` (run spec) + every documented numeric/policy default | `config.py` |
| Errors | `exceptions.py` |
| Schema loading + compiled validation | `schema_validation.py` |
| Replay Clock (deterministic `as_of` sequencer) | `clock.py` |
| Replay Data Source (reads `data/market/*.csv`, feeds the real Market Scanner, lookahead-safe multi-timeframe order) | `data_source.py` |
| Execution Simulator (virtual Broker Adapter: fill rules, cost model, TIF, OCO/bracket) | `execution_simulator.py` |
| Portfolio Simulator (virtual account: accounting, margin, liquidation, `PortfolioState` projection) | `portfolio_simulator.py` |
| Performance Analyzer (metrics, attribution, allocation, risk events, session/daily/monthly rollups, `SimulationReport`) | `performance_analyzer.py` |
| Artifact/report writer (atomic JSONL/JSON + checksummed manifest) | `artifacts.py` |
| Simulation Harness (orchestrator: composes the real six pipeline modules unchanged + the three sim-only components, drives the per-bar cycle, run-lifecycle state machine) | `harness.py` |
| Public API facade (`configure/load/run/step/run_batch/pause/resume/stop/report/status/statistics/health/versions`) | `api.py` |

**87 tests** across 13 test files: unit tests per component (fill rules per order type, cost model,
TIF/expiry, OCO/bracket same-bar conflict resolution, portfolio accounting invariants, margin/
liquidation, performance-metric formulas, schema error paths, artifact atomic-write/checksum
correctness), a real six-module pipeline integration test (Market Scanner → Strategy Manager → Signal
Engine → Scoring Engine → Risk Manager → Execution Engine, composed **unchanged**, driven over real
historical XAUUSD bars), determinism tests (identical `SimulationContext`+seed ⇒ byte-identical
report), a dedicated conformance test against the frozen research engine's documented cost/fill
conventions, and 10 regression tests — one per adversarial-review finding (§4).

`mypy --strict`: **0 errors** across all 102 source files in the full `ai_trader/` tree (89 prior +
13 new), production code only. **Full suite: 1252/1252 passing** (1165 prior + 87 new, zero
regressions). **Coverage: 95%** total (source only; `ai_trader/simulation/` itself ranges 89–100% per
file, all above the 89% floor — see §6 for the two files below 95% and why).

## 2. The 8 frozen IMPLEMENTATION CHOICEs (resolved BEFORE any code, per CEO directive)

Written to `ai_trader/simulation/IMPLEMENTATION_CHOICES.md` before writing any implementation code, and
never revised after seeing performance results. Summary (full rationale in that file):

1. **Execution Simulator ↔ `BrokerAdapter`**: implements the Protocol unmodified (verified against
   `pipeline.py`/`reconciler.py`'s actual calls), plus one simulation-only `advance_bar(as_of, bars)`
   method the Harness calls once per bar.
2. **`PortfolioState` ownership**: reused verbatim (same choice Execution Engine made); Portfolio
   Simulator's own `SimAccount` carries everything richer (margin, per-symbol exposure, ledger) and
   projects `PortfolioState` as a pure, never-cached function.
3. **Partial-fill liquidity proxy**: `FULL_FILL` is the v1 default (the doc's own named default);
   `FIXED_FRACTION` is a deterministic, config-driven alternative for exercising the partial-fill path.
4. **Latency model**: `NONE` only in v1 (immediate acks); any other value rejected at `configure()`.
5. **Margin defaults**: `initial_margin_pct=0.01`, `maintenance_margin_pct=0.005`, `leverage_max=100.0`
   — conservative placeholders, never tuned against results.
6. **Liquidation ordering**: worst-floating-PnL-first, ties by symbol id ascending.
7. **Conformance test**: exact (0-tick tolerance) check against the research engine's documented
   convention (`code/mstrat.py`, read-only, never imported into production code).
8. **Artifact persistence**: atomic JSONL/JSON under `results/simulation_runs/<run_id>/` + a
   sha256-checksummed manifest.

## 3. Design decisions discovered mid-implementation (documented, not silent)

Three additional gaps surfaced only once real code met the real upstream contracts — each resolved and
documented in-line, not silently:

- **`OrderConstraints.valid_until` is a bar COUNT, not an epoch timestamp** — confirmed by reading
  `risk_manager/config.py`'s own `ConstraintDefaults` docstring after a test failure exposed orders
  expiring immediately. Fixed in `execution_simulator._resolve_valid_until`.
- **Spread/slippage per-leg convention**: the frozen research engine (`code/mstrat.py`:
  `cost=(spread_ticks+slip_ticks)*TICK`) applies the FULL configured tick count per leg, not a halved
  bid/ask spread — confirmed and fixed via the conformance test.
- **STOP fills apply slippage only, never spread** — `EXECUTION_SIMULATOR.md`'s own Stop row
  deliberately omits spread (contrasted with Market's explicit "± spread ± slippage"); a BRACKET order
  carrying a `limit_price` must price like a resting LIMIT (neither), not like its raw `order_type`
  label. Both fixed via an explicit `apply_spread`/`apply_slippage` pair per fill, never inferred from
  `order_type` alone.

## 4. Mandatory adversarial review — findings and fixes

A fresh-eyes subagent with no memory of writing the code read all 10 frozen docs + `IMPLEMENTATION_CHOICES.md`
+ every source file, hunting for cost-model deviations, fail-safe violations, determinism violations,
state-machine correctness, sibling-entry-point inconsistency, and prose-vs-execution-order bugs
(`SIMULATION_HANDOFF.md` §13). **8 real issues found (3 CRITICAL, 2 HIGH, 3 MEDIUM)** — every finding
was verified against the actual source before fixing, per the project's own standing discipline:

1. **CRITICAL — FOK partial-fill revert leaked an already-emitted fill.** A FOK order's partial fill
   was appended to the caller's `fills` list BEFORE `_enforce_tif` reverted it (`filled_qty=0`,
   `CANCELLED`) — the Portfolio Simulator booked a fill the Execution Simulator's own book said never
   happened. **Fixed**: TIF enforcement now runs inside the same match step, before the fill is ever
   returned; a reverted FOK fill is never emitted. Regression test:
   `TestFinding1FokPartialFillNeverLeaks`.
2. **CRITICAL — no exception safety net during RUNNING.** `configure()`/`load()` fail-fast to `FAILED`,
   but `step()`'s call into the per-bar loop had no `try/except` — any unexpected exception mid-run
   would crash the whole process instead of producing a deterministic partial report/`FAILED` state.
   **Fixed**: `step()` now wraps `_run_one_bar` and fails the run cleanly. Regression test:
   `TestFinding2HarnessNeverCrashesOnUnexpectedException`.
3. **CRITICAL — the documented pre-fill margin rejection (`IMPLEMENTATION_CHOICES.md` §5) was never
   implemented.** No code path checked `required_margin > free_margin` before opening/increasing a
   position. **Fixed**: `ExecutionSimulator.set_free_margin_provider()` + a pre-fill gate, wired by the
   Harness to the Portfolio Simulator's own free-margin snapshot; reduce-only fills are never blocked.
   Regression tests: `TestFinding3MarginPreFillRejection` (2 tests).
4. **HIGH — liquidation threshold was off by ~100x.** `margin_level` (an equity/used_margin RATIO,
   ~100 for a healthy account) was compared directly against `maintenance_margin_pct` (a small
   PERCENTAGE, 0.005) — liquidation never fired until equity was already catastrophically near zero
   under the shipped defaults. **Fixed**: compare against the dimensionless
   `maintenance_margin_pct / initial_margin_pct` ratio, matching `IMPLEMENTATION_CHOICES.md` §6's own
   stated intent. Regression test: `TestFinding4LiquidationThresholdMath`.
5. **HIGH — `close_at_end_policy` was defined but never consulted anywhere.** Positions open at run end
   were simply left open regardless of config, contradicting `SIMULATION_ARCHITECTURE.md` §8/
   `SIMULATION_SEQUENCE.md` §6/`SIMULATION_STATE_MACHINE.md` R6, and silently desyncing `equity`
   (includes floating PnL) from `trade_ledger`-derived stats (excludes it). **Fixed**:
   `SimulationHarness._finalize_at_end()` synthesizes a reduce-only closing fill for every open position
   under `CLOSE_AT_LAST`, called from both natural completion and `stop()`. Regression tests:
   `TestFinding5CloseAtEndPolicy` (2 tests, one per policy value).
6. **MEDIUM/HIGH — `execution_log.jsonl` was mislabeled.** Gated on `record.risk_events` (not
   `record.execution_log`, which was dead config) and populated with `account.risk_events` instead of
   order-lifecycle fills — the artifact `IMPLEMENTATION_CHOICES.md` §8 promised never existed. **Fixed**:
   `SimAccount.execution_log` now collects real `SimFillEvent`s; `artifacts.py` writes the right data
   under the right flag. Regression test: `TestFinding6ExecutionLogContainsRealFills`.
7. **MEDIUM — Risk Manager DENY/SUSPENDED/EMERGENCY_STOP/cooldown events were dropped entirely.** Only
   liquidation ever reached `report.risk_events`, contradicting `PERFORMANCE_ANALYZER.md` §6. **Fixed**:
   `PortfolioSimulator.record_risk_event()` + the Harness calling it for every non-ALLOW decision and
   non-READY `engine_state`. Regression test: `TestFinding7DenyDecisionsRecordedAsRiskEvents`.
8. **MEDIUM — a partially-filled IOC order was mislabeled `FILLED`.** `filled_qty > 0` alone drove the
   state, falsely implying the full requested quantity executed. **Fixed**: IOC's unfilled remainder is
   always `CANCELLED` regardless of partial fill; `filled_qty` on the record still carries the true
   partial amount. Regression test: `TestFinding8IocPartialFillNeverMislabeledFilled`.

Nothing else was reported — the reviewer explicitly confirmed determinism/seeding, the core spread/
slippage/commission math, weighted-average scale-in and realized-PnL accounting, the intrabar
stop-before-target resolver, multi-timeframe ingest ordering, and the API facade's sibling-entry-point
consistency as correct.

## 5. Performance benchmark

Per `SIMULATION_HANDOFF.md` §12 ("establish a controlled, smaller-scale baseline first"):

- **Small baseline** (~3 months, one symbol, M15+H1+H4+D1): 5,261 bars in 4.77s → **1,103 bars/sec**.
- **Full-scale confirmation** (entire available XAUUSD history, 2023-01 → 2026-07, one symbol):
  **83,479 bars in 51.5s → 1,620 bars/sec**, `COMPLETED`, equity exactly unchanged at
  `starting_balance` throughout (the expected fail-safe result — see §8), no memory/time blow-up. No
  profiler was used for either run (`SIMULATION_HANDOFF.md` §12's own `tracemalloc`-cliff warning); a
  cross-checked, unprofiled wall-clock timing was used throughout.

## 6. Coverage detail

| file | coverage | note |
|---|---|---|
| `types.py` | 100% | |
| `exceptions.py` | 100% | |
| `data_source.py` | 98% | |
| `portfolio_simulator.py` | 98% | |
| `performance_analyzer.py` | 96% | |
| `api.py` | 95% | |
| `clock.py` | 95% | |
| `config.py` | 95% | |
| `schema_validation.py` | 95% | |
| `execution_simulator.py` | 93% | |
| `artifacts.py` | 91% | uncovered: `_json_default`'s type-error fallback branch, one manifest edge |
| `harness.py` | 89% | uncovered: a few defensive `assert`-guarded branches unreachable via the public API, one rare pause/resume interleaving |

Both sub-95% files are exercised by real tests (including full end-to-end integration and the 10
adversarial-fix regression tests); the uncovered lines are defensive/edge branches, not untested core
logic — disclosed rather than padded with low-value tests to hit a number.

## 7. Protected-invariants confirmation (verified live, this session)

- `git diff cef57c1~1 HEAD -- code/ results/ knowledge/` → **empty** (Research Lab + Strategy Library
  still 0-diff since Phase 6.1 began).
- `git diff af00953 -- ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine`
  → **empty** (the six composed pipeline modules are byte-identical to the pre-6.7 HEAD; nothing in
  them was touched this session).
- `git status --porcelain` outside `ai_trader/simulation/` → **empty** (every change this session is
  additive, inside the new package, plus this report / `NEXT_SESSION.md` / `CHANGELOG.md`).
- No broker code, no MT5, no live execution, no Learning Engine anywhere in the tree.

## 8. Known limitations (disclosed, not fixed — deliberate scope discipline)

1. **No real per-strategy signal logic exists yet** (Signal Engine's pre-existing, disclosed gap,
   carried forward unchanged from Phase 6.3/`NEXT_SESSION.md` §G item 1) — every real Strategy Library
   signal is `INVALID` by design, so a real end-to-end historical run over the full XAUUSD dataset
   produces **zero trades** and unchanged equity (§5). The framework is proven to run the real six-module
   pipeline over real historical data deterministically, fail-safe, at ~1,600 bars/sec — **not** that it
   is currently profitable, because no real strategy decision logic exists to trade with. This is a
   separate, not-yet-scoped task (interpreting the Strategy Library's natural-language rules into
   executable code), not part of Phase 6.7.
2. **R-multiple (`pnl_R`) requires an explicit stop hint registered at the order's own fill time** — if
   the originating `RiskDecision.constraints.stop` is absent, `TradeRecord.pnl_r` is `None`, never
   fabricated.
3. **Portfolio-level `max_drawdown_R`** and **per-period (`session`/`daily`/`monthly`) `return_pct`/
   `max_drawdown_pct`** are left `None` — computing them correctly requires either a portfolio-wide R
   unit (no single one exists across mixed-stop strategies) or per-period equity-curve slicing not yet
   implemented; disclosed rather than approximated.
4. **Capital allocation report** is a simplified, single time-point (not time-series) measure of
   realized-trade notional share per strategy — `PERFORMANCE_ANALYZER.md` §5's full time-series
   allocation-vs-contribution report is not implemented.
5. **`atr_fraction` slippage model** falls back to zero extra slippage — bar-level ATR is not threaded
   into the Execution Simulator's matching loop in v1 (it lives in the richer `MarketContext` the
   Signal/Scoring/Risk stages consume, not the bare OHLCV `Bar` this module matches against).
6. **`run_batch` executes sequentially**, not in parallel — still fully independent/reproducible per
   run; parallel execution is deferred (a permission in `SIMULATION_API.md`, not a requirement).
7. **Session classification** (`asia`/`london`/`ny`/`late`) is a simple UTC-hour-bucket approximation,
   not the Market Scanner's own internal session-anchoring logic (not part of its public API).

## 9. Final deliverables checklist

1. This report. ✅
2. `NEXT_SESSION.md` updated for Phase 6.7 close / next-session handoff. ✅ (§ next)
3. `CHANGELOG.md` updated. ✅ (§ next)
4. Files created: 12 production modules + `__init__.py`/`py.typed` + `IMPLEMENTATION_CHOICES.md` under
   `ai_trader/simulation/`, 13 test files under `ai_trader/simulation/tests/`, this report. Zero files
   modified outside `ai_trader/simulation/` (§7).
5. Focused tests: 87/87 passing. Full suite: 1252/1252 passing, zero regressions.
6. `mypy --strict`: 0 errors, 102 source files.
7. Coverage: 95% total; per-file 89–100% (§6).
8. Performance benchmark: §5 (1,103–1,620 bars/sec; 83,479-bar full-history run completes in 51.5s).
9. Adversarial review: 8 findings (3 CRITICAL, 2 HIGH, 3 MEDIUM), all fixed with dedicated regression
   tests (§4).
10. Protected-area 0-diff: confirmed live, §7.
11. Known limitations: §8.
12. **End-to-end historical simulation is operational**: the framework runs the real, composed
    six-module pipeline against real historical XAUUSD data, deterministically, fail-safe, at
    production-relevant speed. It has **not yet demonstrated profitability**, because real strategy
    signal logic doesn't exist yet (§8 item 1) — this is the pre-existing, disclosed, carried-forward
    gap from Phase 6.3, not a Phase 6.7 defect.

## 10. Verdict

**READY.**

The Simulation Framework itself — SimulationContext, Replay Clock, Replay Data Source, Execution
Simulator, Portfolio Simulator, Performance Analyzer, artifact writer, Harness, public API — is
production-quality, fully tested (87 focused + full-suite 1252 passing), `mypy --strict` clean, 95%
covered, adversarially reviewed with every real finding fixed and regression-tested, deterministic
(byte-identical reports proven by direct test), and runs the real composed six-module pipeline over
real historical data at ~1,600 bars/sec without crashing, corrupting state, or touching any protected
area. It is READY as a deterministic backtesting engine.

It is explicitly **not** a demonstration of a profitable AI Trader — that requires real strategy signal
logic (§8 item 1), a separate, larger, not-yet-scoped task outside Phase 6.7's boundaries. Per
`SIMULATION_HANDOFF.md` §17 and the CEO's own explicit instruction, this session stops here: **no**
Learning Engine, strategy optimization, Broker Adapter, MT5, paper trading, or live trading work has
been started or is authorized by this verdict.
