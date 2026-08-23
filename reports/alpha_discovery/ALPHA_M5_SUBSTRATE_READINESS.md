# M5 Substrate Readiness (mandate NATIVE_M5_AUTHORIZED, 2026-08-23)

## §2 Data governance — PASS (with coverage caveat)
Native `OANDA_XAUUSD_M5.csv` (wp5b/data/market, sha256 cbb6eebe, manifest timeframes.M5 bar_seconds 300). Verified mechanically:
354,669 bars, 2021-07-27..2026-07-27, columns [time,open,high,low,close,volume], monotonic, 0 duplicates, OHLC valid
(h>=max(o,c), l<=min(o,c)), tick-volume 100% nonzero, spacing 353,361@300s + weekend/session gaps (1307 gaps>300s, 265>1day).
Source = OANDA via TradingView Desktop (project-authoritative). NO fabrication/interpolation.
**COVERAGE CAVEAT (from DATA_XAUUSD_M5_HISTORICAL_GATED_HANDOFF.md):** native M5 does NOT exist before 2021-07-27 (live-verified
source floor). DEV blocks 0 (2011-13) and 1 (2016-18) have ZERO native M5. => ALL M5 work is within a SINGLE macro-era
(2021-2026); cross-era (pre-2021) M5 testing is impossible. No era-independence claim may be made for any M5-derived edge; the
DISC/CONF/OOS partitions within 2021-2026 are the strongest available temporal robustness, not cross-era proof. Disclosed on every finding.

## §3 Causal alignment — PASS (strict nominal-close, canonical repaired contract)
`m5_data.py`: higher-TF (M15/H1/H4) state aligned to each M5 bar via `cur_data.causal_bucket_asof` (H1/H4) and identical
searchsorted(start+TF_sec) nominal-close logic (M15). Audit over all 354,669 M5 bars: nominal-close-leak=0 and M5-inside-mapped=0
for M15, H1, and H4 -> an M5 decision at T sees only fully-closed higher-TF buckets, never a forming or own bucket (even at gaps).
No new timestamp convention introduced (uses the VE-repaired canonical function). The earlier agg-close (last_M15+900) convention
leaked 6 H1 / 18 H4 sub-M15 gap bars at M5 resolution; the strict nominal-close contract fixes it. M5 SUBSTRATE READY.
