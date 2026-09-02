# S14_RESCUE_FROZEN_SPEC_V1
## Frozen top-ranked ATTRIBUTION_V2 rescue hypothesis — bound verbatim from the final V2 artifacts, unchanged
### Bound by: Red Team · RT-S14-RESCUE-INDEPENDENT-RETEST-V1 · 2026-09-02

This file freezes the EXACT hypothesis that produced the V2 S14 result. No threshold movement, no
neighboring bin, no session adjustment, no parameter retuning, no strategy modification. Values are copied
from the frozen V2 artifacts and independently re-derived from the committed trade ledger.

### Identity
```
SOURCE_FAMILY_ID          = S14
ANALYSIS_OBJECT_ID        = S14::25e44853ad0f
REPRESENTATIVE_VARIANT_ID = 25e44853ad0f
DIRECTION                 = SHORT
SOURCE_TYPE / TIER        = S_LIBRARY_REPRESENTATIVE / T1_REGENERATE_SLIB
MECHANISM_ID              = M08_EXTENSION_MEAN_REVERSION
VARIANT_SPEC              = {"exit":"rr2","roc_k":0.004,"side":"down","stop":"atr"}  (GRAMMAR_FIRST_PER_SIDE=down, 16 variants)
```

### Original strategy definition (code/mstrat.py s14_setups + simulate; the exact generator V2 regenerated)
```
NAME    = S14 "Momentum Exhaustion (accel then stall -> reversal)"  -- mean-reversion SHORT
SIGNAL  (decision bar si=t, M15 native): roc = close/close.shift(3) - 1 ;
          accel = (roc > +0.004)  [an up-move]  AND  stall = |roc| decreasing vs previous bar ;
          event = first onset bar where (accel & stall) becomes true
ENTRY   = next bar open, o[si+1]                                    (engine never enters on the signal bar)
STOP    = entry + 1.5 * ATR(si)   [above entry, short]  => risk = 1.5*ATR
          executable floor: risk = max(risk, max(2*spread_ticks*TICK, 5*TICK, 0.10*ATR[si]))
TARGET  = entry - 2*risk          (RR2, short)
EXIT    = stop or target intrabar; else time-stop at 48 M15 bars, exit at close
NET_R   = (dir*(exit-entry) - 2*cost) / risk
COST    = BASE: (spread_ticks + slip_ticks)*TICK = (1.0 + 1.0)*0.1 = 0.20/side -> 0.40 price round-trip
          TICK = 0.1
```

### Frozen rescue condition (the ONE condition that produced the V2 result)
```
BLINDED_FEATURE_ID   = f028
UNBLINDED_MEANING    = dist_prev_sess_high_atr  = distance of price to the PREVIOUS-SESSION HIGH, in ATR units
BINNING              = numeric, 5 quantile bins (n_bins=5); feature stored as bin label 0..4
FROZEN_CONDITION     = f028 == 0.0   (the nearest-to-previous-session-high bin, i.e. distance ~ 0:
                       price at/through the previous-session high)
ELIGIBILITY          = ELIGIBLE_PRE_ENTRY (not f029, the only excluded feature)
```

### Discovery result (from the final V2 artifacts; INDEPENDENTLY re-derived from ATTRIBUTION_V2_TRADE_FEATURES.parquet — EXACT)
```
OBJECT_FULL_N              = 1239        OBJECT_POOLED_EXPECTANCY = -0.152388 R
RESCUE_SUBSET_N           = 65   (over 56 distinct UTC days)
RESCUE_SUBSET_EXPECTANCY  = +0.492592 R
REMAINDER_N               = 1174        REMAINDER_EXPECTANCY = -0.188098 R
EXPECTANCY_LIFT           = +0.680691 R  (subset - remainder)
OMNIBUS_P                 = 0.000510761   BH_THRESHOLD@rank = 0.002357488
DAY_CLUSTERED_Z           = +3.885422
FDR_STATUS                = fdr_sig = True   (BH-FDR q=0.05 at declared m=5175)
RESCUE_CLASS              = PROFITABLE_RESCUE  (requires chrono>=2/3 thirds positive AND drop-best-5% > 0)
CHRONO_THIRDS             = [+0.9032, -0.0695, +0.6513] -> 2/3 positive (PASS gate)
CONCENTRATION             = drop-best-5% (drop 4/65) = +0.3941 > 0 (PASS gate); drop-best-1 = +0.4691;
                            top-1% share of gross winners = 3.2%; WR 0.538; median R +0.4331; PF 2.083
CONVERGENT_SAME_OBJECT    = f026 rloc_50=0.0 -> +0.4364R (N43); f030 rloc_96=0.0 -> +0.3074R (N70);
                            f010 bars_since_20bar_high=4.0 -> +0.2211R (N123)
CROSS_FAMILY_RECURRENCE   = f028 does NOT clear the recurrence gate (3 families / 3 mechanisms; needs >=5 & >=3)
                            -> S14 is a FAMILY-SPECIFIC profitable sliver, NOT part of the recurrent time-of-day beta
```

### Provenance / exposure status (frozen, from STRATEGY_ATTRIBUTION_V2_PROTOCOL_FREEZE.md)
```
ATTRIBUTION_DISCOVERY_RANGE   = 2011-07-26 .. 2026-07-27 (the entire governed XAU M15 record)
S14_LEDGER_DECISION_RANGE     = 2011-08-02 19:45 UTC .. 2026-07-26 22:15 UTC
RESEARCH_HOLDOUT_CUTOFF_UTC   = 2025-10-23 -- HAS BEEN CONSUMED
HISTORICAL_REUSE_STATUS       = MATERIALLY_EXPOSED -- no clean OOS exists; V2 output is HYPOTHESIS_GENERATION ONLY
GOVERNED_DATA (canonical, sha 57f4ed95) = XAUUSD M15 2011-07-26 16:30 .. 2026-07-27 16:15 UTC (355,696 bars);
                                          native M5 2021-07-27 .. 2026-07-27 17:55 UTC
COST_CONVENTION               = BASE = 0.40 price round-trip (spread 1 + slip 1 tick, TICK 0.1; used in discovery);
                                STRESS = x3 spread+slip (alpha_lab.red_team()); V2 rescue used BASE only
```

*This specification is FROZEN. Any change (adjacent bin, session tweak, different stop/target/RR/direction,
new interaction) voids S14_RESCUE_FROZEN_SPEC_V1 and is a NEW hypothesis. Bound and hashed before any
retest decision.*
