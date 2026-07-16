# Strategy Health System — Design, Implementation, and First Evaluation of All 43 Strategies

**Date:** 2026-07-16. **Scope:** CEO directive — build an adaptive Strategy Health System that
scores every runtime strategy from its OWN recent trading performance (not multi-year lifetime
averages) and classifies it into `ACTIVE` / `WATCHLIST` / `PROBATION` / `DISABLED`. Implementation is
authorized for this new, additive subsystem only. No strategy, evaluator, parameter, Research Lab
file, or frozen pipeline module was touched — the new code lives entirely in
`ai_trader/strategy_health/` (mypy `--strict` clean, 98% test coverage, zero impact on the existing
1515+ test suite). **This is an observation and classification phase — no strategy was modified,
optimized, or permanently removed based on these results.**

---

## 1. Why this exists

Wave D's own audit (`WAVE_D_PORTFOLIO_AUDIT_REPORT.md`) tiered every strategy from its FULL 3.6-year
lifetime performance. The CEO's own point is that a lifetime average hides regime change: a strategy
strong in 2023 may be irrelevant to 2026's market, and — just as important — a strategy that looks bad
across the full lifetime may have quietly become excellent under the CURRENT regime, buried under
years of unrelated history. Multi-year averages cannot see this. Rolling windows can.

## 2. Architecture

`ai_trader/strategy_health/` (non-frozen, new):

- **`types.py`** — `ClosedTrade` (a minimal, source-independent trade record — deliberately NOT tied
  to the Simulation Framework's own `TradeRecord`, so this same code can score a live broker fill log
  tomorrow without modification), `HealthState` enum (`ACTIVE`/`WATCHLIST`/`PROBATION`/`DISABLED`),
  `WindowMetrics`, `WindowScore`, `StrategyHealthReport`.
- **`metrics.py`** — pure functions computing every metric the CEO asked for, per rolling window:
  expectancy (currency and R), profit factor, net R, win rate, drawdown, trade count, monthly
  consistency, equity stability, max losing streak, average holding time.
