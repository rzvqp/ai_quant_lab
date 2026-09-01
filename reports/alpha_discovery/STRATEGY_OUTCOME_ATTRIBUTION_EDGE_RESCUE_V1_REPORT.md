# STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V1_REPORT — final

Systematic outcome attribution across the existing causal strategy graveyard: are failed strategies mixtures of profitable + unprofitable
subpopulations separable by causal PRE-ENTRY state, and do winners/losers diverge early enough POST-ENTRY to support management?
Hypothesis generation only — no promotion, no modification, no validation on reused history. Code: `attr_run.py`. Deliverable CSVs:
`STRATEGY_ATTRIBUTION_MASTER_TABLE / _TIME_BUCKET_MATRIX / _WEEKDAY_MATRIX / _SESSION_MATRIX / _WINNER_LOSER_FEATURE_MATRIX /
_RESCUE_HYPOTHESIS_REGISTER.csv` + `CROSS_STRATEGY_META_STATE_REPORT.md`. `HISTORICAL_REUSE_LIMITATION = ACKNOWLEDGED` (splits are diagnostic).

## §2 Inventory
```
ELIGIBLE_STRATEGIES_ANALYSED = 14 (valid causal, trade-level, on shared M15 panel):
  HTF_{PBK_TREND,RECLAIM,RANGE_FADE,TGT_BREAK} · OBR_A_limit (corrected true resting limit) · OBEXEC_{B,C,D} · SESS_{A,B,C,D,E,Fc}
TOTAL_VALID_TRADES_ANALYSED = 30,703
EXCLUDED_INVALID: OBR fill-artifact version (uses corrected EXEC-A instead) · any lookahead/superseded variants
OTHER OBJECTS (valid but on different panels/formats, not pooled here): M5 Family E, cross-market DXY, long-horizon 24h, direction-agnostic
  OCO (daily), temporal-sequence, contrast-miner H1/H2/H3 — noted; the M15-bar pool gives a coherent cross-strategy feature space.
S5_UNTOUCHED = YES (read-only conceptual benchmark; not filtered/optimized)
```

## §26 Positive control — PASS
Injected synthetic strategy (high-vol=+0.3R, low-vol=−0.3R) → framework recovered lo −0.299 / md −0.001 / hi +0.309. The attribution engine
detects a genuine conditional difference. `POSITIVE_CONTROL = PASS`.

## §7-§16 Attribution result — no strong profitable subpopulation
- **Only 1 of 14 strategies is pooled non-negative** (SESS_A +0.010R = break-even). Every other strategy is negative pooled and in every
  major bucket. The corrected OBR (OBR_A_limit) is −0.067R, best cell NY −0.05 (still negative).
- **Per-strategy "best cells" (e.g. HTF_TGT_BREAK Asia +0.19, small N) are multiplicity-suspect green cells**, not rescues (§8/§11/§17/§18).
- **No recurring day-of-week edge**: best-DoW varies (Mon/Tue/Wed/Thu/Fri all appear for different strategies) = noise.
- **No robustly-positive 30-min bucket** across strategies (see `STRATEGY_TIME_BUCKET_MATRIX.csv`; isolated cells only).
- **Consistent "least-bad" tilt** (the one real cross-strategy signal): NY > other sessions, high-vol > low-vol, H4-ALIGNED > COUNTER,
  LONG > SHORT — each ~+0.09-0.11R, replicated across ~14 strategies. Fully stacked (NY×high-vol×ALIGN×LONG) = **−0.052R** (+0.10R vs base,
  4/11 strategies positive) but **still negative**. See `CROSS_STRATEGY_META_STATE_REPORT.md`.

## §21-§23 Post-entry (management) discriminator — strong but partly mechanical
On strategies with MFE/MAE path data (HTF), fixed causal path classes:
```
favorable_early (+0.5R before -0.5R adverse)  final_exp +1.410  WR 0.957
recovered (adverse then partial recovery)      final_exp -0.247  WR 0.326
stagnation                                     final_exp -0.267  WR 0.220
immediate_fail (-1R adverse before +0.5R fav)  final_exp -1.137  WR 0.000
```
`TOP_POST_ENTRY_DISCRIMINATOR = early MFE/MAE ordering.` A trade that reaches −1R adverse before +0.5R favorable **never** recovers to a win
(0%). Useful as a **loss-reduction management hypothesis** (cut early-adverse trades), though partly mechanical (−1R adverse ≈ near the stop).

