# ALPHA_EXOGENOUS_DATA_REQUIREMENTS

Precise specification of the historical exogenous datasets required to execute `ALPHA-XAUUSD-EXOGENOUS-CONTINUOUS-LOOP-001` (addendum: "identify exactly what historical DXY dataset/specification is required, without fabricating or substituting"). Handed to CEO / Data Acquisition for ratified provisioning. Alpha does NOT self-acquire (§3 no arbitrary scraping; provenance + causal availability must be proven before use).

## Governance requirements for ANY provisioned series (all datasets)
- **Coverage:** must overlap the authorized XAUUSD research periods — **b0 2011-07..2013-09 and b1 2016-01..2018-04** (primary, price-only frontier already run there), and/or **2021-07..2023-12** (native). Protected: 2024+/2025+ excluded.
- **Timestamp semantics:** explicit UTC timestamps; documented bar-close / publication semantics so `EXOGENOUS_FEATURE_AVAILABLE_AT <= XAUUSD_DECISION_TIME` is provable (§5, §8). For continuously-traded series: OHLC with unambiguous bar-close epoch. For releases: authoritative release timestamp (not just date).
- **Vintage (§4):** for any REVISED series (macro econ releases), first-release/vintage values required; revised-as-known-later is forbidden. (Market series DXY/UST-yield levels are not revised, so vintage N/A there — but source/timezone provenance still required.)
- **Provenance (§3):** source, instrument/series ID, timezone, revision policy, coverage, missing periods, frequency, licensing.

## Datasets required, by priority (highest-information first)
| priority | dataset | spec | enables hypotheses |
|---|---|---|---|
| 1 | **DXY (US Dollar Index)** | intraday (M15 or H1) OHLC covering b0/b1 (+2021-2023); UTC; documented bar-close. A ratified continuous DXY or a documented basket proxy. | X1 (USD impulse->gold), X3 (USD+yield agreement), X4 (divergence) |
| 2 | **UST 10Y nominal yield** (DGS10 or intraday futures TNX/ZN) | daily min; intraday preferred for intraday hypotheses; UTC; release/close semantics documented | X2-adjacent, X3, X4 |
| 3 | **10Y real yield (TIPS, DFII10)** | daily; FRED DFII10 or equivalent; publication-lag documented (available next business day) | X2 (real-yield impulse -> gold), X3 |
| 4 | **2s10s / curve** | derived from UST tenors above | X3/X4 curve state |
| 5 | **Positioning / COT (CFTC gold)** | weekly; explicit release timestamp (Fri 15:30 ET, data as of Tue) — causal lag critical | X6 (positioning-regime interaction) |
| 6 | **Historical macro-release calendar + first-release values** covering b0/b1 (NFP, CPI, FOMC, etc.) | authoritative UTC release timestamps + vintage values | X5 (macro-release post-event second-leg) |

## What EXISTS but is UNUSABLE (documented, not used)
- `acquisition_staging/calendar/ff_calendar_2026-W32_*` (ForexFactory, one 2026 week) and `acquisition_staging/news/NEWS_LEDGER.csv` (~2026-08): **2026 protected-future, quarantined/unratified, zero overlap** with any authorized XAUUSD research period. Cannot be used for causal historical discovery.

## Minimal viable first step (if CEO provisions)
A single ratified **DXY H1 series covering b0/b1** would unblock X1/X3/X4 (the highest-prior USD->gold mechanisms) immediately. A ratified **DFII10 daily real-yield series** would unblock X2. Either one is sufficient to resume the loop with a real mechanism-first screen.
