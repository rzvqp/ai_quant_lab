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
TRIGGER_BAR           340 (2020-10-06 16:00:00 UTC)
RESOLUTION_BAR         487 (2020-10-08 06:45:00 UTC)
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
TRIGGER_BAR           787 (2020-10-13 12:45:00 UTC) -- close 1916.054, real volume 1929, first close
                      below the causal H1 EMA50 (1918.2) since the bar-608-trade-era rally began.
                      Immediate, real-volume follow-through: bar 788 close 1909.671 (vol 2718, H1
                      candle closes this bar), bar 789 close 1907.557 (vol 2747).
STRUCTURAL_LEVEL      Not independently identified against a specific pre-registered price level
                      (unlike Q4-P007-001/002/003, which broke a specifically-named prior low) --
                      this is a descriptive gap of the retrospective identification, disclosed rather
                      than backfilled with an invented level.
RESOLUTION_BAR         878 (2020-10-14 12:30:00 UTC) -- close 1905.436 > causal H1 EMA50 1904.592
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
RESOLUTION_BAR         1402 (2020-10-22 05:30:00 UTC)
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
ESCALATION_BAR           1429 (2020-10-22 12:00:00-12:15:00 UTC) -- genuinely different character
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
ESCALATION_BAR (real trigger)  1429 (2020-10-22 12:15:00 UTC)
RESOLUTION_BAR                  1506 (2020-10-23 08:30:00 UTC)
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
RESOLUTION_BAR             1608 (2020-10-26 11:00:00 UTC)
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
GATE_ORIGIN_BAR          1631 (2020-10-26 16:45:00 UTC) -- retroactively confirmed once bar 1632's
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
RESOLUTION_BAR         1633 (2020-10-26 17:15:00 UTC)
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
GATE_ORIGIN_BAR          1634 (2020-10-26 17:30:00 UTC) -- only 1 bar after Q4-P007-008 resolved
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
RESOLUTION_BAR         1658 (2020-10-27 00:30:00 UTC)
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
RESOLUTION_BAR         1708 (2020-10-27 13:00:00 UTC)
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
GATE_ORIGIN_BAR          1710 (2020-10-27 13:30:00 UTC) -- immediately after Q4-P007-010's reclaim
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
RESOLUTION_BAR         1711 (2020-10-27 13:45:00 UTC)
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
RESOLUTION_BAR         1980 (2020-10-30 12:00:00 UTC)
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
GATE_ORIGIN_BAR          1994 (2020-10-30 15:30:00 UTC) -- still-elevated-volume regime following
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
RESOLUTION_BAR         1996 (2020-10-30 16:00:00 UTC)
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
GATE_ORIGIN_BAR          2003 (2020-10-30 17:45:00 UTC)
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
RESOLUTION_BAR         2004 (2020-10-30 18:00:00 UTC)
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
GATE_ORIGIN_BAR          2012 (2020-10-30 20:00:00 UTC)
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
RESOLUTION_BAR         2027 (2020-11-02 01:45:00 UTC)
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
GATE_ORIGIN_BAR          2214 (2020-11-04 02:30:00 UTC) -- direct aftermath of TRADE #11's dramatic
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
RESOLUTION_BAR         2217 (2020-11-04 03:15:00 UTC)
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
GATE_ORIGIN_BAR          2218 (2020-11-04 03:30:00 UTC) -- immediately after Q4-P007-019's reclaim
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
RESOLUTION_BAR         2219 (2020-11-04 03:45:00 UTC)
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
GATE_ORIGIN_BAR          2233 (2020-11-04 07:15:00 UTC)
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
RESOLUTION_BAR         2252 (2020-11-04 12:00:00 UTC)
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
GATE_ORIGIN_BAR          2273 (2020-11-04 17:15:00 UTC)
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
RESOLUTION_BAR         2280 (2020-11-04 19:00:00 UTC)
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
GATE_ORIGIN_BAR          2281 (2020-11-04 19:15:00 UTC) -- immediately after Q4-P007-022's resolution
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
RESOLUTION_BAR         2283 (2020-11-04 19:45:00 UTC)
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
GATE_ORIGIN_BAR          2528 (2020-11-09 12:00:00 UTC) -- unprecedented single-bar shock, zero
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
RESOLUTION_BAR         2812 (2020-11-12 14:00:00 UTC)
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
GATE_ORIGIN_BAR          2830 (2020-11-12 18:30:00 UTC) -- TRADE #16 open (entry 1877.526, currently
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
RESOLUTION_BAR         2831 (2020-11-12 18:45:00 UTC)
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
GATE_ORIGIN_BAR          2834 (2020-11-12 19:30:00 UTC) -- TRADE #16 open, well clear of stop and
                          MGMT-004; trade mechanics ran unconditionally
CONTEXT                    bars 2832-2834 very quiet, thin volume (245-311), tiny drift lower
TRIGGER_CLOSE                1876.073
CAUSAL_H1_EMA50_AT_2834      1876.361
GAP                            -0.29pt
```

**PRE-CLASSIFICATION:** leaning REJECTED -- trivial marginal touch. Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2835 (2020-11-12 19:45:00 UTC)
DURATION                2 bars (2834-2835)
DEEPEST_LOW              1876.073 (bar 2834)
HEAVIEST_VOLUME          382 (bar 2835)
RECLAIM_CLOSE             1876.595
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.361 (margin +0.23pt)
```

Reclaimed immediately, thin volume throughout, no continuation, no fresh extreme. Confirms the
pre-classification's REJECTED lean exactly. TRADE #16 remained open throughout. No S5 trigger.

---

## Q4-P007-027

```
GATE_ORIGIN_BAR          2837 (2020-11-12 20:15:00 UTC) -- immediately after -026's reclaim; TRADE
                          #16 open, well clear of stop and MGMT-004
TRIGGER_CLOSE                1875.685
TRIGGER_LOW                   1875.192 -- marginally undercuts -026's low (1876.073) by ~0.9pt
CAUSAL_H1_EMA50_AT_2837       1876.361
GAP                            -0.68pt
```

**PRE-CLASSIFICATION:** leaning REJECTED -- continuation of the same trivial, thin chop pattern as
-025/-026. Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2843 (2020-11-12 21:45:00 UTC)
DURATION                6 bars (2837-2842)
DEEPEST_LOW              1874.154 (bar 2840)
HEAVIEST_VOLUME          527 (bar 2841)
RECLAIM_CLOSE             1876.416
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.355 (margin +0.06pt -- essentially dead-flat)
```

Extremely thin volume throughout (152-527), tight range, no directional conviction at any point. No
fresh extreme. TRADE #16 remained open throughout. No S5 trigger.

---

## Q4-P007-028

```
GATE_ORIGIN_BAR          2846 (2020-11-12 23:30:00 UTC) -- TRADE #16 open, well clear of stop and
                          MGMT-004; trade mechanics ran unconditionally
CONTEXT                    bars 2843-2846 extremely thin volume (143-160), tight range, continuing
                          the same dead chop as -025 through -027
```

**PRE-CLASSIFICATION:** leaning REJECTED. Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2847 (2020-11-12 23:45:00 UTC)
DURATION                2 bars (2846-2847)
DEEPEST_LOW              1875.405 (bar 2846)
HEAVIEST_VOLUME          160 (bar 2846)
RECLAIM_CLOSE             1876.71
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.379 (margin +0.33pt)
```

Reclaimed immediately, very thin volume, no continuation, no fresh extreme. TRADE #16 remained open
throughout. No S5 trigger.

---

## Q4-P007-029

```
GATE_ORIGIN_BAR          2848 (2020-11-12 23:45:00 UTC) -- immediately after -028's reclaim
TRIGGER_CLOSE                1876.03
TRIGGER_LOW                   1875.576 -- no fresh extreme
VOLUME                          120 -- very thin, same dead-chop regime as -025 through -028
```

**PRE-CLASSIFICATION:** leaning REJECTED. TRADE #16 remains open, well clear of stop and MGMT-004.
Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2851 (2020-11-13 00:30:00 UTC)
DURATION                3 bars (2848-2850)
DEEPEST_LOW              1874.198 (bar 2850)
HEAVIEST_VOLUME          321 (bar 2850)
RECLAIM_CLOSE             1877.443
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.366 (margin +1.08pt)
```

Thin/moderate volume throughout, tight range, no directional conviction, no fresh extreme. TRADE #16
remained open throughout. No S5 trigger.

---

## Q4-P007-030

```
GATE_ORIGIN_BAR          2862 (2020-11-13 03:15:00 UTC) -- right after TRADE #16's MAX_HOLD close
TRIGGER_CLOSE                1876.48
TRIGGER_LOW                   1876.474 -- no fresh extreme
VOLUME                          191 -- thin, same dead-chop regime as -025 through -029
```

**PRE-CLASSIFICATION:** leaning REJECTED. POSITION=FLAT. Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2863 (2020-11-13 03:45:00 UTC)
DURATION                2 bars (2862-2863)
DEEPEST_LOW              1876.17 (bar 2863)
HEAVIEST_VOLUME          212 (bar 2863)
RECLAIM_CLOSE             1877.383
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.628 (margin +0.75pt)
```

Reclaimed immediately, thin volume, no continuation, no fresh extreme. No trade was open; no
MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-031

```
GATE_ORIGIN_BAR          2867 (2020-11-13 04:30:00 UTC)
TRIGGER_CLOSE                1876.642
CAUSAL_H1_EMA50_AT_2867      1876.645
GAP                            -0.003pt -- a hairline touch, essentially noise
VOLUME                          125 -- thin
```

**PRE-CLASSIFICATION:** leaning REJECTED. POSITION=FLAT. Not pre-committing.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2868 (2020-11-13 05:00:00 UTC)
DURATION                2 bars (2867-2868)
DEEPEST_LOW              1876.579 (bar 2867)
HEAVIEST_VOLUME          125 (bar 2867)
RECLAIM_CLOSE             1877.422
CAUSAL_H1_EMA50_AT_RESOLUTION 1876.645 (margin +0.78pt)
```

Reclaimed immediately, very thin volume, no continuation, no fresh extreme. Confirms the
pre-classification's REJECTED lean exactly. No trade was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-032

```
GATE_ORIGIN_BAR          2885 (2020-11-13 09:00:00 UTC)
CONTEXT                    bars 2878-2884 chopped 1876-1880.9, moderate volume (208-562), no strong
                          direction
TRIGGER_CLOSE                1876.28
TRIGGER_LOW                   1876.028 -- modest fresh dip below the recent floor (1877.152)
CAUSAL_H1_EMA50_AT_2885       1876.962
GAP                            -0.68pt
VOLUME                          416 -- in line with the surrounding range, no acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- ordinary chop, not a fresh break. Not pre-committing.
POSITION=FLAT.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         2887 (2020-11-13 09:45:00 UTC)
DURATION                2 bars (2885-2886)
DEEPEST_LOW              1875.965 (bar 2886) -- only a modest extension, no meaningful new extreme
HEAVIEST_VOLUME          416 (bar 2885)
RECLAIM_CLOSE             1879.384
CAUSAL_H1_EMA50_AT_RESOLUTION 1877.043 (margin +2.34pt)
```

No sustained volume confirmation. No trade was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-033

```
GATE_ORIGIN_BAR          2988 (2020-11-16 12:00:00 UTC) -- another unprecedented single-bar shock,
                          similar in shape to Q4-P007-024's opening bar (2528), zero lead-in (bars
                          2953-2987 completely quiet: 1888-1898 range, volume 206-362)
TRIGGER_BAR                 2988 -- open 1892.904, high 1893.156, low 1864.541 (28.6pt intrabar
                          range), close 1869.628
CAUSAL_H1_EMA50_AT_2988      1885.822
GAP                            -16.19pt -- by far the largest gap magnitude of the entire session
VOLUME                          5983 -- exceeds -024's own trigger-adjacent volume (5318 at bar 2528)
```

**PRE-CLASSIFICATION:** given -024's own precedent -- an isolated shock bar with zero lead-in that
became the largest, most significant genuine SUPPORT instance in the whole replay -- taking this
very seriously from the outset. Not pre-committing until follow-through is actually observed.
POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM
RESOLUTION_BAR         2996 (2020-11-16 14:00:00 UTC) -- coincident S5 trigger deferred, see below
DURATION                8 bars (2988-2995) -- shorter than -024's 284 bars, but unambiguous on volume
DEEPEST_LOW              1864.541 (bar 2988) -- 28.4pt decline from the episode's own open, though it
                        does not undercut -024's all-time-replay low (1850.53)
HEAVIEST_VOLUME          5983 (bar 2988)
RECLAIM_CLOSE             1886.113
CAUSAL_H1_EMA50_AT_RESOLUTION 1884.853 (margin +1.26pt)
```

Volume stayed heavily elevated across the ENTIRE episode, not just the trigger bar --
5983/5532/2613/1540/1200/1397/979/2190 across bars 2988-2995, a real multi-bar continuation of
participation, unlike -011/-013's isolated single-bar spikes. Round-trip test (same as -019/-021/
-022/-024): pre-episode level 1892.904 vs reclaim close 1886.113 leaves a ~6.8pt shortfall (~76%
retraced, ~24% unretraced) -- a real, if partial, lasting level shift, not a full round trip. A
coincident S5 breakout trigger surfaced on this exact reclaim bar (bar 2996) -- P007 took priority
per the durable control-flow ordering invariant, S5 deferred not dropped, the same mechanism already
validated after -024 (TRADE #16 opened one bar later). This bar falls on 2020-11-16, plausibly a
continuation of the same broad volatility regime as -024's 2020-11-09 shock -- noted factually, not
causally. No trade was open; no MGMT-004 relevance. Ninth genuinely-resolved SUPPORT instance in Q4
(after Q4-P007-003, Q4-P007-004, Q4-P007-006, Q4-P007-007, Q4-P007-010, Q4-P007-015, Q4-P007-019,
Q4-P007-024).

---

## Q4-P007-034

```
GATE_ORIGIN_BAR          3055 (2020-11-17 05:30:00 UTC)
CONTEXT                    bars 3050-3054 thin volume (121-255), tight range, no direction
TRIGGER_CLOSE                1886.254
TRIGGER_LOW                   1884.891 -- a modest fresh dip
CAUSAL_H1_EMA50_AT_3055       1886.775
GAP                            -0.52pt
VOLUME                          542 -- a real step-up (2-4x the immediate baseline), though modest
                              in absolute terms
```

**PRE-CLASSIFICATION:** some character here but modest scale -- not pre-committing, watching for
real continuation vs an early fade. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         3056 (2020-11-17 06:00:00 UTC)
DURATION                2 bars (3055-3056)
DEEPEST_LOW              1884.891 (bar 3055)
HEAVIEST_VOLUME          542 (bar 3055)
RECLAIM_CLOSE             1886.95
CAUSAL_H1_EMA50_AT_RESOLUTION 1886.775 (margin +0.18pt)
```

The volume step-up on the trigger bar did not sustain into a second bar (274 vs 542). No
continuation, no fresh extreme. No trade was open; no MGMT-004 relevance. No S5 trigger.

---

## Q4-P007-035

```
GATE_ORIGIN_BAR          3057 (2020-11-17 06:00:00 UTC) -- immediately after -034's reclaim
TRIGGER_CLOSE                1885.884
TRIGGER_LOW                   1884.339 -- a marginal fresh dip below -034's own low (1884.891)
CAUSAL_H1_EMA50_AT_3057       1886.775
GAP                            -0.89pt
VOLUME                          472 -- in line with the recent baseline, no acceleration
```

**PRE-CLASSIFICATION:** reads as continuation of the same ordinary chop, not a fresh break. Leaning
REJECTED. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         3058 (2020-11-17 06:30:00 UTC)
DURATION                2 bars (3057-3058)
DEEPEST_LOW              1884.339 (bar 3057)
HEAVIEST_VOLUME          472 (bar 3057)
RECLAIM_CLOSE             1887.602
CAUSAL_H1_EMA50_AT_RESOLUTION 1886.782 (margin +0.82pt)
```

No continuation, no fresh extreme. No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 learning-audit guidance -- not a formal rule):** matches the
emerging volume-persistence + fresh-extreme discriminator's REJECTED profile exactly -- no volume
sustaining past the trigger bar (472 -> 397, no growth), no fresh extreme, full reclaim within 1
bar. Fourth consecutive REJECTED reading of the same dead-chop stretch (-032 through -035),
consistent with the discriminator's own prediction, not a counterexample.

---

## Q4-P007-036

