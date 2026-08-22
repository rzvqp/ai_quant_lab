# DXY_DATA_CONTRACT

**Mandate:** DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001 · **Divizie:** Data Acquisition · **Data:** 2026-08-13
Contract for Alpha Discovery's causal use of the provisioned DXY H1 dataset. **Data only — Alpha performs the research join.**

## Instrument identity (exact — no proxy)
- **Provider:** ICE (Intercontinental Exchange, US).
- **Provider symbol:** `ICEUS:DXY` → resolves to `ICEUS_DLY:DXY` (ICE US, **delayed** feed).
- **Definition:** the **official ICE U.S. Dollar Index**, **cash / index** series (NOT ICE `DX` futures — no contract roll, no methodology break). Type = index.
- **Access route:** TradingView Desktop (delayed ICE index data) via CDP replay-walk.
- **NOT used / NOT substituted:** UUP, EURUSD-inverse, synthetic USD basket, broker DXY proxies (Capital.com/Tickmill/Deriv/…), TVC:DXY (TradingView's own aggregate), DX futures.

## Timestamp semantics (CRITICAL — causal use)
- **Column `time` = bar OPEN time**, absolute **UTC epoch seconds**. (TradingView convention: bar time is the open.)
- **BAR_OPEN_TIME** = `time`. **BAR_CLOSE_TIME** = `time + 3600`. **FEATURE_AVAILABLE_TIME** = `time + 3600` (a completed H1 close is known only at bar close).
- **Timezone / DST:** timestamps are absolute UTC — DST introduces **no ambiguity** in the data (a bar always sits at its true UTC instant; the ICE session shifts with US DST but the epoch is absolute). No wall-clock, no local time, no DST re-localization needed.
- **Session:** trades ~**Sunday 22:00 UTC → Friday 21:00 UTC**, ~24 bars/weekday (uniform across all 24 UTC hours). Closed **Saturday** and **US market holidays** (New Year, Thanksgiving, July 4, etc. → 25–26h gaps). Weekend gap Fri-close → Sun-open.
- **Volume:** the cash index supplies **no volume**; the `volume` column is structurally `0` (schema parity only) — **treat as absent, NOT a trade count.**

## Causal alignment contract (Alpha performs the join)
Invariant Alpha MUST enforce:
```
DXY_FEATURE_AVAILABLE_AT (= dxy.time + 3600)  <=  XAUUSD_DECISION_TIME
```
- To use a DXY H1 close as a feature at an XAUUSD decision, require `dxy.time + 3600 <= xauusd_decision_time`. Never read a DXY bar whose close is at or after the decision instant (no same-bar future-close leakage).
- **Recommended join:** `merge_asof(xauusd, dxy, left_on=decision_time, right_on=(dxy.time+3600), direction='backward')` — i.e. the most recent DXY bar whose close is already known. Do NOT merge on raw `dxy.time` (that would leak the in-progress bar's close).
- The dataset is delivered as a **clean DXY series + these semantics** — it is NOT pre-merged with XAUUSD (no ambiguous pre-join).

## Cross-market availability (matched evidence)
DXY (ICE index) and XAUUSD (OANDA) keep slightly different session/holiday calendars, so not every XAUUSD hour has a same-hour DXY bar. Use the backward-availability join above; the intersection per research block is quantified in `DXY_COVERAGE_OVERLAP_REPORT.json` (B0 97.4%, B1 97.8%, 2021-2023 99.9% of the ratified XAUUSD-H1 hours have an available DXY bar).

## Gap / missing-bar behaviour
Missing observations are **preserved as gaps** (weekends, US holidays, occasional source gaps). **No forward-fill, no interpolation, no invented candles.** A consumer needing a continuous grid must handle gaps explicitly (the raw series is truthful).

## Governance (what Alpha may touch)
- **AVAILABLE_FOR_DISCOVERY:** the three governed slices — `DXY_B0_RESEARCH_SLICE`, `DXY_B1_RESEARCH_SLICE`, `DXY_2021_2023_RESEARCH_SLICE` (and, under explicit governance only, the continuous between-block DXY).
- **PROTECTED — do NOT use as discovery:** 2024-01-01 onward. (The ~4-day 2024 head physically present in RAW is excluded from `NORMALIZED_DXY_H1.csv` and every slice.)
- Data Acquisition provisions and classifies data; it does **not** assign strategy-validation status. See `DXY_EVIDENCE_MANIFEST.json`.

## Files & fingerprints
See `DATA_ACQ_DXY_H1_PROVISIONING_REPORT.md` §5–6 for SHA-256 of RAW, NORMALIZED, and each slice, plus code fingerprints.
