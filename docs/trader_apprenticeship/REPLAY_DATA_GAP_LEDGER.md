# REPLAY_DATA_GAP_LEDGER

Every confirmed TradingView replay data gap encountered during apprenticeship, per CEO governance
(2026-08-24). A gap here means the underlying replay feed has zero bars for the interval at any
resolution checked — not a tool/methodology artifact (each entry below states how that was verified).
Gap intervals are `SOURCE_REPLAY_GAP` / `UNOBSERVED` / `NOT_LEARNABLE` / `NOT_TRADEABLE_FOR_APPRENTICESHIP`
— never reconstructed, never inferred, never used for setup learning, entry decisions, MFE/MAE, trade
review, or morphology conclusions. Any setup/trade that began before a gap and would require observing
the missing interval is marked `OUTCOME_UNOBSERVABLE` and excluded from apprenticeship learning.

## GAP-001

- **START**: 2020-02-17 ~22:00 UTC (last observed M15 bar close: 1581961500, i.e. 21:45 UTC)
- **END**: 2020-02-18 ~03:15 UTC (first observed M15 bar open: 1581980400, i.e. 03:00 UTC bar)
- **DURATION**: ~5.25 hours (18,900s)
- **ACTIVE RESOLUTION AT DISCOVERY**: M15 (single-step-single-read, zero mixed-resolution stepping —
  reproduced under the strictest protocol available)
- **SOURCE**: `OANDA:XAUUSD`, TradingView Bar Replay
- **REPRODUCIBLE**: YES — reproduced identically (same jump size, same resulting bar, byte-for-byte)
  across two independent walks: (1) the original mixed-resolution walk, (2) a full re-anchor + clean
  68-candle single-step re-walk under the CEO's own strict integrity protocol. Confirms this is intrinsic
  to the data feed, not an artifact of tool usage — the original "mixed-resolution stepping caused it"
  diagnosis was wrong and is corrected in the main log.
- **EXPECTED MARKET-CLOSED PERIOD**: NO / UNKNOWN — XAUUSD (OANDA CFD) normally trades continuously
  Mon-Fri; this falls on a Monday night/Tuesday early morning, not a known session boundary or holiday.
  Genuinely unexplained; not flagged as a data-quality-gate trigger yet since it is a single, isolated
  occurrence (per the CEO's own threshold: raise `TRADINGVIEW_REPLAY_DATA_QUALITY_GATE` only if repeated
  unexplained gaps materially affect active trading periods).
- **APPRENTICESHIP IMPACT**: none — no setup/trade was open or developing across this gap. Decision
  state on both sides of the gap was WATCH/NO_TRADE. No `OUTCOME_UNOBSERVABLE` entries required.

### CEO AUDIT — GAP-001 ROOT CAUSE, STRUCTURED CLASSIFICATION (added 2026-08-25, corrects the 2026-08-24 CEO milestone report's chat summary; the narrative below already existed in the log/ledger and is only being restated here in explicit structured form — nothing in this entry is a new finding)

- **INITIAL_DIAGNOSIS**: stepping-related — back-to-back `replay_step` calls without an intervening
  read, interacting with an already-mid-window M15 clock, was suspected to let the replay position
  advance more than one bar per call.
- **LATER_FALSIFIED**: YES — a full re-anchor to 2020-02-17 followed by a clean 68-candle
  single-step-single-read, M15-only re-walk reproduced the exact same jump (current_date
  1581962399 → 1581981299, +18,900s) at the exact same point, with zero mixed-resolution stepping
  and zero back-to-back steps anywhere in the re-walk. Stepping methodology cannot be the cause of
  something that reproduces identically once that methodology is fully eliminated.
- **AUTHORITATIVE_DIAGNOSIS**: `SOURCE_REPLAY_GAP`, `REPRODUCIBLE` — a genuine, intrinsic gap in the
  underlying `OANDA:XAUUSD` TradingView Bar Replay data feed at 2020-02-17 ~22:00 UTC →
  2020-02-18 ~03:15 UTC. NOT a user/agent stepping-caused artifact.
- **WHY THIS IS BEING RESTATED**: the CEO's 2026-08-24 milestone report chat summary (Section A
  "INTEGRITY_INCIDENTS" and Section N lesson #8) incorrectly reintroduced the falsified
  stepping-cause framing as if it were the final, resolved diagnosis. That report text is
  superseded by this entry and by the pre-existing narrative in
  `AI_TRADER_EXPERIENCE_LEDGER.md` and `lane_a_historical/2020_Q1_H4_LOG.md` (~lines 537-693),
  which already recorded both the initial mistaken diagnosis and its falsification honestly, in
  order, undisclosed-nothing. This addendum does not change those source files — it corrects only
  the report-level mischaracterization and gives the correction an explicit, audit-queryable field
  structure per CEO instruction.

## GAP-002

- **START**: bar close 1582063200 (2020-02-20 ~00:40 UTC approx)
- **END**: bar open 1582066800 (2020-02-20 ~01:40 UTC approx)
- **DURATION**: ~1 hour (3600s, 4 missing M15 bars)
- **ACTIVE RESOLUTION AT DISCOVERY**: M15, single-step-single-read, no mixed resolution — same clean
  protocol as GAP-001's confirmed re-walk.
- **SOURCE**: `OANDA:XAUUSD`, TradingView Bar Replay
- **REPRODUCIBLE**: not independently re-tested (GAP-001 already established this class of gap is
  intrinsic to the feed, not a tool artifact — not re-verifying every instance from now on per the
  standing CEO instruction not to re-diagnose each occurrence).
- **EXPECTED MARKET-CLOSED PERIOD**: UNKNOWN — no known session boundary at this time.
- **APPRENTICESHIP IMPACT**: none — WATCH/NO_TRADE on both sides (mid-consolidation after the large
  Feb19 breakout, no setup open). No `OUTCOME_UNOBSERVABLE` entries required.

## GAP-003
- START: bar close 1582149600. END: bar open 1582153200. DURATION: ~1h (4 M15 bars). RESOLUTION: M15.
- SOURCE: OANDA:XAUUSD. REPRODUCIBLE: not re-tested (same class as GAP-001/002). EXPECTED-CLOSED: UNKNOWN.
- IMPACT: none, WATCH/NO_TRADE both sides.

## GAP-004
- START: bar close 1582236000. END: bar open 1582239600. DURATION: ~1h (4 M15 bars). Same class as prior gaps, no impact (WATCH both sides).

