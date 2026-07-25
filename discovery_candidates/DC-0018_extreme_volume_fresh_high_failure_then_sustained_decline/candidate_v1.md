# Discovery Candidate DC-0018: An Extreme-Volume Spike to a Fresh Multi-Session High Fails Completely Within the Same Candle, Then Extends Into a Sustained Multi-Candle Decline

## Metadata

- **candidate_id**: DC-0018
- **title**: An Extreme-Volume Spike to a Fresh Multi-Session High Fails Completely Within the Same Candle, Then Extends Into a Sustained Multi-Candle Decline
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-09-09 14:00-16:00 UTC, OANDA:XAUUSD M15/M5/M1 replay window
- **related_ids**: DC-0006 (extreme-volume candles frequently fail to extend, the closest single-candle precedent), DC-0008 (sustained multi-minute construction), DC-0013/DC-0015 (the "large sustained expansion" family, here inverted in direction), DC-0017 (largest prior single-candle volume, 30,975, now exceeded)
- **content_hash**: sha256:40ce847f27f85220eb26b9ee569b3869fb440b2282d4b07006a4764a1cf4786f

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-09-09, the 14:00-14:15 UTC M15 candle ran O3665.95 H3674.695 L3642.18 C3651.75, volume
36,798 -- the largest single-candle volume observed anywhere in this replay, exceeding DC-0017's
NFP-scale candle (30,975). Dropping to M1, the anatomy showed a rapid spike to the fresh
multi-session high of 3674.695 within the first ~3 minutes, followed by a sharp, sustained reversal
over the next ~8-9 minutes down to 3642.18 (a ~32.5pt round trip within the single candle), before
stabilizing near 3648-3652 for the remainder. Volume was distributed across all 15 one-minute
candles (1712-3237, no single dominant minute).

Unlike a simple failed-breakout that stabilizes, the elevated volume and downward pressure
continued for several further candles: 14:15-14:30 (vol 23,103, choppy 3645.8-3657.7), 14:30-14:45
(vol 23,884, new lower low 3636.005), 14:45-15:00 (vol 15,184), 15:00-15:15 (vol 16,260, new lower
low 3635.105), and 15:15-15:30 (vol 18,652, the lowest low of the sequence at 3626.915). From the
initial spike high (3674.695) to this lowest low, price declined roughly 47.8 points over
approximately 1h30m. Volume then began declining toward normalization over the following two
candles (12,212, 11,074). Dropping to M5 on the lowest-low candle showed distributed volume across
the three M5 sub-candles (7964/4799/5889), consistent with the sustained, non-concentrated
construction already documented in DC-0008/DC-0013/DC-0015.

## 2. Why It Attracted Attention

The v2 pre-investigation filter would ordinarily screen out an isolated large-volume candle as
matching DC-0006 (extreme volume frequently fails to extend). What passed the filter here was the
combination of (a) the largest single-candle volume in this replay to date, (b) reaching a fresh
multi-session high before failing -- not merely an ordinary elevated-volatility candle -- and (c)
the failure did not simply stabilize (as DC-0006 or DC-0017 describe) but extended into a sustained
~47.8-point multi-candle decline over 1h30m, a magnitude and duration comparable to the "large
sustained expansion" family (DC-0013/DC-0015) but in the opposite direction and preceded by a
failed breakout rather than a clean directional start.

## 3. Why It May Repeat

The underlying multi-minute sustained-volume construction is the same mechanism documented
repeatedly since DC-0008. What is new here is the specific combination: an extreme-volume push to a
fresh high, immediate and complete failure within the same candle, and a subsequent sustained
decline of comparable scale to the "large sustained expansion" family. Whether "spike to new high,
fail immediately, then sustained decline" is a recognizable, repeatable sequence -- as opposed to
this instance's large decline being unrelated aftermath -- cannot be established from a single
instance.

## 4. Why It Deserves Further Investigation

This candidate sits at the intersection of two previously separate observations: single-candle
extreme-volume failures (DC-0006) and multi-candle sustained directional moves (DC-0013/DC-0015/
DC-0016/DC-0017). Whether a failed fresh-high breakout on exceptional volume is itself a leading
indicator for a sustained move in the opposite direction -- as opposed to coincidence -- is a
natural question for future instances to address. The magnitude here (largest volume observed, one
of the largest point ranges) also makes this a useful reference point for calibrating what counts
as "extreme" going forward.

## 5. Confidence

**Low.** One instance. The multi-minute sustained-volume construction has strong precedent, but the
specific "extreme-volume fresh-high failure followed by sustained decline" sequence rests on n=1
and should not be treated as predictive of future breakout failures.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone; 14:00 UTC does not
correspond to any previously-documented scheduled-release window in this replay (unlike 12:30 UTC).
This candidate makes no claim about cause. Whether the initial spike to 3674.695 itself represented
a stop-run/liquidity-sweep above a prior high (a construction type documented differently in
DC-0011, where a sweep reclaimed and extended) versus a genuine but ultimately rejected breakout
attempt is not established here -- DC-0011's sweep-reclaim resolved by extending to new highs
afterward, which is the opposite of what happened in this instance.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:40ce847f27f85220eb26b9ee569b3869fb440b2282d4b07006a4764a1cf4786f**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
