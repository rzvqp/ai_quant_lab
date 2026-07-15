# NEXT_SESSION.md — Official Handoff (AI Trader Implementation Phase)

**Official session-close document, rewritten in full on 2026-07-15 per explicit CEO directive, after
Phase 6.7 (Simulation Framework) reached READY.** This document is the single source of truth for the
next Claude session. It is self-contained: a brand-new session must be able to continue correctly from
this file alone, without reading any prior conversation, without any fact surviving only in Claude's
memory. Every fact below was verified directly against `git log`/`git status`/`git diff`/a live
`pytest`+`mypy`+`coverage` run at close time — nothing here is assumed or carried over unverified.

---

## A. Project mission

**AI Quant Research Lab → AI Trader.** Two systems, physically separated by design:

- **Research Lab** (`code/`, `results/`, `knowledge/`) discovers and validates trading strategies
  against historical XAUUSD data. **Frozen and stable; never touched during AI Trader work** — verified
  0-diff at every commit since Phase 6.1 began (§F).
- **Strategy Library** (`knowledge/strategies/`) publishes 51 versioned, executable strategy contracts
  (S1–S51). **Strategy Interface v1** (`knowledge/interface/`) is the ONLY sanctioned contract between
  the Lab and the Trader.
- **AI Trader** (`ai_trader/`) is the execution system. All six live pipeline modules are READY: Market
  Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine. The
  **Simulation Framework** (Phase 6.7) is now ALSO implemented and READY: it composes those six modules
  unchanged with an Execution Simulator + Portfolio Simulator (no real broker) to run deterministic
  historical backtests.

**Simulation-first is mandatory (standing CEO directive, non-negotiable):** the AI Trader must prove
robust historical profitability in simulation before any Broker Adapter/MT5/live execution work begins.
**That profitability proof has NOT yet happened** — see §C7/§G item 1: no real per-strategy signal logic
exists, so the framework currently produces zero trades against real data. The next substantive step
toward "prove profitability" is implementing real strategy signal logic (a separate, not-yet-scoped
task), NOT Broker Adapter/MT5/Learning Engine, which remain explicitly unauthorized.

---

## B. Official Git state (verified this session, live)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
HEAD commit:      af00953 "Correct NEXT_SESSION.md's own HEAD reference to the final close commit"
                  (UNCHANGED this session -- see below)
