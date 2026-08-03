# RED TEAM — OPERATIONAL MODE, PHASE B · Batch RT-OPS-B-0002
### Part B (risk / DEMO_BASELINE) — CAND-0002, CAND-0003, CAND-0007
**Date:** 2026-07-25 · **Auditor:** Red Team · **Policies @ commit `de31dcc`, `alpha-automation-v1`**
**Attack: PART B only** (Part A already SURVIVED for all three — not re-run). Targets = RT-OPS-B-0001 set: lookahead · safety (same-bar stop∧target, near-zero stop, target-already-reached) · ambiguity (intrabar "first of") · circularity · hidden optimization. **No data run · policies not modified · no alternative risk method proposed.**

> Benchmark: the Statistician has already bound the RT-OPS-B-0001 S1/S2/S3 gate as executable preconditions for CAND-0001 (`STAT-CAND0001-DEMO-CRITERIA-v1.0`: worst-case hierarchy STOP>TIME-STOP>TARGET; `min_executable_risk` floor; target scanned from entry+1). The findings below map each candidate onto that **existing** gate — Red Team designs no new method.

---

## Common structure (all three)

- **Lookahead — PASS (all three).** Every Part-B coordinate is a bar extreme, a ratified level/edge, or the clock day-boundary — all known at entry (`next-open`); the event-based exits are observed strictly forward. Verified per field below.
- **Circularity — PASS (all three).** Each stop is anchored on the **trigger/touch bar**, but resolution (stop/target/time-stop) runs strictly from entry (`trigger+1`) forward — selection window and measurement window are **disjoint** (same clean separation as Part A / RT-OPS-B-0001).
- **Hidden optimization — PASS (all three).** **Zero tunable numeric parameters** in every Part B (stops = bar extremes / ratified edges / `min`-`max` selections; targets = existing levels or gap edges; sizing 1R; time-stops = existing boundaries). No ATR multiple, no chosen RR. Where an RR appears (CAND-0003 ≈1) it is a **geometric consequence** of a midpoint entry, explicitly "not chosen." No sign of a data-informed choice.
- **Ambiguity / S1 (all three):** the intrabar order of "**first of** stop / target / time-stop" is **not mechanically specified** in any of the three — identical to the RT-OPS-B-0001 S1 finding. Severity differs per candidate (below). The fix is the **binding** of the existing worst-case convention, not a new method.

---

## CAND-0002 — Compression→Expansion (stop = opposite extreme of the expansion bar; exit = first opposing expansion)

- **Lookahead — PASS.** stop = `low[i]`/`high[i]` (expansion bar `i`, known at entry `i+1`); exit = first opposing `expansion[k]` after entry (causal, forward), filled `open[k+1]`; time-stop = block boundary. ✅
- **CEO question — "can the opposing expansion be absent entirely? then what?"** **Yes, it can never occur.** The policy's fallback is the **block boundary** time-stop — so a trade with no opposing displacement **holds to block-end.** ⚠️ **Finding H (horizon):** the time-stop here is the **BLOCK** boundary, *not* the day (unlike CAND-0001/0007). A block can span many days/weeks, so a position can be held for the remainder of a block — a materially longer, over-night/over-weekend exposure the DEMO criteria must weigh (margin, gap risk). Not a lookahead/crash; a **DEFINED but unbounded-within-block horizon.**
- **Safety — near-zero stop (S2): essentially IMMUNE.** The stop distance is `entry − low[i]`, and bar `i` is by definition an **expansion** (`range > 1.5×ATR`, body `≥ 0.5×range`), so `entry(≈close[i]) − low[i]` is bounded below by ~half the expansion body — inherently **wide**. The near-zero-stop problem cannot arise. (The `≤0` degenerate case is caught by the guard.) `min_executable_risk` floor will rarely if ever bind.
- **Safety — S1 (stop ∧ exit same bar): mild.** If a bar `k` both breaches the stop (intrabar) and is an opposing expansion (exit at `k+1` open), the stop is chronologically first (intrabar on `k`) — so worst-case (stop-first) is also the natural order — **but the policy does not state it.** Bind it.
- **Target-already-reached:** N/A — the "target" is a forward event (opposing expansion), not a pre-existing price level.
- **Circularity / hidden-opt — PASS.**
**→ SURVIVED_RED_TEAM_A — conditional.** Carry: bind S1 worst-case; **flag Finding H (block-length holding horizon)** to the DEMO criteria. S2 N/A (structural immunity — noted as a positive).

## CAND-0003 — FVG CE-50 (stop = FVG far edge / Q4 inversion; target = FVG near edge) — **MOST SAFETY-EXPOSED**

