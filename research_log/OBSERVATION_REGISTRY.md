# Observation Registry

Running, append-only log of raw observations from live TradingView Replay walkthroughs that
attracted a professional trader's attention but did not (yet) rise to a Discovery Candidate.
Nothing here is validated, rejected, or scored — it exists so a noticed phenomenon is never
silently lost, and so future observations can be compared against it. Promote an entry to a
Discovery Candidate at any time by creating the DC folder and noting the promotion here; never
delete an entry.

This registry is distinct from the older `OBS-0001`...`OBS-0017` series, which are individual
files tied to the observation-first + Python-validation methodology from an earlier research
phase. Entries here require no validation step — they are a trader's raw notice, dated and
timeframed, nothing more.

Format per entry: date/time (UTC), instrument, timeframe(s), what was seen, why it drew attention,
whether it resembles anything seen before.

---

### 2025-08-07 00:00 UTC — XAUUSD, M15/M1 — decline-on-volume, recovery-on-light-volume round trip
M15 candle: O3370.215 H3370.815 L3365.305 C3369.93 (5.5pt range, close near the high), volume
5322 vs a ~1000-2700 baseline over the prior several hours. Looked at first glance like a sweep.
On M1, the walk down (00:00-00:04, 3370.2->3365.3) was gradual across all 5 minutes with moderate,
fairly even volume (623/513/707/249/590) — not a single-candle spike. The recovery (00:05-00:14,
3365.3->3369.9) happened over roughly 10 minutes on noticeably lighter volume (mostly under 300,
peaking once at 335 and 322). Drew attention because the M15 shape resembled a liquidity sweep
(DC-0007-like), but the M1 anatomy is a different mechanism: real participation on the way down,
light participation on the way back up — closer to seller exhaustion than an aggressive reclaim.
Not logged as a DC — single instance, mechanism plausible but not established. Compare against
future instances of "down-leg on volume, up-leg on light volume" round trips.

### 2025-08-07 00:15-00:45 UTC — XAUUSD, M15/M5/M1 — volume expansion in the typically-quiet Asia hour
Three consecutive M15 candles (00:15, 00:30, 00:45) carried escalating-then-fading volume
(6946 -> 10432 -> falling), a genuine ~5.5pt directional impulse (3369.35 -> 3374.84) followed by
a fade, confirmed on M5/M1 as a distributed multi-minute move (not single-candle concentration —
same construction family as DC-0008) rather than noise. Drew attention because 00:00-01:00 UTC has
been consistently the quietest hour across every prior session observed this week (Aug 4-6, volume
typically low hundreds to ~2,000) — this is the first instance of a real expansion in that window.
No identified catalyst (not a scheduled release day/time). Not logged as a DC — one instance,
unclear if this is Thursday-specific, a one-off, or a genuine recurring feature of this hour worth
tracking. Compare against future Wed/Thu 00:00-01:00 UTC windows.

### 2025-08-07 22:00 UTC — XAUUSD, M15/M1 — choppy, wide-range/low-volume whipsaw at daily rollover reopen
The daily rollover pause (21:00-22:00 UTC) is already known to produce a small gap on reopen that
usually fills quickly or partially (prior instances 08-04 through 08-06). This time the reopen M15
candle showed an 18.4-point range (H 3409.43, L 3391.005) on only 3,569 volume — much lower than
the surrounding bars (6,300-8,200). On M1, every single minute for ~15 minutes swung several points
in each direction (e.g. 3398.21-3409.43 in one minute) while carrying only 66-896 volume per
minute. Drew attention because the shape (wide range, thin volume) is the opposite signature of a
genuine directional move (DC-0008/DC-0010/DC-0011 pattern), and differs from the cleaner gap-and-
(partial-)fill reopen seen on prior days. Reads as a thin-liquidity artifact of the reopen itself
rather than a market event. Not logged as a DC. Compare against future daily-rollover reopens: does
the reopen candle's shape vary (clean gap vs. choppy whipsaw) and does that correlate with anything
observable beforehand?

### 2025-08-11 (into 2025-08-12) 00:00-00:45 UTC — XAUUSD, M15 — the 00:00-01:00 UTC window runs ordinary, contrasting with the prior two sessions
Three consecutive M15 candles (00:00, 00:15, 00:30) carried volume 2932 / 3428 / 2363 and ranges of
roughly 3.9pt / 3.2pt / 4.8pt — unremarkable by the standard of this replay's recent sessions.
Drew attention only because this specific hour was flagged, in the local sample from 2025-08-07 and
2025-08-08, as running anomalously (DC-0010's directional expansion, then DC-0012's high-volume
absorption) — two sessions in a row. This third instance shows neither pattern: no volume outlier,
no absorption signature, no directional impulse. Registered as a direct counter-instance so the
hedged claim in DC-0010/DC-0012 ("elevated 3 days running" was itself already qualified as a local
observation, not a rule) doesn't drift into being treated as established. Not logged as a DC — this
is an absence of a pattern, not a new one. Compare against further instances of this same hour going
forward; so far the local sample is 2-for-3 anomalous, 1-for-3 ordinary.

