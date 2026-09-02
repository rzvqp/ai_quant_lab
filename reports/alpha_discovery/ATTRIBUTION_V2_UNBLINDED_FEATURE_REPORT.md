# ATTRIBUTION_V2_UNBLINDED_FEATURE_REPORT — what the blind ranking pointed at

Semantic unblinding executed **only after** `BLIND_ATTRIBUTION_RESULTS_V2.csv` was frozen and hashed (`8988448a…`). The blind ranking is
authoritative; unblinding is interpretation and did not reorder anything. Feature map sha256 `dc4dcae1…`.

## The blind ranking, unblinded
Ranked by number of objects with an FDR-significant POSITIVE-expectancy bin (the cross-strategy rescue count):

| blind id | true name | kind | #objects | #families | #mechanisms | recurrence gate (≥5 fam & ≥3 mech) |
|---|---|---|---|---|---|---|
| **f011** | **halfhour_bucket_utc** (30-min UTC bucket 0..47) | categorical | 10 | 10 | 8 | **YES** |
| **f017** | **hour_utc** | categorical | 7 | 7 | 5 | **YES** |
| **f016** | **bars_to_sess_end** (session-position countdown) | numeric | 6 | 5 | 3 | **YES** |
| f005 | atr_over_atrma (volatility state) | numeric | 5 | 4 | 4 | no (families<5) |
| f015 | compress_flag (ATR<0.8×MA) | bool | 4 | 3 | 3 | no |
| f039 | session_id (governed session block) | categorical | 4 | 4 | 4 | no |
| f040 | bar_in_sess (intra-session bar index) | numeric | 4 | 3 | 3 | no |
| f013 / f022 / f028 / f037 | location / range-state features | mixed | 3 each | ≤3 | ≤3 | no |

**Only three features clear the recurrence gate, and all three are TIME/SESSION-POSITION** — the 30-minute clock, the hour, and the
bars-remaining-in-session countdown. Volatility (f005) and coarse session (f039) rank *below* them and miss the gate.

## What this says about the V1 (human-prompted) attribution
- **V1 was partly prompt-seeded.** V1 emphasised session, volatility, H1/H4 alignment, and LONG/SHORT side — four conditions the human prompt
  named. Under blind ranking: **fine time-of-day wins**, coarse **session ranks lower**, **volatility is mid-pack**, and **side (entry_side
  f045, family_variant_side f025) and trend-state (h1 f024, d1 f031) do not rank in the recurrent top at all.**
- **Genuine unseeded discoveries (`NEW_UNSEEDED_DISCOVERY_FOUND = YES`):** (1) the **30-minute clock bucket** is a stronger cross-strategy
  discriminator than the coarse session we had been using; (2) **session-position** features — `bars_to_sess_end` and `bar_in_sess`, a
  countdown/position within the session block we never emphasised — recur across mechanisms. Time-of-day beats volatility (`Q15: TIME > VOL`).

## Interpretation — a lose-less clock, not a profitable clock
The recurrent winner is a **fine time-of-day tilt**: several unrelated mechanisms lose materially less (and a few of their subpopulations turn
positive) inside specific 30-minute UTC windows. But the pooled expectancy of even the single best window is **−0.14R** (§30). So the
unblinded discriminator confirms and sharpens the campaign's standing conclusion — **XAU price-only structure carries a real, cross-mechanism
LOSE-LESS time-of-day beta, not a profitable regime.** The finer clock is the new detail; the economic verdict is unchanged.

## Caveats
Feature VALUES are frozen bin indices (no thresholds were scanned). All results are on MATERIALLY_EXPOSED history — diagnostic only. The
per-cell placebo load (~13%) means individual object-level rescues require independent retest before any belief; the recurrence gate (only
f011/f017/f016) is the robust layer. Nothing here is promotable.
