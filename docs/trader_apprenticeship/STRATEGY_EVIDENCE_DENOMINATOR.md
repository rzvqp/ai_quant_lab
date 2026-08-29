# Strategy Evidence Denominator (Evidence Upgrade V1)

ERRATUM NOTE: every "2020-05-27" clock time in this file from "13:45 UTC" onward through trade
#57's entry is 15 minutes LATER than the true UTC time (self-discovered labeling slip, root cause
and corrected reference times in 2020_Q2_H4_LOG.md's ERRATUM entry; underlying data/decisions
unaffected). Subtract 15 minutes from any such label below to get the true time.

Tracks each developing playbook's full occurrence set — not just the subset that
became trades — so no pattern is judged only from its winners or only from the trades
actually taken. See `EVIDENCE_UPGRADE_METHODOLOGY_V1.md` §4 for governance. Counts below
are seeded from directly-observed evidence already logged in this session's window of
`2020_Q2_H4_LOG.md`; pre-window trades (#47, #49, #50 — the other countertrend-LONG
losses referenced in memory) are excluded pending the same full-portfolio backfill noted
in the methodology doc, not fabricated into these counts.

METHODOLOGY NOTE (CEO correction, 2020-06-08, prospective only): "Playbook A" below (trades
#51-#62) predates the Multi-Timeframe Trend Alignment V1 correction and remains a single pooled
WITH-trend bucket — NOT retroactively split, per governance (no rewriting of historical
labels/P&L). Trades #63 onward will be tracked in separate FULLY_ALIGNED_SHORTS /
PARTIALLY_ALIGNED_SHORTS / CONFLICTED_SHORTS / TRANSITIONAL_SHORTS buckets (and the LONG
equivalents) as new sections below, per the MULTITIMEFRAME_ALIGNMENT frozen at each future entry
in TRADE_EVIDENCE_LOG.md. The multi-timeframe audit of trades #58-#62 (all FULLY_ALIGNED at the
immediate/local level captured by their original tags) is in TRADE_EVIDENCE_LOG.md's "MULTI-
TIMEFRAME ALIGNMENT AUDIT" section — not reflected as a structural change here since it doesn't
change which bucket those trades belong to.

## Playbook A: WITH-trend SHORT (2 consecutive real-volume ~2000+ closes lower, BEARISH H4, no elevated evidence bar required)

