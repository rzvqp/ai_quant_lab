# CLAUDE_CODEX_REVIEW — Experiment Planner v1

Claude (methodology guardian) + Codex (semantic dedup / feasibility / order critique; inline — filesystem PENDING).

## Roles executed
- **Claude:** structural validation, type classification (A–F), Information-Value scoring, the frozen scientific
  specs (research question / null / alternative / matched control / outcomes-and-interpretation / KG updates /
  stopping rules), and over-claim prevention.
- **Codex (inline):** cross-type semantic deduplication, S1–S51 incremental-information check, implementation-size
  estimates, and wave-order critique.

## Codex findings — adopted
1. **Merged HGv1-044 + HGv1-004 → EXP-07** as a 2×2 factorial (generic-break / round-break / round-non-break /
   arbitrary-non-break) — cleanly separating round-number, breakout, and interaction. (They were the same question.)
2. **Every experiment needs explicit control/ablation arms**, else it merely re-runs an existing family. Encoded:
   EXP-01 paired identical-sample; EXP-02 gate-off arm; EXP-07 factorial; EXP-09/10 gate on/off. This is the single
   most important design upgrade.
3. **Build generic matched-null + label-shuffle harnesses once** (EXP-05 builds the shuffle harness; EXP-03/04 build
   the beta/regime-matching pipeline) — reused across experiments; materially reduces implementation size (mostly S–M).
4. **Wave order:** mechanism experiments + shared harnesses in Wave 1; beta diagnostics may run ALONGSIDE (not
   strictly before); placebo randomization rules FROZEN before alpha is read (not statistically before). Reflected
   in the specs (Wave-1 controls/beta/mechanism, Wave-2 contradiction, Wave-3 alpha).
5. **Batch risk = severe multiplicity + correlated event/level/regime reuse.** Adopted as the TOP methodological
   risk: a hierarchical family-wise plan with ONE predeclared primary contrast per experiment and a single global
   multiplicity correction — not 10 independent significance chances (see PRIORITY_MATRIX).

## Codex incremental-information caveats (recorded)
042/048 re-use S1/S21; 049 re-uses S5; 002/005 are conditioned S26/S40 — informative only as paired/gated/factorial
contrasts. 045 is the only pool item with no S1–S51 equivalent (genuinely new).

## Not adopted (with reason)
- None rejected. Codex's methodology points were all adopted. (Claude retained the CEO's Wave1/2/3 template while
  folding in Codex's "beta alongside" and "freeze-before-inspect" refinements.)

## Residual methodological risks (Claude)
1. Multiplicity across 10 correlated experiments (mitigated by the hierarchical family-wise plan; still the top risk).
2. Tag-vs-semantic novelty: the generator's novelty gate is tag-based; a v2 semantic-signature check is still owed.
3. Beta confound (I7) is unresolved lab-wide; EXP-03/04 address it only for two primitives.
4. Small-n on some bases (e.g., the round-number and return-reversal arms) limits power — min-trades and
   UNRESOLVED-if-CI-straddles rules are set to avoid over-reading.

## Status
CODEX INLINE REVIEW: COMPLETE. CODEX FILESYSTEM REVIEW: PENDING (stale sandbox; re-sync to run a file-level pass).
