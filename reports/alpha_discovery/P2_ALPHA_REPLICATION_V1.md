# P2_ALPHA_REPLICATION_V1 — independent Alpha replication of Statistician lead P2 (bottom-of-24h-range downside continuation)

Independent replication of the frozen Statistician Scout-V1 lead **P2**. EXACT spec read from `ai_quant_lab/statistician/scout/scan.py` +
`STAT_ALPHA_SCOUT_V1_REPORT.md` — not reconstructed. Code: `sc_P2.py`. Native governed M5 2021-07-27→2026-07-27.

## §1 Exact spec (from Statistician code)
```
atr=SMA(TR,14) ; hi288=roll(288).max(high).shift(1) ; lo288=roll(288).min(low).shift(1)
S_loc=(c-lo288)/max(hi288-lo288,1e-9)              # location in the trailing 24h (288-bar) range
P2 STATE = S_loc < 0.1                              # lowest decile of the 24h range
speed=(c-c.shift(12))/atr                           # fast-down interaction = speed < -1.5
TARGET T3 = barriers(300,150) = P(+300p before -150p) over t+1..t+288 (ties -> adverse/0 ; nan if neither)
BASELINE = ~state ; DEV <= 2024-06-30 ; day-clustered z
P2_SPEC_REPRODUCIBLE = YES · P2_SPEC_HASH = e902c868037f9e36
```

## §2 Information reproduction — matches the Statistician's DEV/OOS to the digit
```
DEV: cond 0.1743 vs base 0.2270 · lift -0.0527 · z -1.87       (Statistician DEV lift -0.0527) ✓ exact
OOS: lift -0.0367                                              (Statistician OOS lift -0.0367) ✓ exact
INTERACTION (loc<0.1 & speed<-1.5) DEV: lift -0.0539           (Statistician DEV interaction -0.0539) ✓ exact
per-year same-sign: 5/6                                        (Statistician: 5/6 T3, 6/6 interaction) ✓
```
(The Statistician's headline z −3.12 / lift −0.0603 is the POOLED full-sample; the DEV/OOS split I reproduce exactly.)
`P2_INFORMATION_REPRODUCED = YES.` Raw effect direction: lower P(+300 before −150) at range-lows → downside continuation (directional/path).

## §3 GATE 1 — OVERLAP (the Statistician's unresolved caveat) — FAILS
The target is a 288-bar (24h) forward race, so the economically/statistically appropriate independence unit is **one observation per
non-overlapping 288-bar forward window** (equivalently, per distinct visit to the range-low). Consecutive `loc<0.1` bars share ~the same
forward window and are NOT independent.
```
A overlapping (day-clustered)        lift -0.0527  z -1.87   N=7310 bars, 245 days
B episode-first (maximal run)         lift -0.0381  z -3.21   N=1244   [INADEQUATE unit: runs <288 bars apart still overlap]
C one-per-day                         lift +0.0261  z +0.97   N=245    ← REVERSES, insignificant
E non-overlap >=288 bars apart        lift +0.0508  z +1.63   N=180    ← REVERSES (proper unit)
```
Under the two proper independence units (C one-per-day, E non-overlap-288) the effect **reverses to positive and loses significance**. The
negative "downside continuation" exists only under overlapping sampling — thousands of correlated bars near the 24h low counted as
independent. `P2_OVERLAP_ROBUST = NO → P2_OVERLAP_ARTIFACT.` Per §3, **STOP — no strategy is constructed.**

## §5 Gate 2 (trend/location confound) — measured but MOOT (overlap gate already fatal)
For completeness: within trailing-return (speed) strata the effect is NOT subsumed by momentum (N-weighted within-speed lift −0.0466 ≈
unconditional −0.0527). So P2 is not merely a recent-downtrend proxy — but this is irrelevant because the effect is an **overlap** artifact,
not a genuine per-event effect. `P2_INCREMENTAL_INFORMATION_AFTER_MATCHED_CONTROLS = NOT REACHED (overlap gate failed first).`

## §12 VERDICT
```
P2_ALPHA_REPLICATION_COMPLETE = YES
P2_SPEC_REPRODUCIBLE = YES
P2_INFORMATION_REPRODUCED = YES (DEV/OOS/interaction lifts match to the digit)
P2_OVERLAP_ROBUST = NO   →   P2_OVERLAP_ARTIFACT
PRIMARY_INFORMATION_TYPE = DIRECTION / PATH (raw), but overlap-artifact (not a genuine per-event effect)
P2_INCREMENTAL_INFORMATION_AFTER_MATCHED_CONTROLS = NOT REACHED (stopped at the decisive overlap gate; effect was not momentum-subsumed)
STRATEGY_INTERPRETATIONS_TESTED = 0
STRATEGY_INTERPRETATIONS_SURVIVED = 0
NEW_STRATEGY_CANDIDATE = none
READY_FOR_INDEPENDENT_VALIDATION = NO
```

## §13 PROTECTION
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES ·
STRATEGY_CATALOG_UNTOUCHED=YES · L1_UNTOUCHED=YES · V2-4_UNTOUCHED=YES · no promotion.

## Honest summary
P2 reproduces the Statistician's exact DEV/OOS lifts, confirming faithful replication — and then fails on the very gate the Statistician
flagged as unresolved. The bottom-of-24h-range "downside continuation" is an **overlap artifact**: it is negative only because price lingers
near the 24h low for many consecutive, forward-window-sharing bars; under one-per-day or non-overlapping-288-bar sampling the sign reverses.
All three Statistician scout leads replicated so far (L1 timing, V2-4 coiled, P2 range-low) are **real statistics that dissolve under the
proper control** — session composition (V2-4), event overlap (P2), or matched controls (L1). The independent-replication gate is doing
exactly its job: stopping confounded statistics from becoming false strategies. S5 remains the sole tradeable edge.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
