# ALPHA_XAUUSD_BEARISH_MOVE_MECHANISM_MINING_REPORT

**Mandate:** `ALPHA-XAUUSD-BEARISH-MOVE-MECHANISM-MINING-001` · **Date:** 2026-08-22 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_BEARISH_MECHANISM_MINING_COMPLETE` · **`NO_ROBUST_NEW_SHORT_MECHANISM_FOUND`** (in this mechanism-mining campaign — NOT "no short Alpha exists," per §21).
**Firewall:** gated M5 → causal H1/H4; no `read_csv`; N4=0; 2025+=0; no holdout/V1. **0 executable candidate IDs created** (≤30 budget) — per §14, no recurring generalizing mechanism was identified to freeze. DEV-only. No promotion; broker disabled.

---

## 0. Headline — the science (§23), before PnL
- **A. How many meaningful bearish moves?** Many. H4: 38% of bars start a ≥150p net-bearish move (12-bar horizon); ≥200p 710, ≥300p 323, ≥500p 74. H1: 24.5% ≥150p. **Gold falls a lot — bearish moves are common, not rare.**
- **B. Which regime do they start from?** Mostly **RANGE (44%), TRANSITION/OTHER (22%), TREND_UP (21%) — only 12% from TREND_DOWN.** The generic TREND_DOWN scan searched the wrong regime.
- **C–E. What preceded them / what discriminates?** **Nothing that generalizes.** No single causal feature separates bearish-move starts from bull-continuation controls (all std-diffs ≤ |0.12|). A multi-feature linear discriminant, and every event-sequence hypothesis, **fit noise in-sample and INVERT out-of-sample** (discovery→confirmation AUC 0.580→**0.446**; all sequence lifts flip negative).
- **F. Typical adverse path?** **Survivable for a majority:** 54% (H4) / 70% (H1) of bearish moves have adverse excursion ≤50p before the low. Median adverse 45p (H4) / 29p (H1).
- **G–H. Entry / stop location?** Execution is *feasible* (shallow adverse paths → tight stops would survive) — **but irrelevant, because selection (direction) is the binding failure.**
- **I. Which mechanisms recur across years?** **None** — the discovery-period discriminators do not reappear in the confirmation period.

## 1. Bearish-move catalog (§2) — outcome labels DIAGNOSTIC only
| threshold (net-bearish, bear>bull) | H4 (12-bar) | H1 (24-bar) |
|---|---|---|
| ≥80p | 1230 | 4489 |
| ≥100p | 1204 | 3991 |
| ≥150p | **988 (38%)** | **2479 (24.5%)** |
| ≥200p | 710 | 1547 |
| ≥300p | 323 | 595 |
| ≥500p | 74 | 122 |
Future excursion used **only** to label historical examples; never a feature (§2/§4).

## 2. Control population (§3)
Controls = comparable bars (same universe, same causal-feature space) **without** the subsequent ≥150p net-bearish move. H4: 988 bearish-start vs 1609 control. The discovery question is what was *different* before winners vs comparable non-winners (§3) — answered in §5.

## 3. Regime distribution (§23.B)
Bearish-move starts (H4): **RANGE 439 / TRANSITION_OTHER 218 / TREND_UP 209 / TREND_DOWN 122.** Controls: RANGE 703 / TRANSITION 371 / TREND_UP 294 / TREND_DOWN 241. **Bearish moves are NOT concentrated in TREND_DOWN** — they begin from ranges and up-trends, which is why price-structure TREND_DOWN mechanisms could never catch them.

## 4. Pre-move anatomy + feature discrimination (§6, §23.D) — the decisive result
Standardized mean difference (bearish group − control), H4, ranked by |effect|:
| feature | bearish mean | control mean | std-diff |
|---|---|---|---|
| dist_hh20_atr | +2.32 | +2.52 | −0.099 |
| trend_up | 0.536 | 0.582 | −0.093 |
| ext_ema20_atr | +0.213 | +0.109 | +0.071 |
| above_hh20 | 0.070 | 0.053 | +0.071 |
| efficiency | +0.046 | +0.027 | +0.060 |
| … (all others) | … | … | ≤ |0.05| |
**Every single-feature effect is noise-level (|std-diff| ≤ 0.10).** A ≥150p bearish move is statistically **indistinguishable** beforehand from a bar that continues up. (H1 identical: max |std-diff| 0.12.) **This is the root cause of every SHORT failure: there is no static pre-move causal signature.**

## 5. Path anatomy (§11, §23.F) — execution is NOT the problem
Adverse excursion (max high above entry) *before* the bearish low is reached:
| | H4 | H1 |
|---|---|---|
| median adverse | 45p | 29p |
| P25 / P75 | 20 / 90p | 12 / 59p |
| % adverse ≤30p | 36% | 51% |
| % adverse ≤50p | **54%** | **70%** |
**A majority of bearish moves rally little before falling** — a stop ~50p above entry would survive them. So the executable geometry *exists*; the prior failures were **not** primarily wrong-stop-placement — they were **wrong-selection** (couldn't identify which setups fall).

## 6. Sequence discovery + failure anatomy (§7, §8, §23.E) — with discovery/confirmation split (§13)
DEV split chronologically (not by outcome): **DISCOVERY** = first 60% (n=1528, 577 bear), **CONFIRMATION** = last 40% (n=1019, 406 bear). Sequences discovered on DISCOVERY, frozen, tested on CONFIRMATION:
| sequence | DISC n | DISC lift | CONF n | **CONF lift** |
|---|---|---|---|---|
| range-high rejection (rangepos>0.8 + upper wick) | 62 | +0.07 | 36 | **−0.20** |
| overextension vs ema100 (>2 ATR) | 603 | +0.05 | 323 | −0.04 |
| near major (100-bar) high (<0.5 ATR) | 124 | +0.19 | 36 | **−0.09** |
| overextension + rejection wick | 92 | +0.02 | 46 | −0.05 |
| range-high + overextension | 387 | +0.10 | 226 | **−0.10** |
| exhaustion run (≥4 up closes + overext) | 289 | +0.09 | 165 | **−0.14** |
**Every sequence with a positive discovery lift INVERTS to a negative lift on confirmation.** This is the textbook signature of overfitting: the discovery-period "edges" were noise, and they flip sign out-of-sample. **No event sequence generalizes.**

## 7. Multi-feature discriminator (§13) — frozen linear model
Weights learned on DISCOVERY (per-feature std-diff), standardized, frozen, applied to CONFIRMATION:
| | AUC |
|---|---|
| DISCOVERY (in-sample) | 0.580 |
| **CONFIRMATION (out-of-sample, frozen)** | **0.446** |
Best single-feature confirmation AUCs: 0.42–0.45 (all ≤ 0.50). **The out-of-sample AUC is BELOW random** — the model is anti-predictive on fresh data. Combining features does not rescue direction; it overfits and inverts.

## 8. Entry-location + stop-location analysis (§9, §10) — direction vs execution
The mandate's key hypothesis (direction and execution are different problems) is **confirmed and resolved:** execution is *feasible* (§5: shallow adverse paths, survivable stops), but **direction is not predictable** (§4/§6/§7). Losing shorts are caused by **wrong selection** (correct-direction-only 38% of the time, with no way to raise that causally), not by wrong-stop-placement. No entry/stop geometry can fix an unpredictable direction.

## 9. Large-move economics (§17) — targets exist, edge does not
Economic targets are amply available (H4: 323 moves ≥300p, 74 ≥500p; median bearish excursion 131p). The constraint is not target size — it is the inability to *select* these moves ex-ante.

## 10. Discovery / confirmation split (§13) — the guard that worked
The chronological split (no outcome leakage) is precisely what exposed the overfitting: in-sample structure (AUC 0.58, sequence lifts +0.07…+0.19) **vanished or inverted** out-of-sample (AUC 0.446, lifts −0.04…−0.20). Any candidate frozen from the discovery lifts would have failed — the split prevented a false candidate.

## 11. New causal candidates (§14) — NONE (correctly)
**Zero executable candidate IDs created.** Per §14, a candidate may be created *only after a recurring causal mechanism is identified.* No mechanism recurred across the discovery/confirmation split — all inverted. Building a candidate on discovery-only lift would be the hindsight overfitting error §4/§13 forbid. **The disciplined outcome is to create no candidate.** (Candidate results, tail robustness, temporal robustness per-candidate — §24, §19, §20 — are therefore N/A; the discriminator-level temporal evidence is the inversion itself.)

## 12. Graveyard (§25, §28)
- The entire tested **price-structure causal feature space** (location, distance-from-highs, overextension, efficiency, wicks, consecutive closes, ATR state, session, range position, 100-bar-high proximity) — **NO generalizing discriminator** (confirmation AUC ≤ 0.50).
- **6 event-sequence hypotheses** — all invert out-of-sample.
- Prior failed families (generic TREND_DOWN, immediate sweep, sweep+failed-acceptance, sweep+structbreak immediate, post-sweep pullback, generic displacement/follow-through) — reconfirmed as symptoms of the same root cause (no predictable direction). Recorded in `bearish_mining.py` / `bearish_mining2.py`.

## 13. Remaining unexplored hypotheses (§21, §28 — mandatory)
The negative is bounded to the **price-structure OHLC feature space on the 2021–2024 population.** Genuinely unexplored classes — likely where gold's bearish catalysts actually live — remain:
1. **Exogenous macro / news events** (Fed decisions, CPI, DXY prints) — gold's large reversals are frequently news-triggered; **no price-structure feature can predict a news catalyst.** Data Acquisition maintains a news monitor; a news-conditioned study is the highest-value unexplored avenue.
2. **Cross-asset drivers** (DXY, real yields, TIPS) — the fundamental drivers of gold direction, **absent from this price-only dataset.**
3. **Volume / order-flow microstructure** (delta, volume profile, absorption) — only aggregate M5 volume is available; true order-flow was not mined.
4. **A genuinely bearish population** — 2011–2013 (where the frozen `H4-bo-raw-S` short lives); this campaign's 2021–2024 window is structurally long-biased.
5. **Longer-horizon / multi-week regime exhaustion** beyond the 12–24 bar horizons tested.

## 14. CEO recommendation
1. **No new SHORT mechanism is recommended — `NO_ROBUST_NEW_SHORT_MECHANISM_FOUND` (this campaign).** The mechanism-mining approach delivered a *stronger, more general* result than prior candidate-testing: with a rigorous discovery/confirmation split, **bearish direction is shown to be unpredictable from the price-structure causal feature/sequence space** on 2021–2024 XAUUSD (out-of-sample AUC 0.446; all sequence lifts invert). Execution geometry is feasible; **selection is the wall.**
2. **This does NOT mean "no short Alpha exists"** (§21). It means: within price-structure features on this population, no generalizing bearish discriminator exists. **The unexplored classes (§13) — especially news/macro/cross-asset — are the rational next frontier**, and require data beyond the price-only feed (news calendar, DXY/yields), which the CEO/Data Acquisition would need to authorize.
3. **The most defensible interpretation:** gold's large bearish moves in 2021–2024 are predominantly **exogenously driven** (macro catalysts), not endogenously signaled by price structure — consistent with every price-based SHORT failing while price-based LONG-continuation edges (trend beta) succeeded.
4. **No promotion; broker disabled; DEV-only; no candidate frozen; no CALIB.** Existing candidates unaltered; portfolio SHORT remains only frozen `H4-bo-raw-S`.

**Terminal status:** `XAUUSD_BEARISH_MECHANISM_MINING_COMPLETE` · `NO_ROBUST_NEW_SHORT_MECHANISM_FOUND` (direction unpredictable in the price-structure space; unexplored: news/macro/cross-asset/order-flow). **STOP.**
