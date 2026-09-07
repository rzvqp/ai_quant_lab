# GC REAL-VOLUME CONTEXTUAL TRADE SELECTION V1 — EXECUTED (resumed; data gate now satisfied)

The earlier DATA_BLOCKED stop is resolved: Data Acquisition delivered the full 15-year genuine CME GC real-volume history. This resumes the
original mandate unchanged and answers the exact question — *does genuine CME GC real traded volume add causal winner-vs-loser information to
existing XAUUSD setups, beyond XAU context alone and beyond GC price alone?* INTERNAL_GENERALIZATION only; no XAU strategy modified; no OI/MBO;
no new source; protections intact.

## Data identity + causal gates — all PASS
`GC_HANDOFF_IDENTITY_GATE = PASS` · `GC_DATA_GATE = PASS` · `GC_REAL_TRADED_VOLUME_VERIFIED = YES`. Databento GLBX.MDP3, symbol **GC.v.0**
(continuous, volume roll on **previous-day** volume → causal, no lookahead), ohlcv-1m **5,160,829 rows** / derived 15m **350,825 rows**,
2011-07-26 → 2026-07-27, volume present on 100% of bars (677M contracts), 0 duplicates / out-of-order / OHLC violations. `ts_event` = bar-open,
so a GC bar is used only once fully closed (`ts_event ≤ XAU decision`). **`GC_XAU_CAUSAL_ALIGNMENT = PASS`, `FUTURE_GC_OBSERVATIONS_USED = 0`.**
Missing/degraded GC (2014-06/09 gaps) handled by a frozen rule (drop trade if no GC bar at decision or 32-bar lookback spans >5 days): 630
trades dropped. **Matched: SETUP_1 13,418 · SETUP_2 11,605 · SETUP_3 24,617 · TOTAL 49,640** (≫ the 1,000 minimum; overlap gate PASS).

## Central result — GC real volume adds no material winner-vs-loser information (all gates fail)
Four representations (A = XAU setup-relative baseline; B = +GC price; C = +GC real volume; D = +both), same L2-logistic capacity, chronological
walk-forward (4 date-blocks, expanding, purge 96), winner-retention frontier. At the practical 60% winner-retention anchor every representation
is negative (these are lose-less base setups), and the GC increments are far below the gates:

| setup | A (baseline) | B (+GC price) | C (+GC vol) | D (+both) | best-GC − A | best-GC − B |
|---|---|---|---|---|---|---|
| SETUP_1 sweep | −0.347 | −0.351 | −0.337 | −0.344 | +0.011 | +0.014 |
| SETUP_2 breakout | −0.274 | −0.278 | −0.271 | −0.273 | +0.003 | +0.007 |
| SETUP_3 auction | −0.103 | −0.087 | −0.097 | −0.093 | +0.010 | −0.006 |

- **`GC_INFORMATION_INCREMENTAL_VALUE = NO`** (all 3): best GC rep beats the XAU baseline by only +0.003…+0.011R (gate needs ≥+0.05R, ≥+0.03 in 2/3 folds); 0/3 folds positive everywhere.
- **`GC_REAL_VOLUME_SPECIFIC_VALUE = NO`** (all 3) — the central test: the best GC-volume representation beats GC-price-only by at most +0.014R (gate needs ≥+0.03R); on SETUP_3, adding volume is *worse* than price alone (−0.006).
- **`GC_PRICE_ONLY_INCREMENTAL_VALUE = NO`**: GC price beats the baseline by at most +0.016R (SETUP_3), below +0.05R.

## Negative controls confirm the null — the tiny GC-volume effect is within noise
| setup | real C | vol-destroy | TOD-only (A) | label-perm | matched-random | beats vol-destroy? | beats TOD? |
|---|---|---|---|---|---|---|---|
| SETUP_1 | −0.338 | −0.349 | −0.350 | −0.348 | −0.342 | NO | NO |
| SETUP_2 | −0.270 | −0.281 | −0.276 | −0.360 | −0.357 | NO | NO |
| SETUP_3 | −0.098 | −0.104 | −0.103 | −0.182 | −0.177 | NO | NO |

