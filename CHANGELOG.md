# CHANGELOG — AI Quant Research Lab

## Session 2026-07-14 — Experiment Planner v1 (54 HGv1 -> 10-experiment falsifiable plan, no backtest)
- Built knowledge/experiments/: EXPERIMENT_REGISTRY.jsonl/.md, HYPOTHESIS_DEDUPLICATION.md, EXPERIMENT_PRIORITY_MATRIX.md,
  WAVE_1/2/3_SPEC.md, CLAUDE_CODEX_REVIEW.md; code/experiment_planner_v1.py (structural-valid + dedup + type + info-value).
- Funnel: 54 hypotheses -> 54 structurally valid -> 52 after semantic dedup -> all T0 -> **10 selected** (2 mechanism,
  2 contradiction, 2 beta, 2 placebo, 2 alpha) in 3 waves. Prioritized by INFORMATION VALUE (not expectancy/prior).
- Codex inline: merged HGv1-044+004 into a 2x2 factorial (EXP-07); required explicit control/ablation arms per
  experiment; shared matched-null + label-shuffle harness; hierarchical family-wise multiplicity plan (top risk).
  CODEX FILESYSTEM REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; nothing implemented/run; holdout SEALED; no FDR. Stop after planning.

## Session 2026-07-13 (h) — Hypothesis Generator v1 (architecture + logic, no backtest)
- Built knowledge/generator/: HYPOTHESIS_GENERATOR_V1.md (architecture), code/hypothesis_generator_v1.py (logic),
  GENERATED_HYPOTHESES_v1.jsonl/.md (54 demo candidates), CLAUDE_CODEX_REVIEW.md, generator_summary.json.
- Recombines ONLY existing KB/Ontology (primitives/conditions/invariants/contradictions) — no new primitives,
  NO backtest. 7 operators (O1 transfer, O2 stacked-selectivity, O3 cross-level-type, O4 contradiction-resolver,
  O5 beta-deconfound, O6 placebo, O7 boundary/counterfactual). Hard novelty gate vs S1-S51 signatures: every
  candidate auto-states why-new / contradiction / mechanism / differs-from-all-S1-S51 + refinement-vs-genuinely-new.
- Codex inline review adopted: observational novelty is necessary-not-sufficient (v2 semantic signature),
  O2 anti-inflation guards encoded, added O7, prior->prior_plausibility (hidden from validators). CODEX FS REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; nothing implemented/validated; holdout SEALED; no FDR.

## Session 2026-07-13 (g) — lab ONTOLOGY + knowledge graph + hypothesis generator
- Built knowledge/ontology/: ONTOLOGY.md, INVARIANTS.md (9 invariants), RELATIONS.md (38 observational edges),
  HYPOTHESIS_GENERATOR.md, KNOWLEDGE_GRAPH.json/.jsonl, GENERATED_HYPOTHESES.jsonl, CLAUDE_CODEX_REVIEW.md.
- 42 nodes (19 primitives + 14 conditions + 9 invariants); graph-driven generator emitted **19 candidate
  hypotheses** (11 alpha-candidates, 3 experiments, 2 beta-diagnostics, 3 mechanism-tests). Proposals only.
