# MECHANISM_DIVERSITY_LOG — new-family expansion (S41-S51)

Objective (CEO): maximize the DIVERSITY of economic mechanisms, not validate one strategy. For each new family
the FIRST question is: what NEW economic mechanism does it test, and how is it different from existing families?
Same frozen engine (mstrat.py byte-identical to 1bc0ffb); new families in `code/mstrat_ext.py`; research/val
split; holdout SEALED; no optimization (definitional fixes only, pre-PnL); no verdicts.

## Batch 1 — untested INGREDIENTS: volume magnitude, return-reversal, divergence, intrabar pressure, streaks

### S41 — Volume-climax reversal  →  NEGATIVE
- **New mechanism:** volume MAGNITUDE (m_volrank) at a price extreme = capitulation/blow-off → reversal.
- **Different from:** all S1-S40 used volume only inside VWAP; none used volume magnitude as a trigger.
- **Result:** 12 hyps, 0 profitable, best −0.039. Volume spikes at extremes do NOT reverse here.

### S42 — Short-term RETURN reversal (overreaction)  →  **POSITIVE (3 RW, +OOS)** ✅
- **New mechanism:** fade the largest L-bar RETURN (serial-dependence / short-term-reversal anomaly); liquidity
  providers get paid to absorb overreaction.
- **Different from:** S8 (distance-from-SMA) — S42 ranks by the realized return magnitude, not level distance.
- **Result:** 12 hyps, 6 profitable, **3 RW**, best exp .148, **best OOS +.176** (L=6, thr=1.2%). Small n (~43).
  A GENUINE NEW positive mechanism (mean-reversion of large short-term moves). Provisional/high-uncertainty (n).

### S43 — Momentum DIVERGENCE (RSI vs price)  →  NEGATIVE
- **New mechanism:** price new extreme while RSI does not confirm (oscillator/price divergence) → reversal.
- **Different from:** S14 (ROC stall, no price-extreme reference); no family used price-oscillator divergence.
- **Result:** 16 hyps, 0 profitable, best −0.101 (fires very often). RSI divergence carries no edge on M15.

### S44 — Intrabar PRESSURE / close-location  →  NEGATIVE
- **New mechanism:** intrabar buying/selling pressure via close-location-value (an order-flow proxy from OHLC).
- **Different from:** all S1-S40 (none use intrabar close position).
- **Result:** 12 hyps, 0 profitable, best −0.071. The OHLC order-flow proxy carries no edge.

### S45 — Consecutive-bar STREAK  →  EXPLORATORY (weak)
- **New mechanism:** sequential run-length; N consecutive same-direction closes → reverse or continue.
- **Different from:** all (none use raw close-streak length). (k=3 excluded pre-PnL: too common to be a "streak".)
- **Result:** 12 hyps, 1 profitable, 0 RW; best fade-of-6-streak exp .045, OOS +.13 but maxDD 39R → EXPLORATORY.

### S46 — Volume-CONFIRMED breakout  →  marginal / EXPLORATORY (OOS-weak)
- **New mechanism:** participation gate — breakout only with volume expansion (tests whether VOLUME is the
  missing ingredient that made S3/S23 breakouts fail).
- **Different from:** S3/S23 by the m_volrank confirmation.
- **Result:** 24 hyps, 1 profitable, 1 RW but exp only .017 and **OOS +.04 (near-null / negative on the rep)**.
  **Finding: volume confirmation does NOT rescue breakout-chasing** — participation is not the missing ingredient.

## Batch 2 — untested INGREDIENTS: weekend gap, duration, NR pattern, engulfing, range-position

### S47 — Weekend-gap fill/continuation (Monday)  →  TECHNICALLY INVALID
- **New mechanism:** Fri-close→Mon-open weekend gap (distinct from S19 intraday gaps).
- **Result:** valid(n≥25)=0 (only 4–10 trades) — weekend gaps large enough are too RARE on this instrument/period
  to test. Cannot be evaluated with the available sample. CLOSED as untestable (not negative).

### S48 — Consolidation-DURATION breakout  →  NEGATIVE
- **New mechanism:** TIME spent compressed (run-length of compression), not the compression level; longer coil → bigger break.
- **Different from:** S23 (compress level + HTF), which ignores duration.
- **Result:** 12 hyps, 0 profitable, best −0.130. Duration-gated breakout is still a breakout → negative.

### S49 — Narrowest-range (NR) breakout  →  TECHNICALLY INVALID (non-selective)
- **New mechanism:** the NR-N single-bar compression pattern as a breakout trigger.
- **Result:** even gated to breakouts within 3 bars of the NR bar, it fires >10% of bars — the raw NR-breakout
  is not a discrete setup on M15. Not tuned further (avoid over-fitting the definition). CLOSED as untestable.

### S50 — Outside-bar / engulfing reversal  →  NEGATIVE
- **New mechanism:** the engulfing (outside) candle as a control-shift signal (required range>ATR for significance).
- **Different from:** all (candlestick pattern not tested).
- **Result:** 12 hyps, 0 profitable, best −0.072. Engulfing bars carry no reversal/continuation edge.

### S51 — Intraday range-position reversion  →  NEGATIVE
- **New mechanism:** position within the developing SESSION range; extremes revert toward the middle.
- **Different from:** S8 (SMA distance) / S26 (VWAP band) — uses the session range envelope (after it forms).
- **Result:** 8 hyps, 0 profitable, best −0.126.

## Summary — mechanism-diversity yield (S41-S51, 11 families)
- **New positive mechanism found: 1 — short-term RETURN reversal (S42)** (mean-reversion of large moves, +OOS).
- Weak/exploratory: S45 (streak), S46 (volume-confirmed breakout — but volume is NOT the missing ingredient).
- Negative: S41, S43, S44, S48, S50, S51. Technically invalid: S47 (too-rare), S49 (non-discrete).
- **Diminishing returns signal:** 1 genuine new positive in 11 new families. The T0 (OHLCV) mechanism space is
  becoming well-mapped. Confirmed pattern across ALL batches: **mean-reversion-flavoured, selective, context-
  specific mechanisms carry edge** (sweep+confirmation, failed-breakout fade, opening-range, round-number,
  short-term reversal, efficiency-gated); **broad breakout/continuation-chasing, volume-magnitude, divergence,
  intrabar-pressure, streaks, engulfing, range-position, and calendar do NOT** (or are overfit).
- **Implication:** further mechanism DIVERSITY on T0 is likely low-yield; the genuinely-new remaining axes
  (intermarket / macro / positioning: DXY, real yields, risk-regime, COT, options) require the T1/T2 data that
  is currently CEO-gated. Recommend: one more small T0 probe batch OR declare the T0 mechanism library mature
  and revisit the Tier-C data-acquisition question.
