# RED TEAM — CODE ATTACK · Level-3 M15 operational zone map
### RT-CODE-A-0015 · Target: `code/zone_map.py` @ `11ae360`
**Date:** 2026-08-08 · **Auditor:** Red Team · **Spec:** STAT-LEVEL2-CONDITION-AND-LEVEL3-ZONE-MAP-SPEC-v1.0 (`a595cc5`, manifest v2.7.52, Part 3). Level 3, step 3. An **unweighted counter** (not a weighted score): four ratified features in a 1×ATR band (pdh_pdl, fvg, liquidity, discount), k∈0..4, threshold k≥4 = total confluence. Checklist only. **No real-data run** — algorithm verified on synthetic M15 (module + all detector deps read-only from branch); nothing modified; no remedy.

## VERDICT — **PASS_WITH_LIMITATIONS.**
Lookahead-free (proven, reads ≤ i-1), leakage/overfitting/hidden-params/reproducibility clean; k≥4 is legitimately **derived** from falsifiability; the unweighted-counter choice is right (weights would be a second estimator). Three limitations: (ZM-L1) the joint (band, k) derivation **restores falsifiability but MOVES the saturation up a level** — the 1×ATR band makes the map a coarse binary total-confluence *filter*, not a graded map; (ZM-L2) redundancy is a **hand-maintained dict** and the cascade is an **`if` on caller booleans** — both weaker than the type-safe alternatives; (ZM-U1) the empty-set relies on level 6 checking emptiness, not status alone.

---

## CHECKLIST
- **Lookahead — PASS, PROVEN.** All features filter to `available_idx/confirmed_idx ≤ i-1`; `ref = close[i-1]`, `atr[i-1]`. **Numeric proof:** scrambling the **last** bar (i) to a sentinel leaves `counter_k/status/reason/reference` **identical** → the function reads only bars `≤ i-1` and does not even read the current bar. ✅
- **Leakage — PASS.** Pure single-bar function.
- **Circularity — disclosed, by construction.** All four features derive from primitives that **candidates trigger on** (pdh_pdl→0001/0007/…, fvg→0003/…, liquidity→0020/…, discount→0028/0033) → **ZERO independent features** (only NEWS, absent). Same as levels 1/2.
- **Overfitting — PASS.** `k≥4` derived from falsifiability (below); band reused; no fitted params.
- **Hidden params — PASS.** Band and k are **jointly** in `schema_hash`; all declared; units M15 (ZI 92 / SĂPTĂMÂNĂ 460 correct on M15 — the 460 that was a transplant on H4 is native here).
- **Reproducible — PASS.** Deterministic, schema-hashed.

## SPEC TARGET 1 — threshold k≥4: **DERIVED from falsifiability, not arbitrary — but derived *because* the band saturates.**
At the 1×ATR band the counter is saturated (measured: 3/4 features coincide on 94.87 % of bars; k≤3 leaves only 0.07/0.38/5.13 % empty). Only **k≥4 (total)** leaves a material complement (**57.18 % bars with no qualified zone → falsifiable**). So k≥4 is the **only** threshold that restores falsifiability — a genuine derivation, not a free choice. **But it is forced by the band's collinearity**, which is the crux of ZM-L1.

## SPEC TARGET 2 — "total confluence" — map or FILTER? **A binary FILTER.**
Because `THRESHOLD_K = 4` and there are 4 features, the map emits a zone **only** when all four coincide (`counter_k ≥ 4`); otherwise the empty set. The k=1/2/3 **gradient is discarded** (`ranked_by_k` is trivially `(4,)` or `()`). So the "operational map" is a **total-confluence FILTER** (present/absent), not a graded confluence map — it hands level 6 a binary, not a gradient. Design choice, but the "map" name overstates it.

## SPEC TARGET 3 — band 1×ATR, the fourth time: **a reused ratified anchor — but a *proximity* band reused as a *confluence* band imports the collinearity.**
1×ATR is the lab constant ratified at v2.7.41 (primitive-B filter, level-2 liquidity) — **reused, not re-chosen** (consistent, legitimate). **But** a band designed for single-level *proximity* applied as a *confluence* band makes the four features fall within 1 ATR of each other **94.87 %** of the time — this collinearity **is** the saturation that then forces k≥4. So it is an anchor **by reuse**, but arguably **mis-scoped for confluence**: a narrower band would reduce collinearity and permit a graded map. The "fourth time the same saturation" appears **because the same wide band is reused.**

## THE CEO's SATURATION QUESTION — does the joint (band, k) derivation resolve it, or move it up a level? **MOVES it up a level.**
The joint derivation **restores falsifiability** (k≤3 → ~99 % saturated; k=4 → 57 % complement). But it does **not resolve the band-induced collinearity**: "total confluence" still fires on **42.82 %** of bars — a common, coarse state, not a rare high-conviction signal. My **random-walk synthetic saturated to k=4** with no real structure at all — direct confirmation that the 1×ATR band makes total confluence easy. So the problem moves from *"unfalsifiable counter"* to *"falsifiable but coarse binary"*: the map separates 42.82 % (all-4) from 57 % (not-all-4), and **whether all-4 actually outperforms not-all-4 is unquantified** — the value question is pushed to the Statistician (level 6), not resolved here. (ZM-L1.)