```
GATE_ORIGIN_BAR          3083 (2020-11-17 12:30:00 UTC)
CONTEXT                    bars 3078-3082 thin-moderate volume (196-392), tight range, no direction
TRIGGER_CLOSE                1887.068
TRIGGER_LOW                   1886.978 -- a modest step up in volume but still thin in absolute terms
CAUSAL_H1_EMA50_AT_3083       1887.289
GAP                            -0.22pt
VOLUME                          444
```

**PRE-CLASSIFICATION:** leaning REJECTED on the actual evidence for this bar. Not pre-committing.
POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the emerging
discriminator's SUPPORT-leaning signature (no sustained/growing volume, no fresh extreme) --
consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         3085 (2020-11-17 13:15:00 UTC)
DURATION                2 bars (3083-3084)
DEEPEST_LOW              1886.35 (bar 3085) -- barely below 3084's low, well inside the broader range
HEAVIEST_VOLUME          1007 (bar 3085, the RECLAIM bar, not the break)
RECLAIM_CLOSE             1888.154
CAUSAL_H1_EMA50_AT_RESOLUTION 1887.289 (margin +0.87pt)
```

Volume actually grew across the episode (444 -> 547 -> 1007), but the growth landed on the reclaim
bar, not the break -- the opposite of PATTERN-007's signature, matching -011's established profile
exactly. No fresh extreme. No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance):** a genuine test of the emerging discriminator,
not just a confirmation -- volume DID sustain/grow across the episode, superficially resembling the
SUPPORT-leaning pattern, yet the actual reasoning (where the volume landed, no fresh extreme) still
correctly separates it from -024/-033's genuine signature. Shows the discriminator is not a simple
"volume grew = SUPPORT" rule -- where the volume lands and whether a fresh extreme prints still
matter more than raw volume growth alone.

---

## Q4-P007-037

```
GATE_ORIGIN_BAR          3094 (2020-11-17 15:15:00 UTC)
CONTEXT                    bars 3092-3093 pulling back from TRADE #20's entry (1890.787 -> 1888.132),
                            still inside the same broad 1886-1893.5 range this whole stretch has
                            chopped in since bar ~3080
