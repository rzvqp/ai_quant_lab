# WAVE 3 — alpha candidates (FROZEN SPEC)

Runs LAST, and only after the relevant Wave-1 placebo/beta and Wave-2 mechanism results are in. Each alpha test
asks whether a HELPING condition rescues a currently-negative base primitive (ingredient-transfer, O1). Each must
include a gate-ON vs gate-OFF arm and beat BOTH parents, on the matched-null harness. Same engine reuse,
research/OOS split, holdout SEALED. No post-hoc interpretation.

Promotion rule (frozen): an alpha candidate advances toward validation ONLY if (a) it beats its gate-OFF control
AND its parent primitives OOS by the pre-set margin, (b) it survives the matched-null, and (c) it is not explained
by beta (its base's Wave-1 beta diagnostic did not fail). Otherwise it is logged as negative/mixed, not retried.

---

## EXP-09 (type A, alpha) — Does confirmation/structure rescue the value-reaction base?  [HGv1-002, links C8]
- **Research question:** Value/VWAP reaction (P014) is negative; does adding a confirmation stage or a structural
  reference make it positive?
- **H0:** conditioned value-reaction expectancy ≤ max(unconditioned value-reaction, 0).
- **Design:** base = S26/S8 value-reaction; arm A = raw (gate OFF), arm B = require confirmation, arm C = require a
  structural level (not a σ-band). Matched sample.
- **Held constant:** reaction definition, exits, costs, sample.
- **Outcomes:** B/C ≫ A and > 0 OOS → a helping condition generalizes to value-reaction (I1/I2 supported broadly,
  P014 upgraded to mixed-positive); B/C ≈ A ≤ 0 → the condition does NOT generalize here (I9 boundary, P014 stays negative).
- **KG updated:** P014, I1, I2, I8, I9. **Implementation:** M (compose S26/S8 with the confirmation/level filters).

## EXP-10 (type A, alpha) — Does an efficiency gate rescue the always-on router?  [HGv1-005, links C10]
- **Research question:** Regime routing (P016) is negative because it is always-on; does gating deployment on
  trend-efficiency (or standing aside otherwise) make it positive?
- **H0:** efficiency-gated router expectancy ≤ always-on router (and ≤ 0).
- **Design:** base = S40 router; arm A = always-on (gate OFF), arm B = deploy sub-setups only when er ≥ threshold,
  else stand aside. Matched sample; count stand-aside as flat.
- **Held constant:** sub-setup definitions, exits, costs, sample.
- **Outcomes:** B ≫ A and > 0 → selective deployment is the missing ingredient (P016 upgraded, I3 supported —
  stand-aside cuts cost drag); B ≈ A ≤ 0 → routing adds no value even when gated (P016 stays negative).
- **KG updated:** P016, I3, I1. **Implementation:** S–M (reuse S40 + the efficiency gate from S39).

## Wave-3 dependencies
EXP-09 depends on EXP-01 (confirmation contribution) and EXP-06 (level placebo) for interpretation. EXP-10 depends
on EXP-02 (efficiency contribution). Neither is promoted to a validated-alpha track without Wave-1/2 context and a
future CEO gate; both feed their result back into the Knowledge Graph regardless of sign.