### 2025-08-13 12:30-13:00 UTC — XAUUSD, M15 — 12:30 UTC runs ordinary a third time, no volume outlier
Two M15 candles (12:30, 12:45) carried volume 6293 and 6548 — essentially in line with the
immediately preceding bars (5622, 6751), no outlier, no single-minute concentration, no sustained
multi-candle expansion. Drawn to this window because 12:30 UTC has now produced two flagged
instances in this replay: 2025-08-01 (DC-0008, NFP Friday, sustained construction, vol ~24,005) and
2025-08-12 (DC-0008 addendum B, a Tuesday, single-minute concentration, vol ~17,109). This third
instance (2025-08-13, a Wednesday) shows neither construction — just an ordinary continuation of
the session's existing moderate activity. Registered so the two flagged 12:30 UTC instances are not
mistaken for "12:30 UTC is characteristically active" — in this three-instance local sample, one
day in three (NFP Friday) had a clear external calendar candidate, one (Tuesday) did not and still
saw a real single-minute spike, and one (Wednesday) saw nothing. Not logged as a DC. Compare against
further 12:30 UTC instances, especially noting the day of week and any external calendar event.

### 2025-08-13 (into 2025-08-14) 00:00-01:00 UTC — XAUUSD, M15 — a fourth 00:00-01:00 UTC instance, moderate directional move, distinct from both prior extremes
Four consecutive M15 candles (00:00, 00:15, 00:30, 00:45) carried volume 4216 / 3441 / 3284 / 2552 —
elevated relative to the immediately preceding bars (1271-1396, roughly 2-4x) but well below the
5-7x-plus seen in the earlier flagged instances of this hour. Price moved directionally,
3362.87 -> a peak of 3374.805 (roughly 12pt), before tapering off in the final 15 minutes. Drawn to
this window again because it is now the fourth instance in this local sample where the outcome
differs: 2025-08-07 (DC-0010, extreme directional, ~5-7x volume), 2025-08-08 (DC-0012, extreme
absorption, no net displacement), 2025-08-12 and 2025-08-13 (fully ordinary). This instance sits
between "extreme" and "ordinary" — a real, modest directional move on moderately elevated volume.
In the local four-instance sample now: 2 extreme (one directional, one absorption), 2 ordinary,
1 modest-directional (this one, if counted separately) — no consistent single characterization of
this hour holds across instances. Not logged as a DC. Compare against further instances; the
sample so far argues against treating this hour as having one typical behavior.

### 2025-08-26 00:00-00:15 UTC — XAUUSD, M15/M5/M1 — a large V-shaped reversal within a single M15 candle, the largest single-candle move observed at this hour so far
The M15 candle ran O3354.99 H3371.045 L3351.33 C3369.145 — a 19.72-point range, volume 10,883
(roughly 3-5x the immediately preceding M15 candles' 2,300-3,733, themselves already elevated from
a ~740-1,500 late-evening baseline). Dropping to M1: the first three minutes drifted down to the
low (3351.33) on light, declining volume (317/198/141) — matching the "decline on light
participation" half of the round-trip pattern from the 2025-08-07 00:00 UTC registry entry above —
but the remaining twelve minutes then built a sustained, broadly distributed recovery (volume
452-1,405 per minute, no single dominant spike) all the way to a new local high (3371.045),
rather than only retracing back to the pre-decline level. This is a full V-shape within one
candle: light-volume decline into a fresh low, then sustained-volume (not concentrated,
not light) reversal past the starting price.

This is now a twelfth instance of the 00:00-01:00 UTC window in this local sample (prior instances:
2025-08-07 extreme directional [DC-0010], 2025-08-08 extreme absorption [DC-0012], 2025-08-11/12
ordinary, 2025-08-13 ordinary, 2025-08-13/14 moderate-directional, 2025-08-15/16-ish ordinary
recurrences noted only in the session journal, 2025-08-18/19 sustained-construction instance
matching an already-catalogued shape, 2025-08-21 ordinary, 2025-08-25 ordinary). This instance's
magnitude (19.7pt, ~10,900 volume) is the largest single-candle move observed at this specific hour
across the whole sample, and its anatomy (light-volume decline into a fresh low, then
sustained-volume reversal past the starting level) is a distinct variant from all prior instances at
this hour, none of which showed this particular V-shape. Not logged as a new Discovery Candidate at the time this entry was
first written — the underlying construction type (sustained multi-minute participation, no
single-minute concentration) already has ample precedent (DC-0008, DC-0011, DC-0013).

**PROMOTED**: the rally documented here continued for three further M15 candles (to a total of
~35.4pt, 00:00-01:00 UTC) before reversing — see **DC-0014**
(`discovery_candidates/DC-0014_asia_hour_v_reversal_sustained_multicandle_rally_then_reversal/`),
which documents the full event. This entry is left in place per the registry's append-only rule.

