# WAVE 2 — contradiction resolution (FROZEN SPEC)

Runs after Wave 1's harnesses exist. Each experiment separates two competing explanations with explicit
factorial/control arms (Codex requirement — otherwise it merely re-runs an existing family). Same engine reuse,
research/OOS split, holdout SEALED, primary metric = mean expectancy. No post-hoc interpretation.

---

## EXP-07 (type C, contradiction) — Round-number vs breakout: which is the active ingredient?  [merged HGv1-044 + HGv1-004, resolves C4]
- **Research question:** Is S22's edge from the psychological ROUND LEVEL, from the BREAKOUT, or their interaction?
- **H0:** round-level breakout expectancy ≤ generic breakout expectancy (round number adds nothing).
- **Design — 2×2 factorial (the key upgrade):**
  - A generic breakout (arbitrary range edge), B round-level breakout, C round-level NON-breakout (reaction/fade
    at a round level without a break), D arbitrary-level non-breakout.
  - Contrast 1 (round-number main effect): {B,C} vs {A,D}. Contrast 2 (breakout main effect): {A,B} vs {C,D}.
    Interaction: B − A − (C − D).
- **Held constant:** instrument, entry/exit, costs, sample. **Matched control:** arbitrary-level arms.
- **Outcomes:** round-number main effect > 0 and interaction≈0 → the LEVEL carries the edge (P004↑, I8 supported,
  P013 stays negative); breakout main effect only → round-number is incidental (P004 downgraded); interaction
  dominant → S22 is specifically round-level-break (both ingredients needed).
- **KG updated:** P004, P013, I8; edges P004-OUTPERFORMS_MATCHED_VARIANT-P013.
- **Implementation:** M (reuse S22/breakout setups; add the factorial arms + arbitrary-level control).

## EXP-08 (type C, contradiction) — Return-ranked vs value-referenced reversion  [HGv1-045, resolves C5]
- **Research question:** Does mean-reversion edge come from an extreme REALIZED RETURN (overreaction, S42) or
  from distance to a value/price REFERENCE (S8/S26)?
- **H0:** return-ranked reversion expectancy ≤ value-referenced reversion on matched entries.
- **Design:** on the SAME candidate reversion bars, arm A = fade by extreme-return rank (P006), arm B = fade by
  distance-to-VWAP/value (P014). Matched by entry frequency and holding period.
- **Held constant:** exits, costs, sample, trade count.
- **Outcomes:** A ≫ B → overreaction (return-magnitude) is the mechanism (P006↑, I5 supported, P014 stays weak);
  A ≈ B ≤ 0 → neither reversion reference works; B > A → value reference matters (revisit P014).
- **KG updated:** P006, P014, I5, I8. **Implementation:** M (new return-ranking vs value-reference comparator).

## Wave-2 dependencies
Independent of each other. Both depend on the matched-null harness from Wave 1. Neither may be promoted to an
alpha claim without its Wave-1 placebo/beta context (e.g., EXP-07's round-level result is read alongside EXP-05's
level placebo). Beta diagnostics (Wave 1) may run alongside.