## GAP-005
- START: bar close 1582580700 (2020-02-24 ~21:45 UTC). END: bar open 1582585200 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same class as prior gaps (near the ~21:00-23:00 UTC daily rollover window, consistent with GAP-002/003/004's timing). Not re-diagnosed per standing instruction.
- IMPACT: none — WATCH/NO_TRADE both sides (post-breakdown consolidation, no setup open).

## GAP-006
- START: bar close 1582667100 (2020-02-25 ~21:45 UTC). END: bar open 1582671600 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same class/timing as GAP-005 (daily rollover window). Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides (post-record-spike consolidation, no setup open).

## GAP-007
- START: bar close 1582753500 (2020-02-26 ~21:45 UTC). END: bar open 1582758000 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class as GAP-002..006. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## GAP-008
- START: bar close 1582839900 (2020-02-27 ~21:45 UTC). END: bar open 1582844400 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class as GAP-002..007. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## WEEKEND-001 (expected, not counted with GAP-001..004)
- START: bar close 1582322400 (Fri 2020-02-21 ~22:00 UTC). END: bar open 1582498800 (Mon 2020-02-24 ~ 06:00 UTC approx). DURATION: ~49h.
- EXPECTED MARKET-CLOSED PERIOD: YES (weekend) — Feb 21 2020 was a Friday, this is the standard weekend close/reopen, not an anomaly. Not added to the isolated-gap count that would trigger a quality-gate review.
- APPRENTICESHIP IMPACT: none — WATCH/NO_TRADE both sides. The reopen bar itself is a genuine, major real-world development (see main log).

## GAP-009
- START: bar close 1583185500 (2020-03-02 ~21:45 UTC). END: bar open 1583190000 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## GAP-010
- START: bar close 1583271900 (2020-03-03 ~21:45 UTC). END: bar open 1583276400 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## GAP-011
- START: bar close 1583358300 (2020-03-04 ~21:45 UTC). END: bar open 1583362800 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## WEEKEND-003 (expected, not counted with GAP-001..012)
- START: bar close 1583531100 (Fri 2020-03-06 ~21:45 UTC). END: bar open 1583704800 (Sun 2020-03-08 ~22:00 UTC). DURATION: ~48.25h.
- EXPECTED MARKET-CLOSED PERIOD: YES (weekend) — March 6 2020 was a Friday. Reopen bar shows a large gap-up (Friday close 1674.062 → Sunday reopen high 1700.928, close 1693.862, vol 2785) — the first close above 1700 of the whole pilot. Real-world context noted honestly, not used as a forward assumption: this weekend fell during the escalating COVID-19 panic and (per general historical knowledge, not fabricated) coincided with an oil-price-war shock — consistent with, not proof of, the gap size.
- APPRENTICESHIP IMPACT: none — WATCH/NO_TRADE both sides going into the weekend. The reopen bar itself is a genuine, major real-world development (see main log).

## GAP-012
- START: bar close 1583444700 (2020-03-05 ~21:45 UTC). END: bar open 1583449200 (~23:00 UTC). DURATION: ~75min (5 M15 bars). Same recurring daily-rollover class. Not re-diagnosed.
- IMPACT: none — WATCH/NO_TRADE both sides.

## GAP-013
- START: bar close 1583787600 (2020-03-09 ~21:00 UTC). END: bar open 1583791200 (~22:00 UTC). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..012. Not re-diagnosed.
- IMPACT: none — NEUTRAL/NO_TRADE both sides (range chop, no setup open).

## GAP-014
- START: bar close 1583874000 (2020-03-10 ~21:15 UTC est.). END: bar open 1583877600 (~22:15 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..013. Not re-diagnosed.
- IMPACT: none — SHORT bias holding both sides (consolidation below 1649.5, no setup open).

## GAP-015
- START: bar close 1583960400 (2020-03-11 ~20:15 UTC est.). END: bar open 1583964000 (~21:15 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..014. Not re-diagnosed.
- IMPACT: none — SHORT bias holding both sides (approaching 1633.2 test, no setup open).

## GAP-016
- START: bar close 1584046800 (2020-03-12 ~19:30 UTC est.). END: bar open 1584050400 (~20:30 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..015 (timing shifted ~1.5h earlier than the typical 21:00-23:00 window — noted, not re-diagnosed, consistent with day-to-day variance already seen in this class).
- IMPACT: none — SHORT bias holding both sides (contained near 1560.8-1580, no setup open).

## WEEKEND-004 (expected, not counted with GAP-001..016)
- START: bar close 1584132300 (Fri 2020-03-13 ~19:15 UTC). END: bar open 1584309600 (Sun 2020-03-15 ~20:30 UTC). DURATION: ~49.25h.
- EXPECTED MARKET-CLOSED PERIOD: YES (weekend) — March 13 2020 was a Friday, standard weekend close/reopen.
- Reopen bar shows a large gap-up: Friday close 1529.486 → Sunday reopen high 1572.874, close 1570.108, vol 4294 — a ~40-point gap up from Friday's crash-era close. Real-world context, not used as a forward assumption: this weekend fell during the peak of the COVID-19 market panic and (per general historical knowledge, not fabricated) coincided with emergency central-bank actions over that weekend — consistent with, not proof of, the gap size and direction.
- APPRENTICESHIP IMPACT: none — WATCH/NO_TRADE both sides going into the weekend. The reopen bar itself is a genuine, major real-world development (see main log).

## GAP-017
- START: bar close 1584392400 (2020-03-16 ~21:00 UTC est.). END: bar open 1584396000 (~22:00 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..016. Not re-diagnosed.
- IMPACT: none — NEUTRAL/whipsaw both sides (1504.8 pivot contest, no setup open).

## GAP-018
- START: bar close 1584478800 (2020-03-17 ~21:45 UTC est.). END: bar open 1584482400 (~22:45 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..017. Not re-diagnosed.
- IMPACT: none — LONG-leaning bias holding (1524.3 support, no setup open).

## GAP-019
- START: bar close 1584565200 (2020-03-18 ~21:45 UTC est.). END: bar open 1584568800 (~22:45 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..018. Not re-diagnosed.
- IMPACT: none — SHORT-leaning bias holding (contained below 1504.8, no setup open).

## GAP-020
- START: bar close 1584651600 (2020-03-19 ~21:45 UTC est.). END: bar open 1584655200 (~22:45 UTC est.). DURATION: ~1h (4 M15 bars). Same recurring daily-rollover class as GAP-002..019. Not re-diagnosed.
- IMPACT: none — SHORT-leaning bias holding (approaching 1451.4, no setup open).

## WEEKEND-002 (expected, not counted with GAP-001..008)
- START: bar close 1582926300 (Fri 2020-02-28 ~21:45 UTC). END: bar open 1583103600 (Sun 2020-03-01 ~23:00 UTC). DURATION: ~49.25h.
- EXPECTED MARKET-CLOSED PERIOD: YES (weekend) — Feb 28 2020 was a Friday. Reopen bar shows a wide range (H1593.2/L1576.7, close 1581.2, vol 2037) — real continued volatility from the pre-weekend crash episode, not itself anomalous.
- APPRENTICESHIP IMPACT: none — WATCH/NO_TRADE both sides going into the weekend (crash-episode price action, no entry taken per standing discipline).

## GAP-021
- START: bar close 1584996300 (2020-03-24 ~04:05 UTC est.). END: bar open 1585000800 (~05:20 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..020. Not re-diagnosed.
- IMPACT: none — LONG bias holding (consolidation above 1524.3, no setup open).

## GAP-022
- START: bar close 1585082700 (2020-03-25 ~06:05 UTC est.). END: bar open 1585087200 (~07:20 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..021. Not re-diagnosed.
- IMPACT: none — LONG bias holding (consolidation near leg highs, no setup open).

## GAP-023
- START: bar close 1585169100 (2020-03-26 ~05:05 UTC est.). END: bar open 1585173600 (~06:20 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..022. Not re-diagnosed.
- IMPACT: none — NEUTRAL bias holding (compression, no setup open).

## GAP-024
- START: bar close 1585255500 (2020-03-27 ~05:25 UTC est.). END: bar open 1585260000 (~06:40 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..023. Not re-diagnosed.
- IMPACT: none — NEUTRAL bias holding (chop, no setup open).

## GAP-025
- START: bar close 1585601100 (2020-03-31 ~04:05 UTC est.). END: bar open 1585605600 (~05:20 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..024. Not re-diagnosed.
- IMPACT: none — NEUTRAL/SHORT-mild bias holding (chop, no setup open).

## GAP-026
- START: bar close 1585687500 (2020-03-31 corrected ~21:05 UTC est.). END: bar open 1585692900 (~22:35 UTC est.). DURATION: ~90min (slightly longer than the usual ~75min instances, same recurring class). Not re-diagnosed.
- IMPACT: none — SHORT bias holding (continuation, no live setup managed).

## GAP-027
- START: bar close 1585773900 (2020-04-02 ~06:15 UTC est., corrected epoch math). END: bar open 1585778400 (~07:30 UTC est.). DURATION: ~75min. Same recurring daily-rollover class as GAP-002..026. Not re-diagnosed.
- IMPACT: none — LONG(tactical) bias holding (reclaim above 1587, no formal entry yet).

## GAP-028
- START: bar close 1585861200 (2020-04-02 21:00:00 UTC, epoch-verified). END: bar open 1585865700
  (2020-04-02 22:15:00 UTC). DURATION: 75min exactly. Same recurring daily-rollover class as
  GAP-002..027. Not re-diagnosed. Price continuity confirmed: reopen bar's open (1612.866) matches
  the pre-gap close exactly.
- IMPACT: none — NO_TRADE/SHORT-leaning bias holding, no live setup open across the gap.

## GAP-029
- START: bar close 1586205900 (2020-04-06 20:45:00 UTC, epoch-verified). END: bar open 1586210400
  (2020-04-06 22:00:00 UTC). DURATION: 75min exactly. Same recurring daily-rollover class as
  GAP-002..028. Not re-diagnosed. Price moved +4.2pts across the gap (1657.595→1661.809) — a normal
  continuation, not a dislocation; no exact-match continuity expected or required for this gap class.
- IMPACT: none — trade #13 had already fully resolved (PL-0073) before the gap; flat, no live setup
  open across it.

## GAP-030
- START: bar close 1586292300 (2020-04-07 20:45:00 UTC, epoch-verified). END: bar open 1586296800
  (2020-04-07 22:00:00 UTC). DURATION: 75min exactly. Same recurring daily-rollover class as
  GAP-002..029. Not re-diagnosed. Price continuity confirmed: reopen open (1648.838) close to the
  pre-gap close (1649.604), normal continuation.
- IMPACT: none — flat, no live setup open across the gap.

## GAP-031
- START: bar close 1586378700 (2020-04-08 20:45:00 UTC, epoch-verified). END: bar open 1586383200
  (2020-04-08 22:00:00 UTC). DURATION: 75min exactly. Same recurring daily-rollover class as
  GAP-002..030. Not re-diagnosed. Price continuity confirmed: reopen open (1645.544) close to the
  pre-gap close (1646.274), normal continuation.
- IMPACT: none — flat, no live setup open across the gap.

## WEEKEND-008 (expected, extended for Good Friday holiday — not counted with GAP-001..031)
- START: bar close 1586465100 (2020-04-09 20:45:00 UTC, epoch-verified, Thursday). END: bar open
  1586728800 (2020-04-12 22:00:00 UTC, epoch-verified, Sunday). DURATION: 73.25h — longer than the
  standard ~49-50h weekend pattern (WEEKEND-001..007) because 2020-04-10 (Good Friday) was a full
  closed trading day on top of the regular weekend; market closed Thursday evening instead of the
  usual Friday evening and reopened at the standard Sunday 22:00 UTC time. Verified via a genuine
  investigation (current_date jumped ~50h ahead of the last revealed bar before the gap was even
  stepped into, then stepping revealed the actual 73.25h gap) — not silently assumed. Price continuity
  confirmed exact: reopen open (1683.505) matches the pre-gap close (1683.505) precisely.
- IMPACT: none — flat, no live setup open across the gap.

## WEEKEND-007 (expected, not counted with GAP-001..028)
- START: bar close 1585947600 (Fri 2020-04-03 21:00:00 UTC, epoch-verified). END: bar open 1586124000
  (Sun 2020-04-05 22:00:00 UTC). DURATION: 49.25h exactly. Same expected weekend-closure pattern as
  WEEKEND-001..006.
- Reopen bar: O1618.425/H1620.918/L1609.26/C1612.576, vol 3192 — open matches the pre-weekend close
  (1618.425) exactly, no gap-jump.
- APPRENTICESHIP IMPACT: none — NO_TRADE/NEUTRAL going into the weekend, no live setup open.

## WEEKEND-006 (expected, not counted with GAP-001..024)
- START: bar close 1585341900 (Sat 2020-03-28 ~04:45 UTC est.). END: bar open 1585522800 (Mon 2020-03-30 ~05:00 UTC est.). DURATION: ~50.25h. Same expected weekend-closure pattern as WEEKEND-001..005.
- Reopen bar: H1632.3/L1627.2, close 1630.7, vol 633 — reopened essentially at the pre-weekend close level (1627.7), no gap-jump.
- APPRENTICESHIP IMPACT: none — NEUTRAL/NO_TRADE going into the weekend, no setup open.

## WEEKEND-005 (expected, not counted with GAP-001..020)
- START: bar close 1584737100 (Fri 2020-03-20 ~22:45 UTC est.). END: bar open 1584914400 (Sun 2020-03-22 ~23:00 UTC est.). DURATION: ~49.25h. Same expected weekend-closure pattern as WEEKEND-001..004.
- Reopen bar: H1508.4/L1492.6, close 1498.0, vol 2439 — reopened inside the prior 1479-1504 stretch, no gap-jump.
- APPRENTICESHIP IMPACT: none — NO_TRADE/NEUTRAL going into the weekend, no setup open.

Six gaps so far (GAP-001 ~5.25h isolated, GAP-002/003/004/005/006 ~1h-75min each). GAP-002 through
GAP-006 all fall in the same ~21:00-23:00 UTC window on consecutive trading days — this is now a
recognized RECURRING DAILY pattern (most likely the OANDA/broker daily rollover-maintenance window),
not a series of independent unexplained events. Downgrading this class from "isolated unexplained" to
"expected recurring, mechanism inferred but not proven" — still never reconstructed/used for learning,
per the same rules as any other gap, but no longer counted toward the isolated-unexplained-gap escalation
threshold (same treatment as WEEKEND-001). GAP-001 (~5.25h, non-recurring timing) remains the only true
isolated unexplained gap on record. Still below the CEO's `TRADINGVIEW_REPLAY_DATA_QUALITY_GATE`
threshold — no apprenticeship impact from any gap so far, and the daily-rollover class is now predictable
rather than concerning. Will still log each future occurrence tersely and escalate only if apprenticeship
impact ever occurs (a live setup spanning the window) or a genuinely new gap class appears.

## GAP-032 (recurring daily-rollover class, same treatment as GAP-002..031)
- START: bar close 1586897100 (2020-04-14 20:45:00 UTC). END: bar open 1586901600 (2020-04-14
  22:00:00 UTC). DURATION: 75min. Same recurring ~20:45-22:00 UTC daily-rollover window as GAP-030/031.
- Reopen bar: O1727.175/H1729.956/L1727.175, close 1729.259, vol 359 — reopened at the prior close
  (1727.175), no price-jump.
- APPRENTICESHIP IMPACT: trade #27 (SIMULATED SHORT) was open across this gap — noted for the record;
  the reopen bar's close (1729.259) is what closes the trade via the already-tightened 1728.5 stop,
  not the gap itself. No lookahead or gap-exploitation involved (same one-step-one-read discipline).

## GAP-033 (recurring daily-rollover class, same treatment as GAP-002..032)
- START: bar close 1586983500 (2020-04-15 20:45:00 UTC). END: bar open 1586988000 (2020-04-15
  22:00:00 UTC). DURATION: 75min. Same recurring ~20:45-22:00 UTC daily-rollover window.
- Reopen bar: O1715.948/H1716.678/L1714.826, close 1715.923, vol 179 — reopened at the prior close
  (1715.948), no price-jump.
- APPRENTICESHIP IMPACT: none — flat going into the gap, no open position.

## GAP-034 (recurring daily-rollover class, same treatment as GAP-002..033)
- START: bar close 1587069900 (2020-04-16 20:45:00 UTC). END: bar open 1587074400 (2020-04-16
  22:00:00 UTC). DURATION: 75min. Same recurring ~20:45-22:00 UTC daily-rollover window.
- Reopen bar: O1718.352/H1718.352/L1704.036, close 1707.855, vol 1425 — reopened at the prior close
  (1718.352), no price-jump; the wide range and directional move happened WITHIN the reopen bar, not
  as a jump across the gap.
- APPRENTICESHIP IMPACT: this reopen bar's close (1707.855) is the bar that closes below the 1709
  SHORT_IF — see trade #28 entry, logged separately. No lookahead: this is a genuine one-step-one-read
  reveal, not a reconstruction.

## WEEKEND-009 (expected, not counted with GAP-001..034)
- START: bar close 1587156300 (Friday 2020-04-17 20:45 UTC). END: bar open 1587333600 (Sunday
  2020-04-19 22:00 UTC). DURATION: ~49.5h. Same expected weekend-closure pattern as WEEKEND-001..008.
- Reopen bar: O1683.5 (exact match to prior close, no price-jump)/H1684.196/L1681.151, close 1682.97,
  vol 1462.
- APPRENTICESHIP IMPACT: **NOTABLE — first time in this apprenticeship a SIMULATED trade was left OPEN
  across a full weekend gap.** Trade #31 (SHORT, entry 1681.421, stop 1687.0, target 1671-1676) was
  open at Friday close and remained open through the reopen. No lookahead involved — the reopen bar
  was read fresh via the standard one-step-one-read process, exactly like any other bar; the position
  was simply carried forward unmanaged (as it must be — no intervening bars existed to manage it on).
  This is disclosed explicitly because it changes the trade's risk character (49.5 hours of
  unmanageable exposure) in a way worth tracking if it recurs.

## GAP-035 (recurring daily-rollover class, same treatment as GAP-002..034)
- START: bar close 1587415500 (2020-04-20 20:45:00 UTC). END: bar open 1587420000 (2020-04-20
  22:00:00 UTC). DURATION: 75min.
- Reopen bar: O1696.239 (matches prior close, no price-jump)/H1696.703/L1693.994, close 1694.64,
  vol 390.
- APPRENTICESHIP IMPACT: none — flat going into the gap.

## GAP-036 (recurring daily-rollover class, same treatment as GAP-002..035)
- START: bar close 1587501900 (2020-04-21 20:45:00 UTC). END: bar open 1587506400 (2020-04-21
  22:00:00 UTC). DURATION: 75min.
- Reopen bar: O1687.048 (matches prior close, no price-jump)/H1689.692/L1684.172, close 1688.738,
  vol 554.
- APPRENTICESHIP IMPACT: none direct, but see PL-0277 — the pre-gap and post-gap bars both closed
  above LONG_IF on volumes (198, 554) far thinner than the 2000-12000+ real volume that defended this
  level all day — flagged as insufficient confirmation, not treated as a genuine trigger yet.

## GAP-037 (recurring daily-rollover class, same treatment as GAP-002..036)
- START: bar close 1587589200 (2020-04-22 20:45:00 UTC). END: bar open 1587592800 (2020-04-22
  22:00:00 UTC). DURATION: 60min (shorter than the usual 75min).
- Reopen bar: O1714.292 (matches prior close, no price-jump)/H1715.292/L1712.348, close 1714.492,
  vol 273.
- APPRENTICESHIP IMPACT: none — trade #37 (LONG, entry 1709.778, stop 1706.5) carried through
  unmanaged as usual for a gap this size; price continuity confirmed, no lookahead.

## GAP-038 (recurring daily-rollover class, same treatment as GAP-002..037)
- START: bar close 1587675600 (2020-04-23 21:00:00 UTC). END: bar open 1587679200 (2020-04-23
  22:00:00 UTC). DURATION: 60min.
- Reopen bar: O1731.391 (matches prior close, no price-jump)/H1731.391/L1729.586, close 1730.655,
  vol 308.
- APPRENTICESHIP IMPACT: none direct — trade #38 (LONG, entry 1731.293, tightened stop 1722.5)
  carried through unmanaged as usual for a gap this size; price continuity confirmed, no lookahead.

## WEEKEND-010 (expected, not counted with GAP-001..038)
- START: bar close 1587762000 (2020-04-24 21:00:00 UTC, Friday). END: bar open 1587938400
  (2020-04-26 22:00:00 UTC, Sunday). DURATION: 49h.
- Reopen bar: O1729.406 (matches prior close, no price-jump)/H1729.406/L1720.074, close 1721.128,
  vol 1458 — a down bar on reopen.
- APPRENTICESHIP IMPACT: none — flat going into the weekend (no open SIMULATED trade), unlike
  WEEKEND-009. Reading the reopen bar fresh, no lookahead.

## GAP-039 (recurring daily-rollover class, same treatment as GAP-002..038)
- START: bar close 1588021200 (2020-04-27 21:00:00 UTC). END: bar open 1588024800 (2020-04-27
  22:00:00 UTC). DURATION: 60min.
- Reopen bar: O1713.938 (matches prior close, no price-jump)/H1716.958/L1712.007, close 1712.884,
  vol 384.
- APPRENTICESHIP IMPACT: trade #39 (LONG, entry 1717.506, literal stop 1713.7) carried through the
  gap unmanaged as usual; the reopen bar's close (1712.884) closes below the literal stop — see
  trade #39 resolution in 2020_Q2_H4_LOG.md. Open (1713.938) did not gap through the stop; the
  closing violation happened normally within this bar.

## GAP-040 (recurring daily-rollover class, same treatment as GAP-002..039)
- START: bar close 1588107600 (2020-04-28 21:00:00 UTC). END: bar open 1588111200 (2020-04-28
  22:00:00 UTC). DURATION: 60min.
- Reopen bar: O1708.96 (matches prior close, no price-jump)/H1708.96/L1704.678, close 1705.744,
  vol 655.
- APPRENTICESHIP IMPACT: none — flat going into the gap.

## GAP-041 (recurring daily-rollover class, same treatment as GAP-002..040)
- START: bar close 1588194000 (2020-04-29 21:00:00 UTC). END: bar open 1588197600 (2020-04-29
  22:00:00 UTC). DURATION: 60min.
- Reopen bar: O1712.734 (matches prior close, no price-jump)/H1713.382/L1710.432, close 1713.097,
  vol 526.
- APPRENTICESHIP IMPACT: none — flat going into the gap. Logged under V2 pilot; integrity events
  remain immediate-write per rule 7, not buffered.

## GAP-042 (recurring daily-rollover class, same treatment as GAP-002..041)
- START: bar close 1588280400 (2020-04-30 21:00:00 UTC). END: bar open 1588284000 (2020-04-30
  22:00:00 UTC). DURATION: 60min.
- Reopen bar: O1686.618 (matches prior close, no price-jump)/H1688.186/L1685.536, close 1688.108,
  vol 187.
- APPRENTICESHIP IMPACT: none — flat going into the gap.

## WEEKEND-011 (expected, not counted with GAP-001..042)
- START: bar close 1588366800 (2020-05-01 21:00:00 UTC, Friday). END: bar open 1588543200
  (2020-05-03 22:00:00 UTC, Sunday). DURATION: 49h.
- Reopen bar: O1701.282 (matches prior close, no price-jump)/H1701.282/L1697.932, close 1699.768,
  vol 434.
- APPRENTICESHIP IMPACT: none — flat going into the weekend. Logged under V2 pilot; integrity
  events remain immediate-write per rule 7, not buffered.

## GAP-043

- TYPE: standard daily-rollover gap (60-75min class)
- BOUNDARY: last bar 2020-05-04 20:45:00 UTC (T1588625100) -> next bar 2020-05-04 22:00:00 UTC (T1588629600)
- GAP DURATION: ~75 minutes (60 min of missing bar-data + normal 15min bar spacing)
- PRICE CONTINUITY: confirmed -- next bar open (1701.424) exactly matches prior bar close (1701.424), no jump
- COMPLICATIONS: none

## GAP-044

- TYPE: standard daily-rollover gap (60-75min class)
- BOUNDARY: last bar 2020-05-05 20:45:00 UTC (T1588711500) -> next bar 2020-05-05 22:00:00 UTC (T1588716000)
- GAP DURATION: ~75 minutes (60 min of missing bar-data + normal 15min bar spacing)
- PRICE CONTINUITY: confirmed -- next bar open (1705.682) exactly matches prior bar close (1705.682), no jump
- COMPLICATIONS: none

## GAP-045

- TYPE: standard daily-rollover gap (60-75min class)
- BOUNDARY: last bar 2020-05-06 20:45:00 UTC (T1588797900) -> next bar 2020-05-06 22:00:00 UTC (T1588802400)
- GAP DURATION: ~75 minutes (60 min of missing bar-data + normal 15min bar spacing)
- PRICE CONTINUITY: confirmed -- next bar open (1685.384) exactly matches prior bar close (1685.384), no jump
- COMPLICATIONS: none

## GAP-046

- TYPE: standard daily-rollover gap (60-75min class)
- BOUNDARY: last bar 2020-05-07 20:45:00 UTC (T1588884300) -> next bar 2020-05-07 22:00:00 UTC (T1588888800)
- GAP DURATION: ~75 minutes (60 min of missing bar-data + normal 15min bar spacing)
- PRICE CONTINUITY: confirmed -- next bar open (1715.553) exactly matches prior bar close (1715.553), no jump
- COMPLICATIONS: none

### GAP-047
CLASS: Standard weekend market closure
FROM: 2020-05-08 20:45:00 UTC (last Friday bar, close 1702.39)
TO: 2020-05-10 22:00:00 UTC (first Sunday bar, open 1702.39)
PRICE CONTINUITY: exact match (open == prior close, 1702.39) -- no price gap, time gap only
VERIFIED VIA: python3 epoch conversion

### GAP-048
CLASS: Standard daily rollover
FROM: 2020-05-11 20:45:00 UTC (close 1697.826)
TO: 2020-05-11 22:15:00 UTC (open 1697.826)
PRICE CONTINUITY: exact match, no price gap, time gap only (~90 min)
VERIFIED VIA: python3 epoch conversion

### GAP-048 CORRECTION
Original entry said reopen bar TO: 22:15:00 UTC -- imprecise. The actual reopen bar is T=1589234400,
open time 2020-05-11 22:00:00 UTC (spanning 22:00-22:15), open 1697.826 (exact match to the prior
close, no price gap). The 22:14:59 figure was the replay engine's current_date pointer after the step,
not the bar's own timestamp. Data itself was correct throughout; only this ledger's stated reopen time
needed correcting. Disclosed per standing practice rather than silently editing the original entry.

### GAP-049
CLASS: Standard daily rollover
FROM: 2020-05-12 20:45:00 UTC (close 1702.46)
TO: 2020-05-12 22:00:00 UTC (open 1702.46)
PRICE CONTINUITY: exact match, no price gap, time gap only (~90 min)
VERIFIED VIA: python3 epoch conversion

### GAP-050
CLASS: Standard daily rollover
FROM: 2020-05-13 20:45:00 UTC (close 1716.956)
TO: 2020-05-13 22:00:00 UTC (open 1716.956)
PRICE CONTINUITY: exact match, no price gap, time gap only (~90 min)
VERIFIED VIA: python3 epoch conversion
### GAP-051
CLASS: Standard daily rollover
FROM: 2020-05-14 20:45:00 UTC (close 1730.786)
TO: 2020-05-14 22:00:00 UTC (open 1730.786)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion

### GAP-052
CLASS: Weekend gap
FROM: 2020-05-15 20:45:00 UTC (close 1742.624)
TO: 2020-05-17 22:00:00 UTC (open 1742.624)
PRICE CONTINUITY: exact match, no price gap, time gap only (~49.25 hrs)
VERIFIED VIA: python3 epoch conversion

### GAP-053
CLASS: Standard daily rollover
FROM: 2020-05-18 20:45:00 UTC (close 1732.882)
TO: 2020-05-18 22:00:00 UTC (open 1732.882)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion


### GAP-054
CLASS: Standard daily rollover
FROM: 2020-05-19 20:45:00 UTC (close 1744.77)
TO: 2020-05-19 22:00:00 UTC (open 1744.77)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion

### GAP-055
CLASS: Standard daily rollover
FROM: 2020-05-20 20:45:00 UTC (close 1748.104)
TO: 2020-05-20 22:00:00 UTC (open 1748.104)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion

### GAP-056
CLASS: Standard daily rollover
FROM: 2020-05-21 20:45:00 UTC (close 1727.168)
TO: 2020-05-21 22:00:00 UTC (open 1727.168)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion

### GAP-057
CLASS: Weekend gap
FROM: 2020-05-22 20:45:00 UTC (close 1734.448)
TO: 2020-05-24 22:00:00 UTC (open 1734.448)
PRICE CONTINUITY: exact match, no price gap, time gap only (~49.25 hrs)
VERIFIED VIA: python3 epoch conversion

### GAP-058
CLASS: Holiday-shortened session gap (US Memorial Day, 2020-05-25) -- early close, NOT the standard ~75min daily rollover
FROM: 2020-05-25 16:45:00 UTC (close 1729.186)
TO: 2020-05-25 22:00:00 UTC (open 1729.186)
PRICE CONTINUITY: exact match, no price gap, time gap only (5.25 hrs)
VERIFIED VIA: python3 epoch conversion
NOTE: session closed roughly 4 hours earlier than the typical ~20:45 UTC daily rollover, consistent
with reduced US holiday trading hours; still resumed at the standard 22:00 UTC Asia open.

### GAP-059
CLASS: Standard daily rollover
FROM: 2020-05-26 20:45:00 UTC (close 1711.079)
TO: 2020-05-26 22:00:00 UTC (open 1711.079)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: trade #56 remained OPEN across this gap (SHORT, entry 1718.845, stop close-above-1712.888).
### GAP-060
CLASS: Standard daily rollover
FROM: 2020-05-27 20:45:00 UTC (close 1709.417)
TO: 2020-05-27 22:00:00 UTC (open 1709.417)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion (both boundary timestamps double-checked as part of the
15-minute label-drift erratum investigation in 2020_Q2_H4_LOG.md -- this gap is logged at its
confirmed-correct true time, not a drifted label).
NOTE: no open position at this gap. Position: FLAT.
### GAP-061
CLASS: Standard daily rollover
FROM: 2020-05-28 20:45:00 UTC (close 1718.807)
TO: 2020-05-28 22:00:00 UTC (open 1718.807)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: no open position at this gap. Position: FLAT.
### GAP-062
CLASS: Weekend gap
FROM: 2020-05-29 20:45:00 UTC (close 1729.615, Friday)
TO: 2020-05-31 22:00:00 UTC (open 1729.615, Sunday)
PRICE CONTINUITY: exact match, no price gap, time gap only (49.25 hours)
VERIFIED VIA: python3 epoch conversion
NOTE: no open position at this gap. Position: FLAT.
### GAP-063
CLASS: Standard daily rollover
FROM: 2020-06-01 20:45:00 UTC (close 1739.923)
TO: 2020-06-01 22:00:00 UTC (open 1739.923)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: no open position at this gap. Position: FLAT.
### GAP-064
CLASS: Standard daily rollover
FROM: 2020-06-02 20:45:00 UTC (close 1727.951)
TO: 2020-06-02 22:00:00 UTC (open 1727.951)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: no open position at this gap. Position: FLAT.
### GAP-065
CLASS: Standard daily rollover
FROM: 2020-06-03 20:45:00 UTC (close 1698.056)
TO: 2020-06-03 22:00:00 UTC (open 1698.056)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: trade #59 remained OPEN across this gap (SHORT, entry 1712.008, trailed stop 1711.9). No
lookahead -- reopen bar read fresh via standard one-step-one-read, position simply carried forward
unmanaged (no intervening bars existed to manage it on).
### GAP-066
CLASS: Standard daily rollover
FROM: 2020-06-04 20:45:00 UTC (close 1714.272)
TO: 2020-06-04 22:00:00 UTC (open 1714.272)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: no open position at this gap. Position: FLAT.
### GAP-067
CLASS: Weekend gap
FROM: 2020-06-05 20:45:00 UTC (close 1685.27, Friday)
TO: 2020-06-07 22:00:00 UTC (open 1685.27, Sunday)
PRICE CONTINUITY: exact match, no price gap, time gap only (49.25 hours)
VERIFIED VIA: python3 epoch conversion
NOTE: trade #62 remained OPEN across this gap (SHORT, entry 1680.167, stop 1688.5, never
trailed). No lookahead -- reopen bar read fresh via standard one-step-one-read, position simply
carried forward unmanaged (no intervening bars existed to manage it on). Second time in this
apprenticeship a trade has been carried across a full weekend (first was trade #31, WEEKEND-009).
### GAP-068
CLASS: Standard daily rollover
FROM: 2020-06-08 20:45:00 UTC (close 1698.298)
TO: 2020-06-08 22:00:00 UTC (open 1698.298)
PRICE CONTINUITY: exact match, no price gap, time gap only (75 min)
VERIFIED VIA: python3 epoch conversion
NOTE: trade #63 remained OPEN across this gap (LONG, entry 1695.555, trailed stop 1692.9). No
lookahead -- reopen bar read fresh via standard one-step-one-read, position carried forward
unmanaged.

### GAP-069 -- standard daily rollover, 2020-06-09
TIME: 2020-06-09 20:45:00 UTC -> 22:00:00 UTC (T=1591735500 -> 1591740000), verified via python3.
Same recurring window as GAP-068 (2020-06-08, same 20:45->22:00 UTC daily rollover). Price
continuity exact: last bar close 1714.786 -> new bar open 1714.786. 4 M15 bars skipped
(21:00/21:15/21:30/21:45 UTC), consistent with the standard daily maintenance/settlement halt.
No trade open during any prior occurrence of this gap window required special handling beyond
noting it; trade #63 (LONG, entry 1695.555, trailed stop 1706.478) carried across unmanaged, stop
and position unaffected by the gap itself.

### GAP-070 -- standard daily rollover, 2020-06-10
TIME: 2020-06-10 20:45:00 UTC -> 22:00:00 UTC (T=1591821900 -> 1591826400), verified via python3.
Same recurring window as GAP-068/GAP-069 (20:45->22:00 UTC daily rollover). Price continuity exact:
last bar close 1738.67 -> new bar open 1738.67. No position open (FLAT) -- no trade impact.

### GAP-071 -- standard daily rollover, 2020-06-11
TIME: 2020-06-11 20:45:00 UTC -> 22:00:00 UTC (T=1591908300 -> 1591912800), verified via python3.
Same recurring window as GAP-068/069/070. Price continuity exact: last bar close 1727.216 -> new
bar open 1727.216. No position open (FLAT) -- no trade impact.

### GAP-072 -- WEEKEND ROLLOVER, 2020-06-12 -> 2020-06-14
TIME: 2020-06-12 20:45:00 UTC -> 2020-06-14 22:00:00 UTC (T=1591994700 -> 1592172000), verified
via python3. Duration: 49.25 hours -- a genuine weekend gap, NOT the usual ~75-minute daily
rollover pattern (GAP-068 through GAP-071). Standard Friday-evening-to-Sunday-evening FX/CFD
market closure (reopen 22:00 UTC Sunday = 17:00 ET, matching typical forex weekend reopen).

Price continuity exact: last bar close 1730.905 (2020-06-12 20:45 UTC) -> new bar open 1730.905
(2020-06-14 22:00 UTC).

NOTABLE FIRST for this apprenticeship: TRADE #64 (SHORT, entry 1740.496, trailed stop 1733.254,
unrealized +9.591pts/+2.169R at the pre-gap close) was OPEN and carried through this gap --
every prior gap this session (GAP-068 through GAP-071) crossed while FLAT. No action taken or
needed; gaps are not tradeable events under the standing replay methodology, and price continuity
was exact (no jump risk materialized in this instance). Position and stop unaffected.

### GAP-073 -- standard daily rollover, 2020-06-15
TIME: 2020-06-15 20:45:00 UTC -> 22:00:00 UTC (T=1592253900 -> 1592258400), verified via python3.
Same recurring window as GAP-068/069/070/071. Price continuity exact: last bar close 1725.154 ->
new bar open 1725.154. No position open (FLAT) -- no trade impact.

### GAP-074 -- 2020-06-16 20:45 UTC -> 22:00 UTC (75 min, standard daily rollover)

Last bar before gap: 20:45 UTC (close 1727.09). First bar after gap: 22:00 UTC (O1727.09/H1727.09/
L1724.218/C1725.912, V495). Standard recurring ~75-minute daily rollover pattern (consistent with
prior GAP entries this quarter). Trade #65 remained OPEN across this gap; no stop concern (gap
resolves at 1725.912, well clear of the 1732.242 stop; open equals prior close, no jump risk on
this rollover).

### GAP-075 -- 2020-06-17 20:45 UTC -> 22:00 UTC (75 min, standard daily rollover)

Last bar before gap: 20:45 UTC (close 1726.761). First bar after gap: 22:00 UTC (O1726.761/
H1727.476/L1726.071/C1727.368, V69). Standard recurring pattern. Trade #65 remained OPEN across
this gap; no stop concern (open equals prior close, LIVE_STOP 1730.7 well clear).

### GAP-076 -- 2020-06-18 20:45 UTC -> 22:00 UTC (75 min, standard daily rollover)

Last bar before gap: 20:45 UTC (close 1722.644). First bar after gap: 22:00 UTC (O1722.644/
H1723.647/L1722.59/C1723.46, V97). Standard recurring pattern. FLAT position, no concern.

### GAP-077 -- 2020-06-19 20:45 UTC -> 2020-06-21 22:00 UTC (49.25 hours, WEEKEND gap)

Last bar before gap: 2020-06-19 20:45 UTC (Friday close, 1744.189). First bar after gap: 2020-06-21
22:00 UTC (Sunday open, O1744.189/H1750.095/L1744.082/C1746.44, V1031) -- open equals prior close,
no jump/gap risk. FLAT position throughout, no concern. This is the first weekend gap crossed since
GAP-072 (2020-06-11).

### GAP-078 -- 2020-06-22 20:45 UTC -> 22:00 UTC (75 min, standard daily rollover)

Last bar before gap: 20:45 UTC (close 1754.766). First bar after gap: 22:00 UTC (O1754.766/
H1755.428/L1753.39/C1754.417, V379). Standard recurring pattern. FLAT position, no concern.

### GAP-079 (2020-06-23 20:45-22:00 UTC)

Standard daily rollover, 75 minutes (20:45 close -> 22:00 next bar open). Consistent with all prior
standard rollovers this quarter (GAP-074 through GAP-078). Not a data-integrity issue.

### GAP-080 (2020-06-24 20:45-22:00 UTC)

Standard daily rollover, 75 minutes (20:45 close -> 22:00 next bar open). Consistent with prior
standard rollovers this quarter. Not a data-integrity issue.

### GAP-081 (2020-06-25 20:45-22:00 UTC)

Standard daily rollover, 75 minutes. Consistent with prior rollovers this quarter. Not a
data-integrity issue.

### GAP-082 (2020-06-26 20:45 UTC -- 2020-06-28 22:00 UTC)

Standard weekend gap, 49.25 hours (Friday 20:45 close -> Sunday 22:00 next bar open). Consistent
with prior weekend gaps this quarter. Not a data-integrity issue.

### GAP-083 (2020-06-29 20:45-22:00 UTC)

Standard daily rollover, 75 minutes. Consistent with prior rollovers this quarter. Not a
data-integrity issue.

### GAP-084

- **Window:** 2020-06-30 20:45:00 UTC (last pre-gap bar close) -> 2020-06-30 22:00:00 UTC (first
  post-gap bar open). Skips 21:00/21:15/21:30/21:45 UTC.
- **Duration:** 75 minutes.
- **Classification:** standard daily rollover gap -- matches this apprenticeship's recurring class
  (~75min, broker daily-rollover/maintenance window), consistent with GAP-001 through GAP-083.
- **Verification:** confirmed via replay_step jumping current_date directly from 1593550799 to
  1593555299 (4500s), and data_get_ohlcv(count=1) returning the next available bar at 1593554400
  (22:00:00 UTC) with no intervening bars at any resolution checked.
- **Apprenticeship impact:** none. FLAT, no open position at the time of this gap.

### GAP-085

- **Window:** 2020-07-01 20:45:00 UTC -> 2020-07-01 22:00:00 UTC. Skips 21:00/21:15/21:30/21:45 UTC.
- **Duration:** 75 minutes.
- **Classification:** standard daily rollover gap, matches the recurring class (GAP-001..084).
- **Verification:** replay_step jumped current_date directly (4500s), data_get_ohlcv confirmed no
  intervening bars.
- **Apprenticeship impact:** none. FLAT, no open position.

### GAP-086

- **Window:** 2020-07-02 20:45:00 UTC -> 2020-07-02 22:00:00 UTC. Standard daily rollover, 75min.
- **Verification:** replay_step jump (4500s) confirmed, no intervening bars.
- **Apprenticeship impact:** none. FLAT.

### GAP-087 (WEEKEND, July 4th holiday extended)

- **Window:** 2020-07-03 16:45:00 UTC -> 2020-07-05 22:00:00 UTC. Duration 53.25 hours.
- **Classification:** weekend closure, extended by the July 4th (Saturday 2020) US Independence
  Day holiday -- longer than the standard ~49.25h weekend gap, consistent with a holiday weekend.
- **Verification:** replay_step jump (191700s) confirmed, data_get_ohlcv shows no intervening bars.
- **Apprenticeship impact:** none. FLAT, no open position.

### GAP-088

- **Window:** 2020-07-06 20:45:00 UTC -> 2020-07-06 22:00:00 UTC. Standard daily rollover, 75min.
- **Verification:** replay_step jump (4500s) confirmed, no intervening bars.
- **Apprenticeship impact:** none. FLAT.

### GAP-089

- **Window:** 2020-07-07 20:45:00 UTC -> 2020-07-07 22:00:00 UTC. Standard daily rollover, 75min.
- **Verification:** replay_step jump (4500s) confirmed, no intervening bars.
- **Apprenticeship impact:** none. FLAT.

### GAP-090

- **Window:** 2020-07-08 20:45:00 UTC -> 2020-07-08 22:00:00 UTC. Standard daily rollover, 75min.
- **Verification:** replay_step jump (4500s) confirmed, no intervening bars.
- **Apprenticeship impact:** none. FLAT.

### GAP-091
WINDOW: 2020-07-09 21:00 UTC -> 2020-07-09 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-09 20:45 UTC close 1803.382
FIRST_BAR_AFTER_GAP: 2020-07-09 22:00 UTC open 1802.611 (V19, thin)
VERIFICATION: replay_step pointer jumped directly 1594328399 (20:59:59) -> 1594332899 (22:14:59),
confirmed via python3 timestamp conversion; no intermediate 21:00/21:15/21:30/21:45 bars exist in
data_get_ohlcv output for this window.
IMPACT: none -- FLAT throughout, no open position affected. Standard daily rollover pattern
(consistent with GAP-085 through GAP-090).

### GAP-092 (weekend)
WINDOW: 2020-07-10 21:00 UTC (Friday) -> 2020-07-12 22:00 UTC (Sunday), ~49h15m
LAST_BAR_BEFORE_GAP: 2020-07-10 20:45 UTC close 1798.446
FIRST_BAR_AFTER_GAP: 2020-07-12 22:00 UTC open 1798.388 (V318) -- negligible weekend gap (0.058
price / 0.58 pips), no weekend jump risk realized.
VERIFICATION: replay_step pointer jumped directly 1594414799 (2020-07-10 20:59:59) -> 1594592099
(2020-07-12 22:14:59), confirmed via python3 timestamp conversion.
IMPACT: none -- FLAT throughout, no open position affected. Standard weekend rollover.

### GAP-093
WINDOW: 2020-07-13 21:00 UTC -> 2020-07-13 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-13 20:45 UTC close 1802.342
FIRST_BAR_AFTER_GAP: 2020-07-13 22:00 UTC open 1802.717 (V118, thin)
VERIFICATION: replay_step pointer jumped directly 1594673999 (20:59:59) -> 1594678499 (22:14:59),
confirmed via python3 timestamp conversion.
IMPACT: none -- FLAT throughout, no open position affected. Standard daily rollover pattern.

### GAP-094
WINDOW: 2020-07-14 21:00 UTC -> 2020-07-14 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-14 20:45 UTC close 1809.406
FIRST_BAR_AFTER_GAP: 2020-07-14 22:00 UTC open 1808.452 (V64, thin)
VERIFICATION: replay_step pointer jumped directly 1594760399 (20:59:59) -> 1594764899 (22:14:59),
confirmed via python3 timestamp conversion.
IMPACT: none on Q3-003 (open LONG, entry 1807.778, stop 1805.218) -- gap-open price 1808.452 stayed
comfortably within the position's risk band, no stop/TP crossed during the gap. Standard daily
rollover pattern.

### GAP-095
WINDOW: 2020-07-15 21:00 UTC -> 2020-07-15 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-15 20:45 UTC close 1810.36
FIRST_BAR_AFTER_GAP: 2020-07-15 22:00 UTC open 1810.36->close 1811.499 (V31, very thin)
VERIFICATION: replay_step pointer jumped directly 1594846799 (20:59:59) -> 1594851299 (22:14:59),
confirmed via python3 timestamp conversion.
IMPACT: none -- FLAT throughout. Standard daily rollover pattern.

### GAP-096
WINDOW: 2020-07-16 21:00 UTC -> 2020-07-16 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-16 20:45 UTC close 1797.436
FIRST_BAR_AFTER_GAP: 2020-07-16 22:00 UTC open 1797.436->close 1797.816 (V143)
VERIFICATION: replay_step pointer jumped directly 1594933199 (20:59:59) -> 1594937699 (22:14:59),
confirmed via python3 timestamp conversion.
IMPACT: none on Q3-004 (open SHORT, entry 1803.886, stop 1806.513) -- gap-open price 1797.436 stayed
comfortably within the position's risk band. Standard daily rollover pattern.

### GAP-097 (weekend)
WINDOW: 2020-07-17 21:00 UTC (Friday) -> 2020-07-19 22:00 UTC (Sunday), ~49h15m
LAST_BAR_BEFORE_GAP: 2020-07-17 20:45 UTC close 1810.046
FIRST_BAR_AFTER_GAP: 2020-07-19 22:00 UTC close 1808.782 (V278) -- negligible weekend gap
(1.264 price / 12.64 pips off the Friday close, minor).
VERIFICATION: replay_step pointer jumped directly 1595019599 (2020-07-17 20:59:59) -> 1595196899
(2020-07-19 22:14:59), confirmed via python3 timestamp conversion.
IMPACT: none -- FLAT throughout. Standard weekend rollover.

### GAP-098
WINDOW: 2020-07-20 21:00 UTC -> 2020-07-20 22:00 UTC (75 min)
LAST_BAR_BEFORE_GAP: 2020-07-20 20:45 UTC close 1817.312
FIRST_BAR_AFTER_GAP: 2020-07-20 22:00 UTC close 1817.951 (V76, thin)
VERIFICATION: replay_step pointer jumped directly 1595278799 (20:59:59) -> 1595283299 (22:14:59),
confirmed via python3 timestamp conversion.
IMPACT: none -- FLAT throughout. Standard daily rollover pattern.

### GAP-099
WINDOW: 2020-07-21 21:00:00 UTC -> 2020-07-21 22:00:00 UTC (standard daily rollover, ~75min observed
in bar timestamps: last bar close 20:59:59, first bar open 22:00:00)
LAST_BAR_BEFORE_GAP: time=1595364300 (open), close=20:59:59 UTC, close_price=1841.673
FIRST_BAR_AFTER_GAP: time=1595368800 (open), open_price=1841.673, close=22:14:59 UTC, close_price=1841.428
VERIFICATION: python3 utcfromtimestamp confirmed both timestamps; gap = 4500s (75min) matching the
standard daily rollover convention (21:00-22:00 UTC broker downtime + M15 bar alignment).
IMPACT: Zero price gap -- first-bar-after open (1841.673) exactly matches last-bar-before close
(1841.673). Negligible, no trading impact, no watched level affected.

### GAP-100
WINDOW: 2020-07-22 21:00:00 UTC -> 2020-07-22 22:00:00 UTC (standard daily rollover, ~75min observed
in bar timestamps: last bar close 20:59:59, first bar open 22:00:00)
LAST_BAR_BEFORE_GAP: time=1595450700 (open), close=20:59:59 UTC, close_price=1871.828
FIRST_BAR_AFTER_GAP: time=1595455200 (open), open_price=1871.828, close=22:14:59 UTC, close_price=1873.175
VERIFICATION: python3 utcfromtimestamp confirmed both timestamps; gap = 4500s (75min) matching the
standard daily rollover convention.
IMPACT: Zero price gap -- first-bar-after open (1871.828) exactly matches last-bar-before close
(1871.828). Negligible, no trading impact, no watched level affected.

### GAP-101
WINDOW: 2020-07-23 21:00:00 UTC -> 2020-07-23 22:00:00 UTC (standard daily rollover, ~75min observed
in bar timestamps: last bar close 20:59:59, first bar open 22:00:00)
LAST_BAR_BEFORE_GAP: close=20:59:59 UTC, close_price=1887.534
FIRST_BAR_AFTER_GAP: time=1595541600 (open), open_price=1887.534, close=22:14:59 UTC, close_price=1886.964
VERIFICATION: python3 utcfromtimestamp confirmed both timestamps; gap = 4500s (75min) matching the
standard daily rollover convention.
IMPACT: Zero price gap -- first-bar-after open (1887.534) exactly matches last-bar-before close
(1887.534). Negligible, no trading impact, no watched level affected.

### GAP-102
WINDOW: 2020-07-24 21:00:00 UTC -> 2020-07-26 22:00:00 UTC (WEEKEND gap, ~49.25h observed in bar
timestamps: last bar close 20:59:59 Friday, first bar open 22:00:00 Sunday)
LAST_BAR_BEFORE_GAP: time=1595623500 (open), close=20:59:59 UTC (2020-07-24), close_price=1901.637
FIRST_BAR_AFTER_GAP: time=1595800800 (open, 2020-07-26 22:00:00 UTC), open_price=1901.637,
close=22:14:59 UTC, close_price=1906.341
VERIFICATION: python3 utcfromtimestamp confirmed both timestamps; gap = 177300s (49.25h) matching the
standard weekend closure convention.
IMPACT: Zero price gap -- first-bar-after open (1901.637) exactly matches last-bar-before close
(1901.637). Negligible, no trading impact, no watched level affected.

### GAP-103
WINDOW: 2020-07-27 21:00:00 UTC -> 2020-07-27 22:00:00 UTC (standard daily rollover, ~75min observed
in bar timestamps: last bar close 20:59:59, first bar open 22:00:00)
LAST_BAR_BEFORE_GAP: close=20:59:59 UTC, close_price=1942.076
FIRST_BAR_AFTER_GAP: time=1595887200 (open, 22:00:00 UTC), open_price=1942.076, close=22:14:59 UTC,
close_price=1942.422
VERIFICATION: python3 utcfromtimestamp confirmed both timestamps; gap = 4500s (75min) matching the
standard daily rollover convention.
IMPACT: Zero price gap -- first-bar-after open (1942.076) exactly matches last-bar-before close
(1942.076). Negligible, no trading impact, no watched level affected.

### GAP-104
- LAST_BAR_BEFORE_GAP: 2020-07-28 20:45:00-20:59:59 UTC, close=1958.672
- FIRST_BAR_AFTER_GAP: 2020-07-28 22:00:00-22:14:59 UTC, open=1958.672
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-105
- LAST_BAR_BEFORE_GAP: 2020-07-29 20:45:00-20:59:59 UTC, close=1970.91
- FIRST_BAR_AFTER_GAP: 2020-07-29 22:00:00-22:14:59 UTC, open=1970.91
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-106
- LAST_BAR_BEFORE_GAP: 2020-07-30 20:45:00-20:59:59 UTC, close=1956.059
- FIRST_BAR_AFTER_GAP: 2020-07-30 22:00:00-22:14:59 UTC, open=1956.059
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-107
- LAST_BAR_BEFORE_GAP: 2020-07-31 20:45:00-20:59:59 UTC (Friday close), close=1975.962
- FIRST_BAR_AFTER_GAP: 2020-08-02 22:00:00-22:14:59 UTC (Sunday reopen), open=1975.962
- Duration: 49.25h (standard weekend gap)
- Zero price gap (close==open), verified via python3.

### GAP-108
- LAST_BAR_BEFORE_GAP: 2020-08-03 20:45:00-20:59:59 UTC, close=1976.742
- FIRST_BAR_AFTER_GAP: 2020-08-03 22:00:00-22:14:59 UTC, open=1976.742
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-109
- LAST_BAR_BEFORE_GAP: 2020-08-04 20:45:00-20:59:59 UTC, close=2019.413
- FIRST_BAR_AFTER_GAP: 2020-08-04 22:00:00-22:14:59 UTC, open=2019.413
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-110
- LAST_BAR_BEFORE_GAP: 2020-08-05 20:45:00-20:59:59 UTC, close=2038.154
- FIRST_BAR_AFTER_GAP: 2020-08-05 22:00:00-22:14:59 UTC, open=2038.154
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-111
- LAST_BAR_BEFORE_GAP: 2020-08-06 20:45:00-20:59:59 UTC, close=2063.31
- FIRST_BAR_AFTER_GAP: 2020-08-06 22:00:00-22:14:59 UTC, open=2063.31
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-112
- LAST_BAR_BEFORE_GAP: 2020-08-07 20:45:00-20:59:59 UTC (Friday/weekly close), close=2035.23
- FIRST_BAR_AFTER_GAP: 2020-08-09 22:00:00-22:14:59 UTC (Sunday reopen), open=2035.23
- Duration: 49.25h (standard weekend gap)
- Zero price gap (close==open), verified via python3.

### GAP-113
- LAST_BAR_BEFORE_GAP: 2020-08-10 20:45:00-20:59:59 UTC, close=2027.745
- FIRST_BAR_AFTER_GAP: 2020-08-10 22:00:00-22:14:59 UTC, open=2027.745
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-114
- LAST_BAR_BEFORE_GAP: 2020-08-11 20:45:00-20:59:59 UTC, close=1912.075
- FIRST_BAR_AFTER_GAP: 2020-08-11 22:00:00-22:14:59 UTC, open=1912.075
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-115
- LAST_BAR_BEFORE_GAP: 2020-08-12 20:45:00-20:59:59 UTC, close=1916.642
- FIRST_BAR_AFTER_GAP: 2020-08-12 22:00:00-22:14:59 UTC, open=1916.642
- Duration: 75 min (standard daily rollover, 21:00-22:00 UTC)
- Zero price gap (close==open), verified via python3.

### GAP-116
LAST_BAR_BEFORE_GAP: 2020-08-13T20:59:59Z (open 20:45:00, close=1953.57)
FIRST_BAR_AFTER_GAP: 2020-08-13T22:00:00-22:14:59Z (open=1953.57)
Duration: ~60 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1953.57 == next open 1953.57)

### GAP-117
LAST_BAR_BEFORE_GAP: 2020-08-14T20:59:59Z (open 20:45:00, close=1944.714)
FIRST_BAR_AFTER_GAP: 2020-08-16T22:00:00-22:14:59Z (open=1944.714)
Duration: ~49.25h (standard weekend gap, Friday close to Sunday reopen)
Zero-price-gap verified: YES (close 1944.714 == next open 1944.714)
NOTE: this gap falls in the middle of open PATTERN-007 candidate Q3-P007-CAND-08-14-1659
(frozen 16:59:59, still below EMA50 at gap start) -- see resolution entry in
2020_Q3_H4_LOG.md for the active-market-time vs wall-clock-time distinction this produced.

### GAP-118
LAST_BAR_BEFORE_GAP: 2020-08-17T20:59:59Z (open 20:45:00, close=1985.223)
FIRST_BAR_AFTER_GAP: 2020-08-17T22:00:00-22:14:59Z (open=1985.223)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1985.223 == next open 1985.223)

### GAP-119
LAST_BAR_BEFORE_GAP: 2020-08-18T20:59:59Z (open 20:45:00, close=2001.934)
FIRST_BAR_AFTER_GAP: 2020-08-18T22:00:00-22:14:59Z (open=2001.934)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 2001.934 == next open 2001.934)

### GAP-120
LAST_BAR_BEFORE_GAP: 2020-08-19T20:59:59Z (open 20:45:00, close=1929.572)
FIRST_BAR_AFTER_GAP: 2020-08-19T22:00:00-22:14:59Z (open=1929.572)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1929.572 == next open 1929.572)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-19-1459 (still below EMA50
at gap start).

### GAP-121
LAST_BAR_BEFORE_GAP: 2020-08-20T20:59:59Z (open 20:45:00, close=1946.966)
FIRST_BAR_AFTER_GAP: 2020-08-20T22:00:00-22:14:59Z (open=1946.966)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1946.966 == next open 1946.966)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-19-1459 (still below EMA50,
gap ~9.9pt at gap start).

### GAP-122
LAST_BAR_BEFORE_GAP: 2020-08-21T20:59:59Z (open 20:45:00, close=1940.498)
FIRST_BAR_AFTER_GAP: 2020-08-23T22:00:00-22:14:59Z (open=1940.498)
Duration: ~49.25h (standard weekend gap, Friday close to Sunday reopen)
Zero-price-gap verified: YES (close 1940.498 == next open 1940.498)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-19-1459 (still below EMA50 at
gap start, ~59hr wall-clock elapsed since freeze). Per the active-market-time methodology
established on the 08-14 instance, this weekend contributes 0 to
ACTIVE_MARKET_TIME_BELOW_EMA50.

### GAP-123
LAST_BAR_BEFORE_GAP: 2020-08-24T20:59:59Z (open 20:45:00, close=1929.08)
FIRST_BAR_AFTER_GAP: 2020-08-24T22:00:00-22:14:59Z (open=1929.08)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1929.08 == next open 1929.08)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-24-1459 (still below EMA50 at
gap start).

### GAP-124
LAST_BAR_BEFORE_GAP: 2020-08-25T20:59:59Z (open 20:45:00, close=1928.2)
FIRST_BAR_AFTER_GAP: 2020-08-25T22:00:00-22:14:59Z (open=1928.2)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1928.2 == next open 1928.2)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-24-1459 (still below EMA50 at
gap start).

### GAP-125
LAST_BAR_BEFORE_GAP: 2020-08-26T20:59:59Z (open 20:45:00, close=1954.034)
FIRST_BAR_AFTER_GAP: 2020-08-26T22:00:00-22:14:59Z (open=1954.034)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1954.034 == next open 1954.034)

### GAP-126
LAST_BAR_BEFORE_GAP: 2020-08-27T20:59:59Z (open 20:45:00, close=1929.271)
FIRST_BAR_AFTER_GAP: 2020-08-27T22:00:00-22:14:59Z (open=1929.271)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1929.271 == next open 1929.271)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-08-27-1414 (still below EMA50 at
gap start).

