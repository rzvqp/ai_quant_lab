# NEXT_SESSION.md — Official Handoff (AI Trader Implementation Phase)

**Official session-close document, rewritten in full on 2026-07-15 per explicit CEO directive.** This
document is self-contained: a new Claude session must be able to continue correctly from this file
alone, without reading any prior conversation or any other `NEXT_SESSION.md` version. Every fact below
was verified directly against `git log`/`git status`/`git diff`/a live test run at close time — nothing
here is assumed or carried over unverified.

---

## 0. TL;DR for the next session

```
✓ Market Scanner   READY   (Phase 6.1)
✓ Strategy Manager READY   (Phase 6.2)
✓ Signal Engine    READY   (Phase 6.3)
✓ Scoring Engine   READY   (Phase 6.4)
✓ Risk Manager     READY   (Phase 6.5)
✓ Execution Engine READY   (Phase 6.6)   ← just closed

Next: Phase 6.7+ — Simulation Framework implementation (Portfolio Simulator, Execution Simulator,
      Performance Analyzer). NOT STARTED. Requires explicit new CEO approval before writing any code.

Branch: ai-trader-implementation   HEAD: 626e59d   Working tree: CLEAN (before this doc's own commit)
Full ai_trader/ suite: 1165 tests passing · mypy --strict clean (89 source files, 6 modules) ·
overall coverage 95% (single 0%-covered file is a standalone benchmark script, not a defect)
Protected paths (code/, results/, knowledge/): 0-diff since Phase 6.1 began — verified this session.
```

---

## 1. Current project mission

**AI Quant Research Lab → AI Trader.** Two systems, physically separated by design:

- **Research Lab** (`code/`, `results/`, `knowledge/`) — discovers and validates trading strategies against
  historical XAUUSD data through a falsification-first pipeline (engine → matched-null → Wave experiments →
  eventually global-FDR → walk-forward → terminal holdout). Frozen and stable; not touched during AI Trader work.
- **Strategy Library** (`knowledge/strategies/`) — publishes the Research Lab's output as 51 executable strategy
  specifications (S1–S51), each with mechanism/entry/exit/stop/metrics/validation-status.
- **Strategy Interface v1** (`knowledge/interface/`) — the ONLY sanctioned contract between the Lab and the
  Trader: a versioned JSON Schema (`strategy_contract.v1.schema.json`) plus a runtime Strategy API
  (`STRATEGY_API_v1.md`). The Trader may consume strategies ONLY through this interface — never Research Lab
  internals directly.
- **AI Trader** (`ai_trader/`) — the execution system, being built module-by-module: **Market Scanner →
  Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine** (all six now
  READY), plus a **Simulation Framework** that runs this exact same pipeline against historical data with
  a virtual broker/account instead of a real one (not yet implemented — next).

**CEO-mandated sequencing (current, standing directive):** the AI Trader must first become a **complete,
deterministic backtesting/simulation engine** and prove profitability over historical data. **Only after
simulation proves profitable does Broker Adapter / MetaTrader / live execution work begin** (that is Phase 8+,
not authorized now). Within that, the CEO also pivoted from "architecture only" to "implement for real,
production-quality code" starting with Market Scanner (Phase 6.1) and now through Execution Engine (Phase 6.6).

---

## 2. Project status — every phase, verified

### 2a. Design docs (all complete, frozen specification)

