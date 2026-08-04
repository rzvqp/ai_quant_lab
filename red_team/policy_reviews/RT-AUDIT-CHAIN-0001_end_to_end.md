# RED TEAM — END-TO-END CHAIN AUDIT · RT-AUDIT-CHAIN-0001
### The pipeline itself, Alpha → DEMO order — what accumulated unverified
**Date:** 2026-07-28 · **Auditor:** Red Team · **Mandate:** CEO — audit the CHAIN, not a candidate; find assumptions that propagated unattacked. **No data run · nothing modified · no remedy designed.**
**Method:** six parallel evidence sweeps across `ai_quant_lab` (statistician-foundation), `ai_quant_lab-alpha-automation` (alpha-automation-v1 + discovery-mk-matrix-v1), and the vendored ratified mirror; every code claim re-read at source by Red Team before ranking.

---

## 0. HEADLINE — does anything invalidate an existing result?

**The reassuring finding first: nothing has been promoted to a validated result, so there is almost nothing to invalidate — and the chain correctly FAIL-CLOSED before live.** The task's premise that "CAND-0001, 0007, 0019 run on the account" is **not supported by the artifacts:**
- **No `CAND-xxxx` policy has ever placed a live DEMO order.** `VE_CAND0001_DEMO_GATE_VERIFICATION_v1.0.md`: CAND-0001 "**NU tranzacționează pe DEMO**" — the Validation Engine BLOCKED it because Engine-v2 `mstrat.py::simulate` could not be shown to enforce S1/S2/S3. **The gate worked** (exactly the Red Team hard precondition). The only real DEMO order in the whole system (BTCUSD 0.01) came from a *different* pilot line (AI-Trader), not any CAND.
- Every candidate carrying the propagated assumptions is still **`SCREENING_BASELINE` — NOT STATISTICALLY VALIDATED.** DEMO is explicitly *not* validation. The 1,972 legacy hyps are PENDING; **no REJECTED verdict was issued while the p-engine was invalidated.**

**Two result-shaped items are already void, and already on record** (not new): (a) **DC-0004** — holdout consumed, post-2025-10-23 results are *not* independent confirmation (verdicts_ledger §SURVIVED); (b) **ALPHA_REGISTRY** `passed_stat`/`p` columns — built on the invalidated analytic p, stamped "STALE / NON-AUTHORITATIVE." Neither closes anything.

**One latent invalidator remains OPEN (W9):** the matched-null calibration exists in two contradictory states — RESOLVED on `flow-c-foundation`, still OPEN on the official `statistician-foundation`; the Validation Engine rebuilt a *less* complete version (F6, no drift-beta control). No promoted result rests on it **yet**, but it is the statistical engine that any future validation must run through, and it is unfixed on the official line.

---

## 1. SEVERITY-ORDERED FINDINGS

### 🔴 DEFECT (something is actually wrong)

**C-D1 · The dynamic-exit DEMO engine re-embeds Finding H′ (un-remediated) — CAND-0002 class.** *(Red-Team-verified at source.)*
`demo_gate_engine/dynamic_exit_engine.py:6-7,37,67` sets the time-stop to the **BLOCK boundary** (`day_end_idx` "granița de BLOC … n-1"). A block is a discovery-data construct → on a live forward account the block-boundary time-stop **never fires** — this is exactly **Finding H′** (raised as Finding H on CAND-0002 in RT-OPS-B-0002, sharpened on CAND-0011..0019). The session/persistent *policies* fixed this with live-valid horizons; **CAND-0002's Part B never was**, and the DEMO engine faithfully implements the un-remediated spec. Consequence: the DEMO/backtest exit discipline for the dynamic-exit family is **not live-faithful** (the time-stop that bounds the backtest cannot bound live). Contained only because nothing is live. The **same `DemoSignal.day_end_idx` field means the day boundary in `pdh_pdl_demo_engine.py:57` but the block boundary here** — a field with two meanings across two engines that share it.
*Severity: high among findings, but PRE-LIVE. It is the clearest case of an un-closed Red Team finding propagating into executable code.*

### 🟠 RISK (unverified surface / could go wrong)

