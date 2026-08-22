# H4_BO_RAW_S — STRATEGY SPECIFICATION (frozen, self-contained)

**Strategy ID:** `H4-bo-raw-S-rr1.5` · **Side:** SHORT · **Edge TF:** H4 · **Entry TF:** next-H4-bar open (M5-execution PENDING; not part of this frozen spec).
**Status:** FROZEN research candidate — reproduced mechanically; **not validated, not production-ready** (Alpha does not self-ratify). This spec lets an independent validator reproduce the strategy without reading any narrative report.
**Source lineage:** `reports/alpha_discovery/econ_campaign.py` (mechanism `bo-raw-S` = `mk_breakout(up=False, lb=20, accept=False)`), deepened in `deepen_econ.py`. Implementation fingerprint `5dc24217…` (econ_campaign.py).

---

## 1. Exact rule (no parameters changed)
On the H4 series (`OANDA_XAUUSD_H4_from_M15_v2.csv`), per DEV block:
1. **Trend filter (D1-down aligned):** the coarser TF is **D1** (`OANDA_XAUUSD_D1_from_M15_v2.csv`); `trend_up = (EMA20 > EMA50)` on D1 close, merged as-of (backward) onto H4. Eligible only when **`trend_up ≤ 0.5`** (D1 not-up) at the signal bar.
2. **Raw 20-bar-low breakdown (no acceptance):** let `L[i] = rolling_min(low, 20).shift(1)` (causal). **Signal at bar `i` when `close[i] < L[i]`** (and `L[i]` finite). `accept=False` → no confirmation bar; the break level is `brk = L[i]`.
3. **Entry:** next H4 bar open, `entry = open[i+1]` (`ei = i+1`). Causal (next-bar-open); no same-bar fill.
4. **Structural stop (SHORT, above entry):** `sl_usd = max(|entry − brk| + 0.3·ATR14[i], 0.8·ATR14[i])`; `stop = entry + sl_usd`.
5. **Target:** fixed **RR = 1:1.5** → `target = entry − 1.5·(stop − entry)`. Exit via `mstrat.simulate(exit_kind="rr", exit_param=1.5)` (conservative intrabar: **stop wins same-bar ties**, so WR/expectancy are a lower bound). Max look-forward `HOR = 48` H4 bars.

## 2. Data identity
- **Instrument/TF:** OANDA:XAUUSD, H4 derived from canonical M15 (`_from_M15_v2`).
- **DEV blocks (per-block, never crossing the unratified 2013–2016 manifest gap):** `b0` 2011-07-26 → 2013-09-27; `b1` 2016-01-11 → 2018-04-06.
- **CALIB block:** 2020-08-11 → 2021-09-05 (out-of-DEV robustness only).
- **Loader:** `pandas.read_csv` of the ratified `_from_M15_v2` CSVs in `ai_quant_lab-wp5b/data/market`; ATR14 via rolling TR mean.
- **H4 CSV sha256:** `f8f23f6e5c2fb2e402c54f0624252c896f578b92283772a8cb67c4b3e06ffee5`.
- **NOT** the 2021–2023 native-M5 population (a different, unconsumed region — the reason this candidate is validation-worthy where the four 2021–2023 candidates are blocked).

## 3. Cost model
`AI_TRADER_SHADOW_COST_MODEL_v1.json` — round-trip total: **GROSS 0.00 / BASE 0.05 / STRESS 0.24 USD**, applied in `mstrat.simulate` as `slip_ticks = RT/(2·TICK)`, TICK=0.01. R is net of the full round-trip cost divided by structural risk.

## 4. Frozen economics (DEV, single-sequence chronological ledger, N=125)
| metric | GROSS | BASE | STRESS |
|---|---|---|---|
| avg R | +0.320 | +0.3133 | **+0.2876** |
| PF | 1.678 | 1.659 | **1.590** |
| WR (reached 1.5R target) | **0.528** | — | **0.440** |
| WR (any profitable trade) | 0.528 | 0.528 | 0.528 |
| median R (stress) | — | — | +1.434 |
- **maxDD −9.273R** (stress, single-sequence) · **max single loss −1.086R** · **max consecutive losses 9**.
- **best-1%-removed +0.278 · best-5%-removed +0.227 · best-10%-removed +0.160** (stress).
- **Per-block (stress):** b0 +0.2091 · b1 +0.4978. **CALIB (stress): +0.1523 (n=20).**
- **Per-year (stress, n):** 2011 +0.023 (12) · 2012 +0.182 (33) · 2013 +0.277 (46) · 2016 +0.582 (17) · 2017 +0.414 (17) · 2018 +0.0 (0).

## 5. Geometry + frequency
- **Median SL 76.0p** (P25 58.2 / P75 127.5) — **in the 70–100p zone**; **median TP 113.9p**; median MFE 278p.
- **2.33 trades/month** (over 53.7 active DEV-months), median 2.2 days between trades, 98 unique days. (Max no-trade streak 975 days = the 2013–2016 data gap, not a live drought.)

## 6. WR reporting resolution (the documentation defect)
The candidate previously published WR "two ways": `econ_campaign.py:168` computed it on **GROSS** R (reached-target) → **0.528**; `deepen_econ.py:76` computed the same test on **STRESS-net** R → **0.440**. **Both are correct for their scenario.** STRESS reached-target WR (0.44) < GROSS (0.528) because the stress round-trip cost pushes marginal target-hitters below the +1.45-net threshold; the **positive-trade rate is 0.528 in all scenarios** (cost reduces R magnitude but does not flip winners to losers here). Always label WR with its scenario and definition.

## 7. Known limitations
- M5 execution layer PENDING (entry is a next-H4-open proxy; conservative same-bar-stop-wins → lower-bound WR/expectancy).
- Small per-year N (2018 has 0 trades); low frequency (2.33/month).
- Evidence straddles a 2.3-year data gap; the ledger here is a proper **single-sequence** chronological reconstruction across b0→b1 (the metric that was missing).
- SHORT-only; DEV 2011–2018; not evaluated on 2021–2023.
