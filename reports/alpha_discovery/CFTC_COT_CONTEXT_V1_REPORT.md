# CFTC COT POSITIONING CONTEXT V1 — EXECUTED

Tests whether point-in-time CFTC Commitments-of-Traders positioning for COMEX Gold adds winner-vs-loser information to the three frozen XAU
setups, beyond XAU context, GC price, GC real volume, and GC open interest. Public CFTC data (no purchase). INTERNAL_GENERALIZATION only; no XAU
strategy modified; GC volume/OI results untouched; protections intact.

## Data + causality — PASS (with a caught mapping bug and a disclosed revision limitation)
`COT_DATA_GATE = PASS` · `COT_CAUSALITY_GATE = PASS`. Disaggregated Futures-Only, COMEX GOLD (CFTC code **088691**), **817 weekly reports**,
2011-01-04 → 2026-08-25. Each report references a Tuesday and is released the following Friday ~3:30pm ET; frozen availability = Tue+3d+20:00 UTC;
an XAU trade uses only the most recent report released before its decision (no daily interpolation). **`FUTURE_COT_OBSERVATIONS_USED = 0`**,
median COT age 4.5 days. A datetime-scaling bug that had mapped every trade to the last 2026 report was surfaced by the causal-age audit and
fixed before any result was accepted (see data audit). Revisions: open files hold current values (small/rare revisions), assigned to release
time — disclosed point-in-time approximation. Matched: 13,418 / 11,605 / 24,617 = **49,640 trades**.

## Result — COT positioning adds no winner-vs-loser value (all gates fail)
Seven representations (A XAU · B +price · C +volume · D +OI · E +COT · F +price+COT · G +volume+OI+COT), same L2-logistic capacity,
chronological walk-forward, retention frontier. At 60% winner-retention every representation is negative and 0/3 folds positive; the COT
increment over the best non-COT representation is far below the gate:

| setup | best non-COT | best COT-rep | best COT − best non-COT | COT_INCREMENTAL |
|---|---|---|---|---|
| SETUP_1 sweep | C_volume −0.337 | G −0.335 | **+0.0021** | NO |
| SETUP_2 breakout | C_volume −0.271 | G −0.291 | **−0.0201** (worse) | NO |
| SETUP_3 auction | B_price −0.087 | F −0.087 | **−0.0004** | NO |

- **`COT_INCREMENTAL_VALUE_OVERALL = NO`** (gate: ≥+0.05R over the strongest non-COT rep; achieved +0.002R or worse).
- Negative controls: real COT does **not** beat COT-destruction (permuting COT within year buckets) on any setup — on the breakout setup real
  COT is slightly *worse* than destroyed (it adds noise, not signal). The G selection beats label-permutation/matched-random on SETUP_2/3, but
  that is the XAU baseline's own lose-less signal (destroying the COT does not change it). **`NEGATIVE_CONTROL_GATE = FAIL`** for the COT claim.
- No participant category or positioning state carried value; **`COT_CROSS_SETUP_CONTEXT = NO`**; no practical candidate.

## §31 CEO answers
1. **Beyond XAU context?** NO. 2. **Beyond GC price?** NO. 3. **Beyond GC volume?** NO. 4. **Beyond GC OI?** NO. 5. **Which participant carried
most information?** none (COT-destruction leaves the result unchanged). 6. **Positioning LEVEL?** NO. 7. **CHANGE?** NO. 8. **EXTREMES?** NO. 9.
**Participant disagreement?** NO. 10. **Effect decay with report age?** no effect to decay (median age 4.5 d). 11. **Setup-specific?** no
consistent effect (worst on breakout). 12. **Common state ≥2 setups?** NO. 13–14. **80%/60% retention?** all negative. 15. **Any subset
≥+0.10R?** NO. 16. **>0 STRESS?** NO. 17. **≥2/3 folds positive?** NO (0/3). 18. **drop-best-5% >0?** N/A. 19. **Effective rate/yr?** high but
negative. 20. **Strongest conclusion:** with 15.6 years of point-in-time CFTC COMEX-gold positioning causally joined to 49,640 XAU trades, COT
adds no material winner-vs-loser information beyond XAU context, GC price, GC volume, or GC open interest.

## §35 FINAL OUTPUT
```
CFTC_COT_CONTEXT_V1_COMPLETE = YES · COT_DATA_GATE = PASS · COT_CAUSALITY_GATE = PASS
COT_MARKET = COMEX GOLD · COT_MARKET_CODE = 088691 · COT_REPORT_TYPE = Disaggregated Futures-Only
COT_HISTORY_START = 2011-01-04 · COT_HISTORY_END = 2026-08-25 · COT_REPORTS_TOTAL = 817
MATCHED_XAU_TRADES_TOTAL = 49640
COT_FEATURE_HASH = 86e65ba3381c17601f5f · COT_PROTOCOL_HASH = 9df6ff58f285001afae4
SETUP_A_COT_INCREMENTAL_VALUE = NO · SETUP_A_COT_CONTEXTUAL_CANDIDATE = NO
SETUP_B_COT_INCREMENTAL_VALUE = NO · SETUP_B_COT_CONTEXTUAL_CANDIDATE = NO
SETUP_C_COT_INCREMENTAL_VALUE = NO · SETUP_C_COT_CONTEXTUAL_CANDIDATE = NO
COT_INCREMENTAL_VALUE_OVERALL = NO · COT_CROSS_SETUP_CONTEXT = NO
MANAGED_MONEY_VALUE = NO · PRODUCER_VALUE = NO · SWAP_DEALER_VALUE = NO
POSITION_LEVEL_VALUE = NO · POSITION_CHANGE_VALUE = NO · POSITION_EXTREME_VALUE = NO · PARTICIPANT_DISAGREEMENT_VALUE = NO
NEGATIVE_CONTROL_GATE = FAIL (real COT within/below COT-destruction null)
BEST_SETUP = SETUP_3 (auction) · BEST_REPRESENTATION = F_price_cot (-0.0874R) · BEST_COT_STATE = none discriminating
BEST_BASELINE_EXPECTANCY_60 = -0.0870R · BEST_COT_EXPECTANCY_60 = -0.0874R · BEST_COT_STRESS_60 = -0.1374R
BEST_WINNERS_RETAINED = 46.2% · BEST_LOSERS_AVOIDED = 69.2% · BEST_SELECTED_N = ~7200 · BEST_EFFECTIVE_TRADES_PER_YEAR = ~480 (but negative)
COT_INFORMATION_PRESENT = NO
COT_INFORMATION_PRESENT_BUT_NOT_MONETIZABLE = NO
COT_CONTEXTUAL_DISCOVERY_CANDIDATE_FOUND = NO
PRACTICALLY_VALIDATABLE_WITHIN_24_MONTHS = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Scope
A well-powered tested null on a specific COT representation and the three CTS setups. Per §30 no positioning-direction claim is made. No broader
conclusion — that COT, positioning, or external data is information-free — is asserted. Together with the GC volume and GC OI nulls, the
exchange-side futures channels tested so far do not condition these three XAU mechanisms.
```
CFTC_COT_CONTEXT_V1 = COMPLETE — COT positioning adds no winner-vs-loser value to the 3 CTS setups (beyond XAU/price/volume/OI)
```
