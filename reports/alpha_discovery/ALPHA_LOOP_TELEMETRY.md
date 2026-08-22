# ALPHA_LOOP_TELEMETRY (§24)

Updated each loop cycle. Whenever CURRENT_FRONTIER closes, NEXT_FRONTIER becomes CURRENT immediately.

```
LOOP_STATUS               = ACTIVE
CURRENT_POPULATION        = historical _from_M15_v2 b0(2011-2013)+b1(2016-2018)  [DISCOVERY_CONSUMED, causal hist_data.py]
CURRENT_FRONTIER          = (cycle boundary) -> next = HF6
CURRENT_HYPOTHESIS        = -
TOTAL_FRONTIERS_TESTED    = 14  (F1-F7, F-EXT-S2, F-EXT-S4, HF1-HF5)
TOTAL_HYPOTHESES_TESTED   = 36  (H01-H36)
TOTAL_STRATEGY_CONFIGS    = ~230+ (RR/H/W/def/side variants as robustness checks, not separate hypotheses)
TOTAL_FROZEN_PENDING_VAL  = 1   (COMP-CONT-L-rr2 @ 4082c5c)   [+ H4-bo-raw-S in its own separate validation workflow]
DATA_REGIONS_CONSUMED     = 2021-2023 native DEV (exhausted); historical b0+b1 (this population); CALIB readouts. 2024+ PROTECTED untouched.
EXOGENOUS_FRONTIER        = CLOSED (requires CEO authorization)
NEXT_FRONTIER             = HF6 — D1 overnight/gap directional on b0/b1 (temporal-structural class, low prior). If dead: b0/b1 exhausted of new non-redundant robust alpha -> exogenous frontier (CEO-gated) is the next lever
```

## Key structural findings (bounded)
- 2021-2023 native: robust price-only edge = LONG trend-continuation only (COMP-CONT-L frozen). SHORT/range/reversion/temporal dead.
- Historical b0/b1: robust bearish edge = the frozen **H4-bo-raw-S downside-break event**; new bearish-short triggers (HF1 compression, HF3 pullback-EMA, HF4 transition-onset) are tail-carried near-misses OR **redundant** with H4-bo-raw-S (HF4 85% within 3d). Range mean-reversion dead even in a real range (HF2).
- **Implication:** bearish-short and range frontiers on b0/b1 are saturated/dead; remaining genuinely-different price-only options are counter-trend long-reversion and high-vol event alpha (both low prior given reversion's graveyard). If those fail, b0/b1 approaches exhaustion for NEW non-redundant robust alpha.

## Search-lineage summary (multiple-testing, §18)
- Prior program: 60+ hypotheses; froze S5 / H4-bo-raw-S / HR-TU-pb-L / MT-dispaccept-L / TR-rng2trend-L.
- This loop: 34 hypotheses / 13 frontiers -> 1 new independent survivor (COMP-CONT-L-rr2). External S2/S4 NOT_SUPPORTED. Historical b0/b1: no NEW independent robust survivor (HF4 robust-but-redundant).
- Any future survivor discloses this full ancestry + overlap vs all frozen candidates.
