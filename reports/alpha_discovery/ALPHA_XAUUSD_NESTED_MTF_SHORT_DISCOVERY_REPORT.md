# ALPHA_XAUUSD_NESTED_MTF_SHORT_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-NESTED-MTF-SHORT-001` · **Date:** 2026-08-22 · **Stat evidence base:** commit `b8d0447`.
**Terminal status:** `XAUUSD_NESTED_MTF_SHORT_DISCOVERY_COMPLETE` · **`NO_ROBUST_NESTED_MTF_SHORT_FOUND`** (bounded to the price-only nested-MTF space; NOT "no short Alpha exists").
**Firewall:** 100% XAUUSD price-only (no DXY/yields/macro/news/cross-asset/order-flow); gated M5 → causal M15/H1/H4; no `read_csv`; N4=0; 2025+=0; no V1/holdout/CALIB. **12 executable hierarchy IDs (N1–N12, ≤24 budget; checkpoint at 12), 4 taken to execution, 0 frozen** — per §17/§29 no hierarchy passed the directional gate. DEV-only. No promotion; broker disabled; the nine frozen strategies (§31) untouched.

---

## 0. Headline — answers to the §32 scientific questions
1. **Does nested MTF ordering contain bearish information absent from same-TF sequences?** **NO.** A bounded 384-hierarchy cross-TF scan yields **10 "survivors"** of a strict both-splits-positive gate — but **~9.8 are expected by pure chance**. 10 ≈ 9.8: the count of "generalizing" nested hierarchies is **statistically indistinguishable from noise.**
2. **Which hierarchy works best (H4→H1 / H4→H1→M15 / H1→M15 / H1→M15→M5)?** None robustly. The least-bad are `H4-context → H1 HIGH_SWEEP → M15 FAILED_RECLAIM` variants — all within chance.
3. **Which timeframe contributes the largest incremental lift?** The **M15 trigger** (final event). Common-parent attribution shows the **H4 parent and H1 layers add ~0 or negative lift out-of-sample** — the little information present is the same M15 discriminator, not the cross-TF nesting.
4. **Does H1 structural failure become meaningful only inside specific H4 contexts?** **No** — conditioning H1 events on any H4 context (bullish-state/upper-range/overextension/transition) leaves lifts within noise; no context "unlocks" an H1 edge.
5. **Does M15 distinguish real reversals from temporary H1 weakness?** Marginally in-sample, not out-of-sample beyond chance; execution shows it does not separate winners from losers.
6. **Does a second bearish impulse add information?** On DISCOVERY yes (two-stage +0.184 lift, n59) — but it **collapses/inverts on CONFIRMATION (−0.045)**. Same overfitting signature as the same-TF campaign.
7. **Does M5 add execution value?** **N/A by design** (§8): M5 is optional and only evaluated for hierarchies already promising at H4/H1/M15. No hierarchy passed the §17 directional gate, so the parent thesis never generalized — there was nothing for M5 to refine.
8. **Can the hierarchy identify 100–300+ pip bearish moves?** The moves exist (M15 base rate 12–14% for a ≥150p departure over 48 bars), but **no hierarchy selects them robustly.**
9. **Does it work outside a single year?** **NO.** The only positive-expectancy hierarchies (two-stage, upper-close-below) are positive 2021–2022 but **negative in 2023**, carried by a few 2022 (gold-selloff) tail trades (top-10% share 330–476%).
10. **Is there an executable SHORT strategy?** **NO.**

## 1. Evidence integrity
Price-only. Gated M5 → causal M15/H1/H4 (12×/3×/48× aggregation, `m5_data.py`). No exogenous inputs; no `read_csv`; N4=0; 2025+=0; CALIB/V1/holdout not opened; DEV-only.

## 2. MTF causal alignment (§9, §10) — completed-bar, verified
Each causally-aggregated HTF bar carries `close_time` = the last constituent M5 timestamp = when the bar is genuinely **complete/known**. Every M15 trigger conditions on HTF bars aligned by `searchsorted(close_time ≤ trigger.close_time)`. **Assertions PASS on all 51,736 aligned M15 bars:** `H1.close ≤ trigger.close`, `H4.close ≤ trigger.close`, and `H4.close ≤ H1.close` (strict **H4 → H1 → M15** ordering; no partial-HTF-bar leakage). This is the §10 test, run in code, not asserted in prose.

## 3. Population, split, base rates (§11, §18)
M15 valid labelled bars = **40,636.** Chronological split fixed **before searching**: DISCOVERY = first 60% (n=24,381, base bearish rate **0.138**), CONFIRMATION = last 40% (n=16,255, base **0.116**), cut 2023-04-25. Label = ≥150p net-bearish over forward 48 M15 bars (12h), `bear>bull`; **diagnostic only, never a feature.**

