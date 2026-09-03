# GC OPEN INTEREST CONTEXTUAL VALUE V1 — EXECUTED

Tests whether CME GC open interest, available causally before an XAU trade decision, adds winner-vs-loser information beyond XAU setup context,
GC price, and GC real traded volume — using only the already-acquired Databento statistics (no new purchase). This is an OI source test, not a
volume V2; the frozen GC_VOLUME_V1 result is untouched. INTERNAL_GENERALIZATION only; no XAU strategy modified; no COT/options/MBO; protections intact.

## Data + causality — PASS
`OI_CAUSALITY_GATE = PASS`. Databento GLBX.MDP3 statistics GC.FUT, `stat_type=9` OPEN_INTEREST (183,125 raw records → **4,566 daily total-family
OI observations**, 2011-07-26 → 2026-07-27, `OI_UPDATE_FREQUENCY = DAILY`). Primary construction = daily **total-family GC OI** (sum across
outrights, roll-immune, frozen). Availability = `ts_event` (dissemination, ~13-14 UTC); for an XAU decision at T only OI with `ts_event ≤ T` is
used (~1-day lag). **`FUTURE_OI_OBSERVATIONS_USED = 0`.** Matched to the 3 frozen CTS setups: 13,418 / 11,605 / 24,617 = **49,640 trades**.

## Result — GC open interest adds no winner-vs-loser value (all gates fail)
Seven representations isolate OI's contribution (A XAU · B +price · C +volume · D +OI · E +price+OI · F +volume+OI · G +all), same L2-logistic
capacity, chronological walk-forward, retention frontier. At 60% winner-retention every representation is negative and 0/3 folds positive; the
OI increment over the best non-OI representation is far below the gate:

| setup | best non-OI | best OI-rep | best OI − best non-OI | price×OI (E−B) | vol×OI (F−C) | GC_OI_INCREMENTAL |
|---|---|---|---|---|---|---|
| SETUP_1 sweep | C_volume −0.337 | G_all −0.333 | **+0.0035** | +0.007 | +0.001 | NO |
| SETUP_2 breakout | C_volume −0.271 | F_volume_oi −0.265 | **+0.0058** | +0.003 | +0.006 | NO |
| SETUP_3 auction | B_price −0.087 | E_price_oi −0.094 | **−0.0067** | −0.007 | −0.000 | NO |

- **`GC_OI_INCREMENTAL_VALUE_OVERALL = NO`** (gate: ≥+0.05R over the strongest non-OI rep; achieved +0.003…+0.006R or worse).
- **`GC_PRICE_X_OI_VALUE = NO`**, **`GC_VOLUME_X_OI_VALUE = NO`** — OI does not make the previously-useless GC volume conditionally useful (+0.001…+0.006R), and price×OI states carry no value.
- **`GC_XAU_RELATIVE_X_OI_VALUE = NO`**. **`GC_OI_CROSS_SETUP_CONTEXT = NO`**.

## Negative controls confirm the null
| setup | real G | OI-destroy | time-shift | label-perm | matched-random | beats OI-destroy? |
|---|---|---|---|---|---|---|
| SETUP_1 | −0.329 | −0.335 | −0.334 | −0.347 | −0.342 | NO |
| SETUP_2 | −0.269 | −0.274 | −0.274 | −0.356 | −0.357 | NO |
| SETUP_3 | −0.093 | −0.093 | −0.092 | −0.178 | −0.177 | NO |

Real OI does **not** beat OI-destruction (permuting OI within month buckets) on any setup → OI carries no trade-specific information. The G
selection beats label-permutation/matched-random on SETUP_2/3, but that is the XAU baseline's own lose-less signal (destroying the OI does not
change it). **`NEGATIVE_CONTROL_GATE = FAIL`** for the OI claim. No practical candidate.