**C-R1 · The S1/S2 gate engine — the code that enforces Red Team's own hard preconditions — was never attacked; only the Validation Engine self-verified it.** `demo_gate_engine/` was built 2026-07-30/Aug-3, **after** the ledger closed at [28] (2026-07-27). Six Red Team verdicts ([19][21][22][26][27][28]) made S1 worst-case order + S2 floor HARD pre-DEMO conditions; the module that implements them has had **zero independent adversarial review**. This is a **self-verification loop**: the Validation Engine builds candidates, builds the gate that must constrain them, and verifies its own gate. *(I did read `pdh_pdl_demo_engine.py` in this audit and found it clean — day-boundary time-stop live-valid, S1/S2/S3 present — but a spot-read is not the depth of attack that found W11/W12 in market_structure.)* **Highest-value structural gap.**

**C-R2 · The entire statistical stack is never code-attacked, and W9 (a HIGH-severity defect on that exact surface) is still OPEN on the official line.** `matched_null.py`, `mn_adversarial.py`, `mn_calibration.py`, `pilot_pvalue.py`, `scoped_fdr_run.py`, `synth_price.py`, `wp5_null_generator.py` — zero adversarial coverage. Red Team touched matched-null only as a *branch-state* integrity note (W9, "implementation NOT read"). W9 shows this surface already carried defect D3 (matched-null miscalibration) living in two contradictory branch states, and the official `statistician-foundation` still has it OPEN. Every batch review *defers* to "BH-FDR valid" — that implementation is unaudited. **This is the machinery that decides whether anything is real.**

**C-R3 · `mstrat.py::simulate` — the engine that produced EVERY emitted candidate metric — enforces none of S1/S2/S3 and was never attacked.** `demo_gate_engine/README.md` (report `13c0f41`) states it enforces no gates and is left "neatins." So every SCREENING number in the pipeline is a **pre-gate** measurement. Bounded (they are SCREENING, not validated), but it means no emitted expectancy has ever been through the safety model.

**C-R4 · The data/context derivation is never audited, yet every lookahead proof assumes it.** `resample_ny.py` (17:00-NY `day_index` anchor — only sha-pinned, never opened), `build_gc_bars.py`, `quality_and_resample.py`, `generate_htf_context.py` (M15_v2 context), and block *construction* (the `Block` all primitives import as "inert" — its import was checked, its *construction* never). A defect here (there is a documented `VERIFY_M15_v1_DEFECTIVE` history) would silently void the causal-safety verdicts in [16]/[19]/[25].

**C-R5 · 6 of 9 ratified primitives are hash-pinned only, never code-attacked.** `institutional_levels.py`, `imbalance_mechanics.py`, `market_state.py`, `interactions.py`, `order_block_void.py`, `order_flow.py` passed only W10 sha256 + inert-`Block` contamination checks. `market_structure.py` — the one primitive given a *deep* attack — yielded **two real defects (W11 selective-D2, W12 cascade)**. By symmetry these six are unexamined surfaces of equal weight; `institutional_levels.py` underpins the entire PDH/PDL/weekly line including CAND-0001 (the DEMO pilot), and `market_state.atr14` underpins every S2 floor and every ATR-proximity filter.

**C-R6 · `trading_strategies.py` — never attacked, despite Red Team's own [24] flagging it as the decisive open hole.** RT-CODE-A-0003 wrote "verify first-reference stability against `trading_strategies.py` (s2/s3/s10/s11) before relying on 'timing-only'" — then it never happened. A Red-Team-identified open item pointing straight at an unattacked module that consumes the cascade-break fix.

**C-R7 · `dynamic_exit_engine.py:71` reads `open_[j+1]` on an undeclared precondition (F3-class).** Safe under the intended contract (the boundary guard makes `j+1 ≤ scan_end`, and the caller must set `day_end_idx ≤ n-1`), but there is **no internal assertion** — the same shape as the F3 undeclared-ordering-precondition defect. Latent, not live. *(Verified by Red Team; the parallel "dropped target guard" claim was checked and is NOT a defect — a dynamic-event exit has no target price to guard.)*

**C-R8 · Feed-alignment ~3h magnitude is unmeasurable in-repo.** No MT5 data exists ("MT5 integration — nothing exists. Not authorized"). Correctly disclosed as "carried, not repaired" on all 11 session/persistent policies — an irreducible transferability RISK, not a defect, but it will remain an assumption until an external feed exists.

