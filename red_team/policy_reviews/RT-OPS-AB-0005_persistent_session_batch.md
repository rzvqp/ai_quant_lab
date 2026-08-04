# RED TEAM — OPERATIONAL MODE, PHASE A + B · Batch RT-OPS-AB-0005
### Primitive-B (persistent session-level) candidates CAND-0032 … CAND-0036
**Date:** 2026-07-26 · **Auditor:** Red Team · **Policies @ commit `ac9f4ab`, `alpha-automation-v1`.**
Part A + Part B in one pass. **No data run · policies not modified · no remedy.** Verification = frozen policies + `git show | sha256sum` of every W10 pin + the `atr14` filter source.

**Prior binding:** RT-CODE-A-0004 FORBADE Primitive B without a filter that "bounds the active-level count to a small, decidable set" (unfiltered 89–188 active → saturation → unfalsifiable → guaranteed dilution). This batch is the first B use, gated on the Statistician's composed ATR-proximity filter.

## 1. CROSS-CUTTING VERIFICATION

- **W10 hashes — recomputed, all MATCH:** `session_levels 2af2b9e6 @ bf02dd2`, `market_state 823cf66a`, `institutional_levels c284fa2c`, `interactions dafb4804`, `imbalance_mechanics 45f8937e`, `order_flow 728fa557`. ✅
- **Feed-alignment warning — PRESENT in all five.** ✅
- **Finding H′ — ABSENT.** No candidate uses the stale source-session boundary. Time-stops are **20-bar `GROUP_A_HORIZON`** (0032/0033/0035/0036) or the **day boundary** (0034) — both live-valid (fixed bar count / clock). Alpha explicitly rejected the session-boundary time-stop because the source session is months stale — **correct**, and it is exactly what removes Finding H′ here.

## 2. TARGET 1 — THE COMPOSED FILTER (`|level.price − close[j−1]| ≤ k·atr14[j−1]`)

**Verified against source — composition CORRECT, lookahead-free.**
- No ratified filter function exists; Alpha composed it from ratified `atr14` (market_state) + raw `close[j−1]`. **Confirmed at `market_state.py@bf02dd2`:** `atr14[i]` = rolling-14 mean of `tr[i−13..i]`, `tr[i]=max(h−l,|h−c₋₁|,|l−c₋₁|)` — **strictly causal** (`atr14[i]` depends only on bars ≤ i). Therefore **`atr14[j−1]` is complete before bar `j` opens.**
- `close[j−1]` complete before `j`; `level.price` from a closed prior session (`available_idx` after `p1`, verified in RT-CODE-A-0004). **All three filter inputs complete before `j`. No lookahead — PASS.**
- The precedent-bar denominator `atr14[j−1]` **matches the ratified `expansion` convention** (`prior_atr = atr[i−1]`) verbatim — consistent, not a novel timing choice.

## 3. TARGET 2 — OWN SELECTIVITY: real vs decorative (attacked per candidate)

The filter cures **saturation** (188→6), **not volume** (≈8,833 touches/8 yr ≈ 4/day survive — the DZ×FVG / CAND-0020 / CAND-0024 order of magnitude). So each candidate must carry a **real** trigger reduction *beyond* the filter, or it is the pure dilution pattern.

| Cand | Own selectivity | Verdict on it |
|---|---|---|
| **0032** Sweep | close-back-inside (wick sweep) | **REAL** — a sweep is strictly a subset of a touch (penetration **and** close back inside). Genuine reduction on top of the filter. |
| **0033** Mid | containment `low≤Mid≤high` | **THINNEST — claim UNVERIFIED.** For a filter-eligible (already ≤1·ATR) directionless line, a bar straddling it is ≈ "price is at the level" — close to a plain touch, **not** a second reference or a shape signature. The policy asserts it is "a materially rarer population" than the 8,833 H/L touches — **that is asserted, not measured.** If the containment count is not materially below 8,833, 0033 **is** the DZ×FVG pattern on a directionless line. Its trigger count is the decisive pre-performance report. |
| **0034** ×PDH/PDL | prior-day-level confluence | **REAL** — a second independent reference. |
| **0035** ×FVG | polarity-matched FVG | **REAL** — a second independent reference. |
| **0036** ×OB | polarity-matched OB body | **REAL** — a second independent reference. |

**Direct answer to the CEO on 0033:** containment is the weakest own-selectivity of the five and its "rarer" claim is unmeasured; combined with a *declared* (approach-side) direction, **0033 is the candidate most exposed to the volume-dilution failure.** Not a rejection (falsifiable, fail-closed, lookahead-free) — but the hardest-watch; the mandatory containment-count report tests the own-selectivity claim directly.

