# ORDER_BLOCK_RETEST_FACTORY_V1_REPORT — final

One bounded cycle: data audit → causal OB atlas → 20 raw hypotheses → dedup 6 → baseline tests → matched controls → falsification →
M5 execution. **SURVIVED = 1** (first positive discovery of the campaign). Governed OANDA XAUUSD (M15 full + native M5 2021+). S5/Q4/P007/
MGMT-004/holdout untouched; no M5 synthesis; **no promotion, no Statistician/Red Team handoff** (per §32 — CEO decides). Code: `ob_core/
atlas/contrast/candidate/falsify/m5.py`. Docs: atlas, contrast report, hypothesis register, `ALPHA_CANDIDATE_OBR-BULL-1.md`, this report.

## §28 CEO questions — answered
1. **Does a causal OB + displacement + BOS + first retest create positive expectancy?** **YES, conditionally.** The raw OB first-retest is
   ~break-even, but gated on **displacement ≥1.5 ATR** (a monotone dose-response) and **London/NY** it reaches **+0.15R** (bull), cross-era.
2. **Does the ORDER BLOCK add information beyond an ordinary pullback?** **YES.** The OB level beats a matched generic displacement+BOS
   pullback by +0.14–0.36R and a height-matched shifted level by +0.21R — in every era. `OB_INCREMENTAL_INFORMATION_FOUND = YES`.
3. **Does M5 improve execution?** **YES (native 2021+ only)** — stop-tightening to the M5 swing-low lifts +0.23→+0.93R; needs Statistician
   scrutiny on tight-stop R-accounting; not verifiable pre-2021.

## §30 SCOREBOARD
```
ORDER_BLOCK_RETEST_FACTORY_V1_COMPLETE = YES
DATA_AUDIT_PASS = YES

RAW_HYPOTHESES = 20 · DEDUPED_HYPOTHESES = 6 · TESTED = 6 · FALSIFIED = 4 (weak/hindsight/HTF) · SURVIVED = 1

TOTAL_CAUSAL_ORDER_BLOCKS = 17,432 (disp>=0.75) · FIRST_RETEST_EVENTS = 13,137
BULLISH_EVENTS = 6,796 · BEARISH_EVENTS = 6,341 · FRESH_FIRST_RETEST_EVENTS = 13,137 (fresh by construction)

OB_INCREMENTAL_INFORMATION_FOUND = YES
TARGET_SPACE_INFORMATION_FOUND = WEAK
FIRST_RETEST_INFORMATION_FOUND = YES
DISPLACEMENT_INFORMATION_FOUND = YES (monotone dose-response)
BOS_QUALITY_INFORMATION_FOUND = PARTIAL (close-BOS used; wick-only not separately monetized)
HTF_INCREMENTAL_INFORMATION_FOUND = NO
SESSION_SPECIALIZATION_FOUND = YES (LN+NY; NY strongest)

M5_REFINEMENT_RUN = YES · M5_EXECUTION_VALUE_FOUND = YES (native 2021+; VALUE_ADD, caveated)

NEW_STRATEGY_CANDIDATES = 1 (OBR-BULL-1; OBR-BEAR-1 secondary/weaker)
```

### Surviving candidate — OBR-BULL-1 (full spec in ALPHA_CANDIDATE_OBR-BULL-1.md)
```
CANDIDATE_ID = OBR-BULL-1 · DIRECTION = LONG · TIMEFRAMES = M15 setup (H1/H4 not used) · SESSION = London+NY (08:00–20:00 UTC)
DEF = last-bearish-candle OB before a bullish close-BOS of the causal 20-bar swing high, displacement>=1.5 ATR; resting limit BUY at
      block_high on fresh first retest; stop below block_low (floored); target 2R.
N = 2122 · IND_H_EPISODES ~954 · WR = 0.482 · NET_R = +0.154 · PF = 1.86 · median trade R ~ -1..+2 (2R:1R)
MFE(med) = 37 pips · MAE(structural) · TARGET_SPACE = open (price-discovery favourable)
ERA: D +0.123 / C +0.166 / O +0.206 · DEV +0.123 / OOS +0.185 · years positive 13/16
MATCHED_CONTROL: beats CONTROL_C +0.36, CONTROL_SHIFT +0.21, BETA +0.33 (cross-era)
OUTLIER: drop-best-1% +0.135 (robust) · COST: survives price-cost & flat-0.24; thin under harsh +0.15R
ANTI_LOOKAHEAD_AUDIT: ALL PASS (§27) · M5: VALUE_ADD (native 2021+)
```

## §32 PROMOTION GATE
SURVIVED = 1 → **READY_FOR_STATISTICIAN_REVIEW = YES.** No Statistician handoff, no Red Team handoff, no StrategyCatalog promotion
performed. Strongest candidate identified first: **OBR-BULL-1** (bull > bear). CEO decides whether to route to independent validation.

## §33 PROTECTION
```
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES
EXECUTION_UNTOUCHED=YES · NO_M5_SYNTHESIS=YES · NO_LIVE_PROMOTION=YES
```

## Significance & honest framing
This is the **first candidate to survive internal discovery+falsification in the entire multi-frontier campaign** — the first thing that
is net-positive after cost, positive in the pre-2019 era (escaping the R20 era-trend trap that killed every prior lead), mechanism-backed
(displacement dose-response), outlier-robust, and demonstrably better than matched non-OB controls. It is **modest** (+0.15R) and carries
real caveats (cost-thin under harsh stress; control/stop disentanglement; M5 value only measurable post-2021; bear weaker). It is exactly
the kind of result that warrants **independent Statistician + Red Team validation** — which is the CEO's call, not mine.

The broader lesson: prior frontiers searched *direction* (efficient) and *HTF selection* (inherits efficiency). This family found edge in
**level identity + impulse quality** — the order block marks a specific price level, and the strength of the displacement away from it
predicts the quality of its first-retest continuation. That is a structural/level mechanism, not a directional-prediction one.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_STATISTICIAN_REVIEW = YES (OBR-BULL-1) — awaiting CEO authorization to route
```
