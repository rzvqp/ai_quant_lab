# ALPHA PARALLEL INSTANCE #2 — SESSION STATE (last updated 2026-07-25 — **OFFICIALLY CLOSED**)

> **STATUS: CLOSED.** This instance was officially closed by CEO instruction on 2026-07-25. See
> the "OFFICIAL SESSION CLOSURE" entry at the end of this file for the final summary. No further
> replay_step calls, checkpoints, Discovery Candidates, or Addenda will be added under this
> instance unless the CEO explicitly reopens it.

## Identity

This is **Alpha Discovery — Parallel Instance #2**, spun up by CEO directive 2026-07-24 to
accelerate Discovery by researching a separate historical period concurrently with the primary
Alpha instance. Same role, same methodology, same standards — a second worker, not a different
project.

**ID namespace**: this instance's Discovery Candidates use prefix **AP2-DC-XXXX** (AP2-DC-0001,
AP2-DC-0002, ...). These are LOCAL Alpha Parallel Instance #2 IDs and are NOT official lab IDs.
Official `DC-XXXX` IDs are assigned later, during the reconciliation stage. (CEO decision,
2026-07-24; supersedes the earlier `DC2-XXXX` draft naming.)

## Scope boundary

- **Period**: exclusively **2024-08-01 -> 2025-08-01**. Do not research outside this window.
- **Workspace isolation**: this instance reads/writes ONLY files under
  `ai_quant_lab/alpha_instance_2/`. It never writes to the primary instance's
  `research_log/`, `discovery_candidates/`, or any other official Alpha artifact.
- **TradingView tab isolation**: this instance uses ONLY its own dedicated TradingView
  window/tab, once unambiguously identified. It never interacts with any other open
  TradingView tab or window.

## Environment (confirmed 2026-07-24)

Three-level isolation from Alpha #1, CEO-validated:
- **MCP**: `tradingview2` (distinct server process, `TV_CDP_PORT=9223`; primary Alpha uses `tradingview` / port 9222, never touched by this instance)
- **Browser/process**: Microsoft Edge, dedicated profile at `ai_quant_lab/alpha_instance_2/browser_profile/` (separate from personal profile and from TradingView Desktop entirely)
- **TradingView layout**: dedicated layout `QPo6ZNx9` ("ALPHA2_DEDICATED_2024-2025"), created via "Make copy of chart layout" from the account's `d6IJPgKW` ("GRAFIC AI") layout, which belongs to Alpha #1's official session and is never written to by this instance. Confirmed via direct CDP target inspection: `target_id 197DE80D9F24C486E5C8C9F4BD313F6F`.

**Known technical debt (CEO-registered, not to be fixed this session):** `src/core/tab.js` hardcodes CDP port 9222 independent of `TV_CDP_PORT`, making `tab_list`/`tab_switch`/`tab_close`/`tab_new` unreliable across the two MCP instances. **These four tools are NOT used by this instance for the remainder of the session.** All other tools (`chart_get_state`, `data_get_*`, `replay_*`, `ui_*`, etc.) go through `connection.js` and are correctly isolated.

## Replay position

Started 2026-07-24. `replay_start` at `2024-08-01` → chart positioned at 2024-07-31 23:59:59 UTC
(session boundary immediately preceding 2024-08-01), symbol `OANDA:XAUUSD`/`FUSIONMARKETS:XAUUSD`
(broker-feed label toggles between these for the same instrument; not a chart-identity change),
resolution M15. OHLCV sanity-checked: ~2400-2450 range, consistent with real XAUUSD pricing.

## KNOWN HAZARD (2026-07-24): timeframe switching during active replay

Attempting `chart_set_timeframe`/clicking a timeframe button (e.g. "1m") **while replay is
active** triggered TradingView's "Continue your last replay?" dialog and silently substituted a
**different, wrong replay checkpoint** (jumped to 2025-10-23, prices ~4090-4120 -- matching the
primary Alpha instance's own known holdout cutoff). The chart *layout* stayed correctly isolated
throughout (`QPo6ZNx9` / "ALPHA2_DEDICATED_2024-2025", verified via `target_id`) -- only the
*replay position* moved, suggesting TradingView caches "last replay position" per-symbol at the
account level, not strictly per chart layout. `replay_start` then entered a stuck loop (repeated
`DATA_UNAVAILABLE`, replay fully stopped, chart fell back to live data) that the tool alone could
not recover from.

**Recovery that worked**: click the "Bar replay" toolbar button -> "Start new" on the resulting
dialog -> use the "Select date" control's date picker directly (type the date, click "Select")
rather than relying on the `replay_start` tool's automated seek. This reliably re-entered replay
at the correct date.

**Rule going forward**: do not change timeframe while replay is active this session. M1 data also
appears unavailable via replay this far back for this feed ("Data point unavailable" toast) --
M5/M1 drill-down may not be possible at all for early parts of this period. Treat this as an open
constraint: if a future event seems to genuinely require finer-than-M15 confirmation, pause and
flag it rather than risk another timeframe-switch attempt.

## METHODOLOGY (mirrors primary Alpha instance, CEO directive 2026-07-22/23 — unchanged)

Behave like a professional trader with 20+ years of experience observing the market in real
time. The goal is not to find trades, make predictions, or prove that every candle was analyzed.
The goal is to observe exactly as a highly experienced trader would.

- Primary working timeframe: **M15** (switch freely to 1H/5M/1M/4H for context or investigation;
  4H context maintained permanently).
- Advance naturally through Replay WITHOUT documenting every candle. If the market is ordinary,
  simply continue observing, in silence.
- Drop to 5M then 1M ONLY on an event that merits investigation: behavior change, unusual
  impulse, absorption, prolonged compression, unexpected expansion, a significant reaction at a
  relevant zone, or any other phenomenon that would catch an experienced trader's attention.
- During investigation, ask: What is actually happening? Is this ordinary or unusual? Have I seen
  this pattern before? Is it worth tracking going forward?
- After investigation, only two possible outcomes:
  1. The phenomenon justifies research -> create a new Discovery Candidate (`AP2-DC-XXXX`), document it.
  2. It doesn't justify a DC -> it is not lost -> log it in `OBSERVATION_REGISTRY_ALPHA2.md` as a raw
     observation for future comparison.
- Write ONLY when: a relevant event occurs / an investigation concludes / a DC is created / an
  entry is added to the Observation Registry / a session checkpoint is saved. Otherwise, complete
  silence — no long narration during pure observation.

### v2 pre-investigation filter (CEO directive 2026-07-23, unchanged)

Before any drop to M5/M1, answer:
1. Is this phenomenon genuinely different from normal variation?
2. Does it resemble something already documented in Discovery Candidates or the Observation
   Registry?
3. Is there sufficient reason to believe it could produce new information?

- NO -> continue observing without investigating.
- NOT SURE -> watch 1-2 more M15 candles before deciding.
- YES -> only then drop to M5/M1.

Accumulated memory (this instance's own AP2-DC set + Observation Registry + journal) is the FIRST
filter. Do not automatically investigate every large impulse, high volume bar, 00:00 UTC, 12:30
UTC, London open, or NY open once they've been documented here — investigate again only if
materially different from already-documented instances.

## Loop cadence

Per CEO directive 2026-07-24: after each checkpoint, save state and schedule the next iteration
at ~60 seconds, continuing indefinitely (no generic 25-30 minute pause).

## Journal of events

- **2024-08-01 00:00-01:45 UTC**: quiet Asia open, then a two-candle expansion (01:00-01:15,
  vol 7893/6223) that fully reverses over the next four candles on sustained (not fading) volume
  -> Observation Registry entry.
- **2024-08-01 12:30-16:15 UTC**: sustained ~3.5hr high-volatility, two-way regime starting
  sharply at 12:30 UTC -> Observation Registry entry.
- **2024-08-02 01:00-01:45 UTC**: sharp decline swept then reclaimed, extending past the
  pre-decline level within ~1hr -> Observation Registry entry.
- **2024-08-02 12:30-17:15 UTC**: large NFP-timed (first Friday) breakout (22pt, vol 12627) fully
  fails and reverses into a much larger decline (31.5pt candle, vol 12423) undershooting well past
  the pre-breakout level, then stabilizes net-lower -> **AP2-DC-0001 FROZEN** (largest/most
  sustained event observed so far; ~5hrs of 2-4x baseline volume throughout).
- CEO removed the 60s inter-iteration pause (2026-07-24); loop now processes many candles
  continuously per turn, checkpointing (and pausing to report) only at DC/Addendum/methodological-
  issue/period-end, per the CHECKPOINTS rule. `ScheduleWakeup`'s 60s minimum is a hard tool floor,
  not a deliberate pause.
- **2024-08-05 00:00-03:00 UTC**: second instance of the sharp-decline-swept-reclaimed-extends-
  past-origin shape (larger/multi-leg version of the 08-02 01:00 entry) -> Observation Registry
  entry, explicitly cross-referenced, not a new DC (repeat of an existing shape).
- **2024-08-05 12:15-20:45 UTC**: this then extended into a sustained ~8.5hr continuous decline
  (2420 -> low 2364.2 -> settling ~2400-2402) with volume elevated throughout rather than spiking-
  then-fading -- a different category (sustained trend vs. bounded event) -> Observation Registry
  entry. Cumulative decline from the 08-01 Friday NFP peak (~2477) to this low: ~110 points across
  multiple sessions.
- By 2024-08-06 ~00:00 UTC the decline has stabilized: consolidating 2405-2412, volume back to a
  normal 1191-4848 baseline. Daily-rollover gap (~76min) observed again, consistent with prior
  instances, not logged separately.
- Running total this session: 1 Discovery Candidate (AP2-DC-0001), 5 Observation Registry entries.
- **2024-08-06 00:00-19:50 UTC**: the sustained decline continued in fits and starts (further legs
  down to ~2382 with elevated volume 6000-9968, interspersed with quieter consolidation stretches
  2401-2418 and 2382-2390) -- all treated as continuation of the same multi-session decline already
  logged, not separate entries. Daily-rollover gap observed again (consistent, not logged). By
  19:50 UTC, consolidating quietly around 2384-2390.
- **2024-08-06 20:00 -> 2024-08-07 14:15 UTC**: the multi-day decline found equilibrium and market
  settled into a genuinely quiet consolidation phase, roughly 2380-2407, volume back to ordinary
  levels (1070-7467, no outliers). No new phenomena -- pure quiet observation across ~18 hours plus
  another daily-rollover gap (consistent, not logged). This is the first genuinely quiet multi-hour
  stretch since the 08-01 NFP breakout kicked off the active period.
- **2024-08-07 14:15 -> 2024-08-08 14:15 UTC**: quiet continued -- a gradual, smooth partial
  retracement of the week's decline (2385 -> ~2427 over roughly 24hrs, no single standout
  anomalous candle, ordinary volume throughout) followed by tight consolidation (2416-2428, volume
  449-5154). No new phenomena; treated as ordinary price action/retracement, not logged separately.
  Daily-rollover gap observed again (consistent). Isolation re-verified by CEO this checkpoint;
  reading Alpha #1 artifacts is now fully prohibited (previously done only for initial convention
  reference) -- no further reads planned or needed.
- **2024-08-08 14:15 -> 2024-08-09 05:15 UTC**: quiet, ordinary consolidation (2416-2432), except a
  third instance of the sweep-reclaim-extend family (~04:30 UTC, smaller/~11pt) -> brief
  cross-reference note added to the existing registry entry (not a new entry, not a DC -- repeat
  confirmation of an established shape, three instances now across different session contexts).
- **2024-08-09 05:15 UTC -> 2024-08-11 22:15 UTC (weekend)**: quiet, ordinary consolidation through
  Friday close (2427-2437), normal weekend skip, ordinary small-gap Sunday reopen. Nothing logged.
- **2024-08-11 22:15 -> 2024-08-12 16:15 UTC**: continued genuinely quiet, ordinary grind
  (2424-2445), volumes 803-4112 throughout, no outliers. This remains the calmest multi-day
  stretch since the 08-01 NFP breakout kicked off the active period.
- **2024-08-12 16:15 -> 2024-08-13 08:15 UTC**: smooth, sustained rally (2444 -> 2476, no single
  standout candle, ordinary trending price action) followed by an ordinary pullback (2476 -> 2462).
  No new phenomena; daily-rollover gap observed again (consistent). Market has now fully recovered
  from the 08-05/06 decline and made a new local high for this replay period (2476).
- **2024-08-13 08:15 -> 16:15 UTC**: continued genuinely quiet, tight consolidation (2458-2465),
  ordinary volume throughout. No new phenomena.
- **2024-08-13 16:15 -> 2024-08-14 00:15 UTC**: ordinary continued grind higher (2460 -> new local
  high 2475.56 -> settling ~2467-2470), one moderate volume bump (8554) that resolved without
  reversal -- consistent with the week's established grind pattern, not logged separately.
- **2024-08-14 00:15 -> 16:15 UTC**: continued genuinely quiet, very tight consolidation
  (2462-2472), low volume throughout (418-5352). No new phenomena. Daily-rollover gap observed
  again (consistent).
- **2024-08-14 16:15 -> 2024-08-15 00:15 UTC**: ordinary chop/consolidation (2455-2478), moderate
  volume, no outliers. No new phenomena.
- **2024-08-15 ~08:30-10:15 UTC**: a marginal-new-high wick (2479.82) fails within the same candle
  and leads into a sustained ~38pt decline (settling 2438-2445), volume elevated throughout
  (5928-9468) -> a SECOND instance of the AP2-DC-0001 mechanism, this time with no identified
  calendar catalyst -> filed as **AP2-ADD-0001** (Addendum A to AP2-DC-0001): strengthens the core
  mechanism, weakens the NFP-timing-specific framing.
- **2024-08-15 10:15 -> 2024-08-16 00:15 UTC**: quiet, ordinary consolidation (2440-2454), low
  volume. Daily-rollover gap observed again (consistent). No new phenomena.
- **2024-08-16 00:15 -> 08:15 UTC**: quiet, ordinary consolidation (2448-2458), ordinary volume.
  No new phenomena.
- **2024-08-15 12:15-14:15 UTC (revisited later in replay order)**: third instance of the
  AP2-DC-0001 mechanism, this time at 12:30 UTC Thursday (jobless-claims timing, not NFP) ->
  **AP2-ADD-0002** (Addendum B): core mechanism confidence now High (3 consistent instances, 0
  contradicting); calendar link reframed as "12:30 UTC US data slot" rather than NFP-specific.
- **2024-08-16 08:15-16:15 UTC**: otherwise quiet aside from the event above; consolidating
  2454-2470 before/after.
- **2024-08-16 16:15 -> 2024-08-17 00:15 UTC**: very quiet, tight consolidation (2453-2461), low
  volume throughout. Daily-rollover gap observed again (consistent). No new phenomena.
- **2024-08-17 00:15 -> 08:15 UTC**: quiet, ordinary consolidation (2450-2460), ordinary volume.
  No new phenomena.
- **2024-08-16 12:30-15:15 UTC**: a FOURTH 12:30-UTC-clustered volatility event, but this one
  HOLDS and extends to a fresh multi-week high (2500.09), contrasting with the three prior failed
  instances -> new Observation Registry entry (not a DC, not an addendum -- a contrasting single
  instance, distinct outcome at the same recurring time slot). Date verified via `date -d @epoch`
  at write time (correct).
- **METHODOLOGICAL NOTE (2026-07-24)**: discovered my own "current replay position" checkpoint
  labels in this file had drifted ~1 calendar day out of sync with the actual epoch timestamps
  over several recent checkpoints (labels said 08-16/08-17 when the epoch values were actually
  08-15/08-16) -- caused by estimating elapsed time from batch sizes instead of verifying each
  checkpoint. The underlying epoch values recorded in the journal, and every date explicitly
  verified via `date -d @epoch` before writing to the Observation Registry or Discovery
  Candidates/Addenda, remain correct -- this was a labeling drift in my own running commentary
  only, not a data-integrity issue. Corrected now; going forward, every checkpoint label in this
  file will be verified via `date -d @epoch` rather than estimated.
- **2024-08-16 15:30 UTC -> 2024-08-18 23:15 UTC (verified)**: the 08-16 12:30 UTC breakout
  continued to hold and extend through Friday close (new high ~2509.75), ordinary weekend gap
  (verified: Fri 20:59 UTC -> Sun 22:15 UTC), then consolidating 2502-2510 on Sunday reopen --
  confirms the contrast-case entry (breakout holding, not a fluke), no new entry needed (same
  event continuing).
- **2024-08-18 23:15 -> 2024-08-19 06:00 UTC (verified)**: ordinary consolidation holding at the
  elevated level (2497-2507), one mild volume bump (8502) resolving without drama. Continues to
  confirm the breakout is genuinely holding, not fading. No new phenomena.
- **2024-08-19 06:00 -> 12:45 UTC (verified)**: ordinary mild pullback (2506 -> 2491), moderate
  volume, no outliers. Still well above the pre-breakout origin (~2453). No new phenomena.
- **2024-08-19 12:45 -> 19:15 UTC (verified)**: ordinary grind (2489 -> 2506), moderate volume, no
  outliers. Consolidation continuing to hold the elevated level.
- **2024-08-19 19:15 -> 2024-08-20 02:45 UTC (verified)**: daily-rollover gap observed again
  (consistent), otherwise calm consolidation (2498-2508), ordinary volume. No new phenomena.
- **2024-08-20 02:45 -> 09:15 UTC (verified)**: continuation of the sustained rally (already
  logged as a contrast case) to fresh highs (2524.48), moderate-elevated volume, no reversal.
  Ordinary continuation, not a new entry.
- **2024-08-20 09:15 -> 17:30 UTC (verified)**: rally continued to a new peak (2531.67), then its
  first real pullback (~23pt, vol spike to 8733), stabilizing at 2505-2510 -- a normal pullback
  within the ongoing uptrend, NOT a full reversal (still far above the ~2453 pre-rally origin, and
  not matching the AP2-DC-0001 failure pattern). Not logged separately.
- **2024-08-20 17:15 -> 2024-08-21 00:45 UTC (verified)**: calm, tight consolidation (2509-2516),
  ordinary low volume, daily-rollover gap observed again (consistent). Continues to hold the
  elevated level. No new phenomena.
