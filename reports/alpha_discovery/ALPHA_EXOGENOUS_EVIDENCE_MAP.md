# ALPHA_EXOGENOUS_EVIDENCE_MAP

Mandate `ALPHA-XAUUSD-EXOGENOUS-CONTINUOUS-LOOP-001` (2026-08-22). Data-governance classification of every authorized exogenous information class (§6, §28) + the **DXY Data Availability Gate** (addendum). No dataset enters research until causal availability is proven (§3). No fabrication / substitution / arbitrary scraping.

## DXY DATA AVAILABILITY GATE (addendum) — mechanical result
Searched the entire authorized data environment (both `data/market` dirs, `data-acq`, `acquisition_staging`, and the home tree) for DXY / dollar-index / DX / yields / treasury data.
| field | finding |
|---|---|
| DATA_SOURCE | **none** — no DXY (or DXY-proxy) dataset exists in the repository / authorized data environment |
| INSTRUMENT_ID | n/a |
| coverage start/end | n/a |
| native timeframe / timezone / timestamp semantics | n/a |
| row count / missing periods | n/a |
| M15/H1 causally constructible? | n/a (no source) |
| overlap with authorized XAUUSD research periods (b0/b1 2011-2018; 2021-2023) | none |
| protected period present? | n/a |
| suitable for causal historical research? | **NO** |
**Verdict: `DXY_DATA_NOT_AVAILABLE`.** Per the addendum I do NOT fabricate or substitute another instrument (I only hold XAUUSD, so no DXY proxy is constructible either).

## Full exogenous-class classification
| class | dataset present? | status |
|---|---|---|
| A. US Dollar / DXY | no | `DXY_DATA_NOT_AVAILABLE` / `INSUFFICIENT_COVERAGE` |
| B. US Treasury yields | no | NOT_AVAILABLE |
| C. Real yields (TIPS) | no | NOT_AVAILABLE |
| D. Nominal yield curve | no | NOT_AVAILABLE |
| E. Fed / rate-expectation proxies | no | NOT_AVAILABLE |
| F. COT / positioning | no | NOT_AVAILABLE |
| G. Gold fund/flow | no | NOT_AVAILABLE |
| H. High-impact macro-event state | **partial** — `acquisition_staging/calendar/ff_calendar_2026-W32_*` (ForexFactory, 99 rows, one week, 2026-08-02+) + `acquisition_staging/news/NEWS_LEDGER.csv` (506 rows, ~2026-08-10) | `INSUFFICIENT_COVERAGE` + `PROTECTED_FUTURE` (2026) + `UNUSABLE_CAUSALITY` — quarantined/unratified (Data-Acq "supply-never-ratify"); **zero overlap** with any authorized XAUUSD research period; and 2026 XAUUSD is itself protected/holdout. Double-blocked. |

## Conclusion
**No authorized exogenous dataset is available for discovery** on any authorized XAUUSD research period. The only exogenous data that physically exists (2026 calendar/news) is protected-future, quarantined, and non-overlapping. The EXOGENOUS_FRONTIER is authorized in principle but **cannot be executed without provisioning ratified historical exogenous data** — see `ALPHA_EXOGENOUS_DATA_REQUIREMENTS.md`.

Status: **`EXOGENOUS_DATA_GOVERNANCE_BLOCKER`** (§27 genuine blocker — no authorized exogenous research can be performed without violating causal/data governance or fabricating data). Global program ACTIVE; auto-loop paused pending data provisioning. NOT a claim that exogenous alpha is impossible — only that the data to test it does not yet exist in the authorized environment.
