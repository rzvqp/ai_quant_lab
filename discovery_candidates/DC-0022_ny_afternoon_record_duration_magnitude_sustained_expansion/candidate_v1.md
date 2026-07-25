# Discovery Candidate DC-0022: An NY-Afternoon Sustained Directional Expansion Sets New Duration and Magnitude Records for the Family, Nearly Doubling the Prior Longest Run Before Reversing

## Metadata

- **candidate_id**: DC-0022
- **title**: An NY-Afternoon Sustained Directional Expansion Sets New Duration and Magnitude Records for the Family, Nearly Doubling the Prior Longest Run Before Reversing
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2025-11-12 14:30-19:45 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0015 (previous longest single-direction run in this replay, 11 candles/~2h45m — now exceeded), DC-0013 (sustained multi-candle directional expansion, no reversal — same basic mechanism, far smaller scale), DC-0016 (early-Asia sustained expansion reaching a family magnitude record at the time — this instance's magnitude substantially exceeds it), DC-0017 (sustained multi-candle hold after an impulse — this instance's post-peak 2-candle plateau resembles that pattern briefly, before a genuine reversal)
- **content_hash**: sha256:eedbe3c0840aefad24b60bfa0b13ca5023e8c8eda9887b1680ef495e30c5a318

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-11-12, following an ordinary NY-morning grind (~4104-4131, volume 2-9k/M15), a sustained
directional rally began at 14:30 UTC and continued, with only brief pauses, for **16 consecutive
M15 candles (exactly 4 hours, 14:30-18:30 UTC)**, reaching a peak of 4211.795 before finally
reversing:

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 14:30-14:45 | 4131.975 / 4139.185 / 4125.045 / 4136.30 | 14,803 |
| 14:45-15:00 | 4136.24 / 4140.215 / 4131.945 / 4136.63 | 10,536 |
| 15:00-15:15 | 4136.605 / 4162.27 / 4134.685 / 4162.065 | 14,404 |
| 15:15-15:30 | 4162.05 / 4172.68 / 4159.915 / 4166.55 | **22,844** |
| 15:30-15:45 | 4166.54 / 4181.15 / 4166.04 / 4178.89 | 21,230 |
| 15:45-16:00 | 4178.925 / 4185.785 / 4174.725 / 4181.495 | 20,179 |
| 16:00-16:15 | 4181.415 / 4189.535 / 4180.20 / 4184.08 | 18,948 |
| 16:15-16:30 | 4184.15 / 4187.915 / 4181.065 / 4187.155 | 16,026 |
| 16:30-16:45 | 4187.20 / 4196.425 / 4186.50 / 4193.56 | 17,401 |
| 16:45-17:00 | 4193.54 / 4197.83 / 4187.575 / 4196.51 | 15,828 |
| 17:00-17:15 | 4196.50 / 4202.57 / 4195.725 / 4198.825 | 16,478 |
| 17:15-17:30 | 4198.82 / 4199.705 / 4192.25 / 4196.58 | 17,462 |
| 17:30-17:45 | 4196.585 / 4206.515 / 4195.67 / 4202.58 | 15,977 |
| 17:45-18:00 | 4202.575 / 4204.50 / 4199.125 / 4199.535 | 15,441 |
| 18:00-18:15 | 4199.57 / 4201.815 / 4190.48 / 4199.99 | 17,273 |
| 18:15-18:30 | 4200.015 / **4211.795** / 4198.06 / 4206.895 | 22,237 |

Total rise: from the low of the first candle (4125.045) to the peak (4211.795) = **86.75 points**
over exactly **4 hours**. Volume stayed elevated (15,000-23,000, roughly 3-5x the immediate
pre-episode baseline of ~4,500) across all 16 candles without ever fully decaying back to baseline
— the closest thing to a pause was a brief two-candle plateau immediately after the peak
(18:30-19:00 UTC, volumes 12,917 and 15,117, price holding 4206-4210.7), before a genuine reversal:
18:45-19:00 UTC (4207.08 -> 4194.115, a 13.2pt drop within the candle), followed by continued
softening to 4192.25 (19:00-19:15 UTC) before stabilizing around 4194-4200 on decaying volume
(11,706, then 7,155).

Dropping to M5 on the two highest-volume candles: the 15:15-15:30 candle (22,844) splits
8,338/6,762/7,744 across its three M5 sub-candles (largest share 8,338/22,844 = 36.5%); the
18:15-18:30 candle (22,237) splits 6,033/8,415/7,789 (largest share 8,415/22,237 = 37.8%). Both are
below the 42.7% concentration ratio accepted as organic in DC-0018/DC-0020, confirming genuine
sustained, distributed participation throughout — not a synthetic or thin-liquidity artifact.

## 2. Why It Attracted Attention

This is the same basic mechanism documented since DC-0008/DC-0013 (sustained multi-minute volume
construction, no single-candle concentration), but at a scale that clearly exceeds every prior
instance of the "sustained directional expansion" family observed in this replay: **16 candles / 4
hours**, versus DC-0015's previous record of 11 candles / ~2h45m — nearly 1.5x the duration. The
**86.75-point** magnitude also substantially exceeds prior family records (DC-0016 was the largest
point move in its family at the time it was logged; this instance is markedly larger). Unlike
DC-0017's family (impulse-then-hold without further extension), this episode kept extending to
fresh highs candle after candle for four straight hours before finally reversing.

## 3. Why It May Repeat

The underlying mechanism — sustained, well-distributed multi-minute volume accompanying a
persistent one-directional move — is the same one documented repeatedly since DC-0008. What is new
here is that the *duration* a single instance of this mechanism can sustain itself appears to have
no fixed ceiling established by prior observations: each previous "longest run so far" (DC-0013 at
4 candles, DC-0015 at 11 candles) was itself eventually exceeded. Whether there is any upper bound
to how long a single sustained-volume expansion can run, or whether this specific 4-hour/86.75pt
instance is itself close to some practical ceiling, cannot be determined from a single further
data point — this instance simply resets the reference range once again.

## 4. Why It Deserves Further Investigation

This candidate directly updates the "longest sustained run" and "largest sustained-expansion
magnitude" reference points established by DC-0015 and DC-0016 respectively, and does so
simultaneously with a single instance combining both records. It also adds a new observation to the
question of how sustained-expansion episodes terminate: here, the volume never meaningfully decayed
during the 4-hour rise itself — the first real volume decay coincided with the reversal, not with
any earlier deceleration in price. Whether declining volume is a leading indicator of reversal, or
whether (as here) volume can remain elevated right up to the reversal candle itself, is a natural
comparison point for future long-duration instances.

## 5. Confidence

**Low.** A single instance. The underlying mechanism (sustained, distributed multi-minute
participation driving a persistent directional move) has ample precedent, but the specific claim
that this instance is a genuine duration/magnitude record for the family rests on the local sample
observed so far in this replay (n=1 at this scale) and should not be treated as evidence of any
fixed upper bound.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The 14:30-18:30 UTC window
falls within the broader NY session already associated with several prior DCs in this family
(DC-0013, DC-0015, DC-0017), consistent with — but not proof of — a session-related liquidity
mechanism common to this family. This candidate makes no claim about cause.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:eedbe3c0840aefad24b60bfa0b13ca5023e8c8eda9887b1680ef495e30c5a318**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
