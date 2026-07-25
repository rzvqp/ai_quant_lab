# Discovery Candidate DC-0017: An NFP-Scale 12:30 UTC Impulse, Built From Sustained Multi-Minute Volume, Holds Its Gains Across Four Subsequent High-Volume Candles Without Reversing or Extending Dramatically Further

## Metadata

- **candidate_id**: DC-0017
- **title**: An NFP-Scale 12:30 UTC Impulse, Built From Sustained Multi-Minute Volume, Holds Its Gains Across Four Subsequent High-Volume Candles Without Reversing or Extending Dramatically Further
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-09-05 12:15-13:45 UTC, OANDA:XAUUSD M15/M1 replay window
- **related_ids**: DC-0008 (sustained multi-minute construction, originally observed at a 12:30 UTC NFP-type candle), DC-0013/DC-0013 Addendum A, DC-0015, DC-0016/DC-0016 Addendum A (the "large sustained expansion" family)
- **content_hash**: sha256:dbd07f90a927b2a9b9c5fb81a924803c3ab74437fa3242294b9f386d4213c712

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-09-05 (the first Friday of the month), the 12:30-12:45 UTC M15 candle ran O3555.235
H3587.04 L3553.89 C3583.63 -- roughly a 33.15-point range, volume 30,975. This dwarfs every one of
the 22 prior ordinary 12:30 UTC instances observed earlier in this replay, which topped out around
4,500-14,000 volume with modest ranges. Dropping to M1, the displacement was NOT concentrated in a
single minute: volume across the 15 one-minute candles from 12:30 to 12:45 ranged 1,161-3,099 with
no single dominant minute, and price advanced in a genuine multi-leg climb from 3555.235 to a peak
of 3587.04 within roughly the first 10 minutes -- the same "sustained multi-minute" construction
originally documented in DC-0008 (which itself originated from a 12:30 UTC candle of comparable
character).

Unlike a single isolated impulse, the elevated volume and the price level both persisted across the
four subsequent M15 candles: 12:45-13:00 (vol 22,921, range 3572.26-3583.83), 13:00-13:15 (vol
19,012, range 3573.25-3583.72), 13:15-13:30 (vol 16,151, range 3574.96-3585.06), and 13:30-13:45
(vol 20,627, range 3575.47-3585.44, closing 3584.56). Across this roughly 1h15m window, price held
its gains -- oscillating within the 3572-3587 band established by the initial impulse -- without
either reversing back toward the pre-move ~3555 level or extending dramatically to new highs beyond
the initial spike's 3587.04.

## 2. Why It Attracted Attention

The v2 pre-investigation filter would ordinarily screen out the 12:30 UTC window entirely, since 22
prior instances in this replay have already been catalogued as ordinary. This instance passed the
filter specifically because its magnitude (30,975 volume, 33.15pt range) was far outside that
already-documented envelope -- comparable to or exceeding DC-0008's original NFP-scale candle
(24,005 vol, 39pt) and DC-0013's original NY-session candle (29,674 vol, 27.13pt) -- and because the
elevated volume and price level persisted for four further candles rather than immediately fading.

## 3. Why It May Repeat

The underlying construction (sustained, broadly even multi-minute participation, no single-minute
concentration) is the same mechanism already documented in DC-0008 and its addenda. The specific
combination observed here -- an NFP-scale impulse at exactly 12:30 UTC on a first-Friday-of-month
date, followed by several candles of continued elevated volume that hold the new price level rather
than reverting or extending -- has not been observed before in this replay at this magnitude. If
12:30 UTC first-Friday timing does correspond to a scheduled macro release (e.g. US employment
data), similar-magnitude instances would be expected to recur on a monthly cadence, though this
candidate makes no claim about the underlying cause from price/volume data alone.

## 4. Why It Deserves Further Investigation

This is one of the largest single-candle volume/range events observed anywhere in this replay,
comparable to DC-0008's and DC-0013's originating instances. Unlike DC-0013/DC-0015/DC-0016 (which
built gradually across several candles each contributing meaningful net directional progress), this
instance concentrated nearly its entire net move into the first candle, then spent four further
candles absorbing continued high volume while holding rather than extending the new level. Whether
this "impulse-then-hold" resolution shape is characteristic of NFP-scale prints specifically (as
distinct from the gradual-build shape of DC-0013/15/16, or the V-reversal-then-rally shape of
DC-0014/16), and whether it recurs on subsequent first-Fridays, is a natural comparison point for
future large 12:30 UTC instances.

## 5. Confidence

**Low.** One instance. The sustained multi-minute construction has strong precedent (DC-0008), but
the specific "impulse-then-hold across four candles without reversal or further extension" shape at
this magnitude rests on n=1 in this replay.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone, though the date (first
Friday of the month, 2025-09-05) and the 12:30 UTC timing are consistent with a scheduled
macro-release slot (e.g. US Non-Farm Payrolls) already flagged as a plausible, unverified
association in DC-0008's Section 3. This candidate does not claim to confirm that association --
only that the magnitude and timing are consistent with it, and that the resulting price behavior
(hold, not reverse or dramatically extend) differs from the other "large sustained expansion" family
members catalogued so far.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:dbd07f90a927b2a9b9c5fb81a924803c3ab74437fa3242294b9f386d4213c712**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
