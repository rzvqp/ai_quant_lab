# Discovery Candidate DC-0009: A Narrow Resistance Band Survives Seven Touches Across Three Calendar Days, Including A Weekend Gap

## Metadata

- **candidate_id**: DC-0009
- **title**: A Narrow Resistance Band Survives Seven Touches Across Three Calendar Days, Including A Weekend Gap
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint
- **date_first_observed**: 2026-07-22 (replay 2025-08-01 to 2025-08-04)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-01 19:30 UTC through 2025-08-04 07:15 UTC
- **related_ids**: DC-0005
- **content_hash**: sha256:ac7ffdec7dcd15472caafc6e93196381a9427446e7ea4773778746c560354c15
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:ac7ffdec7dcd15472caafc6e93196381a9427446e7ea4773778746c560354c15`

## 1. Observation

A narrow price band, roughly 3361.0-3363.6, was approached and rejected seven separate times
between 2025-08-01 19:39 UTC and 2025-08-04 07:15 UTC on OANDA:XAUUSD M15:

1. 2025-08-01 ~19:39 UTC — high 3361.045
2. 2025-08-01 20:45 UTC — high 3363.6
3. 2025-08-03 23:45 UTC (Sunday weekly reopen) — high 3362.24
4. 2025-08-04 00:00 UTC — high 3362.5
5. 2025-08-04 04:30 UTC — high 3362.25
6. 2025-08-04 06:45 UTC — high 3362.705 (a marginal new high within the band; candle closed near
   its high rather than snapping back)
7. 2025-08-04 07:00-07:15 UTC — opened essentially at the band (3362.64), failed to extend, then
   fell 8.4 points in the next M15 candle to 3353.74 on volume of 3,658 — the largest single-candle
   volume of the entire seven-touch sequence.

Between touches 1 and 3 the instrument closed for the weekly weekend gap (Friday ~21:00 UTC to
Sunday ~22:00 UTC) and gapped up slightly on reopen before the gap was filled within the first
M15 candle (see prior weekend-gap observation, OBS-0015).

## 2. Why It Attracted Attention

The band was tested across three different calendar days and at least four different session
contexts (NY afternoon, the weekly reopen, an Asia-session grind, and Tokyo hours), separated by a
full weekend closure, and never gave way. The final rejection was the sharpest and highest-volume
of the sequence, rather than the level simply eroding gradually — it looked, if anything, more
firmly defended on the last touch than on some of the middle ones.

## 3. Why It May Repeat

Descriptively: a level that has already produced two or more rejections is a visible, shared
reference for participants returning across sessions and even across a weekend closure. Whether a
band's rejection count correlates with how it eventually resolves (erosion vs. sharp final
rejection) is directly observable from repeated instances like this one.

## 4. Why It Deserves Further Investigation

The touch count (seven), the elapsed time (about 60 hours of calendar time, including a full
weekend), and the volume profile of each touch are all countable directly from bar data. Whether
levels surviving many touches behave differently on their eventual break or final rejection than
levels tested only two or three times (per DC-0005) is a measurable question.

## 5. Confidence

**Low.** One instance, one instrument, one timeframe, one band.

## Additional Notes

Related to DC-0005 ("the third test of a level behaves differently from the first two") but distinct
in scale — DC-0005 concerns the transition from a second to a third test; this instance survived
several more tests than that before its most decisive rejection, spanning a weekend closure that
DC-0005 did not involve. Whether these are the same underlying phenomenon at different touch counts,
or something else entirely, is left open.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-22**. Content hash: **sha256:ac7ffdec7dcd15472caafc6e93196381a9427446e7ea4773778746c560354c15**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate, dated
addendum in this candidate's folder, or as a new version file — never as an edit to this file.