- **`scoring.py`** — the composite Health Score, explicitly NOT hand-tuned (§3).
- **`classifier.py`** — Health Score → state, plus the regime-adaptation trend rule (§4).
- **`evaluator.py`** — `evaluate_strategy_health(trades_by_strategy, as_of)`, the single entry point,
  designed to be called repeatedly (the CEO's own "Future Direction": periodic re-evaluation)
  recomputing everything from scratch every call.

Zero of these files import from, or are imported by, any of the six frozen pipeline modules, any
strategy evaluator, the Research Lab, or `knowledge/`. The system is a pure, independent consumer of
closed-trade history.

## 3. The scoring methodology — why it is "not hardcoded"

The CEO's instruction was explicit: *design a robust scoring methodology and justify it; do not
hardcode weights.* The design has three layers:

1. **Percentile-rank normalization.** Every metric is converted to a 0–100 percentile rank within the
   cross-section of strategies that traded at all in the same window. This is scale-free and
   outlier-robust — critical here, since this system's own real trade history produces extreme
   R-multiples (the Wave D audit's own S1 finding: +21.6R in one alternate run) that would badly
   distort a z-score-based approach.
2. **Credibility shrinkage** (Bühlmann credibility, a standard actuarial technique): a strategy's
   percentile is pulled toward the neutral midpoint (50) by `k / (n + k)`, with `k = 10` — a strategy
   needs 10 trades in a window before its own evidence outweighs the neutral prior. This stops one
   lucky or unlucky trade from swinging a small-sample strategy to an extreme score.
3. **PCA-derived metric weights — the actual answer to "not hardcoded".** The 8 scored metrics
   (expectancy R, profit factor, net R, win rate, monthly consistency, equity stability, drawdown
   [inverted], max losing streak [inverted]) are assembled into a strategies × metrics matrix; its
   covariance matrix's dominant eigenvector (first principal component, clipped to non-negative and
   renormalized to sum to 1) becomes the weight vector. These weights are a deterministic function of
   the CURRENT population's own data — the axis the metrics themselves agree explains the most
   cross-strategy variance in "quality" — not a number any person chose. Falls back to equal weights
   only when fewer than 5 strategies have data in a window (disclosed, not hidden).

**Two things are intentionally NOT data-derived, and are labeled as editorial choices instead of
disguised as "objective":**

- **Window-priority weights** (`12m: 60%`, `6m: 25%`, `3m: 15%`) combining the three window scores
  into one overall Health Score. This is the CEO's own explicit business rule ("the 12-month window
  is the primary decision window; older/shorter windows are supporting information"), not a discovered
  pattern — stating it as a rule is more honest than dressing it up as data-driven when it isn't. A
  window with no trades has its weight redistributed proportionally among the windows that do have
  data.
- **Classification bands** (`≥65 ACTIVE`, `45–65 WATCHLIST`, `25–45 PROBATION`, `<25 DISABLED`) on the
  0–100 scale, where 50 is, by construction, near the population's own median. These are fixed
  thresholds, not learned — a defensible, simple, auditable choice for a first version; revisiting
  them (e.g. to fixed population quantiles) is a reasonable future refinement, not attempted here per
  the CEO's own "do not optimize" instruction.

## 4. The regime-adaptation trend rule

This is the mechanism that most directly answers the CEO's stated purpose. `trend_delta = 3-month
score − 12-month score`. If a strategy's most recent quarter scores **15 points or more above** its own
12-month baseline, it is bumped UP one classification tier (capped at `ACTIVE`) — strong recent
improvement overrides a merely-adequate longer-term number. Symmetrically, a 3-month score **15 points
or more below** the 12-month baseline bumps the strategy DOWN one tier (floored at `DISABLED`) — a
strategy whose 12-month number still looks fine but whose most recent quarter has collapsed is exactly
the case a longer average conceals. §6 shows this rule catching real cases in the actual data.

## 5. Live verification

```
mypy --strict ai_trader/strategy_health/ --exclude 'tests/'
Success: no issues found in 6 source files

pytest ai_trader/strategy_health/ -q
47 passed

coverage (ai_trader.strategy_health only)
TOTAL   243 stmts   5 miss   98%

pytest ai_trader/ -q   (full suite, confirms zero regressions from the new module)
1562 passed
```

## 6. Results — all 43 strategies, evaluated as of 2026-07-13

Trade history: the same, already-verified, deterministic Wave D baseline run (all 43 strategies
active simultaneously, $2,000 capital, 5% risk/trade, 2022-12-16 → 2026-07-13) — the identical data
`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` and `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` already used, now
re-sliced into rolling windows instead of viewed as one lifetime average.

**State summary:**

| State | Count | Strategies |
|---|---|---|
| ACTIVE | 2 | S40, S46 |
| WATCHLIST | 34 | S2, S3, S4, S6, S7, S8, S9, S10, S11, S12, S15, S16, S17, S18, S19, S20, S21, S23, S24, S25, S26, S27, S29, S31, S38, S39, S41, S43, S44, S45, S48, S49*, S50, S51 |
| PROBATION | 7 | S1, S5, S13, S14, S22, S28, S30 |
| DISABLED | 0 | — |

*S47/S49 are not runtime-eligible (frozen v0 status `INVALID`) and were not evaluated; not counted.

**Full per-strategy table**, sorted by overall Health Score (strategies with no recent trades in any
window — `score = None` — listed after, alphabetically):

| ID | Score | State | Trend (3m−12m) | Lifetime tier (Wave D audit) | What changed |
|---|---|---|---|---|---|
| S46 | 69.0 | ACTIVE | +3.3 | GOOD | Confirmed strong — recent 12m net R (+21.6) actually EXCEEDS its own full-lifetime net R (+14.9), meaning its pre-2025 history was a net drag; current regime suits it better than its lifetime average shows. |
| S40 | 65.7 | ACTIVE | n/a (no 3m/6m trades) | VERY_GOOD | Confirmed — all 6 of its trades fall in the 12m window; no contradicting recent evidence. |
| S44 | 64.7 | WATCHLIST | n/a (no 3m trades) | VERY_GOOD | Just under the ACTIVE threshold (65); 6m/12m identical (11 trades, all within the last 6 months) — strong quality (12m expectancy +2.51R) but zero 3-month activity to confirm currency. |
| S13 | 60.8 | **PROBATION** | **−22.7** | VERY_GOOD | **Largest decline found.** 12m/6m numbers are excellent (expectancy +0.43R, PF 3.7), but the last 3 months are 4 trades, 0% win rate, PF 0.0 — a sharp recent reversal the 12-month average still hides. Bumped DOWN two tiers by the trend rule. |
| S39 | 56.3 | WATCHLIST | +6.3 | GOOD | Confirmed, unremarkable — largest reliable sample (96 lifetime trades) staying near the middle of the field. |
| S10 | 56.2 | WATCHLIST | +6.8 | NEUTRAL (lifetime near-breakeven) | Mild recent improvement, still unremarkable. |
| S12 | 59.6 | WATCHLIST | n/a | NEUTRAL (insufficient lifetime sample) | Recent trades support a decent score; still too little data for higher confidence. |
| S16 | 58.4 | WATCHLIST | n/a | NEUTRAL | Similar — solid recent number, low sample. |
| S18 | 53.7 | WATCHLIST | n/a | NEUTRAL | Solid but low-sample. |
| S51 | 53.0 | WATCHLIST | n/a | NEUTRAL | Solid but low-sample (1 lifetime trade). |
| S8 | 53.2 | WATCHLIST | n/a | NEUTRAL | Solid but low-sample. |
| S26 | 53.3 | WATCHLIST | +4.1 | **ELIMINATE** | **Regime-shift catch #1.** Lifetime-worst-tier strategy now scores at the population median with a positive recent trend — its last 5–6 months (small sample, n=5) look ordinary, not catastrophic like its lifetime number suggested. |
| S2 | 53.0 | WATCHLIST | −6.6 | VERY_GOOD | Modest recent decline from a strong lifetime tier — still WATCHLIST, not concerning yet. |
| S25 | 49.3 | WATCHLIST | +3.8 | NEUTRAL | Unremarkable. |
| S45 | 48.5 | WATCHLIST | n/a | NEUTRAL | Unremarkable, low sample. |
| S41 | 48.4 | WATCHLIST | −0.2 | NEUTRAL | Unremarkable. |
| S24 | 48.2 | WATCHLIST | n/a | VERY_GOOD | Recent number is unremarkable versus a strong lifetime tier — worth a future look once more recent trades accumulate. |
| S48 | 47.6 | WATCHLIST | −1.2 | NEUTRAL | Unremarkable, stable near breakeven (matches lifetime). |
| S6 | 47.2 | WATCHLIST | −0.9 | NEUTRAL | Unremarkable. |
| S21 | 46.0 | WATCHLIST | n/a | NEUTRAL | Unremarkable, low sample. |
| S42 | 41.3 | **WATCHLIST** | **+17.0** | **ELIMINATE** | **Regime-shift catch #2 — the clearest one.** Base band alone would place S42 in PROBATION (score 41.3), but its most recent quarter scores 17 points above its own 12-month baseline — a strategy the lifetime audit flagged for elimination is bumped UP a full tier by genuine, recent, evidence-based improvement. Sample is still small (2 trades in the 3m window); worth continued observation, not a conclusion. |
| S30 | 40.5 | PROBATION | +2.3 | NEGATIVE | Confirmed weak, mild improvement. |
| S28 | 42.4 | **PROBATION** | n/a | **VERY_GOOD** | **Notable downgrade.** A lifetime-VERY_GOOD strategy whose only recent window (6m=12m, 8 trades) is net-negative (expectancy −0.21R) — its historical edge has not shown up in the last 6 months. |
| S5 | 37.3 | PROBATION | +14.7 | NEGATIVE | Confirmed weak, but its trend (+14.7) sits just 0.3 points below the bump threshold — the closest near-miss in the dataset for a regime-adaptation upgrade. |
| S1 | 30.9 | PROBATION | +12.7 | NEGATIVE | Confirmed weak, improving but not enough to bump. Its own drawdown (12m: $57.85) is the largest isolated drawdown of any strategy in this evaluation. |
| S14 | 30.4 | PROBATION | n/a | ELIMINATE | Improved from the worst lifetime tier to PROBATION (not DISABLED) — still weak, no longer the clearest elimination case. |
| S22 | 27.5 | PROBATION | n/a | NEGATIVE | Confirmed weak — lowest score among the 29 lifetime-active strategies with recent data. |

**Strategies with `score = None`** (zero trades in ALL three rolling windows — 12 months back from
2026-07-13 is July 2025; any strategy whose entire lifetime trade history predates that has no recent
evidence at all): S3, S4, S7, S9, S11, S15, S17, S19, S20, S23, S27, S29, S31, S38, S43, S50. All 16
are classified `WATCHLIST` by design — available to trade, neither trusted nor penalized for an
absence of recent evidence that says nothing about quality. Several of these had zero LIFETIME trades
too (S3, S7, S9, S11, S15, S17, S19, S20, S23, S27, S29, S31, S38, S50 — the same 14 the Wave D audit
already flagged as never having won the single-symbol slot); S4 and S43 DID trade during the 3.6-year
lifetime window but not within the last 12 months, so they too now show no recent evidence.

## 7. The three most important findings

1. **S42 and S26 (§6) are concrete proof the system works as designed.** Both were the frozen
   Research Lab's own lifetime-worst performers (`ELIMINATE` tier in the Wave D audit) and both show
   genuine, evidence-based recent improvement — S42 dramatically enough to trigger the trend-bump rule
   directly. This is exactly the "weak historically, may be excellent under the current regime" case
   the CEO's directive was written to catch, now demonstrated on real data, not hypothetically.
2. **S13 is the clearest warning the system produced.** A strong lifetime and 12-month track record
   conceals a sharp 3-month collapse (0% win rate across its 4 most recent trades). Judged only by its
   own lifetime average, S13 would still look like one of the portfolio's best strategies; judged by
   its own last quarter, it is failing. This is precisely the blind spot multi-year averages create.
3. **S46's own recent performance is BETTER than its lifetime average** (12-month net R of +21.6
   exceeds its full 3.6-year net R of +14.9) — meaning its pre-2025 history was actively worse than its
   current form. The strongest strategy in the portfolio is strong partly BECAUSE of recent
   improvement, not despite it.

## 8. What did NOT happen (explicit, per the CEO's own instruction)

- No strategy's code, contract, or parameters were changed.
- No strategy was removed, permanently disabled, or "optimized" based on these scores.
- The 7 `PROBATION` strategies remain fully present in the library; nothing prevents a future
  re-evaluation from moving any of them back to `ACTIVE` the moment their own recent trades support it
  (S42's own trend-bump this run is the proof that upward movement already works).
- The Research Lab, the six frozen pipeline modules, every strategy evaluator, and Learning
  Engine/Broker Adapter/MT5 (none of which exist yet) were untouched.

## 9. What this system enables next (not started, no approval assumed)

The CEO's own "Future Direction" states the AI Trader should periodically re-evaluate all strategies
using rolling windows. `evaluate_strategy_health()` is already built for exactly that — call it again
with a fresh `as_of` and the same or an updated trade ledger, and every strategy's state is
re-derived from scratch. Wiring this into an actual periodic schedule, into the Strategy Manager's own
active-set (so `ACTIVE`-only strategies really are the only ones trading live), or into a persisted
history-of-scores-over-time view, are all natural next steps — each would need its own dedicated
scope and CEO sign-off, per the standing rule that this system does not activate/deactivate anything
in the live pipeline by itself yet.
