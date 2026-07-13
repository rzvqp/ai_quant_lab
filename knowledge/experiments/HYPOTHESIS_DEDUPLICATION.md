# HYPOTHESIS_DEDUPLICATION — 54 → 52 → the tested questions

Semantic dedup (not just tags), per ETAPA 2. Compares economic mechanism, conditions, direction, session, regime,
reference level, entry/stop/exit, likely signals, and the closest base strategy. Codex did the cross-type semantic pass.

## Tag-level dedup (Claude, automated)
Clustering by (mechanism, non-marker conditions, type) collapsed **54 → 52** representatives (2 exact-signature
redundancies removed). Full mapping in `EXPERIMENT_REGISTRY.jsonl` (`cluster`, `dedup` fields).

## Cross-type semantic dedup (Codex inline — the important pass)
Tag-clustering keeps different-mechanism items separate even when they ask the SAME question. Codex flagged:
- **MERGE HGv1-044 (C, round_number) + HGv1-004 (A, breakout) → one experiment (EXP-07).** Both test "is the
  round-number the active ingredient in breakouts." Merged into a 2×2 factorial (generic-break / round-break /
  round-non-break / arbitrary-non-break) that cleanly separates round-number, breakout, and their interaction.
- The remaining pool items are distinct questions. HGv1-042 (confirmation increment) and HGv1-050 (level-label
  validity) share sweep INFRASTRUCTURE but test different claims — kept separate.

## Codex: incremental-information check vs S1–S51
Each candidate re-uses an existing family; it is informative ONLY WITH explicit control/ablation arms — otherwise
it just re-runs the family. This drove the spec requirement that every experiment carries a gate-off / factorial /
matched control:
- 042 = S1 vs S21 as a PAIRED identical-sample comparison (new info only as a paired test).
- 043 = S39 + a gate-OFF arm (else reruns S39).
- 044/004 = S22 + factorial ablation arms.
- 048/049 = re-evaluations of S1/S5 as beta diagnostics (correctly diagnostics, not new alpha).
- 050/051 = placebo validations of S1/S2 (new).
- 002 = conditioned S26 (new only if S26 didn't already stratify by confirmation/structure).
- 005 = conditioned S40 (new only as a pre-specified gate on/off).
- 045 = genuinely new (no S1–S51 equivalent).

## Representatives kept and why
For each cluster the representative maximizes Information-Value (not prior/expectancy). The 10 selected span 6
distinct questions (confirmation, efficiency, level-identity, beta, round-number, reversion-type) across 8
different base families — a deliberately DIVERSE set rather than the highest-prior stack.

## Discarded as redundant / not selected
The 36 A-type candidates are mostly O2 stacked-selectivity refinements and O3 level-swaps that re-express the
same few questions already covered by EXP-07/08/09; the 5 F scope-tests are logged for a later boundary phase.
None are lost — all remain in the jsonl for future waves.