### GAP-127
LAST_BAR_BEFORE_GAP: 2020-08-28T20:59:59Z (open 20:45:00, close=1965.026)
FIRST_BAR_AFTER_GAP: 2020-08-30T22:00:00-22:14:59Z (open=1965.026)
Duration: ~49.25h (standard weekend gap, Friday close to Sunday reopen)
Zero-price-gap verified: YES (close 1965.026 == next open 1965.026)

### GAP-128
LAST_BAR_BEFORE_GAP: 2020-08-31T20:59:59Z (open 20:45:00, close=1967.646)
FIRST_BAR_AFTER_GAP: 2020-08-31T22:00:00-22:14:59Z (open=1967.646)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1967.646 == next open 1967.646)

### GAP-129
LAST_BAR_BEFORE_GAP: 2020-09-01T20:59:59Z (open 20:45:00, close=1970.486)
FIRST_BAR_AFTER_GAP: 2020-09-01T22:00:00-22:14:59Z (open=1970.486)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1970.486 == next open 1970.486)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-09-01-1859.

### GAP-130
LAST_BAR_BEFORE_GAP: 2020-09-02T20:59:59Z (open 20:45:00, close=1942.888)
FIRST_BAR_AFTER_GAP: 2020-09-02T22:00:00-22:14:59Z (open=1942.888)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1942.888 == next open 1942.888)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-09-02-1129 (still below EMA50 at
gap start).

