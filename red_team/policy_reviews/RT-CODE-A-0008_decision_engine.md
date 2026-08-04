# RED TEAM — CODE ATTACK · Decision engine (level 6)
### RT-CODE-A-0008 · Target: `decision_engine/decision_engine.py` @ `bdd15e5` (alpha-automation-v1)
**Date:** 2026-08-01 · **Auditor:** Red Team · **Spec:** STAT-DECISION-ENGINE-SPEC-v1.0 (`ccb31d9`, manifest v2.7.47). First new piece of the CEO's target architecture; level 6, step 3 of 4 (awaiting CEO approval). **No data run · engine not modified · no remedy designed.** Numeric verification used synthetic counts only (pure math, engine imported read-only).

## HEADLINE — the engine SURVIVES: the math is sound (Beta ppf verified, n=0 gate-repair works, k handled, three-outcome correction applied, fail-closed named). The 80% gate is REAL but LENIENT — not decor, but mostly inert for the thousands-of-trades candidates; its teeth are at the post-DEMO 95%. The genuine exposure is NOT the arithmetic but the THREE caller-boundary trusts the pure function cannot police.

---

## OWN TARGETS — numerically verified at source

**Beta quantile (`_beta_ppf`, hand-rolled, no scipy) — VERIFIED CORRECT, tails included.**
- Exact on closed forms: Beta(1,1)→ppf(q)=q; Beta(2,1)→ppf(0.2)=0.447214; Beta(1,2)→0.105573; arcsine Beta(.5,.5)→0.095492. All match to 1e-6.
- Round-trip `CDF(ppf(q))=q` holds for realistic α,β across the tails — Beta(0.5,50), (50,0.5), (2,500), (500,2), (900,600) at q∈{0.001,0.2,0.999}: all correct. The `_betai` Numerical-Recipes continued fraction + the x<(a+1)/(a+b+2) tail switch is faithful; bisection (200 iters) inverts to machine precision.
- The **only** round-trip "mismatches" are at α or β ≤ 1e-3 (Beta(1e-6,·), Beta(ε,ε)) — the **n=0 regime**. There the ppf returns ≈0 (e.g. `3.11e-61`), which **is the correct quantile** for a distribution whose mass is ~all at {0,1}; the round-trip metric is uninformative because the CDF is near-vertical at 0. **Gate impact: none — a new setup's `p_t_lcb≈0` correctly fail-closes.** (Audit-value note: D-U4.)

**`k` moment estimate — cannot return negative; handled conservatively.** `_estimate_k` clamps `min(max(k,0),K_MAX)` (`:193`). Verified: extreme-split (over-dispersed) siblings → **k=0** (no shrinkage, wide interval — the conservative direction, not a crash); homogeneous → K_MAX; `<2` siblings → 0. Over-dispersion (`σ²_between>m(1−m)` ⇒ raw k<0) → clamped to 0; under-dispersion (`σ²_between≤0`) → K_MAX. No negative k reaches the posterior.

**n=0 contraction repair — works for the GATE in all cases; one AUDIT residual.** Verified: μ_parent=0.40, n=0 → `p_t_hat = 0.400000` **exactly the parent** (the `k_eff=max(k,1e-6)` floor preserves the α:β=μ:(1−μ) ratio, so k cancels at n=0). The repair is real. **Residual (D-U2):** in the **μ=0 corner** (parent target-rate exactly 0) at n=0, `p_t_hat` still degenerates to **0.5** — the *old bug's value* — surfacing in the `ev_point` audit field. **The gate is safe** (`p_t_lcb = 3.11e-61 ≈ 0 → ev_lcb = −1.0 → enter=False`, verified via `decide()`), but the point estimate is misleading and this corner is **untested** (the n=0 test uses μ=0.40).

