# M5_EVENT_REVEALED_DIRECTION_FACTORY_V1_REPORT — final

First native-M5 conditional-response cycle (audit #1). Direction is EVENT-REVEALED via causal state machines, never forecast. **SURVIVED 0**
— but the strongest incremental-information result of the campaign. Native M5 only; conservative same-bar; not an S5 clone. Code:
`m5_core.py`, `m5_families.py`, `m5_scan.py`, `m5_E.py`, `m5_regime.py`.

## §3 data audit — M5_DATA_AUDIT_PASS = YES
```
M5_START = 2021-07-27 15:45 UTC · M5_END = 2026-07-27 17:55 UTC · M5_BARS = 354,669 · median ATR 15 pips
M5_NATIVE_HISTORY_LIMITED = YES (5 years, one broad regime = post-2021; no 2011-2018 bear). DEV=2021-07..2024-06 / OOS=2024-07..2026-07.
```

## §31 SCOREBOARD
```
M5_EVENT_REVEALED_DIRECTION_FACTORY_V1_COMPLETE = YES · M5_DATA_AUDIT_PASS = YES

RAW_HYPOTHESES = 20 · DEDUPED_HYPOTHESES = 5 · TESTED = 5 · FALSIFIED = 5 · SURVIVED = 0

DISPLACEMENT_ACCEPTANCE_TESTED = YES · SWEEP_RECLAIM_TESTED = YES · FAILED_ACCEPTANCE_TESTED = YES
COMPRESSION_SECOND_LEG_TESTED = YES · IMPULSE_REVERSAL_TESTED = YES · VOLATILITY_TRANSITION_TESTED = YES (via compression→expansion)

SEQUENTIAL_EVENT_INCREMENTAL_INFORMATION_FOUND = YES
FIXED_R_ONLY = NO (tested 2R / struct-3R / trailing / time) · M5_NATIVE_DISCOVERY = YES · S5_MECHANISM_CLONED = NO

NEW_STRATEGY_CANDIDATES = 0 · READY_FOR_STATISTICIAN_REVIEW = NO · M5_NATIVE_HISTORY_LIMITED = YES
```

## Results (2R baseline, native M5, price cost)
| family | N | net-R | note |
|---|---|---|---|
| A displacement→acceptance→continuation | 19,902 | **−1.72** | 11-pip stops → cost 0.38R/trade dominates; whipsaw |
| B sweep→reclaim→continuation | 20,259 | −0.41 | negative both dirs/periods |
| C break→failed-acceptance→opposite | 14,721 | −0.31 | negative |
| D compression→expansion→second-leg | 1,263 | **−2.22** | 7-pip stops → cost catastrophic |
| E impulse→rejection→opposite-acceptance | 3,636 | −0.12 | wide 44-pip structural stops; high large-move reach; see below |

A and D fail primarily because their tight stops (7-11 pips) make the fixed price cost 0.38-0.6R per trade — a real frictional death, not
a false negative. B/C are cleanly negative.

## ★ The genuine finding — family E carries strong sequential-event information (§19)
E (impulse d1 → rejection through the impulse origin → opposite-acceptance d2 → enter next open) has wide structural stops (44 pips, cost
only 0.10R) and the highest large-move reach (P(+100 pips)=22%, P200=8%, P300=4.3%). Its information content is decisive:
```
E.LONG.2R  net -0.044   vs   CONTROL (fade first impulse, no reject/accept)  net -1.318   →  E beats control by +1.27R (every year)
E.LONG.UPTREND (causal close>EMA200, time exit)  net +0.117   vs   matched LONG-BETA in uptrend  net -0.081   →  E beats beta +0.198
   and beats beta in BOTH periods: DEV +0.136 (E -0.013 vs beta -0.149) · OOS +0.292 (E +0.298 vs beta +0.006)
```
**`SEQUENTIAL_EVENT_INCREMENTAL_INFORMATION_FOUND = YES` — the strongest incremental result of the whole campaign.** The complete
state-machine sequence adds ~+1.3R over chasing the raw impulse and beats directional beta in both DEV and OOS. This confirms the
architecture-audit thesis: conditional-response / sequential-state / M5-native search finds far more information than directional
prediction did.

## Why E still does NOT survive (honest, held to the bar after the OBR false-positive)
E.LONG.UPTREND is the campaign's best near-miss but fails the §29 survival gate on **two** independent grounds:
1. **DEV not positive:** DEV net = −0.013 (break-even), positive only in OOS (+0.298) and years 2023-2026. The edge is concentrated in the
   recent regime; the strict gate requires DEV positive.
2. **Outlier dependence (decisive):** top 1% of trades = **80%** of total PnL; drop-best-1% → +0.016; **drop-best-5% → −0.228**. Beyond
   legitimate positive skew — the expectancy is a lottery of a handful of large trend-day runs, not a robust edge (§27).
Anti-hindsight audit PASSES (causal impulse, direction revealed by the rejection close, next-open entry, structural stop, conservative
same-bar, pure M5, no HTF aggregation) — E fails on **robustness**, not causality. Therefore **SURVIVED = 0; NOT promoted; NOT handed off.**

## §33 PROTECTION
```
S5_UNTOUCHED=YES · Q4_UNTOUCHED=YES · AI_TRADER_UNTOUCHED=YES · P007_UNTOUCHED=YES · MGMT004_UNTOUCHED=YES · MT5_UNTOUCHED=YES
STRATEGY_CATALOG_UNTOUCHED=YES · NO_LIVE_PROMOTION=YES
```

## §30/§34 close + interpretation
SURVIVED = 0 → cycle closed; NKB updated. The paradigm shift was **correct and productive**: conditional-response M5 search surfaced the
strongest information signal of the campaign (E beats controls decisively) — but within the 5-year native-M5 history that information does
not convert into a robust, non-outlier-dependent, DEV-positive tradeable edge. Two honest paths remain:
1. **Broader native M5 history** (pre-2021) would let E.LONG.UPTREND be tested across a bear regime — the single most decisive follow-up.
   Its DEV weakness is exactly the 2021-2022 thin/choppy start; a real cross-regime test needs earlier M5. **Requires data acquisition.**
2. **Refine the E state machine** (the reject/acceptance thresholds are unmined defaults) in a *bounded* follow-up, held to the same
   outlier/DEV bar — but the outlier dependence (80% PnL in top 1%) is a structural warning that this may be a skew mirage.

Do not re-open BOS/OB/session-breakout/static-M15 searches (§30). The next genuinely-distinct move is either broader-history validation of
the confirmed E information, or the standing exogenous real-yields cycle.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
READY_FOR_STATISTICIAN_REVIEW = NO
```
