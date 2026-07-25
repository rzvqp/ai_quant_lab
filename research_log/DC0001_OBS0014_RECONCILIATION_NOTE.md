# Reconciliation Note: DC-0001 vs OBS-0014

**Status**: CLOSED (2026-07-25), administrative reconciliation only -- per explicit CEO directive
at Alpha 1's official closure. **This note reconciles definitions; it does NOT render a scientific
verdict.** Whether DC-0001 "survives" or "fails" once definitions are aligned is a determination
for Red Team / the Statistician, not for Alpha, consistent with Alpha's exclusively-observational
mandate.

**Type**: Administrative / definitional reconciliation -- NOT a Discovery Candidate, NOT new
market evidence, NOT an addendum. Do not add to `DISCOVERY_CANDIDATE_INDEX.md`.

## The Open Item

`research_log/ALPHA_AUTONOMOUS_STATE.md` and `research_log/KNOWLEDGE_LIBRARY.md` both flagged
`OBS-0014` (`research_log/OBS-0014_velocity_outlier.md`) as an independent statistical test that
appears to **contradict** the frozen `DC-0001` (isolated single-bar velocity outlier -> gradual
multi-bar continuation), with an explicit escalation: "reconcile the exact DC-0001
operationalization... before drawing a conclusion." That reconciliation had not been done.

## Side-by-Side Comparison of What Each Actually Specifies

| Dimension | DC-0001 (`candidate_v1.md`) | OBS-0014 |
|---|---|---|
| Timeframe of the outlier bar | **M15** (H1/H4 used only for surrounding context) | **H1** |
| Outlier definition | Discretionary/visual: one M15 bar's point-distance judged "many times larger" than its immediate M15 neighbors (examples: ~58pt vs. 1-3pt neighbors; ~28pt vs. a similarly small scale) -- no fixed threshold, no ATR normalization | Formal: `\|close-open\|/ATR14 > 1.5`, with an explicit isolation filter (`prior \|body\|/ATR < 0.8`) |
| Forward window measured | "Roughly 1.5-2 hours" following the outlier bar (~6-8 M15 candles) | `fwdK` at K = 3, 6, 12 **H1 bars** (i.e. 3h, 6h, 12h) -- 1.5-2h is not one of the tested horizons |
| Sample | n=2 confirming + 1 contrasting instance, found by deliberate targeted search, judged visually | n=485 outlier bars, systematic scan |
| Claim being tested | Whether the bar's pace alone (independent of direction) precedes a "gradual, smooth" continuation *or* reversal -- direction-agnostic pace/deceleration claim | Whether outlier bars are followed by directional continuation (`dir·(fwdK - drift)`) -- a directional-continuation claim |

## What This Reconciliation Establishes

These are **not the same operationalization of the same claim**. They differ on timeframe (M15 vs.
H1), on outlier definition (raw neighbor-relative visual magnitude vs. ATR-normalized body ratio
with an explicit isolation filter), and on the forward horizon actually tested (OBS-0014 never
tested DC-0001's stated ~1.5-2h window). OBS-0014's own escalation note already anticipated this:
"DC-0001 was defined discretionarily... with a possibly different construction... a contradiction
to reconcile, not a refutation."

Given this, OBS-0014's null result (mild reversal, n.s., n=485 at H1) does not, by itself,
constitute a test of DC-0001 as specified. It is a **related but distinct** hypothesis test that
happens to sample from a similar-sounding phenomenon at a different timeframe and threshold.
Whether a version of OBS-0014's test rebuilt on DC-0001's exact M15/1.5-2h specification would
reproduce DC-0001's discretionary read, or whether it would falsify it as OBS-0014's broader H1
test suggests, is an empirical question this note does not and cannot answer -- that decisive test
belongs to whichever division (Red Team / Statistician) is authorized to run it.

## Disposition

- `KNOWLEDGE_LIBRARY.md`'s DC-0001 row and Open Question #3 are updated to point here and marked
  reconciled-at-the-definitional-level (see that file's changelog).
- `ALPHA_AUTONOMOUS_STATE.md`'s "Discovery Candidates" and "Unresolved questions" sections are
  updated the same way.
- The underlying scientific question (does DC-0001 survive under a matched, correctly-scoped
  test?) remains genuinely open and is explicitly **not** resolved by this note -- it is handed to
  Red Team / the Statistician as a well-defined next test, not closed as a finding either way.

## Cross-References

- `discovery_candidates/DC-0001_isolated_velocity_outlier_then_gradual_continuation/candidate_v1.md`
- `research_log/OBS-0014_velocity_outlier.md`
- `research_log/KNOWLEDGE_LIBRARY.md` §1, §7
- `research_log/ALPHA_AUTONOMOUS_STATE.md`
