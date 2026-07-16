# Phase 6.9 — Rolling Health-Gated Backtest — Validation Report

**Date:** 2026-07-16. **Classification: VALID NEGATIVE RESULT — METHODOLOGY NOT OPERATIONALLY VIABLE
AS SPECIFIED.**

**CEO directive under which this phase closed:** test the frozen Rolling Health-Gated methodology
honestly; do not loosen thresholds, change Health weights, change credibility shrinkage, activate
WATCHLIST strategies retroactively, rerun alternative methodologies, or optimize based on the observed
outcome. This report complies with that directive in full — every number below comes from the
methodology exactly as frozen in `ROLLING_HEALTH_BACKTEST_HANDOFF.md` §8 and the Strategy Health
System as built in the prior session (`STRATEGY_HEALTH_SYSTEM_REPORT.md`). Nothing was retuned after
seeing results.

---

## 0. One-paragraph summary

The Rolling Health-Gated Backtest was implemented exactly to specification, ran deterministically, and
produced a valid, honest, negative result: **the ACTIVE roster was empty at every one of the 32
monthly checkpoints from month 13 onward.** The rolling-gated portfolio traded only during the
12-month ungated bootstrap (71 trades, 2022-12 → 2023-12) and then went completely silent for the
remaining ~2.6 years of the backtest (2024-01 → 2026-07-13). This is not a bug — the static baseline
reproduced Wave D's own documented result exactly, the rolling run was proven byte-for-byte
deterministic across two independent passes, and the anti-lookahead property was proven
programmatically. The methodology's own frozen scoring mechanics, applied to a single-symbol,
low-trade-frequency strategy population, structurally cannot promote any strategy to ACTIVE once the
bootstrap's own trade evidence ages out of the rolling windows — a self-reinforcing lockout, detailed in
§7.

---

## 1. Scope and what changed in the codebase

Per `ROLLING_HEALTH_BACKTEST_HANDOFF.md` §8.4 ("frozen assumptions"), **nothing about the Strategy
Health System's own scoring methodology, strategy contracts, strategy evaluators, Research Lab, or the
six frozen pipeline modules was touched.** The only code changes this phase made:

1. **`ai_trader/simulation/harness.py`** — a CEO-approved (2026-07-16), additive, backward-compatible
   fix: `strategy_id_filter` now gates NEW-signal eligibility only. Time-stop/trailing-stop overlay
   eligibility for an already-open position is derived from the UNFILTERED runtime strategy set, so a
   demoted strategy's existing position keeps its own declared stop/target/time-stop/trailing-stop
   protection until it closes naturally — it just can't open a new one. Byte-identical to the pre-fix
   code whenever `strategy_id_filter is None` (proven both by construction — `overlay_handles is
   handles` in that case, no new call — and empirically, by the full pre-existing regression suite
   passing unchanged, §8). 3 new regression tests added
   (`ai_trader/simulation/tests/test_overlay_survives_demotion.py`) proving: (a) a demoted strategy is
   absent from new-signal handles but present in the unfiltered overlay set; (b) its open position
   still closes via its own declared time-stop; (c) its open position still closes via its own declared
   trailing-stop.
2. **`ai_trader/strategy_health/rolling_gate.py`** (NEW, permanent) — a thin, pure wrapper around the
   existing, unmodified `evaluate_strategy_health()`: `active_strategy_ids_at()` returns the
   ACTIVE-classified strategy id subset at a checkpoint; `health_reports_at()` exposes the full reports
   for orchestration/analysis. No new scoring logic. 3 new unit tests
   (`ai_trader/strategy_health/tests/test_rolling_gate.py`).
3. **`ai_trader/strategy_health/tests/test_anti_lookahead.py`** (NEW) — 3 tests proving the single most
   important correctness property of this phase (§8.3.3, detail in §8 below).
