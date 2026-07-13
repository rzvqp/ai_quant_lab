# BEHAVIOR_REGISTRY — behavioral primitives (S1-S51)

Primitives = observable market behaviors abstracted from strategy families. Status never uses "VALIDATED". Dataset scope: XAUUSD M15, 2022-2025 (predominantly bull). Machine copy: BEHAVIOR_REGISTRY.jsonl.

## P001 — Confirmed Liquidity Sweep Reversal  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Definition: After price sweeps a resting-liquidity level (prior-day/swing/session high/low) it must show a CONFIRMATION (displacement / close-back / consecutive-close) before a reversal entry.
- Observable behavior: Sweep of a level + confirmation is followed by mean-reversion away from the swept side.
- Proposed mechanism: Stop/breakout orders pooled beyond levels are triggered to fill size; confirmation filters the genuine reversal from the continuation.
- Supporting families: S1 (low/swing OOS +0.29; high/pdh short OOS +0.35; multiple RW) · Contradicting: S21 (raw sweep, no confirmation, all negative)
- OOS: mixed-positive · direction both · regimes 2022-25 bull (untested bear) · fragility: spec-dispersion; some low OOS
- Next falsification test: confirmed vs unconfirmed sweep in a frozen side/regime-matched null

## P002 — Failed-Breakout Fade  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Definition: A breakout beyond a prior-day level that fails (closes back inside) is faded back into range.
- Observable behavior: Failed break at prior-day level reverts.
- Proposed mechanism: Breakout buyers trapped on the failed extension are forced to unwind, feeding the fade.
- Supporting families: S2 (low/pdh OOS +0.26) · Contradicting: S12 range-rotation (generic, negative)
- OOS: positive · direction long (tested) · regimes bull · fragility: dd high; one family
- Next falsification test: matched null; test short-side symmetry

## P003 — Opening-Range Momentum  ·  **SUPPORTED EXPLORATORILY** (confidence medium)
- Definition: Break of the session opening range (first ~1h) in the break direction (NY).
- Observable behavior: Opening-range break continues.
- Proposed mechanism: Opening auction sets the day bias; early flow continues intraday.
- Supporting families: S5 (ny/up exp .166, OOS +.18, positive every year 2022-25) · Contradicting: S30 kill-zone (fixed-clock range) negative
- OOS: positive · direction long (tested) · regimes bull · fragility: beta-suspect
- Next falsification test: beta-adjusted matched null across regimes

## P004 — Round-Number Momentum  ·  **SUPPORTED EXPLORATORILY** (confidence low)
- Definition: A clean break THROUGH a psychological round level ($100) continues; rejection at round levels does NOT work.
- Observable behavior: $100-level breakouts continue; rejections fade to noise.
- Proposed mechanism: Clustered orders/stops at round levels; once cleared, momentum follows.
- Supporting families: S22 (mode=breakout, $100, OOS +.15) · Contradicting: S22 (mode=reject, negative)
- OOS: positive · direction both · regimes bull · fragility: single-threshold selection
- Next falsification test: test $50/$100/$200 with multiplicity in a frozen null

## P005 — Trend Efficiency (gated continuation)  ·  **SUPPORTED EXPLORATORILY** (confidence low)
- Definition: Continuation entries only when the trend is CLEAN (high Kaufman efficiency ratio); skip choppy trends.
- Observable behavior: Continuation in efficient trends is weakly positive; raw continuation is negative.
- Proposed mechanism: Clean trends persist; efficiency filters noise.
- Supporting families: S39 (er_thr=0.5, OOS +.02) · Contradicting: S15/S38 (raw continuation, negative)
- OOS: weak-positive · direction both · regimes trend · fragility: tiny effect; threshold-selected
- Next falsification test: efficiency-gate ablation in matched null

