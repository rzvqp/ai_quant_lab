# POLICY — BOS + Retest (structure-break continuation) — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0021.** Trend-continuation on a ratified MK-01 body-BOS after a retest of the broken level. Part A
entry + one frozen, family-native structural Part B — single variant, composed from ratified primitives
+ raw OHLC, chosen BEFORE any result; no invention, no lookahead, no optimization.

> **MK-01/MK-02 ratification note:** as in `POLICY_LIQUIDITY_SWEEP_RETURN_v1.md` — CEO-declared RATIFIED,
> git-corroborated at `000022555…`; the module header still reads DRAFT (stale); cited with a
> freshly-computed hash. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: a **body break of structure** (BOS) confirms trend continuation; the market then **retests**
the broken swing level (former resistance→support, or support→resistance) before continuing. Entry on the
retest, in the BOS direction.

| field | value · reason |
|---|---|
| **family** | `structure_break_retest` (MK-01 `detect_breaks` BOS × `interactions.price_in_zone`) |
| **timeframes_used** | single-TF (discovery TF) |
| **activation** | a `StructureBreak` of kind **BOS_BULL** (`close[b] > price(HH)`) or **BOS_BEAR** (`close[b] < price(LL)`) at bar `b`, ref swing price `P`. **Body-only trigger; wicks do not break (cascade semantics v2.7.38).** D1: the break uses only swings with `confirmed_idx < b` — lookahead-safe. |
| **trigger** | the **first** bar `j > b` whose range straddles the broken level `P` — a retest — via `interactions.price_in_zone(P, low[j], high[j])` = `low[j] ≤ P ≤ high[j]`. **Exact-level straddle; no numeric tolerance chosen.** |
| **entry** | `next-open` after `j`. Direction = **BOS direction**: BOS_BULL → **LONG**; BOS_BEAR → **SHORT**. |
| **invalidation** | the retest bar's far extreme is breached (see Part B). |
| **no_trade_rules** | each swing `idx` consumed once (D7); no swing window crosses a block boundary (D3). No trade if `next-open` already beyond stop or target. If price closes beyond `P` in the trend direction again before a retest occurs, the retest for THIS break lapses. |
| **expiry** | if no straddle of `P` occurs within the block, the signal lapses (no forced entry). |

**No F4 exposure:** the mechanism reads **BOS** kind only (BOS_BULL/BOS_BEAR against DISTINCT HH/LL
references); it does **not** depend on CHoCH direction. A same-bar BOS_BULL and BOS_BEAR would require
`close` to exceed an HH AND fall below an LL simultaneously — mutually exclusive for a single close.

**D2 population restriction (permanent, NOT circumvented):** the HH/LL references come from strict-fractal
swings; equal highs/lows never qualify (measured 24.8%–59.7% selective cost). Tested population = "BOS of
strict-fractal structure," not "all structure breaks." Not compensated.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = structure continuation. The retest supplies the stop; the next liquidity supplies the target.

| field | method · reason |
|---|---|
| **stop_loss** | **The retest bar's far extreme:** long → `low[j]`; short → `high[j]`. **Reason:** a valid retest holds the broken level as new support/resistance — if the retest bar's own extreme is broken, the retest (and the continuation thesis) has failed. Raw OHLC at `j`, known at entry. Same touch-bar-extreme construction ratified for CAND-0001. |
| **exit** | **The nearest liquidity pool in the trend direction**, from ratified `build_pools`, available at entry (`available_idx ≤ j`): long → nearest ABOVE pool above entry; short → nearest BELOW pool below entry. **Reason:** a BOS continuation runs to the next resting liquidity. **Backstop:** if none available → **20-bar `GROUP_A_HORIZON` live time-stop.** |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the retest extreme (stop) or the target pool.
Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = raw OHLC; target = ratified pool
price; time-stop = live-valid constant. Composable — **method stands**.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `000022555e7344ccc89862dbb2091795ccbad25a` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `detect_swings`, `label_structure`, `detect_breaks` | `code/market_structure.py` | `f3dee97bbb619820d1d07ef288be4c2fd74c76d3f6d4101e0402bff53bf95623` |
| `build_pools` (target) | `code/liquidity_mechanics.py` | `1531cffa7498c09b0e663062de874573bb1da13a092845686d261ae636fa32e3` |
| `price_in_zone` (retest straddle) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
