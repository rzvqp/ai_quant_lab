# Discovery Candidate DC-0021: A Sustained NY-Morning Decline Transitions Directly Into a Multi-Candle Absorption Phase at Persistently Elevated Volume, With No Volume Decay Between Phases

## Metadata

- **candidate_id**: DC-0021
- **title**: A Sustained NY-Morning Decline Transitions Directly Into a Multi-Candle Absorption Phase at Persistently Elevated Volume, With No Volume Decay Between Phases
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2025-11-06 14:00-16:45 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0013 (sustained multi-candle directional expansion, no reversal — contrast: here the directional phase does not simply exhaust itself; it hands off into a second, distinct absorption phase at undiminished volume), DC-0015 (11-candle, ~2h45m sustained expansion, the longest single-direction run observed — this episode matches that candle count and duration almost exactly, but is NOT single-direction: it splits into a ~5-candle decline followed by a ~6-candle absorption/consolidation), DC-0012 (sustained high volume with no net displacement, "absorption" — contrast: here absorption is not a stand-alone episode but the immediate second phase of one continuous elevated-volume event, following directly from a directional decline with no volume decay at the transition), DC-0018 / DC-0020 (extreme, record-setting single-candle volume — contrast: here peak volume, 20,973, is moderate — roughly 2.4x the immediate pre-episode baseline of ~8,000 — not a new record and not concentrated in one candle)
- **content_hash**: sha256:2988116288277a049c65127c0e97c780801e6566fb384beb7adf5f7f2c15a9f8

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-11-06, following a quiet baseline (~4012-4014, volume ~8,000/M15), an 11-consecutive-candle,
~2h45m episode (14:00-16:45 UTC) unfolded in two distinct phases without any volume decay at the
transition between them:

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 14:00-14:15 | 4012.315 / 4014.09 / 4005.00 / 4008.305 | 13,871 |
| 14:15-14:30 | 4008.30 / 4008.30 / 3989.095 / 3992.06 | 15,416 |
| 14:30-14:45 | 3992.00 / 4003.265 / 3990.895 / 3998.415 | 19,026 |
| 14:45-15:00 | 3998.395 / 4001.235 / 3992.80 / 3993.41 | 19,017 |
| 15:00-15:15 | 3993.08 / **3993.90** / **3978.245** / 3982.775 | **20,973** |
| 15:15-15:30 | 3982.80 / 3991.10 / 3981.70 / 3986.80 | 16,116 |
| 15:30-15:45 | 3987.055 / 3987.39 / **3975.08** / 3978.48 | 16,743 |
| 15:45-16:00 | 3978.47 / 3984.375 / 3976.84 / 3980.405 | 18,998 |
| 16:00-16:15 | 3980.48 / 3986.45 / 3979.785 / 3981.965 | 18,625 |
| 16:15-16:30 | 3981.985 / 3984.12 / 3976.72 / 3983.755 | 18,307 |
| 16:30-16:45 | 3983.705 / 3984.11 / 3976.595 / 3979.37 | 11,766 |
| 16:45-17:00 (post-episode) | 3979.295 / 3984.825 / 3977.99 / 3981.03 | 9,703 |

**Phase 1 (14:00-15:15 UTC, 5 candles, ~1h15m)**: a net directional decline from the 4012.315 open
to a fresh low of 3978.245 (~34 points), with volume ramping steadily upward across all five
candles (13,871 -> 15,416 -> 19,026 -> 19,017 -> 20,973, the episode's peak). This is a gradual,
multi-candle volume *escalation*, not a single spike.

**Phase 2 (15:15-16:45 UTC, 6 candles, ~1h30m)**: price oscillates within a tightening ~3975-3991
band (net displacement from phase-2 open, 3982.80, to phase-2 close, 3979.37, of only ~3.4 points,
including one further marginal low at 3975.08 that was not sustained) while volume *remains
elevated* (16,116-18,998, averaging ~16.5k) for five consecutive candles before finally dropping to
11,766 and then to 9,703 (near the pre-episode baseline) only in the final two candles. Volume does
**not** decay proportionally with the sharply reduced net price movement at the phase 1 -> phase 2
transition — it stays near its phase-1 peak for roughly another hour before finally normalizing.

Dropping to M5 on the peak-volume candle (15:00-15:15 UTC, 20,973), volume splits 7,144 / 7,710 /
6,119 across the three M5 sub-candles — the largest single component is 7,710/20,973 = 36.8% of the
total, below the 42.7% concentration ratio accepted as organic in DC-0018/DC-0020, confirming a
genuinely sustained, distributed construction rather than a single-minute concentrated spike.

## 2. Why It Attracted Attention

Two already-documented mechanisms appear here, but their **sequencing and continuity** is new: (a)
a sustained, gradually-escalating-volume directional decline (structurally similar to DC-0013's
expansion family, but downward and volume-ramping rather than already-high-from-the-start), followed
immediately by (b) a sustained-high-volume, near-zero-net-displacement absorption phase (DC-0012's
signature) — with **no volume decay at the boundary** between the two phases. In every prior
DC/Addendum documenting either phase in isolation, the episode was treated (and resolved) as one
mechanism. Here, one continuous ~2h45m, 11-candle elevated-volume event visibly hands off from one
mechanism into the other without the volume itself ever signaling the transition.

## 3. Why It May Repeat

If sustained-volume directional moves and sustained-volume absorption are in fact related phases of
a single underlying liquidity/participation event (rather than two unrelated, coincidentally
adjacent phenomena), this sequence — escalate, peak, decline-into-absorption, hold, then decay —
could recur as a general shape for how elevated-volume episodes resolve. A single instance cannot
establish this; DC-0012's own absorption instances were not preceded by an immediately adjacent
directional-decline phase in the same continuous elevated-volume run, so whether this hand-off
pattern is typical or unusual for absorption episodes generally is an open question.

## 4. Why It Deserves Further Investigation

This candidate sits directly at the boundary between three previously separate families (DC-0013
directional expansion, DC-0015 long-duration single-direction runs, DC-0012 absorption) and proposes
that at least in this instance they are not separate mechanisms but sequential phases of one event.
Whether volume level (rather than volume *change*) is the more informative signal — i.e., whether
"volume stays elevated" matters more than "volume is rising vs. falling" for predicting continued
market activity — is a natural question raised directly by this episode's flat ~16.5k plateau
through six candles of net-flat price action.

## 5. Confidence

**Low.** A single instance. Each phase individually replicates an already-documented mechanism
(DC-0013-style escalating-volume decline; DC-0012-style absorption), but the specific claim here —
that they occurred as one continuous, boundary-less event with no intervening volume decay — rests
on n=1 and should not be treated as a repeatable signature.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The 14:00-16:45 UTC window
falls within the broader NY-morning session already associated with several prior DCs (DC-0013,
DC-0015, DC-0017), consistent with — but not proof of — a session-related liquidity mechanism common
to this family. This candidate makes no claim about cause and no claim that the two-phase structure
observed here is the general or typical resolution shape for elevated-volume episodes.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:2988116288277a049c65127c0e97c780801e6566fb384beb7adf5f7f2c15a9f8**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
