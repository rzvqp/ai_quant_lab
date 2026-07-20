# Edge Discovery Registry — v1

**Program**: 40-Edge Alpha Discovery Program. **Date opened**: 2026-07-20. **Status of this document**:
infrastructure, PLUS six Discovery-stage passes: the first 5 (E025, E026, E029, E032, E028 — 2026-07-20)
and E017 (2026-07-21, the first edge run under the post-remediation centralized-loader regime). **The
first 5 passes' original run was found 2026-07-21 to have breached the Research Lab's own sealed
terminal holdout (`PROJECT_STATE_v2.md` §8.23) — the old holdout is CONSUMED/INVALIDATED project-wide. A
holdout-excluded CLEAN RERUN of all 5 completed the same day** (`EDGE_RESEARCH_PROTOCOL.md` §8's
centralized enforcement, `edge_research/_common.py::load()`); E017 was run directly under that same
enforcement from the start. See `edge_research/` (each of the first 5 edges' own log carries both the
original contaminated run, preserved verbatim, and the clean rerun; E017's log has only its own
clean-from-the-start pass) and `NEXT_SESSION_FLOW_A.md` for the full session summary. No edge below has
been implemented, and no Final Verdict has been issued on any edge, in any run (the available data —
~3.6yr contaminated / ~2.85yr clean — is short of the protocol's own ~5-6 year requirement for any Final
Verdict — see `EDGE_RESEARCH_PROTOCOL.md` §2). Every entry's own V0 hypothesis below remains exactly as
originally registered, unedited, per protocol §1.

## How to read this registry

- **Status = UNSTUDIED for 34 of 40 entries; DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE for 5 (E025,
  E026, E028, E029, E032 — studied 2026-07-20, holdout-breach-remediated 2026-07-21); DISCOVERY_IN_PROGRESS
  for 1 more (E017 — studied clean-from-the-start, 2026-07-21)**. Status changes only by passing through
  the stages defined in `EDGE_RESEARCH_PROTOCOL.md` (V0 → Discovery → Frozen Candidate → Validation →
  Walk Forward → Final Verdict); no edge has advanced past Stage 2 (Discovery) yet.
- **Version = V0** for all 40 entries — the original, unmodified hypothesis as registered here. Per the
  protocol, V0 is never edited retroactively; any refinement discovered during research becomes V1, V2,
  etc., appended to the edge's own permanent research log (not created yet — see
  `EDGE_RESEARCH_PROTOCOL.md` §6).
- **Hypothesis (V0)** is deliberately written as a plain, literal statement of the idea as commonly
  described (ICT/SMC/intermarket retail trading literature, or as phrased by the CEO for E001-E008) —
  it is not hedged or pre-qualified, because the entire point of the program is to discover the real
  conditions later, not assume them now. Per the CEO's own explicit instruction, no part of this
  wording should be read as a confirmed claim.
- **Data required / Timeframes / Instruments required** describe what a future Discovery-stage study
  would ideally need per edge, independent of what currently exists on disk. This project's actual data
  inventory was checked (read-only) while preparing this registry: `data/market/` currently holds
  `OANDA_XAUUSD_{D1,H4,H1,M15}.csv`, covering roughly 2022-12-16 to 2026-07-13 (~3.5-4 years, not yet the
  full 5-6 requested), with **M15 as the finest resolution actually available — no M1 or tick-level data
  exists yet**, and a `volume` column present but of unconfirmed provenance (likely a tick-count proxy
  from an OTC/CFD feed, not verified exchange-traded volume). No DXY/US10Y/XAGUSD/USDJPY/SPX data and no
  economic-calendar/news-timestamp data exist anywhere in the project yet. Every "M1" or "tick" entry
  below is therefore an aspirational requirement, not a confirmed capability — the full gap analysis and
  its consequences for sequencing are in `EDGE_DISCOVERY_ROADMAP.md` §1.
- **Observable variables** are the dimensions a Discovery-stage study is expected to slice the data by —
  these are candidates, not a pre-decided answer about which ones matter.
- **Measured outcome** is the dependent variable the edge's existence would be judged against — again,
  a definition to test against, not a pre-supposed result.