- Codex inline review adopted: relations made OBSERVATIONAL (one-family evidence can't support causal edges);
  P001-vs-P011 relabelled a matched-contrast; invariant wording softened; hypotheses tagged by kind; added
  Codex's placebo/mechanism-invariance rule (F). CODEX FILESYSTEM REVIEW PENDING.
- Read-only; engine + S1-S51 byte-frozen; no strategy implemented/validated; holdout SEALED; no FDR.

## Session 2026-07-13 (f) — knowledge/ base (behavioral primitives from S1-S51)
- Built official `knowledge/` folder (read-only synthesis; engine + S1-S51 untouched): README, BEHAVIOR_REGISTRY
  (.md/.jsonl), MECHANISM_REGISTRY (copy), STRATEGY_EVIDENCE_MAP, NEGATIVE_EVIDENCE_REGISTRY, CONTRADICTION_REGISTRY
  (10 contradictions), VALIDATION_STATUS, CLAUDE_CODEX_REVIEW, and primitives/ (13 files).
- **19 behavioral primitives** distilled from the CEO's 23 candidates (5 merged): 6 SUPPORTED-EXPLORATORILY
  (confirmed-sweep, failed-breakout-fade, opening-range, round-number, trend-efficiency, short-term-overreaction),
  4 MIXED, 1 INCONCLUSIVE, 8 REPEATEDLY-NEGATIVE. Status never "VALIDATED".
- Codex inline review (mapping/consistency): adopted P014→MIXED, P019 renamed (two subtypes), +4 contradictions
  (C7-C10). CODEX FILESYSTEM REVIEW PENDING (stale sandbox). No strategy/engine change; holdout SEALED; no FDR.

## Session 2026-07-13 (e) — S21-S40 family implementation + Lab Knowledge System (branch family-implementation-s21-s40)
- Implemented 14 new families (Tier A: S21,S23,S26,S38,S39,S40; Tier B: S22,S24,S25,S27,S28,S29,S30,S31) in
  `code/mstrat_ext.py`, reusing the FROZEN engine (mstrat.py byte-identical to 1bc0ffb). 328 hyps; 2 genuine
  positives with +OOS: **S22 (round-number momentum), S39 (trend-efficiency continuation)**. Others negative or
  calendar-overfit (S29/S31 screen-RW but OOS-refuted). No optimization; definitional fixes only (pre-PnL).
- **Lab Knowledge System** built (Claude + Codex inline collaboration): STRATEGY_REGISTRY (2300/375/139),
  dedup 139 RW → 22 distinct, MECHANISM_REGISTRY (13 mechanisms), KNOWLEDGE_REGISTRY (5 falsifiable claims),
  STRATEGY_PROFILES, TOP_STRATEGIES_SHORTLIST (~8 distinct), EXPLORATORY_PORTFOLIO_DIAGNOSTICS, CLAUDE_CODEX_REVIEW.
- Codex consulted via compact inline prompts (TASKs 2-5 complete); its filesystem snapshot is STALE → CODEX
  FILESYSTEM REVIEW PENDING. Shortlist for future matched-null→global-FDR: S5, S2, S1-short, S1-low/swing(prov),
  one momentum rep, S22 (+ S1-low/pdh, S17-pwlow reserve). Calendar excluded (family-wise selection). Nothing
  validated; holdout SEALED; no global-FDR. Not merged.

## Session 2026-07-13 (c) — Matched-null remediation & validation (branch matched-null-validation, consolidated)
- Diagnosed old miscalibration (bare synthetic R vs real-price null); rebuilt Test B on synthetic PRICE series
  through mstrat.simulate. Adversarial battery exposed a 2nd defect (absolute-risk bootstrap → FPR 0.975 under
  drift); fixed via risk/ATR rescaling (drift FPR 0.975→0.00). Calibration+power+adversarial+parity all PASS.
- Pilot on 10 pre-registered real hyps: rejects losers; only S5 survives research+OOS; most fail OOS.
  **ENGINE VERDICT A — MATCHED-NULL VALIDATED** (unstratified). docs/MATCHED_NULL_VALIDATION.md. Global-FDR/holdout CEO-gated.

## Session 2026-07-13 (b) — Portability fix + reproducibility test (CEO-approved, scope-limited)
- **Git checkpoint:** folder was un-versioned → `git init` + baseline commit `85857234bad5172634e9c2b603e873976a204470` (pre-fix, 58 files). Added `.gitignore` (venv/, __pycache__/).
- **Portability (class A only):** `code/mtf.py` `D` repointed from hardcoded Temp → `Path(__file__).resolve().parents[1]/"data"/"market"` (str-typed, env override `AI_QUANT_DATA_DIR`). This single constant feeds the whole campaign chain (mstrat/s1/mtf). Secondary Temp paths (data-rebuild + GC-foundation scripts) classified and DEFERRED as debt D8 (not on campaign path).
- **Environment:** created `venv` (Python 3.14.6); installed requirements + pyarrow (parquet engine missing from requirements = debt D9). Versions newer than original (pandas 3.0.3/numpy 2.5.1/pyarrow 25.0.0).
- **Reproduction = EXACT (Verdict A):** re-ran `run_full_campaign.py` (ENGINE v2) into `results/reproduction_v2/` → bit-exact vs baseline: 1972/1800/357/130/14/9; per-hypothesis parquet max abs diff 0.0; total trades 1,300,740 identical; boolean verdicts identical; 0 Temp reads; holdout SEALED; baseline untouched.
- **Data note (D10):** M15 file has 84,152 bars (docs said 84,151 = wc off-by-one, no trailing newline); proven identical to baseline data. No data/result change.
- New artifacts: PORTABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md, results/reproduction_v2/{full.log, FAMILY_RESULTS.parquet, ENGINE_RUNTIME_PATHS.json, comparison.json}. Marked stale (non-destructive): results/PROJECT_STATE_v1.0.json, docs/ALPHA_REGISTRY.md.
- **Unchanged:** methodology, S1–S20 definitions, thresholds, holdout, p-value engine. Matched-null NOT started (awaits a new CEO gate).

---

## Session 2026-07-12 → 2026-07-13 (AI Quant Research Lab)

Chronological, verified from code/logs. Earlier foundation (COMEX GC) summarized; main work is the pivot to alpha discovery.

## Foundation (closed)
- COMEX GC MBO acquired (Databento, legacy normalization, GCQ6 iid=42011464, 2026-06-29→07-10).
- Phase B: order-book reconstruction validated **bit-exact vs MBP-10** (foundation_gc/engine.py); dual-compatible legacy/new parser.
- MBO micro-structure discovery (trajectory-divergence design): **NEGATIVE** — no reproducible pre-price MBO edge (60k+ hypotheses).

## Pivot → AI Quant Research Lab (alpha discovery)
- Designed 6-AI separation-of-powers architecture (Director/Generator/Backtest/Statistician/RedTeam/Portfolio).
- Built MVP alpha pipeline (code/alpha_lab.py, families.py, campaign.py, run_mtf.py, mtf.py); validated with positive/negative controls.

## Data (XAUUSD)
- Built M15 history 2023→2026 via TradingView **Replay** (pullers/pull_replay_m15.mjs): 84,151 bars.
- Gap-filled ~5,000 missing M15 bars at replay-window boundaries (pull_gapfill.mjs).
- Resampled H1/H4/D1 anchored **17:00 NY (DST-aware)** (code/resample_ny.py).
- **Cross-check vs native TradingView OANDA = PASS** (0 OHLC mismatches, 2023-2026, all DST changes).

## Multi-strategy campaign
- Built ONE common engine `code/mstrat.py` (shared simulate + simulate_ref parity + 20 families + shared null).
- Implemented families **S1-S20**; grammar = 1,972 canonical hyps; parity + smoke PASS; lookahead-safe.
- Discovery Screen V1 **FROZEN**: n≥25, exp_research>0, PF≥1.02, maxDD≤25R, research-only (no OOS). Development-tuned.
- **Engine v1 → v2**: added pre-registered stop-floor `executable_stop=max(strategy_stop, max(2×spread,5×tick,0.10×ATR))`.
- Ran **full S1-S20 historical backtest on engine v2** → results/FAMILY_RESULTS.parquet + full.log:
  **1,972 gen · 1,800 valid · 357 HIST-PROFITABLE · 130 RESEARCH-WORTHY · 14 families profitable · 9 research-worthy.**

## Statistical remediation (in progress)
- Proved **analytic normal-approx p-value INVALID in tail** (S6: 2.1e-54 analytic vs ~0.12 empirical) → retracted from verdicts.
- **S6 audit**: extreme p caused by tiny-stop outliers + profit concentration (skew 8.3, kurt 77.6; top-5=71% profit) = R-normalization artifact.
- **S1-rep robustness**: NOT tiny-stop (risk/ATR 2.12) but outlier/time-concentrated (remove top-1→exp −0.02; edge only 2024). NOT rejected.
- Pilot p-engine (docs/MONTE_CARLO_AUDIT.md): block-bootstrap well-calibrated (synthetic controls) but METHOD UNDER VALIDATION; matched-null miscalibrated (fix pending).
- Pre-registered stop-floor spec (docs/MIN_STOP_FLOOR_PREREG.md); frozen primary statistic = expectancy, one-sided (docs/EMPIRICAL_PVALUE_SPEC.md).

## Retractions
- "S1=drift", "S1/S5/S9 decorrelated", "no RC significant", S1-standalone "6 candidates" — all RETRACTED/superseded (see PROJECT_STATE §9).

## Session close (2026-07-13)
- Consolidated lab (code + data + docs + results + pullers) to durable `C:\Users\MEDION GAMING\ai_quant_lab\`.
- Wrote PROJECT_STATE_v1.0.md, PROJECT_AUDIT.md, NEXT_SESSION.md, CHANGELOG.md, SESSION_CLOSE_S1_S20.md.
