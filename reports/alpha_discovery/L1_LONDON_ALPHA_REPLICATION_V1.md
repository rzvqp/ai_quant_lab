# L1_LONDON_ALPHA_REPLICATION_V1 — independent Alpha replication of Statistician lead L1

Independent replication of the frozen Statistician lead **L1 — LONDON** (not a validation of Alpha's own M5 work; Family E deliberately not
used during discovery). Code: `sc_L1.py` (information), `sc_L1_strat.py` (minimal interpretations). Native M5 2021-07-27→2026-07-27.

## §1 Spec reproducibility
No written frozen L1 spec was available to me (only its stated properties), so I reconstructed the most faithful causal definition:
```
L1_SPEC = first native-M5 bar at/after the DST-correct London open (08:00 Europe/London), one event per trading day;
          phenomenon = forward path reaches +/-100 project pips FASTER than a matched non-London (Asia 02:00 UTC) baseline.
L1_SPEC_HASH = ac080c2c5bbd0697
AMBIGUITIES: (1) exact London window (open-bar vs a conditional London state); (2) baseline choice (Asia-open vs all-bars);
             (3) censoring horizon; (4) what "6/6 years directionally consistent" refers to given the effect is direction-symmetric.
L1_SPEC_REPRODUCIBLE = PARTIAL — the QUALITATIVE phenomenon reproduces; the exact magnitude (Statistician ~3.4h) does not under a generic
             London-open definition (I get 5.3h), indicating the frozen L1 is a MORE SPECIFIC London state than I can see without the spec.
```

## §2/§3 Information reproduction — what L1 actually predicts
```
                    N      reach100  med_t100   P(+100 first)   MFE    MAE
L1_LONDON          1288    0.992     5.3h       0.507           185p   157p
BASELINE_ASIA      1552    0.986     6.6h       0.517           182p   158p
```
- **London reaches +/-100p faster (5.3h vs 6.6h)** — the time-to-expansion effect reproduces in SIGN (Statistician ~3.4 vs 6.9h; my
  magnitude weaker → their L1 is a tighter London state).
- **P(+100 first) = 0.507 vs 0.517 ≈ 0.50** → **L1 is EXPANSION / TIMING information, NOT directional.** This is the decisive, robust
  property and it is unambiguous.
- Per-year: London faster in 2021-2024 (5.5-6.9h vs 6.5-11.5h) but the relative edge COMPRESSES in 2025-2026 (both ~0.6-2.0h — extreme
  vol makes +/-100p fast everywhere) → **6/6-year speedup NOT reproduced under my reconstruction (4/6)**; may be 6/6 under the exact spec.

```
PRIMARY_INFORMATION_TYPE = EXPANSION / TIMING   (direction-symmetric; NOT directional)
L1_INFORMATION_REPRODUCED = YES (type + sign)   L1_6_OF_6_YEARS_REPRODUCED = NO (my reconstruction; 4/6)
L1_TIME_TO_EXPANSION_EFFECT_REPRODUCED = YES    L1_NONOVERLAP_ROBUSTNESS_REPRODUCED = YES (events are 1/day = inherently non-overlapping)
```

## §4/§6/§9 Minimal strategy interpretations (≤3) — tested
Because direction at L1 is a coinflip (0.507), a directional L1 trade cannot work; the only plausible monetizable form is
conditional-response (L1 gate → a second event reveals direction → continuation). Structural exit; conservative same-bar; matched control.
```
A. L1 London-gated displacement-revealed CONTINUATION   net -0.043  DEV -0.057  OOS -0.031  (FALSIFIED)
   MATCHED CONTROL: same conditional-response at Asia    net +0.118  DEV +0.020  OOS +0.173  (drop-best-5% -0.032; top1%=22%)
   → L1_INCREMENTAL over control = -0.161  (London makes the response WORSE, not better)
B. L1 directional bias  LONG -0.106 / SHORT -0.185       (FALSIFIED; confirms non-directional)
C. L1 as non-directional timing filter                   (not a standalone trade; would only gate size/timing)
```
`STRATEGY_INTERPRETATIONS_TESTED = 3 · STRATEGY_INTERPRETATIONS_SURVIVED = 0.`
`L1_INCREMENTAL_TRADE_INFORMATION = NO` — the London gate adds no incremental tradeable information (it is worse than the same
conditional-response applied at a non-London time). S5_MECHANISM_CLONED = NO.

## §16 Comparison with Alpha (after freeze)
My blind conditional-response interpretation independently surfaced the **event-revealed-continuation expansion effect** (the Asia-control
+0.118 is that effect) — the same class of phenomenon as Alpha's M5 Family E. `ALPHA_PHENOMENON_INDEPENDENTLY_REDISCOVERED = YES`. But the
independent scan adds two important facts: (1) the effect is **session-agnostic** — London specifically adds nothing (indeed subtracts);
(2) it is **fragile** (drop-best-5% → −0.032), consistent with Family E's outlier dependence. So L1 corroborates that the real signal is
expansion/timing + event-revealed continuation, NOT a London-specific directional edge.

## §13 VERDICT
```
L1_LONDON_ALPHA_REPLICATION_COMPLETE = YES
L1_SPEC_REPRODUCIBLE = PARTIAL (qualitative; exact frozen spec unavailable to me)
L1_INFORMATION_REPRODUCED = YES (type: EXPANSION/TIMING, direction-symmetric)
PRIMARY_INFORMATION_TYPE = EXPANSION / TIMING
L1_6_OF_6_YEARS_REPRODUCED = NO (4/6 under my reconstruction; edge compresses in extreme-vol 2025-26)
L1_NONOVERLAP_ROBUSTNESS_REPRODUCED = YES
L1_TIME_TO_EXPANSION_EFFECT_REPRODUCED = YES (sign; magnitude weaker than 3.4h)
STRATEGY_INTERPRETATIONS_TESTED = 3
STRATEGY_INTERPRETATIONS_SURVIVED = 0
L1_INCREMENTAL_TRADE_INFORMATION = NO
NEW_STRATEGY_CANDIDATE = none
READY_FOR_INDEPENDENT_VALIDATION = NO
```

## §14 PROTECTION
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES ·
STRATEGY_CATALOG_UNTOUCHED=YES · P2_NOT_TOUCHED=YES.

## Honest summary
L1 is a **real expansion/timing phenomenon** (London reaches its move faster) but is **direction-symmetric**, so it is not a directional
edge, and gating a conditional-response continuation on London **subtracts** rather than adds versus a non-London control. L1 =
**INFORMATION_ONLY**, not Strategy #2. The genuine (session-agnostic, still fragile) signal is event-revealed continuation — which needs
broader validation, not a London wrapper. If the Statistician's exact L1 spec differs from my reconstruction, the decisive test to re-run
is the matched non-London control on THAT exact spec; direction-symmetry (P(+100 first)≈0.50) makes a directional L1 strategy implausible
regardless.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_INDEPENDENT_VALIDATION = NO
```
