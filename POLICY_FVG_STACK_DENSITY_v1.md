# POLICY — Stacked-FVG Density Reaction — canonical schema

**candidate_id: `CAND-0010`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. **A multi-primitive INTERACTION mechanism** — imbalance *density*.

> **Distinct, not a variant.** CAND-0003 is a single-FVG CE-50 reaction. CAND-0005 (BPR) is an
> **opposite-polarity** FVG overlap. This candidate is a **same-polarity** FVG *stack*: a CE-50 reaction
> whose price also sits inside ≥1 **other** same-polarity FVG zone — an imbalance-density condition
> (concentrated demand/supply), a structural mechanism, not a parameter on CAND-0003.

> **PART A** (entry mechanism) — ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `FVG-STACK-DENSITY` |
| **version** | `1.0` |
| **family** | `imbalance_density` (interaction: MK-03 zones via Module 7) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/imbalance_mechanics.py` | `detect_fvgs`, `FairValueGap` (`upper`, `lower`, `ce_50`, `confirmed_idx=i+1`, `FVGKind`), `detect_fvg_reactions` (CE-50 Q6, consume-once Q5) — MK-03, CLOSED | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `code/interactions.py` | `price_in_any_zone` (price ↔ multiple zones), `confluence`, `to_mask` — Module 7, ratified generic locator | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/imbalance_mechanics.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (FVG detection, zone membership, reaction on execution bars). |
| **activation** | ≥2 same-polarity FVGs exist and are known (`detect_fvgs`, each `confirmed_idx=i+1`, block-confined). The "other" FVG zones considered are only those already confirmed (`confirmed_idx ≤` the current bar) — no future FVGs. |
| **trigger** | A CE-50 reaction on one FVG (`detect_fvg_reactions`, consume-once Q5) whose touch price **also lies inside ≥1 other same-polarity FVG zone**: `price_in_any_zone(price, [other bullish FVG zones])` True at the CE-50-touch bar (symmetric for bearish). Expressed as `confluence([ce50_touch_mask, in_other_samepolarity_zone_mask])`, same bar — no lookahead (all other zones are prior/confirmed). |
| **entry** | **type:** reaction at stacked (concentrated) imbalance. **direction:** the stacked polarity — bullish stack → **long**, bearish stack → **short**. **moment:** `entry@next-open` (bar after the CE-50-touch bar; lookahead-safe). **reference price:** `ce_50` / the overlapping FVG zones. |
| **invalidation** | Void before entry if the reacting FVG is consumed (Q5) or inverted (Q4), if no other same-polarity FVG zone contains the touch price (no stack), or at a block boundary (Q2). |
| **no_trade_rules** | No trade on a single isolated FVG (no stack — that is CAND-0003's case). No trade when the touch price falls only in opposite-polarity zones (that is BPR territory, CAND-0005). No trade after consumption/inversion; none across a block boundary. |
| **expiry** | Expires on consumption (Q5), inversion (Q4), or block boundary (Q2) of the reacting FVG. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of a ratified CE-50 reaction with ratified FVG-zone
density (`price_in_any_zone` over confirmed same-polarity zones); lookahead-safe. Numeric items are
Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the outermost stacked FVG's far edge), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Not constructed. |
| **management** | **UNSPECIFIED.** Not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct interaction mechanism (same-polarity imbalance density) with a complete, lookahead-safe entry
from ratified primitives; risk management unspecified for lack of a ratified structural source.

## Handoff
- **Part A → Red Team, phase A** (check the density condition is genuinely distinct from single-FVG
  reaction and from opposite-polarity BPR).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production.**
