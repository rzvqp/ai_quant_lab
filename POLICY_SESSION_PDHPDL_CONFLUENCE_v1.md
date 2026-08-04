# POLICY — Session Level × PDH/PDL Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0029.** Confluence of a prior-session High/Low (Primitive A) with a prior-day level (MK-04
`institutional_levels`) — two independent reference levels coinciding. Part A + one frozen structural
Part B; composition not invention; no lookahead.

> **Uses PRIMITIVE A only** (2-3 active). **Primitive B NOT used** (saturation ruling). No filter needed.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest session level is NOT the same price as live. **Note: PDH/PDL (day boundary) is comparatively
> feed-robust; the SESSION leg carries the misalignment — the confluence is only as reliable as its
> session leg.** Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

Mechanism: a session extreme that sits at a prior-day level is a doubly-referenced S/R; a touch there is
stronger than a session touch alone.

| field | value · reason |
|---|---|
| **family** | `session_at_daylevel_confluence` (MK-04 sessions × MK-04 PDH/PDL via Module-7) |
| **timeframes_used** | single-TF price + session clock + prior-day levels |
| **activation** | a Primitive-A `SessionLevel` (SESSION_HIGH/LOW) available AND a PDH/PDL level available; the two prices coincide within the ratified `dilate` tolerance. |
| **trigger** | **confluence** via `interactions` (Module-7 alignment used in CAND-0007/0009): the session-level touch bar `j` (`detect_session_level_touches`) coincides with a `detect_level_touches` PDH/PDL touch. Both events use info `≤ j` → lookahead-safe. |
| **entry** | `next-open` after `j`. Direction = **fade the confluent level**: HIGH/PDH → SHORT; LOW/PDL → LONG. |
| **invalidation** | the touch bar's extreme beyond BOTH levels is breached (Part B). |
| **no_trade_rules** | both levels consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | touch within `[available_idx, expiry_idx]`; else lapses. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = doubly-referenced level reaction (session + day). The touch extreme supplies the stop; the
opposite day level supplies the target (day-level target is the more feed-robust reference).

| field | method · reason |
|---|---|
| **stop_loss** | **The touch bar's extreme beyond the coincident levels:** short → `high[j]`; long → `low[j]`. Raw OHLC at `j`, known at entry (both levels sit at ≈ the same price, so a single extreme covers both). |
| **exit** | **The opposite prior-DAY level** (PDH↔PDL; the feed-robust reference), as in CAND-0001. **Backstop / time-stop:** the **day boundary** (`day_index`, 17:00 NY) — the more conservative of day vs session horizon; live-valid. |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop or target. No lookahead. **FAIL-CLOSED:**
stop = raw OHLC; target = ratified PDH/PDL; time-stop = day boundary. Composable — **method stands**.

**W-incr note:** trigger ⊂ both CAND-0027 (session touch) and CAND-0001 (PDH/PDL) → H0 = incremental value
vs the better of the two singles, not a random null.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_session_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `detect_level_touches`, PDH/PDL | `code/institutional_levels.py` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `confluence`, `dilate` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `session_of` (session clock) | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
