# VE — RANGE V4.4.1 T-STALE CALIBRATION PROTOCOL

**Mandate**: `VE-RANGE-V4_4_1-STALE-CALIBRATION-001`, §7. **Date**: 2026-08-21. **Division**: Validation
Engine (VE). **Precommitted before any result-guided parameter selection** — this document fixes candidate
families, resolution methods, and pass/fail criteria for all four parameters, and the joint
anti-churn/slow-range acceptance bar, **before** any calibration scenario is scored.

Builds on the frozen mechanism (`e2b65bf`, `V4_4_1_T_STALE_MECHANISM_FROZEN=TRUE`). No numeric value chosen
here — this document fixes *method*, not *result*.

```
V4_4_1_CALIBRATION_PROTOCOL_PRECOMMITTED = TRUE
```

---

## 1 — Eligible corpus

**Eligible**: analytical/derivational reasoning against already-ratified V4.4 constants (`W`, `d_macro`,
`n_touch`, `K_struct`), and synthetic price-path construction (known-ground-truth, hand-specified OHLC
sequences, in the same style already used throughout the V4.4 delivery and its own original calibration
`898f149`) — constructed to exercise each named scenario in §4/§5, not sampled from any real market.

**Excluded, absolutely**:
```
FB14                = DIAGNOSTIC_ONLY_ZERO_CALIBRATION_WEIGHT
MB3-001→024         = historical diagnostic evidence only, zero calibration weight
MB3-025→048         = SEALED_FUTURE_EVIDENCE, not decrypted, not inspected, not referenced
```
No parameter value in this mandate may be chosen, ranked, adjusted, or accepted because it recovers any of
the three known FB14 losses, reproduces any FB14/MB3 structure, or improves any historical score. Every
scenario used for selection is constructed **before** being scored against any candidate parameter value —
scenario construction itself never looks at the resulting T-STALE firing pattern before being finalized (this
mirrors `898f149`'s own no-fishing discipline exactly).

---

## 2 — Selection procedure (per parameter)

For each of the four parameters:
1. State the **candidate family** — the bounded set or reasoned single hypothesis to be tested (§6).
2. State the **resolution method** in advance — `RESOLVED_DERIVED` (closed-form or structurally-necessary
   relationship to an existing ratified constant), `RESOLVED_RATIFIED_REUSE` (adopt an existing V4.4 constant
   unchanged), or `RESOLVED_CALIBRATED` (selected via the synthetic-scenario battery, §4/§5).
3. Test the **primary hypothesis first** (the analytically-motivated candidate, if one exists) against the
   full scenario battery before considering any wider family — matching the "prefer fewer parameters, prefer
   derivation over sweep" instruction (mandate §15, design §14).
4. If the primary hypothesis passes the dual-sided bar (§3), it is the resolved value; a wider family is
   examined **only** if the primary hypothesis fails.
5. **One resolution attempt per parameter after the protocol is locked** (mirroring the original V4.4
   calibration's own one-attempt-per-parameter discipline) — a parameter that fails its resolution attempt is
   recorded honestly as `UNRESOLVED` or contributes to a foundational-conflict finding, not re-attempted with
   a silently adjusted method chosen after seeing the failure.

**Maximum permitted calibration attempts**: exactly one full pass through all four parameters' primary
hypotheses, followed by at most one fallback-family pass for any parameter whose primary hypothesis failed. No
further iteration. If the fallback family also fails to produce a dual-sided-satisfying value, the parameter
is recorded `UNRESOLVED` and the joint verdict reflects it (§9 below) — not silently retried a third time.

**Protocol-amendment policy**: any change to this document after this commit requires a new, separately
committed amendment, timestamped, with the reason stated, and — critically — the amendment must be committed
**before** the specific result that would motivate it is treated as final (mirroring the precedent already
used once in this mandate chain, `7a2c93d`'s methodologically-valid pre-selection amendment on the
statistician-foundation branch). No silent, unrecorded protocol change is permitted.

---

## 3 — The central dual-sided acceptance bar (mandate §8, §21.4/§21.5)

A parameter set is acceptable **only if it satisfies both sides simultaneously, on the same value**:

- **(A) Stale release**: in every positive-control scenario (§4), `T-STALE` fires and a fresh candidate is
  subsequently able to form and (where the scenario's true structure is a genuine range) confirm.
- **(B) Slow-range protection**: in every negative-control scenario (§5), `T-STALE` never fires.

No averaging, no majority vote, no "mostly satisfies both." A single negative-control false-positive or a
single positive-control non-release is a failure of that specific candidate value on that specific parameter
combination — recorded as such, not smoothed over. If **no** tested value (primary hypothesis or fallback
family) satisfies both sides across the full battery, the honest result is
`V4_4_1_CALIBRATION_INCOMPLETE` (if isolated to specific scenarios/parameters) or
`V4_4_1_CALIBRATION_FOUNDATIONAL_CONFLICT` (if the mechanism itself appears unable to separate the two
classes at all) — never a forced value chosen because it is merely "close enough."

---

## 4 — Positive-control scenario definitions (staleness MUST fire)

| ID | Construction | Expected T-STALE behavior |
|---|---|---|
| P1 | Early one-sided formation (e.g. a rising channel-like leg) forms a candidate that fails T3 (directionally correct rejection); market then genuinely rotates at a displaced price level with alternating swings, all rejected by the stale candidate — reproduces the FB14-003/FB14-012 *shape* synthetically, not the real bars | `T-STALE` fires once the alternating rejected evidence accumulates; a fresh candidate forms on a later bar and correctly confirms against the new zone |
| P2 | A stale candidate exists; construct repeated, clearly alternating (H,L,H,L,...) rejected swings at a zone with zero overlap to the stale candidate's own zone | `T-STALE` fires |
| P3 | A stale candidate whose current zone has literally zero bars of recent price overlap (price has moved a full multiple of its own width away) while alternating rejected evidence accumulates | `T-STALE` fires |
| P4 | Directly following P1's release: verify the freed slot allows a **new** `StructureV44` to be created from the next bar's swing, and that this new candidate is independently evaluated (and, if genuinely a range, confirms) by the unmodified `_evaluate_macro_formation` | slot released; new candidate forms; new candidate independently reaches `OK_RANGE_MACRO` when its own evidence genuinely qualifies |

## 5 — Negative-control scenario definitions (staleness MUST NOT fire)

| ID | Construction | Expected T-STALE behavior |
|---|---|---|
| N1 | A genuine range whose touches simply arrive slowly (long gaps between swings, all *accepted*, no rejections) | never fires |
| N2 | A genuine range with very few total touches (right at the `n_touch=2` floor on each side), each accepted | never fires |
| N3 | Long low-volatility compression: few or no swings detected at all for an extended span | never fires (no evidence accumulates either way) |
| N4 | A candidate whose second (opposite-side) boundary touch arrives much later than the first, but when it arrives it is accepted (within tolerance) | never fires |
| N5 | A genuine range that initially only touches a sub-band of its eventual full width, with later touches still within tolerance of the evolving median | never fires |
| N6 | A genuine range whose boundary migrates gradually over its life, with each new touch remaining within tolerance of the *current* (not original) median as it evolves | never fires |
| N7 | A strong, clean, one-directional trend for an extended span | never fires (one-sided rejected evidence fails the alternation requirement — the anti-churn property, design §10) |
| N8 | A shallow channel (gentle, still directional) for an extended span | never fires, same mechanism as N7 |
| N9 | A one-sided pullback sequence (repeated same-direction retracements within an overall trend) | never fires — rejections, if any, remain predominantly one-sided |
| N10 | A long quiet period with genuinely no new swing evidence at all, following an already-confirmed-track candidate that is still mid-formation | never fires (identical mechanism to N3) |

These 10 negative controls are a superset of, and were cross-checked against, the design's own 16-scenario
self-falsification table (`9aba9b7` §13) — no new protection claim is introduced here that was not already
argued there; this section operationalizes those arguments into scoreable constructions.

---

## 6 — Candidate family and resolution method per parameter (pre-registered)

| Parameter | Primary hypothesis (tested first) | Resolution method if primary passes | Fallback family (tested only if primary fails) |
|---|---|---|---|
| Rejected-touch window length | `W = 29` (reuse the existing trailing-window constant already governing ER/RND/traversal) | `RESOLVED_RATIFIED_REUSE` | A small family anchored to `d_macro`/`d_internal` (e.g. values structurally related to existing floors, not an arbitrary grid) |
| Minimum rejection count | Derived from `n_touch=2`: the smallest count that cannot be satisfied by a single coincidental rejection, i.e. **more than one** rejection required, reasoned analogously to how `MIN_TRAVERSALS=1` was floor-derived from a concrete counterexample in `898f149` — exact floor value to be derived by explicit counterexample construction during execution, not assumed here | `RESOLVED_DERIVED` if a clean floor-counterexample argument succeeds; else `RESOLVED_CALIBRATED` via a small (low/medium/high) synthetic family | A bounded low/medium/high family only, no fine grid |
| Minimum alternation count | `≥ 1` flip (the same floor-logic already used for `MIN_TRAVERSALS=1`: the smallest value that distinguishes "genuinely two-sided" from "entirely one-sided," since 0 flips is definitionally one-sided) | `RESOLVED_DERIVED` | A slightly higher floor (e.g. requiring more than one flip) only if `≥1` proves insufficiently selective against N7/N8/N9 |
| Minimum candidate age before eligibility | Derived from `n_touch=2` and the structural fact that a candidate needs at minimum enough bars to plausibly register 2 up-touches and 2 down-touches under `_detect_confirmed_swings`'s own `K_struct`-bar fractal lag — expressed as a function of `K_struct`/`n_touch`, not an independently swept constant | `RESOLVED_DERIVED` | A small family anchored to `d_internal` (the next-smallest existing structural floor) only if the primary derivation proves insufficient |

Four parameters, as inventoried in `9aba9b7` §14 and independently confirmed complete (no hidden fifth) by
Red Team (`eeb082e` §3 area 15). No candidate family here is a wide, unstructured sweep — every family is
either a single analytically-motivated hypothesis or a small, structurally-anchored fallback set, consistent
with "prefer fewer parameters" and "no grid-search."

---

## 7 — Tie-breaking

If more than one candidate value within a fallback family satisfies the dual-sided bar (§3) equally (i.e.,
zero failures on both sides), prefer, in order: (a) the value closest to an existing ratified V4.4 constant
(minimizing new free-floating numbers); (b) the value classified `STABLE` rather than `MODERATELY_SENSITIVE`
in the sensitivity sweep (§8); (c) the smaller value (a smaller staleness threshold releases genuinely stuck
candidates sooner, all else equal, without weakening the dual-sided guarantee already independently confirmed
for it). This order is fixed now, before any tie is observed.

---

## 8 — Sensitivity neighborhood

For each resolved parameter, re-run the full positive+negative battery (§4/§5) at a small pre-registered
neighborhood around the resolved value — for count-type parameters (rejection count, alternation count,
minimum age), the neighborhood is `{resolved−1, resolved, resolved+1}` (bounded below at the structural
floor, e.g. never below 1 for a count); for the window-length parameter (if it deviates from the `W=29`
reuse hypothesis), the neighborhood matches `898f149`'s own precedent shape (`{lower, resolved, higher}` at a
comparable relative spacing). Classify each parameter `STABLE` / `MODERATELY_SENSITIVE` / `FRAGILE`
per the mandate's own definitions; a `FRAGILE` classification is recorded honestly as
`PARAMETER_FRAGILITY_FLAG` with its materiality explained, never smoothed into a "close enough" STABLE
verdict.

---

## 9 — Anti-churn acceptance criteria

Over each of N7, N8, N9 (§5) run for an extended synthetic span (long enough to contain multiple candidate
lifetimes under V4.4's own existing candidate-replacement cadence — i.e., long enough that, absent the
alternation safeguard, repeated kill/reform cycles would be observable if they were going to happen at all):
count total `T-STALE` firings. **Acceptance**: zero firings, or a firing count that does not grow with span
length (i.e., not an unbounded, ongoing churn pattern) — matching the design's own prediction that a
one-directional regime should simply never satisfy the alternation requirement, not merely "rarely."

## 10 — Slow-range protection acceptance criteria

Over each of N1–N6, N10 (§5): zero `T-STALE` firings, for every tested parameter value in the sensitivity
neighborhood (§8), not merely the resolved central value. A candidate value that protects slow ranges only at
its exact central value but fails at `resolved±1` is `FRAGILE` on this axis specifically and must be
disclosed as such, not silently accepted because the central point passed.

## 11 — Stale-release acceptance criteria

Over P1–P4 (§4): `T-STALE` fires within the constructed scenario, and P4's downstream chain (fresh candidate
forms, independently evaluated, confirms when genuinely warranted) completes — for every tested parameter
value in the sensitivity neighborhood, same discipline as §10.

## 12 — Failure criteria (restated from mandate §21, operationalized)

- Any negative-control (§5) scenario in which `T-STALE` fires at the resolved value → that value **fails**,
  full stop, regardless of how well it performs on positive controls.
- Any positive-control (§4) scenario in which `T-STALE` never fires within a reasonable constructed span at
  the resolved value → that value **fails** on stale-release.
- A resolved value passing both only through the fallback family, with the sensitivity sweep showing
  `FRAGILE` on either axis → recorded honestly, does not by itself block `PASS_WITH_NONBLOCKING_NOTES` but
  must be disclosed as a materiality-explained flag, never silently dropped.
- No single value found across primary + fallback that clears both sides on all scenarios in the sensitivity
  neighborhood, for any one of the four parameters → that parameter is `UNRESOLVED`, and the overall
  verdict per mandate §21/§22 reflects it honestly.

---

```
V4_4_1_CALIBRATION_PROTOCOL_PRECOMMITTED = TRUE
```

This protocol is now locked. Calibration execution follows as a separate, later commit; only results produced
under this precommitted method may be treated as final.
