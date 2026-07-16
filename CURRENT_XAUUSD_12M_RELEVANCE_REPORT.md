# Current XAUUSD 12-Month Relevance Audit

**Date:** 2026-07-16. **Scope: a current-market relevance audit only** — NOT a rolling gate, NOT a
multi-year aggregate, NOT an optimization or tuning exercise. Nothing about the Strategy Health
System's own scoring methodology, strategy contracts, strategy evaluators, Research Lab logic, Scoring
weights, Risk Policy, or execution rules was modified. This report reuses existing, frozen,
already-tested infrastructure read-only (`ai_trader.strategy_health.metrics.compute_window_metrics`,
`ai_trader.strategy_health.scoring.score_window`, `ai_trader.simulation.performance_analyzer`) plus
one new, disclosed, reporting-only volatility-regime proxy computed directly from raw price data (§3).
No live trading, Telegram, Broker Adapter, or MT5 work was started.

---

## 1. Analysis window — decided before running anything

**Window used: 2024-10-23 09:00:00 UTC → 2025-10-23 09:00:00 UTC (exactly 365 days, 23,639 M15
bars).**

**A conflict in the instructions, resolved and disclosed up front.** The CEO asked for "the most
recent completed 12 months" but also explicitly forbade using the sealed terminal holdout. These two
requirements cannot both be satisfied literally: the sealed holdout is the **last 20% of the entire
M15 series** (`docs/S21_S40_IMPLEMENTATION_REPORTS.md`: "holdout = last 20% SEALED"; `PROJECT_STATE_
v1.0.md`: "Terminal holdout (last 20% M15, 16,831 bars): SEALED — never opened"), and it starts at
**2025-10-23 09:15 UTC** and runs to the dataset's own last bar, **2026-07-13 06:00 UTC** — i.e. the
literal most recent 12 months of ALL available data (which would end 2026-07-13) overlaps the sealed
holdout by roughly 8.6 of its 12 months. Per the explicit, repeatedly-stated "do not use the sealed
holdout" rule (and this repository's own standing discipline that opening it requires its own
dedicated CEO gate), this audit instead uses **the most recent COMPLETE 12 months that lie entirely
within the non-sealed 80% of the dataset** — ending at the last non-sealed bar and running back
exactly 365 days.

| | |
|---|---|
| Start date | 2024-10-23 09:00:00 UTC |
| End date | 2025-10-23 09:00:00 UTC |
| Number of bars (M15) | 23,639 |
| Number of trades (portfolio A, all 43 strategies) | 142 |
| Final partial month included/excluded? | The window's own end (2025-10-23) is not a calendar-month boundary — it is the last non-sealed bar, chosen deliberately (see above), not a "today's date" boundary. In calendar terms, October 2025 is included only through the 23rd (partial); October 2024 is symmetrically partial at the start. This is a fixed 365-day window, not a calendar-month window — the same "fixed day-count, not calendar months" convention the Strategy Health System's own `WINDOW_DAYS` already uses, for the same determinism reason. |
| Sealed holdout | Entirely excluded — 0 bars of this window fall inside 2025-10-23 09:15 UTC → 2026-07-13 06:00 UTC. |
| **Fully out-of-sample relative to prior tuning?** | **No — the opposite.** Of this window's 23,639 bars: **~28.8% (6,809 bars, 2024-10-23 → 2025-02-06) is inside the Research Lab's own RESEARCH (in-sample/fitting) segment**; **~71.2% (16,830 bars, 2025-02-06 → 2025-10-23) is the Research Lab's own entire VALIDATION/OOS segment** (data the discovery pipeline already loaded and used as an out-of-sample check while discovering/screening the 43 strategies). This window should NOT be read as fresh, unseen evidence — it is mostly the Lab's own validation slice plus a real chunk of its own fitting slice. **The only genuinely never-seen data in the whole repository is the sealed holdout itself, which this audit does not use.** |