## OWN TARGET — other undisclosed shared-primitive edges? **`REDUNDANT_WITH` is a hand-maintained dict (regression from level 2).**
Unlike level 2 (`bias_h1`), which attached redundancy by **mechanical static inspection** (two tiers, direct + injected), level 3 uses a **hardcoded dict literal** (17 edges). The docstring references "două tiere — L-R1" but does **not** implement the mechanical inspection — so the disclosure is **manual and can be incomplete**, exactly the failure mode level 2's mechanism was built to avoid. I verified the flagged edge (`discount ← SESSION_MID → CAND-0028/0033`) is complete (only the two Mid candidates use SESSION_MID), but **completeness is not guaranteed by construction** — a new candidate using one of these primitives would silently not appear until someone edits the dict. **The mechanism permits undisclosed edges** (the CEO's concern); adopt level 2's static inspection to close it. (ZM-L2a.)

## OWN TARGET — ZERO fully-independent features? **TRUE, verified.** All four features map to candidate triggers; NEWS (the only independent axis) is absent here. Consistent with levels 1/2.

## OWN TARGET — fail-closed: UNAVAILABLE vs EMPTY SET distinguished? **Yes at the classifier; but level 6 must check emptiness, not status.**
Verified: UNAVAILABLE (incomplete_window / cascade / atr_unavailable) → `status=UNAVAILABLE, zones=()`; empty-set-below-threshold → `status=AVAILABLE, reason=empty_set_below_threshold, zones=()`. **The classifier distinguishes them (status + reason).** **But both have `zones=()`**, so level 6 must gate on `status==UNAVAILABLE OR len(zones)==0` — **if it checks `status` alone, the valid empty-set (status=AVAILABLE) is silently consumed as "a map exists" and could proceed to trade with no zone.** Same silent-consumption class as level-4 Z4-L1. (ZM-U1.)

## OWN TARGET — cascade level 1/2 UNAVAILABLE → level 3: **by `if` on caller booleans, NOT by type.**
Verified: `regime_available`/`bias_available` are **boolean parameters**; `if not (regime_available and bias_available): _fail("cascade…")`. So the cascade is an **`if` on values the caller derives**, not a type-propagated `UNAVAILABLE` from an actual RegimeState/BiasState. **If the caller mis-derives the booleans (passes True when level 1/2 is UNAVAILABLE), the cascade silently fails** and level 3 proceeds. Weaker than type propagation. (ZM-L2b.)

## SEVERITY
- 🟠 **ZM-L1 · Saturation moved, not resolved** — the 1×ATR band collinearity (94.87 %) makes the "map" a coarse binary total-confluence filter (42.82 % coverage; random data saturates to k=4); falsifiability is restored but the value of all-4-vs-not is unquantified, and the band may be mis-scoped for confluence.
- 🟠 **ZM-L2 · Two weak-by-design disclosure/propagation mechanisms** — (a) `REDUNDANT_WITH` is a hand-maintained dict (can miss edges; level 2's mechanical inspection was the fix); (b) the level-1/2→3 cascade is an `if` on caller booleans, not type-propagated.
- 🟡 **ZM-U1 · Empty-set silent-consumption** — valid empty-set is `status=AVAILABLE, zones=()`; level 6 must check emptiness, not status alone.

## WHAT SURVIVES (verified)
Lookahead-free by construction (proven, reads ≤ i-1); leakage/overfitting/hidden-params/reproducibility clean; the unweighted counter is the right structural choice (weights = a rejected second estimator); k≥4 legitimately derived from falsifiability; UNAVAILABLE vs empty-set distinguished at the classifier; ZERO independent features correctly disclosed; band/k jointly schema-hashed.

## VERDICT — **PASS_WITH_LIMITATIONS.** The map is causally sound and the counter/threshold are honestly derived; the limitations are (ZM-L1) that the joint (band, k) derivation **relocates** the saturation into a coarse falsifiable-binary rather than resolving the band collinearity, and (ZM-L2/U1) that redundancy disclosure, the level-cascade, and the empty-set all rely on **manual/if/status-alone** mechanisms weaker than the type-safe alternatives the earlier levels moved toward. None is a defect in this file; all must be honored/strengthened at integration.

## HANDOFF → CEO / Statistician
1. **ZM-L1:** measure whether all-4 (42.82 %) actually outperforms not-all-4 — the joint derivation restored falsifiability but the map is a coarse binary; consider a narrower confluence band to recover a gradient.
2. **ZM-L2:** replace the hand-maintained `REDUNDANT_WITH` with level 2's mechanical static inspection (to guarantee no undisclosed edges); propagate the level-1/2 cascade by type/status, not caller booleans.
3. **ZM-U1:** level 6 must NO_TRADE on `status==UNAVAILABLE OR len(zones)==0`, not on status alone.
4. The classification (lookahead, k-derivation, unweighted counter, UNAVAILABLE/empty-set distinction) is **verified clean.**

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
