# LEVEL-TO-LEVEL ACCEPTANCE EXECUTION V2

Bounded execution co-design, ONE frozen implementation, direct follow-up to V1. Same market behavior (`LEVEL_TO_LEVEL_BEHAVIOR_CONFIRMED = YES`,
never re-mined). Two changes only: **(A)** invalidation = **acceptance-failure close** (first completed M15 candle closing back through L1 → exit
next open; no distant structural stop, no same-bar hindsight); **(B)** a pre-entry **natural-geometry gate** `NATURAL_REWARD_RISK = |L2−entry| /
|entry−L1|(floored) ≥ 1.00` (frozen minimal economic condition, NOT PnL-optimized). Bound to the exact V1 event universe —
`V1_IDENTITY_GATE = PASS (102,458 / 72,103 / 30,355)`. `PROTOCOL_HASH = 58c8280847bf794faa84` (frozen before scoring). No parameter search, no
second variant, no context filter.

## Headline — both changes fail; the close-based stop has UNBOUNDED tail risk, the geometry gate is DEGENERATE
`LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_CANDIDATE = NO` · `CLOSE_BASED_INVALIDATION_TAIL_RISK = FAIL` · `ACCEPTANCE_FAILURE_STOP_STILL_SUSPECT = YES`.

The behavior remains real, but the specified execution is worse than V1, for two coupled structural reasons:

### 1. The natural-geometry gate is degenerate under a close-based stop
Because planned risk is defined as the **entry→L1** distance, `RR ≥ 1.00` is *easiest to satisfy when the entry hugs L1* (a near-zero
denominator inflates RR). The gate therefore admits trades with a median natural RR of **3.38** — but that number is illusory: it is high
precisely where the *true* adverse distance (a close back through L1, filled at the next open) is largest relative to the tiny planned risk. The
gate selects the most dangerous geometry, not the safest. It also selects **far** targets, dropping the L2 reach rate from V1's 68.2% (all
accepted) to **39.6%** — far levels are reached less often.

### 2. The acceptance-failure close has no bounded maximum loss
| realized-loss distribution (planned-R) | value |
|---|---|
| P90 | **5.72R** |
| P95 | **7.98R** (gate needs ≤1.50) |
| P99 | **14.29R** (gate needs ≤2.00) |
| MAX | **142.4R** |

An intrabar close through L1 followed by a next-open gap realizes a loss vastly larger than the (floored, tiny) planned risk. `CLOSE_BASED_INVALIDATION_TAIL_RISK = FAIL`.

### Economics
| metric | value |
|---|---|
| trades / year | 1,403 (**VERY_HIGH**) · WR 39.8% |
| **BASE / STRESS expectancy** | **−0.267R / −0.346R** · PF 0.850 · total −5,616R · maxDD 5,963R |
| avg win / avg loss | +3.81R / −2.96R · med win +2.33R / med loss −1.99R |
| exit mix | accept_fail 60.2% · target 39.6% · timeout 0.2% |
| chronological thirds | −0.448 / −0.261 / −0.092 (0/3 positive) |
| drop-best-5% | **−0.934** · **drop-worst-5% +0.267** |

The tail signature is unmistakable: removing the best 5% makes it far worse (−0.934) while removing the **worst** 5% turns it **positive**
(+0.267R). The system is not killed by weak direction — it is killed by a fat **left** tail. The central behavior is intact; the *stop definition*
is uninsurable.

### Stop diagnostic (§26) — not fixed, marginally worse
Of 12,668 losing trades, **52.4%** later reach L2 within 32 bars (V1 was 51.0%). The close-based stop does **not** remove the stop-then-L2
problem — it slightly worsens it and adds the unbounded tail. `ACCEPTANCE_FAILURE_STOP_STILL_SUSPECT = YES`.

### Behavior still confirmed (§18 control, descriptive)
Within the geometry-eligible subset, accepted breaks reach L2 **45.6%** vs geometry-eligible rejected **14.5%** (+31.1pp). The acceptance→level
behavior survives the geometry gate descriptively — the failure is entirely execution, not signal.

