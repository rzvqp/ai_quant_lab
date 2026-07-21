# E011 — Failed 3 Drive Pattern

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Price Action / Structure. **This file is the permanent,
append-only research log for this edge — nothing below is ever deleted or retroactively edited;
refinements are new, dated, appended versions.**

**Fourth edge run under the reordered Tier-1 sequence** (`NEXT_SESSION_FLOW_A.md`, 2026-07-21 priority
audit) — the first pattern-family diversification away from OB/FVG/CHoCH/compression and
session-timing, deliberately selected for this reason in the priority audit. Only E011 authorized this
session. Data loaded exclusively via `_common.load()` (holdout-enforced); no direct CSV read anywhere
in `e011_failed_3_drive_pattern.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> A three-push ("three drive") pattern that fails to complete its third leg produces a reliable
> reversal signal.

Measured outcome (as registered): reversal rate and magnitude following a failed third leg vs. a
completed three-drive. Observable variables: pattern completeness (2 vs. 3 legs), leg symmetry,
volatility regime.

## Definitions predeclared BEFORE any outcome was inspected

1. **Swing point (fractal, k=3)**: a bar whose high/low exceeds the 3 bars on each side — matching
   E009's own already-used fractal-k convention in this program. k=5 and k=8 (E009's other tested
   values) run as a disclosed sensitivity check.
2. **Lookahead-safe confirmation**: a swing point at bar i is only knowable at bar i+k — all forward
   measurement starts from the confirmation bar, never the swing bar itself.
3. **Zigzag simplification**: consecutive same-type swings collapse to the more extreme one (standard
   convention).
4. **Three-drive pattern (symmetry-agnostic, no Fibonacci-ratio curve-fit)**: five alternating swing
   points P0-P1-P2-P3-P4 requiring only P3 beyond P1 in the drive direction — no specific
   retracement/extension ratio is part of the detection criteria.
5. **Completed vs. failed third leg**: the next confirmed swing point in the drive direction after P4
   either exceeds P3 (COMPLETED) or does not (FAILED).
6. **Leg symmetry**: recorded descriptively (tercile slice) only, never a detection criterion.
7. **Response horizon**: 50 bars — the shared program-wide ceiling.
8. **Outcome**: `_profile.movement_profile()` with `direction = -drive_direction` (predicting reversal
   against the drives), relabeled `reversal_confirmed` / `drive_continued` / `stall`.

## Controls

- **Control A — generic swing point**: an ordinary, isolated swing high/low, no 3-drive structure at
  all, same reversal-from-the-extreme question.
- **Control B — random-matched baseline**: fully synthetic random points (seed=42), the same
  convention as every other structural edge's own control in this program.

Timeframes: M15, H1, H4 — all three registered for E011, all present in the clean dataset.

## Results — primary (failed vs. completed 3rd leg)

| Timeframe | n events | Failed reversal rate | Completed reversal rate | p (failed vs. completed) |
|---|---|---|---|---|
| M15 | 4,993 | 52.7% (n=2,738) | 54.2% (n=2,255) | 0.293 |
| H1 | 1,193 | 54.8% (n=664) | 55.4% (n=529) | 0.891 |
| H4 | 344 | 54.3% (n=188) | 57.1% (n=156) | 0.681 |

**No significant difference between failed and completed 3-drives, on any timeframe.** Both hover at
essentially a coin flip (~53-57%).

## Results — controls (failed population vs. each control)

| Timeframe | Control A (generic swing) | p vs. failed | Control B (random matched) | p vs. failed |
|---|---|---|---|---|
| M15 | 53.8% | 0.432 | 51.4% | 0.330 |
| H1 | 54.8% | 1.000 | 55.6% | 0.825 |
| H4 | 61.7% | 0.174 | 50.0% | 0.470 |

Both controls are statistically indistinguishable from the real "failed 3rd leg" population on every
timeframe — the specific 5-point drive structure adds nothing beyond an ordinary swing point or even a
fully synthetic random point. Cross-control (A vs. B) is also non-significant on M15/H1 (p=0.074,
0.825), borderline on H4 (p=0.029, small n=188, not treated as robust given the primary tests are all
null anyway).

## Context slices (failed population)

No significant heterogeneity found on any timeframe for volatility regime (all p>0.05, most p>0.4),
drive direction (bullish vs. bearish setup, p=0.09 M15 — the closest to significance in the whole
analysis, but not significant at conventional α and not replicated on H1/H4, p=0.42/0.29), or leg
symmetry tercile (all p>0.44).

## Robustness — fractal-k sensitivity

Reversal rate stays in the same ~49-61% coin-flip range across k=3, 5, and 8, on all three timeframes
— no parameter choice recovers a meaningfully different result.

## Headline result — V0 NOT SUPPORTED

This is a clean, complete null across the entire predeclared battery: the failed-3rd-leg reversal
rate, the completed-3-drive reversal rate, a generic isolated swing point, and a fully synthetic random
point are all statistically indistinguishable from each other and from a coin flip, on all three
timeframes, at every fractal-k tested, and across every context slice examined. No V1 candidate is
proposed — there is no residual effect anywhere in this analysis to build one from.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** No — no signal distinguishable
   from a random/generic swing point or a fully synthetic reference point, on any timeframe.
2. **Frequency?** 4,993 3-drive events (M15) / 1,193 (H1) / 344 (H4) over ~2.85 years — the pattern
   itself is common; it is the outcome that shows no signal.
3/4. **Days it works/fails?** Not sliced by day-of-week in this pass (deferred — volatility and
   direction were prioritized as the registry's own stated observables, and the primary result is
   already a clean null).
5. **Sessions?** Not sliced in this pass, for the same reason.
6. **Volatility regimes?** No tercile shows a meaningfully elevated reversal rate on any timeframe.
7. **Filters that improve it?** Not searched — would be exactly the "optimize until profitable"
   behavior the protocol forbids, and the fractal-k sensitivity sweep (a disclosed robustness check,
   not a search) already shows no parameter recovers a different result.
8. **Conditions that invalidate it?** The core claim is invalidated broadly — completing vs. failing
   the third leg makes no measurable difference, and the whole "3-drive" structure performs no better
   than an ordinary isolated swing point or pure noise.
9. **Out-of-sample?** Not tested via an explicit time-split; yearly stability of the failed population
   is recorded instead (see `e011_failed_3_drive_pattern_results.json`) and shows no single-year
   concentration.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED. No V1 proposed.** This is a **structural-behavior
Discovery** result only (Protocol v2 §9's own labeling requirement) — no scalping validation
performed, no claim about tradability.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide, not attempted here.
