# Discovery Candidate DC-0007: A Cluster Of Near-Equal Lows Is Taken And Reclaimed Within A Single Candle

## Metadata

- **candidate_id**: DC-0007
- **title**: A Cluster Of Near-Equal Lows Is Taken And Reclaimed Within A Single Candle
- **origin_mode**: discretionary-observation, TradingView Replay manual forward stepping
- **date_first_observed**: 2026-07-22 (replay 2025-08-11)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-11 15:10–19:30 UTC
- **content_hash**: sha256:1823d33ec7394c21d0494d72d47ae0d9310ca0c306b028490152c353282fff10
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `PENDING`

## 1. Observation

During a stepped decline, price printed three near-equal lows — **3358.80, 3357.02, 3358.99** — over
consecutive M15 candles, then lifted to 3366.15. Two candles later a single candle traded down to
**3354.59**, roughly 2.4 points beneath the cluster, and closed at **3363.40** — back above the entire
cluster, within the same candle. Volume through the sequence stayed level (8,400 → 8,075), with no
expansion on the candle that took the lows.

## 2. Why It Attracted Attention

The lows were taken and given back inside one candle, without a volume signature, and the level that
had held three times stopped mattering immediately afterwards. I had not previously seen a level
cluster removed and reclaimed in a single bar.

## 3. Why It May Repeat

Descriptively: a cluster of near-equal lows is a visible, shared reference. Trading beneath it and
returning within the same candle describes a brief excursion past a shared reference that is not
sustained. No causal claim.

## 4. Why It Deserves Further Investigation

Both parts are precisely countable: a cluster of ≥3 lows within a small band, and whether the first
candle to exceed it closes back inside. The outcome after such candles is measurable.

## 5. Confidence

**Very low.** One instance, one instrument, one timeframe.

## 6. Library Concept Scan

Concepts present, listed only.

| Concept | Presence |
|---|---|
| **E017** equal highs/lows | The cluster is literally near-equal lows. |
| **Structure primitive** (level memory, ORQ-009) | Three defences then immediate irrelevance. |
| **K01** raw vs conditioned sweeps | Excursion past a reference without follow-through. |
| **DC-0003** scale inversion | Excursion size ≈2.4 pts against local ranges of 3–7 pts. |
| **DC-0005** repeated tests of one level | Three prior touches precede the event. |
| **DC-0006** extreme volume | Absent here — no volume expansion on the taking candle. |
| **Volatility hour-of-day profile** | Occurred in the NY window. |

## Handoff Statement

Descriptive observation only. Not validated, not an edge, not a strategy, no profitability claim.
Content hash: sha256:1823d33ec7394c21d0494d72d47ae0d9310ca0c306b028490152c353282fff10.