## VE-LEFT TARGET 1 — "EV_LCB at 80%: a GATE or a FORMALITY?" — **a REAL gate, but LENIENT; not decor.**
- It **does** block: thin history (n=10, p_t=0.4) → `ev_point>0` but `ev_lcb≤0` → NO_TRADE; rich history (n=1000, same ratio) → enters (tested, `test_lower_bound_gate…`). So it genuinely discriminates by evidence.
- **But at 80% it is soft.** The 0.2-quantile of a moderate-α+β Beta is ~1 SE below the mean — a mild haircut. For the current candidates (many with **thousands** of trades → narrow interval), `p_t_lcb ≈ p_t_hat`, so the gate is **near-equivalent to `EV_point>0`** — *almost nothing falls at 80% for high-n candidates.* Its real bite is on **new / low-n** setups. The spec itself anchors 80% to DEMO and tightens to **95%** afterward — so the teeth are deferred.
- **Sharper: the LCB is not fully pessimistic.** `ev_lcb` pessimizes **only `p_t`** (→ correspondingly more stop mass) **and cost**; `p_h` enters at its **point** estimate and `E[X|h]` at its point (`:298`). A setup with highly uncertain horizon outcomes gets **no** pessimism on that axis. So "the single pessimistic gate" is pessimistic on the target axis, not the whole EV.
- **Direct answer:** not a formality — it blocks under-evidenced setups — **but at 80% it is a lenient gate that is mostly inert for the high-n candidates; the hard gate is the post-DEMO 95%.**

## VE-LEFT TARGET 2 — "is −1 the worst POSSIBLE or the worst PLAUSIBLE?" — **worst possible IN-MODEL; not worst-possible in live.**
- Within the R-model, a HORIZON exit is one that did **not** hit the stop (else it is `n_stop`, R=−1) → its R ∈ (−1, RR), so real `E[X|h] > −1` always. Thus `_EXH_MISSING=−1` is **below any real horizon mean** → the worst possible **in-model**. ✓ Fail-closed complete against the model.
- **But the whole EV caps per-trade downside at −1R** (stop = exactly −1R via `−p_s·1`; horizon > −1R). **A live gap over the stop fills worse than −1R** — an outcome the model does not admit. So `−1` is the worst *plausible-in-model*, and the model itself **inherits the no-gap-slippage optimism from `mstrat` (RT-CODE-A-0007 R3)**. **Fail-closed is closed against the model's floor, not against live tail risk.** (D-R2.)

## VE-LEFT TARGET 3 — "can the hierarchy be deepened OPPORTUNISTICALLY after results?" — **deepening-for-luck self-defeats; schema-SELECTION is an open, un-audited backdoor.**
- The engine **consumes** a caller-supplied `hierarchy` (`:79`) — it cannot deepen anything itself. And the **LCB self-penalizes lucky deepening**: drilling to a sparse cell with a fluke-high `p_t_hat` also **widens** its interval → **lowers `p_t_lcb`** → the gate blocks it. Heterogeneous siblings → `k=0` → maximum interval width. So the dangerous form (chase a lucky sparse cell) is **structurally self-blocked** — a genuine strength.
- **What is NOT protected:** the choice of **which descriptors/levels define the hierarchy** (schema selection). A caller can search over many candidate hierarchies (descriptor orderings/subsets) and submit the one that passes — a **garden-of-forking-paths at the caller boundary, uncorrected by the LCB** (which only corrects *within* a given hierarchy). And **only the COUNTS are hashed** (`prob_table_hash`, `:250`), **not the schema/depth** — so the audit trail cannot prove the hierarchy was pre-registered rather than chosen post-hoc. (D-R1.)

