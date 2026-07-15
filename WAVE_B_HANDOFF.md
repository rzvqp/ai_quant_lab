# WAVE_B_HANDOFF.md — Official Session-Close Handoff (Phase 6.8, post-Checkpoint 1)

**Written 2026-07-15 at official session close, per explicit CEO directive.** This document, together
with `NEXT_SESSION.md`, `CHANGELOG.md`, `SIMULATION_FRAMEWORK_VALIDATION_REPORT.md`,
`STRATEGY_RUNTIME_INTEGRATION_GAP.md`, `PHASE_6_8_CHECKPOINT_1_REPORT.md`, and
`PHASE_6_8_WAVE_B_PLAN.md`, is intended to let a **brand-new Claude session reconstruct this entire
project using ONLY repository files** — no fact here should require anything from a prior
conversation. Every claim below was verified live (`git`/`pytest`/`mypy`/`coverage`) at the moment this
document was written, not assumed or carried over.

---

## 1. Executive summary

This repository (`ai_quant_lab-research-main`) hosts the **AI Quant Research Lab → AI Trader** project:
a frozen, statistically-validated Research Lab (`code/`, `results/`, `knowledge/`) whose output feeds a
separately-built AI Trader execution system (`ai_trader/`). The AI Trader's six live pipeline modules
(Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine)
are all READY (Phases 6.1–6.6). A Simulation Framework (Phase 6.7) composes those six modules,
unchanged, with a virtual broker/account to run deterministic historical backtests — also READY. Phase
6.8 (Executable Strategy Vertical Slice) is now **underway**: its goal is to make the Strategy
Library's ~43 runtime-eligible strategies actually executable, so the AI Trader can evaluate real
opportunities and choose between them, instead of the fail-safe-only path every module proved before
this phase. **Checkpoint 1 of Phase 6.8 — a generic strategy-runtime framework plus one fully
implemented, proven-end-to-end reference strategy (S1) — is ACHIEVED, committed, and this session is
now closed.** Wave B (the remaining ~42 strategies) is explicitly deferred to a future session by CEO
decision, with a prepared (not executed) plan already on disk.

