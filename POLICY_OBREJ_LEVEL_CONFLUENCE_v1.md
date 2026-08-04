# POLICY — OB Sweep-Rejection × PDH/PDL Confluence — canonical schema

**candidate_id: `CAND-0012`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. **A multi-primitive INTERACTION mechanism** on the CEO-unblocked circularity-free
order-flow reaction primitives.

> **Distinct, not a variant.** CAND-0011 is the OB sweep-rejection alone; CAND-0007 is level × FVG-CE50.
> This candidate is level × **OB-sweep-rejection** — a different second reaction primitive (order-flow
> rejection, not FVG) → a different confirmation mechanism.

> **PART A** (entry mechanism) — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `OBREJ-LEVEL-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `rejection_at_level_confluence` (interaction: Module 5 × MK-04 via Module 7) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections` (D6 sweep-reject), `track_breaker`, `ReactionEvent` (anti-E010 disjoint windows) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/institutional_levels.py` | `compute_prior_day_levels`, `detect_level_touches` (PDH/PDL touch, D7), `LevelKind` — MK-04 | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) — Module 7, ratified generic locator | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB formation, rejection scan, levels, confluence on execution bars). |
| **activation** | Both structures active/known: (1) an order block (`detect_order_blocks`, body zone, block-confined); (2) a PDH/PDL level (`compute_prior_day_levels`, `available_idx`=current day's first bar, D3_bis reset). |
| **trigger** | **Direction-aligned same-bar confluence** (`interactions.confluence`): the bar is BOTH an OB sweep-rejection (`detect_rejections`, `selection_end=event_idx`) AND a PDH/PDL touch (`detect_level_touches`) that **agree in direction** — `confluence([bullish_OB_rejection_mask, PDL_support_touch_mask])` for longs; symmetric (bearish OB rejection × PDH resistance) for shorts. Both classified from bars `≤` the bar — no lookahead. Each constituent consume-once. |
| **entry** | **type:** confirmed rejection at a confluent level. **direction:** the agreed direction — bullish OB rejection × PDL → **long**; bearish OB rejection × PDH → **short**. **moment:** `entry@next-open` (bar after the confluence bar; lookahead-safe). **reference price:** the confluence (OB body zone ∩ level). |
| **invalidation** | Void before entry if the OB has become a breaker (`track_breaker`), either constituent is consumed, or a block boundary intervenes. **No confluence, or direction disagreement → no setup.** |
| **no_trade_rules** | No trade without same-bar direction-aligned confluence. No trade when OB polarity and level side disagree. No trade after the OB flips to breaker (blocked E010 thesis). No trade after either constituent is consumed. No trade on the first day of a block (D3_bis). |
| **expiry** | Expires when either constituent expires — OB breaker/consumption, level consumption (D7), or block boundary — whichever first. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of two ratified reaction primitives (one anti-E010
circularity-free) plus a ratified level primitive; lookahead-safe. Numeric items are Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the swept `Low_OB` / the level), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Not constructed. |
| **management** | **UNSPECIFIED.** Not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct interaction mechanism (OB sweep-rejection confirmed at a PDH/PDL level) with a complete,
lookahead-safe entry from three ratified primitives; risk management unspecified for lack of a ratified
structural source.

## Handoff
- **Part A → Red Team, phase A.**
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production — next candidate follows immediately.**
