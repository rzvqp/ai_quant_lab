# Addendum B to DC-0008 (dated 2026-07-22)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation: Single-Minute Concentration Again, Same Clock Time, Different Weekday, Different Aftermath

On 2025-08-12 (a Tuesday, not the first-Friday NFP slot referenced in v1), the M15 candle
12:30-12:45 UTC ran O3339.64 H3354.725 L3339.61 C3349.8 — a 15.1-point range, volume 17,109
(roughly 3-4x the immediately preceding M15 candles' 4,000-6,000).

Dropping to M1: the entire displacement was concentrated in the single 12:30-12:31 UTC minute —
O3339.64 H3353.46 L3339.61 C3349.745, volume 2,379, a ~13.85-point range in 60 seconds. This
matches the "single-minute concentration" construction from v1's 03:40 instance, not the
"sustained multi-minute" construction from v1's 12:30 NFP instance. The remaining ~14 minutes
(12:31-12:44) did not return to a quiet baseline, but also did not continue the displacement or
fade back toward the pre-impulse level — instead price oscillated within the new 3344-3354 range
at moderate, fairly even volume (roughly 540-1,436 per minute), effectively consolidating around
the level the first minute had established.

## Why This Matters To DC-0008

Two points of contrast with v1:

1. **Same clock time, different weekday, different construction.** v1's 12:30 UTC instance (NFP
   Friday) was built from sustained multi-minute volume; this 12:30 UTC instance (a Tuesday) was
   built from single-minute concentration instead. This weakens any implicit assumption that
   12:30 UTC construction is characteristically "sustained" — the clock time alone does not
   determine which construction occurs; whether that depends on the underlying calendar event
   (NFP vs. some other scheduled release, if any, on this date) is not established here.
2. **A third aftermath type.** Prior single-minute-concentration instances of note (DC-0011: sweep
   reclaimed and extended to new highs) resolved with continuation past the pre-event range. This
   instance instead consolidated sideways around the new post-impulse level for the remainder of
   the M15 candle, neither reverting to the pre-impulse price nor extending further. Whether this
   is a third distinct outcome-after-concentration or simply what a smaller-magnitude concentration
   looks like is not established by one instance.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains
as recorded in `candidate_v1.md` v1. This addendum only files the new evidence for downstream
review.
