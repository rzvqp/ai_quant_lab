# STRATEGY FAMILY LIBRARY — S21–S40 (DESIGN ONLY, no code)

Branch: strategy-development. **Design/taxonomy deliverable only** — no implementation, no backtests, no
engine change. Which of these enter implementation is a CEO decision AFTER the matched-null pilot completes.
Every family below is stated as a *causal economic mechanism* (who is forced to trade, why the inefficiency
exists, who supplies the edge), per the lab's mechanism-over-pattern principle — not as a chart pattern.

## 0. Design principles (carried from the S1–S20 post-mortem)
1. **Mechanism first.** Each family must name WHO is on the losing side and WHY the flow is predictable.
   A pattern with no forced-flow story is not admitted.
2. **Do not duplicate S1–S20.** S1–S20 already cover: liquidity-sweep reversal, failed-breakout fade,
   breakout-retest, raw vol expansion, opening-range, session-transition, trend-pullback, extension-MR,
   MTF-momentum, displacement continuation, structure-break reversal, range rotation, imbalance fill,
   momentum exhaustion, trend acceleration, prev-day levels, weekly levels, time-of-day, session gap, hybrid.
3. **Fix the six S1–S20 failures, don't re-run them.** S4/S7/S10/S11/S12/S15 failed because they *chase*
   moves (late entry) or *fade trends without regime conditioning*. S21–S40 either add a directional/regime
   filter, a patient limit entry, or a genuinely different flow source.
4. **Drift-beta awareness.** S1–S20 survivors are mostly long in a bull market (drift-suspect). Prioritise
   mechanisms that are **direction-symmetric** or **market-neutral-ish** (intermarket, positioning, vol,
   calendar) so the eventual factor portfolio is not just levered long gold.
5. **Falsifiability.** Each family states its expected failure mode and a falsification test.

## 1. Taxonomy (8 mechanism classes) and data tiers
| class | theme | families |
|---|---|---|
| I  | Resting-liquidity / stop-cascade (refined) | S21, S22 |
| II | Volatility structure & risk premium | S23, S24, S25 |
| III| Auction / value / VWAP institutional reference | S26, S27, S28 |
| IV | Temporal / calendar / event flow | S29, S30, S31, S32 |
| V  | Intermarket / macro drivers (gold-specific) | S33, S34, S35 |
| VI | Positioning / dealer-hedging flow | S36, S37 |
| VII| Momentum QUALITY (fixes chasing) | S38, S39 |
| VIII| Regime routing (meta) | S40 |

**Data tiers** (drives feasibility):
- **T0 — existing XAUUSD OHLCV+volume (M15/H1/H4/D1).** No new data. S21,S22,S23,S25,S26,S27,S28,S29,S30,S31,S38,S39,S40.
- **T1 — modest new correlated series** (daily/intraday DXY, US10Y & 10Y-TIPS real yield, SPX, VIX, GC futures).
  A handful of public series, cheap. S24 (partial), S32, S33, S34, S35.
- **T2 — specialised data** (CFTC COT weekly, COMEX/OTC options chain & gamma, futures roll/OI). Higher cost /
  lower frequency / vendor-gated. S36, S37. NOTE: distinct from the *negative* MBO tick-microstructure result —
  these are slow positioning signals, not pre-price order-flow.

---

## CLASS I — Resting-liquidity / stop-cascade (refined)

### S21 — Equal-highs / equal-lows liquidity-pool raid
- **Mechanism.** Breakout traders and trend-followers place stops just beyond *clusters* of equal highs/lows
  (double/triple tops-bottoms). This pooled resting liquidity is a magnet: larger players push price through
  it to fill size, then reverse. Loser = the clustered stop/breakout crowd.
- **Distinct from S1.** S1 sweeps a *single* reference (prior swing/PDH). S21 requires a **cluster of ≥2
  approximately-equal extremes** (a built-up pool), which is a stronger, rarer, higher-conviction signal.
- **Signal (concept).** Detect ≥2 pivots within a small price tolerance (equal highs/lows); trigger when price
  wicks beyond the pool and closes back inside.
- **Dir / entry / stop / exit.** Reversal away from the raided side; entry on reclaim; stop beyond the raid
  extreme; exit at the opposing pool or fixed R.
