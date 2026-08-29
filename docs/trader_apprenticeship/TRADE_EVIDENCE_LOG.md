# Trade Evidence Log (Evidence Upgrade V1)

ERRATUM NOTE: trade #57's entry/close clock times as recorded elsewhere in this session (16:45
entry / 17:30 close) are each 15 minutes LATER than true (true: 16:30 entry / 17:15 close);
self-discovered labeling slip, root cause and full correction in 2020_Q2_H4_LOG.md's ERRATUM
entry. RESULT_R/MFE/MAE/STATIC_BASELINE figures below are unaffected (computed from correct bar
data throughout, independent of the clock label).

Per-trade R-normalized metrics, context tags, and static-baseline tracking. See
`EVIDENCE_UPGRADE_METHODOLOGY_V1.md` for definitions and governance. Backfilled entries
below use ONLY entry/stop/result values already logged in real time in
`2020_Q2_H4_LOG.md` before each trade's outcome was known — nothing here is estimated
or reconstructed from later information.

## Backfilled R-Metrics (trades already closed before this install; RESULT_R only)

| Trade | Dir | Entry | Initial Stop | Exit | Result (pts) | Initial Risk (pts) | RESULT_R | MFE/MAE | Static Baseline |
|---|---|---|---|---|---|---|---|---|---|
| #48 | LONG | 1731.446 | 1723.654 | 1730.03 | -1.416 | 7.792 | -0.182 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED (see methodology) |
| #51 | SHORT | 1754.79 | 1758.448 | 1732.404 | +22.386 | 3.658 | +6.120 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |
| #52 | SHORT | 1733.911 | 1736.338 | 1735.654 | -1.743 | 2.427 | -0.718 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |
| #53 | LONG | 1739.969 | 1733.168 | 1739.222 | -0.747 | 6.801 | -0.110 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |
| #54 | SHORT | 1744.494 | 1752.279 | 1752.328 | -7.834 | 7.785 | -1.006 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |
| #55 | SHORT | 1728.586 | 1735.874 | 1725.33 | +3.256 | 7.288 | +0.447 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |
| #56 | SHORT | 1718.845 | 1728.356 | 1712.988 | +5.857 | 9.511 | +0.616 | NOT_RECOVERABLE_WITHOUT_HINDSIGHT | DEFERRED |

NOTE (honest, at-install observation, not a new rule): trade #54's RESULT_R lands at
almost exactly -1.006R — consistent with the fact that it was never trailed (never
became profitable) and exited a hair past its original stop. This is arithmetic
confirmation of what was already narrated, not a new finding.

Full-portfolio backfill (trades #1–#47) is deferred — see methodology doc §2.

## Template for New Trades (#63 onward -- Multi-Timeframe Trend Alignment V1, CEO correction 2020-06-08)

The bare label WITH_TREND may no longer be used alone. See 2020_Q2_H4_LOG.md's 2020-06-08
ADMINISTRATIVE entry for full methodology. H4 = context, H1 = active structural phase, M15 =
executable directional structure.

```
## TRADE #<N> -- MULTI-TIMEFRAME CONTEXT (frozen at entry, before the six-field contract)
FORMAL_H4_REGIME:
H1_ACTIVE_PHASE:
M15_ACTIVE_STRUCTURE:
H4_DIRECTION_RELATION: ALIGNED_<DIR> | COUNTER_<DIR> | NEUTRAL | TRANSITIONAL | UNCLEAR
H1_DIRECTION_RELATION: ALIGNED_<DIR> | COUNTER_<DIR> | NEUTRAL | TRANSITIONAL | UNCLEAR
M15_DIRECTION_RELATION: ALIGNED_<DIR> | COUNTER_<DIR> | NEUTRAL | TRANSITIONAL | UNCLEAR
MULTITIMEFRAME_ALIGNMENT: FULLY_ALIGNED | PARTIALLY_ALIGNED | CONFLICTED | TRANSITIONAL | UNCLEAR
REGIME_STALENESS_WARNING: ACTIVE | INACTIVE
TRANSITION_WATCH_STATUS: NONE | EARLY | DEVELOPING | STRONG
LOCAL_STRUCTURE_REQUIRED_FOR_ENTRY: (only relevant if MULTITIMEFRAME_ALIGNMENT is CONFLICTED or
  TRANSITIONAL -- describe the specific local re-alignment evidence that justified the entry, e.g.
  failure of a higher-low sequence, break+failed-reclaim of local support, lower-high formation)

## TRADE #<N> -- EVIDENCE TAGS (frozen at entry)
DIRECTION:
ENTRY:
INITIAL_STOP:
INITIAL_RISK_POINTS:
STRUCTURAL_TARGET: (the analytical market objective -- first realistic pre-entry-visible level, no lookahead)
TP_EXECUTION_BUFFER_PIPS: 10 (per Structural TP Execution Buffer V1 -- SHORT: EXECUTABLE_TP = STRUCTURAL_TARGET + 1.000; LONG: EXECUTABLE_TP = STRUCTURAL_TARGET - 1.000)
EXECUTABLE_TP: (the actual close-trigger level -- what the chart Risk/Reward object and stopLevel/profitLevel are set to)
PLANNED_RR_TO_EXECUTABLE_TP: (risk in points : reward-to-EXECUTABLE_TP in points)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop close-trigger, whichever first
H4_REGIME:
H1_PHASE:
M15_STATE:
REGIME_STACK:
DIRECTION_RELATION: H4_ALIGNED_BUT_LOCAL_COUNTERTREND | TRANSITION_CONFLICT_SHORT | FULLY_ALIGNED_SHORT | FULLY_ALIGNED_LONG | COUNTERTREND | NEUTRAL_OR_UNCLEAR (see MULTITIMEFRAME_ALIGNMENT above for the authoritative classification -- this field is now a short descriptive label only, never used alone)
SESSION: ASIA | LONDON | PRE_US | NY_US_CASH | LATE_US | OTHER
VOLATILITY_STATE: LOW | NORMAL | HIGH | EXPANSION | COMPRESSION | UNKNOWN
SETUP_FAMILY:
LOCATION_TYPE:
CONFIRMATION_TYPE:

## TRADE #<N> -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS:
ACTUAL_RESULT_R:
MFE_POINTS / MFE_R:
MAE_POINTS / MAE_R:
STRUCTURAL_TARGET_REACHED: YES | NO (did price ever close at/beyond STRUCTURAL_TARGET itself, whether or not the trade had already closed at EXECUTABLE_TP or SL)
EXECUTABLE_TP_REACHED: YES | NO (did the trade actually close via EXECUTABLE_TP)
STATIC_BASELINE_STATUS: RESOLVED_VIA_ORIGINAL_STOP | HORIZON_MARK | STILL_OPEN
STATIC_RESULT_POINTS:
STATIC_RESULT_R:
ACTUAL_VS_STATIC: (actual - static, positive = trailing added value on this trade)
```

**Structural TP Execution Buffer V1** (CEO decision, installed real-time, PROSPECTIVE ONLY -- see
2020_Q2_H4_LOG.md's ADMINISTRATIVE entry for full text): from the next trade opened after
installation onward, every trade additionally freezes STRUCTURAL_TARGET, TP_EXECUTION_BUFFER_PIPS
(=10, i.e. 1.000 price point), EXECUTABLE_TP, and PLANNED_RR_TO_EXECUTABLE_TP. EXECUTABLE_TP (not
the raw structural target) is what the close-based execution convention and the chart
stopLevel/profitLevel are set to. SL methodology is unchanged -- the buffer applies to TP only.
Does NOT modify Trade #66 or any earlier trade; #66's FROZEN_TP remains 1747.566 exactly as
originally set.

## TRADE #57 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1706.11
INITIAL_STOP: 1710.66
INITIAL_RISK_POINTS: 4.55
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1710.66)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: sharp countertrend spike exhausting into a swing-high rejection
M15_STATE: 2-bar real-volume reversal confirmation off a fresh high
REGIME_STACK: H4 BEARISH / short-term countertrend spike exhaustion
DIRECTION_RELATION: WITH_TREND
SESSION: NY_US_CASH
VOLATILITY_STATE: HIGH/EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close after countertrend exhaustion spike
LOCATION_TYPE: fresh swing-high rejection
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (4286, 2574)

## TRADE #57 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: -6.192
ACTUAL_RESULT_R: -1.361
MFE_POINTS / MFE_R: 0.628 / 0.138
MAE_POINTS / MAE_R: 7.216 / 1.586
STATIC_BASELINE_STATUS: RESOLVED_VIA_ORIGINAL_STOP (identical to actual -- stop was never trailed)
STATIC_RESULT_POINTS: -6.192
STATIC_RESULT_R: -1.361
ACTUAL_VS_STATIC: 0.000 (no discretionary management occurred on this trade)

## TRADE #58 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1740.327
INITIAL_STOP: 1745.304
INITIAL_RISK_POINTS: 4.977
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1745.304)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: fresh apprenticeship high rejected, reversal within the broader H4 downtrend
M15_STATE: 2-bar real-volume reversal confirmation off a fresh high
REGIME_STACK: H4 BEARISH / short-term high rejection
DIRECTION_RELATION: WITH_TREND
SESSION: NY_US_CASH
VOLATILITY_STATE: HIGH/EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close after a fresh-high rejection
LOCATION_TYPE: fresh swing-high rejection
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (2535, 3638)

