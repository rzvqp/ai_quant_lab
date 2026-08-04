# POLICY — Persistent Session Mid Reaction (Primitive B) — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0033.** The CEO's flagship Primitive-B example — "price reacts to an Asia Mid from five months
ago," now testable and bounded by the filter. Mid = containment object, no intrinsic direction → the
policy declares it. Part A + one frozen structural Part B; composition not invention; no lookahead.

> **PRIMITIVE B + MANDATORY FILTER.** Uses `compute_persistent_session_levels` (accumulating; SESSION_MID
> here). **Eligibility filter — k=1.0 primary, k=0.5 & k=2.0 sensitivities — declared, applied:** level
> eligible at `j` iff `|Mid − close[j−1]| ≤ k × atr14[j−1]` (ratified `atr14` + raw `close[j−1]`; **no
> lookahead**). Spec: manifest v2.7.41, `537e495`, doc `62d2379`. Filter restores falsifiability (188→6
> active, 83.6% empty bars) **but not volume → own selectivity below; trigger count is a HARD reporting
> precondition BEFORE performance.**

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest Mid is NOT the same price as live; edge may not reproduce. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (declared direction)**

Mechanism: an old session equilibrium (Mid) still acts as a reference; price returning to it (containment)
reacts. Direction is DECLARED by the policy (Mid has no side).

| field | value · reason |
|---|---|
| **family** | `persistent_session_mid_reaction` (MK-04 sessions, Primitive B; Mid = containment) |
| **OWN SELECTIVITY (beyond the filter)** | **the containment signature** — `low[j] ≤ Mid ≤ high[j]`, a bar must straddle the EXACT Mid price. This is a distinct, materially rarer population than the ≈8,833 H/L penetration touches; it is the candidate's own trigger reduction on top of the ATR filter. **Its containment-trigger count is the hard pre-performance report.** |
| **activation** | a Primitive-B `SessionLevel` of kind SESSION_MID, **filter-eligible at `j`**. Window `[available_idx, expiry_idx]`. |
| **trigger** | first **containment** touch (`detect_session_mid_touches`: `low[j] ≤ Mid ≤ high[j]`, D7 once). |
| **entry** | `next-open` after `j`. **DECLARED DIRECTION — approach side:** `close[j-1] > Mid` (came from above, Mid as support) → **LONG**; `close[j-1] < Mid` → **SHORT**; `close[j-1] == Mid` → **NO TRADE** (fail-closed). `close[j-1]` known at `j` → no lookahead. |
| **invalidation** | the containment bar's far extreme is breached (Part B). |
| **no_trade_rules** | not filter-eligible → no trade; `close[j-1] == Mid` → no trade; Mid consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | until first touch (D7) or block end. |

**Direction disclosure:** the approach-side rule is an ASSUMPTION the policy imposes because Mid is
directionless; falsifiable; not a property of the ratified primitive.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = Mid equilibrium reaction (aged population).

| field | method · reason |
|---|---|
| **stop_loss** | **The containment bar's far extreme:** long → `low[j]`; short → `high[j]`. Raw OHLC at `j`, known at entry. |
| **exit** | **The nearest persistent session extreme in the trade direction** (Primitive-B, filter-eligible at entry): long → nearest SESSION_HIGH above; short → nearest SESSION_LOW below. **Backstop / time-stop:** **20-bar `GROUP_A_HORIZON`** (live-valid; source session stale). |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop or target, or direction undeclarable. No
lookahead. **FAIL-CLOSED:** stop = raw OHLC; target = ratified Primitive-B extreme; time-stop = live-valid;
undeclarable/ineligible → no trade. Composable — **method stands**.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_persistent_session_levels`, `count_active_persistent_levels`, `detect_session_mid_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `atr14` (filter denominator), `session_of` | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it. Filter COMPOSED (`atr14` denominator; manifest `537e495`).*

## Verdict — **DEFINED (SCREENING_BASELINE, declared-direction)** · Primitive B, filter k=1.0 + own selectivity (containment) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