- QUALIFYING_OCCURRENCES (2-bar real-volume sequences meeting the standard, this window): 11
- TRADES_TAKEN: 11 (#51, #52, #54, #55, #56, #57, #58, #59, #60, #61, #62)
- TRADES_DECLINED: 0 (no fully-qualifying WITH-trend sequence was seen and passed on this
  window — every one that reached 2-bar real-volume confirmation was taken)
- WINS: 4 (#51 +22.386, #55 +3.256, #56 +5.857, #58 +12.259)
- LOSSES: 7 (#52 -1.743, #54 -7.834, #57 -6.192, #59 -0.654, #60 -8.948, #61 -12.237, #62 -8.342)
- OPEN: 0
- CORRECT_NO_TRADES: n/a (none declined)
- INCORRECT_NO_TRADES / MISSED_OPPORTUNITIES: 1 (2020-06-10 14:45/15:00 UTC, real-volume 6491/5558
  down-close pair, qualifying WITH-trend SHORT sequence not evaluated in real time -- attention was
  on closing trade #63; no retroactive entry taken per no-hindsight governance, logged honestly)
- COUNTEREXAMPLES: several bar-1-only real-volume attempts that never reached 2-bar
  confirmation (e.g. 2020-05-25 13:45/13:45 UTC single-bar, 2020-05-26 13:30/14:00 UTC
  broken by a massive up-close reversal, 2020-05-27 13:45 UTC ambiguous absorption bar) —
  tracked as ATTEMPTED_BUT_NOT_CONFIRMED, not as declines, since the playbook's own
  2-bar test was never satisfied.

## Playbook B: Countertrend LONG (2 consecutive real-volume ~2000+ closes higher, against BEARISH H4, requires evidence genuinely stronger than trade #53's failed 3544/5373 sequence)

- QUALIFYING_OCCURRENCES (2-bar real-volume sequences meeting the standard 2-bar test,
  regardless of whether they cleared the elevated bar): 21
- TRADES_TAKEN: 2 (#53, sequence 3544/5373 — lost; #63, sequence 5674/6544 — the first sequence
  to actually CLEAR #53's benchmark on both legs, entered 2020-06-08 14:15 UTC, CLOSED 2020-06-10
  14:45 UTC, WIN +2.306R. Classified TRANSITIONAL LONG under Multi-Timeframe Trend Alignment V1,
  not a bare "countertrend" label — see TRADE_EVIDENCE_LOG.md)
- TRADES_DECLINED: 19, all correctly declined per the elevated-evidence-bar policy for
  falling short of #53's own benchmark:
  - 2020-06-15 14:15/14:30 UTC: 2588/3355 (weaker on both legs; part of a 4-bar real-volume
    recovery off the 13:30 UTC low)
  - 2020-06-15 14:00/14:15 UTC: 3057/2588 (weaker on both legs)
  - 2020-06-15 13:45/14:00 UTC: 3391/3057 (leg1 narrowly short of 3544, leg2 well short of 5373)
  - 2020-06-15 12:45/13:00 UTC: 2909/2688 (weaker on both legs; test-and-defend of a fresh
    multi-week low, 1705.038, structurally similar to trade #63's qualifying setup but on
    materially weaker volume -- held to the same standard)
  - 2020-06-12 13:15/13:30 UTC: 2936/3802 (weaker on both legs vs. 3544/5373)
  - 2020-06-12 13:00/13:15 UTC: 3628/2936 (leg1 clears 3544, leg2 short of 5373)
  - 2020-06-12 12:15/12:30 UTC: 3075/4348 (weaker on both legs vs. 3544/5373)
  - 2020-06-11 16:45/17:00 UTC: 6281/3655 (leg1 decisively clears 3544, leg2 well short of 5373 --
    strongest entry leg of any declined sequence yet, still correctly declined on the confirming leg)
  - 2020-06-11 12:45/13:00 UTC: 2632/2666 (weaker on both legs; part of a 4-bar real-volume
    reversal off the 11:30 UTC test of a fresh multi-day low, 1721.294)
  - 2020-06-11 12:30/12:45 UTC: 4129/2632 (leg1 clears 3544, leg2 well short of 5373)
  - 2020-06-10 19:30/19:45 UTC: 5190/4704 (leg1 clears 3544, leg2 falls short of 5373; part of
    the same sustained post-FOMC push, narrow miss)
  - 2020-06-10 19:15/19:30 UTC: 4939/5190 (leg1 clears 3544, leg2 5190 falls just short of 5373,
    ~96.6% of it -- narrowest miss of any declined sequence this window)
  - 2020-06-10 19:00/19:15 UTC: 3082/4939 (weaker on both legs vs. #53's 3544/5373; occurred
    during sustained post-FOMC real-volume continuation -- standing bar not retroactively raised
    despite trade #63's stronger clearing sequence, per governance)
  - 2020-05-19 16:00 UTC: 3845/3793 (weaker on both legs)
  - 2020-05-22 12:00/12:15 UTC: 3041/2080 (weaker on both legs)
  - 2020-05-22 18:00/18:15 UTC: 2107/2056 (weaker on both legs)
  - 2020-05-27 13:30/13:45 UTC (true time, drift-corrected): 2538/4512 (weaker on both
    legs; initially read as an ambiguous single absorption bar, retroactively clarified
    as a genuine 2-bar sequence once the 2nd bar confirmed direction — logged honestly
    rather than smoothed over)
  - 2020-05-28 14:00/14:15 UTC: 5331/2203 (MIXED strength -- first leg stronger than
    #53's, second/confirming leg substantially weaker (~41% of #53's); declined because
    a materially weaker confirming leg is disqualifying regardless of entry-leg strength;
    same honest retroactive-clarification pattern as the 2538/4512 case)
  - 2020-06-01 14:45/15:00 UTC: 3607/2846 (MIXED strength, second such case -- first leg
    stronger than #53's for the first time this window, second/confirming leg razor-thin
    close and well below #53's second leg (~53% of it); declined on both independent
    grounds: ambiguous close AND insufficient confirming-leg volume)
- WINS: 1 (#63, +2.306R / +23.187pts)
- LOSSES: 1 (#53, -0.747)
- ATTEMPTED_BUT_NOT_CONFIRMED (real-volume bar-1 candidates that never reached a clean
  2-bar directional confirmation, so never became qualifying occurrences): 2020-05-27
  14:30 UTC (real vol 4492, up close) -> 14:45 UTC (sub-threshold, essentially sideways)
  -> no pairing; 2020-05-27 15:30 UTC (real vol 4205, up close) -> 15:45 UTC (real vol
  4104, essentially flat close) -> ambiguous, not cleanly confirmed; 2020-05-27 16:15 UTC
  (real vol 4345, strong up close at high, fresh apprenticeship high 1707.869) -> 16:30
  UTC (real vol 4286, down close) -> not confirmed, broken by a pullback; 2020-05-27
  18:15 UTC (real vol 2286, up close, fresh high 1715.386) -> 18:30 UTC (real vol 2005,
  down close) -> not confirmed.
- CORRECT_NO_TRADES: not yet independently verified (declining was consistent with the
  standing policy and each subsequent bar did not show a clean, sustained continuation
  that clearly would have been more profitable than #53's own outcome, but this has not
  been rigorously back-checked against what actually happened after each decline —
  left open for the Q2 checkpoint's adversarial review rather than asserted here)
- INCORRECT_NO_TRADES / MISSED_OPPORTUNITIES: none identified yet
- COUNTEREXAMPLES: n/a yet

## Playbook A-prime: PARTIALLY_ALIGNED_SHORTS (post-Multi-Timeframe-correction, trade #63+)

New bucket per the 2020-06-08 methodology note -- trades #63 onward tracked separately by
MULTITIMEFRAME_ALIGNMENT, not pooled into the pre-correction Playbook A above.

- QUALIFYING_OCCURRENCES: 3
- TRADES_TAKEN: 3 (#64, entered 2020-06-12 14:15 UTC, real-volume rejection 7023/4241 at the
  2020-06-11 whipsaw peak, MULTITIMEFRAME_ALIGNMENT=PARTIALLY_ALIGNED, CLOSED 2020-06-15 00:15 UTC,
  WIN +1.443R -- see TRADE_EVIDENCE_LOG.md and 2020_Q2_H4_LOG.md for full reasoning. First
  WITH-trend SHORT to pass live evaluation under the corrected forward rule -- the rule's first
  test, 2020-06-11 14:00-14:30 UTC, correctly declined a materially weaker signal.
  #65, entered 2020-06-16 12:30 UTC, real-volume continuation 2006/2584 resuming the bearish
  drift after a choppy range, MULTITIMEFRAME_ALIGNMENT=FULLY_ALIGNED (H1 was directionless/ranging
  rather than actively fighting the SHORT), CLOSED 2020-06-18 08:45 UTC, LOSS -1.119R -- entry
  1724.903, frozen SL 1732.242 (hit), frozen TP 1704.484 (never reached, closest approach 1712.78).
  First trade closed under the fixed-SL/TP methodology installed 2026-08-27 real-time -- see
  TRADE_EVIDENCE_LOG.md and 2020_Q2_H4_LOG.md for full computation.
  #66, entered 2020-06-24 12:45 UTC, real-volume structural breakdown 1646/1707 off the 1779.446
  impulse-top high, MULTITIMEFRAME_ALIGNMENT=PARTIALLY_ALIGNED (H1 was in an active bullish
  impulse just broken by this reversal), CLOSED 2020-06-30 15:00 UTC, LOSS -1.398R -- entry
  1766.952, frozen SL 1778.874 (hit), frozen TP 1747.566 (never reached; price never meaningfully
  favored the trade). First trade opened fresh under the fixed-SL/TP methodology. Near-miss at
  2020-06-30 14:30 UTC (high 0.596pts / close 0.977pts clear of frozen SL, heavy real volume)
  did not trigger under the close-based rule; the trade continued live and triggered for real
  30 minutes later on its own close -- see TRADE_EVIDENCE_LOG.md and 2020_Q2_H4_LOG.md for full
  reasoning)
- TRADES_DECLINED: 1 (2020-06-11 14:00-14:30 UTC, bare 2-bar test technically formed but
  trivial-magnitude closes with no rejection context -- correctly declined for lacking genuine
  local bearish re-alignment)
- WINS: 1 (#64, +1.443R / +6.382pts)
- LOSSES: 2 (#65, -1.119R / -8.211pts; #66, -1.398R / -16.662pts)
- OPEN: 0

## Running interpretation (evidence only, not a ratified finding)

Playbook A is now 4/11 (36%, -2.192pts NET NEGATIVE) after trade #62's stopped-out close --
the first time this window's WITH-trend aggregate has gone net negative, on a fifth straight
loss (#59/#60/#61/#62, plus the earlier #57). Trade #62 is itself a remarkable illustration:
its stop (1688.5) was tested four separate times over 5 bars, with THREE distinct wicks
piercing it outright (closest survival margin 0.147pts) before the eventual triggering close
crossed it by just 0.009pts -- yet REALIZED_RESULT_R (-1.001) landed almost exactly at the
nominal -1.0R, a useful counterpoint to trade #60's demonstration of meaningful overshoot:
repeated wick-piercing does not itself imply a large closing overshoot. Combined with trades
#58-#61, this window has now produced the fullest practical demonstration of the
close-based-fill mechanism's entire range: favorable-and-close (#58), sign-flipping (#59),
untrailed-overshoot (#60), wick-survival-then-eventual-break (#61), and
repeated-piercing-yet-near-exact-close (#62). n=11 remains far too small (single trending
quarter, single H4 direction) to validate or invalidate anything -- but the playbook turning
net negative on the SAME setup criteria that produced +27.989pts at its peak (after trade
#58) is itself the clearest demonstration yet of how unstable small-sample aggregates are,
and a genuine reminder not to over-read short streaks in either direction. Playbook B is now
1-for-2 on trades taken (#53 loss -0.747, #63 WIN +2.306R): the elevated-evidence-bar discipline
correctly filtered out 6 declined/non-qualifying sequences this window (4 weaker-on-both-legs, 1
mixed-strength, 1 ambiguous-plus-weak-confirming-leg), and the one sequence that DID clear the bar
(#63, 5674/6544 vs. #53's 3544/5373) went on to a decisive win, surviving six separate wick-tests
across a ~48.5 hour hold before an eventual close-based stop-out on the largest-volume reversal bar
of the trade's life. n=2 remains far too small to validate or invalidate anything -- one data point
consistent with the elevated-bar filter working as intended, not proof of it. Both remain
`NO_VALIDATED_STRATEGY_YET` per the regime matrix.

## Q3 2020 (new quarterly cohort -- all Q2 tallies above are FROZEN and unchanged)

Per AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md, Q3 trades use their own QUARTER_TRADE_ID (Q3-001...)
and are never mixed into Q2 totals. Playbook A-prime and Playbook B's Q2 denominators above remain
exactly as finalized in TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md.

### Playbook A-prime -- Q3 evidence (separate running count, starts at 0)
- QUALIFYING_OCCURRENCES: 1
- TRADES_TAKEN: 0
- TRADES_DECLINED: 1 (2020-07-01 10:15-10:45 UTC: 2 real-volume down-closes technically formed the
  bare pattern, but AI_TRADER_CONTEXT_V1's H1 EMA(50) tripwire showed price still above the
  confirmed H1 EMA -- no genuine H1 re-alignment -- and the very next bar (10:45 UTC, V513)
  reversed on real volume rather than continuing, confirming the stall signature (TOC-003/
  TRADER_LESSON_021). Correctly declined; see 2020_Q3_H4_LOG.md for full reasoning.)

### Playbook A-prime -- Q3 update (Q3-001 resolved)
- TRADES_TAKEN: 1 (Q3-001, entered 2020-07-01 15:15 UTC on the TOC-003 stall-vs-continuation
  signature after a 5x-tested level broke, CLOSED 15:45 UTC, LOSS -1.084R / -38.0 pips)
- WINS: 0 / LOSSES: 1
- Net Q3 so far: -1.084R

### Playbook A-prime -- Q3 update (Q3-002 resolved)
- TRADES_TAKEN: 2 (Q3-001 LOSS -1.084R; Q3-002, entered 2020-07-07 09:00 UTC, FULLY_ALIGNED with
  H1 EMA slope confirmed FALLING -- the strongest entry-time alignment of Q3 so far -- CLOSED
  12:15 UTC, LOSS -1.120R)
- WINS: 0 / LOSSES: 2
- Net Q3 so far: -2.204R / -74.16 pips
- Both losses are GOOD_TRADE_NORMAL_LOSS on well-reasoned, correctly-executed theses -- neither is
  a process error. Both gave back their full favorable excursion (MFE fully surrendered), matching
  the Q2 forensic review's flagged no-partial-capture pattern -- worth watching under the new
  multi-target system once a trade actually reaches TP1.