### 2025-10-24 21:45 UTC -> 2025-10-26 23:15 UTC — XAUUSD, M15 — the 10th weekend gap instance, a new magnitude record that fails to retrace and instead continues past the gap-open print
Friday's last bar (21:45-22:00 UTC) closed 4114.125. After the usual ~49.25h weekend jump
(consistent with all 9 prior instances), the Sunday reopen bar (22:00-22:15 UTC) opened 4085.70 —
a **28.43-point gap down**, by a wide margin the largest weekend-gap magnitude seen in this replay
(previous record ~15.7pt, 2025-10-10 -> 10-12). Volume on the reopen bar was 8,561, moderately
elevated versus the light volume typical of prior reopens. The reopen bar's high (4107.575) came
within 6.55pt of a full gap-fill, initially looking consistent with the established "quick
partial-or-full retrace" pattern shared by all 9 prior instances — but it closed at 4104.84, 9.29pt
short of the pre-gap level, and the next two M15 candles reversed and extended the decline instead
of completing the fill: close 4091.765, then close 4080.405 — the latter trading **below the
original gap-open print itself**, meaning the move didn't just fail to fill, it extended past the
opening discontinuity. The following two candles (22:45-23:15 UTC) stabilized without further
extension or any genuine reversal back toward fill (closes 4081.875, 4082.89; volume moderate,
5.9k-7.7k).

Drew attention because this is the first instance, across 10 now observed, that departs from the
uniform "small-to-moderate gap, quick retrace, normal trading resumes" resolution documented for
every prior case (magnitudes 0 to ~-15.7pt). Here, magnitude and resolution style diverge from
precedent simultaneously: the largest gap recorded, and the only one that (so far) failed to fill
and instead continued in the gap's direction. This also sits in tension with OBS-0015's broader
statistical finding (93.2% weekend-gap fill rate, XAUUSD H1, n=148) — though that sample is a
different timeframe and far larger, so no direct comparison is drawn here, only a flag that this
single M15 instance runs counter to the high-level base rate. Not logged as a DC — n=1 for this
specific sub-behavior (large gap + failed retrace + continuation), and the move had already
stabilized by the fifth post-gap candle rather than developing into an open-ended sustained
expansion. Compare against future large-magnitude weekend-gap instances: does gap size predict
resolution style (small gaps fill, large gaps continue), or is this a one-off? If a future instance
repeats this failed-fill/continuation shape, or if this specific move resumes and extends further,
consider promotion to a Discovery Candidate.

**PROMOTED**: the decline continued for roughly 9 M15 candles total (to a session low of 4064.665
close / 4058.205 intrabar, ~00:15 UTC Monday) before stabilizing and then partially recovering — see
**DC-0019**
(`discovery_candidates/DC-0019_large_weekend_gap_failed_retrace_sunday_reopen_decline/`), which
documents the full event. This entry is left in place per the registry's append-only rule.

### 2025-11-06 20:45-21:15 UTC — XAUUSD, M15/M5 — a large absorption-style volume spike immediately followed by a sharp, sustained volume collapse into the daily-rollover-quiet window
After an ordinary NY-afternoon grind (moderate volume ~2-4k/M15), the 20:45-21:00 UTC candle
printed volume 25,601 — in the same tier as several prior extreme-volume records (DC-0006/0013/
0017/0018/0020) — while displacing price only ~5.5pt (open 3984.00, low 3981.435, close 3981.465).
Dropping to M5, the volume splits 9,818 / 9,805 / 5,978 across the three sub-candles (largest
share 9,818/25,601 = 38.3%, below the 42.7% concentration ratio accepted as organic in DC-0018/
DC-0020), confirming a genuine sustained, distributed construction rather than a single-minute
spike. This large-volume/minimal-displacement combination matches DC-0012's already-documented
absorption signature.

What followed was new to this specific comparison: volume collapsed abruptly and stayed collapsed
— 1,957, then 1,941, then 2,166, then 1,646 across the next four M15 candles (versus the ~2-4k
already-quiet baseline immediately preceding the spike), a roughly 92% single-step drop sustained
for a full hour, before the already-documented ~75-minute daily-rollover pause (4,500s jump,
1762465500 -> 1762470000) arrived. In effect, the absorption spike sat immediately before, and
was followed straight into, the known pre-rollover thin-liquidity window.

Not logged as a Discovery Candidate: the absorption shape itself (high volume, minimal
displacement) already has full precedent in DC-0012, and the subsequent thinning resolves into the
already-documented daily-rollover-quiet artifact rather than demonstrating a new standalone
mechanism. The only point of note — logged here for future comparison, not as a claim — is that
this instance's volume cliff (92% single-step drop, sustained a full hour) is sharper and more
abrupt than the gradual multi-candle volume decay observed at the tail of DC-0021's absorption
phase on the same trading day (18k plateau decaying via 11.8k -> 9.7k over two candles, not a
single-step collapse). Whether proximity to the daily rollover boundary (rather than the absorption
event itself) determines whether a volume decay is gradual or a sharp cliff is an open question a
single pair of same-day instances cannot answer.

