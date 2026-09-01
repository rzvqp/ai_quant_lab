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

---

## Q4-P007-005

**FIRST INSTANCE DETECTED BY THE DURABLE PROSPECTIVE GATE** (`p007_detector.py`, CEO mandate + Red
Team E110) -- registered genuinely prospectively (before resolution), unlike Q4-P007-004.

```
TRIGGER_BAR           1389 (2020-10-22 02:00:00-02:14:59 UTC)
TRIGGER_CLOSE          1911.413
CAUSAL_H1_EMA50_AT_TRIGGER   1915.604 (gap -4.19pt -- LARGER than Q4-P007-004's initial -2.15pt gap)
TRIGGER_VOLUME          980 (moderate -- clearly above the quietest bars in this stretch (~200-400)
                        but well below the historical "heavy/record" instances that opened
                        Q4-P007-003 (1268) or Q4-P007-004 (1929, with immediate 2718/2747/4134
                        follow-through))
```

**PRE-CLASSIFICATION (recorded before further bars read):** genuinely ambiguous by volume. The gap
below EMA is real and larger than P007-004's own opening gap, but the triggering volume alone does
not clearly meet the "sharp, volume-confirmed" bar prior genuine instances set. Watching for: (a)
real-volume follow-through in the bars immediately after (would support classifying as a genuine
PATTERN-007 instance), or (b) a fade/reclaim without ever showing volume confirmation (would support
`REJECTED -- EMA crossing only, does not meet PATTERN-007's volume-confirmed criterion`, clearing the
gate's lock without asserting a false SUPPORT/COUNTEREXAMPLE). Not pre-committing to either outcome.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1402 (2020-10-22 05:29:59 UTC)
DURATION               13 bars (1389-1401)
DEEPEST_LOW             1911.26 (bar 1390)
HEAVIEST_VOLUME         411 (bar 1390) -- never exceeded 411 across the whole 13-bar window; most
                        bars under 200, several under 100
```

No real-volume follow-through at any point after the trigger bar -- volume collapsed to thin levels
immediately and stayed there. Price reclaimed the causal H1 EMA50 within 13 bars without ever
printing a fresh local extreme. This is the ambiguity flagged in the pre-classification resolving to
outcome (b): a mechanical EMA crossing the over-inclusive gate correctly flagged per its own design,
but not a "sharp, volume-confirmed" break matching PATTERN-007's actual definition. Classified
REJECTED rather than SUPPORT to keep the pattern's evidence base honest -- inflating the count with
routine wiggles would dilute, not strengthen, PATTERN-007's evidentiary standing. No trade/MGMT-004
decision affected (no trade was open at the time).

---

## Q4-P007-006

**EPISODE CONTINUITY NOTE (CEO E111 -- every candidate reasoned individually, no auto-reject):** the
underlying price decline the gate tracks here originates at bar 1425 (same reference the gate has
reported since bars 1425/1426/1428, each individually reasoned and rejected as trivial -- see
`AI_TRADER_Q4_M15_LOG.md`). This is NOT a new, independent trigger -- it is the SAME episode,
genuinely escalating. Numbering it as its own entry reflects that the SEVERITY assessment changed
with new information (bar 1429), not that a fresh, unrelated break occurred; the prior REJECTED
determinations for 1425/1426/1428 stand unchanged (correct given what was known at each of those
bars) and are not retroactively rewritten.

```
EPISODE_ORIGIN_BAR      1425 (2020-10-22 11:00:00 UTC) -- gap -0.24pt, vol 243, REJECTED (trivial)
PRIOR_RE-FLAGS           1426 (gap -0.33pt, vol 226, REJECTED), 1428 (gap -1.64pt, vol 282, REJECTED)
ESCALATION_BAR           1429 (2020-10-22 11:45:00-11:59:59 UTC) -- genuinely different character
ESCALATION_CLOSE          1905.122
ESCALATION_LOW             1904.721 -- fresh 60-bar low, ~10pt intrabar range in one M15 bar
CAUSAL_H1_EMA50_AT_1429   1915.865 (gap -10.74pt -- far larger than any prior bar in this episode)
ESCALATION_VOLUME          976 (2-4x the episode's prior thin baseline of 198-527)
```

**PRE-CLASSIFICATION (recorded before further bars read):** bar 1429 looks like a genuine sharp,
volume-confirmed break -- unlike its predecessors in the same episode. Watching for real-volume
follow-through (would support classifying this as a genuine PATTERN-007 instance, SUPPORT pending
eventual reclaim) vs an early fade (would still resolve REJECTED, consistent with the episode's
earlier bars). Not pre-committing to either outcome.

### RESOLUTION

```
STATUS               RESOLVED
CLASSIFICATION        SUPPORT / RECLAIM
ESCALATION_BAR (real trigger)  1429 (2020-10-22 11:45:00 UTC)
RESOLUTION_BAR                  1506 (2020-10-23 09:44:59 UTC)
DURATION_FROM_ESCALATION        77 bars (1429-1505 inclusive)
DURATION_FROM_GATE_ORIGIN       81 bars (1425-1505 inclusive) -- includes the 4 genuinely-trivial
                                bars (1425/1426/1428, already individually REJECTED; not reopened)
DEEPEST_LOW                     1894.775
HEAVIEST_VOLUME                 2053
RECLAIM_CLOSE                    1910.826
CAUSAL_H1_EMA50_AT_RESOLUTION    1909.938 (margin +0.89pt, thin)
```

No S5 setup occurred during this episode (the S5 check ran unconditionally on every bar per CEO
E111 -- confirmed no trigger). One MAINTENANCE gap (GAP-165, bar 1464->1465) inside the episode,
standard. No trade was open; no trade/MGMT-004 decision affected. This is the pattern's third
genuinely-resolved SUPPORT instance in Q4 (after Q4-P007-003 and Q4-P007-004), and the second one
correctly identified as a real pattern only after an initial period of legitimately-trivial activity
under the same durable gate reference -- handled as a continuation, not force-classified either way
prematurely.

---

## Q4-P007-007

```
GATE_ORIGIN_BAR          1525 (trivial at first; bars 1525/1526 individually rejected)
GENUINE_ESCALATION_BAR    1527 (2020-10-23 13:30:00 UTC) -- caps an 8-bar accelerating-volume
                          decline (bars 1520-1527, NY session): volume 326/442/623/511/629/660/
                          792/1592, roughly quadrupling. Close 1907.01, gap -3.01pt at that bar.
RESOLUTION_BAR             1608 (2020-10-26 09:44:59 UTC)
DURATION_FROM_ORIGIN        83 bars (1525-1607)
DURATION_FROM_ESCALATION    81 bars (1527-1607)
DEEPEST_LOW                 1891.508
HEAVIEST_VOLUME              1496
RECLAIM_CLOSE                 1904.76
CAUSAL_H1_EMA50_AT_RESOLUTION 1904.274 (margin +0.49pt, thin)
```

**Why treated differently from the surrounding trivial candidates**: unlike bars 1509/1512/1513/
1514/1525/1526 (each a single thin/moderate bar with no sustained character), bar 1527 capped a
genuine multi-bar, volume-accelerating decline -- the qualitative signature PATTERN-007's definition
actually describes, not a mechanical threshold crossing. Classified **SUPPORT / RECLAIM**. GAP-166
(standard weekend) logged inside the episode. No S5 setup at any point (unconditional check
confirmed). No trade/MGMT-004 decision affected.

---

## Q4-P007-008

**Committed via the durable control flow (`ai_trader/csv_causal_replay/q4_control_flow.py`,
commit `44aee88`) for the first time -- CEO authorization to resume from bar 1632.**

```
GATE_ORIGIN_BAR          1631 (2020-10-26 12:30:00 UTC) -- retroactively confirmed once bar 1632's
                          reveal closed the containing H1 hour (causal H1 EMA only reflects fully-
                          closed hours; the crossing was not computable until then)
TRIGGER_CLOSE (1631)      1904.15
BAR_1632_CLOSE             1904.144
CAUSAL_H1_EMA50_AT_1632    1904.224
GAP                        -0.07 / -0.08pt -- a touch, not a break
VOLUME_CONTEXT (1626-1632) 942 / 817 / 749 / 700 / 595 / 333 / 286 -- steadily tapering; bars 1631
                           and 1632 are the two thinnest of the entire 22-bar window (1610-1632)
FRESH_LOCAL_EXTREME         none -- bar 1632 low 1903.074 sits inside the 1613-1632 range
```

**PRE-CLASSIFICATION (recorded before further bars read):** thin/declining volume into a marginal
EMA touch, no fresh extreme -- the same profile that resolved REJECTED for Q4-P007-005 and for the
early (non-escalating) bars of Q4-P007-006/007's own episodes, not the volume-confirmed-escalation
profile that resolved SUPPORT in those two. Leaning REJECTED, but not pre-committing -- watching for
either an early reclaim (consistent with this read) or a genuine volume-confirmed escalation (would
override this initial read, as it did for -006/-007). No trade open at gate-origin (POSITION=FLAT
since TRADE #7's resolution); no MGMT-004 relevance. No S5 trigger on bar 1632 (unconditional check
confirmed, per the durable control-flow ordering invariant).

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1633 (2020-10-26 13:00:00 UTC)
DURATION                3 bars (1631-1633)
DEEPEST_LOW              1903.074 (bar 1632)
HEAVIEST_VOLUME          333 (bar 1631) -- never exceeded across the whole episode
RECLAIM_CLOSE             1904.928
CAUSAL_H1_EMA50_AT_RESOLUTION 1904.224 (margin +0.70pt)
```

Reclaimed only 2 bars after gate-origin. Volume never escalated at any point (333/286/310 across
the 3-bar episode). Matches the pre-classification's leaning read exactly -- a marginal EMA touch on
tapering volume, not a sharp volume-confirmed break. Consistent with Q4-P007-005's REJECTED
signature. No trade was open at any point; no MGMT-004 relevance. No S5 trigger at any point in the
episode (unconditional check confirmed each bar).

---

## Q4-P007-009

```
GATE_ORIGIN_BAR          1634 (2020-10-26 13:15:00 UTC) -- only 1 bar after Q4-P007-008 resolved
                          REJECTED; price is chopping sideways around a flat causal H1 EMA50 rather
                          than making a decisive move
TRIGGER_CLOSE               1904.115
CAUSAL_H1_EMA50_AT_1634     1904.221
GAP                          -0.11pt -- a touch, not a break
VOLUME                        314 -- continuing the decay trend since bar 1628 (749/700/595/333/
                              286/310/314), no volume confirmation
INTRABAR_RANGE                1.9pt (high 1905.055, low 1903.16) -- wider than recent bars but fully
                              contained inside the 1613-1634 window, no fresh extreme
```

**PRE-CLASSIFICATION:** same profile as Q4-P007-008 -- leaning REJECTED, not pre-committing.
Watching for reclaim vs genuine volume-confirmed escalation. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance (closer to the line than -008)
RESOLUTION_BAR         1658 (2020-10-26 22:15:00 UTC)
DURATION                24 bars (1634-1657)
DEEPEST_LOW              1900.382 (bar 1635) -- not a fresh extreme; bars 1613/1616/1617 already
                        printed lower (1900.066-1900.874) earlier in the same consolidation
HEAVIEST_VOLUME          626 (bar 1642)
RECLAIM_CLOSE             1904.414
CAUSAL_H1_EMA50_AT_RESOLUTION 1903.881 (margin +0.53pt)
```

Full 24-bar episode reviewed, not just the reclaim bar. Bar 1635 (immediately after gate-origin)
printed a real down-move -- close 1904.115 -> 1901.644, low 1900.382, volume 610, roughly 2x the
preceding thin baseline -- and bar 1642 printed a second moderate bar (626). Neither led anywhere:
no accelerating multi-bar volume buildup like Q4-P007-006/007's genuine escalations, just two
isolated moderate bars surrounded by an otherwise-thin, decaying grind (bars 1643-1656 mostly 55-460,
several under 100) that drifted for 14 more bars before an unremarkable reclaim on 314/138 volume.
One MAINTENANCE gap (GAP-167, bar 1648->1649, 60min) inside the episode, standard. No trade was open
at any point; no MGMT-004 relevance. No S5 trigger at any point (unconditional check confirmed each
bar). Classified REJECTED rather than SUPPORT: the two moderate-volume bars were isolated, not
sustained/accelerating, and produced no fresh extreme -- same evidentiary-honesty standard applied
to Q4-P007-005.

---

## Q4-P007-010

```
GATE_ORIGIN_BAR          1688 (2020-10-27 07:45:00 UTC)
CONTEXT                   bars 1675-1684 ground quietly higher on thin volume (79-397), ~1908->1910
BREAK_BAR                  1685 -- close 1908.842 -> 1906.336, low 1904.66, volume 620 (~2x baseline)
CONTINUATION_BAR            1686 -- fresh local low 1904.231 (for the 1675-1685 window), volume 496
RETEST_BOUNCE_BAR            1687 -- close 1905.947, volume dropped to 237
RENEWED_BREAK_BAR (trigger)   1688 -- new low 1903.296 (below 1686's low), volume 453, close 1904.226
CAUSAL_H1_EMA50_AT_1688        1904.801
GAP                             -0.575pt -- largest gap magnitude of any candidate since Q4-P007-007
```

**PRE-CLASSIFICATION:** more credible signature than -008/-009's marginal touches -- a recognizable
break/bounce-retest/renewed-break shape with volume elevated relative to the immediate baseline
(453-620 vs 79-397). Not pre-committing to SUPPORT: volume is still well below TRADE #7-era levels
(700-1700) and below -006/-007's eventual escalation peaks (792-1592). Watching for real continuation
vs an early fade. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM -- on different evidentiary grounds than -006/-007
RESOLUTION_BAR         1708 (2020-10-27 15:15:00 UTC)
DURATION                20 bars (1688-1707)
DEEPEST_LOW              1897.914 (bar 1694) -- genuine fresh multi-hundred-bar extreme (lower than
                        any low seen since at least bar 1610: 1900.066/1900.382/1903.074)
HEAVIEST_VOLUME          619 (bar 1689)
RECLAIM_CLOSE             1905.816
CAUSAL_H1_EMA50_AT_RESOLUTION 1904.303 (margin +1.51pt)
```

Unlike -008/-009's isolated blips, this episode shows a SUSTAINED 7-bar directional decline (bars
1688-1694) making progressively lower lows every single bar -- 1903.296 -> 1901.552 -> 1901.447 ->
1900.854 -> 1900.28 -> 1898.86 -> 1897.914 -- with volume consistently elevated throughout that leg
(453/619/532/501/383/552/378, all above the immediate pre-episode baseline of 79-397). Volume never
reached -006/-007's escalation peaks (792-1592) and collapsed into a long thin consolidation (bars
1695-1704, mostly 240-327) before a final push and reclaim on moderate volume (508/382/551/502). The
SUSTAINED multi-bar progressive-new-lows character across the whole down-leg, plus the genuine fresh
extreme, is real qualitative evidence PATTERN-007's definition is pointing at -- distinct from
-008/-009's thin, isolated non-events, even without -006/-007's accelerating-volume signature. No
trade was open at any point; no MGMT-004 relevance. No S5 trigger at any point (unconditional check
confirmed each bar). Fifth genuinely-resolved SUPPORT instance in Q4 (after Q4-P007-003, Q4-P007-004,
Q4-P007-006, Q4-P007-007) -- the first identified primarily by sustained directional character plus a
fresh extreme rather than accelerating volume alone.

---

## Q4-P007-011

```
GATE_ORIGIN_BAR          1710 (2020-10-27 15:45:00 UTC) -- immediately after Q4-P007-010's reclaim
                          (bar 1708) and a follow-through push bar (1709: close 1905.575, high
                          1907.636, volume 783)
TRIGGER_CLOSE               1904.271
CAUSAL_H1_EMA50_AT_1710      1904.362
GAP                           -0.09pt -- a touch, not a break
VOLUME                         402
```

**PRE-CLASSIFICATION:** reads as a normal pullback/retracement after bar 1709's push higher, not a
fresh severe break -- no continuation lower yet, no fresh extreme (1904.224 is well inside the
1897.914-1907.636 range just established by -010). Leaning REJECTED, similar to -008/-009's profile,
not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1711 (2020-10-27 16:15:00 UTC)
DURATION                2 bars (1710-1711)
DEEPEST_LOW              1902.13 (bar 1711, intrabar -- a minor undershoot, not a fresh extreme;
                        -010's low of 1897.914 stands untouched)
HEAVIEST_VOLUME          1111 (bar 1711, ON THE RECLAIM bar, not the break bar -- the opposite of
                        PATTERN-007's signature)
RECLAIM_CLOSE             1906.622
CAUSAL_H1_EMA50_AT_RESOLUTION 1904.362 (margin +2.26pt)
```

Reclaimed on the very next bar after gate-origin. Bar 1711 dipped intrabar then reversed hard,
closing with the heaviest single-bar volume since TRADE #7's own hold (1111) -- but that volume
printed on the reclaim, not the break (bar 1710 itself was only 402). Confirms the
pre-classification's read exactly: a normal pullback/retracement, not a fresh break. No trade was
open at any point; no MGMT-004 relevance. No S5 trigger (unconditional check confirmed each bar).

---

## Q4-P007-012

**First candidate opened while a trade (TRADE #8) is open, using the durable control flow in
production -- trade mechanics confirmed to run unconditionally before this reasoning stop.**

```
GATE_ORIGIN_BAR          1743 (2020-10-27 22:30:00 UTC)
TRADE_STATE_AT_ORIGIN      TRADE #8 open, entry 1908.268, currently ~1904.965 (~-0.54R), clear of
                          both stop (1902.11) and MGMT-004 trigger (1914.426)
CONTEXT                    post-entry high 1911.354 (bar 1719), then a ~14-bar thin-volume grind
                          lower (1728 high 1911.107 -> 1742 close 1907.376, volume 120-320 throughout)
TRIGGER_CLOSE               1904.965
TRIGGER_LOW                  1904.85 -- fresh short-term low vs the whole 1719-1742 window
CAUSAL_H1_EMA50_AT_1743      1905.329
GAP                           -0.36pt
VOLUME                         515 -- 2-4x the immediate 120-320 baseline
```

**PRE-CLASSIFICATION:** genuine acceleration on the trigger bar itself, but the preceding 14-bar
grind lacked volume conviction -- more ambiguous than -010's clean sustained-decline signature. Not
pre-committing -- watching for real continuation vs an early fade. GAP-168 (standard, 60min) logged
just before this episode.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1748 (2020-10-27 23:45:00 UTC)
DURATION                5 bars (1743-1747)
DEEPEST_LOW              1904.372 (bar 1745) -- only marginally below the trigger bar's own low
                        (1904.85), not a meaningful new extreme
HEAVIEST_VOLUME          515 (bar 1743, the trigger bar itself -- never matched again)
RECLAIM_CLOSE             1905.34
CAUSAL_H1_EMA50_AT_RESOLUTION 1905.307 (margin only +0.03pt -- a bare, marginal reclaim)
```

The pre-classification's ambiguity resolved clearly toward REJECTED once follow-through was
observed: volume collapsed immediately and steadily after the trigger bar -- 515 -> 253 -> 156 -> 72
-> 81 -> 142 (reclaim) -- no continuation whatsoever. The whole 5-bar episode stayed inside a tight
~0.6pt band. An isolated volume spike on the trigger bar with zero follow-through, matching
-008/-009's signature, not -010's sustained decline. TRADE #8 remained open and unaffected
throughout (still ~-0.5R to -0.6R, clear of stop and MGMT-004 trigger); trade mechanics ran
unconditionally each bar, confirmed via `open_trade_state.json` (mgmt004_fired/control_closed both
still false throughout). No S5 trigger at any point.

---

## Q4-P007-013

```
GATE_ORIGIN_BAR          1749 (2020-10-28 00:00:00 UTC) -- immediately after Q4-P007-012 resolved
                          REJECTED one bar earlier; same overall consolidation
CONTEXT                    bars 1744-1748 were the quietest stretch of this session (volume 72-253,
                          tight ~1.6pt range 1904.37-1905.97)
TRIGGER_BAR                 1749 -- open 1905.34, low 1902.513, close 1902.948, 2.875pt intrabar
                          range (far larger than anything in the preceding week)
CAUSAL_H1_EMA50_AT_1749      1905.307
GAP                           -2.36pt -- largest gap magnitude of any candidate opened this session
VOLUME                         313 -- more than 2x the immediate 72-142 dead-zone baseline
TRADE_8_PROXIMITY             bar low 1902.513 only 0.403pt above initial_stop 1902.11 -- trade
                             mechanics ran unconditionally, confirmed stop NOT touched
```

**PRE-CLASSIFICATION:** a sharp, decisive break out of an unusually compressed/quiet session is more
credible than a marginal touch, even though absolute volume is moderate rather than dramatic.
Leaning toward taking this seriously, not pre-committing -- watching for real continuation vs an
early fade, and watching TRADE #8's stop given the proximity.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance, despite real trigger-bar magnitude
RESOLUTION_BAR         1750 (2020-10-28 00:30:00 UTC)
DURATION                2 bars (1749-1750)
DEEPEST_LOW              1902.513 (bar 1749)
HEAVIEST_VOLUME          313 (bar 1749, the trigger bar)
RECLAIM_CLOSE             1905.328 -- almost exactly back at the pre-break level (1905.34)
CAUSAL_H1_EMA50_AT_RESOLUTION 1905.309 (margin +0.02pt)
```

A complete 1-bar round-trip: bar 1750 fully reversed bar 1749's 2.875pt break within the very next
bar, landing back almost exactly at the pre-break level, with no continuation whatsoever. Volume on
the reversal (220) was lower than the break bar (313), unlike -011's reclaim -- but the decisive
fact is the full retrace itself, reading as a sharp spike/liquidity event rather than a sustained
directional break. The pre-classification correctly flagged real magnitude on the trigger bar but
explicitly withheld commitment pending follow-through; follow-through showed none. TRADE #8's stop
(1902.11) was tested closely (bar 1749 low 1902.513, only 0.403pt above) but never touched -- trade
mechanics ran unconditionally each bar, confirmed via `open_trade_state.json`. No S5 trigger at any
point.

---

## Q4-P007-014

```
GATE_ORIGIN_BAR          1761 (2020-10-28 03:00:00 UTC)
CONTEXT                    bars 1751-1760 drifted quietly 1904.8-1908.3, moderate-thin volume
                          (163-451, mostly 170-311), no strong directional character
TRIGGER_CLOSE                1905.152
TRIGGER_LOW                   1904.577 -- no fresh extreme; well inside the range since -013
CAUSAL_H1_EMA50_AT_1761       1905.423
GAP                            -0.27pt
VOLUME                          178 -- in line with the recent baseline, no acceleration
```

**PRE-CLASSIFICATION:** matches -008/-009/-012's trivial-touch signature, not -010/-013's sharper
character. Leaning REJECTED, not pre-committing. TRADE #8 remains open, well clear of stop and
MGMT-004 trigger.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1762 (2020-10-28 03:30:00 UTC)
DURATION                2 bars (1761-1762)
DEEPEST_LOW              1904.577 (bar 1761)
HEAVIEST_VOLUME          178 (bar 1761)
RECLAIM_CLOSE             1906.48
CAUSAL_H1_EMA50_AT_RESOLUTION 1905.434 (margin +1.05pt)
```

Reclaimed immediately, thin volume throughout (115 on the reclaim, below even the immediate baseline).
No continuation, no fresh extreme. Confirms the pre-classification's REJECTED lean exactly. TRADE #8
remained open throughout, well clear of stop and MGMT-004 trigger. No S5 trigger.

---

## Q4-P007-015

```
GATE_ORIGIN_BAR          1782 (2020-10-28 08:15:00 UTC) -- most credible signature since -010
LEAD-IN_DECLINE            bars 1775-1781, 7 bars, real volume throughout (262-523), closes drifting
                          from ~1910 (post bar-1774 high 1910.826) down to ~1906.2
ACCELERATION_BAR (trigger)  1782 -- open 1906.283, low 1902.511, close 1902.655, 3.772pt intrabar
                          range, volume 737 (heaviest single-bar volume of the window)
CAUSAL_H1_EMA50_AT_1782      1905.752
GAP                           -3.10pt -- largest gap magnitude of any candidate this session
LEVEL_NOTE                    low 1902.511 essentially matches -013's low (1902.513) and TRADE #8's
                             former stop (1902.11) -- tested twice now
```

**PRE-CLASSIFICATION:** unlike -013 (isolated spike, no lead-in), this episode has a genuine
multi-bar volume-accompanied decline BEFORE the acceleration bar -- closer to -010's evidentiary
shape, arguably stronger since volume was already elevated through the lead-in. Leaning toward
SUPPORT, not pre-committing -- watching for real continuation vs a fade. POSITION=FLAT; no MGMT-004
relevance.

**INTERIM NOTE (bar 1896, still open, not yet resolved):** this episode did not fade -- it became
the single largest directional move of Q4 so far. Price continued falling from bar 1782's trigger
(close 1902.655) all the way to a new Q4-replay-low of 1860.08 (bar 1893), ~42.6pt over 111 bars,
before a violent reversal on record volume (bars 1894-1896: 1306/4017/3396) triggered TRADE #9 (S5
LONG, see `AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md`). The gate remains open (no bar has closed back above
the causal H1 EMA50 yet) -- not resolving prematurely; the eventual RESOLUTION entry will cover the
full episode once a genuine reclaim occurs. One MAINTENANCE gap (GAP-169, bar 1832->1833, 60min)
logged inside this stretch.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM -- clearest, most dramatic instance in Q4 so far
RESOLUTION_BAR         1980 (2020-10-30 19:45:00 UTC)
DURATION                198 bars (1782-1979) -- by far the longest episode of the quarter
DEEPEST_LOW              1860.08 (bar 1893) -- genuine fresh Q4-replay extreme
HEAVIEST_VOLUME          4017 (bar 1895) -- roughly 8x this session's typical peak
RECLAIM_CLOSE             1879.34
CAUSAL_H1_EMA50_AT_RESOLUTION 1878.530 (margin +0.81pt)
```

Full arc: (1) a fast ~20pt decline in the first 18 bars (bar 1782 close 1902.655 -> bar 1800 close
1882.423, volume up to 1637); (2) an ~80-bar consolidation around 1877-1882 (bars 1820-1880); (3) a
final capitulation leg (bars 1890-1893, volume 1594-1817) to the episode low; (4) a violent reversal
on the heaviest volume of the entire Q4 replay (bars 1894-1896: 1306/4017/3396), mechanically
triggering TRADE #9 (S5 LONG, entry 1871.904); (5) TRADE #9 chopped in a tight ~1866-1876 range for
its full 48-bar hold, closing +0.2323R at MAX_HOLD (bar 1944) without the gate ever reclaiming; (6) a
further 36 bars of consolidation/gradual recovery (including a secondary dip to 1869.302 at bar
1955) before bar 1980 finally reclaimed on real volume (674). Every element of PATTERN-007's
definition is present at genuine scale: a severe break (largest decline of the quarter, fresh
extreme), heavy volume confirmation at the break, and an eventual reclaim on real volume, not a
marginal touch. No other P007 candidate could open during this stretch -- the gate is
one-directional and the lock was held continuously. TRADE #8 was already closed before this episode
began; TRADE #9 is the only trade that overlapped it -- both subsystems processed independently
throughout per the durable control-flow ordering invariant. Two MAINTENANCE gaps (GAP-169, GAP-170)
logged inside the episode, both standard. Sixth genuinely-resolved SUPPORT instance in Q4 (after
Q4-P007-003, Q4-P007-004, Q4-P007-006, Q4-P007-007, Q4-P007-010), and by a wide margin the largest
in both duration and price magnitude.

---

## Q4-P007-016

```
GATE_ORIGIN_BAR          1994 (2020-10-30 23:15:00 UTC) -- still-elevated-volume regime following
                          Q4-P007-015's massive episode (bars 1981-1994 ran 700-2011 volume
                          throughout, well above the 100-500 baseline of most earlier candidates)
CONTEXT                    post-reclaim rally to a high of 1889.756 (bar 1987, volume 716-1726),
                          then a choppy top (bars 1988-1993, still 1052-2011 volume)
TRIGGER_CLOSE                1877.458
TRIGGER_LOW                   1875.946 -- 8pt intrabar range
CAUSAL_H1_EMA50_AT_1994       1879.174
GAP                            -1.72pt
VOLUME                          1483
```

**PRE-CLASSIFICATION:** genuinely ambiguous -- could be ordinary profit-taking/pullback within a
still-volatile post-capitulation regime (REJECTED), or the start of a renewed leg down after the
failed rally topped out (SUPPORT). Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         1996 (2020-10-31 00:00:00 UTC)
DURATION                3 bars (1994-1996)
DEEPEST_LOW              1874.804 (bar 1995) -- barely below 1994's own low, nowhere near -015's
                        episode low of 1860.08
HEAVIEST_VOLUME          1483 (bar 1994)
RECLAIM_CLOSE             1879.472
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.174 (margin +0.30pt)
```

Volume stayed elevated throughout (1483/1364/1058) but matched the whole surrounding window's regime
(700-2011 across bars 1981-1996), not a distinct acceleration relative to local baseline. Reads as
ordinary volatile churn within the still-active post-Q4-P007-015 regime. Confirms the
pre-classification's first scenario (ordinary pullback) over the second (renewed leg down). No trade
was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-017

```
GATE_ORIGIN_BAR          2003 (2020-10-31 01:30:00 UTC)
CONTEXT                    volume normalizing from the 700-2011 regime (bars 1981-1996) back to a
                          moderate 420-889 range across bars 1997-2002, drifting sideways-to-lower
                          1878.5-1882.8
TRIGGER_CLOSE                1878.167
TRIGGER_LOW                   1877.6 -- close to but does not undercut -016's episode low (1874.804)
CAUSAL_H1_EMA50_AT_2003       1879.284
GAP                            -1.12pt
VOLUME                          584 -- in line with the recent moderate baseline, no acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED, similar to -016's ordinary-chop signature, not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2004 (2020-10-31 01:45:00 UTC)
DURATION                2 bars (2003-2004)
DEEPEST_LOW              1877.6 (bar 2003)
HEAVIEST_VOLUME          584 (bar 2003)
RECLAIM_CLOSE             1879.678
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.284 (margin +0.39pt)
```

Reclaimed immediately, volume in line with the moderate baseline throughout, no continuation, no
fresh extreme. Confirms the pre-classification's REJECTED lean exactly. No trade was open; no
MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-018

```
GATE_ORIGIN_BAR          2012 (2020-10-31 03:30:00 UTC)
CONTEXT                    bars 2005-2011 held a tight 1878.5-1881.5 consolidation, thin-moderate
                          volume (277-757), no direction
TRIGGER_CLOSE                1877.747
TRIGGER_LOW                   1877.433 -- no fresh extreme vs -016/-017's recent lows
CAUSAL_H1_EMA50_AT_2012       1879.328
GAP                            -1.58pt
VOLUME                          454 -- unremarkable vs the recent baseline
```

**PRE-CLASSIFICATION:** leaning REJECTED, matching the ordinary-chop signature of -016/-017.
POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2027 (2020-11-01 23:45:00 UTC)
DURATION                15 bars (2012-2026)
DEEPEST_LOW              1873.504 (bar 2025) -- only a modest extension below -016/-017's recent lows
HEAVIEST_VOLUME          970 (bar 2025) -- a late bump, not sustained
RECLAIM_CLOSE             1879.468
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.023 (margin +0.45pt)
```

Mostly thin/moderate volume throughout (136-507), one late bump that wasn't sustained. GAP-171
(standard weekend, 50h, spanning US DST end) sat inside the episode. No sustained directional or
volume-accelerating character at any point -- an ordinary, unremarkable episode despite the longer
duration. No trade was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-019

```
GATE_ORIGIN_BAR          2214 (2020-11-04 00:15:00 UTC) -- direct aftermath of TRADE #11's dramatic
                          stop-out (bar 2209, volume 4229); volume stayed extraordinarily elevated
                          the whole way through (bars 2210-2213: 1222-2471)
TRIGGER_BAR                 2214 -- open 1903.888, high 1903.888, low 1890.952 (~13pt intrabar range,
                          one of the largest single-bar ranges of the whole Q4 replay), close 1895.168
CAUSAL_H1_EMA50_AT_2214      1895.910
GAP                            -0.74pt
VOLUME                          3478
```

**PRE-CLASSIFICATION:** judging 'elevated vs baseline' is genuinely hard since the whole surrounding
regime is elevated (same issue as -016), but the sheer scale of this bar's range and continued
extreme volume suggest real, still-unfolding volatility (likely continued 2020-11-03/04 US
election-period activity, noted factually not causally). Leaning toward taking this seriously, not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM -- borderline vs -011/-013's REJECTED pattern, distinguished
                    by a partial (not full) retracement
RESOLUTION_BAR         2217 (2020-11-04 01:00:00 UTC)
DURATION                3 bars (2214-2216)
DEEPEST_LOW              1883.225 (bar 2215) -- close to but not past bar 2209's earlier stop-run
                        wick of 1882.212
HEAVIEST_VOLUME          5175 (bar 2215) -- THE HEAVIEST SINGLE-BAR VOLUME OF THE ENTIRE Q4 REPLAY
RECLAIM_CLOSE             1896.603
CAUSAL_H1_EMA50_AT_RESOLUTION 1895.910 (margin +0.69pt)
```

Key distinguishing test vs -011/-013 (both REJECTED as full round-trip reversals): those reclaims
landed almost exactly back at their pre-break levels. This one did not -- the episode fell from
~1903.888 (pre-break) to 1883.225 (~20.7pt), and the reclaim bar closed at only 1896.603, about 65%
of the drop retraced. Price settled at a materially lower level, merely crossing back above the
(also-lower) causal H1 EMA50 rather than fully erasing the break -- the signature of a real, lasting
price-level shift, not a spike. Combined with record-breaking volume and a genuine 2-bar decline (not
a single isolated bar), this resolves SUPPORT. Sits inside the continued 2020-11-03/04 US
election-period volatility (TRADE #11's stop-out at bar 2209 was the immediately preceding event) --
noted factually, not causally. No trade was open; no MGMT-004 relevance. No S5 trigger. Seventh
genuinely-resolved SUPPORT instance in Q4 (after Q4-P007-003, Q4-P007-004, Q4-P007-006, Q4-P007-007,
Q4-P007-010, Q4-P007-015).

---

## Q4-P007-020

```
GATE_ORIGIN_BAR          2218 (2020-11-04 01:15:00 UTC) -- immediately after Q4-P007-019's reclaim
TRIGGER_CLOSE                1895.776
TRIGGER_LOW                   1894.641 -- no fresh extreme, sits inside -019's episode range
CAUSAL_H1_EMA50_AT_2218       1895.822
GAP                            -0.05pt -- hairline touch
VOLUME                          2415 -- still part of the same extreme regime, but magnitude is trivial
```

**PRE-CLASSIFICATION:** leaning REJECTED -- ordinary chop right at the EMA boundary, not a fresh
break -- though the still-elevated volume regime makes this harder to call with full confidence than
a quiet-market marginal touch. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2219 (2020-11-04 01:30:00 UTC)
DURATION                2 bars (2218-2219)
DEEPEST_LOW              1893.506 (bar 2219) -- no fresh extreme vs -019's episode range
HEAVIEST_VOLUME          2415 (bar 2218)
RECLAIM_CLOSE             1899.809
CAUSAL_H1_EMA50_AT_RESOLUTION 1895.822 (margin +3.99pt)
```

Immediate strong bullish reclaim, confirming the pre-classification's REJECTED lean exactly --
ordinary chop at the boundary followed by a strong bounce, not a fresh break. No trade was open; no
MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-021

```
GATE_ORIGIN_BAR          2233 (2020-11-04 04:45:00 UTC)
CONTEXT                    bars 2225-2232 chopped 1894.6-1903.3, volume 757-1492 (still elevated but
                          without directional character, oscillating both ways)
TRIGGER_CLOSE                1895.44
TRIGGER_LOW                   1894.626 -- close to but not below bar 2229's recent low (1894.884)
CAUSAL_H1_EMA50_AT_2233       1896.009
GAP                            -0.57pt
VOLUME                          1348 -- in line with the surrounding chop, no acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- ordinary two-sided chop, not a fresh break. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance, despite 19-bar duration
RESOLUTION_BAR         2252 (2020-11-04 05:45:00 UTC)
DURATION                19 bars (2233-2251)
DEEPEST_LOW              1887.103 (bar 2247) -- does not undercut -019's low (1883.225), no fresh
                        extreme
HEAVIEST_VOLUME          3033 (bar 2235) -- a real early spike, but not sustained
RECLAIM_CLOSE             1902.352
CAUSAL_H1_EMA50_AT_RESOLUTION 1895.431 (margin +6.92pt -- large mainly because the EMA itself lagged
                             down through the consolidation, not because the reclaim's own price move
                             was proportionally larger than -019's)
```

Applying the same round-trip test used for Q4-P007-019 (SUPPORT): pre-episode level was 1899.608
(bar 2233's open). Bar 2235's early volume spike led into a decline, then 16 bars of tight
1887.1-1896.7 consolidation with volume normalizing back toward baseline. The reclaim jumped back to
1902.352 -- essentially the SAME level the episode started from, a near-complete round trip, unlike
-019's reclaim which left price ~7pt below its pre-break level. This is the -011/-013/-020 'full
round-trip' signature, not -019's 'lasting level shift' signature. No trade was open; no MGMT-004
relevance. No S5 trigger.

---

## Q4-P007-022

```
GATE_ORIGIN_BAR          2273 (2020-11-04 09:45:00 UTC)
CONTEXT                    bars 2265-2272 chopped 1898-1909.7, volume still elevated (1015-1953, same
                          post-election regime as -021)
TRIGGER_CLOSE                1895.891
TRIGGER_LOW                   1895.696 -- a fresh dip below the 2265-2272 window's floor (1898.522)
CAUSAL_H1_EMA50_AT_2273       1897.061
GAP                            -1.17pt
VOLUME                          1361 -- in line with the surrounding range, no acceleration
```

**PRE-CLASSIFICATION:** a genuine modest new local low, but not dramatic, and volume isn't
distinctly elevated vs the immediate baseline. Genuinely uncertain -- will apply the round-trip test
at resolution (same as -019/-021). Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2280 (2020-11-04 10:45:00 UTC)
DURATION                7 bars (2273-2279)
DEEPEST_LOW              1893.296 (bar 2277) -- does not undercut -021's low (1887.103), no fresh
                        extreme
HEAVIEST_VOLUME          1361 (bar 2273, the trigger bar itself -- never matched again)
RECLAIM_CLOSE             1898.414
CAUSAL_H1_EMA50_AT_RESOLUTION 1897.138 (margin +1.28pt)
```

Volume declined steadily and continuously throughout (1361/1191/725/665/592/460/632), never
re-accelerating -- the opposite of volume confirmation. Note on the round-trip test applied to
-019/-021: this episode's retracement percentage happens to land numerically similar to -019's
(~61% vs ~65% of the move retraced) -- but the total magnitude here (8.36pt) is far smaller than
-019's (20.7pt, on record volume 5175), and this episode's volume never showed any confirmation at
all. Weighing overall severity and volume conviction rather than treating the retracement percentage
as a threshold -- reads as ordinary, thinning-volume chop. No trade was open; no MGMT-004 relevance.
No S5 trigger.

---

## Q4-P007-023

```
GATE_ORIGIN_BAR          2281 (2020-11-04 11:00:00 UTC) -- immediately after Q4-P007-022's resolution
TRIGGER_CLOSE                1896.886
TRIGGER_LOW                   1896.58 -- no fresh extreme
CAUSAL_H1_EMA50_AT_2281       1897.138
GAP                            -0.25pt
VOLUME                          468 -- thin, market finally calming from the post-election regime
```

**PRE-CLASSIFICATION:** leaning REJECTED, matching -020's ordinary-marginal-touch signature. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2283 (2020-11-04 11:30:00 UTC)
DURATION                3 bars (2281-2283)
DEEPEST_LOW              1896.222 (bar 2282)
HEAVIEST_VOLUME          468 (bar 2281)
RECLAIM_CLOSE             1897.824
CAUSAL_H1_EMA50_AT_RESOLUTION 1897.188 (margin +0.64pt)
```

Thin volume throughout (468/414/324), confirming the market has calmed from the post-election
extreme regime. No continuation, no fresh extreme. Confirms the pre-classification's REJECTED lean
exactly. No trade was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-024

```
GATE_ORIGIN_BAR          2528 (2020-11-09 22:45:00 UTC) -- unprecedented single-bar shock, zero
                          lead-in (bars 2515-2527 completely quiet: 1954-1961 range, volume 208-679)
TRIGGER_BAR                 2528 -- open 1953.899, high 1957.354, low 1935.042 (22.3pt intrabar
                          range, LARGEST OF THE ENTIRE Q4 REPLAY), close 1938.474
CAUSAL_H1_EMA50_AT_2528      1944.503
GAP                            -6.03pt -- largest gap magnitude of any candidate this session
VOLUME                          5318 -- THE HEAVIEST SINGLE-BAR VOLUME OF THE ENTIRE Q4 REPLAY,
                              exceeding -019's prior record (5175)
```

**PRE-CLASSIFICATION:** genuinely undecided. More comparable in shape to -013's isolated-spike
pattern (REJECTED, full 1-bar reversal) than -015/-019's multi-bar declines, but at vastly larger
scale and unprecedented volume. Leaning toward taking this seriously given the magnitude, not
pre-committing -- watching for a quick reversal (REJECTED lean) vs holding/extending (SUPPORT lean).
POSITION=FLAT; no MGMT-004 relevance.

**INTERIM NOTE (bar 2633, still open, not yet resolved):** this became, by a wide margin, the
largest episode of the entire Q4 replay. Bar 2529 (immediately after the trigger) alone printed a
38pt intrabar range on 8812 volume -- the heaviest single-bar volume of the entire replay -- and the
decline continued with sustained multi-thousand volume for many more bars (5951/3941/3423/5409/
5215/6167/4850/3399/2706/4534...) down to a new Q4-replay-low of 1850.53 (bar 2548), an ~88pt
decline from bar 2528's own open. Price then stabilized and ground back up over ~85 bars (2548-2632)
on moderating but still-elevated volume, triggering TRADE #15 (S5 LONG, entry 1883.906) before the
gate has reclaimed. GAP-177 (standard, 60min) logged inside this stretch. Not resolving prematurely
-- the eventual RESOLUTION entry will cover the full episode once a genuine reclaim occurs.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM -- overwhelmingly the largest, most unambiguous instance in Q4
RESOLUTION_BAR         2812 (2020-11-12 21:45:00 UTC)
DURATION                284 bars (2528-2811) -- by far the longest episode of the quarter
DEEPEST_LOW              1850.53 (bar 2548) -- new Q4-replay-low, deepest of the entire replay
HEAVIEST_VOLUME          8812 (bar 2529) -- THE HEAVIEST SINGLE-BAR VOLUME OF THE ENTIRE Q4 REPLAY,
                        exceeding the next-largest (-019's 5175) by 70%
RECLAIM_CLOSE             1877.074
CAUSAL_H1_EMA50_AT_RESOLUTION 1875.756 (margin +1.32pt)
```

Bar 2529 alone printed a 38pt intrabar range on record volume, followed by many more bars of
sustained multi-thousand volume declining to the episode low -- an ~88pt decline from bar 2528's own
open, ~103pt from bar 2528's trigger close. After the low, price spent the remaining ~264 bars
stabilizing/grinding higher, never printing a fresh low again, before reclaiming. Applying the
round-trip test used for -019/-021/-022: pre-episode level (1953.899) vs reclaim close (1877.074)
leaves a ~76.8pt shortfall -- an even more pronounced lasting level shift than -019's, nowhere close
to a round trip. TRADE #15 opened and stopped out (-1.0R) entirely inside this episode. Three
MAINTENANCE gaps (GAP-177/178/179) sat inside the episode, no weekend gaps. A coincident S5
breakout trigger also surfaced on this exact reclaim bar -- per the durable control-flow ordering
invariant, P007 reasoning took priority for this bar's commit; the S5 signal is deferred, not
dropped, and will re-check naturally on the next bar. Eighth genuinely-resolved SUPPORT instance in
Q4 (after Q4-P007-003, Q4-P007-004, Q4-P007-006, Q4-P007-007, Q4-P007-010, Q4-P007-015,
Q4-P007-019), and by a wide margin the largest in every dimension.

---

## Q4-P007-025

```
GATE_ORIGIN_BAR          2830 (2020-11-13 02:15:00 UTC) -- TRADE #16 open (entry 1877.526, currently
                          ~1875.2, well clear of stop 1867.594; trade mechanics ran unconditionally)
CONTEXT                    bars 2822-2829 gently declined 1883->1875, moderate volume (350-799), no
                          acceleration
TRIGGER_CLOSE                1875.2
TRIGGER_LOW                   1874.331 -- no fresh extreme
CAUSAL_H1_EMA50_AT_2830       1876.296
GAP                            -1.10pt
VOLUME                          799 -- in line with the immediate baseline
```

**PRE-CLASSIFICATION:** leaning REJECTED -- ordinary gentle drift, not a fresh break. Not
pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2831 (2020-11-13 02:30:00 UTC)
DURATION                2 bars (2830-2831)
DEEPEST_LOW              1874.331 (bar 2830)
HEAVIEST_VOLUME          799 (bar 2830)
RECLAIM_CLOSE             1877.27
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.296 (margin +0.97pt)
```

Reclaimed immediately, thin volume throughout, no continuation, no fresh extreme. Confirms the
pre-classification's REJECTED lean exactly. TRADE #16 remained open throughout, well clear of stop
and MGMT-004 trigger. No S5 trigger.

---

## Q4-P007-026

```
GATE_ORIGIN_BAR          2834 (2020-11-13 03:15:00 UTC) -- TRADE #16 open, well clear of stop and
                          MGMT-004; trade mechanics ran unconditionally
CONTEXT                    bars 2832-2834 very quiet, thin volume (245-311), tiny drift lower
TRIGGER_CLOSE                1876.073
CAUSAL_H1_EMA50_AT_2834      1876.361
GAP                            -0.29pt
```

**PRE-CLASSIFICATION:** leaning REJECTED -- trivial marginal touch. Not pre-committing.
