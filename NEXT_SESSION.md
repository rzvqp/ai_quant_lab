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
✓ Risk Manager     READY   (Phase 6.5)   ← just closed

Next: Phase 6.6 — Execution Engine implementation. NOT STARTED. Requires explicit new CEO approval
      before writing any code. Full pre-read handoff: EXECUTION_ENGINE_HANDOFF.md (repo root).

Branch: ai-trader-implementation   HEAD: 7c225d1   Working tree: CLEAN
Full ai_trader/ suite: 967 tests passing · mypy --strict clean (75 source files, 5 modules) ·
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
  Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine**, plus a **Simulation
  Framework** that runs this exact same pipeline against historical data with a virtual broker/account instead
  of a real one.

**CEO-mandated sequencing (current, standing directive):** the AI Trader must first become a **complete,
deterministic backtesting/simulation engine** and prove profitability over historical data. **Only after
simulation proves profitable does Broker Adapter / MetaTrader / live execution work begin** (that is Phase 8+,
not authorized now). Within that, the CEO also pivoted from "architecture only" to "implement for real,
production-quality code" starting with Market Scanner (Phase 6.1) and now through Risk Manager (Phase 6.5).

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
| Execution Engine docs | `ai_trader/execution_engine/` (README, EXECUTION_ENGINE_ARCHITECTURE.md, ORDER_LIFECYCLE.md, ORDER_SCHEMA.json, EXECUTION_API.md, EXECUTION_SEQUENCE.md, EXECUTION_STATE_MACHINE.md, EXECUTION_FAILURE_POLICY.md) | **DONE** (Phase 5.6) — **NOT implemented yet — this is next (Phase 6.6)** |
| Simulation Framework docs | `ai_trader/simulation/` (README, ARCHITECTURE, PORTFOLIO_SIMULATOR.md, EXECUTION_SIMULATOR.md, PERFORMANCE_ANALYZER.md, CONTEXT.md, API, SEQUENCE, STATE_MACHINE, SIMULATION_SCHEMA.json) | **DONE** (post Phase 5.6 pivot) — **NOT implemented yet** |

### 2b. Implementations (production code)

| module | location | status |
|---|---|---|
| Market Scanner | `ai_trader/market_scanner/*.py` + `adapters/` + `tests/` | **READY** (Phase 6.1, `MARKET_SCANNER_VALIDATION_REPORT.md`). 127 tests. 2 critical bugs found+fixed by adversarial review. Large-scale benchmark completed + root-caused (harness `tracemalloc` artifact, not a scanner defect). |
| Strategy Manager | `ai_trader/strategy_manager/*.py` + `tests/` | **READY** (Phase 6.2, `STRATEGY_MANAGER_VALIDATION_REPORT.md`). 16 source modules, 251 tests, mypy --strict clean, 99% coverage. Adversarial review found 6 real bugs, all fixed. |
| Signal Engine | `ai_trader/signal_engine/*.py` + `tests/` | **READY** (Phase 6.3, `SIGNAL_ENGINE_VALIDATION_REPORT.md`). 10 source modules, 181 tests, mypy --strict clean, 99% coverage. Adversarial review found 5 real bugs + 1 real gap (all fixed), 1 finding confirmed correct-as-designed. |
| Scoring Engine | `ai_trader/scoring_engine/*.py` + `tests/` | **READY** (Phase 6.4, `SCORING_ENGINE_VALIDATION_REPORT.md`). 13 source modules, 199 tests, mypy --strict clean, 98% coverage. Adversarial review found 4 real bugs (2 CRITICAL, 1 HIGH, 1 MEDIUM), all fixed. |
| **Risk Manager** | `ai_trader/risk_manager/*.py` + `tests/` | **READY** (Phase 6.5, `RISK_MANAGER_VALIDATION_REPORT.md`). 13 source modules, 209 tests, mypy --strict clean, **99% coverage (`engine.py` itself 100%)**. Adversarial review found **8 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW)**, all fixed + regression-tested. **Just closed this session.** |
| Execution Engine | `ai_trader/execution_engine/` | **NOT implemented** — docs only. **Phase 6.6, next.** Pre-read: `EXECUTION_ENGINE_HANDOFF.md`. |
| Simulation Framework | `ai_trader/simulation/` | **NOT implemented** — docs only. |
| Portfolio Manager | *(no directory exists)* | **NOT DESIGNED** — see §6 "Portfolio Manager gap" below; important open item for Execution Engine. |
| Learning Engine | *(no directory exists)* | **NOT DESIGNED, NOT STARTED.** |
| Broker Adapter / MT5 Integration | *(no directory exists)* | **NOT AUTHORIZED** — explicitly gated on simulation proving profitable first. |

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
     detect/generate_signal logic yet, see §6)
   → OpportunityScore (Scoring Engine — degrades every real signal to a classified SKIP/INVALID score,
     proven fail-safe end-to-end by test_engine_integration.py)
   → RiskDecision (Risk Manager — degrades every SKIP/INVALID opportunity to a classified DENY,
     proven fail-safe end-to-end by test_engine_integration.py)
   → [Execution Engine — NOT YET BUILT — this is the next link in the chain]
