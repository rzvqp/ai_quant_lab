# ALPHA_M15_PATH_BASELINES

Mandate `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001`, Stage 1. Unconditional M15-decision forward-path base rates (§5), the baseline for M15 state lift. Engine `state_path_m15.py` (causal first-passage P(+X before -Y), multi-horizon). Populations: 2021-2023 gated M15 (swing_base, DEV) + historical b0/b1 M15 (hist_m15_data, governance-proven slice, 2024+ excluded). Labels are RESEARCH labels, NOT strategy TP/SL.

## P(+X/-Y) by horizon (L/S)
### 2021-2023 gated M15 DEV (N=40,649)
| horizon | +30/-30 | +50/-40 | +70/-50 | +100/-70 | +150/-75 |
|---|---|---|---|---|---|
| 2h | L.31/S.30 | .15/.15 | .08/.09 | .04/.04 | .01/.01 |
| 4h | .42/.40 | .26/.25 | .16/.16 | .08/.09 | .04/.03 |
| 8h | .49/.47 | .38/.35 | .28/.27 | **.17/.17** | .08/.08 |
MFE med 46p (P75 84 / P90 140); MAE med 44p (P75 84 / P90 139); adverse>=70p frac ~0.32.
### b0 2011-2013 M15 (N=52,404) — higher vol
8h: +100/-70 L.20/S.23; MFE med 49p; MAE med 52p; adverse>=70p ~0.39.
### b1 2016-2018 M15 (N=52,851) — LOWER vol
8h: +100/-70 L.08/S.08; MFE med 32p; MAE med 31p; adverse>=70p ~0.19.

## Observations (foundation for state discovery)
- **M15 LONG/SHORT base rates are near-SYMMETRIC** (unlike H1 2021-2023's long-bias) -> a genuine SHORT edge is as reachable as LONG here.
- **Natural excursion scale MFE/MAE med ~44-52p (2021-23/b0), ~31p (b1)** -> M15 structural stop is ~50-70p, NOT tight 20-50p (§19 honored); the +70/-50 and +100/-70 labels are the economically meaningful ones.
- **Base rates are strongly era-dependent** (b1 much quieter) -> same-regime-conditional baselines are required (compare states to same-parent-regime base, §10-11), not global M15 base.
- **Discovery target:** causal M15 state (or M15 transition, priority §8) that MATERIALLY lifts P(+70/-50) or P(+100/-70) over the same-parent-regime base AND recurs across same-regime occurrences; event-dedup (§15); no tight-stop forcing (§19).