## 4. Parent contexts (§5) + H1 (§6) + M15 (§7) layers
- **H4 parent contexts (states):** BULLISH_STATE, UPPER_RANGE, SWINGHIGH_INTERACT, OVEREXT_UP, FAILED_CONT, COMPRESSION, EXPANSION, TREND_UP, RANGE, TRANSITION.
- **H1 structural events:** FAILED_HH, BEAR_DISP, STRUCT_BREAK, FAILED_BULL_CONT, CLOSE_BELOW_LEVEL, LOWER_HIGH, FAILED_RECLAIM, HIGH_SWEEP, SECOND_BEAR.
- **M15 triggers:** FAILED_RECLAIM, LOWER_HIGH, BEAR_DISP, MICRO_BREAKDOWN, SECOND_BEAR, COMPR_EXP_DOWN, BREAK_RETEST, FAILED_BULL_IMP, REJECT_RECOVERY.
All causal (fractals confirmed with lag, rolling/EWM features shifted).

## 5. Common-parent attribution (§12, §19) — the decisive directional test
Twelve curated hierarchies (N1–N12), each evaluated as **parent → +H1 event → +M15 trigger on the same population** (the matched control at every layer: parent = same H4 context *without* the lower-TF discriminator). Representative rows (lift over base; DISC ‖ CONF):

| hierarchy | DISC parent → +H1 → +M15 | CONF parent → +H1 → +M15 |
|---|---|---|
| N1 failbull (BULL→FAILED_BULL_CONT→FAILED_RECLAIM) | +0.008 → −0.020 → −0.031 | −0.012 → −0.023 → −0.040 |
| N7 failcont-break (FAILED_CONT→STRUCT_BREAK→MICRO_BREAKDOWN) | +0.010 → +0.026 → **+0.071** (n182) | −0.003 → −0.022 → **+0.019** (n74) |
| N8 twostage (BULL→SECOND_BEAR→SECOND_BEAR) | +0.008 → −0.009 → **+0.184** (n59) | −0.012 → −0.062 → **−0.045** (n42) |
| N12 upper-closebl (UPPER→CLOSE_BELOW_LEVEL→BEAR_DISP) | +0.020 → +0.042 → **+0.144** (n39) | −0.016 → −0.008 → **+0.098** (n14) |

**Pattern (identical to prior campaigns):** the H4 parent lift is ~0 and turns **negative on CONFIRMATION for nearly every bearish context** (a bearish-looking H4 state makes a bearish move *less* likely out-of-sample — the 2021–2024 long-bias). The big discovery lifts (N8 +0.184, N12 +0.144) sit on tiny samples and **collapse or land on n=14 out-of-sample.** No layer robustly adds directional information.

## 6. Bounded automated cross-TF scan (§29) — the statistical verdict
6 H4 contexts × 8 H1 events × 8 M15 triggers = **384 nested hierarchies**, strict gate: nfD≥20, nfC≥20, **DISC lift > +1 SE and CONF lift > +1 SE** (both meaningfully bearish-predictive). Result:

> **survivors = 10 / 384. Expected false-positives by chance ≈ 9.8.**

**10 ≈ 9.8 — the number of "generalizing" nested hierarchies equals the noise expectation.** The survivors moreover cluster on overlapping `HIGH_SWEEP → FAILED_RECLAIM / BREAK_RETEST` firing sets (the same M15 events counted under BULLISH_STATE / UPPER_RANGE / OVEREXT_UP — ~3–4 distinct sets, not 10). Two higher-lift small-n hits (`OVEREXT_UP→BEAR_DISP→FAILED_BULL_IMP` CONF +0.173/n38; `BULLISH_STATE→BEAR_DISP→FAILED_BULL_IMP` CONF +0.093/n86) are exactly where large SE + 384-way multiple testing predict chance winners. **Nested MTF ordering does not carry bearish information beyond chance.**

## 7. Execution architecture + path/tail/temporal (§17→§20, §21, §23, §26, §27) — the closest candidates falsified
Per §17 no hierarchy cleared the directional gate, but to separate *prediction failure* from *stop failure* (§23) the 4 strongest were executed: short next M15 open, **H1 structural stop** (recent completed H1 swing high above entry, §21), RR targets {1.5, 2, 3}, STRESS cost, one-at-a-time:

| hierarchy | rr | n | WR | avgR | medR | best-5%-rem | best-10%-rem | top-10% share | 2021 / 2022 / 2023 |
|---|---|---|---|---|---|---|---|---|---|
| N7 failcont-break | 2.0 | 100 | 0.35 | −0.090 | −0.351 | −0.199 | −0.320 | — | −0.17 / +0.03 / −0.10 |
| N4 swinghi-sweep | 2.0 | 212 | 0.396 | −0.099 | −0.652 | −0.201 | −0.325 | — | −0.20 / +0.07 / −0.12 |
| N8 twostage | 3.0 | 52 | 0.519 | +0.040 | +0.027 | **−0.076** | **−0.168** | **476%** | +0.07 / +0.33 / **−0.08** |
| N12 upper-closebl | 3.0 | 30 | 0.467 | +0.008 | −0.090 | **−0.093** | **−0.208** | **2308%** | +0.44 / +0.66 / **−0.32** |

