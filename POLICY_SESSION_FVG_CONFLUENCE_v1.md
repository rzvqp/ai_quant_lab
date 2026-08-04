# POLICY — Session Level × FVG-CE50 Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0030.** Confluence of a prior-session High/Low (Primitive A) with a ratified MK-03 FVG. Part A +
one frozen structural Part B; composition not invention; no lookahead.

> **Uses PRIMITIVE A only** (2-3 active). **Primitive B NOT used** (saturation ruling). No filter needed.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest session level is NOT the same price as live; edge may not reproduce. The SESSION leg carries
> the misalignment. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

Mechanism: a session extreme reinforced by a fair-value gap at the same price — the level supplies the
"where," the FVG the aggressive imbalance the reaction can fill.

| field | value · reason |
|---|---|
| **family** | `session_imbalance_confluence` (MK-04 sessions × MK-03 via Module-7) |
| **timeframes_used** | single-TF price + session clock |
| **activation** | a Primitive-A `SessionLevel` (SESSION_HIGH/LOW) available AND an FVG (MK-03 `detect_fvg`/`ce_50`) present at the level, matching polarity (bullish FVG at a SESSION_LOW support; bearish at a SESSION_HIGH resistance). |
| **trigger** | **confluence** via `interactions.price_in_zone` — the session-level touch bar `j` (`detect_session_level_touches`) lies inside the FVG zone, FVG `confirmed_idx ≤ j`. |
| **entry** | `next-open` after `j`. Direction = **fade the level**: SESSION_HIGH → SHORT; SESSION_LOW → LONG (must equal FVG polarity else no confluence). |
| **invalidation** | the deeper of the touch extreme / FVG far edge is breached (Part B). |
| **no_trade_rules** | level consumed once (D7); block reset (D3_bis). No trade if `next-open` already beyond stop/target, or polarity mismatch. |
| **expiry** | touch within `[available_idx, expiry_idx]`; else lapses. |

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = level × imbalance confluence. Deeper floor of the two structures stops; the opposite session
level targets.

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond BOTH — the deeper floor:** short → `max(high[j], FVG.upper)`; long → `min(low[j], FVG.lower)`. **Reason:** the confluence holds until both the touch extreme AND the FVG far edge are broken. Raw OHLC + ratified FVG edge, known at entry. |
| **exit** | **The OPPOSITE prior-session level** (Primitive-A), available at entry. **Backstop / time-stop:** the **session boundary** = `expiry_idx`, session-native live-valid. |
| **management** | **DECLARED ABSENT.** |
| **sizing** | **Fixed 1R**, risk-normalized. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the combined stop or target. No lookahead.
**FAIL-CLOSED:** stop = min/max of raw OHLC + ratified FVG edge; target = ratified session level;
time-stop = session boundary. Composable — **method stands**.

**W-incr note:** trigger ⊂ both CAND-0027 (session touch) and CAND-0003 (FVG) → H0 = incremental value vs
the better of the two singles.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_session_levels`, `detect_session_level_touches` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| FVG / `ce_50` | `code/imbalance_mechanics.py` | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `price_in_zone` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |
| `session_of` (session clock) | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
