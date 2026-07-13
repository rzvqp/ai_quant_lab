# BRANCH_CONSOLIDATION_AUDIT — 2026-07-14

## Branches before consolidation (all off common ancestor 1bc0ffb)
| branch | HEAD | role | disposition |
|---|---|---|---|
| master | 1bc0ffb | portable, reproducible baseline (S1–S20 campaign, engine v2) | base of research-main |
| matched-null-validation | 69747fd | matched-null engine + validation + pilot | **MERGED** into research-main |
| family-implementation-s21-s40 | e3901da | S21–S51 families, knowledge/, ontology, generator v1, planner v1 | **MERGED** |
| strategy-development | 0d776ec | S1–S20 dedup registry, S21–S40 design library | **MERGED** |

## Integration plan (not a blind merge)
1. Verified the official engine (`mstrat.py`/`s1.py`/`mtf.py`/`alpha_lab.py`/`run_full_campaign.py`/`run_lot.py`)
   is **byte-identical across all four branches** (empty diffs) → zero engine conflict.
2. Detected the conflict surface: only overlapping MODIFIED file = `CHANGELOG.md`; everything else additive.
3. Created `research-main` from `master`; merged matched-null → family → strategy-development in that order.

## Conflicts and resolution (documented, not arbitrary)
- **CHANGELOG.md** (content conflict, matched-null vs family): resolved by CHRONOLOGICAL UNION — kept the family
  entries (S21–S51/knowledge/ontology/generator/planner) and re-inserted the matched-null "session (c)" in order.
  No content lost.
- **STRATEGY_DEDUPLICATION_REPORT.md** and **TOP_STRATEGIES_SHORTLIST.md** (add/add, strategy-dev S1–S20 vs
  family S1–S40): kept the **S1–S40 knowledge-system versions as canonical** (strict supersets, Codex-reviewed);
  **preserved the S1–S20 variants** as `STRATEGY_DEDUPLICATION_REPORT_S1S20.md` / `TOP_STRATEGIES_SHORTLIST_S1S20.md`.
  Both variants retained — nothing deleted.
- **No CODE conflicts.** No CEO-DECISION-REQUIRED conflict arose.

## Branches remaining separate
None functionally — all three feature branches are integrated into research-main. The original branch refs
(master, matched-null-validation, family-implementation-s21-s40, strategy-development) are RETAINED for audit/history
and are not deleted.

## Post-consolidation verification (all PASS)
- `mstrat.py`/`s1.py`/`mtf.py` = official baseline versions (git diff vs master empty).
- Portability intact: `mtf.D` resolves to `<root>/data/market`, no Temp dependency; data loads 84,152 M15 bars.
- Engine parity+smoke: PASS. Matched-null tests (synthetic generator, parity): PASS. Generator v1: 54. Planner v1: 54→52.
- JSON (14) / JSONL (5) / parquet (35) all valid. knowledge/ = 45 files present. Experiment Planner present. Wave 1 NOT executed.
- Consolidated tree CLEAN (196 tracked files); deterministic re-runs reproduce committed outputs.
