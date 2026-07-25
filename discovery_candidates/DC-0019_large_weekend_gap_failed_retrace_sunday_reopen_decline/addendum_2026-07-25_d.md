# Addendum D to DC-0019 (dated 2026-07-25)

Filed per the Handoff Statement of `candidate_v1.md` — new evidence, not an edit to the frozen
document.

## New Observation

On 2026-02-27 21:45:00 UTC (Friday close, price 5278.51), the market closed for the weekend. On
reopen at 2026-03-01 23:00:00 UTC (Sunday, price 5368.53) — a standard-cadence gap of 177,300s
(49h15m, verified exactly on OHLCV bar timestamps) — the market produced a **+90.02pt gap up**, the
**largest weekend-gap magnitude of either direction observed in this replay**, exceeding Addendum C's
previous record (53.46pt, 2026-01-18) by 36.56pt (+68.4%).

As with every prior instance in this DC's family, the gap did not retrace: the reopen 5-minute
candle traded only 1 unit of volume at the exact gap-open price (5368.53) before the next 5-minute
candle absorbed the initial rush (9,741 volume), and price extended further in the gap's own
direction. Over the following ~40 minutes, price climbed to an intrabar high of **5394.005** (M15
candle 23:30-23:45 UTC, M5 sub-candle 23:40-23:45 UTC) — **115.495 points above the pre-gap close**,
a **new all-time record for total up-direction extension**, exceeding Addendum C's previous record
(94.62pt) by 20.875pt (+22.1%).

Dropping to M5 for organic verification on the two candles most relevant to this record: the reopen
candle (M15 23:00-23:15 UTC, volume 16,786) splits 1/9,741/7,044 — the first 5-min sub-candle's
near-zero volume (1 unit) reflects the same "thin liquidity at instant of reopen" microstructure
already documented for every prior weekend-gap reopen in this DC's history, not a data-quality
concern. The extension-peak candle (M15 23:30-23:45 UTC, volume 17,521) splits 4,579/4,079/8,863
(largest share 50.6%, above the 42.7% reference on a simple concentration basis) — however, checking
the volume-to-range ratio for this specific 5-minute sub-candle (8,863 volume / 19.165pt range =
462.4 vol/pt) shows it is *far above* this replay's normal baseline (~90-110), the opposite of the
thin-volume "data artifact" signature — this is a genuinely heavily-traded candle, not a concentrated
or fabricated print. The prior reopen 5-min candle (9,741 volume / 45.41pt range = 214.6 vol/pt) is
similarly well above baseline. Both candles are treated as fully organic.

## Why This Matters To DC-0019

This is now the **largest gap magnitude on record for this candidate, in either direction** (90.02pt,
displacing Addendum C's 53.46pt), and the **largest total extension on record** (115.495pt,
displacing Addendum C's 94.62pt) — both are decisive new records (+68.4% and +22.1% respectively),
well above the marginal/continuation threshold established elsewhere in this replay. This continues
the pattern first noted in Addendum C: this mechanism's magnitude ceiling keeps being extended by new
instances rather than converging on a fixed value, and the largest instances continue to occur on
up-gaps rather than down-gaps.

Three-part novelty test applied explicitly (CEO directive): (1) Is this a new MECHANISM? No — same
weekend-gap-with-extension-no-retrace mechanism as the base candidate and Addenda A/B/C. (2) Could
this be filed only as an Addendum? Yes — new records within an already-documented mechanism are the
textbook case for an addendum. (3) Is this a new record? Yes, decisively on both gap magnitude
(+68.4%) and total extension (+22.1%) — far above the marginal-noise threshold, which is precisely
why an addendum — not a new candidate — is the correct filing.

## Status

Alpha does not validate, reject, or update the confidence rating in this addendum — that remains as
recorded in `candidate_v1.md` v1 (Low). This addendum only files the new evidence for downstream
review.
