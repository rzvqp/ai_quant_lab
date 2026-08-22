# COMP-CONT-L — STRATEGY SPECIFICATION (frozen, self-contained)

**Strategy ID:** `COMP-CONT-L-rr2` · **Side:** LONG only · **Class:** `REGIME_SPECIFIC_ROBUST_CANDIDATE` (D1-uptrend-only) · **Edge/entry TF:** H4 · **Context TF:** D1.
**Status:** FROZEN research candidate — **not validated, not production-ready** (Alpha does not self-ratify). This spec lets an independent validator reproduce the strategy without reading any narrative report.
**Discovered by:** `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001`, frontier **F5-COMPCONT** (after F1/F2/F3 falsified, F4 near-miss). Implementation fingerprint `c60357cb…` (`frontier5_compcont.py`+`swing_base.py`).

---

## 1. Economic thesis (the NEW pre-entry information, §8)
Inside a **confirmed daily uptrend**, an **H4 volatility contraction** (ATR below its recent norm *and* the recent price box tighter than its norm) marks a **low-risk re-entry**: the contraction floor is a tight, causal invalidation, and the forward path in a live uptrend is asymmetric (continuation more likely than a break below the contraction). This is trend *continuation timing via volatility state*, not a breakout (F1) and not a mean-reversion (F2). The entry is taken **in the D1-trend direction, regardless of any short-term break direction.**

## 2. Exact rule (frozen; no parameters changed after freeze)
On the H4 series (gated M5 -> H4 causal aggregation), per bar `i`:
1. **D1 context (causal):** last COMPLETED D1 bar (D1.close_time <= H4.time) has `EMA20 > EMA50`. (LONG only; the SHORT mirror was tested and is **not supported** — regime-locked, best-10%-removed negative.)
2. **Compression state (causal):** with `W = 20`:
   - `box_high = rolling_max(high, W).shift(1)`, `box_low = rolling_min(low, W).shift(1)`, `box_range = box_high - box_low`;
   - `atr = ATR14`; `atr_ma = rolling_mean(atr, 30).shift(1)`; `box_ma = rolling_mean(box_range, 50).shift(1)`;
   - **compression** = `(atr < atr_ma) AND (box_range < box_ma)` (both finite).
3. **Event dedup (§13):** keep the **first** compression bar in each `cooldown = 20`-bar window (one opportunity per compression event; no re-entry spam — this dedup is **material**, see §6).
4. **Entry:** next H4 bar open, `entry = open[i+1]` (causal; no same-bar fill).
5. **Structural stop (LONG):** `stop = box_low[i]` (the contraction floor). `risk = entry - stop` (median ~190 project pips).
6. **Target:** `target = entry + rr * risk`, **rr = 2.0** (headline; rr=1.5 also robust). Exit via conservative intrabar scan (**stop wins same-bar ties**), max horizon `H = 42` H4 bars (~7 days; trades typically resolve in ~8 bars).

## 3. Data identity
- **Instrument/TF:** OANDA:XAUUSD, H4 built by **causal aggregation of the gated native M5** (`edge_research._common.load('M5', PRE_HOLDOUT_SPLIT_ID, RESEARCH_HOLDOUT_CUTOFF_UTC)`); NO `read_csv` on `data/market`. Loader file_sha256 `cbb6eebe…`, manifest 2.7.94.
- **DEV (selection):** 2021-07-27 -> 2023-12-29 (H4 DEV = 2652 bars).
- **CALIB (out-of-selection robustness only):** 2024-01-01 -> 2024-06-20. Not used for any parameter choice.
- **NOT** the 2011-2018 `_from_M15_v2` population (that is the separate frozen H4-bo-raw-S). Distinct population, distinct mechanism.

## 4. Cost model
`AI_TRADER_SHADOW_COST_MODEL` — round-trip USD: GROSS 0.00 / BASE 0.05 / **STRESS 0.24**; TICK 0.01. R = (net USD PnL) / risk_usd. All headline numbers are **STRESS** (conservative). Project pip = 0.10 USD.

## 5. Frozen economics (DEV, single-sequence, N=53, rr=2.0, STRESS)
| metric | value |
|---|---|
| avg R | **+0.443** (BASE +0.46 — cost-robust) |
| PF | **1.94** |
| WR (reached 2R target) | 0.396 · positive-rate 0.509 |
| median R | +0.257 · max loss −1.114R · maxDD **−6.19R** |
| best-1/5/10%-removed | +0.414 / **+0.350** / **+0.246** (all positive — not tail-carried) |
| DISC / CONF (chronological 60/40) | **+0.52 / +0.33** (both positive) |
| per-year (STRESS) | 2021 +0.053 (n10) · 2022 +1.000 (n8) · 2023 +0.428 (n35) — all positive |
| geometry | median SL **190p** · median TP **379p** · median hold **8 H4 bars** |
| frequency | **2.79 trades/month** (LONG, D1-uptrend regime only) |

## 6. Robustness & honest limitations (forwarded to the validator — §37 bounded)
- **CALIB 2024 out-of-selection: POSITIVE** (N=24, rr2.0 avgR **+0.223**, PF 1.47, posRate 0.50; rr1.5 +0.083). Genuine forward confirmation.
- **Parameter neighborhood:** stable in **H** (30/42/60 all avgR>0, best10>0) and **rr** (1.5/2.0 both robust). Present at **W=14–20**; **collapses at W=28** (best10 −0.16) — the edge lives in a compression-window band W≈14–20, NOT all W. **Local peak at W=20.**
- **Event-dedup is material:** cooldown=20 (principled one-per-compression, §13) is required; cooldown=12 (dense re-entries) turns best-10%-removed negative. The dedup is causal (time-since-last-entry only), not outcome-based.
- **Correlation:** LONG trend-beta -> **P&L-correlated with the frozen LONG survivors** (HR-TU-pb-L / MT-H4-dispaccept-L). Adds *opportunities/frequency*, not a new *direction*. But mechanically distinct entries: only **6%** of signal bars are H4-`TREND_UP` — it fires in consolidations *within* the D1 uptrend that generic protrend misses.
- **Sample:** N=53 (2022 n=8). Emerged after F1–F4 failed this loop + the whole prior program (full multiple-testing lineage in the checkpoint). Not hypothesis #1.
- **SHORT side NOT SUPPORTED** (regime-locked, best10<0). LONG-only.

## 7. Independence pointers
- `S5_OVERLAP`: S5 lives on 2021–2023 **M5 intraday**; different mechanism/horizon — conceptually independent, direct bar-overlap not computed here.
- `H4_BO_RAW_S_OVERLAP`: different population (2011–2018) and opposite side (SHORT) — independent.
- Same-direction correlation with frozen LONG trend-beta is the real overlap to quantify at validation (needs the frozen ledgers).
