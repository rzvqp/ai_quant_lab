# Discovery Candidate DC-0010: A Consistently Quiet Hour Breaks With A Sustained Volume Expansion On One Session

## Metadata

- **candidate_id**: DC-0010
- **title**: A Consistently Quiet Hour Breaks With A Sustained Volume Expansion On One Session
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint
- **date_first_observed**: 2026-07-22 (replay 2025-08-07)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: H1, M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-04 through 2025-08-07, 00:00-01:15 UTC windows
- **related_ids**: DC-0008
- **content_hash**: sha256:5855f9606e7070f86bab1f98b3a8599b5a2a7a684916ab157418e9b2a52b538c
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:5855f9606e7070f86bab1f98b3a8599b5a2a7a684916ab157418e9b2a52b538c`

## 1. Observation

Across three consecutive prior sessions (2025-08-04, 08-05, 08-06), the 00:00-01:00 UTC hour was,
without exception, the quietest hour of the trading day: M15 volumes in the low hundreds to
roughly 2,000, small ranges, no directional persistence.

On 2025-08-07, the same hour broke sharply from that pattern. The H1 candle 00:00-01:00 UTC
carried volume 30,168 — roughly 5-7x the volume of the immediately adjacent hours (4,494-6,393) —
against a real, sustained ~13-point directional move (3365.3 -> 3378.36) that continued into the
following hour (01:00-02:00 UTC, already 18,502 and rising while still forming). On M15, three
consecutive candles (00:15, 00:30, 00:45) showed volume escalating rather than settling
(6,946 -> 10,432 -> 7,468), and the move continued at 01:00-01:15 to a new high with volume still
near 7,000-11,000. On M5 and M1 the move was distributed across many minutes with continuously
elevated participation, not concentrated in a single candle — the same construction family as
DC-0008's "sustained" type, but occurring inside a specific calendar hour that had just been
established, by direct repeated observation, as this instrument's quietest window.

## 2. Why It Attracted Attention

The hour's baseline had been established through three consecutive days of direct, repeated
observation before this instance — not assumed from an external source. Seeing that specific,
independently-established quiet window break with a 5-7x volume multiple and a real multi-hour
directional move, rather than a stray noisy candle, made this the clearest deviation from an
established local baseline seen so far this session.

## 3. Why It May Repeat

Descriptively: an hour that has repeatedly shown itself to be the quietest part of the day is a
meaningful local baseline. Whether this particular hour occasionally produces outsized activity
(a recurring but infrequent feature) or whether 2025-08-07 was an idiosyncratic one-off is
directly testable by continuing to watch the same hour across further sessions.

## 4. Why It Deserves Further Investigation

The comparison is fully countable: hourly volume in the 00:00-01:00 UTC window against its own
multi-day baseline, and whether a real directional move accompanies the volume (as here) or
whether volume spikes in this window are sometimes noise without follow-through. Both the
baseline and the deviation were observed directly, not inferred.

## 5. Confidence

**Low.** One clear deviation against a three-day baseline, one instrument, one timeframe cluster.

## Additional Notes

Filed initially as two separate Observation Registry entries (`OBSERVATION_REGISTRY.md`,
2025-08-07 00:00 UTC and 00:15-00:45 UTC) before the move's persistence into 01:00-01:15 UTC and
its scale relative to the established baseline became clear enough to warrant promotion to a
Discovery Candidate. The registry entries remain as the raw first-pass notice; this document is
the promoted, fuller account.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-22**. Content hash: **sha256:5855f9606e7070f86bab1f98b3a8599b5a2a7a684916ab157418e9b2a52b538c**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
