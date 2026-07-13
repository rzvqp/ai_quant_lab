# STRATEGY_REGISTRY (S1-S40) — FACTS FROM ARTIFACTS

Every historically-profitable OR research-worthy hypothesis across S1-S40, from the verified on-disk parquets (results/FAMILY_RESULTS.parquet + results/ext_families/EXT_FAMILY_RESULTS.parquet). Full machine table: STRATEGY_REGISTRY.parquet. Read-only; no engine/strategy change.

- Total hypotheses S1-S40: **2300** · historically-profitable: **375** · research-worthy: **139**.
- Registry rows (profitable OR RW): **375**.
- Status values: HISTORICALLY PROFITABLE / RESEARCH WORTHY / FRAGILE / NEGATIVE; strict_validation = STRICT VALIDATION PENDING for all (matched-null validated but global-FDR CEO-gated).
- Missing-at-source fields (yearly, risk/ATR, ledgers) were recovered by read-only re-backtest for the 22 distinct representatives only (see kb_dedup.json).

## Counts by status

| status | count |
|---|---|
| RESEARCH WORTHY | 139 |
| HISTORICALLY PROFITABLE | 118 |
| FRAGILE | 118 |

## Research-Worthy by family

| family | rw_count |
|---|---|
| S1 | 90 |
| S5 | 12 |
| S2 | 6 |
| S9 | 6 |
| S17 | 5 |
| S20 | 5 |
| S29 | 4 |
| S6 | 3 |
| S31 | 2 |
| S8 | 2 |
| S39 | 2 |
| S14 | 1 |
| S22 | 1 |
