# ACCEPTED BREAK → STRUCTURAL REACTION ZONE → CONFIRMED ENTRY → L2 V1

New entry-mechanism branch (LOCATION + REACTION + CONFIRMATION), NOT retest-hold V2. Tests whether waiting for a genuine structural-zone reaction
plus continuation confirmation produces a materially better entry into the already-confirmed L1→L2 move. ONE frozen implementation, no parameter
mining, no context filter, no old-strategy rescue. Bound to the frozen V1 universe (`IDENTITY_GATE = PASS`, `PREFLIGHT_DATA = PASS`,
`CAUSALITY_GATE = PASS`, `END_TO_END_EXECUTABLE = YES`). Anchors reuse **canonical** causal detectors: Z1 causal zigzag S/R, **Z2 `ob_core.detect_obs`**,
**Z3 `imbalance_mechanics.detect_fvgs`**, Z4 breakout-retest (broken confirmed swing, flipped). Sequence: acceptance → pullback (≥0.5 ATR) → first
causal zone touched (LOCATION) → rejection close beyond the zone (REACTION) → break of the most recent causal pullback micro lower-high
(CONFIRMATION) → next-open entry → target L2, stop at the zone distal boundary − 0.10 ATR. No R:R filter. `PROTOCOL_HASH = 65af14a1fba623cb9960`.

## Headline — location+reaction+confirmation adds NO reach information, and the late entry gives poor R:R
`STRUCTURAL_REACTION_TO_L2_V1_CANDIDATE = NO` · `STRUCTURAL_REACTION_ENTRY_INFORMATION = NO`.

### The reaction/confirmation apparatus does not discriminate (§17 gate FAIL)
| population | n | L2 reach |
|---|---|---|
| **P1** zone + rejection + confirmation | 6,411 | **65.4%** |
| **P2** zone touch, no confirmed reaction | 27,143 | **64.9%** |
| P3 pullback, no eligible zone | 56 | 26.8% |
| P4 L2 reached before any entry | 28,940 | — |

**P1 beats P2 by +0.55pp** (gate needs ≥ +15pp), with chronological folds [−0.7, +4.6, −1.9] (sign flips, 1/3 positive). The full
location→reaction→confirmation machinery reaches L2 at the *same rate* as a mere zone touch. It does improve path quality (MFE/MAE 1.49 vs 0.93),
but path quality without a higher reach rate is not tradeable selection. `STRUCTURAL_REACTION_ENTRY_INFORMATION = NO`.

### Confirmation is too late → poor R:R (the entry defect returns)
| metric | value |
|---|---|
| trades / year | 312 (VERY_HIGH) · WR **57.5%** |
| BASE / STRESS | **−0.065R / −0.077R** · PF 0.849 · maxDD 336R |
| avg win / avg loss | +0.636R / −1.012R |
| **median natural RR** | **0.60** (V1 0.71 · retest-hold 2.11) — **68.6% of trades < 1R** |
| realized-loss tail | P95 1.06R · P99 1.09R · MAX 1.50R (cleanly bounded) |
| STOP_THEN_L2 (4/8/16/32) | 10.9 / 17.7 / 26.7 / **38.4%** → `STOP_STILL_SUSPECT = YES` |

WR is high (57.5%) but expectancy negative because the confirmation entry — after the rejection *and* the micro-structure break — is **late**: price
has already lifted off the zone, so the target L2 is closer than the zone-based stop in 69% of trades (median RR 0.60). `0.575 × 0.636 − 0.425 ×
1.012 = −0.065R`. Same poor-R:R geometry as immediate entry (V1), slightly worse because the entry is even later.

### Anchor diagnostics (descriptive, `FOLLOW_UP_HYPOTHESIS_ONLY`, not converted)
| anchor | P1 events | P1 L2 reach | trades | expectancy | WR |
|---|---|---|---|---|---|
| FVG (canonical) | 3,213 | 65.6% | 2,346 | −0.050R | 0.599 |
| Order Block (canonical) | 1,924 | 64.0% | 1,410 | −0.076R | 0.600 |
| Support/Resistance | 935 | 65.2% | 694 | −0.061R | 0.474 |
| Breakout-retest | 339 | 72.0% | 235 | −0.152R | 0.472 |

All anchor types negative; FVG least bad. Confluence is **counter**productive descriptively (single-anchor +0.11R vs 2-anchor −0.16R / 3+ −0.07R) —
`CONFLUENCE_DESCRIPTIVELY_USEFUL = NO`. Neither observation is converted into a strategy (§8/§18/§29).