| module | location | status |
|---|---|---|
| Research Lab (S1–S51 discovery, matched-null, knowledge base/ontology) | `code/`, `results/`, `knowledge/` | **DONE / FROZEN** |
| Wave 1 (research experiments EXP-01..06) | `knowledge/experiments/WAVE_1_*` + `code/wave1_harness.py`, `code/run_wave1.py` | **EXECUTED** (results committed) |
| Strategy Library | `knowledge/strategies/` (51 folders + `INDEX.md` + `library_manifest.json`) | **DONE** — all 51 strategies (S1–S51) |
| Strategy Interface v1 | `knowledge/interface/` (README, STRATEGY_INTERFACE_v1.md, strategy_contract.v1.schema.json, STRATEGY_API_v1.md, runtime_responses.v1.schema.json, AI_TRADER_ARCHITECTURE.md) | **DONE** |
| Market Scanner docs | `ai_trader/market_scanner/{README,MARKET_SCANNER_ARCHITECTURE,MARKET_CONTEXT_SCHEMA.json,MARKET_SCANNER_API,MARKET_SCANNER_SEQUENCE}.*` | **DONE** (Phase 5.1) |
| Strategy Manager docs | `ai_trader/strategy_manager/` (README, ARCHITECTURE, API, STATE_MACHINE, SEQUENCE, STRATEGY_REGISTRY_SCHEMA.json) | **DONE** (Phase 5.2) |
| Signal Engine docs | `ai_trader/signal_engine/` (README, ARCHITECTURE, API, SEQUENCE, STATE_MACHINE, SIGNAL_SCHEMA.json, SIGNAL_EXPLANATION_SCHEMA.json) | **DONE** (Phase 5.3) |
| Scoring Engine docs | `ai_trader/scoring_engine/` (README, ARCHITECTURE, SCORING_MODEL.md, API, SEQUENCE, STATE_MACHINE, SCORING_SCHEMA.json) | **DONE** (Phase 5.4) |
| Risk Manager docs | `ai_trader/risk_manager/` (README, ARCHITECTURE, RISK_POLICY.md, POSITION_SIZING.md, API, SEQUENCE, STATE_MACHINE, RISK_SCHEMA.json) | **DONE** (Phase 5.5) |
| Execution Engine docs | `ai_trader/execution_engine/` (README, EXECUTION_ENGINE_ARCHITECTURE.md, ORDER_LIFECYCLE.md, ORDER_SCHEMA.json, EXECUTION_API.md, EXECUTION_SEQUENCE.md, EXECUTION_STATE_MACHINE.md, EXECUTION_FAILURE_POLICY.md) | **DONE** (Phase 5.6) |
| Simulation Framework docs | `ai_trader/simulation/` (README, ARCHITECTURE, PORTFOLIO_SIMULATOR.md, EXECUTION_SIMULATOR.md, PERFORMANCE_ANALYZER.md, CONTEXT.md, API, SEQUENCE, STATE_MACHINE, SIMULATION_SCHEMA.json) | **DONE** (post Phase 5.6 pivot) — **NOT implemented yet — this is next** |

### 2b. Implementations (production code)

| module | location | status |
|---|---|---|
| Market Scanner | `ai_trader/market_scanner/*.py` + `adapters/` + `tests/` | **READY** (Phase 6.1, `MARKET_SCANNER_VALIDATION_REPORT.md`). 127 tests. 2 critical bugs found+fixed by adversarial review. |
| Strategy Manager | `ai_trader/strategy_manager/*.py` + `tests/` | **READY** (Phase 6.2, `STRATEGY_MANAGER_VALIDATION_REPORT.md`). 16 source modules, 251 tests, mypy --strict clean, 99% coverage. Adversarial review found 6 real bugs, all fixed. |
| Signal Engine | `ai_trader/signal_engine/*.py` + `tests/` | **READY** (Phase 6.3, `SIGNAL_ENGINE_VALIDATION_REPORT.md`). 10 source modules, 181 tests, mypy --strict clean, 99% coverage. Adversarial review found 5 real bugs + 1 real gap (all fixed), 1 finding confirmed correct-as-designed. |
| Scoring Engine | `ai_trader/scoring_engine/*.py` + `tests/` | **READY** (Phase 6.4, `SCORING_ENGINE_VALIDATION_REPORT.md`). 13 source modules, 199 tests, mypy --strict clean, 98% coverage. Adversarial review found 4 real bugs (2 CRITICAL, 1 HIGH, 1 MEDIUM), all fixed. |
| Risk Manager | `ai_trader/risk_manager/*.py` + `tests/` | **READY** (Phase 6.5, `RISK_MANAGER_VALIDATION_REPORT.md`). 13 source modules, 209 tests, mypy --strict clean, 99% coverage (`engine.py` 100%). Adversarial review found 8 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW), all fixed. |
| **Execution Engine** | `ai_trader/execution_engine/*.py` + `tests/` | **READY** (Phase 6.6, `EXECUTION_ENGINE_VALIDATION_REPORT.md`). 13 source modules, 198 tests, mypy --strict clean, **99% coverage**. Adversarial review found **7 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW)**, all fixed + regression-tested. **Just closed this session.** |
| Simulation Framework | `ai_trader/simulation/` | **NOT implemented** — docs only. **Next phase.** |
| Portfolio Manager | *(no directory exists)* | **NOT DESIGNED** — resolved for Execution Engine's own purposes by reusing `ai_trader.risk_manager.types.PortfolioState` directly (§6). Still not a real, separate module. |
| Learning Engine | *(no directory exists)* | **NOT DESIGNED, NOT STARTED.** |
| Broker Adapter / MT5 Integration | *(no directory exists)* | **NOT AUTHORIZED** — explicitly gated on simulation proving profitable first. Execution Engine's own `BrokerAdapter` is an abstract `Protocol` only — no real venue integration exists. |

