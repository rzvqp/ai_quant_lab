# GC REAL-VOLUME CONTEXT V1 — pre-flight data audit (§3)

Mandatory executability audit performed BEFORE any outcome-conditioned research. Result: the qualified-data gate FAILS on history length and
matched-trade count. Per §6 the experiment is stopped with no purchase and no substitute. This document records exactly what was checked.

## §3 executability audit
| check | result |
|---|---|
| A. GC datasets available locally | Databento GLBX-MDP3 daily files (MBO / MBP-10 / definition / statistics), 2026-06-29 … 2026-07-10 (~11 sessions), plus a derived `gc_15m.csv` (896 bars) built from them |
| B. vendor / source | Databento (GLBX-MDP3, CME Globex feed) — genuine exchange data |
| C. exchange / instrument identity | CME COMEX Gold futures (GC), Globex MDP3 |
| D. genuine traded CME volume? | **YES** — `gc_15m.csv` carries `volume` and `ntrades` aggregated from the native MBO trade stream (real exchange-traded volume, not tick-count proxy) |
| E. native granularity | trade-level MBO; the derived bar file is 15-minute OHLCV+volume+ntrades |
| F. UTC coverage | **2026-06-29 00:00 → 2026-07-10 20:45 UTC** (≈ 12 calendar days / 11 trading sessions) |
| G. missing intervals | only the 11-session window exists; everything outside it is absent |
| H. duplicate rate | n/a (single short sample) |
| I. timestamp semantics | bar file `ts` = interval-start epoch-ns (verifiable), but moot given the gate fails |
| J. contract identifiers | present in the MBO/definition files (Databento instrument ids) |
| K. roll / contract-selection | not constructed; only ~11 sessions, no roll spans a 5-year requirement |
| L. causal alignment feasible? | mechanically yes in-window, but the window is ~12 days |
| M. overlap with frozen XAU setups | **106 matched CTS trades total** in the 12-day window (SETUP_1=31, SETUP_2=19, SETUP_3=56) |
| N. end-to-end completable? | **NO** — history and matched-trade minimums fail |

## Pre-flight flags
```
GC_DATA_PRESENT = YES
GC_REAL_TRADED_VOLUME_VERIFIED = YES (Databento MBO-aggregated volume + ntrades)
GC_TIMESTAMP_SEMANTICS_VERIFIED = PARTIAL (interval-start; not fully audited — gate fails first)
GC_CONTRACT_IDENTITY_VERIFIED = YES (CME COMEX GC via Databento GLBX-MDP3)
GC_ROLL_METHOD_EXECUTABLE = NO (only ~11 sessions; no multi-year roll construction possible)
GC_XAU_CAUSAL_ALIGNMENT_EXECUTABLE = YES in-window (but window is ~12 days)
SUFFICIENT_OVERLAP = NO (106 matched XAU trades << 1000 minimum; per-setup 19–56 << 250)
END_TO_END_EXECUTABLE = NO
```

## §5 minimum-coverage gate — FAIL
```
GC_HISTORY_YEARS ≈ 0.03  (required >= 5.0)                                  -> FAIL
MATCHED_XAU_TRADES_TOTAL = 106  (required >= 1000)                          -> FAIL
MATCHED_PER_SETUP = 31 / 19 / 56  (preferred >= 250 each)                   -> FAIL
MULTI-YEAR / MULTI-STATE COVERAGE = NO (single 12-day window, one regime)   -> FAIL
GC_DATA_GATE = FAIL
```

## Why the existing data are insufficient (not a workaround — a hard blocker)
The only genuine GC traded-volume data on disk is the ~11-session Databento sample used earlier for the microstructure-infrastructure gate.
That sample is authentic (real CME volume) but is **~12 days**, overlapping the 14-year frozen XAU CTS universe by only **106 trades**. Running
the winner-vs-loser experiment on 106 trades across three setups (19–56 each) would be an underpowered exercise the mandate explicitly forbids
(§1, §5). No multi-year GC dataset exists locally, and `foundation_gc/` contains only a builder (`engine.py`), not built history. The required
2011→present GC volume history was specified previously (Databento GLBX ohlcv-1m GC outrights) but **has not been acquired** — acquisition is a
separate CEO purchase decision, not authorized here.

Per §6/§7: no purchase, no download of a substitute, no continuing with price-only or the short sample. The dataset specification required to
unblock is in `GC_REAL_VOLUME_DATA_REQUIREMENT.md`.
