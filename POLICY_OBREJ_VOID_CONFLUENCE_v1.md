# POLICY — OB Sweep-Rejection × Liquidity-Void Confluence — canonical schema

**candidate_id: `CAND-0018`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. A multi-primitive INTERACTION mechanism.

> **Distinct pair, not a variant.** New confluence pair **OB-sweep-rejection × liquidity-void** — a
> rejection occurring on a bar that opened out of a price discontinuity (gap-driven sweep-rejection). Not
> CAND-0011 (rejection alone), not CAND-0008 (void × displacement — a different second primitive), not
> CAND-0004 (void alone, NCT).

> **PART A** — three ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** — no ratified structural source (standing gap) — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `OBREJ-VOID-CONFLUENCE` |
| **version** | `1.0` |
| **family** | `rejection_at_discontinuity_confluence` (Module 5 rejection × Module 5 void via Module 7) |

## Primitive source references — W10 (hashes re-verified @ commit)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks`, `detect_rejections` (D6 sweep-reject), `track_breaker`, `ReactionEvent` (anti-E010 disjoint) — Module 5, RATIFIED | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `code/order_block_void.py` | `detect_liquidity_voids`, `LiquidityVoid` (`at_idx`=c, hybrid temporal/size), `VOID_SIZE_THRESHOLD=1.20` — RATIFIED | `6ec7adbfd3bbaab2d4c1e35f1ad6de2631875319bb5312e90fba572ded32b921` |
| `code/interactions.py` | `to_mask`, `confluence` (same-bar AND) — Module 7, ratified | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_block_void.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (three ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB, void, confluence on execution bars). |
| **activation** | An order block (`detect_order_blocks`, body zone, block-confined); liquidity voids detected on `c→c+1` transitions (`detect_liquidity_voids`). |
| **trigger** | **Same-bar confluence** (`interactions.confluence`): an OB sweep-rejection (`detect_rejections`, `selection_end=event_idx`) on a bar `i` that is the **downstream bar of a liquidity void** (a void with `at_idx = i-1`, i.e. bar `i` opened out of the gap). Both known at bar `i` (the void at `i-1 < i`; the rejection classified from bars `≤ i`) — no lookahead. Consume-once. |
| **entry** | **type:** gap-driven sweep-rejection at an order block. **direction:** OB polarity — bullish OB → **long**, bearish → **short**. **moment:** `entry@next-open`. **reference price:** the OB zone / swept edge. |
| **invalidation** | Void before entry if the OB has become a breaker (`track_breaker`), the rejection is consumed, or a block boundary intervenes. No void on the rejection bar's open → no setup (that is CAND-0011, not this). |
| **no_trade_rules** | No trade unless the rejection bar opened out of a liquidity void. No trade after the OB flips to a breaker. No trade after consumption. No trade across a block boundary. |
| **expiry** | Expires on breaker inversion, consumption, or block boundary. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Same-bar confluence of a ratified anti-E010 rejection with a ratified void
(via the void's own downstream bar), through the ratified locator; lookahead-safe.

## PART B — RISK MANAGEMENT — **UNSPECIFIED** (standing structural-SL gap; not a DEMO pilot). Routed to Statistician.

---

## Verdict — **PARTIALLY DEFINED**
## Handoff — Part A → Red Team (A); Part B → Statistician (structural risk + numeric params).
**Continuous production — next candidate follows immediately.**