### GAP-131
LAST_BAR_BEFORE_GAP: 2020-09-03T20:59:59Z (open 20:45:00, close=1930.673)
FIRST_BAR_AFTER_GAP: 2020-09-03T22:00:00-22:14:59Z (open=1930.673)
Duration: ~75 min (standard daily rollover, 21:00-22:00 UTC)
Zero-price-gap verified: YES (close 1930.673 == next open 1930.673)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-09-02-1129 (still below EMA50
at gap start).

### GAP-132
LAST_BAR_BEFORE_GAP: 2020-09-04T20:59:59Z (open 20:45:00, close=1934.024)
FIRST_BAR_AFTER_GAP: 2020-09-06T22:00:00-22:14:59Z (open=1934.024)
Duration: ~49.25h (standard weekend gap, Friday close to Sunday reopen)
Zero-price-gap verified: YES (close 1934.024 == next open 1934.024)
NOTE: falls within open PATTERN-007 candidate Q3-P007-CAND-09-02-1129, still below EMA50 at
gap start (~100.25hr wall-clock elapsed since freeze at gap start).

### GAP-133
LAST_BAR_BEFORE_GAP: open=2020-09-07T16:45:00Z, close(implied)=2020-09-07T16:59:59Z, close_price=1928.448
FIRST_BAR_AFTER_GAP: open=2020-09-07T22:00:00Z, open_price=1928.448
Duration: 5.0h (17:00:00-22:00:00 UTC), 2020-09-07 = US Labor Day. NEW GAP TYPE (not daily ~75min,
not weekend ~49.25h) -- holiday-session reduced/no trading, most likely CME Labor Day early
close/holiday schedule for COMEX gold futures.
Zero-price-gap verified: last close 1928.448 == first-bar-after open 1928.448 (exact match, no jump).

