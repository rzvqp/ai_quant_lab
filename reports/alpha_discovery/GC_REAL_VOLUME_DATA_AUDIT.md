# GC REAL-VOLUME CONTEXT V1 — data audit (RESOLVED; supersedes the earlier DATA_BLOCKED audit)

The earlier audit stopped at `GC_DATA_GATE = FAIL` (only ~11 sessions of GC volume, 106 matched trades). Data Acquisition has since delivered
the full 15-year genuine CME GC real-volume history (commit `712a322`). This audit records the verified handoff identity used by the resumed experiment.

## §3 identity gate — PASS
```
GC_HANDOFF_IDENTITY_GATE = PASS
Source          = Databento GLBX.MDP3 (CME Globex, COMEX Gold GC)
Symbol          = GC.v.0 (continuous; roll = highest PREVIOUS-DAY volume outright; causal, no lookahead)
OHLCV_1M_ROWS   = 5,160,829   (matches acquisition)   GC_15M_ROWS = 350,825
Coverage        = 2011-07-26 00:00 UTC -> 2026-07-27 23:59 UTC
Real volume     = present on 100% of bars (677,066,963 contracts); ntrades not in ohlcv-1m (volume only)
Quality         = 0 duplicate ts, 0 out-of-order, 0 off-grid-60s, 0 OHLC violations, 0 non-positive prices
Instruments     = 76 underlying outrights; 75 roll transitions
Timestamp       = ts_event = BAR OPEN (UTC); a GC bar is used only once fully closed (ts_event <= XAU decision)
Preserved gaps  = 25 missing weekdays (holidays + degraded 2014-06-13 and 2014-09-23/24/25) — NOT forward-filled
```

## Missing-data rule (frozen before outcome scoring)
A trade's GC context is marked UNAVAILABLE (trade dropped) if there is no GC bar at the decision timestamp, or if the 32-bar causal lookback
spans more than 5 calendar days (i.e., crosses a data gap). GC volume was never forward-filled and "market closed" was never coded as "zero
volume". Trades dropped by this rule: 630 (no-GC-bar 625 + gap 5). No future or partial GC bar entered any feature (`FUTURE_GC_OBSERVATIONS_USED = 0`).

## Overlap gate — PASS
```
MATCHED_SETUP_A (liquidity-sweep)  = 13,418
MATCHED_SETUP_B (breakout-retest)  = 11,605
MATCHED_SETUP_C (auction-value)    = 24,617
MATCHED_XAU_TRADES_TOTAL           = 49,640   (>= 1,000 required; each setup >= 250)
GC_DATA_GATE = PASS
```
Result of the experiment is in `GC_REAL_VOLUME_CONTEXT_V1_REPORT.md`.
