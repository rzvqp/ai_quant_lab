# Discovery Candidate DC-0025: A Two-Candle Escalating-Volume Waterfall Decline Sets a New All-Time Volume Record, Then Retraces ~75% Before Consolidating

## Metadata

- **candidate_id**: DC-0025
- **title**: A Two-Candle Escalating-Volume Waterfall Decline Sets a New All-Time Volume Record, Then Retraces ~75% Before Consolidating
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-25
- **date_frozen**: 2026-07-25
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2026-01-16 15:00-16:45 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0013/DC-0015/DC-0021/DC-0022/DC-0024 (sustained multi-candle directional decline/expansion family — same basic directional-move-then-partial-recovery shape, but all of those unfold across 4-19 consecutive M15 candles / 45min-4h45m; this instance completes in 2 candles/30min, an order of magnitude faster than the family's stated minimum of four candles), DC-0020 (previous all-time single-candle volume record, 37,204 — now displaced to 2nd place), DC-0018 (36,798, now 3rd place), DC-0013 Addendum L (34,453, now 4th place)
- **content_hash**: sha256:b0929b2063ac55b659418067b8d6b5f3dba0c576a8b8dd68e767bb8d60be4539

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2026-01-16, following an ordinary session grind (~4598-4620, volume 3-21k/M15, consolidating
since the prior weekend), price reached a local high of **4620.39** (candle 15:00-15:15 UTC) before
a sharp decline began at 15:15 UTC and completed in just **two M15 candles (30 minutes)**:

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 15:00-15:15 (pre-decline) | 4607.675 / **4620.39** / 4607.46 / 4616.115 | 16,269 |
| 15:15-15:30 | 4616.08 / 4617.75 / 4564.575 / 4565.21 | 31,293 |
| 15:30-15:45 | 4565.205 / 4570.575 / **4536.49** / 4555.56 | **39,353** |
| 15:45-16:00 (recovery) | 4555.84 / 4575.66 / 4555.84 / 4571.31 | 27,589 |
| 16:00-16:15 (recovery) | 4571.265 / 4593.465 / 4567.795 / 4593.12 | 24,808 |
| 16:30-16:45 (recovery peak) | 4592.03 / **4599.2** / 4588.25 / 4596.34 | 16,607 |

Total decline: from the pre-episode high (4620.39) to the episode low (4536.49) = **83.9 points in
30 minutes** — roughly the same order of magnitude as several DC-0013-family instances, but
compressed into a fraction of their typical duration (the family's defining minimum is four
consecutive M15 candles / ~1h; this instance is two candles / 30min). The second candle's volume,
**39,353**, is a **new all-time single-candle volume record for this replay**, exceeding DC-0020's
previous record (37,204) by 2,149 (+5.8%) and displacing it to 2nd place.

Dropping to M5 to examine the internal structure of the two record candles (six 5-minute
sub-candles, 15:15-15:45 UTC):

| M5 candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 15:15-15:20 | 4616.08 / 4617.75 / 4601.415 / 4601.945 | 6,380 |
| 15:20-15:25 | 4601.97 / 4611.35 / 4588.56 / 4588.6 | 11,290 |
| 15:25-15:30 | 4588.635 / 4593.04 / 4564.575 / 4565.21 | 13,623 |
| 15:30-15:35 | 4565.205 / 4570.575 / **4536.49** / 4544.11 | **15,221** |
| 15:35-15:40 | 4543.94 / 4555.965 / 4538.485 / 4548.375 | 12,953 |
| 15:40-15:45 | 4548.4 / 4557.075 / 4544.37 / 4555.56 | 11,179 |

Volume **escalates smoothly across four consecutive sub-candles** (6,380 -> 11,290 -> 13,623 ->
15,221), peaking in the exact sub-candle that prints the episode low (4536.49), then **decays** as
price recovers (12,953 -> 11,179) — a clean escalating-volume-into-climax-low signature, not a
single isolated spike. Price action across all six sub-candles chains continuously (each close
matches the next open almost exactly, no teleporting), consistent with genuine continuous trading.

Organic-construction check on the two M15 candles: candle 1 (15:15-15:30, 31,293) splits
6,380/11,290/13,623 across its three M5 sub-candles — largest share 13,623/31,293 = **43.5%**,
marginally above the 42.7% reference threshold. Candle 2 (15:30-15:45, the new record, 39,353)
splits 15,221/12,953/11,179 — largest share 15,221/39,353 = **38.7%**, below the threshold. Given
the continuous OHLC chaining, the healthy (not sparse) volume on every sub-candle, and the coherent
escalating-then-decaying volume profile across the full six-candle window, this is judged organic
market activity, not a data artifact — the marginal 43.5% figure on one candle is noted honestly but
is far from the sparse/uniform/low-volume signature of the Black Friday artifact precedent.

After the low, price recovered substantially: from 4536.49 to a peak of 4599.2 (16:30-16:45 UTC) =
**62.71 points, a ~74.7% retracement** of the 83.9-point decline, on gradually decaying volume. Price
then consolidated in a 4576-4599 range for the remainder of the session (already logged in
SESSION_STATE.md as ordinary chop prior to this investigation), closing the week at 4596.32 ahead of
the weekend gap — **24.07 points below the pre-decline high**, a partial but not full recovery,
matching the family's usual "partial recovery, does not fully retrace" resolution shape.

**Methodological note**: this event was initially missed mid-batch — the standard 30-step
`replay_step` batch that contained it also carried the position across the subsequent weekend gap
before the M15 `data_get_ohlcv` check was performed. The M15 record was still fully retrievable
(M15 history is retained for the full replay), and M5 sub-bar data for organic verification was
still reachable by requesting a larger `count` (the 5M buffer holds ~300 bars counted backward from
the live cursor, and the weekend gap does not consume bars, so the event remained within reach this
time). This is filed as an operational caveat for future batches, not a data-quality issue with this
candidate.

## 2. Why It Attracted Attention

This episode sets a new all-time single-candle volume record (39,353) and does so with an unusually
fast (2-candle, 30-minute) escalating-volume-into-climax structure — markedly faster than every
other sustained-decline/expansion candidate in this replay (DC-0013's own defining minimum is four
consecutive M15 candles; DC-0015 spans eleven candles/2h45m; DC-0022 and DC-0024 span hours). The
combination of record volume and extreme velocity, at a session time (mid-morning NY, ~1h45m after
the 13:30 UTC open) distinct from DC-0013's NY-open timing, DC-0018's fresh-high-failure structure,
and DC-0020's 18:00 UTC low-sweep/failed-reclaim/bidirectional structure, does not fit cleanly as an
addendum to any existing candidate.

## 3. Why It May Repeat

The broader family of "large directional move, escalating/sustained volume, partial recovery" is
well established since DC-0008/DC-0013. What is new here is the demonstration that this family's
mechanism can also manifest at a dramatically compressed timescale (30 minutes rather than 1+ hour)
while still reaching record-setting volume — suggesting the underlying driver (aggressive,
continuous order flow) is not inherently tied to any particular duration. Whether such fast, record
episodes recur, and whether they cluster around any particular time-of-day beyond this single
mid-morning-NY instance, is not established by n=1.

## 4. Why It Deserves Further Investigation

This candidate is a natural comparison point against the DC-0013 family (same directional-decline
shape, ~5-8x faster realization) and against DC-0018/DC-0020 (both prior volume-record holders, both
displaced here) to examine whether "speed of realization" and "peak volume" are related or
independent axes of these episodes. It also raises a question about the minimum viable duration for
this replay's largest-volume events — this instance suggests record volume does not require a
multi-hour buildup.

## 5. Confidence

**Low.** A single instance. The underlying "large move, escalating volume, partial recovery"
mechanism has ample precedent, but the specific 2-candle/30-minute compression to a new all-time
volume record rests on n=1 and should not be treated as evidence that record-volume events typically
resolve this fast. The one M5 concentration figure marginally exceeding the organic-construction
convention (43.5% vs. 42.7%) is flagged honestly above and weighed against the coherent, continuous,
healthy-volume price action surrounding it.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The 15:15-15:45 UTC window
falls roughly 1h45m after the NY cash-session open (13:30 UTC), a time not previously associated
with any of this replay's record-setting episodes. This candidate makes no claim about cause.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-25**. Content hash to be computed and recorded in
`HANDOFF_LOG.md` at handoff time. This document is immutable from this point forward. Any correction
or new evidence must be filed as a separate, dated addendum in this candidate's folder, or as a new
version file — never as an edit to this file.
