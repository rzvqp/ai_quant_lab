# NEXT_SESSION — EXPERIMENT PLANNER v1 · WAVE 1 EXECUTION

The next session begins EXCLUSIVELY with Wave 1. Reconstruct state from the official docs, not from memory.

## Mandatory status (do not change)
- Official branch = **research-main**; official engine = `code/mstrat.py` v2 (FROZEN).
- Wave 1 = **PLANNED, FROZEN, NOT STARTED**. EXP-01…EXP-06 = **NOT IMPLEMENTED / NOT RUN**.
- Wave 2 and Wave 3 = **NOT AUTHORIZED**.
- Holdout = **SEALED**. Global-FDR = **NOT AUTHORIZED**. Matched-null = VALIDATED ENGINE (pilot only).

## First task (exact order)
1. Reconstruct the state from PROJECT_STATE_v1.0.md, SESSION_CLOSE_PRE_WAVE1.md, ARTIFACT_INVENTORY_PRE_WAVE1.md.
2. Confirm the official close commit from Git (`git rev-parse HEAD` on research-main) and match it to SESSION_CLOSE_PRE_WAVE1.md.
3. Read `knowledge/experiments/WAVE_1_SPEC.md` and `WAVE1_HANDOFF.md`.
4. Confirm the six experiments EXP-01…EXP-06 (questions, H0/H1, control arms, primary contrast, matched-null, multiplicity plan).
5. Do NOT modify anything (no engine, no S1–S51, no knowledge graph, no new hypotheses, no holdout).
6. **STOP and wait for explicit CEO approval to implement the Wave-1 harness and run EXP-01…EXP-06.**

## When CEO approves Wave 1 (only then)
- Build `code/wave1_harness.py` (generic matched-null + beta/regime-matching + level-label-shuffle, reusable) and
  `code/run_wave1.py`; write results to `results/wave1/` and `knowledge/experiments/WAVE_1_RESULTS.md`.
- Reuse EXISTING S1/S2/S5/S21/S39 setups only. Enforce the frozen multiplicity plan (one primary contrast/experiment,
  one global family-wise correction). Report interpretable results for every experiment (positive OR negative).
- Feed each result back into the Knowledge Graph (update the named nodes/edges). Then request the CEO gate for Wave 2.

## Do NOT
Open the holdout · run global-FDR · declare validated alpha · modify the engine/S1–S51/screen/matched-null ·
generate new hypotheses · run any experiment before CEO approval · reinterpret results post-hoc.

## Deferred (CEO-gated, not next session)
Global-FDR over the full universe · walk-forward · Red Team · terminal-holdout open · portfolio construction ·
Tier-C data acquisition (S32–S37) · Hypothesis-Generator v2 (semantic signature) · Codex filesystem re-sync.