## §31 CEO questions
1. **How many failed strategies contain a profitable subpopulation worth retesting?** Essentially **zero strong ones**; only SESS_A is break-even. Small-N green cells exist but are multiplicity-suspect.
2. **Recurring time-of-day edge across strategies?** No *profitable* one — NY is consistently the least-bad session (not positive).
3. **Recurring day-of-week edge?** No — weekday "best" varies across strategies (noise).
4. **Do LONG/SHORT differ structurally?** Weakly: LONG (−0.138) less-bad than SHORT (−0.163), consistent across most strategies — a beta-like long tilt, both negative.
5. **Does session explain a material part of win/loss?** Partly (NY vs LT = +0.107R shift) but not enough to make anything positive.
6. **Does volatility explain more than session?** Comparable — vol (+0.092R), session (+0.107R), alignment (+0.094R) are similar-strength tilts.
7. **Do H1/H4 states explain winners vs losers?** Yes, weakly/consistently: H4-ALIGNED loses less than COUNTER across strategies — a real "lose-less" discriminator, still negative.
8. **Can early post-entry path identify losers before full stop?** **Yes, strongly** — early −1R-adverse-before-favorable → 0% eventual win.
9. **Cross-strategy XAU tradeability regime?** **Yes, but not profitable** — NY+high-vol+H4-aligned+long is the replicated least-bad regime (−0.052R stacked). Damage-mitigation, not edge.
10. **One rescue hypothesis to retest as Strategy #2?** None crosses robust positive. The strongest *actionable* leads are (a) the post-entry management overlay (cut early-adverse trades) and (b) — from outside this pool — the direction-agnostic OCO near-miss. Within this attribution: no promotable rescue.

## §32 VERDICT
```
STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V1_COMPLETE = YES
TOTAL_STRATEGY_OBJECTS_FOUND ≈ 20 (incl non-pooled) · ELIGIBLE_STRATEGIES_ANALYSED = 14 · TOTAL_VALID_TRADES_ANALYSED = 30,703
POSITIVE_CONTROL = PASS
PRE_ENTRY_DISCRIMINATORS_FOUND = 4 (session/vol/H4-alignment/side — all "lose-less", none profit-making)
POST_ENTRY_DISCRIMINATORS_FOUND = 1 strong (early MFE/MAE ordering)
STRATEGIES_WITH_RESCUE_SIGNAL_STRONG = 0 · MODERATE = 0 · WEAK = 1 (SESS_A break-even) · NONE = 13
CROSS_STRATEGY_META_STATE_FOUND = YES (NY+high-vol+H4-aligned+long) but NOT PROFITABLE (−0.052R fully stacked)
TOP_RESCUE_HYPOTHESIS = post-entry management (cut trades that hit −1R adverse before +0.5R favorable) as a loss-reduction overlay; and the
  stacked tradeability-tilt as a NO-TRADE filter — neither rescues to positive
SOURCE_STRATEGY = cross-strategy (meta-state) / all HTF for post-entry · SUBSET_N = 3,829 (stacked tilt) / 2,508 (immediate_fail class)
SUBSET_EXPECTANCY = −0.052R (stacked tilt) · EXCLUDED_EXPECTANCY ≈ −0.16R
READY_FOR_INDEPENDENT_RETEST = NO (no rescue crosses robust positive; meta-state is a lose-less tilt, not an edge)
```

## §34 PROTECTION
S5·Q4·AI_Trader·P007·MGMT004·MT5·StrategyCatalog untouched; no strategy definition modified; no promotion; Statistician GC/XAU data-gate
work not touched.

## Honest summary
The graveyard does not contain a hidden profitable strategy waiting to be rescued by a pre-entry filter. Two genuine sub-findings emerged:
(1) a **replicated cross-strategy tradeability tilt** — XAU price strategies lose least in NY / high-vol / H4-aligned / long conditions
(+0.10R stacked, still −0.05R), a damage-mitigation regime consistent with liquidity/trend beta; and (2) a **strong post-entry
loser-identifier** — trades that go adverse before favorable essentially never recover. Neither turns a failed strategy positive. This
confirms, from the opposite direction (mining winners vs losers), the campaign's central result: **XAU price-only direction is efficient;
the only conditional structure is a beta-like tilt that reduces, never reverses, the negative expectancy.** S5 remains the sole edge.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_RETEST = NO
```
