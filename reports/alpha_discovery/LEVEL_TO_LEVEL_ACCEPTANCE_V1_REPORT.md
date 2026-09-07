# LEVEL-TO-LEVEL ACCEPTANCE STRATEGY V1

Direct follow-up to the execution forensics. Tests one frozen causal mechanism: known level **L1** → M15 close-break → **acceptance** (next
completed bar closes on the breakout side) → entry next open → **target = next causally-known level L2** → **stop = structural invalidation**
(break→acceptance extreme ±0.10 ATR, floored). Trade every accepted occurrence, one active trade at a time; no parameter mining, no context
filter. `PROTOCOL_HASH = 2a9f0c09eb50be79f3a0`. DISCOVERY / INTERNAL_GENERALIZATION only (hypothesis from materially-exposed forensics). Pre-flight
PASS; protections intact.

## Headline — the market BEHAVIOR is real and robust; the naive geometry is NOT tradeable
`LEVEL_TO_LEVEL_BEHAVIOR_CONFIRMED = YES` · `ACCEPTANCE_INFORMATION_VALUE = YES` — but `LEVEL_TO_LEVEL_STRATEGY_CANDIDATE = NO`.

### Behavior (confirmed, strong, cross-era)
Across 102,458 raw level breaks (70.4% accepted): **accepted breaks reach the next level 68.2% of the time vs 14.5% for rejected breaks —
a +53.7pp lift, confirmed in 3/3 chronological folds (52.6 / 55.2 / 53.3pp).** Acceptance does enormous work: whether a break *holds* (closes
back on the breakout side) is a genuine, stable predictor of whether price travels to the next structural level. This validates the forensic
level-to-level hypothesis decisively.

### Why the strategy still loses — the target is closer than the stop (R:R < 1)
| metric | value |
|---|---|
| independent trades / year | 1,872 (HIGH frequency) · WR 54.7% |
| **BASE expectancy** | **−0.065R** · STRESS −0.085R · PF 0.857 |
| **median natural target (L2)** | **0.71R** (P25 0.32R · P75 1.47R) |
| level-target-R buckets | <0.5R **37.8%** · 0.5–1R 24.1% · 1–1.5R 13.6% · 1.5–2R 7.9% · >2R 16.7% |
| chronological thirds | −0.097 / −0.071 / −0.027 (0/3 positive) · drop-best-5% −0.217 |
| STOP_HIT_THEN_L2 | **51.0%** → `STOP_GEOMETRY_STILL_SUSPECT = YES` |

The next causal level is typically **nearer** than the structural-invalidation stop: 62% of trades have a natural target below 1R while the stop
is a full swing. So even at a 68% reach rate the payoff is sub-1R per win against −1R losses → **negative expectancy from reward/risk < 1**. And
the structural stop is itself still suspect — when hit, price reaches L2 within 32 bars **51%** of the time.

### The forensic problem is half-solved, half-inverted
- **Target problem — SOLVED.** The L2-vs-2R counterfactual: the natural level lies *before* the old fixed 2R target in **80.7%** of trades (reproducing the forensic mismatch). Targeting the reachable level fixes "2R beyond structure".
- **Stop problem — NOT solved, inverted.** The structural stop is now the *farther* distance (target 0.71R, stop 1R), and 51% of stops still
  recover to L2 — so the geometry swings from "target too far" to "target too close relative to a wide structural stop".

