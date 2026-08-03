# RED TEAM — OPERATIONAL MODE, PHASE A · Batch RT-OPS-A-0001
### FIFO processing of the Candidate Queue
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mode:** continuous operational (no per-candidate wait)
**Queue:** `CANDIDATE_QUEUE.md` @ `alpha-automation-v1`. **Eligible (FIFO):** CAND-0001, CAND-0002, CAND-0003, CAND-0007. **Not processed (BLOCKED, missing reaction primitives):** CAND-0004, CAND-0005, CAND-0006. **Not in this batch's current set:** CAND-0008/0009/0010 (present in queue, not handed to this run).
**Per candidate:** (1) lookahead · (2) circularity · (3) duplicates · (4) distinct mechanism · (5) falsifiability · (6) logical consistency. No remedy proposed · policy not modified · no backtest · no data run. Verification = reading the frozen primitives + `git show | sha256sum` of every W10 source pin.

> Phase-A gate outcome only: **SURVIVED_RED_TEAM_A** or **REJECTED_RED_TEAM_A**. Warnings carried below are **Statistician-stage controls**, not phase-A rejections. Red Team does not ratify, promote, or run statistics.

---

## Cross-cutting verification (all four)

- **W10 grounding — RESOLVED and VERIFIED.** Every cited primitive now carries a cross-repo pin (repo/branch/commit + `source_hash`). Red Team recomputed each: **all match.**
  - `institutional_levels.py` @ `8edbf99` → `c284fa2c…` ✅ (CAND-0001, 0007)
  - `resample_ny.py` → `6c623737…` ✅ (CAND-0001)
  - `market_state.py` → `823cf66a…` ✅ (CAND-0002)
  - `imbalance_mechanics.py` → `45f8937e…` ✅ (CAND-0003, 0007)
  - `interactions.py` → `dafb4804…` ✅ (CAND-0007)
  This closes the RT-POLICY-A-0001 / W10 blocker for CAND-0001: grounding is now verifiable without co-location.
- **No MK-01/MK-02 contamination.** The F1 (D2 selection bias) and F2 (consumption cascade) defects from RT-CODE-A-0001 live in `market_structure.detect_swings/detect_breaks/label_structure` and `liquidity_mechanics`. Verified: `institutional_levels.py` and `imbalance_mechanics.py` import **only `Block`** from `market_structure` (an inert interval dataclass — not the defective logic); `market_state.py` and `interactions.py` import neither. **None of the four candidates inherits F1/F2.**

---

## CAND-0001 — PDH/PDL reaction (policy `PDH-PDL` v1.2)
1. **Lookahead — PASS.** Verified field-by-field against `institutional_levels.py` (RT-POLICY-A-0001 §T4): `available_idx`=current day's first bar (Q4), 17:00-NY DST anchor, D3_bis block reset, D7 first-touch consumption, `entry@next-open`.
2. **Circularity — PASS.** No self-overlap; measurement window is downstream (carry W-e010: measurement must start at entry, reuse no bar in `[available_idx, trigger]`).
3. **Duplicates — none.** Canonical MK-04 level reaction; no prior candidate is the same mechanism.
4. **Distinct — yes.**
5. **Falsifiable — PASS.** Precise mechanical rule; disconfirmable vs a matched null.
6. **Logical consistency — PASS.**
**Carry to Statistician:** W-sel (evaluate selection-corrected, 1-of-9; the 6/7-years figure is not evidence), W-conf (session-**and**-level/placebo-matched null), W-ovl (check the single highest-overlap type), W-e010.
**→ SURVIVED_RED_TEAM_A.**

## CAND-0002 — Compression→Expansion breakout (policy `COMPRESSION-EXPANSION-BREAKOUT` v1.1)
1. **Lookahead — PASS (verified in code).** `atr14` trailing rolling(14) on `prev_c`; `expansion[i]` uses `atr[i-1]` + bar i only (E010 verbatim); `compression[i]` uses trailing `[i-window+1, i]`, `is_valid` false until a full window exists — code comment "ZERO lookahead: nicio bară > i" confirmed by the slice bounds.
2. **Circularity — PASS.** Percentile self-includes bar i but is strictly causal; no measurement feedback.
3. **Duplicates — none.** Distinct family (volatility state transition).
4. **Distinct — yes.**
5. **Falsifiable — PASS.** First expansion bar after a compressed bar, enter next-open in displacement direction — testable/disconfirmable.
6. **Logical consistency — PASS.**
**Carry to Statistician:** **compression-anchoring definitional risk** — self-disclosed by the policy and by `market_state.py` (compression is the only un-anchored ratified primitive; the "ten-plausible-variants" risk is reduced-not-eliminated). Parameters are ratified and lookahead-safe, so the mechanism is DEFINED; the definitional arbitrariness is a standing interpretive condition, not a phase-A failure.
**→ SURVIVED_RED_TEAM_A.**

