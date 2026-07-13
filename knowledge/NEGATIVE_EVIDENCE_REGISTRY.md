# NEGATIVE_EVIDENCE_REGISTRY — mechanisms that failed (preserved, not deleted)

Negative results are knowledge. All statements are scoped to **XAUUSD OANDA M15, 2022–2025, the tested
definitions** — never universal. "Do not conclude" lines guard against over-generalization.

## N1 — Raw liquidity sweep without confirmation (P011)
- Families: S21 (48 hyps). Aggregate: all negative, best −0.09, maxDD to 262R.
- Tested: side high/low, pool swing/session/pdh-pdl, min-touches 2/3, structural/beyond-raid stops.
- Exception: none. **Correct statement:** "In the tested S21 definitions, reversing immediately on a sweep
  without confirmation was non-positive." **Do not conclude:** "sweeps don't work" (S1 confirmed sweep is positive).
- Overturn test: a confirmation-ablation study in a matched null.

## N2 — Generic trend / pullback continuation (P012)
- Families: S7, S10, S15, S38 (~100 hyps). Aggregate: negative regardless of entry timing (early or on confirmation).
- Exception: efficiency-gated continuation (S39, P005) is weakly positive → the failure is the *generic* thesis.
- **Correct:** "In the tested definitions, generic pullback/trend continuation was negative." **Do not conclude:**
  "trend continuation never works" (efficiency-gated variant survives).
- Overturn test: exhaustive entry-timing sweep + regime conditioning in a matched null.

## N3 — Breakout / expansion chasing (P013)
- Families: S3, S4, S23 (HTF-filtered), S46 (volume-gated), S48 (duration-gated), S49, S50 (~150 hyps). Negative.
- Exception: round-number breakout (S22, P004) is a distinct LEVEL mechanism, not generic chasing.
- **Finding:** neither an HTF filter, a volume gate, nor a duration gate rescued breakout chasing → **volume is
  NOT the missing ingredient.** **Do not conclude:** "breakouts never work."
- Overturn test: participation + level-context combined gate in a matched null.

## N4 — Value / VWAP reaction (P014)
- Families: S8, S26 (value-area), S27 (VWAP reclaim), S28 (anchored VWAP) (~100 hyps). Mostly negative.
- Exception: S8 (VWAP mean-reversion) marginal OOS +.11 (isolated). **Do not conclude:** "value/VWAP is
  universally negative" — the σ-band VA is a weak proxy; a true volume-profile value area is untested (needs finer data).

## N5 — Calendar / seasonality (P015)
- Families: S18 (time-of-day), S29 (day-of-week), S31 (month-boundary) (~55 hyps). Strong in-sample, FAILED OOS.
- Exception: one weekday (Fri-long) OOS+ but selection-suspect. **Correct:** "calendar effects were strong
  in-sample but failed to replicate OOS under family-wise selection." **Do not conclude:** "proven overfit" —
  say "failed to replicate."
- Overturn test: single pre-registered window, family-wise-corrected, on untouched data.

## N6 — Regime routing (P016), Intrabar pressure (P017), Momentum divergence (P018), Volume confirmation (P019)
- Families: S40 / S44 / S43 / S41+S46. All negative on the tested definitions. No exceptions found.
- **Do not conclude** these are impossible — order-flow (P017) plausibly needs tick/MBO data, and a
  stand-aside router (P016) is untested. These are closed on T0 only.

## Technically invalid (untestable on T0, not negative)
- S47 weekend gap (P—): n<25 (gaps too rare). S49 NR breakout: not a discrete setup (non-selective). Neither
  supports nor refutes its mechanism — the sample/definition could not test it.

## Aggregate
Of 51 families, ~30 map to repeatedly-negative or overfit primitives; this is the majority of the T0 library.
The negative set is coherent: **broad, chasing, high-frequency, or unconfirmed signals lose to cost drag and
noise; the survivors are selective, confirmed, mean-reversion-flavoured, level-anchored setups.**