- **2024-08-21 00:45 -> 07:15 UTC (verified)**: ordinary consolidation (2511-2520), ordinary
  volume, holding the elevated level. No new phenomena. Running total this session: 1 Discovery
  Candidate (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 6 Observation Registry entries.
- Current replay position (verified via `date -d @epoch`): 2024-08-21 ~07:15 UTC (epoch
  1724224499), M15, no autoplay used.
- **2026-07-24, filesystem isolation**: CEO required explicit `_ALPHA2`-suffixed filenames (this
  instance's files previously had the SAME basenames as Alpha #1's official artifacts, just in a
  different directory -- a real collision-of-appearance risk). Renamed: `SESSION_STATE.md` ->
  `SESSION_STATE_ALPHA2.md`, `OBSERVATION_REGISTRY.md` -> `OBSERVATION_REGISTRY_ALPHA2.md`,
  `DISCOVERY_CANDIDATE_INDEX.md` -> `DISCOVERY_INDEX_ALPHA2.md`, `HANDOFF_LOG.md` ->
  `HANDOFF_LOG_ALPHA2.md`, `DISCOVERY_CANDIDATE_TEMPLATE.md` ->
  `DISCOVERY_CANDIDATE_TEMPLATE_ALPHA2.md`; added `Addenda/ADDENDUM_INDEX_ALPHA2.md`. In fixing an
  internal cross-reference inside the already-FROZEN `AP2-DC-0001_v1.md`, directly edited the
  frozen body -- caught this as a violation of the document's own immutability rule and of its
  recorded content_hash. Established a canonicalization rule instead (blank all `sha256:<hex>`
  occurrences to `sha256:PENDING` before hashing, so the hash doesn't reference itself
  circularly), recomputed the correct hash (`8192503d3988...`), and logged the correction as a new
  append-only `HANDOFF_LOG_ALPHA2.md` line rather than silently overwriting the original entry --
  no observation/evidence/confidence text in AP2-DC-0001 changed, only the one filename reference
  and the hash bookkeeping. Lesson: never edit a frozen DC body directly again, even for trivial
  reference fixes -- use an addendum, or leave stale references alone.
- **2024-08-21 07:30 -> 13:30 UTC (verified)**: continued quiet consolidation (2498-2517, ordinary
  volume 1099-5455) holding the elevated rally level, then a step-change decline at 13:30 UTC
  (O2506.5 C2498.71, vol 8516, ~2x baseline).
- **2024-08-21 13:45 -> 16:00 UTC (verified)**: the 13:30 decline extended into a genuine two-way
  chop with sustained elevated volume (7357-12201 across ~4-5 candles), sweeping down to a session
  low of 2494.02/2494.47 and bouncing as high as 2506.71 -- resembles the already-documented
  "sustained multi-hour two-way regime" shape (2024-08-01 12:30 entry), not the sweep-reclaim-
  extend family (no clean extension past the ~2515-2517 pre-decline origin). Volume then faded
  (9881 -> 4934) as price recovered/stabilized into the 2501-2511 band. Applied the 3-question
  filter: different from normal variation (yes, 2-4x volume) but resembles an already-documented
  shape and did not appear to threaten a genuinely new mechanism -> not logged as a new Registry
  entry, tracked here as a continuation/partial-pullback of the ongoing rally thread (started
  2024-08-16 12:30 UTC) rather than a DC-0001-style failure. The rally is basing, not reversing.
- **2024-08-21 16:15 -> 2024-08-22 00:45 UTC (verified)**: quiet recovery/consolidation (2506-2519),
  ordinary volume (433-5143) after the chop above, daily-rollover gap observed again (consistent,
  ~76min). No new phenomena. Rally thread continues to hold well above its ~2453 pre-rally origin.
- Current replay position (verified via `date -d @epoch`): 2024-08-22 ~00:45 UTC (epoch
  1724287499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 6 Observation Registry entries (unchanged
  this iteration).
- **2024-08-22 00:45 -> 11:30 UTC (verified)**: quiet, ordinary consolidation (2499-2514), ordinary
  volume throughout (1708-5384). No new phenomena.
- **2024-08-22 11:30-15:45 UTC (verified)**: the multi-day rally tracked since 2024-08-16 had its
  first real, non-reclaimed breakdown -- a gradual volume build (from ~11:30 UTC) accelerating into
  a sustained ~37pt decline (2508 -> low 2470.87, six candles of 7400-9700 volume, ~13:00-14:00 UTC)
  that did NOT reclaim, stabilizing instead at a new lower range (2477-2486) -> **new Observation
  Registry entry**. Resolves the open tracking question from the 08-16 entry: this is neither a
  DC-0001-style sharp failure nor a continued "holds" outcome -- it resembles the already-
  documented sustained-multi-hour-decline family (2024-08-05 entry), a different instance, not a
  new DC.
- Current replay position (verified via `date -d @epoch`): 2024-08-22 ~16:15 UTC (epoch
  1724347799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 7 Observation Registry entries.
- **2024-08-22 16:15 -> 2024-08-23 09:45 UTC (verified)**: quiet consolidation/gradual grind
  (2478-2501), ordinary volume, daily-rollover gap observed again (consistent, ~76min). No new
  phenomena.
- **2024-08-23 14:00-17:15 UTC (verified, Friday)**: largest single-candle volume seen this
  replay (12999) at a sharp 14:00 UTC breakout (19.6pt range), developing genuine two-way
  structure over ~3hrs with sustained heavy volume (down to 6000s), ultimately holding -> **new
  Observation Registry entry**. Notably RECLAIMS most of the 2024-08-22 breakdown logged
  previously (settles 2509-2513, back above the pre-08-22-breakdown level) -- that breakdown was a
  ~1-day mid-trend pullback, not a trend end. New specific time slot (14:00 UTC Fri) vs the
  already-documented 12:30 UTC US data slot. Not a new DC/addendum -- distinct instance logged for
  future comparison.
- Current replay position (verified via `date -d @epoch`): 2024-08-23 ~17:15 UTC (epoch
  1724437799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries.
- **2024-08-23 17:15 -> 20:59 UTC (verified)**: quiet, ordinary consolidation (2509-2512), low
  volume. Ordinary weekend skip observed (Fri 20:58:59 -> Sun 22:14:59 UTC, consistent with prior
  instances). No new phenomena.
- **2024-08-25 22:15 UTC -> 2024-08-26 16:59 UTC (verified, Sun reopen through Monday)**: ordinary
  Sunday reopen consolidation (2511-2515), then a smooth continued grind higher (2509 -> new local
  high 2525.78, still below the 08-20 peak of 2531.67), moderate volume throughout with one mild
  midday pullback (~13:45-14:15 UTC, 2526 -> 2510.62, volume 5000-8300) that recovered without
  drama -- ordinary intraday variability, not logged separately. No new phenomena. Rally thread
  (tracked since 08-16, reclaimed 08-23) continues to hold and extend.
- Current replay position (verified via `date -d @epoch`): 2024-08-26 ~17:00 UTC (epoch
  1724691599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-26 17:15 UTC -> 2024-08-27 08:15 UTC (verified)**: quiet, tight consolidation/mild chop
  (2504-2523), ordinary low-moderate volume throughout (338-5326), daily-rollover gap observed
  again (consistent, ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-08-27 ~08:15 UTC (epoch
  1724746499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-27 08:30 -> 23:30 UTC (verified)**: ordinary continued grind higher (2503 -> new local
  high ~2529, still below the 08-20 peak of 2531.67), one mild elevated-volume stretch ~13:00-14:00
  UTC (5000-8500, roughly 1.5-2x baseline, brief pullback to 2503.59 then continuation to new
  highs) -- borderline but resolved as ordinary trend continuation, not logged separately. Daily-
  rollover gap observed again (consistent, ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-08-27 ~23:30 UTC (epoch
  1724801399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-27 23:45 -> 2024-08-28 13:30 UTC (verified)**: a gradual, low-intensity multi-hour
  pullback (2525 -> low ~2493.64 around 09:45-10:00 UTC, ~31pt over ~18hrs) with only moderate
  volume throughout (2000-5700, well below the 8000-13000 seen in the established sustained-
  decline family), followed by a recovery back to ~2510 by 13:15 UTC. Too gradual/low-intensity to
  match the documented sustained-decline shape -- treated as an ordinary ongoing-rally pullback and
  recovery, not logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-08-28 ~13:30 UTC (epoch
  1724851799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-28 13:30 -> 2024-08-29 04:15 UTC (verified)**: continued gradual, moderate-volume
  decline (2510 -> low ~2496.43 around 15:15 UTC, sustained 5000-7000 volume for the first ~1.5hrs)
  -- a continuation of the same low-intensity pullback already noted last checkpoint, still below
  the sustained-decline family's intensity threshold -- then quiet consolidation/mild grind back up
  (2503-2518, low volume 550-4083) through the rest of the day and daily-rollover gap (consistent).
  No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-08-29 ~04:15 UTC (epoch
  1724904899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-29 04:30 -> 11:15 UTC (verified)**: quiet, tight consolidation (2513-2524), moderate
  ordinary volume. No new phenomena.
- **2024-08-29 12:30 UTC (verified, Thursday)**: a fourth instance of the sweep-reclaim-extend
  family (already in the registry, 3 prior instances) -- sharp decline at the established 12:30 UTC
  US data slot (O2516.08 L2504.71, vol 9727), reclaimed and extended well past the pre-decline
  level within ~90min -> **cross-reference note added to the existing registry entry** (not a new
  entry, not a DC). Notable: the 12:30 UTC slot has now produced both AP2-DC-0001-style failures
  AND sweep-reclaim-extend outcomes -- calendar timing alone doesn't determine the shape.
- Current replay position (verified via `date -d @epoch`): 2024-08-29 ~18:15 UTC (epoch
  1724955299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  count; 4th sweep-reclaim-extend instance cross-referenced into an existing entry).
- **2024-08-29 18:30 UTC -> 2024-08-30 02:15 UTC (verified)**: very quiet, tight consolidation
  (2514-2526), low volume throughout (258-3900). Daily-rollover gap observed again (consistent,
  ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-08-30 ~02:15 UTC (epoch
  1724984099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-08-30 02:30 -> 12:15 UTC (verified)**: quiet, ordinary grind (2512-2526), moderate
  volume, no outliers. No new phenomena.
- **2024-08-30 12:30-17:45 UTC (verified, Friday/month-end)**: a third instance of the sustained
  multi-hour-decline family (after 08-05 and 08-22) -- starting at the 12:30 UTC data slot with a
  moderate step-change (vol 7716, not a sharp breakout-failure), sustained elevated volume
  (4500-8400) over ~5.5hrs declining ~2524.83 -> low 2494.13, not reclaimed -> **cross-reference
  note added to the existing registry entry** (not a new entry, not a DC).
- Current replay position (verified via `date -d @epoch`): 2024-08-30 ~17:45 UTC (epoch
  1725039899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  count; 3rd sustained-decline instance cross-referenced into an existing entry).
- **2024-08-30 18:00 -> 20:59 UTC (verified)**: quiet stabilization after the 12:30 decline
  (2494-2505), ordinary low volume. Ordinary weekend skip observed (Fri 20:58:59 -> Sun 22:14:59
  UTC, consistent with prior instances). No new phenomena. **August 2024 now complete -- roughly
  one month into the authorized 2024-08-01 -> 2025-08-01 period.**
- **2024-09-01 22:15 UTC -> 2024-09-02 01:45 UTC (verified, Sun reopen through Monday)**: quiet,
  ordinary consolidation (2499-2505), low volume throughout. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-02 ~01:45 UTC (epoch
  1725240599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-02 01:45 -> 08:15 UTC (verified)**: quiet, ordinary consolidation/mild grind
  (2490-2504), ordinary volume throughout (1226-4951), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-02 ~08:15 UTC (epoch
  1725264899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-02 08:30 -> 15:00 UTC (verified, Monday/US Labor Day)**: quiet, tight consolidation
  (2497-2507), low-moderate volume throughout, 12:30 UTC passed without incident (no scheduled US
  data on a holiday). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-02 ~15:00 UTC (epoch
  1725289199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-02 15:15 -> 2024-09-03 01:15 UTC (verified)**: very quiet, low volume throughout
  (296-4877), tight range (2492-2502.5), a longer-than-usual gap (18:30-22:15 UTC, ~3h45min,
  likely US Labor Day holiday session effect) treated as a mechanical/calendar artifact like the
  daily-rollover gaps, not logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-03 ~01:15 UTC (epoch
  1725326099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-03 01:30 -> 08:00 UTC (verified)**: quiet, tight consolidation (2489-2502), moderate
  ordinary volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-03 ~08:00 UTC (epoch
  1725350399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-03 08:15-16:00 UTC (verified, Tuesday)**: two notable events -- (1) ~11:45-12:00 UTC a
  fifth instance of the sweep-reclaim-extend family (sweep to 2487.18, rally to 2502.26, vol 8214)
  -> cross-reference note added; (2) ~13:30-15:30 UTC a fourth instance of the sustained-decline
  family (2493 -> low 2473.47, sustained vol 7300-11369, partial recovery to ~2489), notably NOT at
  the 12:30 UTC slot -- confirms the family is general-shape, not calendar-specific -> cross-
  reference note added. Neither logged as a new DC/addendum.
- Current replay position (verified via `date -d @epoch`): 2024-09-03 ~16:00 UTC (epoch
  1725379199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  count; 2 more cross-referenced instances added to existing entries).
- **2024-09-03 16:15 -> 23:30 UTC (verified)**: quiet consolidation/recovery (2483-2494), moderate-
  low volume, daily-rollover gap observed again (consistent, ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-03 ~23:30 UTC (epoch
  1725406199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-03 23:45 -> 2024-09-04 12:15 UTC (verified)**: quiet overnight consolidation (2491-2497)
  followed by a gradual, low-to-moderate-volume roundtrip pullback (2493 -> low 2471.86 ~09:15 UTC
  -> recovery to ~2491 by 12:15 UTC), no single standout candle -- matches the already-noted
  low-intensity gradual pullback pattern, not logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-04 ~12:15 UTC (epoch
  1725452099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-04 14:00 UTC (verified, Wednesday)**: a second instance of the 14:00 UTC "sharp
  breakout, two-way, net holds" family (first seen 08-23) -- second-largest volume seen this
  replay (11272), extends to a fresh high (2500.28), settles into a stable range -> cross-reference
  note added to the existing entry (not a new DC). Suggests 14:00 UTC recurs as a scheduled-release
  time beyond Fridays.
- Current replay position (verified via `date -d @epoch`): 2024-09-04 ~18:30 UTC (epoch
  1725474599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  count; 1 more cross-referenced instance added).
- **2024-09-04 18:45 UTC -> 2024-09-05 01:45 UTC (verified)**: very quiet, tight consolidation
  (2491-2499), low volume throughout. Daily-rollover gap observed again (consistent, ~76min). No
  new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-05 ~01:45 UTC (epoch
  1725500699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 2 Addenda (AP2-ADD-0001, AP2-ADD-0002), 8 Observation Registry entries (unchanged
  this iteration).
- **2024-09-05 12:15-16:30 UTC (verified, Thursday)**: a fourth instance of the AP2-DC-0001
  mechanism -- marginal new high (2523.49 at 12:30 UTC) fails and reverses into a sustained,
  materially larger decline (peak volume 10095 at 14:00 UTC) to a low of 2503.97, settling
  2506-2510, below the pre-breakout baseline -> **AP2-ADD-0003 (Addendum C) FROZEN/SUBMITTED**.
  Third of four total AP2-DC-0001 instances now tied to the 12:30 UTC US data slot specifically;
  confidence remains High.
- Current replay position (verified via `date -d @epoch`): 2024-09-05 ~16:30 UTC (epoch
  1725553799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 3 Addenda (AP2-ADD-0001, AP2-ADD-0002, AP2-ADD-0003), 8 Observation Registry
  entries.
- **2024-09-05 16:45 -> 23:45 UTC (verified)**: quiet stabilization/tight consolidation
  (2508-2518), low volume throughout, daily-rollover gap observed again (consistent, ~76min). No
  new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-05 ~23:45 UTC (epoch
  1725579899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 3 Addenda (AP2-ADD-0001, AP2-ADD-0002, AP2-ADD-0003), 8 Observation Registry
  entries (unchanged this iteration).
- **2024-09-06 00:00-12:15 UTC (verified)**: quiet, tight consolidation (2513-2521), ordinary
  volume. No new phenomena.
- **2024-09-06 12:30-17:00 UTC (verified, genuine NFP Friday)**: the largest/richest instance yet
  of the AP2-DC-0001 mechanism -- 12:30 UTC breakout to 2529.21 (vol 12451, near-record), then a
  ~4.5hr multi-attempt whipsaw (THREE distinct failed reclaim attempts, peak volume 12640 -- the
  largest single-candle volume observed this replay) before declining to a final low of 2485.15,
  ~44pt below the peak and well below the pre-breakout baseline -> **AP2-ADD-0004 (Addendum D)
  FROZEN/SUBMITTED**. Fifth total instance; new "multi-attempt failed-reclaim" structural nuance
  noted for future comparison; confidence remains High.
- Current replay position (verified via `date -d @epoch`): 2024-09-06 ~18:15 UTC (epoch
  1725646499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries.
- **2024-09-06 18:30-20:59 UTC (verified)**: quiet stabilization after the NFP event (2493-2497),
  ordinary low volume. Ordinary weekend skip observed (Fri 20:58:59 -> Sun 22:14:59 UTC,
  consistent). No new phenomena.
- **2024-09-08 22:15 UTC -> 2024-09-09 01:15 UTC (verified, Sun reopen through Monday)**: quiet,
  ordinary consolidation (2494-2499), low-moderate volume, no outliers. No new phenomena. **First
  full week of September now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-09-09 ~01:15 UTC (epoch
  1725844499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-09 01:30 -> 08:30 UTC (verified)**: quiet consolidation with mild ordinary two-way
  chop (2485-2500), moderate volume, no standout single event exceeding threshold. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-09 ~08:30 UTC (epoch
  1725870599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-09 08:45-15:45 UTC (verified, Monday)**: ordinary mild grind (2490-2505), moderate
  volume, 12:30 UTC passed without incident (no scheduled release on a Monday). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-09 ~15:45 UTC (epoch
  1725896699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-09 16:00-24:00 UTC (verified)**: quiet, gradual grind (2499-2507), moderate-low
  volume, daily-rollover gap observed again (consistent, ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-10 ~00:00 UTC (epoch
  1725926399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-10 00:15-07:00 UTC (verified)**: quiet, tight consolidation (2501-2507), moderate
  volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-10 ~07:00 UTC (epoch
  1725951599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-10 07:15-15:30 UTC (verified, Tuesday)**: quiet consolidation, then a sixth instance of
  the sweep-reclaim-extend family at the 12:30 UTC slot (breakout to 2515.37, hard reversal to
  2500.9, reclaim back to 2513.91 by 15:15 UTC) -> cross-reference note added (not a new DC).
- Current replay position (verified via `date -d @epoch`): 2024-09-10 ~15:30 UTC (epoch
  1725982199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged count; 6th sweep-reclaim-extend instance cross-referenced).
- **2024-09-10 15:45-23:30 UTC (verified)**: quiet consolidation holding the reclaimed level
  (2512-2518), moderate-low volume, daily-rollover gap observed again (consistent, ~76min). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-10 ~23:30 UTC (epoch
  1726010999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-10 23:45 -> 2024-09-11 06:30 UTC (verified)**: ordinary continued mild grind higher
  (2514-2526), moderate volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-11 ~06:30 UTC (epoch
  1726036199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 8 Observation Registry entries
  (unchanged this iteration).
- **2024-09-11 06:45-12:15 UTC (verified)**: ordinary grind (2518-2529), moderate volume, no
  outliers. No new phenomena.
- **2024-09-11 12:30-16:15 UTC (verified, Wednesday, genuine US CPI release)**: a sharp DECLINE
  (not breakout) at 12:30 UTC (near-record volume 12727, second-largest seen this replay), ~3hrs
  sustained heavy two-way chop (2500.96-2514.95), then a gradual, partial reclaim to ~2513-2516 by
  16:15 UTC -> **new Observation Registry entry**. First instance where the 12:30 UTC slot starts
  with a decline rather than a breakout -- consistent with CPI being a distinct catalyst from
  NFP/jobless-claims; doesn't cleanly match any existing family.
- Current replay position (verified via `date -d @epoch`): 2024-09-11 ~16:15 UTC (epoch
  1726071299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 9 Observation Registry entries.
- **2024-09-11 16:30-24:00 UTC (verified)**: quiet, tight consolidation holding the post-CPI
  reclaim level (2509-2520), low-moderate volume, daily-rollover gap observed again (consistent,
  ~76min). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-12 ~00:00 UTC (epoch
  1726099199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 9 Observation Registry entries
  (unchanged this iteration).
- **2024-09-12 00:15-07:00 UTC (verified)**: quiet, ordinary consolidation/mild grind (2511-2522),
  moderate volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-12 ~07:00 UTC (epoch
  1726124399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 9 Observation Registry entries
  (unchanged this iteration).
- **2024-09-12 07:15-12:15 UTC (verified)**: quiet, ordinary consolidation (2513-2521), moderate
  volume, no outliers. No new phenomena.
- **2024-09-12 12:30-15:15 UTC (verified, Thursday, jobless-claims timing)**: a second 12:30 UTC
  breakout that HOLDS and extends dramatically (larger than 08-16) to a fresh all-time high for
  the replay period, 2555.17, with sustained volume (up to 8617) and no meaningful reversal ->
  **new Observation Registry entry**. Not a DC/addendum -- a contrasting "holds" case.
- Current replay position (verified via `date -d @epoch`): 2024-09-12 ~15:15 UTC (epoch
  1726154099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries.
- **2024-09-12 15:30-23:00 UTC (verified)**: the rally continues to hold and extend further to new
  highs (2560.11), ordinary volume, daily-rollover gap observed again (consistent, ~76min) --
  ongoing continuation of the already-logged 12:30 UTC "holds" entry, not a new phenomenon.
- Current replay position (verified via `date -d @epoch`): 2024-09-12 ~23:00 UTC (epoch
  1726181999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-12 23:15 -> 2024-09-13 05:45 UTC (verified)**: ordinary continued smooth grind higher
  (2557-2570), moderate volume, no outliers -- ongoing continuation of the rally. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-13 ~05:45 UTC (epoch
  1726206299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-13 06:00-12:45 UTC (verified)**: quiet, tight consolidation (2563-2573), moderate
  volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-13 ~12:45 UTC (epoch
  1726231499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-13 13:00-19:15 UTC (verified)**: ordinary continued grind higher (2568-2586),
  moderate-elevated volume, no single standout event -- ongoing continuation of the rally. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-13 ~19:15 UTC (epoch
  1726254899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-13 19:30-20:59 UTC (verified)**: quiet, ordinary consolidation (2577-2583), low
  volume. Ordinary weekend skip observed (Fri 20:58:59 -> Sun 22:14:59 UTC, consistent). No new
  phenomena. **Second full week of September now complete.**
- **2024-09-15 22:15 UTC -> 2024-09-16 02:45 UTC (verified, Sun reopen through Monday)**: quiet,
  ordinary consolidation holding the rally level (2577-2585), low volume, no outliers. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-16 ~02:45 UTC (epoch
  1726454699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-16 03:00-09:15 UTC (verified, Monday)**: quiet, ordinary consolidation (2579-2589),
  moderate volume, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-16 ~09:15 UTC (epoch
  1726478099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-16 09:30-15:45 UTC (verified)**: ordinary mild two-way chop (2575-2589), moderate
  volume with a brief bump around 12:30-14:00 UTC (up to 6507) that resolved without a standout
  reversal -- not exceeding threshold clearly. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-16 ~15:45 UTC (epoch
  1726501499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 4 Addenda (AP2-ADD-0001 through AP2-ADD-0004), 10 Observation Registry entries
  (unchanged this iteration).

## CEO REVIEW + CEO DECISION (2026-07-24)

Loop paused at the checkpoint above for a CEO-requested progress review (10-point report delivered,
covering candle count, calendar interval, zero M5/M1 investigations, DC/Addenda detail,
methodological difficulties, market learnings, and retrospective -- no artifacts modified during
the review). CEO then confirmed: **Research Audit #1 handed to Red Team, running independently;
this instance does not wait for its outcome.** Observation loop re-authorized to resume
immediately from this exact checkpoint (no re-analysis of the period already covered), methodology
unchanged and frozen until the CEO's post-audit decision, existing frozen artifacts (AP2-DC-0001,
Addenda A-D, closed checkpoints) untouched. Loop resumed.

- **2024-09-16 16:00-23:30 UTC (verified)**: ordinary quiet grind/consolidation (2577-2586) through
  the daily-rollover pause (~76min, mechanical artifact) into the new Asian session. No new
  phenomena.
- **2024-09-16 23:30 UTC -> 2024-09-17 04:45 UTC (verified, Tue)**: mild Asian-session pullback
  (2586 area -> 2561.71 area local low) and full V-shaped recovery back to ~2586, moderate volume
  (1500-3600), gradual, no acceleration or panic character. Considered against the pre-investigation
  filter (resembles the sweep-reclaim-extend family in shape) but resolved NU -- modest magnitude,
  no new structural nuance, not logged separately (quality over quantity per CEO audit-period
  guidance).
- **2024-09-17 04:45-12:15 UTC (verified)**: ordinary London-session two-way chop (2568-2587),
  volume in the normal London-session range (2700-3500), one moderate pullback (~09:00-11:00 UTC,
  -15pt) fully reclaimed by 11:45 UTC -- resolved NU, ordinary pullback/recovery, not a new
  sustained-decline instance. No new phenomena.
- **2024-09-17 12:30-16:15 UTC (verified, Tuesday -- NOT an NFP/jobless-claims day)**: sixth
  instance of the AP2-DC-0001 mechanism. Volume spike to 8489 at 12:30 UTC, sharp initial decline to
  2568.41, then a three-attempt failed-reclaim structure (marginal highs 2579.07, 2579.18, 2579.6,
  then a strong reclaim to 2581.11/2582.22 that genuinely broke the pre-episode baseline before
  failing just as hard), followed by a decisive breakdown to a final low of 2561.82 -- -20.4pt from
  the episode-high, ~3h45m duration, volume elevated (3300-8500) throughout, fading only in the
  final 1-2 candles. Filed as **Addendum E (AP2-ADD-0005)** against AP2-DC-0001: reinforces the
  multi-attempt failed-reclaim nuance from Addendum D, and is the first instance observed on a
  Tuesday with no Thursday/Friday-specific release framing -- further weakens any
  specific-release-type link, strengthens the general "12:30 UTC US data slot, any weekday" framing.
  Confidence in the core mechanism remains High (6 instances, 0 contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-09-17 ~16:15 UTC (epoch
  1726589699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 5 Addenda (AP2-ADD-0001 through AP2-ADD-0005), 10 Observation Registry entries.
- **2024-09-17 16:30 UTC -> 2024-09-18 00:30 UTC (verified)**: ordinary post-episode consolidation
  and recovery through the NY afternoon, an ordinary daily-rollover pause (~76min, mechanical
  artifact), and a quiet, flat new Asian session (range 2.87-3.21pt, volume 400-1900 throughout).
  No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-18 ~00:30 UTC (epoch
  1726619399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 5 Addenda (AP2-ADD-0001 through AP2-ADD-0005), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-18 00:45-06:15 UTC (verified)**: quiet Asian-session grind (2565-2577), one isolated
  volume spike (6988 at 01:00 UTC) with no directional follow-through -- resolved NU, not logged.
  One modest ordinary pullback (~6.65pt) mid-session, no acceleration. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-18 ~06:15 UTC (epoch
  1726640099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 5 Addenda (AP2-ADD-0001 through AP2-ADD-0005), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-18 06:15-10:15 UTC (verified)**: quiet, ordinary London-session grind (2566-2573),
  moderate volume (1700-3200), no outliers, no directional break. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-18 ~10:15 UTC (epoch
  1726654499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 5 Addenda (AP2-ADD-0001 through AP2-ADD-0005), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-18 (Wednesday) -- note**: this is a known FOMC rate-decision day (public macro
  calendar fact, not something inferred from the chart). Statement/press-conference typically
  falls ~18:00-18:30 UTC given September EDT offset. Watching carefully through the session;
  observations remain strictly chart-based, no external facts asserted about the decision itself
  until/unless price action shows it.
- **2024-09-18 10:15-13:30 UTC (verified)**: ordinary mild grind higher (2571-2578), moderate
  volume (2200-3800). No new phenomena.
- **2024-09-18 13:45-15:00 UTC (verified)**: moderate elevated-volume episode (peak 6685 at 13:45
  UTC), decline to 2568.11 then partial recovery, volume fading 5700->4200 over the episode.
  Magnitude (~5-6pt) and structure did not clearly match the AP2-DC-0001 mechanism or any other
  documented family -- resolved NU, not logged separately.
- **2024-09-18 15:15-16:45 UTC (verified)**: ordinary quiet consolidation (2568-2573), volume
  normalizing (1900-3600). No new phenomena. Approaching the anticipated FOMC window.
- Current replay position (verified via `date -d @epoch`): 2024-09-18 ~16:45 UTC (epoch
  1726677899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 5 Addenda (AP2-ADD-0001 through AP2-ADD-0005), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-18 16:45-17:45 UTC (verified)**: ordinary quiet consolidation (2567-2575), moderate
  volume. No new phenomena.
- **2024-09-18 18:00-20:45 UTC (verified, FOMC decision day)**: seventh instance of the
  AP2-DC-0001 mechanism, and the largest yet. Powerful breakout at 18:00 UTC (volume 11250),
  extending cleanly to a decisive new episode-high 2600.12 by 18:30 UTC, then a hard reversal
  within that same candle followed by an uninterrupted six-candle decline (no multi-attempt
  reclaim battle, unlike Addenda D/E) to a final low of 2546.89 by 20:00 UTC -- -53.2pt total,
  volume sustained at extraordinary levels (8219-11265) across 8 consecutive candles (2 full
  hours) before fading and stabilizing by 20:45 UTC. Filed as **Addendum F (AP2-ADD-0006)**
  against AP2-DC-0001: largest magnitude and most sustained extreme-volume instance to date; single
  clean top rather than multi-attempt structure, refining (not resolving) the open question from
  Addendum E about what determines internal structure; first instance tied to a policy-decision
  event (FOMC) rather than a scheduled data release. Confidence in the core mechanism remains High
  (7 instances, 0 contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-09-18 ~20:45 UTC (epoch
  1726692299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries.
- **2024-09-18 21:00 UTC -> 2024-09-19 02:30 UTC (verified, ordinary daily-rollover pause then
  new Asian session)**: quiet, ordinary post-FOMC stabilization and consolidation (2551-2562).
  Two isolated elevated-volume moments (one flat, no follow-through; one a mild -6.23pt dip that
  fully recovered) -- both resolved NU, not logged. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~02:30 UTC (epoch
  1726712999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 02:30-05:30 UTC (verified)**: quiet, ordinary Asian-session grind (2559-2569),
  moderate volume (1600-4400), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~05:30 UTC (epoch
  1726723799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 05:30-08:00 UTC (verified)**: ordinary steady rally continuing into London
  pre-open (2567-2585), moderate-elevated but steady volume (4200-5000), no spike/reversal
  character. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~08:00 UTC (epoch
  1726732799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 08:00-10:00 UTC (verified, London session)**: ordinary continued rally
  (2581-2595), moderate volume (2800-5400), no outliers, no directional break. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~10:00 UTC (epoch
  1726739999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 10:00-12:15 UTC (verified)**: ordinary mild grind (2584-2592), moderate volume.
  No new phenomena.
- **2024-09-19 12:30-15:45 UTC (verified, Thursday jobless-claims slot)**: sharp decline at 12:30
  UTC (volume 7643), multiple failed bounce/reclaim attempts through 14:00 UTC (bouncing to
  2582.54, 2581.33, 2578.27, each failing and making a fresh low, episode low 2569.87 at 13:45
  UTC), then a decisive reclaim from 14:15 UTC extending steadily back through the pre-episode
  baseline (2588.65) by 15:45 UTC (close 2589.13) as volume normalized (8496 -> 4489). This is a
  clean match for the already-documented sweep-reclaim-extend family (7th instance) -- no overshoot
  below the pre-episode level at final resolution, so it does not match the AP2-DC-0001 mechanism,
  and no new structural nuance versus the 6 prior sweep-reclaim-extend instances -- resolved
  ordinary, not logged separately (quality over quantity).
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~15:45 UTC (epoch
  1726760699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 15:45-18:00 UTC (verified)**: ordinary quiet consolidation (2587-2593), moderate
  volume declining to low (1700-4000) toward end of NY session. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~18:00 UTC (epoch
  1726768799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 18:00-22:30 UTC (verified)**: ordinary quiet grind through the NY afternoon, an
  ordinary daily-rollover pause (~76min, mechanical artifact), and an extremely quiet new Asian
  session (range 1.45pt, volume 380-850). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-19 ~22:30 UTC (epoch
  1726784999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-19 22:30 UTC -> 2024-09-20 00:30 UTC (verified, Thu->Fri)**: extremely quiet Asian
  session (range 0.85-1.32pt, volume 270-1300). No new phenomena. **Third full week of September
  now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~00:30 UTC (epoch
  1726792199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 00:30-02:30 UTC (verified, Friday -- not first-Friday-of-month, no NFP)**: quiet,
  ordinary Asian-session grind (2584-2590), moderate volume (1100-3900). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~02:30 UTC (epoch
  1726799399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 02:30-04:30 UTC (verified)**: ordinary mild grind (2589-2594), moderate volume
  (1100-3900). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~04:30 UTC (epoch
  1726806599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 04:30-06:30 UTC (verified)**: ordinary steady grind higher (2592-2600), moderate
  volume (1150-3200), no spike/reversal character, approaching but not yet exceeding the FOMC
  episode's period-high (2600.12). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~06:30 UTC (epoch
  1726813799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 06:30-08:15 UTC (verified)**: new period all-time high established (2609.78,
  exceeding the FOMC episode's prior peak 2600.12), reached via a clean, sustained two-candle
  extension (volume 5885/5222, moderately elevated but gradually decaying, not a sharp data-release
  spike-and-fade signature). Consolidated 2604-2608 for several candles afterward, holding well
  above the pre-breakout level with no failure/reversal -- a genuine breakout hold, not a match for
  AP2-DC-0001 (no failure), sweep-reclaim-extend (no prior sweep down), or the documented
  12:30/14:00 UTC "holds" family (wrong time-of-day, no clear data-release signature). Resolved
  ordinary trending continuation, not logged separately.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~08:15 UTC (epoch
  1726820099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 08:15-09:30 UTC (verified)**: continued ordinary trend extension to a fresh period
  high (2612.73), then mild consolidation/pullback (2607-2610), volume normalizing (2400-4300), no
  failure/reversal character. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~09:30 UTC (epoch
  1726824599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 09:30-10:45 UTC (verified)**: ordinary consolidation within the rally's range
  (2602-2611), moderate volume (2270-3510). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~10:45 UTC (epoch
  1726829099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 10:45-12:00 UTC (verified)**: ordinary continued grind to a fresh marginal high
  (2615.47), moderate volume (2970-3640). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~12:00 UTC (epoch
  1726833599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 12:00-15:15 UTC (verified, Friday)**: modest 12:30 UTC reaction (volume ~4400,
  ordinary) followed by a real elevated-volume episode starting 13:00 UTC (volume 6250-8388 across
  6 candles) -- sweep down to a low of 2602.63 (13:30 UTC), then a clean reclaim extending past the
  pre-episode high to a fresh period-high 2618.56 (15:00 UTC), volume gradually fading (8388 ->
  6064) as price stabilized. Eighth instance of the already-documented sweep-reclaim-extend family,
  no new structural nuance -- resolved ordinary, not logged separately.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~15:15 UTC (epoch
  1726846199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 15:15-16:30 UTC (verified, NY session)**: sharp breakout (11.56pt range, volume
  7348 at 15:15 UTC) to a fresh period-high (2625.23), holding and consolidating there with volume
  fading (7348 -> 3709) and no failure/reversal. Genuine breakout hold, not a failure -- does not
  match AP2-DC-0001 (no reversal) or sweep-reclaim-extend (no prior sweep down). Resolved ordinary
  trending continuation, not logged separately. **Third full week of September now well underway;
  price has extended significantly beyond the FOMC episode's peak (2600.12 -> now 2625).**
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~16:30 UTC (epoch
  1726850699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 16:30-18:00 UTC (verified)**: ordinary mild pullback/consolidation (2619-2626),
  moderate volume (2580-3830). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~18:00 UTC (epoch
  1726855199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 18:00-19:30 UTC (verified)**: ordinary quiet consolidation (2618-2623), moderate
  volume (2270-4000), approaching Friday close. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-20 ~19:30 UTC (epoch
  1726860599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-20 19:30-20:59 UTC (verified)**: quiet, ordinary consolidation (2621-2623), low
  volume. Ordinary weekend skip observed (Fri ~20:59 UTC -> Sun 22:14:59 UTC, consistent, ~49hrs).
  No new phenomena. **Third full week of September now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-09-22 ~22:15 UTC (epoch
  1727043299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-22 22:15-23:15 UTC (verified, Sunday reopen)**: extremely quiet reopen (2619-2622),
  low volume (680-1000). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-22 ~23:15 UTC (epoch
  1727046899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-22 23:15 UTC -> 2024-09-23 00:15 UTC (verified, Sun->Mon)**: extremely quiet
  (2618-2622), low volume (650-1470). No new phenomena. **Fourth week of September now underway.**
- Current replay position (verified via `date -d @epoch`): 2024-09-23 ~00:15 UTC (epoch
  1727050499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-23 00:15-01:15 UTC (verified)**: quiet Asian session (2616-2620), volume mostly low
  with a brief bump to 3668 that resolved without a standout reversal -- not logged separately. No
  new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-23 ~01:15 UTC (epoch
  1727054099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-23 01:15-02:15 UTC (verified)**: ordinary quiet consolidation (2617-2622), moderate
  volume (2500-3300). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-23 ~02:15 UTC (epoch
  1727057699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-23 02:15-03:15 UTC (verified)**: ordinary steady grind to a fresh period high
  (2628.34), moderate volume (1400-3300), no spike/reversal character. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-23 ~03:15 UTC (epoch
  1727061299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).

## METHODOLOGY INCIDENT + CEO PROTOCOL UPDATE (2026-07-24): autoplay uncontrolled overshoot

CEO requested a new protocol: base analysis on 1H with autoplay at 0.5x speed, letting the market
unfold naturally without stopping every candle; on a notable phenomenon, pause, note the
timestamp, then drop to finer timeframes (originally 5M then 1M; CEO later revised to 15M then 5M)
to investigate the mechanism.

Before adopting, flagged a direct conflict with two standing hard rules established earlier this
session: (1) "NU activa autoplay" and (2) the KNOWN HAZARD note above (timeframe-switch during
active replay previously silently corrupted the replay position). CEO chose "test first safely."

**Safety test results**: M15<->5M timeframe switching round-tripped cleanly (position unchanged,
data continuous, no corruption). M15->1M switching silently failed to apply (chart stayed on M15
despite `chart_set_timeframe` reporting success) -- root cause confirmed via CEO screenshot: a
genuine TradingView "Data point unavailable" toast, i.e. a real 1M-data-availability limitation for
this broker feed at this point in replay history, NOT a repeat of the KNOWN HAZARD position
corruption. No date corruption occurred in either test. CEO adjusted the finer-timeframe cascade
to **15M then 5M** (1M dropped as unavailable).

**Autoplay incident**: started autoplay at 200ms (delay-ms parameter), which the CEO's own
TradingView UI showed as **5x speed**, not the intended 0.5x -- delay-to-speed is inversely
proportional (`delay x speed = ~1000`, calibrated from this data point). Autoplay ran
**uncontrolled** in the background between tool round-trips: by the time `replay_status` was
checked, position had already advanced from 2024-09-23 ~03:15 UTC to 2024-09-24 ~15:00 UTC:
by the next check, to 2024-10-03 ~19:00 UTC; toggling autoplay off did not take effect until
2024-10-11 ~20:59 UTC. **Net result: ~19 days (2024-09-23 03:15 -> 2024-10-11 20:59) passed with
zero candle-by-candle observation** -- a real, acknowledged gap in study completeness.

Corrected autoplay to 2000ms (true ~0.5x per the calibration above) and retested from a
resynced position: markedly better (advanced ~8-9 hours per check/stop cycle instead of days),
but still overshoots by hours each time due to inherent tool-round-trip latency -- pausing
"the instant" a phenomenon is spotted is not achievable in this environment at any autoplay
speed. Flagged this plainly; CEO chose the **hybrid resolution**: abandon autoplay entirely,
resume the original safe `replay_step`-only M15 method, but batch more candles (~20-30) between
summary checks to cover the outstanding gap faster without overshoot risk.

**Recovery so far**: re-seeked replay to 2024-09-23 (via `replay_start` with fail-closed
verification -- first attempt correctly detected and rejected a no-op seek with `TIMESTAMP_MISMATCH`
rather than silently accepting the wrong position; second attempt succeeded and verified against
the expected pre-date boundary, 2024-09-22 23:59:59 UTC), then manually re-stepped M15 back to the
original resync point (2024-09-23 ~03:15 UTC) and continued forward via `replay_step` into the
territory the runaway autoplay had skipped. Investigated the one phenomenon spotted during the 1H
autoplay window (an apparent -14.85pt/2h decline, 2630->2615, flagged from 1H aggregate volume
13364/20464) using the now-available M15 detail: resolved as an **ordinary, gradual ~2hr pullback**
(moderate volume 3799-5716, no violent single-candle spike) followed by an extended organic
recovery to fresh highs -- does not match AP2-DC-0001 (no violent reversal structure) or any other
documented family; not logged separately. **Current standing protocol going forward: M15 +
`replay_step` only, no autoplay, larger per-batch candle counts (~20-30) between summary
checkpoints to cover the remaining recovery ground (through ~2024-10-11 20:59 UTC) faster.**

- Current replay position (verified via `date -d @epoch`): 2024-09-23 ~23:15 UTC (epoch
  1727133299), M15, no autoplay used (autoplay tested and abandoned per above). Running total
  this session: 1 Discovery Candidate (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through
  AP2-ADD-0006), 10 Observation Registry entries (unchanged this iteration).
- **2024-09-23 23:15 UTC -> 2024-09-24 14:15 UTC (verified, large-batch recovery pace)**: ordinary
  two-way chop (2622-2640), volume 2900-7900 -- moderately elevated at times (a pullback from
  2640.11 to 2624.63 mid-stretch, and again 6700-7900 near the end) but each resolved as ordinary
  continuation/consolidation with no violent single-candle spike or reversal structure -- not
  logged separately. No new phenomena warranting Registry/DC/Addendum treatment.
- Current replay position (verified via `date -d @epoch`): 2024-09-24 ~14:15 UTC (epoch
  1727187299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-24 14:15-20:15 UTC (verified)**: strong sustained ordinary rally (+27.68pt,
  2634.59->2664.40), moderate volume (1500-4400), no spike/reversal character -- steady trend
  continuation, not a data-driven event. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-24 ~20:15 UTC (epoch
  1727208899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-24 20:15 UTC -> 2024-09-25 03:30 UTC (verified, incl. ordinary ~76min daily-rollover
  pause)**: ordinary two-way chop (2655-2670), moderate volume (2400-4400). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-25 ~03:30 UTC (epoch
  1727234999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-25 03:30-09:45 UTC (verified)**: ordinary mild pullback/consolidation (2651-2662),
  moderate volume (2000-3300). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-25 ~09:45 UTC (epoch
  1727257499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-25 09:45-16:00 UTC (verified)**: ordinary two-way action (2654-2667), volume
  moderately elevated at times (peak 8340 mid-NY-session) but contained within range, no
  directional break or reversal structure. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-25 ~16:00 UTC (epoch
  1727279999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-25 16:00-23:15 UTC (verified, incl. ordinary ~76min daily-rollover pause)**: ordinary
  NY-afternoon consolidation tapering into a quiet new Asian session (2649-2663), volume declining
  to low (600-800). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-25 ~23:15 UTC (epoch
  1727306099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-25 23:15 UTC -> 2024-09-26 05:30 UTC (verified, Wed->Thu)**: quiet, ordinary Asian
  session grind (2655-2663), low-moderate volume (860-2700). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-26 ~05:30 UTC (epoch
  1727328599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-26 05:30-10:15 UTC (verified, Thursday -- approaching the 12:30 UTC data slot)**:
  ordinary steady rally (2658-2670.50), moderate volume (2265-3150). No new phenomena. Approaching
  12:30 UTC with heightened attention given this instance's documented history at that slot.
- Current replay position (verified via `date -d @epoch`): 2024-09-26 ~10:15 UTC (epoch
  1727345699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 6 Addenda (AP2-ADD-0001 through AP2-ADD-0006), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-26 12:30-15:45 UTC (verified, Thursday jobless-claims slot)**: eighth instance of the
  AP2-DC-0001 mechanism. Bounce to a marginal new local high (2680.02) at 12:45 UTC fails
  decisively, followed by a sustained four-candle decline (13:00-13:45 UTC, volume 8600-9600) to a
  low of 2654.81 (-25.21pt from the reclaim high), then a gradual ~2hr recovery (volume fading
  8100->4314) settling at 2670-2673 by 15:45 UTC -- still below the pre-episode base. Filed as
  **Addendum G (AP2-ADD-0007)** against AP2-DC-0001: structurally closer to the original
  candidate/Addendum F (single failure into sustained decline) than the multi-attempt D/E
  structure; reinforces the Thursday/jobless-claims association from Addenda B/C. Confidence
  remains High (8 instances, 0 contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-09-26 ~16:00 UTC (epoch
  1727366399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 7 Addenda (AP2-ADD-0001 through AP2-ADD-0007), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-26 16:00-23:15 UTC (verified, incl. ordinary ~76min daily-rollover pause)**: ordinary
  NY-afternoon consolidation and post-episode stabilization (2663-2678), volume tapering to low
  (250-400) into a quiet new Asian session. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-26 ~23:15 UTC (epoch
  1727392499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 7 Addenda (AP2-ADD-0001 through AP2-ADD-0007), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-26 23:15 UTC -> 2024-09-27 05:30 UTC (verified, Thu->Fri)**: quiet, ordinary Asian
  session (2666-2674), moderate volume (1200-3500). No new phenomena. **Fourth week of September
  now well underway.**
- Current replay position (verified via `date -d @epoch`): 2024-09-27 ~05:30 UTC (epoch
  1727414999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 7 Addenda (AP2-ADD-0001 through AP2-ADD-0007), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-27 05:30-10:00 UTC (verified, Friday -- not first-Friday-of-month, no NFP)**: ordinary
  two-way chop (2658-2670), moderate volume (2600-4400). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-27 ~10:00 UTC (epoch
  1727431199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 7 Addenda (AP2-ADD-0001 through AP2-ADD-0007), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-27 12:30-16:30 UTC (verified, Friday non-NFP)**: ninth instance of the AP2-DC-0001
  mechanism. New high (2674.35 at 12:45 UTC, volume 7041) fails, followed by an unusually long
  ~4-hour multi-wave grinding decline (14 consecutive candles, volume 4993-8543 throughout) to a
  low of 2644.79 (15:00 UTC, retested 2645.29 at 15:45 UTC) -- -29.56pt from the reclaim high,
  overshooting the pre-episode base (2658-2665) -- before stabilizing 2651-2656 by 16:30 UTC as
  volume normalized. Filed as **Addendum H (AP2-ADD-0008)** against AP2-DC-0001: a third distinct
  sub-shape for the post-failure decline phase (long multi-wave grind, neither single clean slide
  nor multi-attempt reclaim battle); second instance on a non-NFP Friday, reinforcing the "any
  weekday" framing. Confidence remains High (9 instances, 0 contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-09-27 ~16:45 UTC (epoch
  1727455499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-27 16:45-19:00 UTC (verified)**: ordinary quiet post-episode consolidation
  (2643-2654), moderate volume (2300-3900). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-27 ~19:00 UTC (epoch
  1727463599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-27 19:00-20:45 UTC (verified)**: quiet, ordinary consolidation (2651-2660), low
  volume. Ordinary weekend skip observed (Fri ~20:45 UTC -> Sun ~22:14:59 UTC, ~49.5hrs,
  consistent with the established pattern -- an intermediate cursor position at Sun ~16:30 UTC
  with no real bar data was passed through harmlessly mid-skip, not an anomaly). No new phenomena.
  **Fourth week of September now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-09-29 ~22:15 UTC (epoch
  1727648099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-29 22:15 UTC -> 2024-09-30 04:30 UTC (verified, Sun->Mon)**: ordinary two-way Asian
  session chop (2647-2666), moderate volume (1300-2700). No new phenomena. **Fifth week of
  September (final partial week of the month) now underway.**
- Current replay position (verified via `date -d @epoch`): 2024-09-30 ~04:30 UTC (epoch
  1727670599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-30 04:30-09:15 UTC (verified, Monday)**: ordinary quiet London-morning session
  (2649-2661), moderate volume (2700-3900). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-09-30 ~09:15 UTC (epoch
  1727687699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-30 09:15-15:30 UTC (verified, month/quarter-end Monday)**: a modest 12:30 UTC reaction
  (volume peak 4904, range ~9pt) resolved ordinary and recovered within 3 candles -- too mild to
  match AP2-DC-0001, not logged separately. Followed by a broader sustained decline through the NY
  morning (2651.61 -> 2628.87, -22.74pt over several hours, volume moderately elevated 5700-6750
  peak) that stabilized by 15:30 UTC -- matches the already-documented sustained multi-hour-decline
  family (no new structural nuance), not logged separately.
- Current replay position (verified via `date -d @epoch`): 2024-09-30 ~15:30 UTC (epoch
  1727711099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-09-30 15:30-23:00 UTC (verified, incl. ordinary ~76min daily-rollover pause -- last day
  of September)**: ordinary NY-afternoon consolidation tapering into a quiet new Asian session
  (2624-2642), volume declining to low (400-800) into October. No new phenomena. **September
  fully complete -- transitioning into October within the authorized period.**
- Current replay position (verified via `date -d @epoch`): 2024-10-01 ~00:00 UTC (epoch
  1727737199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-01 00:00-05:15 UTC (verified, Tuesday)**: quiet, ordinary Asian session (2634-2643),
  low volume (1050-1930). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-01 ~05:15 UTC (epoch
  1727759699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-01 05:15-09:45 UTC (verified)**: ordinary quiet London-morning grind (2641-2649),
  moderate volume (2270-2930). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-01 ~09:45 UTC (epoch
  1727775899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-01 09:45-16:00 UTC (verified)**: a modest 12:30 UTC reaction (volume peak 4709,
  magnitude ~7pt) resolved ordinary within 3-4 candles, too mild to log separately. Followed by an
  ordinary two-way NY session with a moderate rally (+16.54pt, 2646->2671), volume moderately
  elevated (5600-7655) but no violent single-candle spike or reversal structure. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-01 ~16:00 UTC (epoch
  1727798399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-01 16:15 UTC -> 2024-10-02 03:15 UTC (verified, hybrid batch)**: ordinary quiet NY
  close into Asia session (2657-2673), volume tapering from moderate (3800-6100) down to very low
  (300-1000) overnight. Two ordinary daily-rollover-style low-liquidity gaps observed (17:45->19:00
  UTC ~75min; consistent mechanical/thin-feed artifact, not logged separately). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-02 ~03:15 UTC (epoch
  1727838899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-02 03:15-10:45 UTC (verified, Wednesday, hybrid batch)**: ordinary quiet Asia-into-
  London session, mild gradual decline (2661 -> low ~2645.7) then a gentle recovery (2645.7 ->
  2655.6), moderate volume throughout (1400-4500), no single standout candle. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-02 ~10:45 UTC (epoch
  1727865899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-02 10:45-16:45 UTC (verified, hybrid batch)**: a modest 12:15-12:30 UTC dip/recovery
  (decline to 2643.81 vol 6584, bounce to 2649-2654 vol 5253/4355) resolved ordinary within 2-3
  candles, too mild to log separately (matches the already-established "modest 12:30 reaction"
  pattern). Followed by an ordinary two-way NY session: a rally to a local high 2663.42, then a
  ~22pt pullback (2663 -> low 2641.63, volume 6754-7430) that recovered to ~2649-2652 by 16:45 UTC
  -- matches the already-documented sustained-pullback-within-uptrend shape, no reversal past
  origin. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-02 ~16:45 UTC (epoch
  1727887499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-02 16:45 UTC -> 2024-10-03 01:00 UTC (verified, hybrid batch)**: very quiet, tight
  consolidation (2648-2663), low volume throughout (400-3300, one mild bump to 3285 resolving
  without drama). Ordinary ~76min daily-rollover gap observed again (Wed 20:58:59 -> 22:14:59 UTC,
  consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-03 ~01:00 UTC (epoch
  1727917199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-03 01:00-06:45 UTC (verified, Thursday, hybrid batch)**: quiet, ordinary tight
  consolidation (2652-2659), low-moderate volume throughout (1150-3800), no outliers. Still well
  before the 12:30 UTC jobless-claims data slot. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-03 ~06:45 UTC (epoch
  1727937899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-03 06:45-09:45 UTC (verified)**: a gradual London-morning decline (2657 -> low
  2641.03, ~16pt over ~3hrs), moderate volume throughout (3200-5000), no single standout candle --
  matches the already-documented low-intensity gradual-pullback pattern, not logged separately.
  Approaching the 12:30 UTC jobless-claims data slot.
- Current replay position (verified via `date -d @epoch`): 2024-10-03 ~09:45 UTC (epoch
  1727948699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-03 09:45-12:15 UTC (verified)**: quiet, ordinary tight consolidation (2641-2650),
  low-moderate volume. No new phenomena.
- **2024-10-03 12:30-14:45 UTC (verified, Thursday jobless-claims)**: a second instance of the
  "sustained high-volume two-way chop then reclaim" shape (first seen 2024-09-11 CPI day). 12:30
  candle rallies to 2654.06 then reverses to 2644.41 (vol 7455), continued whipsaw for ~2.25hrs in
  a 2637.35-2654.49 range with sustained elevated volume (5556-9455), then faded (9118 -> 5442) and
  settled 2650-2653 -- essentially back to the pre-event baseline, a fuller reclaim than the CPI
  instance. Notable: occurs on a jobless-claims day, not CPI, showing the shape isn't CPI-specific
  -> **cross-reference note added to the existing Observation Registry entry** (not a new DC).
- Current replay position (verified via `date -d @epoch`): 2024-10-03 ~15:30 UTC (epoch
  1727969399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged count; 1 more cross-referenced instance added). Hybrid-method recovery continuing
  toward ~2024-10-11 20:59 UTC target.
- **2024-10-03 15:30-20:00 UTC (verified)**: quiet, ordinary consolidation/mild grind (2648-2662),
  low-moderate volume throughout (1400-4500), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-03 ~20:00 UTC (epoch
  1727985599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-03 20:00 UTC -> 2024-10-04 01:15 UTC (verified, Friday)**: very quiet, tight
  consolidation (2654-2658), very low volume throughout (350-2300). Ordinary ~76min daily-rollover
  gap observed again (Thu 20:44:39 -> 21:58:59 UTC, consistent with prior instances). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-04 ~01:15 UTC (epoch
  1728004499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-04 01:15-04:45 UTC (verified)**: quiet, ordinary tight consolidation (2657-2666),
  low volume throughout (1000-2300), no outliers. No new phenomena. **NOTE: 2024-10-04 is the
  first Friday of October -- a genuine NFP day, same calendar type as the original AP2-DC-0001
  instance. Watching the upcoming 12:30 UTC window closely.**
- Current replay position (verified via `date -d @epoch`): 2024-10-04 ~04:45 UTC (epoch
  1728017099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-04 04:45-08:00 UTC (verified)**: quiet, ordinary grind (2660-2668), low-moderate
  volume throughout (1350-4550), no outliers. Still well before the 12:30 UTC NFP window.
  No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-04 ~08:00 UTC (epoch
  1728028799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-04 08:00-11:15 UTC (verified)**: quiet, ordinary tight consolidation (2657-2662),
  low-moderate volume throughout (1700-3500), no outliers. No new phenomena. Approaching the
  genuine NFP 12:30 UTC window (~1.25hrs away) -- watching closely next iteration.
- Current replay position (verified via `date -d @epoch`): 2024-10-04 ~11:15 UTC (epoch
  1728040499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 8 Addenda (AP2-ADD-0001 through AP2-ADD-0008), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-04 12:30-16:15 UTC (verified, genuine NFP Friday)**: a tenth instance of the
  AP2-DC-0001 mechanism, novel COMPOUND structure. Phase 1 (12:30-14:15 UTC): a CPI-style
  decline-first reaction (12:30 candle O2656.25 H2656.47 L2637.86 C2640.96, vol 10580 -- near-
  record) extends to an episode low 2632.02 (vol 9734), then recovers back toward but not above
  the pre-event baseline (2657-2662). Phase 2 (14:30-16:15 UTC): the recovery accelerates into a
  genuine new high 2670.2 (above the entire pre-event range), which fails within 1-2 candles and
  reverses into a decline settling 2643-2649 -- below both the Phase 2 high and the original
  pre-event baseline. First instance showing a decline-first (CPI-style) reaction and a classic
  breakout-failure back-to-back within the same session -> **AP2-ADD-0009 (Addendum I)
  FROZEN/SUBMITTED**. Confidence remains High.
- Current replay position (verified via `date -d @epoch`): 2024-10-04 ~16:45 UTC (epoch
  1728060299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries.
  Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-04 16:45-20:59 UTC (verified)**: quiet stabilization after the NFP compound event
  (2643-2654), ordinary low volume throughout (600-3900). Ordinary weekend skip observed (Fri
  20:58:59 -> Sun 22:14:59 UTC, consistent with prior instances), ordinary small-gap Sunday reopen
  (2653.39 -> 2650.49). No new phenomena. **First full week of October now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-10-06 ~22:15 UTC (epoch
  1728252899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-06 22:15 UTC -> 2024-10-07 02:15 UTC (verified, Sun reopen through Monday)**: very
  quiet, tight consolidation (2643-2652), low volume throughout (500-4250, one mild bump resolving
  within a candle). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~02:15 UTC (epoch
  1728267299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 02:15-05:15 UTC (verified, Monday)**: quiet, ordinary tight consolidation
  (2643-2649), low-moderate volume throughout (900-3100), no outliers. 12:30 UTC not yet reached
  (Monday, no scheduled US data typically). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~05:15 UTC (epoch
  1728278099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 05:15-09:00 UTC (verified, Monday)**: quiet, ordinary grind (2640-2657),
  moderate volume throughout (2000-4800), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~09:00 UTC (epoch
  1728291599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 09:00-12:15 UTC (verified, Monday)**: quiet, ordinary grind (2649-2659),
  moderate volume throughout (2350-3600), no outliers. No new phenomena.
- **2024-10-07 12:15-14:30 UTC (verified, Monday, no scheduled US data)**: an instance of the
  sustained multi-hour two-way regime family, unusually starting at 12:15 UTC (not the usual 12:30
  slot) with no identifiable scheduled catalyst. Sharp decline (O2657.2 -> low 2648.66, vol 5822)
  extends further to 2637.8, then a sustained ~2.25hr whipsaw (5393-7314 volume) in a
  2637.8-2653.81 range, fading and settling ~2640-2646 -- below the pre-event baseline, no clean
  reclaim -> **cross-reference note added to the original 2024-08-01 12:30 Observation Registry
  entry** (not a new DC). Reinforces that this shape recurs even off-slot and without a scheduled
  release.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~15:30 UTC (epoch
  1728314999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 1 more cross-referenced instance added). Hybrid-method recovery continuing
  toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 15:30-18:45 UTC (verified)**: quiet stabilization after the earlier two-way regime
  (2643-2650), low volume throughout (1470-4050). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~18:45 UTC (epoch
  1728325799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 18:45-22:15 UTC (verified)**: quiet, tight consolidation (2639-2645), low volume
  throughout (450-3900). Ordinary ~76min daily-rollover gap observed again (Mon 20:58:59 -> 22:14:59
  UTC, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-07 ~22:15 UTC (epoch
  1728339299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-07 22:15 UTC -> 2024-10-08 01:00 UTC (verified, Tuesday)**: quiet, ordinary
  consolidation (2638-2645), low volume. No new phenomena.
- **2024-10-08 01:00-04:00 UTC (verified, Tuesday, early Asia session)**: another instance of the
  sustained multi-hour two-way regime family, this time in the early-Asia session (a new timing
  context vs. all prior London/NY-overlap instances). 01:00 candle decline (vol 7242) off a quiet
  baseline, sustained elevated volume (3433-7879) for ~3hrs as price whipsaws to a low of 2633.76,
  then fully recovers to 2645.08 by 04:00 UTC -- a full round-trip back to baseline -> **cross-
  reference note added to the existing Observation Registry entry** (not a new DC). Confirms the
  shape isn't tied to any specific session/calendar catalyst.
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~03:45 UTC (epoch
  1728359099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 1 more cross-referenced instance added). Hybrid-method recovery continuing
  toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 03:45-07:45 UTC (verified)**: quiet consolidation (2638-2646) followed by a
  gradual, low-intensity pullback (2645.5 -> low 2631.19, ~14pt over ~1.5hrs, volume rising then
  fading 4129-6557) -- matches the already-documented low-intensity gradual-pullback pattern, not
  logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~07:45 UTC (epoch
  1728373499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 07:45-10:30 UTC (verified)**: ordinary continued mild grind/recovery (2628-2642),
  moderate volume throughout (2160-5060), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~10:30 UTC (epoch
  1728383399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 10:30-12:15 UTC (verified)**: quiet, ordinary continued grind higher (2641-2653),
  moderate volume. No new phenomena. Approaching the 12:30 UTC data slot.
- **2024-10-08 12:30-16:30 UTC (verified, Tuesday)**: the largest-magnitude instance yet of the
  sustained multi-hour continuous decline family. 12:30 candle decline (O2648.83 C2646.59, vol
  7049, no initial up-breakout), continuing for ~4hrs with volume staying elevated (4643-9046)
  throughout -- from ~2648-2652 down to a low of 2604.79 (~47.2pt), before partial recovery/
  stabilization at 2611-2616 as volume faded. Magnitude exceeds the previous largest instance
  (08-22's ~37pt) -> **cross-reference note added to the existing Observation Registry entry**
  (not a new DC -- distinct mechanism from AP2-DC-0001, no initial breakout).
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~16:30 UTC (epoch
  1728404999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 1 more cross-referenced instance added). Hybrid-method recovery continuing
  toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 16:30-19:00 UTC (verified)**: quiet stabilization after the sustained decline
  (2609-2618), low-moderate volume throughout (1950-5800). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~19:00 UTC (epoch
  1728413999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 19:00-22:15 UTC (verified)**: quiet, tight consolidation (2618-2624), low volume
  throughout (470-3400). Ordinary ~76min daily-rollover gap observed again (Tue 20:58:59 -> 22:14:59
  UTC, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-08 ~22:15 UTC (epoch
  1728425699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-08 22:15 UTC -> 2024-10-09 01:30 UTC (verified, Wednesday)**: very quiet, tight
  consolidation (2619-2624), low volume throughout (400-4700). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~01:30 UTC (epoch
  1728437399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 01:30-04:30 UTC (verified)**: quiet, ordinary tight consolidation (2615-2623),
  low-moderate volume throughout (1280-5460), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~04:30 UTC (epoch
  1728448199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 04:30-07:00 UTC (verified)**: quiet, ordinary mild grind/gradual decline
  (2610-2624), moderate volume throughout (960-5700), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~07:00 UTC (epoch
  1728457199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 07:00-08:45 UTC (verified)**: quiet, ordinary tight consolidation (2609-2617),
  moderate volume throughout (2960-4400), no outliers. No new phenomena. Approaching the 12:30
  UTC data slot (~3.75hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~08:45 UTC (epoch
  1728463499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 08:45-10:45 UTC (verified)**: quiet, ordinary tight consolidation (2614-2618),
  low-moderate volume throughout (1900-3700), no outliers. No new phenomena. Approaching the
  12:30 UTC data slot (~1.75hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~10:45 UTC (epoch
  1728470699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 10:45-12:30 UTC (verified)**: quiet, ordinary tight consolidation (2615-2622),
  moderate volume. No new phenomena.
- **2024-10-09 12:30-15:45 UTC (verified, Wednesday)**: a moderate sustained decline/partial-
  reclaim instance -- 12:30 candle modest reaction (vol 4683), extending into a ~15.7pt decline
  (2621 -> low 2605.28) over ~2.75hrs with sustained elevated volume (peak 7905), then partial
  recovery to ~2612-2616 as volume faded to 3885. Magnitude/duration squarely within the range of
  the already-documented sustained multi-hour decline/two-way family -- no new structural nuance,
  timing context, or record magnitude, so not logged as a separate cross-reference. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~15:45 UTC (epoch
  1728488699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 15:45-18:30 UTC (verified)**: quiet, ordinary tight consolidation (2605-2615),
  low-moderate volume throughout (2250-4020), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~18:30 UTC (epoch
  1728498599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 18:30-22:15 UTC (verified)**: quiet, tight consolidation (2606-2610), low volume
  throughout (430-2250). Ordinary ~76min daily-rollover gap observed again (Wed 20:58:59 -> 22:14:59
  UTC, consistent with prior instances). No new phenomena. **First full week of October now
  complete (Mon 10-07 through Wed 10-09 of week 2 covered; recovery continuing).**
- Current replay position (verified via `date -d @epoch`): 2024-10-09 ~22:15 UTC (epoch
  1728512099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-09 22:15 UTC -> 2024-10-10 01:30 UTC (verified, Thursday)**: very quiet, tight
  consolidation (2605-2611), low-moderate volume throughout (280-3420). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~01:30 UTC (epoch
  1728523799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 01:30-04:00 UTC (verified, Thursday)**: quiet, ordinary grind (2606-2617),
  moderate volume throughout (2100-5200), no outliers. No new phenomena. Approaching the 12:30
  UTC jobless-claims data slot (~8.5hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~04:00 UTC (epoch
  1728532799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 04:00-06:30 UTC (verified)**: quiet, ordinary tight consolidation (2612-2616),
  low-moderate volume throughout (970-3760), no outliers. No new phenomena. Approaching the 12:30
  UTC jobless-claims data slot (~6hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~06:30 UTC (epoch
  1728541799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 06:30-08:45 UTC (verified)**: quiet, ordinary tight consolidation (2610-2617),
  moderate volume throughout (2100-4770), no outliers. No new phenomena. Approaching the 12:30
  UTC jobless-claims data slot (~3.75hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~08:45 UTC (epoch
  1728549899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 08:45-10:45 UTC (verified)**: quiet, ordinary tight consolidation (2614-2618),
  low-moderate volume throughout (1660-2780), no outliers. No new phenomena. Approaching the
  12:30 UTC jobless-claims data slot (~1.75hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~10:45 UTC (epoch
  1728557099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 10:45-15:15 UTC (verified, Thursday, jobless-claims)**: the largest-magnitude
  instance yet of the sweep-reclaim-extend family. The 12:30 candle sweeps from ~2612-2614 down to
  2601.76, then reverses within the SAME candle to close at 2621.21 (vol 10722 -- near-record,
  third-largest single-candle volume observed this replay). Continues extending for ~1.5hrs more
  with sustained heavy volume (7500-9100) to a peak of 2629.82, then holds at an elevated 2622-2626
  range as volume gradually fades (5900-9000) -> **cross-reference note added to the existing
  sweep-reclaim-extend Observation Registry entry** (not a new DC -- combines intra-candle sweep
  with a multi-hour sustained hold at the new level, unlike smaller prior instances). No AP2-DC-0001
  match (no initial breakout-up that then fails).
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~15:15 UTC (epoch
  1728573299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 1 more cross-referenced instance added). Hybrid-method recovery continuing
  toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 15:15-17:45 UTC (verified)**: quiet stabilization after the earlier sweep-reclaim-
  extend event (2617-2629), moderate volume throughout (3900-6290). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~17:45 UTC (epoch
  1728582299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target.
- **2024-10-10 17:45-20:15 UTC (verified)**: quiet, tight consolidation (2623-2631), low-moderate
  volume throughout (1190-3330). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~20:15 UTC (epoch
  1728591299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~1 day away).
- **2024-10-10 20:15-22:15 UTC (verified)**: quiet, tight consolidation (2628-2631), low volume
  throughout (730-1190). Ordinary ~76min daily-rollover gap observed again (Thu 20:58:59 -> 22:14:59
  UTC, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-10 ~22:15 UTC (epoch
  1728598499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~23hrs away).
- **2024-10-10 22:15 UTC -> 2024-10-11 01:15 UTC (verified, Friday -- recovery target day)**:
  quiet, ordinary tight consolidation (2628-2636), low-moderate volume throughout (280-4460), no
  outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~01:15 UTC (epoch
  1728609299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~19.75hrs away, same day now).
- **2024-10-11 01:15-03:30 UTC (verified, Friday)**: quiet, ordinary tight consolidation
  (2633-2644), moderate volume throughout (3100-4120), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~03:30 UTC (epoch
  1728617399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~17.5hrs away).
- **2024-10-11 03:30-05:45 UTC (verified)**: quiet, ordinary tight consolidation (2640-2646),
  low-moderate volume throughout (1180-2600), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~05:45 UTC (epoch
  1728625499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~15.25hrs away).
- **2024-10-11 05:45-08:00 UTC (verified)**: quiet, ordinary tight consolidation (2638-2647),
  moderate volume throughout (2440-5060), no outliers. No new phenomena. Approaching the 12:30
  UTC data slot (~4.5hrs away, non-NFP Friday since NFP was 10-04).
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~08:00 UTC (epoch
  1728633599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~13hrs away).
- **2024-10-11 08:00-10:15 UTC (verified)**: quiet, ordinary tight consolidation (2636-2646),
  moderate volume throughout (1840-3160), no outliers. No new phenomena. Approaching the 12:30
  UTC data slot (~2.25hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~10:15 UTC (epoch
  1728641699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~10.75hrs away).
- **2024-10-11 10:15-12:30 UTC (verified)**: quiet, ordinary grind (2637-2648), moderate volume.
  No new phenomena.
- **2024-10-11 12:30-15:15 UTC (verified, Friday)**: a modest 12:30 reaction (O2643.61 H2650.11
  L2641.6 C2642.51, vol 7719, ~2x baseline) declines ~7.7pt then recovers and gently extends to a
  new high 2655.29 over ~2hrs, volume gradually fading (5700-7700) -- matches the already-
  documented "12:30 reaction recovers and extends" pattern, no new record or structural nuance, not
  logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~15:15 UTC (epoch
  1728659699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~5.75hrs away).
- **2024-10-11 15:15-17:30 UTC (verified)**: quiet, ordinary tight consolidation (2656-2661),
  moderate volume throughout (3000-4970), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~17:30 UTC (epoch
  1728667799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~3.5hrs away).
- **2024-10-11 17:30-19:45 UTC (verified)**: quiet, ordinary tight consolidation (2655-2660),
  low-moderate volume throughout (1480-2320), no outliers. No new phenomena. Approaching the
  recovery target (~2024-10-11 20:59 UTC, ~1.25hrs away).
- Current replay position (verified via `date -d @epoch`): 2024-10-11 ~19:45 UTC (epoch
  1728675899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration). Hybrid-method recovery continuing toward ~2024-10-11 20:59 UTC target
  (~1.25hrs away -- very close now).
- **2024-10-11 19:45-20:59 UTC (verified)**: quiet, ordinary tight consolidation (2654-2658), low
  volume throughout (750-1900), no outliers. No new phenomena.

## MILESTONE: HYBRID-METHOD RECOVERY COMPLETE (2024-10-11 ~20:59 UTC)

Current replay position (verified via `date -d @epoch`): 2024-10-11 ~20:59 UTC (epoch 1728680339)
-- **this is the exact target point where the original runaway-autoplay incident stopped**
(2026-07-24 methodology incident, documented above). The entire ~19-day gap
(2024-09-23 03:15 UTC -> 2024-10-11 20:59 UTC) has now been fully re-walked candle-by-candle using
the CEO-mandated hybrid method (`replay_step` only, M15, batches of ~25-30 candles between summary
checks, `date -d @epoch` verification before every checkpoint). During this recovery stretch, 8 new
Addenda were filed (AP2-ADD-0002 through AP2-ADD-0009) against AP2-DC-0001, plus numerous
Observation Registry cross-references (sweep-reclaim-extend family, sustained-decline family,
sustained two-way regime family), all properly investigated and documented per the standard
pre-investigation filter -- no phenomenon was skipped or silently absorbed into the gap.

**Going forward**: the recovery target has been reached. Reverting to the standard observation
pace/methodology for the remainder of the authorized period (2024-08-01 -> 2025-08-01) -- continue
with `replay_step` (M15, no autoplay, per the permanent KNOWN HAZARD constraint on timeframe
switching), compressing quiet stretches into single checkpoint summaries as before. The "hybrid"
batch-size framing (~25-30 candles) may continue as the standing pace since it worked well and
caused no issues, unless the CEO directs otherwise.

Running total this session: 1 Discovery Candidate (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through
AP2-ADD-0009), 10 Observation Registry entries.

- **2024-10-11 20:59 UTC -> 2024-10-13 22:30 UTC (verified)**: ordinary weekend skip (Fri 20:58:59
  -> Sun 22:14:59 UTC, consistent with prior instances), then a modest Sunday-reopen gap-and-decline
  (2657 -> low 2645.06, vol 2383) that stabilized within an hour (2646-2653, volume fading to 1334)
  -- within the range of already-documented weekend-gap variability, not logged separately. No new
  phenomena. **Second full week of October now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-10-13 ~22:30 UTC (epoch
  1728858599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-13 22:30 UTC -> 2024-10-14 01:00 UTC (verified, Sun reopen through Monday)**: very
  quiet, tight consolidation (2645-2651), low-moderate volume throughout (550-2730). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-14 ~01:00 UTC (epoch
  1728867599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-14 01:00-03:15 UTC (verified, Monday)**: quiet, ordinary consolidation/mild grind
  (2643-2657), moderate volume throughout (1980-5430), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-14 ~03:15 UTC (epoch
  1728875699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-14 03:15-10:15 UTC (verified, Monday)**: quiet, ordinary grind with a mild rally into
  the London session (2654.82 -> local high 2666.8 around 06:15 UTC), then a gradual partial
  pullback/consolidation (2657-2662), ordinary volume throughout (779-4313), no outliers. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-14 ~10:15 UTC (epoch
  1728900899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-14 10:15-19:30 UTC (verified, Monday)**: mild step-decline at the 12:30 UTC slot
  (vol 4202, well below documented breakout-failure/sustained-decline thresholds), followed by a
  moderate two-way US-session chop (13:00-14:30 UTC, range ~2644.83-2661.24, peak volume 7657 --
  borderline but below the 8000-13000 sustained-volume threshold seen in established families),
  then quiet consolidation (2645-2651) through the rest of the afternoon/evening. No new
  phenomena -- within normal variation, does not match any documented family's magnitude.
- Current replay position (verified via `date -d @epoch`): 2024-10-14 ~19:30 UTC (epoch
  1728934199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-14 19:35 UTC -> 2024-10-15 03:00 UTC (verified, Mon->Tue)**: very quiet, tight
  consolidation (2646.13-2653.33), low volume throughout (228-3674), daily-rollover gap observed
  again (~75min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-15 ~03:00 UTC (epoch
  1728961199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-15 03:00-09:15 UTC (verified, Tuesday)**: gradual, ordinary Asia/early-London grind
  (2651.63 -> low 2638.09 ~07:30 UTC, vol peak 6384, moderate) then a mild recovery to 2654-2655,
  settling ~2651.47. No outliers, well below documented thresholds. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-15 ~09:15 UTC (epoch
  1728983699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-15 09:15-15:30 UTC (verified, Tuesday)**: quiet consolidation, an unremarkable 12:30
  UTC candle (vol 5558, no scheduled US data on a Tuesday), then a genuine breakout starting ~14:00
  UTC that holds and extends to a fresh local high (2664.42, vol peak 8160 at 14:15 UTC), only mild
  pullback-and-continue, no reversal -> **third instance of the "12:30 UTC breakout holds and
  extends" family** cross-referenced into the existing Observation Registry entry; first instance
  NOT tied to a specific data-release day, further weakening any calendar-release link for the
  "holds" outcome.
- Current replay position (verified via `date -d @epoch`): 2024-10-15 ~15:30 UTC (epoch
  1729006199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 3rd "holds and extends" instance cross-referenced).
- **2024-10-15 15:30-22:15 UTC (verified, Tuesday)**: the rally continued to extend further to a
  new local high (2668.94 ~16:15 UTC), then a gradual, ordinary pullback/consolidation (2659-2666)
  through the evening, moderate-low volume throughout (524-4432), tapering into the close. Daily-
  rollover gap observed again (~76min, consistent). No new phenomena -- continuation of the
  already-logged breakout, not a new event.
- Current replay position (verified via `date -d @epoch`): 2024-10-15 ~22:15 UTC (epoch
  1729030499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-15 22:15 UTC -> 2024-10-16 04:15 UTC (verified, Tue->Wed)**: very quiet, tight
  consolidation through the Asia session (2658.79-2662.86), then a mild grind higher from ~01:15
  UTC (2660 -> local high 2670.14 ~02:00 UTC, vol peak 5077) holding around 2665-2669 through
  pre-London. No outliers, ordinary moderate volume throughout. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-16 ~04:15 UTC (epoch
  1729052099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-16 04:15-09:30 UTC (verified, Wednesday)**: continued gradual, steady grind higher
  through the London open (2666.76 -> 2681.95, a new local high), moderate volume throughout
  (1137-5866), no reversal, no outliers. Ordinary continuation of the ongoing rally, not a new
  phenomenon.
- Current replay position (verified via `date -d @epoch`): 2024-10-16 ~09:30 UTC (epoch
  1729070999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-16 09:30-14:30 UTC (verified, Wednesday)**: quiet chop (2673-2685) ahead of an
  unremarkable 12:30 UTC candle (vol 4819), rally continuation to a fresh local high (2685.36
  ~14:00 UTC), then a single-candle ~13pt reversal (vol 8784) with quick stabilization
  (2678-2679) rather than extension -- resembles already-documented ordinary intraday pullback
  patterns (not the sharp-breakout-failure or sustained-decline shapes), too brief/moderate to
  warrant a new entry. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-16 ~14:30 UTC (epoch
  1729088999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-16 14:30-20:45 UTC (verified, Wednesday)**: the pullback continued briefly to a low
  of 2666.76 (~15:30 UTC, vol 6080-7135 for two candles) -- total ~18.6pt off the 2685.36 peak --
  then stabilized into quiet consolidation (2670-2676) for the rest of the session, volume fading
  to ordinary levels (588-2918). Confirms the reversal was an ordinary pullback-and-consolidate,
  below the established sustained-decline family's magnitude/volume threshold. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-16 ~20:45 UTC (epoch
  1729111499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-16 20:45 UTC -> 2024-10-17 02:45 UTC (verified, Wed->Thu)**: very quiet, tight
  consolidation through the Asia session (2673-2675), daily-rollover gap observed again (~76min,
  consistent), then a mild grind higher continuing (2675 -> local high 2684.94, moderate volume
  1697-5690, no reversal). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-17 ~02:45 UTC (epoch
  1729133099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-17 02:45-05:45 UTC (verified, Thursday)**: quiet, ordinary consolidation (2674.63-
  2684.3), moderate volume throughout (1105-4643), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-17 ~05:45 UTC (epoch
  1729143899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-17 05:45-12:00 UTC (verified, Thursday)**: quiet, ordinary consolidation/mild grind
  (2676.93-2688.8), moderate volume throughout (1737-5256), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-17 ~12:00 UTC (epoch
  1729166399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-17 12:30-13:15 UTC (verified, Thursday, jobless-claims timing)**: a sharp 12:30 UTC
  gap-down sweep (pre-event baseline ~2681.3 -> low 2673.18, vol 8873), reclaimed and extended to
  a fresh local high (2686.26, ~13pt above baseline) by 13:15 UTC, volume fading (8873 -> 6884 ->
  7294 -> 6500) -> **eighth instance of the sweep-reclaim-extend family** cross-referenced into the
  existing Observation Registry entry; again at the Thursday jobless-claims slot.
- Current replay position (verified via `date -d @epoch`): 2024-10-17 ~13:15 UTC (epoch
  1729171799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 8th sweep-reclaim-extend instance cross-referenced).
- **2024-10-17 13:15-19:00 UTC (verified, Thursday)**: the reclaim rally continued to extend
  further to a fresh local high (2696.76 ~15:15 UTC), sustained moderate-elevated volume
  (4300-8004) fading through the afternoon, then quiet consolidation into the evening
  (2687-2694). No new phenomena -- continuation of the already-logged sweep-reclaim-extend
  instance.
- Current replay position (verified via `date -d @epoch`): 2024-10-17 ~19:00 UTC (epoch
  1729191599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-17 19:00 UTC -> 2024-10-18 01:15 UTC (verified, Thu->Fri)**: very quiet, extremely
  tight consolidation (2688.9-2698.48), daily-rollover gap observed again (~76min, consistent),
  very low volume throughout (302-4901). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-18 ~01:15 UTC (epoch
  1729214099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-18 01:15-06:30 UTC (verified, Friday)**: continued gradual, steady grind higher
  (2696.11 -> new local high 2714.11 ~05:30 UTC), moderate volume throughout (1072-6038), then a
  mild pullback in the final two candles (2708.26, 2703.87, vol 5381-6866). No outliers, no
  reversal pattern matching documented families. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-18 ~06:30 UTC (epoch
  1729232999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-18 06:30-13:00 UTC (verified, Friday)**: quiet, ordinary consolidation/mild chop
  (2701.73-2717.07), moderate volume throughout (2131-6519), an unremarkable 12:30 UTC candle
  (vol 5522), then a mild pullback at 12:45 UTC (2717.07 -> 2709.19, vol 5706). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-18 ~13:00 UTC (epoch
  1729256399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-18 13:00-18:15 UTC (verified, Friday)**: continued gradual grind higher through the
  US session (2704.96 -> new local high 2720.16 ~14:30 UTC), moderate-elevated volume throughout
  (2492-8200), no reversal, gradually consolidating into the afternoon (2713-2720). No new
  phenomena -- ordinary continuation of the ongoing rally.
- Current replay position (verified via `date -d @epoch`): 2024-10-18 ~18:15 UTC (epoch
  1729275299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-18 18:15-20:59 UTC -> 2024-10-20 22:15 UTC (verified, Fri->Sun)**: quiet, tight
  consolidation into Friday close (2716.86-2722.54), low volume. Ordinary weekend gap observed
  (Fri 20:58:59 -> Sun 22:14:59 UTC, ~49.3hrs, consistent with prior instances), minimal Sunday
  reopen gap (2721.2 -> 2720.37). No new phenomena. **Third full week of October now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-10-20 ~22:15 UTC (epoch
  1729462499), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-20 22:15 UTC -> 2024-10-21 03:30 UTC (verified, Sun->Mon)**: quiet Sunday reopen
  consolidation (2721.02-2725.86), then a mild step-change ~00:45 UTC Monday (vol 7533) continuing
  to grind higher to a fresh local high (2732.39), moderate-elevated volume (3363-7533). No
  outliers, ordinary continuation into the new week. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-21 ~03:30 UTC (epoch
  1729481399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-21 03:30-08:45 UTC (verified, Monday)**: quiet, tight consolidation/mild two-way chop
  (2723.62-2733.12), moderate volume throughout (1173-4855), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-21 ~08:45 UTC (epoch
  1729500299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-21 08:45-14:00 UTC (verified, Monday)**: quiet, ordinary consolidation/mild two-way
  chop (2727.75-2740.55), moderate volume throughout (3042-7988), an unremarkable 12:30 UTC candle
  (vol 6241, no scheduled release on a Monday). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-21 ~14:00 UTC (epoch
  1729519199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-21 14:00-19:15 UTC (verified, Monday)**: a moderate, gradual multi-hour decline
  (2739.4 -> low 2714.17, ~25.2pt), volume elevated for the first ~2hrs (6717-8792) then fading
  (1757-3051), no reclaim yet, not tied to the 12:30 UTC slot -> **sixth instance of the
  sustained multi-hour decline family** cross-referenced into the existing Observation Registry
  entry.
- Current replay position (verified via `date -d @epoch`): 2024-10-21 ~19:15 UTC (epoch
  1729538099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 6th sustained-decline instance cross-referenced).
- **2024-10-21 19:15 UTC -> 2024-10-22 01:15 UTC (verified, Mon->Tue)**: the decline stabilized
  into quiet, tight consolidation (2718.33-2725.93), daily-rollover gap observed again (~76min,
  consistent), low-moderate volume throughout (382-5091). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-22 ~01:15 UTC (epoch
  1729559699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-22 01:15-06:30 UTC (verified, Tuesday)**: quiet, ordinary consolidation/mild grind
  (2727.75-2737.1), moderate volume throughout (1558-4490), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-22 ~06:30 UTC (epoch
  1729578599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-22 06:30-13:00 UTC (verified, Tuesday)**: quiet, ordinary consolidation/mild chop
  (2729.51-2739.32), moderate volume throughout (1984-5141), an unremarkable 12:30 UTC candle
  (vol 5141). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-22 ~13:00 UTC (epoch
  1729601999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-22 13:00-18:15 UTC (verified, Tuesday)**: continued gradual grind higher through the
  US session (2733.74 -> new local high 2748.3 ~18:00 UTC), moderate volume throughout
  (2871-8442), no reversal. No new phenomena -- ordinary continuation.
- Current replay position (verified via `date -d @epoch`): 2024-10-22 ~18:15 UTC (epoch
  1729620899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-22 18:15 UTC -> 2024-10-23 00:45 UTC (verified, Tue->Wed)**: very quiet, extremely
  tight consolidation (2743.83-2748.9), daily-rollover gap observed again (~76min, consistent),
  very low volume throughout (356-2633). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-23 ~00:45 UTC (epoch
  1729644299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-23 00:45-06:00 UTC (verified, Wednesday)**: quiet, ordinary two-way chop (2737.96-
  2753.22, a new local high), moderate volume throughout (1403-5461), no outliers. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-23 ~06:00 UTC (epoch
  1729663199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-23 06:00-13:00 UTC (verified, Wednesday)**: quiet grind to a fresh local high
  (2758.46 ~11:30 UTC), an unremarkable 12:30 UTC candle (vol 5821, no scheduled release), then a
  gradual pullback (2758.46 -> low 2740.77, ~17.7pt over ~1.5hrs, vol peak 6109 fading to 4931) --
  below the established sustained-decline family's magnitude/volume threshold, resembles ordinary
  pullback-within-rally already documented, not logged separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-23 ~13:00 UTC (epoch
  1729688399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-23 13:00-18:15 UTC (verified, Wednesday)**: the "ordinary pullback" from the prior
  checkpoint continued far past the typical threshold -- sustained heavy volume (7215-8971) drove
  the decline (from the 11:30 peak of 2758.46) to a low of 2708.76 by ~15:45 UTC (~49.7pt total),
  exceeding the previous largest instance (~47.2pt, 2024-10-08), then partial recovery/stabilization
  to 2712-2722 as volume faded (3047-4952) -> **seventh instance of the sustained multi-hour decline
  family, new largest-magnitude instance** cross-referenced into the existing Observation Registry
  entry.
- Current replay position (verified via `date -d @epoch`): 2024-10-23 ~18:15 UTC (epoch
  1729707299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 7th sustained-decline instance cross-referenced).
- **2024-10-23 18:15 UTC -> 2024-10-24 00:45 UTC (verified, Wed->Thu)**: very quiet, tight
  consolidation (2712.79-2721.92), daily-rollover gap observed again (~76min, consistent), low
  volume throughout (414-3355). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-24 ~00:45 UTC (epoch
  1729730699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-24 00:45-06:15 UTC (verified, Thursday)**: quiet, ordinary consolidation/mild grind
  (2718.88-2729.79), moderate volume throughout (1236-5055), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-24 ~06:15 UTC (epoch
  1729749599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-24 06:15-12:45 UTC (verified, Thursday, jobless-claims timing)**: quiet, very tight
  consolidation (2728.37-2741.63), moderate volume throughout (1788-6814), a moderate 12:30 UTC
  candle (vol 6814, ~7pt range) below documented thresholds. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-24 ~12:45 UTC (epoch
  1729773899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-24 12:45-18:00 UTC (verified, Thursday)**: a moderate gradual decline (2743.26 -> low
  2722.45, ~20.8pt) with elevated volume (6228-9046, several candles at/above 8000) over ~2hrs,
  then recovery/stabilization to 2727-2737 as volume faded (2964-4781) -- resembles the
  well-established sustained-decline family shape but on the smaller/mid end of the magnitude
  range already covered by 7 documented instances; not distinct enough to warrant a new
  cross-reference line. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-24 ~18:00 UTC (epoch
  1729792799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-24 18:00 UTC -> 2024-10-25 00:30 UTC (verified, Thu->Fri)**: extremely quiet, tight
  consolidation (2732.23-2737.79), daily-rollover gap observed again (~76min, consistent), very
  low volume throughout (268-2830). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-25 ~00:30 UTC (epoch
  1729816199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-25 00:30-05:45 UTC (verified, Friday)**: quiet, ordinary consolidation/mild grind
  (2723.97-2735.16), low-moderate volume throughout (985-3806), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-25 ~05:45 UTC (epoch
  1729835099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-25 05:45-12:45 UTC (verified, Friday, non-NFP/month-end)**: gradual mild decline
  (2732.56 -> low 2717.05, ~15.5pt) through the morning, moderate volume throughout
  (2448-4404), an unremarkable 12:30 UTC candle (vol 4362, ~4pt range). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-25 ~12:45 UTC (epoch
  1729860299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-25 12:45-18:00 UTC (verified, Friday)**: recovered from the morning decline and
  continued grinding higher through the US session (2725.26 -> new local high 2745.02 ~17:45
  UTC), moderate-elevated volume throughout (2589-7848), no reversal. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-25 ~18:00 UTC (epoch
  1729879199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-25 18:00-20:59 UTC -> 2024-10-27 22:15 UTC (verified, Fri->Sun)**: quiet, tight
  consolidation into Friday close (2740.34-2747.8), low volume. Ordinary weekend gap observed
  (Fri 20:58:59 -> Sun 22:14:59 UTC, ~49.3hrs, consistent with prior instances), modest Sunday
  reopen gap-down (2747.46 -> 2734.36, ~13pt), ordinary variability. No new phenomena. **Fourth
  full week of October now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-10-27 ~22:15 UTC (epoch
  1730067299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-27 22:15 UTC -> 2024-10-28 03:30 UTC (verified, Sun->Mon)**: quiet Sunday reopen
  consolidation, then a mild step-change ~00:45 UTC Monday (vol 6003, brief dip to 2724.73) with
  quiet recovery/consolidation (2724.73-2740.21) through early Monday. No outliers, ordinary
  continuation into the new week. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-28 ~03:30 UTC (epoch
  1730086199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-28 03:30-08:45 UTC (verified, Monday)**: quiet, ordinary consolidation/mild two-way
  chop (2729.18-2744.58), moderate volume throughout (1192-4385), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-28 ~08:45 UTC (epoch
  1730105099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-28 08:45-14:00 UTC (verified, Monday)**: quiet consolidation, an unremarkable 12:30
  UTC candle (vol 3482, no scheduled release on a Monday), then a mild rally starting ~13:15 UTC
  to a fresh local high (2743.43), moderate-elevated volume (5239-7180). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-28 ~14:00 UTC (epoch
  1730123999), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-28 14:00-19:15 UTC (verified, Monday)**: quiet, ordinary consolidation/mild two-way
  chop (2739.01-2745.98), moderate volume throughout (1886-6596), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-28 ~19:15 UTC (epoch
  1730142899), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-28 19:15 UTC -> 2024-10-29 01:30 UTC (verified, Mon->Tue)**: very quiet, tight
  consolidation (2739.89-2750.15), daily-rollover gap observed again (~76min, consistent),
  low-moderate volume throughout (347-5019). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-29 ~01:30 UTC (epoch
  1730165399), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-29 01:30-06:45 UTC (verified, Tuesday)**: quiet, ordinary consolidation/mild grind
  (2747.64-2757.74), moderate volume throughout (1034-5155), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-29 ~06:45 UTC (epoch
  1730184299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-29 06:45-13:00 UTC (verified, Tuesday)**: quiet, ordinary consolidation/mild two-way
  chop (2746.33-2756.59), moderate volume throughout (1843-5439), an unremarkable 12:30 UTC candle
  (vol 4342). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-29 ~13:00 UTC (epoch
  1730206799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-29 13:00-18:15 UTC (verified, Tuesday)**: a moderate rally starting ~13:15 UTC
  (2748.28 -> new local high 2772.56, ~24.3pt) with sustained elevated volume (5464-8883) over
  ~3.5hrs, then quiet consolidation (2765-2772) -- resembles the established "breakout holds and
  extends" family shape, though off the exact 12:30 UTC timing; ordinary continuation, not logged
  separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-29 ~18:15 UTC (epoch
  1730225699), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-29 18:15 UTC -> 2024-10-30 00:30 UTC (verified, Tue->Wed)**: extremely quiet, tight
  consolidation (2768.98-2778.86), daily-rollover gap observed again (~76min, consistent), very
  low volume throughout (495-3109). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-30 ~00:30 UTC (epoch
  1730248199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-30 00:30-05:45 UTC (verified, Wednesday)**: quiet, ordinary consolidation/mild grind
  (2776.1-2783.92), moderate volume throughout (1052-4234), no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-30 ~05:45 UTC (epoch
  1730267099), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-30 05:45-12:45 UTC (verified, Wednesday)**: quiet, ordinary consolidation/mild
  two-way chop (2773.31-2789.83), moderate volume throughout (1837-6076), a moderate 12:30 UTC
  candle (vol 5915, ~5.9pt range) below documented thresholds. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-10-30 ~12:45 UTC (epoch
  1730292299), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-10-30 12:45-18:00 UTC (verified, Wednesday)**: a sharp single-candle sweep at 14:15 UTC
  (2787.48 -> low 2770.93, vol 9964 -- near-record), then a gradual reclaim over ~3hrs (sustained
  volume 5312-8105 fading) extending to a fresh local high of 2789.6 by ~17:45 UTC -> **ninth
  instance of the sweep-reclaim-extend family** cross-referenced into the existing Observation
  Registry entry; first instance clearly off the 12:30 UTC slot, at ~14:15 UTC with no identified
  scheduled release.
- Current replay position (verified via `date -d @epoch`): 2024-10-30 ~18:00 UTC (epoch
  1730311199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 9th sweep-reclaim-extend instance cross-referenced).
- **2024-10-30 18:00 -> 2024-10-31 12:15 UTC (verified)**: quiet overnight/early-London grind
  (2761.51-2790.12, moderate-low volume 476-4138 throughout, one mild volume bump 4138 that
  resolved without reversal), ordinary daily-rollover gap observed again (consistent, ~76min). No
  new phenomena.
- **2024-10-31 12:30-16:15 UTC (verified, Thursday, jobless-claims timing) -- NEW LARGEST-
  MAGNITUDE INSTANCE**: starting exactly at the established 12:30 UTC data slot, a moderate
  step-change candle (O2776.87 H2778.85 L2774.18 C2774.34, vol 7448) opened a sustained decline
  with continuously elevated-to-near-record volume (7147-9650, eight consecutive candles at/above
  7000, five above 8000) driving price from a pre-event baseline high of 2781.96 (12:15 UTC) down
  to a low of 2731.56 by 15:00 UTC -- a total ~50.4pt decline over ~2.75hrs, exceeding the previous
  largest instance (~49.7pt, 2024-10-23) -> **eighth instance of the sustained multi-hour decline
  family** cross-referenced into the existing Observation Registry entry. Volume then faded
  (7305 -> 5369) as price stabilized/partially recovered to 2738-2743 by 16:15 UTC, still well below
  the pre-event baseline. Third instance tied to the established 12:30 UTC slot on a genuine
  jobless-claims Thursday; not logged as a new DC/addendum -- same established family, not a new
  mechanism.
- Current replay position (verified via `date -d @epoch`): 2024-10-31 ~16:15 UTC (epoch
  1730392199), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 9 Addenda (AP2-ADD-0001 through AP2-ADD-0009), 10 Observation Registry entries
  (unchanged count; 8th sustained-multi-hour-decline instance cross-referenced, new record
  magnitude).
- **2024-10-31 16:15 UTC -> 2024-11-01 12:15 UTC (verified)**: quiet overnight/morning grind
  (mostly 2740-2755, tight range), ordinary low-moderate volume throughout, daily-rollover gap
  observed again (consistent, ~76min). No new phenomena in this stretch aside from the 12:30 UTC
  event below.
- **2024-11-01 12:30-16:00 UTC (verified, first Friday of November -- genuine NFP)**: an eleventh
  instance of the AP2-DC-0001 mechanism -- 12:30 UTC breakout (vol 9599, near-record) to a marginal
  new high, followed by THREE distinct failed new-high attempts (2759.89 / 2761.49 / 2762.22)
  within ~90min (sustained volume 7487-9599), then a decisive decline from 14:15 UTC to an episode
  low of 2739.73 (14:30 UTC, vol 8655), settling ~2743-2745 by 16:00 UTC as volume faded
  (8303 -> 4972) -- below the pre-event baseline (2747-2754) but only a modest overshoot, unlike
  the larger undershoots in Addenda D/H -> **AP2-ADD-0010 (Addendum J) FROZEN/SUBMITTED**. Third
  genuine-NFP-Friday instance; confidence remains High.
- Current replay position (verified via `date -d @epoch`): 2024-11-01 ~16:00 UTC (epoch
  1730476799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 10 Addenda (AP2-ADD-0001 through AP2-ADD-0010), 10 Observation Registry entries.
- **2024-11-01 16:15 -> 20:58:59 UTC (verified, Friday)**: quiet stabilization after the NFP event
  (2734-2745), ordinary low-moderate volume, no outliers. Ordinary weekend skip observed
  (Fri 20:58:59 UTC -> Sun 23:14:59 UTC) -- notably ~50.3hrs this time vs. the usual ~49.3hrs, one
  hour longer, plausibly explained by the 2024-11-03 US DST end shifting the broker's session-open
  time by 1hr relative to UTC -- a calendar/mechanical artifact, not a market phenomenon, not
  logged as a new Registry entry. **October 2024 now complete.**
- **2024-11-03 23:15 UTC -> 2024-11-04 12:15 UTC (verified, Sun reopen through Monday)**: ordinary
  small gap-up reopen, tight consolidation (2729-2748), low-moderate volume throughout, daily-
  rollover-style gap observed again within the stretch (consistent). 12:30 UTC passed without a
  sharp reaction (vol 2784, unremarkable) -- expected, no scheduled US release on a Monday. No new
  phenomena.
- **2024-11-04 12:45-16:45 UTC (verified, Monday)**: a moderate, bounded two-way regime -- elevated
  volume (4559-7423) sustained for ~8-9 candles (~2.25hrs) while price oscillated within a ~11pt
  range (2732-2748) without ever producing a clean directional breakout, sweep, or sustained
  decline. Resembles the already-documented "sustained multi-hour two-way regime" shape (2024-08-01
  and 2024-08-21 entries) but milder in both magnitude and volume intensity -- treated as ordinary
  variation within an already-characterized shape, not logged as a new Registry entry. Volume faded
  (7423 -> 4329) as the regime wound down, settling ~2732-2738 by 16:45 UTC.
- Current replay position (verified via `date -d @epoch`): 2024-11-04 ~17:00 UTC (epoch
  1730739599), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 10 Addenda (AP2-ADD-0001 through AP2-ADD-0010), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-04 17:00 -> 2024-11-05 12:30 UTC (verified, Election Day)**: quiet, ordinary grind
  (2724-2750 range, gradual), moderate volume throughout, daily-rollover gap observed again
  (consistent, ~76min). One moderate decline candle (~10pt, vol 5874) around 12:45 UTC (11-05, pre-
  12:30 recheck) recovered without becoming a sustained-decline instance -- ordinary pullback, not
  logged. 12:30 UTC candle itself unremarkable (vol 2187) -- expected, no scheduled US data release
  on Election Day itself.
- **2024-11-05 17:00-19:30 UTC (verified, Election Day)**: the day's gradual rally (which had
  reached a marginal new high of 2750.01 at 17:00 UTC) failed within the same candle and gave back
  its gains in a choppy, two-way fashion over ~2.5hrs -- sharp legs down to an episode low of
  2733.48 (17:45 UTC, vol 7213) alternating with bounces back to 2744 (18:30 UTC), sustained
  elevated volume (4000-8574) throughout, before normalizing (3330-3421) and settling ~2741-2743 by
  19:30 UTC -- close to, not dramatically below, the broader pre-rally-leg range. Resembles the
  already-documented "sustained multi-hour two-way regime" shape (2024-08-01, 2024-08-21, and the
  2024-11-04 entry) rather than a clean AP2-DC-0001-style one-way failure or the sustained-decline
  family (no clean one-directional extended decline here, genuine two-way chop) -- not logged as a
  new Registry entry, treated as ordinary variation within an already-characterized shape.
- Current replay position (verified via `date -d @epoch`): 2024-11-05 ~17:30 UTC (epoch
  1730827799), M15, no autoplay used. Running total this session: 1 Discovery Candidate
  (AP2-DC-0001), 10 Addenda (AP2-ADD-0001 through AP2-ADD-0010), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-05 17:30-19:30 UTC (verified)**: quiet stabilization after the earlier give-back
  episode (2740-2744), low volume. No new phenomena.
- **2024-11-06 00:15-10:15 UTC (verified) -- MAJOR EVENT, SECOND DISCOVERY CANDIDATE**: overnight
  (coinciding with U.S. election results reporting following the 2024-11-05 presidential election),
  a ~10-hour episode of sustained, near-record volume (peaking 9981) unfolded in three phases: (1)
  ~00:15-04:15 UTC prolonged two-way chop (2730-2750, vol 4800-7600), exceeding the already-
  documented "sustained multi-hour two-way regime" family's typical duration; (2) ~05:45-07:00 UTC
  a sharp decisive decline to an episode low of 2701.40 (06:30 UTC, vol 9981 -- near-record); (3)
  ~07:00-10:15 UTC a strong but incomplete recovery rally, settling ~2723-2727 as volume normalized.
  Total range ~48.6pt, by far the longest sustained-elevated-volume episode observed this replay.
  Does not cleanly match any established family (not a clean one-way decline, not a clean
  AP2-DC-0001-style single breakout-failure, far exceeds the two-way-regime family in scale) ->
  **AP2-DC-0002 FROZEN/SUBMITTED** ("A Major Scheduled Political Catalyst Produces a Multi-Hour,
  Near-Record-Volume, Complex Two-Way Volatility Episode Far Exceeding Any Routine Data-Release
  Reaction"). Confidence: Medium (single instance, low-frequency calendar catalyst, limited
  repetition opportunity within the authorized period).
- Current replay position (verified via `date -d @epoch`): 2024-11-06 ~10:30 UTC (epoch
  1730888999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 10 Addenda (AP2-ADD-0001 through AP2-ADD-0010, all against
  AP2-DC-0001), 10 Observation Registry entries.
- **2024-11-06 10:30-11:15 UTC (verified)**: brief ~1hr lull, volume back to baseline
  (2807-3457), appeared at first to be the AP2-DC-0002 episode's true resolution.
- **2024-11-06 11:15-18:00 UTC (verified) -- AP2-DC-0002 CONTINUES, ADDENDUM FILED**: after the
  lull, a second, substantially larger wave of decline began -- volume rebuilding (4219-6368)
  through 12:15 UTC, then a decisive acceleration from 13:00-14:30 UTC with repeated near-record
  volume (10158 at 13:00 UTC -- a new peak, exceeding the original episode's 9981; also 8827, 9607,
  9910, 9515, 9579) driving price to a fresh low of **2652.40** (14:30 UTC), well below the original
  episode's 2701.40 low. Continued volatile two-way churn (2652-2678, vol 7398-8799) through 16:00
  UTC, then volume progressively normalized (7693 -> 3472-4900) as price settled ~2663-2669 by
  18:00 UTC. Combined with the original episode, the full event now spans ~00:15-18:00 UTC (nearly
  18hrs, one ~1hr lull) with a total ~88-92pt range -- roughly double the originally-documented
  scale -> **AP2-ADD-0011 (Addendum A to AP2-DC-0002) FROZEN/SUBMITTED**: documents the extended
  duration/magnitude; this second wave's shape (sustained decline with volatile legs) differs from
  the original's three-phase composite, closer to the already-documented "sustained multi-hour
  decline" family in character, but treated as a continuation of the same catalyst/event rather
  than a new DC.
- Current replay position (verified via `date -d @epoch`): 2024-11-06 ~18:00 UTC (epoch
  1730915999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 11 Addenda (AP2-ADD-0001 through AP2-ADD-0010 against AP2-DC-0001,
  AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries.
- **2024-11-06 18:00 UTC -> 2024-11-07 12:15 UTC (verified)**: quiet, ordinary consolidation/mild
  grind (2643-2668 range, one moderate ~21pt pullback around 01:30-02:45 UTC on 11-07 that
  recovered without becoming a sustained-decline instance), ordinary daily-rollover gap observed
  again (consistent, ~76min). 12:30 UTC candle unremarkable (vol 3212) -- expected, main event
  today is the FOMC decision later. No new phenomena in this stretch.
- **2024-11-07 13:30-16:15 UTC (verified, Thursday, pre-FOMC)**: a sustained pre-event rally
  (2670 -> fresh high 2700.11), elevated volume throughout (5600-8066) for ~2.75hrs, then fading/
  consolidating (2694-2700) ahead of the 19:00 UTC FOMC decision -- ordinary pre-event positioning,
  not logged separately (no clean family match, no reversal to characterize).
- **2024-11-07 19:00-21:00 UTC (verified, Thursday, genuine FOMC rate decision + press
  conference)**: an initial two-way dip at the 19:00 UTC statement (low 2687.49, vol 7070-7320)
  followed by a sustained rally from ~19:45 UTC (during the press conference) to a fresh high
  (2710.23, vol 7037 peak) that HOLDS, settling ~2704-2705 by 21:00 UTC -- a genuine ~10pt net gain
  above the pre-event baseline (~2694-2699), no reversal -> **fourth instance of the "breakout
  holds and extends" family**, first at a FOMC-specific time slot, notably CONTRASTING with the
  only other FOMC-decision instance in this instance's history (2024-09-18, AP2-DC-0001 Addendum
  F, a sharp -53.2pt decline) -- cross-referenced into the existing Observation Registry entry, not
  a new DC/addendum.
- Current replay position (verified via `date -d @epoch`): 2024-11-07 ~21:15 UTC (epoch
  1731014099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 11 Addenda (AP2-ADD-0001 through AP2-ADD-0010 against AP2-DC-0001,
  AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries (unchanged count; 4th
  "breakout holds and extends" instance cross-referenced).
- **2024-11-07 21:15 UTC -> 2024-11-08 12:15 UTC (verified)**: quiet, ordinary consolidation/mild
  grind (2680-2710 range, one moderate ~10pt pullback around 01:00 UTC on 11-08 that recovered
  without becoming a sustained-decline instance), ordinary daily-rollover gap observed again
  (consistent, ~76min). No new phenomena.
- **2024-11-08 12:30-17:15 UTC (verified, Friday, second Friday of November -- not NFP)**: a
  twelfth instance of the AP2-DC-0001 mechanism -- a modest 12:30 UTC reaction (vol 6515) followed
  by an unusually gradual ~2hr build-up (new build-up sub-shape, vs. prior instances' sharper
  breakouts) to a high of 2704.1 (14:15 UTC), then failure into a decline (sharp spike-down candle
  vol 8195 mid-decline) to a low of 2682.90, settling ~2683-2687 by 17:15 UTC -- only a modest
  overshoot below the pre-event baseline (2688-2694), similar to Addendum J -> **AP2-ADD-0012
  (Addendum K) FROZEN/SUBMITTED**. Confidence remains High (12 instances, zero contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-11-08 ~17:15 UTC (epoch
  1731086099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries.
- **2024-11-08 17:15 -> 21:58:59 UTC (verified, Friday)**: quiet, ordinary consolidation
  (2682-2688), low volume. Weekend skip observed -- notably at a NEW time, Fri 21:58:59 UTC ->
  Sun 23:14:59 UTC (~49.3hrs, same duration as always, but ~1hr later in UTC than the pre-DST
  pattern of Fri 20:58:59 -> Sun 22:14:59) -- confirms the DST-driven shift hypothesized in the
  2024-11-01 checkpoint is now the standing pattern following the 2024-11-03 US DST end; calendar/
  mechanical artifact, not logged as a new phenomenon.
- **2024-11-10 23:15 UTC -> 2024-11-11 04:15 UTC (verified, Sun reopen through Monday, US
  Veterans Day)**: ordinary small gap-up reopen, quiet consolidation (2678-2685), one moderate
  ~14pt pullback (~01:15-01:45 UTC) that recovered/stabilized without becoming a sustained-decline
  instance -- not logged separately. No new phenomena; markets trading normally despite the US
  federal holiday.
- Current replay position (verified via `date -d @epoch`): 2024-11-11 ~05:45 UTC (epoch
  1731303899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-11 05:45-12:30 UTC (verified)**: quiet, ordinary grind (2652-2675), one moderate
  ~14pt pullback (~10:45-11:15 UTC) that recovered without becoming a sustained-decline instance.
  12:30 UTC candle unremarkable (vol 3207) -- expected, Monday, no scheduled release. No new
  phenomena.
- **2024-11-11 13:00-16:45 UTC (verified, Monday, no identified scheduled release)**: a ninth
  instance of the sustained multi-hour decline family -- starting ~30min after the (unremarkable)
  12:30 UTC slot, a moderate step-change candle (vol 6590) opened a sustained decline with
  continuously elevated-to-near-record volume (4504-9437) driving price from a pre-event baseline
  of ~2662-2670 down to a low of 2612.70 by 16:15 UTC -- a total ~50-57pt decline over ~3.5hrs,
  comparable to the largest instance observed. Volume then faded (5802 -> 3720) as price stabilized
  ~2614-2618 by 16:45 UTC, not reclaimed -> **cross-reference note added to the existing
  Observation Registry entry**; first instance tied to a Monday with no identified catalyst at all,
  reinforcing the general-mechanism (not calendar-specific) framing. Not a new DC/addendum.
- Current replay position (verified via `date -d @epoch`): 2024-11-11 ~17:00 UTC (epoch
  1731344399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged count; 9th sustained-multi-hour-decline instance cross-referenced).
- **2024-11-11 17:00 UTC -> 2024-11-12 02:15 UTC (verified)**: quiet stabilization after the
  ninth sustained-decline instance (2611-2627), low-moderate volume throughout, daily-rollover gap
  observed again (consistent, ~76min, now at the DST-shifted ~21:58:59 UTC time). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-12 ~02:15 UTC (epoch
  1731377699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-12 05:15-10:15 UTC (verified, Tuesday, no identified scheduled release)**: a tenth
  instance of the sustained multi-hour decline family -- a gradual multi-wave decline in three
  distinct legs with partial bounces between (2617 -> 2603.48 -> bounce -> 2595.22 -> bounce ->
  2590.86), sustained moderate-to-elevated volume throughout (2578-6634), settling ~2591-2596 by
  10:15 UTC, not reclaimed. Total ~26.1pt over ~5hrs, comparable to the Sixth instance. Initially
  nearly dismissed as three separate ordinary pullbacks before the full multi-wave arc became
  clear -> **cross-reference note added to the existing Observation Registry entry**, not a new
  DC/addendum.
- Current replay position (verified via `date -d @epoch`): 2024-11-12 ~10:15 UTC (epoch
  1731406499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged count; 10th sustained-multi-hour-decline instance cross-referenced).
- **2024-11-12 10:15-12:00 UTC (verified)**: quiet, ordinary consolidation (2590-2599), moderate
  volume. 12:00-12:30 UTC saw a moderate rally start (2595 -> 2604.57), 12:30 UTC candle itself
  unremarkable (vol 4863) -- expected, Tuesday, no scheduled release.
- **2024-11-12 12:00-17:45 UTC (verified, Tuesday)**: a sustained, ~5.75hr two-way episode --
  continued rally with elevated volume to an episode high of 2617.15 (14:15 UTC), then reversed
  into a decline with sustained heavy volume (5365-7728) to an episode low of 2592.54 (17:00 UTC,
  below the episode's starting point) -- a ~24.6pt swing with no net directional resolution
  (settling ~2597-2599, roughly back near the starting level). Resembles the already-documented
  "sustained multi-hour two-way regime" shape (2024-08-01, 2024-08-21, 2024-11-04, 2024-11-05
  entries) -- not logged as a new Registry entry, treated as ordinary variation within an
  already-characterized shape.
- Current replay position (verified via `date -d @epoch`): 2024-11-12 ~18:00 UTC (epoch
  1731434399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-12 18:00 UTC -> 2024-11-13 05:00 UTC (verified)**: quiet, ordinary consolidation/mild
  grind (2595-2613), low-moderate volume throughout, one moderate rally-and-pullback (~01:00-02:15
  UTC on 11-13, 2599 -> 2611.18 -> settling ~2606-2607, vol 4029-5289) that resolved without drama,
  daily-rollover gap observed again (consistent, ~76min, DST-shifted timing). No new phenomena.
  **2024-11-13 is expected to be a US CPI release day; approaching the ~13:30 UTC (DST-shifted)
  release window.**
- Current replay position (verified via `date -d @epoch`): 2024-11-13 ~05:00 UTC (epoch
  1731473999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 12 Addenda (AP2-ADD-0001 through AP2-ADD-0010 and AP2-ADD-0012
  against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry entries
  (unchanged this iteration).
- **2024-11-13 05:00-13:00 UTC (verified)**: quiet, ordinary consolidation (2601-2613), low-
  moderate volume throughout. 12:30 UTC candle unremarkable, confirming the CPI release itself was
  now DST-shifted to 13:30 UTC. No new phenomena.
- **2024-11-13 13:30-18:15 UTC (verified, Wednesday, genuine US CPI release, DST-shifted to
  13:30 UTC)**: a thirteenth instance of the AP2-DC-0001 mechanism -- near-record volume (10541)
  at 13:30 UTC drove a sharp spike to a marginal new high (2618.85) that failed within the same
  candle, followed by a genuine reclaim attempt to 2616.4 (14:00 UTC), then a sustained, heavy-
  volume decline (5724-8765) through multiple legs to an episode low of 2577.60 (17:15 UTC) --
  a ~41.25pt decline from the spike high, settling ~2582-2585 (~25pt overshoot below the 2608-2611
  pre-event baseline) as volume faded. Contrasts with the 2024-09-11 CPI instance (decline-first,
  not an AP2-DC-0001 match) -> **AP2-ADD-0013 (Addendum L) FROZEN/SUBMITTED**. Confidence remains
  High (13 instances, zero contradicting).
- Current replay position (verified via `date -d @epoch`): 2024-11-13 ~18:15 UTC (epoch
  1731521699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries.
- **2024-11-13 18:15 UTC -> 2024-11-14 03:00 UTC (verified)**: quiet stabilization after the
  major CPI episode (2559-2585), low-moderate volume throughout, daily-rollover gap observed again
  (consistent, ~76min). One moderate ~12pt decline (~01:30-03:00 UTC on 11-14) that recovered
  without becoming a sustained-decline instance, not logged separately. No new phenomena.
  **2024-11-14 is expected to be a jobless-claims Thursday; approaching the ~13:30 UTC
  (DST-shifted) release window.**
- Current replay position (verified via `date -d @epoch`): 2024-11-14 ~03:00 UTC (epoch
  1731553199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-14 03:00-13:15 UTC (verified)**: quiet, ordinary consolidation/mild grind
  (2536-2559), two moderate pullbacks (~05:30-06:15 and ~09:45-11:00 UTC, both ~15pt) that
  recovered without becoming sustained-decline instances. 12:30 UTC candle unremarkable, confirming
  the jobless-claims release itself was DST-shifted to 13:30 UTC. No new phenomena.
- **2024-11-14 13:30-16:45 UTC (verified, Thursday, genuine jobless-claims release, DST-shifted
  to 13:30 UTC)**: a fifth instance of the "breakout holds and extends" family -- near-record
  volume (9340) at 13:30 UTC, followed by a sustained rally with elevated volume throughout
  (4447-8802) climbing from the ~2552-2558 pre-event baseline to a fresh high of 2577.45
  (17:00 UTC) and HOLDING, settling ~2572-2576 as volume faded -- a genuine ~20-25pt sustained
  gain, no reversal -> **cross-reference note added to the existing Observation Registry entry**,
  not a new DC/addendum. First jobless-claims-Thursday instance tied to the new DST-shifted
  13:30 UTC timing.
- Current replay position (verified via `date -d @epoch`): 2024-11-14 ~17:00 UTC (epoch
  1731603599), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 5th "breakout holds and extends" instance cross-referenced).
- **2024-11-14 17:00-24:00 UTC (verified)**: quiet stabilization after the jobless-claims rally
  (2563-2577), one moderate ~12.6pt two-way stretch (~20:00-20:45 UTC, vol 4707-7407) that resolved
  without becoming a directional event, daily-rollover gap observed again (consistent, ~76min,
  DST-shifted timing). No new phenomena. **Second full week of November now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-11-15 ~00:00 UTC (epoch
  1731628799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-15 00:00-04:30 UTC (verified, Friday, not NFP)**: quiet, ordinary consolidation/mild
  grind (2563-2572), low-moderate volume throughout, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-15 ~04:30 UTC (epoch
  1731644999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-15 04:30-09:15 UTC (verified, Friday)**: quiet, ordinary consolidation/mild grind
  (2554-2569), one moderate ~11pt pullback (~06:15-06:45 UTC) that recovered without becoming a
  sustained-decline instance, low-moderate volume throughout. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-15 ~09:15 UTC (epoch
  1731662099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-15 09:15-13:15 UTC (verified, Friday)**: quiet, ordinary consolidation/mild grind
  (2563-2573), low-moderate volume throughout, 12:30 UTC candle unremarkable (vol 2996) -- expected,
  no scheduled release identified. No new phenomena.
- **2024-11-15 13:15-18:45 UTC (verified, Friday, no identified scheduled catalyst)**: a large,
  sustained ~5.5hr two-way volatility episode -- near-record peak volume (9759 at 13:30 UTC),
  continuously elevated-to-heavy volume (3441-9759) throughout, price oscillating within a
  ~16.6pt range (2559.47-2576.06) with multiple sharp legs both up and down but no clean net
  directional resolution (opened ~2568-2570, settled ~2564-2566 by 18:45 UTC, roughly flat).
  Resembles the already-documented "sustained multi-hour two-way regime" shape (2024-08-01,
  2024-08-21, 2024-11-04, 2024-11-05, 2024-11-12 entries) -- notable for its near-record volume
  intensity and long duration despite no identified specific catalyst, but not logged as a new
  Registry entry, treated as ordinary variation within an already-characterized shape.
- Current replay position (verified via `date -d @epoch`): 2024-11-15 ~18:45 UTC (epoch
  1731696299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-15 18:45-21:58:59 UTC (verified, Friday)**: quiet stabilization, ordinary low-volume
  grind (2559-2568), no new phenomena. Ordinary weekend skip observed (Fri 21:58:59 UTC ->
  Sun 23:14:59 UTC, ~49.3hrs, consistent with the DST-shifted pattern). **Third full week of
  November now complete.**
- **2024-11-17 23:15 UTC -> 2024-11-18 00:00 UTC (verified, Sun reopen)**: ordinary modest gap-up
  reopen (2571-2576), low volume. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~00:00 UTC (epoch
  1731887999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 01:30-02:45 UTC (verified, Monday, early Asian session, no identified catalyst)**:
  a sixth instance of the "breakout holds and extends" family -- a sharp rally with elevated
  volume (5063-6401) pushing from the ~2571-2577 pre-event baseline to a fresh high of 2597.27
  (02:00 UTC), then settling into two-way chop (2590-2595) as volume faded, holding well above
  baseline with no reversal -> **cross-reference note added to the existing Observation Registry
  entry**; first instance at an unusual off-hours time slot, not a new DC/addendum.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~02:45 UTC (epoch
  1731897899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 6th "breakout holds and extends" instance cross-referenced).
- **2024-11-18 02:45-05:00 UTC (verified, Monday)**: quiet stabilization after the overnight
  rally (2587-2593), low volume throughout. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~05:00 UTC (epoch
  1731905999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 05:00-08:15 UTC (verified, Monday)**: quiet, ordinary consolidation/mild grind
  (2580-2587), low-moderate volume throughout, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~08:15 UTC (epoch
  1731917699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 08:15-12:45 UTC (verified, Monday)**: quiet, ordinary consolidation/gradual grind
  (2583-2597), low-moderate volume throughout. 12:30 UTC candle unremarkable (vol 3053) --
  expected, no scheduled release. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~12:45 UTC (epoch
  1731934799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 12:45-17:00 UTC (verified, Monday, no identified specific catalyst)**: a sustained
  ~3.75hr rally with elevated volume throughout (3901-7665), climbing steadily from ~2591-2595 to a
  peak of 2615.08 (16:00 UTC) and holding, settling ~2610-2612 as volume faded -- a ~20-24pt
  sustained gain, no reversal. Resembles the already well-established "breakout holds and extends"
  shape (6 instances documented) -- not logged as a new cross-reference given the family is now
  saturated with diverse instances, treated as ordinary variation within the characterized shape.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~17:00 UTC (epoch
  1731949199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 17:00-21:15 UTC (verified, Monday)**: quiet stabilization after the Monday rally
  (2607-2613), low volume throughout, no new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-18 ~21:15 UTC (epoch
  1731964499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-18 21:15 UTC -> 2024-11-19 00:45 UTC (verified)**: very quiet, tight consolidation
  (2610-2613), low volume throughout, daily-rollover gap observed again (consistent, ~76min). No
  new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~00:45 UTC (epoch
  1731976199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-19 00:45-03:30 UTC (verified, Tuesday)**: a gradual, sustained mild rally (2612 ->
  2625.59), moderate volume throughout (1643-5218), no failure or reversal -- resembles ordinary
  continuation/drift, not matching any established family cleanly given its mild, gradual
  character. Not logged separately.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~03:30 UTC (epoch
  1731986999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-19 03:30-06:15 UTC (verified, Tuesday)**: quiet, very tight consolidation
  (2620-2625), low-moderate volume throughout. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~06:15 UTC (epoch
  1731996899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-19 06:15-09:00 UTC (verified, Tuesday)**: quiet, ordinary consolidation/mild grind
  (2617-2627), low-moderate volume throughout, no outliers. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~09:00 UTC (epoch
  1732005899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-19 09:15-11:00 UTC (verified, Tuesday, no identified catalyst)**: a sustained ~2hr
  rally with elevated volume throughout (3125-7665), climbing from ~2623 to a peak of 2636.50 and
  holding, settling ~2634-2636 as volume faded -- a ~13.5pt sustained gain, no reversal. Resembles
  the already well-established "breakout holds and extends" shape (multiple prior instances) --
  not logged as a new cross-reference, treated as ordinary variation.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~11:00 UTC (epoch
  1732013999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **LABEL CORRECTION (2026-07-25, verified)**: the checkpoint line above previously read "~19:30
  UTC" for epoch 1730827799 -- rechecked via `date -d @epoch` this iteration and the correct label
  is ~17:30 UTC (a ~2hr labeling slip, likely from estimating rather than re-verifying at write
  time). The underlying epoch value was always correct and no observation content is affected --
  this is a display-label fix only, consistent with the standing NOTĂ 2 rule (always verify via
  `date -d @epoch`, never estimate). Continuing from the correct position below.
- **2024-11-19 12:30-23:15 UTC (verified, Tuesday)**: the 12:30 UTC slot passed unremarkably (no
  scheduled US release expected on this date; O2635.77 H2636.95 L2635.09 C2635.31, ordinary
  volume) -- consistent with the many other "quiet 12:30 UTC" instances this replay. Rest of the
  stretch was ordinary choppy grind (2622-2639), volume gradually tapering into the NY-evening/Asia
  low-liquidity period (down to ~500-2000), then the usual daily-rollover gap (12:52:00 UTC ->
  14:00:00 UTC gap in this evening rollover instance, ~75min, consistent with prior instances). No
  new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-19 ~23:15 UTC (epoch
  1732058099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-19 23:15 UTC -> 2024-11-20 06:45 UTC (verified, Wed Asia/early-London session)**: very
  quiet, low volume (650-3900) tight consolidation (2618-2641), including one gradual low-intensity
  pullback (2641 peak ~04:15 UTC -> low 2618.89 ~08:15 UTC, moderate volume 3300-5400, no single
  standout candle) -- matches the already well-documented "gradual low-intensity pullback" shape,
  not logged separately. No new phenomena.
- **2024-11-20 06:45-12:30 UTC (verified)**: continued quiet consolidation (2620-2631), ordinary
  volume, then the 12:30 UTC slot passed unremarkably (O2628.41 H2631.83 L2627.09 C2631.64, vol
  3204, no scheduled release expected on this Wednesday) -- consistent with prior quiet 12:30 UTC
  instances.
- **2024-11-20 12:30-20:15 UTC (verified)**: a gradual, moderate-volume sustained rally (2624 ->
  new local high 2655.46 ~17:00 UTC, ~31pt over ~5hrs, volume 3000-6600 throughout, no single
  standout breakout candle) that then plateaus/holds (2645-2653) into the NY afternoon --
  resembles the already well-established "breakout holds and extends" shape (multiple prior
  instances), not logged as a new cross-reference.
- **2024-11-20 20:15-23:45 UTC (verified)**: quiet stabilization holding the elevated level
  (2645-2653), ordinary low volume tapering into the evening, daily-rollover gap observed again
  (12:52:19 UTC internal candle count -> confirmed ~15min-offset gap this instance, ~76min total,
  consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-20 ~23:45 UTC (epoch
  1732146299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-20 23:45 UTC -> 2024-11-21 12:15 UTC (verified, Thu Asia/London)**: very quiet, gradual
  grind higher (2652 -> new local high 2671.7 ~09:30 UTC), low-moderate volume throughout
  (700-4800), no single standout candle. 12:30 UTC slot passed unremarkably (O2667.17 H2667.37
  L2664.49 C2665.51, vol 2467). No new phenomena.
- **2024-11-21 13:30-15:30 UTC (verified, Thursday jobless-claims, DST-shifted timing)**: a
  moderate volume bump at 13:30 UTC (vol 6489, decline to 2660.45 then recovery to 2667.11 within
  the same candle) followed by ~2hrs of elevated-volume (5600-7960) two-way chop (2661-2673, no
  clean directional break) -- resembles the already well-established "sustained multi-hour two-way
  regime" shape, not logged as a new cross-reference.
- **2024-11-21 15:45-24:00 UTC (verified)**: volume faded back to ordinary (2000-6400) as the chop
  narrowed and stabilized (2668-2673), daily-rollover gap observed again (23:58:59 UTC -> Fri
  00:00:00-ish internal boundary, ~76min total, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-22 ~00:15 UTC (epoch
  1732234499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-22 00:15-12:30 UTC (verified, Friday, non-NFP)**: continued gradual, moderate-volume
  grind higher (2671 -> new highs through 2708.22 ~10:00 UTC), no single standout candle, part of
  the same multi-day rally thread already treated as ordinary "holds and extends" variation. 12:30
  UTC slot passed without a sharp reaction (O2698.27 C2703.37, marginal new high, no reversal).
- **2024-11-22 12:45-15:15 UTC (verified)**: the rally's first real pullback since 11-20 -- a
  ~24pt decline (2708.22 peak -> low 2684.47 ~14:15 UTC) over ~2.5hrs, elevated volume throughout
  (5700-8200, above baseline but not near-record) -- resembles the already-documented "normal
  pullback within an ongoing uptrend, not a full reversal" shape (2024-08-20 precedent: still well
  above the deeper rally origin, no AP2-DC-0001-style failed-breakout structure) -- not logged
  separately.
- **2024-11-22 15:15-21:59 UTC (verified)**: the pullback fully reclaimed and the rally resumed to
  fresh highs (2716.22), moderate-low volume tapering into the close. Ordinary weekend skip
  observed: Fri 21:58:59 UTC -> Sun 23:14:59 UTC (~49.3hrs, DST-shifted timing consistent with all
  post-2024-11-03 instances this replay), small ordinary reopen gap (Fri close 2716.02 -> Sun open
  ~2713.52). **Week of 2024-11-18 now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-11-24 ~23:15 UTC (epoch
  1732490099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-24 23:15 UTC -> 2024-11-25 08:30 UTC (verified, Sun reopen through Monday)**: an
  eleventh instance of the sustained multi-hour-decline family -- multi-wave decline from the
  Sunday-reopen local peak (2721.36) through a sharp single-candle spike-down (2659.54, vol 5647)
  to an episode low of 2658.23 (~05:15 UTC), ~63pt over ~5hrs, sustained moderate-elevated volume
  (4300-7900), settling ~2665-2673, not reclaimed -> **cross-reference note added to the existing
  registry entry** (not a new entry, not a DC). Monday reopen, no identified catalyst.
- Current replay position (verified via `date -d @epoch`): 2024-11-25 ~08:30 UTC (epoch
  1732523399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 11th sustained-decline instance cross-referenced).
- **2024-11-25 08:30-13:30 UTC (verified, Monday)**: quiet, tight consolidation (2668-2688),
  ordinary volume, then a moderate step-change at the DST-shifted 13:30 UTC slot (vol 6634,
  O2685.3 C2681.26).
- **2024-11-25 13:45-17:15 UTC (verified)**: a twelfth instance of the sustained multi-hour-decline
  family -- continuously near-record volume (6021-9910) drove price from ~2688 down to a new
  session low of 2624.62 by 17:15 UTC, ~63.3pt over ~3.75hrs, tying the Eleventh instance (this
  same trading day's overnight decline) as the largest-magnitude instance observed so far, settling
  ~2625-2628, not reclaimed -> **cross-reference note added to the existing registry entry** (not a
  new entry, not a DC). Second same-session-day record-magnitude instance in a row -- notable
  clustering flagged for continued tracking, not yet enough data to distinguish signal from
  coincidence.
- Current replay position (verified via `date -d @epoch`): 2024-11-25 ~17:59 UTC (epoch
  1732557599), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 12th sustained-decline instance cross-referenced).
- **2024-11-25 17:59-23:15 UTC (verified)**: the twelfth sustained-decline instance extended
  marginally further (new low 2615.62 ~18:15 UTC) then stabilized/consolidated (2617-2627),
  ordinary tapering volume, daily-rollover gap observed again (23:11:59 UTC -> ~00:00:00 UTC
  boundary, ~76min, consistent with prior instances). No further new phenomena.
- **2024-11-25 23:30 UTC -> 2024-11-26 01:00 UTC (verified)**: a tenth instance of the
  sweep-reclaim-extend family -- a sharp sweep to 2605.1 (vol 3487, moderate) reclaimed and
  extended to a fresh local high of 2629.43 within ~1.5hrs, ~3.4pt above the pre-sweep origin ->
  **cross-reference note added to the existing registry entry** (not a new entry, not a DC).
- **2024-11-26 01:00-03:15 UTC (verified)**: the reclaim held, tight consolidation (2623-2632),
  ordinary volume. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-26 ~03:15 UTC (epoch
  1732590899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 10th sweep-reclaim-extend instance cross-referenced).
- **2024-11-26 03:15-13:00 UTC (verified, Tuesday)**: quiet, ordinary variation throughout -- a
  gradual decline (2628 -> low 2610.84 ~08:00 UTC), moderate volume, no outliers, then a recovery
  back to ~2633-2634 by 13:00 UTC. 12:30 UTC slot passed unremarkably (O2631.75 C2630.38, vol
  3805). No new phenomena.
- **2024-11-26 13:00-16:00 UTC (verified)**: a marginal new high (2641.94, 13:00 UTC) failed
  within the same candle and led into a moderate sustained decline (near-record volume 5300-8056)
  to a low of 2616.71 (~14:30 UTC, ~25.2pt), then partial recovery/stabilization to ~2626-2631 by
  16:00 UTC -- settling close to, not clearly below, the pre-breakout baseline (~2632-2633).
  Structurally a clean match to the AP2-DC-0001 mechanism, but given 13 addenda already on file for
  this now well-saturated family and no novel structural nuance here, applied the same
  "avoid over-documenting a saturated pattern" reasoning used for the "breakout holds and extends"
  family -- not filed as a new addendum, tracked here as ordinary continuation instead.
- Current replay position (verified via `date -d @epoch`): 2024-11-26 ~16:59 UTC (epoch
  1732640399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-26 16:59 UTC -> 2024-11-27 01:30 UTC (verified)**: quiet, ordinary consolidation/mild
  grind (2619-2634), volume tapering into the evening and Asia session, daily-rollover gap
  observed again (~76min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-27 ~01:30 UTC (epoch
  1732670999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-27 01:30-12:30 UTC (verified, Wednesday, day before US Thanksgiving)**: quiet, ordinary
  gradual grind higher (2628 -> new highs through 2655.03), moderate volume, no outliers. 12:30 UTC
  slot passed unremarkably (O2653.01 C2653.71, vol 3823).
- **2024-11-27 13:30-17:15 UTC (verified, DST-shifted US data slot)**: a moderate step-change at
  13:30 UTC (vol 6243) opened a moderate two-way decline (peak ~2658 -> low 2635.55 ~15:15 UTC,
  ~22.8pt over ~1.5hrs, elevated volume 5400-8400) -- resembles the well-established sustained
  multi-hour-decline family at the smaller end of its observed magnitude range; given how saturated
  this family is (12 instances on file), not logged as a further cross-reference, tracked here as
  ordinary continuation. Volume then faded (4200-5388) as price stabilized 2635-2644 by 17:15 UTC.
- Current replay position (verified via `date -d @epoch`): 2024-11-27 ~17:15 UTC (epoch
  1732727699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-27 17:15-23:15 UTC (verified)**: very quiet, tight consolidation (2633-2640), low
  volume throughout (386-3617, tapering into the evening ahead of the US Thanksgiving holiday),
  daily-rollover gap observed again (~76min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-27 ~23:15 UTC (epoch
  1732749299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-27 23:15 -> 2024-11-28 00:45 UTC (verified, US Thanksgiving Day)**: extremely thin
  holiday liquidity (volume 230-1346, the lowest sustained stretch observed this replay), tight
  range 2634-2639.
- **2024-11-28 00:45-02:45 UTC (verified)**: a modest decline (2637 -> low 2620.96, ~15.4pt over
  ~45min, elevated volume 5400-6700 -- notably active for an otherwise holiday-thin session) then
  recovery/stabilization to ~2625-2629. Magnitude too modest to match any established family
  cleanly (partial, not full, extension past origin); notable mainly for occurring during otherwise
  extreme holiday-thin liquidity -- not logged as a new Registry entry given the modest scale.
- **2024-11-28 02:45-07:45 UTC (verified)**: quiet, ordinary consolidation (2625-2640), volume
  gradually normalizing (1124-3577) as the holiday session progressed. No further new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-28 ~07:45 UTC (epoch
  1732779899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-28 07:45-17:45 UTC (verified, remainder of US Thanksgiving Day)**: quiet, ordinary
  variation throughout -- a gradual grind (2635 -> 2649.7) then a mild pullback (2648 -> 2636.33),
  low-moderate volume (861-4968) consistent with holiday-thinned liquidity, 12:30 UTC slot passed
  unremarkably (no scheduled release, market holiday). No new phenomena. **Thanksgiving Day now
  complete without any events departing from the established shapes.**
- Current replay position (verified via `date -d @epoch`): 2024-11-28 ~17:45 UTC (epoch
  1732815899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-28 17:45-19:30 UTC (verified)**: very quiet, tight consolidation (2636-2640), low
  volume. **Then an unusual intraday gap**: Thu Nov 28 19:29:59 UTC -> Thu Nov 28 23:14:59 UTC
  (~3.75hrs, WITHIN the same calendar day, not the usual ~76min midnight-UTC daily rollover) -- no
  price discontinuity across the gap (~2638 both sides), consistent with a mechanical/session
  artifact (US Thanksgiving Day early-close then Globex reopen) rather than a market event, same
  category as the previously-noted longer Labor Day gap. Not logged as a new phenomenon.
- **2024-11-28 23:15 UTC -> 2024-11-29 05:45 UTC (verified, post-Thanksgiving Friday, shortened US
  session)**: a gradual overnight rally (2637 -> new highs through 2664.39), moderate volume
  (3500-5600), then holding/consolidating at the elevated level (2656-2664) -- resembles the
  already well-established "breakout holds and extends" shape, not logged as a new
  cross-reference.
- Current replay position (verified via `date -d @epoch`): 2024-11-29 ~05:45 UTC (epoch
  1732859099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-29 05:45-12:30 UTC (verified, Friday post-Thanksgiving, shortened US session)**: quiet,
  ordinary consolidation holding the elevated level (2654-2666), moderate volume, no outliers.
  12:30 UTC slot passed unremarkably (O2662.14 C2659.44, vol 2701).
- **2024-11-29 12:30-16:15 UTC (verified)**: a modest, gradual two-way decline (2663.33 -> low
  2650.64, ~12.7pt over ~2.5hrs, moderate-elevated volume 5000-6454) that fully recovered
  (back to 2662.05 by 16:15 UTC) -- ordinary variation, not matching any established family's
  scale or shape closely enough to log. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-11-29 ~16:15 UTC (epoch
  1732896899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-11-29 16:15-19:45 UTC (verified)**: quiet, tight consolidation (2652-2662), volume
  tapering as the shortened post-Thanksgiving session wound down. **Unusual weekend gap**: Fri
  Nov 29 19:44:59 UTC -> Sun Dec 1 23:14:59 UTC (~51.5hrs, longer than the standard ~49.3hr weekend
  skip) -- explained by the early Friday close following the US Thanksgiving holiday (COMEX/CME
  early-close convention), same category as the previously-noted Labor Day extended-gap precedent;
  small ordinary reopen gap, no price discontinuity of note. **November 2024 now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-12-02 ~00:30 UTC (epoch
  1733099399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-02 00:30-04:00 UTC (verified, Monday reopen)**: a moderate multi-wave decline right at
  the Sunday-reopen/Monday transition (~2646 pre-weekend level -> low 2622.97 ~01:15 UTC, ~23pt
  over ~3.5hrs, moderate-elevated volume 3100-6848), settling ~2624-2631, not reclaimed --
  resembles the well-established sustained multi-hour-decline family (already 12 instances,
  including two prior Monday-reopen instances); given the family's saturation and no novel
  structural nuance here, not logged as a further cross-reference, tracked as ordinary
  continuation.
- Current replay position (verified via `date -d @epoch`): 2024-12-02 ~04:00 UTC (epoch
  1733111999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-02 04:00-12:30 UTC (verified, Monday)**: quiet, ordinary grind (2622-2646), moderate
  volume throughout, no outliers. 12:30 UTC slot passed unremarkably (O2642.18 C2641.36, vol 3828,
  no scheduled release expected). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-02 ~12:45 UTC (epoch
  1733143499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-02 12:45-17:15 UTC (verified, Monday, no identified catalyst)**: a sustained ~5hr
  two-way regime, range ~2637-2652, sustained elevated volume throughout (5600-8100, no single
  extreme spike), gradual rally to 2651.82 (~14:00 UTC) then gradual decline back to 2638.58
  (~16:15 UTC), settling ~2638-2644 as volume tapered (3700-6200) -- resembles the already
  well-established "sustained multi-hour two-way regime" shape, not logged as a new
  cross-reference.
- Current replay position (verified via `date -d @epoch`): 2024-12-02 ~17:15 UTC (epoch
  1733159699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-02 17:15-23:15 UTC (verified)**: quiet, tight consolidation (2633-2644), volume
  normalizing back to ordinary levels (564-4457) as the earlier two-way regime faded, daily-
  rollover gap observed again (~76min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-02 ~23:15 UTC (epoch
  1733181299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-02 23:15 -> 2024-12-03 12:45 UTC (verified, Tuesday)**: quiet, ordinary variation
  throughout -- a mild two-way move overnight (2645.32 -> 2634.14, vol up to 5310, modest),
  gradual grind higher through Asia/London (to new highs 2650.11), then consolidating/mild
  pullback into the US morning (2638-2648). 12:30 UTC slot passed unremarkably (O2638.76
  C2640.39, vol 2822, no scheduled release expected). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-03 ~12:45 UTC (epoch
  1733229899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-03 12:45-16:15 UTC (verified, Tuesday)**: a gradual rally (2640 -> new high 2655.63,
  ~14:00 UTC) failed and reversed into a sustained heavy-volume decline (5162-8732, near-record
  8732 the single largest candle) to a low of 2635.26 (~15:00 UTC), settling ~2638-2643, modestly
  below the pre-rally baseline -- structurally a clean match to AP2-DC-0001, but with no novel
  structural nuance (single clean decline, no multi-attempt reclaim battle) and this family
  already at 13 addenda; applied the same "avoid over-documenting a saturated pattern" reasoning
  used for the 11-26 13:00 UTC instance -- not filed as a new addendum, tracked as ordinary
  continuation.
- Current replay position (verified via `date -d @epoch`): 2024-12-03 ~16:15 UTC (epoch
  1733242499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-03 16:15 UTC -> 2024-12-04 00:45 UTC (verified)**: quiet recovery/stabilization
  (2640-2649) after the earlier decline, volume tapering to ordinary/low levels (600-4957) through
  the evening, daily-rollover gap observed again (~76min, consistent with prior instances). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-04 ~00:45 UTC (epoch
  1733273099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-04 00:45-12:45 UTC (verified, Wednesday)**: quiet, ordinary variation throughout -- a
  gradual grind higher (2637 -> new highs through 2651.41 ~06:15 UTC), a mild pullback
  (2639.56 ~08:15 UTC), then consolidating 2641-2647, moderate volume, no outliers. 12:30 UTC slot
  passed unremarkably (O2643.32 C2643.18, vol 3191, no scheduled release expected). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-04 ~12:45 UTC (epoch
  1733316299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-04 12:45-16:15 UTC (verified, Wednesday)**: an eleventh instance of the
  sweep-reclaim-extend family -- a sweep from ~2643 down to 2632.42 (vol 5821), then a sustained
  ~2.25hr reclaim (elevated volume 5000-7000 throughout) extending to a fresh local high of
  2657.13, ~14pt above the pre-sweep origin -- larger/more sustained than the two most recent
  prior instances -> **cross-reference note added to the existing registry entry** (not a new
  entry, not a DC). Settling ~2653-2656 by 16:15 UTC.
- Current replay position (verified via `date -d @epoch`): 2024-12-04 ~16:15 UTC (epoch
  1733328899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 11th sweep-reclaim-extend instance cross-referenced).
- **2024-12-04 16:15 UTC -> 2024-12-05 00:45 UTC (verified)**: quiet consolidation holding the
  elevated level (2646-2656), volume tapering to ordinary/low levels (508-3652) through the
  evening, daily-rollover gap observed again (~76min, consistent with prior instances). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-05 ~00:45 UTC (epoch
  1733359499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-05 00:45-13:15 UTC (verified, Thursday)**: quiet, ordinary variation throughout, 12:30
  UTC slot passed unremarkably (O2649.18 C2650.87, vol 3467).
- **2024-12-05 13:30-16:15 UTC (verified, DST-shifted jobless-claims slot)**: a moderate step-change
  at 13:30 UTC (vol 6715) opened a sustained decline (heavy volume 4500-7100 throughout) from a
  peak of 2650.62 to a low of 2631.96 (~15:30 UTC, ~18.7pt over ~2hrs), then a partial reclaim to
  2643.43 by 16:00 UTC -- not a clean extension past the pre-decline peak, resembles the
  well-established sustained multi-hour-decline family at typical magnitude; given the family's
  saturation, not logged as a further cross-reference, tracked as ordinary continuation.
- Current replay position (verified via `date -d @epoch`): 2024-12-05 ~16:15 UTC (epoch
  1733415299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-05 16:15-21:15 UTC (verified)**: the 13:30 UTC decline continued further after its
  partial reclaim, extending to a final low of 2623.55 (~17:45 UTC) -- total ~27pt from the
  13:30 UTC peak (2650.62) over ~4.25hrs, sustained moderate-elevated volume throughout
  (1500-7100 across the full arc) -- consistent with the well-established sustained
  multi-hour-decline family, magnitude within its typical range. Settled ~2627-2632 by 21:15 UTC
  as volume normalized. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-05 ~21:15 UTC (epoch
  1733433299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-05 21:15 UTC -> 2024-12-06 05:15 UTC (verified, genuine NFP Friday)**: quiet overnight
  consolidation, daily-rollover gap observed again (~76min, consistent), then a sweep from ~2630 to
  2612.82 (~01:00 UTC, vol 5972) reclaimed and extended to a fresh high of 2644.48 by ~04:15 UTC --
  ~14.5pt above the pre-sweep origin over ~3.25hrs -- typical-magnitude instance of the
  well-established sweep-reclaim-extend family (11 prior instances); not logged as a further
  cross-reference given the family's saturation, tracked as ordinary continuation. Settled
  ~2641-2644 by 05:15 UTC.
- Current replay position (verified via `date -d @epoch`): 2024-12-06 ~05:15 UTC (epoch
  1733462099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-06 05:15-13:00 UTC (verified, genuine NFP Friday)**: quiet, ordinary variation
  throughout, 12:30 UTC slot passed unremarkably (O2639.53 C2639.33, vol 2782, not the actual
  DST-shifted NFP time).
- **2024-12-06 13:30-16:15 UTC (verified, genuine NFP release, DST-shifted)**: a wide two-way
  spike at 13:30 UTC (O2635.22 H2643.39 L2631.23 C2635.81, vol 10129, near-record) opened a
  sustained decline with near-record volume (7300-10129) to a low of 2624.1 (~14:00 UTC, ~19.3pt
  from the spike high), then a partial recovery/consolidation to 2634-2640 by 16:15 UTC as volume
  tapered (4900-6800) -- structurally a clean AP2-DC-0001-style instance, but of typical magnitude
  and no novel structural nuance for this now heavily-saturated family (13 addenda already);
  applying the same reasoning as recent instances, not filed as a new addendum.
- Current replay position (verified via `date -d @epoch`): 2024-12-06 ~16:15 UTC (epoch
  1733501699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-06 16:15-21:59 UTC (verified)**: quiet stabilization/consolidation (2631-2642) after
  the NFP event, ordinary low volume tapering into the close. Ordinary weekend skip observed: Fri
  21:58:59 UTC -> Sun 23:14:59 UTC (~49.3hrs, DST-shifted timing consistent with all post-2024-11-03
  instances), small ordinary reopen gap (Fri close ~2632-2634 -> Sun open ~2643). **Week of
  2024-12-02 now complete.**
- Current replay position (verified via `date -d @epoch`): 2024-12-09 ~00:15 UTC (epoch
  1733703299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-09 00:15-03:45 UTC (verified, Monday reopen)**: a sharp overnight rally (2630.92 ->
  2650.62, ~19.7pt, vol 6438-6892) that held its gains through a mild pullback/consolidation
  (2640-2646) -- resembles the already well-established "breakout holds and extends" shape, not
  logged as a new cross-reference. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-09 ~03:45 UTC (epoch
  1733715899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-09 03:45-12:30 UTC (verified, Monday)**: quiet, ordinary grind (2635-2660), moderate
  volume, no outliers. 12:30 UTC slot passed unremarkably (O2658.18 C2656.32, vol 3180, no
  scheduled release expected on a Monday).
- **2024-12-09 12:30-16:45 UTC (verified)**: a sustained ~4hr rally (2656 -> new highs through
  2676.42 ~15:15 UTC, ~20.4pt, moderate-elevated volume 3200-7186 throughout, no identified
  catalyst) that then held its gains through a mild pullback/consolidation (2666-2670) -- resembles
  the already well-established "breakout holds and extends" shape, not logged as a new
  cross-reference.
- Current replay position (verified via `date -d @epoch`): 2024-12-09 ~16:45 UTC (epoch
  1733762699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-09 16:45 UTC -> 2024-12-10 01:15 UTC (verified)**: quiet stabilization holding the
  elevated level (2657-2670), ordinary volume tapering into the evening, daily-rollover gap
  observed again (~76min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-10 ~01:15 UTC (epoch
  1733793299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-10 01:15-12:30 UTC (verified, Tuesday)**: quiet, ordinary grind higher (2663-2677),
  moderate volume, no outliers. 12:30 UTC slot passed unremarkably (O2671.44 C2672.3, vol 3154).
- **2024-12-10 12:30-16:15 UTC (verified)**: 13:30 UTC slot passed without a sharp reaction
  (O2675.39 C2677.77, vol 2609), followed by a sustained ~4hr rally (2670 -> new highs through
  2691.87, ~21.5pt, elevated volume 4100-6874 throughout, no identified catalyst) -- resembles the
  already well-established "breakout holds and extends" shape, not logged as a new
  cross-reference.
- Current replay position (verified via `date -d @epoch`): 2024-12-10 ~16:15 UTC (epoch
  1733847299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-10 16:15-21:15 UTC (verified)**: quiet stabilization holding the elevated level
  (2690-2696), ordinary low volume tapering into the evening. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-10 ~21:15 UTC (epoch
  1733865299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-10 21:15 UTC -> 2024-12-11 00:45 UTC (verified)**: very quiet, low volume, daily-
  rollover gap observed again (~76min, consistent with prior instances), then a gradual continued
  grind higher to fresh highs (2700.45), moderate volume -- ordinary continuation of the
  multi-session rally already treated as "breakout holds and extends" variation, not logged
  separately. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-11 ~00:45 UTC (epoch
  1733877899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-11 00:45-06:45 UTC (verified, Wednesday)**: quiet consolidation holding the elevated
  level (2693-2704), then a multi-wave decline (peak 2704.28 ~03:45 UTC -> low 2674.77 ~05:15 UTC,
  ~29.5pt over ~1.5hrs, moderate volume 2100-5127) partially reclaimed (recovery to 2697.61 by
  06:15 UTC, not fully extending past the pre-decline peak) -- magnitude/structure typical of the
  well-established sustained-decline/sweep-reclaim families, no novel nuance; not logged as a new
  cross-reference given their saturation.
- Current replay position (verified via `date -d @epoch`): 2024-12-11 ~06:45 UTC (epoch
  1733899499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-11 06:45-12:30 UTC (verified, Wednesday, genuine US CPI day)**: quiet, ordinary
  consolidation (2685-2699), moderate volume, no outliers. 12:30 UTC slot passed unremarkably
  (O2696.43 C2696.23, vol 4298).
- **2024-12-11 13:30-14:45 UTC (verified, DST-shifted CPI release)**: a moderate step-change at
  13:30 UTC (vol 7389) opened a rally that held and extended to a new high (2704.28, ~14:00 UTC),
  sustained elevated volume (5100-6624) throughout, settling ~2700-2702 -- resembles the already
  well-established "breakout holds and extends" shape, not logged as a new cross-reference.
- Current replay position (verified via `date -d @epoch`): 2024-12-11 ~14:44 UTC (epoch
  1733928299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-11 14:44-18:15 UTC (verified)**: the CPI-driven rally continued far further than
  initially assessed -- sustained elevated volume (3050-7679) pushing to a fresh high of 2720.08
  (~17:15 UTC), a genuine ~30-32pt sustained gain over ~4.75hrs from the ~2688-2698 pre-event
  baseline, holding well, one of the largest-magnitude instances of the "breakout holds and
  extends" family observed so far -> **cross-reference note added to the existing registry entry**
  (seventh instance; not a new entry, not a DC). Settled ~2714-2720 by 18:15 UTC as volume
  normalized.
- Current replay position (verified via `date -d @epoch`): 2024-12-11 ~18:15 UTC (epoch
  1733940899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; 7th "breakout holds and extends" instance cross-referenced).
- **2024-12-11 18:15 UTC -> 2024-12-12 00:15 UTC (verified)**: quiet stabilization holding the
  elevated level (2716-2721), ordinary low volume tapering into the evening, daily-rollover gap
  observed again (~76min, consistent with prior instances). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-12 ~00:15 UTC (epoch
  1733962499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-12 00:15 UTC -> 05:15 UTC (verified)**: a modest breakout-fail during thin Asian-session
  liquidity (~01:00 UTC, no calendar catalyst) -- a marginal new high (2726.05) failed within the
  same candle (vol 5788), followed by a sustained decline through ~2699-2705 (~26.8pt off the high)
  over roughly two hours, then a slow low-volume (1500-2400) grind back up to ~2713 by 05:15 UTC,
  reclaiming over half the decline. Textbook-shape match to the AP2-DC-0001 family (14th such
  instance observed informally) but with no calendar catalyst, ordinary Asian-session magnitude, and
  no novel structural nuance -- given 13 addenda already on file for this mechanism, not logged as a
  new addendum. No new phenomena otherwise; no other gaps or anomalies this batch.
- Current replay position (verified via `date -d @epoch`): 2024-12-12 ~05:15 UTC (epoch
  1733980499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-12 05:15 UTC -> 12:45 UTC (verified)**: quiet, unremarkable ranging (~2707-2720) through
  the remainder of Asian session and into London open (~07:00-08:00 UTC), a mild volume pickup
  consistent with the ordinary London-open pattern already documented; no spikes, no gaps, no
  breakout/decline structures. Approaching the 12:30 UTC US data slot with no unusual pre-event
  positioning. No new phenomena this batch.
- Current replay position (verified via `date -d @epoch`): 2024-12-12 ~12:45 UTC (epoch
  1734007499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-12 12:45 UTC -> 17:00 UTC (verified)**: a genuine US PPI-release-day (November PPI,
  DST-shifted 13:30 UTC slot) sustained decline -- from a ~2708-2711 baseline, a gradual-then-
  escalating decline (no initial breakout spike) with near-record volume (peak 8812) over ~3hrs to
  an episode low of 2675.09 (~15:45 UTC), a ~33.8pt move, then stabilizing 2678-2683 as volume
  tapered (4578->3346) with no reclaim of the pre-event level. Textbook match to the already-
  saturated "sustained multi-hour decline" family (12th+ instance; that family's 3rd instance
  already established the 12:30 UTC data-slot as a valid trigger context) -- no novel structural
  nuance, not logged as a new instance note given the family's saturation. No other phenomena this
  batch.
- Current replay position (verified via `date -d @epoch`): 2024-12-12 ~17:00 UTC (epoch
  1734022799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-12 17:00 UTC -> 23:45 UTC (verified)**: quiet stabilization holding the post-PPI level
  (2679-2687), ordinary tapering volume through the New York afternoon and evening, ordinary
  ~76min daily-rollover gap observed again (21:58:59 -> 23:14:59 UTC, price flat across the gap:
  2680.6 -> 2680.58), price continuing to hold ~2680-2681 into the new trading day. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-12 ~23:45 UTC (epoch
  1734047099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-12 23:45 UTC -> 2024-12-13 04:45 UTC (verified, now Friday, non-NFP)**: an ordinary
  modest overnight Asian-session build from ~2680 to ~2692 (00:45-02:15 UTC, moderate volume up to
  4674), then quiet ranging 2684-2691 with ordinary volume (1650-3400) through the remainder of the
  Asian session. No spikes, no gaps, no breakout/decline structures. No new phenomena this batch.
- Current replay position (verified via `date -d @epoch`): 2024-12-13 ~04:45 UTC (epoch
  1734065099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-13 04:45 UTC -> 10:15 UTC (verified)**: quiet ranging (2682-2690) through the remainder
  of Asia into London pre-open, then a gradual, moderate-volume (peak 4849, not near-record)
  multi-candle grind lower from ~2683 to ~2667-2670 (~08:45-10:15 UTC, ~15pt over ~1.5hrs) --
  ordinary London-morning variation, no sharp single-candle break, no data-slot timing, no clean
  match to any saturated family shape. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-13 ~10:15 UTC (epoch
  1734084899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-13 10:15 UTC -> 14:30 UTC (verified)**: quiet ranging (2662-2672) through late London
  morning, then a gradual, moderate-volume (4400-6090, not near-record) grind lower spanning the
  12:30/13:30 UTC window -- no sharp single-candle break, no genuine data-release-magnitude reaction
  (this is a non-NFP/CPI/PPI/FOMC Friday); cumulative ~13pt drift from ~2672 to ~2659-2662 over
  ~1.75hrs, ordinary pre-weekend positioning-type variation. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-13 ~14:30 UTC (epoch
  1734100199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-13 14:30 UTC -> 16:45 UTC (verified)**: continued ordinary NY-session chop, 2654-2664
  range, moderate volume (3100-6790) with no sustained directional break and no calendar-catalyst
  timing (consistent with a quiet pre-weekend Friday). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-13 ~16:45 UTC (epoch
  1734108299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-13 16:45 UTC -> 18:45 UTC (verified)**: continued gradual, low-moderate-volume
  (2750-3600) grind lower through the NY afternoon, 2652-2664, no spikes, no sharp breaks -- ordinary
  pre-weekend drift. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-13 ~18:45 UTC (epoch
  1734115499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-13 18:45 UTC -> 21:59 UTC (verified)**: quiet Friday-afternoon grind lower into the
  close, 2646-2652, ordinary low-tapering volume (1000-3400), settling ~2648 by market close. Then
  the ordinary ~49.3hr DST-shifted weekend gap (Fri 21:58:59 UTC -> Sun 23:14:59 UTC), consistent
  with every prior weekend transition. Sunday reopen flat (2648.14 -> 2649.75), no price
  discontinuity. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-15 ~23:15 UTC (epoch
  1734304499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-15 23:15 UTC -> 2024-12-16 01:30 UTC (verified, Sunday reopen into Monday Asian
  session)**: very quiet, low-volume (500-4500) ranging 2643-2656, ordinary Sunday-evening/early-
  Monday character, no spikes, no gaps. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~01:30 UTC (epoch
  1734312599), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 01:30 UTC -> 03:45 UTC (verified)**: quiet ranging 2650-2656 through the Asian
  session, ordinary low volume (1750-3800). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~03:45 UTC (epoch
  1734320699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 03:45 UTC -> 06:00 UTC (verified)**: very quiet, narrow-range (2649-2656) Asian
  session, ordinary low volume (1000-2800). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~06:00 UTC (epoch
  1734328799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 06:00 UTC -> 08:15 UTC (verified)**: continued very quiet, narrow-range (2651-2656)
  trading through London pre-open, ordinary low volume (1670-2500). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~08:15 UTC (epoch
  1734336899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 08:15 UTC -> 10:15 UTC (verified)**: ordinary London-morning ranging (2654-2662),
  moderate volume (1700-4470), no spikes, no sharp breaks. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~10:15 UTC (epoch
  1734344099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 10:15 UTC -> 12:15 UTC (verified)**: ordinary quiet grind higher, 2657-2664, ordinary
  volume (1770-2650), no spikes, approaching the 12:30 UTC window with no unusual pre-event
  positioning (Monday, no major scheduled US data release expected). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~12:15 UTC (epoch
  1734351299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 12:15 UTC -> 14:15 UTC (verified)**: the 12:30 UTC candle showed only a modest,
  ordinary move (vol 3570, no sharp break) consistent with no major scheduled release; continued
  ordinary two-way chop through the NY morning, 2658-2664, moderate volume (2000-5000). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~14:15 UTC (epoch
  1734358499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 14:15 UTC -> 16:15 UTC (verified)**: ordinary gradual grind lower through the NY
  session, ~2663 to ~2653-2655 (~13pt over 2hrs), moderate volume (4000-5750, not near-record), no
  sharp single-candle break, no calendar-catalyst timing. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~16:15 UTC (epoch
  1734365699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 16:15 UTC -> 18:15 UTC (verified)**: continued quiet, narrow-range (2648-2656)
  trading through the NY afternoon, ordinary tapering volume (2300-4600). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~18:15 UTC (epoch
  1734372899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 18:15 UTC -> 23:15 UTC (verified)**: quiet, narrow-range (2651-2655) grind through
  the NY evening, ordinary low volume tapering (2300 -> 550), ordinary ~76min daily-rollover gap
  observed again (21:58:59 -> 23:14:59 UTC, price flat across the gap: 2652.64 -> 2652.76). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-16 ~23:15 UTC (epoch
  1734390899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-16 23:15 UTC -> 2024-12-17 01:15 UTC (verified, now Tuesday)**: very quiet, low-volume
  (350-2000) Asian-session open, narrow range 2651-2657, mild volume pickup toward 01:00 UTC. No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~01:15 UTC (epoch
  1734398099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 01:15 UTC -> 03:30 UTC (verified)**: ordinary quiet ranging 2651-2659 through the
  Asian session, ordinary low-moderate volume (1450-3730). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~03:30 UTC (epoch
  1734406199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 03:30 UTC -> 05:30 UTC (verified)**: continued very quiet, narrow-range (2649-2656)
  Asian session, ordinary low volume (1030-2040). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~05:30 UTC (epoch
  1734413399), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 05:30 UTC -> 07:30 UTC (verified)**: ordinary mild dip-and-recover into London
  pre-open, 2646-2656, moderate volume (2200-4240), no sharp breaks. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~07:30 UTC (epoch
  1734420599), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 07:30 UTC -> 09:30 UTC (verified)**: ordinary gradual London-morning grind lower,
  ~2657 to ~2642-2645 (~15pt over ~2hrs), moderate volume (2400-4600, not near-record), no sharp
  single-candle break, no calendar-catalyst timing. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~09:30 UTC (epoch
  1734427799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 09:30 UTC -> 11:30 UTC (verified)**: the gradual London-morning drift continued at
  the same modest pace, ~2642 to ~2636-2640 (cumulative ~19pt over ~4hrs since 07:30), moderate
  tapering volume (1700-3600), no acceleration, no calendar-catalyst timing. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~11:30 UTC (epoch
  1734434999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 11:30 UTC -> 14:30 UTC (verified)**: an ordinary 12:30 UTC candle (vol 3053, no
  unusual reaction, no major scheduled release identified for this Tuesday); continued gentle chop
  2634-2646 with a brief ~10pt dip-and-reclaim (2633.12 low at ~13:45 UTC, back to 2641 within the
  hour), moderate volume (4300-5300, not near-record). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~14:30 UTC (epoch
  1734445799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 14:30 UTC -> 16:30 UTC (verified)**: continued ordinary NY-session chop, 2634-2643,
  moderate volume (4000-6040), no sustained directional break. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~16:30 UTC (epoch
  1734452999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 16:30 UTC -> 18:30 UTC (verified)**: ordinary gentle recovery, 2637-2648, moderate
  volume (2600-3500), no sharp breaks. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~18:30 UTC (epoch
  1734460199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 18:30 UTC -> 23:15 UTC (verified)**: quiet, narrow-range (2643-2647) grind through
  the NY evening, ordinary low volume tapering (1800 -> 500), ordinary ~76min daily-rollover gap
  observed again (21:58:59 -> 23:14:59 UTC, price flat across the gap: 2646.39 -> 2646.48). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-17 ~23:15 UTC (epoch
  1734477299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-17 23:15 UTC -> 2024-12-18 01:15 UTC (verified, now Wednesday)**: very quiet, low-volume
  (190-3300) Asian-session open, mild grind from 2645 to ~2650, no spikes. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~01:15 UTC (epoch
  1734484499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 01:15 UTC -> 03:15 UTC (verified)**: quiet consolidation 2646-2652, moderate volume
  (1650-3300), ahead of today's scheduled FOMC decision (Dec 18, typically ~19:00 UTC post-DST) --
  no unusual pre-event positioning yet. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~03:15 UTC (epoch
  1734491699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 03:15 UTC -> 05:15 UTC (verified)**: ordinary quiet Asian-session ranging, 2642-2649,
  low volume (1360-3210). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~05:15 UTC (epoch
  1734498899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 05:15 UTC -> 07:15 UTC (verified)**: ordinary quiet ranging 2644-2650, ordinary
  volume (1400-2760). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~07:15 UTC (epoch
  1734506099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 07:15 UTC -> 09:15 UTC (verified)**: ordinary continued London-morning chop,
  2642-2650, moderate volume (2000-2980). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~09:15 UTC (epoch
  1734513299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 09:15 UTC -> 11:15 UTC (verified)**: very quiet, narrow-range (2645-2650) consolidation,
  low volume (1480-2990) -- consistent with a pre-FOMC calm ahead of today's rate decision (typically
  ~19:00 UTC post-DST). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~11:15 UTC (epoch
  1734520499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 11:15 UTC -> 13:45 UTC (verified)**: an ordinary 12:30 UTC candle (vol 1523, no
  reaction, no scheduled release expected at this slot today); a mild NY-morning volume pickup
  (3460-4280) with choppy two-way action 2641-2648, no clean directional break -- ordinary pre-FOMC
  jitter ahead of today's ~19:00 UTC rate decision. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~13:45 UTC (epoch
  1734529499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 13:45 UTC -> 15:45 UTC (verified)**: a gradual, sustained NY-morning decline building
  ahead of today's FOMC, ~2646 to ~2635 (~11pt over 2hrs), moderate escalating volume (3600-5560,
  not near-record), no sharp single-candle break -- matches the already-saturated "sustained
  multi-hour decline" family, no novel structural nuance, not logged. Continuing to watch closely
  into the ~19:00 UTC FOMC decision window. No new phenomena otherwise.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~15:45 UTC (epoch
  1734536699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 15:45 UTC -> 17:30 UTC (verified)**: ordinary NY-session chop, 2633-2640, moderate
  volume (3000-4200), no clean directional break -- continued pre-FOMC positioning ahead of the
  ~19:00 UTC decision. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~17:30 UTC (epoch
  1734542999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-18 17:30 UTC -> 23:15 UTC (verified)**: today's FOMC rate decision (19:00 UTC,
  DST-shifted) produced a genuine major event -- the 19:00 UTC candle opened directly into a sharp
  decline with no prior breakout (O2635.65 H2635.67 L2615.32 C2616.6, vol 8430, near-record),
  followed by ~2.5hrs of sustained near-record volume (7 consecutive candles 6138-7943) driving
  price from ~2635-2640 down to an episode low of 2583.69 (~21:45 UTC, ~52pt decline), then
  stabilizing ~2583-2589 as volume faded -- **cross-reference note added to the existing
  "sustained multi-hour decline" Observation Registry entry** (thirteenth instance; not a new DC,
  no breakout component so not filed under AP2-DC-0001 -- this is the first FOMC instance to show
  the decline-first no-breakout shape, distinct from the 2024-09-18 breakout-fail FOMC instance and
  the 2024-11-07 hold instance; reinforces that FOMC catalyst type alone doesn't predict reaction
  shape). Ordinary ~76min daily-rollover gap observed again afterward (21:58:59 -> 23:14:59 UTC).
  No other new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-18 ~23:15 UTC (epoch
  1734563699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged count; sustained-decline family cross-referenced with 13th instance, the
  first FOMC-tied decline-first instance).
- **2024-12-18 23:15 UTC -> 2024-12-19 01:15 UTC (verified, now Thursday)**: quiet consolidation
  holding the post-FOMC level (2583-2602), ordinary low-moderate volume (930-2340, one mild pickup
  to 4674 on a modest recovery push), no new sharp moves. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~01:15 UTC (epoch
  1734570899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 01:15 UTC -> 03:15 UTC (verified)**: ordinary partial reclaim of the FOMC decline,
  ~2595 to ~2618, moderate volume (1640-4670), then quiet chop 2606-2618. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~03:15 UTC (epoch
  1734578099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 03:15 UTC -> 05:15 UTC (verified)**: very quiet, narrow-range (2606-2613) Asian
  session, ordinary low volume (1170-2270). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~05:15 UTC (epoch
  1734585299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 05:15 UTC -> 07:15 UTC (verified)**: ordinary quiet ranging 2603-2615, ordinary
  volume (1280-3050), no spikes. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~07:15 UTC (epoch
  1734592499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 07:15 UTC -> 09:00 UTC (verified)**: ordinary London-morning ranging, 2613-2622,
  ordinary volume (2230-3480). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~09:00 UTC (epoch
  1734598799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 09:00 UTC -> 11:00 UTC (verified)**: ordinary quiet ranging 2617-2627, ordinary
  volume (1820-4220). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~11:00 UTC (epoch
  1734605999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 11:00 UTC -> 16:45 UTC (verified, genuine jobless-claims Thursday)**: a genuine
  12:30 UTC data-slot sustained decline -- moderate step-change candle (O2613.52 H2614.14 L2608.28
  C2608.53, vol 3627), then ~2hrs of continued decline with sustained elevated volume (3600-7300,
  several candles above 5500) from the pre-event baseline (~2614-2619) down to an episode low of
  2587.03 (~14:30 UTC, ~27-32pt decline), before volume faded (6389 -> 4182) and price stabilized/
  mildly recovered ~2588-2597. Textbook match to the already-saturated "sustained multi-hour
  decline" family (14th+ instance informally; same jobless-claims-Thursday-at-12:30-UTC pattern
  already documented multiple times) -- no novel structural nuance, not logged as a new instance
  note given the family's saturation. No other new phenomena this batch.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~16:45 UTC (epoch
  1734626699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 16:45 UTC -> 18:45 UTC (verified)**: ordinary quiet consolidation holding the
  post-decline level, 2590-2599, ordinary volume (2750-4910). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~18:45 UTC (epoch
  1734633899), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 18:45 UTC -> 23:15 UTC (verified)**: quiet, narrow-range (2593-2600) grind through
  the NY evening, ordinary low volume tapering (2800 -> 600), ordinary ~76min daily-rollover gap
  observed again (21:58:59 -> 23:14:59 UTC, price flat across the gap: 2594.52 -> 2593.92). No new
  phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-19 ~23:15 UTC (epoch
  1734650099), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-19 23:15 UTC -> 2024-12-20 01:15 UTC (verified, now Friday)**: very quiet, narrow-range
  (2589-2599) Asian-session open, low volume with a modest late pickup (4954) on a small recovery
  push. No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~01:15 UTC (epoch
  1734657299), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-20 01:15 UTC -> 03:15 UTC (verified)**: ordinary quiet ranging 2595-2604, ordinary
  volume (2100-4950). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~03:15 UTC (epoch
  1734664499), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-20 03:15 UTC -> 05:15 UTC (verified)**: very quiet, narrow-range (2596-2601) Asian
  session, ordinary low volume (1180-2480). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~05:15 UTC (epoch
  1734671699), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-20 05:15 UTC -> 07:00 UTC (verified)**: ordinary quiet gentle recovery, 2596-2606,
  ordinary volume (1175-2850). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~07:00 UTC (epoch
  1734677999), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-20 07:00 UTC -> 09:00 UTC (verified)**: very quiet, narrow-range (2602-2608) London
  session, ordinary volume (1930-3020). No new phenomena.
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~09:00 UTC (epoch
  1734685199), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).
- **2024-12-20 09:00 UTC -> 10:00 UTC (verified)**: very quiet, narrow-range (2603-2607) London
  session, ordinary volume (2380-2830). No new phenomena. **Session paused here on explicit CEO
  instruction ("Opreste te aici, salveaza tot si intra in stand by pana la urmatoarea comanda") --
  loop stopped, no further replay_step calls until a new /loop or explicit instruction resumes it.**
- Current replay position (verified via `date -d @epoch`): 2024-12-20 ~10:00 UTC (epoch
  1734688799), M15, no autoplay used. Running total this session: 2 Discovery Candidates
  (AP2-DC-0001, AP2-DC-0002), 13 Addenda (AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, and
  AP2-ADD-0013 against AP2-DC-0001, AP2-ADD-0011 against AP2-DC-0002), 10 Observation Registry
  entries (unchanged this iteration).

## OFFICIAL SESSION CLOSURE (2026-07-25, CEO instruction: "Acum inchidem oficial Alpha 2. Actualizeaza
documentele de stare si fa commit. Nu implementa nimic nou.")

This instance is **officially closed**. No further observation, replay advancement, Discovery
Candidates, or Addenda are being produced under Alpha Parallel Instance #2. This section is the
final, authoritative summary of everything this instance produced during its run.

**Final replay position**: 2024-12-20 ~10:00 UTC (epoch 1734688799), M15, no autoplay used at any
point this session (per the KNOWN HAZARD note above, timeframe was never changed during active
replay). Coverage: 2024-08-01 (period start) through 2024-12-20 ~10:00 UTC — roughly the first
4.5 months of the authorized 2024-08-01 -> 2025-08-01 window. The remaining ~7.5 months
(2024-12-20 onward through 2025-08-01) were **not observed** and remain open for a future instance
or a reopened Alpha #2 session.

**Final output inventory**:
- **2 Discovery Candidates**, both FROZEN v1, handed off and indexed in `DISCOVERY_INDEX_ALPHA2.md`:
  - `AP2-DC-0001` — "A Sharp Breakout On A First-Friday-Of-Month Session Fully Reverses Into A
    Larger, Extended Decline That Overshoots The Pre-Breakout Level" — 13 Addenda (A through L,
    local IDs AP2-ADD-0001 through AP2-ADD-0010, AP2-ADD-0012, AP2-ADD-0013).
  - `AP2-DC-0002` — "A Major Scheduled Political Catalyst Produces a Multi-Hour, Near-Record-Volume,
    Complex Two-Way Volatility Episode Far Exceeding Any Routine Data-Release Reaction" — 1
    Addendum (AP2-ADD-0011).
- **14 Addenda total**, all indexed in `Addenda/ADDENDUM_INDEX_ALPHA2.md` and cross-referenced in
  `discovery_candidates/HANDOFF_LOG_ALPHA2.md` (append-only audit trail, entries through Addendum L).
- **10 Observation Registry entries** in `research_log/OBSERVATION_REGISTRY_ALPHA2.md`, several
  extended with many numbered instance notes over the course of the run (the "sustained multi-hour
  decline" family alone reached 13 instances; the "sweep-reclaim-extend" and "breakout holds and
  extends" families each reached 7+ instances).
- **No filesystem-isolation incidents, no cross-contamination with Alpha #1's workspace or
  artifacts** for the remainder of the session after the one early timeframe-switching hazard
  (documented above, fully recovered, `tab_list`/`tab_switch`/`tab_close`/`tab_new` avoided
  thereafter per the standing workaround).

**Reopening**: if the CEO reopens this instance, resume from the final replay position above
(epoch 1734688799 / 2024-12-20 ~10:00 UTC) using the same methodology (`replay_step` on M15, no
autoplay, `date -d @epoch` verification before every checkpoint) documented throughout this file.
No cleanup or migration is required — all indices (`DISCOVERY_INDEX_ALPHA2.md`,
`ADDENDUM_INDEX_ALPHA2.md`, `HANDOFF_LOG_ALPHA2.md`, `OBSERVATION_REGISTRY_ALPHA2.md`) are
already in a consistent, append-ready state.