```
The pipeline is fully wired and fail-safe end-to-end for today's "every real strategy signal is
INVALID" state; it has never yet produced (or needed to handle) a real ALLOW decision flowing into an
Execution Engine, because that module doesn't exist yet. This is expected and by design (see §6).

---

## 3. Current git state

**Branch:** `ai-trader-implementation`
**HEAD commit:** `7c225d1` — "Phase 6.5: implement Risk Manager v1, adversarially reviewed, READY"
**Working tree:** CLEAN (`git status --porcelain` returns nothing) — verified at close time.

All branches, in chronological order (oldest → newest), with their HEAD commit at handoff time:

| # | branch | HEAD commit | what it contains |
|---|---|---|---|
| 1 | `master` | `1bc0ffb` | Research Lab baseline (S1–S20 campaign, engine v2) |
| 2 | `strategy-development` | `0d776ec` | S1–S20 dedup registry + S21–S40 design library |
| 3 | `research-main` | `7afbd3b` | Consolidated Research Lab, S1–S51, matched-null, Wave 1 EXECUTED |
| 4 | `ai-trader-implementation` | `7c225d1` | **Current.** Strategy Library, Strategy Interface, AI Trader architecture (Phases 5.1–5.6 + Simulation), Market Scanner/Strategy Manager/Signal Engine/Scoring Engine/Risk Manager implementations (Phases 6.1–6.5), all READY |

Last 8 commits on `ai-trader-implementation` (newest first):
```
7c225d1 Phase 6.5: implement Risk Manager v1, adversarially reviewed, READY
7825726 Phase 6.4: Scoring Engine v1 implementation, adversarially reviewed, READY
19069f4 Phase 6.3: Signal Engine v1 implementation, adversarially reviewed, READY
ceb50b5 Deep-validation addendum: Market Scanner CPU profile, memory, parity vs frozen engine
b62288e Phase 6.2: Strategy Manager v1 implementation, adversarially reviewed, READY
526a921 Phase 6.1 RESOLUTION: root-cause Market Scanner large-scale benchmark, verdict READY
f61edfb CORRECTION: retract unconfirmed "super-linear benchmark slowdown" claim in NEXT_SESSION.md
14bef43 END OF SESSION: official handoff (NEXT_SESSION.md) for context-limit close
```

**Protected-path 0-diff verification (re-run this session, not assumed):**
```
git diff cef57c1~1 HEAD -- code/ results/ knowledge/
```
returns **empty** — `cef57c1` is the commit that started Phase 6.1 (Market Scanner implementation, the
first AI Trader production code). Nothing under `code/`, `results/`, or `knowledge/` has changed across
the entire Phase 6.1→6.5 implementation span. (Note: comparing against the much older `master`/`1bc0ffb`
baseline instead is NOT the right check — it would show the legitimate, pre-Phase-6.1 Strategy Library
build (`code/build_strategy_library.py`, `knowledge/strategies/`) as a "diff," which is expected,
documented history, not a violation. Always diff from `cef57c1~1` forward.)

---

## 4. Testing, coverage, and type-checking statistics (verified this session)

```
pytest ai_trader/ -q
967 passed in ~4.3s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine \
              ai_trader/scoring_engine ai_trader/risk_manager --exclude 'tests/'
