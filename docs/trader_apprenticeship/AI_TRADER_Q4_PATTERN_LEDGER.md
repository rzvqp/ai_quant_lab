# AI_TRADER_Q4_PATTERN_LEDGER

Prospective PATTERN-007 field-capture (per `AI_TRADER_Q4_APPRENTICESHIP_V1` §13-14) and any new
recurring-behavior observations (§15). PATTERN-007 remains BEHAVIORALLY_REAL=YES /
TRADEABLE=NO / DISCRIMINATOR=INSUFFICIENT_EVIDENCE / PLAYBOOK_READY=NO throughout — this ledger
captures evidence, it does not authorize trading the pattern. Every P007-shaped event is registered
with a PRE-CLASSIFICATION before its resolution, exactly as the Q1-Q3 record's own standing
discipline required, extended now with the systematic field set the Q3 forensic audit found was
missing.

---

## Q4-P007-001

TIMESTAMP: 2020-10-02 02:29:59 UTC (bar 103), ASIA session (00-08 UTC).
REGISTERED BEFORE RESOLUTION -- fields below reflect only what was causally available through bar
104 (02:44:59 UTC); FOLLOW_THROUGH/ACCEPTANCE fields are marked PENDING and will be filled from
subsequent bars without altering anything already recorded here.

TRIGGER: Bar 103 (close 02:29:59) closed at 1894.036, the first real close-basis break below H1
EMA50 confirmed (1895.658) since Q4 opened (EMA50 gap had been >8pt for the entire prior 100 bars,
compressing steadily since bar 76's ~16.6pt peak). Bar 103's low (1892.438) also broke well below
every prior Q4 local low back to the bar-92/95/100 grind-lower sequence -- the first genuinely fresh
multi-bar structural low of the quarter, not merely an EMA touch.
STRUCTURAL_LEVEL_BROKEN: ~1897.39 (bar 100's low, the most recent local reference) -- bar 103 broke
well beyond it to 1892.438, not a marginal undershoot.
BREAK_DEPTH_ATR: NOT_AVAILABLE (M15 ATR14 not present in current `data_get_study_values` output --
only H1 EMA50 confirmed and Session VWAP are visible this session; not fabricated).
BREAK_VELOCITY: Fast -- bar 102 close 1897.512 to bar 103 low 1892.438 = 5.074pt move within a
single 15-min bar.
BODY_ATR: NOT_AVAILABLE (same reason as BREAK_DEPTH_ATR).
WICK_BODY_RATIO (bar 103): body=3.476 (1897.512->1894.036), wick=1.646 (0.048 upper + 1.598 lower),
ratio ~0.474 -- body-dominant, not a pure rejection wick.
FOLLOW_THROUGH_1_BAR: Bar 104 (02:44:59) extended further -- close 1893.24 (below bar 103's close),
low 1891.406 (a fresh lower low). Direction = CONTINUATION, not reclaim, through 1 bar.
FOLLOW_THROUGH_2_BAR: Bar 105 (close 1893.64) -- still below EMA50 (1895.563 at that point), no
reclaim, but no further extension down either (consolidating just above bar104's low).
FOLLOW_THROUGH_4_BAR: Bars 106-107 -- bar 106 closed 1895.226, the closest approach to EMA50
(0.337pt below, a near-reclaim on a closing basis) with real bounce strength; bar 107 wicked ABOVE
EMA50 intrabar (high 1896.139) for the first time since the break but closed back below (1894.39,
0.397pt below EMA at that point) -- per this apprenticeship's standing close-based-trigger
convention, this is NOT a genuine reclaim, only a wick-based approach. Through the full 4-bar
follow-through window (bars 104-107), NO close-based reclaim of EMA50 has occurred -- price has
oscillated 1891.4-1896.1 without ever closing back above the EMA.
TIME_BEYOND_LEVEL: 5 consecutive bars (103-107) closed below EMA50 so far; ongoing, ATTEMPTED but
NOT YET reclaimed on a closing basis (bar 107's wick was the closest).
DISTANCE_H1_EMA50: bar103 close -1.622pt; bar104 close -2.418pt (deepening).
H4_H1_M15_RELATION: H4 context unchanged (same continuous 07-20-originating episode, formal stale
BEARISH tag never resolved); H1 now showing its first genuine multi-bar pullback of Q4; M15 is the
break itself.
SESSION: ASIA (00-08 UTC).
PRIOR_LEVEL_TEST_COUNT: 0 (fresh break of a level never tested before in Q4).
PRIOR_REJECTION_COUNT: 0.
ACTIVITY_MAGNITUDE: bar103 vol 531, bar104 vol 618 -- both a step up from the immediately preceding
thin-drift bars (205-352) but still well below this session's own "real volume" precedent (>700-800
established at bars 47-63) -- ACTIVITY_TREND = RISING but not yet at the session's own confirmed-
real-volume threshold.
PRICE_PROGRESS_PER_ACTIVITY: NOT_COMPUTABLE cleanly without ATR; qualitatively, price moved 5.074pt
on bar103's 531 volume vs. the bar-50 breakout's 9.169pt range on 1318 volume -- a materially
steeper price-per-volume ratio than the confirmed real-volume breakout, worth noting but not
over-interpreting from two bars.
EXPANSION_STATE: First genuine expansion bar since the bar-73 volume spike (which had no
follow-through); bars 103-104 DO show follow-through so far.
ACCEPTANCE_BEHAVIOR: PENDING.

PRE-CLASSIFICATION (recorded before any further bars are read): EXPECTED_BEHAVIOR per the standing
PATTERN-007 prior = eventual reclaim (fast/slow/deep) rather than sustained acceptance below EMA50.
FAILURE_CONDITION (would count as COUNTEREXAMPLE to the standing prior) = sustained acceptance below
EMA50 for multiple further bars without a reclaim attempt, i.e. NON_RECLAIM/ACCEPTANCE behavior.
Two bars of continuation-without-reclaim (103-104) is NOT yet enough to classify either way --
genuinely watching.

### RESOLUTION (bars 105-114, 2020-10-02 02:44:59-05:29:59 UTC)
Bar 105 (02:44:59): close 1893.64, still below EMA, no further extension.
Bar 106 (02:59:59): close 1895.226, near-reclaim (0.337pt below EMA), real bounce strength.
Bar 107 (03:14:59): high 1896.139 wicked ABOVE EMA intrabar but closed 1894.39, back below --
wick-only, not a genuine reclaim per standing close-based convention.
Bar 108 (03:59:59): close 1894.637, still below, thin vol 176.
Bar 109 (04:14:59): close 1894.061, still below, thin vol 222.
Bar 110 (04:29:59): close 1893.808, still below, thin vol 140 -- 8th consecutive bar below EMA50
(103-110), all on thin volume, no reclaim attempt of substance.
Bar 111 (04:44:59): close 1895.668, a genuine but marginal close-based RECLAIM (+0.141pt above EMA),
still on thin volume (220) -- a SLOW_RECLAIM by elapsed time (8 bars / 2h) but weak by volume.
Bar 112 (04:59:59): reclaim FAILED within exactly 1 bar -- close 1891.342, low 1890.525 (a fresh,
deeper low than bar 104's), on REAL volume (816, the heaviest of the episode to that point).
Bar 113 (05:14:59): capitulation-style wick to a new episode-sequence low (1889.866) followed by a
massive real-volume (2001) reversal, closing 1897.806 -- decisively back above EMA50 (+2.443pt).
Bar 114 (05:29:59): strong real-volume (1642) continuation, close 1902.946, high 1905.8 -- fully
back inside the pre-break consolidation zone and above 1902.349.

FINAL CLASSIFICATION: **SUPPORT** (for the standing PATTERN-007 "eventual reclaim" prior), with the
specific sub-type **DEEP_RECLAIM** -- the pattern did NOT resolve as a fast or clean reclaim; it
included a genuine failed-reclaim fakeout (bar 111, thin volume) followed by a deeper real-volume
breakdown (bar 112) before the actual, durable, real-volume reclaim occurred (bars 113-114). This is
recorded as SUPPORT because the terminal behavior matches the pattern's core prior (EMA50 break
followed by reclaim, not sustained acceptance/trend-continuation below it), but the PATH was more
complex and volume-differentiated than any single Q1-Q3 instance on record -- explicitly flagged as
a genuinely new texture (thin-volume fakeout-reclaim, then real-volume deeper-break, then
real-volume durable-reclaim) not previously captured in the Q1-Q3 field set. This is the richest
single field-capture in the pattern's history to date, per the mandate's own §13 instruction to
extend systematic capture going forward -- not modified or reclassified after the fact to fit a
predetermined tally.
ACCEPTANCE_BEHAVIOR: None -- the market did not accept price below EMA50; every approach eventually
reversed, culminating in a real-volume reclaim.
TOTAL_TIME_BEYOND_LEVEL: 9 consecutive bars closed below EMA50 (103-111 inclusive, counting bar
111's marginal reclaim as the first close back above), ~2.25 hours -- the longest sub-EMA excursion
observed in this apprenticeship's entire Q1-Q4 record before a genuine reclaim held.

---

## Q4-P007-002

TIMESTAMP: 2020-10-05 07:14:59 UTC (bar 213), ASIA session.
REGISTERED BEFORE RESOLUTION.

TRIGGER: Bar 213 closed 1887.99 (= its own low, weak close), real volume 1061 -- a genuine
close-based break below 1889.866, the structural low set by Q4-P007-001's deep pullback (bars
103-114). H1 EMA50 was BELOW/FALLING (qualitative -- exact numeric EMA50 unavailable this instance
due to the disclosed `data_get_study_values` tooling anomaly at bar 191; using `data_get_pine_tables`
qualitative fields instead, per the disclosed workaround).
STRUCTURAL_LEVEL_BROKEN: 1889.866 (Q4-P007-001's own low -- this is the first time that specific
level has been retested since it was set).
BREAK_DEPTH_ATR: ATR14 at break = 22.4 pips = 2.24pt; break extended from bar212's close (1893.176)
to bar214's low (1887.132) = 6.044pt = ~2.7x ATR14.
BREAK_VELOCITY: Fast -- bar 212 close to bar 213 low = 5.186pt in one 15-min bar.
WICK_BODY_RATIO (bar 213): body=5.186 (1893.176->1887.99), wick=0.35 (0->1893.43 high minus open...
recomputed: open=1893.176, close=1887.99, high=1893.43, low=1887.99; body=5.186, upper wick=0.254,
lower wick=0; ratio=0.254/5.186=0.049 -- a strongly body-dominant, low-wick bar (a real breakdown
bar, not a rejection wick).
FOLLOW_THROUGH_1_BAR: Bar 214 extended -- close 1888.568, fresh low 1887.132. CONTINUATION.
SESSION: ASIA.
PRIOR_LEVEL_TEST_COUNT: 0 (first retest of the 1889.866 reference since it was set).
ACTIVITY_MAGNITUDE: bar213 vol 1061, bar214 vol 832 -- both real by this quarter's standard (>700).
ACTIVITY_TREND: RISING then bar215's 569 (moderating on the bounce).
EXPANSION_STATE: Genuine expansion, 2 consecutive real-volume bars.
PRE-CLASSIFICATION (recorded before resolution): EXPECTED_BEHAVIOR per the standing PATTERN-007
prior = eventual reclaim (fast/slow/deep). FAILURE_CONDITION = sustained acceptance below EMA50/this
level without reclaim. Bar 215's bounce (close 1890.16, still below EMA50/VWAP) is NOT yet a
reclaim -- watching.

### RESOLUTION (bars 216-222, 2020-10-05 07:59:59-09:29:59 UTC)
Bar 216 (07:59:59): close 1892.476, real vol 610, continued bounce, still below EMA50.
Bar 217 (08:14:59, London session begins, VWAP resets): close 1893.3, vol 539, still below EMA50.
Bar 218 (08:29:59): close 1893.693, vol 510, still below EMA50.
Bar 219 (08:44:59): close 1895.576, vol 528, still below EMA50, narrowing.
Bar 220 (08:59:59): close 1897.974, vol 518, still below EMA50, narrowing further.
Bar 221 (09:14:59): close 1900.403, vol 602 -- genuine close-based RECLAIM (Price vs EMA50 flips to
ABOVE).
Bar 222 (09:29:59): close 1899.798, vol 338, reclaim HOLDS for a second bar.
FINAL CLASSIFICATION: **SUPPORT** (for the standing PATTERN-007 prior), sub-type **SLOW_RECLAIM** --
8 bars (213-220 inclusive) below EMA50 before a clean, sustained close-based reclaim (221-222), a
smoother path than Q4-P007-001 (no failed-reclaim-then-deeper-break complication this time). Real
volume present on both the break (213-214) and the reclaim (221), unlike Q4-P007-001's break leg
which was volume-mixed. This is the SECOND consecutive SUPPORT instance for the pattern in Q4 (2/2),
though both instances share the same underlying episode/regime (INDEPENDENCE_LIMITATION unchanged --
see `alpha-broad-discovery-v2`-era discussion in the standing knowledge base).
NOTE ON DATA SOURCE: exact numeric H1 EMA50 confirmed values were unavailable for this entire
instance due to the disclosed `data_get_study_values` tooling anomaly (see M15 log, bar 191) --
all EMA-relative fields here are qualitative (ABOVE/BELOW/slope) via the verified `data_get_pine_tables`
workaround, not exact point distances. This limitation is disclosed, not silently patched over.

---

## Q4-P007-003

TIMESTAMP: 2020-10-06 15:59:59 UTC (bar 340), NY session.
REGISTERED BEFORE RESOLUTION.

TRIGGER: Bar 340 closed 1902.232 (real volume 1268), a decisive close-based break of BOTH 1902.349
(the quarter's most contested reference level) AND H1 EMA50 (qualitative: flips ABOVE->BELOW) in
the same bar -- the first time this quarter these two references have broken together on real
volume. This followed a genuine multi-bar real-volume distribution leg (bars 335-339, off the
bar-331 fresh ATH of 1921.277).
STRUCTURAL_LEVEL_BROKEN: 1902.349.
BREAK_VELOCITY: bar 339 close (1908.994) to bar 340 low (1901.81) = 7.184pt in one 15-min bar --
fast.
FOLLOW_THROUGH_1_BAR: Bar 341 -- close 1906.044 (real vol 1393), a real-volume bounce that reclaimed
above 1902.349 on a closing basis but did NOT reclaim EMA50 (still qualitatively BELOW). Low 1900.988
even dipped further before the bounce. Mixed signal -- NOT yet a genuine EMA reclaim.
SESSION: NY.
ACTIVITY_MAGNITUDE: bars 340-341 volumes 1268/1393, both real by this quarter's threshold.
PRE-CLASSIFICATION (recorded before further bars read): EXPECTED_BEHAVIOR per the standing
PATTERN-007 prior = eventual EMA50 reclaim. FAILURE_CONDITION = sustained acceptance below EMA50
without reclaim. Bar 342 (close 1905.568, still below EMA50 qualitatively) continues the watch --
genuinely unresolved.

### INTERIM UPDATE (bars 343-347, 2020-10-06 16:44:59-17:44:59 UTC)
Bars 343-347: closes 1904.488/1903.974/1903.8/1903.986/1902.508, volume 544/618/539/617/368
(moderate, not thin, not heavy) -- 8 consecutive bars now (340-347) below EMA50 qualitatively, no
reclaim attempt of substance yet, gentle further drift down toward 1902.349 (bar 347 low 1902.208,
back below the level intrabar). EMA slope flipped FALLING at bar 345. Genuinely still unresolved --
watching.

### MAJOR VOLUME EVENT (bars 352-353, 2020-10-06 18:59:59-19:14:59 UTC) -- record volume of the quarter
Bar 348 (17:59:59): close 1900.844, real vol 866, low 1898.53 (below 1900.39).
Bar 349 (18:14:59): close 1902.87, vol 483, brief reclaim of 1902.349.
Bar 350 (18:29:59): close 1905.306, vol 448.
Bar 351 (18:44:59): close 1905.65, vol 437 -- still qualitatively below EMA50 despite the bounce
(EMA itself had been falling since bar 345).
Bar 352 (18:59:59): close 1897.514, volume **4743** -- the heaviest bar of the ENTIRE quarter to
that point (prior record: bar 57's 3626), wide range (high 1906.334, low 1892.286 = 14.048pt).
Bar 353 (19:14:59): close 1894.61, volume **6203** -- a new, even larger record (nearly double bar
352's), low 1890.31 (0.444pt above the bar-103/113 deep-pullback low of 1889.866, not yet broken).
Bar 354 (19:29:59): close 1893.973, vol 3268 (still very heavy), low 1891.207.
Bar 355 (19:44:59): close 1892.952, vol 1916 (moderating), low 1892.042.
OBSERVATION: two consecutive record-shattering volume bars (352-353) during NY session, consistent
with a genuine macro/news-type event by signature (magnitude and abruptness far beyond anything
else in the Q1-Q4 record) -- NOT asserting a specific headline or cause, since no verified news
feed is available to this apprenticeship; this is a price/volume observation only, per the
standing discipline against inventing unverified mechanisms. Q4-P007-003 remains open and
unresolved -- price has now spent 16 consecutive bars (340-355) below EMA50, the longest sub-EMA
excursion of the entire Q1-Q4 apprenticeship record (exceeding Q4-P007-001's 9 bars), still on
real/heavy volume rather than thin drift. Watching for eventual resolution -- this is now the
richest and most stress-tested P007 instance on record.

### CONTINUED DECLINE (bars 356-360, 2020-10-06 19:59:59-20:59:59 UTC)
Bar 356 (19:59:59): close 1888.13, real vol 1707, low 1887.088 -- breaks BELOW 1889.866 (the
bar-103/113 deep-pullback low) for the first time this quarter.
Bar 357 (20:14:59): close 1886.348, real vol 1151, low 1883.738 -- breaks below the Q4 opening-day
dip low (1884.72, bars 2-4) -- now the lowest price of the entire Q4 record.
Bar 358 (20:29:59): close 1886.328, vol 325 (moderating), narrow range.
Bar 359 (20:44:59): close 1882.376, real vol 641, low 1880.68 -- fresh Q4 low again.
Bar 360 (20:59:59, Tuesday NY close): close 1878.177, real vol 1319, low 1874.808 -- fresh Q4 low,
now ~31pt below the pre-event high (bar 351's 1905.65).
This is the single largest sustained decline of the entire Q1-Q4 apprenticeship record. Q4-P007-003
remains open -- price has now spent 21 consecutive bars (340-360) below EMA50, still on real volume
throughout, no reclaim attempt of any substance. Genuinely unresolved heading into the daily
rollover.

GAP-154 (75min standard daily rollover, Tuesday 2020-10-06T20:59:59Z -> 22:00:00Z, zero-price-gap
verified 1878.177==1878.177) logged in `REPLAY_DATA_GAP_LEDGER.md`.

### CONTINUATION (bars 361-486, CSV_CAUSAL_REPLAY_ADAPTER_V1 transport, 2026-08-30 session)
No reclaim attempt of substance across bars 361-486 (full detail in `AI_TRADER_Q4_M15_LOG.md`,
bars 379 session-stop entry onward). GAP-155 (75min standard daily rollover, Wednesday
2020-10-07T20:59:59Z -> 22:00:00Z, zero-price-gap verified 1887.592==1887.592) logged in
`REPLAY_DATA_GAP_LEDGER.md`. One full NY session (bars 421-452, 2020-10-07) formed a genuine S5
opening range (or_high 1891.928, or_low 1883.452, bars 421-424) but the session high (1890.544)
never reached or_high -- no S5 setup, mechanically correct NO_TRADE, not a judgment call. The
below-causal-H1-EMA50 excursion reached 147 consecutive M15 bars (340-486 inclusive, ~36.75 real
hours net of the GAP-155 rollover) before resolving -- see RESOLUTION below.

### RESOLUTION

```
STATUS               RESOLVED
CLASSIFICATION        SUPPORT / EXTREME_DELAYED_RECLAIM
TRIGGER_BAR           340 (2020-10-06 15:59:59 UTC)
RESOLUTION_BAR         487 (2020-10-08 06:44:59 UTC)
DURATION               147 consecutive M15 bars below causal H1 EMA50 (340-486 inclusive)
RECLAIM_CLOSE           1893.26
CAUSAL_H1_EMA50_AT_RESOLUTION   1891.748 (independently reconstructed and cross-validated by two
                        methods -- see integrity note below)
RECLAIM_MARGIN          +1.512 (thin -- not a decisive break)
RECLAIM_BAR_VOLUME       704 (moderate/real, not exceptional)
DEEPEST_LOW_THIS_EPISODE 1872.898 (bar 375) -- ~29pt below the 1902.349 trigger level, the deepest
                        pullback of the entire Q1-Q4 apprenticeship record
```

**Why EXTREME_DELAYED_RECLAIM, a new subtype**: the standing PATTERN-007 prior (eventual EMA50
reclaim) held -- this is genuinely SUPPORT, not the pattern's first COUNTEREXAMPLE -- but only after
147 consecutive bars, by a very wide margin the longest and most severely stress-tested instance in
the pattern's entire history (prior max: Q4-P007-001, 9-12 bars; the interim "record" noted at the
bar-378/379 checkpoint was itself only 38-40 bars, well under a third of the final duration). This
instance should weigh heavily against ever treating PATTERN-007 as a fast/reliable-timing setup --
it supports the pattern only as a very-long-horizon reversion prior, not an actionable near-term
signal. The reclaim itself is marginal (+1.512pt, not a decisive break) on moderate, not exceptional,
volume (704) -- follow-through is tracked in `AI_TRADER_Q4_M15_LOG.md` in the bars immediately
following resolution, not assumed here.

**Integrity note on the causal H1 EMA50 figure (disclosed, not silently corrected)**: the live
batch-processing script used during bars 389-486 re-seeded its EMA tracker from a stale bar-385
snapshot on each fresh process restart, silently missing bars 386-388's contribution to the H1
aggregation for the remainder of that run. This produced a slightly-wrong EMA figure at the moment
of resolution (recorded live as 1892.001; the true value, independently reconstructed by a clean
batch pass over the complete `Q4_SEALED_1_487.csv` and cross-validated against a corrected
incremental re-run, is **1891.748**). The bug was caught and fixed (the runner now always re-seeds
from whatever is currently sealed in durable state) before any further bars were processed. Every
one of the 98 `ROUTINE_NO_EVENT` decisions committed for bars 389-486 was independently re-verified
against the corrected EMA trajectory: all remain genuinely below EMA under the true figure (no false
negative, no missed reclaim, no bar wrongly classified) -- the bug affected only the reported EMA
*value*, never a decision, since bar 487 is confirmed as the sole reclaim point either way (both
1892.001 and 1891.748 are below bar 487's 1893.26 close). The figures in this RESOLUTION section use
the corrected, true value throughout.

---

## Q4-P007-004

**PROCESS DISCLOSURE (read before the event detail below):** this instance was identified
**retrospectively**, not pre-registered before its resolution. The autonomous batch runner used from
bar 386 onward mechanically checks for gaps, S5 triggers, and all-time price/volume extremes, but was
never extended to check for a NEW P007-eligible break (a judgment call: "severe" break, "record/heavy"
volume) -- so bars 787-884 were committed as plain `ROUTINE_NO_EVENT` in real time, and this event was
only recognized when reviewing the batch's own output afterward, by which point bar 884 (well past the
reclaim) had already been revealed. This is a genuine, disclosed gap in the mechanical process, not a
causal-integrity violation: every bar was still individually revealed and committed one at a time (no
bulk exposure, no lookahead), and the reclaim determination itself is unaffected by when a human/AI
noticed the pattern. The batch runner has been extended (see `q4_batch_runner.py`, current version)
to flag a heavy-volume EMA-crossing going forward so this gap does not recur silently.

```
STATUS               RESOLVED (identified retrospectively -- see disclosure above)
CLASSIFICATION        SUPPORT / RECLAIM (duration comparable to, though shorter than, Q4-P007-003)
TRIGGER_BAR           787 (2020-10-13 12:29:59 UTC) -- close 1916.054, real volume 1929, first close
                      below the causal H1 EMA50 (1918.2) since the bar-608-trade-era rally began.
                      Immediate, real-volume follow-through: bar 788 close 1909.671 (vol 2718, H1
                      candle closes this bar), bar 789 close 1907.557 (vol 2747).
STRUCTURAL_LEVEL      Not independently identified against a specific pre-registered price level
                      (unlike Q4-P007-001/002/003, which broke a specifically-named prior low) --
                      this is a descriptive gap of the retrospective identification, disclosed rather
                      than backfilled with an invented level.
RESOLUTION_BAR         878 (2020-10-14 12:14:59 UTC) -- close 1905.436 > causal H1 EMA50 1904.592
DURATION               91 consecutive M15 bars below causal H1 EMA50 (787-877 inclusive)
DEEPEST_LOW_THIS_EPISODE 1882.434 (bar 834) -- well above the all-time Q4 low (1872.898, bar 375),
                        not a new record
HEAVIEST_VOLUME_THIS_EPISODE 4134 (bar 791) -- real/heavy, comparable to the historic bars 352/353
                        (4743/6203) but not a new record
```

**Why RECLAIM, not a new COUNTEREXAMPLE**: price closed back above the causal H1 EMA50 at bar 878
and held (above-streak continuing through at least bar 884, where the S5 breakout at bar 884 itself
occurred from a position above EMA). No trade/MGMT-004 decision was affected by the late recognition
of this event -- `TRADES_TOTAL` and `MGMT004_TRIGGERS_TOTAL` are unchanged by this entry; it is a
pattern-taxonomy record only.
