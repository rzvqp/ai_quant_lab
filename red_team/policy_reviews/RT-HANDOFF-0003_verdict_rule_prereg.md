# RED TEAM — VERDICT RULE (CEO-fixed) + PRE-REGISTERED revalidation criteria
### RT-HANDOFF-0003 · binds the NEXT ve_brain revalidation (after VE's corrective commit)
**Date:** 2026-08-13 · **Auditor:** Red Team · **Trigger:** CEO fixes the handoff verdict rule; applies from the next revalidation. **No engine modified; no repair; no real data.** This is a governance checkpoint — no new commit was delivered (HEAD is `4cfeb90`; VE has not re-submitted), so there is nothing to attack yet. This document pre-registers the criteria **before** seeing VE's fix.

## RULE_RECEIVED ✅ — the operational objective is a REAL VE_HANDOFF_PASS, not an open-ended audit
Pre-registered, three-way, no post-hoc criteria drift:
- **Reproducible defect that can affect the decision path → FAIL.**
- **Documentary limitation with no impact on the path → CONDITIONAL (with justification).**
- **All criteria pass and no reproducible bypass → PASS.**
- I do **not** invent defects; I do **not** extend criteria after the result without demonstrating a **material** risk; **if I find no reproducible violation, I emit PASS.**

## RECLASSIFICATION of the outstanding item under the new rule
My last verdict (RT-HANDOFF-0002, `c111d82`) was **CONDITIONAL** for the forged-eligibility hole. Under the now-fixed rule that item is a **reproducible defect that affects the decision path** (a RANGE strategy obtains a real TRADE via a matching-id forged `EligibilityDecision`) → it maps to **FAIL**, not CONDITIONAL. The rule "applies from the next revalidation," so the prior verdict stands as issued; **at the next revalidation this class of defect is FAIL if it persists.** CONDITIONAL is reserved for a documentary limitation with no path impact (e.g., a per-bar-proxy disclosure, a delegated-persistence note) — not for a live bypass.

## PRE-REGISTERED test plan for the next revalidation (fixed now, before VE's commit)
On the corrective commit I will run exactly these — nothing added after seeing the result unless I can demonstrate a material, reproducible decision-path risk (and I will say so explicitly if I do):
1. **Forged-eligibility fixture (the blocking defect):** range strategy + hand-built `EligibilityDecision(matching ids, eligible=True, reason omits range)` → `decide_n6` must return **NO_TRADE / TRUE_RANGE_NOT_IDENTIFIABLE**. Confirm the candidate now carries a **bound** `requires_true_range` (or `strategy_family`/`allowed_regimes`) that N6 checks **independently** of the eligibility object, and that it cannot be omitted, falsified, or altered between Router and N6.
2. **The eight points:** (1) router not bypassable · (2) a RANGE strategy cannot TRADE · (3) N6 requires a valid EligibilityDecision · (4) compression/displacement axes independent · (5) simultaneity survives to the Router · (6) A5 complete data identity · (7) comparability imposed on all internal paths (accept **by absence** if verified, as before) · (8) 12 deliverables complete.
3. **Complete path** N1 `RawAxes` → `StrategyRouter` → `EligibilityDecision` → EV → N6 — run it, then **try to break it**, each bypass explicit.
4. **Public-export inventory:** every public class/function through which a consumer could hand-build a `StrategyCandidate`/`EligibilityDecision` and reach EV/N6 — enumerated, each tested for a reproducible bypass.
5. **All manual-construction attempts:** direct instantiation, EV without eligibility, router omission, legacy recognizers, hand-built `SemanticRegime`/`RawAxes`, implicit activation on no-match.
6. **The 12 handoff deliverables:** each verified present and consistent (not just listed).

**Verdict mapping:** any one reproducible decision-path bypass → **FAIL**; only documentary limitations remain → **CONDITIONAL** (justified); clean → **PASS**. On **PASS, Mandate 2 distributes automatically — no further CEO approval.**

## DISCIPLINE ACKNOWLEDGED (and continued)
I will keep to what the CEO credited: no fabricated divergence (a hunt that surfaces a real structural hole reports that, not a manufactured number); a claim like point-7 is closed **by verifying it**, not marked FAIL for a missing wire that guards nothing. The bar for FAIL is a **reproducible** path-affecting bypass, demonstrated with a fixture — not a hypothetical.

## STATE
Standing by for VE's corrective commit. Nothing to attack until then. A2 and the canonical contract remain an independent track (extended suite + zero unexplained divergences + CEO approval). The freeze on that track holds; it is separate from this handoff gate.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
