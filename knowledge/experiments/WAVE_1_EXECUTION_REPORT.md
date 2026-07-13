# WAVE_1_EXECUTION_REPORT — EXP-01..EXP-06 (branch `wave1-execution`)

Frozen spec: `knowledge/experiments/WAVE_1_SPEC.md`. Harness: `code/wave1_harness.py`. Driver: `code/run_wave1.py`.
Pre-registration (ids/seeds/B/K/margins/multiplicity fixed BEFORE any p): `results/experiments/wave1/wave1_prereg.json`.
Runtime env: Python 3.14.6 / pandas 3.0.3 / numpy 2.5.1 / pyarrow 25.0.0 (matches `runtime_versions.json`).
Segments: research=50,491 · OOS=16,830 · **holdout=16,831 SEALED (never loaded)**. Full run 1,622 s.

**No VALIDATED ALPHA / PRODUCTION READY / FINAL STRATEGY is claimed anywhere.** All statuses are research-segment,
family-wise-corrected, DIAGNOSTIC. Success criterion = information gain, not profitability.

## 0. Headline table (primary contrasts, Holm-adjusted across the family of 6)

| exp | question | primary contrast | n (primary) | raw p | Holm adj p | **STATUS** |
|---|---|---|---|---|---|---|
| EXP-01 | does confirmation carry the S1 sweep edge? | confirmed − raw (paired, same events) | 337 | 0.0883 | 0.441 | **NO DIFFERENCE DETECTED** |
| EXP-02 | does the efficiency gate carry S39's edge? | gated vs random-subset of continuation | 159 | 0.297 | 0.532 | **NO DIFFERENCE DETECTED** |
| EXP-03 | sweep: timing-alpha or gold beta? | observed vs β/regime-matched null | 399 | 0.00695 | **0.0417** | **SUPPORTS CLAIM** *(diagnostic-grade)* |
| EXP-04 | opening-range: alpha or beta? | observed vs β/regime-matched null | 406 | 0.177 | 0.532 | **WEAKENS CLAIM** |
| EXP-05 | does the sweep LEVEL matter? | real vs level-label shuffle | 399 | 0.118 | 0.471 | **NO DIFFERENCE DETECTED** |
| EXP-06 | does the prior-day level matter for the fade? | real vs level-label shuffle | 272 | 0.238 | 0.532 | **NO DIFFERENCE DETECTED** |

**Wave-1 family-wise correction = Holm-Bonferroni across the 6 primary p's. Only EXP-03 crosses α=0.05 after
correction (BH-FDR q=0.10 agrees: EXP-03 only). Global S1–S51 FDR NOT run. Holdout SEALED.**

---

## 1. Per-experiment results

### EXP-01 — Confirmation contribution in liquidity sweeps (S1, HGv1-042) → NO DIFFERENCE DETECTED
- **Arms (research):** confirmed n=399, exp **+0.0320** R, PF 1.05, maxDD 20.7R · raw(all sweeps) n=510, exp **−0.145** R, PF 0.81, maxDD 88.7R.
- **Primary paired contrast** (337 events executed in BOTH arms): Δ(confirmed−raw) = **+0.107 R**, 95% bootstrap CI **[−0.047, +0.261] straddles 0**, sign-flip p=0.088, Holm adj p=0.441.
- **Decomposition (CEO-mandated — the arms differ mechanically in ≥4 ways, so NO simple-causality claim):**
  971 sweeps → 827 confirm (confirm-rate 0.85); mean entry **delay 3.07 bars**; mean dir-adjusted **entry-price shift +0.84** (confirmed enters later & worse); trade count **510 → 399**.
  - confirmation-as-**SELECTION**: raw on *all* sweeps −0.145 → raw on *confirmed-only* sweeps −0.031 (≈ +0.114 from dropping the 15% that never confirm).
  - confirmation-as-**TIMING** (delay+price): raw confirmed-only −0.031 → confirmed +0.032 (≈ +0.063 from the delayed entry).
