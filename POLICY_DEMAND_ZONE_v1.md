# POLICY — Demand/Supply-Zone Re-entry Reaction — canonical schema

**candidate_id: `CAND-0013`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. A CEO-unblocked order-flow family.

> **Distinct object, not a variant of the OB candidates.** A `DemandZone` is the **full anchor bar
> `[Low, High]`** (wick-inclusive superset of the OB body) and is **NON-consumable** — a different object
> and a different reaction semantics than the OB body zone (consumable) used by CAND-0011/0012.

> **PART A** (entry mechanism) — two ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `DEMAND-ZONE-REENTRY` |
| **version** | `1.0` |
| **family** | `demand_supply_zone_reaction` (Module 5, non-consumable zone) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_demand_zones`, `DemandZone` (`zone_lower`=Low, `zone_upper`=High of anchor bar; non-consumable), `detect_order_blocks` (formation anchor) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/interactions.py` | `price_in_zone` (per-bar price ↔ zone membership) — Module 7, ratified generic locator | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (two ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (zone formation + re-entry on execution bars). |
| **activation** | A **demand/supply zone** exists (`detect_demand_zones`, per OB formation anchor bar; `zone = [Low, High]` of that bar, wick-inclusive; polarity = OB kind; **non-consumable**). Block-confined; known from the anchor bar forward (lookahead-safe). |
| **trigger** | The **first re-entry** of the zone after formation: the first bar `j > formation_idx` (same block) where `price_in_zone(close/low-high, zone_lower, zone_upper)` is True — for a bullish (demand) zone, `low[j] <= zone_upper AND high[j] >= zone_lower` (the bar overlaps the zone). Membership evaluated on bar `j` only — no lookahead. **First re-entry** is the primary trigger to avoid serial correlation (the zone is non-consumable; whether later re-entries also fire is a Statistician parameter, not chosen here). |
| **entry** | **type:** reaction off the demand/supply zone. **direction:** zone polarity — demand (bullish) → **long**, supply (bearish) → **short**. **moment:** `entry@next-open` (bar after the re-entry bar; lookahead-safe). **reference price:** the zone `[zone_lower, zone_upper]`. |
| **invalidation** | Void before entry if a block boundary intervenes before any re-entry. (The zone is non-consumable and has no ratified breaker/flip of its own — it is a passive zone; a decisive close beyond it is not a ratified invalidation event for `DemandZone`, so none is asserted — see no_trade.) |
| **no_trade_rules** | No trade without a zone re-entry. First-re-entry only under this policy's primary rule (later re-entries deferred to a Statistician parameter). No trade across a block boundary. No trade before the anchor bar. |
| **expiry** | The setup (awaiting first re-entry) expires at the block boundary. Non-consumable zone → no consumption event; expiry is the block boundary or the first re-entry firing. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Two ratified, lookahead-safe primitives; a distinct (full-bar, non-consumable)
zone object with a first-re-entry trigger. Numeric items (re-entry policy, regimes, min_trades) are
Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the zone's far edge), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Not constructed. |
| **management** | **UNSPECIFIED.** Not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct-object mechanism (non-consumable full-bar demand/supply zone re-entry) with a complete,
lookahead-safe entry from two ratified primitives; risk management unspecified for lack of a ratified
structural source.

## Handoff
- **Part A → Red Team, phase A** (confirm the full-bar non-consumable zone is distinct from the OB body
  candidates, and the first-re-entry trigger).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params,
  incl. the re-entry policy for the non-consumable zone).

**Continuous production — next candidate follows immediately.**