- **Data.** T0. **Failure mode.** In strong trends the pool breaks and runs (no reversal) → must gate by
  range/exhaustion context. **Falsify.** No edge vs S1 single-sweep after controlling for level type.

### S22 — Round-number magnet & rejection ($25/$50/$100 gold levels)
- **Mechanism.** Gold has strong psychological levels ($2000, $2050, $3000…). Option strikes, limit orders and
  human stops cluster there → price is *attracted* to the level then *rejected* as resting orders absorb.
  Loser = momentum traders expecting clean breaks of the round number.
- **Distinct.** No S1–S20 family uses price-modulo psychological levels; all use derived swings/sessions.
- **Signal.** Proximity to nearest $X0/$X00 level + rejection wick / failure to close through.
- **Data.** T0 (pure price modulo). **Failure.** Levels get overrun in trend/news; needs a "quiet approach"
  filter (low momentum into the level). **Falsify.** Rejection rate at round numbers ≤ rate at random levels.

---

## CLASS II — Volatility structure & risk premium

### S23 — Squeeze breakout WITH higher-timeframe directional filter  *(fixes S4)*
- **Mechanism.** Volatility mean-reverts: compression (low ATR / narrow Bollinger-Keltner) precedes expansion.
  S4 failed because the *direction* of expansion was random. Fix: only take the expansion **in the direction
  of the HTF trend / prevailing order-flow bias**. Loser = premium sellers / range faders caught at the
  regime change.
- **Distinct from S4.** S4 = directionless expansion. S23 = compression + **HTF-aligned** directional break.
- **Signal.** BB-width or ATR percentile in bottom decile (squeeze) → break of the squeeze range in the
  H4/D1 trend direction only.
- **Data.** T0. **Failure.** False breaks (fakeouts) during the squeeze; needs a close-confirmation + volume
  expansion. **Falsify.** HTF-filtered expansion is no better than unfiltered S4.

### S24 — Overnight-gap vs intraday-range variance asymmetry
- **Mechanism.** Gold's variance is unevenly distributed: news and Asian/physical flow load the overnight
  (Asia) window; the intraday auction is calmer. Systematic overnight risk premium / gap behaviour is
  harvestable (fade or follow the Asian range into the London auction). Loser = traders holding naked
  overnight exposure demanding compensation.
- **Distinct from S19.** S19 trades the *gap* event once; S24 models the *variance regime* (overnight vs day)
  and positions for the London handover conditionally on the overnight range.
- **Signal.** Overnight (Asia) range percentile → conditional London-session drive or fade.
- **Data.** T0 (session-tagged bars); T1 if adding an event-calendar overlay. **Failure.** Regime-dependent;
  fails when macro news dominates. **Falsify.** Overnight-range percentile has no predictive link to day return.

### S25 — Volatility-regime transition (low-vol → high-vol onset)
- **Mechanism.** Volatility clusters (the promoted Volatility PRIMITIVE in the KB). The *transition* from a
  quiet regime to an active regime is itself tradeable: as realised vol crosses up through its own slow
  average, trend-following payoff rises and mean-reversion payoff falls. Loser = mean-reversion traders still
  fading in a newly-trending regime.
- **Distinct.** No S1–S20 family conditions on vol-of-vol / regime *onset*; S4 uses a single expansion bar.
- **Signal.** Realised-vol (Parkinson) short-avg crossing long-avg upward → switch bias to continuation.
- **Data.** T0. **Failure.** Whipsaw at the regime boundary; needs hysteresis. **Falsify.** Payoff to
  continuation is invariant to the vol-regime state (would kill the whole premise + touch the KB primitive).

---

## CLASS III — Auction / value / VWAP institutional reference

### S26 — Developing value-area rejection / acceptance
- **Mechanism.** Market-profile/auction theory: price spends ~70% of time in a value area; excursions outside
  value are either *rejected* (return to value = fade) or *accepted* (value migrates = follow). Institutions
  anchor to value. Loser = breakout traders faded at value edges, or mean-reverters run over on acceptance.
- **Distinct from S8/S12.** S8 = extension vs SMA/VWAP point; S12 = range rotation on raw rolling min/max.
  S26 uses a **developing value area (volume-weighted price distribution, ±σ / VA-high/low)** and the
  accept-vs-reject decision, which neither does.
