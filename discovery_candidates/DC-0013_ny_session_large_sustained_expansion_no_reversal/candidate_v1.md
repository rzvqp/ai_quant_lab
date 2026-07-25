# Discovery Candidate DC-0013: A Large NY-Session Directional Expansion Built From Sustained Multi-Minute Volume, Extending Across Four Consecutive M15 Candles With No Reversal

## Metadata

- **candidate_id**: DC-0013
- **title**: A Large NY-Session Directional Expansion Built From Sustained Multi-Minute Volume, Extending Across Four Consecutive M15 Candles With No Reversal
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-08-22 13:30-15:00 UTC, OANDA:XAUUSD M15/M5/M1 replay window
- **related_ids**: DC-0008 (sustained multi-minute construction), DC-0011 (single-minute sweep-reclaim-extend — contrasted here as a different construction type), DC-0002/DC-0003 (HTF-scale directional resolution)
- **content_hash**: sha256:fc8991fbf2f994e7d4ea112fac913610a31c95eacbbb37ec6dcbcff4c36c3b9a

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-08-22, during the New York session, the M15 candle 14:00-14:15 UTC ran O3333.97 H3361.10
L3333.97 C3358.90 — a 27.13-point range, volume 29,674 (roughly 5-6x the immediately preceding M15
candles' 3,755-6,614). Dropping to M1, the displacement was NOT concentrated in a single minute:
every one of the 15 one-minute candles carried real, broadly comparable volume (1,164-3,226, no
single dominant minute), and price advanced in a genuine multi-leg climb from 3333.97 to a session
high near 3361 across the full 15 minutes — the same "sustained multi-minute" construction
documented in DC-0008, not the single-minute-concentration construction of DC-0011.

Unlike prior sustained-construction instances (DC-0008's original 39-point NFP candle, or the
various ordinary/ordinary-adjacent instances catalogued since), this move did not stop at one
candle: the following three M15 candles each extended further in the same direction on continued
elevated volume — 14:15-14:30 (+10.7pt, vol 20,436, new high 3367.865), 14:30-14:45 (+8.3pt, vol
13,763, new high 3374.32), and 14:45-15:00 (a smaller +4.25pt, vol 10,487, consolidating near
3372.5-3376.8). A fifth candle (15:00-15:15, vol 9,833) continued to consolidate near the highs
(3373-3377.9) rather than reverse. Across the full four-candle expansion (14:00-15:00 UTC), price
moved roughly 43 points (3333.97 -> 3376.77 high) without a single meaningful pullback candle.

## 2. Why It Attracted Attention

This is one of the largest sustained, multi-candle directional moves observed anywhere in this
replay to date — comparable in single-candle magnitude to DC-0008's original NFP instance (39pt,
24,005 vol) and DC-0011's sweep instance (15.5pt, 23,286 vol), but distinct from both in that: (a)
it repeated across four consecutive M15 candles rather than resolving in one, and (b) it showed no
sweep-and-reclaim anatomy at all — no wick deep into a level followed by reversal, just a
continuous, broadly sustained-volume climb. The v2 pre-investigation filter would have screened out
an ordinary NY-session volume pickup (volumes in the 5,000-12,000 range have been common and are
already catalogued as unremarkable NY character); this instance passed the filter specifically
because its first candle's volume (29,674) and range (27pt) were far outside that already-documented
NY-session envelope, and because the expansion continued rather than faded on the next candle.

## 3. Why It May Repeat

The underlying construction (sustained, broadly even multi-minute participation, no single-minute
concentration) is the same mechanism already documented in DC-0008 across six-plus instances at a
different clock time (12:30 UTC); this instance extends that construction type to the NY session
and to a much larger, multi-candle scale. Whether "large sustained multi-candle expansions with no
reversal" recur specifically during NY session hours, or whether this is a one-off magnitude
outlier, is not established by a single instance — this candidate exists so future NY-session
expansions of comparable scale can be compared against it.

## 4. Why It Deserves Further Investigation

The combination of (a) sustained rather than concentrated construction, (b) multi-candle
persistence without a pullback, and (c) magnitude near the top of everything observed in this
replay makes this a natural comparison point for any future large NY-session move — specifically to
determine whether the "extends across multiple candles without reversal" behavior recurs, or
whether the four-candle continuation here was itself an unusual, non-representative feature of this
particular instance.

## 5. Confidence

**Low.** One instance, one instrument, one session type. The construction mechanism (sustained
multi-minute volume) has multiple precedents (DC-0008), but the multi-candle, no-reversal
persistence at this magnitude has not been observed before in this replay and rests on n=1.

## Additional Notes (optional)

No external calendar catalyst is visible from price/volume data alone; this candidate makes no
claim about cause. The move's clock time (14:00-15:00 UTC) sits roughly 30-90 minutes after the
NY cash-equities-adjacent open (13:30 UTC) already characterized in prior sessions as an ordinary
elevated-volatility window — this instance's magnitude is well outside that ordinary envelope,
which is why it was flagged despite the v2 filter's intent to reduce investigation of routine
NY-open volatility.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:fc8991fbf2f994e7d4ea112fac913610a31c95eacbbb37ec6dcbcff4c36c3b9a**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