- **Lookahead — PASS.** stop = `lower`, target = `upper` (the FVG's own ratified edges, known at `confirmed_idx=i+1`, before the CE-50 touch and entry); time-stop = block boundary. ✅
- **CEO question — "stop and target are both edges of the SAME FVG; can the distance be arbitrarily small?"** **Yes — directly.** Entry is `ce_50` (midpoint), so the **stop distance = `ce_50 − lower` = (upper − lower)/2 = half the FVG height.** FVG height (`low[i+1] − high[i-1]`) can be **arbitrarily small** (a near-touching 3-bar gap), so the stop distance → arbitrarily small. 🔴 **S2 is LIVE and routine here** (not a corner case): a small FVG ⇒ a tiny stop ⇒ an unbounded 1R position. The `min_executable_risk` floor is **essential**, and the policy's own guard only catches the `≤0` case, not the tiny-positive one.
- **Safety — S1 (stop ∧ target same bar): ACUTE.** stop and target are the **two edges of one (possibly small) FVG**; a single ordinary bar routinely spans **both** ⇒ stop and target hit on the same bar, order **unspecified**. Worst-case binding is critical here — an optimistic (target-first) default would systematically over-report a family whose zone is small by construction.
- **Target-already-reached:** guard covers "next-open already beyond near edge." An intraday earlier touch of an edge is inside the same tiny zone — subsumed by S1/S2 handling.
- **Circularity / hidden-opt — PASS.** R:R ≈ 1 is explicitly a **geometric consequence** of the midpoint entry, not a chosen ratio — no hidden optimization.
**→ SURVIVED_RED_TEAM_A — conditional, and the tightest gate of the three.** Carry S1 (worst-case, acute) **and** S2 (`min_executable_risk` floor, routine not corner-case). **If the DEMO engine cannot be shown to apply the floor + worst-case convention, CAND-0003 must NOT trade** — small FVGs make both defects the common case, not the tail.

## CAND-0007 — Level × FVG Confluence (stop = below BOTH structures; exit = opposite prior-day level + day time-stop)

- **Lookahead — PASS.** stop = `min(low[touch_idx], FVG.lower)` / `max(high[touch_idx], FVG.upper)` (both known at entry); target = `PDH`/`PDL`; time-stop = 17:00-NY clock day-boundary. ✅
- **CEO question — "the stop is below both structures, so wider; how does it interact with the `min_executable_risk` floor?"** The combined stop is the **deeper** of two floors ⇒ the stop distance is **≥** either structure alone ⇒ **wider** ⇒ it **rarely hits the floor.** So "below both structures" is **protective against S2** (the opposite of CAND-0003). The floor almost never binds. ⚠️ **Flip side (risk-quality, not safety):** a very wide combined stop can exceed the distance to the opposite-level target ⇒ **R:R < 1** vs `PDH`/`PDL`; the guards check "beyond stop/target" but not the stop-vs-target *ratio*, so an unfavourable-RR trade is allowed. DEMO criteria should be aware; it is not a safety defect (it falls out of the structures, no parameter chosen).
- **Safety — S1: rare.** stop (near entry, below the confluence) and target (opposite day level, across the daily range) can co-occur only on a bar spanning ~the whole PDH-PDL range — uncommon. Bind worst-case anyway.
- **Circularity / hidden-opt — PASS.** stop = `min`/`max` of two ratified prices (a selection, not a formula); zero free parameters. *(Note: this Part B's exit = CAND-0001's exit (opposite day level), and its entry zone ⊂ CAND-0003 — reinforcing the Part-A W-incr control: test whether the confluence adds value over its constituents, in risk as well as entry.)*
**→ SURVIVED_RED_TEAM_A — conditional.** Carry: bind S1 worst-case; S2 essentially N/A (protected — the wider stop rarely floors); note the R:R<1 possibility for the DEMO criteria.

---

## BATCH RESULT

| Candidate | Lookahead | Circular. | Hidden-opt | S1 intrabar order | S2 near-zero stop | Candidate-specific | **Phase-B** |
|---|---|---|---|---|---|---|---|
| CAND-0002 | ✅ | ✅ | ✅ | 🟡 mild (stop precedes next-open exit) | ✅ immune (wide by construction) | 🔴 **Finding H: block-length holding horizon** | **SURVIVED_RED_TEAM_A — conditional** |
| CAND-0003 | ✅ | ✅ | ✅ | 🔴 **acute** (one bar spans both edges) | 🔴 **live/routine** (stop = FVG height ÷ 2) | tightest gate | **SURVIVED_RED_TEAM_A — conditional** |
| CAND-0007 | ✅ | ✅ | ✅ | 🟡 rare (bar spans daily range) | ✅ protected (wider combined stop) | ⚠️ possible R:R<1 | **SURVIVED_RED_TEAM_A — conditional** |

**3 processed · 3 SURVIVED_RED_TEAM_A (conditional) · 0 REJECTED.** No lookahead, no circularity, no hidden optimization in any. Every safety item is governed by the **existing** DEMO convention already bound for CAND-0001 (`STAT-CAND0001-DEMO-CRITERIA-v1.0`: worst-case hierarchy + `min_executable_risk` floor); Part B's fault is silence, not a mechanism flaw.

## HANDOFF → Statistician, for the DEMO criteria
Apply the same executable-precondition gate (worst-case intrabar hierarchy STOP>TIME-STOP>TARGET; `min_executable_risk` floor on 1R sizing; forward-only target scan) to CAND-0002/0003/0007, **with per-candidate emphasis:**
- **CAND-0002:** add a rule for the **block-length holding horizon** (Finding H) — the opposing-expansion exit can be absent for a whole block.
- **CAND-0003:** the floor + worst-case are **routine, not corner-case** (small FVGs) — **if unenforceable, do not trade.**
- **CAND-0007:** the floor rarely binds (wide stop is protective); record the possible **R:R < 1**.

Nothing modified, nothing run on data, no risk method proposed. Part A unchanged (already SURVIVED).
