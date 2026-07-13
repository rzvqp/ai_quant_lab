# ARTIFACT_INVENTORY_PRE_WAVE1 — 2026-07-14

Consolidated branch `research-main`, 196 tracked files. All artifacts verified present and valid (JSON/parquet load).

## Code (`code/`, 740K)
- OFFICIAL ENGINE (FROZEN): `mstrat.py` (v2, 20 families), `s1.py`, `mtf.py`, `alpha_lab.py`, `run_full_campaign.py`, `run_lot.py`.
- Data build / audits (S1–S20): resample_ny, quality_and_resample, build_gc_bars, s6_audit, robustness_s1, drift_core, pilot_pvalue, calibrate_screen, freeze_screen_v1, validate_*, diag*, gapfind, run_* …
- MATCHED-NULL: `matched_null.py`, `synth_price.py`, `mn_calibration.py`, `mn_power.py`, `mn_adversarial.py`, `run_matched_null_pilot.py`.
- EXTENSION FAMILIES: `mstrat_ext.py` (S21–S51), `run_ext_family.py`.
- KNOWLEDGE SYSTEM: `knowledge_system.py`, `knowledge_gen.py`, `knowledge_gen2.py`, `knowledge_build.py`, `knowledge_ontology.py`, `hypothesis_generator_v1.py`, `experiment_planner_v1.py`.
- STRATEGY-DEV: `stratdev_registry.py`, `stratdev_portfolio.py`.

## Data (`data/market/`, 5.5M) — sha256 verified
`OANDA_XAUUSD_{M15,H1,H4,D1}.csv` (84,152 / 20,832 / 5,450 / 909 bars).

## Results (`results/`, 1.1M)
- S1–S20 campaign: `FAMILY_RESULTS.parquet` (1,972), `full.log`, `PROJECT_STATE_v1.0.json`, run logs; `reproduction_v2/` (exact reproduction).
- Matched-null: `matched_null_validation/` — null_calibration.parquet, power_curve.parquet, adversarial.parquet, pilot_real_hypotheses.parquet, *_summary.json, seeds.json, runtime_versions.json, ENGINE_RUNTIME_PATHS.json, comparison.json.
- Extensions: `ext_families/` — 24 `S*_results.parquet` + `EXT_FAMILY_RESULTS.parquet` (460 hyps).

## Knowledge (`knowledge/`, 393K, 45 files)
- Base: BEHAVIOR_REGISTRY.md/.jsonl (19 primitives), MECHANISM_REGISTRY.md/.parquet, STRATEGY_EVIDENCE_MAP.md, NEGATIVE_EVIDENCE_REGISTRY.md, CONTRADICTION_REGISTRY.md (10), VALIDATION_STATUS.md, README.md, CLAUDE_CODEX_REVIEW.md, primitives/ (13).
- Ontology: ONTOLOGY.md, INVARIANTS.md (9), RELATIONS.md (38 edges), HYPOTHESIS_GENERATOR.md, KNOWLEDGE_GRAPH.json/.jsonl, GENERATED_HYPOTHESES.jsonl, CLAUDE_CODEX_REVIEW.md.
- Generator: HYPOTHESIS_GENERATOR_V1.md, GENERATED_HYPOTHESES_v1.jsonl/.md (54), generator_summary.json, CLAUDE_CODEX_REVIEW.md.
- Experiments: EXPERIMENT_REGISTRY.jsonl/.md, HYPOTHESIS_DEDUPLICATION.md, EXPERIMENT_PRIORITY_MATRIX.md, WAVE_1/2/3_SPEC.md, planner_summary.json, CLAUDE_CODEX_REVIEW.md.

## Docs (`docs/`, 104K)
MATCHED_NULL_SPEC, MATCHED_NULL_VALIDATION, SYNTHETIC_PRICE_GENERATOR, EMPIRICAL_PVALUE_SPEC, MIN_STOP_FLOOR_PREREG,
MONTE_CARLO_AUDIT, ALPHA_REGISTRY (marked stale), STRATEGY_FAMILY_LIBRARY_S21_S40, MECHANISM_DIVERSITY_LOG, S21_S40_IMPLEMENTATION_REPORTS, S21_S31_TIERB_CONSOLIDATED.

## Tests (`tests/`, 16K)
test_synthetic_generator.py, test_matched_null_parity.py, test_matched_null_calibration.py.

## Root-level registries & reports
STRATEGY_REGISTRY.parquet/.md, STRATEGY_CANDIDATE_REGISTRY.parquet, STRATEGY_DEDUPLICATION_REPORT(.md/_S1S20.md),
TOP_STRATEGIES_SHORTLIST(.md/_S1S20.md), STRATEGY_PROFILES.md, STRATEGY_DEVELOPMENT_REPORT.md, MECHANISM_REGISTRY.md/.parquet,
KNOWLEDGE_REGISTRY.md/.jsonl, EXPLORATORY_PORTFOLIO_DIAGNOSTICS.md, EXPLORATORY_CORRELATION_REPORT.md, kb_*.json,
CLAUDE_CODEX_REVIEW.md, PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md.

## State & close docs (root)
PROJECT_STATE_v1.0.md, PROJECT_AUDIT.md, NEXT_SESSION.md, CHANGELOG.md, SESSION_CLOSE_S1_S20.md,
SESSION_CLOSE_PRE_WAVE1.md, BRANCH_CONSOLIDATION_AUDIT.md, ARTIFACT_INVENTORY_PRE_WAVE1.md, WAVE1_HANDOFF.md, requirements.txt.

## Excluded from the tree/archive (by design)
venv/, __pycache__/, *.pyc (gitignored); matched-null battery `*_run.log` stdout (redundant with committed
summaries); GC MBO raw data (`scratchpad/phaseb/data2`, ~1GB, foundation/closed track, re-downloadable).
