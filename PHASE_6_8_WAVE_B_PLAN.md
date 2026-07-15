# Phase 6.8 Wave B — Implementation Plan (planning only, NOT authorized to execute)

**Date:** 2026-07-15. **Status: PLAN ONLY.** Per CEO decision after Checkpoint 1: "Wave B will start in
a fresh session... Do not implement additional strategies. Stop after the commit and final report."
Nothing in this document has been implemented, tested, or migrated — it is the requested preparation
for whichever session the CEO next authorizes to begin Wave B.

---

## 1. Starting state (verified, Checkpoint 1)

- 43 RUNTIME-ELIGIBLE strategies (research status `IMPLEMENTED`); S1 migrated + implemented + proven
  end-to-end. **42 remain.**
- 2 INVALID (S47, S49) — remain quarantined, out of scope.
- 6 NOT_IMPLEMENTED (S32–S37) — remain disabled, out of scope.
- Generic framework READY: `ai_trader/strategy_runtime/{context_access,confirmations,risk,evaluator,
  migration,registry}.py` — every group below reuses these directly; only genuinely new shared
  mechanisms (VWAP anchoring, oscillator divergence, volume-climax, streak-counting) need a new shared
  helper module, added once and reused across that group's strategies, not duplicated per-strategy.

## 2. Grouping by shared mechanism

Grouped using the Strategy Library's OWN embedded taxonomy (`strategy.json`'s `klass` field —
"Class I–VIII" / "Batch1/2" — verified present on every real entry, not invented for this plan) plus
the shared-code-reuse lens Checkpoint 1 established. Each group lists: strategy ids, what's shared,
and what NEW helper (if any) the group needs beyond what already exists.

| # | group | ids (count) | shared mechanism | new shared helper needed |
|---|---|---|---|---|
| B1 | **Session / calendar / time-based** | S6, S16, S17, S18, S19, S24, S29, S30, S31 (9) | pure comparisons against already-computed session/calendar/level features (`session`, `blk`, `bar_in_sess`, `pdh`/`pdl`, `pw_high`/`pw_low`, `sess_high`/`sess_low`, `gap`) — no new pattern-detection logic, lowest implementation risk | none — `context_access.py` already exposes every needed feature |
| B2 | **Liquidity / sweep / reversal** (S1's own family) | S2, S11, S12, S21, S22 (5) | directly reuses `confirmations.swept_level`/`consecutive_same_direction_closes`/`rolling_extreme_touch`, `risk.executable_stop_floor` — the SAME pattern Checkpoint 1 already proved, different reference levels (equal highs/lows, round numbers, structure breaks) | none, or a small `structure.py` helper for CHoCH (S11) swing-point detection if `rmax20`/`rmin20` alone prove insufficient |
| B3 | **Value / VWAP / auction** | S26, S27, S28 (3) | all anchor to the `vwap` feature already in `M15_FEATURE_NAMES`; reclaim/rejection logic is structurally close to B2's sweep-then-reversal shape | small `vwap.py` helper (distance-from-vwap, reclaim detection) shared by all 3 |
| B4 | **Imbalance / FVG** | S13 (1) | reuses `fvg_bull`/`fvg_bear` features directly | none |
| B5 | **Candlestick / bar-pattern** | S45, S50 (2) | pure OHLC bar-shape checks (outside bar, engulfing, streak) | small `patterns.py` helper (engulfing/outside-bar detection); streak counting is a 3-line extension of `confirmations.consecutive_same_direction_closes` |
| B6 | **Order-flow proxy** | S44 (1) | intrabar close-location value from OHLC only | none (a single formula, no shared helper needed for just one strategy) |
| B7 | **Breakout / compression / continuation** | S3, S4, S5, S10, S23, S46, S48 (7) | opening-range/compression/displacement breakout confirmation; several explicitly reuse `or_high`/`or_low`/`compress`/`atr_ma`/`disp` features already present; S23 is an explicit redesign of S4 (implement together) | `breakout.py` helper (range-breakout confirmation, compression-duration tracking) |
| B8 | **Trend / pullback / momentum** | S7, S9, S14, S15, S38, S39, S43 (7) | trend-state + pullback/exhaustion/divergence logic against `m_trend_up`/`h1_trend_up`/`h4_trend_up`/`d1_trend_up`/`m_rsi`; S38 is an explicit redesign of S7/S10, S39 of S15 (implement together with their predecessors) | `trend.py` helper (pullback depth, RSI divergence, multi-timeframe alignment check) |
| B9 | **Mean-reversion / volume-driven reversal** | S8, S41, S42, S51 (4) | distance-from-mean / extreme-return / range-position reversion, some volume-gated | `mean_reversion.py` helper (z-score-style extension measure, volume-climax detection using bar volume) |
| B10 | **Composite / regime / meta** | S20, S25, S40 (3) | S20 (hybrid sweep+MTF) composes B2+B8 patterns; S25 (volatility-regime onset) pairs with B7's compression logic; S40 (regime router) explicitly ROUTES between other strategies' signals — must be implemented LAST, after the mechanisms it routes between exist | none new; composes existing group helpers |

**42 strategies, 10 groups** (B1–B10), consistent with the 43 RUNTIME-ELIGIBLE total (S1 already done).

## 3. Estimated migration order

Ordered by (a) implementation risk (simplest/lowest-risk first, to keep finding bugs cheap the way
Checkpoint 1 did) and (b) dependency (redesigns after their predecessors; the meta-router last):

1. **B1** (session/calendar, 9) — simplest, no new pattern logic, highest confidence of a clean batch.
2. **B2** (liquidity/sweep, 5) — directly extends the ALREADY-PROVEN S1 pattern; highest confidence of
   correctness given Checkpoint 1's own verification.
3. **B4** (imbalance, 1) + **B6** (order-flow proxy, 1) — trivially small groups, bundle with B2's
   checkpoint for efficiency.
4. **B3** (VWAP/value, 3) — one new small helper, moderate risk.
5. **B5** (candlestick, 2) — one new small helper, low risk (pure OHLC shape checks).
6. **B7** (breakout/compression, 7) — larger group, one substantial new helper; implement S4 and S23
   (its redesign) together.
7. **B8** (trend/momentum, 7) — largest group, one substantial new helper; implement S7/S38 and
   S15/S39 pairs together.
8. **B9** (mean-reversion/volume, 4) — one new helper.
9. **B10** (composite/meta, 3) — LAST, since S20/S25/S40 compose or route between the other groups'
   now-implemented mechanisms.

## 4. Expected checkpoints (mapping onto the CEO's own Checkpoint 2–6 structure)

- **Checkpoint 2 ("first mechanism batch integrated and conformance-tested")** = B1 + B2 (14
  strategies) — the first REAL batch beyond the S1 reference slice, exercising both the
  "trivial reuse" case (B1) and the "extend an already-proven pattern" case (B2).
- **Checkpoint 3 ("all runtime-eligible contracts migrated")** = every one of the 42 remaining
  `strategy.json` files converted v0→v1 (this can run AHEAD of evaluator implementation per strategy,
  since migration is pure data restructuring — but each contract's `required_data`/
  `required_confirmations` fields still require the same per-strategy authorial care Checkpoint 1
  used, never auto-invented).
- **Checkpoint 4 ("all runtime evaluators loaded and signal-producing")** = B3 through B9 complete
  (33 more strategies; B10 deferred to its own gate since it depends on the others).
- **Checkpoint 5 ("full-library deterministic integration test")** = B10 complete (all 43 active
  simultaneously) + the Wave C verification list from the CEO's own approval message (independent
  evaluation, no cross-strategy mutation, simultaneous BUY/SELL reaching Scoring Engine, deterministic
  ranking/conflict handling, Risk Manager receiving ranked opportunities, only approved opportunities
  producing orders).
