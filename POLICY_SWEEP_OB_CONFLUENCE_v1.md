# POLICY — Liquidity Sweep × Order-Block Confluence — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0025.** Confluence of a ratified MK-02 wick-sweep with a ratified `order_flow` order block
(Mod.5; the OB primitives are directive-UNBLOCKED — `detect_order_blocks`/`track_breaker` as anchors,
E010/E013 hypotheses remain blocked). Part A entry + one frozen, family-native structural Part B — single
variant, composed from ratified primitives + raw OHLC, chosen BEFORE any result; no invention, no
lookahead, no optimization.

> **MK-01/MK-02 ratification note:** CEO-declared RATIFIED, git-corroborated at `000022555…`; module
> header still reads DRAFT (stale); cited with a freshly-computed hash. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED (interaction)**

Mechanism: a liquidity sweep that occurs **at an order block** — the stop-hunt runs price into an OB where
resting institutional interest reverses it; the OB supplies the reaction floor, the sweep the trigger.

| field | value · reason |
|---|---|
| **family** | `sweep_at_orderblock_confluence` (MK-02 × Mod.5 via Module-7) |
| **timeframes_used** | single-TF (discovery TF) |
| **activation** | a `SweepEvent` (wick-sweep, `close_back_inside=True`) at bar `c` (MK-02, D6 lookahead-safe) AND an order block (Mod.5 `detect_order_blocks`) whose body zone contains the sweep extreme, same polarity as the reversal. |
| **trigger** | **confluence** via `interactions.price_in_zone` — the sweep extreme lies inside the OB body zone (`OB.zone_lower ≤ swept extreme ≤ OB.zone_upper`), OB `confirmed ≤ c`. |
| **entry** | `next-open` after `c`. Direction = **sweep-reversal direction**: BELOW-pool sweep into a bullish OB → **LONG**; ABOVE-pool sweep into a bearish OB → **SHORT** (polarities must agree — else no confluence). |
| **invalidation** | the OB breaker floor fails (see Part B). |
| **no_trade_rules** | pool consumed once (D7); block boundaries (D3/D4). No trade if `next-open` already beyond stop/target, or if sweep direction ≠ OB polarity. |
| **expiry** | entry the bar after `c` or lapses. |

**No F4 exposure:** MK-02 sweep + Mod.5 OB; no CHoCH direction read.
**D2 population restriction (permanent, NOT circumvented):** the swept pool derives from a strict-fractal
swing; equal highs/lows never form a pool (24.8%–59.7% selective cost). Not compensated.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = order-block reaction, sweep-qualified. The OB supplies its ratified breaker floor (as in
CAND-0011/0014/0018); the sweep tightens nothing structurally — the OB's own levels carry the risk.

| field | method · reason |
|---|---|
| **stop_loss** | **The deeper of the OB breaker floor and the swept wick:** long → `min(Low_OB, low[c])`; short → `max(High_OB, high[c])`. **Reason:** the reaction fails when the OB breaks (`track_breaker`); the sweep wick can be deeper, so the deeper floor is the true invalidation. Ratified OB level + raw OHLC, known at entry. |
| **exit** | **The OB body far edge** in the reaction direction (as in CAND-0011/0014): long → `OB.zone_upper`; short → `OB.zone_lower`. **Backstop:** **20-bar `GROUP_A_HORIZON` live time-stop.** |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` already beyond the combined stop or the OB far edge. Coords
known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = min/max of ratified OB floor + raw OHLC;
target = ratified OB edge; time-stop = live-valid. Composable — **method stands**.

**W-incr note (for Statistician):** the trigger is a subset of both CAND-0020 (sweep) and CAND-0011
(OB-rejection) bars → H0 = incremental value vs the better of the two singles, not a random null.

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
| `detect_order_blocks`, `track_breaker` | `code/order_flow.py` | `728fa557674702f46ad135f34cb121687a16d5b4c8a78551e9b252ab1b8f74d0` |
| `price_in_zone` (Module-7) | `code/interactions.py` | `dafb4804f642e964f314824b3a070fc421449ecf36001794dab9c6045ec807e7` |

*Verify the hash, don't assume it.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
