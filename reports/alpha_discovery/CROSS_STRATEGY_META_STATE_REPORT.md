# CROSS_STRATEGY_META_STATE_REPORT — is there an XAU tradeability regime?

§24-25 deliverable. Pooled 30,703 valid causal trades across 14 independent strategy objects (HTF ×4, OBR-corrected true-limit + OB-exec
×3, session ×6) on the shared M15 panel. Question: do unrelated strategies succeed/fail in the SAME market states? Positive control PASS
(injected high-vol=+0.3 / low-vol=−0.3 recovered exactly). All from `attr_run.py` + `STRATEGY_*.csv`.

## The finding — a consistent "least-bad" tilt, replicated across ~14 strategies, but NOT profitable
Every state category is pooled-negative (no profitable regime), BUT the same axes independently reduce the loss across many strategies:
```
axis            best state       pooled_exp   worst state      pooled_exp   Δ (least-bad lift)
session         NY               -0.112       LT               -0.219       +0.107
volatility      high             -0.106       low              -0.198       +0.092
H4-alignment    ALIGNED          -0.105       COUNTER          -0.199       +0.094
side            LONG             -0.138       SHORT            -0.163       +0.025
```
Each axis is a genuine, cross-strategy conditional-expectancy shift (~+0.09-0.11R). **Stacking them:**
```
ALIGN                       -0.105 (2/13 strategies +)
ALIGN x LONG                -0.085 (3/13)
ALIGN x high-vol            -0.080 (1/13)
NY x high-vol x ALIGN       -0.068 (3/13)
NY x high-vol x ALIGN x LONG -0.052 (4/11)   N=3,829
```
The fully-stacked best-tilt regime improves the average strategy from ~−0.15R to **−0.052R (+0.10R)** and turns 4/11 strategies positive —
**but it remains negative.**

## Interpretation
`CROSS_STRATEGY_META_STATE_FOUND = YES` — there is a real, replicated XAU **tradeability tilt**: price strategies systematically fail LESS
in NY session + high volatility + H4-trend-aligned + long-side conditions. This is consistent across mechanically-unrelated strategies, so
it is a property of the market state, not of any one strategy (most plausibly liquidity + trend/era beta: aligned longs in the active,
volatile NY session bleed least). **But it is a DAMAGE-MITIGATION regime, not a profitable one** — even fully stacked it is −0.05R, so it
cannot rescue any strategy into positive expectancy. It is "where to lose least," not "where to win."

## Practical implication
The tilt is usable as a **NO-TRADE / de-emphasis filter** (avoid COUNTER-trend, Asia/late, low-vol, short-side price entries) to cut losses,
but not as a standalone entry edge. It corroborates the campaign meta-finding: XAU price-only direction is efficient; the only conditional
structure is a beta-like tilt that reduces (never reverses) the negative expectancy of price-only strategies. S5's edge is not explained by
this tilt (S5 is a specific session+structure mechanism, read-only benchmark, untouched).
