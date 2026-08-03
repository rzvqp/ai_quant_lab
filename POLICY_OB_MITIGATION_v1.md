# POLICY — Order-Block Mitigation Reaction — canonical schema

**candidate_id: `CAND-0014`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. On the CEO-unblocked circularity-free order-flow primitives.

> **Distinct new family, not a blocked candidate.** A **mitigation** (a wick touch overlapping the OB body
> zone, cooldown-merged, visit-numbered) is a different reaction *type* than CAND-0011 (sweep-rejection =
> penetrate-and-close-back). It is NOT the blocked E015 (re-mitigation), which used the OLD **circular**
> construction (identical selection/measurement windows); `detect_mitigations` has the **anti-E010
> disjoint** windows (`selection_end=event_idx`; `measurement=[event_idx, +H)`) — E010 circularity
> impossible.

> **PART A** (entry mechanism) — two ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source (standing gap) — **UNSPECIFIED** (DEMO_BASELINE Part B
> is only for CEO-authorized pilots; this is not one).

| Field | Value |
|---|---|
| **policy_id** | `OB-MITIGATION` |
| **version** | `1.0` |
| **family** | `order_block_mitigation` (Module 5, circularity-free) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks` (OB formation, body zone), `detect_mitigations` (E015-convention touch: contiguous span overlapping the body zone, `VISIT_COOLDOWN=4`, visit-numbered, stops at first breaker), `track_breaker` (invalidation), `ReactionEvent` (`selection_end`/`measurement_start`/`measurement_end`, anti-E010 disjoint), `GROUP_A_HORIZON=20` — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (two ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB formation + mitigation scan on execution bars). |
| **activation** | An **order block** exists (`detect_order_blocks`: E010 impulse + body-engulf, no volume; zone = body `[min(Close,Open), max(Close,Open)]`). Block-confined. |
| **trigger** | The **first mitigation** at the OB zone (`detect_mitigations`, visit-numbered): a contiguous span whose range overlaps the body zone (`low<=zone_high ∧ high>=zone_low`), consecutive touches within `VISIT_COOLDOWN=4` merged into one visit; tracking stops at the first breaker. Classification uses **only** bars `≤ event_idx` (`selection_end=event_idx`) — no lookahead. Primary trigger = **visit 1** (first mitigation). |
| **entry** | **type:** reaction off the mitigated order block. **direction:** OB polarity — bullish OB → **long**, bearish → **short**. **moment:** `entry@next-open` (bar after `event_idx`; within `measurement_start=event_idx`, lookahead-safe). **reference price:** the OB body zone. |
| **invalidation** | Void before entry if the OB has become a **breaker** (`track_breaker`: a close beyond the whole-bar floor `Low_OB`/`High_OB`), if the mitigation is consumed, or at a block boundary. |
| **no_trade_rules** | No trade without a mitigation event. No trade after the OB flips to a breaker (blocked E010 thesis). No trade on visit ≥2 under the primary rule (visit-1 only; later visits a Statistician parameter). No trade before ATR14 is valid. |
| **expiry** | The setup expires on breaker inversion, consumption, or block boundary. `measurement_end=min(event_idx+GROUP_A_HORIZON, block_end)` bounds the reaction window, disjoint from selection. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Two ratified, lookahead-safe primitives with the anti-E010 disjoint-window
guarantee. Numeric items are Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (standing structural-SL gap)**

Fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists. (A structural Part B is
*composable* — e.g. stop at the ratified breaker floor `Low_OB`, target at the OB body far edge — as done
for the DEMO_BASELINE pilots; but Part B completion is authorized only for CEO-designated pilots, and this
candidate is not one.) Routed to the Statistician.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED** (composable from `Low_OB`/`High_OB`; not constructed here). |
| **exit** | **UNSPECIFIED.** |
| **management** | **UNSPECIFIED.** |

---

## Verdict — **PARTIALLY DEFINED**
A distinct, circularity-free reaction mechanism (first mitigation at an OB body zone) with a complete,
lookahead-safe entry from two ratified primitives; risk management routed to the Statistician.

## Handoff
- **Part A → Red Team, phase A** (confirm anti-E010 disjoint windows; distinct from CAND-0011 and blocked E015).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production — next candidate follows immediately.**
