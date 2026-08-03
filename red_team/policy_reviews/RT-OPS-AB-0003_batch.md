# RED TEAM — OPERATIONAL MODE, PHASE A + B (single pass) · Batch RT-OPS-AB-0003
### CAND-0011 … CAND-0019 (nine candidates, Part A + Part B v2.0)
**Date:** 2026-07-25 · **Auditor:** Red Team · **Policies @ commit `0806d00`, `alpha-automation-v1`** (Part A in the `_v1.md` files; Part B in `_v2.md`).
**No data run · policies not modified · no alternative risk method proposed.** Verification = reading the frozen policies + `git show | sha256sum` of every W10 pin + reading the cited primitives.

> Phase-A gate + Phase-B safety, one pass each. Findings are Statistician-stage controls unless marked a hard gate.

---

## 1. CROSS-CUTTING VERIFICATION (all nine)

- **W10 hashes — recomputed, all MATCH.** New this batch: **`order_flow.py` `728fa557…`** ✅. Re-confirmed: `institutional_levels c284fa2c`, `imbalance_mechanics 45f8937e`, `order_block_void 6ec7adbf`, `interactions dafb4804` ✅.
- **MK-01/MK-02 contamination — clean.** `order_flow` imports only `order_block_void` (`OrderBlock`, `GROUP_A_HORIZON`) and `market_state.atr14` — **neither MK-01 nor MK-02.** The confluence candidates add `institutional_levels`/`imbalance_mechanics` (import only the inert `Block`) and `interactions` (clean). **None of the nine inherits F1/F2.**
- **`order_flow` causality — verified in code.** `detect_order_blocks` `formation_idx = i-1` (bars ≤ i); `track_breaker` scans `formation_idx+1 →`; `_scan_reactions` scans `formation_idx+2 →` (skips the impulse bar). Module carries a **CEO-added anti-E010 constraint** (rejection/mitigation reaction windows **disjoint by construction**, `selection_end=event_idx`), **Research-Lab-verified**, with `test_no_lookahead_*`. Forward-only, no lookahead, no selection↔measurement overlap.
- **Directive-block reconciliation.** The queue header still reads *"order_flow … OB family is directive-BLOCKED,"* but this is **superseded** by the CEO ruling in the same queue: *"order_flow re-engineered primitives **unblocked**; E010/E013/E015/E016 stay blocked **as hypotheses**; MK-01/MK-02 remain DRAFT-forbidden."* These nine use the **unblocked re-engineered primitives**; **none is the blocked E010 standalone breaker-continuation** (all are rejection / mitigation / demand-zone / confluences). Batch is clear of the block — the stale header line should be corrected (a documentation item, not Red Team's to edit).

---

## 2. PHASE A — mechanism (all nine)

| Axis | Result |
|---|---|
| Lookahead | ✅ PASS (all) — OB detectors forward-only; FVG `confirmed_idx=i+1`; level `available_idx`=day first bar; confluence same-bar; `entry@next-open` |
| Circularity | ✅ PASS (all) — order_flow's anti-E010 disjoint windows (`selection_end=event_idx`) are the circularity guard; measurement runs forward of the event |
| Falsifiability | ✅ PASS (all) — precise mechanical rules; the confluences are falsifiable *as* "does the confluence beat its base?" |
| MK-01/02 | ✅ clean (all) |
| Distinct / duplicate | **Distinct, but a combinatorial-subset lattice** — see below |

**Distinctness / W-incr (batch-wide).** The batch is a **base × second-structure** expansion:
- Bases: **OB-Rejection** (0011), **OB-Mitigation** (0014), **Demand-Zone** (0013) — three mechanistically distinct OB-anchored reactions (sweep-reclaim vs touch/visit vs full-bar re-entry).
- Confluences, each a **strict subset of its base**: 0012 (OBREJ×Level ⊂ 0011), 0015 (OBREJ×FVG ⊂ 0011), 0018 (OBREJ×Void ⊂ 0011), 0016 (Mitig×Level ⊂ 0014), 0017 (DZ×FVG ⊂ 0013), 0019 (DZ×Level ⊂ 0013).

None is a pure duplicate, but **every confluence's triggers are a subset of its base** (same pattern as CAND-0007/0010). **W-incr (mandatory, all six confluences):** each must be tested for **incremental value vs its base and vs the second structure alone**, not vs a random null. This batch also materially grows the **multiple-testing family** (Statistician already at **=7 cumulative, STAT-BATCH-A-0002**); nine more mechanisms, heavily overlapping, is a family-wide correction concern for the Statistician.

**Phase-A verdict: all nine SURVIVED_RED_TEAM_A** (six carry W-incr).

---

## 3. PHASE B — risk layer

Common: **lookahead PASS** (stops = OB floor / zone edge / `min`-`max`; targets = zone edge / opposite level — all known at entry), **circularity PASS** (stop anchored on formation/touch bar; measurement forward of entry), **hidden-optimization PASS** (zero tunable numeric parameters), **S1** (intrabar "first of" order) unspecified in all — governed by the existing DEMO convention (`STAT-CAND0001-DEMO-CRITERIA-v1.0`), carry.

**S2 (near-zero stop) — structurally LOW across this batch.** Every stop is anchored to a **large impulse-bar extreme** (`Low_OB`/`High_OB` = the whole E010 impulse bar's floor; the demand zone = that bar's full `[Low,High]`; the confluences take the *deeper* `min`/`max`). E010 guarantees `range > 1.5×ATR`, so these stops are **inherently wide** — the arbitrarily-small-stop problem that made CAND-0003 acute **does not arise here.** (Flip side, as with CAND-0007: a wide/deeper stop can yield **R:R < 1** vs a near target — a risk-quality note for the DEMO criteria, not a safety defect.)

### 🔴 3.1 SEVERE — Finding H′ (block-only time-stop → **the live exit disappears**)

The Statistician established that a **block is a discovery-data construct**: live, there is **no current block**, so a **block-boundary time-stop never fires**. For any candidate whose only third-exit is the **block boundary**, live the trade has **only two exits — stop and target-zone-edge**; if neither is hit, the position **never closes.** The horizon does not lengthen — it **vanishes.**

| Candidate | 3rd-exit fallback | Live status |
|---|---|---|
| **CAND-0011** OB-Rejection | **block boundary** | 🔴 **no live time-stop** |
| **CAND-0013** Demand-Zone | **block boundary** | 🔴 **no live time-stop** |
| **CAND-0014** OB-Mitigation | **block boundary** | 🔴 **no live time-stop** |
| **CAND-0015** OBREJ×FVG | **block boundary** | 🔴 **no live time-stop** |
| **CAND-0017** DZ×FVG | **block boundary** | 🔴 **no live time-stop** |
| **CAND-0018** OBREJ×Void | **block boundary** | 🔴 **no live time-stop** |
| CAND-0012 OBREJ×Level | same-day time-stop (`day_index`) | ✅ live-valid (day boundary exists live) |
| CAND-0016 Mitig×Level | same-day time-stop (`day_index`) | ✅ live-valid |
| CAND-0019 DZ×Level | same-day time-stop (`day_index`) | ✅ live-valid |

**Six of the nine (0011/0013/0014/0015/0017/0018) have no live-valid time-stop.** This is the CAND-0002 Finding H escalated — and it read-across **worsens CAND-0002 too** (its expansion-family block time-stop is likewise inert live: the opposing-expansion exit can be absent, and then there is no exit at all). The three **level-bearing** confluences (0012/0016/0019) are safe on this axis **precisely because a PDH/PDL level supplies a day-boundary time-stop that exists live.**

**This is a hard safety gate, stated directly (DEMO account):** for CAND-0011/0013/0014/0015/0017/0018, the DEMO criteria **must bind a live-valid time-stop** (e.g. a day/session boundary, as the level-confluences already do). **If a live time-stop cannot be supplied, these six must NOT trade** — a position with no guaranteed exit is unacceptable.

---

## 4. VERDICTS

| Cand | Family | Phase A | Phase B safety | **Verdict** |
|---|---|---|---|---|
| **CAND-0011** | OB-Rejection | ✅ | 🔴 Finding H′ (no live time-stop); S2 low; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0012** | OBREJ×Level | ✅ (W-incr) | day time-stop ✅; S2 protected; S1; R:R note | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0013** | Demand-Zone | ✅ | 🔴 Finding H′; S2 low; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0014** | OB-Mitigation | ✅ | 🔴 Finding H′; S2 low; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0015** | OBREJ×FVG | ✅ (W-incr) | 🔴 Finding H′; S2 protected; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0016** | Mitig×Level | ✅ (W-incr) | day time-stop ✅; S2 protected; S1; R:R note | **SURVIVED_RED_TEAM_A — B conditional** |
| **CAND-0017** | DZ×FVG | ✅ (W-incr) | 🔴 Finding H′; S2 protected; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0018** | OBREJ×Void | ✅ (W-incr) | 🔴 Finding H′; S2 low; S1 | **SURVIVED_RED_TEAM_A — B conditional (hard gate)** |
| **CAND-0019** | DZ×Level | ✅ (W-incr) | day time-stop ✅; S2 protected; S1; R:R note | **SURVIVED_RED_TEAM_A — B conditional** |

**9 processed · 9 SURVIVED_RED_TEAM_A (Phase A) · Phase B all conditional · 0 REJECTED.** No lookahead, no circularity, no hidden optimization, no MK-01/02 contamination in any. Two safety items dominate: the **block-only time-stop (severe, six candidates)** and the routine **S1** (existing convention).

## 5. HANDOFF → Statistician, for protocol & DEMO criteria
1. **HARD GATE (0011/0013/0014/0015/0017/0018):** bind a **live-valid time-stop**; if unavailable, do not trade. **Read-across: re-open CAND-0002 for the same defect** (its block time-stop is also inert live).
2. **S1** worst-case intrabar hierarchy + **S2** floor: apply the existing `STAT-CAND0001-DEMO-CRITERIA` gate (S2 rarely binds here — wide OB stops).
3. **W-incr (six confluences):** test incremental value vs the base and vs the second structure alone.
4. **Multiple-testing family:** nine heavily-overlapping additions to a family already at 7 cumulative — a family-wide correction concern.
5. **Doc item (not Red Team's to edit):** the stale "OB family directive-BLOCKED" queue header is superseded by the CEO unblock ruling.

Part A and Part B unchanged; nothing run on data; no risk method proposed.
