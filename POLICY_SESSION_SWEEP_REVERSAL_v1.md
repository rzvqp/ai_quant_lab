# POLICY — Session Sweep + Reversal — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0026.** CEO-priority candidate on the newly-ratified `session_levels.py` (MK-04 sessions,
RT-CODE-A-0004). A prior-session extreme (e.g. Asia High) is **swept** — the wick takes the level and
the bar **closes back inside** — then price reverses. Part A entry + one frozen, family-native structural
Part B — single variant, composition not invention, chosen BEFORE any result; no lookahead.

> **Uses PRIMITIVE A only (`compute_prior_session_levels`).** 2-3 levels active at any time (prior
> session's High/Low/Mid, expiring after the current session) — clean, exactly like PDH/PDL. **Primitive B
> (`compute_persistent_session_levels`, 89-188 active) is NOT used** — per the CEO/Red Team saturation
> ruling (unfiltered volume is the pattern that lost most: DZ×FVG −2,432$, CAND-0020 −15,409R, CAND-0024
> −2,605R). No filter needed here because Primitive A is bounded by construction.

> ### ⚠️ FEED-ALIGNMENT WARNING (mandatory, every session candidate — do NOT circumvent)
> `session_of` uses **fixed UTC hours**, but the **set of bars** inside a session differs between the
> OANDA historical feed and an MT5 live feed — the schedules diverge by ~3 hours. **Therefore an Asia
> High (or any session extreme) computed on backtest is NOT the same price as the live Asia High.** An
> edge validated on history may fail to reproduce live. This is a feed-dependency of the session clock,
> carried on the candidate; it is not repaired here.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: session-liquidity stop-hunt. Resting stops sit beyond a prior-session extreme; price sweeps
them (wick through the level) and closes back inside → the move that took liquidity reverses.

| field | value · reason |
|---|---|
| **family** | `session_sweep_reversal` (MK-04 sessions, Primitive A) |
| **timeframes_used** | single-TF price + session clock (`session_of`, UTC) |
| **activation** | a Primitive-A `SessionLevel` (SESSION_HIGH / SESSION_LOW of the prior session) is available — `available_idx` = first bar of the current session (Q4, no lookahead); valid on `[available_idx, expiry_idx]` (current session only). |
| **trigger** | the level's **first penetration** via `detect_session_level_touches` (SESSION_HIGH → `high[j] >= price`; SESSION_LOW → `low[j] <= price`; D7 consumed once) **AND** a **close back inside** on the SAME bar `j`: SESSION_HIGH → `close[j] < price`; SESSION_LOW → `close[j] > price`. Both conditions on bar `j` → **no lookahead** (the exact D6 wick-sweep rule the CEO cites, mirroring PDH/PDL). |
| **entry** | `next-open` after `j`. Direction = **fade the swept side**: SESSION_HIGH swept (Asia High taken, closed below) → **SHORT**; SESSION_LOW swept → **LONG**. |
| **invalidation** | the sweep wick extreme is breached (see Part B). |
| **no_trade_rules** | if the first penetration bar closes **beyond** the level (`close[j] ≥ price` for HIGH) it is a **break, not a sweep → NO TRADE** (fail-closed). Level consumed once (D7); reset at block boundary (D3_bis). No trade if `next-open` already beyond stop/target. |
| **expiry** | the sweep must occur within `[available_idx, expiry_idx]` (the current session); else the level expires unswept (Primitive A). |

**Chainings covered:** Asia High, Asia Low, London High, London Low — including cross-session (a London
level swept during NY): the level's `session_label` records the source session; the sweep is detected in
whatever later bar falls in its validity window. Same mechanism, different `source_session`.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = session-liquidity sweep. The sweep wick supplies the stop; the opposite prior-session level
supplies the target (session-native mirror of CAND-0001's PDH/PDL risk grammar).

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond the sweep wick extreme:** short (HIGH swept) → `high[j]`; long (LOW swept) → `low[j]`. **Reason:** the sweep's own extreme is the invalidation — if price returns beyond the wick that swept, the reversal has failed. Raw OHLC at `j`, known at entry. |
| **exit** | **The OPPOSITE prior-session level** from the same Primitive-A set (SESSION_LOW as target for a short off SESSION_HIGH, and vice-versa), available at entry. **Backstop / time-stop:** the **session boundary** = the level's `expiry_idx` (end of the current session) — a session-native, live-valid horizon derived from the `session_of` clock caller-side (mirrors the day-boundary time-stop for PDH/PDL). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the sweep-wick stop or the opposite-level
target. Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = raw OHLC extreme; target =
ratified Primitive-A level; time-stop = session boundary (live-valid); a close-beyond bar → no trade.
Composable — **method stands**.

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

*Verify the hash, don't assume it — `git show <commit>:<file> | sha256sum`. Note: `market_structure.py`
and `liquidity_mechanics.py` changed at `bf02dd2` vs `0000225` (629e662c / d5bdc126) — this candidate
cites neither.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
