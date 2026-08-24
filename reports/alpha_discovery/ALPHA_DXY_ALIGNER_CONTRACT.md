# ALPHA_DXY_ALIGNER_CONTRACT (FROZEN)

**Mandate:** `ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001` (Decision A). Foundation for causal DXY→XAUUSD research (`dxy_data.py`). Data-only join performed by Alpha per the ratified Data Acquisition contract (`acquisition_staging/dxy/DXY_DATA_CONTRACT.md`).

## Data identity (ratified, no proxy)
- **DXY:** ICE U.S. Dollar Index cash/index (`ICEUS:DXY`→`ICEUS_DLY:DXY`), H1, from the three governed slices `DXY_{B0,B1,2021_2023}_RESEARCH_SLICE.csv`. NOT TVC:DXY / DX futures / EURUSD-inverse / synthetic baskets / broker proxies.
- **XAUUSD:** `OANDA_XAUUSD_H1_from_M15_v2.csv` (the exact reference the DXY coverage was matched against), features via `hist_data._feat`, parent-regime via frozen `state_regime.regime`.
- **Populations:** b0 (2011-2013), b1 (2016-2018), y2123 (2021-07-27..2023-12-29). 2024+ PROTECTED, excluded.

## Timestamp / causal contract (ENFORCED)
- DXY `time` = bar OPEN (UTC epoch). DXY close/FEATURE_AVAILABLE = `time+3600`.
- XAUUSD decision instant = bar close = `time+3600`.
- **Join:** `merge_asof(xau, dxy, left_on=decision(=xau.time+3600), right_on=dxy_close(=dxy.time+3600), direction=backward)` — the most recent DXY bar whose close is already known at the XAUUSD decision. Causal assertion `dxy_close <= decision` runs every build (passes).
- **Lag set (predeclared, §12):** {0,1,2,4} H1 (lag0 = last-closed DXY bar; lags shifted on the DXY series). No dozens-of-lags scan.

## Coverage (verified == ratified report)
| era | XAUUSD H1 | same-hour DXY | % |
|---|---|---|---|
| b0 | 13397 | 13053 | 97.4 |
| b1 | 13213 | 12918 | 97.8 |
| y2123 | 6777 | 6772 | 99.9 |
Gaps preserved (weekends/holidays), no forward-fill.

## DXY feature set (predeclared, §5/§11 — no mining)
Per-slice, causal from DXY closes: `d_ret1`/`d_ret4` (1h/4h change), `d_eff` (dir efficiency 8), `d_atr`/`d_vr` (vol + vol ratio), `d_imp` (4h impulse in ATR), `d_accel` (4h vel vs prior), `d_dist` (distance from EMA20 in ATR). Maps to mandate info classes: return, persistence/efficiency, volatility, vol-change, impulse, acceleration, extension/distance.

## Foundation finding (frames the mandate)
Sanity linear check: corr(DXY recent 4h return, XAUUSD forward 24h return) ≈ 0 in every era (b0 -0.027, b1 -0.000, y2123 +0.004). The well-known DXY↔gold inverse correlation is **CONTEMPORANEOUS** (both react to shared drivers at the same instant), NOT predictive from past DXY to future gold. => the mandate's real question (does *causal/lagged* DXY add *incremental* info about *future* XAUUSD path, above XAUUSD's own state) is non-trivial; naive lagged DXY-return alone carries no edge. Stage A tests the conditional/path/incremental map before any conclusion.

**Frozen. Next:** Stage A DXY information map (DXY state → XAUUSD P(+X/-Y) path lift vs XAUUSD parent-state base, LONG/SHORT separate, lag curve, cross-era, event-deduped, incremental-over-price-only test §7).
