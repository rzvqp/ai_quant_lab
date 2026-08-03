# RED TEAM — OPERATIONAL MODE, PHASE A · Batch RT-OPS-A-0002
### FIFO processing — CAND-0008, CAND-0009, CAND-0010
**Date:** 2026-07-25 · **Auditor:** Red Team · **Mode:** continuous operational
**Policies @ commit `32236fd`, `alpha-automation-v1`:** `POLICY_VOID_DISPLACEMENT_v1.md` (CAND-0008), `POLICY_LEVEL_BREAK_DRIVE_v1.md` (CAND-0009), `POLICY_FVG_STACK_DENSITY_v1.md` (CAND-0010).
**Attack: PART A only** (all three Part B UNSPECIFIED — not attacked). Six dimensions each: W10-hash verify · lookahead · circularity · duplicate/subset · distinct · falsifiable, plus the **MK-01/MK-02 contamination** control. No data run · policies not modified · no remedy.

> Phase-A gate: **SURVIVED_RED_TEAM_A** / **REJECTED_RED_TEAM_A**. Carried warnings are Statistician-stage controls.

---

## Cross-cutting verification (all three)

- **W10 hashes — recomputed, all MATCH:** `order_block_void.py` `6ec7adbf…` ✅ (new this batch); `institutional_levels.py` `c284fa2c…`, `market_state.py` `823cf66a…`, `imbalance_mechanics.py` `45f8937e…`, `interactions.py` `dafb4804…` ✅ (re-confirmed from RT-OPS-A-0001).
- **MK-01/MK-02 contamination — checked per cited primitive (imports read at `8edbf99`):** `order_block_void`, `market_state`, `interactions` import **neither** MK-01 nor MK-02. `imbalance_mechanics` and `institutional_levels` import **only `Block`** from `market_structure` — the inert interval dataclass, **not** the F1/F2-defective `detect_swings`/`detect_breaks`/`label_structure`. **None of CAND-0008/0009/0010 inherits F1 (D2 selection bias) or F2 (consumption cascade).**
- **New primitives verified causal in code:** `detect_liquidity_voids` (void on transition `c→c+1` from `time[c]`, `time[c+1]`, `open[c+1]`, `close[c]` — all known at `c+1`); `price_in_any_zone` (pure element-wise membership, no cross-bar/future).

---

