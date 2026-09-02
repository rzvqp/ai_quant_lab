# GC_FULL15Y_ACQUISITION_REPORT

**Mandate:** ACQUIRE GC FULL 15Y DATASET (Databento GLBX.MDP3, cap USD 25.00) · **Divizie:** Data Acquisition · **Data:** 2026-09-03

> # ✅ ACQUISITION COMPLETE — cost 22.118228 USD (cap 25.00 respected)
> Exact ICE… no — exact **Databento GLBX.MDP3 GC.v.0 continuous ohlcv-1m + definition + statistics**, 2011-07-26→2026-07-27, quality-gate PASS, continuous-roll causality PASS, 1m+15m research derivatives built. **DATA ONLY** — no Alpha research, no S5/AI Trader/CTS/StrategyCatalog touched.

## Purchase record (§14)
Read-only `metadata.get_cost` recheck ran immediately before the paid request and the cap was enforced mechanically:
```
FINAL_OHLCV_COST      = 18.841074 USD
FINAL_DEFINITION_COST =  2.361728 USD
FINAL_STATISTICS_COST =  0.915425 USD
FINAL_TOTAL_COST      = 22.118228 USD   (≤ MAX 25.00 → authorized)
COST_CAP_RESPECTED    = YES
```
Costs matched the CEO's verified quotes exactly. Account credit applied: not surfaced by the API response (get_cost returns list price; any credit is applied at billing — not exposed here). `DATABENTO_API_KEY` was read from the environment only and never printed/logged/committed/transmitted/stored.

## Raw artifacts (§8, §9) — preserved immutable in `raw/`, manifest `GC_FULL15Y_RAW_MANIFEST.json`
| request | schema | symbol / stype | file | bytes | sha256 |
|---|---|---|---|---|---|
| OHLCV | ohlcv-1m | `GC.v.0` / continuous | gc_ohlcv-1m_GC.v.0_2011-07-26_2026-07-28.dbn | 76,680,322 | `99ac4ae8…` |
| definition | definition | `GC.FUT` / parent | gc_definition_GC.FUT_2011-07-26_2026-07-28.dbn | 23,679,001 | `e73d9b94…` |
| statistics | statistics | `GC.FUT` / parent | gc_statistics_GC.FUT_2011-07-26_2026-07-28.dbn | 209,240,648 | `51385a27…` |
Range 2011-07-26 → 2026-07-28 (Databento end EXCLUSIVE → includes all of 2026-07-27). `databento` lib 0.86.0. Raw files not modified. Derived files under `derived/`.

## Data quality (§10) — see `GC_FULL15Y_DATA_QUALITY_REPORT.md`
5,160,829 ohlcv-1m rows; 0 duplicates / 0 out-of-order / 0 off-grid / 0 OHLC-violations / 0 non-positive; real volume present; ntrades NOT in schema. 25 holiday/anomaly missing-weekdays + 3 Databento-degraded days (2014-06-11..13) documented, gaps preserved (no forward-fill). `DATA_QUALITY_GATE = PASS`.

## Continuous-contract causality (§11) — see `GC_FULL15Y_CONTRACT_ROLL_AUDIT.md`
`GC.v.0` = volume roll (front, rank 0), ranked by **previous-day volume** → uses only prior information → **no look-ahead**. 76 underlying instruments, 75 causal rolls. `CONTINUOUS_CONTRACT_CAUSALITY = PASS`.

## Derived research data (§12)
`derived/GC_1M_RESEARCH.parquet` (5,160,829 rows) + `derived/GC_15M_RESEARCH.parquet` (350,825 rows). 15m = O(first)/H(max)/L(min)/C(last)/V(sum real volume), UTC, no forward-fill, ntrades unavailable in ohlcv-1m.

## REQUIRED FINAL OUTPUT (§16)
```
GC_FULL15Y_ACQUISITION_COMPLETE = YES

PURCHASE_AUTHORIZED_BY_CEO = YES
MAX_AUTHORIZED_COST_USD = 25.00

FINAL_OHLCV_COST = 18.841074 USD
FINAL_DEFINITION_COST = 2.361728 USD
FINAL_STATISTICS_COST = 0.915425 USD
FINAL_TOTAL_COST = 22.118228 USD
COST_CAP_RESPECTED = YES

DATABENTO_DATASET = GLBX.MDP3
GC_OHLCV_SCHEMA = ohlcv-1m
GC_OHLCV_SYMBOL = GC.v.0 (stype_in=continuous)
GC_HISTORY_START = 2011-07-26T00:00:00Z
GC_HISTORY_END = 2026-07-27T23:59:00Z

OHLCV_ROWS = 5160829
DEFINITION_ROWS = 2869910
STATISTICS_ROWS = 12286623

RAW_FILES_SHA256_VERIFIED = YES
DATA_QUALITY_GATE = PASS

REAL_TRADED_VOLUME_PRESENT = YES
TIMESTAMP_SEMANTICS_VERIFIED = YES
CONTINUOUS_CONTRACT_CAUSALITY = PASS

GC_1M_RESEARCH_READY = YES
GC_15M_RESEARCH_READY = YES

READY_FOR_ALPHA_GC_REAL_VOLUME_CONTEXT_V1 = YES

DATA_PURCHASE_AUTHORIZED = YES (CEO, cap 25.00); executed at 22.118228 USD
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
STOP.

## Scope & safety confirmation
Acquired ONLY the authorized dataset/schemas (GC.v.0 ohlcv-1m + GC.FUT definition + GC.FUT statistics). NOT acquired: MBO/MBP-1/MBP-10/trades-separately/options/spreads/other metals/other products/extra years/extra schemas/subscriptions/Standard/real-time. No second competing roll methodology. No Alpha research run. S5 / AI Trader / CTS / StrategyCatalog / Market Intelligence untouched. API key never exposed. Raw DBN + Parquet are gitignored (large binaries; the manifest + audit JSON are the committed record).