- **N7, N4: outright negative** (avg −0.09/−0.10, median −0.35/−0.65). Prediction fails → execution fails.
- **N8, N12: avg ≈ 0 but every robustness gate fails** — best-5% and best-10%-removed **negative** (tail-fragile, §26), top-10% profit share **330–2308%** (a handful of trades carry all profit), and **2023 negative** while 2021/22 positive (§27 single-period dependence — the 2022 gold selloff bleeding through a few tail trades). Not an edge; a lottery on one adverse year.

**Path diagnosis (§23):** the failure is **wrong selection**, not wrong stop or wrong timing — the H1 structural stop is honest and shallow, yet expectancy is zero-to-negative because the nested sequence does not identify which setups actually fall. Identical to the mechanism-mining and same-TF findings.

## 7b. Failed-bullish-continuation / two-stage / high-to-low / compression (§13–§16) — tested, none robust
- **Failed-bullish-continuation (§13, N1/N2):** negative lift at every layer, both splits.
- **Two-stage reversal (§14, N8):** biggest discovery lift (+0.184) → confirmation collapse (−0.045); execution positive only via 2022 tail.
- **High-to-low structural handoff (§15, N4/N5/N12):** within chance; execution negative or tail-fragile.
- **Compression hierarchy (§16, N9):** M15 conditional too sparse (n=1–3) to evaluate — falsified for insufficient support.

## 8. Candidate table (§33) — EMPTY
**Zero frozen executable candidates.** Per §17/§29 a candidate requires a hierarchy that first generalizes directionally; none did (scan survivors ≈ chance; the closest executables are tail-fragile and single-period-dependent). Freezing one from a discovery-only or chance-level lift would be the overfitting the split and the matched controls exist to catch.

## 9. Graveyard (§29, §30)
- 12 curated nested hierarchies N1–N12 — no robust directional lift; the discovery spikes (N8, N12) invert/collapse on confirmation.
- 384-combo automated cross-TF scan — survivors indistinguishable from chance (10 vs 9.8), clustered on overlapping HIGH_SWEEP→FAILED_RECLAIM sets.
- Executed hierarchies N7/N4 (negative), N8/N12 (tail-lottery, 2023-negative). Recorded in `nested_mtf_short.py` / `nested_mtf_short2.py`.

## 10. Remaining unexplored classes (§34)
Bounded to **hard-boolean nested hierarchies over the tested H4/H1/M15 alphabet on 2021–2024.** Genuinely unexplored (weak priors given the component events do not discriminate):
1. **Probabilistic / learned MTF models** (hierarchical HMM, Markov, gradient-boosted cross-TF state) rather than hard boolean AND-chains.
2. **Continuous cross-TF state interactions** (e.g., H4-location × H1-momentum surfaces) instead of discrete events.
3. **M5-native micro-hierarchies** as the primary edge TF (M5-native already failed in prior work — low prior).
4. **A genuinely bearish population** (2011–2013), where the frozen `H4-bo-raw-S` short lives and nested structure may carry real information.
5. **Exogenous conditioning** (macro/news/DXY/yields) — out of this mandate's price-only scope, and the most likely true driver of gold's bearish catalysts.

## 11. CEO recommendation
1. **No nested-MTF SHORT candidate — `NO_ROBUST_NESTED_MTF_SHORT_FOUND`.** Cross-timeframe conditional sequences do **not** recover a generalizing bearish discriminator. The definitive evidence is the automated scan: across 384 nested hierarchies the survivor count equals the chance expectation (10 ≈ 9.8), and common-parent attribution shows the H4/H1 layers add ~0-or-negative out-of-sample lift — the nesting contributes no information beyond the M15 event, which is itself within noise.
2. **This is a genuinely new class, honestly tested and negative** — not a repeat. The completed-bar cross-TF causality was verified in code (H4→H1→M15 ordering, no partial-bar leakage). The prior same-TF negative (0/130 pairs) and this nested negative (10/384 ≈ chance) now jointly bound the **price-only sequential SHORT space** on 2021–2024 gold.
3. **Most defensible interpretation (unchanged, now stronger):** gold's 2021–2024 large bearish moves are predominantly **exogenously (macro) driven** — no price-only representation (static, same-TF sequential, or nested cross-TF sequential) reliably anticipates them. Execution geometry is feasible; **selection is the wall.**
4. **No promotion; broker disabled; DEV-only; no candidate; no CALIB.** The nine frozen strategies (§31) are unaltered; portfolio SHORT exposure remains only frozen `H4-bo-raw-S` (2011–2018 population). Genuinely unexplored: probabilistic/continuous MTF models, a bearish population, and (out of scope) exogenous conditioning.

**Terminal status:** `XAUUSD_NESTED_MTF_SHORT_DISCOVERY_COMPLETE` · `NO_ROBUST_NESTED_MTF_SHORT_FOUND`. **STOP.**
