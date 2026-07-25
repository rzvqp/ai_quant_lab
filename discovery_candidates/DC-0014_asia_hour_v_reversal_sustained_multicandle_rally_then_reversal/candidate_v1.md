# Discovery Candidate DC-0014: A V-Shaped Reversal at the 00:00-01:00 UTC Hour Builds Into a Sustained Four-Candle Rally, Then Reverses

## Metadata

- **candidate_id**: DC-0014
- **title**: A V-Shaped Reversal at the 00:00-01:00 UTC Hour Builds Into a Sustained Four-Candle Rally, Then Reverses
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-08-26 00:00-01:45 UTC, OANDA:XAUUSD M15/M5/M1 replay window; initial candle also logged in `OBSERVATION_REGISTRY.md` (2025-08-26 00:00-00:15 UTC entry) before its full extent was known
- **related_ids**: DC-0013 (large sustained NY-session expansion — the comparable "large sustained multi-candle move" construction, here at a different clock time and with a reversal instead of consolidation), DC-0008 (sustained multi-minute construction), DC-0010/DC-0012 (prior notable 00:00-01:00 UTC instances)
- **content_hash**: sha256:3cdc39b74e1db801b2ead9ff0c2b63d93a92347d58ab49570bcc7f2fb7b056df

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-08-26, the M15 candle 00:00-00:15 UTC ran O3354.99 H3371.045 L3351.33 C3369.145 — a
19.72-point range, volume 10,883 (roughly 3-5x the immediately preceding bars' 2,300-3,733).
Dropping to M1, the first three minutes drifted down to a fresh low (3351.33) on light, declining
volume (317/198/141), then the remaining twelve minutes built a sustained, broadly distributed
recovery (volume 452-1,405/minute, no dominant single-minute spike) all the way past the starting
price to a new local high — a full V-shape within one candle. This candle alone was logged as an
Observation Registry entry before its full extent was known.

The rally did not stop there. The following three M15 candles each extended further on continued
elevated, distributed volume: 00:15-00:30 (+11.2pt, vol 10,358, new high 3380.50), 00:30-00:45
(+5.75pt, vol 6,840, new high 3383.075), and 00:45-01:00 (+3.6pt, vol 9,078, new high 3386.685).
Across the full sequence from the 00:00 low to the 01:00 high, price moved roughly 35.4 points
(3351.33 -> 3386.685) over four consecutive M15 candles, all on sustained rather than
single-minute-concentrated volume.

Unlike DC-0013 (which consolidated near its highs after the expansion), this move reversed: the
01:00-01:15 candle dropped 9.76pt to 3375.19 on 8,377 volume, and 01:15-01:30 continued down
another 4.09pt to 3371.665 on 8,158 volume, before 01:30-01:45 stabilized with volume normalizing
to 4,221.

## 2. Why It Attracted Attention

The initial candle's V-shape (light-volume decline into a fresh low, then sustained-volume reversal
past the starting price, all within one M15 candle) was already unusual enough for a registry entry.
That the reversal then continued building for three more candles, reaching a scale (~35pt) close to
DC-0013's (~43pt) — but at a completely different clock time (00:00-01:00 UTC, the specific hour
already carrying an eleven-instance comparative history in the Observation Registry) and ending in a
genuine reversal rather than consolidation — made this pass the v2 filter's bar for "materially
different from anything already catalogued at this hour." No prior 00:00-01:00 UTC instance in this
replay showed a decline-into-fresh-low-then-sustained-multi-candle-reversal-then-reversal shape.

## 3. Why It May Repeat

The underlying multi-minute sustained-volume construction has ample precedent (DC-0008, DC-0011,
DC-0013); what is new here is the specific sequencing (V-reversal from a fresh low -> multi-candle
continuation -> reversal) occurring at a clock time that has otherwise shown extreme-directional,
extreme-absorption, ordinary, and moderate-directional outcomes with no consistent characterization.
Whether this V-reversal-then-multi-candle-continuation shape recurs at this hour, or was a one-off,
cannot be established from a single instance.

## 4. Why It Deserves Further Investigation

This candidate, together with DC-0013, gives Alpha two documented instances of a "large sustained
multi-candle expansion" construction at two very different clock times and session contexts (NY
session vs. the Asia-hour transition already flagged for mixed behavior). Comparing how these two
instances resolved (DC-0013: consolidation near highs; DC-0014: reversal) is a natural next
comparison point for any future large sustained expansion, at this hour or elsewhere.

## 5. Confidence

**Low.** One instance, one instrument, one clock-time window (which itself already has a highly
mixed eleven-instance history). The initial V-shape anatomy and the multi-candle continuation are
each individually plausible mechanisms, but their combination and the subsequent reversal rest on
n=1 and should not be read as a repeatable pattern for this hour.

## Additional Notes (optional)

This candidate supersedes, in scope, the standalone Observation Registry entry filed for the
2025-08-26 00:00-00:15 UTC candle alone (that entry is left in place per the registry's append-only
rule, but is cross-referenced here as the origin of this candidate — see the registry's promotion
note added alongside this candidate). No external calendar catalyst is visible from price/volume
data alone; this candidate makes no claim about cause.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:3cdc39b74e1db801b2ead9ff0c2b63d93a92347d58ab49570bcc7f2fb7b056df**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