### GAP-134
LAST_BAR_BEFORE_GAP: open=2020-09-08T20:45:00Z, close(implied)=2020-09-08T20:59:59Z, close_price=1931.694
FIRST_BAR_AFTER_GAP: open=2020-09-08T22:00:00Z, open_price=1931.694
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1931.694 == first-bar-after open 1931.694 (exact match).

### GAP-135
LAST_BAR_BEFORE_GAP: open=2020-09-09T20:45:00Z, close(implied)=2020-09-09T20:59:59Z, close_price=1946.534
FIRST_BAR_AFTER_GAP: open=2020-09-09T22:00:00Z, open_price=1946.534
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1946.534 == first-bar-after open 1946.534 (exact match).

### GAP-136
LAST_BAR_BEFORE_GAP: open=2020-09-10T20:45:00Z, close(implied)=2020-09-10T20:59:59Z, close_price=1946.27
FIRST_BAR_AFTER_GAP: open=2020-09-10T22:00:00Z, open_price=1946.27
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1946.27 == first-bar-after open 1946.27 (exact match).

### GAP-137
LAST_BAR_BEFORE_GAP: open=2020-09-11T20:45:00Z, close(implied)=2020-09-11T20:59:59Z, close_price=1940.456
FIRST_BAR_AFTER_GAP: open=2020-09-13T21:00:00Z, open_price=1940.456
Duration: 49.25h (2020-09-11 21:00:00 UTC Friday close -> 2020-09-13 21:00:00 UTC Sunday reopen),
standard weekend gap.
Zero-price-gap verified: last close 1940.456 == first-bar-after open 1940.456 (exact match).