**Key architectural invariant across every AI Trader module:** the documented pipeline order is fixed —
`Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine →
[Execution Simulator today / Broker Adapter later] → Portfolio Simulator → Performance Analyzer → Learning Engine
(future, not designed)`. Each module talks ONLY to its immediate documented neighbors (strict interaction
matrices are specified in each module's ARCHITECTURE.md) — e.g. Signal Engine never calls `get_score()`, Scoring
Engine never touches the broker, Risk Manager never generates signals, Execution Engine never re-decides risk.

### 2c. Current pipeline (implemented portion, end-to-end)

```
MarketContext (Market Scanner, real bars via ReplayAdapter)
   → StrategySignal (Signal Engine, per configured strategy — currently every real strategy in
     Strategy Library returns INVALID/CORRUPTED_OUTPUT because StrategyRuntimeHandle.api has no real
     detect/generate_signal logic yet, see §8 item 1)
   → OpportunityScore (Scoring Engine — degrades every real signal to a classified SKIP/INVALID score)
   → RiskDecision (Risk Manager — degrades every SKIP/INVALID opportunity to a classified DENY)
   → OrderStatus (Execution Engine — a DENY/non-ALLOW decision is a no-op REJECTED status; proven
     fail-safe end-to-end for the real-strategy chain by test_engine_integration.py)
   → [Execution Simulator / Broker Adapter — NOT YET BUILT — the next link in the chain]
```
The pipeline is fully wired and fail-safe end-to-end for today's "every real strategy signal is
INVALID" state, all the way through the Execution Engine now. It has been proven end-to-end against a
REAL, schema-valid ALLOW `RiskDecision` too (built via Risk Manager's own fixtures against a real
Scoring Engine chain, `test_engine_integration.py::TestRealAllowDecisionFillsEndToEnd`) — that decision
flows through the Execution Engine to a FILLED order against a fake (Protocol-conformant) broker. No
module has yet been exercised against a genuine ALLOW produced by a REAL strategy's own logic, because
that logic doesn't exist yet (see §8 item 1) — the Execution Engine itself has no such gap.

---

## 3. Current git state

**Branch:** `ai-trader-implementation`
**HEAD commit:** `626e59d` — "Phase 6.6: implement Execution Engine v1, adversarially reviewed, READY"
**Working tree:** CLEAN at the time this document itself was written (before its own commit, which will
also include `EXECUTION_ENGINE_VALIDATION_REPORT.md`'s companion doc updates).

All branches, in chronological order (oldest → newest), with their HEAD commit at handoff time:

| # | branch | HEAD commit | what it contains |
|---|---|---|---|
| 1 | `master` | `1bc0ffb` | Research Lab baseline (S1–S20 campaign, engine v2) |
| 2 | `strategy-development` | `0d776ec` | S1–S20 dedup registry + S21–S40 design library |
| 3 | `research-main` | `7afbd3b` | Consolidated Research Lab, S1–S51, matched-null, Wave 1 EXECUTED |
| 4 | `ai-trader-implementation` | `626e59d` | **Current.** Strategy Library, Strategy Interface, AI Trader architecture (Phases 5.1–5.6 + Simulation), Market Scanner/Strategy Manager/Signal Engine/Scoring Engine/Risk Manager/Execution Engine implementations (Phases 6.1–6.6), all READY |

Last 8 commits on `ai-trader-implementation` (newest first):
```
626e59d Phase 6.6: implement Execution Engine v1, adversarially reviewed, READY
6761e39 Official session close: Phase 6.5 complete, Phase 6.6 handoff prepared
7c225d1 Phase 6.5: implement Risk Manager v1, adversarially reviewed, READY
7825726 Phase 6.4: Scoring Engine v1 implementation, adversarially reviewed, READY
19069f4 Phase 6.3: Signal Engine v1 implementation, adversarially reviewed, READY
ceb50b5 Deep-validation addendum: Market Scanner CPU profile, memory, parity vs frozen engine
b62288e Phase 6.2: Strategy Manager v1 implementation, adversarially reviewed, READY
526a921 Phase 6.1 RESOLUTION: root-cause Market Scanner large-scale benchmark, verdict READY
```

**Protected-path 0-diff verification (re-run this session, not assumed):**
```
git diff cef57c1~1 HEAD -- code/ results/ knowledge/
```
returns **empty** — `cef57c1` is the commit that started Phase 6.1 (Market Scanner implementation, the
first AI Trader production code). Nothing under `code/`, `results/`, or `knowledge/` has changed across
the entire Phase 6.1→6.6 implementation span. (Note: comparing against the much older `master`/`1bc0ffb`
baseline instead is NOT the right check — it would show the legitimate, pre-Phase-6.1 Strategy Library
build as a "diff," which is expected, documented history, not a violation. Always diff from `cef57c1~1`
forward.)

---

## 4. Testing, coverage, and type-checking statistics (verified this session)

```
pytest ai_trader/ -q
1165 passed in ~4.5s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine \
              ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine --exclude 'tests/'
Success: no issues found in 89 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   5805 stmts   266 miss   95%
```

Per-module test counts (sum to 1165): Market Scanner 127, Strategy Manager 251, Signal Engine 181,
Scoring Engine 199, Risk Manager 209, **Execution Engine 198**.

The 95% *overall* figure is pulled down by exactly one file:
`ai_trader/market_scanner/benchmarks/bench_market_scanner.py` (181 stmts, 0% — a standalone CLI
benchmark script, never exercised by pytest, not a source-code defect). Every module's own coverage
(reported in its own validation report) is 98–100%:

| module | coverage | mypy --strict | notes |
|---|---|---|---|
| Market Scanner | see `MARKET_SCANNER_VALIDATION_REPORT.md` | clean | benchmark script excluded from the module's own reported % |
| Strategy Manager | 99% | clean | |
| Signal Engine | 99% | clean | |
| Scoring Engine | 98% | clean | |
| Risk Manager | 99% (`engine.py` 100%) | clean | remaining gaps: 2 lines in `pipeline.py`, 6 lines in `schema_validation.py` (environment paths) |
| **Execution Engine** | **99%** (`builder.py`/`pipeline.py`/`reconciler.py` 100%) | clean | remaining gaps: `schema_validation.py`'s environment paths (6 lines, same class as every prior module), one `lifecycle.py` transition-table branch, two `validator.py` defensive fallbacks, `engine.py`'s doubly-defensive `emergency_flatten` inner safety net |

`mypy --strict` across the FULL `ai_trader/` tree (including every module's own `tests/` package) shows
98 pre-existing errors in 16 files — **all** in Strategy Manager's and Market Scanner's own test files
(`union-attr`/`type-arg`/`no-untyped-def`). These predate the Execution Engine session, are outside its
scope, and were NOT touched. Each module's own validation report scopes its "mypy --strict clean" claim
to that module's source + its own tests (Execution Engine's own `tests/` package IS mypy --strict clean,
unlike Strategy Manager's/Market Scanner's); the cross-module combined run above intentionally excludes
`tests/` for exactly this reason. **Known, disclosed item for a future cleanup pass — not blocking.**

---

## 5. Validation reports (one per implemented module, repo root)

| report | module | verdict |
|---|---|---|
| `MARKET_SCANNER_VALIDATION_REPORT.md` | Market Scanner | READY |
| `STRATEGY_MANAGER_VALIDATION_REPORT.md` | Strategy Manager | READY |
| `SIGNAL_ENGINE_VALIDATION_REPORT.md` | Signal Engine | READY |
| `SCORING_ENGINE_VALIDATION_REPORT.md` | Scoring Engine | READY |
| `RISK_MANAGER_VALIDATION_REPORT.md` | Risk Manager | READY |
| `EXECUTION_ENGINE_VALIDATION_REPORT.md` | Execution Engine | READY |
| `EXECUTION_ENGINE_HANDOFF.md` | Execution Engine | *(the pre-implementation handoff written at the Phase 6.5→6.6 boundary — now historical; superseded by the validation report above for anything about the actual implementation, but still useful for the design-decision rationale it captured before code existed)* |

Every validation report follows the identical, mandatory template established at Phase 6.1 and held to
every phase since: what was built → design decisions (gap-fills, marked "IMPLEMENTATION CHOICE") →
independent adversarial review findings + fixes → final test/mypy/coverage numbers → protected-invariant
confirmation → verdict. **Follow this exact template for the Simulation Framework's own report(s) too.**

---

## 6. Important design decisions and open items to carry forward

- **Portfolio Manager gap — RESOLVED for Execution Engine, still open more broadly.** No real Portfolio
  Manager module exists. Execution Engine resolved this by reusing
  `ai_trader.risk_manager.types.PortfolioState` directly (documented IMPLEMENTATION CHOICE #1 in
  `execution_engine/types.py`'s own module docstring) — Risk Manager is an allowed direct dependency for
  Execution Engine per the interaction matrix. **The Simulation Framework will face the SAME question**
  for its own Portfolio Simulator (`PORTFOLIO_SIMULATOR.md`) — it may make sense to formalize
  `PortfolioState` as a genuinely shared type at that point (e.g. promoted to its own small module both
  Risk Manager and Execution Engine import from) rather than each new consumer re-deciding independently,
  but that is a decision for the next session/CEO, not made here.
- **Broker Adapter remains abstract-only.** Execution Engine's `broker_adapter.py` defines a pull-based
  `Protocol` (`submit_order`/`cancel_order`/`query_status`/`query_open_orders`/`capabilities`) with a
  deterministic fake test double (`tests/fixtures/fake_broker.py`) — no real venue integration exists.
  **The Simulation Framework's own Execution Simulator (`EXECUTION_SIMULATOR.md`) is the natural next
  implementer of this exact `BrokerAdapter` Protocol** (a simulated, historical-data-driven broker) —
  check whether `EXECUTION_SIMULATOR.md`'s own documented contract matches this Protocol shape, or
  whether it names something different; do not assume they're identical without checking.
- **`fastjsonschema` from the start.** Every implemented module's hot-path schema validation uses
  `fastjsonschema` (compiled once) for the hot path and `jsonschema` only for one-time startup
  shape-sanity checks. `SIMULATION_SCHEMA.json` exists and is ready for the same pattern.
- **The independent adversarial-review technique is mandatory, not optional, for every future module
  too.** It has found real bugs in all six implemented modules: 2 (Market Scanner), 6 (Strategy
  Manager), 5+1 (Signal Engine), 4 (Scoring Engine), 8 (Risk Manager), 7 (Execution Engine) — **33 real
  issues total, zero false-negative sessions.** Run it (a fresh-eyes subagent with no memory of writing
  the code, reading every frozen spec doc in full then every source file) before declaring the
  Simulation Framework READY.
- **Sibling-entry-point inconsistency is the dominant recurring bug class across the last two modules.**
  Risk Manager: 3 of 8 findings. Execution Engine: at least 3 of 7 findings (the duplicate-guard-ordering
  bug, the missing exception safety in `cancel()`/`reconcile()`/`shutdown()`, and `emergency_flatten`'s
  build stage lacking what its submit stage already had). **When a module's public API has multiple
  entry points that can each independently touch shared mutable state (a Ledger, a Portfolio, a
  Simulator's clock/account), design ONE shared internal helper for that mutation from the very first
  draft, and have the adversarial review check every entry point against it explicitly** — do not treat
  this as an afterthought fixed only after review; it is now a KNOWN failure mode this codebase produces
  reliably when not designed against from the start.
- **A new, generalizable lesson from Execution Engine's own review**: when a pipeline stage ordering
  matters for CORRECTNESS (not just prose-readability), verify the actual code order matches the
  necessary order, not just what the architecture doc's prose HAPPENS to list first. Here,
  `EXECUTION_ENGINE_ARCHITECTURE.md` §6 lists "3. Validate ... 4. Duplicate guard" in that prose order,
  but the CORRECT implementation runs duplicate-guard BEFORE validate (re-validating an idempotent retry
  against a possibly-changed input can silently corrupt a terminal record). **Prose ordering in a frozen
  doc is not always the same as execution-order correctness — reason about WHY each stage exists, not
  just copy the list order.**
- **Gap-fill pattern, reaffirmed every phase:** when a frozen spec names an input/output without fully
  specifying its mechanism, fill it with an explicit, documented, honesty/safety-preserving default and
  mark it "IMPLEMENTATION CHOICE" in the source — never silently redesign, never leave it unstated.
  Execution Engine's `config.py` (order-type mapping policy, rounding policy, quantity-limit policy,
  flatten max-slippage placeholder) is a fresh worked example of this pattern.

---

## 7. Protected invariants — confirmed untouched (verified this session)

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; 0-diff confirmed via
  `git diff cef57c1~1 HEAD -- code/ results/ knowledge/` (empty), covering the entire Phase 6.1–6.6 span.
- **Market Scanner, Strategy Manager, Signal Engine, Scoring Engine, Risk Manager implementations** —
  zero files modified by the Execution Engine session (verified via the Phase 6.6 commit's own file
  list: every changed/added file is under `ai_trader/execution_engine/` or a repo-root doc). Execution
  Engine only *imports* already-published types from Risk Manager/Signal Engine — never mutates them.
- **No broker code, no MT5, no live trading, no Simulation Framework, no Learning Engine, no ML** — none
  exist anywhere in the tree, per the CEO directive's standing exclusion list. Execution Engine's
  `BrokerAdapter` is a `Protocol` (an interface definition), not an integration.
- **Determinism preserved end-to-end**: no module reached from any of the six implemented engines'
  `engine.py` imports `time`/`random`; every engine's own `TestDeterminism` suite passes; decisions/
  orders within one batch are always processed in a fixed (rank or equivalent) order regardless of input
  order; `client_order_id`/`order_request_id` are pure functions of `decision_id`.

---

## 8. Technical debt and remaining risks (disclosed, not fixed — deliberate scope discipline)

1. **Real per-strategy `detect`/`generate_signal` logic does not exist.** `StrategyRuntimeHandle.api`
   (Signal Engine) raises `StrategyApiNotImplementedError` for every method except `required_context()`.
   Every real strategy's signal is currently `INVALID`/`CORRUPTED_OUTPUT` by design, so every real
   `OpportunityScore`/`RiskDecision`/order downstream is correspondingly `SKIP`/`DENY`/no-op too — proven
   fail-safe end-to-end, but it means **no module has ever been exercised against a genuine ALLOW
   produced by a real strategy's own logic** (only against fixture-forced ALLOW decisions built through
   the real Risk Manager). This remains open, out of scope for Phases 6.1–6.6. It is a SEPARATE,
   not-yet-scoped task (interpreting the Strategy Library's natural-language entry/exit/stop
   specifications into executable rules) — raise it explicitly with the CEO; do not assume it is bundled
   into the Simulation Framework or any other phase.
2. **mypy --strict test-file gaps in Strategy Manager and Market Scanner** (98 errors, 16 files, all
   pre-existing, all `union-attr`/`type-arg`/`no-untyped-def` in test files, not source) — see §4.
   Disclosed, not fixed; out of scope for the Execution Engine session; a future cleanup task.
3. **Portfolio Manager is still not a real, separate module** — see §6. Resolved pragmatically for
   Execution Engine by reusing Risk Manager's `PortfolioState`; the Simulation Framework's own Portfolio
   Simulator will need to either continue that pattern or formalize a genuinely shared type. Flag this
   explicitly at the start of that work rather than silently re-deciding it a third time.
4. **`BrokerAdapter`'s exact relationship to `EXECUTION_SIMULATOR.md`'s own documented contract is
   unverified.** Execution Engine designed its own `Protocol` shape (an IMPLEMENTATION CHOICE, since the
   architecture only describes the concept in prose) — check whether the Simulation Framework's own
   frozen docs describe something compatible before assuming the Execution Simulator can just implement
   this exact Protocol unmodified.
5. **Large-scale Market Scanner benchmark** — resolved and closed (§10 below), included here only so a
   future session doesn't need to re-discover that it WAS resolved, not still open.

---

## 9. Non-negotiable rules (standing CEO directives — apply to every future session)

- **No shortcuts.** No prototype/demo code presented as production code.
- **No fake benchmarks.** A benchmark that didn't finish is not a result — report it as incomplete.
  Never estimate/extrapolate a number and present it as measured.
- **No fabricated statistics.** Every number in any report must come from an actual, reproducible run.
  If a number can't be reproduced or the run didn't finish, say so explicitly.
- **No hidden redesign.** Architecture documents (the `*_ARCHITECTURE.md`, `*_SCHEMA.json`, `*_API.md`
  files) are the frozen specification once approved. Implementation follows them; it does not quietly
  change them. (Bug fixes to actual code defects are not redesign — e.g. Execution Engine's duplicate-
  guard-before-validate reordering fixed a genuine correctness bug, it didn't redesign the architecture.)
- **No touching frozen Research Lab artifacts** — verified 0-diff at every commit so far (§3/§7); keep
  doing this at every future commit too (`git diff cef57c1~1 HEAD -- code/ results/ knowledge/` should
  stay empty).
- **Simulation before broker.** No Broker Adapter, no MetaTrader integration, no live execution until
  the Simulation Framework is implemented and has demonstrated profitable, robust portfolio management
  across many historical runs.
- **Broker only after simulation is profitable.** Not merely "implemented" — profitable, per the CEO's
  own words.
- **Documentation before implementation.** Every module gets its full architecture (README, ARCHITECTURE,
  API, SEQUENCE, STATE_MACHINE, and any relevant SCHEMA.json) approved before a single line of
  implementation code is written. Simulation Framework's docs are already complete — this gate is
  already satisfied for the next phase.
- **Implementation before optimization.** Get it correct and tested first; only optimize when a real,
  measured problem is found.
- **Everything versioned.** Every schema has an explicit version field baked into every emitted object.
- **Everything deterministic.** No wall-clock in business logic, no unseeded randomness, fixed iteration
  order where it could otherwise vary. This will matter MORE for the Simulation Framework than any prior
  module — a backtest that isn't perfectly reproducible given the same inputs is close to worthless.
- **Everything reproducible.** A given input (bars + config + versions) must always produce the same
  output.
- **Fix ONLY critical issues when told to.** When a validation/audit task says "fix only critical
  issues," that is a scope discipline, not laziness.
- **Independent adversarial code review is mandatory** before any module is declared READY (§6). This
  has never once come back clean — budget time for it and for fixing what it finds.
- **Stop and wait for explicit CEO approval** between every phase. Do not self-authorize moving to the
  next module, to Learning Engine, to Broker Adapter/MT5, or to opening the holdout.

---

## 10. Lessons learned across all six implemented modules (do not re-discover these from scratch)

### Performance
- **`jsonschema.Draft202012Validator.iter_errors()` is too slow for any hot path called once per
  event/bar/opportunity/order.** It re-resolves `$ref`s on every call. `fastjsonschema.compile(schema)`
  solves this (measured 10.3x speedup on Market Scanner). Keep `jsonschema` only for one-time startup
  shape-sanity checks. Every implemented module follows this pattern; the Simulation Framework should too.
- **`tracemalloc.start()` around a hot loop is not free and its cost is non-linear** — invisible at
  small/medium scale, catastrophic at large scale (a cliff, not a gradual slowdown). Default memory
  profiling to OFF with an explicit opt-in flag and a documented safe-scale ceiling. **This will matter
  for the Simulation Framework** if any large-scale historical backtest run needs profiling.
- **`cProfile` adds enormous overhead to code with millions of tiny function calls** — always cross-check
  profiler-derived conclusions against a real, unprofiled timing measurement.

### Process discipline
- **An independent, fresh-eyes adversarial code review (a subagent with no memory of writing the code)
  finds real issues the implementer misses, every single time it has been run** (§6). Non-negotiable.
- **Verify EVERY claimed finding independently before acting** — don't trust an audit's claims at face
  value, even a careful one. Execution Engine's own review self-verification confirmed all 7 findings
  were real by reading the exact source lines before fixing anything.
- **Sibling-entry-point inconsistency is now a KNOWN, RECURRING failure mode** (§6) — design the shared
  safety helper FIRST, not after review finds the gap.
- **Prose ordering in a frozen doc is not always execution-order-correct** (§6, new this session) —
  reason about causal necessity, not list position.
- **Test-design traps compound across engines**: tuning one upstream engine's "obvious" knob does not
  reliably control a downstream engine's threshold check, because intermediate engines have their own
  neutral-default fallbacks. Force the exact field under test directly via `dataclasses.replace` with a
  comment explaining why the naive cross-engine approach doesn't work (Risk Manager's
  `make_below_floor_opportunity()`; Execution Engine's `make_reduce_only_allow_decision()`).
- **A missing-data signal and a "the world was legitimately closed" signal look identical from inside a
  bar feed alone** — never infer a semantic fact purely from an absence-of-data pattern; disclose the
  absence, don't invent an explanation for it (Market Scanner's `calendar_engine.py` lesson).
- **Committing verified, tested fixes before writing a handoff document** (never leaving them as
  uncommitted working-tree changes) — followed at every phase close, including this one.

### Architectural decisions reaffirmed across modules
- **Streaming, incremental, pure-Python computation** (no pandas/numpy at runtime) chosen for the
  Market Scanner so it can process one bar at a time with bounded state.
- **Derived properties over stored redundant state** — Risk Manager's `PortfolioState.drawdown_pct` /
  `daily_pnl_pct` / `portfolio_risk_pct` / `leverage` are always computed from equity/positions, never
  stored fields. Execution Engine's `OrderRecord.remaining_qty` follows the same principle (derived from
  `quantity`/`filled_qty`, never stored).
- **Gap-fill types documented as IMPLEMENTATION CHOICE, never silently redesigned** — the consistent
  pattern across every module when a frozen doc names an input without fully specifying it (§6).
- **A pull-based (query), never push-based (event/callback), boundary to an external/future system** —
  Execution Engine's `BrokerAdapter` Protocol and its own Reconciler are built entirely around
  synchronous queries (`query_status`, `query_open_orders`), matching `EXECUTION_SEQUENCE.md`'s own
  prose exactly and avoiding the complexity of an async event system in a v1 with no real venue yet.

---

## 11. Exact first task of the next session

1. **Ask the CEO for explicit approval to begin Simulation Framework implementation** — a READY verdict
   on Execution Engine does not self-authorize starting the next phase (§9: "stop and wait for explicit
   CEO approval between every phase"). This is the one open gate.
2. **Once approved, re-read all of `ai_trader/simulation/`'s frozen docs in full first**: README,
   ARCHITECTURE, PORTFOLIO_SIMULATOR.md, EXECUTION_SIMULATOR.md, PERFORMANCE_ANALYZER.md, CONTEXT.md,
   API, SEQUENCE, STATE_MACHINE, SIMULATION_SCHEMA.json — there is no dedicated `_HANDOFF.md` for this
   phase yet (unlike Execution Engine's), so budget time to build that same level of understanding
   directly from the frozen docs, or write one first if the scope justifies it.
3. **Before writing any code, resolve explicitly (and document as IMPLEMENTATION CHOICE) §6/§8 item 3**
   (Portfolio Manager / shared `PortfolioState` type) and **§8 item 4** (whether `EXECUTION_SIMULATOR.md`
   names a `BrokerAdapter`-compatible contract or something different) — do not silently assume either.
4. **Build strictly against the frozen Simulation Framework docs** — no redesign, following the exact
   same "production-quality: types, tests, mypy strict, docstrings, deterministic, logging, config
   objects" bar every prior module was held to, including a mandatory independent adversarial
   code-review pass before declaring it READY. Pay special attention to the sibling-entry-point and
   prose-vs-execution-order lessons from §6/§10 — they are the two most likely recurring bug classes.
5. **Do NOT start Learning Engine, Broker Adapter, or MT5 integration** — all remain explicitly not
   authorized until the Simulation Framework is READY, has demonstrated profitable/robust portfolio
   management across many historical runs, and the CEO grants the next approval.
6. **Follow the exact validation-report template** (§5) and update `NEXT_SESSION.md`/`CHANGELOG.md`
   again at the end of that phase, exactly as done for every phase so far.

---

*Prior-session narrative history (Market Scanner large-scale-benchmark investigation, the two-concurrent-
sessions incident, the tracemalloc cliff discovery, etc.) has been condensed into §10 above across
several rewrites of this document. The full blow-by-blow account remains available in git history and in
`MARKET_SCANNER_VALIDATION_REPORT.md` for anyone who needs the original detail; it is intentionally not
reproduced verbatim here to keep this handoff a usable entry point rather than an archive.*