- **Signal.** Excursion beyond VA-high/low → rejection wick (fade) or time-acceptance beyond (follow).
- **Data.** T0 (needs volume-at-price / TPO approximation from OHLCV+volume). **Failure.** Poor VA estimate on
  M15; may need finer data. **Falsify.** VA edges no more reactive than arbitrary bands.

### S27 — VWAP-band statistical reversion with volume confirmation
- **Mechanism.** Intraday VWAP is the execution benchmark; algos mean-revert client flow toward VWAP. Extreme
  deviation (±2–3σ VWAP bands) on *declining* volume signals exhausted flow → revert to VWAP. Loser = late
  momentum chasers at the band extreme.
- **Distinct from S8.** S8 uses static SMA/VWAP point + ATR extension; S27 uses **VWAP σ-bands + a volume
  exhaustion confirmation** (flow-based, not just distance).
- **Data.** T0. **Failure.** Trends ride the band (VWAP walk); needs the volume-decline gate. **Falsify.**
  Volume-confirmed reversion no better than distance-only S8.

### S28 — Anchored-VWAP from a significant event (institutional cost basis)
- **Mechanism.** VWAP anchored to a major swing/high-volume event = the average institutional entry price
  since that event. Price revisiting anchored-VWAP finds support/resistance because trapped/hedged positions
  defend break-even. Loser = those forced to defend or exit at cost basis.
- **Distinct.** No S1–S20 family uses event-anchored VWAP; S8/S27 use rolling/session VWAP.
- **Signal.** Anchor at last major D1 swing or gap; trade first clean retest of anchored-VWAP.
- **Data.** T0. **Failure.** Anchor selection is discretionary → must pre-register anchor rule. **Falsify.**
  Anchored-VWAP retest reaction ≈ random-line retest.

---

## CLASS IV — Temporal / calendar / event flow

### S29 — Day-of-week / weekly seasonality
- **Mechanism.** Systematic weekly flows (Monday positioning after weekend gap risk, Friday de-risking, mid-
  week auction). Gold shows documented weekday tendencies tied to macro-release scheduling and fund flows.
  Loser = the systematic weekly flow itself (predictable rebalancers).
- **Distinct from S18.** S18 = intraday hour-of-day; S29 = **day-of-week / week-structure**, a different axis.
- **Data.** T0. **Failure.** Weak, unstable, easily data-mined (multiple-testing trap) → must be pre-registered
  and FDR-controlled. **Falsify.** Weekday effect vanishes out-of-sample / under global-FDR.

### S30 — Session-open drive & reversal (London / NY "kill-zone")
- **Mechanism.** The first ~1h after London and NY opens injects concentrated liquidity (desks, algos begin).
  A displacement *drive* forms, then either continues (real flow) or reverses (liquidity grab). Loser =
  breakout traders trapped by the open's liquidity-grab spike.
- **Distinct from S5/S6.** S5 = opening-range breakout; S6 = session-transition vs prior-session level. S30
  focuses on the **open-drive impulse then its reversal within the kill-zone**, a distinct micro-timing bet.
- **Data.** T0. **Failure.** Overlaps S5/S6 economically → must show incremental edge or be merged. **Falsify.**
  Kill-zone reversal no better than S5/S6.

### S31 — Turn-of-month / month-end rebalancing flow
- **Mechanism.** Portfolio and index rebalancing, futures roll, and month-end marks concentrate flow in the
  last/first sessions of the month. Predictable calendar-driven pressure. Loser = the mechanical rebalancers.
- **Distinct.** No S1–S20 calendar family beyond intraday time; this is a **monthly** flow axis.
- **Data.** T0 (calendar from timestamps). **Failure.** Small, noisy, multiple-testing risk. **Falsify.**
  No return concentration in the turn-of-month window vs mid-month.

### S32 — Scheduled macro-event volatility (FOMC / CPI / NFP)
- **Mechanism.** Gold is acutely sensitive to US rates/inflation data. Around scheduled releases there is a
  pre-event vol compression (positioning paralysis) and a post-event directional repricing. Two sub-edges:
  pre-event drift/compression and post-event momentum. Loser = those forced to hedge/unwind around the event.