## P006 — Short-Term Overreaction / Return Reversal  ·  **SUPPORTED EXPLORATORILY** (confidence low)
- Definition: Fade the largest L-bar return (overreaction); the biggest recent mover reverses.
- Observable behavior: Large 6-bar moves partially reverse.
- Proposed mechanism: Liquidity providers are compensated for absorbing overreaction.
- Supporting families: S42 (L=6, thr=1.2%, OOS +.18, 3 RW) · Contradicting: S8 distance-from-SMA extension (marginal)
- OOS: positive · direction both · regimes bull · fragility: small n / high uncertainty
- Next falsification test: matched null; larger-n replication

## P007 — MTF Trend Alignment  ·  **MIXED** (confidence medium)
- Definition: HTF-aligned (h4/h1) trend-continuation triggers on the LTF.
- Observable behavior: HTF-aligned longs positive but highly correlated with S20/S17-break.
- Proposed mechanism: Higher-TF order-flow bias persists onto lower TF.
- Supporting families: S9 (OOS +.10-.20), S20 (OOS +.17) · Contradicting: correlated cluster; beta-suspect
- OOS: positive-but-correlated · direction long · regimes bull · fragility: beta + redundancy
- Next falsification test: collapse to one predeclared representative; beta-adjust

## P008 — Session Transition  ·  **MIXED** (confidence low)
- Definition: Cross of the prior-session extreme at a new session start (breakout/fade).
- Observable behavior: Weak positive OOS but near-zero expectancy.
- Proposed mechanism: New-session liquidity injection continues or fades the prior range.
- Supporting families: S6 (OOS +.12-.16) · Contradicting: near-zero exp (~.02); fragile
- OOS: positive-tiny · direction long · regimes bull · fragility: near-cost edge
- Next falsification test: matched null; is edge > costs?

## P010 — Liquidity Memory (levels revisited)  ·  **MIXED** (confidence low)
- Definition: Prior-day / weekly reference levels are revisited and react (support/resistance memory).
- Observable behavior: Some level reactions (weekly pw_high break, pw_low reject) positive; prev-day marginal.
- Proposed mechanism: Resting orders and reference anchoring at remembered levels.
- Supporting families: S17 (weekly pw_high-break, pw_low-reject partial +OOS) · Contradicting: S16 (prev-day levels, marginal); several S17 variants OOS-negative
- OOS: mixed · direction both · regimes bull · fragility: knife-edge variants
- Next falsification test: level-memory vs random-line reaction in a frozen null

## P014 — Value / VWAP Reaction (incl. acceptance/rejection)  ·  **MIXED** (confidence medium)
- Definition: Reversion/continuation at VWAP, VWAP bands, value-area edges, or anchored VWAP. NOTE: acceptance and rejection are OPPOSITE-direction subtypes (Codex review) — treated as subtypes, both tested.
- Observable behavior: Mostly negative with one isolated marginal exception (S8) -> MIXED, not uniformly negative (Codex review).
- Proposed mechanism: Auction value should attract price, but the sigma-band VA proxy carries no edge on M15.
- Supporting families: S8 marginal (OOS +.11, isolated) · Contradicting: S26 value-area, S27 reclaim, S28 anchored all negative
- OOS: mostly-negative · direction long · regimes bull · fragility: S8 exception
- Next falsification test: true volume-profile value area (needs finer data)

## P009 — Streak Persistence  ·  **INCONCLUSIVE** (confidence low)
- Definition: N consecutive same-direction closes then reverse (overextension) or continue.
- Observable behavior: Fade of a 6-bar streak weakly positive OOS but high drawdown.
- Proposed mechanism: Short runs overextend / attract mean-reversion.
- Supporting families: S45 (fade k=6, OOS +.13) · Contradicting: maxDD 39R; 0 RW
- OOS: weak-positive · direction both · regimes bull · fragility: high DD
- Next falsification test: drawdown control + matched null

