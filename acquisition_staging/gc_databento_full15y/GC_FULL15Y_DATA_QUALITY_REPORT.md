# GC_FULL15Y_DATA_QUALITY_REPORT

**Mandate:** ACQUIRE GC FULL 15Y DATASET · **Divizie:** Data Acquisition · **Data:** 2026-09-03
Read-only audit of the preserved raw DBN (never modified). Metrics: `GC_FULL15Y_AUDIT_METRICS.json`.

## OHLCV (research stream — `GC.v.0` continuous, `ohlcv-1m`)
| Check | Result |
|---|---|
| rows | **5,160,829** |
| first / last bar (UTC) | 2011-07-26 00:00:00Z / 2026-07-27 23:59:00Z |
| duplicate timestamps | **0** |
| out-of-order timestamps | **0** |
| off-grid (non-60s) timestamps | **0** |
| OHLC constraint violations (H≥o/c/l, L≤o/c/h) | **0** |
| zero/negative-price bars | **0** |
| `volume` present (real traded contracts) | **YES** (total 677,066,963 contracts over 15y) |
| `ntrades` present | **NO** — the `ohlcv-1m` schema does not carry ntrades (not fabricated) |
| distinct underlying instrument_ids | 76 (the outrights the continuous series rolled through) |
| trading dates present | 4,656 (incl. Sunday-evening CME sessions) |

**Timestamp semantics (VERIFIED):** `ts_event` = bar **OPEN**, UTC nanoseconds; a 1-min bar covers `[ts, ts+60s)`; a completed bar's information is available at `ts+60s`. Prices float (Databento fixed-point decoded). `TIMESTAMP_SEMANTICS_VERIFIED = YES`.

## Missing days & data-condition flags (preserved, NOT forward-filled)
- **25 weekday dates with no GC bars** — almost all major holidays the CME gold session is closed/curtailed: Good Friday (2012-04-06, 2013-03-29, 2014-04-18, 2015-04-03, 2016-03-25, …), Christmas (2015-12-25), New Year (2016-01-01), year-end sessions. One genuine anomaly: **2014-09-23/24/25 (3 consecutive weekdays absent)** — flagged for the research team.
- **3 Databento-flagged "degraded" days: 2014-06-11, 2014-06-12, 2014-06-13** (reduced source quality per Databento's dataset-condition endpoint; the bars are present but marked reduced-quality). 2014-06-13 also appears among the missing-weekday set.
- Gaps are **preserved as gaps** (weekends, holidays, the 2014 anomaly). No forward-fill, no interpolation, no invented candles.

## Supporting streams
- `definition` (GC.FUT parent): **2,869,910 records** — contract identity / expiry / provenance.
- `statistics` (GC.FUT parent): **12,286,623 records** — daily OI / settlement / session stats for roll diagnostics.

## Verdict
`DATA_QUALITY_GATE = PASS`. Core OHLCV is pristine (0 dup / 0 out-of-order / 0 OHLC violation / 0 non-positive, exact 60s grid, real volume). The 25 holiday/anomaly gaps and 3 degraded 2014-06 days are **documented, not silently repaired**; the research team should treat 2014-06-11..13 and 2014-09-23..25 as reduced-quality/absent when they matter.
