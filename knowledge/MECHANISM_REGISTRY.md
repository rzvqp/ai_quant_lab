# MECHANISM_REGISTRY (S1-S40)

Mechanism > strategy name. Status reconciled from **Codex inline mechanism review (TASK 4)** + **Claude interpretation**, evidence from verified artifacts. Statuses: SUPPORTED EXPLORATORILY / MIXED / REPEATEDLY NEGATIVE / OVERFIT / INCONCLUSIVE / DATA REQUIRED / VALIDATION PENDING. None are validated alpha (matched-null validated as an engine; global-FDR CEO-gated).

## M01 — liquidity-sweep + confirmation  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Families: S1
- Positive: S1 low/swing OOS +.29, high/pdh(short) OOS +.35, multiple RW
- Negative: low/pdh OOS ~+.01 (~null)
- Contradictory: S21 raw sweep w/o confirmation all negative
- Direction dep: both sides RW · cost sens: low-mid · outlier sens: low (t1<=.09) · OOS: mixed-positive
- Next falsification test: confirmed vs unconfirmed sweep in a frozen side/regime-matched null

## M02 — raw liquidity sweep (no confirmation)  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Families: S21
- Positive: none
- Negative: all 48 variants negative
- Contradictory: none
- Direction dep: short worse (bull) · cost sens: high (freq) · outlier sens: - · OOS: negative
- Next falsification test: none — closed

## M03 — opening-range momentum  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Families: S5
- Positive: exp .166, OOS +.18, positive every year 2022-25
- Negative: long/bull exposure
- Contradictory: S30 kill-zone (fixed-clock range) negative
- Direction dep: long (ny/up) · cost sens: low · outlier sens: low (t1=.02) · OOS: positive
- Next falsification test: beta-adjusted matched null; test in flat/bear regimes

## M04 — failed-breakout fade / mean-reversion at prior-day level  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Families: S2
- Positive: OOS +.26, distinct mean-reversion
- Negative: dd 24R high; limited independent replication
- Contradictory: S12 range-rotation negative
- Direction dep: long · cost sens: low · outlier sens: low · OOS: positive
- Next falsification test: matched null; check short side symmetry

## M05 — MTF trend-momentum (HTF-aligned continuation)  ·  **MIXED** (confidence medium)
- Families: S9,S20,S17-break
- Positive: OOS +.10-.20
- Negative: beta-suspect long
- Contradictory: monthly corr .75-.88 -> ONE bet, not independent confirmations
- Direction dep: long · cost sens: low · outlier sens: low · OOS: positive-but-correlated
- Next falsification test: collapse to one predeclared representative; beta-adjust

## M06 — round-number momentum breakout  ·  **SUPPORTED EXPLORATORILY** (confidence low)
- Families: S22
- Positive: $100 breakout OOS +.15
- Negative: one threshold may be selected; thin evidence
- Contradictory: round-number REJECT negative
- Direction dep: both · cost sens: low · outlier sens: low · OOS: positive
- Next falsification test: test $50/$100/$200 in a frozen null; multiplicity over thresholds

## M07 — trend-efficiency-gated continuation  ·  **MIXED** (confidence low)
- Families: S39
- Positive: high-efficiency variant +OOS .02
- Negative: economically weak, variant-dependent
- Contradictory: raw continuation (S15/S38) negative
- Direction dep: both · cost sens: mid · outlier sens: low · OOS: weak-positive
- Next falsification test: efficiency-gate ablation in matched null

## M08 — breakout / expansion chasing  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Families: S3,S4,S23,S30
- Positive: none material
- Negative: consistent failures
- Contradictory: none
- Direction dep: - · cost sens: high · outlier sens: - · OOS: negative
- Next falsification test: none — closed

## M09 — pullback continuation  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Families: S7,S10,S15,S38
- Positive: none
- Negative: negative across entry-timing choices tested
- Contradictory: S39 efficiency-gated weakly positive
- Direction dep: - · cost sens: mid · outlier sens: - · OOS: negative
- Next falsification test: none — closed (efficiency gate is the live variant, M07)

## M10 — value-area / VWAP reversion  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Families: S8,S26,S27,S28
- Positive: S8 marginal OOS +.11 (isolated)
- Negative: family mostly negative; sigma-band VA is a weak proxy
- Contradictory: S8 exception -> not universally negative
- Direction dep: long · cost sens: high (freq) · outlier sens: low · OOS: mostly-negative
- Next falsification test: true volume-profile value area (needs finer data)

## M11 — calendar / day-of-week / month seasonality  ·  **OVERFIT (failed OOS)** (confidence high)
- Families: S18,S29,S31
- Positive: strong in-sample (exp up to .42)
- Negative: OOS-refuted (S31 OOS -.44); family-wise selection
- Contradictory: one weekday (Fri) OOS+ but selection-suspect
- Direction dep: long-biased · cost sens: low · outlier sens: low · OOS: failed to replicate
- Next falsification test: pre-registered single window in a frozen family-wise-corrected test

## M12 — session-transition  ·  **MIXED** (confidence low)
- Families: S6
- Positive: OOS +.12-.16
- Negative: near-zero expectancy (~.02), fragile
- Contradictory: -
- Direction dep: long · cost sens: mid · outlier sens: low · OOS: positive-but-tiny
- Next falsification test: matched null; is edge > costs?

## M13 — regime routing (meta)  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Families: S40
- Positive: none
- Negative: always-on router doubles cost drag
- Contradictory: -
- Direction dep: - · cost sens: high · outlier sens: - · OOS: negative
- Next falsification test: selective stand-aside router (future redesign)