### 🟡 UNDOCUMENTED / hygiene (not wrong, but misleading or drifting)

**C-U1 · Queue labels overstate chain readiness.** `DEMO_BASELINE` sits on CAND-0001/0002/0003/0007/0009 and reads as "live-ready," but **none is live**, CAND-0001 is BLOCKED, and **CAND-0009 carries `DEMO_BASELINE` with NO DEMO-criteria doc at all.** The live-design doc (`MULTI_POLICY_LIVE_DESIGN.md`) names **CAND-0019 in the intended live set, but it exists only as a SCREENING queue row with no policy artifact.** A reader of the queue would over-estimate how far the chain has progressed.

**C-U2 · DEMO-criteria coverage is uneven and undocumented as such.** Dedicated for CAND-0001; **inherited verbatim via a batch doc** for 0002/0003/0007 (`STAT-BATCH-B-0002`); **none** for 0009 (despite the label) or 0019 (never reached the stage). No single roster states which candidates are gate-bound.

**C-U3 · Stale v1 policies with the inert block-boundary time-stop are still on disk.** `POLICY_OB_MITIGATION_v1.md` retains `measurement_end = min(event_idx+GROUP_A_HORIZON, block_end)` — the exact Finding-H′ pattern that the v3 policies dropped. Not consumed if only v3 is live, but the defective spec coexists on disk with its fix.

**C-U4 · Convention namespace collisions.** (i) **Q4/Q5/Q6 mean different things in different ratified modules** — `Q4` = "first-bar availability" in MK-04 (`institutional_levels.py:28`) but "inverted-FVG close-through" in MK-03 (`imbalance_mechanics.py:21`); only Q5 aligns. (ii) `DemoSignal.day_end_idx` = day boundary in one engine, block boundary in the other (see C-D1). (iii) `ATR_WINDOW=14` defined independently in `market_scanner/config.py` and `market_state.py` — both 14, silently divergeable. Cross-module reasoning that cites a bare label is ambiguous.

**C-U5 · Non-single-valued horizon convention.** "Session level" uses the **session boundary** in Primitive-A but the **20-bar `GROUP_A_HORIZON`** in Primitive-B; CAND-0009 uses **14 bars** where its level-family siblings use 20 or the day boundary. Each is internally justified as "the structure's native horizon," but "the ratified horizon" is not single-valued — a documentation/consistency risk.

**C-U6 · The D2/F1 vs equal-high-liquidity tension is carried unresolved, and a KB strategy targets exactly what the detector is blind to.** MK-01's strict-inequality D2 means equal highs/lows never become swings, so `build_pools` can never emit an equal-high pool — yet `knowledge/strategies/S21_equal_highs_lows_liquidity_pool_raid` trades precisely equal-high/low liquidity. Documented (F1/W11) as "not circumvented, not compensated," but any MK-02 output understates equal-high liquidity by construction, and S21 is provably unreachable through the ratified pipeline.

**C-U7 · Legacy-428 `ZERO_ALPHA_BASE_RATE` conflates insufficient-n with measured-negative.** The 367-hyp REJECTED bucket uses an AND-screen that includes `n≥25`, so an underpowered hypothesis and a truly-negative one share one label — the clean negative/insufficient split the MK triage draws is *not* drawn here. Disclosed as descriptive/non-final, so bounded, but it is the one place "insufficient treated as negative" survives.

**C-U8 · `RED_TEAM_STATE.md` resume doc is 15 entries stale** (says "next entry [13]"; the ledger is at [28]). The division's own resume artifact would mislead a fresh session.

---

## 2. WHAT IS CLEAN (verified — stated so the audit is honest)

