# ACCEPTANCE → RETEST → HOLD → L2 V1

New mechanism branch (NOT level-to-level V4). Tests whether waiting for a **retest of the broken level L1 that holds** — rather than entering at
acceptance — fixes the geometry that the closed execution arc could not. ONE frozen implementation, no parameter mining, no context filter, no
old-strategy rescue. Break + acceptance + L1/L2 identities all bound to the frozen V1 universe (`IDENTITY_GATE = PASS`, `PREFLIGHT_DATA = PASS`,
`CAUSALITY_GATE = PASS`, `END_TO_END_EXECUTABLE = YES`). After acceptance, search the next **8** completed M15 bars for the first retest of the
**L1 ± 0.20 ATR** zone; **HOLD** = that bar closes back on the accepted side; enter next open; **target = frozen L2**; **stop = retest-bar extreme
± 0.10 ATR** (floored); 1R = |entry − retest stop|; **no R:R filter**. `PROTOCOL_HASH = 67e69e446511e66ef1c7` (frozen before scoring).

## Headline — the retest fixes reward/risk, but the stop is now too tight and the hold signal too weak
`ACCEPTANCE_RETEST_HOLD_L2_V1_CANDIDATE = NO` · `RETEST_HOLD_INFORMATION_VALUE = NO` · `RETEST_STOP_STILL_SUSPECT = YES`.

Retests are **frequent** and the reward geometry is **repaired**, but two coupled defects keep expectancy negative.

### Retest funnel (of 62,550 accepted breaks with a valid L2)
| population | count | share |
|---|---|---|
| L2 reached **before** any retest (P4) | 23,025 | 36.8% |
| retest **HOLD** (P1, traded) | 24,685 | 39.5% |
| retest **FAILURE** (P2, control) | 13,245 | 21.2% |
| no retest within 8 bars (P3) | 1,595 | 2.6% |
| **retest within 8 bars** | **37,930** | **60.7%** |

→ 16,994 independent trades, **1,133/yr** (HIGH frequency).

### The retest-hold signal does NOT discriminate (§18 gate FAIL)
| | L2 reach rate |
|---|---|
| after retest **HOLD** | **73.8%** |
| after retest **FAILURE** | **60.7%** |
| **lift** | **+13.1pp** (gate needs ≥ +15pp) |
| chronological folds | [13.1, 13.1, 13.1] (3/3 same sign, but sub-threshold) |
| MFE/MAE after hold vs fail | 1.00 vs 0.99 (not materially better) |

Even a **failed** retest reaches L2 60.7% of the time — once a break is accepted, price travels to L2 regardless of whether the retest holds. The
hold/fail distinction carries only weak incremental information. Over acceptance alone (§19), waiting for a hold lifts the L2 rate just **+5.6pp**
(68.2% → 73.8%). `RETEST_HOLD_INFORMATION_VALUE = NO`.

### Reward/risk — FIXED; stop survivability — BROKEN
| metric | value |
|---|---|
| **median natural RR** | **2.11** (P25 0.93 · P75 4.56; 73% ≥ 1R, 61% ≥ 1.5R, 38% > 3R) |
| WR / BASE / STRESS | 33.4% / **−0.112R** / −0.160R · PF 0.843 |
| avg win / avg loss | +1.809R / −1.077R |
| realized-loss tail | P95 1.25R · P99 1.45R · MAX 1.50R (bounded — clean structural stop) |
| **STOP_THEN_L2 (4/8/16/32 bars)** | 22.2% / 32.8% / 45.8% / **58.0%** |
| winner MAE (median) | 0.36R · 31.3% of winners come within 20% of the stop |

The retest entry near L1 **repairs the reward geometry** — median RR climbs from V1's 0.71 to **2.11**. But the tight retest stop sits exactly where
price probes: **58% of stopped trades later reach L2** within 32 bars (worse than V1's 51%), and winners routinely graze the stop (median MAE 0.36R,
a third within 20% of it). WR collapses to 33.4%, and `0.334 × 1.809 − 0.666 × 1.077 = −0.112R`. `RETEST_STOP_STILL_SUSPECT = YES`. The deficit is
broad, not a tail (drop-worst-5% still −0.049); 0/3 chronological thirds positive.