## §32 CEO answers
1. **Breaks/yr?** ~6,830. 2. **Accepted?** 72,103 (70.4%). 3. **Independent trades/yr?** 1,872. 4. **Accepted → L2 reached?** 68.2%. 5.
**Rejected → L2?** 14.5%. 6. **Lift?** +53.7pp. 7. **Acceptance info ≥2/3 chronology?** YES (3/3). 8. **Median L1→L2?** 0.71R. 9. **Median
structural risk?** the floored structural stop (~a full swing; > the median target). 10. **Median natural target in R?** 0.71R. 11. **<1R?**
61.9%. 12. **1–2R?** 21.5%. 13. **>2R?** 16.7%. 14. **BASE exp?** −0.065R. 15. **STRESS?** −0.085R. 16. **PF?** 0.857. 17. **maxDD?** 1,863R over
28,086 trades (a losing system, not a drawdown of an edge). 18. **drop-best-5% positive?** NO (−0.217). 19. **Stops still stop-then-L2?** 51%.
20–23. **Moves/yr:** 50-pip 232 · 100-pip 76 · 150-pip 39 · 200-pip 23 (meaningful moves ARE frequent). 24. **Best level class (descriptive):**
previous-day levels (LTYPE_1, exp +0.037R, reach 63.7%) — `FOLLOW_UP_HYPOTHESIS_ONLY`. 25. **Level-to-level solve the target problem?** YES. 26.
**Structural invalidation solve the stop problem?** NO (51% stop-then-L2; stop too wide vs the near target). 27. **Frequent enough?** YES (HIGH).
28. **Pass full gate?** NO.

## §37 FINAL OUTPUT
```
LEVEL_TO_LEVEL_ACCEPTANCE_V1_COMPLETE = YES · PROTOCOL_HASH = 2a9f0c09eb50be79f3a0 · PREFLIGHT = PASS
RAW_BREAK_EVENTS = 102458 · ACCEPTED_BREAK_EVENTS = 72103 · REJECTED_BREAK_EVENTS = 30355
INDEPENDENT_TRADES = 28086 · TRADES_PER_YEAR = 1872
ACCEPTED_BREAK_NEXT_LEVEL_RATE = 68.2% · REJECTED_BREAK_NEXT_LEVEL_RATE = 14.5% · NEXT_LEVEL_REACH_LIFT_PP = 53.7
LEVEL_TO_LEVEL_BEHAVIOR_CONFIRMED = YES · ACCEPTANCE_INFORMATION_VALUE = YES
BASE_EXPECTANCY_R = -0.0652 · STRESS_EXPECTANCY_R = -0.0847 · PROFIT_FACTOR = 0.857 · MAX_DRAWDOWN_R = 1863
MEDIAN_LEVEL_TARGET_R = 0.71 · DROP_BEST_5_PERCENT_EXPECTANCY = -0.2168
STOP_HIT_THEN_L2_PERCENT = 51.0 · STOP_GEOMETRY_STILL_SUSPECT = YES
MOVES_50_PIPS_PER_YEAR = 232 · MOVES_100_PIPS_PER_YEAR = 76 · MOVES_150_PIPS_PER_YEAR = 39 · MOVES_200_PIPS_PER_YEAR = 23
BEST_LEVEL_TYPE_DESCRIPTIVE = LTYPE_1 previous-day H/L (FOLLOW_UP_HYPOTHESIS_ONLY)
LEVEL_TO_LEVEL_STRATEGY_CANDIDATE = NO
READY_FOR_INDEPENDENT_FALSIFICATION = NO
BINDING_FAILURE_REASON = POOR_RISK_REWARD_GEOMETRY (natural target 0.71R < structural stop; reward/risk < 1) + STOP_GEOMETRY_STILL_WRONG (51% stop-then-L2)
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scope
The specified frozen level-to-level acceptance mechanism did not produce a tradeable edge on the governed M15 history: the *behavior* is real
and strongly confirmed (accepted breaks reach the next level 68% vs 15%, +53.7pp, 3/3 folds), but the naive structural-stop + next-level-target
*geometry* has reward/risk < 1 (median 0.71R) and a still-suspect stop, so expectancy is negative. No parameter was mined, no strategy promoted,
no post-hoc subtype converted into the strategy (previous-day levels are `FOLLOW_UP_HYPOTHESIS_ONLY`). No broader claim.
```
LEVEL_TO_LEVEL_ACCEPTANCE_V1 = COMPLETE — behavior CONFIRMED (+53.7pp) but geometry not tradeable (target 0.71R < stop); candidate = NO
```