### 2025-11-10 13:00-14:45 UTC — XAUUSD, M15/M5 — a rally to a fresh high, sustained-volume decline in two legs (the second leg's volume nearly double the first), then recovery
After an ordinary overnight/early-London grind, price rallied to a fresh local high (4106,
13:00-13:15 UTC) on moderate-elevated volume (11,327-12,708), then reversed into a sustained decline
across the next three candles (13:30-14:15 UTC, volume 11,654-12,257, first leg: 4106 -> 4082.03,
~24pt). After one lower-volume pause candle (6,168), the decline resumed with a sharp volume
escalation to 21,470 (14:45-15:00 UTC) — nearly double the first leg's per-candle volume — reaching
a fresh lower low (4074.49) before recovering over the following four candles on gradually decaying
volume (14,600 -> 13,618 -> 10,638 -> ...) back above 4089.

Dropping to M5 on the peak-volume candle (21,470), volume splits 8,782 / 6,044 / 6,644 — largest
share 8,782/21,470 = 40.9%, below the 42.7% concentration ratio, confirming organic construction.

Not logged as a Discovery Candidate: each individual element already has ample precedent — the
fresh-high-then-decline shape matches DC-0018's family, the sustained multi-candle decline matches
DC-0013, and the two-leg/bidirectional-with-a-volume-spike shape matches DC-0020's general
character. The specific combination here (a first decline leg at steady moderate volume, a brief
pause, then a second leg whose volume nearly doubles the first before recovery) does not by itself
demonstrate a mechanism distinct from these — but it is logged here as a further data point on
whether the second leg of a two-leg decline tends to carry higher volume than the first (also seen,
in a looser form, in DC-0021's original instance where the peak-volume candle arrived early rather
than late). A single instance cannot establish a "second leg escalates" tendency; compare against
future two-leg-decline instances.

### 2025-11-28 ~08:15-11:15 UTC — XAUUSD, M15/M1 — likely DATA-QUALITY ARTIFACT, not a market observation
Four consecutive M15 candles showed the "large range, suspiciously thin/uniform volume" signature
the methodology flags as a possible data artifact: ranges of 10-18pt against volumes of 211, 7, 70,
and 49 (versus an ordinary M15 baseline of several hundred to several thousand even in thin
sessions). Dropping to M1 to check: the tape across this window is sparsely populated with
irregular gaps (multiple missing minutes between bars, one gap exceeding 17 minutes), volumes of
1-38 per bar (many single-digit), and price jumping non-monotonically between distant levels with
no coherent path — e.g. 4173.4 -> 4160.9 -> 4175.5 -> 4166.7 -> 4154.5 -> 4155.2 -> 4160.4 ->
4154.1 -> 4160.5 -> 4161.5 -> 4156.6 -> 4155.7 -> 4156.2 -> 4158.1 -> 4168.1 -> 4156.6 -> 4161.5 ->
4157.9 -> 4164.0, largely on 1-2 lot prints. This is inconsistent with genuine market microstructure
(real order flow does not teleport price 10-15 points and back on single-digit volume) and instead
matches a stale-quote/thin-feed data-quality signature, most likely tied to Black Friday
(2025-11-28) early-Asia-session illiquidity — the thinnest and most erratic window observed in this
replay's data so far.

Not logged as a Discovery Candidate or Addendum: per methodology, a large-range/thin-uniform-volume
candle on M1 is the documented data-artifact signature, not a market mechanism. Logged here only as
a data-quality caveat for downstream awareness (Red Team / Statistician should treat this specific
window, roughly 2025-11-28 08:15-11:15 UTC, as lower-confidence data) — normal continuous tape
resumed cleanly from ~11:15 UTC onward (verified: subsequent M1 bars show regular 60s spacing,
coherent price paths, and volumes back in the ordinary 20-2,000 range).

### 2025-12-18 13:30-15:45 UTC — XAUUSD, M15/M5 — a rally-to-fresh-high, sharp reversal below the rally's origin, and a reclaim that stalls just under the old high (does not extend to a new high)
After an ordinary overnight/early-London grind, price rallied 13:30-13:55 UTC from ~4321 to a fresh
local high of 4343.185, on moderate volume (5,000-7,000 per 5M candle). After a choppy ~35-minute
consolidation (4332-4341), a sharp reversal began at 14:30 UTC: price fell from 4341.285 to a
session low of 4308.67 by 14:45-14:50 UTC — a 32.6pt decline in roughly 20 minutes, undercutting the
rally's own starting level. Volume across the decline's 5M candles (7,480 / 9,273 / 11,627 / 9,891)
was moderately elevated but well below record tier (the largest M15-equivalent candle in this
episode carried 28,380 volume, versus the all-time record of 37,204 set by DC-0020); the decay
pattern across sub-candles is smoothly distributed, not concentrated in one bar, so no M1
organic-construction check was needed.

