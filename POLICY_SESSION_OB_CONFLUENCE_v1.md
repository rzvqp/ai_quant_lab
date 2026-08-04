# POLICY — Session Level × Order-Block Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0031.** Confluence of a prior-session High/Low (Primitive A) with a ratified `order_flow` order
block (Mod.5; OB primitives directive-UNBLOCKED as anchors, E010/E013 hypotheses remain blocked). Part A
+ one frozen structural Part B; composition not invention; no lookahead.

> **Uses PRIMITIVE A only** (2-3 active). **Primitive B NOT used** (saturation ruling). No filter needed.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest session level is NOT the same price as live; edge may not reproduce. The SESSION leg carries
> the misalignment. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

Mechanism: a session extreme that coincides with an order block — the level marks where price reverses,
the OB the resting institutional interest that reverses it.

| field | value · reason |
|---|---|
| **family** | `session_at_orderblock_confluence` (MK-04 sessions × Mod.5 via Module-7) |
| **timeframes_used** | single-TF price + session clock |
| **activation** | a Primitive-A `SessionLevel` (SESSION_HIGH/LOW) available AND an order block (Mod.5 `detect_order_blocks`) whose body zone contains the level, matching polarity (bullish OB at a SESSION_LOW; bearish at a SESSION_HIGH). |
| **trigger** | **confluence** via `interactions.price_in_zone` — the session-level touch bar `j` lies inside the OB body zone (`OB.zone_lower ≤ price ≤ OB.zone_upper`), OB `confirmed ≤ j`. |
| **entry** | `next-open` after `j`. Direction = **fade the level**: SESSION_HIGH → SHORT; SESSION_LOW → LONG (must equal OB polarity else no confluence). |
| **invalidation** | the deeper of the touch extreme / OB breaker floor is breached (Part B). |
| **no_trade_rules** | level consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target, or polarity mismatch. |
| **expiry** | touch within `[available_idx, expiry_idx]`; else lapses. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = level × order-block confluence. The OB supplies its ratified breaker floor (as in
CAND-0011/0014); the deeper of it and the touch extreme is the invalidation.

| field | method · reason |
|---|---|
| **stop_loss** | **The deeper of the OB breaker floor and the touch extreme:** long → `min(Low_OB, low[j])`; short → `max(High_OB, high[j])`. **Reason:** the reaction fails when the OB breaks (`track_breaker`); the touch wick can be deeper. Ratified OB level + raw OHLC, known at entry. |
| **exit** | **The OB body far edge** in the reaction direction (as in CAND-0011/0014): long → `OB.zone_upper`; short → `OB.zone_lower`. **Backstop / time-stop:** the **session boundary** = `expiry_idx`, session-native live-valid. |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the combined stop or the OB far edge. No
lookahead. **FAIL-CLOSED:** stop = min/max of ratified OB floor + raw OHLC; target = ratified OB edge;
time-stop = session boundary. Composable — **method stands**.

**W-incr note:** trigger ⊂ both CAND-0027 (session touch) and CAND-0011 (OB-rejection) → H0 = incremental
value vs the better of the two singles.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_session_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `detect_order_blocks`, `track_breaker` | `code/order_flow.py` | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `price_in_zone` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `session_of` (session clock) | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
