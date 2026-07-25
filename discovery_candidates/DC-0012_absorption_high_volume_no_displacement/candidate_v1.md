# Discovery Candidate DC-0012: Sustained High Volume With No Net Displacement (Two-Sided Absorption)

## Metadata

- **candidate_id**: DC-0012
- **title**: Sustained High Volume With No Net Displacement (Two-Sided Absorption)
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint
- **date_first_observed**: 2026-07-22 (replay 2025-08-08)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-08 00:00-00:15 UTC
- **related_ids**: DC-0008, DC-0010
- **content_hash**: sha256:4a4791c183230291c9af6f1665d78f76886da8a06131385d2a5301bba3b24081
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:4a4791c183230291c9af6f1665d78f76886da8a06131385d2a5301bba3b24081`

## 1. Observation

At 2025-08-08, 00:00-00:15 UTC, the M15 candle carried O3400.64 H3402.34 L3397.59 C3399.93 —
volume 23,718 against a range of only 4.75 points. Dropping to M5, the volume was distributed
across all three 5-minute segments (9,152 / 9,080 / 5,486), each with a similarly narrow range
(roughly 4-4.5 points). On M1, every single one of the 15 minutes carried elevated volume
(roughly 650-2,150, versus a typical sub-300-500 baseline established for this hour on prior
days), while price oscillated tightly within the same ~4.7-point band the entire time, never
trending in either direction. Every construction-type instance logged so far this session
(DC-0008, DC-0010, DC-0011) paired elevated/sustained volume with a real, measurable directional
displacement. This is the first instance where sustained high volume produced essentially no net
displacement at all.

## 2. Why It Attracted Attention

This is the opposite signature of everything else logged this session. A trader watching this live
would read it as two-sided absorption — heavy participation on both sides of a tight range, with
neither side able to move price — rather than a directional event. It is also the second time this
specific hour (00:00-01:00 UTC) has broken from its established quiet-hour baseline within two
consecutive sessions (cf. DC-0010, 2025-08-07, same hour, but that instance was a directional
expansion, not absorption).

## 3. Why It May Repeat

Descriptively: volume and price displacement are two independent, both countable quantities per
bar or per minute. A bar or short window with volume well above baseline but range at or below
baseline is a distinct, nameable shape from the more commonly logged "volume with displacement."
Whether this specific hour has a general tendency toward unusual activity (of either sign) is
directly testable by continuing to watch it across further sessions.

## 4. Why It Deserves Further Investigation

Both halves of the definition are fully countable: volume relative to a bar's own established
baseline, and range/net displacement relative to that same baseline. A systematic scan for
bars/windows with high relative volume and low relative range is a well-defined query once a
baseline is established, and what happens immediately after such windows (does absorption resolve
into a delayed breakout, or does it simply dissipate) is directly observable.

## 5. Confidence

**Low.** One instance, one instrument, one timeframe cluster.

## Additional Notes

Occurs the day after DC-0010 flagged the same calendar hour (00:00-01:00 UTC) for anomalously high
volume on 2025-08-07, though that instance was directional and this one is not — worth tracking
whether 00:00-01:00 UTC is becoming a locally unusual hour on this instrument in general, independent
of the direction the anomaly takes.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-22**. Content hash: **sha256:4a4791c183230291c9af6f1665d78f76886da8a06131385d2a5301bba3b24081**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