- This project already has three building blocks in `ai_trader/market_intelligence/` that overlap with
  several edges below — `structure.py` (swing/BOS/CHoCH detection), `volatility.py` (regime
  classification), and `session_behavior.py` (session/time-of-day classification). They are named here
  as *candidate* reusable components for a future Discovery stage. **None of them has been wired into
  this program, modified, or run against any edge below** — naming them is not implementation.

---

## Category 1 — Session Timing

### E001 — London Open Liquidity Hunt
- **Category**: Session Timing
- **Hypothesis (V0)**: After an Asia session that traded in a range, the London Open frequently sweeps
  one extreme of that range and then moves toward the opposite extreme.
- **Data required**: XAUUSD intraday OHLCV (M1-M5 precision), ~5-6 years, with exact Asia/London session
  boundary timestamps.
- **Timeframes**: M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Asia-range width, day of week, which extreme is swept first, time-of-day of
  the sweep, follow-through distance/duration, volatility regime (candidate: `volatility.py`)
- **Measured outcome**: Whether price reaches the opposite Asia extreme within a defined post-sweep
  window, and the R-multiple/points captured if it does
- **Status**: UNSTUDIED
- **Version**: V0

### E002 — Frankfurt Pre-Market Trap
- **Category**: Session Timing
- **Hypothesis (V0)**: Aggressive price moves during the Frankfurt session are sometimes pure
  manipulation ahead of the London session, i.e. they reverse once London opens.
- **Data required**: XAUUSD intraday OHLCV (M1-M5), ~5-6 years, exact Frankfurt/London boundary
  timestamps
- **Timeframes**: M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Frankfurt-session move size/direction, day of week, whether London reverses
  or extends the Frankfurt move, time between Frankfurt move and London reaction
- **Measured outcome**: Reversal rate and magnitude of the London reaction relative to the Frankfurt move
- **Status**: UNSTUDIED
- **Version**: V0

### E003 — NY Silver Fix Momentum
- **Category**: Session Timing
- **Hypothesis (V0)**: The NY Silver Fix produces momentum and correlation effects that spill over into
  gold.
- **Data required**: XAUUSD + XAGUSD intraday OHLCV (M1), ~5-6 years, plus a verified daily Silver Fix
  timestamp (not currently confirmed to exist in this project)
- **Timeframes**: M1, M5
- **Instruments required**: XAUUSD, XAGUSD
- **Observable variables**: Pre-fix vs. post-fix price behavior, silver/gold co-movement magnitude,
  day of week
- **Measured outcome**: Directional move size and gold/silver correlation shift in a fixed post-fix
  window
- **Status**: UNSTUDIED
- **Version**: V0

### E004 — US Market Open First FVG
- **Category**: Session Timing
- **Hypothesis (V0)**: The first Fair Value Gap formed immediately after the US cash market open has
  statistically meaningful predictive value.
- **Data required**: XAUUSD intraday OHLCV (M1-M5), ~5-6 years, exact US cash-open timestamp
- **Timeframes**: M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: FVG size, direction, day of week, whether the FVG is later filled/respected,
  volatility regime
- **Measured outcome**: Directional follow-through after the first post-open FVG forms, and fill rate
- **Status**: UNSTUDIED
- **Version**: V0

### E005 — London Close Reversal
- **Category**: Session Timing
- **Hypothesis (V0)**: The London session close produces recurring reversals.
- **Data required**: XAUUSD intraday OHLCV (M1-M15), ~5-6 years, exact London close timestamp
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Pre-close trend direction/strength, day of week, size of the reversal,
  duration until reversal exhausts
- **Measured outcome**: Reversal rate and magnitude in a fixed post-London-close window
- **Status**: UNSTUDIED
- **Version**: V0

### E006 — Asia Range Expansion Failure
- **Category**: Session Timing
- **Hypothesis (V0)**: Breakouts of the Asia session range fail more often under certain conditions than
  others.
- **Data required**: XAUUSD intraday OHLCV (M1-M15), ~5-6 years, exact Asia session boundaries
- **Timeframes**: M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Asia range width, breakout direction, day of week, volatility regime, which
  later session the breakout occurs in
- **Measured outcome**: Breakout failure rate (price returns inside the Asia range within a defined
  window) vs. sustained-breakout rate
