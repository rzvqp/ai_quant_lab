# GC REAL-VOLUME DATA REQUIREMENT (§6) — what must be acquired to run this experiment

The GC real-volume contextual trade-selection experiment cannot run on local data (12-day sample, 106 matched trades). This specifies the
dataset the experiment requires. **No purchase is authorized by this document — CEO decides acquisition separately.**

```
INSTRUMENT = CME COMEX Gold futures (GC), CME Globex (GLBX-MDP3)
REQUIRED_SCHEMA = time-bar OHLCV with GENUINE exchange-traded volume + trade count (ntrades), per contract
PREFERRED_NATIVE_GRANULARITY = 1-minute bars (ohlcv-1m) built from the native trade stream; open interest (statistics) alongside
MINIMUM_ACCEPTABLE_GRANULARITY = 5-minute bars, ONLY if verifiably aggregated from genuine exchange trades with explicit provenance
REQUIRED_START_DATE = 2011-07-26  (to cover the frozen XAU CTS universe start)
REQUIRED_END_DATE   = 2026-07-27  (to the XAU record boundary; later is fine)
MINIMUM_HISTORY_YEARS = 5.0 (target ~15 years to match the XAU setups and span multiple regimes)
REQUIRED_FIELDS = ts(UTC, explicit open/close semantics), open, high, low, close, volume(traded contracts), ntrades, instrument_id, symbol/expiry
TIMESTAMP_REQUIREMENTS = UTC; documented whether ts is bar-open or bar-close; only fully-closed bars usable at/ before the XAU decision time
CONTRACT_ID_REQUIREMENTS = per-bar contract/expiry identifier so a point-in-time active-contract rule can be applied causally
ROLL_REQUIREMENTS = either a vendor point-in-time continuous contract with DOCUMENTED causal roll methodology, OR raw per-contract outright
                    bars so an internal causal roll (e.g. active = highest completed-session volume on D-1) can be frozen before outcome testing
ESTIMATED_STORAGE = ohlcv-1m GC outrights 2011→present ≈ single-digit GB compressed (well within local capacity); full MBO NOT required and
                    is NOT justified (two prior GC MBO microstructure runs were already negative)
KNOWN_COMPATIBLE_VENDOR_OPTIONS = Databento (GLBX-MDP3 ohlcv-1m GC + definition + statistics) — already the local vendor/tooling
                                  (build_gc_bars.py, foundation_gc/engine.py) so ingestion is turnkey once history is acquired.
                                  Other CME-authorized historical vendors providing genuine traded volume are acceptable if provenance is explicit.
WHY_EXISTING_DATA_FAIL = local GC = ~11 sessions (2026-06-29..07-10), genuine volume but only 106 matched XAU trades (<< 1000) and ~0.03 years
                         (<< 5.0); no multi-year history, no roll construction possible, single regime.
```

## What unblocks the experiment
Acquire the Databento GLBX-MDP3 **ohlcv-1m GC** history (outrights, 2011→present) plus definition + statistics (for causal roll + open
interest). The local tooling already ingests this schema. Once present, this exact mandate runs end-to-end: causal active-contract construction,
roll-contamination diagnosis, causal time-of-day volume normalization, the six predeclared GC information families, the A/B/C/D representation
decomposition (isolating GC real-volume value beyond GC price), the winner-retention frontier, and the full negative-control battery.
```
DATA_PURCHASE_AUTHORIZED = NO — CEO decides acquisition
```
