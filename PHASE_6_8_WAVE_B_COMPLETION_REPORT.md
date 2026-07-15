# Phase 6.8 — Wave B Completion Report: All 43 Runtime-Eligible Strategies Migrated

**Date:** 2026-07-15. **Scope:** Complete Phase 6.8 Wave B (per `PHASE_6_8_WAVE_B_PLAN.md`) — migrate
and implement every remaining mechanism batch (B3–B10) beyond Checkpoint 2's own 15-strategy slice,
per the CEO's standing "continue automatically, batch-by-batch, without re-asking" authorization.
**Verdict: WAVE B COMPLETE.** All 43 of the Strategy Library's 43 runtime-eligible strategies (S1–S51
minus S32–S37 NOT_IMPLEMENTED and S47/S49 INVALID in the frozen v0 spec) now have real,
evidence-faithful runtime evaluators.

---

## 1. What was built, batch by batch (beyond Checkpoint 2's own 15)

| batch | strategies | mechanism |
|---|---|---|
| B3 | S26, S27, S28 (3) | VWAP/value-area (new `vwap.py` helper: `value_area_edges`, `week_bucket`, `anchored_vwap`, `distance_in_atr`) |
| B4 | S13 (1) | imbalance/FVG fill |
| B5 | S45, S50 (2) | candlestick pattern (new `patterns.py` helper: `is_outside_bar`, `is_range_expansion`, `close_to_close_direction`, `exact_close_to_close_streak`) |
| B6 | S44 (1) | intrabar pressure / close-location order-flow proxy |
| B7 | S3, S4, S5, S10, S23, S46, S48 (7) | breakout/compression |
| B8 | S7, S9, S14, S15, S38, S39, S43 (7) | trend/momentum |
| B9 | S8, S41, S42, S51 (4) | mean-reversion/volume |
| B10 | S20, S25, S40 (3) | composite/meta — LAST, per plan, composing other groups' mechanisms |

Every strategy implements EXACTLY its own contract's `executable_default` parameter tuple, verified
against the frozen research engine's own grammar functions (`code/mstrat.py`, `code/mstrat_ext.py`,
read-only reference, never imported) rather than the v0 JSON's prose alone — the same discipline
Checkpoints 1–2 established. Non-obvious fidelity traps caught this way: S12's `target=='center'`
override (Checkpoint 2); S27's exit branching resolving `exit=rr2` to a VWAP-band target, not a fixed
R-multiple; S46's `stop='level'` placing the stop at the OPPOSITE 50-bar extreme, not near the
breakout.

## 2. Two genuine research/runtime parity gaps found and resolved this Wave

### 2a. The generic trailing-stop mechanism

Six strategies' own evidence-backed `executable_default` selected the frozen engine's `exit=trailing`
grammar option (S4, S10, S15, S23, S38, S48) — a 1.5×ATR-at-entry trailing stop with NO corresponding
execution mechanism in the AI Trader runtime (`BrokerAdapter`'s own Protocol has no order-amend
capability; `emergency_flatten()` was considered and rejected after discovering it permanently latches
the engine's lifecycle state, which would have blocked every future entry — a real regression caught
during design). Per CEO design mandate (generic, deterministic, reusable, broker-independent, no
strategy-specific code, single Execution Engine gateway):

- `RuntimeEvaluator.trailing_stop_atr_mult: float | None` (new, additive field) — opt-in per strategy.
- `ai_trader/simulation/trailing_stop.py` (new) — reuses Portfolio Simulator's already-tracked
  `Position.mfe` (max favorable excursion) to derive the best-favorable-price with ZERO new `Position`
  fields; the only new state is `entry_atr` per position, tracked in the harness's own dict. Submits a
  synthetic reduce-only `RiskDecision` through the SAME `ExecutionEngine.execute()` gateway every other
  order already uses.
- `ai_trader/simulation/harness.py` gained `enable_trailing_stops: bool = False` (opt-in, Phase 6.7's
  original behavior unchanged when omitted).
- **Zero edits to any of the six frozen pipeline modules.**

### 2b. The generic historical-features window in Market Scanner

