# CONTRADICTION_REGISTRY — context-dependent contradictions

Each pair is two results that conflict; the resolution is usually a CONTEXT difference (an ingredient that
turns a negative into a positive). These are the highest-value knowledge items — they point at the actual edge.

## C1 — Raw sweep (negative) vs confirmed sweep (positive)
- Claim A: liquidity-sweep reversal is positive (S1, OOS +.29/+.35). Claim B: liquidity-sweep reversal is
  negative (S21). Context difference: **CONFIRMATION stage** (displacement/close-back) present in S1, absent in S21.
- Likely explanation: confirmation filters genuine reversals from continuations. Separating test: a
  confirmation-ablation study on the same signals in a frozen matched null.

## C2 — Generic continuation (negative) vs efficiency-gated continuation (positive)
- Claim A: trend continuation is negative (S7/S10/S15/S38). Claim B: continuation is positive (S39, OOS +.02).
  Context difference: **trend-efficiency gate** (only clean trends). Separating test: efficiency-gate ablation.

## C3 — Calendar strong in-sample vs negative OOS
- Claim A: day-of-week / month effects are strongly positive (S29 exp +.42). Claim B: they are negative OOS
  (S31 OOS −.44). Context difference: **in-sample vs out-of-sample under family-wise selection.** Likely
  explanation: overfitting / multiple testing. Separating test: single pre-registered window on untouched data.

## C4 — Generic breakout (negative) vs round-number breakout (positive)
- Claim A: breakout chasing is negative (S3/S23). Claim B: round-number breakout is positive (S22, OOS +.15).
  Context difference: the breakout LEVEL is a **psychological round number** vs an arbitrary range edge.
  Separating test: round-number vs matched arbitrary-level breakouts in a frozen null.

## C5 — Generic mean-reversion (mixed) vs short-term return reversal (positive)
- Claim A: value/VWAP mean-reversion is mostly negative (S26/S27/S28). Claim B: short-term return reversal is
  positive (S42, OOS +.18). Context difference: reversion **ranked by realized return magnitude** (overreaction)
  vs reversion to a value/price reference. Separating test: return-ranked vs level-referenced reversion in a null.

## C6 — Volume as ingredient: expected to help, did not
- Claim A (prior): breakouts fail because they lack participation. Claim B (result): volume-confirmed breakouts
  (S46) still failed (OOS −.02), as did volume-climax reversal (S41). Context: volume magnitude added no
  predictive content. Explanation: OHLC volume is too coarse / not the missing ingredient. Separating test:
  true order-flow (tick/MBO) data — outside T0.

## C7 — Opening-range momentum (positive) vs generic breakout/expansion (negative)  [added, Codex review]
- Claim A: opening-range break continues (S5, +.18). Claim B: generic range/squeeze breakouts fail (S3/S23/S48).
  Context difference: the **opening auction** is a specific high-information window vs an arbitrary range edge.
  Separating test: opening-range break vs matched non-open breakouts in a frozen null.

## C8 — Failed-breakout fade (positive) vs value/VWAP rejection (negative)  [added, Codex review]
- Claim A: fading a failed break at a prior-day level is positive (S2, +.26). Claim B: rejection at VWAP/value
  edges is negative (S26/S27). Context difference: **prior-day structural level** vs a σ-band value reference.
  Separating test: level-type ablation (structural vs statistical reference) in a null.

## C9 — Volume climax (reversal) vs volume confirmation (continuation)  [added, Codex review]
- Within P019 the two volume subtypes imply OPPOSITE trades (climax→reversal, expansion→continuation) yet BOTH
  are negative. Context: volume magnitude is directionally uninformative here. Separating test: true order-flow data.

## C10 — MTF alignment (mixed) vs regime routing (negative)  [added, Codex review]
- Both claim that CONDITIONING improves selection: P007 (HTF alignment) is mixed-positive; P016 (regime routing)
  is negative. Context difference: alignment conditions on a persistent HTF bias; the router conditions on a
  noisy regime label and stays always-on. Separating test: conditioning-quality ablation (persistent bias vs
  regime label) with a stand-aside option.

## Meta-observation
The recurring resolving ingredient across C1/C2/C4/C5 is **selectivity / a qualifying condition** (confirmation,
efficiency, a psychological level, extreme return). Broad/unconditioned versions lose; conditioned versions
survive. This is the strongest cross-family pattern in the T0 library — and the primary hypothesis to test when
validation resumes.