- **Reading:** the full S1-vs-raw gap is a MIXTURE of selection and timing; on the identical event sample the confirmation step's marginal effect is positive-leaning but **not family-wise significant and the CI straddles zero**. OOS confirmed exp = **−0.061** (n=106, negative). Exposure/holding-time not measured (engine returns R,si,ei only — documented limitation).

### EXP-02 — Efficiency-gate contribution in continuation (S39, HGv1-043) → NO DIFFERENCE DETECTED
- **Same-universe design:** the ungated generic-continuation universe is executed once (n=1286, exp **−0.098** R); gate-ON = the efficiency-labeled partition (er≥0.5 at the signal bar) n=159, exp **−0.052** R.
- **Primary contrast:** gated mean vs random equal-size subsets of the whole continuation universe: Δ = **+0.046 R**, gated-mean 95% CI **[−0.180, +0.078]** (straddles the ungated mean −0.098), p=0.297, Holm adj p=0.532.
- **Decomposition:** efficient = 12.4% of continuation events; long-share 0.53 (on) vs 0.56 (off); cost-drag 0.023R (on) vs 0.043R (off, efficient trends have wider stops). S39 *as-registered* (its own onset) exp = +0.029 (n=320) — marginally positive, but that reflects S39's specific onset timing, **not** the isolated selection value of the gate (which is what the primary tests).
- **Reading:** the ungated continuation population is a losing population; the efficiency gate improves it (−0.098→−0.052) but **does not select better-than-random trends significantly**, and the gated arm is still negative in-sample. OOS gate-ON exp = +0.024 (n=58). No genuine efficiency edge demonstrated at the Wave-1 bar.

### EXP-03 — Sweep: timing-alpha or gold beta? (S1, HGv1-048) → SUPPORTS CLAIM *(diagnostic-grade)*
- **Long side (representative, side=low):** obs mean **+0.0320** R (n=399) vs **β/regime-matched null mean −0.139** → p=**0.00695**, Wilson CI [0.0058,0.0081] (no α-straddle), **Holm adj p=0.0417 (< 0.05)**.
- **Unstratified (calibration-VALIDATED) anchor:** p=**0.0046**, null mean −0.150 — agrees and is even stronger.
- **Short side (mirror, side=high):** obs −0.136 (n=437), p=0.0126 — beats its (very negative) null but is itself unprofitable ("survives null" ≠ "profitable").
- **Reading:** on the research segment the long-sweep expectancy significantly exceeds a session×vol×trend-matched null (and the validated unstratified null agrees) → the sweep's *timing* carries information beyond direction/regime/gold-beta. **BUT** this is (a) **diagnostic-grade** (the stratified null is not separately calibration-validated), (b) a **small** effect (+0.032R), (c) **OOS expectancy is negative (−0.061, n=106)**, and (d) marginal after correction (adj p=0.042). **This is NOT evidence of a durable tradable edge** — only that the sweep timing is not pure beta within research. **Not promotable.**

### EXP-04 — Opening-range: alpha or beta? (S5, HGv1-049) → WEAKENS CLAIM
- **Long side (representative, side=up):** obs mean +0.0756 R (n=406) vs **β/regime-matched null mean +0.019** → p=**0.177** (NOT significant), Holm adj p=0.532.
- **Unstratified anchor:** p=0.034, null mean −0.052 — i.e. opening-range *does* beat a NON-regime-matched null, but **once the null is matched on NY-session×vol×trend the null itself earns +0.019** and the excess is no longer significant.
- **Short side (mirror, side=down):** obs −0.165 (n=373), p=0.406 — losing, does not survive.
- **Reading:** the opening-range "edge" is **substantially explained by regime/beta** — regime-matched random entries already earn most of it. This WEAKENS the timing-alpha claim for opening-range; **I7 (beta confound) STANDS for P003.** (OOS exp = +0.237, n=125 — positive, but being long in a continued trending NY window is again consistent with beta, not a refutation of the beta finding.) This is the single most informative negative of Wave 1.

