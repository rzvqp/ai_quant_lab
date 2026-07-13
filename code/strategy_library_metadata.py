"""CURATED per-family metadata for the Executable Strategy Library. QUALITATIVE fields only (mechanism /
entry / exit / stop / confirmations / sessions / applicability / invalid conditions), transcribed from the
FROZEN family code (mstrat.py grammars+setups, mstrat_ext.py grammars+setups+design comments) and the ECON
tags. NO new research, NO metrics here — the QUANTITATIVE metrics are read from the frozen result parquets by
build_strategy_library.py. This module is documentation of what the engine ALREADY does; it does not change it.

Universal engine facts (apply to EVERY strategy, injected once by the builder — not repeated per family):
- Timeframe: M15 execution. Signal evaluated at bar CLOSE; entry filled at the NEXT M15 bar OPEN (lookahead-safe).
  Higher-timeframe context (H1/H4/D1) is used by the families whose `htf` field says so.
- Position sizing: RISK-NORMALISED. risk = |entry - stop| (after the v2 stop-floor). Per-trade result is
  R = (dir*(exit-entry) - 2*cost) / risk. The research assumes 1 unit of risk (1R) per trade, ONE position at a
  time (overlap suppressed: a new signal is skipped until the prior trade closes). Absolute lot size = the AI
  Trader's per-trade risk budget / risk-distance — an EXECUTION-LAYER decision, not fixed by the research.
- v2 stop-floor (pre-registered, frozen): executable risk = max(2*spread_ticks*tick, 5*tick, 0.10*ATR) =
  max(0.20, 0.50, 0.10*ATR) price units; a tighter strategy stop is widened to this floor before sizing.
- Costs: (spread 1 tick + slippage 1 tick) per side * tick 0.1 = 0.10/side; round-trip 0.20 charged in R.
- Universal INVALID conditions (all families): ATR non-finite or <= 0 at the signal bar; signal in the last bar
  (no next-open to fill); a position already open (overlap). XAUUSD (OANDA), NY 17:00-anchored sessions.
"""

