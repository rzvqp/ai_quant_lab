# HYPOTHESIS GENERATOR v1 — architecture & logic

**Deliverable = architecture + logic + demonstration output. NO backtest, NO family implementation, NO
validation** (per CEO). The generator produces NEW candidate hypotheses **exclusively** by recombining existing
Knowledge-Base + Ontology elements (primitives, conditions, invariants, contradictions). It invents **no new
primitives**. Code: `code/hypothesis_generator_v1.py`. Output: `GENERATED_HYPOTHESES_v1.jsonl` / `.md` (49 candidates).

## 1. Design constraints
- Inputs are ONLY: `knowledge/BEHAVIOR_REGISTRY.jsonl` (19 primitives), `knowledge/ontology/KNOWLEDGE_GRAPH.json`
  (nodes/edges/invariants), the contradiction set (C1–C10), and a **signature index of all S1–S51 families**.
- Every emitted candidate MUST state, automatically: **why it is new**, **which contradiction it targets**,
  **which mechanism it tests**, and **how it differs from ALL S1–S51 families**.
- No primitive is invented; only existing mechanisms × conditions × invariants are recombined.

## 2. Pipeline (components & data flow)
```
KB Loader ─▶ Operators (O1..O6) ─▶ Novelty Checker ─▶ Contradiction Linker ─▶ Mechanism/Invariant Tagger
          ─▶ Prior Scorer (heuristic, NOT expectancy) ─▶ Emitter (jsonl + md)
```
- **KB Loader** — parses the primitives, graph and invariants into memory.
- **Operators** — the combination rules that PROPOSE (mechanism, condition-set) candidates (§3).
- **Novelty Checker** — the gate (§4): discards anything an existing family already implements; annotates the rest.
- **Contradiction Linker / Mechanism Tagger** — attaches the targeted contradiction and the mechanism/invariant.
- **Prior Scorer** — a heuristic ordering from parent-primitive support + invariant confidence. **It never uses
  backtest results** (there is no backtest in v1); it only ranks by evidence already in the KB.
- **Emitter** — writes the structured candidates.

## 3. Combination operators (the logic)
- **O1 — Ingredient transfer.** Take a HELPING condition {confirmation, efficiency_gate, psych_level,
  structural_level, extreme_return} and apply it to a currently-NEGATIVE base mechanism (value_area, breakout,
  regime_router, …). Tests whether the invariant that helped elsewhere (I1/I8/I9) generalizes. → alpha-candidates.
- **O2 — Stacked selectivity.** Qualify a POSITIVE mechanism with an ADDITIONAL qualifier condition from another
  positive primitive (only genuine qualifiers, never contextual conditions; skip the mechanism's native one).
  Guard: the candidate must beat BOTH parent primitives (anti feature-stacking / selection inflation). → alpha-candidates.
- **O3 — Cross level-type.** Swap the reference-level type (structural ↔ psychological ↔ statistical) of a
  mechanism, directly testing I8 (Level-Type Dependence). → alpha-candidates.
- **O4 — Contradiction resolver.** For each contradiction C1–C10, emit its separating EXPERIMENT (an ablation
  that isolates the resolving condition). → experiments (not trading hypotheses).
- **O5 — Beta de-confound.** Beta/regime-matched + short-side evaluation of a long positive, attacking I7. → beta-diagnostics.
- **O6 — Placebo / mechanism-invariance.** Randomize level labels / re-time events (preserve local structure);
  a mechanism-driven edge must DIE under the placebo. → mechanism-tests.
- **O7 — Boundary / counterfactual (Codex-added).** Shift ONE threshold/window/horizon of an existing
  mechanism-condition pair, holding all else fixed, to produce a falsifiable **scope claim** (where the edge
  ceases / reverses / stays invariant) — e.g. vary the confirmation window, the opening-range window, the
  efficiency threshold, or the round-number spacing. → scope-tests.

### O2 anti-inflation guards (validation-time, from Codex review)
"Beat both parents" alone is NOT enough. A stacked O2 candidate is only accepted if, when eventually tested:
min effective sample fixed BEFORE evaluation · complexity penalty scaled to the search multiplicity ·
**incremental OOS margin vs EACH parent** (prespecified) · regime/time-block stability · **redundancy guard**
(the added qualifier must add conditional information, not merely proxy the parent) · capped nesting depth.

### Novelty type
Each candidate is classified **refinement** (same mechanism as an existing family, adds a condition) vs
**genuinely_new** (no family shares the mechanism) — Codex's request to separate refinements from new hypotheses.

## 4. Novelty checker (how "differs from all S1–S51" is computed)
Each S1–S51 family has a **signature** = (mechanism_tag, {condition_tags}). Each candidate has a signature =
(mechanism_tag, {added conditions}). `find_conflict(mech, conds)`:
1. If any family has the SAME mechanism and `conds ⊆ family.conditions` → **NOT novel → discarded** (the family
   already implements it).
2. Else the closest family = same mechanism with max condition overlap (or, cross-mechanism, max tag overlap),
   and the **difference = the conditions the closest family LACKS**. This string is the auto-generated
   `why_new` and `differs_from_all_S1_S51`.
This makes non-duplication a hard, checkable gate — not a claim.
**v1 limitation (Codex review):** the tag-subset check is NECESSARY but not SUFFICIENT — semantic duplicates can
hide behind aliases, nested/equivalent predicates, or threshold reparameterizations. **v2** must add a canonical
semantic signature (normalized predicate/feature + direction + horizon + conditioning set + target + invariances)
and implication/equivalence checks, not just subset matching.

## 5. Output schema (per candidate)
`hypothesis_id · operator · kind ∈ {alpha-candidate, experiment, beta-diagnostic, mechanism-test, scope-test} ·
novelty_type ∈ {refinement, genuinely_new} · description · mechanism_tested · conditions · tests_invariant ·
contradiction_targeted · why_new · differs_from_all_S1_S51 · prior_plausibility · data_tier · next_test (deferred) · guardrails`.
**prior_plausibility** is a coarse KB-evidence heuristic (never a probability, never a backtest result); per Codex
it is HIDDEN from validators until hypotheses/tests/decision-rules are frozen, and is NEVER used to alter validation thresholds.

## 6. Demonstration output (54 candidates — GENERATED_HYPOTHESES_v1.md)
38 alpha-candidates · 6 experiments · 2 beta-diagnostics · 3 mechanism-tests · 5 scope-tests. Examples (auto-annotated):
- **HGv1-009** confirmed liquidity_sweep **at a psychological round level** — differs from S1 (adds psych_level,
  borrowed from S22) and from S22 (adds the sweep+confirmation mechanism). Targets C4/C1; tests I1/I8.
- **HGv1-033** failed_breakout fade **at a round level** — differs from S2 (LACKS psych_level). Tests I8; targets C8.
- **HGv1-001** value_area reaction **with a confirmation stage** — differs from S26 (LACKS confirmation). Tests I2/I1; targets C5/C8.
- **HGv1-042** confirmation-ablation on the sweep set (EXPERIMENT) — resolves C1.
- **HGv1-050** liquidity_sweep level-label PLACEBO (mechanism-test) — edge must die if level-driven.

## 7. What v1 does NOT do (by design)
No backtest, no engine call, no screen, no matched-null, no FDR, no holdout, no new primitive, no strategy
implemented. `next_test` records the (deferred) validation path; nothing is executed. Prior confidence is a
KB-evidence heuristic, not a probability of success. All candidates are gated behind a future CEO decision.