## TRADE #58 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: +12.259
ACTUAL_RESULT_R (REALIZED_RESULT_R): +2.463
MFE_POINTS / MFE_R: 18.629 / 3.743
MAE_POINTS / MAE_R: 0.543 / 0.109
STATIC_BASELINE_STATUS: HORIZON_MARK (resolved 2020-06-04 20:30:00 UTC, T=1591302600 -- the
  192nd M15 bar since entry per this session's running bar-count tracking; original stop 1745.304
  was never threatened at any point across the whole window)
STATIC_RESULT_POINTS: 27.492 (entry 1740.327 minus horizon bar close 1712.835)
STATIC_RESULT_R: 5.524
ACTUAL_VS_STATIC: -15.233 (ACTUAL_RESULT_POINTS +12.259 minus STATIC_RESULT_POINTS +27.492 -- the
  actual trailed trade underperformed the hypothetical never-trailed static baseline by 15.233pts,
  since the market continued favorably well past where the trail closed the real trade)
NOTE: the actual fill (1728.068) landed 0.166pts beyond the nominal trailed stop (1727.902),
confirming the CEO's mid-trade correction that a trail level is a TRIGGER threshold only, not a
guaranteed REALIZED_RESULT_R.
NOTE (horizon resolution, disclosed honestly): the 192-bar count above comes from this session's
running informal tracking across many turns (incremented per bar/batch read, not from a fresh
precise replay-verified recount) -- consistent with how it was tracked throughout, and stated here
plainly since this is the field where it matters most. The underlying market fact (original stop
never threatened, continued favorable drift well past the trail) is independent of any small
imprecision in the exact bar count.

## TRADE #59 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1712.008
INITIAL_STOP: 1726.146
INITIAL_RISK_POINTS: 14.138
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1726.146)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: decisive fresh-low breakdown, accelerating multi-bar real-volume down move
M15_STATE: 2-bar real-volume reversal confirmation, both bars decisive real volume with wide
  ranges
REGIME_STACK: H4 BEARISH / accelerating downside breakdown
DIRECTION_RELATION: WITH_TREND
SESSION: PRE_US
VOLATILITY_STATE: HIGH/EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close accelerating breakdown after a fresh
  local-high rejection
LOCATION_TYPE: fresh swing-high rejection / breakdown continuation
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (3365, 4993)

## TRADE #59 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: -0.654
ACTUAL_RESULT_R (REALIZED_RESULT_R): -0.046
MFE_POINTS / MFE_R: 22.419 / 1.586 (low 1689.589 @ 2020-06-03 14:30 UTC)
MAE_POINTS / MAE_R: 3.773 / 0.267 (high 1715.781 @ the closing bar itself, 2020-06-04 10:45 UTC)
STATIC_BASELINE_STATUS: HORIZON_MARK (resolved 2020-06-05 16:30:00 UTC, T=1591374600 -- the
  192nd M15 bar since entry per this session's running bar-count tracking; original stop 1726.146
  was never threatened at any point across the whole window)
STATIC_RESULT_POINTS: 30.805 (entry 1712.008 minus horizon bar close 1681.203)
STATIC_RESULT_R: 2.179
ACTUAL_VS_STATIC: -31.459 (ACTUAL_RESULT_POINTS -0.654 minus STATIC_RESULT_POINTS +30.805 -- the
  actual trailed trade dramatically underperformed the hypothetical never-trailed static baseline,
  since the market continued favorably (from a SHORT perspective) well past where the trail closed
  the real trade, and even trade #60/#61/#62's subsequent price action stayed well below entry)
NOTE (horizon resolution, disclosed honestly): the 192-bar count above comes from this session's
running informal tracking across many turns (incremented per bar/batch read, not from a fresh
precise replay-verified recount) -- consistent with how trade #58's resolution was handled. The
underlying market fact (original stop never threatened, continued favorable drift well past the
trail) is independent of any small imprecision in the exact bar count.
NOTE: the TRAIL_TRIGGER_LEVEL_R at the moment of the trail (1711.9) was +0.008R -- the actual
close-based fill (1712.662) landed past both the nominal stop and the entry price, flipping the
outcome to a small genuine LOSS (-0.046R). The sharpest illustration yet of the CEO's correction:
a trail level is a trigger threshold only, never a guaranteed result, in either direction.
NOTE: MFE was previously mislabeled in intermediate session notes as "19.926pts/+1.412R @ 14:15
UTC" -- that figure was actually computed from the adjacent 14:15 UTC bar's low (1692.082), not
the true trade-life low (1689.589 @ 14:30 UTC). Corrected here; the error was measurement-only
(Evidence Upgrade instrumentation) and never affected any entry/exit/trail decision.

## TRADE #60 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1707.01
INITIAL_STOP: 1713.5
INITIAL_RISK_POINTS: 6.49
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1713.5)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: real-volume breakdown resuming after an extended thin-volume compression
M15_STATE: 2-bar real-volume reversal confirmation off a local high
REGIME_STACK: H4 BEARISH / compression-to-expansion breakdown
DIRECTION_RELATION: WITH_TREND
SESSION: PRE_US
VOLATILITY_STATE: EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close breaking a multi-hour compression
LOCATION_TYPE: breakdown from extended compression / local-high rejection
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (2700, 2912)

## TRADE #60 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: -8.948
ACTUAL_RESULT_R (REALIZED_RESULT_R): -1.379
MFE_POINTS / MFE_R: 1.45 / 0.223 (low 1705.56 @ 2020-06-04 12:15 UTC)
MAE_POINTS / MAE_R: 9.718 / 1.497 (high 1716.728, the closing bar's own high)
STATIC_BASELINE_STATUS: RESOLVED_VIA_ORIGINAL_STOP (identical to actual -- stop was never trailed,
  only 2 bars elapsed since entry before the reversal)
STATIC_RESULT_POINTS: -8.948
STATIC_RESULT_R: -1.379
ACTUAL_VS_STATIC: 0.000 (no discretionary management occurred on this trade)
NOTE: had the fill occurred exactly at the nominal stop (1713.5), the loss would have been exactly
-1.0R; the actual close-based fill was -1.379R because the decisive real-volume (7566) triggering
bar's own close landed 2.458pts past the stop. The mirror-image risk of the CEO's trail-level
correction, here on the loss side and on an untrailed original stop -- confirms the close-based
mechanism applies to every stop in this apprenticeship, not only trailed ones.

## TRADE #61 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1707.856
INITIAL_STOP: 1718.5
INITIAL_RISK_POINTS: 10.644
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1718.5)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: resumption of the WITH-trend move after a sharp intraday reversal spike
M15_STATE: 2-bar real-volume reversal confirmation, wide-range confirmation bar
REGIME_STACK: H4 BEARISH / post-reversal-spike resumption
DIRECTION_RELATION: WITH_TREND
SESSION: NY_US_CASH
VOLATILITY_STATE: EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close resuming after a reversal spike
LOCATION_TYPE: resumption below the reversal-spike high cluster
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (4558, 2585)