4. **`phase69_rolling_backtest.py`, `phase69_analysis.py`, `phase69_analysis2.py`** (repo root,
   diagnostic scripts) and **`phase69_results.json`, `phase69_analysis.json`, `phase69_analysis2.json`**
   (repo root, raw diagnostic data) — preserved per explicit CEO instruction ("preserve all artifacts
   and diagnostics"), unlike prior phases' scratch scripts which were deleted after report capture.
   These are the actual orchestrator/analysis code and raw output this report is built from — kept for
   full reproducibility.

No Research Lab, strategy contract, strategy evaluator, or frozen-pipeline-module change of any kind.

---

## 2. Run configuration

Identical to Wave D's own documented configuration (`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` §1) in
every respect except the health-gating mechanism itself:

```
date_range:        2022-12-16 -> 2026-07-13  (1,671,187,500 -> 1,783,922,400 epoch seconds, ~3.6 years)
symbols:            ("XAUUSD",); timeframes: ("M15", "H1", "H4", "D1"); warmup_bars: 200
starting_balance:   $2,000.00; run_seed: 1
use_strategy_runtime: True (43 runtime-eligible strategies, auto_admit_min_maturity="EXPLORATORY")
enable_time_stops:  True; enable_trailing_stops: True
RiskConfig.sizing.risk_per_trade_pct: 0.05 (5%, matches Wave D)
RiskConfig.filters.reference_spread["XAUUSD"] = 0.10; liquidity_floor["XAUUSD"] = 1.0
```

**Bootstrap:** first 365 days (2022-12-16 → 2023-12-16) ungated, `strategy_id_filter=None` — identical
to the static baseline's own behavior for this period.

**Checkpoint cadence:** fixed 30-day "months" (not calendar months, for determinism, per §8.2) starting
at day 365, continuing to the end of the run — **32 monthly checkpoints** (2023-12-16 → 2026-07-03).

**Roster mechanics:** ONE continuous `SimulationHarness` (never re-instantiated — this preserves
Market Scanner's own session/weekly/day-of-week anchor state exactly as continuously as the static
baseline, avoiding the warmup-discontinuity risk that independently re-running per-month harnesses
would introduce). At each checkpoint, `harness._strategy_id_filter` is mutated to the
`ACTIVE`-classified id set returned by `active_strategy_ids_at()`, computed from every trade closed so
far. A checkpoint's own new roster takes effect starting the NEXT bar (the checkpoint's own bar still
executes under the prior roster) — the same one-bar-lag convention every other mechanism in this
Simulation Framework already uses.

---

## 3. A. Static baseline (all 43 strategies, `strategy_id_filter=None`)

Reproduced fresh in this session as a config-correctness cross-check.

| Metric | Value | Wave D's own documented value |
|---|---|---|
| Trades | **513** | 513 |
| Win rate | 39.77% | 39.77% |
| Expectancy | +0.1787 R (+$0.611/trade) | +0.179 R (+$0.611/trade) |
| Profit factor | 1.264 | 1.264 |
| Payoff ratio | 1.915 | 1.915 |
| Net profit | **+$313.21** | +$313.21 |
| Return | **+15.66%** | +15.66% |
| CAGR | 4.157% | 4.16% |
| Max drawdown | 6.159% | 6.16% |
| Recovery factor | 2.543 | 2.543 |
| Calmar ratio | 0.675 | 0.675 |
| Sharpe | 1.1965 | 1.196 |
| Sortino | 1.3718 | 1.372 |
| Max losing streak | 11 | 11 |
| Avg holding period | 173.2 bars | 173.2 bars |
| Avg exposure | 87.7% of bars | 87.7% |
| Turnover | 106.4 | 106.4 |
| Long / Short trades | 306 / 207 | 306 / 207 |
| Long / Short net PnL | +$360.43 / -$47.22 | +$360.43 / -$47.22 |

**Exact match to every figure in `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` §2**, confirming: (a) this
session's reconstructed `RiskConfig`/`SimulationContext` is identical to Wave D's own (undocumented,
scratch-script) configuration; (b) the harness.py overlay-isolation fix is empirically byte-identical
to pre-fix behavior when no filter is active, on the single most consequential real workload in this
codebase.

---

## 4. B. Rolling Health-Gated backtest

