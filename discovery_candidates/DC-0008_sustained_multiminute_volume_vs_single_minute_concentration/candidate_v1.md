# Discovery Candidate DC-0008: A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration

## Metadata

- **candidate_id**: DC-0008
- **title**: A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint
- **date_first_observed**: 2026-07-22 (replay 2025-08-01)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-01 07:10-12:45 UTC
- **related_ids**: DC-0003, DC-0006
- **content_hash**: sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130`

## 1. Observation

On 2025-08-01, the M15 candle from 12:30 to 12:45 UTC on OANDA:XAUUSD ran from 3302.36 to a high of
3340.82 (low 3301.79), closing at 3339.225 — a 39-point range on volume of 24,005, roughly 8-10x the
volume of the immediately preceding M15 candles (~2,000-3,000). Dropping to M5, the range was
distributed across all three M5 candles inside it, each carrying comparable, strongly elevated volume
(8,653 / 7,802 / 7,550) rather than one dominant candle. Dropping further to M1, every one of the
~15 one-minute candles from 12:30 through 12:44 carried elevated volume (roughly 1,300-1,900, versus
~175-280 in the minutes immediately before), and price advanced in three visible legs (12:30-12:33,
12:37, 12:42-12:44) separated by brief consolidation plateaus, without returning to baseline volume
until after 12:44.

Earlier in the same session (2025-08-01, 03:40 UTC), a comparably large M15 candle (6.8pt range,
volume 3,862) had a different anatomy: on M1, the entire displacement occurred inside a single
one-minute candle (volume 459 vs a 163-219 baseline), with every other minute in the M15 candle
trading in a ~2.5pt drift at baseline volume.

## 2. Why It Attracted Attention

Both events produced a large, high-volume M15 candle, but their internal construction was opposite.
The 03:40 candle was one instantaneous concentration surrounded by inactivity. The 12:30 candle was
continuous, elevated activity sustained across the entire 15 minutes, with no single minute
dominating and no return to baseline until the M15 candle closed. The M15 candle alone does not
distinguish between these two constructions — only stepping down to M1 does.

## 3. Why It May Repeat

Descriptively: a large M15 candle can be the visible aggregate of either (a) a brief, concentrated
displacement or (b) continuous, elevated multi-minute repricing. The 12:30 timing coincides with a
standard weekly/monthly US scheduled-release slot (first Friday of the month, 12:30 UTC), which is
one plausible source of sustained repricing, though this was not verified against any news calendar
or external source — it is offered as a contextual observation, not a causal claim.

## 4. Why It Deserves Further Investigation

Both constructions are countable from bar data alone: the ratio of the single largest M1 (or M5)
volume share to the total M15 volume, and whether volume returns to baseline before the M15 candle
closes. Whether these two constructions have different downstream behaviour is measurable.

## 5. Confidence

**Low.** Two instances (one of each construction type), same session, same instrument.

## Additional Notes

Both large-candle events sit within the same continuous replay session (2025-08-01, pre-cutoff),
examined back-to-back, which is why the contrast was visible without deliberately searching for it.

| Concept | Presence |
|---|---|
| **DC-0003** scale inversion | Directly related: construction differs by which scale you inspect, not just resolution outcome. |
| **DC-0006** extreme volume candle fails to extend | Contrast: the 12:30 candle carried extreme volume AND extended (new session highs on the following two M15 candles), unlike DC-0006's pattern. |

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-22**. Content hash: **sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate, dated
addendum in this candidate's folder, or as a new version file — never as an edit to this file.
