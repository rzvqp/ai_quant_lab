# AI_TRADER_REGIME_STRATEGY_MATRIX

Permanent, continuously-maintained tracker per CEO directive (2020-05-06 in-replay / PERMANENT
APPRENTICESHIP OBJECTIVE). Updated at every quarterly checkpoint and whenever a regime's status
materially changes. Regimes may overlap; not forced mutually exclusive. Nothing here is invented —
every entry reflects genuine forward-observed experience or is explicitly marked as not yet observed.

Last updated: 2020-05-08 16:00 UTC (in-replay). The 1709.7-1713.73 zone -- just logged as the
strongest role-reversal instance yet -- has now FAILED: a false upside reclaim (weak volume, 439)
was immediately followed by a real-volume (4010) close-based break below the entire zone. Logged
honestly as a counterexample to the R02 role-reversal pattern, not smoothed over. See R02 and R11
below.

EVIDENCE UPGRADE V1 installed 2020-05-27 (replay clock) per CEO mandate: measurement/
learning instrumentation only (R-normalized metrics, actual-vs-static-baseline tracking,
prospective context tags, strategy evidence denominators, regime transition watch). Does
NOT change any entry logic, confirmation rules, or regime definitions below. See
EVIDENCE_UPGRADE_METHODOLOGY_V1.md, TRADE_EVIDENCE_LOG.md, STRATEGY_EVIDENCE_DENOMINATOR.md,
REGIME_TRANSITION_WATCH.md.

---

## R01 — CLEAN_BULL_TREND
STATUS: REGIMES_WITH_INSUFFICIENT_EXPERIENCE
EXPERIENCE_SEEN: none this quarter. H4 context has been BEARISH continuously since Q2 began (unbroken
through 44 trades). Q1 checkpoint (pre-dates this file) may hold relevant history not re-summarized
here.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

