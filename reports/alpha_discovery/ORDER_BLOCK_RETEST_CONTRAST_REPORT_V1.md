# ORDER_BLOCK_RETEST_CONTRAST_REPORT_V1 — does the ORDER BLOCK add information? (§21/§26)

The central scientific test of the mandate. A positive OB result is not enough; we must show the **order-block identity** adds information
beyond ordinary pullbacks / displacement+BOS alone / trend beta. Tradeable model = resting limit at the block edge, 2R, price-cost.
Code: `ob_contrast.py`, `ob_candidate.py`.

## 1. Matched-control ladder (§21) — full population, both directions
```
                         net-R      D        C        O
BULL  OB_RETEST         -0.006    -0.061   -0.025   +0.122
      CONTROL_C(genPB)  -0.142    -0.228   -0.139   +0.023      (generic displacement+BOS pullback, non-OB)
      CONTROL_SHIFT     -0.216    -0.326   -0.190   -0.029      (block shifted by its own height = non-OB level, matched distance)
      CONTROL_BETA      -0.332    -0.390   -0.352   -0.254      (random longs, matched era)
BEAR  OB_RETEST         +0.020    +0.010   -0.036   +0.109
      CONTROL_C         -0.141 ...   CONTROL_SHIFT -0.201 ...   CONTROL_BETA -0.353
```
**Ordering `OB > CONTROL_C > CONTROL_SHIFT > CONTROL_BETA` holds in BOTH directions and in EVERY era.** The OB level beats a generic
pullback by ~+0.14R, a height-matched shifted level by ~+0.21R, and beta by ~+0.33R.

## 2. §26 PRIMARY INFORMATION TEST — answer
**OB_INCREMENTAL_INFORMATION_FOUND = YES.** Entering at the causal order-block level is consistently, cross-era, better than matched
non-OB pullback levels with the same displacement+BOS precondition. The effect is present pre-2019 (D era), ruling out an R20 artifact.

## 3. Where the information becomes monetizable
The OB retest alone is ~break-even; the OB's incremental value **grows with the target** (the block marks a level continuation runs
*further* from): in-cell vs CONTROL_C the OB advantage is ~0 at 1R but **+0.24 to +0.52 at 2R–3R**. Gating on **displacement ≥1.5 ATR**
(a monotone dose-response, not a threshold pick) and **London/NY** sessions lifts the OB retest into positive net-R:
```
BULL  disp>=1.5 LN+NY 2R:  net +0.154  PF 1.86  D+0.123/C+0.166/O+0.206  vsCONTROL_C +0.36  (N 2122, ie 954)
BEAR  disp>=1.5 LN+NY 2R:  net +0.127  PF 1.77  D+0.111/C+0.063/O+0.246  vsCONTROL_C +0.35  (N 1954, ie 940)
```

## 4. Secondary-question answers (§2, §30)
```
OB_INCREMENTAL_INFORMATION_FOUND = YES   (OB level beats matched non-OB pullbacks cross-era)
FIRST_RETEST_INFORMATION_FOUND   = YES   (fresh first retest of the frozen block is the tradeable event)
DISPLACEMENT_INFORMATION_FOUND   = YES   (monotone dose-response 1.0→2.5 ATR; strongest single lever)
TARGET_SPACE_INFORMATION_FOUND   = WEAK  (room>=3 mildly positive; not decisive vs displacement/session)
BOS_QUALITY_INFORMATION_FOUND    = PARTIAL (close-acceptance BOS used throughout; wick-only not separately monetized)
HTF_INCREMENTAL_INFORMATION_FOUND= NO    (H4 align/neutral/counter ≈ equal on top of displacement+session)
SESSION_SPECIALIZATION_FOUND     = YES   (LN+NY >> Asia/late; NY strongest)
FRESHNESS(mitigation)            = primary population is fresh-first-retest; later retests not monetized (secondary diagnostic)
```

## 5. Caveats for independent validation (§26 honesty)
- The OB-vs-CONTROL_C gap partly reflects **stop placement** (structural stop below the block vs fixed 1-ATR); CONTROL_SHIFT (height-
  matched, structural-ish stop) is the cleaner control and OB still beats it by +0.21. A **fully stop-matched** control is recommended for
  the Statistician to isolate OB-level information from structural-stop benefit.
- The displacement dose-response is **independent of the control question** and is the strongest mechanism evidence: stronger impulse from
  the origin block ⇒ higher-quality level ⇒ better first-retest continuation.
