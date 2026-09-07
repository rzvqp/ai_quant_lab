# FAILED ACCEPTANCE → PRIOR LEVEL BEHAVIOR V1

New mechanism family, **behavior-first** — no strategy, no entry/stop/target, no PnL. Question: when a level break FAILS acceptance (price closes
beyond L1, then the acceptance-test bar closes back through L1), does price return toward the previous causally-known level L0? Bound to the frozen
V1 universe — `IDENTITY_GATE = PASS (102,458 / 72,103 / 30,355)`. Failed-acceptance events are exactly the 30,355 rejected breaks. L0 reconstructed
with the exact frozen `levels_at` (0.20 ATR clustering) as the nearest causal level on the reversal side of L1. `PROTOCOL_HASH = ffc5e8e019e4546cdca1`
(frozen before analysis). No parameter mining, no context filter.

## Headline — the destination information is real and strong; the clean-reversal behavior is NOT confirmed
`FAILED_ACCEPTANCE_REVERSAL_INFORMATION = YES` · **but** `FAILED_ACCEPTANCE_REVERSAL_BEHAVIOR_CONFIRMED = NO` · `EXECUTION_RESEARCH_JUSTIFIED = NO`.

### Destination genuinely shifts (§5–§8, the information gate PASSES)
| among failed-acceptance events (valid L0, n=30,262) | value |
|---|---|
| **L0 reached FIRST** | **70.8%** |
| L2 reached first | 25.0% |
| neither within 32 bars | 4.1% |
| L0 / L2 ratio | **2.83** |
| **failed-acceptance L0-reach vs accepted control** | **83.3% vs 62.0% → +21.3pp** |
| chronological folds of the lift | [20.8, 21.5, 21.4] → **3/3** |

This is the strongest, most stable information signal the entire level program has produced: a failed break reaches the prior level first ~2.8× more
often than it continues, and reaches L0 21.3pp more than an accepted break does — rock-stable across all three eras. `FAILED_ACCEPTANCE_REVERSAL_INFORMATION = YES`.

### …but it is a PROXIMITY effect, not a clean directional reversal (§9–§10, the behavior gate FAILS)
| metric | value |
|---|---|
| **reversal MFE/MAE (failed)** | **0.98** — vs accepted control **0.99** (NOT materially better) |
| median bars to L0 | **0** (P25 0 · P75 3) |
| L0 reached within 4 / 8 / 16 / 32 bars | 61.6% / 69.7% / 77.2% / 83.3% |
| distance failure-close → L0 | **0.71 ATR** (L1→L0 1.08 ATR; overshoot beyond L1 before failure 0.53 ATR) |

L0 sits only ~0.71 ATR beyond the failure close and is reached almost immediately (median 0 bars, 62% within 4 bars). The reversal-direction path is
symmetric (MFE/MAE 0.98 ≈ control 0.99) — price does *not* travel more cleanly toward L0 than a random accepted break travels backward. The high
L0-first rate is a **proximity / short-hop-to-a-near-level** effect, not a tradeable directional swing. Even accepted breaks dip back to L0 62% of the
time, confirming L0 is simply close. Per §18's conjunction (which requires reversal MFE/MAE materially better than control), `FAILED_ACCEPTANCE_REVERSAL_BEHAVIOR_CONFIRMED = NO`.

### Move sizes exist but are volatility, not edge (§11)
Reversal-direction favorable excursions/yr: 50-pip 948 · 100-pip 471 · 150-pip 270 · 200-pip 168. Frequent — but with MFE/MAE ≈ 1.0 the comparable
adverse excursion means these are two-sided volatility, not a directional reversal edge. Consistent with the campaign's R20 (XAU M15 direction efficient).