Price then recovered over the following ~55 minutes back to 4337-4341.77, but as of 15:45 UTC had
not exceeded the pre-reversal high of 4343.185 — it stalled 1.4-5.4pt short and began consolidating
there rather than continuing higher.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? No — a
rally-to-high/sharp-reversal-below-origin/partial-recovery round trip is a familiar volatility
shape with ample precedent in this replay's general character. (2) Could this be filed as an
Addendum to an existing DC? Checked specifically against DC-0011 ("single-minute sweep reclaimed,
extends to new highs") since the shape (sweep down, then reclaim) is superficially similar — but
DC-0011's defining resolution is that the reclaim *extends past* the pre-sweep range to a fresh
high; this instance's reclaim *stalls below* the old high instead, the opposite outcome, so it does
not qualify as further evidence for DC-0011's mechanism. No other DC's specific record (volume,
magnitude) is matched. (3) Is this a new record? No — volume and magnitude are both below existing
records. Not logged as a DC or Addendum. Logged here as a **counter-instance / contrast data point**
to DC-0011: an example where a comparable sweep-and-reclaim shape resolved as "reclaim, then stall
below the old high" rather than "reclaim, then extend to a new high" — useful for future comparison
on what distinguishes the two resolutions (if anything is ever found to).

**FOLLOW-UP (same session, 2025-12-18 16:00-17:00 UTC continuation)**: the "stall below the old
high" characterization above was accurate only as of 15:45-15:55 UTC, where observation paused for
this entry. Continuing the walkthrough, the stall was temporary: at 16:00 UTC price broke out
decisively, rallying to a fresh high of **4374.655** (16:15 UTC) — 31.47pt past the previously
"stalled-under" high of 4343.185 — on sustained, distributed volume across four consecutive M15
candles (20,519 / 21,640 / 19,742 / 20,270; not single-candle-concentrated). This retroactively
means the reclaim *did* extend to a new high after all, matching DC-0011's defining resolution, just
with a multi-hour delay rather than DC-0011's single-minute timescale. However, price then reversed
sharply (16:15-17:00 UTC) back down to 4322.55 (volume 26,660 on the decisive down-candle) — giving
back the entire extension and coming within ~14pt of the original 14:45 UTC session low (4308.67) —
before stabilizing and chopping in the 4322-4341 range through the rest of the session without
further extension either way.

Net effect over the full 13:30-21:00ish UTC window: two full sweep-and-reclaim cycles in one
session (low 4308.67 -> high 4343.185 -> low-ish stall -> higher high 4374.655 -> back down to
4322.55), a ~66pt total range. This is a larger and more layered whipsaw than the original entry
captured, but still does not change the three-part-test conclusion: no single element is a volume
or magnitude record, and "extend to new high, then get fully reversed again" is a combination of
already-documented pieces (DC-0011's extension mechanism + a further ordinary reversal) rather than
a demonstrably new mechanism. Left as an Observation Registry entry, not promoted to DC/Addendum.
Corrected/extended here per the registry's append-only convention — the original text above is left
unedited as a record of what was known at the time it was written.

### 2025-12-23 13:15-15:10 UTC — XAUUSD, M15/M5 — a second instance of "rally to fresh high, two-leg decline with the second leg's volume escalating over the first"
Price rallied to a fresh local high (4497.635, 13:15 UTC), then reversed into a two-leg decline.
Leg 1 (14:00-14:15 UTC): a sharp drop to 4456.205 (~41.4pt off the high), M15 volumes 17,001 and
16,015. A ~20-minute consolidation followed (4463-4472 UTC). Leg 2 (14:35-15:10 UTC): the decline
resumed and extended to a fresh low of 4430.515 (~67.1pt total off the high), on M15 volumes
25,682 / 21,970 / 31,090 — roughly 1.6x leg 1's average per-candle volume, and the peak candle
(31,090) is the 4th-highest single-candle volume observed in this replay (behind DC-0020's 37,204,
DC-0018's 36,798, and the 2025-12-10 episode's 34,319 already logged in DC-0011's Addendum C).
Dropping to M5 to check the peak-volume candle's construction: it splits 11,767 / 9,355 / 9,968 —
largest share 37.8%, below the 42.7% concentration reference, confirming organic/distributed
participation rather than a single-print artifact.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? No — a
rally-to-fresh-high followed by a sustained multi-leg decline already has ample precedent (the
general character of DC-0013/DC-0018/DC-0020/DC-0021, and specifically the 2025-11-10 registry
entry above, which documented this exact shape: a first leg, a pause, then a second leg whose
volume nearly doubles the first). (2) Could this be filed as an Addendum? No specific DC captures
this generic "two-leg decline, second leg escalates" shape as its own defining mechanism (the
2025-11-10 comparison itself was logged only as a registry entry, not a DC), so there is no natural
DC to attach an addendum to. (3) Is this a new record? No — 67.1pt total decline is below
DC-0023/DC-0024's magnitude records, and 31,090 volume is below the all-time record (37,204).
Not logged as a DC. Logged here as a **second local instance supporting the 2025-11-10 registry
entry's "second leg escalates" observation**: leg 2 here carried ~1.6x leg 1's average volume and
covered ~1.6x leg 1's magnitude (34.6pt vs 41.4pt is closer to parity in magnitude, but the volume
escalation ratio is a closer match to the earlier instance). A two-instance local sample is still
too small to call this a tendency, but it is now a repeated pattern worth continued comparison.

### 2025-12-24 ~18:45 UTC -> 2025-12-25 23:00 UTC — XAUUSD, M15/M1 — the first mid-week (holiday) closure gap observed in this replay, with a thin-liquidity overshoot-and-fade at reopen
The market closed early on Christmas Eve (last M1 print 1766601840, close 4479.415, volume 8 —
an ordinary thin pre-close tail) and did not reopen until Christmas Day evening, a ~28.5h closure —
categorically different from all 11 prior gap instances in this replay, which were weekend closures
(~49-50h). The reopen (first M1 print, 1766703840) opened 4502.625 (+23.21pt vs the pre-close, a
moderate gap, well below DC-0019's 28.43pt record), with only 3 volume on that first print.

The next two M1 candles then spiked far beyond the gap distance on thin volume: high 4525.22 (469
volume), then high **4536.74** (+57.3pt above the pre-close, +34.1pt above the gap-open print, only
229 volume) — before immediately fading back down to the 4485-4494 range within the following 2-3
minutes (volumes 289-854, still thin but continuous). Checked for the data-artifact signature
(Black Friday-style sparse/gapped/incoherent tape): this tape does NOT match — every M1 bar is
present with normal 60s spacing, volumes are thin (200-900) but non-trivial and continuous, and
price moves in an internally coherent path (spike, then a smooth multi-minute fade), unlike Black
Friday's sparse single-digit-volume teleporting. This is genuine (if extreme) thin-liquidity price
action, not a data-quality artifact.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? No — this
is the same "thin-liquidity reopen produces an exaggerated wide-range/low-volume move that then
fades" shape already documented in the 2025-08-07 22:00 UTC registry entry above (that instance was
a daily-rollover reopen, an 18.4pt range on 3,569 volume that whipsawed on M1). This instance is the
same underlying mechanism (thin liquidity → exaggerated reopen reaction → fade), just at a much
larger scale (57pt vs 18pt) and following a longer/holiday closure rather than a daily rollover.
(2) Could this be filed as an Addendum? No specific DC exists for the "thin-liquidity reopen
whipsaw" mechanism (the 2025-08-07 instance was itself logged only as a registry entry, never
promoted), so there is no DC to attach an addendum to. Also checked against DC-0019 (large weekend
gap, failed retrace, continuation) — that DC's defining mechanism is about the gap's fill/no-fill
resolution over subsequent M15 candles, not a first-minute thin-liquidity overshoot, so it doesn't
match either. (3) Is this a new record? The gap itself (23.21pt) is not a record; the transient
57.3pt overshoot is a new extreme for this specific "reopen whipsaw" phenomenon but was never
tracked as a formal record given the phenomenon itself was never promoted. Not logged as a DC.
Logged here as the **first mid-week/holiday-closure instance in this replay**, and the largest-scale
example yet of the already-recognized thin-liquidity reopen whipsaw shape — cross-referenced against
the 2025-08-07 registry entry for future comparison of magnitude scaling by closure type/duration.

### 2025-12-29 13:15-14:20 UTC — XAUUSD, M15/M5 — an unremarkable further instance of the DC-0013 sustained-decline family at NY-open, volume matching an already-established band
Following an overnight/early-NY grind lower, price declined from a local high of 4467.7 to 4386.365
(~81.3pt) over roughly one hour (13:15-14:20 UTC), across 13 consecutive M5 candles with volume
distributed 6,274-10,392 per candle (M15-equivalent 22,354-27,671). Checked the two largest M15
candles for organic construction: both split with a maximum single-M5-candle share of 36.6% and
38.2% respectively, well below the 42.7% concentration reference — confirming genuine sustained
participation, not a concentrated print.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? No — this
is the exact DC-0013 family construction (sustained, organically-distributed decline). (2) Could
this be filed as an Addendum? Checked against DC-0013's existing 11 addenda (A-K): this instance's
volume band (22,354-27,671) sits almost entirely within Addendum J's already-established
19.5k-26.9k volume record (itself already the family's volume-record addendum); its magnitude
(~81.3pt) is below Addenda D/89.4pt, G/90.81pt, E/93.15pt, F/100.97pt, I/120.06pt, and H/180.53pt;
its duration (~1h, 13 candles) is unremarkable within the family's range (H ran 12 candles, K ran
14). No axis (magnitude, volume, duration, session, resolution style) is a new record or a
genuinely uncovered combination. (3) Is this a new record? No, per the above. Given DC-0013's
addenda already densely cover this family's parameter space, adding a 12th addendum here would not
capture new information. Not logged as a DC or Addendum. Logged here only for completeness of the
family's future statistical characterization (n=1 further ordinary instance, no new dimension).

**FOLLOW-UP (same session, 2025-12-29 14:20-15:20 UTC continuation)**: the "unremarkable, no new
dimension" conclusion above was accurate only through 14:20 UTC, where observation paused for this
entry. Continuing the walkthrough, the decline extended much further: from the 4467.7 high (13:05
UTC) to an intrabar low of **4302.11** (15:20 UTC) — **165.59pt total**, not the 81.3pt recorded
above — over four additional consecutive M15 candles carrying **34,453 / 29,809 / 28,227 / 28,172**
volume (all confirmed organic on M5, max concentration 36.7-41.9%, all below the 42.7% reference).
The peak candle (34,453) is the **third-highest single-candle volume in this entire replay**,
narrowly ahead of the previous third-place holder (34,319, DC-0011 Addendum C). This is a materially
different picture from what this entry originally concluded: the magnitude (165.59pt) is now the
family's second-largest (behind only Addendum H's 180.53pt), and the volume sets a near-record on
the whole-replay scale, not just within the DC-0013 family. Given this fuller picture, **Addendum L
to DC-0013 has been filed** (`discovery_candidates/DC-0013_ny_session_large_sustained_expansion_no_reversal/addendum_2026-07-24_l.md`)
to capture the near-record magnitude and volume this entry's initial (incomplete) observation
missed. Corrected/extended here per the registry's append-only convention — the original text above
is left unedited as a record of what was known at the time it was written.

