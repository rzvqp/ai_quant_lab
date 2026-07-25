# Addendum B to DC-0013 (dated 2026-07-24)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation

On 2025-10-02, during the New York session, price declined across six consecutive M15 candles
(15:00-16:15 UTC) from a high of 3896.79 to a low of 3825.21 — a 71.58-point move, the largest
single directional displacement observed so far in this family (exceeding DC-0013's original
~43pt, Addendum A's ~32-38pt, DC-0015's magnitude, and comparable to or exceeding DC-0016's
~47.2pt and DC-0018's ~47.8pt). The decline was essentially uninterrupted: only one candle
(16:00-16:15 UTC) closed marginally higher than the prior candle's close (+2.17pt, an immaterial
pause rather than a genuine pullback) before the move continued to a new low the same candle.
Two further candles (16:15-16:45 UTC) then stabilized/consolidated in a 3825-3845 band rather than
reversing sharply — the same consolidation-ending resolution as DC-0013's original and Addendum A,
not the sharp-reversal ending seen in DC-0014/DC-0016.

Per-candle M15 volume across the seven decline-and-stabilization candles was 9329, 9168, 9513,
9289, 10898, 11354, 9916, 8587 — remarkably flat and consistent (no single dominant candle), but
critically **far below** both DC-0013's original range (29674 down to 9833) and Addendum A's range
(19156-23646). This is roughly half the volume of every prior instance in this family, despite
being the largest-magnitude instance yet. Dropping to M5 on the 15:00-16:00 UTC portion confirmed
the same distributed, non-concentrated construction already documented for this family: volume per
5-minute sub-candle ranged narrowly (2400-3860) across virtually every bar with no single dominant
sub-candle, and it tracked the price acceleration (rising as the decline steepened in the final
20 minutes) rather than sitting flat/uniform — ruling out a data-artifact signature (contrast with
`DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md`, where volume was flat/uniform and did NOT track a
large wick).

## Why This Matters To DC-0013

DC-0013 and its Addendum A both established this family's per-candle volume in a 15,000-30,000+
range as part of what "attracted attention." This instance breaks that pattern while preserving
every other qualitative feature (sustained, distributed, multi-candle, no-reversal, consolidation
ending): it shows that a comparable-or-larger magnitude, multi-candle directional expansion can
occur at roughly half the previously-documented volume level, provided the move is unusually
consistent in duration (six consecutive candles with essentially no pullback). This weakens a
strict "high single/per-candle volume is required" characterization of the family and suggests the
more durable signature may be sustained *directional persistence without pullback* across several
candles, with volume elevated relative to session baseline (here ~2-3x the immediately preceding
quiet NY-midday candles) rather than an absolute high-volume floor. Whether this represents a
distinct sub-type (moderate-volume/long-duration vs. high-volume/short-duration) or simply the low
end of a continuous distribution is not established by a single instance.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains
as recorded in `candidate_v1.md` v1 (Low). This addendum only files the new evidence for downstream
review.
