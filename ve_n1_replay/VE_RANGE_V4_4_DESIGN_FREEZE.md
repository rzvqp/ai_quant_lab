# RANGE V4.4 — Design Freeze

**Locks the mechanism/specification. Does not lock any numeric value. Authorized by CEO
(`AUTHORIZE_RANGE_V4_4_DESIGN_FREEZE`) on the basis of `RT-RANGE-V4_4-DESIGN-AUDIT-001` (`ca550d4`,
`V4_4_DESIGN_AUDIT_PASS_WITH_NONBLOCKING_NOTES`, `V4_4_DESIGN_FREEZE_AUTHORIZED_FOR_CEO_DECISION`,
independently re-verified this mandate: local=remote ×4, full 106-line report read in full).**

This artifact is a locking declaration over content already fully specified and independently audited in
`VE-RANGE-V4_4-DESIGN-001` (`236e8e7`) and `VE-RANGE-V4_4-CONVERGENCE-001` (`f241698`). It restates each
locked element with its exact source location rather than re-deriving it, per the standing discipline of
reading an artifact with its producer's exact convention rather than retyping from memory.

```
V4_4_MECHANISM_FROZEN = TRUE
V4_4_NUMERIC_VALUES_FROZEN = FALSE   (7 parameters + 2 anchors remain UNRESOLVED_PARAMETER / pending validation)
```

## Locked elements

| Element | Locked content | Source |
|---|---|---|
| State machine | `CANDIDATE → FORMING → CONFIRMED → WEAKENING → TERMINATED`; no other legal state | `236e8e7` §5 |
| Legal transitions | T1–T9 + T-KILL, exhaustive | `f241698` §3 |
| Transition priority | T-KILL=0 (highest) → formation → confirmation gate → weakening entry (T4 excursion > T5 trailing-degradation) → recovery (AND-for-both-triggers) → termination (OR-for-either-bound) | `f241698` §3 |
| Directional-discrimination architecture | Four causal signals over a bounded trailing window, combined by AND for confirmation; not a single threshold | `236e8e7` §4 |
| Signal roles | ER: `HARD_GATE`. Traversal: `HARD_GATE`. RND: `HARD_GATE`. Alternation: `SUPPORTING_ONLY` (not promotable to hard gate without a new CEO-authorized amendment — mandate §11 explicit). Raw whole-life `normalized_drift`: `DIAGNOSTIC_ONLY`, permanently excluded as a MACRO hard gate | `f241698` §4 |
| `WEAKENING` lifecycle | Dual entry (T4/T5), dual recovery (T6/T7, same gates as confirmation — no weaker re-confirmation path), dual termination (T8/T9) | `f241698` §3 |
| Episode continuation/merge/replacement | Priority: `MERGE` (vs. live structures) → `CONTINUATION` (vs. terminated/weakening priors) → `REPLACEMENT` (default; forced after any `BREAKOUT_ACCEPTED` regardless of zone `IoU`) | `f241698` §6 |
| `NESTING` | Unchanged V4.3 `assign_level`/`DEPTH_LIMIT_EXCEEDED` — not implicated, not touched | `236e8e7` §11 |
| Confirmation-timing semantics | Evidence-gated, not time-gated; duration (`d_macro`) is a floor, not a trigger; `RANGE_CANDIDATE_PRESENT` distinguishes RANGE-PRESENT from FIRST-CONFIRMED-NOW | `236e8e7` §6.1–6.2 |
| Invalidation logic | `WEAKENING_PERSISTENCE_TERMINATED` (new pathway) alongside unchanged `ZONES_DEGENERATE`/`ZONES_INVERTED`/`BREAKOUT_ACCEPTED` | `236e8e7` §6.4 |
| Event semantics | New non-authoritative `RANGE_CANDIDATE_PRESENT`; existing event kinds unchanged in meaning | `236e8e7` §6.2 |
| Reason-code semantics | 29 existing V4.3 codes unchanged, unrenumbered; 11 new additive codes, one per new mechanism | `f241698` §12 |
| Invariants | No-lookahead, prefix/chunk/snapshot invariance (carried over in kind), no simultaneous contradictory terminals, bounded V4.4-owned memory, no stale RANGE after termination, no duplicate confirmed episode without explicit `REPLACEMENT`, discrimination-gate monotonicity under recovery | `236e8e7` §9 |
| Snapshot/versioning plan | New `range-hierarchical-v4.4`/`range-hierarchical-v4.4-snapshot`; fail-closed across the V4.3/V4.4 boundary; `config_id` deferred until parameters resolve; fingerprint computed-after-implementation procedure (not faked) | `f241698` §12 |
| Adversarial-test semantics | 20 scenarios, input pattern/expected chronology/events/forbidden-output/rule-exercised per scenario | `236e8e7` §10, confirmed complete by `ca550d4` (no new failure mode found, no scenario added) |
| TP-preservation requirements | Every hard-gate mechanism carries a target-defect/at-risk-population/survival-argument/counterexample row; the core claim is an explicit, undischarged hypothesis, not a demonstrated result | `236e8e7` §12, `f241698` §8 |
| Known-risk register | Slow drifting-equilibrium (false-reject), violent zigzag (false-accept), over-merge (`IOU_CONTINUE` too loose) — each fail-closed, each with a named test, none blocking | `f241698` §10 |

## Explicit non-locks

`ER_max`, `RND_max` (anchors — currently `0.5`/`1.0`, DERIVED but not yet validated this mandate),
`ALT_MIN` (supporting-only, already settled, not part of this calibration's scope), `W`, `MIN_TRAVERSALS`,
`ER_weakening`, `RND_weakening`, `WEAKENING_MAX_BARS`, `IOU_CONTINUE`, `GAP_MAX` — all remain open pending
`VE-RANGE-V4_4-CALIBRATION-001`. `config_id()` cannot be computed until they resolve.

## Amendment discipline during calibration

No element in the locked table above may change while calibration proceeds. If a calibration finding implies
the *mechanism* itself (not a numeric value) must change, calibration stops immediately with
`V4_4_CALIBRATION_FOUNDATIONAL_CONFLICT` and returns to CEO — the design is not silently amended. This freeze
artifact is the reference against which that check is made.
