# RED TEAM — OPERATIONAL MODE, PHASE A + B · Batch RT-OPS-AB-0004
### Session-level candidates CAND-0026 … CAND-0031
**Date:** 2026-07-25 · **Auditor:** Red Team · **Policies @ commit `0ce1e57`, `alpha-automation-v1`.**
Part A + Part B in one pass. **No data run · policies not modified · no remedy.** Verification = frozen policies + `git show | sha256sum` of every W10 pin + the cited primitives.

## 1. CROSS-CUTTING VERIFICATION

- **W10 hashes — recomputed, all MATCH.** All six pin `session_levels.py` @ **`bf02dd2`** with hash **`2af2b9e6…`** — verified: `session_levels @ bf02dd2 = 2af2b9e6` ✅ (and it hashes to the empty-file value on `alpha-automation-v1`, confirming the correct **not-co-located** W10 pin). `market_state 823cf66a`, `institutional_levels c284fa2c`, `interactions dafb4804`, `imbalance_mechanics 45f8937e`, `order_flow 728fa557` — all re-confirmed.
- **The `market_structure` / `liquidity_mechanics` change (0000225 → bf02dd2) — cleanly handled.** **No candidate cites either file.** They cite `session_levels @ bf02dd2`; `session_levels`'s only transitive touch of `market_structure` is the **`Block`** dataclass, which is **unchanged** across that window (verified: empty diff for `class Block`). The 6-line `market_structure` change is in the break logic (not `Block`, not used here). So the changed files do not reach any candidate.
- **MK-01/MK-02 contamination — clean.** `session_levels` imports only `Block` (inert) + `session_of` + `_runs`; the OB confluence adds `order_flow` (imports `order_block_void` + `market_state.atr14`). **No F1/F2 logic reaches any candidate.**
- **Feed-alignment warning — PRESENT in all six** (the RT-CODE-A-0004 transferability finding is attached, counts 2–6). ✅
- **Finding H′ (block-only time-stop) — ABSENT in this batch.** Unlike CAND-0011…0019, **every** candidate here has a **live-valid time-stop**: the **session boundary** (`expiry_idx`, session-native) or the **day boundary** (17:00-NY, CAND-0029). A session/day boundary exists live (clock-derived) → the trade always has a live exit. **No Finding H′.** ✅

## 2. SPECIFIC VERIFICATIONS THE CEO REQUESTED

**Sweep composition (CAND-0026) — CORRECT, faithful mirror of PDH/PDL sweep-reject.** No `detect_session_sweeps` exists; Alpha composed sweep = **penetration** (`detect_session_level_touches`: `high[j] ≥ price`) **AND close-back-inside** (`close[j] < price` for HIGH) from raw OHLC, with **close-beyond → NO TRADE (fail-closed)**. This is exactly the ratified PDH/PDL sweep-reject signature. ✅ **One inherited property (not a defect):** the ratified touch detector **consumes at first penetration (D7)** regardless of close, so a level first **broken** (close beyond) and later genuinely **swept** loses the later sweep — CAND-0026 detects *first-penetration sweeps*, not *all sweeps*. Identical to the PDH/PDL family; a recall limitation to disclose, not a correctness fault (no false trades).

**Mid direction (CAND-0028) — a DISCLOSED choice, not a hidden assumption.** Mid has no intrinsic side; the policy declares direction **by approach side** (`close[j-1] > Mid` → came from above, LONG; `< Mid` → SHORT) and **labels it explicitly** "DECLARED DIRECTION (policy, not level)" with an "Explicit direction disclosure (for Red Team / Statistician): the approach-side rule is an ASSUMPTION." So it is a **transparent policy claim**, not concealed. **`close[j-1] == Mid` → NO TRADE (fail-closed)** — verified present. The approach-side rule is the **load-bearing untested assumption** → the Statistician must test whether it carries any edge.

## 3. WEEKLY-STRUCTURE SIGNAL (per the CEO's explicit request)

The Statistician measured that **"touched" and "bias-aligned-for-reversal" fight by construction**, worsening with period length. **Five of six candidates inherit that structure:** CAND-0026/0027 and the three confluences (0029/0030/0031) trade a **SESSION_HIGH reached by rallying UP → faded SHORT** (and SESSION_LOW reached by falling → LONG). So "level touched" (price went up to it) and "short-reversal bias" (wants down) are **anti-correlated by construction** — the exact PWH/PWL pathology.