## §38 CEO answers
1. **Retest L1 within 8 bars?** 37,930. 2. **Reach L2 before retesting?** 23,025. 3. **HOLD?** 24,685. 4. **FAIL?** 13,245. 5. **Trades/yr?**
1,133. 6. **L2 rate after HOLD?** 73.8%. 7. **After FAILURE?** 60.7%. 8. **Lift?** +13.1pp. 9. **Info ≥2/3 chronology?** sign yes (3/3) but
magnitude < 15pp and MFE/MAE flat → `INFO_VALUE = NO`. 10. **Improve on acceptance alone?** +5.6pp (marginal). 11. **Median entry→L2?** 2.11R. 12.
**Median retest-stop distance?** ≈ the retest-bar range + 0.10 ATR (tight — that is the problem). 13. **Median natural RR?** 2.11. 14. **% RR ≥ 1?**
73.2%. 15. **% RR ≥ 1.5?** 61.4%. 16. **BASE?** −0.112R. 17. **STRESS?** −0.160R. 18. **PF?** 0.843. 19. **MaxDD?** 1,998R. 20. **% stopped later
reach L2?** 58.0%. 21. **Retest solve the stop problem?** NO — the retest stop is *too tight* (58% stop-then-L2). 22. **Retest solve the
reward/risk problem?** YES (median RR 0.71 → 2.11). 23. **100-pip opportunities/yr?** 34 (50p 104 · 150p 17 · 200p 10). 24. **L2 within
4/8/16/32 bars?** 86.4% / 93.6% / 97.1% / 98.8% (fast when it works). 25. **Best level type (descriptive)?** LTYPE_2 session H/L (−0.098, least
bad; none positive) — `FOLLOW_UP_HYPOTHESIS_ONLY`. 26. **Frequent enough?** YES (HIGH). 27. **Pass the full gate?** NO.

Direction (diagnostic, not converted): LONG −0.091R (n 8,467) · SHORT −0.133R (n 8,527) — both negative. Retest depth: median 0.02 ATR (shallow).

## §40 FINAL OUTPUT
```
ACCEPTANCE_RETEST_HOLD_L2_V1_COMPLETE = YES · PROTOCOL_HASH = 67e69e446511e66ef1c7 · IDENTITY_GATE = PASS
ACCEPTED_BREAK_EVENTS = 72103
L2_REACHED_BEFORE_RETEST = 23025 · RETEST_WITHIN_8_BARS = 37930 · RETEST_HOLD_EVENTS = 24685 · RETEST_FAILURE_EVENTS = 13245 · NO_RETEST_WITHIN_WINDOW = 1595
INDEPENDENT_TRADES = 16994 · TRADES_PER_YEAR = 1133
ACCEPTANCE_ONLY_L2_RATE = 68.2% · RETEST_HOLD_L2_RATE = 73.8% · RETEST_FAILURE_L2_RATE = 60.7%
RETEST_HOLD_INCREMENTAL_LIFT_PP = 5.6 · RETEST_HOLD_VS_FAILURE_LIFT_PP = 13.1
RETEST_HOLD_INFORMATION_VALUE = NO
MEDIAN_NATURAL_RR = 2.11
BASE_EXPECTANCY_R = -0.1124 · STRESS_EXPECTANCY_R = -0.1596 · PROFIT_FACTOR = 0.843 · MAX_DRAWDOWN_R = 1998
STOP_THEN_L2_32_PERCENT = 58.0 · RETEST_STOP_STILL_SUSPECT = YES
MOVES_50_PIPS_PER_YEAR = 104 · MOVES_100_PIPS_PER_YEAR = 34 · MOVES_150_PIPS_PER_YEAR = 17 · MOVES_200_PIPS_PER_YEAR = 10
BEST_LEVEL_TYPE_DESCRIPTIVE = LTYPE_2 session H/L (FOLLOW_UP_HYPOTHESIS_ONLY)
ACCEPTANCE_RETEST_HOLD_L2_V1_CANDIDATE = NO
READY_FOR_INDEPENDENT_FALSIFICATION = NO
BINDING_FAILURE_REASON = RETEST_HOLD_DOES_NOT_DISCRIMINATE (+13.1pp < 15pp, MFE/MAE 1.00 vs 0.99, failed retests still reach L2 60.7%) + RETEST_STOP_TOO_TIGHT (58% stop-then-L2, WR 33%, winner MAE grazes stop) + NEGATIVE_EXPECTANCY
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scientific interpretation (§36) — the level-to-level behavior is NOT falsified
The accepted-break → L2 behavior is already established and is *reconfirmed* here (hold 73.8%, failure 60.7%, acceptance-only 68.2%). The retest
mechanism specifically: it **repairs the reward geometry** the execution arc lacked (median RR 0.71 → 2.11) and keeps the tail clean (P99 1.45R),
but it fails for two new reasons — the retest **hold/fail signal does not discriminate** strongly enough (+13.1pp; failed retests still reach L2
60.7%), and the retest-based **stop is too tight** (58% stop-then-L2, WR 33%). Read together with the execution arc, the two branches **bracket**
the problem: a wide structural stop gives poor R:R (V1) or low reach at RR≥1 (V3); a tight retest stop gives good R:R but is wicked out (this
branch). No structural stop distance simultaneously survives the noise around the level **and** yields positive expectancy — the accepted-break L2
move is real but **shallow and fast relative to the noise band around the level** (86% of winners reach L2 within 4 bars, median retest depth 0.02
ATR). This is market microstructure, not an execution defect, and not a refutation of the behavior. Per §37 this is the final iteration of this
branch — no V2, no window/buffer change, no R:R filter, no level-type selection. No parameter mined, no strategy promoted, no subtype converted. S5
remains the sole validated tradeable XAUUSD edge. Protections intact.
```
ACCEPTANCE_RETEST_HOLD_L2_V1 = COMPLETE — retest FIXES R:R (2.11) but stop too tight (58% stop-then-L2) + hold signal weak (+13.1pp); candidate = NO
```