## CAND-0008 — Void × Displacement (`VOID-DISPLACEMENT` v1.0)
1. **Lookahead — PASS (code-verified).** Void known at `c+1`; `expansion[c+1]` uses `atr[c]` + bar `c+1` only; `entry@next-open` (`c+2`). Nothing reads past the decision bar.
2. **Circularity — PASS.** Trigger uses void(`c`) + displacement(`c+1`); measurement from entry (`c+2`) forward — selection and measurement disjoint.
3. **Duplicate/subset — none.** Distinct from CAND-0004 (void *alone*, not currently testable — no trigger) and CAND-0002 (compression, a volatility state, not a discontinuity). The trigger (immediate displacement on the void's downstream bar) is what makes it both testable and a *different* mechanism.
4. **Distinct — yes** (a driven gap, not merely a gap).
5. **Falsifiable — PASS.** Void's downstream bar is a displacement → gap-and-go continuation; disconfirmable vs a null.
6. **Logic — PASS.** Maintenance-window pseudo-gaps excluded by the ratified void definition (not re-handled — correct).
*Note (ratified, not a policy defect):* the void's size term is a fixed absolute `$1.20` (`VOID_SIZE_THRESHOLD`, ratified) — an instrument-scale-specific constant; a standing characteristic, not chosen by the policy.
**→ SURVIVED_RED_TEAM_A.** Cleanest of the batch.

## CAND-0009 — Level-Break-Drive (`LEVEL-BREAK-DRIVE` v1.0)
1. **Lookahead — PASS (code-verified).** Level `available_idx`=current day's first bar; `expansion[i]` uses `atr[i-1]`+bar `i`; `confluence` same-bar; `entry@next-open`.
2. **Circularity — PASS.** Same-bar confluence; measurement downstream.
3. **Duplicate/subset — DISTINCT, but a one-sided boundary with CAND-0001 (finding W-partition).** CAND-0009 = PDH/PDL touch **coincident with a displacement through** the level → continuation (PDH break→long). CAND-0001 = touch → reversal (PDH→short). Different mechanism, opposite thesis — **not** a duplicate. **But the two overlap on displacement-touch bars, and there they take OPPOSITE positions.** The partition is **asymmetric**: CAND-0009 cleanly *excludes* the reversal case (no trade if displacement contradicts a break), yet **CAND-0001 does NOT exclude the break case** — CAND-0001 still fires its reversal short on the very bar CAND-0009 fires its break long. Not a phase-A failure of CAND-0009 (which is self-consistent), but the CAND-0001↔CAND-0009 boundary is one-sided.
4. **Distinct — yes.**
5. **Falsifiable — PASS.**
6. **Logic — PASS** (self-side exclusion coherent). *Minor precision note:* the trigger prose requires a **direction-aligned** displacement (PDH+bullish, PDL+bearish), but the mask expression is written `confluence([level_touch_mask, expansion_mask])` without splitting `expansion` by direction — the intent is clear and implementable (direction-aligned masks, as CAND-0007 does explicitly), but the expression under-specifies it. Not a defect; a precision item.
**Carry to Statistician:** **W-partition** — decide whether CAND-0001 must exclude displacement-touch bars so the two candidates are mutually exclusive (else CAND-0001 systematically takes the losing reversal side on breaks). **W-dir-mask** — make the confluence expression direction-aligned.
**→ SURVIVED_RED_TEAM_A.**

## CAND-0010 — FVG-Stack-Density (`FVG-STACK-DENSITY` v1.0)
1. **Lookahead — PASS (code-verified).** FVGs `confirmed_idx=i+1`; the "other" zones are restricted to **confirmed** ones (`confirmed_idx ≤` current bar); `price_in_any_zone` causal; `confluence` same-bar; `entry@next-open`.
2. **Circularity — PASS.** Same-bar; measurement downstream.
3. **Duplicate/subset — DISTINCT, but a strict SUBSET of CAND-0003 (finding W-incr).** Distinct from CAND-0003 (single-FVG CE-50) and CAND-0005 (BPR = *opposite*-polarity overlap, and currently blocked). CAND-0010 = same-polarity FVG **stack**: a CE-50 reaction whose price also sits inside ≥1 other same-polarity FVG. **But every CAND-0010 trigger is also a CAND-0003 CE-50 reaction** plus the density condition → its event set is a subset of CAND-0003 (same pattern as CAND-0007 ⊂ CAND-0001∩CAND-0003). Distinct hypothesis (density adds information?), heavy designed overlap.
4. **Distinct — yes** (imbalance density).
5. **Falsifiable — PASS, specifically:** if stacked FVGs perform no better than a single FVG, density adds nothing.
6. **Logic — PASS** (excludes single-FVG and opposite-polarity cases).
**Carry to Statistician:** **W-incr** — test the density condition's **incremental** value against CAND-0003 single-FVG (its triggers are a subset; the hypothesis must be tested against the single-FVG null, not a random null).
**→ SURVIVED_RED_TEAM_A.**

---

## BATCH RESULT

| Candidate | W10 hash | Lookahead | Circular. | Duplicate | Distinct | Falsifiable | MK-01/02 | **Phase-A** |
|---|---|---|---|---|---|---|---|---|
| CAND-0008 | ✅ | ✅ | ✅ | none | ✅ | ✅ | clean | **SURVIVED_RED_TEAM_A** |
| CAND-0009 | ✅ | ✅ | ✅ | one-sided vs CAND-0001 | ✅ | ✅ | clean | **SURVIVED_RED_TEAM_A** |
| CAND-0010 | ✅ | ✅ | ✅ | subset of CAND-0003 | ✅ | ✅ | clean | **SURVIVED_RED_TEAM_A** |

**3 processed · 3 SURVIVED_RED_TEAM_A · 0 REJECTED.** Carried controls (W-partition, W-dir-mask, W-incr) are Statistician-stage, not phase-A blockers. All Part B UNSPECIFIED → Statistician spec request, unchanged. Nothing ratified, promoted, modified, or run on data.

**Queue idle after this batch** (Alpha entered WAITING_FOR_NEW_PRIMITIVES after CAND-0010). Pending Phase B on CAND-0002/0003/0007 when Alpha publishes their Part B.