### GAP-138
LAST_BAR_BEFORE_GAP: open=2020-09-14T20:45:00Z, close(implied)=2020-09-14T20:59:59Z, close_price=1956.442
FIRST_BAR_AFTER_GAP: open=2020-09-14T22:00:00Z, open_price=1956.442
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1956.442 == first-bar-after open 1956.442 (exact match).

### GAP-139
LAST_BAR_BEFORE_GAP: open=2020-09-15T20:45:00Z, close(implied)=2020-09-15T20:59:59Z, close_price=1954.198
FIRST_BAR_AFTER_GAP: open=2020-09-15T22:00:00Z, open_price=1954.198
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1954.198 == first-bar-after open 1954.198 (exact match).

### GAP-140
LAST_BAR_BEFORE_GAP: open=2020-09-16T20:45:00Z, close(implied)=2020-09-16T20:59:59Z, close_price=1959.59
FIRST_BAR_AFTER_GAP: open=2020-09-16T22:00:00Z, open_price=1959.59
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1959.59 == first-bar-after open 1959.59 (exact match).

### GAP-141
LAST_BAR_BEFORE_GAP: open=2020-09-17T20:45:00Z, close(implied)=2020-09-17T20:59:59Z, close_price=1944.276
FIRST_BAR_AFTER_GAP: open=2020-09-17T22:00:00Z, open_price=1944.276
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1944.276 == first-bar-after open 1944.276 (exact match).

