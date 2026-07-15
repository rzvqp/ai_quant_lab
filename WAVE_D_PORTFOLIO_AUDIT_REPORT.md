# Wave D Portfolio Audit — Full Analysis of the 513-Trade Result

**Date:** 2026-07-16. **Scope:** CEO-directed, analysis-only session. No strategy was implemented,
modified, or tuned; no parameter was changed; no new edge was created; the Research Lab and all six
frozen pipeline modules were not touched. This report analyzes results already obtained
(`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`'s own 513-trade run) at finer granularity, and simulates 3
alternative strategy-inclusion sets using the Simulation Framework's own pre-existing
`strategy_id_filter` parameter — no strategy code or parameter differs between any of the 4 runs
compared here, only WHICH strategies are allowed to trade.

---

## 0. Reconstruction and live verification

State was reconstructed exclusively from `NEXT_SESSION.md`, `CHANGELOG.md`,
`PHASE_6_8_WAVE_B_COMPLETION_REPORT.md`, and `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`, then verified
live:

| Check | Documented | Live result | Match |
|---|---|---|---|
| Branch | `ai-trader-implementation` | `ai-trader-implementation` | ✅ |
| HEAD | `848a9c3` | `848a9c3` | ✅ |
| Working tree | clean | clean | ✅ |
| `pytest ai_trader/ -q` | 1515 passed | 1515 passed | ✅ |
| `mypy --strict ai_trader/ --exclude 'tests/'` | 158 files, 0 errors | 158 files, 0 errors | ✅ |
| `coverage` | 95% (9392 stmts, 434 miss) | 95% (9394 stmts, 427 miss) | ✅ (same %, tiny stmt-count drift from the two Wave D bug fixes, already disclosed as expected in `NEXT_SESSION.md`) |

**All documented claims are confirmed live. No discrepancy found.** `WAVE_D_PORTFOLIO_SIMULATION_
REPORT.md` is used as the single source of truth for the baseline numbers throughout this report.

A deterministic re-run of the exact documented Wave D configuration (same seed, date range,
`risk_per_trade_pct=0.05`, `enable_time_stops`/`enable_trailing_stops=True`, all 43 strategies) was
also performed to extract the full trade-level ledger the summary report doesn't carry (per-trade
strategy_id, timestamps, `pnl_r`, `holding_bars`). It reproduced **513 trades, net PnL $313.21 —
exact match** (to floating-point rounding order) to the documented result. Every metric below is
derived from that ledger plus the summary report; nothing is estimated or assumed.

---

## 1. Methodology and its limits (disclosed up front)

- **One symbol, one slot.** XAUUSD is the only symbol and only one position may be open at a time
  system-wide. This means "cannibalization" here is structurally universal — ANY open position blocks
  ALL other strategies, not just similar ones — so a clean, pairwise cannibalization score does not
  exist from a single run. Two proxies are used instead (§5): monthly-PnL correlation (does a pair's
  return pattern move together or apart?) and trade-count shift across the 4 portfolio compositions
  simulated in §7 (does a strategy's OWN trade count change when others are excluded? — direct
  evidence of who was competing for the slot).
- **Per-strategy drawdown is an isolated proxy**, not true portfolio-attributed drawdown: each
  strategy's own trades are chained into their own cumulative PnL curve (in their own exit order) and
  the peak-to-trough of THAT curve is reported. Real strategies share one capital account and one
  slot, so this cannot be summed to the portfolio's own 6.16% max drawdown — it answers "how painful
  was this strategy's own worst stretch," not "how much of the shared drawdown it caused."
  Portfolio-level `max_drawdown_R` remains an unresolved gap (already named in `NEXT_SESSION.md` §F).
- **Correlation is only reported as reliable for strategies with ≥5 distinct active months** (11 of
  29 active strategies qualify: S46, S39, S1, S25, S48, S10, S13, S5, S26, S44, S30). Strategies with
  fewer active months produce numerically valid but statistically meaningless correlation coefficients
  and are excluded from the correlation findings.