**Practical consequence, stated plainly:** this audit cannot show what these 43 strategies would do in
market conditions nobody has looked at yet — it shows how they performed over data the discovery
process was substantially already exposed to. Treat every "current relevance" classification below as
informative, not as proof of forward-looking edge.

---

## 2. Per-strategy 12-month metrics (all 43 strategies, none hidden)

**Methodology**: every metric below comes from `ai_trader.strategy_health.metrics.compute_window_
metrics()` called with `window="12m"`, `as_of=2025-10-23 09:00 UTC`, on the REAL trade ledger produced
by a fresh, standalone `SimulationHarness` run scoped to exactly this window (`strategy_id_filter=
None`, all 43 strategies competing for the single XAUUSD slot — "Portfolio A" in §4). This is the
SAME frozen function the Strategy Health System already uses for its own rolling windows — reused
read-only, not modified, not redesigned.

**Sample sufficiency** (reuses the Health System's own existing `CREDIBILITY_K=10` reference sample
size — not a new number invented for this report): `SUFFICIENT` ≥ 10 trades, `LIMITED` 5–9 trades,
`INSUFFICIENT` < 5 trades. **A strategy with INSUFFICIENT sample is never labeled good or bad** — see
§3.

| Strategy | Trades | Buy | Sell | Win | Loss | Win% | ExpR | NetR | PF | NetPnL($) | Contrib% | MaxDD($) | MaxLossStreak | MonthCons | ActiveMo | AvgHold(bars) | Sufficiency | Score | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 14 | 14 | 0 | 3 | 11 | 21.4 | 0.209 | 2.926 | 0.881 | -3.67 | -5.9 | 16.76 | 5 | 0.20 | 5 | 84.6 | SUFFICIENT | 31.5 | CURRENTLY_WEAK |
| S2 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S3 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S4 | 2 | 2 | 0 | 1 | 1 | 50.0 | -0.247 | -0.494 | 0.506 | -0.63 | -1.0 | 1.28 | 1 | 0.00 | 1 | 1.5 | INSUFFICIENT | 50.0 | INSUFFICIENT_EVIDENCE |
| S5 | 2 | 2 | 0 | 1 | 1 | 50.0 | 0.581 | 1.163 | 2.162 | 2.33 | 3.7 | 2.00 | 1 | 1.00 | 1 | 19.0 | INSUFFICIENT | 50.6 | INSUFFICIENT_EVIDENCE |
| S6 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S7 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S8 | 2 | 2 | 0 | 2 | 0 | 100.0 | 2.279 | 4.559 | — | 9.66 | 15.5 | 0.00 | 0 | 1.00 | 1 | 58.5 | INSUFFICIENT | 55.7 | INSUFFICIENT_EVIDENCE |
| S9 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S10 | 1 | 0 | 1 | 0 | 1 | 0.0 | -1.000 | -1.000 | 0.000 | -2.11 | -3.4 | 2.11 | 1 | 0.00 | 1 | 1.0 | INSUFFICIENT | 49.1 | INSUFFICIENT_EVIDENCE |
| S11 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S12 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S13 | 1 | 1 | 0 | 1 | 0 | 100.0 | 0.926 | 0.926 | — | 2.83 | 4.5 | 0.00 | 0 | 1.00 | 1 | 24.0 | INSUFFICIENT | 52.9 | INSUFFICIENT_EVIDENCE |
| S14 | 1 | 0 | 1 | 0 | 1 | 0.0 | -0.149 | -0.149 | 0.000 | -0.33 | -0.5 | 0.33 | 1 | 0.00 | 1 | 1.0 | INSUFFICIENT | 50.2 | INSUFFICIENT_EVIDENCE |
| S15 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S16 | 1 | 1 | 0 | 0 | 1 | 0.0 | -0.241 | -0.241 | 0.000 | -1.12 | -1.8 | 1.12 | 1 | 0.00 | 1 | 24.0 | INSUFFICIENT | 49.9 | INSUFFICIENT_EVIDENCE |
| S17 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S18 | 1 | 1 | 0 | 1 | 0 | 100.0 | 0.673 | 0.673 | — | 1.69 | 2.7 | 0.00 | 0 | 1.00 | 1 | 1.0 | INSUFFICIENT | 52.9 | INSUFFICIENT_EVIDENCE |
| S19 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S20 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S21 | 2 | 0 | 2 | 0 | 2 | 0.0 | -1.001 | -2.001 | 0.000 | -4.91 | -7.9 | 4.91 | 2 | 0.00 | 1 | 374.0 | INSUFFICIENT | 45.6 | INSUFFICIENT_EVIDENCE |
| S22 | 1 | 1 | 0 | 0 | 1 | 0.0 | -0.440 | -0.440 | 0.000 | -1.00 | -1.6 | 1.00 | 1 | 0.00 | 1 | 1.0 | INSUFFICIENT | 49.9 | INSUFFICIENT_EVIDENCE |
| S23 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S24 | 2 | 2 | 0 | 2 | 0 | 100.0 | 1.385 | 2.771 | — | 10.96 | 17.6 | 0.00 | 0 | 1.00 | 1 | 14.5 | INSUFFICIENT | 55.4 | INSUFFICIENT_EVIDENCE |
| S25 | 4 | 1 | 3 | 2 | 2 | 50.0 | -0.067 | -0.270 | 0.685 | -1.06 | -1.7 | 2.69 | 1 | 0.50 | 4 | 23.5 | INSUFFICIENT | 48.0 | INSUFFICIENT_EVIDENCE |
| S26 | 4 | 1 | 3 | 0 | 4 | 0.0 | -0.375 | -1.502 | 0.000 | -4.03 | -6.5 | 4.03 | 4 | 0.00 | 1 | 9.5 | INSUFFICIENT | 42.4 | INSUFFICIENT_EVIDENCE |
| S27 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S28 | 2 | 0 | 2 | 2 | 0 | 100.0 | 4.783 | 9.566 | — | 19.54 | 31.3 | 0.00 | 0 | 1.00 | 1 | 17.0 | INSUFFICIENT | 55.7 | INSUFFICIENT_EVIDENCE |
| S29 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S30 | 2 | 0 | 2 | 2 | 0 | 100.0 | 1.964 | 3.928 | — | 8.44 | 13.5 | 0.00 | 0 | 1.00 | 1 | 4.5 | INSUFFICIENT | 55.6 | INSUFFICIENT_EVIDENCE |
| S31 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S38 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S39 | 36 | 23 | 13 | 15 | 21 | 41.7 | 0.120 | 4.315 | 1.201 | 16.73 | 26.8 | 15.03 | 4 | 0.38 | 13 | 246.1 | SUFFICIENT | 31.6 | CURRENTLY_WEAK |
| S40 | 3 | 3 | 0 | 2 | 1 | 66.7 | 1.411 | 4.234 | 6.621 | 11.60 | 18.6 | 2.06 | 1 | 1.00 | 2 | 223.0 | INSUFFICIENT | 51.2 | INSUFFICIENT_EVIDENCE |
| S41 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S42 | 1 | 1 | 0 | 0 | 1 | 0.0 | -1.001 | -1.001 | 0.000 | -2.22 | -3.6 | 2.22 | 1 | 0.00 | 1 | 39.0 | INSUFFICIENT | 48.9 | INSUFFICIENT_EVIDENCE |
| S43 | 2 | 0 | 2 | 0 | 2 | 0.0 | -1.000 | -2.001 | 0.000 | -5.29 | -8.5 | 5.29 | 2 | 0.00 | 1 | 22.0 | INSUFFICIENT | 45.4 | INSUFFICIENT_EVIDENCE |
| S44 | 7 | 6 | 1 | 1 | 6 | 14.3 | -0.602 | -4.214 | 0.282 | -11.10 | -17.8 | 15.47 | 6 | 0.33 | 3 | 43.1 | LIMITED | 34.7 | CURRENTLY_WEAK |
| S45 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S46 | 47 | 19 | 28 | 15 | 32 | 31.9 | -0.020 | -0.936 | 1.101 | 13.59 | 21.8 | 68.29 | 13 | 0.42 | 12 | 224.0 | SUFFICIENT | 19.4 | CURRENTLY_WEAK |
| S48 | 4 | 3 | 1 | 4 | 0 | 100.0 | 0.218 | 0.870 | — | 2.45 | 3.9 | 0.00 | 0 | 1.00 | 3 | 7.0 | INSUFFICIENT | 59.3 | INSUFFICIENT_EVIDENCE |
| S50 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |
| S51 | 0 | 0 | 0 | 0 | 0 | — | — | — | — | 0.00 | 0.0 | 0.00 | 0 | — | 0 | — | INSUFFICIENT | — | INSUFFICIENT_EVIDENCE |

