# POLICY — Session Level Touch + Rejection (High/Low) — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0027.** Direct session analog of CAND-0001 (PDH/PDL) — the module mirrors PDH/PDL bar-for-bar. A
prior-session High/Low is touched and holds as resistance/support; price rejects. Part A entry + one
frozen, family-native structural Part B — single variant, composition not invention, chosen BEFORE any
result; no lookahead.

> **Uses PRIMITIVE A only** (2-3 active, prior session, expiring). **Primitive B NOT used** (saturation
> ruling). No filter needed — A is bounded by construction.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the **bar set** per session differs OANDA-historic vs MT5-live by
> ~3h → a backtest session High/Low is NOT the same price as live. An edge validated on history may not
> reproduce. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: a prior-session extreme acts as intraday support/resistance; price reaches it and rejects.
(Distinct from CAND-0026: no close-back-inside refinement is required — this is the plain touch-reaction.
**CAND-0026 ⊂ CAND-0027**: a sweep is a touch that ALSO exceeded-and-reclaimed → W-incr, below.)

| field | value · reason |
|---|---|
| **family** | `session_level_touch_reaction` (MK-04 sessions, Primitive A) |
| **timeframes_used** | single-TF price + session clock |
| **activation** | a Primitive-A `SessionLevel` (SESSION_HIGH / SESSION_LOW) available; window `[available_idx, expiry_idx]`, Q4 no-lookahead. |
| **trigger** | first touch via `detect_session_level_touches` (SESSION_HIGH → `high[j] >= price`; SESSION_LOW → `low[j] <= price`; D7 once). The level is traded as S/R. |
| **entry** | `next-open` after `j`. Direction = **fade the level**: SESSION_HIGH (resistance) → **SHORT**; SESSION_LOW (support) → **LONG**. |
| **invalidation** | the touch bar's extreme beyond the level is breached (see Part B). |
| **no_trade_rules** | level consumed once (D7); reset at block boundary (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | touch must fall in `[available_idx, expiry_idx]`; else the level expires untouched (Primitive A). |

**Chainings covered:** Asia/London High & Low, incl. a London level touched during NY (`session_label`
records the source).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = session-level touch-reaction. Same risk grammar as CAND-0001 (touch-bar extreme stop; opposite
level target).

| field | method · reason |
|---|---|
| **stop_loss** | **The touch bar's extreme beyond the level:** short (SESSION_HIGH) → `high[j]`; long (SESSION_LOW) → `low[j]`. **Reason:** the reaction thesis fails if price closes through the level and drives beyond the touch extreme. Raw OHLC at `j`, known at entry (identical construction to CAND-0001). |
| **exit** | **The OPPOSITE prior-session level** (Primitive-A), available at entry. **Backstop / time-stop:** the **session boundary** = `expiry_idx` (end of current session), session-native live-valid horizon. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop or target. Coords known at entry → **no
lookahead**. **FAIL-CLOSED check:** stop = raw OHLC; target = ratified Primitive-A level; time-stop =
session boundary. Composable — **method stands**.

**W-incr note (for Statistician):** **CAND-0026 (sweep) ⊂ CAND-0027 (touch)** — every sweep is a touch
that additionally closed back inside after exceeding. H0 for CAND-0026 should test the incremental value
of the close-back-inside refinement vs this plain touch-reaction on the IDENTICAL touched bars, not a
random null (same discipline as CAND-0007/0010).

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_session_levels`, `detect_session_level_touches`, `derive_session_index`, `session_labels` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `session_of` (session clock, UTC) | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
