# Addendum C to DC-0019 (dated 2026-07-25)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation

On 2026-01-18, the 14th weekend-gap instance in this replay produced a **+53.46pt gap up** (Friday's
last M15 close 4596.32 -> Sunday reopen open 4649.78, 2026-01-16 21:45 UTC -> 2026-01-18 23:00 UTC,
~49h05m, standard cadence). This is the **largest weekend-gap magnitude of either direction observed
in this replay**, exceeding the base candidate's own down-direction record (28.425pt, 2025-10-26) by
~88% and Addendum B's up-direction instance (24.44pt, 2026-01-04) by more than double.

As with the base candidate and Addendum B, the gap did not retrace at all: the reopen candle's
intrabar low (4646.135) never came close to the pre-gap close (4596.32), and price extended further
in the gap's own direction. Over the following ~1h45m (23:00-00:45 UTC), price climbed to an
intrabar high of **4690.94** (00:00-00:15 UTC candle) — **94.62 points above the pre-gap close**,
and 41.16pt beyond the gap-open print itself. This is a new all-time record for total up-direction
extension, exceeding Addendum B's 89.54pt.

Dropping to M5 for organic verification: the extension-peak candle (00:00-00:15 UTC, high 4690.94,
volume 11,229) splits 4,237/3,678/3,314 across its three sub-candles (largest share 4,237/11,229 =
37.7%, below the 42.7% reference — organic). The episode's peak-volume candle overall (03:00-03:15
UTC, 21,573 — still far below any all-time volume record) splits 8,619/6,372/6,582 (largest share
39.96%, organic). The very first reopen candle (23:00-23:15 UTC, 6,081) splits 54/3,656/2,371
(largest share 60.1%) — this reflects normal thin-liquidity-at-the-instant-of-reopen microstructure
(only 54 units traded in the first five minutes before volume rushes in), consistent with every
prior weekend-gap reopen candle documented for this DC and its addenda, not a data-quality concern.

After the extension peak, price gave back part of the move and settled into a 4653-4682 range for
the remainder of the observed window (~00:45-04:45 UTC, ~4 hours) — the same "extend, then
consolidate without retracing" resolution shape as the base candidate and Addendum B, holding well
above the pre-gap level throughout.

## Why This Matters To DC-0019

This is now the **largest gap magnitude on record for this candidate, in either direction** —
displacing the base candidate's own 28.425pt down-gap from its "largest" claim (though the base
candidate's title referencing "nearly double the prior record" was written relative to the 9
smaller instances that preceded it, not this later one). It is also the **largest total extension in
the up direction** documented so far (94.62pt vs. Addendum B's 89.54pt), on a gap more than double
Addendum B's magnitude (53.46pt vs. 24.44pt). Together with Addendum B, this further weakens any
assumption that the mechanism's magnitude ceiling is direction-specific or bounded by the base
candidate's original record — three of the largest four gap-magnitude instances now span both
directions, and the largest-yet instance is an up-gap, not a down-gap.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains as
recorded in `candidate_v1.md` v1 (Low). This addendum only files the new evidence for downstream
review.