# klass = mechanism family/class · htf = higher-timeframe context used · long_short = symmetric unless noted
META = {
 # ---------------- S1-S20 (mstrat.py) ----------------
 'S1': dict(name='Confirmed Liquidity Sweep Reversal', klass='Liquidity / stop-hunt reversal',
   mechanism='Price sweeps a resting liquidity level (prior swing / session / prev-day high-low), trapping breakout '
             'traders and triggering stops, then closes back inside the range. The reversal is the absorption of that '
             'forced flow. Loser = breakout entrants and stopped-out positions.',
   entry='A sweep bar takes out the reference level (high>refH & close<refH for a high-sweep; low<refL & close>refL '
         'for a low-sweep), THEN a confirmation occurs within `window` bars; enter next open after confirmation.',
   exit_rules='Grammar: rr2 / rr3 (2R or 3R fixed target) | opp_liq (opposite liquidity level) | time (24-bar timeout).',
   stop_rules='beyond_sweep (2 ticks past the sweep extreme) or structural (2 ticks past the 20-bar extreme at entry).',
   confirmations='REQUIRED: consecutive2 (two same-direction closes) | close_beyond (close back through the level) | '
                 'displacement (displacement bar with matching close). Optional imbalance filter (FVG present).',
   sessions='All sessions', long_short='both', htf='none',
   grammar_dims='side, liq_ref(swing|session|pdh_pdl), liq_lb(20|50), confirm, imb(none|fvg), stop, exit, window(4|8)'),

 'S2': dict(name='Failed-Breakout Fade', klass='Failed-breakout / contrarian',
   mechanism='A close breaks beyond a reference level then FAILS (closes back inside) within a few bars — a false '
             'breakout. Fade back into the range. Loser = breakout buyers of the false break.',
   entry='Close beyond ref (up: close>refH; low: close<refL); within `fail_within` bars a close returns inside; '
         'enter next open (contrarian, into the range).',
   exit_rules='rr2 | opp_liq | time.', stop_rules='beyond_ext (2 ticks past the failed-break extreme) or atr (1.5*ATR).',
   confirmations='The failure itself (close back inside within the window) is the confirmation.',
   sessions='All sessions', long_short='both', htf='none',
   grammar_dims='ref(swing|session|pdh_pdl), lb(20|50), fail_within(2|4), stop, exit, side'),

 'S3': dict(name='Breakout Retest Continuation', klass='Breakout-retest momentum',
   mechanism='A genuine breakout of a level, then a retest of that level as new support/resistance, then continuation. '
             'Loser = faders of the confirmed breakout.',
   entry='Close breaks the level; within `retest_within` bars price returns to the level; enter next open in the '
         'breakout direction.',
   exit_rules='rr2 | rr3 | trailing (1.5*ATR trail).', stop_rules='beyond_level (2 ticks past the level) or atr.',
   confirmations='The retest hold is the confirmation.', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='ref(swing|session), lb(20|50), retest_within(4|8), stop, exit, side'),

 'S4': dict(name='Volatility Compression Expansion', klass='Volatility-regime expansion',
   mechanism='After a compression regime (ATR below its mean), a range-expansion bar (>k*ATR) signals a volatility '
             'breakout; trade its direction. NOTE: S4 was found NEGATIVE — expansion direction is near-random without a '
             'trend filter (the fix is S23).',
   entry='Prior compression for `min_compress` bars; an expansion bar range>k*ATR; direction = the expansion bar colour; '
         'enter next open.',
   exit_rules='rr2 | rr3 | trailing | time.', stop_rules='bar (2 ticks past the expansion bar) or atr.',
   confirmations='none', sessions='All sessions', long_short='both (bar-directional)', htf='none',
   grammar_dims='exp_k(1.5|2.0), stop, exit, min_compress(1|3)'),

 'S5': dict(name='Opening-Range Breakout', klass='Opening-range momentum',
   mechanism='The first 4 M15 bars of a session define an opening range; a break of that range signals the session '
             'directional bias. Loser = mean-reversion faders of the OR break. (Wave-1 EXP-04: much of the edge is '
             'session/regime BETA.)',
   entry='After the OR forms (bar_in_sess in 4..20), close breaks the OR high (up) or low (down); enter next open.',
   exit_rules='rr2 | rr3 | opp_liq | time.', stop_rules='or_opp (opposite OR edge) or atr.',
   confirmations='none (breakout close is the trigger)', sessions='Session-specific: asia | london | ny (parameter)',
   long_short='both', htf='none', grammar_dims='session, mode(breakout|retest), stop, exit, side'),

 'S6': dict(name='Session-Transition', klass='Session-transition momentum',
   mechanism='Early in London/NY, price interacts with the PRIOR session high/low; breakout (continuation) or fade '
             '(reversion) of that level as the new session takes control.',
   entry='In the first ~10 bars of the target session, cross of the prior-session high/low; breakout enters with the '
         'cross, fade enters against a tag-without-cross; enter next open.',
   exit_rules='rr2 | time.', stop_rules='prev_ext (2 ticks past the level) or atr.',
   confirmations='none', sessions='london | ny (parameter)', long_short='both', htf='none',
   grammar_dims='session(london|ny), mode(breakout|fade), side, stop, exit'),

 'S7': dict(name='Trend Pullback Continuation', klass='Trend-pullback continuation',
   mechanism='In an established HTF trend, a pullback to the M15 EMA20 then a confirmation close back in the trend '
             'direction resumes the move. Found NEGATIVE (late entries; the redesign is S38).',
   entry='HTF trend up/down; price pulls to the wrong side of EMA20; within `pb_within` bars a close returns through '
         'EMA20; enter next open.',
   exit_rules='rr2 | rr3 | trailing.', stop_rules='ema (2 ticks past EMA at entry) or atr.',
   confirmations='REQUIRED: the confirmation close back through EMA20.', sessions='All sessions', long_short='both',
   htf='H4 or H1 trend', grammar_dims='htf(h4|h1), stop, exit, pb_within(4|8)'),

 'S8': dict(name='Extension Mean-Reversion', klass='Extension mean-reversion',
   mechanism='Price extends k*ATR beyond a reference (SMA or session VWAP); the onset of over-extension reverts toward '
             'the reference. Loser = late trend-chasers.',
   entry='At the ONSET of |close-ref| > k*ATR (first bar of the extension); enter next open toward the reference.',
   exit_rules='rr2 | opp_liq (revert to the reference) | time.', stop_rules='atr (1.5*ATR) or ext (2 ticks past the bar extreme).',
   confirmations='none (extension onset is selective)', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='ref(sma|vwap), k(2.0|3.0), side, stop, exit'),

 'S9': dict(name='Multi-Timeframe Alignment', klass='MTF-trend momentum',
   mechanism='4H trend context (optionally 1H-aligned) plus a fresh M15 breakout trigger — trade only with the higher-'
             'timeframe. Loser = counter-trend breakout faders.',
   entry='4H trend in the trade direction (and 1H aligned if conf1h=align); ONSET of a close beyond the `lb`-bar rolling '
         'extreme; enter next open.',
   exit_rules='rr2 | rr3.', stop_rules='atr (1.5*ATR) or structural (20-bar extreme).',
   confirmations='HTF trend alignment (and optional 1H confirm).', sessions='All sessions', long_short='both',
   htf='H4 trend (+optional H1)', grammar_dims='c4h(up|down), conf1h(align|any), lb(10|20), stop, exit'),

 'S10': dict(name='Displacement Continuation', klass='Displacement continuation',
   mechanism='A displacement bar (range>k*ATR with matching close) marks strong intent; a controlled pullback then '
             'continuation. Found NEGATIVE standalone.',
   entry='Displacement bar; within `pb` bars price pulls back to the displacement close; enter next open in the '
         'displacement direction.',
   exit_rules='rr2 | rr3 | trailing.', stop_rules='bar (2 ticks past the displacement bar) or atr.',
   confirmations='the controlled pullback', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='disp_k(1.5|2.0), pb(2|4), side, stop, exit'),

 'S11': dict(name='Structure-Break Reversal (CHoCH)', klass='Structure-break reversal',
   mechanism='In an HTF trend, a break of the opposite recent swing (change-of-character) signals a reversal. Found '
             'NEGATIVE (regime-blind; the router S40 addresses this).',
   entry='HTF trend up and close < `lb`-bar rolling min (or trend down and close > rolling max) — onset only; enter next '
         'open counter to the prior trend.',
   exit_rules='rr2 | rr3 | time.', stop_rules='struct (20-bar extreme) or atr.', confirmations='none',
   sessions='All sessions', long_short='both', htf='H4 or H1 trend', grammar_dims='htf(h4|h1), lb(20|50), stop, exit'),

 'S12': dict(name='Range Rotation', klass='Range rotation',
   mechanism='At a range extreme, a rejection rotates price back toward the centre/opposite edge. Found NEGATIVE '
             '(regime-blind — fails in trends).',
   entry='Onset of price tagging the `lb`-bar rolling extreme; enter next open toward the middle/opposite side.',
   exit_rules='rr (to centre ~1.5R) | opp_liq | time.', stop_rules='ext (2 ticks past the extreme) or atr.',
   confirmations='none', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='lb(20|50), target(center|opp), side, stop, exit'),

 'S13': dict(name='Imbalance Fill', klass='Imbalance / FVG reaction',
   mechanism='A fair-value gap (imbalance) tends to be filled then produce a reaction (revert) or act as continuation. '
             'Loser depends on mode.',
   entry='Onset of an FVG (bull or bear); enter next open — revert (against the gap) or continue (with it).',
   exit_rules='rr2 | rr3 | time.', stop_rules='atr or struct (20-bar extreme).', confirmations='none',
   sessions='All sessions', long_short='both', htf='none', grammar_dims='fvg(bull|bear), mode(revert|continue), stop, exit'),

 'S14': dict(name='Momentum Exhaustion', klass='Momentum exhaustion',
   mechanism='A sharp move (high |ROC|) that then STALLS (ROC magnitude shrinks) signals exhaustion; fade it. Loser = '
             'late momentum chasers.',
   entry='Onset of acceleration (|ROC3|>k) together with a stall (current |ROC| < prior |ROC|); enter next open against '
         'the exhausted move.', exit_rules='rr2 | time.', stop_rules='atr or bar (2 ticks past the bar extreme).',
   confirmations='the stall', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='roc_k(0.004|0.008), side, stop, exit'),

 'S15': dict(name='Trend Acceleration', klass='Trend acceleration',
   mechanism='A trend plus a fresh range/momentum expansion bar continues. Found NEGATIVE (buys local tops; the fix is '
             'the efficiency-gated S39).',
   entry='HTF/M15 trend and onset of an expansion bar (range>k*ATR) in the trend direction; enter next open.',
   exit_rules='rr2 | rr3 | trailing.', stop_rules='atr or struct.', confirmations='none', sessions='All sessions',
   long_short='both', htf='H4 or H1 trend', grammar_dims='htf(h4|h1), exp_k(1.5|2.0), stop, exit'),

 'S16': dict(name='Previous-Day Levels', klass='Reference-level (daily)',
   mechanism='Prior-day high/low/open/close/mid act as magnets/decision points — breakout or rejection. Loser = the '
             'crowd anchored to the daily level.',
   entry='Onset of a close beyond the chosen prev-day level (breakout) or a wick-tag-then-reject (reject); enter next open.',
   exit_rules='rr2 | time.', stop_rules='atr or level (2 ticks past the level).', confirmations='none',
   sessions='All sessions', long_short='both', htf='D1 levels', grammar_dims='level(pdh|pdl|pd_open|pd_close|pd_mid), mode(breakout|reject), stop, exit'),

 'S17': dict(name='Weekly Levels', klass='Reference-level (weekly)',
   mechanism='Prior-week high/low as higher-timeframe decision levels — breakout or rejection.',
   entry='Onset of a close beyond prev-week high/low (breakout) or a tag-then-reject; enter next open.',
   exit_rules='rr2 | rr3 | time.', stop_rules='atr or level.', confirmations='none', sessions='All sessions',
   long_short='both', htf='Weekly levels', grammar_dims='level(pw_high|pw_low), mode(breakout|reject), stop, exit'),

 'S18': dict(name='Time-of-Day Edge', klass='Calendar / time-of-day',
   mechanism='A fixed intraday hour with a directional bias (session-open flows). Pure clock effect; multiple-testing '
             'across hours acknowledged.',
   entry='At a fixed UTC hour (00,07,08,13,14,20) on the hour, enter next open directionally.',
   exit_rules='rr2 | time.', stop_rules='atr (1.5*ATR).', confirmations='none', sessions='Fixed hours 00/07/08/13/14/20 UTC',
   long_short='both', htf='none', grammar_dims='hour, side, exit'),

 'S19': dict(name='Session Gap', klass='Gap fill / continuation',
   mechanism='A session-open gap (open vs prior-session close) either fills (revert to prior close) or continues. Small '
             'sample. Loser depends on mode.',
   entry='At session start a gap > 0.5*ATR (up or down); fill = trade toward the prior close, continue = with the gap; '
         'enter next open.', exit_rules='rr2 | opp_liq (prior close for fills) | time.', stop_rules='atr.',
   confirmations='none', sessions='Session opens', long_short='both', htf='none',
   grammar_dims='gap_dir(up|down), mode(fill|continue), exit'),

 'S20': dict(name='Hybrid Sweep + MTF', klass='Hybrid (composite)',
   mechanism='Combines S9 MTF-trend context with an S1-style sweep or breakout trigger — a non-arbitrary composite. '
             'Loser = counter-trend sweep faders.',
   entry='4H trend context plus a sweep (or breakout onset) of the `lb`-bar extreme in the trend direction; enter next open.',
   exit_rules='rr2 | rr3.', stop_rules='atr or struct.', confirmations='MTF trend context', sessions='All sessions',
   long_short='both', htf='H4 trend', grammar_dims='ctx(h4up|h4down), trig(sweep|breakout), lb(20|50), stop, exit'),

 # ---------------- S21-S51 (mstrat_ext.py) ----------------
 'S21': dict(name='Equal-Highs/Lows Liquidity-Pool Raid', klass='Class I — resting liquidity',
   mechanism='Stops/breakout orders pool at CLUSTERS of equal highs/lows (a level tested >=2x). Large players raid the '
             'pool then price reverses. Stronger/rarer than S1 (requires a multi-touch pool).',
   entry='A level touched >= min_touches times in the last 20 bars, then a raid (sweep beyond) with a close back inside; '
         'enter next open (reversal).', exit_rules='rr2 | rr3 | time.', stop_rules='beyond_raid (2 ticks past the raid) or structural.',
   confirmations='the multi-touch pool + close-back-inside rejection.', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='side, lb(20|50), min_touches(2|3), stop, exit'),

 'S22': dict(name='Round-Number Magnet / Rejection', klass='Class I — psychological levels',
   mechanism='Psychological $ levels ($50/$100 on gold) attract limit orders and stops; price rejects or cleanly breaks '
             'them. Loser = orders resting at the round number.',
   entry='reject: wick tags the round level and closes back (fade); breakout: the floor(price/step) band changes (crossed '
         'a round level); onset only; enter next open.', exit_rules='rr2 | rr3 | time.', stop_rules='atr or level (2 ticks past the round level).',
   confirmations='none', sessions='All sessions', long_short='both', htf='none', grammar_dims='step(50|100), mode(reject|breakout), stop, exit'),

 'S23': dict(name='Squeeze Breakout + HTF Filter', klass='Class II — volatility regime (redesign of S4)',
   mechanism='Volatility compresses then expands; take the squeeze breakout ONLY in the HTF trend direction (fixes S4 '
             'random direction). Loser = range faders caught at the regime change.',
   entry='Sustained prior compression (min_sq bars); close breaks the squeeze range on the HTF-trend side; enter next open.',
   exit_rules='rr2 | rr3 | trailing | time.', stop_rules='range_opp (opposite squeeze edge) or atr.',
   confirmations='HTF trend filter.', sessions='All sessions', long_short='both', htf='H4 or H1 trend',
   grammar_dims='htf(h4|h1), min_sq(3|6), stop, exit'),

 'S24': dict(name='Overnight Variance / Session Carry', klass='Class IV — session structure',
   mechanism='The prior session\'s close position in its range conditions the next session; carry (same bias) or fade '
             'at the target session\'s early bar.',
   entry='At bar `entry_bar` of London/NY, bias from where the prior session closed in its range; carry or fade; enter next open.',
   exit_rules='rr2 | rr3 | time.', stop_rules='atr (1.5*ATR).', confirmations='none', sessions='london | ny (target)',
   long_short='both', htf='prior-session structure', grammar_dims='sess(london|ny), mode(carry|fade), entry_bar(1|2), exit'),

 'S25': dict(name='Volatility-Regime Onset', klass='Class II — volatility transition',
   mechanism='Trades the TRANSITION of ATR across its moving average (not a squeeze breakout): expand-onset -> ride the '
             'move, contract-onset -> revert to mean.',
   entry='Onset of ATR crossing above (expand) or below (contract) its mean; expand rides the ROC direction, contract '
         'reverts toward the SMA; enter next open.', exit_rules='rr2 | rr3 | time.', stop_rules='atr or swing (20-bar extreme).',
   confirmations='none', sessions='All sessions', long_short='both', htf='none', grammar_dims='mode(expand|contract), stop, exit'),

 'S26': dict(name='Value-Area Rejection / Acceptance', klass='Class III — auction / value',
   mechanism='Excursions beyond the value-area edge (session VWAP +/- k*sigma) are rejected (revert) or accepted (value '
             'migrates -> follow). Institutions anchor to value.',
   entry='reject: onset of an excursion beyond the VA edge that closes back inside (fade); accept: close beyond the edge '
         '(follow); enter next open.', exit_rules='rr2 | rr3 | vwap (revert to VWAP for rejects) | time.',
   stop_rules='atr or edge (2 ticks past the excursion bar).', confirmations='none', sessions='All sessions',
   long_short='both', htf='session VWAP', grammar_dims='mode(reject|accept), k(2.0|3.0), stop, exit'),

 'S27': dict(name='VWAP Reclaim in Trend', klass='Class III — value + trend',
   mechanism='In the HTF trend, price reclaims session VWAP (mean-revert to VWAP then continue with the trend). Distinct '
             'from S26 (excursion).',
   entry='HTF trend up and a close reclaims above VWAP (or trend down and close breaks below VWAP); onset only; enter next open.',
   exit_rules='opp_struct (far VWAP band) | time.', stop_rules='atr or vwap (fraction of sigma past VWAP).',
   confirmations='HTF trend.', sessions='All sessions', long_short='both', htf='H4/H1 trend + session VWAP',
   grammar_dims='htf(h4|h1), band_k(1.0|2.0), stop, exit'),

 'S28': dict(name='Anchored-VWAP Reaction', klass='Class III — anchored value',
   mechanism='Reactions at a WEEK/MONTH anchored VWAP (a stable institutional cost basis) after a genuine departure. '
             'Day/swing/impulse anchors excluded (too noisy).',
   entry='After price departed >= 0.75*ATR from the anchored VWAP within 8 bars, a reclaim (cross) or bounce (tag-and-hold) '
         'at the anchor; enter next open.', exit_rules='rr2 | rr3 | time.', stop_rules='atr (1.5*ATR).',
   confirmations='the prior departure (retest).', sessions='All sessions', long_short='both', htf='week/month anchored VWAP',
   grammar_dims='anchor(week|month), mode(reclaim|bounce), exit'),

 'S29': dict(name='Day-of-Week Effect', klass='Class IV — calendar',
   mechanism='A fixed weekday directional bias, entered at that day\'s first bar. Pure calendar effect; in-sample-favourable, '
             'multiple-testing across weekdays acknowledged (calendar families are overfit-prone).',
   entry='At the first bar of the chosen weekday, enter next open directionally; hold.', exit_rules='rr2 | time.',
   stop_rules='atr (1.5*ATR).', confirmations='none', sessions='Weekday first bar', long_short='both', htf='none',
   grammar_dims='dow(0..4), side, exit'),

 'S30': dict(name='Kill-Zone Time-Window', klass='Class IV — session time-window',
   mechanism='Pre-registered UTC kill-zones (London 07-10, NY 12-15); breakout of the prior 4-bar range inside the window '
             '-> continuation or reversal. Fixed clock (not S5\'s session-relative range).',
   entry='Inside the kill-zone, close breaks the prior 4-bar high/low; onset only; continuation or reversal; enter next open.',
   exit_rules='rr2 | rr3 | time.', stop_rules='atr (1.5*ATR).', confirmations='none',
   sessions='London KZ 07-10 UTC | NY KZ 12-15 UTC', long_short='both', htf='none',
   grammar_dims='zone(london_kz|ny_kz), mode(continuation|reversal), exit'),

 'S31': dict(name='Month-End / Month-Start Effect', klass='Class IV — calendar',
   mechanism='Fixed windows around the month change (day-of-month >=27 or <=2), entered at the day\'s first bar. Calendar '
             'effect; small sample; in-sample-only overfit risk.',
   entry='In the month-end/start window, at the day\'s first bar, enter next open directionally.', exit_rules='rr2 | rr3 | time.',
   stop_rules='atr (1.5*ATR).', confirmations='none', sessions='Month-end/start first bar', long_short='both', htf='none',
   grammar_dims='window(month_end|month_start), side, exit'),

 'S38': dict(name='Patient Pullback-into-Zone', klass='Class VII — trend continuation (redesign of S7/S10)',
   mechanism='In an HTF trend, enter on a pullback INTO a discount zone (EMA20/EMA50/fib-0.5) WITHOUT waiting for a '
             'confirmation close (better fill than the confirmation crowd). Approximated by market-on-next-open.',
   entry='HTF trend; onset of price tagging the zone (uptrend pullback down / downtrend pullback up); enter next open.',
   exit_rules='rr2 | rr3 | trailing.', stop_rules='swing (20-bar extreme) or atr.', confirmations='none (patient entry, no confirmation)',
   sessions='All sessions', long_short='both', htf='H4 or H1 trend', grammar_dims='htf(h4|h1), zone(ema20|ema50|fib50), stop, exit'),

 'S39': dict(name='Trend-Efficiency-Gated Continuation', klass='Class VII — efficient continuation (redesign of S15)',
   mechanism='Take continuation ONLY when the trend is CLEAN — high Kaufman efficiency ratio (net move / path length) '
             'predicts persistence; skip noisy chop. Loser = counter-trend faders in efficient trends. (Wave-1 EXP-02: '
             'the gate did not beat random selection at the family-wise bar.)',
   entry='M15 trend + an expansion bar (range>1.5*ATR, matching close) GATED by efficiency ratio >= er_thr over L bars; '
         'onset only; enter next open.', exit_rules='rr2 | rr3 | trailing.', stop_rules='atr or swing (20-bar extreme).',
   confirmations='the efficiency-ratio gate.', sessions='All sessions', long_short='both', htf='M15 trend + efficiency ratio',
   grammar_dims='L(10|20), er_thr(0.3|0.5), stop, exit'),

 'S40': dict(name='Regime Router', klass='Class VIII — meta / regime router',
   mechanism='Deploy each sub-edge only where its mechanism holds: TREND regime (efficiency>=thr) -> efficient continuation; '
             'RANGE regime -> fade extremes back to the middle. Addresses S11/S12 regime-blindness.',
   entry='Classify regime by efficiency ratio; trend -> expansion continuation (like S39); range -> fade the `range_lb` '
         'rolling extreme back to the middle; onset only; enter next open.', exit_rules='rr2 | rr3 (range legs target the range middle).',
   stop_rules='atr or swing.', confirmations='the regime classification.', sessions='All sessions', long_short='both',
   htf='efficiency-ratio regime', grammar_dims='er_thr(0.3|0.5), range_lb(20|50), stop, exit'),

 'S41': dict(name='Volume-Climax Reversal', klass='Batch1 — volume magnitude',
   mechanism='A participation spike (high volume rank) at a 20-bar price extreme = capitulation/blow-off; forced flow '
             'exhausts -> reversal. NEW ingredient: volume MAGNITUDE.',
   entry='Volume rank >= vthr at a 20-bar high (short) or low (long); onset only; enter next open (reversal).',
   exit_rules='rr2 | rr3 | time.', stop_rules='bar (2 ticks past the climax bar) or atr.', confirmations='the volume climax.',
   sessions='All sessions', long_short='both', htf='none', grammar_dims='vthr(0.90|0.95), stop, exit'),

 'S42': dict(name='Short-Term Return Reversal', klass='Batch1 — short-term reversal (overreaction)',
   mechanism='The largest recent L-bar mover reverses (liquidity providers absorb overreaction) — the classic short-term-'
             'reversal anomaly. Distinct from S8 (distance-from-SMA).',
   entry='Onset of L-bar return > thr (overbought -> short) or < -thr (oversold -> long); enter next open (fade).',
   exit_rules='rr2 | rr3 | time.', stop_rules='atr (1.5*ATR).', confirmations='none', sessions='All sessions',
   long_short='both', htf='none', grammar_dims='L(3|6), thr(0.006|0.012), exit'),

 'S43': dict(name='Momentum Divergence (RSI/Price)', klass='Batch1 — oscillator divergence',
   mechanism='Price makes a new extreme while RSI does NOT — momentum weakening -> reversal. NEW ingredient: price/'
             'oscillator divergence.',
   entry='New `lb`-bar price high with RSI below its recent high (bearish) or new low with RSI above its recent low '
         '(bullish); onset only; enter next open (reversal).', exit_rules='rr2 | time.',
   stop_rules='bar (2 ticks past the divergence bar) or atr.', confirmations='the divergence.', sessions='All sessions',
   long_short='both', htf='RSI (M15 or H1)', grammar_dims='rsi_tf(m|h1), lb(14|20), stop, exit'),

 'S44': dict(name='Intrabar Pressure / Close-Location', klass='Batch1 — order-flow proxy',
   mechanism='Intrabar buying/selling pressure via close-location-value CLV=((C-L)-(H-C))/(H-L). Persistent pressure -> '
             'continuation; extreme -> exhaustion. NEW ingredient: intrabar close position.',
   entry='N-bar mean CLV crosses > 0.5 (buy) or < -0.5 (sell); continue = with the pressure, exhaust = against it; onset '
         'only; enter next open.', exit_rules='rr2 | rr3 | time.', stop_rules='atr (1.5*ATR).', confirmations='none',
   sessions='All sessions', long_short='both', htf='none', grammar_dims='N(3|5), mode(continue|exhaust), stop, exit'),

 'S45': dict(name='Consecutive-Bar Streak', klass='Batch1 — sequence / run-length',
   mechanism='N consecutive same-direction closes -> reverse (overextension) or continue (momentum). NEW ingredient: raw '
             'close-streak length. k=3 excluded (not "extended").',
   entry='Exactly k consecutive up/down closes (streak onset); reverse or continue; enter next open.', exit_rules='rr2 | time.',
   stop_rules='atr (1.5*ATR).', confirmations='none', sessions='All sessions', long_short='both', htf='none',
   grammar_dims='k(4|5|6), mode(reverse|continue), exit'),

 'S46': dict(name='Volume-Confirmed Breakout', klass='Batch1 — participation-gated breakout',
   mechanism='Breakout of a level ONLY when volume expands (conviction) — tests whether VOLUME is the missing ingredient '
             'that made the volume-blind breakouts (S3/S23) fail.',
   entry='Close beyond the `lb`-bar extreme with volume rank >= vthr; onset only; enter next open.', exit_rules='rr2 | rr3 | trailing.',
   stop_rules='level (2 ticks past the level) or atr.', confirmations='REQUIRED: volume expansion.', sessions='All sessions',
   long_short='both', htf='none', grammar_dims='vthr(0.70|0.85), lb(20|50), stop, exit'),

 'S47': dict(name='Weekend-Gap Fill / Continuation', klass='Batch2 — weekend gap',
   mechanism='The Friday-close -> Monday-open weekend liquidity gap either fills or continues. Distinct from S19 '
             '(intraday gaps). TECHNICALLY INVALID for research: sample too small (n<25).',
   entry='At Monday open, a gap > thr*ATR; fill = toward the prior close, continue = with the gap; enter next open.',
   exit_rules='rr2 | rr3 | opp_struct (prior close for fills) | time.', stop_rules='atr (1.5*ATR).', confirmations='none',
   sessions='Monday open only', long_short='both', htf='none', grammar_dims='mode(fill|continue), thr(0.3|0.6), exit',
   status_override='INVALID — sample size n<25 (weekend Mondays only); not a valid research result.'),

 'S48': dict(name='Consolidation-Duration Breakout', klass='Batch2 — compression duration',
   mechanism='TIME spent compressed (run-length of compression), not the compression level — longer coil -> larger '
             'expansion. Distinct from S23 (level + HTF).',
   entry='D consecutive compressed bars, then a close beyond the D-bar band; onset only; enter next open.',
   exit_rules='rr2 | rr3 | trailing.', stop_rules='range (opposite band edge) or atr.', confirmations='the sustained coil.',
   sessions='All sessions', long_short='both', htf='none', grammar_dims='D(6|12), stop, exit'),

 'S49': dict(name='Narrowest-Range (NR) Breakout', klass='Batch2 — NR pattern',
   mechanism='The NR-N compression pattern (smallest range of the last N bars) as the breakout trigger. TECHNICALLY '
             'INVALID: the pattern is non-selective (fires too often to be a discrete setup); NOT backtested/retained.',
   entry='An NR-N bar, then a close beyond that bar\'s high/low within a few bars; breakout or fade; enter next open.',
   exit_rules='rr2 | time.', stop_rules='bar (2 ticks past the NR bar) or atr.', confirmations='none',
   sessions='All sessions', long_short='both', htf='none', grammar_dims='N(4|7), mode(breakout|fade), stop, exit',
   status_override='INVALID — non-selective trigger (fails the discrete-setup selectivity gate); excluded from results.'),

 'S50': dict(name='Outside-Bar / Engulfing Reversal', klass='Batch2 — candlestick pattern',
   mechanism='An engulfing (outside) candle that is also a genuine range expansion (>ATR) = a control shift; reversal or '
             'continuation. NEW ingredient: candlestick pattern.',
   entry='Outside bar (high>prior high & low<prior low) with range>ATR; bullish/bearish engulfing; reversal or '
         'continuation; enter next open.', exit_rules='rr2 | rr3 | time.', stop_rules='bar (2 ticks past the engulfing bar) or atr.',
   confirmations='none', sessions='All sessions', long_short='both', htf='none', grammar_dims='mode(reversal|continuation), stop, exit'),

 'S51': dict(name='Intraday Range-Position Reversion', klass='Batch2 — session range position',
   mechanism='Position within the developing SESSION range: near the top/bottom -> revert toward the middle. Distinct '
             'from S8 (SMA distance) and S26 (VWAP band).',
   entry='After the session range has formed (>=8 bars), price at >= thr (short) or <= 1-thr (long) of the session range; '
         'onset only; enter next open (revert).', exit_rules='rr2 | time.', stop_rules='atr or edge (2 ticks past the session extreme).',
   confirmations='none', sessions='All sessions (intraday range)', long_short='both', htf='none', grammar_dims='thr(0.85|0.95), stop, exit'),
}

# Not-implemented families (blocked on external Tier-1/Tier-2 data; documented for completeness, no executable spec).
NOT_IMPLEMENTED = {
 'S32': 'Intermarket / macro correlation (needs external DXY/rates/related-asset data) — CEO-gated, NOT implemented.',
 'S33': 'Cross-asset lead-lag (needs external correlated-asset series) — CEO-gated, NOT implemented.',
 'S34': 'Rates / yield-curve conditioning (needs external rates data) — CEO-gated, NOT implemented.',
 'S35': 'Positioning / COT (needs external positioning data) — CEO-gated, NOT implemented.',
 'S36': 'Macro-event / calendar-surprise (needs external event data) — CEO-gated, NOT implemented.',
 'S37': 'Sentiment / flow (needs external sentiment/flow data) — CEO-gated, NOT implemented.',
}