TRIGGER_CLOSE                1887.4
TRIGGER_LOW                   1886.482 -- NOT a fresh low (shallower than bar 3091's 1886.297)
CAUSAL_H1_EMA50_AT_3094       1887.5614
GAP                            -0.161pt -- a marginal, barely-below-EMA close
VOLUME                          888 -- below the recent active-bar range (1156-1266) but above the
                                 thin dead-chop baseline (196-444) seen earlier in this stretch
```

**PRE-CLASSIFICATION:** leaning REJECTED on the actual evidence for this bar -- a shallow,
non-extreme dip inside an already-established chop range, not a fresh structural break. Not
pre-committing. **POSITION=LONG (TRADE #20, open since bar 3092, entry 1890.787, stop 1886.33) --
this bar's close (1887.4) and low (1886.482) do not threaten the stop; MGMT-004 has not fired (needs
close >= 1895.244).**
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the emerging
discriminator's SUPPORT-leaning signature (no fresh extreme, volume below the recent active range
rather than accelerating) -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         3096 (2020-11-17 15:45:00 UTC)
DURATION                3 bars (3094-3096)
DEEPEST_LOW              1884.739 (bar 3095) -- a genuine fresh extreme on a LOW basis, deeper than
                          anything else in this stretch (incl. TRADE #19's stop-run low of 1886.297)
HEAVIEST_VOLUME          907 (bar 3095, the break/continuation bar) -- barely above bar 3094's 888,
                          and higher than the reclaim bar's 623
RECLAIM_CLOSE             1888.707
CAUSAL_H1_EMA50_AT_RESOLUTION 1887.5614 (margin +1.15pt)
```

A genuinely mixed case, not a clean read either way. TRADE #20 was open through bar 3094 and closed
(STOP, bar 3095) before this resolved; no MGMT-004 relevance (never fired). No S5 trigger this
episode (POSITION=FLAT since bar 3095).
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this is the sharpest test of
the emerging discriminator so far. Taken alone, the fresh-extreme low at bar 3095 (1884.739, a
genuine new stretch-low on a LOW basis) points toward SUPPORT. But every other component points the
other way: (1) that low was a wick, not a close -- bar 3095 closed back at 1887.42, essentially flat
versus the EMA, the same intrabar-wick-gets-bought character as TRADE #19's and TRADE #20's own
stop-runs rather than a structural break; (2) the reclaim close (1888.707) lands almost exactly where
price was sitting before the gate origin (bar 3093 close 1888.132) -- a full round-trip, not a
partial one; (3) volume did NOT persist or grow into the reclaim -- it peaked mid-episode (907) and
fell on the reclaim bar (623), the same "growth-not-sustained-to-reclaim" shape that argued REJECTED
at -036. The reasoning here is that a fresh extreme on a bare LOW basis, by itself, is not sufficient when the
CLOSE never meaningfully breaks and the round-trip is full -- consistent with the
discriminator being a composite of correlated signals, not any single one being decisive alone. This
episode is recorded as a genuine test that partially disconfirms a naive single-factor reading of the
"fresh extreme" component, not as a confirmation.

---

## Q4-P007-038

```
GATE_ORIGIN_BAR          3097 (2020-11-17 16:00:00 UTC) -- immediately after -037's reclaim
CONTEXT                    bar 3096 closed 1888.707, reclaiming well clear of the EMA; this bar
                            dips straight back through it
TRIGGER_CLOSE                1887.348
TRIGGER_LOW                   1886.941 -- NOT a fresh extreme (well above -037's 1884.739 and TRADE
                              #19/#20's stop-run lows)
CAUSAL_H1_EMA50_AT_3097       1887.5614
GAP                            -0.213pt
VOLUME                          468 -- modest, below -037's episode range (623-907), close to the
                                 thin dead-chop baseline (196-444) seen earlier in this stretch
```

**PRE-CLASSIFICATION:** leaning REJECTED on the actual evidence for this bar -- another shallow,
non-extreme dip immediately following -037's own REJECTED resolution, same dead-chop character. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the emerging
discriminator's SUPPORT-leaning signature (no fresh extreme, volume modest and not accelerating) --
consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         3186 (2020-11-18 15:15:00 UTC)
DURATION                90 bars (3097-3186) -- by far the longest episode in the Q4 replay so far
DEEPEST_LOW              1863.772 (bar 3173) -- a genuine multi-session low, not a shallow wick (the
                          bar's own CLOSE, 1868.404, was also well below the EMA, not just the low)
HEAVIEST_VOLUME          2554 (bar 3173) -- the SAME bar as the deepest low: volume and price extreme
                          coincide, a capitulation signature
RECLAIM_CLOSE             1883.53 (bar 3186)
CAUSAL_H1_EMA50_AT_RESOLUTION 1882.6746 (margin +0.855pt)
```

This is Q4-P007-038's own episode, not -037's -- gate origin bar 3097, immediately following -037's
REJECTED resolution. Across bars 3098-3172 (73 bars) price ground down gradually and thinly (mostly
100-500 volume) from ~1887 to ~1875, before a genuine capitulation move at bars 3172-3173 (volume
1842, then 2554 -- the heaviest single-bar volume in the Q4 replay to date) drove the low to 1863.772.
Recovery from there was gradual and multi-bar (13 bars from the low to this reclaim), not a sharp
V-reversal. TRADE #21 (opened bar 3181) was open throughout this resolution and remains open,
unaffected -- P007 classification does not influence trade management. A coincident S5 trigger fired
this same bar (bis=10, same OR as TRADE #21) but is not actionable since a position is already open;
no deferral needed.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the clearest, most
textbook-consistent case yet -- every component of the emerging discriminator agrees, in contrast to
-037's mixed signals immediately prior. (1) The fresh extreme is genuine on a CLOSE basis, not just a
wick (bar 3173 closed at 1868.404, deep below the EMA). (2) The heaviest volume of the episode landed
on the break itself (bar 3173), not the reclaim -- matching -024/-033's genuine PATTERN-007 signature,
the opposite of -011/-036's REJECTED signature. (3) The reclaim close (1883.53) sits meaningfully
below the pre-episode level (bar 3096 close 1888.707) -- a ~79% retracement of the full decline
(1888.707 to 1863.772), still ~5.2pt short of a full round-trip, not a full reclaim back to the
pre-episode price -- consistent with, though on the higher end of, the SUPPORT-leaning discriminator's
established partial-retracement profile (not being treated as a rigid threshold).
Recorded as a strong confirmation, immediately following a case (-037) that showed the same
components can disagree -- underscoring that it is their AGREEMENT, not any single factor, that makes
this reading confident.

---

## Q4-P007-039

```
GATE_ORIGIN_BAR          3187 (2020-11-18 15:30:00 UTC) -- immediately after -038's reclaim
CONTEXT                    bar 3186 closed 1883.53, reclaiming -038's episode; this bar pulls back
                            below the EMA again, a retest rather than a fresh break
TRIGGER_CLOSE                1881.93
TRIGGER_LOW                   1880.51 -- NOT a fresh extreme (well above -038's 1863.772)
CAUSAL_H1_EMA50_AT_3187       1882.6746
GAP                            -0.745pt -- moderate, deeper than -037's shallow dips but far short of
                                 -038's genuine break
VOLUME                          1027 -- moderate, comparable to several bars within -038's own episode,
                                 not a clear acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- reads as a retest/pullback immediately following a
genuine reclaim, not a fresh structural break. Not pre-committing. POSITION=LONG (TRADE #21, open
since bar 3181, entry 1877.656, stop 1869.032) -- this bar's close/low do not threaten the stop;
MGMT-004 has not fired (needs close >= 1886.280). A coincident S5 trigger fired this bar (bis=11,
same OR) but is not actionable since a position is already open.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the emerging
discriminator's SUPPORT-leaning signature (no fresh extreme, volume moderate but not clearly
accelerating past the episode's own recent range) -- consistent with, not the basis for, the REJECTED
lean.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         3365 (2020-11-20 14:00:00 UTC)
DURATION                179 bars (3187-3365) -- the longest episode in the Q4 replay so far,
                          surpassing -038's 90 bars
DEEPEST_LOW              1852.792 (bar 3271) -- a genuine fresh extreme, well beyond -038's own
                          1863.772
HEAVIEST_VOLUME          1992 (bar 3271) -- the same bar as the deepest low, a capitulation signature;
                          the reclaim bar itself (3365) also carried real volume (1698), but the
                          absolute heaviest still sits on the break
RECLAIM_CLOSE             1877.586 (bar 3365)
CAUSAL_H1_EMA50_AT_RESOLUTION 1868.667 (margin +8.92pt -- a sharp, decisive reclaim, not a marginal one)
```

TRADE #21 (opened bar 3181, resolved STOP bar 3218) was open for the first 32 bars of this episode
and closed before it resolved; no trade was open for the remaining ~147 bars. Price declined steadily
from ~1881 (bar 3219) through ~1866 (bar 3230), ~1862 (bar 3240), to the capitulation low at bar 3271,
then based in a 1857-1869 range for roughly 93 bars (3272-3364) -- a genuine, extended consolidation
at the new, lower level, not a quick bounce -- before a sharp single-bar breakout at bar 3365 (close
jumping from 1867.497 to 1877.586, ~10pt in one bar) that reclaimed the EMA decisively and
simultaneously triggered a fresh S5 OR breakout (bis=5, informational only this bar -- position was
FLAT, so per the established coincident-signal handling this S5 trigger is deferred and expected to
re-surface on the next bar once this P007 gate clears). GAP-183 already logged (inside TRADE #21's
prior hold); a standard MAINTENANCE gap (60min) fell inside this episode's basing period, to be logged
in the gap ledger as GAP-184.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** an even more compelling case
than -038 by several measures -- deeper fresh extreme, volume-price coincidence at the capitulation
bar, AND (unlike -038's 13-bar recovery) an extended ~93-bar basing period at the new lower level
before the reclaim, rather than an immediate bounce. The reclaim close sits ~81% of the way back
toward the pre-episode level (bar 3186 close 1883.53), ~5.9pt short of a full round-trip -- again a
partial, not full, retracement, in the same range as -038's ~79%. The one point of nuance: the
reclaim bar's own volume (1698) is substantial, not negligible, so this is not a story of "volume
only on the break" -- it is heaviest-on-the-break WITH a genuinely well-participated reclaim, which
reads as a decisive structural shift rather than a thin, unconvincing bounce. Recorded as a further
confirmation that when fresh-extreme, volume-on-the-break, and partial-retracement agree, the reading
has been reliable across this stretch of Q4 so far -- while still treating this as an ongoing test,
not a settled rule, per standing instruction.

---

## Q4-P007-040

```
GATE_ORIGIN_BAR          3436 (2020-11-23 08:45:00 UTC)
CONTEXT                    bars 3415-3435 a calm, thin-volume drift (mostly 50-550 volume) in the
                            1872-1876 range, well after TRADE #22's own hold; this bar breaks below
                            with a deeper gap than -037/-039's shallow origins, though still moderate
TRIGGER_CLOSE                1869.158
TRIGGER_LOW                   1868.754 -- a modest fresh local low relative to the last ~20 bars,
                              comparable to (marginally below) TRADE #22's own hold low of 1868.925
CAUSAL_H1_EMA50_AT_3436       1871.0008
GAP                            -1.843pt -- deeper than -037/-039's origins but not a dramatic break
VOLUME                          426 -- roughly in line with the 3429-3435 stretch (411-551), not a
                                 clear acceleration
```

**PRE-CLASSIFICATION:** genuinely uncertain, leaning slightly REJECTED -- the gap is deeper than the
shallow dips seen at -037/-039's origins, and there is a modest fresh local low, but volume is not
accelerating past the immediate recent range, and the preceding stretch was calm/thin rather than
showing building pressure. Not pre-committing; this one needs the reclaim/continuation evidence to
resolve properly. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuinely mixed read on the
emerging discriminator -- modest fresh extreme present, but volume not accelerating -- unlike -038/
-039's unambiguous readings. Recorded honestly as ambiguous going in, not forced into a confident
lean.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         3709 (2020-11-26 08:00:00 UTC)
DURATION                273 bars (3436-3709) -- by far the longest episode in the Q4 replay so far,
                          well beyond -039's 179 bars
DEEPEST_LOW              1800.424 (bar 3555) -- a confirmed genuine all-time-low-so-far for the Q4
                          replay (is_new_low flag true against full prior sealed history)
HEAVIEST_VOLUME          7296 (bar 3460) -- the heaviest bar of this episode by a wide margin, though
                          NOT a new Q4-wide record (is_new_vol_record flag false -- an even larger
                          volume bar exists somewhere earlier in the already-sealed history)
RECLAIM_CLOSE             1816.928 (bar 3709), margin only +0.48pt -- a marginal, not decisive, reclaim
CAUSAL_H1_EMA50_AT_RESOLUTION 1816.4514
```

The starting context (bars 3437-3459) was the same calm drift the pre-classification described, then
bar 3460 broke violently -- close fell from 1866.246 to 1841.655 in a single bar (~24.6pt) on 7296
volume, this session's largest single-bar move, landing 2020-11-23 14:45 UTC. Heavy volume continued
for several more bars (4852, 2552, 1824, 1761, 1917), then an extended, sustained decline (bars
3465-3540, ~75 bars) carried price from ~1833 to ~1810. A second heavy-volume wave (2898, 2184, 2993,
1690, 1688 across bars 3550-3555) drove the final capitulation to 1800.424. From there, an extremely
long, slow, low-volume basing period (bars 3556-3709, ~154 bars, mostly 100-500 volume) ground
gradually higher in a 1800-1813 range before finally closing marginally above the EMA. No S5 trigger
fired anywhere in this 273-bar span (POSITION stayed FLAT throughout, so nothing was deferred). GAP-
186, -187, -188 (all standard MAINTENANCE, 60min) logged inside this episode.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the largest, most genuine
structural event of the Q4 replay so far by every measure (magnitude, duration, and the record-
setting low), but its SHAPE is meaningfully different from -038/-039: those were V-shaped or
gradual-then-decisive reclaims; this one is a violent break followed by an extremely long, slow,
low-volume grind that only marginally closes above a heavily-lagging EMA (+0.48pt, the thinnest
reclaim margin of any SUPPORT case so far), with the retracement only ~23% of the full decline (16.5pt
of a 71.1pt move) -- far more partial than -038/-039's ~79-81%. The core discriminator components
still agree (fresh extreme genuine on both low and close basis; heaviest volume unambiguously on the
break, not the reclaim -- the reclaim bar itself carried only 480, quite modest), so this is recorded
SUPPORT with confidence. But the marginal reclaim margin is a genuinely new texture worth tracking: it
raises the open, unresolved question of whether a bare EMA-cross with a razor-thin margin after a move
this large represents the same kind of "reclaim" as -038/-039's more decisive ones, or whether it
should be watched for a possible re-test/failure in subsequent bars -- an open question for future
episodes to test, not a conclusion drawn here.

---

## Q4-P007-041

```
GATE_ORIGIN_BAR          3710 (2020-11-26 08:15:00 UTC) -- the very next bar after -040's marginal
                            reclaim (bar 3709, margin only +0.48pt)
CONTEXT                    directly tests the concern flagged in -040's own resolution: does a
                            razor-thin reclaim after a massive move hold, or fail immediately?
TRIGGER_CLOSE                1815.828
TRIGGER_LOW                   1815.718 -- NOT a fresh extreme (well above -040's 1800.424)
CAUSAL_H1_EMA50_AT_3710       1816.3976
GAP                            -0.570pt -- shallow, similar magnitude to -037/-039's origins
VOLUME                          625 -- moderate, not a clear spike
```

**PRE-CLASSIFICATION:** genuinely uncertain. On the surface this reads like the shallow, REJECTED-
leaning dips seen at -037/-039 (no fresh extreme, moderate volume). But the context is different: this
is an IMMEDIATE failure of -040's own marginal reclaim, one bar after it printed -- directly bearing
on the open question -040 raised about whether that reclaim was durable. Leaning slightly toward
REJECTED on the bar's own evidence (no fresh extreme, no volume acceleration), but flagging this
honestly as a live test of -040's own uncertainty rather than a fresh, independent read. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the emerging
discriminator's SUPPORT-leaning signature on its own bar (no fresh extreme, volume not accelerating)
-- but this episode's resolution will be read together with -040 as a pair, not in isolation, given
how directly it follows.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         3947 (2020-12-01 05:45:00 UTC)
DURATION                238 bars (3710-3947) -- the second-longest episode in the Q4 replay so far,
                          after -040's 273 bars; see note below on how -040/-041 relate
DEEPEST_LOW              1764.57 (bar 3843) -- deeper than -040's own confirmed low (1800.424),
                          another genuine fresh extreme continuing the same structural decline
HEAVIEST_VOLUME          3477 (bar 3807) -- landed ~36 bars BEFORE the ultimate low (bar 3843), not
                          coincident with it -- a genuine departure from -038/-039/-040's pattern of
                          volume peaking exactly at the extreme
RECLAIM_CLOSE             1787.212 (bar 3947), margin +0.61pt -- again marginal, similar texture to
                          -040's own +0.48pt reclaim
CAUSAL_H1_EMA50_AT_RESOLUTION 1786.5975
```

TRADE #23 (opened bar 3889, MAX_HOLD exit bar 3937, +0.78R) was open for part of this episode and
closed before it resolved. This episode directly follows -040's own resolution (bar 3709) and its
gate origin is the very next bar (3710) -- effectively continuing the SAME underlying decline rather
than being a fully independent event: pre-episode level (bar 3709 close 1816.928) fell to 1764.57, a
further ~52pt beyond where -040 already stood, before this reclaim.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this pair (-040 then -041)
directly and prospectively tested the durability question -040's own resolution raised -- and the
concern was borne out: -040's marginal +0.48pt reclaim did NOT hold, failing on the very next bar
(-041's gate origin), and price fell another ~36pt beyond -040's own low before finally basing here.
Read together, -040 and -041 look less like two separate SUPPORT instances and more like one
continuous, still-ongoing structural decline that P007 detected in two segments because of a brief,
thin EMA-crossing pause in between. Two further nuances worth flagging honestly: (1) retracement here
is ~43% (22.6 of 52.4pt) -- a genuinely intermediate value between -040's ~23% and -038/-039's
~79-81%, not clustering neatly with either; (2) the heaviest volume (bar 3807) did NOT coincide with
the ultimate low (bar 3843) this time, landing well before it -- a partial departure from the
volume-price-coincidence signature seen in -038/-039/-040's capitulation bars. Both discriminator
components still point toward SUPPORT overall (fresh extreme genuine; heaviest volume still
unambiguously on the break side, not the reclaim), so this is recorded SUPPORT with confidence, but
these nuances are recorded as genuine, useful tests, not swept aside -- the discriminator's individual
components appear to have some texture/variance even within confirmed SUPPORT cases, which is itself
informative for how much weight any single component should carry going forward.

---

## Q4-P007-042

```
GATE_ORIGIN_BAR          3948 (2020-12-01 06:00:00 UTC) -- the very next bar after -041's reclaim,
                            the third consecutive instance of this exact shape (-040 reclaim -> -041
                            origin next bar; -041 reclaim -> -042 origin next bar)
TRIGGER_CLOSE                1785.841
TRIGGER_LOW                   1785.841 -- NOT a fresh extreme (well above -041's 1764.57)
CAUSAL_H1_EMA50_AT_3948       1786.5975
GAP                            -0.757pt -- shallow, similar magnitude to -039/-041's origins
VOLUME                          296 -- modest, no acceleration
```

**PRE-CLASSIFICATION:** genuinely uncertain, treated individually rather than assumed to repeat the
prior pattern. On its own bar evidence this leans REJECTED (no fresh extreme, no volume
acceleration) -- similar shallow shape to -041's own origin. But given -040/-041 revealed that this
stretch's marginal reclaims have NOT been holding, this deserves the same honest, non-assumed
treatment -- it will be judged on its own eventual evidence, not on the streak. Not pre-committing.
POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature on its own bar. Whatever this resolves to will be a further data point on how
reliably a marginal EMA-cross reclaim holds in this specific volatile stretch -- genuinely useful
regardless of which way it goes, not a foregone conclusion.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         3952 (2020-12-01 07:00:00 UTC)
DURATION                5 bars (3948-3952)
DEEPEST_LOW              1785.093 (bar 3949) -- NOT a fresh extreme by any measure, nowhere near
                          -041's 1764.57
HEAVIEST_VOLUME          431 (bar 3952, the RECLAIM bar itself) -- volume actually grew across the
                          episode (296 -> 242 -> 212 -> 322 -> 431), landing on the reclaim, not the
                          break -- the classic REJECTED signature, matching -011/-036
RECLAIM_CLOSE             1787.784 -- ABOVE the pre-episode level (bar 3947 close 1787.212) by
                          +0.57pt, a full round-trip and slight overshoot, not a partial retracement
CAUSAL_H1_EMA50_AT_RESOLUTION 1786.6216 (margin +1.16pt)
```

The answer to the question this episode's own pre-classification posed: this one does NOT hold up as
SUPPORT -- it breaks the streak. No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the cleanest REJECTED signature
in a while -- every component agrees in the REJECTED direction (no fresh extreme, volume growing into
the reclaim not the break, a full-plus round-trip). Read together with -040/-041/-042 as a triplet:
after two genuine, deep structural SUPPORT episodes, the market appears to be settling into calmer,
shallower chop -- this shallow dip did not carry the same weight as its two immediate predecessors,
and the individual, non-assumed reasoning applied to it (rather than extrapolating from the "marginal
reclaims keep failing" streak) correctly caught that. Evidence that treating each candidate on its own
merits, as instructed, matters in practice -- assuming this would repeat the prior pattern would have
been wrong here.

---

## Q4-P007-043

```
GATE_ORIGIN_BAR          4263 (2020-12-04 15:45:00 UTC)
CONTEXT                    a genuinely volatile stretch precedes this: bar 4254 (5190 volume, a wide
                            1833.318-1847.976 whipsaw range) kicked off several bars of elevated
                            volume (2847/2530/2048/1912), a push up to ~1848, then a reversal down
                            through bars 4259-4263 on still-elevated volume (1341-1664)
TRIGGER_CLOSE                1832.146
TRIGGER_LOW                   1829.276 -- a fresh LOCAL low relative to the last ~30 bars, but NOT a
                              fresh extreme relative to the full stretch (bar 4172's 1823.772, well
                              earlier, sits deeper)
CAUSAL_H1_EMA50_AT_4263       1833.5809
GAP                            -1.435pt -- a meaningful, not shallow, break
VOLUME                          1450 -- moderate, below the 4254-4258 volume spike but still elevated
                                 versus the thin baseline seen earlier in this range (bars 4180-4240,
                                 mostly 130-620)
```

**PRE-CLASSIFICATION:** genuinely uncertain -- an intermediate case, not a clean read either way. The
preceding volatility (the 4254 whipsaw and its aftermath) is real, elevated activity, distinguishing
this from the simplest shallow-dip origins (-037/-039/-042). But the trigger bar's own low is only a
local, not a full-stretch, fresh extreme, and the gate-origin bar's own volume (1450) is well off the
spike's peak (5190). Not pre-committing; leaning neither way strongly. POSITION=FLAT; no MGMT-004
relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a mixed read -- meaningful
recent volatility/volume argues some weight toward SUPPORT, but the lack of a genuine full-stretch
fresh extreme and the trigger bar's own moderate (not accelerating) volume argue the other way.
Recorded honestly as a close call, not forced into a lean it doesn't earn.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4264 (2020-12-04 16:00:00 UTC)
DURATION                2 bars (4263-4264) -- the fastest resolution since the shallowest dead-chop
                          episodes
DEEPEST_LOW              1829.276 (bar 4263, the gate origin itself)
HEAVIEST_VOLUME          1450 (bar 4263, the break bar) -- modestly higher than the reclaim bar's 995,
                          but not by a dramatic margin
RECLAIM_CLOSE             1833.948 -- essentially a FULL round-trip back to the pre-episode level
                          (bar 4262 close 1834.968, only -1.02pt short)
CAUSAL_H1_EMA50_AT_RESOLUTION 1833.5809 (margin +0.37pt)
```

The pre-classification's genuine uncertainty resolves cleanly once the actual reclaim evidence is in:
a 2-bar episode, no fresh extreme, and an essentially complete round-trip. No trade was open; no
MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the preceding volatility (bar
4254's whipsaw) turned out not to carry through into this specific gate origin's own episode -- by the
time this candidate opened, the market had already absorbed that volatility and this dip was just an
ordinary, quickly-reversed pullback. A useful reminder that recent volatility in the surrounding
context does not automatically transfer weight to the NEXT candidate that happens to follow it --
each episode's own evidence (duration, round-trip, volume placement) still has to be judged on its
own terms.

---

## Q4-P007-044

```
GATE_ORIGIN_BAR          4266 (2020-12-04 16:30:00 UTC) -- one bar after -043's own reclaim
TRIGGER_CLOSE                1832.914
TRIGGER_LOW                   1831.698 -- NOT a fresh extreme (well above the recent 1829.276/
                              1823.772 lows)
CAUSAL_H1_EMA50_AT_4266       1833.5246
GAP                            -0.611pt -- shallow, similar magnitude to -043's own origin
VOLUME                          585 -- modest, below both -043's break-bar (1450) and reclaim-bar
                                 (995) volumes
```

**PRE-CLASSIFICATION:** leaning REJECTED on the actual evidence for this bar -- same shallow,
choppy-around-the-EMA character as -043, treated on its own merits rather than assumed from that
precedent. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature (no fresh extreme, volume modest and not accelerating) -- consistent with, not the
basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4269 (2020-12-04 17:15:00 UTC)
DURATION                4 bars (4266-4269)
DEEPEST_LOW              1831.698 (bar 4266, the gate origin itself)
HEAVIEST_VOLUME          585 (bar 4266, the break bar) -- modestly higher than the following bars
                          (406/320/382), but shallow in absolute terms throughout
RECLAIM_CLOSE             1834.647 -- OVERSHOOTS the pre-episode level (bar 4265 close 1834.052) by
                          +0.60pt, a full-plus round-trip, not a partial retracement
CAUSAL_H1_EMA50_AT_RESOLUTION 1833.5165 (margin +1.13pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuinely mixed-but-leaning
case, similar in shape to -043: the heaviest volume did land on the break, a SUPPORT-consistent
detail, but it was shallow in absolute terms, and the full-plus round-trip and lack of any fresh
extreme dominate the overall read. REJECTED, matching the pre-classification's lean and continuing the
now-established character of this particular price zone (~1830-1835) as a choppy, low-conviction area
following the earlier massive moves -- three of the last four candidates in this immediate stretch
(-042, -043, -044) have resolved REJECTED.

---

## Q4-P007-045

```
GATE_ORIGIN_BAR          4325 (2020-12-07 08:15:00 UTC)
CONTEXT                    a very quiet, thin 56-bar drift (bars 4270-4323, mostly 87-485 volume) in
                            the 1833-1841 range, then a step-up in volume as price declined into this
                            bar (bars 4324-4325: 1112/1093, well above the stretch's baseline)
TRIGGER_CLOSE                1834.06
TRIGGER_LOW                   1833.412 -- NOT a fresh extreme (bar 4290's 1833.113, within this same
                              stretch, sits slightly deeper)
CAUSAL_H1_EMA50_AT_4325       1835.4190
GAP                            -1.359pt -- meaningful, not shallow
VOLUME                          1093 -- a genuine acceleration versus the very thin recent baseline
                                 (87-485), though the deepest low is not exceeded
```

**PRE-CLASSIFICATION:** genuinely uncertain, leaning slightly toward SUPPORT on the volume evidence --
the two-bar volume step-up (1112, 1093) breaking out of an unusually thin, quiet stretch is a real
signal, even though the low itself is not a fresh extreme. Not pre-committing; this is the kind of
case the volume-persistence component of the emerging discriminator was meant to help distinguish from
ordinary noise, and it will be watched for whether the volume actually persists into further bars or
decays immediately. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuine test of the volume-
persistence component in isolation from the fresh-extreme component (they disagree here) -- useful
regardless of outcome for understanding whether volume alone can carry weight when the low doesn't
confirm it.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         4345 (2020-12-07 13:15:00 UTC)
DURATION                20 bars (4325-4345)
DEEPEST_LOW              1822.253 (bar 4326) -- a genuine fresh extreme, well beyond the 1833.113
                          recent-stretch floor; printed the bar IMMEDIATELY after the gate origin
HEAVIEST_VOLUME          2494 (bar 4326) -- the SAME bar as the deepest low, a capitulation signature
RECLAIM_CLOSE             1834.788 -- ~89% retracement of the decline (12.5 of 14.1pt), still ~1.6pt
                          short of the pre-episode level (bar 4324 close 1836.361)
CAUSAL_H1_EMA50_AT_RESOLUTION 1834.6704 (margin +0.12pt -- thin, but the underlying episode is not)
```

The pre-classification framed this as a test of volume-persistence in isolation from fresh-extreme --
that framing turned out to be premature: the fresh extreme showed up on the very next bar (4326), not
at the gate origin itself. Once that bar is in, this reads as a straightforward, if compressed, SUPPORT
case: fresh extreme and heaviest volume coincide exactly, the classic capitulation signature. The
reclaim margin itself is thin (+0.12pt), but that thinness reflects the EMA's own proximity to price at
this point in the replay, not a weak underlying move -- the ~89% retracement and volume-price
coincidence are the more decisive evidence. No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a useful correction to how the
pre-classification framed the test -- the "isolation" premise (volume without a confirming fresh
extreme) didn't hold up once one more bar of evidence arrived. Worth remembering for future
pre-classifications: an initial read based on the gate-origin bar alone can be superseded quickly by
the very next bar, and the eventual classification should follow the fuller episode, not lock in to the
opening bar's framing.

---

## Q4-P007-046

```
GATE_ORIGIN_BAR          4494 (2020-12-09 04:00:00 UTC)
CONTEXT                    TRADE #28 stopped out 3 bars earlier (bar 4491); this bar continues that
                            decline
TRIGGER_CLOSE                1856.634
TRIGGER_LOW                   1855.698 -- a genuine fresh local low relative to recent trading
                              (TRADE #28's hold ranged ~1861-1874; no bar in the last several dozen
                              has closed or wicked this low), though not a multi-week extreme (bar
                              3271's 1852.792, from Q4-P007-040's episode, sits deeper further back)
CAUSAL_H1_EMA50_AT_4494       1859.3514
GAP                            -2.717pt -- meaningfully deep, well beyond the shallow dead-chop
                                 origins seen recently
VOLUME                          763 -- a real acceleration versus the 328-635 seen in the two
                                 preceding bars
```

**PRE-CLASSIFICATION:** genuinely uncertain, leaning slightly toward SUPPORT -- a meaningful gap depth,
a genuine local fresh low, and a real volume acceleration all point that direction, though none of
them are as decisive as -038/-039/-040/-041/-045's clearest cases. Not pre-committing. POSITION=FLAT;
no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** components lean the same
direction here (unlike -043's genuinely mixed case), but all at moderate rather than extreme
magnitude -- a useful mid-strength test case for the discriminator.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4497 (2020-12-09 04:45:00 UTC)
DURATION                4 bars (4494-4497)
DEEPEST_LOW              1855.698 (bar 4494, the gate origin itself)
HEAVIEST_VOLUME          763 (bar 4494, the break bar) -- clearly higher than the following bars
                          (321/372/201), a genuine SUPPORT-consistent detail
RECLAIM_CLOSE             1860.558 -- ~89% retracement of the decline (4.86 of 5.45pt), essentially a
                          near-complete round-trip back to the pre-episode level (bar 4493 close
                          1861.145)
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.4217 (margin +1.14pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the pre-classification flagged
this as a mid-strength test against -045's precedent, and that comparison resolves it: -045 had a
DRAMATIC fresh extreme (1822.253, far below anything recent) and capitulation-scale volume (2494)
alongside its own ~89% retracement, and still read SUPPORT because those components were so strong.
Here the fresh low (1855.698) is only modestly deeper than recent trading, and the volume (763) is a
real but modest acceleration, not a capitulation spike. When the retracement is this high (~89%,
essentially complete) and the supporting evidence is only moderate rather than dramatic, the round-
trip dominates the read. REJECTED -- a useful data point that magnitude, not just direction, of the
individual components matters when they're weighed against a near-complete retracement.

---

## Q4-P007-047

```
GATE_ORIGIN_BAR          4501 (2020-12-09 05:45:00 UTC)
TRIGGER_CLOSE                1859.196
TRIGGER_LOW                   1857.843 -- NOT a fresh extreme (well above -046's 1855.698)
CAUSAL_H1_EMA50_AT_4501       1859.4663
GAP                            -0.270pt -- shallow
VOLUME                          417 -- moderate, below bar 4500's 544, above the earlier 220/167
```

**PRE-CLASSIFICATION:** leaning REJECTED on the actual evidence for this bar -- shallow, ordinary
dip continuing this choppy zone, no fresh extreme, no clear volume acceleration. Not pre-committing.
POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4502 (2020-12-09 06:00:00 UTC)
DURATION                2 bars (4501-4502)
DEEPEST_LOW              1857.843 (bar 4501, the gate origin itself)
HEAVIEST_VOLUME          417 (bar 4501, the break bar) -- essentially flat versus the reclaim bar's
                          409, no meaningful distinguishing signal either way
RECLAIM_CLOSE             1861.572 -- OVERSHOOTS the pre-episode level (bar 4500 close 1859.702) by
                          +1.87pt, a full-plus round-trip
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.4663 (margin +2.11pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a clean, quick REJECTED read
matching the pre-classification's lean -- no fresh extreme, no distinguishing volume signal, and a
full-plus round-trip, all pointing the same direction with nothing to weigh against them.

---

## Q4-P007-048

```
GATE_ORIGIN_BAR          4506 (2020-12-09 07:00:00 UTC)
TRIGGER_CLOSE                1858.374
TRIGGER_LOW                   1858.374 -- no wick below the close; NOT a fresh extreme (well above
                              -046/-047's 1855.698/1857.843)
CAUSAL_H1_EMA50_AT_4506       1859.4557
GAP                            -1.082pt -- moderate
VOLUME                          567 -- moderate, similar to 498/520 in the preceding bars, no clear
                                 acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- another ordinary, moderate dip continuing this choppy
zone, no fresh extreme, no volume acceleration. Not pre-committing. POSITION=FLAT; no MGMT-004
relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4507 (2020-12-09 07:15:00 UTC)
DURATION                2 bars (4506-4507)
DEEPEST_LOW              1858.321 (bar 4507) -- marginally deeper than the gate origin's 1858.374,
                          not a meaningful fresh extreme
HEAVIEST_VOLUME          567 (bar 4506, the break bar) -- somewhat higher than the reclaim bar's 480,
                          not dramatically so
RECLAIM_CLOSE             1860.015 -- essentially a FULL round-trip back to the pre-episode level
                          (bar 4505 close 1860.244, only -0.23pt short)
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.4866 (margin +0.53pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** another clean REJECTED read
matching the pre-classification -- the third consecutive REJECTED resolution in this stretch (-046,
-047, -048), consistent with the ordinary, shallow-chop character this zone has settled into since
TRADE #28 closed.

---

## Q4-P007-049

```
GATE_ORIGIN_BAR          4515 (2020-12-09 09:15:00 UTC)
CONTEXT                    a sharp one-bar reversal: bar 4513 closed 1864.896 (session high 1865.356),
                            bar 4514 pulled back to 1863.164, then this bar dropped further to 1858.794
                            -- a ~4.4pt one-bar decline from bar 4514's close
TRIGGER_CLOSE                1858.794
TRIGGER_LOW                   1858.368 -- close to but NOT below the recent 1858.108 (bar 4510), not
                              a fresh extreme
CAUSAL_H1_EMA50_AT_4515       1859.7237
GAP                            -0.930pt -- moderate
VOLUME                          736 -- a real acceleration versus bar 4514's 543, similar in magnitude
                                 to earlier peaks in this stretch (768, 792)
```

**PRE-CLASSIFICATION:** leaning REJECTED -- the one-bar decline is sharper than the recent shallow
dips, but the low doesn't exceed the stretch's own recent floor and volume, while elevated, isn't
clearly beyond what this choppy zone has already shown. Not pre-committing. POSITION=FLAT; no MGMT-004
relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a modestly more active bar than
-046/-047/-048, but not clearly enough to break from their REJECTED pattern -- worth watching for
whether it resolves differently or continues the streak.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4516 (2020-12-09 09:30:00 UTC)
DURATION                2 bars (4515-4516)
DEEPEST_LOW              1858.368 (bar 4515, the gate origin itself)
HEAVIEST_VOLUME          736 (bar 4515, the break bar) -- clearly heavier than the reclaim bar's 374,
                          a real gap, though not capitulation-scale in absolute terms
RECLAIM_CLOSE             1862.91 -- essentially a FULL round-trip back to the pre-episode level (bar
                          4514 close 1863.164, only -0.25pt short)
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.7237 (margin +3.19pt -- a decisive reclaim)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the volume placement (clearly
heavier on the break) is the one SUPPORT-consistent detail, but an essentially complete round-trip and
no fresh extreme dominate -- the fourth consecutive REJECTED resolution in this stretch (-046 through
-049). Consistent with -046's own lesson: a single favorable component doesn't override a near-100%
retracement when the other evidence is only moderate.

---

## Q4-P007-050

```
GATE_ORIGIN_BAR          4519 (2020-12-09 10:15:00 UTC)
TRIGGER_CLOSE                1858.014
TRIGGER_LOW                   1856.192 -- deeper than -047/-048/-049's recent lows (1857.843/
                              1858.321/1858.368), a moderate fresh low, though still shallower than
                              -046's own 1855.698
CAUSAL_H1_EMA50_AT_4519       1859.7738
GAP                            -1.760pt -- meaningful
VOLUME                          715 -- a real acceleration versus bars 4517/4518's 521/496
```

**PRE-CLASSIFICATION:** genuinely uncertain, leaning slightly toward SUPPORT -- the moderate fresh low
and volume acceleration are real, similar in shape to -046, which still resolved REJECTED once the
round-trip evidence came in. Treating this as its own case, not assumed to repeat -046's outcome. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** another mid-strength test,
structurally similar to -046 -- will be judged on its own retracement/volume evidence at resolution,
not on the precedent alone.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4522 (2020-12-09 11:00:00 UTC)
DURATION                4 bars (4519-4522)
DEEPEST_LOW              1856.192 (bar 4519, the gate origin itself)
HEAVIEST_VOLUME          715 (bar 4519, the break bar) -- a real gap over the following bars
                          (473/282/339)
RECLAIM_CLOSE             1859.927 -- essentially EXACTLY the pre-episode level (bar 4518 close
                          1859.934, only -0.01pt short, a near-perfect round-trip)
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.7738 (margin +0.15pt -- thin)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the fifth consecutive REJECTED
resolution in this stretch (-046 through -050). As predicted going in, this played out structurally
like -046: a real volume gap on the break, but a round-trip even more complete than -046's (~100%
here vs -046's ~89%), which settles it firmly REJECTED. This stretch (since TRADE #28's stop, bars
~4494-4522) is now a clear, consistent example of a range where moderate-strength P007 triggers
repeatedly fail to represent genuine structural breaks -- five out of five in a row.

---

## Q4-P007-051

```
GATE_ORIGIN_BAR          4524 (2020-12-09 11:30:00 UTC) -- breaks decisively from the -046/-050
                            dead-chop stretch
TRIGGER_CLOSE                1853.937
TRIGGER_LOW                   1852.849 -- clearly deeper than -046's 1855.698 (the deepest of the
                              recent stretch), and very close to (0.06pt above) bar 3271's 1852.792
                              from -040's episode, one of the deepest points in the whole Q4 replay
CAUSAL_H1_EMA50_AT_4524       1859.7195
GAP                            -5.783pt -- by far the deepest gap of this whole recent stretch
VOLUME                          1138 -- clearly breaks out of the 715-767 ceiling seen across
                                 -046 through -050, a genuine acceleration
```

**PRE-CLASSIFICATION:** leaning SUPPORT -- this is qualitatively different from the five REJECTED
predecessors: a genuinely deep gap, a near-record fresh extreme, and volume clearly above anything
seen in this stretch. Not pre-committing; the reclaim/round-trip evidence still needs to confirm this,
but the magnitude here is a real step up. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the discriminator components
all agree at genuinely strong magnitude here, unlike the moderate -046/-049/-050 cases -- a useful
contrast that reinforces the "magnitude matters" lesson from the immediately preceding streak.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4530 (2020-12-09 13:00:00 UTC)
DURATION                6 bars (4524-4530)
DEEPEST_LOW              1851.636 (bar 4525) -- a genuine NEW RECORD low for this trading zone,
                          deeper than bar 3271's 1852.792 (from -040's episode); the bar's own CLOSE
                          (1853.82) also stayed convincingly below the EMA, not just a wick
HEAVIEST_VOLUME          1266 (bar 4530, the RECLAIM bar) -- essentially tied with bar 4525's 1251
                          (the deepest-low bar); NOT a clean break-side concentration
RECLAIM_CLOSE             1860.734 -- OVERSHOOTS the pre-episode level (bar 4523 close 1860.028) by
                          +0.71pt, a full-plus round-trip, completed in just 6 bars
CAUSAL_H1_EMA50_AT_RESOLUTION 1859.4882 (margin +1.25pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuinely novel tension case
-- the fresh extreme here is dramatic and real (a new record low for this whole trading zone, on a
close basis, not just a wick), qualitatively stronger than any REJECTED case seen so far. But every
confirmed SUPPORT case to date (-038/-039/-040/-041/-045) paired its fresh extreme with a PARTIAL
retracement (23-89%) and a genuinely extended process (20-273 bars); this episode instead round-tripped
completely (and overshot) in just 6 bars, and the heaviest volume landed on the reclaim, not cleanly on
the break. Read this way -- as a fast, aggressive liquidity-grab-and-reclaim rather than a genuine
multi-bar structural process -- REJECTED is the more consistent call: a full-plus round-trip has been
the single most reliable REJECTED signal across every prior episode, with zero exceptions, and this one
is both complete AND fast. The dramatic fresh extreme is recorded honestly as a genuine point of
tension, not dismissed -- but on balance it is not treated as sufficient on its own when the round-trip
and duration both point the other way, consistent with -043's own earlier lesson that a fresh extreme
alone does not override a full round-trip.

---

## Q4-P007-052

```
GATE_ORIGIN_BAR          4533 (2020-12-09 13:45:00 UTC)
TRIGGER_CLOSE                1859.108
TRIGGER_LOW                   1858.811 -- NOT a fresh extreme (well above -051's 1851.636)
CAUSAL_H1_EMA50_AT_4533       1859.3929
GAP                            -0.285pt -- shallow
VOLUME                          1040 -- elevated in absolute terms, but continuing the generally
                                 elevated volume regime seen since -051 (1125, 850 in the two
                                 preceding bars), NOT a clear acceleration relative to immediate
                                 context
```

**PRE-CLASSIFICATION:** leaning REJECTED -- shallow gap, no fresh extreme; the volume is high in
absolute terms but that reflects the generally more active period following -051's capitulation-and-
reclaim, not a distinguishing signal for this specific bar. Not pre-committing. POSITION=FLAT; no
MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a useful reminder that absolute
volume level matters less than volume RELATIVE to the immediate surrounding context -- this bar's 1040
would have looked dramatic against -046/-050's baseline, but is unremarkable against -051's own
elevated regime.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         4628 (2020-12-10 14:30:00 UTC)
DURATION                96 bars (4533-4628) -- a substantial, genuine structural episode, unlike
                          -051's fast 6-bar liquidity grab
DEEPEST_LOW              1825.579 (bar 4553) -- a genuine, dramatic new low, deeper than -051's own
                          1851.636 by ~26pt, approaching (though not exceeding) -040's historic
                          1800.424
HEAVIEST_VOLUME          3220 (bar 4538) -- one of the heaviest single-bar volumes in the whole Q4
                          replay, though 15 bars before the ultimate low (bar 4553), not exactly
                          coincident -- a similar nuance to -041's own volume/low timing
RECLAIM_CLOSE             1848.65 -- a ~64% retracement of the full decline (23.1 of 35.8pt), a
                          genuinely partial retracement, not full or overshooting
CAUSAL_H1_EMA50_AT_RESOLUTION 1846.3098 (margin +2.34pt)
```

A coincident S5 OR breakout fired the same bar (POSITION was FLAT); per established handling this is
deferred and expected to re-surface on the next bar. GAP-199 (standard MAINTENANCE) logged inside the
episode's basing period.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a clear, genuine SUPPORT case,
the sharpest contrast possible with the immediately preceding -051 tension episode. Same qualitative
ingredients as -038/-039/-040/-041/-045: a dramatic, genuinely record-approaching new low; massive
volume near the break (though not exactly coincident with the ultimate low, echoing -041); a partial,
not complete, retracement (~64%); and a substantial multi-day duration (96 bars) reflecting a genuine
structural process rather than a fast grab-and-reclaim. This pairing with -051 is itself useful: two
back-to-back episodes with genuinely deep fresh extremes resolved oppositely (REJECTED then SUPPORT)
because the round-trip completeness and duration -- not the extreme alone -- told the real story in
each case.

---

## Q4-P007-053

```
GATE_ORIGIN_BAR          4630 (2020-12-10 15:00:00 UTC) -- one bar after TRADE #29 opened
TRIGGER_CLOSE                1844.904
TRIGGER_LOW                   1842.92 -- NOT a fresh extreme (well above -052's 1825.579)
CAUSAL_H1_EMA50_AT_4630       1846.3098
GAP                            -1.406pt -- moderate
VOLUME                          1813 -- high in absolute terms, but roughly flat versus the two
                                 immediately preceding bars (bar 4628 reclaim 1808, bar 4629 TRADE #29
                                 entry 1724), not a clear acceleration relative to context
```

**PRE-CLASSIFICATION:** leaning REJECTED -- same "-052's own lesson" applies: absolute volume level
is high because this whole stretch has been active since -052's reclaim, but this bar's volume isn't
distinguishing relative to its immediate neighbors, and there's no fresh extreme. Not pre-committing.
POSITION=LONG (TRADE #29, open since bar 4629, entry 1847.771, stop 1834.287) -- this bar's low
(1842.92) and close (1844.904) do not threaten the stop; MGMT-004 has not fired (needs close >=
1861.255).
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature relative to its own immediate context -- consistent with, not the basis for, the
REJECTED lean.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         4718 (2020-12-11 14:00:00 UTC)
DURATION                89 bars (4630-4718)
DEEPEST_LOW              1824.184 (bar 4707) -- ANOTHER new record low for this zone, deeper even
                          than -052's own 1825.579 -- continuing the same broader decline
HEAVIEST_VOLUME          1813 (bar 4630, the GATE ORIGIN itself) -- a genuinely clean SUPPORT-
                          consistent placement, heaviest right at the break
RECLAIM_CLOSE             1840.514 -- a ~69% retracement of the decline (16.3 of 23.6pt), genuinely
                          partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1840.1202 (margin +0.39pt)
```

TRADE #30 (opened bar 4717) was open through this resolution and remains open, unaffected -- P007
classification does not influence trade management. A coincident S5 trigger fired this same bar
(bis=5, same OR as TRADE #30) but is not actionable since a position is already open.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** another clear SUPPORT case,
directly continuing -052's own episode as effectively a second leg of the same broader decline (deeper
low, same general zone, same eventual reclaim character). Unlike -051's tension case, this one has
every component pointing the same direction: heaviest volume cleanly at the break (an even cleaner
placement than -052's own 15-bar-early volume), a genuine new record low, a partial (not complete)
retracement, and a substantial 89-bar duration -- a textbook case with no real ambiguity.

---

## Q4-P007-054

```
GATE_ORIGIN_BAR          4719 (2020-12-11 14:15:00 UTC) -- one bar after -053's reclaim
TRIGGER_CLOSE                1836.242
TRIGGER_LOW                   1835.262 -- NOT deeper than -053's own record 1824.184, but a
                              meaningfully deep dip for a fresh gate origin
CAUSAL_H1_EMA50_AT_4719       1840.1196
GAP                            -3.878pt -- meaningfully deep
VOLUME                          1020 -- moderate-high but roughly in line with the recent elevated
                                 regime (1813, 1035), not a clear standout acceleration
```

**PRE-CLASSIFICATION:** genuinely uncertain -- the gap depth is notable, but volume doesn't clearly
distinguish itself from the recent elevated baseline, and the low isn't a fresh record. Not
pre-committing. POSITION=LONG (TRADE #30, open since bar 4717, entry 1840.106, stop 1831.794) -- this
bar's low/close do not threaten the stop; MGMT-004 has not fired (needs close >= 1848.418).
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuine mid-strength case,
similar in spirit to -046/-050 -- will be judged on its own round-trip evidence at resolution.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4721 (2020-12-11 14:45:00 UTC)
DURATION                3 bars (4719-4721)
DEEPEST_LOW              1834.956 (bar 4720) -- not a fresh record beyond -053's own 1824.184
HEAVIEST_VOLUME          1320 (bar 4720) -- coincides with the deepest-low bar, a genuine
                          SUPPORT-consistent detail
RECLAIM_CLOSE             1841.426 -- OVERSHOOTS the pre-episode level (bar 4718 close 1840.514) by
                          +0.91pt, a full-plus round-trip
CAUSAL_H1_EMA50_AT_RESOLUTION 1840.1196 (margin +1.31pt)
```

TRADE #30 remains open, unaffected. A coincident S5 trigger fired this same bar (same OR as TRADE
#30) but is not actionable since a position is already open.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the volume/low coincidence is a
genuine SUPPORT-consistent detail, but the low itself was not a fresh record and the round-trip
overshot completely -- REJECTED, matching the now-established pattern that a full-plus round-trip has
proven the single most reliable signal, overriding a favorable volume placement when the extreme
itself isn't dramatic.

---

## Q4-P007-055

```
GATE_ORIGIN_BAR          4735 (2020-12-11 18:15:00 UTC)
CONTEXT                    a push up to ~1846-1847 (bars 4722-4723, close to but short of MGMT-004's
                            1848.418) then a steady, thinning decline through bars 4724-4734 (volume
                            fading from 891 down to 173)
TRIGGER_CLOSE                1839.452
TRIGGER_LOW                   1838.904 -- NOT a fresh extreme for this zone
CAUSAL_H1_EMA50_AT_4735       1840.4933
GAP                            -1.041pt -- moderate
VOLUME                          445 -- a modest uptick from bar 4734's 173, but still well below the
                                 1424-1614 seen at the start of this batch, thin overall
```

**PRE-CLASSIFICATION:** leaning REJECTED -- a shallow, low-conviction dip at the tail of a thinning
decline, no fresh extreme, volume thin in absolute terms despite the small uptick. Not pre-committing.
POSITION=LONG (TRADE #30, open since bar 4717, entry 1840.106, stop 1831.794) -- this bar's low/close
do not threaten the stop; MGMT-004 has not fired (best approach was bar 4723's 1846.714, +0.79R, still
short of the +1.0R trigger).
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         4737 (2020-12-11 18:45:00 UTC)
DURATION                3 bars (4735-4737)
DEEPEST_LOW              1838.772 (bar 4736)
HEAVIEST_VOLUME          445 (bar 4735, the break bar) -- heaviest on the break, but thin in
                          absolute terms throughout the episode
RECLAIM_CLOSE             1840.746 -- a ~73% retracement of the decline (1.97 of 2.70pt), partial but
                          on a very small total move
CAUSAL_H1_EMA50_AT_RESOLUTION 1840.4933 (margin +0.25pt)
```

TRADE #30 remains open, unaffected. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a clean REJECTED read on
overall weakness rather than any single dominant signal -- every measure here (gap depth, volume,
total decline) was thin in absolute terms, consistent with a low-conviction dip rather than a genuine
structural break, regardless of the retracement percentage.

---

## Q4-P007-056

```
GATE_ORIGIN_BAR          4738 (2020-12-11 19:00:00 UTC) -- one bar after -055's own reclaim
TRIGGER_CLOSE                1839.648
TRIGGER_LOW                   1839.23 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_4738       1840.4933
GAP                            -0.845pt -- shallow-moderate
VOLUME                          302 -- thin, similar to -055's own thin episode
```

**PRE-CLASSIFICATION:** leaning REJECTED -- continuing the same thin, low-conviction character as
-055, no fresh extreme, no volume acceleration. Not pre-committing. POSITION=LONG (TRADE #30, open
since bar 4717, entry 1840.106, stop 1831.794) -- this bar's low/close do not threaten the stop;
MGMT-004 has not fired.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         4812 (2020-12-14 14:30:00 UTC)
DURATION                75 bars (4738-4812)
DEEPEST_LOW              1819.418 (bar 4795) -- ANOTHER new record low, deeper than -053's own
                          1824.184, continuing the exact same broader decline chain (-052 -> -053 ->
                          -056), each episode setting a new record
HEAVIEST_VOLUME          2309 (bar 4812, the RECLAIM bar) -- NOT cleanly on the break; bar 4796 (the
                          bounce right after the low) carried 1398, and bar 4807 (mid-consolidation)
                          carried 1545, but nothing at the actual low bar (4795, only 770)
RECLAIM_CLOSE             1837.814 -- an 86% retracement of the decline (18.4 of 21.3pt), high but
                          not complete or overshooting
CAUSAL_H1_EMA50_AT_RESOLUTION 1836.4906 (margin +1.32pt)
```

TRADE #31 (opened bar 4809) was open through this resolution and remains open, unaffected. A
coincident S5 trigger fired this same bar (same OR as TRADE #31) but is not actionable since a
position is already open.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a genuinely weighed case,
unlike -046/-049/-050/-054's cleaner REJECTED reads. The volume-on-reclaim placement is a real
REJECTED-consistent detail (echoing -011/-036's signature), and the 86% retracement alone would
usually lean REJECTED per -046's lesson. But this episode's SUBSTANTIAL 75-bar duration and its role
as the third consecutive episode in an unbroken record-low chain (-052 -> -053 -> -056, each deeper
than the last) carry more weight here than in the fast, isolated REJECTED cases -- this reads as a
genuine continuation of an already-established downtrend, not an isolated test. SUPPORT, with the
volume-placement nuance recorded honestly rather than smoothed over: not every confirmed SUPPORT case
has to match every component of the discriminator cleanly, and duration + chain-context are treated as
carrying real weight alongside (not simply overridden by) the retracement percentage.

---

## Q4-P007-057

```
GATE_ORIGIN_BAR          4813 (2020-12-14 14:45:00 UTC) -- one bar after -056's reclaim
TRIGGER_CLOSE                1833.246
TRIGGER_LOW                   1832.073 -- NOT deeper than -056's own record 1819.418
CAUSAL_H1_EMA50_AT_4813       1836.4906
GAP                            -3.245pt -- meaningfully deep
VOLUME                          1371 -- high in absolute terms but continuing the elevated regime
                                 around -056's reclaim (2309, bar 4812), not a clear acceleration
                                 relative to context
```

**PRE-CLASSIFICATION:** leaning REJECTED, similar in shape to -054 (which followed -053's reclaim the
same way) -- the gap depth is notable, but volume isn't distinguishing relative to the immediately
preceding elevated bars, and the low isn't a fresh record. Not pre-committing. POSITION=LONG (TRADE
#31, open since bar 4809, entry 1832.711, stop 1822.309) -- this bar's low (1832.073, below entry but
well above the stop) and close do not threaten the stop; MGMT-004 has not fired.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the direct echo of -054's own
shape (both following a reclaim by one bar, both deep-looking but volume-context-relative rather than
absolute) is a useful pattern to watch -- will be judged on its own resolution evidence, not assumed.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         4860 (2020-12-15 03:30:00 UTC)
DURATION                48 bars (4813-4860)
DEEPEST_LOW              1822.282 (bar 4820, TRADE #31's own stop-run low) -- very close to but NOT
                          exceeding -056's own record 1819.418; a fourth consecutive episode in the
                          same decline chain (-052 -> -053 -> -056 -> -057)
HEAVIEST_VOLUME          1371 (bar 4813, the GATE ORIGIN itself) -- a clean SUPPORT-consistent
                          placement, matching -056's own origin-heavy signature
RECLAIM_CLOSE             1833.524 -- a ~72% retracement of the decline (11.2 of 15.5pt), genuinely
                          partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1833.3689 (margin +0.16pt -- thin, though the episode itself is not)
```

TRADE #32 (opened bar 4823) was open through this resolution and remains open, unaffected -- best
close so far is this very bar's 1833.524 (+0.81R), still short of MGMT-004. GAP-202 (standard
MAINTENANCE) logged inside the episode.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** unlike -056's genuinely mixed
case, this one reads cleanly: heaviest volume sits right at the break (echoing -038/-045/-056's own
origin-heavy signature), the low is a near-record continuing the same well-established decline chain,
and the retracement is comfortably partial. The thin reclaim margin (+0.16pt) reflects EMA proximity,
not a weak underlying move, consistent with -045/-053's own pattern. A confident SUPPORT read, the
fourth consecutive confirmed episode in this decline chain.

---

## Q4-P007-058

```
GATE_ORIGIN_BAR          5014 (2020-12-16 19:00:00 UTC)
CONTEXT                    a calm, steady climb from ~1841 (bar 4872) to ~1863 (bar 4980), then a
                            gentle pullback to ~1854-1857 (bars 4995-5013, thin volume 180-300)
TRIGGER_CLOSE                1848.839
TRIGGER_LOW                   1848.552 -- NOT a fresh extreme (well above -057's 1822.282)
CAUSAL_H1_EMA50_AT_5014       1849.4245
GAP                            -0.586pt -- shallow, despite the dramatic bar
VOLUME                          3784 -- MASSIVE, among the heaviest single-bar volumes in the entire
                                 Q4 replay (comparable to -052's 3220, -038's 2554), a genuine outlier
                                 against the thin 180-500 baseline of the preceding weeks
```

**PRE-CLASSIFICATION:** genuinely uncertain -- an unusual combination: the gap is shallow (price had
been climbing steadily, so the EMA sat close by), but the volume is dramatic and the single-bar range
is wide (1848.552-1857.826, ~9.3pt), a real, sharp reversal-type event, not an ordinary dip. Not
pre-committing; this directly tests whether massive volume alone, without either a deep gap or a fresh
extreme, is sufficient -- a genuinely novel combination not yet seen in this ledger. POSITION=FLAT; no
MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a useful test case precisely
because it decouples volume from the other two components (gap depth, fresh extreme) that have
usually moved together -- the resolution evidence will show whether volume magnitude alone can carry
real weight.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5016 (2020-12-16 19:30:00 UTC)
DURATION                3 bars (5014-5016) -- very fast
DEEPEST_LOW              1844.844 (bar 5015) -- deeper than the gate origin, but not a record for
                          this general zone (well above -057's 1822.282), just a local dip within a
                          broader uptrend
HEAVIEST_VOLUME          3784 (bar 5014, the GATE ORIGIN itself) -- still the heaviest of the episode
                          by a wide margin, one of the most dramatic single-bar volumes in the whole
                          Q4 replay
RECLAIM_CLOSE             1855.372 -- a ~97% retracement of the decline (10.5 of 10.8pt), essentially
                          a near-complete round-trip (bar 5013 pre-episode close 1855.672, only
                          -0.30pt short)
CAUSAL_H1_EMA50_AT_RESOLUTION 1849.6695 (margin +5.70pt -- a very decisive reclaim)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this directly answers the
question the pre-classification posed -- does massive volume alone, without either a deep gap or a
fresh extreme, carry weight? Here the answer is NO: despite volume that dwarfs almost every REJECTED
case seen so far (and rivals -052/-038's confirmed SUPPORT episodes), the episode reabsorbed almost
completely (~97%) in just 3 bars, with no fresh extreme to anchor it. This closely echoes -051's own
lesson (dramatic single-bar events, however extreme in isolation, still read REJECTED when the
round-trip is this complete and the duration this short) -- but pushes it further: -051 at least had a
genuine new record low; this episode has neither a record extreme nor extended duration, only volume.
Volume magnitude alone, decoupled from the other components, is not sufficient.

---

## Q4-P007-059

```
GATE_ORIGIN_BAR          5254 (2020-12-21 10:00:00 UTC) -- Monday, 2020-12-21
CONTEXT                    a calm, generally rising stretch through bars 5134-5252 (~1880-1902 range,
                            no P007 candidates), then two consecutive bars of dramatic, sharply
                            escalating volume: bar 5253 (close fell 1895.4 -> 1886.642, -8.76pt,
                            volume 3445) and bar 5254 itself
TRIGGER_CLOSE                1868.98 -- itself well below the EMA, not just a wick
TRIGGER_LOW                   1855.148 -- a genuine fresh extreme relative to the recent uptrend
                              (though the runner's own seed-scan confirms this is not an all-time Q4
                              record; is_new_low/is_new_vol_record both false against full sealed
                              history)
CAUSAL_H1_EMA50_AT_5254       1883.1180
GAP                            -14.138pt -- BY FAR the deepest gap of the entire Q4 replay to date,
                                 well beyond anything seen in any prior episode
VOLUME                          6482 -- one of the heaviest single-bar volumes in the whole Q4 replay
                                 (exceeding the script's own tracked constant of 6203), following
                                 bar 5253's already-elevated 3445 -- two consecutive bars of dramatic
                                 escalation, not an isolated spike
```

**PRE-CLASSIFICATION:** leaning strongly SUPPORT -- this is categorically different from -058's
"volume only" test: here the gap depth, the volume, AND the close-basis break are all simultaneously
extreme, a combination not seen anywhere else in this ledger. The two-bar escalation (5253's 3445 into
5254's 6482) also argues against a single-bar liquidity-grab shape like -051/-058. This bar falls on
2020-12-21 (Monday) -- noted factually, not asserted as a specific cause, consistent with how prior
date-linked observations (2020-11-03 election, 2020-11-26 Thanksgiving) have been handled: the visible
price/volume pattern is the evidence, not an assumed news catalyst. Not pre-committing; the reclaim
evidence still needs to confirm this. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the strongest, most
multi-dimensionally extreme gate origin in the ledger to date -- a genuine test of whether an episode
this dramatic at the origin still needs the extended-duration/partial-retracement confirmation seen in
-038/-039/-040/-041/-052/-053/-056/-057, or whether origin-magnitude this large can stand on its own.

### RESOLUTION

```
STATUS               SUPPORT -- a genuine PATTERN-007 instance
RESOLUTION_BAR         5268 (2020-12-21 13:30:00 UTC)
DURATION                15 bars (5254-5268)
DEEPEST_LOW              1855.148 (bar 5254, the gate origin itself)
HEAVIEST_VOLUME          6482 (bar 5254, the GATE ORIGIN itself) -- and unlike every prior episode,
                          volume stayed SUSTAINED and dramatically elevated across the ENTIRE 15-bar
                          episode (4636/3733/3406/3025/1501/1964/2014/2470/1256/993/1225/4176/
                          3089/2179), never dropping back to the thin 100-500 baseline seen elsewhere
                          in this ledger -- a genuinely novel shape, not a single spike
RECLAIM_CLOSE             1882.866 -- an 88% retracement of the decline (27.7 of 31.5pt), high but
                          genuinely partial, not complete or overshooting
CAUSAL_H1_EMA50_AT_RESOLUTION 1882.4723 (margin +0.39pt -- thin, though the episode itself is anything
                          but)
```

No trade was open; no MGMT-004 relevance. No S5 trigger this bar.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** answers this episode's own
framed question -- origin-magnitude this extreme did NOT need extended multi-day duration to confirm
itself; what it needed instead was sustained follow-through, which it had in abundance. This is the
clearest contrast with -058's isolated-spike REJECTED case: there, massive volume hit once and the
market absorbed it in 3 bars back to baseline; here, elevated volume persisted across all 15 bars of
the episode, evidence of a genuinely sustained repricing event rather than a single liquidity grab.
Combined with the deepest gap and heaviest single-bar volume in the whole Q4 replay, and a partial (not
complete) retracement, this reads as a confident SUPPORT case despite its comparatively short duration
-- sustained volume, not bar count alone, is treated as the real marker of a genuine structural event.

---

## Q4-P007-060

```
GATE_ORIGIN_BAR          5269 (2020-12-21 13:45:00 UTC) -- one bar after -059's reclaim
TRIGGER_CLOSE                1882.28
TRIGGER_LOW                   1881.662 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5269       1882.4723
GAP                            -0.192pt -- very shallow
VOLUME                          1680 -- elevated in absolute terms, but continuing -059's own
                                 elevated regime (2179 at bar 5268, 3089 at bar 5267), not a clear
                                 acceleration relative to that specific context
```

**PRE-CLASSIFICATION:** leaning REJECTED -- very shallow gap immediately after a reclaim, no fresh
extreme, volume high only in absolute terms, not relative to the just-resolved episode's own regime.
Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature relative to its own immediate context -- consistent with, not the basis for, the
REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5275 (2020-12-21 15:15:00 UTC)
DURATION                6 bars (5269-5275)
DEEPEST_LOW              1877.636 (bar 5273) -- not a fresh extreme
HEAVIEST_VOLUME          2424 (bar 5272) -- neither at the gate origin nor at the deepest-low bar;
                          volume stayed elevated but diffuse throughout, part of -059's general
                          aftermath rather than concentrated anywhere meaningful
RECLAIM_CLOSE             1882.983 -- OVERSHOOTS the pre-episode level (bar 5268 close 1882.866) by
                          +0.12pt, essentially a full round-trip
CAUSAL_H1_EMA50_AT_RESOLUTION 1882.3917 (margin +0.59pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a clean REJECTED read matching
the pre-classification's lean -- no fresh extreme, volume diffuse rather than concentrated, and an
essentially complete round-trip. Continues the pattern seen after -052/-053/-056/-057's own reclaims:
the immediate next candidate in the same stretch often reads REJECTED even when overall volume stays
elevated, since it's the RELATIVE, not absolute, evidence that matters.

---

## Q4-P007-061

```
GATE_ORIGIN_BAR          5276 (2020-12-21 15:30:00 UTC) -- immediately after -060's own reclaim
TRIGGER_CLOSE                1881.396
TRIGGER_LOW                   1880.768 -- NOT deeper than -060's own 1877.636
CAUSAL_H1_EMA50_AT_5276       1882.3917
GAP                            -0.996pt -- moderate
VOLUME                          1305 -- continuing the elevated-but-normalizing regime (2424, 1907,
                                 2048, 1722 in the immediately preceding bars), not a clear
                                 acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- same character as -060, no fresh extreme, volume
moderate and fading rather than accelerating. Not pre-committing. POSITION=FLAT; no MGMT-004
relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** does not show the SUPPORT-
leaning signature -- consistent with, not the basis for, the REJECTED lean.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5282 (2020-12-21 17:00:00 UTC)
DURATION                6 bars (5276-5282)
DEEPEST_LOW              1874.64 (bar 5278) -- a modest fresh low, deeper than -060's own 1877.636
HEAVIEST_VOLUME          1305 (bar 5276, the GATE ORIGIN) -- a clean SUPPORT-consistent placement,
                          but modest in absolute terms, nowhere near -059's dramatic volumes
RECLAIM_CLOSE             1882.856 -- a ~98% retracement of the decline (8.2 of 8.3pt), essentially
                          a near-perfect round-trip
CAUSAL_H1_EMA50_AT_RESOLUTION 1882.2050 (margin +0.65pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the pattern from -046/-049/-050
repeats: a modest fresh low and origin-favoring volume placement, but both at modest magnitude, and a
near-perfect round-trip dominates the read. REJECTED.

---

## Q4-P007-062

```
GATE_ORIGIN_BAR          5283 (2020-12-21 17:15:00 UTC) -- immediately after -061's own reclaim
TRIGGER_CLOSE                1881.484
TRIGGER_LOW                   1880.926 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5283       1882.1358
GAP                            -0.652pt -- shallow-moderate
VOLUME                          385 -- notably LOWER than the recent elevated regime (1305, 1051,
                                 1272...), a genuine sign of the market calming after the Dec 21 event
```

**PRE-CLASSIFICATION:** leaning REJECTED, clearly -- shallow gap, no fresh extreme, and volume has
genuinely dropped back toward baseline rather than remaining elevated. Not pre-committing.
POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the clearest REJECTED lean of
this immediate aftermath sequence (-060, -061, -062) -- volume finally normalizing is itself a
meaningful signal that the elevated-volume period has run its course.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5312 (2020-12-22 01:30:00 UTC)
DURATION                30 bars (5283-5312)
DEEPEST_LOW              1874.034 (bar 5295) -- a modest fresh low, not dramatic
HEAVIEST_VOLUME          883 (bar 5310) -- lands near the end of the episode, close to but not
                          exactly at the reclaim, and not cleanly at the break either; modest in
                          absolute terms throughout (nothing above 883 the whole episode)
RECLAIM_CLOSE             1881.829 -- an 88% retracement of the decline (7.8 of 8.8pt), high but
                          genuinely partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1881.0822 (margin +0.75pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger. GAP-207 (standard MAINTENANCE) logged inside
the episode.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** consistent with the now-
established lesson from -046/-049/-050/-061: modest-magnitude evidence across the board (a modest
low, volume that never exceeds 883, no clean break-side concentration) does not override a high (88%)
retracement. REJECTED -- the market has genuinely settled into a calmer, lower-conviction stretch
following the Dec 21 volatility spike.

---

## Q4-P007-063

```
GATE_ORIGIN_BAR          5320 (2020-12-22 03:30:00 UTC)
TRIGGER_CLOSE                1880.454
TRIGGER_LOW                   1880.019 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5320       1881.2006
GAP                            -0.7466pt -- shallow-moderate
VOLUME                          251 -- notably low; lower than every bar in the immediate lead-in
                                 window (403/376/218/551/412/260/332 across bars 5313-5319) except
                                 bar 5315's 218, and well below the elevated Dec-21 regime
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme, a shallow-moderate gap, and volume
that is not just failing to escalate but sits at the low end of an already-quiet window. Continues
the calming trend noted at -062. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** a third consecutive
low-volume, no-fresh-extreme gate origin (following -062's own normalization read) -- the
post-Dec-21 quiet regime looks to be persisting rather than reverting.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5322 (2020-12-22 04:00:00 UTC)
DURATION                2 bars (5320-5321)
DEEPEST_LOW              1880.019 (bar 5320, the gate-origin/trigger bar itself) -- not a fresh
                        extreme, confirmed at pre-classification
HEAVIEST_VOLUME          251 (bar 5320, the trigger bar) -- modest, never exceeded across the
                        2-bar episode (bar 5321 only 116)
RECLAIM_CLOSE             1882.772 -- a full overshoot: ~193% of the 1.427pt decline from the last
                          pre-break close (1881.446), reclaiming well past the pre-episode level
CAUSAL_H1_EMA50_AT_RESOLUTION 1881.2006 (margin +1.571pt)
```

No trade was open; no MGMT-004 relevance. No S5 trigger. A 2-bar round-trip with a decisive
overshoot reclaim, matching the "fast liquidity-grab-and-reclaim" signature seen before at
Q4-P007-051 (there 107% in 6 bars; here 193% in 2 bars, an even faster and more extreme overshoot)
-- not a sustained structural process. Modest volume throughout, no fresh extreme. REJECTED.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the fastest complete
round-trip of the whole Q4 record so far (2 bars gate-to-reclaim) -- extends the "speed +
overshoot beats magnitude" reading from -051 to an even shorter timescale, and continues the
post-Dec-21 quiet-regime pattern noted at -062/-063's own pre-classification.

---

## Q4-P007-064

```
GATE_ORIGIN_BAR          5324 (2020-12-22 04:30:00 UTC) -- immediately after -063's own reclaim
                          (bar 5322) and one routine bar (5323)
TRIGGER_CLOSE                1880.943
TRIGGER_LOW                   1880.649 -- NOT a fresh extreme (well above -063's own low of
                              1880.019, let alone the all-time Q4 low)
CAUSAL_H1_EMA50_AT_5324       1881.1658
GAP                            -0.2228pt -- a touch, not a break
VOLUME                          194 -- thinner even than -063's own trigger bar (251), continuing
                                 the quiet-regime decay
```

**PRE-CLASSIFICATION:** leaning REJECTED, clearly -- a marginal EMA touch, no fresh extreme, and
volume thinner than the already-quiet -063 episode. Matches the -008/-009/-011/-014 trivial-touch
signature. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the quiet post-Dec-21 regime
continues to deepen -- each successive gate origin in this stretch (-062, -063, -064) has printed
progressively thinner volume.

### RESOLUTION

**Significant divergence from the pre-classification lean, disclosed rather than smoothed over:**
the trigger bar itself (5324) was genuinely trivial, exactly as pre-classified. But the episode did
not fade the way -062/-063 did -- starting at bar 5326, price began a genuine sustained decline that
ran for the better part of the next 2 hours, escalating well beyond anything the thin trigger bar
suggested. Handled as a continuation of the same durable gate reference, not reopened or split, per
the same discipline applied to -006/-010/-015/-016.

```
STATUS               SUPPORT / RECLAIM
GATE_ORIGIN_BAR         5324 (2020-12-22 04:30:00 UTC) -- trivial trigger bar
GENUINE_ESCALATION       bars 5326-5334, a sustained 9-bar decline with volume stepping up well
                          above the trigger bar's own 194 (434/408/911/805/1248/690/692/1565/993)
RESOLUTION_BAR           5361 (2020-12-22 13:45:00 UTC)
DURATION                 37 bars (5324-5360)
DEEPEST_LOW              1866.794 (bar 5334, 2020-12-22 07:00:00 UTC) -- not an all-time Q4 record
                          (Q4-P007-015's 1860.08 stands), but a genuine fresh multi-week local
                          extreme -- the entire post-Dec-21 stretch (-057 through -064) had held
                          inside roughly 1874-1884 until this episode broke well below it
HEAVIEST_VOLUME          1565 (bar 5333, 2020-12-22 06:45:00 UTC) -- one bar before the deepest low,
                          landing cleanly on the decline leg itself, not at the reclaim
RECLAIM_CLOSE             1878.88 -- an 83% retracement of the 14.513pt decline (12.086 of 14.513,
                          measured from the last pre-episode close of 1881.307), genuinely partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1878.6945 (margin +0.186pt, thin)
```

No trade was open; no MGMT-004 relevance. No S5 trigger at any point in the 37-bar episode
(unconditional check confirmed each bar). No gap inside the episode -- fully continuous M15 data
throughout.

This is a clear SUPPORT case by the now-established discriminator components: a genuine fresh local
extreme (deepest in weeks, even though not an all-time Q4 record), volume concentrated near the
break leg rather than diffuse or reclaim-side, a PARTIAL (83%, not complete/overshoot) retracement,
and an extended multi-hour duration (37 bars) with volume staying elevated through most of the
episode rather than collapsing immediately. The pre-classification's REJECTED lean was reasonable
given only the trigger bar's own thin signature, but explicitly did not pre-commit -- exactly the
kind of divergence the escalation-episode precedent (-006/-010/-015/-016) exists to capture
honestly.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the quiet post-Dec-21 regime
noted building at -062/-063/-064's own pre-classifications did NOT persist -- it broke into the
quarter's next genuine directional episode instead, underscoring that a string of thin/REJECTED
gate origins says nothing about what the following bar will do. A trivial trigger bar remains a
poor predictor of the episode's eventual character on its own; the escalation, when it comes, is
visible only in the bars that follow.

---

## Q4-P007-065

**First candidate opened while TRADE #34 is live -- trade mechanics confirmed to run unconditionally
before this reasoning stop (`trade_monitoring_already_executed=True`, `p007_coincided_with_open_trade`
flag set).**

```
GATE_ORIGIN_BAR          5363 (2020-12-22 14:15:00 UTC) -- immediately after TRADE #34's own signal
                          bar (5362)
TRADE_STATE_AT_ORIGIN      TRADE #34 open, entry 1880.196, currently 1878.7 (~-0.165R), clear of
                          both stop (1871.150) and MGMT-004 trigger (1889.242)
TRIGGER_CLOSE                1878.7
TRIGGER_LOW                   1878.208 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5363       1878.7018
GAP                            -0.0018pt -- essentially zero, a bare touch
VOLUME                          897 -- real/moderate
```

**PRE-CLASSIFICATION:** leaning REJECTED -- the gap is essentially nonexistent (0.0018pt), well
inside noise, and there is no fresh extreme. Real volume alone (897) is not, on its own, sufficient
per the established -058 lesson (massive volume decoupled from a fresh extreme still resolved
REJECTED there). Not pre-committing. TRADE #34 remains open and unaffected.

**INTERIM NOTE:** TRADE #34 stopped out at bar 5366 (-1.0000R), one bar into this episode; the gate
remained open and unaffected -- both subsystems processed independently. This episode did not fade
the way its own trigger bar suggested -- it became the largest directional decline since
Q4-P007-064, running 93 bars with a genuine fresh multi-week low. One MAINTENANCE gap (GAP-208, bar
5393->5394) logged inside the episode, standard.

### RESOLUTION

**Second consecutive significant divergence from a thin-trigger pre-classification** (after -064) --
handled as a continuation of the same durable gate reference, per the -006/-010/-015/-016/-064
precedent.

```
STATUS               SUPPORT / RECLAIM
GATE_ORIGIN_BAR         5363 (2020-12-22 14:15:00 UTC) -- trivial trigger bar (gap -0.0018pt)
GENUINE_ESCALATION       bars 5364-5369, a fast 6-bar decline (1878.7 -> 1861.764) on rapidly
                          building volume (1568/926/1657/1927), reaching this episode's heaviest
                          volume (1927, bar 5369) right at the break leg
RESOLUTION_BAR           5456 (2020-12-23 14:30:00 UTC)
DURATION                 93 bars (5363-5455) -- the 4th-longest episode of the whole Q4 record
                          (after -015's 198, -003's 147, -004's 91 -- this narrowly exceeds -004)
DEEPEST_LOW              1857.132 (bar 5446, 2020-12-23 12:00:00 UTC) -- NOT an all-time Q4 record
                          (independently verified against the sealed CSV: the true Q4 minimum,
                          1848.801, was set far earlier at bar 1759, 2020-09-28), but well below
                          every recent reference including Q4-P007-064's own deep low (1866.794) --
                          a genuine fresh multi-week local extreme
HEAVIEST_VOLUME          1927 (bar 5369, 2020-12-22 15:45:00 UTC) -- lands cleanly on the initial
                          break leg (6 bars after gate origin), not diffuse and not at the reclaim
RECLAIM_CLOSE             1874.868 -- a 77% retracement of the 23.064pt decline (17.736 of 23.064,
                          measured from the last pre-episode close of 1880.196), genuinely partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1870.8608 (margin +4.007pt, the largest reclaim margin of the
                          episode-tracked record to date)
```

**Coincident S5 trigger at the resolution bar, deferred per standing priority:** bar 5456 also
produced a fresh S5 opening-range-breakout signal (entry 1874.868, stop 1860.711, target 1917.339,
bis=7) on the exact same bar as this P007 reclaim. POSITION=FLAT (TRADE #34 closed at bar 5366).
Per the established decide() priority (P007 reasoning stop takes precedence over a coincident S5
signal when FLAT), this P007 resolution is handled first; the S5 signal is expected to re-fire on
the next bar via S5's own stateless `evaluate()`, exactly as seen at Q4-P007-039->TRADE #26 and
Q4-P007-052->TRADE #29. No MGMT-004 relevance (no trade open at any point during this episode after
TRADE #34's own bar-5366 close).

This is a clear SUPPORT case: a genuine fresh local extreme (deepest in many weeks, even though not
an all-time Q4 record), volume concentrated tightly on the break leg rather than diffuse, a PARTIAL
(77%) retracement, and the second-longest duration of the recent stretch. The trigger bar's own
thin signature was, again, a poor predictor of the episode's eventual character.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** two consecutive P007
instances now (-064, -065) have escalated dramatically from genuinely trivial trigger bars into the
largest directional episodes of this stretch -- reinforcing that a quiet/thin gate origin carries no
predictive weight on its own about what follows; only the bars that come after the origin reveal
the episode's real character.

---

## Q4-P007-066

**Second candidate opened while a trade (TRADE #35) is live -- trade mechanics confirmed to run
unconditionally before this reasoning stop (`trade_monitoring_already_executed=True`,
`p007_coincided_with_open_trade` flag set).**

```
GATE_ORIGIN_BAR          5476 (2020-12-23 19:30:00 UTC)
TRADE_STATE_AT_ORIGIN      TRADE #35 open, entry 1876.580, currently 1871.29 (~-0.333R), clear of
                          both stop (1860.711) and MGMT-004 trigger (1892.449)
CONTEXT                    bars 5468-5475 drifted quietly 1871.5-1874.5, thin-moderate volume
                          (130-381), no strong directional character
TRIGGER_CLOSE                1871.29
TRIGGER_LOW                   1871.277 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5476       1871.3992
GAP                            -0.1092pt -- a touch, not a break
VOLUME                          240 -- thin, in line with the recent quiet baseline, no acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- matches the -008/-009/-011/-014 trivial-touch signature:
shallow gap, no fresh extreme, thin volume with no acceleration. Not pre-committing, especially
given -064 and -065 both diverged from an initially-similar-looking thin lean. TRADE #35 remains
open and unaffected.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5477 (2020-12-23 19:45:00 UTC)
DURATION                1 bar (5476) -- the fastest possible complete round-trip
DEEPEST_LOW              1871.277 (bar 5476, the gate-origin/trigger bar itself)
HEAVIEST_VOLUME          240 (bar 5476, the trigger bar) -- never exceeded (bar 5477 only 208)
RECLAIM_CLOSE             1871.724 -- a full overshoot: ~174% of the tiny 0.257pt decline from the
                          last pre-break close (1871.534)
CAUSAL_H1_EMA50_AT_RESOLUTION 1871.3992 (margin +0.325pt)
```

TRADE #35 remained open throughout, unaffected (~-0.33R at the time, clear of stop and MGMT-004
trigger). This time the thin trigger DID resolve exactly as pre-classified -- unlike -064/-065,
there was no escalation here, just the trivial-touch/immediate-overshoot signature seen repeatedly
at -008/-009/-011/-014/-063. No S5 trigger.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** confirms that not every thin
trigger bar escalates -- -064 and -065 diverged, but -066 did not, underscoring that the divergence
risk cuts both ways and genuinely has to be watched for each time, not assumed from recent
precedent in either direction.

---

## Q4-P007-067

**Third candidate opened while TRADE #35 is live -- immediately after -066's own reclaim (bar 5477)
-- trade mechanics confirmed to run unconditionally before this reasoning stop.**

```
GATE_ORIGIN_BAR          5478 (2020-12-23 20:00:00 UTC) -- 1 bar after -066 resolved REJECTED
TRADE_STATE_AT_ORIGIN      TRADE #35 open, entry 1876.580, currently 1870.348 (~-0.393R), clear of
                          both stop (1860.711) and MGMT-004 trigger (1892.449)
TRIGGER_CLOSE                1870.348
TRIGGER_LOW                   1870.214 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5478       1871.3992
GAP                            -1.0512pt -- moderate, larger than -066's own tiny gap
VOLUME                          208 -- thin, no acceleration
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme and thin volume, despite the somewhat
larger gap than -066. The gap magnitude alone has not been a reliable SUPPORT signal on its own in
this record (e.g. -013's -2.36pt gap still resolved REJECTED). Not pre-committing. TRADE #35
remains open and unaffected.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5481 (2020-12-23 20:45:00 UTC)
DURATION                3 bars (5478-5480)
DEEPEST_LOW              1869.956 (bar 5479) -- barely below the trigger bar's own low, not a
                        meaningful new extreme
HEAVIEST_VOLUME          208 (bar 5478, the trigger bar) -- volume never exceeded 208 across the
                        3-bar episode (159/142 on the following bars), thin throughout
RECLAIM_CLOSE             1872.636 -- a full overshoot: ~152% of the 1.768pt decline from the last
                          pre-break close (1871.724)
CAUSAL_H1_EMA50_AT_RESOLUTION 1871.4119 (margin +1.224pt)
```

TRADE #35 remained open throughout, unaffected (~-0.28R to -0.43R across the episode, clear of stop
and MGMT-004 trigger). No S5 trigger. Second consecutive fast, thin, overshoot-reclaim REJECTED
(after -066, and matching -063's own earlier signature), continuing the quarter's late-Q4 pattern
of quick, low-conviction P007 flickers around this price zone.

---

## Q4-P007-068

```
GATE_ORIGIN_BAR          5533 (2020-12-24 10:45:00 UTC) -- TRADE #35 closed (bar 5505, MAX_HOLD);
                          POSITION=FLAT
TRIGGER_CLOSE                1872.772
TRIGGER_LOW                   1871.242 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5533       1873.2796
GAP                            -0.5076pt -- shallow-moderate
VOLUME                          477 -- moderate, real
```

**PRE-CLASSIFICATION:** genuinely ambiguous by the recent pattern -- moderate gap and moderate
volume, somewhat more real volume than the recent thin/fast REJECTED instances (-066/-067), but no
fresh extreme yet. Leaning slightly REJECTED but watching for real continuation. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5534 (2020-12-24 11:00:00 UTC)
DURATION                1 bar (5533)
DEEPEST_LOW              1871.242 (bar 5533, the gate-origin/trigger bar itself)
HEAVIEST_VOLUME          477 (bar 5533, the trigger bar) -- higher than -066/-067's own thin
                        figures, but concentrated entirely at the origin with zero follow-through
RECLAIM_CLOSE             1875.446 -- a full overshoot: ~156% of the 2.696pt decline from the last
                          pre-break close (1873.938)
CAUSAL_H1_EMA50_AT_RESOLUTION 1873.2796 (margin +2.166pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. The ambiguity flagged in the pre-classification
resolved toward REJECTED: the moderate volume never got a chance to build or confirm -- it printed
once at the origin and the whole move round-tripped within a single bar, the defining REJECTED
signature regardless of the origin volume's own moderate size. Third fast, overshoot-reclaim
REJECTED in four candidates now (-066, -067, -068), reinforcing that this late-Q4 stretch is
genuinely low-conviction.

---

## Q4-P007-069

```
GATE_ORIGIN_BAR          5546 (2020-12-24 14:00:00 UTC) -- Christmas Eve, NY session
TRIGGER_CLOSE                1873.304
TRIGGER_LOW                   1872.19 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5546       1873.4317
GAP                            -0.1277pt -- a touch, not a break
VOLUME                          627 -- moderate, real
```

**PRE-CLASSIFICATION:** leaning REJECTED -- a bare touch (gap essentially negligible) with no fresh
extreme, matching the -008/-009/-011/-014 trivial-touch signature despite real-ish volume. This is
Christmas Eve; watching for any holiday-driven thinning of subsequent volume as additional context,
not as a rule. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5548 (2020-12-24 14:30:00 UTC)
DURATION                2 bars (5546-5547)
DEEPEST_LOW              1869.582 (bar 5547) -- a real move beyond the trigger bar's own low, but
                        not a fresh extreme against the wider record
HEAVIEST_VOLUME          1159 (bar 5547) -- genuinely real volume, larger than the trigger bar's own
                        627, but landing on a bar that immediately reversed
RECLAIM_CLOSE             1873.952 -- an essentially complete round-trip: ~100% of the 4.366pt
                          decline from the last pre-break close (1873.948), reclaiming right back to
                          the pre-episode level
CAUSAL_H1_EMA50_AT_RESOLUTION 1873.4520 (margin +0.500pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. Real volume (1159) on the break bar did NOT
override the near-perfect round-trip -- consistent with the established -058/-059 lesson that
volume magnitude alone does not decide the outcome, and with the "full-plus round-trip is the most
reliable REJECTED signal" pattern seen at -013/-051/-061 (there ~98-107%; here ~100%, right in the
same near-complete band). REJECTED.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this is a clean confirming
case for the round-trip-over-volume discriminator -- real, not thin, volume on the break bar, yet
still REJECTED because the retracement was essentially complete within 2 bars.

---

## Q4-P007-070

```
GATE_ORIGIN_BAR          5611 (2020-12-28 10:30:00 UTC) -- first business day after the Christmas
                          weekend (GAP-210); TRADE #36 closed +3.0000R at bar 5565; POSITION=FLAT
TRIGGER_CLOSE                1879.278
TRIGGER_LOW                   1879.047 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5611       1879.8998
GAP                            -0.6218pt -- shallow-moderate
VOLUME                          818 -- moderate, real
```

**PRE-CLASSIFICATION:** genuinely ambiguous -- moderate gap and moderate volume, similar in scale
to -068's own moderate-but-ultimately-REJECTED profile. No fresh extreme yet. Leaning slightly
REJECTED but watching for real continuation, especially given the extended gap since -069 (bars
5549-5610 ran without a new candidate, the market having spent the whole intervening stretch,
including the reopening surge, comfortably above EMA50). Not pre-committing. POSITION=FLAT; no
MGMT-004 relevance.

### RESOLUTION

```
STATUS               SUPPORT / RECLAIM
GATE_ORIGIN_BAR         5611 (2020-12-28 10:30:00 UTC) -- moderate trigger, ambiguous pre-classification
RESOLUTION_BAR           5621 (2020-12-28 13:00:00 UTC)
DURATION                 10 bars (5611-5620)
DEEPEST_LOW              1869.309 (bar 5616, 2020-12-28 11:45:00 UTC) -- NOT an all-time Q4 record,
                          but the deepest point since the Christmas reopening, a genuine local
                          multi-day extreme
HEAVIEST_VOLUME          1995 (bar 5616) -- the SAME bar as the deepest low, a clean, tight
                          concentration exactly at the extreme (roughly 2x the surrounding bars'
                          796-1033 range), not diffuse and not off to the side
RECLAIM_CLOSE             1879.656 -- an 87% retracement of the 11.941pt decline (10.347 of 11.941,
                          measured from the last pre-episode close of 1881.25), high but clearly
                          short of the ~97%+ near-complete-round-trip threshold that has been the
                          most reliable REJECTED signal in this record
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.6096 (margin +0.046pt, the thinnest reclaim margin recorded)
```

No trade open; no MGMT-004 relevance. No S5 trigger. A genuine close call, resolved toward SUPPORT:
the fresh low is only moderately significant in absolute Q4 terms (not an all-time record), and the
87% retracement sits in the upper part of the range that has sometimes gone either way (-046/-062
REJECTED at 88-89%; -045 SUPPORT at 89%). What tips this one is the volume placement -- 1995 landing
in the SAME bar as the deepest low is a cleaner, tighter concentration than several of the
REJECTED high-retracement cases (-062's heaviest volume, 883, landed near but not at the low), and
the retracement, while high, stayed meaningfully below the ~97%+ near-complete band that has been
the more decisive REJECTED signal throughout this record.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this instance sharpens the
retracement-threshold reading -- the reliable REJECTED boundary looks closer to ~90-97%+ (near-
complete/overshoot) than to the ~85-89% band, where volume placement and other components still
carry real weight, as they did here.

---

## Q4-P007-071

**Fourth candidate opened while a trade (TRADE #37) is live -- trade mechanics confirmed to run
unconditionally before this reasoning stop.**

```
GATE_ORIGIN_BAR          5635 (2020-12-28 16:30:00 UTC)
TRADE_STATE_AT_ORIGIN      TRADE #37 open, entry 1889.380, currently 1879.925 (~-0.640R) -- a real
                          pullback from the +0.30R high (bar 5628, close 1893.856), but still clear
                          of both stop (1874.604) and MGMT-004 trigger (1904.156)
TRIGGER_CLOSE                1879.925
TRIGGER_LOW                   1877.551 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5635       1880.3987
GAP                            -0.4737pt -- shallow-moderate
VOLUME                          784 -- moderate, real
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme, shallow-moderate gap, moderate but
unremarkable volume. Matches the general profile of several recent REJECTED instances (-068/-069)
more than the SUPPORT case (-070). Not pre-committing. TRADE #37 remains open, now meaningfully
underwater but still well clear of its stop.

**INTERIM NOTE:** TRADE #37 stopped out at bar 5644 (-1.0000R), well inside this episode; the gate
remained open and unaffected -- both subsystems processed independently. One MAINTENANCE gap
(GAP-211, bar 5656->5657) logged inside the episode, standard.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
GATE_ORIGIN_BAR         5635 (2020-12-28 16:30:00 UTC)
RESOLUTION_BAR           5661 (2020-12-29 00:00:00 UTC)
DURATION                 26 bars (5635-5660)
DEEPEST_LOW              1871.198 (bar 5656, 2020-12-28 21:45:00 UTC) -- NOT an all-time Q4 record,
                          and NOT even a fresh low relative to -070's own recent low (1869.309, only
                          ~40 bars/2 days earlier) -- the market has essentially been oscillating in
                          the same 1869-1880 zone without genuine new progress lower
HEAVIEST_VOLUME          784 (bar 5635, the gate-origin bar itself) -- a real, moderate spike right
                          at the origin, but the following 25 bars stayed thin-to-moderate (138-479)
                          throughout, no sustained elevation
RECLAIM_CLOSE             1879.579 -- a 90% retracement of the 9.315pt decline (8.381 of 9.315,
                          measured from the last pre-episode close of 1880.513), right at the
                          boundary of the "reliable REJECTED zone" identified at -070's own
                          resolution
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.4311 (margin +0.148pt, thin)
```

TRADE #37's stop-out (bar 5644, -1.0000R) fell inside this episode, unaffected by it; both
subsystems processed independently. No S5 trigger at resolution. REJECTED: the decisive factor here
is the absence of any genuine fresh extreme -- 1871.198 doesn't even undercut -070's own recent low
from just two days earlier, meaning this 26-bar episode represents continued chop within an
already-established range rather than a new structural move. The origin-bar volume spike (784)
faded into a long, thin, directionless grind rather than sustaining or building. The 90% retracement
sits right at, not clearly below, the boundary identified at -070 -- consistent with REJECTED given
the other components also point that way.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this instance sharpens the
"fresh extreme" component further -- what counts as fresh should be judged against the most recent
comparable episode's own extreme, not just the all-time Q4 record. A low that fails to undercut
even a very recent prior episode's low is a meaningfully weaker signal than one that does, even when
both would show is_new_low=False against the whole-quarter record.

---

## Q4-P007-072

```
GATE_ORIGIN_BAR          5662 (2020-12-29 00:15:00 UTC) -- immediately after -071's own reclaim
                          (bar 5661)
TRIGGER_CLOSE                1879.308
TRIGGER_LOW                   1878.606 -- NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5662       1879.3313
GAP                            -0.0233pt -- essentially zero, a bare touch
VOLUME                          245 -- thin
```

**PRE-CLASSIFICATION:** leaning REJECTED -- a bare touch immediately following -071's own
inconclusive 26-bar grind, matching the -008/-009/-011/-014/-066 trivial-touch signature. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5667 (2020-12-29 01:30:00 UTC)
DURATION                5 bars (5662-5666)
DEEPEST_LOW              1877.49 (bar 5666) -- well above -071's own recent low (1871.198, ~6 bars
                        earlier), decisively fails the sharpened "fresh vs. most recent comparable
                        episode" test from -071's own observational note
HEAVIEST_VOLUME          1131 (bar 5665) -- real, but lands mid-episode, not at the deepest point
                        (bar 5666, only 482)
RECLAIM_CLOSE             1879.325 -- an 88% retracement of the 2.089pt decline (1.835 of 2.089,
                          measured from the last pre-episode close of 1879.579)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.3012 (margin +0.024pt, essentially a bare reclaim)
```

No trade open; no MGMT-004 relevance. No S5 trigger. REJECTED, clearly: the deepest low fails to
undercut -071's own very recent low by a wide margin (1877.49 vs 1871.198), the heaviest volume
landed off the deepest point rather than at it, and the high retracement (88%) adds no counter-
evidence. Continues the theme -- since -070, the market has been unable to make any genuine fresh
progress lower, each subsequent episode's low landing higher than the last (-070: 1869.309 ->
-071: 1871.198 -> -072: 1877.49), consistent with a broader stabilizing/basing character following
the Christmas reopening.

---

## Q4-P007-073

```
GATE_ORIGIN_BAR          5668 (2020-12-29 01:45:00 UTC) -- immediately after -072's own reclaim
                          (bar 5667)
TRIGGER_CLOSE                1878.526
TRIGGER_LOW                   1877.654 -- still HIGHER than -072's own low (1877.49); NOT a fresh
                              extreme, continuing the higher-lows theme
CAUSAL_H1_EMA50_AT_5668       1879.3012
GAP                            -0.7752pt -- moderate
VOLUME                          511 -- moderate
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme (continues the higher-lows pattern
since -070), moderate gap and volume, similar in scale to several recent REJECTED instances. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5671 (2020-12-29 02:30:00 UTC)
DURATION                3 bars (5668-5670)
DEEPEST_LOW              1875.236 (bar 5669) -- FINALLY breaks below both -072's low (1877.49) and
                        -073's own trigger low (1877.654), the first genuine progress lower since
                        -070, though still above -071's own low (1871.198); not an all-time record
HEAVIEST_VOLUME          881 (bar 5669) -- real, and lands cleanly at the deepest point itself, a
                        clean concentration
RECLAIM_CLOSE             1879.55 -- a full overshoot: ~106% of the 4.089pt decline from the last
                          pre-break close (1879.325), reclaiming beyond the pre-episode level
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.2708 (margin +0.279pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. Despite a genuinely fresher low than the
immediately preceding episodes and clean volume concentration at the extreme, the full-overshoot
retracement (~106% in just 3 bars) is decisive -- consistent with the "full-plus round-trip is the
most reliable REJECTED signal" pattern established at -013/-051/-061/-069, which has held even
against otherwise-favorable individual components. REJECTED.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this instance is a clean
test of component-priority -- a fresher low + clean volume placement (both SUPPORT-favoring) still
lost to a fast full-overshoot retracement, reinforcing that the round-trip completeness is the
single strongest discriminator component observed in this record, capable of overriding otherwise-
positive signals.

---

## Q4-P007-074

```
GATE_ORIGIN_BAR          5672 (2020-12-29 02:45:00 UTC) -- immediately after -073's own reclaim
                          (bar 5671)
TRIGGER_CLOSE                1878.096
TRIGGER_LOW                   1877.35 -- still above -073's own low (1875.236); NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5672       1879.2708
GAP                            -1.1748pt -- moderate-larger than recent candidates
VOLUME                          333 -- thin
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme and thin volume, despite the somewhat
larger gap. Gap magnitude alone has repeatedly not been a reliable SUPPORT signal in this record
(-013, -067). Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5674 (2020-12-29 03:15:00 UTC)
DURATION                2 bars (5672-5673)
DEEPEST_LOW              1875.358 (bar 5673) -- barely fails to undercut -073's own low (1875.236),
                        essentially matching it rather than breaking fresh ground
HEAVIEST_VOLUME          796 (bar 5673) -- real, higher than the origin bar's 333
RECLAIM_CLOSE             1879.656 -- a full overshoot: ~103% of the 4.192pt decline from the last
                          pre-break close (1879.55)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.2247 (margin +0.431pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. Another fast, real-volume overshoot REJECTED,
directly following the same pattern just confirmed at -073 -- the deepest low essentially retested
rather than broke the prior episode's floor, and the full-overshoot reclaim (~103% in 2 bars)
decided REJECTED regardless of the real volume. Fourth consecutive REJECTED (-070 excepted;
-071/-072/-073/-074), all sharing the same signature: no fresh progress lower and fast overshoot
reclaims, consistent with a market that has settled into a stable, higher-lows floor since -070.

---

## Q4-P007-075

```
GATE_ORIGIN_BAR          5678 (2020-12-29 04:15:00 UTC)
TRIGGER_CLOSE                1879.12
TRIGGER_LOW                   1878.466 -- still above both -073's low (1875.236) and -074's low
                              (1875.358); NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5678       1879.2447
GAP                            -0.1247pt -- a bare touch
VOLUME                          255 -- thin
```

**PRE-CLASSIFICATION:** leaning REJECTED -- a bare touch, no fresh extreme, thin volume, matching
the -008/-009/-011/-014/-066 trivial-touch signature and continuing the stable higher-lows floor
theme since -070. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5685 (2020-12-29 06:00:00 UTC)
DURATION                7 bars (5678-5684)
DEEPEST_LOW              1875.632 (bar 5684) -- still above both -073's low (1875.236) and -074's
                        low (1875.358); the floor zone continues to hold, no fresh progress lower
HEAVIEST_VOLUME          654 (bar 5683) -- real, near but not exactly at the deepest point (bar
                        5684, only 460)
RECLAIM_CLOSE             1879.289 -- an 87% retracement of the 4.222pt decline (3.657 of 4.222,
                          measured from the last pre-episode close of 1879.854), high but genuinely
                          partial
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.1725 (margin +0.117pt, thin)
```

No trade open; no MGMT-004 relevance. No S5 trigger. REJECTED: although the 87% retracement alone
sits in the ambiguous band where -070 resolved SUPPORT, the decisive factor is the persistent
absence of any fresh extreme -- this is now the fifth consecutive episode since -070 (-071 through
-075) failing to break below the same ~1875.2-1875.4 floor zone, and the heaviest volume landed
near, not exactly at, the deepest point (unlike -070's clean concentration). The weight of repeated
floor-retests without a fresh extreme outweighs the single moderately-high retracement figure.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** the market has now spent
five consecutive gate cycles (~50 bars) unable to close below approximately 1875.2-1875.4, forming
a genuine, repeatedly-tested support floor -- a structural observation independent of, but
consistent with, the P007 discriminator's own REJECTED reads throughout this stretch.

---

## Q4-P007-076

```
GATE_ORIGIN_BAR          5686 (2020-12-29 06:15:00 UTC) -- immediately after -075's own reclaim
                          (bar 5685)
TRIGGER_CLOSE                1878.578
TRIGGER_LOW                   1878.468 -- well above the 1875.2-1875.4 floor zone tested repeatedly
                              since -071; NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5686       1879.0880
GAP                            -0.5100pt -- shallow-moderate
VOLUME                          338 -- thin
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme, well above the established floor
zone, thin volume. Continues the same low-conviction pattern seen across -071 through -075. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5692 (2020-12-29 07:45:00 UTC)
DURATION                6 bars (5686-5691)
DEEPEST_LOW              1875.644 (bar 5687) -- still above the ~1875.2-1875.4 floor zone tested at
                        -071 through -075; NOT a fresh extreme
HEAVIEST_VOLUME          867 (bar 5687) -- real, and lands cleanly at the deepest point itself
RECLAIM_CLOSE             1879.785 -- a full overshoot: ~114% of the 3.645pt decline from the last
                          pre-break close (1879.289), reclaiming beyond the pre-episode level
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.0706 (margin +0.714pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. Despite clean volume concentration at the
extreme (a SUPPORT-favoring signal, as at -070), the full-overshoot retracement (~114%) decided
REJECTED, consistent with the established priority of round-trip completeness over volume
placement (-058/-073). Sixth consecutive REJECTED since -070 (-071 through -076), the market
continuing to hold the same floor zone without genuine fresh progress lower.

---

## Q4-P007-077

```
GATE_ORIGIN_BAR          5696 (2020-12-29 08:45:00 UTC)
TRIGGER_CLOSE                1877.792
TRIGGER_LOW                   1877.611 -- still above the 1875.2-1875.4 floor zone; NOT a fresh
                              extreme
CAUSAL_H1_EMA50_AT_5696       1879.0986
GAP                            -1.3066pt -- larger than most recent candidates in this stretch
VOLUME                          413 -- moderate
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme despite the somewhat larger gap.
Continues the same low-conviction pattern across the whole -071 through -076 stretch. Not
pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5697 (2020-12-29 09:00:00 UTC)
DURATION                1 bar (5696) -- the entire decline (1881.722 -> 1877.611) happened within
                        the origin bar's own intrabar range, not a multi-bar slide
DEEPEST_LOW              1877.611 (bar 5696, the origin bar itself) -- still above the 1875.2-1875.4
                        floor zone; NOT a fresh extreme
HEAVIEST_VOLUME          413 (bar 5696, the origin bar) -- moderate, no dramatic concentration
                        either bar (bar 5697 only 364)
RECLAIM_CLOSE             1879.122 -- a genuinely LOW retracement for this record, ~37% of the
                          4.111pt decline (1.511 of 4.111, measured from the last pre-episode close
                          of 1881.722) -- but the reclaim itself is marginal, barely above the
                          causal H1 EMA50 (+0.023pt, the thinnest margin recorded)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.0986 (margin +0.023pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. A genuinely different character from the
recent overshoot-REJECTED run: a LOW retracement (37%, technically inside the 23-89% SUPPORT-
compatible range on that single metric) but with none of the other required SUPPORT components --
no fresh extreme, no volume concentration at the extreme, no extended duration or sustained
elevated volume, and the reclaim itself is barely above EMA (+0.023pt), a weak, marginal move
rather than a decisive one. Per the established discriminator, a partial retracement alone,
without any of the other supporting components, does not meet the SUPPORT bar. REJECTED.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** this instance is a useful
counter-example to a naive retracement-only read -- a low retracement percentage is necessary but
not sufficient for SUPPORT; the reclaim's own decisiveness (margin above EMA, volume behind the
move) matters independently.

---

## Q4-P007-078

```
GATE_ORIGIN_BAR          5703 (2020-12-29 10:30:00 UTC) -- the first genuine break of the
                          1875.2-1875.4 floor zone tested repeatedly since -071
TRIGGER_CLOSE                1877.098
TRIGGER_LOW                   1874.342 -- undercuts the whole floor zone (below both -073's
                              1875.236 and -074's 1875.358) for the first time in six episodes;
                              not an all-time Q4 record, but a genuine fresh local extreme
CAUSAL_H1_EMA50_AT_5703       1879.1615
GAP                            -2.0635pt -- the largest gap of the entire -070 through -078 stretch
VOLUME                          1182 -- real/heavy, the heaviest single-bar volume of the whole
                                 recent stretch, and lands right at the trigger/break bar itself
```

**PRE-CLASSIFICATION:** leaning toward taking this seriously -- unlike the six prior candidates in
this stretch, this one finally breaks the repeatedly-tested floor with real, heavy volume landing
right at the break. Genuine escalation, not a marginal touch. Not pre-committing -- watching for
real continuation vs an early fade (per the -013 precedent, even real trigger-bar magnitude has
fully reversed before). POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5705 (2020-12-29 11:00:00 UTC)
DURATION                2 bars (5703-5704)
DEEPEST_LOW              1874.342 (bar 5703, the origin bar itself) -- the deepest point of the
                        whole episode; a genuine fresh local extreme, but never built on
HEAVIEST_VOLUME          1182 (bar 5703, the origin bar) -- collapsed immediately and completely
                        (243, then 316 on the following two bars), an isolated spike with zero
                        follow-through
RECLAIM_CLOSE             1879.273 -- a near-complete round-trip: ~98% of the 5.032pt decline
                          (4.931 of 5.032, measured from the last pre-episode close of 1879.374)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.1615 (margin +0.111pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. Despite the pre-classification's genuine
leaning-toward-seriousness -- a real fresh floor break on heavy volume -- the episode fizzled
completely: volume collapsed immediately and the retracement reached a near-total 98% within just
2 bars. This is the isolated-spike-with-no-follow-through signature (-008/-009/-012) compounding
with the near-complete-round-trip signature (-013/-051/-061/-069/-078) -- both point the same
direction. REJECTED.
**OBSERVATIONAL NOTE (per CEO Q4 audit guidance, not a formal rule):** confirms the standing lesson
from -013 that even a genuinely credible trigger bar (fresh extreme + heavy volume + large gap) can
still fully reverse within 2 bars -- no combination of favorable trigger-bar characteristics
guarantees follow-through; only the subsequent bars can confirm it, and this record continues to
show that isolated spikes without sustained volume are consistently unreliable regardless of their
initial size.

---

## Q4-P007-079

```
GATE_ORIGIN_BAR          5706 (2020-12-29 11:15:00 UTC) -- immediately after -078's own reclaim
                          (bar 5705)
TRIGGER_CLOSE                1878.074
TRIGGER_LOW                   1877.03 -- still above -078's own low (1874.342); NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5706       1879.1059
GAP                            -1.0319pt -- moderate
VOLUME                          371 -- thin-moderate
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme, moderate gap, thin-moderate volume.
Reverts to the same low-conviction profile that dominated -071 through -077, now that -078's own
promising break has already faded. Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5711 (2020-12-29 12:30:00 UTC)
DURATION                5 bars (5706-5710)
DEEPEST_LOW              1875.832 (bar 5710) -- still above -078's own low (1874.342) and even the
                        earlier 1875.2-1875.4 floor zone; NOT a fresh extreme
HEAVIEST_VOLUME          514 (bar 5709) -- moderate, lands 2 bars before the deepest low, not
                        concentrated at the extreme
RECLAIM_CLOSE             1879.518 -- a full overshoot: ~107% of the 3.441pt decline from the last
                          pre-break close (1879.273)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.0364 (margin +0.482pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. REJECTED, consistent with the whole -071
through -079 stretch: no fresh extreme, volume not concentrated at the extreme, and a full-overshoot
retracement. The -078 floor break remains an isolated exception in this stretch rather than the
start of a new trend.

---

## Q4-P007-080

```
GATE_ORIGIN_BAR          5712 (2020-12-29 12:45:00 UTC) -- immediately after -079's own reclaim
                          (bar 5711)
TRIGGER_CLOSE                1878.4
TRIGGER_LOW                   1877.522 -- still above all recent floors; NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5712       1879.0364
GAP                            -0.6364pt -- shallow-moderate
VOLUME                          480 -- moderate
```

**PRE-CLASSIFICATION:** leaning REJECTED -- no fresh extreme, shallow-moderate gap and volume,
continuing the same low-conviction pattern that has dominated since -071 (with -078 as the lone
exception, which itself faded). Not pre-committing. POSITION=FLAT; no MGMT-004 relevance.

### RESOLUTION

```
STATUS               REJECTED -- not a genuine PATTERN-007 instance
RESOLUTION_BAR         5714 (2020-12-29 13:15:00 UTC)
DURATION                2 bars (5712-5713)
DEEPEST_LOW              1874.44 (bar 5713) -- just 0.098pt above -078's own low (1874.342);
                        essentially retesting rather than breaking it, NOT counted as fresh
HEAVIEST_VOLUME          1202 (bar 5713) -- real/heavy, comparable in magnitude to -078's own
                          trigger volume (1182)
RECLAIM_CLOSE             1879.206 -- a near-complete round-trip: ~94% of the 5.078pt decline
                          (4.766 of 5.078, measured from the last pre-episode close of 1879.518)
CAUSAL_H1_EMA50_AT_RESOLUTION 1879.0115 (margin +0.195pt)
```

No trade open; no MGMT-004 relevance. No S5 trigger. A close echo of -078's own resolution: real,
heavy volume at the break bar, a low that essentially retests (but doesn't clear) the recent floor,
and a near-complete retracement (94% in just 2 bars) -- REJECTED for the same reasons, reinforcing
that this whole zone has become a genuine, repeatedly-defended support level that heavy volume
alone has twice failed to break through decisively.

---

## Q4-P007-081

```
GATE_ORIGIN_BAR          5715 (2020-12-29 13:30:00 UTC) -- immediately after -080's own reclaim
                          (bar 5714)
TRIGGER_CLOSE                1877.15
TRIGGER_LOW                   1877.096 -- still above -078's low (1874.342) and -080's low
                              (1874.44); NOT a fresh extreme
CAUSAL_H1_EMA50_AT_5715       1879.0115
GAP                            -1.8615pt -- the second-largest gap of this whole recent stretch
                                 (after -078's -2.06)
VOLUME                          858 -- real/moderate
```

**PRE-CLASSIFICATION:** genuinely watching -- a larger gap and real volume, similar in scale to
-078/-080's own trigger characteristics, both of which ultimately faded despite credible starts.
No fresh extreme yet. Leaning REJECTED given the established pattern in this zone, but not
pre-committing -- this defended floor has shown real volume before without genuine follow-through.
POSITION=FLAT; no MGMT-004 relevance.
