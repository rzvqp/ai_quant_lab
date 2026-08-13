# RED TEAM — RANGE DECISION · +5 handoff conditions + multi-axial router check
### RT-AUDIT-MEAS-0007 · CEO ruling "block RANGE, continue the rest" — handoff verification extended 12 → 17 (+router form)
**Date:** 2026-08-13 · **Auditor:** Red Team · **Trigger:** CEO decision on the RANGE defect. Extends the VE_HANDOFF verification (RT-AUDIT-MEAS-0006). **No engine modified; no repair; no real data.** Preparable reconnaissance only — VE is still building the corrected artifact; nothing here is a PASS.

## DECISION_RECEIVED ✅
**Block RANGE, continue the rest.** Strategies that need a real RANGE regime get `eligibility = FALSE` + `reason_code = TRUE_RANGE_NOT_IDENTIFIABLE`; they never reach EV. Everything else proceeds: N1–N6, EV, Risk Manager, LIVE_SHADOW, and routing for **TREND_UP, TREND_DOWN, MOMENTUM, COMPRESSION, BREAKOUT_TRANSITION**.

## FIVE ADDED HANDOFF CONDITIONS (13→17; all must pass, `AND` with the original 12)
| # | condition | how I will verify (adversarially) |
|---|---|---|
| 13 | **range strategies are fail-closed** | a range-requiring strategy returns `eligibility=FALSE`, `reason_code=TRUE_RANGE_NOT_IDENTIFIABLE`, and **never** an EV call — proven by tracing the path, not by a passing happy-path test |
| 14 | **`StructBand.RANGE` and `Direction.NEUTRAL` cannot activate them** | inject RANGE / NEUTRAL context and assert **no** range strategy becomes eligible; assert these two enum members map to the fail-closed reason, not to a live route |
| 15 | **reason_code is PERSISTED, not just returned** | the `TRUE_RANGE_NOT_IDENTIFIABLE` code is written to the decision record / audit trail (queryable later), not only present in the return value that a caller may drop |
| 16 | **the other families work** | TREND_UP/TREND_DOWN/MOMENTUM/COMPRESSION/BREAKOUT_TRANSITION each route and reach EV under their own regimes — the block is surgical, not a blanket kill |
| 17 | **NO fallback or implicit routing to range** (the most important) | enumerate **every** path to eligibility and prove none defaults, falls back, or coerces to a range strategy — no `else: range`, no default-arm, no "nearest regime", no direct-construction bypass |

**Condition 17 is the adversarial priority.** This is the bypassable-guard pattern I have found repeatedly (E2E-L2 direct-construction bypass; `compare()` never wired). The hunt: a range strategy reaching eligibility **indirectly** — via a default/`else` arm, an enum coerced to a nearby band, a direct object construction that skips the gate, or a router that treats "no other match" as "route to range." A fail-closed rule that only fires on the front-door path is not fail-closed.

## ROUTER FORM — MULTI-AXIAL, no global precedence (CEO)
`COMPRESSED and UP and STRONG` must be able to activate **trend AND compression strategies simultaneously.** I verify VE routes on the **independent axes**, and that **no hidden precedence / partition** silently drops one axis — a concealed precedence rule is **disguised selection** (Statistician-flagged).

### ★ CONCRETE LEAD (pre-existing precedence to check VE does NOT inherit)
`ai_trader/market_intelligence/expansion.py::_state_for` collapses the volatility axis into a **single mutually-exclusive** `ExpansionState` with an **internal precedence**: *"EXPANDING takes priority over COMPRESSED when both are somehow true at once"* — a bar that is both `compress` (14–50-bar context) and `disp` (this bar) is forced to `EXPANDING`, **dropping COMPRESSED**. If VE's multi-axial router keys on this collapsed `.state`, then whenever displacement co-occurs, **compression strategies can never fire** — an implicit partition = disguised selection, exactly what the CEO forbids. **Mitigating fact:** the reading still carries the **raw** `is_compressed`/`is_displacement` flags, so the correct multi-axial router reads the **raw axes**, not `.state`. **Handoff check:** confirm VE's router consumes the raw per-axis flags and does **not** route on any precedence-collapsed single-state label (here or elsewhere). This is a lead for where to attack, not yet a verdict — the corrected artifact is not built.

## STATE (unchanged)
- **VE_HANDOFF = FAIL** (current). A2 (strict geometry) and A5 (T17 five-identity incl. strategy + `require_comparable` enforcement) remain **open**; the 17 range/handoff conditions are unverified because the artifact is not delivered. **VE_HANDOFF_PASS is forbidden until the amendment is fully applied.**
- **I attack the CORRECTED evaluator, not `3344bff`.** **Test 18A rewritten** — the target-gap (`reward ≤ 0`) now expects **INVALID_EXECUTION** (was exit-at-entry), plus the two boundary cases (`open == stop`, `open == target`).
- **Freeze holds/widens:** all asymmetric-variant results (incl. S3 −0.17) are PROVISIONAL / NON-COMPARABLE.

## HANDOFF → CEO / VE
1. **VE:** implement RANGE fail-closed (conditions 13–17), reason_code **persisted**, and a **multi-axial** router with **no** precedence-collapsed axis (do **not** route on `ExpansionState.state`; use the raw flags).
2. **Red Team on delivery:** run the 17 handoff conditions + the multi-axial no-partition proof (condition 17 + router form as the two adversarial priorities), alongside the corrected-evaluator suite (strict geometry, revised Test 18) and the A5 five-identity/`require_comparable` re-check. Emit VE_HANDOFF_PASS only if **all** pass and the amendment is fully applied.

Red Team designed no remedy, modified no engine, ran no data on the market, changed nothing outside `red_team/`.
