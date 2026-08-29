# Trader Strategy Candidates

PERMANENT apprenticeship objective, installed 2020-06-09 (replay time) per CEO DIRECTIVE --
STRATEGY CANDIDATE FORMALIZATION. The apprenticeship's end goal is not only observation and
learning: when a recurring behavior/playbook reaches sufficient forward evidence, it must be
evaluated for promotion to an explicit, falsifiable `TRADER_STRATEGY_CANDIDATE_<ID>`, status
`UNVALIDATED` at creation. Candidate creation is NOT validation -- it means "this market behavior
is now explicit enough to be falsified." Validation is Alpha's job (falsification) and
Statistician/Red Team's job (independent validation) downstream.

## Promotion path

OBSERVATION -> RECURRING_OBSERVATION -> REPEATED_LESSON -> DEVELOPING_PLAYBOOK ->
TRADER_STRATEGY_CANDIDATE -> CEO REVIEW -> ALPHA FALSIFICATION -> independent validation if it
survives. Stages are not to be skipped artificially.

## When a candidate may be created

Requires prospectively observed evidence of: recurring market behavior; plausible
structural/mechanical explanation; identifiable market regime; explicit entry conditions; explicit
invalidation; stop logic; target logic; management logic; no-trade conditions; known failure modes;
supporting examples; genuine counterexamples. No fixed minimum N. Use judgment -- do not wait for
statistical validation, but do not lower standards just to produce a candidate either.

## Required candidate format

```
STRATEGY_ID
STATUS = UNVALIDATED
REGIME
DIRECTION
TIMEFRAME_STACK
MARKET_MECHANISM
CONTEXT
LOCATION
ENTRY_CONDITION
CONFIRMATION
INVALIDATION
INITIAL_STOP_LOGIC
PRIMARY_TARGET_LOGIC
EXPECTED_RR_PROFILE
MANAGEMENT_PLAN
NO_TRADE_CONDITIONS
FAILURE_MODES
SUPPORTING_EXAMPLES
COUNTEREXAMPLES
KNOWN_LIMITATIONS
WHY_THIS_IS_A_STRATEGY_AND_NOT_ONLY_AN_OBSERVATION
```

## Regime specialization

Use the existing regime matrix (`AI_TRADER_REGIME_STRATEGY_MATRIX.md`). No single universal
strategy is sought. The intended long-term portfolio may hold distinct specialists per regime:
clean bull trend, clean bear trend, range, high volatility, low volatility/compression, volatility
expansion, bullish transition, bearish transition, breakout, failed breakout/whipsaw,
session-specific behavior. Only create candidates where actual evidence exists. Empty regimes stay
`NO_VALIDATED_STRATEGY_YET`.

## Governance (non-negotiable)

Do NOT: optimize retrospectively; rewrite historical observations; use future bars; lower
standards just to produce a strategy; send anything to Alpha automatically; modify StrategyCatalog;
modify S5; promote anything to demo/live.

## Candidate registry

*(none yet -- see readiness assessments below)*

## Readiness assessments (append-only log, most recent first)

### 2020-06-09 (replay time) -- initial assessment at directive installation

`NO_STRATEGY_CANDIDATE_READY_YET`

Reviewed the two active playbooks in `STRATEGY_EVIDENCE_DENOMINATOR.md` as of trade #63 (open):

