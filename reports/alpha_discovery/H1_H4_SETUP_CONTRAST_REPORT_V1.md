# H1_H4_SETUP_CONTRAST_REPORT_V1 — does HTF context selection add tradeable information?

§17/§28 deliverable. For every H1 setup we compare WITH the H4-context/location filter (HTF_ON) vs WITHOUT (HTF_OFF), and split every
survivor by direction × era, to isolate whether value comes from **HTF selection** or is merely direction×era (the known R20 era-trend
artifact). Net-R uses the principled per-trade price cost (0.419/risk); flat-0.24R reported as a conservative check. STRESS methodology.

## 1. HTF-ON vs HTF-OFF (the core §17 test)
| family | HTF_ON net-R | HTF_OFF net-R | Δ from H4 filter |
|---|---|---|---|
| PBK_TREND | −0.084 | −0.102 | +0.018 (negligible) |
| RECLAIM | −0.100 | −0.123 | +0.023 (negligible) |
| RANGE_FADE | −0.146 | −0.149 | +0.003 (none) |
| TGT_BREAK | −0.023 | −0.008 | **−0.015 (filter HURTS)** |

The H4-context filter never moves net-R by more than ~0.02R, and for the best family (TGT_BREAK) it is actively harmful. **HTF context
selection does not add tradeable directional information** the raw H1 setup did not already contain.

## 2. Direction × era decomposition (where does any positive cell come from?)
```
PBK_TREND  LONG   D +0.033  C +0.017  O −0.336     SHORT  D −0.029  C −0.501  O +0.166   (sign-reverses)
RECLAIM    LONG   D −0.069  C −0.110  O +0.014     SHORT  D −0.122  C −0.209  O −0.126   (all-neg but O-LONG≈0)
RANGE_FADE LONG   D −0.121  C −0.015  O −0.231     SHORT  D −0.128  C −0.126  O −0.311   (all negative)
TGT_BREAK  LONG   D −0.179  C +0.004  O +0.349     SHORT  D −0.071  C −0.063  O +0.023   (LONG positive only in O)
```
**Every positive cell is direction-aligned with the prevailing era trend** (long in the 2023-26 bull O, short in the 2011-18 bear D) and
**sign-reverses across eras**. No family has a single cross-era-sign-stable positive cell. This is the R20 signature: directional price
information = era-trend, non-generalizing.

## 3. The one candidate-shaped result — TGT_BREAK LONG O-era — and its falsification
LONG O-era: net-R **+0.349**, WR 0.596, N=47 (NY-session +0.290, WR 0.575, N=40). Against a **matched bull-beta control** (random longs,
same era, matched structural-stop distribution, same horizon): control O-LONG = +0.087. So TGT_BREAK beats beta by ~+0.26 **within O** —
but the excess-over-beta is itself era-unstable (O +0.26, C +0.05, **D −0.10**), and the raw cell sign-reverses (O +0.349 vs **D −0.179**).
An edge that exists only in the parabolic-bull era and reverses in the bear era is **regime beta with a momentum-persistence overlay, not a
cross-era structural edge**. FAILS §20 (era-split sign-reversal) and §24.7 (chronological stability). Not promoted.

## 4. M5 execution comparison (§22/§28.2) — measurement, not a rescue
No family produced a cross-era-stable baseline survivor, so per §12 none qualified for M5 optimization. We still measured M5 vs baseline on
TGT_BREAK signals in the native-M5 window (2021-07-27+, N=158): a causal M5-pullback entry (wait ≤6 M5 bars for a 0.33×risk pullback,
tighter M5 stop, same structural target):
```
BASELINE (M15 close entry, M5-resolved)  N=158  net-R +0.116  WR 0.475
M5-REFINED (pullback entry)              N= 20  missed_rate 0.87  WR 0.35   (net-R inflated by tight-stop denominator)
```
**M5_VALUE = HARMFUL/NEUTRAL for this thesis:** the pullback entry misses **87%** of signals — structurally counterproductive for a
breakout-continuation idea (waiting for a pullback that usually never arrives means you miss the very breakout you wanted). The +49-pip
median "entry improvement" is illusory because 87% never fill. M5 did not demonstrate incremental value.

## 5. §28 answers
1. **Does H4/H1 selection produce tradeable info M15-centric research did not?** **NO.** HTF_ON ≈ HTF_OFF (Δ<0.02R, sometimes worse); the
   only positive cells are era-trend, present with or without HTF selection, and sign-reverse across eras.
2. **Does M5 improve execution or add noise?** **Adds noise / no clean value** — the pullback method misses 87% of breakout signals and
   distorts risk; no evidence it improves execution without abandoning the thesis.
3. **Are surviving opportunities large enough to justify complexity?** **NO** — the only positive cell is bull-era beta; ~50-pip MFE moves
   are meaningful in size, but with no cross-era-stable entry edge the operational complexity is not justified.