## TRADE #61 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: -12.237
ACTUAL_RESULT_R (REALIZED_RESULT_R): -1.150
MFE_POINTS / MFE_R: 7.401 / 0.695 (low 1700.455 @ 2020-06-04 14:00 UTC)
MAE_POINTS / MAE_R: 13.627 / 1.280 (high 1721.483, the closing bar's own high)
STATIC_BASELINE_STATUS: RESOLVED_VIA_ORIGINAL_STOP (identical to actual -- stop was never trailed)
STATIC_RESULT_POINTS: -12.237
STATIC_RESULT_R: -1.150
ACTUAL_VS_STATIC: 0.000 (no discretionary management occurred on this trade)
NOTE: three consecutive bars (16:15, 16:30, 16:45, 17:00 UTC) had highs within 0.27-1.63pts of the
stop and closed back below it, surviving on the close-based convention each time, before the fourth
test finally closed beyond it. A clean, repeated demonstration of why the close-based (not
wick-based) trigger convention matters in practice, not just in theory.

## TRADE #62 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY: 1680.167
INITIAL_STOP: 1688.5
INITIAL_RISK_POINTS: 8.333
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1688.5)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: resolution of an extreme 5-bar whipsaw episode into a genuine breakdown
M15_STATE: 2-bar real-volume reversal confirmation, descending-high staircase
REGIME_STACK: H4 BEARISH / whipsaw-resolution breakdown
DIRECTION_RELATION: WITH_TREND
SESSION: LONDON
VOLATILITY_STATE: EXTREME_EXPANSION
SETUP_FAMILY: WITH-trend SHORT, 2-bar real-volume down-close resolving an extreme whipsaw
LOCATION_TYPE: breakdown continuation below a descending-high staircase
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (6299, 7431)

## TRADE #62 -- EVIDENCE CLOSE (frozen at close)
ACTUAL_RESULT_POINTS: -8.342
ACTUAL_RESULT_R (REALIZED_RESULT_R): -1.001
MFE_POINTS / MFE_R: 9.729 / 1.168 (low 1670.438 @ 2020-06-05 14:45 UTC)
MAE_POINTS / MAE_R: 8.817 / 1.058 (high 1688.984, the closing bar's own high)
STATIC_BASELINE_STATUS: RESOLVED_VIA_ORIGINAL_STOP (identical to actual -- stop was never trailed)
STATIC_RESULT_POINTS: -8.342
STATIC_RESULT_R: -1.001
ACTUAL_VS_STATIC: 0.000 (no discretionary management occurred on this trade)
NOTE: this trade's stop level (1688.5) was tested four separate times over 5 bars, with three
distinct wicks piercing it outright (closest survival margin: 0.147pts) before the eventual
triggering close crossed it by just 0.009pts -- the narrowest margin of the entire apprenticeship.
Despite this extraordinary intrabar drama, the final REALIZED_RESULT_R (-1.001) landed almost
exactly at the nominal -1.0R, a useful counterpoint to trade #60's demonstration of meaningful
close-based overshoot: repeated wick-piercing does not by itself imply the eventual close will
land far past the stop.

## MULTI-TIMEFRAME ALIGNMENT AUDIT (CEO correction, 2020-06-08, prospective methodology only)

Historical labels for trades #58-#62 below are NOT rewritten. This is an annotation only, derived
strictly from each trade's contemporaneously frozen H1_PHASE/M15_STATE tags (written at entry,
before outcome was known) -- no hindsight reconstruction. Where the new framework's question goes
beyond what the original tags captured, the answer is NOT_RECOVERABLE_WITHOUT_HINDSIGHT rather than
inferred from the eventual outcome.

### TRADE #58
ORIGINAL_LABEL: WITH_TREND
H4_RELATION_AT_ENTRY: ALIGNED_SHORT (H4_REGIME frozen as BEARISH; entry direction SHORT)
H1_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen H1_PHASE: "fresh apprenticeship high rejected, reversal
  within the broader H4 downtrend" -- describes H1 itself reversing downward)
M15_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen M15_STATE: 2-bar real-volume reversal confirmation off
  a fresh high)
MULTITIMEFRAME_ALIGNMENT_AT_ENTRY: FULLY_ALIGNED (at the immediate/local structural level captured
  by the original tags -- whether a larger-degree H1 channel coexisted is
  NOT_RECOVERABLE_WITHOUT_HINDSIGHT)

### TRADE #59
ORIGINAL_LABEL: WITH_TREND
H4_RELATION_AT_ENTRY: ALIGNED_SHORT
H1_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen H1_PHASE: "decisive fresh-low breakdown, accelerating
  multi-bar real-volume down move")
M15_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen M15_STATE: 2-bar real-volume reversal confirmation,
  both bars decisive real volume with wide ranges)
MULTITIMEFRAME_ALIGNMENT_AT_ENTRY: FULLY_ALIGNED (immediate/local level; larger-degree channel
  question NOT_RECOVERABLE_WITHOUT_HINDSIGHT)

### TRADE #60
ORIGINAL_LABEL: WITH_TREND
H4_RELATION_AT_ENTRY: ALIGNED_SHORT
H1_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen H1_PHASE: "real-volume breakdown resuming after an
  extended thin-volume compression")
M15_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen M15_STATE: 2-bar real-volume reversal confirmation off
  a local high)
MULTITIMEFRAME_ALIGNMENT_AT_ENTRY: FULLY_ALIGNED (immediate/local level; larger-degree channel
  question NOT_RECOVERABLE_WITHOUT_HINDSIGHT). Note: this trade reversed almost immediately after
  entry on the largest-volume bar seen up to that point -- an OUTCOME, not entry-time evidence, and
  is not used to reinterpret this classification per the CEO's explicit governance rule.

### TRADE #61
ORIGINAL_LABEL: WITH_TREND
H4_RELATION_AT_ENTRY: ALIGNED_SHORT
H1_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen H1_PHASE: "resumption of the WITH-trend move after a
  sharp intraday reversal spike")
M15_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen M15_STATE: 2-bar real-volume reversal confirmation,
  wide-range confirmation bar)
MULTITIMEFRAME_ALIGNMENT_AT_ENTRY: FULLY_ALIGNED (immediate/local level; larger-degree channel
  question NOT_RECOVERABLE_WITHOUT_HINDSIGHT)

### TRADE #62
ORIGINAL_LABEL: WITH_TREND
H4_RELATION_AT_ENTRY: ALIGNED_SHORT
H1_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen H1_PHASE: "resolution of an extreme 5-bar whipsaw
  episode into a genuine breakdown")
M15_RELATION_AT_ENTRY: ALIGNED_SHORT (frozen M15_STATE: 2-bar real-volume reversal confirmation,
  descending-high staircase)
MULTITIMEFRAME_ALIGNMENT_AT_ENTRY: FULLY_ALIGNED (immediate/local level; larger-degree channel
  question NOT_RECOVERABLE_WITHOUT_HINDSIGHT). Already separately noted
  VALID_AT_ENTRY_BUT_REGIME_LATER_WEAKENED in the 10:45 UTC regime audit -- that finding stands
  unchanged; this entry adds the multi-timeframe breakdown only.

## TRADE #63 -- MULTI-TIMEFRAME CONTEXT (frozen at entry)
FORMAL_H4_REGIME: BEARISH
H1_ACTIVE_PHASE: confirmed real-volume bullish recovery/reclaim, extending to fresh highs
M15_ACTIVE_STRUCTURE: decisive real-volume breakout, 3 consecutive massive-volume up-closes
H4_DIRECTION_RELATION: COUNTER_LONG
H1_DIRECTION_RELATION: ALIGNED_LONG
M15_DIRECTION_RELATION: ALIGNED_LONG
MULTITIMEFRAME_ALIGNMENT: TRANSITIONAL
REGIME_STALENESS_WARNING: ACTIVE
TRANSITION_WATCH_STATUS: DEVELOPING
LOCAL_STRUCTURE_REQUIRED_FOR_ENTRY: real-volume test-and-defend of 1688.5 (13:30 down / 13:45 up)
  followed by 2 consecutive real-volume continuation closes higher (5674, 6544), both exceeding
  trade #53's 3544/5373 benchmark on both legs

## TRADE #63 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: LONG
ENTRY: 1695.555
INITIAL_STOP: 1685.5
INITIAL_RISK_POINTS: 10.055
PRIMARY_TARGET: none fixed (consistent with standing practice)
TERMINAL_HORIZON (static baseline only): 192 M15 bars post-entry, or original-stop (1685.5)
  close-trigger, whichever first
