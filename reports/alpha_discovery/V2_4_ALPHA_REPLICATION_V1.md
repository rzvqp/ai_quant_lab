# V2_4_ALPHA_REPLICATION_V1 — independent Alpha replication of Statistician lead V2-4 (RANGE COILED)

Independent replication of the frozen Statistician Scout-V2 lead **V2-4 (range coiled → faster ±100p)**. EXACT spec read from
`ai_quant_lab/statistician/scout_v2/{v2_scan.py,v2_targets.py}` — not reconstructed. Code: `sc_V2_4.py`. Native governed M5 2021-07-27→2026-07-27.

## §1 Exact spec (from Statistician code, verbatim logic)
```
tr=true range ; atr=SMA(tr,14)
hi48=roll(48).max(high).shift(1) ; lo48=roll(48).min(low).shift(1)
w48=(hi48-lo48)/max(atr,1e-9)                    # 48-bar range in ATR units
w48p=roll(2000).rank(pct=True)(w48).shift(1)     # causal trailing-2000-bar percentile
V2-4 STATE (D1) = w48p < 0.2                      # 48-bar range bottom-20% vs ATR = "coiled" (energy without displacement)
TARGET A1 = hours to FIRST ±100p touch (first_touch(100,100), horizon H=288 bars = 24h)
BASELINE = ~state ; DEV ≤ 2024-06-30 ; day-clustered SE/z (Statistician cl); per-bar events
V2_4_SPEC_REPRODUCIBLE = YES · V2_4_SPEC_HASH = bc163f1133debcf4
```

## §2 Information reproduction — EXACT match to Statistician
```
DEV: coiled 8.49h vs base 9.38h · lift -0.89h · z -5.43 · N=36,036 · days=802   (Statistician: -0.89h, z≈-5.43) ✓
OOS: lift -0.55h · z -4.49                                                       (Statistician: z≈-4.49)          ✓
per-year lift: 2021 -0.94 / 2022 -0.86 / 2023 -1.01 / 2024 -0.76 / 2025 -0.65 / 2026 -0.20  → 6/6 same sign ✓
```
`V2_4_INFORMATION_REPRODUCED = YES` — the exact headline reproduces, confirming spec fidelity. The phenomenon is real *as a statistic*.

## §3 What it predicts
`B2 = P(+100 before -100)`: coiled 0.511 vs base 0.516 (lift −0.005 ≈ 0). **`PRIMARY_INFORMATION_TYPE = TIMING / EXPANSION` — not
directional.** Coiled changes WHEN a ±100p move happens (unconditionally faster), not WHICH way.

## §4 Session confound — RESOLVED (the decisive test)
```
unconditional DEV lift          = -0.89h  (coiled FASTER)
N-weighted WITHIN-HOUR lift      = +0.20h  (sign REVERSES after controlling for hour-of-day)
by session:  AS +0.43h (z+2.50)  LN +0.42h (z+1.82)  NY -0.67h (z-2.15)  LT -2.47h (z-5.60, N=1749)
non-overlap (1 coiled event/day) = +0.92h (z+4.62)   (coiled SLOWER on non-overlapping daily events)
```
Within any given hour, coiled is **not** faster (Asia/London it is slightly SLOWER; only NY/late is faster, i.e. coiled states that
persist into the active-session expansion resolve there). The unconditional −0.89h is almost entirely a **time-of-day composition
artifact**: coiled clusters in quiet hours, and its "fast" ±100p resolutions are the ones that survive into London/NY.
`SESSION_CONFOUND_RESOLVED = YES` → `V2_4_INCREMENTAL_INFORMATION_AFTER_SESSION_CONTROL = NO`.

## §6 Strategy formation — gate NOT passed
§6 requires BOTH information-reproduced AND incremental-after-session-control. The latter is NO, so **no strategy interpretation is
constructed** (per the mandate's own gate). `STRATEGY_INTERPRETATIONS_TESTED = 0`.

## §11 VERDICT
```
V2_4_ALPHA_REPLICATION_COMPLETE = YES
V2_4_SPEC_REPRODUCIBLE = YES
V2_4_INFORMATION_REPRODUCED = YES (exact: DEV z -5.43 / OOS z -4.49 / 6-of-6 years / -0.89h)
PRIMARY_INFORMATION_TYPE = TIMING / EXPANSION (direction-symmetric, B2≈0.51)
SESSION_CONFOUND_RESOLVED = YES
V2_4_INCREMENTAL_INFORMATION_AFTER_SESSION_CONTROL = NO
STRATEGY_INTERPRETATIONS_TESTED = 0
STRATEGY_INTERPRETATIONS_SURVIVED = 0
V2_4_INCREMENTAL_TRADE_INFORMATION = NO
NEW_STRATEGY_CANDIDATE = none
READY_FOR_INDEPENDENT_VALIDATION = NO
```

## §12 PROTECTION
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES ·
STRATEGY_CATALOG_UNTOUCHED=YES · L1_UNTOUCHED=YES · P2_UNTOUCHED=YES · no promotion.

## Honest summary
V2-4 is a **real statistic but a confounded one**. The independent replication reproduced the Statistician's exact z-scores (−5.43/−4.49,
6/6 years), which is strong evidence of faithful reproduction — and then resolved the session concern the Statistician flagged: after
controlling for hour-of-day the "coiled → faster" effect reverses (+0.20h) and is sign-mixed across sessions. **V2-4 captures WHEN a coiled
state tends to occur (quiet hours that resolve into active sessions), not a genuine coiled-state hazard.** It is not Strategy #2. This is the
independent-replication gate working as intended: a strong statistic that does not survive the confound control that discovery flagged.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