- **Distinct.** Fully new axis (event-conditioned). No S1–S20 uses an economic calendar.
- **Data.** **T1 — needs an economic-release calendar** (dates/times of FOMC, CPI, NFP, PCE). **Failure.**
  Direction is genuinely unpredictable pre-event → likely only the *vol/compression* leg is tradeable, not
  direction. **Falsify.** Event windows show no vol or drift anomaly vs matched non-event windows.

---

## CLASS V — Intermarket / macro drivers (gold-specific)  [needs T1 data]

### S33 — Gold–DXY divergence
- **Mechanism.** Gold is priced in USD → strong inverse link to the dollar (DXY). When gold *fails to follow*
  an inverse-DXY move (divergence), it flags either exhaustion or a non-USD driver (real demand) → a lead/lag
  correction. Loser = traders assuming a rigid 1:1 inverse.
- **Distinct.** No S1–S20 uses a second asset. Genuinely new, and **direction-symmetric** (good for the
  drift-beta problem).
- **Data.** **T1 — intraday/daily DXY.** **Failure.** Correlation is unstable/regime-dependent → must condition
  on the rolling gold-DXY beta. **Falsify.** Divergence has no predictive content for the subsequent gold move.

### S34 — Real-yield shock reaction
- **Mechanism.** Gold (a zero-coupon real asset) is anchored to US real yields (10Y TIPS): rising real yields
  raise the opportunity cost of holding gold → sell pressure, and vice-versa. Sharp real-yield moves force a
  repricing that gold sometimes lags intraday. Loser = slow-to-reprice gold flow.
- **Distinct.** New macro axis; the most economically fundamental gold driver.
- **Data.** **T1 — 10Y nominal & 10Y-TIPS (real yield), daily minimum.** **Failure.** Low frequency (daily
  yields) limits intraday use; relationship weakens when other drivers (risk-off, CB buying) dominate.
  **Falsify.** Gold's forward return is independent of real-yield innovations.

### S35 — Risk-sentiment / safe-haven regime
- **Mechanism.** In risk-off episodes (equity selloff, VIX spike) gold receives flight-to-safety bids; in
  calm risk-on it trades on rates/USD. Conditioning gold's behaviour on the risk regime (SPX/VIX) separates
  two different gold "modes". Loser = traders applying one model across both regimes.
- **Distinct.** New axis; regime-conditioning that S1–S20 lack.
- **Data.** **T1 — SPX & VIX.** **Failure.** Safe-haven bid is episodic and sometimes absent (2022 gold fell
  with stocks). **Falsify.** Risk-off windows show no differential gold response.

---

## CLASS VI — Positioning / dealer-hedging flow  [needs T2 data]

### S36 — COT positioning-extreme mean-reversion
- **Mechanism.** When CFTC managed-money net positioning reaches a crowded extreme, the marginal buyer/seller
  is exhausted → a positioning washout / mean-reversion follows. Slow, weekly, contrarian. Loser = the
  crowded late crowd forced to unwind. **Distinct from the negative MBO result** (that was tick microstructure;
  this is weekly positioning — a different timescale and mechanism).
- **Distinct.** New data axis; the canonical positioning factor.
- **Data.** **T2 — CFTC COT (weekly).** **Failure.** Weekly granularity → slow, few signals, hard to time
  entry; needs a price trigger. **Falsify.** COT extremes do not precede reversals beyond chance.

### S37 — Options gamma / max-pain pinning near expiry
- **Mechanism.** Near COMEX/OTC option expiry, dealer delta-hedging of large gamma exposure pins price toward
  high open-interest strikes (max pain) and dampens/amplifies vol depending on dealer gamma sign. Loser =
  breakout traders near expiry fighting dealer hedging.
- **Distinct.** Entirely new; dealer-flow mechanism.
- **Data.** **T2 — options chain (strikes, OI, expiries) or a gamma-exposure proxy.** **Failure.** OTC gold
  gamma is opaque; COMEX-only proxy may be weak. **Falsify.** No pinning/vol effect near high-OI strikes at expiry.

---

## CLASS VII — Momentum QUALITY (fixes S7/S10/S15 chasing)

### S38 — Patient pullback-into-zone LIMIT entry  *(fixes S7/S10)*
- **Mechanism.** S7/S10 failed by entering *after* the pullback confirmed (late, poor fill). Fix: in an
  established trend, place a **passive limit** into a pre-defined discount zone (prior FVG / 0.5–0.618 retrace /
  anchored-VWAP) and let price come to you. Loser = the impatient market-order continuation crowd (better fill
  than them). Edge source = execution asymmetry + trend persistence.
