# POLICY — Persistent Session Level × Order-Block Confluence (Primitive B) — **v1.0 (screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0036.** An aged, untouched persistent session extreme coinciding with an order block. Part A + one
frozen structural Part B; composition not invention; no lookahead. (OB primitives directive-UNBLOCKED as
anchors; E010/E013 hypotheses remain blocked.)

> **PRIMITIVE B + MANDATORY FILTER.** `compute_persistent_session_levels` (accumulating). **Filter — k=1.0
> primary, k=0.5 & k=2.0 sensitivities — declared, applied:** level eligible at `j` iff `|level.price −
> close[j−1]| ≤ k × atr14[j−1]` (ratified `atr14` + raw `close[j−1]`; **no lookahead**). Spec: v2.7.41,
> `537e495`, doc `62d2379`. Restores falsifiability, not volume → own selectivity below; trigger count is a
> HARD pre-performance report.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; session bar sets differ OANDA-historic vs MT5-live ~3h → backtest
> session level ≠ live; edge may not reproduce. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

| field | value · reason |
|---|---|
| **family** | `persistent_session_at_orderblock_confluence` (MK-04 sessions × Mod.5 via Module-7) |
| **OWN SELECTIVITY (beyond the filter)** | **the OB confluence** — only a filter-eligible persistent session level whose price sits inside a polarity-matched OB body qualifies. Resting institutional interest is a hard trigger reduction on top of the ATR filter. |
| **activation** | a filter-eligible Primitive-B `SessionLevel` (HIGH/LOW) AND an order block (`detect_order_blocks`) whose body zone contains the level, matching polarity. |
| **trigger** | **confluence** via `interactions.price_in_zone` — the session-level touch bar `j` lies inside the OB body zone (`OB.zone_lower ≤ price ≤ OB.zone_upper`), OB `confirmed ≤ j`. No lookahead. |
| **entry** | `next-open` after `j`. Direction = **fade the level**: HIGH → SHORT; LOW → LONG (must equal OB polarity). |
| **invalidation** | the deeper of touch extreme / OB breaker floor breached (Part B). |
| **no_trade_rules** | not filter-eligible → no trade; polarity mismatch → no trade; consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | until first touch (D7) or block end. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

| field | method · reason |
|---|---|
| **stop_loss** | **The deeper of OB breaker floor and touch extreme:** long → `min(Low_OB, low[j])`; short → `max(High_OB, high[j])`. Ratified OB level + raw OHLC, known at entry. |
| **exit** | **The OB body far edge** in the reaction direction: long → `OB.zone_upper`; short → `OB.zone_lower`. **Backstop / time-stop:** **20-bar `GROUP_A_HORIZON`** (live-valid; source session stale). |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond combined stop or OB far edge. No lookahead.
**FAIL-CLOSED:** stop = min/max of ratified OB floor + raw OHLC; target = ratified OB edge; time-stop =
live-valid; ineligible/mismatch → no trade. **Method stands.**

**W-incr note:** trigger ⊂ both session-touch and CAND-0011 (OB-rejection) → H0 = incremental value vs the better single.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_persistent_session_levels`, `count_active_persistent_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `detect_order_blocks`, `track_breaker` | `code/order_flow.py` | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `price_in_zone` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `atr14` (filter denominator), `session_of` | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it. Filter COMPOSED (`atr14` denominator; manifest `537e495`).*

## Verdict — **DEFINED (SCREENING_BASELINE)** · Primitive B, filter k=1.0 + own selectivity (OB confluence) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