Real GC-volume selection does **not** beat the volume-destruction null (permuting GC volume within time-of-day buckets) or the time-of-day-only
baseline on any setup → **`GC_VOLUME_BEYOND_TOD_VALUE = NO`**. On SETUP_2/3 the C selection does beat label-permutation and matched-random — but
so does the XAU baseline (that is the setups' own lose-less signal, unchanged by destroying the real volume). So no part of the selection edge
is attributable to real GC participation. **`NEGATIVE_CONTROL_GATE = FAIL`** for the real-volume claim (real ≈ destroyed ≈ TOD). No practical
candidate is possible (`§36` requires real-volume-specific = YES). `GC_CROSS_SETUP_CONTEXT = NO`.

## §39 CEO answers
1. **Beyond XAU context?** NO (+0.003…+0.011R). 2. **Beyond GC price?** NO (≤+0.014R; SETUP_3 volume worse than price). 3. **GC price useful?**
NO (≤+0.016R). 4. **Merely time-of-day?** the little there is doesn't even beat TOD-only → not real participation. 5. **Sustained vs spike?** no
(persistence within null). 6. **Effort-vs-result?** no. 7. **Impulse-vs-pullback participation?** no. 8. **GC/XAU disagreement?** no. 9. **High GC
participation → failure?** no systematic effect. 10. **Favorable GC state by mechanism?** none consistent. 11. **Same GC state ≥2 mechanisms?**
NO. 12–13. **At 80%/60% retention?** all negative; GC adds +0.003…+0.011R. 14. **Any subset ≥+0.10R BASE?** NO. 15. **>0 STRESS?** NO. 16.
**≥2/3 folds positive?** NO (0/3). 17. **drop-best-5% positive?** N/A (nothing positive). 18. **Effective selected rate/yr?** high but negative.
19. **50 future obs ≤24mo?** by frequency yes, but there is nothing positive to validate. 20. **Strongest factual conclusion:** with 15 years of
genuine CME GC real traded volume causally joined to 49,640 XAU trades, GC real volume adds no material winner-vs-loser information to these
three XAU setups — not beyond XAU context, not beyond GC price, not beyond time-of-day volume seasonality.

## §44 FINAL OUTPUT
```
GC_REAL_VOLUME_CONTEXT_V1_COMPLETE = YES
GC_HANDOFF_IDENTITY_GATE = PASS · GC_DATA_GATE = PASS · GC_REAL_TRADED_VOLUME_VERIFIED = YES
GC_SOURCE = DATABENTO · GC_DATASET = GLBX.MDP3 · GC_SYMBOL = GC.v.0
GC_HISTORY_START = 2011-07-26 · GC_HISTORY_END = 2026-07-27 · GC_1M_ROWS = 5160829 · GC_15M_ROWS = 350825
GC_ROLL_RULE_VERIFIED = YES · GC_ROLL_LOOKAHEAD = NO
GC_XAU_CAUSAL_ALIGNMENT = PASS · FUTURE_GC_OBSERVATIONS_USED = 0
MATCHED_SETUP_A = 13418 · MATCHED_SETUP_B = 11605 · MATCHED_SETUP_C = 24617 · MATCHED_XAU_TRADES_TOTAL = 49640
GC_FEATURE_INVENTORY_HASH = 4915d71eff1ded6647c9 · GC_PROTOCOL_HASH = ea0adbe554f79f99838a
SETUP_A_GC_INFORMATION_INCREMENTAL_VALUE = NO · SETUP_A_GC_REAL_VOLUME_SPECIFIC_VALUE = NO · SETUP_A_GC_CONTEXTUAL_CANDIDATE = NO
SETUP_B_GC_INFORMATION_INCREMENTAL_VALUE = NO · SETUP_B_GC_REAL_VOLUME_SPECIFIC_VALUE = NO · SETUP_B_GC_CONTEXTUAL_CANDIDATE = NO
SETUP_C_GC_INFORMATION_INCREMENTAL_VALUE = NO · SETUP_C_GC_REAL_VOLUME_SPECIFIC_VALUE = NO · SETUP_C_GC_CONTEXTUAL_CANDIDATE = NO
GC_PRICE_ONLY_INCREMENTAL_VALUE = NO · GC_REAL_VOLUME_SPECIFIC_VALUE_OVERALL = NO · GC_VOLUME_BEYOND_TOD_VALUE = NO
GC_CROSS_SETUP_CONTEXT = NO · NEGATIVE_CONTROL_GATE = FAIL (real GC-volume within vol-destroy/TOD null)
BEST_SETUP = SETUP_3 (auction) · BEST_REPRESENTATION = B_plus_gc_price (least negative, -0.087R)
BEST_BASELINE_EXPECTANCY_60 = -0.1031R · BEST_GC_AUGMENTED_EXPECTANCY_60 = -0.0870R · BEST_GC_AUGMENTED_STRESS_60 = -0.1370R
BEST_WINNERS_RETAINED = 47.2% · BEST_LOSERS_AVOIDED = 69.4% · BEST_SELECTED_N = 7218 · BEST_EFFECTIVE_TRADES_PER_YEAR = ~480 (but negative)
GC_INFORMATION_PRESENT = NO
GC_INFORMATION_PRESENT_BUT_NOT_MONETIZABLE = NO
GC_CONTEXTUAL_DISCOVERY_CANDIDATE_FOUND = NO
PRACTICALLY_VALIDATABLE_WITHIN_24_MONTHS = NO
READY_FOR_PROSPECTIVE_FREEZE = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Authorized scope of conclusion (§43)
The specified GC real-volume representation did NOT add sufficient incremental information on the three frozen CTS setups: it does not beat XAU
context, GC price, or time-of-day volume seasonality, and it does not survive the volume-destruction control. No broader claim — that futures
volume is useless, that order flow is useless, that GC contains no information, or that external information cannot work — is made or supported.
This is now a genuinely *tested* null (49,640 causally-matched trades), not a data-blocked stop.
```
GC_REAL_VOLUME_CONTEXT_V1 = COMPLETE — GC real traded volume adds no material winner-vs-loser value to the 3 CTS setups (tested, not blocked)
```
