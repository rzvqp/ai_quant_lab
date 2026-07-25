# Discovery Candidate DC-0023: An 8-Hour Multi-Leg, Choppy Episode at Persistently Extreme Volume, Containing a Single Candle Among the Largest-Volume Candles in the Replay

## Metadata

- **candidate_id**: DC-0023
- **title**: An 8-Hour Multi-Leg, Choppy Episode at Persistently Extreme Volume, Containing a Single Candle Among the Largest-Volume Candles in the Replay
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2025-11-13 13:00-21:00 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0022 (the immediately preceding candidate — longest *clean one-directional* sustained expansion, 4h/16 candles — this episode is instead choppy/multi-leg and roughly double the duration), DC-0020 (37,204 volume, the current all-time single-candle volume record) and DC-0018 (36,798) — this episode's peak candle (28,254) is the third-highest single-candle volume observed in the replay, DC-0017 Addendum A (extended high-volume choppy regime, the closest prior precedent for a multi-hour non-directional high-volume episode — this instance is substantially longer and at higher volume), DC-0012 (sustained high volume, no net displacement — the "absorption" framing this episode's choppiness partially resembles, though this episode does eventually displace price by ~55pt net)
- **content_hash**: sha256:5113f459c27ae3ce39110515e923db31a7db2fc8f146116fa7283ed1993e288e

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

Immediately following the record sustained expansion documented in DC-0022 (which peaked at
4245.195, 12:45-13:00 UTC), price entered a markedly different regime: instead of a clean
directional move or a quiet absorption, it produced a **continuous 8-hour (13:00-21:00 UTC, 32
consecutive M15 candles), multi-leg, choppy episode in which volume never fully returned to
baseline** (pre-episode baseline was ~1-4k/M15; this episode ran almost entirely in the
9,000-22,700 range) until its very end.

Representative candles from across the episode:

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 13:00-13:15 | 4242.80 / 4244.10 / 4225.955 / 4230.795 | 18,586 |
| 13:45-14:00 | 4228.55 / 4232.505 / 4224.25 / 4231.745 | 15,125 |
| 14:30-14:45 | 4211.12 / 4220.275 / **4184.51** / 4187.89 | 22,697 |
| 14:45-15:00 | 4187.94 / 4201.14 / 4185.34 / 4195.525 | 22,434 |
| 15:45-16:00 | 4197.79 / 4203.54 / 4188.725 / 4202.675 | 20,067 |
| 16:30-16:45 | 4206.665 / 4208.985 / 4195.705 / 4197.755 | 18,325 |
| 17:30-17:45 | 4195.28 / 4205.05 / 4193.35 / 4202.865 | 15,952 |
| 18:15-18:30 | 4202.095 / 4203.03 / **4187.705** / 4190.575 | 13,758 |
| 18:30-18:45 | 4190.505 / 4190.915 / **4145.19** / 4155.915 | **28,254** |
| 19:15-19:30 | 4160.03 / 4169.95 / 4158.215 / 4169.85 | 12,773 |
| 20:30-20:45 | 4164.925 / 4167.32 / 4160.88 / 4164.17 | 14,260 |
| 20:45-21:00 | 4164.16 / 4181.265 / 4161.23 / 4178.58 | 4,999 |
| 21:00-21:15 | 4178.56 / 4178.635 / 4175.535 / 4174.06 | 2,298 |

Throughout the episode, price oscillated repeatedly — declining, bouncing, declining further to a
new low, bouncing again — rather than resolving cleanly in one direction (unlike DC-0022) or
sitting still on high volume (unlike DC-0012). The single most extreme moment came at 18:30-18:45
UTC: a **45.7-point single-candle range** (4190.915 high to 4145.19 low) on **28,254 volume** — the
**third-highest single-candle volume observed anywhere in this replay**, behind only DC-0020
(37,204) and DC-0018 (36,798). Dropping to M5 on this candle, volume splits 9,974/11,933/6,347
across the three sub-candles (largest share 11,933/28,254 = 42.2%, just under the 42.7%
concentration ratio accepted as organic in DC-0018/DC-0020), confirming genuine sustained
participation rather than a single-minute artifact. A second organic check on an earlier
high-volume candle (14:30-14:45 UTC, 22,697) splits 6,720/7,669/8,308 (largest share 36.6%),
likewise organic.

Total range across the full episode: from the pre-episode peak (4245.195) to the episode's lowest
point (4145.19) = **100.005 points**. Volume only returned to the pre-episode baseline in the final
two candles (4,999, then 2,298) — the first sustained volume decay of the entire 8 hours.

## 2. Why It Attracted Attention

This episode combines duration, magnitude, and an embedded extreme-volume event in a way no prior
candidate has: (a) at **8 hours / 32 candles**, it is roughly double the duration of DC-0022's
record-setting clean expansion (4h/16 candles) — but where DC-0022 resolved cleanly in one
direction, this episode never did, oscillating instead; (b) its **100.005-point total range**
exceeds even DC-0022's 86.75pt; (c) it contains a single candle (28,254 volume) that is itself a
near-record event on par with DC-0018/DC-0020, embedded in the middle of a much longer episode
rather than standing alone. No prior candidate documents an episode where volume stays this
elevated for this long without either a clean directional resolution or a stable absorption
plateau.

## 3. Why It May Repeat

The underlying mechanism (sustained, well-distributed multi-minute participation) is the same one
documented since DC-0008, but this instance shows that mechanism can persist far longer, and in a
non-directional/choppy form, than any prior instance suggested. Whether this reflects the market
"working off" the preceding DC-0022 expansion (i.e., the sustained-expansion and choppy-absorption
mechanisms are causally linked as a two-part sequence at a larger scale than DC-0021's smaller
decline-into-absorption pairing), or is an independent event that merely happened to follow
DC-0022, cannot be determined from a single instance immediately following a single other instance.

## 4. Why It Deserves Further Investigation

This candidate raises a specific question about DC-0021's smaller-scale "decline into absorption"
mechanism: does that same two-phase logic scale up, with a large one-directional expansion
(DC-0022) followed by a proportionally large and long choppy/absorption episode (this candidate)?
The two episodes occurred back-to-back in this replay, which is suggestive but is only n=1 for this
specific sequencing claim. It also updates the reference point for "extreme single-candle volume"
context — the 28,254 candle here is organic and embedded mid-episode, unlike DC-0018/DC-0020 where
the record candle triggered or capped its episode.

## 5. Confidence

**Low.** A single instance, immediately following a single other instance (DC-0022) in this local
sample. The individual elements (sustained multi-minute volume, choppy/two-sided resolution,
organic extreme-volume candles) all have precedent, but the specific combination — 8 hours of
continuous elevated volume without a directional resolution, containing a near-record single
candle — rests on n=1 and should not be treated as a repeatable signature. The apparent
DC-0022-then-DC-0023 sequencing is noted only as an observation for future comparison, not a claim.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The 13:00-21:00 UTC window
spans NY-morning through NY-evening, overlapping several session windows already associated with
other DCs in this family. This candidate makes no claim about cause.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:5113f459c27ae3ce39110515e923db31a7db2fc8f146116fa7283ed1993e288e**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
