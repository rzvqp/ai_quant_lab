# DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1_REPORT — final

The final price-only architectural branch: monetize XAU's confirmed large-move distribution WITHOUT predicting direction — a two-sided OCO
activation where the market selects the side via the first causal trigger. Native M15 2011-2026 (355,696 bars, 14yr), one independent
episode/day, conservative same-bar (both activations in one bar → ambiguous/skip; entry+stop in one bar → stop), cost 0.419 price/trade,
24h=96-bar horizon. Code: `dae_scan.py`, `dae_payoff.py`. **The first architecture besides S5 to show cross-era-stable positive expectancy —
but too marginal to promote.**

## §5 Positive control — PASS
Injected +1 prior-day-range/day upward drift → OCO continuation net **+0.867** (WR 0.972), stable DEV/OOS/pre/post, drop-best-5% +0.861.
The framework correctly monetizes a genuine two-sided expansion when direction persists. `POSITIVE_CONTROL = PASS`.

## §7/§19 Two-sided activation & whipsaw stats (anchor B = prior-day high/low)
```
episodes(days) ≈ 4,665 · median prior-day range 17.5 USD (175 pips)
FILL_RATE ≈ 0.865 · NO_TRIGGER_RATE ≈ 0.134 · BOTH_SIDES_SAME_BAR ≈ 0.002 (conservatively skipped)
```

## §14/§16 Architectures vs benchmark (net-R after cost, independent daily episodes)
```
A.daily-open ±0.5·PDR  CONTINUATION   net +0.018  DEV -0.003/OOS +0.045  PRE +0.005/POST +0.040
B.prior-day H/L        CONTINUATION   net +0.032  DEV +0.019/OOS +0.047  PRE +0.022/POST +0.047   dropBest1% +0.022 / dropBest5% -0.019
   ... target 1.5R                     net +0.045  ...  PRE +0.034/POST +0.064                       dropBest1% +0.030 / dropBest5% -0.030
   ... target 2.0R                     net +0.054  DEV +0.043/OOS +0.069  PRE +0.048/POST +0.066     dropBest1% +0.035 / dropBest5% -0.046
A/B  FAILED-REVERSAL                   net -0.10 .. -0.19  (all negative)
BENCHMARK random-direction            net -0.026
```
**`DIRECTION_AGNOSTIC_SELECTION_INCREMENTAL_VALUE = YES`** — the OCO continuation beats random-direction by +0.05..+0.08R and is positive in
DEV, OOS, pre-2021 AND post-2021. **Failed-first-side reversal has no value** (all negative). Higher targets pay more (+0.054R at 2R).

## §18/§20 Outlier & robustness — genuine but THIN (not a Family-E mirage)
`dropBest1% stays POSITIVE` at every payoff (+0.022..+0.035) — removing the single most-extreme 1% does NOT flip it (top1%PnL 0.31–0.36, vs
Family-E's 0.80). So it is **not** a single-outlier mirage. BUT `dropBest5% is negative` (−0.019..−0.046): the per-trade edge is small
(WR ~0.51 on 1:1), so removing 5% of wins flips it. This is a **thin** edge, not a fake one.

## §24 CEO questions
1. **Can XAU's large-move distribution be monetized WITHOUT predicting direction?** **YES, marginally.** The two-sided OCO continuation is +0.03..+0.05R, cross-era-stable, and beats random — the campaign's best result besides S5. Direction-agnostic harvest genuinely works.
2. **Does the first market-selected side persist enough to pay for whipsaws + costs?** **Barely.** WR ~0.51; the first side continues just often enough (with wide, cheap structural stops) to net +0.03..+0.05R. Thin.
3. **If first-side continuation fails, does failed-first-side reversal contain information?** **NO** — all reversal architectures net −0.10..−0.19.
4. **Is direction prediction actually necessary for Strategy #2?** **NO.** Direction-agnostic market-selection is the only architecture besides S5 to show cross-era-stable positive expectancy. Prediction is not required; the harvest frame is correct.
5. **If this branch fails, is further price-only discovery high-value?** For NEW price-only *prediction* mechanisms: **LOW** (exhausted). Refining this direction-agnostic *harvest* edge (payoff/episode selection, better anchors) is the one remaining price-only avenue with a positive signal — but it is marginal, so exogenous data remains the higher-value direction.

## §23 VERDICT
```
DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1_COMPLETE = YES
POSITIVE_CONTROL = PASS
ANCHOR_CLASSES_TESTED = 2 (daily-open, prior-day-range) · ACTIVATION_GEOMETRIES_TESTED = 3 (0.25/0.5·PDR, prior-day extremes)
ARCHITECTURES_TESTED = 2 (continuation, failed-reversal) × 3 payoffs (1/1.5/2R)
INDEPENDENT_EPISODES ≈ 4,033 (anchor B) / 4,665 total days
FIRST_SIDE_FILL_RATE ≈ 0.865 · BOTH_SIDES_SAME_BAR ≈ 0.002 · NO_TRIGGER ≈ 0.134
DIRECTION_AGNOSTIC_SELECTION_INCREMENTAL_VALUE = YES
STATISTICALLY_MEANINGFUL_INFORMATION_FOUND = YES
STRATEGY_INTERPRETATIONS_SURVIVED = 0 (strict gate: economically marginal +0.03..0.05R; dropBest5% negative)
BEST_GROSS_EXPECTANCY ≈ +0.065R · BEST_BASE_NET_EXPECTANCY = +0.054R (2R target) · BEST_STRESS_NET ≈ +0.045R (2× cost)
PRE_2021_SUPPORT = YES (+0.02..+0.05) · POST_2021_SUPPORT = YES (+0.04..+0.07)
OUTLIER_ROBUST = PARTIAL (dropBest1% positive = not a single-outlier mirage; dropBest5% negative = thin)
NEW_STRATEGY_CANDIDATE = none promoted — OCO prior-day continuation flagged as the campaign's strongest near-miss
READY_FOR_INDEPENDENT_VALIDATION = NO (too marginal to hand off; cross-era-stable but thin)
S5_MECHANISM_CLONED = NO
```

## §25 PROTECTION
S5·Q4·AI_Trader·P007·MGMT004·MT5·StrategyCatalog untouched; L1·P2·V2-4·Family-E·Scheduled-Events not reopened; no promotion.

## Honest summary — the thesis is validated, the edge is thin
This closes the price-only search on a genuinely positive note that vindicates the architecture audit: after ~13 frontiers of failed
*direction prediction*, the **direction-AGNOSTIC** architecture is the first thing besides S5 to beat random and stay positive across both
eras, with a passing positive control and no single-outlier dependence. **Direction prediction is not necessary** — the market can select
the side. But the harvested edge is **economically marginal** (+0.03..+0.05R, WR ~0.51), so it does not clear the bar for a robust standalone
Strategy #2 today. It is the strongest lead the campaign has produced besides S5, and the only remaining price-only avenue worth refining;
the higher-value direction overall remains exogenous data (real yields). S5 remains the sole deployable edge.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