- **Severity should be MILDER than daily/weekly** (the Statistician's own prediction: the effect grows with period length; a session is shorter than a day). **Signalled, not a rejection** — but the Statistician must expect the same anti-correlation, measured per session.
- **CAND-0028 (Mid) is EXEMPT:** Mid is **containment-touched** (no exceedance) with **no intrinsic side**, so it has no "reached-by-going-up-then-shorted" structure. This matches Mid being a different class of object.

## 4. PER-CANDIDATE VERDICTS

| Cand | Mechanism | Phase A | Part B (S1/S2, time-stop) | Weekly | **Verdict** |
|---|---|---|---|---|---|
| **CAND-0026** Sweep+Reversal | session sweep (penetration+close-back), fade | ✅; **W-incr ⊂ 0027**; sweep composed correctly | S2 exposed (touch-extreme stop → bind floor); **session time-stop, live-valid**; hidden-opt PASS | **inherits** (milder) | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0027** Touch+Rejection | session touch, fade (analog PDH/PDL) | ✅ (base) | S2 exposed; **session time-stop, live-valid**; S1 bind | **inherits** (milder) | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0028** Mid Reaction | containment, direction by approach side | ✅; direction **disclosed assumption**; `close==Mid`→no-trade ✅ | S2 exposed (containment-extreme stop); **session time-stop**; S1 bind | **EXEMPT** | **SURVIVED_RED_TEAM_A — B conditional; approach-side assumption → Statistician must test** |
| **CAND-0029** Session×PDH/PDL | confluence (session touch ∩ PDH/PDL touch) | ✅; **W-incr ⊂ 0027 ∩ 0001** | S2 **protected** (touch-extreme, day-level target); **day time-stop, live-valid**; S1 bind | **inherits** (milder) | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0030** Session×FVG | confluence (session touch inside FVG) | ✅; **W-incr ⊂ 0027 ∩ 0003** | S2 **protected** (deeper min/max stop); **session time-stop, live-valid**; S1 bind | **inherits** (milder) | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0031** Session×OB | confluence (session touch inside OB body) | ✅; **W-incr ⊂ 0027 ∩ 0011** | S2 **protected** (deeper min/max stop); **session time-stop, live-valid**; S1 bind | **inherits** (milder) | **SURVIVED_RED_TEAM_A — B conditional** |

**6 processed · 6 SURVIVED_RED_TEAM_A · 0 REJECTED.** No lookahead, no circularity, no hidden optimization, no MK-01/02 contamination, **no Finding H′** (all live-valid time-stops). Part B conditional on the existing DEMO gate (S1 worst-case + `min_executable_risk` floor); floor is routine for the base candidates (0026/0027/0028, touch/containment-extreme stops) and rarely binds for the confluences (wider min/max stops).

## 5. HANDOFF → Statistician, for protocol & DEMO criteria
1. **W-incr (mandatory):** CAND-0026 ⊂ 0027; CAND-0029 ⊂ 0027∩0001; CAND-0030 ⊂ 0027∩0003; CAND-0031 ⊂ 0027∩0011 — test incremental value vs the base(s), not a random null. Batch grows the multiple-testing family.
2. **Weekly-structure signal:** 0026/0027/0029/0030/0031 carry the touched-by-rallying-up vs short-bias anti-correlation (milder than daily per the Statistician's prediction — measure it per session). CAND-0028 (Mid) exempt.
3. **CAND-0028 approach-side direction is a disclosed, untested assumption** — its edge (if any) must be tested; the rule fades the approach, `close==Mid` fail-closed.
4. **DEMO gate:** apply the existing S1 worst-case + `min_executable_risk` floor (STAT-CAND0001-DEMO-CRITERIA). Floor routine on the base candidates, rare on the confluences.
5. **Feed-alignment transferability warning** already attached to all six (RT-CODE-A-0004) — session levels are feed-dependent; an OANDA-validated edge may not reproduce on MT5.
6. **Sweep recall note (CAND-0026):** consume-at-first-penetration means break-then-sweep sequences are not detected (faithful to PDH/PDL; disclose).

Nothing modified, nothing run on data; no risk method proposed.
