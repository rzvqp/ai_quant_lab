# PROJECT_STATE — AI Quant Research Lab — v1.0 (SESSION CLOSE PRE-WAVE1, 2026-07-14)

Mission (CEO, permanent): discover and build a PORTFOLIO of INDEPENDENT ALPHA FACTORS. Unit of research = alpha
FACTOR (economic mechanism), not a single strategy. Falsification-first. Everything below is verified from
on-disk code/artifacts/Git — nothing reconstructed from memory.

## 0. OFFICIAL STATE (authoritative)
- **Official project home:** the consolidated tree on branch **research-main** (this folder). Portable archive:
  `AI_QUANT_LAB_PRE_WAVE1_2026-07-14.zip` (+ SHA256SUMS.txt, RESTORE_INSTRUCTIONS.md).
- **Official branch:** `research-main` (consolidation of master + matched-null-validation + family-implementation-s21-s40 + strategy-development).
- **Official close commit:** see the final commit on research-main (this doc is committed in it); recorded in SESSION_CLOSE_PRE_WAVE1.md.
- **Official engine:** `code/mstrat.py` = ENGINE v2 (pre-registered stop-floor). FROZEN — byte-identical to baseline 1bc0ffb across all branches. `code/s1.py`, `code/mtf.py`, `code/run_full_campaign.py`, `code/run_lot.py` also frozen.
- **Dataset + hashes (sha256, first 16):** M15 `c777cb9c60972878` (84,152 bars) · H1 `5ff7420ac6698e63` (20,832) · H4 `9a6e1111b6af576e` (5,450) · D1 `a5fc340cfcd2cfc3` (909). Coverage 2022→2026-07, NY-17:00 anchored. Portable path `code/mtf.py D = Path(__file__).resolve().parents[1]/"data"/"market"` (no Temp dependency).
- Runtime: Python 3.14 venv (`pip install -r requirements.txt` + pyarrow). Versions in results/matched_null_validation/runtime_versions.json.

## 1. STRATEGIES IMPLEMENTED
- **S1–S20** (official campaign, `mstrat.py` REGISTRY): 1,972 canonical hypotheses, engine v2.
- **S21–S51** (`mstrat_ext.py`, reuses MS.simulate/MS.load, engine untouched): 24 families implemented+backtested,
  460 hypotheses. NOT implemented: S32–S37 (need external T1/T2 data — CEO-gated). Technically invalid: S47 (weekend
  gap, n<25), S49 (NR breakout, non-selective).
- **Total hypotheses tested (S1–S51): 2,432** (1,972 + 460).

## 2. HISTORICAL RESULTS (research segment; strict validation PENDING)
- **Historically profitable: 383** (S1–S20 357 + S21–S51 26). **Research-Worthy: 143** (130 + 13).
- Positive families with +OOS: S1 (confirmed sweep), S2 (failed-breakout fade), S5 (opening-range), S9/S20 (MTF-momentum, correlated), S22 (round-number breakout), S39 (trend-efficiency), S42 (short-term reversal). Calendar (S29/S31) = in-sample-only overfit.
- All results are EXPLORATORY. No statistical verdicts issued.

## 3. STATISTICAL VALIDATION STATUS
- **Matched-null (Test B): VALIDATED ENGINE (Verdict A)** — calibration (KS p=0.11, FPR covers nominal), power
  (monotone), adversarial (12/12 incl. drift after risk/ATR fix), parity (observed R == MS.backtest) all PASS.
  Applied only to a **10-hypothesis pre-registered pilot**, NOT the full universe. `docs/MATCHED_NULL_VALIDATION.md`.
- **Global-FDR: NOT RUN** on the full eligible universe.
- **Walk-forward / Red Team: NOT RUN.**
- **Terminal holdout (last 20% M15, 16,831 bars): SEALED — never opened.**

## 4. KNOWLEDGE SYSTEM (knowledge/)
- **Knowledge Base:** 19 behavioral **primitives** (BEHAVIOR_REGISTRY): 6 SUPPORTED-EXPLORATORILY, 4 MIXED, 1 INCONCLUSIVE, 8 REPEATEDLY-NEGATIVE. 13 primitive files.
- **Invariants: 9** (I1 Selectivity … I9 Ingredient-Selectivity). INVARIANTS.md.
- **Knowledge Graph:** 42 nodes (19 primitives + 14 conditions + 9 invariants), 38 OBSERVATIONAL edges. KNOWLEDGE_GRAPH.json/.jsonl.
- **Hypothesis Generator v1:** built (7 operators, hard S1–S51 novelty gate). **54 candidate hypotheses generated** (38 alpha / 6 experiment / 2 beta-diagnostic / 3 mechanism-test / 5 scope-test). knowledge/generator/.
- **Experiment Planner v1:** built. 54 → 52 (semantic dedup) → **10 experiments selected** (2 mechanism, 2 contradiction, 2 beta, 2 placebo, 2 alpha) across 3 waves. knowledge/experiments/.

## 5. WAVE 1 STATUS
- **Wave 1 = PLANNED, FROZEN, NOT STARTED.** EXP-01…EXP-06 = NOT IMPLEMENTED / NOT RUN. Wave 2/3 = NOT AUTHORIZED.
- Spec: knowledge/experiments/WAVE_1_SPEC.md. Handoff: WAVE1_HANDOFF.md.

## 6. OPEN BLOCKERS / DEBTS
- Matched-null not yet applied to the full candidate set; global-FDR not run (both CEO-gated).
- Beta confound (I7) unresolved lab-wide (Wave-1 EXP-03/04 address only 2 primitives).
- Hypothesis-Generator novelty gate is TAG-based (v2 needs a canonical semantic signature + implication checks).
- Multiplicity risk across the 10 correlated experiments (mitigated by the hierarchical family-wise plan).
- S32–S37 (intermarket/macro/positioning) blocked on external T1/T2 data acquisition (CEO-gated).
- CODEX FILESYSTEM REVIEW PENDING (its MCP sandbox is stale; all Codex reviews so far are INLINE).
- Secondary Temp paths remain in non-campaign scripts (D8: resample_ny/quality_and_resample/run_prod/run_cycle/build_gc_bars/foundation_gc); pyarrow missing from requirements (D9). Neither affects the campaign or Wave 1.

## 7. FIRST TASK NEXT SESSION
See NEXT_SESSION.md and WAVE1_HANDOFF.md. The next session begins with EXPERIMENT PLANNER v1 — WAVE 1 EXECUTION,
and must STOP for CEO approval before implementing/running anything.