H4_REGIME: BEARISH
H1_PHASE: confirmed real-volume bullish recovery, extending to fresh highs
M15_STATE: 2-bar real-volume breakout confirmation, both bars exceeding trade #53's benchmark
REGIME_STACK: H4 BEARISH (stale) / H1 bullish recovery (real-volume confirmed) / M15 breakout
DIRECTION_RELATION: TRANSITIONAL LONG (see MULTITIMEFRAME_ALIGNMENT above)
SESSION: LONDON
VOLATILITY_STATE: EXTREME_EXPANSION
SETUP_FAMILY: TRANSITIONAL LONG, real-volume reclaim-and-continuation clearing the elevated
  countertrend bar
LOCATION_TYPE: breakout from a defended support zone (1688.5)
CONFIRMATION_TYPE: 2 consecutive real-volume closes higher (5674, 6544)

### TRADE #63 EVIDENCE CLOSE
STATUS: CLOSED, WIN
ENTRY: 1695.555 (2020-06-08 14:15 UTC) / EXIT (close-based fill): 1718.742 (2020-06-10 14:45 UTC)
INITIAL_RISK_POINTS: 10.055
GROSS: +23.187pts / REALIZED_RESULT_R: +2.306R
TRADE_MFE: +31.801pts / +3.1627R (high 1727.356, 2020-06-10 14:15 UTC)
TRADE_MAE: -5.087pts / -0.5059R (low 1690.468, 2020-06-08 15:00 UTC)
DURATION: ~48.5 hours, 194 M15 bars
TRAIL HISTORY: 1685.5 (initial) -> 1692.9 (2020-06-08 17:30 UTC) -> 1696.394 (2020-06-09 08:45 UTC)
-> 1706.478 (2020-06-09 09:30 UTC ref) -> 1721.134 (2020-06-10 11:45 UTC ref). Four trails, all
TRADER_MISTAKE_004-checked clean, zero premature triggers across six distinct wick-tests.

STATIC_BASELINE (Evidence Upgrade V1): resolved via HORIZON_MARK (192 bars/~48h, 2020-06-10 14:15
UTC, price 1726.148) -- STATIC_BASELINE_RESULT: +30.593pts / +3.0426R. Trailed result (+2.306R)
came in below the static-at-horizon snapshot because price continued to the trade's true MFE
(+3.1627R, coincidentally the same bar as the horizon) before a sharp reversal 30 minutes later.
Single data point (n=1); the trailing approach also fully avoided the -0.506R MAE exposure a pure
static hold carried the entire time. No conclusion drawn from one trade.

MULTI-TIMEFRAME CONTEXT AT ENTRY (unchanged from entry, frozen): FORMAL_H4_REGIME BEARISH /
H1_DIRECTION_RELATION ALIGNED_LONG / M15_DIRECTION_RELATION ALIGNED_LONG / MULTITIMEFRAME_ALIGNMENT
TRANSITIONAL / REGIME_STALENESS_WARNING ACTIVE / R08_BULLISH_TRANSITION_WATCH DEVELOPING at entry.

