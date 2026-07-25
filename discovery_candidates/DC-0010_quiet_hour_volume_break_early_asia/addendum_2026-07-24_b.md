# Addendum B to DC-0010 (dated 2026-07-24)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation: A Far More Extreme Quiet Baseline, Tied To A Specific Holiday Calendar Event, Breaking Via A Single-Minute Velocity Outlier

On 2025-11-27 (US Thanksgiving Thursday), following an ordinary session, the market entered an
unusually extreme lull: M15 volume collapsed to near-zero (single digits to low hundreds — 21, 14,
53, 113, 30, 37, 4, 13, 16) for roughly 2h15m (19:30-21:45 UTC), far below even DC-0010's original
quiet-hour baseline (low hundreds to ~2,000). After the daily rollover pause, volume began a slow
recovery (533-2,177 across four candles, 23:00-00:15 UTC on 2025-11-28) while still well under the
instrument's ordinary baseline, before breaking sharply at 00:30 UTC: M15 volume 8,919, range
13.6pt, directional +8.5pt.

Dropping to M5: the largest 5-minute sub-bar (00:35-00:40 UTC) carried 4,958 of the 8,919 total
(55.6% concentration — above the 42.7% organic-construction reference, higher than any prior
instance's flagged caveat). Dropping further to M1 to resolve this: the elevated 5M bucket itself
resolves into five 1-minute bars (1,494 / 1,256 / 800 / 667 / 741), none dominating (max 30.1% of
the 5M bucket) — not a data artifact. The true concentration point is one specific PRIOR minute
(00:34 UTC, just before the 5M bucket examined above): a single 60-second bar spanning 4173.055 to
4184.055 (11.0pt range in one minute, volume 1,199) — an isolated single-bar velocity outlier
matching DC-0001's exact pattern, immediately followed by ~5 minutes of continued elevated,
whipsaw-like trading (price oscillating 4176-4183) before the move settled into a sustained,
gradual, gain-holding rally that continued for at least 1h30m afterward without reversing
(4180 -> ~4193 by 02:00 UTC).

## Why This Matters To DC-0010

This instance shows the same fundamental shape as v1 (an established quiet baseline broken by real
volume + a real, sustained directional move), but adds texture not present in the original: (1) the
quiet baseline here is tied to a specific, identifiable calendar cause (US Thanksgiving holiday)
rather than an ordinary session-timing lull, and is far more extreme (near-zero vs. low
hundreds-to-2,000); (2) the break's internal anatomy is not a simple volume ramp but opens with a
single-minute velocity-outlier ignition (the DC-0001 pattern) followed by a brief whipsaw before
transitioning into the sustained hold.

Three-part novelty test applied explicitly (CEO directive) before deciding artifact type: (1) Is
this a new MECHANISM? No — it is DC-0010's mechanism (quiet baseline -> real volume/move break),
with an ignition sub-pattern already separately documented as DC-0001, chained together; nothing
here requires a causal story not already on file. (2) Could this be filed only as an Addendum? Yes
— that is exactly what this document is; there was genuine doubt whether this belonged to DC-0010
or DC-0001 specifically, which is itself a signal to under-promote rather than create a third
artifact. (3) Is this a new record? No — 1,199 (peak single-minute volume) and 8,919 (M15 volume)
are both far below this replay's established volume records (24,000-37,500+); the ~30pt total move
is far below the magnitude records (100pt+). The only genuinely novel element (the specific
holiday-calendar cause of the quiet baseline) is noted here as context, not promoted as its own
mechanism claim.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains
as recorded in `candidate_v1.md` v1. This addendum only files the new evidence for downstream
review.