### GAP-142
LAST_BAR_BEFORE_GAP: open=2020-09-18T20:45:00Z, close(implied)=2020-09-18T20:59:59Z, close_price=1950.506
FIRST_BAR_AFTER_GAP: open=2020-09-20T21:00:00Z, open_price=1950.506
Duration: 49.25h (2020-09-18 21:00:00 UTC Friday close -> 2020-09-20 21:00:00 UTC Sunday reopen),
standard weekend gap.
Zero-price-gap verified: last close 1950.506 == first-bar-after open 1950.506 (exact match).

### GAP-143
LAST_BAR_BEFORE_GAP: open=2020-09-21T20:45:00Z, close(implied)=2020-09-21T20:59:59Z, close_price=1912.674
FIRST_BAR_AFTER_GAP: open=2020-09-21T22:00:00Z, open_price=1912.674
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1912.674 == first-bar-after open 1912.674 (exact match).

### GAP-144
LAST_BAR_BEFORE_GAP: open=2020-09-22T20:45:00Z, close(implied)=2020-09-22T20:59:59Z, close_price=1900.038
FIRST_BAR_AFTER_GAP: open=2020-09-22T22:00:00Z, open_price=1900.038
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1900.038 == first-bar-after open 1900.038 (exact match).

### GAP-145
LAST_BAR_BEFORE_GAP: open=2020-09-23T20:45:00Z, close(implied)=2020-09-23T20:59:59Z, close_price=1863.45
FIRST_BAR_AFTER_GAP: open=2020-09-23T22:00:00Z, open_price=1863.45
Duration: 75min (21:00:00-22:00:00 UTC), standard daily rollover.
Zero-price-gap verified: last close 1863.45 == first-bar-after open 1863.45 (exact match).