## OWN TARGETS — lookahead & circularity (both live at the caller boundary)
- **Lookahead:** the engine is a **pure function of counts** — it holds no time/price data, so there is **no lookahead in the engine**. It **trusts** that each `OutcomeCell` (n, n_target, n_horizon, sum_horizon_R — the setup's "medical record") is computed on trades **strictly prior to the decision**. There is **no as-of-time enforcement**; the window over which `p_t`/`p_h` are tallied is unverifiable in-engine. (D-R1.)
- **Circularity:** decisions → executions → outcomes → counts → decisions **is a real loop** — **iff the counts come from executed-only trades** (selection bias: observed `p_t` is conditioned on "we chose to trade it"; plus an **un-blockable freeze** — a setup blocked early never trades, never accumulates data, so it can never escape the block). The loop is **avoided iff the counts come from a shadow/paper record of ALL setups** (backtest-style). The engine does **not specify or enforce** the source. (D-R1.)

## THREE-OUTCOME CORRECTION — confirmed applied
`p_t` is the **target-hit** proportion (`_shrink_proportion(…, c.n_target)`, `:288`), NOT winrate; `p_h`/`E[X|h]` are separate (`:289,293`); `EV = p_t·RR − p_s·1 + p_h·E[X|h] − c/R` (`:247`). The two-outcome model (horizon counted as target) over-estimates EV materially (tested, `:47`). The CAND-0001 category correction (p_t≈0.05, not winrate 0.175) is structurally in force. ✓

## SEVERITY
- 🟠 **D-R1 · Three caller-boundary trusts the pure function cannot police:** (a) hierarchy **schema/depth** selection (opportunistic *deepening* self-blocks via the LCB, but *schema selection* is an uncorrected garden-of-forking-paths; only counts, not the schema, are hashed); (b) count **as-of-time** (no lookahead enforcement); (c) count **source** (executed-only → selection-bias + un-blockable freeze; shadow → clean). These are the engine's real exposure and are invisible to it.
- 🟠 **D-R2 · The −1 floor / the whole EV inherit `mstrat`'s no-gap-slippage optimism** — worst-in-model (−1R) is not worst-in-live (gap over stop < −1R). Fail-closed is closed against the model, not the tail.
- 🟡 **D-U1 · The 80% EV_LCB gate is lenient** — real, but near-equivalent to `EV_point>0` for high-n candidates, and pessimistic only on `p_t`+cost (not `p_h`/`E[X|h]`); the hard gate is the deferred 95%.
- 🟡 **D-U2 · n=0 μ=0 residual** — point estimate `p_t_hat` degenerates to 0.5 (old-bug value) in the audit field; gate-safe (LCB≈0), untested.
- 🟡 **D-U3 · Independent shrinkage of `p_t` and `p_h`** (different `k_t`,`k_h`) can yield `p_t+p_h>1`; the `p_s≥0` clamp then drops the stop penalty (**optimistic**). Author-acknowledged (`:245`); rare at the LCB, partially offset by the horizon term.
- 🟡 **D-U4 · Beta ppf audit value at n=0** is a numerically-extreme ≈0 (e.g. `3.11e-61`) — correct as a quantile, un-interpretable as audit; undocumented reliability floor (~α,β≥1e-3) that n=0 routinely crosses (gate still correct).

## WHAT SURVIVES (verified)
Beta ppf accurate for realistic α,β and gate-safe at n=0; n=0 contraction returns exactly the parent for μ>0 (repair real); `k` never negative, conservative on over/under-dispersion; three-outcome EV correction applied (target-hit, not winrate); fail-closed with the field NAMED, D2 strict equality (`ev_lcb>0` strict), feasibility filter `RR>c/R`, cost as a read parameter (stays 0.20). 13 tests + mypy clean; the LCB genuinely blocks thin history.

## VERDICT — **SURVIVES.** The arithmetic is sound and the shrinkage+LCB design is genuinely self-protecting against the *dangerous* form of data-fitting (lucky deepening). The gate is **real but lenient at 80%** (direct answer: **not a formality, but soft and mostly inert for the high-n candidates — the teeth are at 95%**). Nothing here invalidates a result: the engine is level-6, not wired to execution (step 3 of 4). The real risk is displaced to **what the engine trusts** — the caller populating the hierarchy (schema selection, as-of-time, count source) and the `mstrat`-inherited −1R downside cap — none of which the pure function can enforce.

## HANDOFF → CEO (step 4 of 4), then Statistician
1. **D-R1** — before wiring, bind at the caller: (i) a **pre-registered, hashed hierarchy SCHEMA** (not just counts) so schema-selection can't be gamed; (ii) an **as-of-decision-time guarantee** on the cell counts (no lookahead in the "medical record"); (iii) the count **source must be a shadow/paper record of all setups**, not executed-only, or the selection-bias + freeze loop bites.
2. **D-R2** — the −1R downside cap is only as sound as `mstrat`'s no-gap model; live gap slippage is unmodeled (ties to RT-CODE-A-0007 R3).
3. **D-U1** — decide whether 80% is intended to be near-inert for high-n candidates (it is); the 95% post-DEMO tightening is where real blocking happens.
4. **D-U2/U3/U4** — add the μ=0/n=0 test, decide the `p_t+p_h>1` clamp semantics, and consider clamping the reported `p_t_lcb` audit value to a floor for interpretability.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