**20 of 43 strategies (S2, S3, S6, S7, S9, S11, S12, S15, S17, S19, S20, S23, S27, S29, S31, S38, S41,
S45, S50, S51) took ZERO trades in this 12-month window** — shown explicitly above, not hidden, per
the CEO's own instruction.

**Portfolio-level session/regime attribution** (aggregated across all 142 trades, portfolio A):

| Session | Trades | % | | Regime (14-bar True-Range tertile of this window's own distribution) | Trades | % |
|---|---|---|---|---|---|---|
| NY | 67 | 47.2% | | High-vol | 98 | 69.0% |
| Asia | 42 | 29.6% | | Mid-vol | 34 | 23.9% |
| London | 20 | 14.1% | | Low-vol | 10 | 7.0% |
| Late | 13 | 9.2% | | | | |

**Signal frequency, rejection reasons, execution costs — disclosed data-model limitations (using
ONLY existing infrastructure, per instruction, not new instrumentation):**

- **Execution costs**: $0.00 for every strategy — the Simulation Framework's cost model is configured
  at its zero-cost defaults for this run (same disclosed, repo-wide limitation as Wave D and Phase
  6.9; not specific to this analysis).
- **Signal frequency** (pre-risk-filter signal counts, as distinct from trades taken): **not available
  per-strategy from the existing trade ledger** — the Simulation Framework records executed trades and
  aggregate portfolio-level risk-event counts, but does not currently tag risk/rejection events with a
  `strategy_id` (`ai_trader/simulation/portfolio_simulator.py`'s `RiskEventRecord` has no such field).
  Reporting a per-strategy signal-frequency or rejection-reason breakdown would require adding
  instrumentation to the frozen Simulation Framework, which is out of scope for this audit ("use only
  existing infrastructure"). The closest available proxy is each strategy's own trade count above.
- **Portfolio-level rejection reasons for this window** (aggregate across all strategies, not
  attributable to any one of them): `DENY_NOT_ACTIONABLE` 986,238; `DENY_LIMIT_MAX_PER_SYMBOL` 18,879;
  `DENY_BELOW_FLOOR` 7,296; `DENY_SIZE_BELOW_MIN` 3,233; `DENY_INVALID_INPUT` 397;
  `DENY_COOLDOWN_AFTER_LOSS` 289. `DENY_LIMIT_MAX_PER_SYMBOL` (the single-shared-XAUUSD-slot
  constraint) alone accounts for far more denials than there were trades — direct evidence of how much
  signal volume the single-symbol architecture discards regardless of strategy quality.

---

## 3. Current relevance classification — methodology and results

**Reused, not reinvented**: `score_window()` (`ai_trader/strategy_health/scoring.py`, unmodified) is
called on the 12-month `WindowMetrics` ALONE (no blending with any other window, no trend-bump rule —
`combine_windows()`/`classify()`/`evaluate_strategy_health()` are NOT used here, since those blend
3m/6m/12m and would let older performance influence the result, which the CEO's own instruction
forbids). The population for percentile-ranking is every strategy with ≥1 trade in this window (23 of
43). Classification bands reuse the Health System's own existing 65/45 thresholds, renamed for this
report:

- `score ≥ 65` → **CURRENTLY_STRONG**
- `45 ≤ score < 65` → **CURRENTLY_USABLE**
- `score < 45` → **CURRENTLY_WEAK**
- **`INSUFFICIENT_EVIDENCE`** overrides all of the above whenever sample sufficiency is `INSUFFICIENT`
  (< 5 trades) or the strategy has zero trades (no score at all) — a strategy is never called good or
  bad on fewer than 5 trades.

**Result:**

| Classification | Count | Strategies |
|---|---|---|
| CURRENTLY_STRONG | **0** | — |
| CURRENTLY_USABLE | **0** | — |
| CURRENTLY_WEAK | **4** | S1, S39, S44, S46 |
| INSUFFICIENT_EVIDENCE | **39** | every other strategy (20 with zero trades, 19 with 1–4 trades) |

**Zero strategies reach CURRENTLY_STRONG or CURRENTLY_USABLE.** The only strategies with enough
evidence to be judged at all (S1, S39, S44, S46 — precisely the four with a `SUFFICIENT` or `LIMITED`
sample) all land in CURRENTLY_WEAK. Notably, **S46** — the top-tier, "VERY_GOOD"-lifetime, previously
`ACTIVE`-classified strategy from the original Wave D / Strategy Health System snapshot — shows a
materially different recent picture: 47 trades, expectancy essentially flat (-0.02R), a 13-trade
losing streak, and a $68.29 isolated max drawdown (its largest of any strategy in this table) — a real,
concrete instance of exactly the "regime change" risk the Strategy Health System was built to detect.

**An important caveat on the scoring itself**: with only 23 of 43 strategies having ANY trade this
window, and most of those 23 having 1–4 trades, the percentile-rank population is itself extremely
thin. Several 1-trade strategies with a single lucky win (e.g. S28: 2 trades, both winners, score 55.7)
score HIGHER than S46's 47-trade, real, credible track record (score 19.4) — an artifact of how
percentile-rank + credibility shrinkage behaves when most of the comparison population is itself
low-evidence noise, not a claim that those small-sample strategies are actually better. This is
disclosed, not hidden: **scores in this report should be read alongside `n_trades` and sample
sufficiency, never alone.**

---

## 4. Portfolio tests (A/B/C/D) — same window, same $2,000 capital, 5% risk, cost model, seed=1,
execution model, market data — nothing changed between variants except `strategy_id_filter`

Because zero strategies reached CURRENTLY_STRONG or CURRENTLY_USABLE, **variants B and C are
identical to each other and both trivially empty** — this is reported, not hidden.

| Metric | A (all 43) | B (STRONG only) | C (STRONG+USABLE) | D (all except WEAK) |
|---|---|---|---|---|
| Strategy count | 43 | **0** | **0** | 39 |
| Trades | 142 | 0 | 0 | 164 |
| Net profit | +$62.35 | $0.00 | $0.00 | **+$102.45** |
| Return % | +3.12% | 0.00% | 0.00% | **+5.12%** |
| Profit factor | 1.212 | — | — | **1.387** |
| Expectancy | +0.153 R | — | — | **+0.186 R** |
| Sharpe | 0.982 | — | — | **1.751** |
| Sortino | 1.155 | — | — | 1.805 |
| Max drawdown | 3.57% | 0.00% | 0.00% | **2.39%** |
| Calmar | 0.874 | — | — | 2.147 |
| Win rate | 38.0% | — | — | 41.5% |
| Avg exposure | 83.8% of bars | 0.0% | 0.0% | 64.9% |
| Turnover | 28.87 | 0.00 | 0.00 | 32.97 |
| Avg holding (bars) | 160.7 | — | — | 110.8 |
| Max losing streak | 7 | 0 | 0 | 10 |

**On the surface, D outperforms A on every single metric.** This must NOT be read as "removing
CURRENTLY_WEAK strategies improves the portfolio" without the following critical qualification:

### D's outperformance is driven almost entirely by ONE strategy trading far more often — not by broadly better strategy selection

- **S40** took only **3** trades in portfolio A (and was itself classified `INSUFFICIENT_EVIDENCE`,
  score 51.2 — not `CURRENTLY_STRONG`, not even `CURRENTLY_USABLE`). Once S1/S39/S44/S46 were excluded
  from competing for XAUUSD's single shared position slot, **S40 alone took 79 trades in portfolio D**
  — a 26x increase — netting **+$96.75, i.e. 94.4% of D's entire +$102.45 net profit.**
- This is the SAME single-shared-symbol-slot path-dependence effect already documented in
  `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` §1 and the Phase 6.9 report §6: removing a strategy does not
  simply subtract its own trades from the total — it changes which OTHER strategy's signals get to
  occupy the freed-up slot, in a way that can dominate the entire result.
- **D's own apparent edge is therefore concentrated in a single, under-evidenced strategy that this
  same audit could not classify as good** — not a validated, broad-based improvement.

### Portfolio A is itself dominated by a handful of outlier trades and one outlier month

- The **top 3 winning trades** in portfolio A sum to **$62.61 — slightly MORE than A's entire net
  profit ($62.35)**. Every other trade in the 142-trade sample collectively nets to roughly breakeven.
- The **single best trade** (S46, +$21.29, closed 2025-10-16) is **34.1% of A's entire net profit** on
  its own.
- **October 2025 alone contributed +$78.81** of A's +$62.35 total net profit — meaning **every other
  month combined was net NEGATIVE (-$16.46)**. Portfolio A's headline profitability over this window
  is a one-month story.
- Portfolio D is somewhat less outlier-trade-dependent (top 3 trades = 44.3% of net profit, vs A's
  100.4%) but is, as shown above, even MORE strategy-concentrated (one strategy = 94.4% of profit).

### Monthly returns (both variants)

| Month | A: PnL ($) | A: Trades | D: PnL ($) | D: Trades |
|---|---|---|---|---|
| 2024-10 | -3.07 | 1 | -3.07 | 1 |
| 2024-11 | +4.62 | 10 | +23.37 | 14 |
| 2024-12 | -2.79 | 7 | +17.03 | 2 |
| 2025-01 | -4.64 | 5 | -0.70 | 4 |
| 2025-02 | -5.67 | 11 | +8.16 | 12 |
| 2025-03 | -7.68 | 13 | +4.95 | 4 |
| 2025-04 | +25.59 | 30 | +25.67 | 34 |
| 2025-05 | +6.97 | 6 | +3.06 | 19 |
| 2025-06 | -22.49 | 11 | +9.41 | 13 |
| 2025-07 | -2.81 | 10 | -6.44 | 9 |
| 2025-08 | -17.78 | 8 | -8.53 | 10 |
| 2025-09 | +13.27 | 12 | +10.90 | 10 |
| 2025-10 (partial, 23 days) | **+78.81** | 18 | +18.64 | 32 |

Portfolio A is net-negative in 8 of its 13 months (2024-10, 2024-12, 2025-01, 2025-02, 2025-03,
2025-06, 2025-07, 2025-08); D is net-negative in only 4 of its 13 months (2024-10, 2025-01, 2025-07,
2025-08) — D is more consistently profitable month-to-month even setting aside the S40-concentration
finding, though both share the same single strongly-positive final partial month.

---

## 5. Answers to the seven required questions

**1. Which strategies appear relevant now?** None qualify as `CURRENTLY_STRONG`. None qualify as
`CURRENTLY_USABLE`. Zero strategies currently meet a bar for live relevance under this frozen
methodology.

**2. Which strategies appear weak now?** S1, S39, S44, S46 — the ONLY four strategies with enough
recent evidence to be judged at all, and all four score below the USABLE threshold. S46 in particular
shows a real, concrete decline from its historical (lifetime) strong tier.

**3. Which strategies lack enough recent evidence?** 39 of 43 — 20 with literally zero trades in the
window, 19 more with only 1–4 trades. This is the overwhelming majority of the strategy population.

**4. Which portfolio composition performs best over the latest 12 months?** By every numerical metric,
**D (all except CURRENTLY_WEAK, 39 strategies)** — but see §4: this result is not evidence of good
strategy selection. It is 94.4% attributable to one strategy (S40) that this same audit rates
`INSUFFICIENT_EVIDENCE`, trading vastly more often only because the slot competition around it
changed. **A's own result is dominated by 3 outlier trades and one outlier month.** Neither result
should be read as a validated, repeatable edge.

**5. Is the result broad-based or concentrated?** **Concentrated, in every variant, by every measure
tested**: A is concentrated in outlier trades (top 3 = >100% of net profit) and one outlier month
(October alone = 126% of the annual total); D is concentrated in a single strategy (94.4% of net
profit from S40 alone). Neither portfolio shows broad-based, diversified profitability across many
strategies or many months.

**6. Is the current evidence strong enough to justify Shadow Mode?** **Not for live capital under a
strict current-relevance gate** — zero strategies clear even the USABLE bar, so a portfolio built
strictly from currently-proven strategies would trade nothing at all (portfolios B/C, both empty).
**Yes, evidence is strong enough to justify continued, careful, capital-free observation**: the 39
`INSUFFICIENT_EVIDENCE` strategies need more trades before they can be judged one way or the other at
all (most have gone an entire year with 0–4 trades on this single symbol), and the 4 `CURRENTLY_WEAK`
strategies are worth watching for whether their evidence continues to accumulate in the negative
direction or recovers. Given the "not fully out-of-sample" caveat (§1), even this observation-only
recommendation should be weighted cautiously.

**7. What should remain active for observation, not live trading?** All 43 strategies should continue
to be tracked (none is recommended for permanent elimination — the CEO's own strict rule). In
particular: (a) the 4 `CURRENTLY_WEAK` strategies (S1, S39, S44, S46) warrant close, continued
observation given they are the only ones with enough evidence to show a real (negative) recent signal;
(b) S40 warrants specific attention given its outsized role in portfolio D's result despite its own
`INSUFFICIENT_EVIDENCE` status — more evidence is needed before its apparent edge can be trusted; (c)
the 20 zero-trade strategies warrant no action at all beyond continued passive observation — there is
nothing yet to evaluate.

---

## 6. Strict-rules compliance

No threshold was tuned after seeing results (bands/sufficiency cutoffs were fixed BEFORE running any
simulation, reusing existing frozen numbers — §2, §3). No strategy was permanently eliminated. No
strategy rule, risk parameter, or scoring weight was changed. The sealed holdout was not used (§1). The
window was chosen before results were seen and was not re-chosen afterward. No negative or zero-trade
strategy was hidden (§2's table shows all 43, including the 20 with zero trades).

## 7. Artifacts preserved

`relevance12m_run.py`, `relevance12m_run_bcd.py`, `relevance12m_perstrategy.py` (orchestrator/analysis
scripts) and `relevance12m_portfolioA.json`, `relevance12m_portfolioBCD.json`,
`relevance12m_perstrategy.json` (raw output, including every trade's full record) — all at repo root,
preserved per the same "preserve all artifacts and diagnostics" precedent established in Phase 6.9.

---

**No implementation follows this report.** No live trading, Telegram, Broker Adapter, or MT5 work has
been started. Waiting for CEO review.
