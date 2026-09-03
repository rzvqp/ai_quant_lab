# GC OPEN INTEREST — data audit (pre-flight, §2/§3)

Uses ONLY the already-acquired Databento GLBX.MDP3 statistics for GC.FUT (no new purchase). Open interest exists, its causal availability is
established, and point-in-time causality holds.

## §2 pre-flight
```
OI_FIELD_PRESENT = YES            (Databento statistics stat_type=9 OPEN_INTEREST, 183,125 raw records across GC outrights)
OI_STAT_TYPE_IDENTIFIED = YES     (stat_type=9; value in `quantity` = contracts; price=NaN as expected for OI)
OI_UNITS_VERIFIED = YES           (contracts; total-family range 326,581 .. 2,413,366)
OI_TIMESTAMP_SEMANTICS_VERIFIED = YES (ts_event = dissemination time; ts_ref not populated -> ts_event used as availability, conservative)
OI_PUBLICATION_TIMING_VERIFIED = YES (daily batch disseminated ~13-14 UTC; represents prior-session positioning, knowable at ts_event)
OI_CONTRACT_IDENTITY_VERIFIED = YES (per-outright symbols GCN1/GCQ1/...; 22-27 active contracts/day)
OI_HISTORY_START = 2011-07-26 · OI_HISTORY_END = 2026-07-27 · OI_COVERAGE_YEARS ~ 15.0 · OI_UPDATE_FREQUENCY = DAILY (4,566 daily obs)
OI_CAUSALITY_GATE = PASS
```

## §3 point-in-time causality (absolute)
Each daily OI observation carries an availability time = `ts_event` (dissemination). For an XAU decision at T, the OI used is the total-family
OI of the most recent daily observation with `ts_event <= T` (searchsorted, right-1). This guarantees only OI disseminated before the decision
is used — a genuine ~1-day lag. **`FUTURE_OI_OBSERVATIONS_USED = 0`** (verified in the join). No backfilled same-day OI, no lookahead.

## §4 continuous-contract OI construction (frozen before outcomes)
Primary = **DAILY TOTAL-FAMILY GC OI** = sum of open interest across all active GC outrights per session. This is roll-immune (OI migrating
between contracts at roll does not change the total), mechanically well-defined, and fully point-in-time — chosen over front-contract OI (which
needs a per-day roll mapping and shows roll discontinuities). Front-contract OI is noted as a possible diagnostic; total-family is the frozen
primary. `OI_ACTIVE_CONTRACT_RULE = total-family sum`; `OI_ROLL_HANDLING = roll-immune (total)`; `OI_AGGREGATION_RULE = sum across outrights/day`.

## Matched universe
Joined to the 3 frozen CTS setups (reusing the GC price+volume features from GC_VOLUME_V1): SETUP_1 13,418 · SETUP_2 11,605 · SETUP_3 24,617 ·
**TOTAL 49,640** (all trades had OI available; overlap gate PASS). Result in GC_OI_CONTEXT_V1_REPORT.md.
