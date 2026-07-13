# WAVE 1 — controls, beta diagnostics, high-information mechanism experiments (FROZEN SPEC)

Wave 1 builds the two shared harnesses (matched-null control + level-label shuffle) and runs the highest-
information / control experiments. **Frozen before any execution; no post-hoc interpretation.** Nothing here is
implemented or run — this is the plan. All experiments reuse EXISTING S1–S51 family setups (no new primitive);
research = first 60% M15, OOS = next 20%, holdout SEALED. Min trades = 30 unless stated. Primary metric = mean
expectancy (R/trade); secondary = PF, maxDD(R), pos-month share, top-1 share, OOS expectancy.

Predeclared multiplicity: Wave 1's PRIMARY contrasts are the treatment-vs-matched-control differences below;
all else is secondary/diagnostic. Family-wise control applied across the whole 10-experiment plan (see PRIORITY_MATRIX).

---

## EXP-01 (type B, mechanism) — Confirmation contribution in liquidity sweeps  [HGv1-042, resolves C1]
- **Research question:** Does the confirmation stage account for the S1 edge, holding the sweep event fixed?
- **H0:** confirmed-sweep expectancy ≤ raw-sweep expectancy on the identical signal set.
- **H1:** confirmed > raw by a pre-specified margin.
- **Base strategy:** S1 confirmed sweep. **Treatment vs control:** SAME sweep events (S21 raw signal set),
  arm A = enter raw (no confirmation), arm B = enter only after confirmation — PAIRED, identical universe/sample.
- **Held constant:** instrument, sweep definition, level source, exits, costs, overlap, sample.
- **Possible outcomes / interpretation:** (i) B≫A → confirmation carries the edge (update P001↑, P011 explains raw,
  I2 supported). (ii) B≈A → confirmation is not the differentiator (I2 weakened; look elsewhere). (iii) both ≤0 →
  S1's earlier positive was sample/level-specific.
- **KG updated:** P001, P011, I1, I2, edge P001-IMPROVED_BY-confirmation.
- **Stopping rule:** fixed B (matched-null); report p-CI; UNRESOLVED if CI straddles the pre-set margin.
- **Implementation:** S (reuse S1/S21 setups + paired comparator on the matched-null harness).

## EXP-02 (type B, mechanism) — Efficiency-gate contribution in continuation  [HGv1-043, resolves C2]
- **Research question:** Does the trend-efficiency gate account for S39's edge vs generic continuation?
- **H0/H1:** gated-continuation expectancy ≤ / > gate-OFF continuation on the same signal set.
- **Base:** S39. **Treatment vs control:** gate-ON (er≥0.5) vs gate-OFF (all trends) arm, same universe.
- **Held constant:** continuation definition, exits, costs, sample.
- **Outcomes:** ON≫OFF → efficiency is the active ingredient (P005↑, I1 supported); ON≈OFF → S39 was a fluke of
  the specific threshold (P005 weakened, flag as tuning). 
- **KG updated:** P005, P012, I1; edge P005-IMPROVED_BY-efficiency_gate.
- **Implementation:** S–M (reuse S39; expose a gate-off arm).

## EXP-03 (type D, beta diagnostic) — Is the sweep edge timing-alpha or gold beta?  [HGv1-048]
- **Research question:** Does the S1 sweep edge survive a beta/regime-matched null and on the short side?
- **H0:** sweep expectancy ≤ its beta/regime-matched-null expectancy (i.e., explained by drift/beta).
- **Treatment vs control:** observed sweep vs a null matched on direction, regime, session, and realized
  gold trend exposure (beta-residualized). Report long and short arms separately.
- **Outcomes:** survives matched null on both sides → timing-alpha (I7 partially resolved for this primitive);
  fails → consistent with beta (P001 CONSISTENT_WITH_BETA↑, I7 stands).
- **KG updated:** P001, I7. **Implementation:** M (reuse sweep + the generic beta/regime-matching pipeline).

## EXP-04 (type D, beta diagnostic) — Opening-range: alpha or beta?  [HGv1-049]
- Same design as EXP-03 for **S5 opening-range** (P003). H0: expectancy ≤ beta/regime-matched null.
- **Outcomes:** survives → P003 timing-alpha (strongest current candidate confirmed non-beta); fails → beta.
- **KG updated:** P003, I7. **Implementation:** M (reuse S5 + shared matching pipeline).

## EXP-05 (type E, placebo / negative control) — Does the sweep LEVEL matter?  [HGv1-050]
- **Research question:** Is the confirmed-sweep edge driven by the real liquidity level, or by local structure
  independent of the level identity?
- **H0 (placebo):** performance with RANDOMIZED level labels ≈ performance with real levels.
- **Treatment vs control:** real levels vs a level-label shuffle (preserve local price structure, permute WHICH
  level is "the" reference). **Freeze the shuffle rule + failure threshold BEFORE inspecting any alpha result.**
- **Outcomes:** real ≫ shuffled → the level is the mechanism (P001/P010/I8 supported); real ≈ shuffled → the
  "liquidity level" is a spurious label (P001 downgraded — a key negative-control result).
- **KG updated:** P001, P010, I1, I8. **Implementation:** L (build the reusable label-shuffle harness here).

## EXP-06 (type E, placebo / negative control) — Does the prior-day LEVEL matter for the fade?  [HGv1-051]
- Same label-shuffle placebo for **S2 failed-breakout fade** (P002). H0: shuffled ≈ real.
- **Outcomes:** real ≫ shuffled → structural level is the mechanism (P002/I8 supported); else P002 downgraded.
- **KG updated:** P002, I8. **Implementation:** S (plug S2 into the EXP-05 harness).

## Wave-1 dependencies
EXP-01/02 (mechanism) and EXP-03/04 (beta) are independent and can run in parallel. EXP-05 builds the shuffle
harness that EXP-06 reuses. The placebo randomization rules must be frozen before Wave-3 alpha results are read.
