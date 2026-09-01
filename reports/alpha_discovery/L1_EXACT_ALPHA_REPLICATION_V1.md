# L1_EXACT_ALPHA_REPLICATION_V1 — exact replication of the FROZEN Statistician L1 (corrected)

Correction: my earlier `L1_LONDON_ALPHA_REPLICATION_V1` tested the WRONG statistic (London-open / time-to-±100p). This replicates the
EXACT frozen `STAT_L1_LONDON_FROZEN_SPEC_V1` (SPEC_HASH b2bc79c6…, DATASET cbb6eebe…). Code: `sc_L1_exact.py`. Native governed M5.

## §1 Spec + provenance
```
L1 = every M5 bar with UTC hour ∈ {8,9,10,11,12} (sess=="LN"), NO DST, no other filter — 77,393 bars (21.8%)
BASELINE = complement (AS∪NY∪LT). TARGET T1 = P(+100p before -80p) over t+1..t+288, ties→adverse(0), unresolved→excluded.
L1_EXACT_SPEC_READ = YES · declared SPEC_HASH in file = b2bc79c6… (== expected) · DATASET sha256 = cbb6eebe… VERIFIED == expected
L1_SPEC_HASH_MATCH = YES (definition read verbatim; dataset provenance hash matches exactly)
```

## §2 Headline reproduced — to the digit
```
BASELINE_P_UP100_BEFORE_DN80 = 0.4663 · L1_P_UP100_BEFORE_DN80 = 0.4286 · LIFT = -0.0377 · Z = -3.59   (Statistician: 0.4663→0.4286, z -3.59) ✓
DEV lift -0.0344 z -2.22 · OOS lift -0.0418 z -3.16
L1_HEADLINE_REPRODUCED = YES
```

## §3 Robustness attribution
T1(100/80) full lift −0.0377 z −3.59, **6/6 years same sign** (the headline). T2(200/100) −0.0267 z −2.32, 6/6. T3(300/150) −0.0219
z −1.57, 6/6. T1 is the strongest and is the 6/6 / Bonferroni-relevant statistic.

## §4/§5 What it changes — GENUINE DOWNSIDE PATH ASYMMETRY (not barrier geometry)
`PRIMARY_INFORMATION_TYPE = DIRECTION / PATH (downside asymmetry).` The pre-declared mirrored races (L1 lift, up-first prob):
```
P(+80 b -80)  base .5199 L1 .4864 lift -0.0335 z -3.29     P(+100 b -100) base .5266 L1 .4928 lift -0.0338 z -3.03
P(+100 b -80) base .4663 L1 .4286 lift -0.0377 z -3.59     P(+80 b -100)  base .5789 L1 .5503 lift -0.0286 z -2.69
P(+150 b -100) lift -0.0323 z -2.76                        P(+200 b -100) lift -0.0267 z -2.32
```
The **symmetric** races (+80/−80, +100/−100) are also strongly negative — so it is a genuine downward path bias during these hours, NOT an
artifact of the +100/−80 geometry. `GENUINE_DOWNSIDE_PATH_ASYMMETRY = YES.`

## §6 Time-of-day structure — a smooth diurnal cycle, not a London "state"
Hour-by-hour T1 lift is a smooth diurnal wave: **morning-UTC leans down-first** (03h −0.020 z−4.9 … 08h −0.028 z−6.8 … 12h −0.044 z−10.8 …
13h −0.035 z−8.5), **evening-UTC leans up-first** (17-21h +0.014…+0.081, z up to +11). The {8–12} window is simply the deepest slice of a
continuous intraday seasonality; 13h (outside L1) is as strong, and 02–07h are also negative. L1 is a *time window over a seasonal pattern*,
not a special market state.

## §7 Dependence robustness — FAILS (the decisive gate)
77,393 L1 bars but only ~1,289 days; bars within the daily 5-hour window share overlapping 288-bar forward races. Proper independence units:
```
A day-clustered (headline)   lift -0.0377  z -3.59  N=73,796
B one-per-day (first L1 bar)  lift -0.0195  z -1.40  N=1,289   ← sub-significant
C non-overlap ≥288 apart      lift -0.0270  z -1.77  N=1,063   ← sub-significant (|z|<1.96)
```
The sign is stable (unlike P2, it does NOT reverse) but significance is lost on independent observations: the z −3.59 is inflated by
within-day overlap. `L1_DEPENDENCE_ROBUST = NO` (real but sub-significant per independent day).

## §8 Price-state control — not a momentum confound
Within recent-return (12-bar/ATR) strata the N-weighted L1 lift = −0.0377 = the unconditional −0.0377. The window effect is NOT explained by
recent return/trend. `L1_INCREMENTAL_INFORMATION_AFTER_PRICE_STATE_CONTROL = YES` (but moot for a strategy — see gate).

## §9 Natural path shape (descriptive)
Mild downside asymmetry: down barriers touched ~2–4% more often than up across all mirrored races; economically small. Not a large-move or
tail effect (T3 z only −1.57). No RR was imposed.

## §10 Strategy-formation gate — NOT passed
Requires headline YES AND dependence-robust YES AND price-state-incremental YES. **Dependence-robust = NO**, so per the mandate's own gate
**no strategy interpretation is constructed.** `STRATEGY_INTERPRETATIONS_TESTED = 0.` (The implied morning-UTC short bias — P(down-80 first)
≈0.571 vs 0.534 — is directionally real but sub-significant on independent days and economically thin given the 80:100 geometry and cost.)

## §15 VERDICT
```
L1_EXACT_ALPHA_REPLICATION_COMPLETE = YES
L1_EXACT_SPEC_READ = YES · L1_SPEC_HASH_MATCH = YES
L1_HEADLINE_REPRODUCED = YES (0.4663→0.4286, z -3.59, exact)
PRIMARY_INFORMATION_TYPE = DIRECTION / PATH (downside asymmetry; a diurnal time-of-day seasonality)
L1_DEPENDENCE_ROBUST = NO (one-per-day z -1.40 / non-overlap z -1.77; sign stable, sub-significant)
L1_INCREMENTAL_INFORMATION_AFTER_PRICE_STATE_CONTROL = YES (not a momentum confound)
GENUINE_DOWNSIDE_PATH_ASYMMETRY = YES (symmetric races confirm)
STRATEGY_INTERPRETATIONS_TESTED = 0 · STRATEGY_INTERPRETATIONS_SURVIVED = 0
L1_INCREMENTAL_TRADE_INFORMATION = NO
NEW_STRATEGY_CANDIDATE = none
READY_FOR_INDEPENDENT_VALIDATION = NO
```

## §14 PROTECTION
P2_UNTOUCHED=YES · V2-4_UNTOUCHED=YES · S5_UNTOUCHED=YES · FAMILY_E_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES ·
P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES · STRATEGY_CATALOG_UNTOUCHED=YES · event-scout not read · no promotion.

## Honest summary
The exact frozen L1 is the most *genuine* of the three scout leads: a real, momentum-independent **downside path asymmetry** confirmed on
symmetric barriers and reproduced to the digit (z −3.59, 6/6 years). But it is a **diurnal time-of-day seasonality** (morning-UTC down-first,
evening-UTC up-first), not a special "London" state, and it **fails dependence robustness** — on ~1,289 independent days the effect falls to
z ≈ −1.4/−1.8 (sub-significant) and is economically marginal. It is INFORMATION (a real intraday path bias) but not a robust tradeable
edge. Corrects my earlier replication, which tested the wrong statistic. S5 remains the sole tradeable edge.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