## 4. TARGET 3 — HORIZON (20-bar `GROUP_A_HORIZON`)

- **Live-valid — PASS.** A fixed bar count is computable live from `entry_idx`; it does **not** depend on the stale source session. `GROUP_A_HORIZON=20` is a **shared constant** (uniform across S01/S09/S11/S13/… and the queue) — **not per-candidate tuning.** 0034 uses the **day boundary** instead (more conservative, also live-valid).
- **FLAG (Statistician, not a defect):** 20 bars is a Group-A constant designed for **fresh** setups. Transferring it unexamined to an **aged-level** family is an untested fit — the reaction dynamics of a months-old level need not match Group A's population, and the horizon's *value* is unmeasured for this family. Live-valid ≠ appropriate. This is a specification question, not a lookahead/safety fault.

## 5. TARGET 4 — the HELD plain-touch-B candidate

**Alpha's refusal to build a plain touch-rejection on B is CORRECT and hides nothing.** A plain touch on aged B levels carries **only the filter** as selectivity → the ≈8,833/4-per-day population with no own trigger reduction = exactly the pure-volume-dilution loser my RT-CODE-A-0004 warned against (a B-candidate needs own selectivity beyond the filter). Its only viable standalone selectivity on B *is* the sweep — which **is** CAND-0032. So holding it is consistent with the standing condition, not an evasion.
- **Consequence to carry:** the three confluences (0034/0035/0036) use **plain-touch-on-B + a confluence** (no sweep), so their session-touch leg is precisely that held plain-B-touch — they rest **entirely** on the confluence as own selectivity. Acceptable (the confluence is a real reduction), but there is **no standalone plain-B-touch arm** to measure increment against, so their W-incr baseline must be the *other* constituent (CAND-0001/0003/0011) or 0032 — "vs the better single," as the policies state.

## 6. TARGET 5 — is CAND-0032 ⊂ CAND-0027?

