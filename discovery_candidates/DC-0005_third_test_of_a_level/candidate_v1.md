# Discovery Candidate DC-0005: The Third Test Of A Level Behaves Differently From The First Two

## Metadata

- **candidate_id**: DC-0005
- **title**: The Third Test Of A Level Behaves Differently From The First Two
- **origin_mode**: discretionary-observation, TradingView Replay manual forward stepping
- **date_first_observed**: 2026-07-22 (replay 2024-03-27 and 2024-07-24→08-01)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15 (event), H1/H4 (context)
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: field journal #013, #016–#019; ledger case L1; manual stepping logs 2024-03-27 and 2024-07-24→08-01
- **related_ids**: DC-0003 (scale), E017 (equal highs/lows), OBS-0004
- **content_hash**: sha256:7c8750551b31c2e8da4833a40f9a31a12c58a5000c3fed782838f4a23dc01714
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `PENDING`

## 1. Observation

The same price level tested repeatedly does not behave the same way on each visit. In two
independently observed sequences the **third** interaction differed materially from the first two:

- **2024-03-27, ~2180 (M15):** two marginal breaks failed and reverted quietly (logged m1, m2). The
  **third** rejection produced genuine displacement — −7 points on the largest volume of the sequence
  (1810), timed to the London open — although the move then died inside the range.
- **2024-07-24 → 08-01, ~2412 (M15):** the level rejected price twice (24 Jul, 26 Jul). On the
  **third** test (31 Jul → 1 Aug) it was taken cleanly, price running to 2429.1.

In both cases the first two interactions resolved into nothing; the third produced the move.

## 2. Why It Attracted Attention

I was not looking for it. Both sequences were encountered during chronological forward stepping, four
months apart in replay time, in different regimes (lateral after an expansion; recovery inside a
downtrend). The repetition of "twice nothing, third time something" is what made me stop.

## 3. Why It May Repeat

Descriptively: each test of a level consumes resting interest at that price. After two defences the
population of participants willing to defend it may be depleted, so the third arrival meets less
resistance. No causal claim is made — this is a description of what was seen.

## 4. Why It Deserves Further Investigation

It is countable and precisely specifiable (count interactions with a level; compare outcome
distribution by interaction index), it appeared in two different regimes, and it offers a possible
reason why single-touch level studies return nulls: they pool first, second and third touches
together.

## 5. Confidence

**Low.** n=2 sequences, single instrument, observed by eye during forward stepping.

Opposing evidence recorded:
- In the 2180 case the third-test displacement **died inside the range** — the difference was in
  character, not in follow-through.
- "Third time breaks" is folk knowledge in trading; a well-known belief is a warning sign, not support.
- No count exists of levels tested three times that produced nothing on the third — almost certainly
  the majority.

## 6. Library Concept Scan

Concepts identifiable in this event, **listed not judged**.

| Library concept | How it appears |
|---|---|
| **E017** equal highs / lows | Repeated interaction with one price is the same family as equal highs/lows. |
| **Structure primitive** (CANDIDATE-DEFERRED; residue = level memory, ORQ-009) | This candidate is a direct statement about level memory — the primitive's open residue. |
| **OBS-0004** sweep depth uninformative | Prior geometric refinement of level interaction failed; this proposes a *count* refinement instead. |
| **OBS-0010** no round-number clustering | Prior level-attraction claim in this market was refuted. |
| **DC-0003** scale inversion | The 2180 third-test produced displacement that died — a micro-scale outcome consistent with DC-0003. |
| **K01** raw vs conditioned sweeps | Interaction-count is a *conditioning* variable of the kind K01 points to. |
| **Volatility hour-of-day profile** | The 2180 third test fired at the London open — session timing is entangled with the count. |
| **E-program** "~52% reversal, both M15 and H1" | Prior single-touch level tests returned coin-flip outcomes. |

## Handoff Statement

Submitted to Red Team as a descriptive observation only. Not validated, not an edge, not a strategy,
no profitability claim. Content hash: sha256:7c8750551b31c2e8da4833a40f9a31a12c58a5000c3fed782838f4a23dc01714.
