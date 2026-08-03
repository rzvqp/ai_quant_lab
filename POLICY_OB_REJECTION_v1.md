# POLICY — Order-Block Sweep-Rejection — canonical schema

**candidate_id: `CAND-0011`.** Design artifact only. No execution, no data, no numeric parameter chosen,
no method constructed. First candidate on the CEO-unblocked, **circularity-free** order-flow reaction
primitives (ruling: the order-block *family* block covers the old circular candidates E010/E013/E015/E016,
NOT the re-engineered `order_flow.py` primitives, whose selection/measurement windows are disjoint by
construction).

> **Distinct new family, not a blocked candidate.** This is a **sweep-rejection** reaction (D6 wick-sweep +
> close back inside) at an order-block body zone — a different reaction *type* than the blocked E010
> (breaker), E015 (re-mitigation), or E013/E016. The anti-E010 disjoint-window construction (`selection_end
> = event_idx`; `measurement = [event_idx, +H)`) makes the E010 circularity impossible.

> **PART A** (entry mechanism) — two ratified, lookahead-safe primitives — **FULLY DEFINED.**
> **PART B** (risk) — no ratified structural source — **UNSPECIFIED.**

| Field | Value |
|---|---|
| **policy_id** | `OB-SWEEP-REJECTION` |
| **version** | `1.0` |
| **family** | `order_block_rejection` (Module 5, circularity-free) |

## Primitive source references — W10 (cross-repo grounding)
- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1` · **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6`

| source_file | primitive(s) | source_hash (sha256 @ commit) |
|---|---|---|
| `code/order_flow.py` | `detect_order_blocks` (OB formation: E010 impulse + body-engulf, no volume), `OrderBlock` (body zone), `detect_rejections` (D6 sweep-reject), `track_breaker` (E010 inversion, invalidation), `ReactionEvent` (`selection_end`/`measurement_start`/`measurement_end`, anti-E010 disjoint) — Module 5, RATIFIED (Statistician v2.6.1→v2.7.9) | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/order_flow.py | sha256sum`.

---

## PART A — ENTRY MECHANISM (two ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric — Statistician; not chosen.* |
| **timeframes_used** | **M15** (OB formation + rejection scan on execution bars). |
| **activation** | An **order block** exists (`detect_order_blocks`): impulse bar (E010: `range>1.5×ATR14[i-1]` ∧ `|close-open|>=0.5×range`) engulfing the prior opposite bar's body; zone = the OB **body** `[min(Close,Open), max(Close,Open)]`. Block-confined. |
| **trigger** | A **sweep-rejection** at the OB zone (`detect_rejections`, D6): bullish OB — `low[i] < zone_lower AND close[i] > zone_lower` (wick sweeps below the body floor, closes back above); bearish OB symmetric at `zone_upper`. Classification uses **only** bars `≤ event_idx` (`selection_end=i`) — no lookahead. Consume-once (visit-numbered; tracking stops at the first breaker). |
| **entry** | **type:** rejection reaction (the OB holds after a liquidity sweep). **direction:** OB polarity — bullish OB → **long**, bearish OB → **short**. **moment:** `entry@next-open` (bar after `event_idx`; lookahead-safe, within `measurement_start=event_idx`). **reference price:** the OB body zone / the swept edge. |
| **invalidation** | Void before entry if the OB has become a **breaker** (`track_breaker`: a close beyond `Low_OB`/`High_OB`, the whole-bar floor), if the rejection is already consumed, or at a block boundary. |
| **no_trade_rules** | No trade without a sweep-rejection event. No trade after the OB flips to a breaker (that is the blocked E010 thesis, excluded). No trade after consumption. No trade before ATR14 is valid. |
| **expiry** | The setup expires on breaker inversion, consumption, or block boundary. `measurement_end = min(event_idx+H, block_end)` bounds the reaction window (H = Group-A horizon = 20), disjoint from selection. |
| **min_trades** (per policy & per regime) | *Numeric — Statistician.* |

**PART A status: complete.** Two ratified, lookahead-safe primitives with the anti-E010 disjoint-window
guarantee baked into `ReactionEvent`. Numeric items are Statistician parameters.

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap: fixed-ATR/RR disqualified; no ratified structural stop/exit primitive exists.

| Field | Declaration |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop (e.g. beyond the swept whole-bar floor `Low_OB`), method not value. Absent → not constructed. |
| **exit** | **UNSPECIFIED.** Not constructed. |
| **management** | **UNSPECIFIED.** Not constructed. |

---

## Verdict — **PARTIALLY DEFINED**
A distinct, circularity-free reaction mechanism (sweep-rejection at an OB body zone) with a complete,
lookahead-safe entry from two ratified primitives; risk management unspecified for lack of a ratified
structural source.

## Handoff
- **Part A → Red Team, phase A** (confirm the anti-E010 disjoint windows and that this is a distinct
  reaction type from the blocked E010/E015).
- **Part B → Statistician, specification request** (structural stop/exit/management + numeric params).

**Continuous production — next candidate follows immediately.**