**NO — not a subset.** Different level primitives: **0027 = touch-rejection on Primitive A** (prior session, expires after the next session, 2–3 active); **0032 = sweep on Primitive B** (persistent, accumulates for months, ATR-filtered). 
- **Level sets overlap only at the single youngest session-level, and only during A's brief lifetime.** B's value *is* the aged levels — exactly what A has already expired and 0027 can never see.
- **Triggers differ:** sweep (penetration **and** close-back-inside) ⊂ touch — so 0032's *trigger type* is a subset of a touch, but on a **different level population**.
- **Net:** a trade fires in both only when a level is simultaneously an A-level and a B-level (youngest, within A's lifetime) **and** filter-eligible **and** swept — a thin intersection, **not containment either way.** 0032 has the bulk (sweeps of aged B levels) that 0027 lacks; 0027 has plain/unfiltered fresh touches that 0032 lacks. **They are largely DISJOINT.** Good for family independence (disjoint tests keep BH-FDR valid); but **0032 must NOT be scored as an increment over 0027** — it is a distinct population.

## 7. PART B — SAFETY

- **Lookahead / circularity — PASS** (stops = raw OHLC or ratified edges at `j`; targets = ratified levels/edges; horizons live-valid).
- **Hidden optimization — PASS with a condition.** Zero per-candidate free parameters; `k=1.0` primary with `k=0.5 / k=2.0` **pre-declared** sensitivities (the correct pre-registration, not post-hoc tuning); `GROUP_A_HORIZON` shared. **Condition:** `k=1.0` was chosen on the *level-count* distribution (a structural saturation target), not on returns — acceptable — **but the pre-declared k=0.5/2.0 sensitivities MUST be run and reported** so the primary is not cherry-picked.
- **S1 (intrabar order):** unspecified per candidate → governed by the existing DEMO worst-case convention (STAT-CAND0001-DEMO). Carry.
- **S2 (arbitrarily-small stop):** **0032** (sweep-wick extreme), **0033** (containment-bar extreme), **0034** (touch extreme) — **exposed → bind `min_executable_risk` floor.** **0035 / 0036** — stop = deeper min/max of two references → **wider → protected.**

## 8. WEEKLY-STRUCTURE SIGNAL — and it is WORST here

0032, 0034, 0035, 0036 fade a **SESSION_HIGH/LOW** → they inherit the touched-by-rallying-up vs short-bias anti-correlation (a HIGH is *reached* by rallying up, then *faded short*). **Critical amplification:** the Statistician measured this effect **grows with period length**, and I earlier predicted session < daily. **Primitive B inverts that for the aged population** — a level untouched **for months** is the *longest-period* extreme in the pipeline; being finally reached implies a sustained directional move, so "touched" and "faded-against" are **maximally** anti-correlated. **The persistence that makes B attractive is exactly what maximizes the weekly pathology.** Expect this family to suffer the anti-correlation **more** than session-A (0026/0027) and even more than daily. **Strong signal.** **CAND-0033 (Mid, containment, no exceedance, no intrinsic side) is EXEMPT.**

## 9. CENTRAL QUESTION (answered directly)

> "Is your condition — a filter bounding the active-level count to a small, decidable set — met? Or does 4 triggers/day remain too much for a family with no history?"

- **The condition is FORMALLY MET.** 188→6 active (median 0), 83.6 % empty bars, falsifiability restored. The **saturation/unfalsifiability defect I raised in RT-CODE-A-0004 is CURED.** ✅
- **"4/day too much" is a DIFFERENT failure mode** — volume-dilution-below-cost — **not** the saturation defect and **not** a Red Team lookahead/circularity/safety question. It is **per-candidate and measurable** (the mandatory trigger-count + expectancy-vs-cost report the Statistician already requires). Red Team does **not** reject on it. The filter cured saturation; **each candidate's own selectivity must carry it below the dilution threshold** — and **0033's own selectivity is the thinnest and unverified**, so it is the one most likely to reproduce the DZ×FVG loss.

## 10. PER-CANDIDATE VERDICTS

| Cand | Phase A | Part B (S1/S2, horizon) | Weekly | **Verdict** |
|---|---|---|---|---|
| **0032** Sweep-B | ✅ own-sel REAL (sweep); **⊄ 0027 (distinct population)** | S2 exposed→floor; 20-bar horizon live-valid; S1 bind | **inherits (WORST — aged)** | **SURVIVED_RED_TEAM_A — B conditional** |
| **0033** Mid-B | ✅ own-sel THINNEST/UNVERIFIED (containment); direction disclosed-assumption; close==Mid→no-trade | S2 exposed→floor; 20-bar horizon; S1 bind | **EXEMPT** | **SURVIVED_RED_TEAM_A — B conditional; volume-most-at-risk → containment-count report decisive** |
| **0034** ×PDH/PDL | ✅ own-sel REAL (day confluence); **W-incr ⊂ {session-touch, 0001}** | S2 exposed→floor; **day-boundary** horizon live-valid; S1 bind | **inherits (WORST)** | **SURVIVED_RED_TEAM_A — B conditional** |
| **0035** ×FVG | ✅ own-sel REAL (FVG); **W-incr ⊂ {session-touch, 0003}** | S2 **protected** (min/max stop); 20-bar horizon; S1 bind | **inherits (WORST)** | **SURVIVED_RED_TEAM_A — B conditional** |
| **0036** ×OB | ✅ own-sel REAL (OB); **W-incr ⊂ {session-touch, 0011}** | S2 **protected** (min/max stop); 20-bar horizon; S1 bind | **inherits (WORST)** | **SURVIVED_RED_TEAM_A — B conditional** |

**5 processed · 5 SURVIVED_RED_TEAM_A · 0 REJECTED.** No lookahead, no circularity, no hidden per-candidate optimization, filter composition verified, no Finding H′.

## 11. HANDOFF → Statistician, for protocol & DEMO criteria
1. **Trigger-count report is a HARD pre-performance gate on all five** — and **decisive for 0033** (test the "containment is materially rarer than 8,833" claim; if it is not, 0033 is the DZ×FVG dilution pattern).
2. **Run the pre-declared sensitivities k=0.5 / k=2.0** alongside k=1.0 — the primary must not be cherry-picked; report all three.
3. **Weekly-structure signal is WORST for Primitive B** (aged HIGH/LOW extremes = longest-period → maximal touched-vs-short anti-correlation) on 0032/0034/0035/0036; measure it explicitly. 0033 exempt.
4. **W-incr:** 0034 ⊂ {session-touch, 0001}; 0035 ⊂ {session-touch, 0003}; 0036 ⊂ {session-touch, 0011}. **No standalone plain-B-touch arm exists** (held) → increment vs the other constituent (or 0032). **0032 ⊄ 0027** — distinct population, not an increment; treat as its own family member (keeps disjointness / BH validity).
5. **CAND-0033 direction** is a disclosed approach-side assumption — test its edge; close==Mid fail-closed.
6. **20-bar `GROUP_A_HORIZON` fit for aged levels is unmeasured** — live-valid but transferred from a fresh-setup population; consider measuring the reaction horizon for this family.
7. **DEMO gate:** existing S1 worst-case + `min_executable_risk` floor. Floor routine on 0032/0033/0034 (single-reference stops), rare on 0035/0036 (min/max stops).
8. **Feed-alignment transferability warning** attached to all five (RT-CODE-A-0004).

Multiple-testing family grows. Nothing modified, nothing run on data; no risk method proposed.
