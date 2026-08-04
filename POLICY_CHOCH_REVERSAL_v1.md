# POLICY — CHoCH Reversal (change of character) — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
# ⚠️ F4-DEPENDENT — direction reads CHoCH sign · SEE F4 FLAG BELOW (CEO-mandated)

**CAND-0022.** Trend-reversal on a ratified MK-01 Change-of-Character. Part A entry + one frozen,
family-native structural Part B — single variant, composed from ratified primitives, chosen BEFORE any
result; no invention, no lookahead, no optimization.

> **MK-01/MK-02 ratification note:** CEO-declared RATIFIED, git-corroborated at `000022555…`; module
> header still reads DRAFT (stale); cited with a freshly-computed hash. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED (with F4 caveat)**

Mechanism: a **Change of Character** is the first counter-trend body break — the trend's most recent
counter-swing is closed through, signalling the prior trend's character has changed. Entry in the CHoCH
direction (the new character).

| field | value · reason |
|---|---|
| **family** | `change_of_character` (MK-01 `detect_breaks` CHoCH) |
| **timeframes_used** | single-TF (discovery TF) |
| **activation** | a `StructureBreak` of kind **CHOCH_BULL** (`close[c] > price(LH)` — closes above the last lower-high in a down-sequence) or **CHOCH_BEAR** (`close[c] < price(HL)` — closes below the last higher-low in an up-sequence) at bar `c`. **Body-only; D1 lookahead-safe** (swings `confirmed_idx < c`). |
| **trigger** | self-triggering — the CHoCH bar IS the event (like compression→expansion). |
| **entry** | `next-open` after `c`. Direction = **CHoCH sign**: CHOCH_BULL → **LONG**; CHOCH_BEAR → **SHORT**. |
| **invalidation** | the most recent opposite-side swing extreme before `c` is breached (see Part B). |
| **no_trade_rules** | each swing `idx` consumed once (D7); no window crosses a block boundary (D3). **F4 no-trade rule (below).** No trade if `next-open` already beyond stop/target. |
| **expiry** | entry is the bar immediately after `c` or the signal lapses. |

### ⚠️ F4 FLAG (CEO-mandated — this candidate DEPENDS on CHoCH direction)

Per the ratified cascade semantics (v2.7.38), **BOS and CHoCH can occur on the SAME bar against DISTINCT
references, and — the open F4 concern — opposite-direction CHoCH can co-occur on one bar** (a close that
exceeds a prior LH while also falling below… cannot happen for a single scalar close, but the cascade can
emit CHOCH_BULL against one reference and, on the SAME bar via a different active swing set, a competing
break). **Because this policy's entire direction is the CHoCH sign, a same-bar directional collision is a
live ambiguity.** Mandatory handling, chosen before results and fail-closed:

> **F4 no-trade rule:** if bar `c` emits CHoCH breaks of **both** signs (any CHOCH_BULL **and** any
> CHOCH_BEAR at the same `idx`), the bar is **ambiguous → NO TRADE** on `c`. Only bars with a single CHoCH
> sign produce an entry. The ambiguous-bar count is a **required audit field** routed to Statistician/VE
> (the CEO noted opposite CHoCH "mai des sub noua semantică" — its live frequency must be measured, not
> assumed negligible).

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = character reversal. The prior-trend extreme that must NOT be revisited supplies the stop; the
opposite liquidity supplies the target.

| field | method · reason |
|---|---|
| **stop_loss** | **The most recent opposite-kind swing extreme before `c`:** long (CHOCH_BULL) → price of the most recent LOW swing (`confirmed_idx < c`, largest `idx`); short → most recent HIGH swing. **Reason:** a genuine character change does not revisit the extreme the prior trend just made — if it does, the reversal is void. Ratified swing extreme, lookahead-safe. |
| **exit** | **The nearest OPPOSITE-side liquidity pool** in the new direction (ratified `build_pools`, `available_idx ≤ c`): long → nearest ABOVE pool; short → nearest BELOW pool. **Backstop:** none available → **20-bar `GROUP_A_HORIZON` live time-stop.** |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the swing-extreme stop or the target pool; F4
ambiguous bars excluded. Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = ratified
swing extreme; target = ratified pool; time-stop = live-valid constant; F4 collision → no trade.
Composable — **method stands**.

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

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · F4-DEPENDENT (flagged) · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
