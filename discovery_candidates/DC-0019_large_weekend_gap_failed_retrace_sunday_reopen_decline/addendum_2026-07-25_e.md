# Addendum E to DC-0019 (dated 2026-07-25)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation

On 2026-04-02 20:45:00 UTC (Thursday, close 4676.745), the market closed. On reopen at
2026-04-05 22:00:00 UTC (Sunday, open 4638.25) the closure lasted **263,700s (73h15m)**, verified
exactly on OHLCV bar timestamps — this is **not** the standard 177,300s (49h15m) weekend cadence
documented in every prior instance of this DC (base candidate, Addenda A-D). This is the first
instance in this replay of a closure duration longer than the routine weekend gap. The date falls on
a calendar position consistent with the Good Friday holiday (2026-04-03) sitting adjacent to the
weekend, though Alpha has no direct indicator/calendar confirmation of the holiday — this is offered
as a plausible, hedged explanation for the extended closure duration, not an established fact.

The reopen produced a **-38.495pt gap down** (4676.745 -> 4638.25) — well below this DC's existing
gap-magnitude records (largest: 90.02pt, Addendum D) and not itself record-setting on the magnitude
axis. As with every prior instance in this DC's family, the reopen 5-minute candle traded thin
volume (101 units, M15 candle 1775426400, splitting 101/5,203/7,876 across its three M5 sub-candles)
before the next 5-minute candles absorbed the rush — the same "thin liquidity at instant of reopen"
microstructure already documented for every prior weekend-gap reopen in this DC's history. Checking
the volume-to-range ratio for the concentrated second/third sub-candles: the 7,876-volume sub-candle
(range 21.07pt) yields 373.8 vol/pt, far above this replay's normal baseline (~90-110) — the opposite
of a thin-volume artifact signature, confirming genuine organic participation, not a concentrated or
fabricated print.

Following the reopen, price attempted a partial recovery (up to an intrabar high of 4654.59, ~16.3pt
above the reopen open, still well below the pre-gap close of 4676.745) before fading back down to the
4609-4632 range as this batch ended — consistent with the "gap does not retrace" pattern already
established throughout this DC's history, now demonstrated to also hold across a longer,
holiday-extended closure, not just the routine weekend closure.

## Why This Matters To DC-0019

This is the first documented instance in this replay of a closure/gap event whose duration exceeds
the routine 49.25h weekly weekend cadence, extending this candidate's scope: the same reopen
mechanism (thin initial liquidity, no full retrace) holds even when the closure itself is
calendar-holiday-extended rather than purely weekly. No axis here is record-setting (gap magnitude
and extension are both well below existing records) — this addendum documents a new *type* of
closure-duration instance within the same underlying mechanism, not a new magnitude record.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? Not
wholly — the reopen behavior (thin liquidity, no full retrace) is identical to the routine weekend
gap mechanism already documented; what is new is that the closure itself can be calendar-extended
beyond the routine weekly cycle. (2) Could this be filed only as an Addendum? Yes — this is squarely
a new instance/variant within the already-documented closure-gap mechanism, which is the textbook
case for an addendum. (3) Is this a new record? No, on any magnitude axis — this addendum is filed
specifically because the closure-duration variability itself (holiday vs. routine weekend) is a
previously undocumented fact about this mechanism's triggering conditions, not because any metric hit
a new high.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains as
recorded in `candidate_v1.md` v1 (Low). This addendum only files the new evidence for downstream
review.