OUTCOME NOTE FOR STRATEGY_EVIDENCE_DENOMINATOR.md: Playbook B (Countertrend LONG, elevated evidence
bar) now 1-for-2 (#53 loss, #63 win). This is the first sequence to clear #53's benchmark on both
legs, and it resolved in the elevated bar's favor -- one data point, not validation (n=2).

### TRADE #64 EVIDENCE OPEN
STATUS: OPEN
ENTRY: 1740.496 (2020-06-12 14:15 UTC) / INITIAL_STOP: 1744.918 / INITIAL_RISK_POINTS: 4.422
DIRECTION: SHORT (WITH_TREND, Playbook A)
CONFIRMATION: 2 consecutive real-volume down closes (7023, 4241), rejection at the 2020-06-11
whipsaw peak (1744.918) after testing to within 1.578pts of it (13:45 UTC high 1743.34).

MULTI-TIMEFRAME CONTEXT AT ENTRY: FORMAL_H4_REGIME BEARISH / H1_ACTIVE_PHASE extended recovery
testing resistance for the 2nd time / M15_ACTIVE_STRUCTURE real-volume rejection /
H4_DIRECTION_RELATION ALIGNED_SHORT / H1_DIRECTION_RELATION TRANSITIONAL / M15_DIRECTION_RELATION
ALIGNED_SHORT / MULTITIMEFRAME_ALIGNMENT PARTIALLY_ALIGNED / REGIME_STALENESS_WARNING ACTIVE /
R08_BULLISH_TRANSITION_WATCH ACTIVE.

FIRST WITH-trend SHORT entry evaluated under the corrected Multi-Timeframe forward SHORT rule
(installed 2020-06-08) to actually pass -- the rule's first live test (2020-06-11 14:00-14:30 UTC)
correctly declined a materially weaker signal. See 2020_Q2_H4_LOG.md for full entry reasoning.

STATIC_BASELINE (Evidence Upgrade V1): tracking begins now, original stop 1744.918, resolves via
RESOLVED_VIA_ORIGINAL_STOP or HORIZON_MARK (192 M15 bars / ~48h post-entry = 2020-06-14 14:15 UTC),
whichever first.

### TRADE #64 EVIDENCE CLOSE
STATUS: CLOSED, WIN
ENTRY: 1740.496 (2020-06-12 14:15 UTC) / EXIT (close-based fill): 1734.114 (2020-06-15 00:15 UTC)
INITIAL_RISK_POINTS: 4.422
GROSS: +6.382pts / REALIZED_RESULT_R: +1.443R
TRADE_MFE: +10.91pts / +2.467R (low 1729.586, 2020-06-12 17:15 UTC)
TRADE_MAE: -0.926pts / -0.2094R (high 1741.422, 2020-06-12 14:30 UTC)
DURATION: ~58 hours wall-clock / ~35 M15 bars actual trading time (weekend closure intervened)
TRAIL HISTORY: 1744.918 (initial) -> 1736.066 (2020-06-12 15:45 UTC) -> 1735.232 (2020-06-12 17:00
UTC) -> 1733.254 (2020-06-12 18:00 UTC). Three trails, all TRADER_MISTAKE_004-checked clean.
Survived nine distinct wick-tests, including a 0.031pt margin -- the narrowest of the entire
apprenticeship. First trade to carry a live position through a weekend gap (GAP-072).

STATIC_BASELINE (Evidence Upgrade V1): STILL OPEN, not yet resolved at trade close (original stop
1744.918 never threatened, 192-bar horizon not yet reached -- only ~35 actual bars elapsed due to
the weekend closure). First STATIC_BASELINE to outlive its own trade's close; continuing to track
in background per methodology, no fabricated early resolution.

MULTI-TIMEFRAME CONTEXT AT ENTRY (frozen): FORMAL_H4_REGIME BEARISH / H1_DIRECTION_RELATION
TRANSITIONAL / M15_DIRECTION_RELATION ALIGNED_SHORT / MULTITIMEFRAME_ALIGNMENT PARTIALLY_ALIGNED.

OUTCOME NOTE: First WITH-trend SHORT to pass live evaluation under the Multi-Timeframe forward
SHORT rule (installed 2020-06-08), and it won. One data point (n=1 for the corrected rule's
"passed" cases; n=2 total including the correctly-declined 2020-06-11 test) -- not validation.

## TRADE #65 -- EVIDENCE OPEN

ENTRY_TIME: 2020-06-16 12:30:00 UTC (T=1592310600)
DIRECTION: SHORT
ENTRY_PRICE: 1724.903
INITIAL_STOP: 1732.242
INITIAL_RISK_POINTS: 7.339
FIXED_PRIMARY_TARGET: NONE (TRAILING/STRUCTURAL management, consistent with every prior trade)

CONTEXT_TAGS_AT_ENTRY (frozen):
- H4_REGIME: BEARISH
- H1_ACTIVE_PHASE: wide choppy range since trade #64's close, resolving downward on real volume
- M15_ACTIVE_STRUCTURE: 4 consecutive down-closes, last 2 real-volume (2006, 2584), decisive
  fresh local low
- H4_DIRECTION_RELATION: ALIGNED_SHORT
- H1_DIRECTION_RELATION: ALIGNED_SHORT
- M15_DIRECTION_RELATION: ALIGNED_SHORT
- MULTITIMEFRAME_ALIGNMENT: FULLY_ALIGNED
- SESSION: LONDON
- VOLATILITY_STATE: MODERATE_EXPANSION (real volume after an extended range)
- SETUP_FAMILY: WITH-trend SHORT, real-volume range-resolution continuation (Playbook A-prime)
- LOCATION_TYPE: range breakdown
- CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (2006, 2584), preceded by 2 further
  down-closes (4-bar total down sequence)

STATIC_BASELINE: tracking, original stop only (1732.242), no trail. Resolves at original-stop
close-trigger or 192-M15-bar (~48h) horizon, whichever first. Horizon mark bar target:
2020-06-18 ~12:30 UTC (subject to weekday/weekend calendar in the underlying replay feed).

STATUS: OPEN

## TRADE #65 -- EVIDENCE CLOSE

CLOSE_TIME: 2020-06-18 08:45:00 UTC (T=1592469900)
EXIT_FILL: 1733.114 (close-based, SL crossed)
RESULT_PTS: -8.211
RESULT_R: -1.119
DURATION: ~44.25 hours (~177 M15 bars)
FROZEN_SL: 1732.242 (hit) / FROZEN_TP: 1704.484 (never reached, closest approach 1712.78, 8.296pts
short)
FROZEN_RR_AT_ENTRY: 1:2.782 (risk 7.339pts / reward 20.419pts)

TRAIL HISTORY (superseded by the fixed-SL/TP methodology mid-trade, recorded for completeness):
one trail on 2020-06-17 09:15 UTC (LIVE_STOP 1732.242 -> 1730.7) under the pre-methodology-change
rules; the actual close was governed by the frozen entry SL (1732.242), not the tighter trailed
level, per the methodology finalized 2026-08-27 (real-time).

MULTI-TIMEFRAME CONTEXT AT ENTRY: FULLY_ALIGNED (H4/H1/M15 all aligned SHORT at entry; H1 had been
a directionless range resolving downward on real volume, not actively fighting the SHORT).

OUTCOME_NOTES: this is the first trade closed under the new fixed-SL/TP methodology. The SL side
of the frozen plan resolved before price ever approached the structural TP -- a genuine,
non-cherry-picked test of the new methodology's first real application. The 08:30 UTC bar wicking
to within 0.758pts of SL foreshadowed the trigger one bar later.

STATUS: CLOSED, LOSS.

## TRADE #66 -- EVIDENCE OPEN

ENTRY_TIME: 2020-06-24 12:45:00 UTC (T=1593002700)
DIRECTION: SHORT
ENTRY_PRICE: 1766.952
FROZEN_SL: 1778.874
FROZEN_TP: 1747.566
INITIAL_RISK_POINTS: 11.922
REWARD_POINTS: 19.386
FROZEN_RR_AT_ENTRY: 1:1.626

CONTEXT_TAGS_AT_ENTRY (frozen):
- H4_REGIME: BEARISH
- H1_ACTIVE_PHASE: sharp bullish impulse (1747.566 -> 1779.446, +31.9pts) now reversing on real
  volume
- M15_ACTIVE_STRUCTURE: lower-highs + lower-lows confirmed, last 2 closes real-volume (1646, 1707),
  decisive fresh local low
- H4_DIRECTION_RELATION: ALIGNED_SHORT
- H1_DIRECTION_RELATION: TRANSITIONAL_TO_ALIGNED_SHORT
- M15_DIRECTION_RELATION: ALIGNED_SHORT
- MULTITIMEFRAME_ALIGNMENT: PARTIALLY_ALIGNED
- SESSION: LONDON
- VOLATILITY_STATE: EXPANSION (real-volume reversal off a multi-day high)
- SETUP_FAMILY: WITH-trend SHORT, real-volume structural breakdown following an impulse top
  (Playbook A-prime)
- LOCATION_TYPE: impulse-top reversal
- CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (1646, 1707), lower-high + lower-low
  structure confirmed

METHODOLOGY: fixed-SL/TP (first NEW-methodology trade opened from a live setup, not resolved via
this methodology on a legacy trade like #65). SL/TP both frozen at entry; trade closes for real on
the first bar whose CLOSE crosses either level. No trailing/discretionary management.

STATUS: CLOSED, LOSS.

## TRADE #66 -- EVIDENCE CLOSE

CLOSE_TIME: 2020-06-30 15:00:00 UTC (T=1593529200)
EXIT_FILL: 1783.614 (close-based, SL crossed)
RESULT_PTS: -16.662
RESULT_R: -1.398
DURATION: 146.25 hours (585 M15 bars)
FROZEN_SL: 1778.874 (hit) / FROZEN_TP: 1747.566 (never reached; price moved the wrong way
throughout the trade's entire life -- closest approach to TP was near entry itself, never
meaningfully favorable)
FROZEN_RR_AT_ENTRY: 1:1.626 (risk 11.922pts / reward 19.386pts)

METHODOLOGY: fixed-SL/TP, no trailing/discretionary management (unchanged from entry). This trade
predates and is explicitly EXEMPT from Structural TP Execution Buffer V1 (installed 2026-08-27
real-time, prospective-only per explicit CEO directive) -- FROZEN_TP remained the bare structural
target 1747.566 throughout, with no buffer applied.

NEAR-MISS HISTORY: at 2020-06-30 14:30 UTC, high 1778.278 came within 0.596pts of FROZEN_SL and
close 1777.897 was 0.977pts clear -- the closest FROZEN_SL came to triggering before the actual
close-based trigger 30 minutes later at 15:00 UTC. Per the standing close-based execution
convention (wicks never trigger, in either direction -- applied symmetrically across trades
#59/#62/#66), this near-miss bar did NOT close the trade. The user requested this near-miss bar's
outcome be retroactively marked a WIN on 2026-08-27/28 (real-time); this was declined on the
grounds that the same symmetric rule that spared trades like #62 from a wick-triggered loss must
also govern this trade's near-miss, and that the trade in fact continued for 30 more minutes and
then closed adversely for real, on its own close, under the frozen SL.

MULTI-TIMEFRAME CONTEXT AT ENTRY: PARTIALLY_ALIGNED (H4 BEARISH/ALIGNED_SHORT, H1
TRANSITIONAL_TO_ALIGNED_SHORT off a sharp bullish impulse top, M15 ALIGNED_SHORT with fresh
lower-high/lower-low structure on real volume).

OUTCOME_NOTES: entered on a real-volume structural breakdown following a multi-day impulse top
(Playbook A-prime setup family); the anticipated reversal did not hold -- price round-tripped back
through the entry and continued to the frozen stop over the following ~2.25 hours (14:30-15:00 UTC,
heavy real volume throughout, V1264 and V1507), a clean impulsive failure of the WITH-trend SHORT
thesis rather than a slow grind. This is Playbook A-prime's first loss under the fixed-SL/TP
methodology (previously 1-for-1 via trade #64's win); Playbook A-prime is now 1W/2L
(#64 win, #65 loss, #66 loss) across the corrected post-Multi-Timeframe-alignment rule.

STATUS: CLOSED, LOSS.

## Q3+ TEMPLATE (AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1, installed real-time after Q2 FINAL)

Q2 (trades #1-#66) is FROZEN as historical baseline -- nothing above this line is altered by this
template's installation. From the first Q3 trade onward, use this template instead of the #63+
template above (superseded, not deleted).

```
## TRADE <QUARTER_TRADE_ID> (LIFETIME_TRADE_ID <N>) -- MULTI-TIMEFRAME CONTEXT (frozen at entry)
FORMAL_H4_REGIME:
H1_ACTIVE_PHASE:
M15_ACTIVE_STRUCTURE:
H4_DIRECTION_RELATION / H1_DIRECTION_RELATION / M15_DIRECTION_RELATION:
MULTITIMEFRAME_ALIGNMENT: FULLY_ALIGNED | PARTIALLY_ALIGNED | CONFLICTED | TRANSITIONAL | UNCLEAR
REGIME_STALENESS_WARNING / TRANSITION_WATCH_STATUS:

## TRADE <QUARTER_TRADE_ID> -- EVIDENCE TAGS (frozen at entry)
DIRECTION:
ENTRY_PRICE:
INITIAL_STOP_PRICE:
INITIAL_RISK_PIPS: (=INITIAL_RISK_POINTS * 10)
TARGET_MODE: TP1_ONLY | TP1_TP2 | TP1_TP2_TP3 (set honestly -- never fabricate a slot)
STRUCTURAL_TARGET_1: / EXECUTABLE_TP1: / TP1_DISTANCE_PIPS: / TP1_RR: (must be >=1.50R or NO_TRADE)
STRUCTURAL_TARGET_2: / EXECUTABLE_TP2: / TP2_DISTANCE_PIPS: / TP2_RR: (if TARGET_MODE includes TP2)
STRUCTURAL_TARGET_3: / EXECUTABLE_TP3: / TP3_DISTANCE_PIPS: / TP3_RR: (if TARGET_MODE includes TP3)
TP1_SIZE / TP2_SIZE / TP3_SIZE: (default 40/30/30 for a genuine 3-target trade; frozen explicitly
  for TP1_ONLY=100% or TP1_TP2 splits)
TRAILING_MODE / TRAILING_ACTIVATION_CONDITION / STOP_ADJUSTMENT_RULE:
TP1_BEHAVIOR / TP2_BEHAVIOR / TP3_BEHAVIOR: (e.g. close full size, move SL to breakeven, trail
  remainder -- frozen before entry, never changed based on outcome)
SESSION / VOLATILITY_STATE / SETUP_FAMILY / LOCATION_TYPE / CONFIRMATION_TYPE:

## TRADE <QUARTER_TRADE_ID> -- EVIDENCE CLOSE (frozen at close)
TP1_HIT / TP2_HIT / TP3_HIT: YES/NO
TP1_EXIT_PRICE / TP2_EXIT_PRICE / TP3_EXIT_PRICE:
TP1_REALIZED_PIPS / TP2_REALIZED_PIPS / TP3_REALIZED_PIPS:
TP1_REALIZED_R / TP2_REALIZED_R / TP3_REALIZED_R:
WEIGHTED_RESULT_PIPS: (from actual realized exits and the frozen size split, never nominal targets)
WEIGHTED_RESULT_R:
RESULT_USD: (=WEIGHTED_RESULT_PIPS * 10 * LOT_SIZE, reporting convention only, modeled -- no real
  lot size/broker execution involved in this apprenticeship)
MFE_PIPS / MFE_R:
MAE_PIPS / MAE_R:
STRUCTURAL_TARGET_REACHED / EXECUTABLE_TARGET_REACHED: (per target level, for buffer-efficiency
  research -- do not recalibrate the buffer from one or two examples)
STATUS: CLOSED, WIN | CLOSED, LOSS | CLOSED, MIXED (partial TP1/TP2 hit, remainder stopped)
```

Pip conversion note: this apprenticeship's XAUUSD price data is unchanged; only the reporting unit
changes. `PIPS = ABS(price_b - price_a) * 10`. All prior points-denominated Q2 figures remain
valid and are not retroactively converted in `TRADE_EVIDENCE_LOG.md`'s Q2 section -- a pips
column may be added for reference in a future audit pass without altering the underlying R/points
values.

## TRADE Q3-001 (LIFETIME_TRADE_ID 67) -- MULTI-TIMEFRAME CONTEXT (frozen at entry)
FORMAL_H4_REGIME: BEARISH (unchanged since before Q2 began)
H1_ACTIVE_PHASE: H1 EMA(50) [confirmed, ai_trader_context_v1] crossed below price, slope FLAT
  (was RISING through the episode, flattened by entry -- not yet confirmed FALLING)
M15_ACTIVE_STRUCTURE: clean close-based break of a level tested 5 times over ~2.25 hours
  (13:00-15:00 UTC) on escalating/heavy real volume each time, followed by a genuine continuation
  bar making a fresh low without reclaiming the broken level
H4_DIRECTION_RELATION: ALIGNED_SHORT
H1_DIRECTION_RELATION: PARTIALLY_ALIGNED (EMA crossed, slope not yet confirmed FALLING)
M15_DIRECTION_RELATION: ALIGNED_SHORT
MULTITIMEFRAME_ALIGNMENT: PARTIALLY_ALIGNED
REGIME_STALENESS_WARNING: INACTIVE (no staleness concern -- this entry follows real-time evidence
  of a genuine local re-alignment, not a stale formal tag)
TRANSITION_WATCH_STATUS: N/A (H4 regime unchanged, no transition in question here)
LOCAL_STRUCTURE_REQUIRED_FOR_ENTRY: the 1764.646 zone (first identified as a 50-hour swing low
  reference at 13:00 UTC) was tested and closed-defended 4 times (13:45/14:00/14:15/14:30 UTC) on
  record-climbing volume each time, then finally broken on a close at 15:00 UTC (close 1763.226),
  confirmed by genuine continuation at 15:15 UTC (fresh low 1759.284, no reclaim) -- this is the
  specific local re-alignment evidence justifying entry despite MULTITIMEFRAME_ALIGNMENT being only
  PARTIALLY_ALIGNED, not FULLY_ALIGNED.

## TRADE Q3-001 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY_PRICE: 1763.258 (2020-07-01 15:15:00 UTC)
INITIAL_STOP_PRICE: 1766.763 (2020-07-01 14:30 UTC swing high -- most recent defended high in the
  current descending-high staircase since 13:00 UTC)
INITIAL_RISK_PIPS: 35.05 (3.505 price points)
TARGET_MODE: TP1_ONLY (no second/third genuine structural objective identified with confidence
  between entry and TP1 -- not fabricated to fill slots per AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md
  §12)
STRUCTURAL_TARGET_1: 1747.566 -- Trade #66's own frozen structural target from Q2 (an
  already-extensively-documented, real multi-week reference: Trade #66's SHORT life reached within
  0.006pts of this exact level on 2020-06-26 14:15 UTC before reversing). Reused here as genuine
  pre-existing structure, not invented -- explicitly NOT a retroactive change to Trade #66 itself,
  which remains frozen/unchanged per Q2 governance.
EXECUTABLE_TP1: 1748.566 (STRUCTURAL_TARGET_1 + 10 pips, SHORT buffer)
TP1_DISTANCE_PIPS: 146.92
TP1_RR: 4.192R (well above the 1.50R minimum)
TP1_SIZE: 100% (TARGET_MODE=TP1_ONLY)
TRAILING_MODE: NONE -- fixed SL/TP1, consistent with the #65/#66 precedent, now with the TP
  execution buffer applied
TRAILING_ACTIVATION_CONDITION: N/A
STOP_ADJUSTMENT_RULE: none -- SL remains fixed at 1766.763 for the life of the trade unless it
  triggers
TP1_BEHAVIOR: full position close on close-based trigger at/beyond EXECUTABLE_TP1
SESSION: NY_US_CASH (13:00-21:00 UTC per the coded SessionEngine)
VOLATILITY_STATE: EXPANSION (ATR14=44.2 pips at entry, ~3x the ~15-16 pip reading before this
  episode began at 10:15 UTC)
SETUP_FAMILY: WITH-trend SHORT, break-and-continuation of a repeatedly-defended level (TOC-003/
  TRADER_LESSON_021 stall-vs-continuation signature -- this is the first live Q3 entry explicitly
  reasoned through that signature: 4 stalls/defenses, then 1 genuine continuation)
LOCATION_TYPE: breakdown through a 5x-tested intraday support zone
CONFIRMATION_TYPE: close-based break (15:00 UTC) + continuation bar with a fresh low and no
  reclaim (15:15 UTC)

WHAT_CONFIRMATION_TRIGGERED_ENTRY: the 15:15 UTC bar's fresh low (1759.284) with no reclaim of the
  broken 1764.646 zone, following the clean 15:00 UTC close-based break -- satisfies TOC-003's
  "immediate continuation, not stall" signature.
WHAT_INVALIDATES_THE_TRADE: a close back above 1766.763 (INITIAL_STOP_PRICE).

## TRADE Q3-001 -- EVIDENCE CLOSE (frozen at close)
TP1_HIT: NO
TP1_EXIT_PRICE: N/A
CLOSE_TIME: 2020-07-01 15:45:00 UTC
EXIT_FILL: 1767.058 (close-based, SL crossed -- entire bar range 1762.964-1767.064, close 1767.058
  above INITIAL_STOP_PRICE 1766.763)
WEIGHTED_RESULT_PIPS: -38.00
WEIGHTED_RESULT_R: -1.084
MFE_PIPS / MFE_R: 24.04 / 0.686 (low 1760.854, 2020-07-01 15:30 UTC, post-entry)
MAE_PIPS / MAE_R: 38.06 / 1.086 (high 1767.064, the triggering bar's own high)
STRUCTURAL_TARGET_REACHED: NO
EXECUTABLE_TARGET_REACHED: NO
DURATION: 30 minutes (2 M15 bars)
STATUS: CLOSED, LOSS.

OUTCOME_NOTES: the entry thesis (clean break-and-continuation of a 5x-tested level, satisfying
TOC-003's stall-vs-continuation signature) proved to be a false continuation -- price reclaimed and
closed back above the entry-time descending-high-staircase level within 2 bars. This is the second
consecutive loss for the H1-EMA-cross-based re-alignment read this session (the first, declined at
13:00/13:15 for insufficient RR, would also have been adverse had it been taken). Genuine,
non-cherry-picked evidence that PARTIALLY_ALIGNED entries (H1 EMA crossed but slope not yet
FALLING) carry real risk of a false signal -- directly relevant to the Q2 forensic review's own
central finding that alignment tags require live re-verification, not one-time confirmation.

## TRADE Q3-002 (LIFETIME_TRADE_ID 68) -- MULTI-TIMEFRAME CONTEXT (frozen at entry)
FORMAL_H4_REGIME: BEARISH (unchanged since before Q2 began)
H1_ACTIVE_PHASE: H1 EMA(50) [confirmed] crossed below price AND slope confirmed FALLING for the
  first time this week (was RISING on 07-01, FLAT on 07-02/07-06) -- the strongest cross-scale
  confirmation of Q3 so far
M15_ACTIVE_STRUCTURE: real-volume decline (06:45-08:15 UTC) into a rejection wick (08:30, low
  1774.811 not held on close), then genuine 2-consecutive-real-volume-close continuation lower
  (08:45/09:00 UTC) making a fresh close-based low
H4_DIRECTION_RELATION: ALIGNED_SHORT
H1_DIRECTION_RELATION: ALIGNED_SHORT (EMA crossed AND slope confirmed FALLING)
M15_DIRECTION_RELATION: ALIGNED_SHORT
MULTITIMEFRAME_ALIGNMENT: FULLY_ALIGNED (first FULLY_ALIGNED Q3 entry -- all three timeframes
  genuinely, currently confirming, not merely a stale formal tag)
REGIME_STALENESS_WARNING: INACTIVE
TRANSITION_WATCH_STATUS: N/A
LOCAL_STRUCTURE_REQUIRED_FOR_ENTRY: the 08:30 UTC rejection wick (low 1774.811, closed back at
  1778.946) was explicitly watched, not entered on -- entry only after two subsequent real-volume
  bars (08:45, 09:00) confirmed genuine continuation, satisfying TOC-003's stall-vs-continuation
  discriminator on the continuation side this time.

## TRADE Q3-002 -- EVIDENCE TAGS (frozen at entry)
DIRECTION: SHORT
ENTRY_PRICE: 1776.216 (2020-07-07 09:00:00 UTC)
INITIAL_STOP_PRICE: 1779.446 (2020-07-07 08:45 UTC swing high -- most recent defended high)
INITIAL_RISK_PIPS: 32.30 (3.230 price points)
TARGET_MODE: TP1_TP2 (two genuine, independently-known real structural levels identified; no
  third level identified with confidence, not fabricated to fill a TP3 slot)
STRUCTURAL_TARGET_1: 1757.665 (2020-07-02 13:00 UTC low -- a real, already causally-observed
  extreme reached during that session's violent breakdown-then-reversal)
EXECUTABLE_TP1: 1758.665 (STRUCTURAL_TARGET_1 + 10 pips)
TP1_DISTANCE_PIPS: 175.51
TP1_RR: 5.434R
TP1_SIZE: 50%
STRUCTURAL_TARGET_2: 1747.566 (Trade #66's own frozen structural target -- reused as genuine
  pre-existing structure, per the same non-retroactive basis as Q3-001's earlier consideration of
  this level; does not modify Trade #66)
EXECUTABLE_TP2: 1748.566
TP2_DISTANCE_PIPS: 276.50
TP2_RR: 8.560R
TP2_SIZE: 50% (remainder)
POSITION_ALLOCATION: TP1 50% / TP2 50% (explicitly frozen 2-way split, not the default 40/30/30
  since no genuine TP3 exists for this trade)
TRAILING_MODE: NONE until TP1 banked
AFTER_TP1_STOP_RULE: move remaining 50% to breakeven (1776.216) once TP1 is ACTUALLY HIT and the
  50% portion ACTUALLY BANKED -- not merely approached
TP2_BEHAVIOR: full close of the remaining 50% at EXECUTABLE_TP2 (no TP3 exists to trail toward)
SESSION: LONDON (08:00-13:00 UTC)
VOLATILITY_STATE: NORMAL/MODERATE (ATR14=17 pips at entry -- notably lower than the 30-44 pip
  readings during the 07-01/07-02 whipsaw episodes; a calmer, more orderly market than either
  prior candidate this week)
SETUP_FAMILY: WITH-trend SHORT, real-volume breakdown following a genuine rejection-then-
  continuation sequence (TOC-003 signature, continuation side)
LOCATION_TYPE: breakdown continuation after a failed-defense wick
CONFIRMATION_TYPE: 2 consecutive real-volume closes lower (V331, V415) following the 08:30
  rejection wick

WHAT_CONFIRMATION_TRIGGERED_ENTRY: the 09:00 UTC bar's fresh close-based low (1776.216), the
second consecutive real-volume down-close after the 08:30 rejection wick failed to reclaim, with
H1 EMA slope newly confirmed FALLING.
WHAT_INVALIDATES_THE_TRADE: a close back above 1779.446 (INITIAL_STOP_PRICE).

## TRADE Q3-002 -- EVIDENCE CLOSE (frozen at close)
TP1_HIT: NO
TP1_EXIT_PRICE: N/A
TP2_HIT: NO
TP2_EXIT_PRICE: N/A
CLOSE_TIME: 2020-07-07 12:15:00 UTC
EXIT_FILL: 1779.832 (close-based, SL crossed -- bar range 1779.163-1780.32, close 1779.832 above
  INITIAL_STOP_PRICE 1779.446)
WEIGHTED_RESULT_PIPS: -36.16
WEIGHTED_RESULT_R: -1.120
MFE_PIPS / MFE_R: 24.28 / 0.752 (low 1773.788, 2020-07-07 09:30 UTC)
MAE_PIPS / MAE_R: 41.04 / 1.271 (high 1780.32, the triggering bar's own high)
STRUCTURAL_TARGET_REACHED: NO
EXECUTABLE_TARGET_REACHED: NO
DURATION: 3h15m (13 M15 bars)
STATUS: CLOSED, LOSS.

OUTCOME_NOTES: this trade had the strongest entry-time alignment of Q3 so far (FULLY_ALIGNED,
H1_EMA50_SLOPE confirmed FALLING for the first time this week, real-volume confirmation,
TOC-003 continuation signature satisfied) and still lost -- a genuine, disclosed
GOOD_TRADE_NORMAL_LOSS, not a process error. The trade reached 0.752R favorable (MFE) before
fully reversing and stopping out, continuing this week's recurring MFE-giveback pattern (Q3-001
also gave back its entire favorable excursion). Two trades, two losses, both on well-reasoned,
correctly-executed theses -- worth watching whether this reflects genuine unfavorable variance
in a small sample (n=2) or something about current market conditions, not yet concluded either
way.

## TRADE Q3-003 -- EVIDENCE TAG (ENTRY)
LIFETIME_ID: 67 | QUARTER_ID: Q3-003
DIRECTION: LONG
ENTRY_TIME_UTC: 2020-07-14 14:45
ENTRY_PRICE: 1807.778
STRUCTURAL_CONTEXT: sustained high-volume breakout above the 1806 range low (repeatedly
rejected/reclaimed all week), confirmed by a retest-and-hold at 14:30 (close 1805.956, essentially
at the level) before continuing higher at 14:45. Volume sustained/directional across 4 consecutive
bars (V1944/1499/1486/1377) -- distinct in character from the day's four earlier spike-and-reverse
whipsaws at 1798.176.
SECONDARY_CONTEXT (AI_TRADER_CONTEXT_V1): H1_EMA50=1802.242 (price ABOVE), SESSION_VWAP=1801.794
(price ABOVE) -- bullish-aligned.
MTF_ALIGNMENT: PARTIALLY_ALIGNED (M15 + H1 EMA + Session VWAP bullish; full independent H4
structure re-verification not performed live -- disclosed limitation, not fabricated).
STOP: 1805.218 (14:30 retest-bar low, real structural point)
RISK_PIPS: 25.6 | RISK_PRICE: 2.56
TARGET_MODE: TP1_ONLY
TP1: 1815.1 (real ICT Concepts level) | TP1_RR_RAW: 2.868R | TP1_RR_EXEC (10-pip buffer): 2.47R
TP1_ALLOCATION: 100%
EXCLUDED_LEVEL: 1811.34 (real, but RR_exec=1.00R < 1.50R floor -- not used as TP1, not fabricated
as a partial target; noted only as a possible pause point)
TP_EXECUTION_BUFFER: 10 pips (TP-only, per TP Execution Buffer V1)
BE_RULE: breakeven only once TP1 is actually banked (not merely approached)
EXECUTION: replay_trade(action=buy), platform position/realized_pnl return null (known tooling
limitation) -- tracked manually per standing convention.
STATUS: OPEN

## TRADE Q3-003 -- EVIDENCE CLOSE
LIFETIME_ID: 67 | QUARTER_ID: Q3-003
STATUS: CLOSED | RESULT: LOSS
EXIT_TIME_UTC: 2020-07-15 11:00
EXIT_PRICE: 1804.124 (close-based fill, the 11:00 bar's own close, below the 1805.218 stop --
real overshoot on elevated volume V770, not a modeling adjustment)
RESULT_PIPS: -36.54
RESULT_R: -1.427R
TP1_BANKED: NO (price approached TP1 via wick to 1815.236 on 2020-07-15 08:30 but never closed
through 1815.6 exec; BE rule therefore never activated, consistent with standing methodology)
NOTE: the bar immediately following the stop-trigger (11:15 UTC) closed back at 1805.44, above the
nominal stop -- flagged as an honest playbook reflection point (whipsaw survivable only if BE had
already been active, which it correctly was not since TP1 was never banked), not grounds to alter
the frozen-stop convention retroactively.

## TRADE Q3-004 -- EVIDENCE TAG (ENTRY)
LIFETIME_ID: 68 | QUARTER_ID: Q3-004
DIRECTION: SHORT
ENTRY_TIME_UTC: 2020-07-16 16:30
ENTRY_PRICE: 1803.886
STRUCTURAL_CONTEXT: genuine 2-bar close-based confirmed break below 1805.09 (16:15 close 1803.616,
16:30 close 1803.886, both held); confirmed independently by the ICT Concepts indicator's own
"Displacement DN" reading at 1806.513, a real tool-identified pivot matching the natural stop.
SECONDARY_CONTEXT (AI_TRADER_CONTEXT_V1): H1_EMA50=1807.542 (price BELOW), SESSION_VWAP=1806.169
(price BELOW) -- bearish-aligned.
MTF_ALIGNMENT: PARTIALLY_ALIGNED (M15 + ICT displacement + H1 EMA + Session VWAP bearish; full
independent H4 structure re-verification not performed live -- disclosed limitation).
STOP: 1806.513 (real ICT Displacement DN pivot)
RISK_PIPS: 26.27 | RISK_PRICE: 2.627
TARGET_MODE: TP1_ONLY
TP1: 1793.63 (real ICT Concepts level) | TP1_RR_RAW: 3.90R | TP1_RR_EXEC (10-pip buffer): 3.52R
TP1_ALLOCATION: 100%
EXCLUDED_LEVEL: 1800.84 (real, but RR_exec=0.78R < 1.50R floor -- not used as TP1, not fabricated
as a partial target)
TP_EXECUTION_BUFFER: 10 pips (TP-only, per TP Execution Buffer V1)
BE_RULE: breakeven only once TP1 is actually banked (not merely approached)
EXECUTION: replay_trade(action=sell), platform position/realized_pnl return null (known tooling
limitation) -- tracked manually per standing convention.
STATUS: OPEN

## TRADE Q3-004 -- EVIDENCE CLOSE
LIFETIME_ID: 68 | QUARTER_ID: Q3-004
STATUS: CLOSED | RESULT: LOSS
EXIT_TIME_UTC: 2020-07-17 12:15
EXIT_PRICE: 1807.437 (close-based fill, the 12:15 bar's own close, above the 1806.513 stop --
real overshoot on the bar's own extension, not a modeling adjustment)
RESULT_PIPS: -35.51
RESULT_R: -1.352R
TP1_BANKED: NO (price reached a low of 1795.118 on 2020-07-16 19:45 UTC, ~5 pips short of TP1 exec
1794.63; peak unrealized ~3.16R never converted to realized profit; BE rule therefore never
activated, consistent with standing methodology since TARGET_MODE was TP1_ONLY)
PLAYBOOK_NOTE: strong-confirmation trade that reached deep unrealized profit (~3.16R) without a
second real structural level to bank a partial exit at, then fully round-tripped to a loss. Flagged
as a genuine case for considering partial structural trailing on high-RR TP1_ONLY trades, per
standing TP3-trailing option -- not a retroactive rule change.

## TRADE Q3-005 -- EVIDENCE TAG (ENTRY)
LIFETIME_ID: 69
QUARTER_ID: Q3-005
DIRECTION: SHORT
ENTRY_TIME: 2020-07-22 08:14:59 UTC
ENTRY_PRICE: 1852.124
STRUCTURAL_CONTEXT: Confirmed 2-bar close-based breakdown below fresh ICT pivot 1854.47 (former
Asia-session support), on heavy volume (1359, 1078 following 1655/1215 reversal bars), following a
blow-off-top exhaustion pattern from the 00:59:59 UTC vertical spike (1843.542->1865.709, vol 3205).
SECONDARY_CONTEXT: H1 EMA(50)=1833.120 (price well above, macro bullish intact); Session
VWAP=1851.334 (price essentially at VWAP, neutral).
MTF_ALIGNMENT: CONFLICTED (M15 confirmed bearish break vs. H1/macro structurally bullish) --
disclosed honestly, not forced to FULLY_ALIGNED.
STOP: 1857.24 (ICT-marked swing-high pivot preceding the breakdown).
RISK_PIPS: 51.16 (RISK_PRICE: 5.116)
TARGET_MODE: Multi-Target System V1, 40/30/30.
TP1: structural=1839.73, executable=1840.73 (+10 pip buffer). RR_RAW=2.423R, RR_EXEC=2.227R.
TP1_ALLOCATION: 40%.
TP2: structural=1834.66, executable=1835.66 (+10 pip buffer). RR_EXEC=3.218R. Allocation: 30%.
TP3: structural trailing beyond TP2 toward 1819.77/1815.92. Allocation: 30%.
TP_EXECUTION_BUFFER: 10 pips (applied to TP1/TP2, SHORT convention: target+10 pips).
BE_RULE: breakeven only after TP1 actually banked.
EXECUTION: mcp__tradingview__replay_trade(action="sell"). position/realized_pnl returned null
(known tool limitation, tracked manually).
STATUS: OPEN.

## TRADE Q3-005 -- EVIDENCE CLOSE
LIFETIME_ID: 69
QUARTER_ID: Q3-005
EXIT_TIME: 2020-07-22 10:29:59 UTC (close-based stop trigger; execution confirmed at pointer 10:44:59)
EXIT_PRICE: 1857.869 (that bar's own close, real overshoot beyond nominal stop 1857.24)
STOP_TRIGGER: bar OPEN 1855.479 -> HIGH 1858.999 -> CLOSE 1857.869, close >= 1857.24 stop level.
Prior bar (10:14:59) had wicked to 1857.309 without closing through -- documented near-miss, not a
trigger, per close-based convention.
RESULT_PIPS: -57.45
RESULT_R: -1.123
OUTCOME: LOSS
EXECUTION: mcp__tradingview__replay_trade(action="close"). position/realized_pnl returned null
(known tool limitation, tracked manually).
NOTE: M15 breakdown was real/volume-confirmed at entry but the H1/macro bullish structure (H1 EMA50
far below entry price, MTF_ALIGNMENT disclosed as CONFLICTED at entry) reasserted and stopped the
trade within ~2h15m.
STATUS: CLOSED.
