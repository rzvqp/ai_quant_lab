# POLICY — OB Mitigation × PDH/PDL Confluence — canonical schema

**candidate_id: `CAND-0016`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. A multi-primitive INTERACTION mechanism.

> **Distinct pair, not a variant.** New confluence pair **OB-mitigation × PDH/PDL-touch** — not CAND-0012
> (rejection × level; a different reaction *type*), not CAND-0014 (mitigation alone), not CAND-0001 (level
> alone). A mitigation (zone-overlap touch) coinciding with a daily-level test.

> **PART A** — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** — no ratified structural source (standing gap) — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `MITIG-LEVEL-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `mitigation_at_level_confluence` (Module 5 × MK-04 via Module 7) |

## Primitive source references — W10 (hashes re-verified @ commit)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_mitigations` (zone-overlap touch, cooldown, visit-numbered), `track_breaker`, `ReactionEvent` (anti-E010 disjoint) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches`, `LevelKind` — MK-04 | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) — Module 7, ratified | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB, levels, confluence on execution bars). |
| **activation** | Both structures active/known: an order block (`detect_order_blocks`, body zone) and a PDH/PDL level (`compute_prior_day_levels`, `available_idx`=current day's first bar, D3_bis reset). |
| **trigger** | **Direction-aligned same-bar confluence** (`interactions.confluence`): the bar is BOTH an OB mitigation (`detect_mitigations`, visit-1, `selection_end=event_idx`) AND a PDH/PDL touch (`detect_level_touches`) that **agree in direction** — bullish OB mitigation × PDL support → longs; bearish OB × PDH resistance → shorts. Classified from bars `≤` the bar — no lookahead. Each consume-once. |
| **entry** | **type:** confirmed reaction where an OB mitigation coincides with a daily-level test. **direction:** the agreed polarity. **moment:** `entry@next-open`. **reference price:** the OB zone ∩ level. |
| **invalidation** | Void before entry if the OB has become a breaker, either constituent is consumed, or a block boundary intervenes. No confluence / direction disagreement → no setup. |
| **no_trade_rules** | No trade without same-bar direction-aligned confluence. No trade when OB polarity and level side disagree. No trade after breaker/consumption. No trade on the first day of a block (D3_bis). No trade on OB visit ≥2 (visit-1 only). |
| **expiry** | Expires when either constituent expires (OB breaker/consumption; level consumption/day boundary), whichever first. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of an anti-E010 circularity-free mitigation with a
ratified level, via the ratified locator; lookahead-safe.

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; not a DEMO pilot). Routed to Statistician.

---

## Verdict — **PARTIALLY DEFINED**
## Handoff — Part A → Red Team (A); Part B → Statistician (structural risk + numeric params).
**Continuous production — next candidate follows immediately.**