| Metric | Value |
|---|---|
| Trades | **71** (all in the bootstrap period; zero from 2024-01 onward) |
| Win rate | 39.44% |
| Expectancy | +0.326 R (+$1.181/trade) |
| Profit factor | 1.453 |
| Payoff ratio | 2.231 |
| Net profit | **+$83.87** |
| Return | **+4.19%** |
| CAGR | 1.157% |
| Max drawdown | 4.204% |
| Recovery factor | 0.998 |
| Calmar ratio | 0.275 |
| Sharpe | 0.832 |
| Sortino | 0.533 |
| Max losing streak | 8 |
| Avg holding period | 355.2 bars (~2x the static baseline's own 173.2) |
| Avg exposure | 25.0% of bars (vs 87.7% static) |
| Turnover | 14.0 (vs 106.4 static) |
| Long / Short trades | 42 / 29 |
| Long / Short net PnL | +$71.03 / +$12.84 |

**Monthly trade distribution (every month with a trade):**

| Month | Trades | Net PnL |
|---|---|---|
| 2022-12 | 5 | -$12.89 |
| 2023-01 | 4 | +$10.16 |
| 2023-02 | 5 | +$33.05 |
| 2023-03 | 9 | +$52.65 |
| 2023-04 | 5 | -$17.28 |
| 2023-05 | 7 | -$14.66 |
| 2023-06 | 7 | -$25.92 |
| 2023-07 | 5 | -$4.49 |
| 2023-08 | 1 | -$3.18 |
| 2023-09 | 1 | +$12.55 |
| 2023-10 | 7 | +$41.61 |
| 2023-11 | 8 | -$17.57 |
| 2023-12 | 7 | +$29.86 |
| **2024-01 → 2026-07** | **0** | **$0.00** |

All 71 trades close on or before 2023-12-16 (the bootstrap boundary) or in its immediate vicinity.
**Not one trade occurs in the ~2.6 years after the first gating checkpoint.**

---

## 5. ACTIVE / WATCHLIST / PROBATION / DISABLED counts at every checkpoint

"Zero-evidence" = number of strategies with `overall_score = None` (no trades in any of the 3/6/12-month
windows at that checkpoint — automatically classified WATCHLIST for lack of evidence, per
`classifier.py`'s own documented rule, never penalized).

| Checkpoint | ACTIVE | WATCHLIST | PROBATION | DISABLED | Zero-evidence |
|---|---|---|---|---|---|
| 2023-12-16 | 0 | 42 | 1 | 0 | 39 |
| 2024-01-15 | 0 | 42 | 1 | 0 | 39 |
| 2024-02-14 | 0 | 43 | 0 | 0 | 39 |
| 2024-03-15 | 0 | 42 | 1 | 0 | 39 |
| 2024-04-14 | 0 | 42 | 1 | 0 | 39 |
| 2024-05-14 | 0 | 42 | 1 | 0 | 39 |
| 2024-06-13 | 0 | 42 | 1 | 0 | 39 |
| 2024-07-13 | 0 | 42 | 1 | 0 | 39 |
| 2024-08-12 | 0 | 42 | 1 | 0 | 39 |
| 2024-09-11 | 0 | 42 | 1 | 0 | 39 |
| 2024-10-11 | 0 | 42 | 1 | 0 | 40 |
| 2024-11-10 | 0 | 42 | 1 | 0 | 41 |
| 2024-12-10 | 0 | 43 | 0 | 0 | 41 |
| **2025-01-09** | 0 | 43 | 0 | 0 | **43 (first all-zero-evidence checkpoint)** |
| 2025-02-08 | 0 | 43 | 0 | 0 | 43 |
| 2025-03-10 | 0 | 43 | 0 | 0 | 43 |
| 2025-04-09 | 0 | 43 | 0 | 0 | 43 |
| 2025-05-09 | 0 | 43 | 0 | 0 | 43 |
| 2025-06-08 | 0 | 43 | 0 | 0 | 43 |
| 2025-07-08 | 0 | 43 | 0 | 0 | 43 |
| 2025-08-07 | 0 | 43 | 0 | 0 | 43 |
| 2025-09-06 | 0 | 43 | 0 | 0 | 43 |
| 2025-10-06 | 0 | 43 | 0 | 0 | 43 |
| 2025-11-05 | 0 | 43 | 0 | 0 | 43 |
| 2025-12-05 | 0 | 43 | 0 | 0 | 43 |
| 2026-01-04 | 0 | 43 | 0 | 0 | 43 |
| 2026-02-03 | 0 | 43 | 0 | 0 | 43 |
| 2026-03-05 | 0 | 43 | 0 | 0 | 43 |
| 2026-04-04 | 0 | 43 | 0 | 0 | 43 |
| 2026-05-04 | 0 | 43 | 0 | 0 | 43 |
| 2026-06-03 | 0 | 43 | 0 | 0 | 43 |
| 2026-07-03 | 0 | 43 | 0 | 0 | 43 |

**ACTIVE = 0 at all 32 checkpoints. DISABLED = 0 at all 32 checkpoints** (nobody ever accumulated
enough evidence to be judged badly either — the population never had enough trades to be penalized,
only enough to sit at "no evidence"). The single PROBATION classification (present at 9 of the first 13
checkpoints, gone by 2024-02-14 and never seen again after 2024-12-10) belongs to one strategy with a
short-lived run of early evidence that itself aged out.

**Promotions across the whole 32-checkpoint schedule: 0. Demotions: 0. ACTIVE turnover: 0.0 per
transition. Average ACTIVE lifetime: undefined (zero ACTIVE spells ever occurred).** The rolling-gate
mechanism, once triggered, never had anything to gate again.

---

## 6. Trade counts per strategy, per rolling window, and the sample-size distribution

**Lifetime (full 3.6-year static baseline), for context:**

| | |
|---|---|
| Strategies with ≥1 lifetime trade | 29 / 43 |
| Strategies with **zero** lifetime trades | **14 / 43** |
| Mean lifetime trades/strategy | 17.7 |
| Median lifetime trades/strategy | 7 |
| Strategies with ≥10 lifetime trades (the `CREDIBILITY_K` reference size) | **13 / 43** |

Top 5 by lifetime trade count: S46 (144), S39 (96), S1 (49), S22 (31), S5 (23). Bottom of the
distribution: S41/S45/S51 (1 each), S4/S21/S43 (2 each) — the strategy population is heavily
right-skewed; most strategies trade XAUUSD only a handful of times across the ENTIRE 3.6-year history,
because only one position may be open on this single symbol at a time (the same single-shared-slot
architecture already documented in `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` §1).

**Rolling 12-month window, at the very first gating checkpoint (2023-12-16 — the single checkpoint
with the MOST evidence of any post-bootstrap checkpoint, since the bootstrap's own trades have not yet
begun aging out):**

| Strategy | Trades in the 12m window |
|---|---|
| S46 | 48 |
| S39 | 17 |
| S1 | 4 |
| S25 | 1 |
| *(all other 39 strategies)* | **0** |

Only 4 of 43 strategies have ANY trade evidence at all at this, the most favorable possible checkpoint.
**Zero strategies clear the ACTIVE band (score ≥ 65) even here** — including S46 and S39, whose
credibility weights (`n/(n+10)` = 0.828 and 0.630 respectively) are high enough that shrinkage alone
does not explain their non-promotion; their own actual blended Health Score, computed from real
metrics, simply does not reach 65 at this checkpoint.

---

## 7. Exact reason no strategy ever crossed the ACTIVE threshold

Two distinct, sequential mechanisms, both already-disclosed properties of the frozen methodology
(`ROLLING_HEALTH_BACKTEST_HANDOFF.md` §7) — this run is the first time either has been observed
end-to-end:

**Phase 1 — insufficient rolling evidence, even at the best-case checkpoint (2023-12-16 → roughly
2024-12).** 39 of 43 strategies have literally zero trades in any rolling window. Of the remaining 4,
credibility shrinkage (`credibility_weight(n) = n/(n+10)`, `CREDIBILITY_K=10`) pulls even the
best-populated ones (S46: 48 trades, S39: 17 trades) partway toward the neutral percentile of 50 — but
even without shrinkage, neither strategy's own actual metrics blend to a score ≥ 65 at this checkpoint.
The ACTIVE bar is high (65th percentile-equivalent) and the 12-month window carries 60% of the blended
weight (`WINDOW_PRIORITY`); a strategy needs both real trade volume AND standout performance within
that specific rolling slice to clear it, and none did.

**Phase 2 — self-reinforcing lockout (2025-01-09 onward, the remaining ~19 months of the backtest).**
Because ACTIVE was already empty from month 13, **no new trades were ever generated** anywhere in the
portfolio. Once the bootstrap's own 71 trades age out of even the 12-month (365-day) rolling window —
which happens by construction roughly 12 months after the bootstrap trades stopped, i.e. around
2025-01 — **every one of the 43 strategies simultaneously has zero trades in all three windows**,
confirmed exactly: 2025-01-09 is the first checkpoint where all 43 strategies show
`overall_score = None`, and every checkpoint from there to the end of the backtest (18 more monthly
re-evaluations) shows the same. With no evidence anywhere, `classify()`'s own explicit rule places
every strategy on WATCHLIST — not because any of them performed badly, but because the gating
mechanism that excluded them from trading is the SAME mechanism that prevented them from ever
generating the evidence needed to re-enter. **This is an absorbing state**: once the ACTIVE roster
reaches zero on a single-symbol, low-frequency population, it can never recover on its own, because
recovery requires new trades and new trades require ACTIVE status.

This is the "exact reason" requested: not a scoring bug, not a threshold that happens to be set too
high by chance, but a structural interaction between (a) a strategy population that trades a shared
single-symbol slot too rarely to populate rolling (as opposed to lifetime) windows, and (b) a gating
mechanism whose only source of new evidence is the trading it itself permits.

---

## 8. Determinism evidence

Two full, independent 3.6-year rolling-gated runs (`PHASE69-ROLLING-1`, `PHASE69-ROLLING-2`), same
`SimulationContext`/`run_seed=1`/checkpoint schedule, executed back-to-back in the same process:

- `asdict`-equivalent full performance dict (`portfolio_summary` + `performance` + `attribution` +
  `monthly` + `risk_events`) — **byte-identical** between the two runs.
- The full 32-checkpoint roster history (every strategy's state, trend delta, 12-month confidence, and
  overall score, at every checkpoint) — **byte-identical** between the two runs.

Both assertions are enforced programmatically in `phase69_rolling_backtest.py::main()` and both passed
on the actual full-scale run (not a toy fixture) — see §1 for the script's preserved location.

---

## 9. Anti-lookahead evidence

`ai_trader/strategy_health/tests/test_anti_lookahead.py` (3 tests, all passing) proves, against a
realistic, multi-strategy (all 43 ids), multi-year (spanning the full Wave D date range), fixed-seed
synthetic trade ledger:

1. At four checkpoints spanning the bootstrap boundary, mid-run, and near the very end, evaluating
   `evaluate_strategy_health()` on a ledger PRE-TRUNCATED to `exit_as_of <= as_of` produces a
   byte-identical `StrategyHealthReport` (every window's metrics, scores, overall score, trend delta,
   state, and rationale) to evaluating on the FULL, untruncated ledger (including trades far in the
   future of that checkpoint).
2. Appending a single future trade (30 days after a fixed checkpoint) to every strategy's ledger and
   re-evaluating at the SAME checkpoint produces byte-identical reports to the pre-addition baseline.
3. A strategy whose ONLY trades close after `as_of` scores identically to a strategy with a genuinely
   empty ledger.

This is proven true by construction (`metrics.trades_in_window` already filters every window by
`start <= exit_as_of <= as_of`), and now also proven programmatically against realistic data shapes, as
the CEO's own directive required (§8.3.3) rather than merely assumed from tiny synthetic unit fixtures.

---

## 10. Opportunity cost of the empty roster

| | Static (A) | Rolling-gated (B) | Δ |
|---|---|---|---|
| Trades | 513 | 71 | **-86.2%** |
| Turnover | 106.4 | 14.0 | **-86.8%** |
| Avg exposure (% of bars with an open position) | 87.7% | 25.0% | **-71.5%** |
| Net profit | +$313.21 | +$83.87 | **-73.2%** |
| Return | +15.66% | +4.19% | **-73.2%** |
| CAGR | 4.16% | 1.16% | **-72.2%** |

The rolling-gated portfolio captured roughly **one-quarter of the static baseline's own return**, having
participated in the market for only a quarter of the time the static portfolio did — almost entirely
because it stopped participating altogether for 2.6 of its 3.6 years, not because its own per-trade
quality was worse (see §11).

---

## 11. Additional analysis (the CEO's own specific questions)

- **Does the adaptive portfolio reduce drawdown?** Yes — 4.20% vs 6.16% max drawdown (-31.8%
  relative). But this reduction is a direct, mechanical byproduct of trading far less, not evidence the
  gate avoided genuinely bad periods (there were no genuinely bad periods to avoid post-bootstrap —
  there was no trading at all to be good or bad).
- **Does it improve stability?** No, by the standard risk-adjusted measures: Sharpe 0.83 (vs 1.20
  static), Sortino 0.53 (vs 1.37 static), Calmar 0.275 (vs 0.675 static), recovery factor 0.998 (vs
  2.543 static) are all WORSE for the rolling-gated portfolio. Its own per-trade metrics are better
  (expectancy +0.326R vs +0.179R; profit factor 1.453 vs 1.264; payoff ratio 2.231 vs 1.915) — but a
  small number of good trades followed by 2.6 years of complete inactivity does not produce a smoother
  equity curve in aggregate risk-adjusted terms; it produces a curve that rises briefly then goes flat.
- **Does it sacrifice too much opportunity?** Yes, decisively — see §10. 86% fewer trades, 87% less
  turnover, 72% less absolute return.
- **Which strategies spend the most time ACTIVE?** None — every strategy spent exactly 0 of the 32
  checkpoints ACTIVE.
- **Which strategies oscillate excessively between ACTIVE and PROBATION?** None oscillate at all in the
  ACTIVE/PROBATION sense (ACTIVE never occurred). One strategy (the same one behind the single
  PROBATION count in §5) transitioned WATCHLIST↔PROBATION 3 times before settling permanently on
  WATCHLIST once its own evidence aged out — the only strategy with any state transitions whatsoever
  across all 32 checkpoints.
- **Are Health decisions statistically robust given each strategy's sample size?** The question is
  moot in the strict sense the CEO asked it (no ACTIVE decision was ever made to be robust or fragile),
  but the underlying sample sizes were themselves the proximate cause of every non-promotion: even the
  single most-traded strategy (S46, 144 lifetime trades) has only 48 trades in its best-ever 12-month
  rolling slice — below what this system's own credibility formula treats as fully reliable evidence
  (`credibility_weight(48) = 0.828`, meaning even S46's own strongest rolling window is still ~17%
  shrunk toward the neutral prior).
- **Regime-adaptation trend-rule signal count** (§5.5's own ≥15-point trend-bump mechanism, a distinct
  concept from a roster-level "regime change"): fired **exactly once** across the entire 32-checkpoint
  schedule (one strong-improvement bump, zero strong-decline bumps) — consistent with a population that
  mostly has no evidence to show a trend in either direction.

---

## 12. Verification

```
pytest ai_trader/ -q
1571 passed   (1562 baseline + 9 new: 3 overlay-isolation, 3 anti-lookahead, 3 rolling-gate wrapper)

mypy --strict ai_trader/ --exclude 'tests/'
Success: no issues found in 165 source files   (164 baseline + 1 new: rolling_gate.py)

coverage run --source=ai_trader -m pytest ai_trader/ -q
coverage report --omit="*/tests/*"
TOTAL   9648 stmts   432 miss   96%   (rolling_gate.py itself: 100%)
```

All three verified live in this session. Protected invariants confirmed: `code/`, `results/` (Research
Lab) untouched; `knowledge/` untouched; the six frozen pipeline modules' production code untouched; the
Strategy Health System's own scoring methodology (`types.py`/`metrics.py`/`scoring.py`/`classifier.py`/
`evaluator.py`) byte-for-byte unmodified. The only production-code change anywhere is the disclosed,
additive `harness.py` overlay-isolation fix (§1).

---

## 13. Final classification

**VALID NEGATIVE RESULT — METHODOLOGY NOT OPERATIONALLY VIABLE AS SPECIFIED.**

The Rolling Health-Gated methodology, exactly as frozen and specified in `ROLLING_HEALTH_BACKTEST_
HANDOFF.md` §8, is not operationally viable for a single-symbol (XAUUSD), 43-strategy population whose
lifetime trade frequency (median 7 trades/strategy over 3.6 years) is too sparse to populate rolling
3/6/12-month evaluation windows. The mechanism is correct, deterministic, and lookahead-safe; the
population it was tested against cannot supply it with enough rolling evidence to ever promote a
strategy to ACTIVE, and once the roster empties, it cannot recover on its own. No threshold, weight, or
shrinkage parameter was altered to reach or avoid this conclusion.

---

## 14. Recommended next phase (not started, not implemented, no selection made)

**Phase 6.10 — Sparse-Evidence Strategy Governance Design.** A future, separately-scoped design phase
(no implementation authorized by this report) to study, without committing to any one approach:

- ACTIVE + WATCHLIST with differentiated risk (rather than a hard ACTIVE/not-ACTIVE gate).
- Hierarchical/Bayesian pooling of evidence across related strategies.
- Longer evidence windows (beyond 12 months).
- A minimum exploration allocation (guaranteed small size/frequency for WATCHLIST strategies, so
  evidence can still accumulate without full ACTIVE trading rights).
- Portfolio-level rather than per-strategy Health scoring.
- Shadow-mode evidence accumulation (paper-track WATCHLIST/PROBATION strategies' hypothetical signals
  without real capital, to keep evidence flowing without the self-reinforcing lockout found here).
- Regime-conditioned evidence (weighting trades by market-regime similarity rather than pure recency).
- Keeping incumbent (previously-ACTIVE) strategies active until sufficient NEGATIVE evidence
  accumulates against them, rather than requiring fresh positive evidence to re-qualify.

No alternative has been selected or implemented. This list is a starting menu for the CEO's own future
scoping decision.