## §27 CEO answers
1. **Accepted events surviving RR≥1?** 32,395 (45% of 72,103). 2. **V2 trades/yr?** 1,403. 3. **% reach L2?** 39.6% (trades) / 45.6% (eligible
events). 4. **% fail acceptance first?** 60.2%. 5. **Median natural target R after gate?** 3.38R (illusory — see §1). 6. **Median realized losing
R?** −1.99R. 7. **P95 / P99 losing R?** 7.98 / 14.29. 8. **Does close-based invalidation remove the 51% stop-then-L2?** NO — 52.4% (worse). 9. **%
of V2 losers later reaching L2?** 52.4%. 10. **BASE?** −0.267R. 11. **STRESS?** −0.346R. 12. **PF?** 0.850. 13. **MaxDD?** 5,963R. 14. **≥2/3
thirds positive?** NO (0/3). 15. **drop-best-5% positive?** NO (−0.934). 16. **100-pip-class/yr?** 62 (50p 181 · 150p 33 · 200p 20). 17.
**Sufficient frequency?** YES (VERY_HIGH) — frequency is not the constraint. 18. **Reward/risk geometry coherent now?** NO — the gate is
degenerate (planned risk → 0 as entry hugs L1). 19. **Risk tail manageable?** NO (P99 14.29R, MAX 142R). 20. **Pass the complete gate?** NO.

Level types (diagnostic, `FOLLOW_UP_HYPOTHESIS_ONLY`, not converted): LTYPE_1 prev-day the only positive class (+0.132R, n=486); LTYPE_2 −0.200,
LTYPE_3 −0.409, LTYPE_4 −0.152.

## §29 FINAL OUTPUT
```
LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_COMPLETE = YES · PROTOCOL_HASH = 58c8280847bf794faa84
V1_ACCEPTED_EVENTS = 72103
V2_GEOMETRY_ELIGIBLE_EVENTS = 32395
V2_INDEPENDENT_TRADES = 21050
V2_TRADES_PER_YEAR = 1403   (VERY_HIGH)
MEDIAN_NATURAL_TARGET_R = 3.38
L2_REACH_RATE = 39.6%
BASE_EXPECTANCY_R = -0.2668
STRESS_EXPECTANCY_R = -0.3458
PROFIT_FACTOR = 0.850
MAX_DRAWDOWN_R = 5963
MEDIAN_REALIZED_LOSS_R = -1.99
P95_REALIZED_LOSS_R = 7.98
P99_REALIZED_LOSS_R = 14.29
MAX_REALIZED_LOSS_R = 142.38
LOSERS_THAT_LATER_REACH_L2_PERCENT = 52.4
ACCEPTANCE_FAILURE_STOP_STILL_SUSPECT = YES
CLOSE_BASED_INVALIDATION_TAIL_RISK = FAIL
MOVES_50_PIPS_PER_YEAR = 181 · MOVES_100_PIPS_PER_YEAR = 62 · MOVES_150_PIPS_PER_YEAR = 33 · MOVES_200_PIPS_PER_YEAR = 20
LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2_CANDIDATE = NO
READY_FOR_INDEPENDENT_FALSIFICATION = NO
BINDING_FAILURE_REASON = CLOSE_BASED_INVALIDATION_UNBOUNDED_TAIL_RISK (P99 14.3R / MAX 142R) + DEGENERATE_NATURAL_GEOMETRY_GATE (planned risk -> 0 as entry hugs L1) + ACCEPTANCE_FAILURE_STOP_STILL_SUSPECT (52.4%)
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scope
The specified frozen V2 execution did not produce a tradeable edge and is worse than V1: the acceptance-failure-close invalidation has no bounded
maximum adverse distance (uninsurable left tail), and the natural-geometry gate — because it normalizes reward by the entry→L1 distance — is
degenerate, admitting the most dangerous "entry-hugging-L1" geometry. The central acceptance→level behavior remains real (drop-worst-5% turns the
system positive; +31pp geometry-eligible lift), so the binding failure is *execution risk geometry*, not signal. Per §8 no hard stop was invented
after seeing the tail; per §24 no second variant was tried. No parameter mined, no strategy promoted, no level-type converted (LTYPE_1 is
`FOLLOW_UP_HYPOTHESIS_ONLY`). No broader claim. Protections intact.
```
LEVEL_TO_LEVEL_ACCEPTANCE_EXECUTION_V2 = COMPLETE — close-based stop UNBOUNDED-TAIL (P99 14R/MAX 142R), geometry gate DEGENERATE; candidate = NO
```
