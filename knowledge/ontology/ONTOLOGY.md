# LAB ONTOLOGY — S1–S51 knowledge graph

The ontology turns the 19 behavioral primitives into a machine-usable **knowledge graph**: nodes (primitives,
conditions/ingredients, invariants) linked by typed, evidence-backed, confidence-weighted relations — which in
turn drives an automatic **hypothesis generator**. Everything is exploratory; nothing is validated alpha.

## Node types (42 nodes)
- **PRIMITIVE (19):** observable behaviors P001–P019 (polarity: positive / mixed / negative / overfit).
- **CONDITION / INGREDIENT (14):** the qualifiers that modify a base behavior, tagged by observed effect —
  HELPS (confirmation, efficiency, psych-level, structural-level, extreme-return), CONTEXT (session window),
  MIXED (HTF alignment), WEAK (VWAP reference), NO-HELP (volume, divergence, intrabar, regime-label),
  OVERFIT (calendar), DEGRADES (cost drag).
- **INVARIANT (9):** the fundamental cross-primitive principles (I1–I9), the deepest layer of the ontology.

## Relation types (38 edges — see RELATIONS.md)
Relations are **OBSERVATIONAL** (per Codex review — one-family evidence cannot support causal claims):
IMPROVED_BY · ASSOCIATED_WITH_FAILURE_WITHOUT · OUTPERFORMS_MATCHED_VARIANT · CONSISTENT_WITH_BETA ·
CONSISTENT_WITH · UNDERPERFORMED_WITH · NO_INCREMENTAL_EDGE_DETECTED · FAILED_OOS · CORRELATED_WITH ·
ASSOCIATED_WITH · SUPPORTS. Every edge cites its evidence and a confidence. Note: the P001-vs-P011 contrast is
an OUTPERFORMS_MATCHED_VARIANT (confirmation also shifts entry/exposure), NOT a clean single-factor contradiction.

## The core structure (why the graph has predictive shape)
The graph's spine is the **Selectivity Principle (I1)**: for a base behavior, an *unconditioned* version
(P011 raw sweep, P012 generic continuation, P013 generic breakout) is NEGATIVE, while the *same behavior + a
helping condition* (P001 = sweep + confirmation, P005 = continuation + efficiency, P004 = breakout + psych-level)
becomes POSITIVE. These appear in the graph as CONTRADICTS edges between a negative and a positive primitive whose
only difference is one condition node — and those condition nodes are exactly the levers a generator can pull.

## The invariants (INVARIANTS.md)
I1 Selectivity · I2 Confirmation-Required · I3 Cost-Drag Floor · I4 Chasing Penalty · I5 Structure-Reversion Edge ·
I6 OOS-Selection Guard · I7 Beta Confound · I8 Level-Type Dependence · I9 Ingredient Selectivity.

## Automatic hypothesis generation (HYPOTHESIS_GENERATOR.md)
The generator walks the graph with six rules — (A) transfer a HELPING ingredient onto a negative base, (B)
stack two positive primitives, (C) de-confound beta, (D) run a contradiction's separating test, (E) data-gated
upgrades, and **(F) placebo / mechanism-invariance** (Codex-added: hypotheses that should survive beta-irrelevant
transforms but fail mechanism-breaking placebos). It emitted **19 candidates, tagged by KIND**: 11 alpha-candidates,
3 experiments, 2 beta-diagnostics, 3 mechanism-tests — separating genuine trading hypotheses from graph-tests and
beta-diagnostics (Codex review). **Proposals only** — nothing implemented, backtested, or validated (CEO constraints).

## How to extend the ontology
When a new family is tested: (1) map it to a primitive (or add one if it has sufficient evidence); (2) add its
condition node(s) and their effect; (3) add evidence-backed edges; (4) update/adjust an invariant only if the
new evidence changes the balance (record support AND against); (5) re-run the generator. If a generated
hypothesis is later tested, its result feeds back as a new edge (confirming or refuting the invariant it probed).

## Guardrails
Read-only synthesis. No engine/strategy/screen/holdout change. Confidence levels are evidence-graded heuristics,
not probabilities. The graph proposes; validation (matched-null → global-FDR → walk-forward → holdout) remains
CEO-gated and is the only path from "candidate" to "alpha".