- **Playbook A -- WITH-trend SHORT** (2 consecutive real-volume ~2000+ down-closes, BEARISH H4,
  bare test, no multi-timeframe alignment check): `DEVELOPING_PLAYBOOK`, NOT ready. Most complete
  documentation of any playbook (n=11 taken, 11/11 qualifying occurrences taken, explicit
  entry/stop/trail/management logic, multiple documented failure modes -- wick-survival,
  overshoot, sign-flipping, repeated-piercing -- across trades #58-62), but (1) currently NET
  NEGATIVE on its own criteria (4W/7L, -2.192pts, five straight losses #59-62 as of the last
  count) and (2) the apprenticeship's own Multi-Timeframe Trend Alignment V1 correction was
  installed specifically because this bare-test entry proved insufficient during active H1/M15
  bullish misalignment -- exactly the period that produced the recent loss streak. Formalizing the
  pre-correction bare-test version now would codify a specification with a known, already-
  identified defect. MISSING: forward evidence under the corrected, alignment-aware entry rule
  (requiring genuine local bearish re-alignment during active bullish H1/M15 recovery, not a bare
  2-bar test) -- zero SHORT trades have been taken since the correction (trade #63, the only trade
  since, is a LONG under Playbook B). Needs several forward-aligned SHORT attempts, resolved, before
  re-evaluation.

- **Playbook B -- Countertrend LONG** (elevated evidence bar vs. trade #53's benchmark, now also
  MULTITIMEFRAME_ALIGNMENT-tagged): `DEVELOPING_PLAYBOOK`, NOT ready. n=1 resolved (trade #53,
  loss) + 1 open/unresolved (trade #63) -- far too small, and the one open trade cannot be used as
  supporting evidence until it closes (using an open trade's current unrealized state would risk
  outcome-informed reasoning). 6 correctly-declined non-qualifying sequences are useful
  counterexample material but do not substitute for resolved qualifying trades. MISSING: at least
  a handful of resolved qualifying trades (taken or correctly-declined-and-verified) post
  Multi-Timeframe correction.

No other recurring pattern in the log currently carries an explicit, complete entry/stop/
target/management specification distinct from the two playbooks above. Re-assess opportunistically
as forward evidence accumulates -- next natural checkpoint is trade #63's resolution (adds Playbook
B's second data point) and the next several WITH-trend SHORT attempts under the corrected rule
(tests Playbook A's aligned version).

### 2020-06-10 14:45 UTC (replay time) -- trade #63 resolved, Playbook B update (not a re-assessment)

Trade #63 closed WIN, +2.306R -- Playbook B (Countertrend LONG, elevated evidence bar) is now
1-for-2 (#53 loss, #63 win), the first sequence to clear the elevated bar and the first
countertrend LONG win of the entire apprenticeship (6 attempts total: #47-#50/#53 losses, #63
win). This is a genuinely encouraging single data point but STILL `DEVELOPING_PLAYBOOK`, not
`READY_FOR_STRATEGY_CANDIDATE` -- n=2 resolved trades under the elevated-bar rule remains far too
small, and one win does not establish the entry/stop/management specification as reliable (the
prior 5/5 losing streak was itself entered on real, if lesser, confirmation). MISSING: at least a
few more resolved qualifying trades under the elevated bar before re-assessment. Not re-running the
full readiness assessment for a single trade outcome -- next full re-assessment remains
opportunistic, per standing governance (do not force a candidate to justify checking in).

### 2020-06-15 00:15 UTC (replay time) -- trade #64 resolved, Playbook A-prime update (not a re-assessment)

Trade #64 closed WIN, +1.443R -- Playbook A-prime (PARTIALLY_ALIGNED_SHORTS, post-Multi-Timeframe-
correction) is now 1-for-1 (its only resolved trade). This is the first WITH-trend SHORT to pass
live evaluation under the corrected forward rule, and it won -- a genuinely encouraging single data
point but still `DEVELOPING_PLAYBOOK` at n=1 resolved trade (n=2 total including the correctly-
declined 2020-06-11 test). MISSING: several more resolved trades under the corrected rule (both
wins and losses) before any candidate assessment is warranted. Not re-running the full readiness
assessment for a single trade outcome, per standing governance.

### 2020-06-18 08:45 UTC (replay time) -- trade #65 resolved, Playbook A-prime update (not a re-assessment)

Trade #65 closed LOSS, -1.119R -- Playbook A-prime (PARTIALLY_ALIGNED_SHORTS/FULLY_ALIGNED_SHORTS,
post-Multi-Timeframe-correction) is now 1-for-2 (#64 win, #65 loss). This is also the first trade
in the entire apprenticeship closed under the new fixed-SL/TP methodology (installed 2026-08-27
real-time, superseding the old NO_FIXED_TP/trailing-only template for trades #1-65) -- SL and TP
are now set and frozen at entry using the first realistic pre-entry-visible structural target, and
the trade closes for real on the first close beyond either level. Still `DEVELOPING_PLAYBOOK` at
n=2 resolved trades -- MISSING: several more resolved trades under both the corrected forward rule
AND the new fixed-SL/TP methodology before any candidate assessment is warranted. Not re-running
the full readiness assessment for a single trade outcome, per standing governance.

### 2020-06-30 15:00 UTC (replay time) -- trade #66 resolved, Playbook A-prime update (not a re-assessment)

Trade #66 closed LOSS, -1.398R -- Playbook A-prime (PARTIALLY_ALIGNED_SHORTS/FULLY_ALIGNED_SHORTS,
post-Multi-Timeframe-correction) is now 1-for-3 (#64 win, #65 loss, #66 loss). Two straight losses
under the corrected forward rule and the fixed-SL/TP methodology, following the single #64 win.
Still `DEVELOPING_PLAYBOOK` at n=3 resolved trades -- MISSING: several more resolved trades before
any candidate assessment is warranted; the current small sample (1W/2L) is consistent with both "the
corrected rule still needs more forward evidence" and "this specific setup family may be marginal,"
and cannot yet distinguish between them. Not re-running the full readiness assessment for a single
trade outcome, per standing governance.
