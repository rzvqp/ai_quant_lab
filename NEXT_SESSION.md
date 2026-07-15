# NEXT_SESSION.md — Official Handoff (AI Trader Implementation Phase)

**Official session-close document, rewritten in full on 2026-07-15 per explicit CEO directive, after
Phase 6.6 (Execution Engine) reached READY.** This document is the single source of truth for the next
Claude session. It is self-contained: a brand-new session must be able to continue correctly from this
file alone, without reading any prior conversation, without any fact surviving only in Claude's memory,
and without any fact surviving only in a stale Codex/other-tool sandbox. Every fact below was verified
directly against `git log`/`git status`/`git diff`/a live `pytest`+`mypy`+`coverage` run at close time —
nothing here is assumed or carried over unverified.

---

## A. Project mission

**AI Quant Research Lab → AI Trader.** Two systems, physically separated by design:

- **Research Lab** (`code/`, `results/`, `knowledge/`) discovers and validates trading strategies against
  historical XAUUSD data through a falsification-first pipeline (engine → matched-null → Wave experiments
  → eventually global-FDR → walk-forward → terminal holdout). **Frozen and stable; never touched during
  AI Trader work** — verified 0-diff at every commit since Phase 6.1 began (§F).
- **Strategy Library** (`knowledge/strategies/`) publishes the Research Lab's output as **51 versioned,
  executable strategy contracts** (S1–S51), each with mechanism/entry/exit/stop/metrics/validation-status.
- **Strategy Interface v1** (`knowledge/interface/`) is the ONLY sanctioned contract between the Lab and
  the Trader: a versioned JSON Schema (`strategy_contract.v1.schema.json`) plus a runtime Strategy API
  (`STRATEGY_API_v1.md`). **The AI Trader consumes strategies ONLY through this interface** — never
  Research Lab internals directly.
- **AI Trader** (`ai_trader/`) is the execution system, built module-by-module. All six pipeline modules
  are now READY: **Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager →
  Execution Engine**. Next: a **Simulation Framework** that runs this exact same pipeline against
  historical data with a virtual broker/account instead of a real one.

**Simulation-first is mandatory (standing CEO directive, non-negotiable):** the AI Trader must first
become a complete, deterministic backtesting/simulation engine and prove **robust profitability** over
historical data. **No Broker Adapter, no MetaTrader/MT5 integration, and no live execution work begins
until that is demonstrated.** This is Phase 8+ territory and is explicitly NOT authorized now, nor by any
verdict reached in this or any prior session.

---

