# POLICY — OB Sweep-Rejection × FVG-CE50 Confluence — canonical schema

**candidate_id: `CAND-0015`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. A multi-primitive INTERACTION mechanism.

> **Distinct pair, not a variant.** New confluence pair **OB-sweep-rejection × FVG-CE50-reaction** — not
> CAND-0007 (level × FVG), not CAND-0012 (rejection × level), not CAND-0011 (rejection alone). Two
> independent imbalance-reaction events must co-fire and agree in direction.

> **PART A** — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** — no ratified structural source (standing gap) — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `OBREJ-FVG-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `rejection_imbalance_confluence` (Module 5 × MK-03 via Module 7) |

## Primitive source references — W10 (hashes re-verified @ commit)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections` (D6 sweep-reject), `track_breaker`, `ReactionEvent` (anti-E010 disjoint) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/imbalance_mechanics.py` | `detect_fvgs`, `detect_fvg_reactions` (CE-50 Q6, consume-once Q5), `FVGKind` — MK-03, CLOSED | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) — Module 7, ratified | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB, FVG, confluence on execution bars). |
| **activation** | Both structures active/known: an order block (`detect_order_blocks`, body zone, block-confined) and a 3-bar FVG (`confirmed_idx=i+1`, block-confined). |
| **trigger** | **Direction-aligned same-bar confluence** (`interactions.confluence`): the bar is BOTH an OB sweep-rejection (`detect_rejections`, `selection_end=event_idx`) AND an FVG CE-50 touch (`detect_fvg_reactions`) that **agree in direction** — bullish OB rejection × bullish FVG → longs; bearish × bearish → shorts. Both classified from bars `≤` the bar — no lookahead. Each consume-once. |
| **entry** | **type:** confirmed reaction where a rejection and an imbalance coincide. **direction:** the agreed polarity — bullish → **long**, bearish → **short**. **moment:** `entry@next-open`. **reference price:** the co-located OB zone ∩ FVG zone. |
| **invalidation** | Void before entry if the OB has become a breaker (`track_breaker`), either constituent is consumed/inverted (Q4/Q5), or a block boundary intervenes. No confluence or direction disagreement → no setup. |
| **no_trade_rules** | No trade without same-bar direction-aligned confluence. No trade when OB and FVG polarity disagree. No trade after breaker/consumption/inversion. No trade across a block boundary. |
| **expiry** | Expires when either constituent expires (OB breaker/consumption; FVG consumption/inversion; block boundary), whichever first. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of two ratified reaction primitives (one anti-E010
circularity-free) plus the ratified locator; lookahead-safe.

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; not a DEMO pilot). Routed to Statistician.

---

## Verdict — **PARTIALLY DEFINED**
## Handoff — Part A → Red Team (A); Part B → Statistician (structural risk + numeric params).
**Continuous production — next candidate follows immediately.**