## 2. Current repository state (verified live at session close)

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
```

## 3. Current branch

```
ai-trader-implementation
```

## 4. Final HEAD

```
19bd4e09c641ff82ec0e72ceaa92e481d63be831
"Phase 6.8 Checkpoint 1: generic strategy runtime + S1 reference slice READY"
(2026-07-15 10:50:33 +0300)
```
This is the HEAD as verified before this handoff document's own commit. **The commit that adds this
file (and the accompanying `NEXT_SESSION.md`/`CHANGELOG.md` updates) will advance HEAD by exactly one
commit past this hash — the next session MUST re-verify `git log -1` directly rather than trust this
number blindly** (the same "verify live, never assume" discipline this entire project has followed at
every prior handoff).

## 5. Working tree

**CLEAN**, verified via `git status --porcelain` immediately before writing this document (returned
nothing). It will show exactly this handoff's own new/modified files until committed at the end of this
session-close procedure.

## 6. Completed phases

| phase | scope | status |
|---|---|---|
| 5.1–5.6 | AI Trader architecture design (docs only, all `ai_trader/*/​*.md`/`*.json`) | COMPLETE |
| 6.1 | Market Scanner v1 | READY |
| 6.2 | Strategy Manager v1 | READY |
| 6.3 | Signal Engine v1 | READY |
| 6.4 | Scoring Engine v1 | READY |
| 6.5 | Risk Manager v1 | READY |
| 6.6 | Execution Engine v1 | READY |
| 6.7 | Simulation Framework v1 | READY |
| 6.8 Checkpoint 1 | Generic strategy runtime + S1 reference slice | **ACHIEVED** |
| 6.8 Wave B | Remaining ~42 strategies | **NOT STARTED** (planned only) |

## 7. READY modules

- `ai_trader/market_scanner/` — Market Scanner v1.
- `ai_trader/strategy_manager/` — Strategy Manager v1.
- `ai_trader/signal_engine/` — Signal Engine v1.
- `ai_trader/scoring_engine/` — Scoring Engine v1.
- `ai_trader/risk_manager/` — Risk Manager v1.
- `ai_trader/execution_engine/` — Execution Engine v1.
- `ai_trader/simulation/` — Simulation Framework v1 (Phase 6.7).
- `ai_trader/strategy_runtime/` — generic strategy-runtime framework (Phase 6.8 Wave A) + S1's real
  evaluator (Phase 6.8 Checkpoint 1). **Only S1 has a real evaluator; the framework itself is READY,
  but the Strategy Library as a whole is NOT yet executable** (see §12).

## 8. Modules not started

- **Learning Engine** — no code, no design docs beyond a named "future slot" in the Simulation
  Framework's own architecture doc. Not authorized.
- **Broker Adapter (real)** — only the abstract `Protocol` in `ai_trader/execution_engine/
  broker_adapter.py` exists (an interface definition, not a venue integration). Not authorized.
- **MT5 integration** — nothing exists. Not authorized.
- **Wave B / B–J of Phase 6.8** — 42 of 43 runtime-eligible strategies still lack real evaluators (see
  §19–23). Planned, not implemented.

## 9. Current architecture

```
Research Lab (code/, results/, knowledge/{strategies,interface}) — FROZEN, 0-diff since Phase 6.1
   │  publishes via Strategy Interface v1 (the ONLY sanctioned Lab -> Trader contract)
   ▼
AI Trader (ai_trader/)
   Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine
   (all six READY, composed unchanged everywhere below)
      │
      ├─▶ Simulation Framework (ai_trader/simulation/) — Execution Simulator + Portfolio Simulator +
      │    Performance Analyzer standing in for a real broker/account; deterministic historical replay.
      │
      └─▶ Strategy Runtime (ai_trader/strategy_runtime/) — real, per-strategy Strategy API evaluators,
           composed into Signal Engine via its own structural StrategyHandleLike/StrategyApiLike
           Protocols (NO frozen module ever modified to make this work).
```

## 10. Runtime architecture (Strategy Runtime package detail)

`ai_trader/strategy_runtime/` — 7 production modules, all additive, zero frozen-module edits:

| module | role |
|---|---|
| `context_access.py` | read-only `MarketContext` helpers (features/bars/session/data-quality) — the source of every evaluator's lookahead-safety guarantee |
| `confirmations.py` | shared bar-pattern primitives: consecutive closes, liquidity-sweep detection, displacement, rolling-extreme touch |
| `risk.py` | shared stop-floor/target helpers mirroring the frozen research engine's own conventions (`RESEARCH_ENGINE_TICK = 0.1`, `executable_stop_floor`, `widen_stop_to_floor`, `rr_target`, `risk_r_of`) |
| `evaluator.py` | `RuntimeEvaluator` base class (subclass and implement ONE method, `evaluate() -> SetupResult`; the base class translates that into the 3 real Strategy API dict responses `detect`/`generate_signal`/`explain_signal`, with per-`(symbol, as_of)` caching) + `RuntimeStrategyHandle` (the `{id, contract, api}` object hand ed to Signal Engine) |
| `migration.py` | v0 (Research Lab export) → Strategy Interface v1 contract mapper: mechanical/boilerplate fields (identity, lifecycle, evidence/metrics, provenance) are automated from the v0 document; SEMANTIC fields (`required_data`, `required_confirmations`, `entry`/`exit`/`stop` `RuleSpec` text) are REQUIRED explicit arguments — never auto-invented |
| `registry.py` | `strategy_id -> evaluator class` registry (`@register("S1")` decorator); `build_runtime_handles(strategy_manager, symbols)` builds real handles ONLY for strategies BOTH active in Strategy Manager's own registry AND registered here — authority for "is this strategy allowed to run" stays with Strategy Manager, never duplicated |
| `families/s01_confirmed_liquidity_sweep_reversal.py` | S1's real evaluator — the only implemented family so far |

**Integration point** (`ai_trader/simulation/harness.py`, extended, NOT a frozen module): three new,
all-default-preserving, opt-in constructor parameters —
- `manager_config: ManagerConfig | None` — pass `ManagerConfig(auto_admit_min_maturity="EXPLORATORY")`
  to let loaded strategies reach `active_strategies()` (default: `ManagerConfig()`, no auto-admission,
  Phase 6.7's original behavior).
- `use_strategy_runtime: bool = False` — `True` swaps `active_strategies()` for
  `ai_trader.strategy_runtime.registry.build_runtime_handles()` when building the handles Signal Engine
  evaluates (default `False`: Phase 6.7's original fail-safe-stub path, unchanged).
- `risk_config: RiskConfig | None` — MUST set `filters.reference_spread["XAUUSD"]` and
  `filters.liquidity_floor["XAUUSD"]` (or any other configured symbol) for Risk Manager to ever ALLOW a
  real opportunity — its own fail-safe default denies any symbol with no configured threshold (default:
  `RiskConfig()`, everything denied, Phase 6.7's original behavior).

## 11. Simulation Framework status

**READY** (Phase 6.7, unchanged this session except the harness extension in §10). Full detail:
`SIMULATION_FRAMEWORK_VALIDATION_REPORT.md`. Composes the six live modules with:
`ai_trader/simulation/{execution_simulator,portfolio_simulator,performance_analyzer,harness,api,
config,types,clock,data_source,artifacts,schema_validation,exceptions}.py`. 87 tests (as of Phase 6.7
close; unchanged this session), full historical XAUUSD replay (83,479 M15 bars) runs in ~35–55 seconds
depending on machine load, fully deterministic (byte-identical reports for identical context+seed,
proven directly by test, INCLUDING with real Strategy Runtime evaluators active — see §13).

## 12. Strategy Runtime status

**Framework READY. Library coverage: 1 of 43 runtime-eligible strategies (S1) has a real evaluator.**
`StrategyManager.load_library()` against the real `knowledge/strategies/` library today reports (live,
re-verified this session): `loaded=('S1',)`, 50 strategies still fail Strategy Interface v1 schema
validation (v0 seed format), plus S1 itself also appears in `failed` under a scanner-feature-limited
test fixture (`FakeScanner`) — see `ai_trader/strategy_manager/tests/test_real_library_integration.py`
for the exact, current, live-verified counts and why `loaded`/`failed` are not mutually exclusive by
design. Against the REAL `MarketScanner` (which the Simulation Harness uses), S1 loads AND is fully
compatible.

## 13. Checkpoint 1 summary

**ACHIEVED.** Full detail: `PHASE_6_8_CHECKPOINT_1_REPORT.md`. In one sentence: the generic Strategy
Runtime framework was built, S1 was migrated and given a real evaluator, and the whole pattern was
proven — not just unit-tested — by running S1's real evaluator through the REAL six-module pipeline
plus the Simulation Framework over real historical XAUUSD data, producing real closed trades with
correct R-multiples (rr2 exit, risk normalized), a schema-valid `SimulationReport`, and bit-identical
determinism with real strategy logic active. Two genuine, non-obvious bugs were found and fixed only
because of this end-to-end proof (§15) — unit tests on S1 in isolation passed cleanly and would NOT
have caught either.

## 14. S1 migration summary

- **Strategy:** S1, "Confirmed Liquidity Sweep Reversal" — price sweeps a resting liquidity level
  (previous-day low, via the Market Scanner's own `pdl` feature), trapping breakout traders, then
  closes back inside the range; two consecutive bullish closes confirm the reversal; LONG-only
  (`side=low` in the v0 grammar); stop 2 ticks past the true sweep-sequence extreme (floored);
  2R fixed target.
- **Migration**: `knowledge/strategies/S01_confirmed_liquidity_sweep_reversal/strategy.json` converted
  from the Research Lab's v0 export shape to Strategy Interface v1
  (`knowledge/interface/strategy_contract.v1.schema.json`). Original preserved, never deleted, at
  `strategy.v0.json` in the same folder.
- **Fidelity choice**: implements EXACTLY the v0 contract's own `executable_default` parameter tuple —
  the specific, evidence-backed configuration the Research Lab's own historical performance numbers
  (`n=399, expectancy_R=0.032, ...`) were measured on — NOT the full general grammar, which would be a
  broader, un-evidenced strategy.
- **Evaluator**: `ai_trader/strategy_runtime/families/s01_confirmed_liquidity_sweep_reversal.py`, one
  class, `evaluate()` implements the sweep-detection → confirmation-window → stop/target logic using
  only the shared framework helpers (§10).

## 15. Bugs discovered and fixed (Checkpoint 1)

1. **S1 evaluator stop-calculation bug**: the original implementation anchored the stop 2 ticks past
   the nominal sweep bar's OWN low. Real XAUUSD data showed price can make a new, LOWER low between the
   sweep bar and confirmation completing — anchoring only to the sweep bar's own low could place the
   computed stop ABOVE the entry price, which Risk Manager's own `_valid_stop_side` sanity gate
   correctly caught and denied (`INVALID_INPUT`). **Fix**: the stop now clears the minimum low across
   the ENTIRE sweep-to-confirmation bar range (mathematically guaranteed `<= entry`, since the
   confirmation bars — including the current bar — are part of that range, and a bar's own low is
   always `<=` its own close). Regression test:
   `ai_trader/strategy_runtime/tests/families/test_s01_confirmed_liquidity_sweep_reversal.py::
   TestActionable::test_regression_stop_never_above_entry_when_price_dips_after_sweep`.
2. **Phase 6.7 `_build_risk_context` gap (a real, pre-existing bug in `ai_trader/simulation/
   harness.py`, not new this session but only surfaced now)**: `SIMULATION_FRAMEWORK_VALIDATION_REPORT.
   md`'s own original §8 claimed `atr`/`current_spread`/`liquidity_proxy` were "not present in the
   Market Scanner's own public `MarketContext` feature namespace." **This was factually wrong** —
   confirmed by reading `ai_trader/market_scanner/features.py` directly:
   `M15_FEATURE_NAMES` publishes `m_atr` and `atr_ma`. Because of this, every real ALLOW opportunity
   Risk Manager ever evaluated was denied on `FILTER_VOLATILITY` ("atr data unavailable") for no real
   reason — a Phase 6.7 harness defect that produced ZERO trades even once S1's own evaluator was
   correctly firing. **Fix**: `_build_risk_context` now reads `m_atr`/`atr_ma` for `atr`/
   `atr_rolling_median`, derives `current_spread` from the SAME cost-model convention the Execution
   Simulator already uses (not a fabricated new number), and `liquidity_proxy` from the current bar's
   own real traded volume.

**Lesson carried forward from both**: end-to-end proof against real data is not optional polish — it
is the ONLY thing that caught either bug. Unit tests in isolation (which both S1's evaluator and
Phase 6.7's own 87-test suite had, extensively) passed cleanly around both defects. Wave B must budget
real end-to-end verification per batch, not just per-strategy unit tests, or it will silently ship
strategies whose signals never actually reach a fill.

## 16. Lessons learned (broader, for Wave B's own planning)

- The Strategy Library's `strategy.json` v0 files are STRUCTURALLY UNIFORM across all 43
  runtime-eligible entries (verified: only the 6 `NOT_IMPLEMENTED` stub files differ in shape) — a
  generic migration mapper (`migration.py`) is safe to reuse for all of them, but the SEMANTIC fields
  (what data each strategy actually reads) must still be supplied per-strategy by whoever implements
  that strategy's evaluator, in lockstep with the evaluator code itself — never mechanically guessed
  from the v0 prose.
- The Market Scanner's own `M15_FEATURE_NAMES` (`ai_trader/market_scanner/features.py`) already
  publishes almost everything the 43 strategies need natively: ATR, EMA/RSI/trend flags, rolling
  extremes, previous-day/week levels, opening range, VWAP, FVG/displacement flags, HTF trend/RSI/
  volrank folded in with `h1_`/`h4_`/`d1_` prefixes. **Before writing a new shared helper for Wave B,
  check whether the feature already exists** — Checkpoint 1's own false-negative belief that ATR was
  unavailable (§15 item 2) is the cautionary example.
- `StrategyManager`'s `active_strategies()` requires an explicit `ManagerConfig(auto_admit_min_
  maturity=...)` — the Manager's own conservative default never auto-activates anything, by design.
- Risk Manager's spread/liquidity filters deny any symbol with no configured threshold, by design —
  every new `SimulationHarness`/`SimulationAPI` instance driving real strategies MUST pass a
  `risk_config` with those thresholds set, or every decision will DENY regardless of how correct the
  strategy logic is.
- `StrategyHandleLike`/`StrategyApiLike` (`ai_trader/signal_engine/pipeline.py`) are plain (non
  -runtime-checkable) `Protocol`s — structural typing works at the type-checker/behavioral level, but
  `isinstance()` checks against them will raise `TypeError`; test conformance behaviorally (run the
  real pipeline function against the object) instead.

## 17. Protected invariants (status at session close, verified live)

- **Research Lab** (`code/`, `results/`) — **FROZEN**, `git diff cef57c1~1 HEAD -- code/ results/` is
  empty, verified this session.
- **Strategy Library / Strategy Interface** (`knowledge/`) — frozen EXCEPT the explicitly CEO-approved,
  disclosed S1 migration, confined to `knowledge/strategies/S01_confirmed_liquidity_sweep_reversal/`
  only (verified: `git diff --stat` against the pre-Phase-6.8 HEAD shows exactly that one folder's two
  files changed, nothing else under `knowledge/`).
- **The six live pipeline modules' production code** — byte-identical to the pre-Phase-6.7 HEAD
  (`af00953`); only two TEST files were updated (`strategy_manager/tests/
  test_real_library_integration.py`, `scoring_engine/tests/test_engine_integration.py`), both
  pre-existing, explicit, documented tripwires that anticipated exactly the S1 migration event.
- **Terminal holdout** — SEALED, untouched, never referenced by any Phase 6.x work.
- **No broker code, no MT5, no live trading, no Learning Engine** anywhere in the tree.

## 18. Strategy Runtime Integration Gap summary

Full document: `STRATEGY_RUNTIME_INTEGRATION_GAP.md` (committed prior to Checkpoint 1, still fully
accurate for the 42 strategies Wave B has not yet touched). Two independent, stacked gaps were
diagnosed and confirmed empirically (not by inference): (1) a CONTRACT-FORMAT gap — all 51 real
`strategy.json` files were v0 seed shape, none validated against Strategy Interface v1, so
`active_strategies()` was always empty; (2) a RUNTIME-LOGIC gap — even a migrated contract would do
nothing, because `ai_trader/strategy_manager/handle.py`'s `StrategyRuntimeHandle` is an intentional
universal stub (every method but `required_context()` raises `StrategyApiNotImplementedError`, by
design, for every strategy). Checkpoint 1 closed BOTH gaps for S1 specifically, via the
Strategy-Runtime package (§10) — a purely additive composition layer, never a modification to
`handle.py` itself. 42 strategies remain with gap (1) fully diagnosed and gap (2) now solved in
principle (the framework exists) but not yet applied to them.

## 19. Wave B objectives

Per the CEO's Phase 6.8 approval (full original text preserved in git history of this conversation's
prior turns; summarized authoritatively here and in `PHASE_6_8_WAVE_B_PLAN.md`): make the COMPLETE
eligible Strategy Library executable, not just S1. At every historical bar, each active strategy must
independently produce one of `BUY`/`SELL`/`WAIT_CONFIRMATION`/`NEED_CONTEXT`/`BLOCKED`/`NO_SIGNAL`/
`INVALID` per its own frozen rules; the AI Trader must then compare all simultaneous opportunities and
decide eligibility, direction, strongest score, conflicts, Risk Manager approval, and which single
order executes in simulation. Strategies must be classified honestly first — RUNTIME-ELIGIBLE (43,
already verified) vs INVALID (2: S47, S49, remain quarantined) vs NOT_IMPLEMENTED/DATA-BLOCKED (6:
S32–S37, remain disabled) — never forced into runtime. **CEO decision after Checkpoint 1: Wave B does
NOT start in this or the immediately-following session — it starts in a FRESH session, once explicitly
authorized.**

## 20. Mechanism batches (planned, not executed — full detail in `PHASE_6_8_WAVE_B_PLAN.md`)

Grouped using the Strategy Library's own embedded `klass` taxonomy (Class I–VIII / Batch1–2, verified
present on every real entry):

| batch | ids (count) | mechanism | new shared helper needed |
|---|---|---|---|
| B1 | S6, S16, S17, S18, S19, S24, S29, S30, S31 (9) | session/calendar/time-based, pure feature comparisons | none |
| B2 | S2, S11, S12, S21, S22 (5) | liquidity/sweep/reversal — extends S1's own proven pattern | none, maybe a small `structure.py` for CHoCH swing points |
| B3 | S26, S27, S28 (3) | value/VWAP/auction | new `vwap.py` |
| B4 | S13 (1) | imbalance/FVG | none |
| B5 | S45, S50 (2) | candlestick/bar-pattern | new `patterns.py` |
| B6 | S44 (1) | order-flow proxy (intrabar close-location) | none |
| B7 | S3, S4, S5, S10, S23, S46, S48 (7) | breakout/compression/continuation | new `breakout.py` |
| B8 | S7, S9, S14, S15, S38, S39, S43 (7) | trend/pullback/momentum | new `trend.py` |
| B9 | S8, S41, S42, S51 (4) | mean-reversion/volume-driven reversal | new `mean_reversion.py` |
| B10 | S20, S25, S40 (3) | composite/regime/meta — depends on the other batches, implement LAST | none (composes existing helpers) |

**42 strategies total across 10 batches**, matching the 43 RUNTIME-ELIGIBLE count minus S1.

## 21. Planned migration order

1. B1 (session/calendar, 9) — lowest risk, no new pattern logic.
2. B2 (liquidity/sweep, 5) — directly extends the already-proven S1 pattern.
3. B4 (imbalance, 1) + B6 (order-flow proxy, 1) — trivial, bundle with B2's checkpoint.
4. B3 (VWAP/value, 3).
5. B5 (candlestick, 2).
6. B7 (breakout/compression, 7) — implement S4 and its redesign S23 together.
7. B8 (trend/momentum, 7) — implement S7/S38 and S15/S39 pairs together.
8. B9 (mean-reversion/volume, 4).
9. B10 (composite/meta, 3) — LAST, composes/routes the other batches' now-implemented mechanisms.

## 22. Testing methodology (for Wave B, per-batch, not deferred)

1. Unit tests per strategy (no-setup / waiting / actionable cases minimum, plus a dedicated edge-case
   test for that strategy's own stop/target formula — Checkpoint 1's own stop-bug is the concrete
   precedent for why this matters).
2. Contract-migration tests: every new v1 `strategy.json` passes `validate_contract` (schema) and
   `parse_contract` (typed).
3. Registry tests: `StrategyManager.load_library()` + `build_runtime_handles()` show the expected
   loaded/active count for that batch.
4. **Per-batch end-to-end proof** (not deferred to the very end): each of the 9 remaining batches gets
   its own real-pipeline + Simulation Framework run over real historical data, mirroring
   `ai_trader/strategy_runtime/tests/test_s1_end_to_end.py`'s own pattern.
5. Full-suite regression check (`pytest ai_trader/ -q`, `mypy --strict`, coverage) after EVERY batch,
   never accumulated across multiple batches.
6. Any strategy whose runtime behavior cannot be verified against the frozen research engine's own
   fill/cost convention must be disclosed as such in that batch's checkpoint report, never silently
   assumed conformant.

## 23. Expected checkpoints (Wave B, mapped from the CEO's own Checkpoint 2–6 structure)

- **Checkpoint 2**: B1 + B2 (14 strategies) — first real batch beyond the S1 reference slice.
- **Checkpoint 3**: all 42 remaining contracts migrated v0→v1 (can run ahead of evaluator
  implementation, since migration is pure data restructuring, but `required_data`/
  `required_confirmations` still need per-strategy authorial care).
- **Checkpoint 4**: B3 through B9 evaluators implemented and signal-producing (33 more strategies).
- **Checkpoint 5**: B10 complete (all 43 active simultaneously) + full-library deterministic
  integration test (independent evaluation, no cross-strategy mutation, simultaneous BUY/SELL reaching
  Scoring Engine, deterministic ranking/conflict handling, Risk Manager receiving ranked opportunities,
  only approved opportunities producing orders).
- **Checkpoint 6**: the complete economic backtest (Wave D) — XAUUSD, $2,000 starting capital, USD
  account currency, 5% risk per trade, full attribution/session/regime/correlation report.

## 24. Current known limitations

- Only S1 of 43 runtime-eligible strategies has a real evaluator; the other 42 still resolve to
  `INVALID`/no-signal via the frozen Strategy Manager stub or are simply not loaded (v0 seed shape).
- `PortfolioState`/`RiskContext` still carry several disclosed Phase 6.7 approximations even after
  the §15 item 2 fix: `atr_rolling_median` is approximated by `atr_ma` (a mean, not a true rolling
  median — no rolling-median feature is published); `current_spread` is a constant policy assumption,
  not a live feed (none exists in this repo); `liquidity_proxy` uses raw bar volume, not a true
  participation/depth measure.
- Portfolio-level `max_drawdown_R` and per-period (`session`/`daily`/`monthly`) `return_pct`/
  `max_drawdown_pct` in the Simulation Framework's own reports are `None` (no sound formula established
  yet without further design) — disclosed, not fabricated.
- `mypy --strict` test-file gaps in Strategy Manager and Market Scanner (98 pre-existing errors, 16
  files, all in TEST files, not source) — unchanged since Phase 6.2/6.1, still disclosed, still out of
  scope for every phase so far.
- No conformance test exists yet between S1's real evaluator's OWN historical trade generation and the
  frozen research engine's own historical trade log for S1 specifically (Checkpoint 1 proved the COST
  MODEL conforms via `test_conformance_vs_research_engine.py`'s pre-existing pattern, but did not
  re-run S1's exact hypothesis against `code/mstrat.py` bar-for-bar) — a good candidate for Wave B's
  own "material research/runtime parity" checks per batch.

## 25. Future roadmap (in order, each gated on explicit new CEO approval)

1. **Wave B** (this handoff's own subject) — make all 43 runtime-eligible strategies executable.
2. **Wave C** — full-library simultaneous integration test (multi-strategy conflict resolution, ranking,
   Risk Manager arbitration).
3. **Wave D** — the complete economic backtest and its full performance/attribution report.
4. Only AFTER Wave D's own results are reviewed by the CEO: a possible future phase to interpret
   results, decide on strategy pruning/allocation (still NOT optimization — no parameter tuning against
   backtest results is ever authorized), and design what (if anything) comes after — Learning Engine,
   Broker Adapter, and MT5 integration remain explicitly NOT authorized until that point, and each
   would need its own dedicated CEO-approved phase exactly like every phase so far.

## 26. Exact next task

**Do not self-authorize Wave B.** The exact next task, once a NEW session is explicitly told to begin
Wave B, is: **Checkpoint 2 — migrate and implement batch B1 (S6, S16, S17, S18, S19, S24, S29, S30,
S31 — session/calendar/time-based, 9 strategies) and batch B2 (S2, S11, S12, S21, S22 —
liquidity/sweep/reversal, 5 strategies)**, following `PHASE_6_8_WAVE_B_PLAN.md` §5's testing
methodology per strategy, with a per-batch end-to-end proof before moving to the next batch, and a full
regression check (`pytest ai_trader/ -q`, `mypy --strict`, coverage) after each batch — never
accumulating untested strategies across batches.

## 27. First prompt for the next Claude session

```
CEO SESSION START — PHASE 6.8 WAVE B AUTHORIZATION

Read, in this order:
1. NEXT_SESSION.md
2. WAVE_B_HANDOFF.md
3. CHANGELOG.md
4. PHASE_6_8_WAVE_B_PLAN.md
5. PHASE_6_8_CHECKPOINT_1_REPORT.md
6. STRATEGY_RUNTIME_INTEGRATION_GAP.md

Verify directly from git (do not trust any document blindly):
- repository path, current branch, HEAD commit, working tree status
- protected-area 0-diff (Research Lab, the six pipeline modules, knowledge/ confined to S1)
- full ai_trader/ test suite, mypy --strict, coverage

Report the reconstructed state back to me before writing any code.

Once confirmed, you are authorized to begin Phase 6.8 Wave B, Checkpoint 2:
migrate and implement mechanism batches B1 (session/calendar, 9 strategies) and B2
(liquidity/sweep/reversal, 5 strategies), per PHASE_6_8_WAVE_B_PLAN.md's own testing
methodology -- unit tests per strategy, contract-migration tests, registry tests, a
per-batch end-to-end proof through the real pipeline + Simulation Framework, and a full
regression check after the batch, before moving to the next.

Do not batch-migrate beyond B1+B2 without reporting back. Do not begin Wave C/D,
Learning Engine, Broker Adapter, MT5, or live/paper trading under cover of this task.
Stop and ask only for: a frozen-contract change, semantic ambiguity, missing required
data, or a research/runtime parity failure.
```
