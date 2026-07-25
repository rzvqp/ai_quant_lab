# Discovery Candidate DC-0024: A London-Morning Sustained Decline Sets a New All-Time Magnitude Record (125.7 Points), Then Partially Recovers

## Metadata

- **candidate_id**: DC-0024
- **title**: A London-Morning Sustained Decline Sets a New All-Time Magnitude Record (125.7 Points), Then Partially Recovers
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2025-11-14 11:45-16:30 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0022 (previous all-time magnitude record, 86.75pt clean upward expansion — now exceeded, in the opposite direction), DC-0023 (previous episode, 8h/100pt choppy — this instance is shorter but reaches a larger total point range), DC-0013/DC-0021 (sustained multi-candle decline family — same basic mechanism at a larger scale), DC-0020/DC-0018 (37,204 / 36,798 all-time single-candle volume records — this episode's peak candle, 24,655, ranks below both but is still a large, organic-verified volume event)
- **content_hash**: sha256:813c1d0edb21b54885374fa4e5b34f8309817ddee01f1bf1e84924b863757dad

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-11-14, following an ordinary London-morning grind (~4148-4158, volume 2-5k/M15), a sustained
decline began at 11:45 UTC and continued, with volume staying elevated almost throughout, for **19
consecutive M15 candles (4h45m, 11:45-16:30 UTC)**, reaching a low of 4032.23 before partially
recovering:

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 11:45-12:00 | 4153.585 / 4153.75 / 4130.92 / 4133.18 | 13,743 |
| 12:00-12:15 | 4133.085 / 4140.75 / 4123.88 / 4125.98 | 12,005 |
| 12:15-12:30 | 4125.925 / 4128.705 / 4111.09 / 4113.335 | 11,794 |
| 12:45-13:00 | 4115.455 / 4119.675 / 4109.83 / 4116.26 | 11,207 |
| 13:00-13:15 | 4116.255 / 4119.245 / **4084.31** / 4086.395 | 15,417 |
| 13:15-13:30 | 4086.47 / 4092.13 / **4053.41** / 4055.835 | 19,949 |
| 13:30-13:45 | 4055.735 / 4063.83 / 4046.47 / 4054.95 | 18,112 |
| 13:45-14:00 | 4054.965 / 4058.005 / 4041.37 / 4055.975 | 16,838 |
| 14:00-14:15 | 4055.835 / 4056.05 / **4037.68** / 4050.43 | 16,958 |
| 14:15-14:30 | 4050.36 / 4060.47 / 4046.495 / 4053.63 | 10,793 |
| 14:30-14:45 | 4053.66 / 4072.45 / **4032.23** / 4067.8 | **24,655** |
| 14:45-15:00 | 4067.8 / 4084.145 / 4063.29 / 4082.86 | 17,376 |
| 15:00-15:15 | 4082.81 / 4082.81 / 4068.31 / 4079.28 | 17,075 |
| 15:15-15:30 | 4079.35 / 4082.375 / 4071.465 / 4081.08 | 12,655 |
| 15:30-15:45 | 4081.12 / 4083.715 / 4072.66 / 4073.395 | 10,343 |
| 15:45-16:00 | 4073.33 / 4096.76 / 4072.05 / 4093.76 | 13,104 |
| 16:00-16:15 | 4093.75 / 4095.48 / 4081.1 / 4084.305 | 10,772 |
| 16:15-16:30 | 4084.31 / 4103.405 / 4082.485 / 4102.22 | 9,385 |
| 16:30-16:45 (recovery) | 4102.24 / 4111.185 / 4096.42 / 4108.295 | 8,119 |

Total decline: from the pre-episode high (4157.915, the candle just before 11:45 UTC) to the
episode low (4032.23) = **125.685 points** — a new all-time magnitude record for any single
directional leg observed in this replay, exceeding DC-0022's 86.75-point record (in the opposite
direction) and DC-0023's 100.005-point total range (which was choppy/bidirectional rather than one
clean leg). The decline's deepest point coincided with the episode's peak-volume candle
(14:30-14:45 UTC, 24,655) — the fourth-highest single-candle volume observed in this replay, behind
DC-0020 (37,204), DC-0018 (36,798), and DC-0023's embedded candle (28,254).

After the low, price recovered substantially over the following candles (4032.23 -> 4108.295, a
~76-point partial recovery by 16:30-16:45 UTC) on gradually decaying volume, without yet reaching a
full retrace of the decline.

Dropping to M5 for organic verification: the peak-volume candle (14:30-14:45 UTC, 24,655) splits
10,124/7,443/7,088 across its three sub-candles (largest share 10,124/24,655 = 41.1%, below the
42.7% concentration ratio, confirming organic construction). A second check on the candle
containing the episode's second-lowest point (14:00-14:15 UTC, 16,958) splits 8,162/4,830/3,966 —
largest share 8,162/16,958 = **48.1%, above the 42.7% threshold**. This one candle's volume is more
concentrated than the organic-construction convention established in DC-0018/DC-0020, though still
far from the flat/uniform-volume signature of a thin-liquidity artifact (all three M5 sub-candles
carried real, substantial volume and genuine price movement). It is noted here as a partial
data-quality caveat rather than treated as invalidating — a brief concentrated push at the exact
low of an extended decline (a stop-cascade-like moment) is a plausible market microstructure
feature, not necessarily an artifact signature.

## 2. Why It Attracted Attention

This episode sets a new all-time magnitude record (125.685pt) for any single directional leg in
this replay, in the exact opposite direction from DC-0022's own record-setting rally just one day
of replay-time earlier. It also demonstrates the same "large decline immediately followed by
substantial recovery" shape seen at smaller scale in DC-0019/DC-0021, but at nearly triple the
point-magnitude of any prior instance of that shape.

## 3. Why It May Repeat

The underlying mechanism (sustained, organically-distributed multi-minute volume driving a
persistent directional move) is the same one documented repeatedly since DC-0008/DC-0013. What
continues to be new, instance after instance, is that each "largest magnitude so far" record
(DC-0013's original scale, then DC-0022's 86.75pt, now this candidate's 125.685pt) has so far always
been superseded by a subsequent instance. Whether there is a practical ceiling to this magnitude, or
whether records will simply continue to be broken as more of the replay is observed, remains an
open question this instance does not resolve.

## 4. Why It Deserves Further Investigation

This candidate is a natural comparison point against DC-0022 (same underlying mechanism, opposite
direction, similar order of magnitude) and against DC-0019/DC-0021 (same "large move then partial
recovery" shape, much smaller scale). Whether large-magnitude moves in either direction show a
consistent partial-recovery percentage, or whether recovery extent is unrelated to the initiating
move's magnitude, is a question this single instance contributes one data point toward, not an
answer.

## 5. Confidence

**Low.** A single instance. The underlying mechanism has ample precedent, but the specific
125.685-point magnitude, and the partial (not yet complete, not yet quantified as a final ratio)
recovery observed so far, rest on n=1 and should not be treated as a repeatable magnitude ceiling or
recovery pattern. The one M5 concentration figure exceeding the organic-construction convention
(48.1% vs. the 42.7% reference) is flagged honestly above and should be weighed accordingly rather
than treated as fully resolved.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The 11:45-16:30 UTC window
spans London-morning through NY-morning-open, overlapping session windows already associated with
several prior DCs. This candidate makes no claim about cause.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:813c1d0edb21b54885374fa4e5b34f8309817ddee01f1bf1e84924b863757dad**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
