# POLICY — Level × BOS Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0023.** Confluence of a ratified institutional reference level (MK-04) with a ratified MK-01
body-BOS. Part A entry + one frozen, family-native structural Part B — single variant, composed from
ratified primitives, chosen BEFORE any result; no invention, no lookahead, no optimization. Distinct from
CAND-0009 (`level_break_with_displacement`): the qualifier there is a market_state **expansion**; here it
is a structural **BOS** (MK-01), a different primitive and a different claim (structure, not volatility).

> **MK-01/MK-02 ratification note:** CEO-declared RATIFIED, git-corroborated at `000022555…`; module
> header still reads DRAFT (stale); cited with a freshly-computed hash. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED (3-primitive interaction)**

Mechanism: a body break of structure that occurs **at a prior-day reference level** is a level break
confirmed by structure — the level supplies the "where," the BOS the "confirmed direction."

| field | value · reason |
|---|---|
| **family** | `structure_break_at_level_confluence` (MK-04 × MK-01 via Module-7) |
| **timeframes_used** | single-TF price + prior-day levels (same construction as CAND-0001) |
| **activation** | a `StructureBreak` **BOS_BULL**/**BOS_BEAR** at bar `b` (MK-01, body-only, D1 lookahead-safe) AND a `detect_level_touches` touch of a PDH/PDL level on a bar aligned with `b`. |
| **trigger** | **confluence** of the two event sets via `interactions` (the Module-7 alignment used in CAND-0009): the BOS bar `b` coincides with (or, under the ratified `dilate` tolerance, is adjacent to) a level-touch bar. Both events use only information `≤ b` → lookahead-safe. |
| **entry** | `next-open` after `b`. Direction = **BOS direction** (BOS_BULL → LONG; BOS_BEAR → SHORT). |
| **invalidation** | the broken reference level fails (see Part B). |
| **no_trade_rules** | swing `idx` consumed once (D7); no cross-block window (D3); level active per its own MK-04 rules. No trade if `next-open` already beyond stop/target. |
| **expiry** | entry the bar after `b` or lapses. |

**No F4 exposure:** reads BOS kind only, not CHoCH direction.
**D2 population restriction (permanent, NOT circumvented):** BOS references are strict-fractal swings;
equal highs/lows excluded (24.8%–59.7% selective cost). Not compensated.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = level-confirmed structure break. The broken level supplies the stop; the opposite prior-day level
supplies the target (same risk grammar as CAND-0001/0007/0009).

| field | method · reason |
|---|---|
| **stop_loss** | **Just beyond the broken reference level:** long → the PDL/PDH level price (the level that, having broken as support/resistance, must hold); short → symmetric. **Reason:** the confluence thesis is dead the moment the level it was built on is reclaimed. Ratified MK-04 level price, known at entry. |
| **exit** | **The opposite prior-day level** in the trade direction (ratified MK-04), as in CAND-0001/0007. **Backstop / time-stop:** the **day boundary (17:00 NY, `day_index`)** — a prior-day-level policy's native live horizon. |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the level stop or the opposite-level target.
Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop/target = ratified MK-04 level prices;
time-stop = day boundary (live-valid). Composable — **method stands**.

**W-incr note (for Statistician):** every trigger is a subset of CAND-0001-eligible bars (a level is
involved) AND of a standalone BOS set → H0 should test **incremental value vs the better of {CAND-0001,
a standalone BOS baseline}**, not a random null (same discipline as CAND-0007/0009/0010).

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `000022555e7344ccc89862dbb2091795ccbad25a` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `detect_swings`, `label_structure`, `detect_breaks` | `code/market_structure.py` | `f3dee97bbb619820d1d07ef288be4c2fd74c76d3f6d4101e0402bff53bf95623` |
| `detect_level_touches`, PDH/PDL levels | `code/institutional_levels.py` | `c284fa2c8cde5a4b345d773a65a3b7a563cdd2548c712a27e3d97cc0fb15b4a9` |
| `confluence`, `dilate` (Module-7 alignment) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