### EXP-05 — Does the sweep LEVEL matter? (S1 placebo, HGv1-050) → NO DIFFERENCE DETECTED
- real exp **+0.032** (n=399) vs **level-label-shuffle** mean **−0.038** (K=500). p = P(shuffled≥real) = **0.118** (adj 0.471); lower-tail p_low=0.884.
- **Placebo integrity:** freq-ratio **0.995** (shuffled median n=397 vs real 399) — frequency/geometry preserved essentially perfectly; identity destroyed.
- **Reading:** the real liquidity level out-performs the shuffled level (real > 88% of shuffles) but **not at the family-wise bar** → NO DIFFERENCE DETECTED. Suggestive-but-inconclusive that the level identity matters; it is **not** shown spurious (p_low high). Well-behaved negative control.

### EXP-06 — Does the prior-day level matter for the fade? (S2 placebo, HGv1-051) → NO DIFFERENCE DETECTED
- real exp **+0.019** (n=272) vs shuffle mean **−0.034** (K=500). p=**0.238** (adj 0.532); p_low=0.764; freq-ratio **1.07**.
- **Reading:** same pattern — real above shuffle (beats 76%) but not significant → NO DIFFERENCE DETECTED. Suggestive-but-inconclusive; not spurious.

---

## 2. Cross-experiment synthesis
1. **Mechanism ingredients (EXP-01/02) are not shown to carry their edges at the Wave-1 bar.** Confirmation and the efficiency gate both give positive-leaning point estimates whose CIs straddle zero; neither survives Holm. The named KG "IMPROVED_BY" edges are **unsupported** (not refuted) by Wave 1.
2. **The beta diagnostics separate two primitives.** The **sweep (P001)** carries information beyond beta on research (diagnostic-grade, marginal, negative OOS → not tradable); the **opening-range (P003)** is largely **beta/regime** → I7 stands for it. This is a genuine, decision-relevant distinction between the lab's two strongest positive families.
3. **The placebos are inconclusive but well-constructed** (frequency preserved to within 0.5–7%). The level identity is neither confirmed nor refuted for either primitive; both lean weakly positive.
4. **Only EXP-03 crosses the family-wise bar, and it is diagnostic-grade with negative OOS.** Wave 1 therefore yields **no promotable alpha** and **no confirmed mechanism** — its value is the map of *which* claims survive and which don't.

## 3. Limitations (carried into every claim above)
- **EXP-03/04 primary null is STRATIFIED and NOT separately calibration-validated** → those two are DIAGNOSTIC-grade; the validated unstratified anchor is reported alongside (and disagrees for EXP-04, which is the whole point of matching on regime).
- **Representatives are single-direction**; the opposite side is reported as a mirror arm, not pooled.
- **EXP-01 primary bundles confirmation's timing components** (delay+price+exposure); the selection component is reported separately. No single-cause claim is made.
- **Holding time / exposure is not measured** (frozen engine returns R,si,ei only).
- **Placebo residual identity:** a donor day may occasionally carry a coincidentally-similar level; this can only *weaken* a positive placebo, never inflate it.
- **Research-segment only. Holdout SEALED. Global S1–S51 FDR NOT run. No parameter tuning, no post-hoc arm selection.**
- **Frozen-engine note:** `matched_null.matched_null_p` crashes on a multi-column strata list (latent bug, never hit by the pilot); worked around via a single composite `strat_combo` column without modifying the frozen module. Flagged for a future engine fix.

## 4. Claims supported / weakened / contradicted (for the Knowledge-Graph proposal)
- **Supported (diagnostic-grade, research-only):** sweep timing (P001) is not pure gold-beta — EXP-03.
- **Weakened:** opening-range (P003) as timing-alpha — largely beta/regime (EXP-04); I7 stands for P003.
- **Neither supported nor refuted (inconclusive):** confirmation carries the S1 edge (EXP-01); efficiency gate carries S39's edge (EXP-02); the sweep level identity (EXP-05); the fade level identity (EXP-06).
- **Contradicted:** none (no experiment produced a significant reverse effect).

See `WAVE_1_KNOWLEDGE_UPDATE_PROPOSAL.md` for the exact proposed node/edge edits (NOT yet applied — CEO gate).
Artifacts: `results/experiments/wave1/{wave1_prereg.json, EXP-0X_result.json, WAVE_1_SUMMARY.parquet, wave1_summary.json, run.log}`.