## B. Official Git state (verified this session, live)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD commit:      ad168b1  "Official session close after Phase 6.6: full handoff for Phase 6.7"
Working tree:     CLEAN (git status --porcelain returns nothing; verified, not assumed)
```

Important commit chain (newest → oldest, this branch):
```
ad168b1 Official session close after Phase 6.6: full handoff for Phase 6.7
3add548 Session close: Phase 6.6 Execution Engine documented, handoff updated
626e59d Phase 6.6: implement Execution Engine v1, adversarially reviewed, READY
6761e39 Official session close: Phase 6.5 complete, Phase 6.6 handoff prepared
7c225d1 Phase 6.5: implement Risk Manager v1, adversarially reviewed, READY
7825726 Phase 6.4: Scoring Engine v1 implementation, adversarially reviewed, READY
19069f4 Phase 6.3: Signal Engine v1 implementation, adversarially reviewed, READY
ceb50b5 Deep-validation addendum: Market Scanner CPU profile, memory, parity vs frozen engine
b62288e Phase 6.2: Strategy Manager v1 implementation, adversarially reviewed, READY
526a921 Phase 6.1 RESOLUTION: root-cause Market Scanner large-scale benchmark, verdict READY
```

All branches in the repo (oldest → newest by lineage):

| # | branch | HEAD commit | what it contains |
|---|---|---|---|
| 1 | `master` | `1bc0ffb` | Research Lab baseline (S1–S20 campaign, engine v2) |
| 2 | `strategy-development` | `0d776ec` | S1–S20 dedup registry + S21–S40 design library |
| 3 | `research-main` | `7afbd3b` | Consolidated Research Lab, S1–S51, matched-null, Wave 1 EXECUTED |
| 4 | `ai-trader-implementation` | `ad168b1` | **Current/active.** Strategy Library, Strategy Interface, AI Trader architecture (Phases 5.1–5.6 + Simulation docs), all 6 pipeline modules implemented (Phases 6.1–6.6), all READY, plus `SIMULATION_HANDOFF.md` for Phase 6.7 |

**No untracked or uncommitted files of any kind** (`git status -uall --porcelain` returns nothing,
verified this session).

---

## C. Completed implementation — every module, verified

All six pipeline modules are **READY**. Per-module detail (source-file counts, tests, coverage, mypy,
validation report, bugs found, known limitations):

### C1. Market Scanner (Phase 6.1)
- **Source:** `ai_trader/market_scanner/*.py` + `adapters/` (14 source files)
- **Tests:** 127 · **Coverage:** see `MARKET_SCANNER_VALIDATION_REPORT.md` (module's own benchmark
  script `benchmarks/bench_market_scanner.py` is intentionally excluded from the module's reported %,
  since it is a CLI tool never exercised by pytest, not a source defect)
- **mypy --strict:** clean
- **Validation report:** `MARKET_SCANNER_VALIDATION_REPORT.md`
- **Bugs found+fixed by adversarial review:** 2 (1 correctness, 1 performance — the
  `jsonschema`→`fastjsonschema` hot-path fix, 10.3x speedup)
- **Known limitations:** large-scale benchmark was root-caused (a `tracemalloc` measurement artifact,
  not a scanner defect) — resolved, not open.

### C2. Strategy Manager (Phase 6.2)
- **Source:** `ai_trader/strategy_manager/*.py` (16 source modules)
- **Tests:** 251 · **Coverage:** 99% · **mypy --strict:** clean
- **Validation report:** `STRATEGY_MANAGER_VALIDATION_REPORT.md`
- **Bugs found+fixed:** 6 real bugs (adversarial review)
- **Known limitations:** none outstanding beyond the pre-existing test-file mypy gaps noted in §G.

### C3. Signal Engine (Phase 6.3)
- **Source:** `ai_trader/signal_engine/*.py` (10 source modules)
- **Tests:** 181 · **Coverage:** 99% · **mypy --strict:** clean
- **Validation report:** `SIGNAL_ENGINE_VALIDATION_REPORT.md`
- **Bugs found+fixed:** 5 real bugs + 1 real gap (adversarial review); 1 finding confirmed
  correct-as-designed (not a bug)
- **Known limitations:** `StrategyRuntimeHandle.api` raises `StrategyApiNotImplementedError` for every
  method except `required_context()` — **no real per-strategy `detect`/`generate_signal` logic exists
  yet.** Every real strategy's signal is currently `INVALID`/`CORRUPTED_OUTPUT` by design (see §G item 1
  — still true, carried forward unchanged through Phase 6.6).

### C4. Scoring Engine (Phase 6.4)
- **Source:** `ai_trader/scoring_engine/*.py` (13 source modules)
- **Tests:** 199 · **Coverage:** 98% · **mypy --strict:** clean
- **Validation report:** `SCORING_ENGINE_VALIDATION_REPORT.md`
- **Bugs found+fixed:** 4 real bugs (2 CRITICAL, 1 HIGH, 1 MEDIUM — adversarial review)
- **Known limitations:** none outstanding.

### C5. Risk Manager (Phase 6.5)
- **Source:** `ai_trader/risk_manager/*.py` (13 source modules)
- **Tests:** 209 · **Coverage:** 99% (`engine.py` itself 100%) · **mypy --strict:** clean
- **Validation report:** `RISK_MANAGER_VALIDATION_REPORT.md`
- **Bugs found+fixed:** 8 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 2 LOW — adversarial review)
- **Known limitations:** **Portfolio Manager does not exist as a real, separate runtime module** — Risk
  Manager designed and owns its own `PortfolioState`/`OpenPosition`/`ClosedPosition`/`RiskContext` types
  as a documented IMPLEMENTATION CHOICE gap-fill (still true, see §G item 2).

### C6. Execution Engine (Phase 6.6 — just closed this session)
- **Source:** `ai_trader/execution_engine/*.py` (13 source modules: types, config, exceptions,
  schema_validation, broker_adapter, builder, validator, ledger, lifecycle, reconciler, pipeline,
  reporter, engine)
- **Tests:** 198 · **Coverage:** 99% (`builder.py`/`pipeline.py`/`reconciler.py` at 100%)
  **mypy --strict:** clean (31 files: 14 production + test package)
- **Validation report:** `EXECUTION_ENGINE_VALIDATION_REPORT.md`
- **Bugs found+fixed:** **7 real issues (2 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW — adversarial review)**:
  1. **CRITICAL** — the pipeline validated an order BEFORE checking the duplicate guard; a retry of an
     already-FILLED order evaluated against a since-changed `PortfolioState` could fail validation and
     silently overwrite the Ledger's terminal FILLED record with a bogus REJECTED. **Fixed**: duplicate
     guard now runs first, before validation.
  2. **CRITICAL** — the Reconciler and `engine.cancel()` had no exception handling around Broker Adapter
     calls, violating `EXECUTION_API.md`'s "never thrown across the boundary" contract; a broker
     exception during `shutdown()`'s draining reconciliation could propagate out of the public API.
     **Fixed**: every Broker Adapter call in `reconciler.py` is now exception-safe; `engine.cancel()`
     routes through a new `reconciler.request_cancel()` instead of calling the adapter directly.
  3. **HIGH** — `emergency_flatten()` silently no-op'd (empty report, no degraded signal) when called
     before any portfolio had ever been observed — dangerous for an emergency safety mechanism.
     **Fixed**: now marks the engine DEGRADED with an explicit reason.
  4. **MEDIUM** — the Order Validator had no "time restrictions" check at all despite the architecture
     naming one. **Fixed**: added a documented, partial (no-wall-clock) implementation.
  5. **MEDIUM** — an advisory broker-transition sanity-check function was written but never wired in.
     **Fixed**: now wired into `apply_broker_update()` as an advisory warning log.
  6. **MEDIUM** — `emergency_flatten()`'s build stage had no exception safety net even though its submit
     stage already did. **Fixed**: wrapped in the same `try/except` pattern.
  7. **LOW** — a broker reporting a fill without a price had that price silently fabricated as `0.0`.
     **Fixed**: falls back to the order's own `limit_price` first.
  All 7 fixed with dedicated regression tests; see `EXECUTION_ENGINE_VALIDATION_REPORT.md` §3 for the
  full table.
- **Known limitations:**
  - **Portfolio Manager gap resolved PRAGMATICALLY, not architecturally** — Execution Engine reuses
    `ai_trader.risk_manager.types.PortfolioState` directly (documented IMPLEMENTATION CHOICE #1). No real
    Portfolio Manager module exists anywhere in the repo. See §G item 2.
  - **`BrokerAdapter`'s relationship to the future Execution Simulator's own contract is UNVERIFIED.**
    Execution Engine designed its own abstract `Protocol` (`submit_order`/`cancel_order`/`query_status`/
    `query_open_orders`/`capabilities`) as an IMPLEMENTATION CHOICE, since the architecture only
    describes the concept in prose. Whether `EXECUTION_SIMULATOR.md` (Simulation Framework docs) names a
    compatible contract, an incompatible one, or something else entirely has NOT been checked. See §G
    item 3 — this is the single most important open question for the next phase.

---

## D. Full pipeline status

```
Market Scanner        READY  (Phase 6.1)
   → Strategy Manager  READY  (Phase 6.2)
      → Signal Engine  READY  (Phase 6.3)
         → Scoring Engine  READY  (Phase 6.4)
            → Risk Manager  READY  (Phase 6.5)
               → Execution Engine  READY  (Phase 6.6)
                  → Simulation Framework  [NEXT — NOT STARTED, Phase 6.7]
```

End-to-end proof status: the pipeline is fully wired and fail-safe end-to-end for the real-strategy
chain (every real strategy signal is currently `INVALID` by design → `SKIP`/`INVALID` score → `DENY`
decision → no-op `REJECTED` order status — never a crash anywhere, proven by every module's own
`test_engine_integration.py`). It has ALSO been proven end-to-end against a real, schema-valid **ALLOW**
`RiskDecision` (built via Risk Manager's own fixtures against a real Scoring Engine chain) — that
decision flows through the Execution Engine to a FILLED order against a fake (Protocol-conformant)
broker (`test_engine_integration.py::TestRealAllowDecisionFillsEndToEnd`). No module has yet been
exercised against a genuine ALLOW produced by a REAL strategy's own decision logic, because that logic
doesn't exist yet (§C3, §G item 1).

---

## E. Global implementation statistics (verified live this session)

```
pytest ai_trader/ -q
1165 passed in ~6.5s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine \
              ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine --exclude 'tests/'
Success: no issues found in 89 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   5805 stmts   266 miss   95%
```

- **Total tests:** 1165 (Market Scanner 127, Strategy Manager 251, Signal Engine 181, Scoring Engine 199,
  Risk Manager 209, Execution Engine 198)
- **Total production source files (6 modules, excluding tests):** 89 (`mypy --strict` clean across all)
- **Full-suite result:** 1165/1165 passing
- **Overall coverage:** 95% (pulled down by exactly one file:
  `ai_trader/market_scanner/benchmarks/bench_market_scanner.py`, a standalone CLI benchmark script never
  exercised by pytest — not a source-code defect; every module's OWN coverage is 98–100%)
- **mypy status:** clean across all 6 modules' production source. The FULL tree (including every
  module's own `tests/` package) shows 98 PRE-EXISTING errors in 16 files, all in Strategy Manager's and
  Market Scanner's own test files (`union-attr`/`type-arg`/`no-untyped-def`) — disclosed, not fixed, out
  of scope for every session since they were first found, a known future cleanup item (§G item 5).

---

## F. Protected invariants — confirmed untouched (verified this session, live)

- **Research Lab** (`code/`, `results/`, `data/`) — **FROZEN.**
- **S1–S51** (`knowledge/strategies/`, 51 folders confirmed present this session via direct directory
  listing) — **FROZEN.**
- **Wave 1** (`knowledge/experiments/WAVE_1_*`, confirmed present this session) — **FROZEN / EXECUTED,**
  not re-run.
- **Strategy Library** (`knowledge/strategies/` + `INDEX.md` + `library_manifest.json`) — **FROZEN.**
- **Strategy Interface v1** (`knowledge/interface/`) — **FROZEN.**
- **Knowledge Base / Ontology / Knowledge Graph** (`knowledge/` more broadly) — **FROZEN**, part of the
  same 0-diff guarantee below.
- **Terminal holdout** — **SEALED** (unchanged status; not touched by any AI Trader implementation work,
  consistent with the entire Phase 6.x effort never opening or referencing it).
- **0-diff verification** (re-run this session, live):
  ```
  git diff cef57c1~1 HEAD -- code/ results/ knowledge/
  ```
  returns **EMPTY** — `cef57c1` is the commit that started Phase 6.1 (Market Scanner implementation, the
  first AI Trader production code). Nothing under `code/`, `results/`, or `knowledge/` has changed across
  the entire Phase 6.1→6.6 implementation span, confirmed directly this session, not assumed.
- **No broker code, no MT5, no live trading** — none exist anywhere in the tree (verified: no
  `broker_adapter`/`mt5`/`learning_engine` directories exist outside the documented, abstract
  `ai_trader/execution_engine/broker_adapter.py` `Protocol`, which defines an INTERFACE only, never a
  venue integration).
- **Existing frozen module documentation** (every `*_ARCHITECTURE.md`/`*_SCHEMA.json`/`*_API.md` for all
  6 implemented modules, plus all 10 Simulation Framework docs) — unmodified by any implementation
  session; bug fixes changed only implementation code, never the frozen specification.

---

## G. Technical debt / known limitations (disclosed, not fixed — deliberate scope discipline)

1. **No real Strategy Signal implementation from the Strategy Library exists yet — STILL TRUE.**
   `StrategyRuntimeHandle.api` (Signal Engine) raises `StrategyApiNotImplementedError` for every method
   except `required_context()`. Every real strategy's signal is `INVALID`/`CORRUPTED_OUTPUT` by design,
   so every real `OpportunityScore`/`RiskDecision`/order downstream is correspondingly `SKIP`/`DENY`/
   no-op too — proven fail-safe end-to-end, but no module has ever been exercised against a genuine ALLOW
   produced by a real strategy's own logic (only against fixture-forced ALLOW decisions). This is a
   SEPARATE, not-yet-scoped task (interpreting the Strategy Library's natural-language entry/exit/stop
   specifications into executable rules) — raise it explicitly with the CEO; do not assume it is bundled
   into the Simulation Framework or any other phase.
2. **Portfolio Manager is NOT implemented as a separate runtime module.** Risk Manager designed its own
   `PortfolioState`/`OpenPosition`/`ClosedPosition`/`RiskContext` types; Execution Engine reuses Risk
   Manager's `PortfolioState` directly. Both are documented IMPLEMENTATION CHOICE gap-fills, not a real
   Portfolio Manager module. **The Simulation Framework's own Portfolio Simulator
   (`PORTFOLIO_SIMULATOR.md`) will face this exact question a third time** — resolve it explicitly at the
   start of that work (formalize a genuinely shared type, or continue the reuse pattern) rather than
   silently re-deciding it again.
3. **The relationship between `BrokerAdapter` and the future Execution Simulator's own contract requires
   verification.** Execution Engine's `broker_adapter.py` defines a pull-based `Protocol`
   (`submit_order`/`cancel_order`/`query_status`/`query_open_orders`/`capabilities`), an IMPLEMENTATION
   CHOICE since the architecture only describes the concept in prose. `EXECUTION_SIMULATOR.md` (part of
   the Simulation Framework's frozen docs) may name a compatible, incompatible, or entirely different
   contract — **this has not been checked** and must be the first thing verified before assuming the
   Execution Simulator can just implement this exact `Protocol` unmodified.
4. **`ORDER_LIFECYCLE.md` §6's "entry price ≈ current market" threshold has no live quote feed to
   evaluate against in v1** — Execution Engine's `builder.py` resolves this with a documented, fully
   deterministic default (marketable LIMIT at the decision's own entry, BRACKET whenever stop/target is
   present). Disclosed as an IMPLEMENTATION CHOICE, not a defect; carried forward for awareness only.
5. **mypy --strict test-file gaps in Strategy Manager and Market Scanner** (98 errors, 16 files, all
   pre-existing, all `union-attr`/`type-arg`/`no-untyped-def` in TEST files, not source) — disclosed
   every session since first found, not fixed, out of scope for every implementation phase so far, a
   future cleanup task whenever the CEO chooses to prioritize it.
6. **Large-scale Market Scanner benchmark** — resolved and closed (a `tracemalloc` measurement artifact,
   not a scanner defect). Included here only so a future session doesn't need to re-discover that it WAS
   resolved, not still open.

---

## H. Immediate next phase

**Phase 6.7 — Simulation Framework implementation.**
**Status: NOT STARTED. Requires explicit new CEO approval before any code is written.**

Components named by the frozen docs: Execution Simulator, Portfolio Simulator, Performance Analyzer,
plus simulation orchestration/context/config and an artifact/report writer. Full pre-implementation
briefing: **`SIMULATION_HANDOFF.md`** (repo root, written this session — read it in full before doing
anything else).

Do NOT begin implementation of: Simulation Framework, Learning Engine, Broker Adapter (a real one), or
MT5 integration, in this or any future session, without an explicit new CEO go-ahead for that specific
phase.

---

## I. Exact next-session order

1. **Read this document (`NEXT_SESSION.md`) in full first.**
2. **Verify Git branch/HEAD/clean tree directly** — do not trust this document's own git-state section
   blindly; re-run `git branch --show-current`, `git log -1`, `git status --porcelain` and confirm they
   still match §B (or note and report any drift — another session or the user may have acted since this
   was written).
3. **Read `SIMULATION_HANDOFF.md` (repo root) in full.**
4. **Read all frozen `ai_trader/simulation/` architecture documents in full**: `README.md`,
   `SIMULATION_ARCHITECTURE.md`, `PORTFOLIO_SIMULATOR.md`, `EXECUTION_SIMULATOR.md`,
   `PERFORMANCE_ANALYZER.md`, `SIMULATION_CONTEXT.md`, `SIMULATION_API.md`, `SIMULATION_SEQUENCE.md`,
   `SIMULATION_STATE_MACHINE.md`, `SIMULATION_SCHEMA.json` (10 files total, confirmed present this
   session via direct listing).
5. **Report the reconstructed state back to the CEO** (modules READY, git state, what's next) — prove
   the handoff worked before proceeding.
6. **Wait for explicit CEO approval to begin Phase 6.7.** Do not self-authorize.
7. **Only after approval**, implement, in the order `SIMULATION_HANDOFF.md` recommends:
   - Execution Simulator
   - Portfolio Simulator
   - Performance Analyzer
   - Simulation orchestration
   Following the exact same "production-quality: types, tests, mypy strict, docstrings, deterministic,
   logging, config objects" bar every prior module was held to, including a MANDATORY independent
   adversarial code-review pass (it has found real bugs in every single one of the 6 modules so far — 33
   real issues total, zero false-negative sessions) before declaring any component READY.

---

*Prior-session narrative history (Market Scanner large-scale-benchmark investigation, the two-concurrent-
sessions incident, the tracemalloc cliff discovery, detailed lessons-learned from Phases 6.1–6.5, etc.)
has been condensed across several rewrites of this document to keep it a usable entry point rather than
an ever-growing archive. The full detail remains available in git history and in each module's own
`*_VALIDATION_REPORT.md`. If a future session needs the granular lessons-learned/process-discipline notes
that used to live in this document's own §10, they are preserved in the git history of this file
(`git log -p -- NEXT_SESSION.md`) and in `EXECUTION_ENGINE_VALIDATION_REPORT.md`/
`RISK_MANAGER_VALIDATION_REPORT.md`'s own §2/§3 sections, which capture the same lessons in their
original, module-specific context.*
