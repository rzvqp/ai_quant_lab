# N1 RERUN MANIFEST — summary (READ-ONLY, no rerun executed)

**Machine-readable:** `reports/N1_RERUN_MANIFEST.json` (schema `alpha_n1_rerun_manifest_v1`).
**Mandate:** CEO 2026-08-16. **Blocked on:** `N1_HANDOFF_PASS`. **No rerun executed.**

Every existing hypothesis is flagged for canonical rerun. Nothing is deleted, nothing is re-evaluated.
All **355** hypotheses preserved; all **62** `AWAITING_COST` preserved.

## Per-hypothesis fields (each of 355 rows)
`candidate_id` · `strategy_version` · `hypothesis_semantic_fingerprint` · `mechanism_cluster` ·
`current_diagnostic_run_hash` · `current_classifier_version` (`alpha_swing_regime_v1`) ·
`status` = **`GROSS_DIAGNOSTIC_NONCANONICAL`** (with `original_gross_substatus` retained) ·
`needs_n1_rerun` = **TRUE (all 355)** · `needs_cost_rerun` (TRUE for the 62 AWAITING_COST, FALSE otherwise) ·
`preregistration_identity` · `metadata_source`.

## Counts
| metric | value |
|---|---|
| total hypotheses | 355 |
| needs_n1_rerun = TRUE | 355 (all) |
| needs_cost_rerun = TRUE | 62 (= AWAITING_COST_QUEUE) |
| distinct diagnostic run_hashes | 355 |
| metadata from full registry record | 205 |
| metadata grid-backfilled (by run_hash) | 136 |
| unresolved compact records (flagged) | 10 |

**`current_diagnostic_run_hash`** is `evaluation_run_hash(hsf, noncanonical_context)` — the FULL evaluation
identity under the swing classifier (no router, gross cost). This is exactly what the official N1 rerun
must change: comparing the post-rerun run_hash against this value is the fail-closed **proof** the rerun
actually happened on the canonical producer. The `hypothesis_semantic_fingerprint` (economic identity) is
SEPARATE and does **not** change on rerun — same hypothesis, same m.

**Data-completeness honesty:** 10 compact records (e.g. early `GROSS_STRUCTURALLY_FALSIFIED` writes) persist
only `candidate_id/status/reason/ts` and their `run_hash` is not in the current grid — their
`mechanism_cluster` is `UNRESOLVED_COMPACT_RECORD`. They stay flagged `needs_n1_rerun=TRUE`; at rerun time
they are re-expanded from the generator or retired. No silent drop.

## Rerun order (after `N1_HANDOFF_PASS`, not before)
1. Official N1 / Router rerun (canonical eligibility)
2. Cost BASE / STRESS (ratified `AI_TRADER_SHADOW_COST_MODEL_v1`)
3. MDE
4. New shortlist

Until `N1_HANDOFF_PASS`: no rerun, no cost gate, no MDE, no edge, no OOS.
