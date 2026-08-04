# POLICY — Persistent Session Level Sweep + Reversal (Primitive B) — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0032.** First candidate on **Primitive B** (persistent/accumulating session levels), now unblocked
by the ratified density filter. An OLD session extreme not yet touched — active for months — is swept and
reverses. Part A + one frozen structural Part B; composition not invention; no lookahead.

> **PRIMITIVE B + MANDATORY FILTER.** Uses `compute_persistent_session_levels` (every closed session's
> High/Low/Mid, available from the next session, active until first touch (D7) or block end; ACCUMULATES).
> **Eligibility filter — k=1.0 primary, k=0.5 & k=2.0 pre-declared sensitivities — declared explicitly and
> applied to this candidate:** a level is eligible at bar `j` iff `|level.price − close[j−1]| ≤ k ×
> atr14[j−1]`. Composed from ratified `atr14` (market_state) + raw `close[j−1]`; **no lookahead** (both
> complete before bar `j` opens). Spec: manifest v2.7.41, commit `537e495`, doc `62d2379`. The filter cut
> active levels 188→6 (median 0), empty bars 0%→83.6%, touches kept 53.3% — restoring falsifiability.
> **It does NOT solve volume** (≈8,833 touches / 8 yr ≈ 4/day remain — same order as the DZ×FVG / CAND-0020
> / CAND-0024 failures). **→ own selectivity below; trigger count is a HARD reporting precondition BEFORE
> performance (Statistician requirement).**

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest session level is NOT the same price as live; edge may not reproduce. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: liquidity resting at an old, untouched session extreme is swept (wick through + close back
inside) and price reverses. The persistence lets a months-old level still matter — but only while it is
filter-eligible (near price).

| field | value · reason |
|---|---|
| **family** | `persistent_session_sweep_reversal` (MK-04 sessions, Primitive B) |
| **OWN SELECTIVITY (beyond the filter)** | **the wick-sweep signature** — only a penetration that CLOSES BACK INSIDE qualifies (not every filter-eligible touch). This is strictly more selective than a plain touch; it is the candidate's own trigger reduction on top of the ATR filter. |
| **activation** | a Primitive-B `SessionLevel` (SESSION_HIGH/LOW) that is **filter-eligible at `j`** (above). Window `[available_idx, expiry_idx]` (next session → block end / first touch). |
| **trigger** | first penetration (`detect_session_level_touches`: HIGH `high[j]≥price`; LOW `low[j]≤price`; D7 once) **AND** close back inside on bar `j` (HIGH `close[j]<price`; LOW `close[j]>price`). Both on `j` → no lookahead. |
| **entry** | `next-open` after `j`. Direction = **fade the swept side**: SESSION_HIGH swept → **SHORT**; SESSION_LOW swept → **LONG**. |
| **invalidation** | the sweep wick extreme is breached (Part B). |
| **no_trade_rules** | level not filter-eligible at `j` → no trade; first-penetration bar closes beyond (break, not sweep) → no trade (fail-closed); level consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | until first touch (D7) or block end. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = session-liquidity sweep (aged population). The sweep wick supplies the stop; the nearest opposite
persistent level supplies the target; a live bar-count horizon backstops (the source session is long past,
so no session-boundary time-stop applies).

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond the sweep wick extreme:** short → `high[j]`; long → `low[j]`. Raw OHLC at `j`, known at entry. |
| **exit** | **The nearest OPPOSITE-kind persistent session level** filter-eligible at entry (Primitive-B set). **Backstop / time-stop:** **20-bar `GROUP_A_HORIZON`** (short-horizon reversal; live-valid — the session boundary is stale for an aged level). |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the sweep-wick stop or the target. No lookahead.
**FAIL-CLOSED:** stop = raw OHLC; target = ratified Primitive-B level; time-stop = live-valid constant;
close-beyond → no trade; not filter-eligible → no trade. Composable — **method stands**.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_persistent_session_levels`, `count_active_persistent_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `atr14` (filter denominator), `session_of` | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it. Filter is COMPOSED (no ratified filter function — manifest `537e495`
specifies it; `atr14` supplies the denominator).*

## Verdict — **DEFINED (SCREENING_BASELINE)** · Primitive B, filter k=1.0 + own selectivity · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