- **Checkpoint 6 ("complete economic backtest")** = Wave D: the full historical XAUUSD run at
  $2,000 capital / 5% risk-per-trade with the complete attribution/session/regime/correlation report
  the CEO's approval message specified.

## 5. Testing strategy for batch migration

Per-strategy, not batched-and-hoped-for — the SAME rigor Checkpoint 1 used, because it is what
actually caught both real bugs:

1. **Unit tests per strategy**, hand-constructed bar sequences (mirroring
   `tests/families/test_s01_confirmed_liquidity_sweep_reversal.py`): no-setup, waiting, and actionable
   cases at minimum; a dedicated edge-case test for whatever that strategy's OWN stop/target formula
   could get wrong (Checkpoint 1's own stop-bug is the concrete precedent for why this matters).
2. **Contract migration tests**: every new v1 `strategy.json` passes `validate_contract` (schema) and
   `parse_contract` (typed) — mirrors `test_migration.py`'s own `TestS1FileOnDisk` tripwire pattern,
   extended to every migrated file.
3. **Registry tests**: after each batch, `StrategyManager.load_library()` + `build_runtime_handles()`
   against the REAL library must show exactly the expected loaded/active count for that batch — a
   direct extension of `test_registry.py`.
4. **Per-batch end-to-end proof** (not deferred to the very end): after each of the 9 remaining groups
   (B1, B2+B4+B6, B3, B5, B7, B8, B9, B10), run the group's own strategies through the real six-module
   pipeline + Simulation Framework over a real historical window and confirm: at least the strategies
   expected to be capable of a signal in that window produce one, decisions flow through Risk Manager
   sensibly, and the full test suite + `mypy --strict` + coverage stay green — exactly
   `test_s1_end_to_end.py`'s own pattern, reused per batch rather than only once at the very end.
5. **Full-suite regression check after every batch** (`pytest ai_trader/ -q`, `mypy --strict`,
   coverage) — never accumulate untested strategies across multiple batches before checking for
   regressions; Checkpoint 1's own two-bug discovery is the reason this must stay per-batch, not
   deferred.
6. **No conformance claim without a check**: per the CEO's own Wave B item 6 ("classify any divergence
   honestly"), any strategy whose runtime behavior cannot be verified against the frozen research
   engine's own convention (spread/slippage/next-open/stop-before-target — already established in
   `ai_trader/simulation/tests/test_conformance_vs_research_engine.py`'s own pattern) must be disclosed
   as such in that batch's own checkpoint report, never silently assumed conformant.

## 6. Anti-optimization discipline carried forward

Every IMPLEMENTATION CHOICE Wave B's evaluators require (stop-floor formulas, session boundaries,
confirmation windows, etc.) must be frozen from each strategy's OWN `strategy.json` spec BEFORE running
any backtest against it — never tuned after observing PnL, exactly the rule the CEO's original Phase
6.8 approval and this session's own `IMPLEMENTATION_CHOICES.md` precedent (Phase 6.7) both establish.
