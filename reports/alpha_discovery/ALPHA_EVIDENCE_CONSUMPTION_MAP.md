# ALPHA_EVIDENCE_CONSUMPTION_MAP

Mechanical inventory of XAUUSD price-only populations for `ALPHA-XAUUSD-CONTINUOUS-RESEARCH-LOOP-001` after CEO authorization `DIFFERENT_PRICE_ONLY_POPULATION` (2026-08-22). Every region classified before use (§3). Exogenous stays closed (§22). No 2025+/protected-2024 consumption (§5).

## Sources
- **Gated native M5** (`edge_research._common.load`) -> M15/H1/H4/D1, 2021-07-27..2024-06-20. Firewall: gated loader only.
- **Historical `_from_M15_v2` CSVs** (`data/market/OANDA_XAUUSD_{D1,H4,H1}_from_M15_v2.csv`), coverage 2011-07-26..2025-10 WITH GAPS. This is the econ_campaign / H4-bo-raw-S lineage (read_csv). Accessed here via a NEW **causal** loader `hist_data.py` (§6) — never the legacy non-causal D1->H4 merge.

## Per-year regime character (D1, historical CSV)
| year | ndays | ret% | character |
|---|---|---|---|
| 2011 | 113 | -3.0 | top / range (post-blowoff) |
| 2012 | 259 | +4.5 | choppy range |
| **2013** | 192 | **-21.5** | **sustained BEAR** (the key different regime) |
| 2014-2015 | — | — | **MISSING** (manifest gap) |
| 2016 | 252 | +5.9 | recovery |
| 2017 | 257 | +12.5 | uptrend |
| 2018 | 67 | +0.7 | partial (to Apr) |
| 2019 | — | — | **MISSING** |
| 2020 | 101 | -1.0 | high-vol range |
| 2021 | 174 | -5.9 | down/range |
| 2022 | 9 | — | negligible (9 days) |
| 2023 | 257 | +12.1 | uptrend |
| 2024 | 259 | +27.5 | strong uptrend |
| 2025 | 201 | +51.1 | parabolic |

## Region classification (§3)
| region | dates | status | usable for NEW discovery? |
|---|---|---|---|
| b0 | 2011-07-26 .. 2013-09-27 | **DISCOVERY_CONSUMED** (econ_campaign / H4-bo-raw-S DEV) | YES for new mechanism (§4); NOT validation; discloses overlap w/ H4-bo-raw-S |
| gap | 2013-09 .. 2016-01 (2014-15) | **MISSING** | no |
| b1 | 2016-01-11 .. 2018-04-06 | **DISCOVERY_CONSUMED** | YES for new mechanism (§4); NOT validation |
| gap | 2018-04 .. 2020 (2019) | **MISSING** | no |
| calib | 2020-08-11 .. 2021-09-05 | **CALIB_CONSUMED** (H4-bo-raw-S CALIB) | out-of-discovery readout only; NOT primary discovery, NOT validation |
| native | 2021-07 .. 2023-12 | **DISCOVERY_CONSUMED** (exhausted 2021-2023 loop) | already mined; avoid re-mining |
| native-calib | 2024-01 .. 2024-06 | **PROTECTED** (native CALIB / protected-2024) | **NO** |
| holdout | 2024-07 .. 2025+ | **PROTECTED_UNTOUCHED** (2025+ holdout) | **NO** |

## Decision for this loop cycle
- **Discovery territory = b0 (2011-2013) + b1 (2016-2018).** Materially different from the trend-up 2021-2023 population: b0 contains gold's **2013 bear** (sustained downtrend) + 2011-2012 range/top. This is where SHORT / bearish-regime / mean-reversion alpha (proven ABSENT in 2021-2023) could plausibly exist.
- **Governance honored:** these are DISCOVERY_CONSUMED (§4) -> usable for NEW-mechanism discovery, **NOT** called OOS/validation; a survivor needs later independent validation on a genuinely-independent region/owner. CALIB 2020-2021 is an out-of-discovery readout only. **2024-2025 excluded entirely.** No exogenous (§22).
- **Causality (§6):** `hist_data.py` computes HTF context with `FEATURE_AVAILABLE_AT <= DECISION_TIME` (a D1/H4 bar is usable only after its successor bar has opened, i.e., it has fully closed). Verified by assertion. The legacy non-causal merge is NOT used. Frozen strategy artifacts untouched (§6, §7).

## Update (loop cycle 4) — raw intraday coverage for b0/b1
- `OANDA_XAUUSD_M5.csv`: 2021-07..2026-07 ONLY -> **NO M5 for b0/b1** (native window only).
- `OANDA_XAUUSD_M15.csv`: 2011-07..2026-07, ~52k bars in b0 and ~52k in b1 -> **M15 intraday-historical for b0/b1 IS available** BUT: (a) it is the raw source the ratified `_from_M15_v2` H1/H4/D1 were derived from — whether raw M15 is authorized for DISCOVERY (vs only the v2 derivation) is a GOVERNANCE-UNRESOLVED question; (b) the file extends into PROTECTED 2024+ (must be windowed out); (c) intraday price-only was exhausted on 2021-2023 (low prior). Classified `INTRADAY_HISTORICAL_M15_AVAILABLE_BUT_GOVERNANCE_UNRESOLVED` -> requires a CEO data-scope decision before use.
- D1 synthesized bars have no overnight gaps (open==prior close) -> gap frontiers not testable on this data object.