- **MK triage (Target 5): sound.** Five archived-negative candidates each have real n (7k–34k) and uniformly negative expectancy; the one sub-threshold candidate (CAND-0023, n=7) was correctly **rescued** as insufficient, not archived. Two-ledger governance (family vs exploration) correctly applied. **No candidate was archived as "negative" that actually had insufficient n.**
- **Invalid analytic p (Target 5): not load-bearing.** Retracted before any rejection; the only artifact carrying it is stamped stale/non-authoritative. No closure rests on it.
- **C5 "contamination" (Target 4): premise mis-stated; path ratified discovery-safe.** There is no Statistician "C5 holdout register." The M15_v2→H1/H4 derivation is in-sample vs discovery but **provably never touches the sealed holdout** (fail-closed construction) and was **ratified discovery-safe**; the real leak (native-H1 path) was caught and fixed. **The DEMO candidates consume no H1/H4 bias at all → C5 is inert for them.** It reaches only research hypotheses/legacy code, none on DEMO.
- **S2 `min_executable_risk` (Target 1): consistent** — identical formula/constants at all 7+ citations.
- **Q4 availability semantics (Target 1): consistent** for day/session/week (only the *label* Q4 collides across modules, C-U4).
- **PDH/PDL DEMO engine (CAND-0001): gate code clean** — live-valid day-boundary time-stop, S1/S2/S3 all present.
- **The chain fail-closed before live** — the single most important structural fact of the audit.

---

## 3. NEVER-ATTACKED INVENTORY (Target 6, consolidated)

| Component | Path | Status | Why it matters |
|---|---|---|---|
| DEMO gate engine | `demo_gate_engine/pdh_pdl_demo_engine.py`, `dynamic_exit_engine.py` | **never attacked** (VE self-verified only) | enforces S1/S2 that six verdicts made hard; one variant re-embeds H′ (C-D1) |
| Statistical stack | `matched_null.py`, `mn_*.py`, `pilot_pvalue.py`, `scoped_fdr_run.py`, `synth_price.py`, `wp5_null_generator.py` | **never attacked** | decides significance; W9 defect still open here |
| Research engine | `mstrat.py`, `mstrat_ext.py`, `mtf.py`, `run_prod.py`, `campaign.py` | **never attacked** | produced every candidate metric; enforces no gates |
| Data/context derivation | `resample_ny.py`, `build_gc_bars.py`, `quality_and_resample.py`, `generate_htf_context.py`, `ai_trader/context_memory/*` | **never attacked** | every lookahead proof assumes these correct |
| `trading_strategies.py` | `discovery-mk-matrix-v1:code/` | **never attacked** | Red Team's own [24] flagged it and didn't follow through |
| 6 ratified primitives | `institutional_levels / imbalance_mechanics / market_state / interactions / order_block_void / order_flow` | **hash-pinned only** | the deeply-attacked 7th (market_structure) yielded W11+W12 |

**Fully attacked (code):** `market_structure.py`, `liquidity_mechanics.py`, `session_levels.py`. **Attacked (policy only):** CAND-0001..0036 family + PDH/PDL v1.1/v2.

---

## 4. VERDICT

**No existing *validated* result is invalidated — because none exists yet; the chain fail-closed before live, correctly.** The accumulated-unverified mass is concentrated at the two ends the divisions built for themselves and Red Team never saw: **the enforcement code (`demo_gate_engine/`) and the validation code (`matched_null`/`pilot_pvalue`/`scoped_fdr`)** — the components that respectively *enforce* Red Team's preconditions and *decide truth*. One of them (the dynamic-exit engine) already re-embeds an un-closed finding (H′, C-D1); the other still carries an open HIGH-severity defect on the official line (W9). Everything measured in between is SCREENING, pre-gate, and honestly labelled as such — the discipline held where Red Team looked; the risk is what Red Team was never pointed at.

**Priority order for the CEO/Statistician (risk, not remedy — Red Team designs neither):**
1. **C-R1/C-D1** — the DEMO gate engine (esp. the dynamic-exit block-boundary time-stop) needs an independent attack before any live wiring; it is currently self-verified and re-embeds H′.
2. **C-R2 + W9** — resolve the two-state matched-null on the official line and attack the statistical stack before any candidate is validated.
3. **C-R3/C-R4/C-R5** — `mstrat.py::simulate`, the data/context derivation, and the 6 hash-pinned primitives are unexamined load-bearing surfaces.
4. **C-U1/C-U2** — correct the labels so `DEMO_BASELINE` and the live-design roster stop overstating readiness.
5. **C-R6, C-U3..U8** — the self-identified `trading_strategies.py` hole; the namespace/horizon/label drifts; the stale docs.

Nothing modified, nothing run on data, no remedy designed. Handoff → **Statistician**, for protocol / prioritisation.