Success: no issues found in 75 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   4893 stmts   255 miss   95%
```

Per-module test counts (sum to 967): Market Scanner 127, Strategy Manager 251, Signal Engine 181,
Scoring Engine 199, Risk Manager 209.

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
| Risk Manager | **99% (`engine.py` 100%)** | clean | remaining gaps: 2 lines in `pipeline.py` (an unreachable `Direction.NONE` branch), 6 lines in `schema_validation.py` (file-missing/corrupt-JSON/compile-failure environment paths) |

`mypy --strict` across the FULL `ai_trader/` tree (including every module's own `tests/` package) shows
98 pre-existing errors in 16 files — **all** in Strategy Manager's and Market Scanner's own test files
(`union-attr` on `NotFound`/`TimeframeWindow | None` narrowing, a couple of `type-arg`/`no-untyped-def`
gaps). These predate the Risk Manager session, are outside its scope, and were NOT touched. Each
module's own validation report scopes its "mypy --strict clean" claim to that module's source + its own
tests; the cross-module combined run above intentionally excludes `tests/` for exactly this reason.
**This is a known, disclosed item for a future cleanup pass — not a Risk Manager regression, not
blocking Phase 6.6.**

---

## 5. Validation reports (one per implemented module, repo root)

| report | module | verdict |
|---|---|---|
| `MARKET_SCANNER_VALIDATION_REPORT.md` | Market Scanner | READY |
| `STRATEGY_MANAGER_VALIDATION_REPORT.md` | Strategy Manager | READY |
| `SIGNAL_ENGINE_VALIDATION_REPORT.md` | Signal Engine | READY |
| `SCORING_ENGINE_VALIDATION_REPORT.md` | Scoring Engine | READY |
| `RISK_MANAGER_VALIDATION_REPORT.md` | Risk Manager | READY |
| `EXECUTION_ENGINE_HANDOFF.md` | Execution Engine | *(pre-implementation handoff, not a validation report — nothing to validate yet)* |

Every validation report follows the identical, mandatory template established at Phase 6.1 and held to
every phase since: what was built → design decisions (gap-fills, marked "IMPLEMENTATION CHOICE") →
independent adversarial review findings + fixes → final test/mypy/coverage numbers → protected-invariant
confirmation → verdict. Follow this exact template for Execution Engine's own report at the end of
Phase 6.6.

---

## 6. Important design decisions and open items to carry forward

- **Portfolio Manager gap.** `EXECUTION_ENGINE_ARCHITECTURE.md` names a `Portfolio Manager` module as a
  required upstream/read dependency (`PortfolioState`, fill reporting) — but **no such module exists,
  is designed, or is scheduled**. The Risk Manager already solved an analogous problem: it designed and
  owns its own `PortfolioState`/`OpenPosition`/`ClosedPosition` types (`ai_trader/risk_manager/types.py`)
  as a documented "IMPLEMENTATION CHOICE" gap-fill, since no canonical schema existed for them either.
  **Execution Engine will face the identical decision** — whether to import/reuse
  `ai_trader.risk_manager.types.PortfolioState` (Risk Manager IS an allowed direct dependency per the
  Execution Engine's own interaction matrix) or to define its own analogous type. This is an open design
  question for Phase 6.6, not resolved by this session, and should be raised with the CEO or decided
  explicitly (and documented as an IMPLEMENTATION CHOICE) at the start of that implementation — see
  `EXECUTION_ENGINE_HANDOFF.md` for the full analysis.
- **Broker Adapter is abstract-only in v1.** Every Execution Engine doc is explicit that v1 documents
  and implements the Broker Adapter *contract* (an interface/capabilities profile), never a real venue
  integration. Phase 6.6 should build the Execution Engine against a fake/test double implementing that
  contract, exactly as the Risk Manager was tested against real `OpportunityScore`s from a real Scoring
  Engine rather than a live broker.
- **`fastjsonschema` from the start.** Every implemented module's hot-path schema validation uses
  `fastjsonschema` (compiled once) for the hot path and `jsonschema` only for one-time startup
  shape-sanity checks — a lesson learned expensively during Market Scanner (Phase 6.1, §10 below) and
  followed correctly by all four subsequent modules. `ORDER_SCHEMA.json` exists and is ready for the
  same pattern.
- **The independent adversarial-review technique is now mandatory, not optional.** It has found real
  bugs in all five implemented modules: 2 (Market Scanner), 6 (Strategy Manager), 5+1 (Signal Engine), 4
  (Scoring Engine), 8 (Risk Manager) — 26 real issues total, zero false-negative sessions. Run it (a
  fresh-eyes subagent with no memory of writing the code, reading every frozen spec doc in full then
  every source file, hunting for policy/formula deviations, fail-safe violations, determinism
  violations, and — the newest lesson, see below — sibling-entry-point inconsistency) before declaring
  Execution Engine READY.
- **New lesson from Risk Manager's review, generalize it to Execution Engine:** when a module's public
  API has more than one entry point that can independently produce the same kind of output (Risk
  Manager had `evaluate()`'s batch loop AND `allow_trade()`'s single-opportunity path, plus a
  degraded-input branch inside `evaluate()`), verify EVERY entry point routes through the SAME
  validation/reassembly/exception-safety helper. 3 of Risk Manager's 8 findings were exactly this class
  of bug: one path got the safety net, a sibling path didn't. Execution Engine's API
  (`execute`/`build_order`/`cancel`/`reconcile`/`emergency_flatten`) has FIVE entry points that can each
  independently touch the Order Ledger — this class of bug is a strong candidate to recur; design a
  single shared internal helper for order-state mutation + validation from the start, and have the
  adversarial review check every entry point against it explicitly.
- **Gap-fill pattern, reaffirmed every phase:** when a frozen spec names an input/output without fully
  specifying its mechanism (Scoring Engine's `risk_penalty` weights, Risk Manager's `correlation_groups`
  and `per_strategy_cooldown_bars`), fill it with an explicit, documented, honesty/safety-preserving
  default and mark it "IMPLEMENTATION CHOICE" in the source — never silently redesign, never leave it
  unstated. Execution Engine's `ConstraintDefaults`-equivalent numeric placeholders (retry bounds, rate
  limits, reconciliation timeouts — none fixed by the docs) will need the same treatment.

---

## 7. Protected invariants — confirmed untouched (verified this session)

- **Research Lab** (`code/`, `results/`, `data/`), **Strategy Library** (`knowledge/strategies/`),
  **Strategy Interface v1** (`knowledge/interface/`) — read-only; 0-diff confirmed via
  `git diff cef57c1~1 HEAD -- code/ results/ knowledge/` (empty), covering the entire Phase 6.1–6.5 span.
- **Market Scanner, Strategy Manager, Signal Engine, Scoring Engine implementations** — zero files
  modified by the Risk Manager session (verified via the Phase 6.5 commit's own file list: every
  changed/added file is under `ai_trader/risk_manager/` or a repo-root doc). Risk Manager only *imports*
  already-published types from Scoring Engine/Signal Engine/Market Scanner — never mutates them.
- **No broker code, no MT5, no live trading, no Execution Engine, no Simulation, no Learning Engine, no
  ML** — none exist anywhere in the tree, per the CEO directive's standing exclusion list.
- **Determinism preserved end-to-end**: no module reached from any of the five implemented engines'
  `engine.py` imports `time`/`random`; every engine's own `TestDeterminism` suite passes; opportunities/
  decisions within one batch are always processed in a fixed (rank or equivalent) order regardless of
  input order.

---

## 8. Technical debt and remaining risks (disclosed, not fixed — deliberate scope discipline)

1. **Real per-strategy `detect`/`generate_signal` logic does not exist.** `StrategyRuntimeHandle.api`
   (Signal Engine) raises `StrategyApiNotImplementedError` for every method except `required_context()`.
   Every real strategy's signal is currently `INVALID`/`CORRUPTED_OUTPUT` by design, so every real
   `OpportunityScore`/`RiskDecision` downstream is correspondingly `SKIP`/`DENY` too — proven fail-safe
   end-to-end, but it means **no module has ever been exercised against a genuine ALLOW flowing all the
   way through from a real strategy.** This was explicitly out of scope for Phases 6.1–6.5 and remains
   open. It is a SEPARATE, not-yet-scoped task (interpreting the Strategy Library's natural-language
   entry/exit/stop specifications into executable rules) — raise it explicitly with the CEO; do not
   assume it is bundled into Execution Engine or any other phase.
2. **mypy --strict test-file gaps in Strategy Manager and Market Scanner** (98 errors, 16 files, all
   pre-existing, all `union-attr`/`type-arg`/`no-untyped-def` in test files, not source) — see §4.
   Disclosed, not fixed; out of scope for the Risk Manager session; a future cleanup task.
3. **Portfolio Manager is undesigned** — see §6. Execution Engine implementation cannot fully start
   without resolving this (either reuse Risk Manager's `PortfolioState` type or design a new one) —
   flag this explicitly at the start of Phase 6.6 rather than silently picking one.
4. **`RiskDecision.constraints`/`sizing` → `OrderRequest` mapping has policy choices the architecture
   names but does not fully pin down** (§`ORDER_LIFECYCLE.md` §6: "Mapping RiskDecision → order type
   (default policy)" — Market vs. Limit vs. Stop selection based on "entry price ≈ current market" has
   no numeric threshold for "≈"). This will need an explicit, documented IMPLEMENTATION CHOICE default
   during Phase 6.6, exactly like every prior module's own gap-fills.
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
  change them. (Bug fixes to actual code defects are not redesign.)
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
  implementation code is written. Execution Engine's docs are already complete (Phase 5.6) — this gate
  is already satisfied for Phase 6.6.
- **Implementation before optimization.** Get it correct and tested first; only optimize when a real,
  measured problem is found.
- **Everything versioned.** Every schema has an explicit version field baked into every emitted object
  (`order_schema_version`, `execution_engine_version`, etc. already defined in `ORDER_SCHEMA.json`).
- **Everything deterministic.** No wall-clock in business logic, no unseeded randomness, fixed iteration
  order where it could otherwise vary. `EXECUTION_ENGINE_ARCHITECTURE.md` §11 already states order
  *construction/validation* must be deterministic (order *outcomes* depend on the future venue and are
  not — but must always reconcile to a definite state).
- **Everything reproducible.** A given input (bars + config + versions) must always produce the same
  output.
- **Fix ONLY critical issues when told to.** When a validation/audit task says "fix only critical
  issues," that is a scope discipline, not laziness.
- **Independent adversarial code review is mandatory** before any module is declared READY (§6). This
  has never once come back clean — budget time for it and for fixing what it finds.
- **Stop and wait for explicit CEO approval** between every phase. Do not self-authorize moving to the
  next module, to Simulation, to Learning Engine, to Broker Adapter/MT5, or to opening the holdout.

---

## 10. Lessons learned across all five implemented modules (do not re-discover these from scratch)

### Performance
- **`jsonschema.Draft202012Validator.iter_errors()` is too slow for any hot path called once per
  event/bar/opportunity.** It re-resolves `$ref`s on every call. `fastjsonschema.compile(schema)` solves
  this (measured 10.3x speedup on Market Scanner). Keep `jsonschema` only for one-time startup
  shape-sanity checks. Every implemented module (Market Scanner, Strategy Manager, Signal Engine,
  Scoring Engine, Risk Manager) follows this pattern; Execution Engine should too from the start.
- **`tracemalloc.start()` around a hot loop is not free and its cost is non-linear** — invisible at
  small/medium scale, catastrophic at large scale (a cliff, not a gradual slowdown). Default memory
  profiling to OFF with an explicit opt-in flag and a documented safe-scale ceiling.
- **`cProfile` adds enormous overhead to code with millions of tiny function calls** — always cross-check
  profiler-derived conclusions against a real, unprofiled timing measurement.

### Process discipline
- **An independent, fresh-eyes adversarial code review (a subagent with no memory of writing the code)
  finds real issues the implementer misses, every single time it has been run** (§6). Non-negotiable.
- **Verify EVERY claimed finding independently before acting** — don't trust an audit's claims at face
  value, even a careful one.
- **When a module's public API has multiple entry points that can produce the same kind of output,
  verify they all route through the same safety/validation helper** — the newest, most generalizable
  lesson, from Risk Manager's review (§6). Directly relevant to Execution Engine's 5-entry-point API.
- **Test-design traps compound across engines**: tuning one upstream engine's "obvious" knob
  (`signal_strength`) does not reliably control a downstream engine's threshold check, because
  intermediate engines have their own neutral-default fallbacks. When a test needs a specific
  downstream state, force it directly via `dataclasses.replace` on the exact field under test, with a
  comment explaining why the naive cross-engine approach doesn't work (see Risk Manager's
  `make_below_floor_opportunity()`).
- **A missing-data signal and a "the world was legitimately closed" signal look identical from inside a
  bar feed alone** — never infer a semantic fact purely from an absence-of-data pattern; disclose the
  absence, don't invent an explanation for it (Market Scanner's `calendar_engine.py` lesson).
- **Committing verified, tested fixes before writing a handoff document** (never leaving them as
  uncommitted working-tree changes) — followed at every phase close, including this one.
- **When monitoring a long-running background task, verify you are watching the SAME process the task
  tracker is tracking** — a rising CPU number from an unrelated/orphaned process proves nothing about
  the tracked run (Market Scanner Phase 6.1 large-scale-benchmark lesson).

### Architectural decisions reaffirmed across modules
- **Streaming, incremental, pure-Python computation** (no pandas/numpy at runtime) chosen for the
  Market Scanner so it can process one bar at a time with bounded state — appropriate for both live and
  replay use.
- **Derived properties over stored redundant state** — Risk Manager's `PortfolioState.drawdown_pct` /
  `daily_pnl_pct` / `portfolio_risk_pct` / `leverage` are always computed from equity/positions, never
  stored fields, eliminating a whole class of stale-derived-value bug by construction. Apply the same
  principle to Execution Engine's Order Ledger where possible.
- **Gap-fill types documented as IMPLEMENTATION CHOICE, never silently redesigned** — the consistent
  pattern across every module when a frozen doc names an input without fully specifying it (§6).

---

## 11. Exact first task of the next session

1. **Read `EXECUTION_ENGINE_HANDOFF.md` (repo root) in full first** — it is the dedicated, complete
   pre-implementation briefing for Phase 6.6, built this session specifically so the next session does
   not need to re-derive it from the raw architecture docs.
2. **Ask the CEO for explicit approval to begin Execution Engine implementation (Phase 6.6)** — a READY
   verdict on Risk Manager does not self-authorize starting the next module (§9: "stop and wait for
   explicit CEO approval between every phase"). This is the one open gate.
3. **Once approved**, resolve the Portfolio Manager gap explicitly first (§6/§8 item 3) — decide
   (and document as an IMPLEMENTATION CHOICE) whether to reuse `ai_trader.risk_manager.types.PortfolioState`
   or design a new type, before writing the Order Builder.
4. **Build the Execution Engine strictly against `ai_trader/execution_engine/`'s existing, frozen
   architecture docs** — no redesign, following the exact same "production-quality: types, tests, mypy
   strict, docstrings, deterministic, logging, config objects" bar every prior module was held to,
   including a mandatory independent adversarial code-review pass before declaring it READY.
5. **Do NOT start Simulation Framework, Learning Engine, Broker Adapter, or MT5 integration** — all
   remain explicitly not authorized until Execution Engine is READY and the CEO grants the next approval.
6. **Follow the exact validation-report template** (§5) and update `NEXT_SESSION.md`/`CHANGELOG.md`
   again at the end of Phase 6.6, exactly as done for every phase so far.

---

*Prior-session narrative history (Market Scanner large-scale-benchmark investigation, the two-concurrent-
sessions incident, the tracemalloc cliff discovery, etc.) has been condensed into §10 above. The full
blow-by-blow account of those investigations remains available in git history (commits `f61edfb` through
`526a921`) and in `MARKET_SCANNER_VALIDATION_REPORT.md` for anyone who needs the original detail; it is
intentionally not reproduced verbatim here to keep this handoff a usable entry point rather than an
archive.*
