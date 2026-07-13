# STRATEGY DEDUPLICATION REPORT — workstream B (branch strategy-development, baseline 1bc0ffb)

Read-only over the official reproducible baseline. No change to S1–S20, the engine, the screen, or the
holdout. No statistical verdicts. Source: results/FAMILY_RESULTS.parquet (1,972 hyps, 130 Research-Worthy).

## 1. Method
The 130 Research-Worthy (RW) variants were grouped by **economic mechanism**, not by parameter tuple. Per CEO,
two variants are NOT distinct strategies if they differ only in RR, lookback, confirmation window, stop
variant, entry type, or neighbouring params. For each family a **mechanism key** was defined from the
grammar dims that change the ECONOMIC bet (direction + reference/level/mode), collapsing all tuning dims:

| family | mechanism key (economic) | collapsed as tuning |
|---|---|---|
| S1 | side, liq_ref (which liquidity pool) | liq_lb, confirm, imb, stop, exit, window |
| S2 | side, ref | lb, fail_within, stop, exit |
| S5 | session, side | **mode (DEAD dim)**, stop, exit |
| S6 | session, mode, side | stop, exit |
| S8 | ref, side | k, stop, exit |
| S9 | c4h dir, conf1h (align/any) | lb, stop, exit |
| S14 | side | roc_k, stop, exit |
| S17 | level, mode | stop, exit |
| S20 | ctx, trig | lb, stop, exit |

## 2. Result
- **130 Research-Worthy → 17 distinct economic candidates. 113 (87%) are duplicates** (parametric/economic
  variations of the same mechanism).
- Duplication is dominated by **S1: 90 RW variants → 5 distinct mechanisms** (S1's grammar has 1,152 tuning
  combinations; e.g. hyps `94cd3ebb46af` and `d4c06178855b` are byte-identical in every metric).
- Distinct candidates per family: S1=5, S17=3, S6=2, S9=2, S2=1, S5=1, S8=1, S14=1, S20=1.

## 3. Two defects found during dedup (Claude economic-verification catches)
1. **DEAD grammar dimension in S5.** `S5_DIMS` contains `mode ∈ {breakout, retest}`, but `s5_setups()`
   never reads `h['mode']` — both modes generate IDENTICAL trades. This over-split S5 into two phantom twins
   with byte-identical metrics (n=287, exp=0.16582, dd=7.33). Fixed by dropping `mode` from S5's mechanism
   key → S5 collapses to ONE candidate (ny/up). *This is a real grammar bug in mstrat.py, logged as tech
   debt; NOT patched here (mstrat.py is frozen this workstream).*
2. **Knife-edge mechanisms mislabelled as robust.** The screen marked some variants Research-Worthy whose
   mechanism only works for a single narrow tuning combo. Added a neighbour-robustness gate: a mechanism is
   `knife_edge` if <20% of its tuning variants are historically profitable. This reclassified 3 candidates
   from research-candidate to fragile: `S1/high/swing` (only **3%** of its 192 tuning neighbours profitable),
   `S17/pw_low/reject` and `S17/pw_high/reject` (1 of 6 neighbours = 17%).

## 4. Duplicate classes
- **Exact / parametric duplicates**: 113 collapsed members (same mechanism, differing only in tuning).
- **Economic duplicates across candidates** (same bet, different family/params — from correlation analysis,
  see EXPLORATORY_CORRELATION_REPORT): the long-momentum cluster **S9(any), S9(align), S20(breakout),
  S17(pw_high breakout)** correlate r=0.6–0.71 → one economic bet; the two S9 variants (r=0.70) are near-
  redundant. After this second collapse, ~17 distinct candidates → **~6–8 truly independent economic bets**.

## 5. Registry artifact
`STRATEGY_CANDIDATE_REGISTRY.parquet` — one row per distinct candidate with candidate_id,
representative_hypothesis_id, member_hypothesis_ids, mechanism, canonical_strategy_spec, raw + robustness
metrics (incl. mech_profitable_frac = neighbour robustness), knife_edge, classification, shortlisted,
robustness_score.

## 6. Headline answers
1. **113 of 130 RW are duplicates (87%).**
2. **17 distinct economic candidates** (→ ~6–8 after correlation-based economic de-redundancy).
3. Classification: **11 research-candidate, 6 profitable-but-fragile** (see STRATEGY_DEVELOPMENT_REPORT).