## §20 CEO answers
1. **Failed acceptances?** 30,355. 2. **Per year?** 2,023. 3. **Valid L0?** 30,262. 4. **% reach L0?** 83.3%. 5. **% reach L0 before L2?** 70.8%. 6.
**% reach L2 first?** 25.0%. 7. **% neither within 32?** 4.1%. 8. **Accepted control L0 rate?** 62.0%. 9. **Failed-vs-accepted L0 lift?** +21.3pp. 10.
**Positive in ≥2/3 chronology?** YES (3/3). 11. **Median time to L0?** 0 bars (P75 3) — near-immediate. 12. **% reach L0 within 4/8/16/32?**
61.6/69.7/77.2/83.3%. 13. **Reversal MFE/MAE?** 0.98 (control 0.99 — not better). 14. **Overshoot beyond L1 before failure?** 0.53 ATR. 15.
**Distance failure-close → L0?** 0.71 ATR. 16. **50-pip reversals/yr?** 948. 17. **100-pip?** 471. 18. **150-pip?** 270. 19. **200-pip?** 168. 20.
**Strongest level type?** previous-day L1 (L0-first 73.5%) — `FOLLOW_UP_HYPOTHESIS_ONLY`. 21. **Frequent enough?** YES (daily). 22. **Behavior
confirmed?** NO — destination-information YES, but the clean-travel criterion fails (proximity effect). 23. **Execution research justified?** NO.

Direction (diagnostic): UP-break failures L0-first 73.6% (n 15,435) · DOWN 68.0% (n 14,827). Level types (L1): prev-day 73.5% · session 73.1% ·
swing 65.9% · range 69.3% — none converted.

## §23 FINAL OUTPUT
```
FAILED_ACCEPTANCE_PRIOR_LEVEL_V1_COMPLETE = YES · PROTOCOL_HASH = ffc5e8e019e4546cdca1 · IDENTITY_GATE = PASS
FAILED_ACCEPTANCE_EVENTS = 30355 · FAILED_ACCEPTANCE_EVENTS_PER_YEAR = 2023 · VALID_L0_EVENTS = 30262
FAILED_ACCEPTANCE_L0_RATE = 83.3% · ACCEPTED_BREAK_L0_RATE = 62.0% · L0_REACH_LIFT_PP = 21.3
L0_REACHED_FIRST_PERCENT = 70.8 · L2_REACHED_FIRST_PERCENT = 25.0 · NEITHER_32_PERCENT = 4.1
MEDIAN_BARS_TO_L0 = 0
REVERSAL_MFE_MAE_RATIO = 0.98   (accepted control 0.99)
MEDIAN_FAILURE_OVERSHOOT_ATR = 0.53 · MEDIAN_DISTANCE_FAILURE_TO_L0_ATR = 0.71
MOVES_50_PIPS_PER_YEAR = 948 · MOVES_100_PIPS_PER_YEAR = 471 · MOVES_150_PIPS_PER_YEAR = 270 · MOVES_200_PIPS_PER_YEAR = 168
FAILED_ACCEPTANCE_REVERSAL_INFORMATION = YES
FAILED_ACCEPTANCE_REVERSAL_BEHAVIOR_CONFIRMED = NO
EXECUTION_RESEARCH_JUSTIFIED = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Interpretation
Failed acceptance carries genuine, highly stable **destination information** — the prior level L0 is reached first ~71% of the time and +21.3pp more
than after an accepted break (3/3 folds). This is the clearest information signal in the level program. But it does **not** clear the behavior gate:
L0 is only 0.71 ATR away and is reached in a median of 0 bars, and the reversal path is no cleaner than the accepted-break control (MFE/MAE 0.98 vs
0.99). The signal is a **proximity / mean-reversion-to-nearest-level** effect, not a clean directional reversal swing — reaching a near level quickly
is not the same as travelling to it profitably. This complements the program's R20 finding: level *ordering* (which nearby level is hit first) is
predictable, but directional *travel quality* is not. Per §22 no strategy, stop, target, or V2 was designed. No parameter mined, no subtype
converted (prev-day L1 is `FOLLOW_UP_HYPOTHESIS_ONLY`). S5 remains the sole validated tradeable XAUUSD edge. Protections intact.
```
FAILED_ACCEPTANCE_PRIOR_LEVEL_V1 = COMPLETE — destination-information YES (+21.3pp, L0-first 71%) but a PROXIMITY effect (L0 0.71 ATR, 0 bars, MFE/MAE 0.98); behavior NOT confirmed, execution NOT justified
```