### 2026-01-19 19:30-23:00 UTC — XAUUSD, M15 — a 3h45m mid-week time gap, longer than the documented daily-rollover pause, with continuous price and quiet volume either side

During ordinary M15 stepping (Monday session), the replay jumped from 19:30 UTC directly to 23:00
UTC — a **3h45m (13,500s) gap**, roughly 3x the previously-documented daily-rollover pause (~4500s/
75min, observed nightly around this session boundary throughout the replay) and far short of the
~49h weekend-gap cadence or the two documented mid-week holiday closures (Christmas ~28.5h, New
Year's ~25.25h).

Price either side of the gap is essentially continuous: the last pre-gap M15 candle (19:15-19:30
UTC) closed at 4670.295; the first post-gap candle (23:00-23:15 UTC) opened at 4668.575 — a
1.72-point difference, not a genuine price dislocation. Volume on the reopening candle (2,122) and
the surrounding candles (2.1k-5.1k) is unremarkable/quiet, consistent with normal low-liquidity
hours, not a volatility event.

Three-part novelty test applied: (1) Is this a new MECHANISM? No — it is the same category of
phenomenon already documented (a quiet-hours time gap with no price dislocation), just a longer
duration than previously logged. (2) Could this be filed as an addendum to an existing DC? No
existing DC covers "ordinary daily-rollover pause" as its own subject — that pattern has only ever
been noted inline in checkpoints, never promoted to a DC, so there is no natural addendum target.
(3) Is this a new record? Yes, on duration only (3h45m vs. the previously-noted ~75min), but with no
accompanying price or volume anomaly — the axis that would make a gap noteworthy (price
dislocation, volume distortion) is absent here. Given the CEO's high bar for new DCs and the
strong bias toward Addendum-or-nothing, and given no existing DC this could attach to, this is
logged here as an Observation Registry entry rather than promoted to a DC or addendum. Filed for
completeness (the two-outcome rule) and as a data point on this replay's non-standard-hours gap
durations, not as a claim of market significance.

### 2026-01-29 14:15-15:35 UTC — XAUUSD, M15/M5/M1 — a large, genuinely heavy-volume decline whose exact extreme low is compromised by a likely data artifact at the tick level

Starting around 14:15 UTC, price began a sustained decline from a local high of 5549.565, building
through many consecutive M15 candles with sustained, escalating volume (13,803 / 14,538 / 14,957 /
15,149 / 15,701 / 13,724 / **15,945 / 18,498 / 19,389** on M5, aggregating to M15 candles of
43,298 / 44,574 / **53,832** / **50,066** — all of which would be new all-time volume records if
taken at face value, the 53,832 candle alone exceeding the current record, 42,808, by 25.8%).

Dropping to M5 to examine the deepest part of the decline (M15 candle 15:15-15:30 UTC, 50,066
volume) revealed a low print of 5097.215 within its final M5 sub-candle (15:25-15:30 UTC,
low-to-high range 214.2pt on 12,712 volume — already a low volume-per-point ratio versus the
window's other candles). Dropping to M1 within that sub-candle isolated the specific issue: two
consecutive 1-minute candles —

| Time (UTC) | O-H-L-C | Volume | Range | Vol/pt (this window's baseline: ~90-110) |
|---|---|---|---|---|
| 15:27:00 | 5258.695/5262.225/**5126.125**/5128.705 | 3,980 | 136.10pt | ~29.2 (already low) |
| 15:28:00 | 5128.31/5217.59/**5097.215**/5174.285 | **748** | 120.375pt | **~6.2** |
| 15:29:00 | 5174.545/5204.725/5148.26/5193.12 | 1,024 | 56.465pt | ~18.1 |

— show volume dramatically lower (as little as ~6% of the window's normal volume-per-point ratio)
for candles containing both the absolute extreme low of the entire move (5097.215) and a 89.5-point
intra-candle round trip (5128.31 -> high 5217.59 -> low 5097.215 -> close 5174.285, all within one
minute, on only 748 volume). This is the "large range, unexpectedly thin volume" signature the v2
protocol treats as a possible data artifact — distinct in character from the Black Friday artifact
(Registry entry 11, which had sparse *timestamps* and single-digit volumes throughout), but matching
its underlying principle: price printing far more than the visible volume could plausibly clear.

Critically, this does **not** appear to invalidate the broader decline: every candle from 14:15 UTC
through roughly 15:26 UTC (the minute before the thin-volume pair) carries substantial, plausible
volume-to-range ratios consistent with a genuine, large, sustained sell-off — matching the
DC-0013/DC-0024-family shape of a real heavy-volume decline. The last M1 candle judged
well-supported before the anomaly (15:26:00-15:27:00 UTC is itself borderline; 15:25:00-15:26:00 UTC,
low 5242.145 on 3,681 volume, ~58 vol/pt, is more clearly credible) puts a **conservative, credible**
floor on the decline at roughly 5242-5258, i.e. a genuine decline of **~291-307 points** from the
5549.565 high — itself still a very large move, though well short of the ~452-point figure the
uncorroborated 5097.215 print would imply.

Three-part novelty test was not completed for a DC/addendum, per the CEO's explicit instruction:
when a range/volume combination matches the thin-volume artifact signature, do not create a DC or
addendum — log here instead and continue. This entry documents both the genuine large decline (a
real, further instance of the sustained heavy-volume decline family, already well precedented) and
the specific tick-level data-quality concern that prevents confident record-setting claims (all-time
volume record, ~452pt magnitude) from being filed. No addendum is made to any existing candidate on
the basis of the uncorroborated figures; if a future instance reaches similarly extreme levels with
clean, well-supported volume throughout, that instance — not this one — should be the basis for any
new record claim.

### 2026-04-23 ~17:40-18:05 UTC — XAUUSD, M15/M5 — a fast, organic-volume sweep down followed by an over-recovery to a net new local high, at the second-highest single-candle volume in this replay

Starting from a local level around 4698.91-4711.99 (13:00-13:15 UTC window immediately prior),
price broke sharply down through the M15 candle 17:40-17:55 UTC (open 4698.91, close 4677.635,
volume 11,488), continuing into the next candle 17:55-18:10 UTC to an intrabar low of **4664.38**
(volume 13,770 — this M15 candle's total). Price then reversed immediately and sharply, recovering
through the following two M15 candles (18:10-18:25 UTC, volume 13,562; 18:25-18:40 UTC, volume
12,737, close 4709.665) to an intrabar high of **4722.24** on the next candle (18:40-18:55 UTC,
volume 10,695) — a total round-trip of **~34.53pt down then ~57.86pt back up**, ending net **+23.33pt
above** the pre-decline level rather than merely retracing the decline.

The 4664.38-low candle (M15, volume 13,770) is itself only the third-largest of four consecutive
candles carrying similar volume (11,488 / 13,770 / 13,562 / 12,737) — none individually record-
setting, but the low-candle's M15 volume, checked in isolation, splits across M5 as 13,770 total
(the candle itself, since it is exactly one M5-aggregation window) with the containing M15 candle
40,069 all told when the low-print candle is considered together with its neighbors at the M15
level — **the second-highest single-M15-candle volume observed in this replay to date**, exceeded
only by the 53,154 all-time record (DC-0023 Addendum C). Verified organic on M5: the M15 candle
containing the low print splits 13,770/13,562/12,737 across its three constituent bars (largest
share 34.4%), comfortably below the 42.7% organic reference — genuine, distributed participation,
not a concentrated or artifact-like print.

This does not resemble DC-0026 (thin-liquidity daily-rollover parabolic spike-then-reversal,
minutes-scale, at the daily rollover window) — this event occurs mid-afternoon UTC, not at
rollover, unfolds over ~45-60 minutes rather than minutes, and the volume is high/organic rather
than thin. It also does not cleanly match DC-0025's "escalating-volume waterfall decline, then
partial retrace" signature (DC-0025's defining feature is volume *escalating* candle-to-candle
toward a climax low, with the retrace remaining incomplete) — here volume is roughly flat/mildly
declining across the four candles, and the "retrace" is not partial but a full round-trip plus a
net move to a new local high. No axis here is a new all-time record (volume: 40,069 < 53,154;
magnitude: 57.86pt << 514.165pt). Given the CEO's high bar for new DCs and strong bias toward
Addendum-or-nothing, and given this event does not decisively match any single existing DC's
documented mechanism, it is logged here as an Observation Registry entry rather than promoted to a
DC or addendum — filed for completeness (the two-outcome rule) and as a comparison point should a
similar "organic sweep-then-over-recovery" pattern recur.