Five strategies (S4, S23, S25, S43, S48) needed genuine PER-BAR historical feature values (a prior
bar's own `compress` flag, `m_rsi`, or `m_atr`/`atr_ma` snapshot) to reproduce onset/duration/
divergence conditions the frozen engine computes via `pandas` rolling-window operations
(`.rolling(n).sum().shift(1)`, `.rolling(n).max().shift(1)`, etc.). Only the CURRENT bar's feature
snapshot was ever exposed to strategies before this session — `MarketScanner` discarded every prior
snapshot (`self._last_base_result` kept only the latest). Initially scoped narrowly (RSI only, for
S43), then correctly broadened after finding the identical root cause blocks S4/S23/S25/S48 too — CEO
approved the generic fix over four narrow patches. Per CEO design mandate (generic, deterministic,
reusable, no strategy-specific implementation, no approximation, no synthetic reconstruction):

- `ai_trader/market_scanner/scanner.py` (frozen module, first-ever touch, explicitly CEO-approved) —
  new `self._base_feature_history: dict[str, deque[tuple[int, dict]]]` populated in `ingest_bar()`,
  exposed via `build_context()`.
- `ai_trader/market_scanner/timeframe_sync.py` (frozen module, touched) — `build_timeframe_context()`
  gained an optional `feature_history` parameter, additive (omitted entirely for callers with no
  history to offer, so existing consumers reading only `features` are unaffected).
- `ai_trader/market_scanner/MARKET_CONTEXT_SCHEMA.json` (frozen module, touched) — new OPTIONAL
  `feature_history` array field on `TimeframeContext`, not added to `required`, so a producer omitting
  it stays schema-valid.
- `ai_trader/strategy_runtime/context_access.py` (non-frozen, extended) — new `feature_history()`,
  `feature_n_ago()`, `flag_n_ago()` helpers, index-aligned 1:1 with `bars()`, never fabricating a value
  for history that was not retained.
- Verified: full pre-existing `ai_trader/market_scanner/` test suite (127 tests) passes unchanged after
  the touch — zero regressions from the first-ever edit to a frozen module.

## 3. Migration (v0 → v1), all 43 strategies

`knowledge/strategies/{folder}/strategy.json` converted from the Research Lab's v0 export shape to
Strategy Interface v1 for all 43 strategies (originals preserved as `strategy.v0.json` in each folder,
never deleted), via one-off migration scripts (not committed, output only) reusing
`ai_trader.strategy_runtime.migration.build_v1_contract_dict`. Every migrated contract is schema-valid
and matches its own strategy_id. Live-verified: `knowledge/strategies/*/strategy.json` shows changes
confined to exactly these 43 folders; `code/` and `results/` (Research Lab) remain 0-diff.

## 4. Full active-strategy count — verified live against the real pipeline

```
StrategyManager.load_library() + registry.build_runtime_handles() against the REAL Strategy Library:
43 strategies -> real runtime handles (S1-S31 excl. gaps, S38-S51 excl. gaps)
time_stop_bars set for: S13, S14, S16, S17, S18, S19, S24, S25, S28, S45 (10)
trailing_stop_atr_mult set for: S4, S10, S15, S23, S38, S48 (6)
```

This is every strategy the frozen Research Lab marks IMPLEMENTED and runtime-eligible — none remain.
The other 8 of 51 folders (S32–S37 NOT_IMPLEMENTED, S47/S49 INVALID in the frozen v0 spec) are
correctly absent, unchanged from Wave B's start.

## 5. Testing discipline — every batch, no accumulation

Each batch received: unit tests (hand-constructed bar/feature-history sequences, no live data),
contract-migration verification (schema-valid v1), registry tests (`registry.build_runtime_handles`
shows exactly the expected active set), and — for the two new generic mechanisms — dedicated
end-to-end proof through the real six-module pipeline + Simulation Framework over real historical
XAUUSD data, with determinism re-verified (`asdict(report_a) == asdict(report_b)` for identical
`(SimulationContext, seed)`).

## 6. Pre-existing tripwires updated (documented, not a regression)

Same "tripwire fires, gets updated deliberately" pattern every prior checkpoint established:

- `ai_trader/strategy_manager/tests/test_real_library_integration.py` — `report.loaded` now asserts
  the full 43-strategy set (verified live); `len(report.failed)` updated to 36 (8 still-v0
  INVALID/NOT_IMPLEMENTED + schema-valid-but-INCOMPATIBLE under the fixture's own minimal
  `FakeScanner`). Docstring updated to note this is the FINAL count — no further strategy is expected
  to move from `failed` to `loaded` under the current Strategy Library.
- `ai_trader/strategy_runtime/tests/test_registry.py` — `CURRENT_MIGRATED_IDS` now the full 43-id set;
  `time_stop_bars` expected-set gained S25.
- `ai_trader/strategy_runtime/tests/test_checkpoint2_end_to_end.py` — `CURRENT_MIGRATED_IDS`/
  `TIME_EXIT_IDS` updated to match; harness run now also passes `enable_trailing_stops=True` so the
  six trailing-stop strategies exit correctly during this test's own real-pipeline run.
- `ai_trader/strategy_runtime/tests/test_s1_end_to_end.py` — unaffected this Wave (already isolated via
  `strategy_id_filter=frozenset({"S1"})`, the generic filtering capability added earlier this session
  to prevent 40+ strategies from crowding S1 out of the shared single-position-per-symbol slot).

## 7. Global implementation statistics (verified live this session, current HEAD)

```
pytest ai_trader/ -q
1514 passed

mypy --strict ai_trader/ --exclude 'tests/'
Success: no issues found in 158 source files

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   9392 stmts   434 miss   95%
```

## 8. Protected areas — confirmed live

- `code/`, `results/` (Research Lab) — still 0-diff (`git status --porcelain -- code/ results/` empty).
- The six live pipeline modules' production code — untouched this Wave EXCEPT the two explicitly
  CEO-approved, additive, schema-optional touches to Market Scanner (`scanner.py`, `timeframe_sync.py`,
  `MARKET_CONTEXT_SCHEMA.json`) described in §2b — every existing consumer of these modules is
  unaffected (full pre-existing test suites pass unchanged), and no other of the six modules
  (Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine) was touched at all.
- `knowledge/` — changes confined EXACTLY to the 43 migrated strategy folders; every other folder, and
  `knowledge/interface/` itself, untouched.
- Terminal holdout — SEALED, untouched. No broker code, no MT5, no Learning Engine anywhere.

## 9. Wave B verdict

**COMPLETE.** All 43 of 43 runtime-eligible strategies now have real, evidence-faithful evaluators,
tested (unit + contract-migration + registry + end-to-end), `mypy --strict` clean, 95% covered, zero
regressions, every protected invariant verified live. Two genuine research/runtime parity gaps
(trailing-stop execution, historical-feature access) were found, disclosed, designed with explicit CEO
sign-off, and resolved with generic, reusable mechanisms — neither strategy-specific, neither a
frozen-module rewrite.

**Next: Wave D** — the first full historical XAUUSD portfolio simulation with all 43 strategies active
simultaneously ($2,000 initial capital, 5% risk per trade), per the CEO's own standing instructions.
Report findings only; underperforming strategies are neither removed nor optimized at this stage.
