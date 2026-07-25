# Open Item: Suspected Data-Quality Artifact, 2025-09-17 ~18:00-19:00 UTC (Replay)

**Status**: OPEN (opened 2026-07-23, during live replay observation; not yet investigated)
**Opened by**: Alpha (autonomous replay observation)
**Type**: Data-integrity / instrument-quality concern -- NOT a Discovery Candidate and NOT an
Observation Registry entry. This does not describe a market mechanism; it describes a suspected
defect in the replay data feed itself. Do not add it to `DISCOVERY_CANDIDATE_INDEX.md` or the
Observation Registry.

## What Was Observed

During silent replay observation, the OANDA:XAUUSD M15 candle at **2025-09-17 18:00-18:15 UTC**
(18:00 UTC = 14:00 ET, the standard FOMC statement release time) showed an unusually large range
-- O3686.52, H3707.59, L3651.33, C3687.9, roughly 56.3 points -- on volume of only 12,556. For
comparison, other large-range events already catalogued in this replay (DC-0017's NFP impulse,
DC-0018's fresh-high failure) showed volume in the 30,000-37,000 range for comparable or smaller
point ranges. A 56-point range on ~12.5k volume is far outside that established relationship
between range and volume for this instrument in this replay.

Dropping to M1 for this candle showed per-minute volume clustered tightly between roughly 800 and
870 across all 15 one-minute bars -- essentially flat, minute to minute. Genuine tick-based minute
volume in every other instance examined in this replay (including ordinary quiet hours) shows much
larger minute-to-minute variability than this. The anomalous flatness persisted across the following
three M15 candles as well (18:15-19:00 UTC, ~1 additional hour), with M1 volumes clustered in
similarly narrow bands (roughly 700-870, then declining toward more normal-looking variability by
19:00-19:15 UTC).

Within the 18:00-18:15 candle specifically, the second one-minute bar (18:01-18:02 UTC) showed a
sharp wick down to 3651.33 (from a local level near 3681-3682) and an equally sharp recovery within
the same single minute, on volume (870) indistinguishable from the surrounding ordinary minutes --
no volume spike accompanies this large, fast excursion, which would be atypical for a genuine
liquidity event.

## Why This Looks Like a Data Artifact, Not a Market Event

- Real market volume is bursty: quiet periods and active periods differ by a factor of several
  times within the same session, and large-range candles in this replay have consistently shown
  volume scaling with range (see DC-0006, DC-0008, DC-0013, DC-0017, DC-0018). This candle and its
  neighbors break that pattern in both directions: too little volume for the range, and too little
  variability minute to minute for volume to be organic.
- The unaccompanied sharp one-minute wick to 3651.33 with no distinguishing volume signature is not
  consistent with any construction type already catalogued in this replay (compare to DC-0011's
  genuine sweep-reclaim, which showed clear volume concentration).
- 18:00 UTC on this date is a scheduled US macro-release slot (FOMC), which is exactly the kind of
  moment where a data vendor might backfill a gap with synthetic/interpolated bars if the original
  feed dropped ticks, which would produce exactly this signature: large range, smoothed/uniform
  volume, no real minute-to-minute burstiness.

## What This Investigation Should Determine

1. Whether this is a known artifact of the underlying OANDA/TradingView replay data source for this
   specific date/time (e.g., a documented data-vendor backfill or gap-fill event).
2. Whether other replay dates show the same signature at scheduled macro-release times, which would
   support the synthetic-backfill hypothesis systematically rather than as a one-off.
3. Whether any Discovery Candidate or Observation Registry entry already created in this replay
   overlaps this window and should be re-examined for reliability (a search of existing DC/OBS
   source_artifacts for 2025-09-17 18:00-19:00 UTC found none as of this writing).

## Action Taken

Alpha did **not** treat this window as a market discovery: no Discovery Candidate or Observation
Registry entry was created for the 18:00-19:00 UTC price action itself, despite its large point
range, specifically because the volume signature made it impossible to distinguish genuine price
discovery from feed artifact. Alpha resumed normal silent observation once volume and minute-level
variability returned to patterns consistent with the rest of this replay (by approximately 19:00-
19:15 UTC).

## Cross-References

- `research_log/SESSION_STATE.md` -- journal entry for 2025-09-17 documents this window inline and
  points here.
