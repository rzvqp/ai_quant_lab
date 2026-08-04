# POLICY — Persistent Session Level × PDH/PDL Confluence (Primitive B) — **v1.0 (screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0034.** An aged, untouched persistent session extreme coinciding with a prior-day level. Part A +
one frozen structural Part B; composition not invention; no lookahead.

> **PRIMITIVE B + MANDATORY FILTER.** `compute_persistent_session_levels` (accumulating). **Filter — k=1.0
> primary, k=0.5 & k=2.0 sensitivities — declared, applied:** level eligible at `j` iff `|level.price −
> close[j−1]| ≤ k × atr14[j−1]` (ratified `atr14` + raw `close[j−1]`; **no lookahead**). Spec: v2.7.41,
> `537e495`, doc `62d2379`. Restores falsifiability, not volume → own selectivity below; trigger count is a
> HARD pre-performance report.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; session bar sets differ OANDA-historic vs MT5-live ~3h → backtest
> session level ≠ live. The session leg carries the misalignment (day leg is feed-robust). Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

| field | value · reason |
|---|---|
| **family** | `persistent_session_at_daylevel_confluence` (MK-04 sessions × MK-04 PDH/PDL via Module-7) |
| **OWN SELECTIVITY (beyond the filter)** | **the PDH/PDL confluence** — only a filter-eligible persistent session level that ALSO coincides (within ratified `dilate`) with a prior-day level qualifies. The second independent reference is a hard trigger reduction on top of the ATR filter. |
| **activation** | a filter-eligible Primitive-B `SessionLevel` (HIGH/LOW) AND a PDH/PDL level coinciding within `dilate`. |
| **trigger** | **confluence** via `interactions` (Module-7): the session-level touch bar `j` (`detect_session_level_touches`) coincides with a `detect_level_touches` PDH/PDL touch. Info `≤ j` → no lookahead. |
| **entry** | `next-open` after `j`. Direction = **fade the confluent level**: HIGH/PDH → SHORT; LOW/PDL → LONG. |
| **invalidation** | the touch extreme beyond both levels breached (Part B). |
| **no_trade_rules** | not filter-eligible → no trade; both levels consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | until first touch (D7) or block end. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

| field | method · reason |
|---|---|
| **stop_loss** | **The touch bar's extreme beyond the coincident levels:** short → `high[j]`; long → `low[j]`. Raw OHLC at `j` (both levels ≈ same price). |
| **exit** | **The opposite prior-DAY level** (PDH↔PDL, feed-robust reference). **Backstop / time-stop:** the **day boundary** (`day_index`, 17:00 NY) — live-valid, more conservative than session horizon. |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop/target. No lookahead. **FAIL-CLOSED:** stop
= raw OHLC; target = ratified PDH/PDL; time-stop = day boundary; ineligible → no trade. **Method stands.**

**W-incr note:** trigger ⊂ both CAND-0032/0027-family (session touch) and CAND-0001 (PDH/PDL) → H0 =
incremental value vs the better single, not a random null.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_persistent_session_levels`, `count_active_persistent_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `detect_level_touches`, PDH/PDL | `code/institutional_levels.py` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `confluence`, `dilate` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `atr14` (filter denominator), `session_of` | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it. Filter COMPOSED (`atr14` denominator; manifest `537e495`).*

## Verdict — **DEFINED (SCREENING_BASELINE)** · Primitive B, filter k=1.0 + own selectivity (day-level confluence) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
