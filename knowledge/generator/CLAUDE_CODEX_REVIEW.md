# CLAUDE_CODEX_REVIEW — Hypothesis Generator v1

Claude (architect) + Codex (inline; filesystem PENDING) review of the generator architecture/logic.

## Codex inline review — adopted
1. **Novelty rule is necessary-not-sufficient.** Documented as a v1 limitation; v2 needs a canonical semantic
   signature (normalized predicate + direction + horizon + conditioning set + target + invariances) with
   implication/equivalence checks, not just tag-subset matching.
2. **"Beat both parents" is insufficient for O2** (highest data-mining risk). Encoded the extra guards into every
   candidate's `guardrails`: min effective support fixed pre-evaluation, complexity penalty scaled to search
   multiplicity, incremental OOS margin vs EACH parent, regime/time-block stability, redundancy guard (added
   qualifier must add conditional information), capped nesting depth.
3. **Added the missing operator O7 (boundary/counterfactual)** — shift one threshold/window/horizon holding all
   else fixed to produce falsifiable SCOPE claims (5 scope-tests generated).
4. **prior → prior_plausibility**, coarse bins, KB-heuristic only; **hidden from validators until frozen; never
   alters validation thresholds** (anti-anchoring). Provenance recorded for later audit.
5. **Refinement vs genuinely_new** classification added to every candidate (separate refinements from new hypotheses).

## Codex risk ranking (recorded)
O2 (stacked selectivity) is the highest data-mining risk; O3 next; O4–O7 are comparatively safe (they generate
falsification/scope tests, not alpha claims). This ranking is attached so the eventual validation phase weights
the family-wise multiplicity correction accordingly.

## Claude assessment
The generator's value is that novelty is a **hard, checkable gate** (candidates an existing family already
implements are discarded) and that it emits its OWN falsifiers (O4/O6/O7) alongside alpha-candidates. Its main
residual weakness (semantic vs tag novelty, O2 inflation) is exactly what Codex flagged and what v2 must fix
before any of these candidates is implemented.

## Status
CODEX INLINE REVIEW: COMPLETE. CODEX FILESYSTEM REVIEW: PENDING (stale sandbox).
