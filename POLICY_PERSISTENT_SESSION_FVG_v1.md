# POLICY — Persistent Session Level × FVG-CE50 Confluence (Primitive B) — **v1.0 (screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0035.** An aged, untouched persistent session extreme reinforced by an FVG at the same price.
Part A + one frozen structural Part B; composition not invention; no lookahead.

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
| **family** | `persistent_session_imbalance_confluence` (MK-04 sessions × MK-03 via Module-7) |
| **OWN SELECTIVITY (beyond the filter)** | **the FVG confluence** — only a filter-eligible persistent session level with a polarity-matched FVG at it qualifies. The imbalance is a hard trigger reduction on top of the ATR filter. |
| **activation** | a filter-eligible Primitive-B `SessionLevel` (HIGH/LOW) AND a polarity-matched FVG (bullish at a LOW, bearish at a HIGH) at the level. |
| **trigger** | **confluence** via `interactions.price_in_zone` — the session-level touch bar `j` lies inside the FVG zone, FVG `confirmed_idx ≤ j`. No lookahead. |
| **entry** | `next-open` after `j`. Direction = **fade the level**: HIGH → SHORT; LOW → LONG (must equal FVG polarity). |
| **invalidation** | the deeper of touch extreme / FVG far edge breached (Part B). |
| **no_trade_rules** | not filter-eligible → no trade; polarity mismatch → no trade; consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | until first touch (D7) or block end. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond BOTH — the deeper floor:** short → `max(high[j], FVG.upper)`; long → `min(low[j], FVG.lower)`. Raw OHLC + ratified FVG edge, known at entry. |
| **exit** | **The FVG near edge** in the reaction direction (reaction target). **Backstop / time-stop:** **20-bar `GROUP_A_HORIZON`** (live-valid; source session stale). |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond combined stop or FVG-edge target. No lookahead.
**FAIL-CLOSED:** stop = min/max of raw OHLC + ratified FVG edge; target = ratified FVG edge; time-stop =
live-valid; ineligible/mismatch → no trade. **Method stands.**

**W-incr note:** trigger ⊂ both session-touch and CAND-0003 (FVG) → H0 = incremental value vs the better single.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_persistent_session_levels`, `count_active_persistent_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| FVG / `ce_50` | `code/imbalance_mechanics.py` | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `price_in_zone` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `atr14` (filter denominator), `session_of` | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it. Filter COMPOSED (`atr14` denominator; manifest `537e495`).*

## Verdict — **DEFINED (SCREENING_BASELINE)** · Primitive B, filter k=1.0 + own selectivity (FVG confluence) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
