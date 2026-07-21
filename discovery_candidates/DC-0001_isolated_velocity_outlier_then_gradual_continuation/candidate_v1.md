# Discovery Candidate DC-0001: Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation

## Metadata

- **candidate_id**: DC-0001
- **title**: Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation
- **origin_mode**: discretionary-observation, Discovery Cycle #3
- **date_first_observed**: 2026-07-21
- **date_frozen**: 2026-07-21
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: H1, H4, M15
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: H1 windows 2023-02-06/27, 2023-06-05/26, 2023-12-01/22, 2024-06-03/24,
  2024-12-02/23, 2025-05-05/26; H4 windows 2023-03-01/06-01, 2024-09-01/12-01; M15 zooms
  2023-12-03 18h/2023-12-04 06h, 2023-06-08 15h/2023-06-09 03h, 2024-02-13 13h/2024-02-14 01h,
  2024-08-04 19h/2024-08-05 13h, 2024-12-18 18h/2024-12-19 06h
- **related_ids**: none (first candidate entered into this repository structure)
- **content_hash**: sha256:1f1b3d399f2e9613b18d1d4ecaede8d7e3b0dec085ab709482b4d2c3f40cf75c
  (computed over this file with both `content_hash` and Handoff Statement hash fields holding the
  literal placeholder `PENDING` -- recompute after restoring those two fields to `PENDING` to verify)

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

Across several multi-week hourly charts and closer 15-minute views of specific moments within
them, a specific short-lived construction recurs: on at least two occasions, one single 15-minute
bar moves a distance many times larger than any of its immediate neighbors -- in one instance
roughly 58 points in 15 minutes where neighboring bars typically moved 1-3 points; in another,
roughly 28 points in 15 minutes against a similarly small neighboring scale. In both cases this
outsized single bar is never repeated at anything close to that pace again nearby. What follows
it, over the next roughly 1.5-2 hours, is a smooth, gradual, largely uninterrupted sequence of many
smaller bars covering a comparable total distance -- in one case undoing the outsized bar's move
entirely and continuing past its starting point (2023-12-03), and in the other continuing on in
the very same direction as the outsized bar, as if finishing the move at a slower pace
(2024-02-13). A third, separately examined multi-hour move of comparable total size (2024-08-04/05)
showed no such isolated outsized bar at all -- it was paced evenly throughout, bar after bar, with
nothing standing out as a velocity outlier.

## 2. Why It Attracted Attention

The single outsized bar looked disconnected from the pace of everything around it -- as though the
market briefly moved at a distinctly different speed for exactly one interval and then, regardless
of which direction things went afterward, never sustained that speed again. That the deceleration
appeared both in a case that reversed and in a case that continued in the same direction suggests
the drop in pace itself may be the more basic feature, separate from which direction the following
bars actually took.

## 3. Why It May Repeat

The same shape -- one bar moving far faster than its surroundings, followed by several bars at a
distinctly slower pace -- appeared independently in two different years, at different times of
day, and in both possible follow-through directions (continuation and reversal). That range of
contexts suggests it is not tied to one specific event, date, or direction.

## 4. Why It Deserves Further Investigation

This raises a question the discretionary-observation cycles prior to this handoff interface did
not address: whether a single bar's pace, considered on its own, carries information about what
follows, independent of which direction that follow-through takes. Whether that is true, and how
it would be distinguished from the many ordinary bars that show no such velocity gap, is not
something visual review alone can settle.

## 5. Confidence

Low. Based on two confirming instances found through deliberate, targeted searching (not a
systematic scan of the dataset) plus one useful contrasting case where a comparably sized move
showed no such outlier bar -- a small sample, and "how much faster than neighboring bars" was
judged only visually, with no measurement applied.

## Additional Notes (optional)

This observation is conceptually distinct from two discretionary-observation findings discussed in
earlier Discovery cycles, prior to this handoff interface's implementation: an extreme-price-level
reversal behaviour, and a longer quiet/active macro-scale rhythm. This candidate concerns the pace
of individual bars, not price levels or multi-day/week regime alternation. Neither earlier finding
was ever entered into this repository's Discovery Candidate structure, so no related_ids are
recorded above.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-21**. Content hash:
**sha256:1f1b3d399f2e9613b18d1d4ecaede8d7e3b0dec085ab709482b4d2c3f40cf75c** (see `metadata_v1.json`
for the same value in machine-readable form). This document is immutable from this point forward.
Any correction or new evidence must be filed as a separate, dated addendum in this candidate's
folder, or as a new version file -- never as an edit to this file.
