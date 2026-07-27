# E013 / E016 pre-test dependence checks — NUMBERS ONLY (2026-07-26)

CEO/Statistician task. Run on the **existing Set A window** (`_common.load`, `pre_holdout` split, M15,
67,321 bars, 2022-12-16 → 2025-10-23) — **the incoming 2011-2022 data was NOT touched.** E013 and E016
implemented exactly as operationalized in `V1_OPERATIONALIZED_CONTRACTS.md`, reusing the inherited
E010/E015 order-block detector (`e010`/`e015` scripts). Script + raw JSON:
`e013_e016_dependence_checks.py`, `e013_e016_dependence_checks_results.json`. No validity conclusion —
that is the Statistician's call. Where a check shows the same defect as E010 or E015, it is stated as
such, not softened.

## Entry counts (distinct entry bars, Set A M15)

| Set | Distinct entry bars | Total rows |
|---|---|---|
| E010 (breaker revisit) | 4,197 | — |
| E013 (first mitigation) | 5,802 | 6,919 |
| E016 (retrace touch) | 5,802 | 6,919 |
| E015 visit-1 | 5,802 | — |
| E015 all visits | 10,075 | — |

## Check 1 — Circularity (verified in the inherited detector code, not the V1 contract)

- Selection window: first break-censored touch within `[ob_idx+1, ob_idx+480]`.
- Outcome window: `movement_profile [entry_idx+1, entry_idx+50]`.
- **windows_overlap = FALSE.** The measurement starts strictly AFTER the mitigation bar; the two windows
  are adjacent, not overlapping. Structure is identical to E015 visit-1: a reversal at the first touch is
  **retained** (break censoring stops only LATER visits), so the reversal outcome is not suppressed.
- **E010's circularity defect is ABSENT in E013 and E016.** (E010's "unflipped" selection window
  `[ob+1, ob+480]` coincided with its outcome window; that coincidence does not occur here.)

## Check 2 — Entry overlap (S18-style)

| Pair | ∩ | % of first set | Jaccard |
|---|---|---|---|
| **E013 vs E016** | 5,802 / 5,802 | **100%** | **1.00** |
| **E013 vs E015 visit-1** | 5,802 / 5,802 | **100%** | **1.00** |
| **E016 vs E015 visit-1** | 5,802 / 5,802 | **100%** | **1.00** |
| E013 vs E015 all visits | 5,802 / 5,802 | 100% | 0.58 |
| E013 vs E010 | 652 / 5,802 | 11.24% | 0.070 |
| E016 vs E010 | 652 / 5,802 | 11.24% | 0.070 |

- **The S18 defect is PRESENT and total.** E013, E016, and E015 visit-1 are the **identical entry set**
  (100% of the same bars). E013 and E016 are not two hypotheses — they are one.
- Overlap with E010 (breaker/flipped population) is 11.24%.

## Check 3 — Repeated measurements per order-block zone (E015-style)

E013 and E016 are byte-identical here (same detector, same events):

| | E013 | E016 |
|---|---|---|
| OB events (rows) | 6,919 | 6,919 |
| Distinct zones (`ob_idx`) | 5,803 | 5,803 |
| Duplicate OB events (re-detection) | 1,116 | 1,116 |
| Exact-duplicate entry rows | 1,116 | 1,116 |
| Forward 50-bar overlap: median | 5 | 5 |
| — mean / max | 4.89 / 15 | 4.89 / 15 |
| — % with zero overlap | 0.62% | 0.62% |

- **The E015 re-detection defect is PRESENT.** E013 and E016 use the same `detect_obs`, so they inherit
  it: 1,116 of 6,919 rows are exact duplicates from the same zone re-detected by multiple displacement
  bars; each entry's 50-bar forward window overlaps a median of 5 other entries.

## Facts summary (no validity call)

| Defect | E013 | E016 |
|---|---|---|
| E010 circularity (overlapping selection/outcome windows) | ABSENT | ABSENT |
| S18 entry redundancy | PRESENT — 100% identical to E016 and to E015 visit-1 | PRESENT — 100% identical to E013 and to E015 visit-1 |
| E015 per-zone re-detection duplication | PRESENT (1,116/6,919 dup rows; fwd-overlap median 5) | PRESENT (same) |
