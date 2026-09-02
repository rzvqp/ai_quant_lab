# ORDER_BLOCK_RETEST_ATLAS_V1 — causal order-block census & baseline outcome

ORDER_BLOCK_RETEST_FACTORY_V1 §31 deliverable. Governed OANDA XAUUSD M15 only. Causal construction (§4/§27): block frozen at BOS bar,
retest strictly after. Code: `ob_core.py`, `ob_atlas.py`.

## 1. Data audit (§3) — DATA_AUDIT_PASS = YES
```
M15_SOURCE = OANDA XAUUSD (cur_data), 355,696 bars, 2011-07-26 → 2026-07-27, UTC, 15-min (weekend gaps normal)
H1/H4      = causal UTC aggregation (used only for context subgroup; the surviving candidate is M15-only)
M5_NATIVE  = OANDA_XAUUSD_M5.csv, 2021-07-27 → 2026-07-27 (354,669 bars) — execution research restricted to this; NO synthesis
median ATR = M15 $1.747 ; cost = $0.419 round-trip per-trade (0.24R@1ATR), applied as 0.419/risk
```

## 2. Causal order-block construction (§4–§9)
Bullish: **BOS** at i = `close[i] > swH[i]` (prior causal 20-bar swing high, shift-1) AND fresh (`close[i-1]<=swH[i-1]`). **Origin OB** =
last bearish candle in `[i-10,i-1]`; block `[low,high]` **frozen at i**. **Displacement** = `(close[i]-block_high)/ATR[i]`. **First retest**
= first `k>i` with `low[k]<=block_high` before any close below `block_low`. Bearish = exact mirror. Coordinates never resized.

## 3. Census (§30 counts)
```
TOTAL_CAUSAL_ORDER_BLOCKS (disp>=0.75) = 17,432  (bull 8,985 / bear 8,447)
FIRST_RETEST_EVENTS (fresh, pre-invalidation) = 13,137  (bull 6,796 / bear 6,341)
BULLISH_EVENTS = 6,796 · BEARISH_EVENTS = 6,341 · all fresh-first-retest by construction
```

## 4. ★ Anti-hindsight lesson — entry model matters (documented so it is never re-derived as an edge)
- **Resting LIMIT at block edge** (fills on touch; the tradeable model): OB fresh first-retest ≈ **break-even** overall
  (bull −0.006R / bear +0.020R at 2R). Depth/rejection of the entry bar is **NOT** knowable at limit-fill time.
- Conditioning on **shallow first-retest depth** under limit entry showed a spurious **+0.28R** — a **limit-fill intrabar selection
  artifact**. Under a fully causal **close-of-retest entry** (resolve from k+1, depth known) the same shallow-depth cells are **−0.19 to
  −0.23R** and every depth/era/HTF cell is negative. **The depth/reject "edge" is hindsight and is NOT used by the candidate.**
- The genuine, causal edge lives in **pre-retest-selectable** variables only: **displacement strength** and **session**.

## 5. Baseline subgroups (limit entry, 2R, net-R; causally-selectable only)
```
displacement:  disp>=1.5  bull +0.076 (D+0.026/C+0.075/O+0.178)   bear +0.084 (D+0.074/C+0.032/O+0.168)  [monotone in disp]
session:       NY         bull +0.115 (D+0.054/C+0.143/O+0.205)   bear +0.098
               LN         bull -0.001                              bear +0.032
target-space:  room>=3    bull +0.026                              bear +0.057   (weak; room alone not decisive)
```
Displacement and NY/LN session are the causal levers. Combined (disp>=1.5 & LN+NY, 2R) → the surviving candidate (see contrast report
and `ALPHA_CANDIDATE_OBR-BULL-1.md`): bull +0.154R, cross-era, monotone in displacement, outlier-robust.

## 6. HTF context (subgroup, §13 — not an assumed edge)
H4-aligned vs counter vs neutral did **not** add incremental value on top of displacement+session (align ≈ neutral ≈ counter within
noise at limit entry); consistent with the prior HTF-selection negative. The candidate is deliberately **HTF-free** (M15-only), which also
keeps it fully causal with no HTF-leak surface.