### GAP-146
TYPE: Standard daily rollover (75min)
SPAN: 2020-09-24T20:59:59Z (last close 1867.818) -> 2020-09-24T22:00:00Z (first open 1867.818)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-147
TYPE: Standard weekend gap (49.25h)
SPAN: 2020-09-25T20:59:59Z (last close 1861.62) -> 2020-09-27T22:00:00Z (first open 1861.62)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 49.25h.

### GAP-148
TYPE: Standard daily rollover (75min)
SPAN: 2020-09-28T20:59:59Z (last close 1881.414) -> 2020-09-28T22:00:00Z (first open 1881.414)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-149
TYPE: Standard daily rollover (75min)
SPAN: 2020-09-29T20:59:59Z (last close 1897.205) -> 2020-09-29T22:00:00Z (first open 1897.205)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-150
TYPE: Standard daily rollover (75min)
SPAN: 2020-09-30T20:59:59Z (last close 1885.5) -> 2020-09-30T22:00:00Z (first open 1885.5)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-151 [Q4 2020, first Q4 gap]
TYPE: Standard daily rollover (75min)
SPAN: 2020-10-01T20:59:59Z (last close 1906.12, Q4 bar 84) -> 2020-10-01T22:00:00Z (first open
1906.12, Q4 bar 85)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-152 [Q4 2020, first Q4 weekend gap]
TYPE: Standard weekend gap (49.25h)
SPAN: 2020-10-02T20:59:59Z (last close 1899.168, Q4 bar 176, Friday) -> 2020-10-04T22:00:00Z (first
open 1899.168, Q4 bar 177, Sunday)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 49.25h.

### GAP-153 [Q4 2020]
TYPE: Standard daily rollover (75min)
SPAN: 2020-10-05T20:59:59Z (last close 1913.445, Q4 bar 268, Monday) -> 2020-10-05T22:00:00Z (first
open 1913.445, Q4 bar 269)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-154 [Q4 2020]
TYPE: Standard daily rollover (75min)
SPAN: 2020-10-06T20:59:59Z (last close 1878.177, Q4 bar 360, Tuesday, immediately following the
bars-352-360 major-volume decline) -> 2020-10-06T22:00:00Z (first open 1878.177, Q4 bar 361)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-155 [Q4 2020, CSV_CAUSAL_REPLAY_ADAPTER_V1 transport]
TYPE: Standard daily rollover (75min)
SPAN: 2020-10-07T20:59:59Z (last close 1887.592, Q4 bar 452, Wednesday, immediately following the
day's NY session, no S5 setup) -> 2020-10-07T22:00:00Z (first open 1887.592, Q4 bar 453)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min. Detected
mechanically by the CSV adapter's own gap classifier (`sealed_reader.classify_gap`, reused verbatim
from `live_signal_source`), matching every prior GAP-1xx entry's detection method.

### GAP-156 [Q4 2020, CSV_CAUSAL_REPLAY_ADAPTER_V1 transport]
TYPE: Standard daily rollover (75min)
SPAN: 2020-10-08T20:44:59Z (last close 1893.608, Q4 bar 544, Thursday) -> 2020-10-08T22:00:00Z
(first open 1893.608, Q4 bar 545)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 75min.

### GAP-157 [Q4 2020, CSV_CAUSAL_REPLAY_ADAPTER_V1 transport]
TYPE: Standard weekend (49.25h)
SPAN: 2020-10-09T20:44:59Z (last close 1930.521, Q4 bar 636, Friday -- inside the open bar-608 S5
trade's holding period) -> 2020-10-11T22:00:00Z (first open 1930.521, Q4 bar 637, Sunday)
VERIFICATION: exact last-close == first-open match (zero-price-gap). Duration 49.25h, matching the
established weekend-gap duration (GAP-152). No trade-management action occurs across a weekend gap
under the frozen S5/MGMT-004 protocols (stop/target/max-hold are evaluated bar-by-bar as bars are
revealed, not on wall-clock time) -- the bar-608 trade's max-hold count is in M15 bars, not elapsed
calendar time, so this gap does not shorten or extend its effective holding window.