- **Sample sizes are mostly small.** 14 of 43 strategies had zero trades this run; 11 more had 1–4
  trades. Only 18 strategies traded ≥5 times. Every tier/keep-eliminate call below states its own
  confidence level explicitly — this is not a substitute for the Research Lab's own larger historical
  backtests, which remain the authoritative source for any individual strategy's standalone edge.

---

## 2. Full per-strategy metrics — all 43

Sorted by strategy ID. **Tier** and **Confidence** are this audit's own calls (§3 explains the tier
rule); **v0 Confidence** is the frozen Research Lab's own prior assessment (`knowledge/strategies/*/
strategy.json`), reported for cross-reference, not overridden.

| ID | Trades | Win rate | Profit factor | Expectancy R | Net profit | Total R | Isolated DD | Contribution | Tier | Confidence | Keep/Eliminate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 49 | 34.7% | 0.803 | +0.296 | -$23.56 | +14.49 | $57.85 | -7.52% | NEGATIVE | MEDIUM (n=49) | Investigate — positive R but negative $ is a red flag (§6) |
| S2 | 7 | 57.1% | 3.288 | +0.810 | +$13.93 | +5.67 | $6.09 | +4.45% | VERY_GOOD | LOW (n=7) | Keep, watch |
| S3 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: VERY LOW, historically profitable but not research-worthy) |
| S4 | 2 | 50.0% | 0.506 | -0.247 | -$0.68 | -0.49 | $1.39 | -0.22% | NEUTRAL | insufficient (n=2) | No call possible |
| S5 | 23 | 34.8% | 0.765 | -0.259 | -$10.14 | -5.97 | $20.23 | -3.24% | NEGATIVE | MEDIUM (n=23) | Candidate for elimination, not yet clear-cut |
| S6 | 4 | 25.0% | 0.657 | -0.297 | -$2.40 | -1.19 | $5.37 | -0.77% | NEUTRAL | insufficient (n=4) | No call possible |
| S7 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S8 | 4 | 50.0% | 2.146 | +0.636 | +$5.68 | +2.54 | $4.95 | +1.81% | NEUTRAL | insufficient (n=4) | Promising direction, too small to call |
| S9 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: LOW) |
| S10 | 16 | 43.8% | 0.909 | -0.032 | -$1.34 | -0.51 | $8.67 | -0.43% | NEUTRAL | MEDIUM (n=16) | Near-breakeven, keep as-is |
| S11 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S12 | 3 | 100.0% | ∞ (no losses) | +1.390 | +$12.34 | +4.17 | $0.00 | +3.94% | NEUTRAL | insufficient (n=3) | Promising, too small to call |
| S13 | 18 | 55.6% | 3.726 | +0.430 | +$36.75 | +7.73 | $8.26 | +11.73% | VERY_GOOD | MEDIUM (n=18) | Keep |
| S14 | 9 | 0.0% | 0.000 | -0.672 | -$40.46 | -6.05 | $40.46 | -12.92% | ELIMINATE | MEDIUM-HIGH (n=9, 0% win rate) | Eliminate-tier — matches v0's own FRAGILE flag |
| S15 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S16 | 4 | 75.0% | 6.854 | +0.599 | +$6.53 | +2.40 | $1.12 | +2.08% | NEUTRAL | insufficient (n=4) | Promising, too small to call |
| S17 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: LOW) |
| S18 | 3 | 66.7% | 4.485 | +0.519 | +$15.86 | +1.56 | $4.55 | +5.06% | NEUTRAL | insufficient (n=3) | Promising, too small to call |
| S19 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: VERY LOW, FRAGILE flag) |
| S20 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: LOW) |
| S21 | 2 | 0.0% | 0.000 | -1.001 | -$5.36 | -2.00 | $5.36 | -1.71% | NEUTRAL | insufficient (n=2) | Negative direction, too small to call |
| S22 | 31 | 29.0% | 0.466 | -0.210 | -$38.41 | -6.50 | $49.44 | -12.26% | NEGATIVE | MEDIUM-HIGH (n=31) | Candidate for elimination |
| S23 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S24 | 5 | 60.0% | 1.914 | +0.433 | +$8.69 | +2.17 | $9.52 | +2.78% | VERY_GOOD | LOW (n=5, boundary) | Keep, watch |
| S25 | 11 | 54.5% | 0.825 | -0.128 | -$1.86 | -1.41 | $6.34 | -0.59% | NEUTRAL | MEDIUM (n=11) | Near-breakeven, keep as-is |
| S26 | 10 | 30.0% | 0.281 | -0.202 | -$5.82 | -2.02 | $6.64 | -1.86% | ELIMINATE | MEDIUM (n=10) | Eliminate-tier |
| S27 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S28 | 10 | 40.0% | 2.058 | +0.790 | +$14.74 | +7.90 | $8.17 | +4.71% | VERY_GOOD | MEDIUM (n=10) | Keep |
| S29 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: VERY LOW) |
| S30 | 13 | 30.8% | 0.619 | -0.102 | -$9.55 | -1.32 | $18.00 | -3.05% | NEGATIVE | MEDIUM (n=13) | Candidate for elimination |
| S31 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: VERY LOW) |
| S38 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S39 | 96 | 46.9% | 1.262 | +0.263 | +$72.23 | +25.29 | $64.02 | +23.06% | GOOD | HIGH (n=96) | Keep — largest reliable positive sample |
| S40 | 6 | 83.3% | 14.889 | +1.758 | +$28.67 | +10.55 | $2.06 | +9.15% | VERY_GOOD | LOW (n=6, extreme PF is a sample-size artifact) | Keep, watch closely |
| S41 | 1 | 0.0% | 0.000 | -1.000 | -$2.37 | -1.00 | $2.37 | -0.76% | NEUTRAL | insufficient (n=1) | No call possible |
| S42 | 7 | 28.6% | 0.056 | -0.383 | -$10.87 | -2.68 | $11.52 | -3.47% | ELIMINATE | MEDIUM (n=7) | Eliminate-tier |
| S43 | 2 | 0.0% | 0.000 | -1.000 | -$5.74 | -2.00 | $5.74 | -1.83% | NEUTRAL | insufficient (n=2) | Negative direction, too small to call |
| S44 | 18 | 33.3% | 3.009 | +1.300 | +$75.05 | +23.40 | $18.30 | +23.96% | VERY_GOOD | MEDIUM (n=18) | Keep — high-conviction, low-frequency |
| S45 | 1 | 0.0% | 0.000 | -0.589 | -$5.44 | -0.59 | $5.44 | -1.74% | NEUTRAL | insufficient (n=1) | No call possible |
| S46 | 144 | 36.1% | 1.410 | +0.104 | +$179.32 | +14.93 | $79.25 | +57.25% | GOOD | HIGH (n=144) | Keep — dominant contributor, high volume |
| S47 | — | — | — | — | — | — | — | — | n/a | n/a | Not runtime-eligible (v0 status: INVALID) |
| S48 | 13 | 46.2% | 1.071 | +0.046 | +$0.45 | +0.59 | $4.06 | +0.14% | NEUTRAL | MEDIUM (n=13) | Near-breakeven, keep as-is |
| S49 | — | — | — | — | — | — | — | — | n/a | n/a | Not runtime-eligible (v0 status: INVALID) |
| S50 | 0 | — | — | — | $0.00 | — | — | 0% | NEUTRAL | n/a | No Wave D data (v0: NEGATIVE) |
| S51 | 1 | 100.0% | ∞ (no losses) | +1.999 | +$7.00 | +2.00 | $0.00 | +2.23% | NEUTRAL | insufficient (n=1) | No call possible |

S32–S37 are not listed (frozen v0 status `NOT_IMPLEMENTED`, no folder-level strategy spec exists to
audit). Sum of `Contribution` across active strategies ≈ 100% of net PnL (small rounding).

---

## 3. Tier grouping — rule and rationale

Tiers are derived MECHANICALLY from this run's own numbers (not tuned, not adjusted for any
strategy individually):

1. **Trades = 0 → NEUTRAL** ("no Wave D data").
2. **Trades < 5 → NEUTRAL** regardless of sign — too small a sample to call VERY_GOOD/GOOD/NEGATIVE/
   ELIMINATE responsibly; the observed direction is still reported.
3. **Trades ≥ 5, `|net_pnl| < $2` → NEUTRAL** (economically breakeven despite a technical PF sign).
4. **Trades ≥ 5, `win_rate == 0` or `profit_factor ≤ 0.3` → ELIMINATE** (a clear, consistent losing
   pattern, not noise).
5. **Trades ≥ 5, `net_pnl > 0` and `profit_factor ≥ 1.5` → VERY_GOOD**.
6. **Trades ≥ 5, `net_pnl > 0` (not very-good) → GOOD**.
7. Everything else with `trades ≥ 5` → **NEGATIVE**.

| Tier | Count | Strategies |
|---|---|---|
| VERY_GOOD | 6 | S2, S13, S24, S28, S40, S44 |
| GOOD | 2 | S39, S46 |
| NEUTRAL | 28 | S3, S4, S6, S7, S8, S9, S10, S11, S12, S15, S16, S17, S18, S19, S20, S21, S23, S25, S27, S29, S31, S38, S41, S43, S45, S48, S50, S51 |
| NEGATIVE | 4 | S1, S5, S22, S30 |
| ELIMINATE | 3 | S14, S26, S42 |

Note: this tiering is a mechanical read of ONE 3.6-year run under severe single-slot competition
(only 29 of 43 strategies even got to trade). It is **not** equivalent to, and does not override, the
Research Lab's own v0 confidence ratings (§2's own column) — most strategies here (including several
VERY_GOOD ones, like S2/S13/S28/S44) carry v0 confidence of VERY LOW/NEGATIVE from the Research Lab's
own unconstrained, single-strategy backtests. The disagreement itself is a notable finding (§8).

---

## 4. Correlation analysis (reliable pairs only, n ≥ 5 active months each)

11 strategies qualify: S1, S5, S10, S13, S25, S26, S30, S39, S44, S46, S48 (55 pairs).

**Most negatively correlated (diversifying / complementary) pairs:**

| Pair | Correlation | Month overlap (Jaccard) |
|---|---|---|
| S30 – S44 | -0.73 | 0.22 |
| S25 – S44 | -0.65 | 0.23 |
| S1 – S44 | -0.59 | 0.20 |
| S13 – S25 | -0.47 | 0.21 |
| S1 – S26 | -0.40 | 0.26 |

**Most positively correlated (redundant) pairs:**

| Pair | Correlation | Month overlap (Jaccard) |
|---|---|---|
| S13 – S44 | +0.64 | 0.18 |
| S30 – S48 | +0.52 | 0.50 |
| S10 – S26 | +0.48 | 0.40 |
| S25 – S30 | +0.42 | 0.15 |
| S1 – S30 | +0.38 | 0.21 |

**Reading these carefully**: S44 shows up as BOTH the strongest complement to S30/S25/S1 (negative
correlation) AND positively correlated with S13. S44 (VERY_GOOD tier) and S13 (VERY_GOOD tier) moving
together is a mild redundancy signal between the portfolio's own two best-performing low-frequency
strategies — not a problem, but worth knowing neither is a hedge for the other. S30 and S42 (both
NEGATIVE/ELIMINATE tier) correlating positively with S48/S25 (NEUTRAL) suggests these losing months
cluster together — consistent with a shared market-regime driver (§6) rather than 4 independent
edges failing simultaneously by coincidence.

---

## 5. Cannibalization — methodology and findings

A true pairwise cannibalization score does not exist in a single-slot, single-symbol system: opening
ANY position blocks ALL 42 other strategies, not just similar ones. `LIMIT_MAX_PER_SYMBOL` denials
(70,467 in the baseline run) are the dominant rejection reason after `NOT_ACTIONABLE`, confirming slot
contention is severe and universal, not strategy-pair-specific.

The strongest EMPIRICAL evidence of cannibalization comes from the 3 portfolio-variant reruns (§7):
when the strategy set shrinks, individual survivors' own trade counts change dramatically —
direct proof of who was competing for the shared slot.

| Strategy | Baseline (43) trades | Conservative (6) trades | Balanced (8) trades |
|---|---|---|---|
| S40 | 6 | **275** | 2 |
| S13 | 18 | 58 | 31 |
| S44 | 18 | 49 | 31 |
| S28 | 10 | 34 | 12 |
| S2 | 7 | 24 | 7 |
| S24 | 5 | 9 | 7 |
| S46 | 144 | — | **153** |
| S39 | 96 | — | 90 |

**S40 is the most heavily cannibalized strategy found**: 6 trades in the 43-strategy baseline vs.
**275 trades** when only 5 other strategies compete for the slot — a 46× increase. S40 is a
"Class VIII — meta/regime router" (composite strategy per its own `klass`), which structurally
depends on OTHER strategies' own signals being scarce to get a turn; in the full 43-strategy
portfolio it is almost entirely crowded out. **S13 and S44 are also substantially cannibalized**
(3–3.2× more trades when the field shrinks to 6–8 strategies). This directly explains why several
VERY_GOOD-tier strategies show such small baseline trade counts despite a strong per-trade edge — the
edge is real on the trades they DO get, but the full portfolio starves them of opportunities.

**Complementary strategies** (from §4's negative correlations, corroborated by low month-overlap):
S30/S44, S25/S44, S1/S44 — different active periods AND opposing-sign monthly returns, genuine
diversification value if both were kept.

---

## 6. Notable individual finding: S1's own contradiction

S1 shows **positive R-expectancy (+0.296) but negative dollar net PnL (-$23.56)** over 49 trades —
already flagged in the original Wave D report as "variance around a thin edge." This audit's own
variant reruns make this MUCH more visible and more concerning (§7): in the Aggressive variant, S1
gets only 6 trades but an **expectancy of +21.6R** and **+$327.04 net PnL** — a wildly different
outcome from the baseline's 49-trade, -$23.56 result, driven by 1–2 extreme-length trades captured
because the position-slot dynamics changed (§7). This is the clearest evidence in the entire audit
that S1's own baseline performance is **not a stable, repeatable number** — it is highly sensitive to
which OTHER strategies are competing for the slot, i.e., to path-dependent luck in a shared-resource
system, not to S1's own edge alone. **S1 should not be judged from either run in isolation.**

---

## 7. Portfolio variants — definition, simulation, and comparison

Three variants were defined purely by strategy INCLUSION (no code, parameter, or rule changes) and
run through the identical, unmodified `SimulationHarness` over the identical historical period,
seed, and risk configuration as the baseline:

- **Conservative** = VERY_GOOD tier only: `{S2, S13, S24, S28, S40, S44}` (6 strategies)
- **Balanced** = VERY_GOOD + GOOD tiers: `{S2, S13, S24, S28, S40, S44, S39, S46}` (8 strategies)
- **Aggressive** = everything except the ELIMINATE tier: all 40 non-eliminated runtime-eligible
  strategies (43 minus `{S14, S26, S42}`)
- **Current (baseline)** = all 43, unchanged from `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`

| Metric | Current (43) | Conservative (6) | Balanced (8) | Aggressive (40) |
|---|---|---|---|---|
| Trades | 513 | 449 | 333 | 82 |
| Net profit | +$313.21 | +$208.81 | +$242.75 | +$431.60 |
| Return | +15.66% | +10.44% | +12.14% | +21.58% |
| Sharpe | 1.196 | **1.025** | 0.894 | **1.224** |
| Max drawdown | 6.16% | **4.95%** | 7.00% | 10.83% |
| Profit factor | 1.264 | 1.194 | 1.231 | **3.039** |
| Avg holding (bars) | 173.2 | 115.7 | 273.7 | **1046.8** |
| Avg exposure | 87.7% | 60.6% | 87.8% | 96.2% |
| Distinct strategies that traded | 29 | 6/6 | 8/8 | 5/40 |

### Reading this table honestly

- **Conservative** has the LOWEST drawdown (4.95%) of all four and a solid Sharpe (1.025), with the
  fewest moving parts (6 strategies) — the most legible, easiest-to-audit portfolio. Its return
  (+10.44%) is the lowest of the four, a real tradeoff, not a flaw.
- **Balanced** adds S39/S46 (the two GOOD-tier, high-volume strategies) and produces the second-best
  return, but its Sharpe (0.894) is the WORST of the four and its drawdown (7.00%) exceeds even the
  current baseline — high-volume strategies added more volatility than return per unit of risk.
- **Aggressive looks best on paper (Sharpe 1.224, profit factor 3.039, return 21.58%) but this number
  should NOT be trusted at face value.** Only 5 of its 40 eligible strategies traded AT ALL (S1, S5,
  S25, S39, S46), and **S1 alone contributed +$327.04 of the +$431.60 total** via just 6 trades at an
  extreme +21.6R expectancy (§6) — a result driven by path-dependent slot-timing luck, not by 40
  strategies genuinely working together. Average holding period ballooned to 1,046 bars (vs. 173 in
  the baseline) — a handful of positions rode extremely long trends while occupying the shared slot
  for the majority of the entire 3.6-year window, mechanically suppressing every other strategy's own
  opportunity to trade. **This is the single most important finding of this audit**: removing just 3
  clearly-losing strategies (S14/S26/S42) triggered a completely different, far more concentrated
  trade sequence for the remaining 40 — proof that this portfolio's results are highly sensitive to
  strategy-set composition in a way that is NOT simply "sum of the parts," because of the single
  shared position slot.
- **Current (all 43)** sits in the middle on every metric except trade count and diversity (most
  distinct strategies contributing, 29 of 43) — the most BROADLY-representative sample of the
  portfolio's real behavior, even though not the highest Sharpe or return of the four.

---

## 8. Verdict

**AI Trader is NOT yet ready to proceed to broker/live/paper-trading stages, and further
investigation is needed before ANY optimization or portfolio-composition decision — this is an
analytical finding of this audit, not a new instruction to act on it.**

Reasons, all evidence-based:

1. **The system is highly path-dependent on strategy-set composition.** §7's Aggressive-variant
   result demonstrates that removing 3 losing strategies can concentrate over 75% of total profit
   into 6 trades from ONE strategy (S1) via extended slot occupation — a fragility, not a robustness
   signal. Any portfolio-composition decision made from a single run's numbers (this one included)
   risks mistaking a lucky, non-repeatable trade sequence for a genuine edge.
2. **Sample sizes are mostly too small to act on.** 25 of 43 strategies have fewer than 5 trades in
   the baseline run (14 with zero); even the VERY_GOOD tier's own 6 members average only ~10 trades
   each. No statistically meaningful conclusion can be drawn about most individual strategies from
   this run alone.
3. **The Research Lab's own v0 confidence and this run's own tiering frequently disagree** (§3) — most
   VERY_GOOD-tier strategies here (S2, S13, S28, S44) carry VERY LOW/NEGATIVE confidence from the
   Research Lab's own unconstrained backtests. This divergence is not resolved by this audit and
   needs its own investigation (is the disagreement caused by the single-slot constraint changing
   which trades each strategy actually gets, per §5/§6? Or a genuine difference between isolated and
   portfolio-context performance?).
4. **Zero execution costs were modeled** (spread/commission/slippage all $0.00, already disclosed in
   the original Wave D report) — every number in this audit, including all 4 portfolio variants,
   overstates real-world profitability by an unknown amount.
5. **A single symbol, single slot** means these results say nothing about a multi-symbol future, and
   the severe slot competition (70,467 `LIMIT_MAX_PER_SYMBOL` denials) is itself evidence that the
   current 43-strategy portfolio is not well-matched to a single-symbol, single-position execution
   model — most strategies barely get to express their edge at all.

**Recommended next investigation (analysis only, still no implementation)**: a longer, or
multiple-seed/multiple-period, set of reruns to test whether the Conservative/Balanced/Aggressive
rankings in §7 are stable or artifacts of this one specific historical path — before treating any of
the 4 portfolios compared here as a genuine improvement over another. This report does not recommend
adopting any of the 3 variants; it demonstrates that the current evidence base is not yet sufficient
to choose between them with confidence.