## CAND-0003 — FVG CE-50 reaction (policy `FVG-CE50-REACTION` v1.0)
1. **Lookahead — PASS (verified in code).** `detect_fvgs` sets `confirmed_idx=i+1` (Q1, mechanically forced — the 3-bar gap isn't known until i+1); `detect_fvg_reactions` and `detect_inverse_fvgs` scan strictly `range(confirmed_idx+1, block.end)`; `entry@next-open`. Nothing reads forward of the decision bar.
2. **Circularity — PASS.** Block-confined, consume-once, no measurement feedback.
3. **Duplicates — none.** Distinct family (MK-03 imbalance).
4. **Distinct — yes.**
5. **Falsifiable — PASS.** First CE-50 touch of an un-inverted FVG, enter next-open in gap polarity — disconfirmable.
6. **Logical consistency — PASS.** Invalidation via consumption (Q5), inversion (Q4), block boundary (Q2) is coherent and non-overlapping.
**→ SURVIVED_RED_TEAM_A.** Cleanest of the batch.

## CAND-0007 — PDH/PDL × FVG-CE50 direction-aligned confluence (policy `LEVEL-FVG-CONFLUENCE` v1.0)
1. **Lookahead — PASS (verified in code).** Three primitives each causal (above); `interactions.confluence` = same-bar element-wise AND; `interactions.dilate` default `after=0` = trailing-only. **Note (declared, not a defect):** the module *permits* `after>0` (which would be lookahead); the policy pins `after=0` fail-closed. Lookahead-safety therefore rests on honoring `after=0` — a **declared** hand-off constraint (W-dilate), not an undeclared one.
2. **Circularity — PASS.** Same-bar/trailing masks; no measurement feedback.
3. **Duplicates — DISTINCT, but a strict subset by construction.** The mechanism (co-occurrence + direction agreement) is neither CAND-0001 nor CAND-0003 — it is a *confirmation* hypothesis neither tests. **But every CAND-0007 trigger is also a CAND-0001 trigger AND a CAND-0003 trigger** (same-bar conjunction), so its event set is a subset of both. Not a duplicate; heavy designed overlap.
4. **Distinct — yes** (the interaction is the mechanism).
5. **Falsifiable — PASS, and specifically:** if confluence performs no better than CAND-0001-alone or CAND-0003-alone, the confirmation adds nothing. Clean disconfirming result.
6. **Logical consistency — PASS.** Direction-agreement (PDL support × bullish FVG → long; PDH resistance × bearish FVG → short) and disagreement→no-trade are coherent.
**Carry to Statistician:** **W-incr (mandatory) — test the confluence's *incremental* value against each constituent alone** (its triggers are a subset of both; the hypothesis is that requiring both beats requiring one — it must be tested against that null, not a random null); **W-dilate** (honor `after=0`).
**→ SURVIVED_RED_TEAM_A.**

---

## BATCH RESULT

| Candidate | Lookahead | Circularity | Duplicate | Distinct | Falsifiable | Logic | **Phase-A** |
|---|---|---|---|---|---|---|---|
| CAND-0001 | ✅ | ✅ | none | ✅ | ✅ | ✅ | **SURVIVED_RED_TEAM_A** |
| CAND-0002 | ✅ | ✅ | none | ✅ | ✅ | ✅ | **SURVIVED_RED_TEAM_A** |
| CAND-0003 | ✅ | ✅ | none | ✅ | ✅ | ✅ | **SURVIVED_RED_TEAM_A** |
| CAND-0007 | ✅ | ✅ | subset (distinct) | ✅ | ✅ | ✅ | **SURVIVED_RED_TEAM_A** |

**4 processed · 4 SURVIVED_RED_TEAM_A · 0 REJECTED.** No eligible candidate remains in this set (CAND-0004/0005/0006 BLOCKED and not processed; CAND-0008/0009/0010 not in the handed set). Loop idle.

All four are **Part A only**; every Part B is UNSPECIFIED by decision (standing structural-stop gap) → Statistician specification request, unchanged. Carried controls (W-sel, W-conf, W-ovl, W-e010, compression-anchoring, W-incr, W-dilate) are **Statistician-stage**, not phase-A blockers. Nothing ratified, promoted, modified, or run on data.

**Queue updated:** the four state cells set to SURVIVED_RED_TEAM_A. Handoff → Statistician (Part A) / Statistician spec request (Part B).