## P011 — Raw Liquidity Sweep (no confirmation)  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Definition: Reverse immediately on a sweep of a level WITHOUT any confirmation.
- Observable behavior: Immediate sweep-reversal loses.
- Proposed mechanism: Without confirmation the sweep is as likely continuation as reversal.
- Supporting families: none · Contradicting: S21 (all 48 variants negative; short side worse)
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: none (closed); contrast documents the value of confirmation (P001)

## P012 — Generic Trend / Pullback Continuation  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Definition: Enter continuation on a pullback to EMA/zone in an established trend, with or without confirmation.
- Observable behavior: Pullback continuation loses regardless of entry timing.
- Proposed mechanism: On M15 gold the pullback whipsaws eat the continuation edge.
- Supporting families: none (efficiency-gated variant is P005) · Contradicting: S7, S10, S15, S38 (all negative, early or late entry)
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: none (closed); the only live variant is efficiency-gated (P005)

## P013 — Breakout / Expansion Chasing (incl. volatility compression)  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Definition: Enter on a breakout/expansion of a range (with HTF filter, volume gate, squeeze, or duration).
- Observable behavior: Breakout chasing loses even with HTF/volume/duration gates.
- Proposed mechanism: Fakeout rate + chasing the move + wide stops dominate.
- Supporting families: none (round-number breakout is a distinct level mechanism, P004) · Contradicting: S3, S4, S23, S46, S48 negative
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: none (closed); volume is NOT the missing ingredient (S46)

## P015 — Calendar Seasonality  ·  **REPEATEDLY NEGATIVE** (confidence high)
- Definition: Fixed weekday / month-boundary / time-of-day directional effects.
- Observable behavior: Strong in-sample but failed to replicate OOS.
- Proposed mechanism: No persistent mechanism; family-wise selection produces in-sample artifacts.
- Supporting families: in-sample only (S29 exp up to .42) · Contradicting: OOS-refuted (S31 OOS -.44; S29-Thu -.03)
- OOS: failed to replicate · direction long-biased · regimes in-sample only · fragility: overfit
- Next falsification test: single pre-registered window, family-wise-corrected, untouched data

## P016 — Regime Routing  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Definition: A meta-router deploying continuation in trend regime and mean-reversion in range regime.
- Observable behavior: Always-on router adds no value.
- Proposed mechanism: Firing in every regime doubles cost drag; a router must mostly stand aside.
- Supporting families: none · Contradicting: S40 (all negative, n very high)
- OOS: negative · direction both · regimes all · fragility: -
- Next falsification test: selective stand-aside router (future redesign)

## P017 — Intrabar Pressure (order-flow proxy)  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Definition: Close-location-value (intrabar buying/selling pressure) continuation/exhaustion.
- Observable behavior: No edge.
- Proposed mechanism: OHLC close position is too coarse a flow proxy on M15.
- Supporting families: none · Contradicting: S44 (negative)
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: requires true order-flow (tick/MBO) data — outside T0

## P018 — Momentum Divergence (RSI/price)  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Definition: Price new extreme while RSI does not confirm -> reversal.
- Observable behavior: No edge; fires very often.
- Proposed mechanism: Divergence is not predictive on M15 gold.
- Supporting families: none · Contradicting: S43 (negative)
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: none (closed)

## P019 — Volume-derived signals (climax reversal + breakout confirmation)  ·  **REPEATEDLY NEGATIVE** (confidence medium)
- Definition: Two OPPOSITE-direction volume subtypes (Codex review): (a) volume-climax at an extreme -> REVERSAL; (b) volume expansion -> breakout CONTINUATION. Both tested; both negative.
- Observable behavior: No edge in either subtype; volume magnitude is not the missing ingredient for breakouts.
- Proposed mechanism: Participation magnitude adds no predictive content on M15 OHLC volume.
- Supporting families: none · Contradicting: S41 climax, S46 volume-confirmed breakout
- OOS: negative · direction both · regimes bull · fragility: -
- Next falsification test: none (closed)