- **Status**: UNSTUDIED
- **Version**: V0

### E007 — Central Bank Whisper
- **Category**: Session Timing
- **Hypothesis (V0)**: Detectable algorithmic price drift occurs ahead of major scheduled news releases.
- **Data required**: XAUUSD intraday OHLCV (M1-tick), ~5-6 years, plus a verified economic calendar with
  exact release timestamps (does not yet exist in this project — see `EDGE_DISCOVERY_ROADMAP.md`)
- **Timeframes**: M1, M5
- **Instruments required**: XAUUSD
- **Observable variables**: Pre-release drift direction/size, which news category, minutes before release
- **Measured outcome**: Directional bias and magnitude of price drift in a fixed pre-release window,
  compared against a no-news control window
- **Status**: UNSTUDIED
- **Version**: V0

### E008 — Friday Profit Taking Shift
- **Category**: Session Timing
- **Hypothesis (V0)**: Friday afternoon shows a distinct behavior pattern caused by position-closing
  flows ahead of the weekend.
- **Data required**: XAUUSD intraday OHLCV (M5-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Time-of-day within Friday, week's prevailing trend direction, volatility
  regime, week-of-month
- **Measured outcome**: Change in directional persistence/volatility on Friday afternoon vs. the rest of
  the week
- **Status**: UNSTUDIED
- **Version**: V0

---

## Category 2 — Price Action / Structure

### E009 — Change of Character Retest
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: After a Change of Character (CHoCH) signals a possible trend shift, price
  frequently retests the CHoCH level before continuing in the new direction.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years, sufficient resolution for swing detection
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Swing-structure classification (candidate: `structure.py`), retest depth,
  time-to-retest, whether continuation follows, volatility regime
- **Measured outcome**: Retest rate, and continuation-vs-failure rate after the retest
- **Status**: UNSTUDIED
- **Version**: V0

### E010 — Breaker Block Snatch
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: A failed order block that flips polarity ("breaker") is often revisited and
  respected as support/resistance in the opposite direction.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Breaker formation context (candidate: `structure.py`), revisit rate, reaction
  magnitude, day of week
- **Measured outcome**: Rate at which the breaker level produces a reaction, and reaction magnitude
- **Status**: UNSTUDIED
- **Version**: V0

### E011 — Failed 3 Drive Pattern
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: A three-push ("three drive") pattern that fails to complete its third leg
  produces a reliable reversal signal.
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years
- **Timeframes**: M15, H1, H4
- **Instruments required**: XAUUSD
- **Observable variables**: Pattern completeness (2 vs. 3 legs), leg symmetry, volatility regime
- **Measured outcome**: Reversal rate and magnitude following a failed third leg vs. a completed
  three-drive
- **Status**: UNSTUDIED
- **Version**: V0

### E012 — Inverted Fair Value Gap
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: A Fair Value Gap that is fully violated ("inverted") flips role and acts as an
  opposite-direction reaction zone.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: FVG size, time-to-inversion, subsequent reaction magnitude, day of week
- **Measured outcome**: Reaction rate/magnitude at the inverted FVG level vs. a no-reaction baseline
- **Status**: UNSTUDIED
- **Version**: V0

### E013 — Mitigation Block Sniping
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: Price returns to "mitigate" an unfilled order block/imbalance left behind by an
  aggressive move, offering a precise entry zone.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Block formation impulse size, time-to-mitigation, precision of the reaction,
  session
- **Measured outcome**: Rate and magnitude of a directional reaction at the mitigation level
- **Status**: UNSTUDIED
- **Version**: V0

### E014 — Inside Bar False Breakout
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: A false breakout of an inside-bar range frequently reverses back through the
  range, offering a fade entry.
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years
- **Timeframes**: M15, H1, H4
- **Instruments required**: XAUUSD
- **Observable variables**: Inside-bar range width, breakout direction, time-to-reversal, volatility
  regime
- **Measured outcome**: False-breakout rate and magnitude of the reverse move
- **Status**: UNSTUDIED
- **Version**: V0

### E015 — Order Block Re-Mitigation
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: An order block that has already been mitigated once can be revisited a second
  time and still produce a reaction.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Number of prior mitigations, time between visits, reaction magnitude decay
  across visits
- **Measured outcome**: Reaction rate/magnitude on the second (and later) mitigation vs. the first
- **Status**: UNSTUDIED
- **Version**: V0

### E016 — Propulsion Block Entry
- **Category**: Price Action / Structure
- **Hypothesis (V0)**: The last opposing candle before a strong impulsive move ("propulsion block") acts
  as a reliable continuation-entry zone on retracement.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Impulse strength/speed, retracement depth to the block, day of week,
  volatility regime
- **Measured outcome**: Continuation rate and magnitude after price retraces to the propulsion block
- **Status**: UNSTUDIED
- **Version**: V0

---

## Category 3 — Liquidity

### E017 — Equal Highs / Lows Target
- **Category**: Liquidity
- **Hypothesis (V0)**: Clusters of equal highs/lows act as magnet levels that price is statistically
  likely to reach before reversing.
- **Data required**: XAUUSD OHLCV (M1-M15), ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Cluster tightness/age, time-to-reach, reaction magnitude after reaching,
  session
- **Measured outcome**: Rate at which price reaches the equal-highs/lows level, and reversal
  rate/magnitude once reached
- **Status**: DISCOVERY_IN_PROGRESS (Stage 2, first pass complete 2026-07-21, run under the
  post-remediation centralized-loader regime — `holdout_excluded=true`, `data_split_id =
  pre_holdout_2025-10-23T09-15-00Z_v1`; no Final Verdict — below the protocol's ~5-6yr horizon; strong,
  robust negative evidence across every tolerance/horizon/session/volatility slice tested; full detail
  `edge_research/E017_equal_highs_lows.md`)
- **Version**: V0 (frozen; no V1 candidate framing offered — see the research log's own explanation)

### E018 — B-Book Stop Hunt
- **Category**: Liquidity
- **Hypothesis (V0)**: Retail stop-loss clusters are deliberately targeted by price excursions before
  reversing. **Note**: as literally named this references broker-internal order routing, which is not
  observable from price data alone — before this can even enter the Discovery stage it needs
  reformulation into an observable price-based proxy (e.g. "an excursion beyond a well-known level
  immediately followed by reversal," without any claim about intent or broker routing). Flagged
  explicitly rather than silently reworded, per the protocol's requirement not to presume the initial
  description is correct.
- **Data required**: XAUUSD OHLCV (M1-M5), ~5-6 years
- **Timeframes**: M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Excursion size beyond the reference level, reversal speed/magnitude, session,
  which level type (equal highs/lows, prior day high/low, round number)
- **Measured outcome**: Reversal rate and magnitude following a beyond-level excursion, once redefined
  as an observable proxy
- **Status**: UNSTUDIED
- **Version**: V0

### E019 — Volume Climax Exhaustion
- **Category**: Liquidity
- **Hypothesis (V0)**: A volume spike at a price extreme signals exhaustion and precedes a reversal.
- **Data required**: XAUUSD OHLCV + volume/tick-count series (M1-M5), ~5-6 years — **volume data
  availability at this resolution is not yet confirmed for this project's feed** (see
  `EDGE_DISCOVERY_ROADMAP.md`)
- **Timeframes**: M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Volume relative to recent average, price-extreme context, reversal
  magnitude/speed
- **Measured outcome**: Reversal rate and magnitude following a volume-climax bar vs. a matched
  non-climax control
- **Status**: UNSTUDIED
- **Version**: V0

### E020 — Delta Divergence
- **Category**: Liquidity
- **Hypothesis (V0)**: Divergence between price direction and cumulative volume delta (buy/sell
  pressure) precedes a reversal.
- **Data required**: XAUUSD tick/order-flow delta series, ~5-6 years — **not yet confirmed to exist for
  this project's feed** (requires bid/ask-side volume, typically unavailable on standard OHLCV feeds)
- **Timeframes**: M1, M5
- **Instruments required**: XAUUSD
- **Observable variables**: Delta/price divergence magnitude, duration of divergence, session
- **Measured outcome**: Reversal rate and magnitude following a divergence signal
- **Status**: UNSTUDIED
- **Version**: V0

### E021 — Iceberg Order Absorption
- **Category**: Liquidity
- **Hypothesis (V0)**: Repeated absorption of aggressive orders at a price level (visible as stalling
  despite volume) precedes a reversal.
- **Data required**: XAUUSD tick/order-book or time-and-sales data, ~5-6 years — **not confirmed to
  exist for this project**; standard OHLCV cannot directly observe absorption
- **Timeframes**: tick, M1
- **Instruments required**: XAUUSD
- **Observable variables**: Price stall duration at a level relative to volume traded, reaction after
  stall resolves
- **Measured outcome**: Reversal rate/magnitude following a detected absorption episode
- **Status**: UNSTUDIED
- **Version**: V0

### E022 — VWAP Touch And Go
- **Category**: Liquidity
- **Hypothesis (V0)**: Price touching the session VWAP from a trending state tends to continue in the
  prior trend direction rather than reverse.
- **Data required**: XAUUSD OHLCV + volume (for VWAP calculation), M1-M15, ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Pre-touch trend strength, angle of approach to VWAP, continuation vs.
  reversal outcome, session
- **Measured outcome**: Continuation rate and magnitude after a VWAP touch, vs. reversal rate
- **Status**: UNSTUDIED
- **Version**: V0

### E023 — High Relative Volume Breakout
- **Category**: Liquidity
- **Hypothesis (V0)**: A breakout accompanied by volume significantly above its recent average is more
  likely to sustain than a low-volume breakout.
- **Data required**: XAUUSD OHLCV + volume (M1-M15), ~5-6 years — volume-resolution caveat as in E019
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Relative volume ratio at breakout, sustain-vs-fail outcome, day of week
- **Measured outcome**: Breakout sustain rate conditioned on relative volume, vs. a low-volume control
  group
- **Status**: UNSTUDIED
- **Version**: V0

### E024 — SP500 / Gold Delta Shift
- **Category**: Liquidity
- **Hypothesis (V0)**: Divergences in the typical SPX/Gold relationship (a shift in their rolling
  correlation) precede directional moves in gold.
- **Data required**: XAUUSD + SPX (or a liquid SPX-tracking instrument) OHLCV, M15-H1, ~5-6 years —
  SPX historical data not yet confirmed present in this project
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD, SPX
- **Observable variables**: Rolling correlation level/shift, which instrument leads, regime (risk-on vs.
  risk-off)
- **Measured outcome**: Gold directional move size following a detected correlation-regime shift
- **Status**: UNSTUDIED
- **Version**: V0

---

## Category 4 — Mathematical

### E025 — Round Numbers
- **Category**: Mathematical
- **Hypothesis (V0)**: Price reacts (as support/resistance/magnet) at round psychological levels (e.g.
  multiples of $10/$50/$100).
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD
- **Observable variables**: Round-number granularity ($10/$50/$100), approach direction, reaction
  magnitude, session
- **Measured outcome**: Reaction rate/magnitude at each round-number granularity vs. a matched
  non-round-level control
- **Status**: DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE (Stage 2, first pass 2026-07-20 was
  TERMINAL-HOLDOUT-BREACHED — see `PROJECT_STATE_v2.md` §8.23 — and is preserved as a contaminated
  audit-trail record; a holdout-excluded clean rerun completed 2026-07-21 partially CONFIRMS (short
  ~1h horizon) and WEAKENS (longer ~4h horizon, approach-from-above subslice) the original findings;
  no Final Verdict — below the ~5-6yr horizon either way; full detail
  `edge_research/E025_round_numbers.md`)
- **Version**: V0 (frozen; the research log's V1 candidate framing was revised 2026-07-21 to reflect
  only the clean-rerun-confirmed portion of the original finding)

### E026 — ADR Exhaustion
- **Category**: Mathematical
- **Hypothesis (V0)**: Once price has moved a large fraction of its Average Daily Range, further
  continuation in the same direction becomes statistically less likely for the remainder of the
  session.
- **Data required**: XAUUSD OHLCV (M15-D), ~5-6 years
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD
- **Observable variables**: % of ADR already consumed, time-of-day, day of week, volatility regime
- **Measured outcome**: Continuation-rate change conditioned on % of ADR already used
- **Status**: DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE (Stage 2, first pass 2026-07-20 was
  TERMINAL-HOLDOUT-BREACHED — see `PROJECT_STATE_v2.md` §8.23 — and is preserved as a contaminated
  audit-trail record; a holdout-excluded clean rerun completed 2026-07-21 CONFIRMS the original finding
  (upside effect even slightly stronger, downside null and session-confound caveat both replicate
  unchanged); no Final Verdict — below the ~5-6yr horizon either way; full detail
  `edge_research/E026_adr_exhaustion.md`)
- **Version**: V0 (frozen; the research log's V1 candidate framing is unchanged/confirmed by the clean
  rerun)

### E027 — Midnight Open Anchor
- **Category**: Mathematical
- **Hypothesis (V0)**: The midnight (00:00) candle open acts as a reference/anchor level that price
  frequently revisits or reacts to during the following session.
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years, exact midnight-anchor timestamp convention
- **Timeframes**: M15, H1, H4
- **Instruments required**: XAUUSD
- **Observable variables**: Distance from midnight open, time-to-revisit, reaction magnitude, session
- **Measured outcome**: Revisit rate and reaction magnitude relative to the midnight open level
- **Status**: UNSTUDIED
- **Version**: V0

### E028 — Fibonacci OTE
- **Category**: Mathematical
- **Hypothesis (V0)**: The 61.8%-79% "optimal trade entry" retracement zone of an impulsive move offers
  a statistically favorable continuation entry.
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years
- **Timeframes**: M15, H1, H4
- **Instruments required**: XAUUSD
- **Observable variables**: Impulse-leg size/speed, retracement depth reached, continuation-vs-failure
  outcome
- **Measured outcome**: Continuation rate/magnitude from the OTE zone vs. shallower or deeper
  retracements
- **Status**: DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE (Stage 2, first pass 2026-07-20 was
  TERMINAL-HOLDOUT-BREACHED — see `PROJECT_STATE_v2.md` §8.23 — and is preserved as a contaminated
  audit-trail record; a holdout-excluded clean rerun completed 2026-07-21 CONFIRMS the original finding
  (shallow-retracement > OTE-zone continuation rate replicates closely, chi-square weaker but still
  p=0.027); no Final Verdict — below the ~5-6yr horizon either way; full detail
  `edge_research/E028_fibonacci_ote.md`)
- **Version**: V0 (frozen; the research log's V1 candidate framing is unchanged/confirmed by the clean
  rerun)

### E029 — Weekly Gap Fill
- **Category**: Mathematical
- **Hypothesis (V0)**: A price gap between Friday's close and Sunday/Monday's open tends to be filled
  within the following sessions.
- **Data required**: XAUUSD OHLCV (H1-D), ~5-6 years
- **Timeframes**: H1, H4, D
- **Instruments required**: XAUUSD
- **Observable variables**: Gap size/direction, time-to-fill, week-of-month, whether filled same day or
  later in the week
- **Measured outcome**: Fill rate and time-to-fill distribution
- **Status**: DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE (Stage 2, first pass 2026-07-20 was
  TERMINAL-HOLDOUT-BREACHED — see `PROJECT_STATE_v2.md` §8.23 — and is preserved as a contaminated
  audit-trail record; a holdout-excluded clean rerun completed 2026-07-21 CONFIRMS the fill-rate-by-size
  pattern (large gaps still ~78% vs 100% for small) but the large-tercile time-to-fill figure changed
  substantially (11.0h contaminated vs 1.875h clean, small-n-sensitive, flagged not resolved); no Final
  Verdict — below the ~5-6yr horizon either way; full detail
  `edge_research/E029_weekly_gap_fill.md`)
- **Version**: V0 (frozen; no refinement written yet, still blocked on the matched-control question per
  the research log)

### E030 — Tick Speed Acceleration
- **Category**: Mathematical
- **Hypothesis (V0)**: A sudden acceleration in tick/quote update frequency precedes or confirms the
  start of an impulsive directional move.
- **Data required**: XAUUSD tick/quote-frequency series, ~5-6 years — **tick-level data not yet
  confirmed present in this project**
- **Timeframes**: tick, M1
- **Instruments required**: XAUUSD
- **Observable variables**: Tick-frequency acceleration magnitude, subsequent price-move size/direction
- **Measured outcome**: Directional move size/duration following a detected tick-speed acceleration
- **Status**: UNSTUDIED
- **Version**: V0

### E031 — 3 Standard Deviations VWAP
- **Category**: Mathematical
- **Hypothesis (V0)**: Price reaching the 3rd standard-deviation band of the session VWAP is
  statistically likely to revert toward the mean.
- **Data required**: XAUUSD OHLCV + volume (for VWAP/band calculation), M1-M15, ~5-6 years
- **Timeframes**: M5, M15, H1
- **Instruments required**: XAUUSD
- **Observable variables**: Which band touched, session, volatility regime, reversion speed/magnitude
- **Measured outcome**: Reversion rate/magnitude toward VWAP after a 3rd-band touch vs. a 1st/2nd-band
  control
- **Status**: UNSTUDIED
- **Version**: V0

### E032 — Premium Discount Flip
- **Category**: Mathematical
- **Hypothesis (V0)**: Price trading above/below the 50% equilibrium of a defined range (premium/
  discount) is more likely to move toward, not away from, that equilibrium.
- **Data required**: XAUUSD OHLCV (M5-H1), ~5-6 years
- **Timeframes**: M15, H1, H4
- **Instruments required**: XAUUSD
- **Observable variables**: Range-defining logic used, distance from equilibrium, day of week
- **Measured outcome**: Rate/magnitude of movement toward equilibrium vs. away from it
- **Status**: DISCOVERY_IN_PROGRESS / CLEAN_RERUN_COMPLETE (Stage 2, first pass 2026-07-20 was
  TERMINAL-HOLDOUT-BREACHED — see `PROJECT_STATE_v2.md` §8.23 — and is preserved as a contaminated
  audit-trail record; a holdout-excluded clean rerun completed 2026-07-21 CONFIRMS the original finding
  almost exactly, the most robust of the five edges rerun this batch; no Final Verdict — below the
  ~5-6yr horizon either way; full detail `edge_research/E032_premium_discount_flip.md`)
- **Version**: V0 (frozen; no refinement written yet, still blocked on the overextension-confound
  control per the research log)

---

## Category 5 — Intermarket

### E033 — DXY Lead
- **Category**: Intermarket
- **Hypothesis (V0)**: Moves in the US Dollar Index (DXY) lead corresponding inverse moves in gold with
  a measurable lag.
- **Data required**: XAUUSD + DXY OHLCV, ~5-6 years — DXY historical data not yet confirmed present in
  this project
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD, DXY
- **Observable variables**: Lead/lag time, DXY move size, correlation stability by regime
- **Measured outcome**: Gold move size/direction conditioned on a preceding DXY move, and the
  measured lag
- **Status**: UNSTUDIED
- **Version**: V0

### E034 — US10Y Lead
- **Category**: Intermarket
- **Hypothesis (V0)**: Moves in the US 10-Year Treasury yield lead corresponding inverse moves in gold
  with a measurable lag.
- **Data required**: XAUUSD + US10Y yield series, ~5-6 years — not yet confirmed present in this project
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD, US10Y
- **Observable variables**: Lead/lag time, yield move size, correlation stability by regime
- **Measured outcome**: Gold move size/direction conditioned on a preceding US10Y move, and the
  measured lag
- **Status**: UNSTUDIED
- **Version**: V0

### E035 — Silver Leading Indicator
- **Category**: Intermarket
- **Hypothesis (V0)**: Silver (XAG) price moves lead gold price moves, acting as an early directional
  signal.
- **Data required**: XAUUSD + XAGUSD OHLCV, ~5-6 years
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD, XAGUSD
- **Observable variables**: Lead/lag time, gold/silver ratio level, correlation stability by regime
- **Measured outcome**: Gold move size/direction conditioned on a preceding silver move, and the
  measured lag
- **Status**: UNSTUDIED
- **Version**: V0

### E036 — USDJPY Inversion
- **Category**: Intermarket
- **Hypothesis (V0)**: USDJPY moves show an inverse/lead relationship with gold during specific regimes
  (e.g. risk-off episodes).
- **Data required**: XAUUSD + USDJPY OHLCV, ~5-6 years — USDJPY historical data not yet confirmed
  present in this project
- **Timeframes**: M15, H1, D
- **Instruments required**: XAUUSD, USDJPY
- **Observable variables**: Risk-on/risk-off regime classification, lead/lag time, correlation stability
- **Measured outcome**: Gold move size/direction conditioned on a preceding USDJPY move, by regime
- **Status**: UNSTUDIED
- **Version**: V0

---

## Category 6 — News

### E037 — NFP First Wave Liquidation
- **Category**: News
- **Hypothesis (V0)**: The initial (first-wave) price reaction to the US Non-Farm Payrolls release is
  frequently a liquidity-driven overshoot that partially reverses.
- **Data required**: XAUUSD OHLCV (tick-M1), ~5-6 years of NFP release windows, plus a verified economic
  calendar with exact release timestamps (does not yet exist in this project)
- **Timeframes**: tick, M1, M5
- **Instruments required**: XAUUSD
- **Observable variables**: First-wave move size/direction, time-to-reversal, reversal magnitude,
  surprise vs. expectation (if calendar data includes consensus figures)
- **Measured outcome**: Reversal rate and magnitude of the first-wave NFP reaction within a fixed
  post-release window
- **Status**: UNSTUDIED
- **Version**: V0

### E038 — CPI Initial Reaction Reversal
- **Category**: News
- **Hypothesis (V0)**: The initial directional reaction to a CPI release frequently reverses within a
  short window after release.
- **Data required**: XAUUSD OHLCV (tick-M1), ~5-6 years of CPI release windows, plus a verified economic
  calendar
- **Timeframes**: tick, M1, M5
- **Instruments required**: XAUUSD
- **Observable variables**: Initial-reaction size/direction, time-to-reversal, reversal magnitude,
  surprise vs. expectation
- **Measured outcome**: Reversal rate and magnitude of the initial CPI reaction within a fixed
  post-release window
- **Status**: UNSTUDIED
- **Version**: V0

### E039 — FOMC Slingshot
- **Category**: News
- **Hypothesis (V0)**: Price frequently makes an initial move in one direction around an FOMC
  statement/press conference, then reverses sharply in the opposite direction ("slingshot").
- **Data required**: XAUUSD OHLCV (tick-M1), ~5-6 years of FOMC statement/press-conference windows, plus
  a verified economic calendar with exact statement and press-conference start times
- **Timeframes**: tick, M1, M5, M15
- **Instruments required**: XAUUSD
- **Observable variables**: Initial-move size/direction, slingshot magnitude, time between statement and
  press conference, whether the effect is statement-driven or press-conference-driven
- **Measured outcome**: Reversal rate and magnitude of the "slingshot" move within a fixed
  post-statement/post-press-conference window
- **Status**: UNSTUDIED
- **Version**: V0

### E040 — Flash PMI Sentiment Flip
- **Category**: News
- **Hypothesis (V0)**: Flash PMI releases produce an initial reaction that is frequently reversed once
  the full report is digested.
- **Data required**: XAUUSD OHLCV (tick-M1), ~5-6 years of Flash PMI release windows, plus a verified
  economic calendar
- **Timeframes**: tick, M1, M5
- **Instruments required**: XAUUSD
- **Observable variables**: Initial-reaction size/direction, time-to-reversal, reversal magnitude,
  headline vs. sub-index divergence (if calendar data includes sub-indices)
- **Measured outcome**: Reversal rate and magnitude of the initial Flash PMI reaction within a fixed
  post-release window
- **Status**: UNSTUDIED
- **Version**: V0

---

## Registry summary

| # | Category | Edge count | IDs |
|---|---|---|---|
| 1 | Session Timing | 8 | E001-E008 |
| 2 | Price Action / Structure | 8 | E009-E016 |
| 3 | Liquidity | 8 | E017-E024 |
| 4 | Mathematical | 8 | E025-E032 |
| 5 | Intermarket | 4 | E033-E036 |
| 6 | News | 4 | E037-E040 |
| **Total** | | **40** | E001-E040 |

All 40 entries: **Status = UNSTUDIED, Version = V0**. No edge has been implemented, backtested, or had
its hypothesis modified since registration.
