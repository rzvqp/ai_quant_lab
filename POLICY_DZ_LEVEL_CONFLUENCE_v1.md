# POLICY — Demand-Zone Re-entry × PDH/PDL Confluence — canonical schema

**candidate_id: `CAND-0019`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. A multi-primitive INTERACTION mechanism.

> **Distinct pair, not a variant.** New confluence pair **demand-zone re-entry × PDH/PDL-touch** — a
> non-consumable full-bar zone re-entry coinciding with a daily-level test. Not CAND-0013 (zone alone),
> not CAND-0001 (level alone), not CAND-0012/0016 (OB-body reactions × level). Completes the
> `× level` confluence set alongside FVG / rejection / mitigation.

> **PART A** — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** — no ratified structural source (standing gap) — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `DZ-LEVEL-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `zone_at_level_confluence` (Module 5 × MK-04 via Module 7) |

## Primitive source references — W10 (hashes re-verified @ commit)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_demand_zones`, `DemandZone` (full-bar `[Low,High]`, non-consumable) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches`, `LevelKind` — MK-04 | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/interactions.py` | `price_in_zone`, `to_mask`, `confluence` (same-bar AND) — Module 7, ratified | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (demand zones, levels, confluence on execution bars). |
| **activation** | A demand/supply zone (`detect_demand_zones`, full-bar, block-confined) and a PDH/PDL level (`compute_prior_day_levels`, `available_idx`=current day's first bar, D3_bis reset). |
| **trigger** | **Direction-aligned same-bar confluence** (`interactions.confluence`): the bar is BOTH inside a same-polarity demand/supply zone (`price_in_zone`) AND a PDH/PDL touch (`detect_level_touches`) that **agree in direction** — bullish demand zone × PDL support → longs; bearish supply zone × PDH resistance → shorts. Zone membership same-bar; level touch classified from bars `≤` the bar — no lookahead. |
| **entry** | **type:** confirmed reaction where a demand/supply zone coincides with a daily level. **direction:** the agreed polarity. **moment:** `entry@next-open`. **reference price:** the zone ∩ level. |
| **invalidation** | Void before entry if the level is consumed (D7) or a block boundary intervenes. (Demand zone non-consumable.) No confluence / direction disagreement → no setup. |
| **no_trade_rules** | No trade without same-bar direction-aligned confluence. No trade when zone polarity and level side disagree. No trade after level consumption. No trade on the first day of a block (D3_bis). |
| **expiry** | Expires on level consumption / day boundary / block boundary. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of a ratified non-consumable zone membership and a
ratified level, via the ratified locator; lookahead-safe.

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; not a DEMO pilot). Routed to Statistician.

---

## Verdict — **PARTIALLY DEFINED**
## Handoff — Part A → Red Team (A); Part B → Statistician (structural risk + numeric params).
**Continuous production — next candidate follows immediately.**