## R02 — CLEAN_BEAR_TREND
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: the standing H4 context for the entire Q2 walk so far. No genuine H4 structural break
has occurred.
KEY_BEHAVIORS: countertrend M15 bounces off reaction lows with real-volume structure breaks have
produced several wins (trades #38-41 family) even though the HTF context stayed bearish throughout —
these are NOT trend-following trades, they are bounded countertrend plays inside a still-intact
downtrend.
PLAYBOOKS: none frozen. The countertrend-bounce pattern (reaction low + 2 consecutive closes above
minor structure + real-volume follow-through) has repeated enough (trades #38, #39, #40, #41) to be a
DEVELOPING_PATTERN candidate but lacks a frozen stop/target/management spec — see Part 4 of the status
report for the honest gap.
UPDATE 2020-05-08: the role-reversal sub-pattern (a broken resistance zone holding as new support)
now has 3 distinct instances with growing real-volume confirmation: (1) after trade #42's floor break
(thin/moderate volume), (2) after trade #45's compound zone break (thin-volume dips, held), (3) this
session — a near-record-volume breakdown bar (5483) drove price into and briefly below the
1709.7-1713.73 zone across 4 consecutive real-volume bars, and it still held, confirmed by a strong
real-volume reversal back above it. This third instance is meaningfully stronger evidence than the
first two (real volume throughout the test, not just on the reversal). Still OBSERVATION_ONLY — no
stop/target/management spec exists for trading the role-reversal hold itself (as opposed to the
original zone-break trades already taken).
UPDATE 2020-05-08 16:00 UTC — COUNTEREXAMPLE: the same zone just cited above as the strongest
role-reversal instance has now FAILED. Sequence: a false upside reclaim (close 1715.424, weak volume
439) was immediately followed, one bar later, by a genuine close-based break below the entire zone
(close 1709.367, real volume 4010 — not record, but not thin either). The zone survived two
consecutive near-record-volume internal-close tests (5115, 4957) yet still ultimately broke on a
smaller-volume bar shortly after. Candidate mechanism (n=1, NOT promoted): repeated high-volume tests
that don't individually close through a level may still absorb/exhaust its defense, such that a later,
lower-volume bar completes the break once the defenders are used up. This directly complicates the
role-reversal pattern — holding through record-volume tests did NOT guarantee the zone would hold
overall. Both the earlier "held" instances and this "failed" instance are kept in the record; neither
is deleted or reinterpreted to fit the other.
FAILED_IDEAS: none formally logged yet as failed strategies (individual losing trades within the
pattern exist, but the pattern itself hasn't been retired). The role-reversal PATTERN itself is not
being retired off one counterexample — but it is no longer being treated as strengthening
monotonically with each successive real-volume test, which was the (incorrect) implicit assumption
building through the last several updates.
COUNTEREXAMPLES: trade #39, #41 losses within the same countertrend-bounce family. The 1709.7-1713.73
zone's ultimate failure (2020-05-08 16:00 UTC) after being logged as the strongest role-reversal
instance yet is now the pattern's clearest counterexample.
OPEN_QUESTIONS: is there a genuine TREND-FOLLOWING (not countertrend) playbook for this regime? Not
yet tested — every real-volume breakdown attempt this session (trades #42-44) was itself a
continuation-with-the-trend SHORT, but none has yet produced a clean, uncomplicated win under the
now-corrected close-based convention (trade #42 -1.376, #43 -6.599, #44 -0.453 — all losses).
UPDATE 2020-05-11 20:15 UTC — trade #46 (SHORT, entry 1699.075, exit 1698.217, +0.858pts) ends the
0-for-4 run: the first clean, trend-aligned continuation SHORT win of the apprenticeship. Trigger was
a PRE-COMMITTED SHORT_IF (defined before the triggering bar was revealed) off a paired 5001+5579
real-volume test of the (twice-broken) 1699.567-1701.044 zone — the first time two consecutive
very-large-volume bars appeared at that zone all week. Honest caveat: the win is modest relative to
the ~4.68pts of unrealized profit seen at the deepest point of the trade (18:15 UTC) — the 2-trail
stop management gave back roughly 3.8pts before triggering. Not concluding whether the trail pace was
too loose or appropriately conservative (it also correctly avoided being shaken out by an earlier,
more dangerous 16:15-16:45 pullback that wicked to within 0.1pt of the eventual exit). n=1 for a clean
trend-following win in this regime — genuinely new evidence, not yet enough to answer the open question.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET — but the open question above now has its first
supporting data point (trade #46) alongside the 3 contradicting ones (#42-44).

## R03 — WEAK_CHOPPY_TREND
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: much of the M15 price action inside the standing H4 BEARISH context has actually been
choppy/two-sided rather than cleanly trending — see R04/R11 below, which better describe the actual
M15 texture.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

## R04 — RANGE_BALANCED_MARKET
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: extensive — this is the single most-observed M15 texture of the entire post-pilot V2
stretch. The 1699.567-1701.044 zone and (separately) the 1709.7-1713.73 zone each functioned as
genuine two-sided battlegrounds for multiple sessions.
KEY_BEHAVIORS: TOC-003 (continuation-vs-stall after a heavily-defended level finally breaks) is the
clearest range-adjacent finding — see TOC-003 status below.
FAILED_IDEAS: CORRECT_NO_TRADE_003/004/005 — three separate real-volume triggers off range boundaries
that fired but failed their own confirmation bar; correctly declined each time, not traded.
COUNTEREXAMPLES: none yet for TOC-003 itself within this stretch (see TOC-003 section).
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET (TOC-003 is the closest candidate but is not yet a
complete playbook — see Part 4 gap analysis)

## R05 — HIGH_VOLATILITY
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: 2020-05-05/06 produced the most volatile stretch of the apprenticeship so far —
multiple 2000-5300 volume M15 bars, a session volume record (5311, later matched at 5209), sharp
multi-point reversals within single bars.
KEY_BEHAVIORS: real-volume triggers in this regime have a notably HIGH failure-to-confirm rate this
session (CORRECT_NO_TRADE_003/004/005 all occurred inside high-volatility stretches); when a trigger
DID confirm and get traded (trades #42-44), all three lost money under the corrected close-based
convention despite looking clean at entry.
OPEN_QUESTIONS: is high volatility itself adverse to this apprenticeship's current entry/confirmation
logic, or is this a small-sample artifact (n=3 traded, n=3 losses)? Genuinely uncertain — flagging, not
concluding.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

## R06 — LOW_VOLATILITY_COMPRESSION
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: extensive — multiple overnight/Asia-session stretches with volume as low as 21-60 per
bar, holding tight sub-5-point ranges for 8+ consecutive bars.
KEY_BEHAVIORS: thin-volume approaches to key zones explicitly do NOT count as real tests under this
apprenticeship's standing discipline (repeatedly applied, e.g. the drift toward 1699.567-1701.044
across several thin batches without being treated as a genuine test).
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET — this regime has produced zero trade attempts by design
(the discipline is specifically to NOT trade thin-volume drift), which is itself a working NO-TRADE
filter, not a strategy.

## R07 — VOLATILITY_EXPANSION
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
EXPERIENCE_SEEN: the transition from R06 (thin overnight) into real London/NY volume has been observed
repeatedly and cleanly (e.g. the 2020-05-05 session: volume went from 21-106 to a 5311 record within a
few hours).
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

## R08 — BULLISH_TRANSITION (bear/range to bull)
STATUS: REGIMES_WITH_INSUFFICIENT_EXPERIENCE
EXPERIENCE_SEEN: none — no genuine H4 structural reversal has occurred this quarter.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET
UPDATE 2020-06-08 10:45 UTC (CEO-directed regime staleness audit) -- STATUS unchanged, but this
regime is now ACTIVELY WATCHED rather than untouched: no fresh low below 1670.438 in 68 hours, a
persistent thin-volume recovery leg, and the 1688.5 zone (trade #62's own stop) now held above for
~7 hours without a volume-confirmed retest-and-reject. Not yet sufficient to reclassify (one leg,
not a multi-swing higher-low structure; no real-volume confirmation). REGIME_STALENESS_WARNING =
ACTIVE on the formal H4_BEARISH classification, logged in full in REGIME_TRANSITION_WATCH.md.
Concrete triggers being watched: next real-volume test of 1688.5 either direction; whether the next
pullback holds above the 1670.438 area before pushing higher again.

## R09 — BEARISH_TRANSITION (bull/range to bear)
STATUS: REGIMES_WITH_INSUFFICIENT_EXPERIENCE
EXPERIENCE_SEEN: none clean — the H4 context was already BEARISH before this walk's current stretch;
no fresh transition INTO bearish has been observed within this file's scope.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

## R10 — CLEAN_BREAKOUT / PRICE_DISCOVERY
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS (upgraded from REGIMES_WITH_FAILED_IDEAS, 2020-05-07)
EXPERIENCE_SEEN: the 1709.7-1713.73 and 1699.567-1701.044 zones were each tested 7-8+ times with real
volume before either finally broke. Trading the break itself (trades #42-44) went 0-for-3 under the
corrected close-based fill convention. Trade #45 (2020-05-07) then produced the single largest win of
the apprenticeship (+10.265pts) trading a genuine close-based break of the SAME 1701.044 zone after
its deepest test yet (a full-zone-penetration bar that still closed back below it, hours earlier) --
and the same impulse also broke the 1713.73 zone in one continuous move (the first observed "compound
zone break," n=1, not yet a pattern).
KEY_BEHAVIORS: the discriminator between trades #42-44 (losses) and #45 (the biggest win) is not yet
understood -- all four had a real-volume trigger and a real-volume confirmation bar under the same
TOC-003-style discipline. Open question: does the DEPTH/COUNT of prior real-volume defenses (8+ for
trade #45's level vs. 2-4 for trades #42-44's levels) matter, or does confirmation-bar VOLUME MAGNITUDE
matter (trade #45's confirmation was a new session record, 6282; trades #42-44's confirmations were
smaller), or is this still just small-sample noise (n=4)? Not concluding -- flagging for future
instances to help discriminate.
FAILED_IDEAS: trading a breakout/breakdown purely on TOC-003-style confirmation, without regard to how
many times the level was defended or the confirmation bar's relative volume size, is still unproven
(1-for-4 this session).
UPDATE 2020-05-11 10:00 UTC -- a second break of the SAME 1699.567-1701.044 zone occurred (it had
reclaimed above 1701.044 at some point after trade #45, then was re-tested and broken again here).
New candidate discriminator flagged (n=1, NOT concluding): this break arrived via a steady multi-hour
real-volume GRIND lower (several consecutive moderate-real-volume bars drifting down, PL-0465/0466)
rather than a single sharp impulsive bar (which characterized both trade #45's win and the 2020-05-08
1709.7-1713.73 break). Open question added: does a "grind-then-break" mechanism behave differently
(more reliable continuation, since it reflects sustained absorption rather than a single shock) than
an "impulse break"? Genuinely untested -- watching this specific instance's continuation/stall as the
first data point.
UPDATE 2020-05-11 12:00 UTC -- outcome disclosed: the "grind-then-break" did NOT produce clean
continuation. After 2 real-volume confirming bars, the zone entered a ~2-hour, 7-bar whipsaw, then
reclaimed back ABOVE the zone with real volume (2317) -- the opposite resolution from the 1709.7 zone,
which whipsawed once then continued lower. The "grind-then-break more reliable" hypothesis from
2020-05-11 10:00 UTC is NOT supported by this instance -- logged as a genuine counterexample to that
candidate discriminator, not smoothed over. Both discriminators floated so far (defense depth, confirmation
volume, break mechanism shape) remain unresolved at n=1-2 each.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET -- but this is now the regime with the single strongest
positive data point (trade #45) of the entire apprenticeship, worth prioritizing for further evidence.
UPDATE 2020-05-13 15:45 UTC -- trade #47 (LONG, entry 1715.882, exit 1711.65, -4.232pts) tested the
strictest entry discipline yet at the 1709.7-1713.73 zone: TWO consecutive real-volume closes above
1713.73 (6199, 6305 volume) after the longest sustained massive-volume battle of the entire
apprenticeship (6+ bars >2400 volume across ~2 hours, including a violent breakout-then-reversal and
multiple knife's-edge tests). The reclaim held for exactly 2 bars before failing on the 3rd. This
zone has now defeated every discriminator/entry-shape tried this week: sharp-impulse break (#42-44
losses), grind-then-break (whipsawed), thin-then-real-volume sequence (violently reversed same day),
and now a full 2-bar real-volume-confirmed reclaim. Open question flagged honestly, NOT concluded:
is 1709.7-1713.73 specifically anomalous/adversarial this quarter, or is there a real mechanism (e.g.
a large resting order, an options strike, a round-number effect at ~1710-1714) making it structurally
resistant to standard continuation entries regardless of confirmation rigor? Worth tracking as its own
candidate observation for a future context, not answerable from current evidence.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-14 17:30 UTC -- trade #48 (LONG, entry 1731.446, exit 1730.03, -1.416pts) tested the
same 2-consecutive-real-volume-close entry discipline at a genuinely FRESH, independent zone
(1721.822-1723.654, vol 3492/8448 near the apprenticeship's single-bar volume record), deliberately
distinct from the resistant 1709.7-1713.73 zone where trade #47 failed. Outcome: also a loss, but via
a DIFFERENT failure mechanism than trade #47's fast 2-bar rejection -- trade #48 extended strongly
first (+4.034pts unrealized at its peak, 16:15 UTC), then gave that back through a genuinely-defended
3-bar real-volume battle (16:45-17:15 UTC, including a stop-level wick at 17:00 UTC that closed back
above, per the close-based convention) before finally breaking the trailed stop on the 4th bar as
volume faded (3562->3140->2281->1407). Two consecutive 2-bar-real-volume-confirmed entries have now
both lost (#47 and #48), but the entry mechanism itself is not the obvious common thread -- the
failure shapes were different (fast rejection vs. slow give-back-after-extension), while what IS
common to both is that both are COUNTERTREND LONGS against a BEARISH H4 context. Flagging honestly,
not concluding at n=2: does 2-bar real-volume confirmation specifically underperform on countertrend
entries against the dominant H4 trend, regardless of which zone or failure shape? Worth tracking as
its own candidate discriminator for future countertrend attempts.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-15 14:00 UTC -- trade #49 (LONG, entry 1743.151, exit 1737.712, -5.439pts) is now the
THIRD consecutive countertrend LONG loss this window, and a genuinely important data point: it was
entered on the STRONGEST confirmation sequence of the three (2 consecutive real-volume closes of
4836 and 2317 -- more than double the ~2000+ threshold, after three earlier failed confirmation
attempts that session had already been correctly declined). It still lost, and by the WIDEST margin
of the three (#47 -4.232, #48 -1.416, #49 -5.439). The failure mechanism was again distinct: three
consecutive large-real-volume bars (5096, 3729, 6058, each exceeding the entry sequence's own
volume) progressively tested and finally broke the stop zone -- this reads as genuine, determined
selling pressure, not a thin/unconfirmed fakeout. Stop management was correct throughout (two
prior wicks at 13:30/13:45 UTC were honestly NOT fills per the close-based convention and were
correctly held through; the final close crossing was taken immediately).
Updating the open question from the trade #47/#48 note: stronger real-volume confirmation-bar
volume did NOT protect this trade -- if anything it produced the worst outcome of the three. At
n=3, all countertrend LONGS against this BEARISH H4 context have lost, regardless of confirmation
strength or failure shape (fast rejection / slow give-back / progressive large-volume rejection).
This is starting to look less like "confirmation discipline needs refinement" and more like a
structural signal: entering LONG against a dominant BEARISH H4 trend may carry a real, mechanism-
level disadvantage (more determined counter-trend sellers available at any zone) that 2-bar
real-volume confirmation, however strong, does not discriminate away. NOT concluding this formally
at n=3 -- flagging it as the leading candidate hypothesis for the next countertrend attempt, and as
a genuine open question for whether the standing entry discipline should treat WITH-trend and
AGAINST-trend real-volume breakouts as two different setups rather than one.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-15 18:00 UTC -- trade #50 (LONG, entry 1744.135, exit 1742.366, -1.769pts) is now the
FOURTH consecutive countertrend LONG loss this window. This was the single strongest entry of all
four by every measure: the cleanest 2-bar real-volume confirmation of the session (4292/4396, both
closing near their own highs), a well-formed rising-lows structure that justified two disciplined
stop trails, a guaranteed-profit-locking stop after the 2nd trail, and the most favorable intrabar
development of any of the four (+6.691pts unrealized intrabar at 17:45 UTC's high of 1751.718). It
STILL lost -- a large real-volume reversal bar (3422) plunged straight through the trailed stop and
closed even below entry. ALL FOUR countertrend LONGs against this BEARISH H4 context have now lost
this window (#47 -4.232, #48 -1.416, #49 -5.439, #50 -1.769), via four distinct failure mechanisms
(fast rejection / slow give-back-after-extension / progressive large-volume rejection / sharp
reversal-through-a-well-managed-trailed-stop). At n=4, with the best-managed and best-confirmed
attempt of the four still failing, this is no longer read as "confirmation discipline needs
refinement" -- it is now the apprenticeship's leading structural finding: entering LONG against a
dominant H4 trend appears to carry a genuine, mechanism-level disadvantage that neither entry
confirmation strength nor disciplined stop management fully offsets. STILL not formally promoted to
a hard rule (n=4 within one trending quarter is not enough for that), but this is now strong enough
evidence to actively bias future entry decisions: a countertrend real-volume setup should be treated
as needing a meaningfully higher bar of evidence than a with-trend setup, not treated as equivalent.
SEPARATE, independently important correction from this trade: the 16:30 UTC 2nd trail was described
in the H4 log as "locking in guaranteed profit" (stop above entry). That framing was WRONG and
directly falsified by this trade's own exit -- the close-based fill convention means the exit price
is the triggering bar's own CLOSE, not the nominal stop level, so a single large-volume bar can
plunge straight through the stop and close below both the stop AND the entry. "Stop is above entry"
bounds the LOSS-side risk on ordinary bars but does NOT guarantee a profitable worst case when
volatility/volume spikes on the triggering bar itself. This nuance was absent from every prior trail
description this apprenticeship (trades #45/#46/#48/#49 all used similar "locks in X minimum"
language) -- those specific numeric claims should now be read as describing the STOP LEVEL's
relationship to entry, not a true floor on the realized exit price, going forward.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-18 16:30 UTC -- trade #51 (SHORT, entry 1754.79, exit 1732.404, +22.386pts) is the
FIRST WITH-trend (BEARISH H4) real-volume entry attempted this window, immediately following the
four consecutive countertrend LONG losses (#47-#50). It is the single largest winning trade of the
entire apprenticeship (prior best +10.265pts, trade #45), entered on exceptional 2-bar confirmation
(4532, 8149) after ~17hrs of real-volume silence, breaking a long consolidation. Managed through 6
disciplined stop trails, survived several of the largest-volume bars of the apprenticeship (7576,
9045) and one sustained 4-bar consolidation battle that resolved favorably, before finally closing
out from its peak (+25.257pts unrealized) at +22.386pts realized.
This is genuine, concrete n=1 evidence directly supporting the open hypothesis raised after trade
#50: that WITH-trend real-volume entries may carry a structural advantage over countertrend ones
that neither confirmation strength nor stop discipline alone can produce for the countertrend side.
Explicitly NOT concluding a formal WITH-trend edge from a single trade -- but the magnitude and
cleanliness of this result, immediately following four countertrend failures under otherwise
identical discipline, is the strongest single data point the apprenticeship has produced on this
question. Leading candidate discriminator going forward: entry direction relative to the dominant
H4 trend may matter more than confirmation-bar volume size, entry cleanliness, or any factor
examined so far. Worth prioritizing further WITH-trend vs. countertrend real-volume entries as
directly comparable evidence in future contexts.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-19 12:45 UTC -- trade #52 (SHORT, entry 1733.911, exit 1735.654, -1.743pts) is the
SECOND WITH-trend (SHORT, BEARISH H4) real-volume entry this window. Unlike trade #51, this one
lost -- a real-volume reversal bar (3469) took out a genuinely tight trail (0.459pts risk) that had
been applied after only 2 bars of continuation, versus trade #51's trails which came after more
developed multi-bar structure. Honest, mixed result at n=2 for WITH-trend: #51 WIN +22.386, #52
LOSS -1.743. This is genuinely important -- WITH-trend entries are NOT automatically winners, and
the open hypothesis from trade #51 (that WITH-trend carries a structural advantage) is NOT
confirmed as a clean win-rate edge at n=2. What DOES hold up at n=2: the WITH-trend loss (-1.743)
is far smaller in magnitude than any of the four countertrend losses this window (#47 -4.232, #48
-1.416 [close but smaller], #49 -5.439, #50 -1.769) -- actually #48 is comparable in size, so even
this magnitude observation is not yet clean. Flagging a SEPARATE, likely more actionable finding
from trade #52's specific failure mode: trailing this tightly (sub-0.5pt risk) after only 2 bars of
real-volume continuation may be premature regardless of trend direction -- trade #51 didn't trail
this tight until much more structure had formed. Candidate discriminator for future trades: require
more bars of continuation (or a clear consolidation/pause) before applying a very tight trail, not
just direction relative to H4 trend. Not concluding either hypothesis formally; both remain open
with genuine, sometimes conflicting evidence.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-19 15:00 UTC -- trade #53 (LONG, entry 1739.969, exit 1739.222, -0.747pts) was the
strongest-confirmed countertrend LONG of the entire window (volume comparable to trade #50's
confirmation), survived the two largest single-bar volumes of the entire apprenticeship (10582,
8359) moving against it, reversed to genuine profit with a confirmed multi-bar structure, and
STILL closed as a loss when a final sharp reversal (2872 volume) plunged through its trailed stop.
This is now n=5 for countertrend LONGs against BEARISH H4 this window: ALL FIVE have lost (#47
-4.232, #48 -1.416, #49 -5.439, #50 -1.769, #53 -0.747). The countertrend-disadvantage hypothesis
is now considerably stronger evidence at 5/5 -- while still not a formal validated rule (n=5 within
one trending quarter, all against the same H4 direction, is not independent enough to promote to a
strategy), the pattern is now the single most consistent finding of this apprenticeship. Genuinely
useful nuance alongside the losing streak: loss magnitudes have shrunk monotonically with better
confirmation/management (#49's -5.439 down to #53's -0.747), suggesting confirmation quality and
management discipline DO help even though they have not yet flipped a single countertrend attempt
into a win this window. SEPARATE finding also confirmed here: this is the SECOND instance (after
trade #50) of a "profit-locking" trail still producing a loss because the triggering bar plunged
through both the stop and the entry -- now treated as an established, recurring risk of the
close-based convention under real-volume reversals, not a one-off.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-20 18:00 UTC -- trade #54 (SHORT, entry 1744.494, exit 1752.328, -7.834pts) is the
THIRD WITH-trend (SHORT, BEARISH H4) real-volume entry this window, and by entry-quality alone the
best of the three: 2 consecutive real-volume closes lower (2371/5219), the 2nd being a decisive,
large single-bar move, stronger confirmation than trade #52's. Management was arguably flawless too
-- it survived a genuine 2-consecutive-massive-volume-adverse-bar stress test including a wick that
pierced the stop by 0.341pts while the close stayed clear (the close-based convention working IN the
trade's favor that time), never traded tight/premature per the trade #52 lesson (never trailed at
all, since the position was never genuinely profitable -- closest approach was ~-1.126pts). It still
lost, and lost by MORE than trade #52 (-7.834 vs -1.743), on a razor-thin final close only 0.049pts
past the stop on unremarkable thin volume. WITH-trend n=3 this window: #51 WIN +22.386, #52 LOSS
-1.743, #54 LOSS -7.834 -- now 2 losses out of 3, and the aggregate WITH-trend record (+22.386
-1.743 -7.834 = +12.809) is still net positive purely on trade #51's single large win, not on a
favorable win rate (1/3). This meaningfully TEMPERS the earlier tentative lean (from trade #51 alone)
toward "WITH-trend carries a structural advantage over countertrend" -- entry-trigger strength and
disciplined management (both genuinely present in trade #54) did not translate into a safer or more
likely-to-win outcome here. Neither the WITH-trend-advantage hypothesis nor its rejection is being
formally concluded at n=3 (too small, single trending quarter, single H4 direction) -- but the honest
picture is now considerably more mixed than after trade #51, and the practical takeaway is that
WITH-trend entries should NOT be treated as materially safer bets than countertrend ones on current
evidence, even though the entry bar itself does not need the elevated countertrend evidence threshold.
SEPARATE finding: trade #54 gives the cleanest illustration yet of the close-based convention's exact
mechanics -- it survived a much larger wick-through (0.341pts, high volume) earlier in the same trade
but was taken out by a much smaller close-only breach (0.049pts, unremarkable volume) later. Wick
depth and volume at the moment of the touch are irrelevant to the convention; only the closing print
matters. This is not a new risk (already established via trades #50/#53's plunge-through pattern) but
the first case within a single trade of surviving a bigger threat and later succumbing to a smaller
one, worth keeping as a vivid reference example.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-21 16:30 UTC -- trade #55 (SHORT, entry 1728.586, exit 1725.33, +3.256pts) is the
FOURTH WITH-trend (SHORT, BEARISH H4) real-volume entry this window, and by entry-quality the
strongest of all: 2 consecutive real-volume closes lower (5410/7730), the largest, most decisive
confirmation sequence of the entire apprenticeship, exceeding even trade #54's own strong 2371/5219
pair. Management was disciplined: explicitly declined a premature trail at 14:30 UTC that would have
mirrored trade #52's known mistake (tightening to ~0.636pts risk after only 2 bars of continuation),
instead waiting for genuine 2-bar pullback structure before trailing once at 15:00 UTC. The trade
survived a wick-through at 15:15 UTC (close-based convention working in its favor again) before
finally closing on a razor-thin close-only breach (0.05pts past the stop, thinner even than trade
#54's 0.049pts) -- but because the trail had been moved into profit territory, this produced a WIN
rather than a loss. WITH-trend n=4 this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834,
#55 WIN +3.256 -- now an even 2/2 win rate, aggregate +16.065pts (still positive, still driven more
by magnitude of wins than by win rate). This is a genuinely useful, symmetric pair with trade #54:
both trades were stopped by a razor-thin close-only breach on unremarkable volume with the wick depth
and triggering-bar volume being irrelevant either way -- the ONLY difference was whether the trail
had already been moved into profit territory before that final bar. This crystallizes the practical
lesson from this WITH-trend cluster: disciplined trail management (patient but not absent) is what
converts a strong entry into a survivable/winning outcome under the close-based convention, more than
the entry-trigger strength itself. Neither the WITH-trend-advantage hypothesis nor its rejection is
concluded at n=4 -- still too small a sample within one trending quarter -- but the even win rate
combined with the clear management-quality signal is the most actionable finding from this cluster so
far.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-27 00:30 UTC -- trade #56 (SHORT, entry 1718.845, exit 1712.988, +5.857pts) is the
FIFTH WITH-trend (SHORT, BEARISH H4) real-volume entry this window, entered on one of the most
decisive confirmation sequences of the entire apprenticeship (real-volume 5051/9575). Trailed 5 times,
each on genuinely confirmed multi-bar structure (never prematurely, never razor-thin at the moment of
tightening) as unrealized grew to as much as ~+9.039pts. The final stop level (1712.888) was then
tested closely by wicks on roughly 6-7 separate bars across nearly 6 hours without a single close
crossing it, until a modest 0.1pts close-only breach finally triggered -- landing as a clear
+5.857pts win, not a breakeven scrape. This is the clearest demonstration yet of a specific, generalizable
lesson: because each trail in this trade was set with genuine structural distance (never chasing the
tightest possible level just because price was nearby), even the "worst case" eventual stop-out still
resolved as a solid win. Direct counterpoint to trades #54 and #55, whose final stops were also
razor-thin-triggered but had been left closer to entry/breakeven by comparison. WITH-trend n=5 this
window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834, #55 WIN +3.256, #56 WIN +5.857 -- now 3
wins / 2 losses, aggregate +21.922pts, the win rate turning positive for the first time in this
window's WITH-trend sample. Still too small a sample (n=5, one trending quarter, one H4 direction) to
formally validate a WITH-trend edge, but the accumulating evidence across #52/#54/#55/#56 increasingly
points to trail discipline and structural distance at each tightening step -- not entry-trigger
strength or raw win/loss outcome -- as the dominant driver of result quality under the close-based
convention. Worth carrying forward as the leading practical heuristic from this entire WITH-trend
cluster.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-05-27 17:15 UTC (ERRATUM-corrected; originally labeled 17:30 UTC, see
2020_Q2_H4_LOG.md's ERRATUM entry for the self-discovered 15-minute label-drift root cause -- true
entry was 16:30 UTC, not 16:45; figures below are unaffected) -- trade #57 (SHORT, entry 1706.11,
exit 1712.302, -6.192pts) is the
SIXTH WITH-trend entry this window, entered immediately after a sharp countertrend spike made a
fresh apprenticeship high (1710.66 intrabar) and then produced a 2-bar real-volume down-close
reversal confirmation. Never reached profit (best excursion only +0.628pts) so no trail was ever
applied -- a clean loss-with-plan, not a management mistake. The structural read ("spike
exhausting") was wrong in real time: price continued to a new extreme (1713.326) before the
close-based stop finally triggered. Under the new Evidence Upgrade V1 instrumentation, this is the
first trade with full forward MFE/MAE tracked (MFE +0.138R, MAE -1.586R, RESULT -1.361R) and a
STATIC_BASELINE comparison (identical to actual here, since the stop was never trailed --
ACTUAL_VS_STATIC = 0). WITH-trend n=6 this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS
-7.834, #55 WIN +3.256, #56 WIN +5.857, #57 LOSS -6.192 -- now 3 wins / 3 losses, aggregate
+15.730pts, the win rate receding from 3/5 back to 3/6 (50%) on this single additional trade. This
is itself informative: a headline win rate this sensitive to one more observation is further
confirmation that n=6 in one trending quarter/one H4 direction remains far too small to validate
anything. See STRATEGY_EVIDENCE_DENOMINATOR.md for the full qualifying-occurrence accounting.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-02 18:45 UTC -- trade #58 (SHORT, entry 1740.327, exit 1728.068, +12.259pts,
+2.463R) is the SEVENTH WITH-trend entry this window, entered on a 2-bar real-volume down-close
confirmation immediately after a fresh apprenticeship high (1745.304) was rejected. Managed with
two genuine pause-then-resume trails (1745.304 -> 1734.564 -> 1727.902), each placed with real
structural distance (recent swing highs), not razor-thin. Notably: mid-trade, the CEO corrected
this apprenticeship's own reporting language -- a trailed stop's "trigger level" (~2.50R here at
the final trail) is NOT a guaranteed REALIZED_RESULT_R, since the close-based fill lands at the
triggering bar's own close, which can land beyond the nominal stop. Trade #58 confirmed this
directly: the actual fill (1728.068) landed 0.166pts beyond the nominal stop, so the REALIZED
result (+2.463R) came in slightly below the ~2.50R trigger-level reference -- a small, real
illustration of the same close-based-fill mechanism that has driven razor-thin wins/losses
throughout this apprenticeship (trades #54/#55/#56/#57), just from the favorable side this time.
Full forward MFE/MAE tracked: MFE +3.743R (low 1721.698), MAE +0.109R (the trade's only real
adverse excursion, one bar after entry, before running favorable and never looking back).
STATIC_BASELINE (original entry/stop 1740.327/1745.304, never trailed) remained STILL_OPEN at the
moment of actual closure -- the original stop was never even threatened, so the shadow will
continue tracking forward until it resolves via its own close-trigger or the 192-bar/~48h horizon.
WITH-trend n=7 this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834, #55 WIN +3.256, #56
WIN +5.857, #57 LOSS -6.192, #58 WIN +12.259 -- now 4 wins / 3 losses, aggregate +27.989pts, the
win rate moving back to 57% on this single additional trade. Still far too small a sample (n=7,
one trending quarter, one H4 direction) to formally validate a WITH-trend edge, but the
accumulating pattern across #54/#55/#56/#57/#58 continues to point to trail discipline and
structural distance at each tightening step as the dominant driver of result quality, now further
sharpened by the trigger-level-vs-realized-result distinction.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-04 10:45 UTC -- trade #59 (SHORT, entry 1712.008, exit 1712.662, -0.654pts,
-0.046R) is the EIGHTH WITH-trend entry this window, entered on a decisive 2-bar real-volume
breakdown (combined volume 8358) after a fresh local-high rejection, with an unusually wide initial
stop (14.138pts, honestly reflecting the sharp move already covered before entry). Trailed once
(1726.146 -> 1711.9) after a genuine pause-then-resume/reject cycle and a decisive real-volume
continuation bar, at a level with TRAIL_TRIGGER_LEVEL_R of +0.008R (just below entry). Price then
spent ~68 bars in a thin-volume compression before a slow, mostly sub-threshold-volume grind
carried it back up and the trade was stopped out. This is the sharpest illustration yet of the
CEO's TRAIL_TRIGGER_LEVEL_R vs REALIZED_RESULT_R correction: the trigger level implied a small
positive result (+0.008R), but the actual close-based fill (1712.662) landed past BOTH the nominal
stop AND the entry price, flipping the sign entirely to a small genuine loss (-0.046R) -- unlike
trade #58's case (same sign, different magnitude), here the trigger reference was directionally
wrong. Full forward MFE/MAE tracked: MFE +1.586R (low 1689.589, corrected from an earlier
mislabeled intermediate figure -- disclosed in TRADE_EVIDENCE_LOG.md, measurement-only, no
decision impact), MAE +0.267R (high 1715.781, reached only on the closing bar itself, the trade's
single largest adverse excursion coming right at the very end). STATIC_BASELINE (original
entry/stop 1712.008/1726.146, never trailed) remained STILL_OPEN at the moment of actual closure
(~86/192 bars, original stop never threatened) -- will continue tracking forward like trade #58's
shadow. WITH-trend n=8 this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834, #55 WIN
+3.256, #56 WIN +5.857, #57 LOSS -6.192, #58 WIN +12.259, #59 LOSS -0.654 -- now 4 wins / 4 losses,
aggregate +27.335pts, win rate receding to 50% on this single additional trade -- again the
clearest practical evidence of how small n=8 (one trending quarter, one H4 direction) still is.
Trades #58 and #59 together, closing back-to-back with opposite-sign trigger/realized deltas, are
the strongest evidence yet that trail-trigger levels must never be reported as guaranteed outcomes.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-04 12:30 UTC -- trade #60 (SHORT, entry 1707.01, exit 1715.958, -8.948pts,
-1.379R) is the NINTH WITH-trend entry this window, entered on a fresh 2-bar real-volume (2700,
2912) breakdown just 75 minutes after trade #59 closed, ending the multi-hour compression that had
dominated the prior day/night. Only 2 bars into the trade, a decisive real-volume (7566, by far the
largest volume bar of this entire stretch) reversal bar closed well beyond the original,
never-trailed stop (1713.5) at 1715.958. This is the mirror-image risk of the CEO's trail-level
correction, now demonstrated on an UNTRAILED original stop and on the loss side: had the fill
landed exactly at the nominal stop, the loss would have been exactly -1.0R; the actual close-based
fill was -1.379R, 0.379R worse, because the triggering bar's own close overshot the stop by
2.458pts. Confirms the close-based-fill mechanism governs every stop in this apprenticeship, not
only trailed ones. MFE +0.223R (low 1705.56, the trade was never meaningfully profitable), MAE
+1.497R (high 1716.728, the closing bar's own high). STATIC_BASELINE = RESOLVED_VIA_ORIGINAL_STOP,
identical to actual (no discretionary management occurred -- too few bars had elapsed to trail).
WITH-trend n=9 this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834, #55 WIN +3.256, #56
WIN +5.857, #57 LOSS -6.192, #58 WIN +12.259, #59 LOSS -0.654, #60 LOSS -8.948 -- now 4 wins / 5
losses, aggregate +18.387pts, win rate receding to 44%. The headline win rate has now moved on
every single additional trade this window (57%->50%->44%), the clearest practical demonstration yet
of how small n=9 (one trending quarter, one H4 direction) remains. Trades #58/#59/#60 together, in
sequence, are the most complete illustration this apprenticeship has produced of the close-based
fill mechanism cutting in every direction -- favorable on a trail (#58), sign-flipping on a trail
(#59), and unfavorable on an untrailed stop (#60).
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-04 17:15 UTC -- trade #61 (SHORT, entry 1707.856, exit 1720.093, -12.237pts,
-1.150R) is the TENTH WITH-trend entry this window, entered on a 2-bar real-volume (4558, 2585)
resumption 90 minutes after trade #60's reversal. Three real-volume down-close bars gave a
promising start before a sustained adverse retracement developed, ultimately stopping the trade out
on its original (never-trailed) stop. The most instructive part of this trade: three consecutive
bars (16:15-17:00 UTC) had highs within 0.27-1.63pts of the stop and closed back below it,
surviving each time on the close-based convention, before a fourth bar's close finally broke
through -- a clean, repeated, practical demonstration of why this apprenticeship trades the
close-based (not wick-based) trigger convention. A wick-based rule would have exited on any of the
three survivals; the close-based rule correctly let the trade continue until a genuine close
confirmed the break. REALIZED_RESULT_R (-1.150) came in somewhat worse than the nominal -1.0R,
consistent with (though far milder than) trade #60's demonstration of the same overshoot mechanism.
Full forward MFE/MAE tracked: MFE +0.695R (low 1700.455), MAE +1.280R (high 1721.483, the closing
bar's own high). STATIC_BASELINE = RESOLVED_VIA_ORIGINAL_STOP, identical to actual. WITH-trend n=10
this window: #51 WIN +22.386, #52 LOSS -1.743, #54 LOSS -7.834, #55 WIN +3.256, #56 WIN +5.857, #57
LOSS -6.192, #58 WIN +12.259, #59 LOSS -0.654, #60 LOSS -8.948, #61 LOSS -12.237 -- now 4 wins / 6
losses, aggregate +6.150pts, win rate down to 40% and four losses in a row (#57 is not consecutive
with these three, but #59/#60/#61 are). This is the weakest stretch this playbook has shown all
window. Still NOT being read as strategy failure or a reason to change entry/exit rules -- n=10 in
one trending quarter/one H4 direction remains far too small to validate or invalidate anything, and
every qualifying occurrence has been taken per standing discipline, none cherry-picked. Combined,
trades #58-#61 now form the fullest practical illustration this apprenticeship has produced of the
close-based fill mechanism's full range of behavior: favorable-and-close, sign-flipping,
untrailed-overshoot, and wick-survival-then-eventual-break.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-08 03:45 UTC -- trade #62 (SHORT, entry 1680.167, exit 1688.509, -8.342pts,
-1.001R) is the ELEVENTH WITH-trend entry this window, entered on a 2-bar real-volume (6299, 7431)
resumption resolving an extreme 5-bar whipsaw episode (the highest-volume stretch of the entire
apprenticeship, one bar reaching 10603 volume). The trade's own resolution was itself a remarkable
illustration of the close-based convention: its stop (1688.5) was tested FOUR separate times over
the final 5 bars, with THREE distinct wicks piercing it outright (closest survival margin
0.147pts) before the eventual triggering close finally crossed it by just 0.009pts -- the
narrowest margin of the entire apprenticeship. Despite that drama, REALIZED_RESULT_R (-1.001)
landed almost exactly at the nominal -1.0R, a useful counterpoint to trade #60's demonstration
that close-based fills can overshoot meaningfully: repeated wick-piercing does not itself imply a
large closing overshoot. Full forward MFE/MAE tracked: MFE +1.168R (low 1670.438), MAE +1.058R
(high 1688.984, the closing bar's own high). STATIC_BASELINE = RESOLVED_VIA_ORIGINAL_STOP,
identical to actual (never trailed). WITH-trend n=11 this window: #51 WIN +22.386, #52 LOSS
-1.743, #54 LOSS -7.834, #55 WIN +3.256, #56 WIN +5.857, #57 LOSS -6.192, #58 WIN +12.259, #59
LOSS -0.654, #60 LOSS -8.948, #61 LOSS -12.237, #62 LOSS -8.342 -- now 4 wins / 7 losses,
aggregate -2.192pts, the FIRST TIME this window's WITH-trend aggregate has turned net negative,
on a fifth straight loss (#59-#62). Still NOT being read as strategy failure or a reason to change
entry/exit rules -- n=11 in one trending quarter/one H4 direction remains far too small to
validate or invalidate anything, and every qualifying occurrence has been taken per standing
discipline, none cherry-picked. The playbook's aggregate swinging from +27.989pts (peak, after
trade #58) to -2.192pts (now) on the exact same setup criteria is itself the clearest
demonstration yet of how unstable small-sample aggregates are -- a genuine lesson in humility
about reading short streaks in either direction, not evidence the setup itself changed. Trades
#58-#62 together now form the fullest practical catalogue this apprenticeship has produced of the
close-based fill mechanism's entire range: favorable-and-close, sign-flipping, untrailed-overshoot,
wick-survival-then-eventual-break, and repeated-piercing-yet-near-exact-close.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET.
UPDATE 2020-06-10 14:45 UTC -- trade #63 (LONG, entry 1695.555, exit 1718.742, +23.187pts,
+2.306R) is the SIXTH countertrend LONG against this BEARISH H4 context this apprenticeship, and
the FIRST TO WIN. Entered on a real-volume test-and-defend-then-continuation sequence (5674/6544)
at the 1688.5 zone, the first sequence to clear trade #53's elevated-evidence benchmark
(3544/5373) on both legs -- installed specifically because trades #47-#50/#53 (all losses) showed
no countertrend LONG entry discipline alone was sufficient against a dominant H4 trend. Classified
TRANSITIONAL LONG under Multi-Timeframe Trend Alignment V1 (H4 BEARISH unchanged, H1/M15 both
ALIGNED_LONG on confirmed real-volume evidence), not a bare countertrend label. Survived SIX
distinct wick-tests across four progressively-trailed stops (1685.5 -> 1692.9 -> 1696.394 ->
1706.478 -> 1721.134) over ~48.5 hours, including the deepest (2.323pts) and narrowest (0.252pts
survival) wick-tests of the trade's own life, before an eventual close-based stop-out on the
largest-volume reversal bar (6491) of the trade's entire duration. Countertrend LONG n=6 against
BEARISH H4 this window: #47 -4.232, #48 -1.416, #49 -5.439, #50 -1.769, #53 -0.747, #63 +2.306R
(pts: -4.232,-1.416,-5.439,-1.769,-0.747,+23.187) -- 1 win / 5 losses, first break in the
countertrend-disadvantage pattern that had been 5/5 losses through trade #53. This is genuine,
concrete evidence that the elevated-evidence-bar discipline (installed specifically in response to
the 5/5 losing streak) CAN produce a winning countertrend entry when the bar is genuinely cleared
-- but n=1 clearing instance is far too small to conclude the discipline "works"; the prior 5
losses were themselves entered on real, if lesser, confirmation too. STATIC_BASELINE comparison
(Evidence Upgrade V1): the untrailed shadow would have shown +3.0426R at its 48h horizon mark vs.
the actual trailed +2.306R -- one data point on trailing-vs-static tradeoffs, not concluded (see
TRADE_EVIDENCE_LOG.md for full detail). STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET -- but this
is now, alongside trade #45, one of the two strongest positive countertrend/breakout data points
in the entire apprenticeship, worth prioritizing for further evidence per the new Strategy
Candidate Formalization framework (TRADER_STRATEGY_CANDIDATES.md) once more forward evidence
accumulates.
UPDATE 2020-06-15 00:15 UTC -- trade #64 (SHORT, entry 1740.496, exit 1734.114, +6.382pts,
+1.443R) is the FIRST WITH-trend SHORT to pass live evaluation under the Multi-Timeframe forward
SHORT rule (installed 2020-06-08 specifically because the pre-correction Playbook A's bare 2-bar
test had gone 4W/7L including a 5-loss streak during unacknowledged H1/M15 bullish misalignment).
The rule's first live test (2020-06-11 14:00-14:30 UTC) correctly declined a technically-qualifying
but trivial-magnitude signal; this trade cleared the bar on a real-volume rejection (7023/4241
volume) at a twice-tested resistance zone (the 2020-06-11 whipsaw peak, 1744.918), classified
MULTITIMEFRAME_ALIGNMENT=PARTIALLY_ALIGNED (H4 formal bearish + fresh M15 rejection evidence, H1
broader phase not yet confirmed broken). Survived NINE distinct wick-tests across its life --
including a 0.031pt margin, the narrowest of the entire apprenticeship -- and was the FIRST trade
this apprenticeship carried through a weekend gap (GAP-072, 49.25 hours, exact price continuity,
no adverse jump materialized). This is genuine, concrete evidence that the corrected forward SHORT
rule can both correctly filter a weak signal (2020-06-11) AND correctly pass a strong one
(2020-06-12) -- n=1 win for the corrected rule's "passed" cases (n=2 total including the decline)
is far too small to validate the rule's overall calibration, but it is a clean first demonstration
that the rule discriminates rather than just blocking everything. STRATEGY_COVERAGE:
NO_VALIDATED_STRATEGY_YET.

## R11 — FAILED_BREAKOUT / WHIPSAW
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS (strongest evidence base of any regime)
EXPERIENCE_SEEN: this is arguably the best-evidenced regime in the entire apprenticeship right now.
TOC-003 (continuation-vs-stall discrimination after a heavily-defended level breaks) lives here.
CORRECT_NO_TRADE_003/004/005 are all whipsaw-avoidance instances. TOC-001 and TOC-002 (from Q1) are
also whipsaw/fade observations, though in different regimes (range-bound and high-volatility
respectively) — see TOC status below for how they relate. UPDATE 2020-05-07: a second, independent
heavily-defended level (1699.567-1701.044, distinct from the earlier 1709.7-1713.73 zone) has now
absorbed 8+ real-volume rejections including one full-zone-penetration bar (vol2151, high 1701.071)
that still closed back below the zone — the deepest test either level has taken. This strengthens
TOC-003's evidence base (two independently-observed 3+-defended levels in the same regime, not one)
without altering its definition or promoting it. UPDATE 2020-05-08 16:00 UTC: a genuine whipsaw
instance at the SAME 1709.7-1713.73 zone — a false upside reclaim (weak volume) immediately reversed
into a real-volume close-based breakdown one bar later. This is a whipsaw around the zone's upper
boundary, distinct from TOC-003 (which concerns the level's own eventual break after repeated
defenses) — flagged as a new, separate observation (n=1) of upside-fakeout-then-breakdown, not merged
into TOC-003's definition.
UPDATE 2020-05-11 12:00 UTC — a second, even more extreme whipsaw instance at the 1699.567-1701.044
zone (the deepest-defended level in the apprenticeship): after breaking with 2 real-volume confirming
bars (10:00-10:15), it whipsawed for ~2 hours across 7 bars (closes alternating above/below the zone
repeatedly) before reclaiming above it with real volume at 12:00. HONEST CROSS-INSTANCE COMPARISON
(n=2 whipsaws after a major zone break this week): the 1709.7 zone's whipsaw resolved DOWN (continued
the breakdown after one failed reclaim), while the 1699.567-1701.044 zone's whipsaw resolved UP
(reclaimed back above after a real-volume breakdown). Same surface pattern (break -> whipsaw), opposite
outcomes — this is genuinely important: it means "a major zone broke and then whipsawed" is NOT by
itself informative about the eventual direction with only n=2. Both instances are kept in the record
side by side, not merged into a single narrative. A real, validated discipline benefit WAS observed
in this second instance: requiring a second confirming bar before entering (applied at PL-0467/0468)
correctly avoided a trade that would very likely have been chopped up in the subsequent whipsaw.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET — TOC-003 is the strongest single candidate for eventual
promotion but is not yet a complete, frozen playbook (see Part 4 gap). The n=2 whipsaw-direction
ambiguity above is itself an argument for NOT trading the immediate post-break bar without a
confirming second bar, regardless of which direction the break went.
UPDATE 2020-05-12 14:00-16:00 UTC — the single most extreme real-volume event of the apprenticeship:
5 CONSECUTIVE bars all exceeding 5000 volume (8743 NEW record, 6563, 5474, 5393, 8420) at the 1709.7
boundary, oscillating across the exact line bar-to-bar (below/above/above/above/below) before finally
resolving DOWN as volume normalized. The zone held as resistance despite this being by a wide margin
the largest, most sustained real-volume test any level has faced this apprenticeship. This is the
strongest single data point yet for "defended-level resilience" (a level can survive even
extraordinary, sustained real-volume pressure) — but the SAME episode also produced the single most
dangerous whipsaw risk of the week: two consecutive bars carrying the largest and second-largest
volumes of the whole apprenticeship, in OPPOSITE directions, one bar apart. Both facts are kept side
by side deliberately — "the zone held" and "this was extremely whipsaw-dangerous mid-episode" are not
in tension, they are two true things about the same event. The 2-bar confirmation discipline was
validated a further two times during this episode (once after the initial rejection bar, once
implicitly by never having chased any of the 5 extreme bars individually).
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET — no trade was taken during this episode; still
NO_VALIDATED_STRATEGY_YET, but the evidence base for eventual TOC-003-style promotion is now
considerably stronger given this extreme, clean (in hindsight) resolution.
UPDATE 2020-05-13 13:00-16:45 UTC — a SECOND, even longer extraordinary episode at the SAME
1709.7-1713.73 zone: ~10 consecutive bars with volume in the thousands (most >5000, several >7000)
across ~3.5 hours, the longest sustained-volume stretch of the entire apprenticeship (surpassing
2020-05-12's in duration, though not in single-bar peak — no bar here reached 8743). This episode
included a violent breakout-then-reversal (13.7pt range in one bar), multiple knife's-edge tests
exactly at 1713.73, and a genuine 2-bar real-volume-confirmed reclaim (trade #47) that still failed
after holding for exactly 2 bars, for a clean -4.232pt loss. Net outcome: price round-tripped from
~1708 to ~1718 and back multiple times, ending back inside the zone with NO decisive break in either
direction, even under the most sustained real-volume pressure of the apprenticeship. HONEST STANDING
OBSERVATION (n=2 major episodes now, both at THIS specific zone): 1709.7-1713.73 has resisted
resolution under both extreme single-bar-record volume (2020-05-12) and extreme sustained-duration
volume (2020-05-13), and has now defeated every entry discipline tried against it this week
(sharp-impulse break, grind-then-break, thin-then-real-volume sequence, and 2-bar-confirmed reclaim —
see R10). Open question, not concluded: is this specific price zone genuinely anomalous/adversarial
for this quarter (e.g. a large resting order or round-number cluster around 1710-1714), or is "extreme
volume does not guarantee resolution" itself the real, generalizable lesson and this zone is simply
where it has been observed twice? Flagging for continued tracking, not resolving from n=2.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET — trade #47 (the one trade taken into this second
episode) lost. This zone specifically should be treated with the apprenticeship's highest caution
going forward, regardless of how compelling any future setup here looks.

## R12 — SESSION_SPECIFIC
STATUS: REGIMES_WITH_ONLY_OBSERVATIONS
SUBCLASSES:
- ASIA: consistently the thinnest, most compressed volume of each day this session (R06 largely
  coincides with Asia hours in this data).
- LONDON: consistently where real-volume expansion has begun (R07 transitions largely coincide with
  London open).
- PRE_US: insufficient distinct observation yet to separate from London.
- NY_US_CASH: the largest single-bar volumes recorded this session (5209, 5311) occurred in this
  window.
- LATE_US: insufficient distinct observation yet.
OPEN_QUESTIONS: whether London-open expansion or NY-session expansion produce genuinely different
tradable mechanisms is an explicit open question per CEO Part 11 — not yet answered with evidence.
STRATEGY_COVERAGE: NO_VALIDATED_STRATEGY_YET

---

## SUMMARY INDEX (per Part 10)

REGIMES_WITH_CANDIDATES: none.
REGIMES_WITH_DEVELOPING_PLAYBOOKS: none yet fully qualify (see Part 4 gap analysis in the status
report delivered 2020-05-06) — closest is the R02 countertrend-bounce pattern and the R04/R11 TOC-003
continuation-vs-stall pattern, both still OBSERVATION_ONLY / DEVELOPING_PATTERN, not DEVELOPING_PLAYBOOK.
REGIMES_WITH_ONLY_OBSERVATIONS: R02, R03, R04, R05, R06, R07, R10, R11, R12.
REGIMES_WITH_FAILED_IDEAS: none currently (R10 upgraded 2020-05-07 after trade #45's +10.265pt win;
breakout/breakdown-chasing is now 1-for-4 this session, not 0-for-3).
REGIMES_WITH_INSUFFICIENT_EXPERIENCE: R01, R08, R09.
REGIMES_WITH_NO_STRATEGY: all twelve, currently. Zero candidate strategies exist yet — reported
honestly per CEO governance ("zero is allowed").