Working tree:     NOT CLEAN -- Phase 6.7's entire implementation is UNCOMMITTED.
```

**IMPORTANT — this session did NOT commit.** The assistant operates under a standing "never commit
without explicit user instruction" rule and the CEO approval message for Phase 6.7 did not explicitly
instruct a commit (its Final Deliverables list did not include one, unlike `SIMULATION_HANDOFF.md` §16's
own suggested workflow, which the assistant did not treat as CEO authorization). **Every Phase 6.7 file
is on disk, fully verified (tests/mypy/coverage/adversarial review all passed live), and staged for the
CEO's review — but git-uncommitted.**

`git status --porcelain` shows (all untracked, all new, all confined to `ai_trader/simulation/` plus
three root-level docs):
```
ai_trader/simulation/__init__.py
ai_trader/simulation/api.py
ai_trader/simulation/artifacts.py
ai_trader/simulation/clock.py
ai_trader/simulation/config.py
ai_trader/simulation/data_source.py
ai_trader/simulation/exceptions.py
ai_trader/simulation/execution_simulator.py
ai_trader/simulation/harness.py
ai_trader/simulation/performance_analyzer.py
ai_trader/simulation/portfolio_simulator.py
ai_trader/simulation/py.typed
ai_trader/simulation/schema_validation.py
ai_trader/simulation/types.py
ai_trader/simulation/IMPLEMENTATION_CHOICES.md
ai_trader/simulation/tests/                    (13 test files)
SIMULATION_FRAMEWORK_VALIDATION_REPORT.md
NEXT_SESSION.md                                 (this file, modified)
CHANGELOG.md                                    (modified)
```
**The 10 frozen `ai_trader/simulation/*.md`/`.json` design docs and `SIMULATION_HANDOFF.md` were NOT
modified** (frozen specification, read-only throughout).

**Next session's FIRST action regarding git**: ask the CEO whether to commit this work now. If yes,
stage exactly the files above (never `git add -A`), commit with a message describing Phase 6.7, and
re-verify `git status --porcelain` is clean afterward. Do not assume authorization from this document
alone — it records what happened, not a standing instruction to commit.

## C. Completed implementation — every module, verified

### C1–C6. The six live pipeline modules (Phases 6.1–6.6) — READY, UNCHANGED this session
Verified via `git diff af00953 -- ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine`
→ **empty**. Full per-module detail (tests/coverage/mypy/bugs found) is unchanged from the prior
handoff; see git history of this file (`git log -p -- NEXT_SESSION.md`) or each module's own
`*_VALIDATION_REPORT.md` for the original Phase 6.1–6.6 detail, not repeated here to keep this document
a usable entry point.

### C7. Simulation Framework (Phase 6.7 — just closed this session)
- **Source:** `ai_trader/simulation/*.py` (12 production modules + `__init__.py`/`py.typed`)
- **Tests:** 87 (13 test files) · **Coverage:** 95% total (per-file 89–100%, see
  `SIMULATION_FRAMEWORK_VALIDATION_REPORT.md` §6) · **mypy --strict:** clean (13 files)
- **Validation report:** `SIMULATION_FRAMEWORK_VALIDATION_REPORT.md` (full detail; this section
  summarizes)
- **Bugs found+fixed by adversarial review:** 8 real issues (3 CRITICAL, 2 HIGH, 3 MEDIUM) — FOK
  partial-fill-revert fill leak; no exception safety net during RUNNING; the documented pre-fill
  margin rejection was never wired up; the liquidation threshold was off by ~100x (comparing a
  margin-level ratio against a margin percentage); `close_at_end_policy` was never consulted;
  `execution_log.jsonl` was mislabeled (wrong flag, wrong content); Risk Manager DENY/SUSPENDED/
  EMERGENCY_STOP events never reached `report.risk_events`; a partially-filled IOC order was mislabeled
  `FILLED`. All 8 fixed with dedicated regression tests (`test_adversarial_fixes.py`); see the
  validation report §4 for the full table.
- **What it proves:** the real, composed six-module pipeline runs deterministically and fail-safe over
  real historical XAUUSD data (full 2023–2026 dataset, 83,479 M15 bars, ~1,620 bars/sec, no crash, no
  state corruption) via the Execution Simulator (virtual Broker Adapter) + Portfolio Simulator (virtual
  account) + Performance Analyzer (`SimulationReport`, schema-validated). Determinism proven directly
  (identical context+seed ⇒ byte-identical report).
- **What it does NOT prove:** profitability. No real per-strategy signal logic exists (carried forward
  unchanged from §C3/Phase 6.3's own disclosed gap) — every real strategy's signal is `INVALID` by
  design, so a full-history run produces **zero trades**, equity exactly unchanged. This is the single
  most important carried-forward fact for whoever picks up strategy-logic work next.
- **Known limitations (disclosed, not fixed):** R-multiple requires an explicit stop hint (else `None`,
  never fabricated); portfolio-level `max_drawdown_R` and per-period `return_pct`/`max_drawdown_pct` in
  session/daily/monthly rollups are `None` (no sound formula without further design); capital
  allocation report is a simplified single-time-point measure, not the full time series;
  `atr_fraction` slippage falls back to zero (no ATR threaded into the bar-matching loop in v1);
  `run_batch` executes sequentially, not in parallel (a permission, not a requirement); session
  classification is a simple UTC-hour-bucket approximation. Full list: validation report §8.

---

## D. Full pipeline status

```
Market Scanner        READY  (Phase 6.1)
   → Strategy Manager  READY  (Phase 6.2)
      → Signal Engine  READY  (Phase 6.3)  [no real per-strategy signal logic yet -- see below]
         → Scoring Engine  READY  (Phase 6.4)
            → Risk Manager  READY  (Phase 6.5)
               → Execution Engine  READY  (Phase 6.6)
                  → Simulation Framework  READY  (Phase 6.7) -- proves the pipeline runs, not that it profits
                     → Learning Engine  [NOT STARTED -- not authorized]
```

## E. Global implementation statistics (verified live this session)

```
pytest ai_trader/ -q
1252 passed in ~55s

mypy --strict ai_trader/market_scanner ai_trader/strategy_manager ai_trader/signal_engine \
              ai_trader/scoring_engine ai_trader/risk_manager ai_trader/execution_engine \
              ai_trader/simulation --exclude 'tests/'
Success: no issues found in 102 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   7345 stmts   345 miss   95%
```

- **Total tests:** 1252 (six live modules: 1165, unchanged; Simulation Framework: 87, new)
- **Total production source files:** 102 (89 prior + 13 new), `mypy --strict` clean across all
- **Overall coverage:** 95%

## F. Protected invariants — confirmed untouched (verified this session, live)

- **Research Lab** (`code/`, `results/`, `data/`) — **FROZEN.** `git diff cef57c1~1 HEAD -- code/ results/ knowledge/`
  → empty.
- **S1–S51**, **Wave 1**, **Strategy Library**, **Strategy Interface v1**, **Knowledge Base** — all
  **FROZEN**, part of the same 0-diff guarantee above.
- **The six live pipeline modules** — byte-identical to the pre-Phase-6.7 HEAD (`af00953`), confirmed
  by direct `git diff`, §B.
- **Terminal holdout** — **SEALED**, untouched.
- **No broker code, no MT5, no live trading, no Learning Engine** — none exist anywhere in the tree.
- **Existing frozen module documentation** (every `*_ARCHITECTURE.md`/`*_SCHEMA.json`/`*_API.md`,
  including all 10 Simulation Framework docs + `SIMULATION_HANDOFF.md`) — unmodified; the new
  `ai_trader/simulation/IMPLEMENTATION_CHOICES.md` is an ADDITIVE companion document, not an edit to any
  frozen spec.

## G. Technical debt / known limitations carried forward

1. **No real Strategy Signal implementation exists yet — STILL TRUE, now fully diagnosed as TWO
   independent, stacked gaps** (`STRATEGY_RUNTIME_INTEGRATION_GAP.md`, a dedicated read-only analysis
   committed 2026-07-15, read it in full before touching anything strategy-related):
   - **Contract-format gap:** all 51 `knowledge/strategies/S*/strategy.json` files are still the
     Research Lab's own v0 research-export shape, none carry Strategy Interface v1's required
     top-level keys. Verified LIVE by running the real `StrategyManager.load_library()` against the
     real library: **51/51 fail schema validation identically** (`loaded=0, failed=51`,
     `counts_by_health={'INVALID': 51, ...}`), so `active_strategies()` always returns `[]`.
   - **Runtime-logic gap (independent of the above):** `StrategyRuntimeHandle` (`handle.py`) is a
     universal stub — every method except `required_context()` unconditionally raises
     `StrategyApiNotImplementedError`, by explicit design, for every strategy, always. Fixing the
     contract format alone would NOT produce a single signal without this also being closed.
   - Zero executable strategy code exists anywhere under `knowledge/strategies/` (confirmed: 0 `.py`
     files). The Research Lab's own `code/mstrat.py`/`families.py` are whole-DataFrame batch functions,
     architecturally incompatible with per-bar `MarketContext` evaluation, and **must never be imported
     at AI Trader runtime** (would violate the Research-Lab-frozen boundary) — only their logic may be
     read offline and re-implemented natively.
   - This is why Phase 6.7's own full-history run trades zero times. **CEO has since named this Phase
     6.8 — Executable Strategy Vertical Slice** (§H) — approved for planning only, NOT yet authorized to
     implement.
2. **Portfolio Manager is still NOT a separate runtime module.** Execution Engine and now the Simulation
   Framework's Portfolio Simulator both reuse/project `ai_trader.risk_manager.types.PortfolioState`
   directly — a documented IMPLEMENTATION CHOICE, resolved consistently a second time (Simulation
   Framework §C7), not silently re-decided.
3. **`BrokerAdapter` ↔ Execution Simulator mapping** is now resolved and verified (Simulation Framework
   §C7 IMPLEMENTATION CHOICE #1) — the open question from the Phase 6.6 handoff is CLOSED.
4. **`mypy --strict` test-file gaps in Strategy Manager and Market Scanner** (98 pre-existing errors, 16
   files, all in TEST files, not source) — unchanged, still disclosed, still out of scope.
5. Simulation Framework's own disclosed limitations — see §C7 above / validation report §8 (not
   repeated here).

## H. Immediate next phase

**PHASE 6.8 — EXECUTABLE STRATEGY VERTICAL SLICE.** CEO-named (2026-07-15), following the gap analysis
in `STRATEGY_RUNTIME_INTEGRATION_GAP.md` (§G item 1). **Explicitly NOT yet authorized to implement** —
"Do not begin Phase 6.8 until a new explicit CEO approval is given." The objective is ONE real strategy
proven end-to-end, not a 51-strategy batch migration:

1. Select one frozen strategy family with existing research code and sufficient historical evidence
   (the gap analysis's own §10 recommends S1 — best-specified contract, no HTF context required,
   already-honest "no confirmed alpha" research verdict).
2. Migrate its contract v0 → Strategy Interface v1.
3. Implement its runtime evaluator WITHOUT importing Research Lab code at runtime.
4. Validate runtime outputs against the frozen research implementation on identical historical contexts.
5. Load it through Strategy Manager; produce real actionable signals through Signal Engine.
6. Pass through Scoring Engine, Risk Manager, Execution Engine.
7. Run the first economic backtest through the Simulation Framework: **XAUUSD, 2,000 USD starting
   capital, USD account currency, 5% risk per trade.**
8. Report trades, net profit, return, expectancy, profit factor, max drawdown, equity curve, strategy
   attribution, execution costs.

Do not batch-migrate S2–S51 before this vertical slice proves out. Do not begin Learning Engine, Broker
Adapter, MT5, or live/paper trading under cover of this phase.

## I. Exact next-session order

1. **Read this document in full first.**
2. **Verify Git state directly** — `git branch --show-current`, `git log -1`, `git status --porcelain`
   — re-confirm §B, especially whether the CEO has since instructed (in this or another session) that
   Phase 6.7's work be committed; do not assume it was.
3. **Read `SIMULATION_FRAMEWORK_VALIDATION_REPORT.md` and `STRATEGY_RUNTIME_INTEGRATION_GAP.md` in
   full** for the complete Phase 6.7 detail and the Phase 6.8 gap diagnosis this document only
   summarizes.
4. **Report the reconstructed state back to the CEO** before proceeding on anything new.
5. **Wait for explicit CEO direction** — Phase 6.8 (§H) is named but NOT yet approved to implement; do
   not self-authorize starting it.

---

*Prior-session narrative history for Phases 6.1–6.6 (Market Scanner large-scale-benchmark
investigation, the two-concurrent-sessions incident, the tracemalloc cliff discovery, per-phase
lessons-learned) remains available in git history of this file (`git log -p -- NEXT_SESSION.md`) and in
each module's own `*_VALIDATION_REPORT.md`.*