## §26 CEO answers
1. **Beyond XAU context?** NO (≤+0.006R). 2. **Beyond GC price?** NO. 3. **Beyond GC volume?** NO. 4. **Does OI make GC volume conditionally
useful?** NO (vol×OI +0.001…+0.006R). 5. **Price×OI?** NO. 6. **Volume×OI?** NO. 7. **XAU/GC disagreement×OI?** NO. 8. **Setup-specific?** no
consistent OI effect. 9. **Same OI state ≥2 mechanisms?** NO. 10–11. **80%/60% retention?** all negative. 12. **Any ≥+0.10R?** NO. 13. **>0
STRESS?** NO. 14. **≥2/3 folds positive?** NO (0/3). 15. **drop-best-5% positive?** N/A. 16. **Effective rate/yr?** high but negative. 17. **50
future obs ≤24mo?** by frequency yes, but nothing positive to validate. 18. **Strongest conclusion:** with 15 years of genuine daily CME GC open
interest causally (point-in-time) joined to 49,640 XAU trades, OI adds no material winner-vs-loser information beyond XAU context, GC price, or
GC volume, and does not make GC volume conditionally useful.

## §30 FINAL OUTPUT
```
GC_OI_CONTEXT_V1_COMPLETE = YES · OI_CAUSALITY_GATE = PASS
OI_FIELD_PRESENT = YES · OI_HISTORY_START = 2011-07-26 · OI_HISTORY_END = 2026-07-27 · OI_UPDATE_FREQUENCY = DAILY
MATCHED_XAU_TRADES_TOTAL = 49640
GC_OI_FEATURE_HASH = 2a2c66ac3007ea3c4167 · GC_OI_PROTOCOL_HASH = 841f8b5f7fcbdddd5a7c
SETUP_A_GC_OI_INCREMENTAL_VALUE = NO · SETUP_A_GC_OI_CONTEXTUAL_CANDIDATE = NO
SETUP_B_GC_OI_INCREMENTAL_VALUE = NO · SETUP_B_GC_OI_CONTEXTUAL_CANDIDATE = NO
SETUP_C_GC_OI_INCREMENTAL_VALUE = NO · SETUP_C_GC_OI_CONTEXTUAL_CANDIDATE = NO
GC_OI_INCREMENTAL_VALUE_OVERALL = NO · GC_OI_CROSS_SETUP_CONTEXT = NO
GC_PRICE_X_OI_VALUE = NO · GC_VOLUME_X_OI_VALUE = NO · GC_XAU_RELATIVE_X_OI_VALUE = NO
NEGATIVE_CONTROL_GATE = FAIL (real OI within OI-destruction null)
BEST_SETUP = SETUP_3 (auction) · BEST_REPRESENTATION = G_all (least negative OI rep, -0.0938R)
BEST_BASELINE_EXPECTANCY_60 = -0.0870R · BEST_OI_AUGMENTED_EXPECTANCY_60 = -0.0938R · BEST_OI_AUGMENTED_STRESS_60 = -0.1438R
BEST_WINNERS_RETAINED = 47.5% · BEST_LOSERS_AVOIDED = 68.5% · BEST_SELECTED_N = 7389 · BEST_EFFECTIVE_TRADES_PER_YEAR = ~480 (but negative)
GC_OI_INFORMATION_PRESENT = NO
GC_OI_INFORMATION_PRESENT_BUT_NOT_MONETIZABLE = NO
GC_OI_CONTEXTUAL_DISCOVERY_CANDIDATE_FOUND = NO
PRACTICALLY_VALIDATABLE_WITHIN_24_MONTHS = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scope
A well-powered tested null on a specific OI representation and the three CTS setups. Per §25 no positioning-direction claim is made. No broader
conclusion — that open interest, positioning, or external data is information-free — is asserted or supported.
```
GC_OI_CONTEXT_V1 = COMPLETE — GC open interest adds no winner-vs-loser value to the 3 CTS setups (beyond XAU/price/volume); does not rescue volume
```
