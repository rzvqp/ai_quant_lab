# M5_EVENT_REVEALED_CONTRAST_REPORT_V1 — does the COMPLETE sequence add information? (§19)

The §19 test: does the full sequential event beat simply chasing the first directional move? Focus on family E (the info-bearing one).
Code: `m5_E.py`, `m5_regime.py`.

## 1. Sequence vs "chase the first move" control
```
E.LONG.2R                                        net -0.044
CONTROL (fade first impulse, no reject/accept)   net -1.318      →  E beats control by +1.27R
```
The control (enter opposite immediately after the impulse, skipping the rejection + opposite-acceptance states) loses −1.3R; the full
state machine recovers +1.3R of that. Holds in every year (2021 E −0.30 vs ctrl −2.19 … 2025 E +0.15 vs ctrl −0.76). **The rejection +
acceptance confirmation is where the information lives.**

## 2. Sequence vs directional beta, within a causal uptrend regime (§23 — one transparent regime test)
Prospectively-observable regime = causal `close > EMA200`. Exit = time.
```
E.LONG.UPTREND        net +0.117   DEV -0.013   OOS +0.298   (2023..2026 all ≥0)
BETA.LONG.UPTREND     net -0.081   DEV -0.149   OOS +0.006   (unconditional longs in uptrend, matched stops)
→ E beats beta +0.198 overall; +0.136 in DEV; +0.292 in OOS  (beats beta in BOTH periods)
```

## 3. §19 answer
**SEQUENTIAL_EVENT_INCREMENTAL_INFORMATION_FOUND = YES.** The complete impulse→rejection→opposite-acceptance sequence carries strong,
cross-period information: it beats both "chase the first move" (+1.3R) and directional beta (+0.14 DEV / +0.29 OOS). This is the strongest
incremental-information finding of the entire Alpha campaign and validates the conditional-response / sequential-state paradigm.

## 4. Why the information does not become a survivor
Despite the strong information, E.LONG.UPTREND fails the tradeable-survival bar (§29) on two independent grounds:
- **DEV net not positive** (−0.013): positive only in the recent regime (OOS +0.298, years 2023-2026).
- **Outlier dependence**: top 1% of trades = **80%** of net PnL; drop-best-5% → **−0.228**. The positive expectancy is carried by a handful
  of large trend-day runs, not a robust edge (§27).
Anti-hindsight audit PASSES; the failure is robustness, not causality. **Information confirmed; robust monetization not achieved in the
2021+ M5 history.** A pre-2021 native-M5 dataset (to test across a bear regime) is the single most decisive follow-up.
