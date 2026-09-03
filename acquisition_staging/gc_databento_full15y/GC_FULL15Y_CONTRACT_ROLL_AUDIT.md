# GC_FULL15Y_CONTRACT_ROLL_AUDIT — `GC.v.0` continuous-contract causality

**Mandate:** ACQUIRE GC FULL 15Y DATASET §11 · **Divizie:** Data Acquisition · **Data:** 2026-09-03
Purpose: document EXACTLY what `GC.v.0` means and whether its roll is causal (uses only prior information). **Semantics are NOT invented — taken from Databento's authoritative documentation.**

## What `GC.v.0` means (Databento continuous symbology)
- `GC` = root (COMEX Gold futures); `.v` = **volume-based roll rule**; `.0` = **rank 0 = the front / lead** continuous contract.
- Requested with `stype_in = continuous` on `GLBX.MDP3`.

## Roll rule (authoritative)
- **`ROLL_BASIS` = trading VOLUME of the PREVIOUS DAY.** Per Databento's continuous-contract / symbology documentation, the volume roll ranks the outrights by **the previous day's trading volume** and the continuous series holds the rank-0 (highest-volume) outright.
- **`WHEN_ROLL_BECOMES_EFFECTIVE`:** on the session after the previous day's volume ranking makes a different outright the front — i.e. the switch takes effect once the prior day's volumes are known.
- **`WHETHER_RULE_USES_ONLY_PRIOR_AVAILABLE_INFORMATION` = YES.** The ranking input is the *previous* day's volume, which is fully known at roll time. There is **no use of same-bar or future information**.

## Causality verdict
```
CONTINUOUS_CONTRACT_CAUSALITY = PASS
```
The roll is **point-in-time / causal** — it cannot look ahead (it decides on already-observed previous-day volume). Therefore the continuous stream does NOT introduce a forward-looking roll, and (per §11) Alpha research is not blocked on this ground. *(Data Acquisition provides this data + audit; the research team will independently re-audit the causal construction before any Alpha outcome testing — this report does not substitute for that.)*

## Observed rolls in the acquired data
- **76 distinct underlying instrument_ids**; **75 rolls** over 2011-07-26 → 2026-07-27 (~5/yr, consistent with GC's active Feb/Apr/Jun/Aug/Oct/Dec cycle + volume timing).
- First rolls: 2011-07-31, 2011-12-01, 2012-02-01, 2012-04-01, 2012-06-01. Last rolls: 2025-07-31, 2025-11-27, 2026-01-30, 2026-03-30, 2026-05-29.
- The full roll ledger (timestamp → to_instrument_id) is in `GC_FULL15Y_AUDIT_METRICS.json` (`ROLL_AUDIT`). Supporting `definition` (expiry/contract identity) and `statistics` (daily OI) are preserved for the research team's independent roll diagnostics.

## Discipline (mandate §7)
This is the ONE roll methodology used for the research stream (Databento's volume-based `GC.v.0`). **No second, competing, PnL-selected roll was created.** The definition/statistics streams are for provenance/identity/roll-diagnostics only.