- **Distinct from S7/S10.** Same continuation thesis, opposite *execution* (limit-in-discount vs
  market-on-confirmation). This is the corrective redesign, not a re-run.
- **Data.** T0. **Failure.** Missed trades (limit not filled) and catching a real reversal; needs a trend-still-
  intact invalidation. **Falsify.** Limit-in-zone fills are no better than S7/S10 market entries.

### S39 — Trend-efficiency-gated continuation  *(fixes S15)*
- **Mechanism.** S15 bought raw acceleration (buying local tops). Fix: trade continuation only when the trend
  is **clean/efficient** (high Kaufman efficiency ratio = net move ÷ path length), which empirically predicts
  persistence; skip noisy, choppy "trends". Loser = counter-trend faders in efficient trends.
- **Distinct from S9/S15.** S9 = MTF alignment; S15 = acceleration. S39 gates on **trend *quality* (efficiency
  ratio)**, a signal-to-noise filter neither uses.
- **Data.** T0. **Failure.** Efficiency ratio is lagging; may enter late in the clean trend. **Falsify.**
  Continuation payoff is independent of the efficiency ratio.

---

## CLASS VIII — Regime routing (meta)

### S40 — Regime-router (trend / range / event) conditional deployment
- **Mechanism.** Most S1–S20 failures (S11 structure-break, S12 range-rotation) were *regime-conditional*
  strategies deployed unconditionally. S40 is a **meta-family**: a pre-registered regime classifier (using the
  Volatility primitive + trend/efficiency + session/event state) that ROUTES to the sub-mechanism appropriate
  to the current regime (continuation in clean trend, mean-reversion in range, stand-aside around events).
  Edge source = deploying each sub-edge only where its mechanism holds.
- **Distinct.** Not a new signal — a **conditioning layer** over existing/other families; the lab has none.
- **Data.** T0 (+ whatever the routed sub-families need). **Failure.** Classifier overfitting / regime-label
  lag; must be pre-registered and validated as a router, not tuned per outcome. **Falsify.** Routed deployment
  is no better than always-on for the same sub-families.

---

## 2. Distinctness matrix vs S1–S20 (summary)
- New AXES introduced (absent in S1–S20): psychological-price modulo (S22), volume-at-price/value-area (S26),
  event-anchored VWAP (S28), day-of-week & month-end (S29/S31), economic-event calendar (S32), a SECOND asset
  (S33/S34/S35), positioning (S36), options/gamma (S37), execution-asymmetry limit entry (S38), trend-quality
  (S39), regime routing (S40).
- Explicit REDESIGNS of failed families: S23←S4, S38←S7/S10, S39←S15, S40←S11/S12.
- Refinements of survivors (must prove *incremental* edge or be merged): S21←S1, S24←S19, S27←S8, S30←S5/S6.

## 3. Recommended implementation priority (for the post-pilot CEO decision)
- **Tier A (implement first — T0 data, distinct mechanism, fixes a known gap, direction-symmetric):**
  S23, S26, S38, S39, S40, S21. (No new data; directly address failures; portfolio-diversifying.)
- **Tier B (implement next — T0 but overlap-risk or noisy):** S22, S25, S27, S28, S24, S29, S30, S31.
- **Tier C (needs T1 data — highest *economic* value for gold, breaks the long-only drift dependence):**
  S33, S34, S35, S32. Strong candidates once a small macro dataset (DXY, real yields, SPX/VIX, econ calendar)
  is acquired — CEO gate on data.
- **Tier D (needs T2 specialised data):** S36 (COT), S37 (gamma). Design-complete; acquire only if Tier A–C
  underdeliver.

## 4. Guardrails (unchanged)
No code, no backtests, no parameters here. Each family, when/if implemented, must go through the SAME frozen
pipeline: common engine → Discovery Screen V1 → **matched-null (now validated)** → global-FDR → walk-forward →
Red Team → sealed holdout. Calendar/seasonality families (S29/S31/S32) carry high multiple-testing risk and
must be pre-registered before any fit. Intermarket/positioning families must pre-register the conditioning
variable to avoid look-ahead. New data acquisition (T1/T2) is a separate CEO gate.
