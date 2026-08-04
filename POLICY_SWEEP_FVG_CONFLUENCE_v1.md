# POLICY — Liquidity Sweep × FVG-CE50 Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0024.** Confluence of a ratified MK-02 wick-sweep with a ratified MK-03 FVG. Part A entry + one
frozen, family-native structural Part B — single variant, composed from ratified primitives + raw OHLC,
chosen BEFORE any result; no invention, no lookahead, no optimization.

> **MK-01/MK-02 ratification note:** CEO-declared RATIFIED, git-corroborated at `000022555…`; module
> header still reads DRAFT (stale); cited with a freshly-computed hash. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

Mechanism: a liquidity sweep (stop-hunt reversal) whose reversal displacement leaves a **fair-value gap**
in the reversal direction — the sweep grabs liquidity and the FVG marks the aggressive return, a stronger
reversal signature than either alone.

| field | value · reason |
|---|---|
| **family** | `sweep_imbalance_confluence` (MK-02 × MK-03 via Module-7) |
| **timeframes_used** | single-TF (discovery TF) |
| **activation** | a `SweepEvent` (wick-sweep, `close_back_inside=True`) at bar `c` (MK-02, D6 lookahead-safe) AND an FVG (MK-03 `detect_fvg`/`ce_50`) present in the reversal direction, aligned with the sweep. |
| **trigger** | **confluence** via `interactions` (Module-7): the sweep bar `c` and the FVG are aligned (the FVG is one of the bars forming/adjacent to the reversal displacement, `confirmed_idx ≤ c`). |
| **entry** | `next-open` after `c`. Direction = **sweep-reversal direction** (BELOW-pool sweep → LONG; ABOVE-pool sweep → SHORT), which must equal the FVG polarity (bullish FVG for a long) — else no confluence. |
| **invalidation** | the deeper of the sweep extreme / FVG far edge is breached (see Part B). |
| **no_trade_rules** | pool consumed once (D7); block boundaries (D3/D4). No trade if `next-open` already beyond stop/target, or if sweep direction ≠ FVG polarity. |
| **expiry** | entry the bar after `c` or lapses. |

**No F4 exposure:** MK-02 sweep + MK-03 FVG; no CHoCH direction read.
**D2 population restriction (permanent, NOT circumvented):** the swept pool derives from a strict-fractal
swing; equal highs/lows never form a pool (24.8%–59.7% selective cost). Not compensated.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = two-structure confluence (sweep geometry × imbalance). No daily level → the two structures supply
the risk (same grammar as CAND-0015/0017 two-zone confluences).

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond BOTH — the deeper floor:** long → `min(low[c], FVG.lower)`; short → `max(high[c], FVG.upper)`. **Reason:** the confluence holds until both the swept wick AND the FVG far edge are broken. Raw OHLC + ratified FVG edge, known at entry. |
| **exit** | **The FVG near edge** in the reversal direction (the reaction target, as in CAND-0003/0010): long → `FVG.upper` (near edge from below); short → `FVG.lower`. **Backstop:** **20-bar `GROUP_A_HORIZON` live time-stop** (short-horizon reversal). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the combined stop or the FVG-edge target.
Coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = min/max of raw OHLC + ratified FVG
edge; target = ratified FVG edge; time-stop = live-valid. Composable — **method stands**.

**W-incr note (for Statistician):** the trigger is a subset of both CAND-0020 (sweep) and CAND-0003 (FVG)
bars → H0 = incremental value vs the better of the two singles, not a random null.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `000022555e7344ccc89862dbb2091795ccbad25a` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `detect_swings`, `label_structure` | `code/market_structure.py` | `f3dee97bbb619820d1d07ef288be4c2fd74c76d3f6d4101e0402bff53bf95623` |
| `build_pools`, `detect_sweeps` | `code/liquidity_mechanics.py` | `1531cffa7498c09b0e663062de874573bb1da13a092845686d261ae636fa32e3` |
| FVG / `ce_50` | `code/imbalance_mechanics.py` | `45f8937e221d3dd0ec533c9672b54a1f1e8aab0fe7ed0a66bf6700d3678e9923` |
| `confluence`, `dilate` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