## §30 CEO answers
1. **Pullback before L2?** 33,610 (P1+P2+P3; 46.3% reach L2 first). 2. **Pullbacks meeting a zone?** 33,554 (99.8% — zones abundant). 3–6.
**Confirmed-entry anchor mix (P1):** S/R 935 · OB 1,924 · FVG 3,213 · breakout-retest 339. 7–8. **Rejection + confirmation (P1)?** 6,411. 9.
**Trades/yr?** 312. 10. **L2 rate after loc+react+confirm?** 65.4%. 11. **After touch, no reaction?** 64.9%. 12. **No zone?** 26.8%. 13. **Adds ≥
15pp?** NO (+0.55pp). 14. **Stable ≥2/3 chronology?** NO. 15. **Median natural RR?** 0.60. 16. **% > 1R?** 31.4%. 17. **% ≥ 1.5R?** 20.0%. 18. **% ≥
2R?** 13.7%. 19. **BASE?** −0.065R. 20. **STRESS?** −0.077R. 21. **PF?** 0.849. 22. **MaxDD?** 336R. 23. **% stopped later reach L2?** 38.4%. 24.
**Did confirmation solve premature entry?** Partially — better path (MFE/MAE 1.49 vs 0.93) but no reach lift and it is *late* → poor RR; net NO. 25.
**Did zone invalidation improve the stop?** Tail cleanly bounded (P99 1.09R) but stop-then-L2 still 38% — the R:R, not the stop, is the killer. 26.
**100-pip opportunities/yr?** 18. 27. **Strongest anchor (descriptive)?** FVG. 28. **Confluence useful?** NO. 29. **M5 earlier confirmation?** NO
(median touch→confirm 1.0 M15 bar; M15-latency proxy, native M5 timing study deferred). 30. **Pass the gate?** NO.

Direction (diagnostic): LONG −0.048R · SHORT −0.084R (both negative).

## §31 FINAL OUTPUT
```
STRUCTURAL_REACTION_TO_L2_V1_COMPLETE = YES · PROTOCOL_HASH = 65af14a1fba623cb9960 · IDENTITY_GATE = PASS
ACCEPTED_BREAK_EVENTS = 72103
PULLBACK_EVENTS = 33610 · WITH_ELIGIBLE_STRUCTURAL_ZONE = 33554
SUPPORT_RESISTANCE_EVENTS = 935 · ORDER_BLOCK_EVENTS = 1924 · FVG_EVENTS = 3213 · BREAKOUT_RETEST_ZONE_EVENTS = 339   (P1 primary-anchor mix)
CONFIRMED_REACTION_EVENTS = 6411
INDEPENDENT_TRADES = 4685 · TRADES_PER_YEAR = 312
CONFIRMED_REACTION_L2_RATE = 65.4% · TOUCH_NO_REACTION_L2_RATE = 64.9% · NO_ZONE_L2_RATE = 26.8%
REACTION_INFORMATION_LIFT_PP = 0.55
STRUCTURAL_REACTION_ENTRY_INFORMATION = NO
MEDIAN_NATURAL_RR = 0.60
BASE_EXPECTANCY_R = -0.0649 · STRESS_EXPECTANCY_R = -0.0773 · PROFIT_FACTOR = 0.849 · MAX_DRAWDOWN_R = 336
STOP_THEN_L2_32_PERCENT = 38.4 · STRUCTURAL_ZONE_STOP_STILL_SUSPECT = YES
MOVES_100_PIPS_PER_YEAR = 18
BEST_ANCHOR_TYPE_DESCRIPTIVE = FVG (FOLLOW_UP_HYPOTHESIS_ONLY) · CONFLUENCE_DESCRIPTIVELY_USEFUL = NO
M5_EARLIER_CONFIRMATION_DIAGNOSTIC = NO
STRUCTURAL_REACTION_TO_L2_V1_CANDIDATE = NO
READY_FOR_INDEPENDENT_FALSIFICATION = NO
BINDING_FAILURE_REASON = REACTION_DOES_NOT_DISCRIMINATE (P1 65.4% vs P2 64.9%, +0.55pp; folds inconsistent) + CONFIRMATION_TOO_LATE + POOR_RR_AFTER_CONFIRMATION (median RR 0.60, 69% < 1R) + NEGATIVE_EXPECTANCY
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scientific interpretation (§28) — no anchor family is refuted
Only this exact frozen relational mechanism was tested — a structural zone as the *location* for a confirmed pullback entry into the accepted
L1→L2 move. It fails because (a) the reaction+confirmation does not raise the probability of reaching L2 (P1 65.4% ≈ P2 64.9%), and (b) waiting for
confirmation makes the entry *late*, so the target is closer than the zone-based stop (median RR 0.60). This does **not** show that support, order
blocks, FVGs, or price action "don't work" — the canonical OB and FVG detectors were used verbatim; they simply carry no incremental information in
this specific relational entry role, and the confirmation timing is geometrically self-defeating here. Read with the prior branches, all five entry
mechanisms tested on the L1→L2 move now agree: the move is real (65–74% reach) but **not monetizable by any entry/stop geometry** — early entry →
poor R:R (V1 0.71); RR≥1 filter → low reach (V3 27%); tight retest stop → wicked out (RTH 58%); late confirmation entry → poor R:R + no selection
(this branch 0.60, +0.55pp). The accepted-break L2 move is shallow and fast relative to the structural noise band. Per §29 this is the final
iteration of this branch — no alternate reaction candle, no M5-entry strategy, no confluence filter, no level-type selection, no parameter tuning.
No parameter mined, no strategy promoted, no subtype converted. S5 remains the sole validated tradeable XAUUSD edge. Protections intact.
```
STRUCTURAL_REACTION_TO_L2_V1 = COMPLETE — reaction+confirmation adds no reach info (+0.55pp), late entry gives poor R:R (0.60); candidate = NO
```
