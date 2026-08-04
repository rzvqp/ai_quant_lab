# POLICY — Session Mid Reaction — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0028.** Reaction at the prior-session **Mid** — a DIFFERENT object from High/Low (ratified spec):
touch by **containment** (`low[j] ≤ Mid ≤ high[j]`), and **Mid has no intrinsic direction — the policy
declares it.** Part A entry + one frozen structural Part B — single variant, composition not invention,
chosen BEFORE any result; no lookahead.

> **Uses PRIMITIVE A only** (2-3 active). **Primitive B NOT used** (saturation ruling). No filter needed.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory)
> `session_of` uses fixed UTC hours; the bar set per session differs OANDA-historic vs MT5-live by ~3h →
> a backtest session Mid is NOT the same price as live. Edge may not reproduce. Carried, not repaired.

## PART A — ENTRY MECHANISM — **DEFINED (with declared direction)**

Mechanism: the prior-session Mid (midpoint of its range) is an equilibrium reference; price returning to
it reacts. Because Mid is **containment-touched and has NO intrinsic side**, the module refuses to supply
direction (`detect_session_mid_touches` is separate from H/L, returns no side). **This policy DECLARES the
direction — by approach side — and that declaration is the policy's own claim, not a property of Mid.**

| field | value · reason |
|---|---|
| **family** | `session_mid_reaction` (MK-04 sessions, Primitive A; Mid = containment object) |
| **timeframes_used** | single-TF price + session clock |
| **activation** | a Primitive-A `SessionLevel` of kind **SESSION_MID** available; window `[available_idx, expiry_idx]`, Q4 no-lookahead. |
| **trigger** | first **containment** touch via `detect_session_mid_touches` (`low[j] ≤ Mid ≤ high[j]`, D7 once). |
| **entry** | `next-open` after `j`. **DECLARED DIRECTION (policy, not level) — by approach side:** if `close[j-1] > Mid` (price came from ABOVE, Mid tested as support) → **LONG**; if `close[j-1] < Mid` → **SHORT**. `close[j-1]` is known at `j` → no lookahead. If `close[j-1] == Mid` exactly → **NO TRADE** (fail-closed, direction undeclarable). |
| **invalidation** | the containment bar's far extreme is breached (see Part B). |
| **no_trade_rules** | `close[j-1] == Mid` → no trade; Mid consumed once (D7); reset at block boundary (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | containment must fall in `[available_idx, expiry_idx]`; else Mid expires untouched (Primitive A). |

**Explicit direction disclosure (for Red Team / Statistician):** the approach-side rule is an ASSUMPTION
the policy imposes because Mid is directionless. It is falsifiable (a null result would say Mid carries no
tradable reaction under this declaration) and must not be read as a property of the ratified primitive.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = Mid equilibrium reaction. The containment bar supplies the stop; the prior-session extreme in the
trade direction supplies the target (Mid → the nearer same-side extreme).

| field | method · reason |
|---|---|
| **stop_loss** | **The containment bar's far extreme:** long → `low[j]`; short → `high[j]`. **Reason:** a reaction off Mid fails if price drives through the containment bar against the declared direction. Raw OHLC at `j`, known at entry. |
| **exit** | **The prior-session extreme in the trade direction** (Primitive-A): long → the SESSION_HIGH; short → the SESSION_LOW (Mid reverts toward the range extreme it is heading to). **Backstop / time-stop:** the **session boundary** = `expiry_idx`, session-native live-valid. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond stop or target, or if the approach side is
undeclarable (`close[j-1] == Mid`). Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop =
raw OHLC; target = ratified Primitive-A extreme; time-stop = session boundary; undeclarable direction → no
trade. Composable — **method stands**.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `bf02dd2b91b0c809da1489198d3efe5f28723a95` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `compute_prior_session_levels`, `detect_session_mid_touches`, `derive_session_index`, `session_labels` | `code/session_levels.py` | `2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0` |
| `session_of` (session clock, UTC) | `code/market_state.py` | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE, declared-direction)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
