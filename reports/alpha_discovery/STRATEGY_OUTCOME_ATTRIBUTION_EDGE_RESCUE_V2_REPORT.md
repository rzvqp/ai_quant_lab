# STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V2_REPORT — EXECUTED (blind → frozen → unblinded)

Alpha independent execution against the Statistician-frozen V2 package, resumed after the blinded feature-value matrix was supplied.
Identity gate PASSED; blind stage-1 scoring, placebo, recurrence, and per-family autopsy EXECUTED; blind results frozen + hashed **before**
any semantic unblinding. **Hypothesis-generation mandate only — nothing promoted, no strategy modified, no Strategy #2 declared, no Red Team
routing. History is MATERIALLY_EXPOSED, so every number below is diagnostic, not validation.**

## Protocol executed (in frozen order)
1. **§1 Identity — 7/7 hashes exact.** MANIFEST `433f1cec`, EXECUTION_UNIVERSE `78ea539f`, PROTOCOL_CORE `4488f0e8`, BLINDED_FEATURE_VALUES
   `2ea066c6`, HANDOFF_MANIFEST `edf196e5`, TRADE_LEVEL_SPEC `03e63663`, STAGE1_ELIGIBLE `8a629d7d`. `IDENTITY_VERIFIED = YES`.
2. **§2 Universe bound** — 115 analysis objects / 102 source families / 25 mechanisms; **f029 EXCLUDED** (AT_FILL_POST_DECISION) → **45**
   Stage-1-eligible features loaded from the machine-authoritative `ATTRIBUTION_V2_STAGE1_ELIGIBLE_FEATURES.csv`, not from the 46-col matrix.
3. **§4 Trade regeneration (causal, join at DECISION bar)** — 56 S-library reps via `mstrat.simulate` (decision = signal bar `si`) + 14 T1
   from the V1 causal ledger = **70 ANALYSED**; **45 T2 = FAILED_REGENERATION** (bespoke per-object generators; **kept in every denominator**).
   Blinded panel verified index-aligned with `mstrat.load()` (BAR_OPEN_TIME == d.time elementwise). **505,794 trades joined, 0 unmatched.**
4. **§9 Blind stage-1** — per (object × eligible feature): each frozen bin with **N≥30 AND ≥20 independent days**, day-clustered z of
   (bin expectancy − object remainder). Omnibus p = Bonferroni-within-feature. **BH-FDR q=0.05 at the DECLARED m=5,175.** Feature ids stayed
   blind (f001..f046) throughout. **2,887 (object,feature) tests scored → 368 FDR-significant; 79 FDR-sig POSITIVE-expectancy bins / 29 objects.**
5. **§17 Placebo hard gate — PASS.** Shuffling net_R within each object (3 seeds) yields **9–12** FDR-sig positive "rescues" vs **79** real →
   the aggregate signal is real, not a pipeline artifact. (Implied per-cell false-positive load ≈13%, so individual rescues still need retest.)
6. **Freeze** — `BLIND_ATTRIBUTION_RESULTS_V2.csv` written and hashed **before** unblinding. `BLIND_RESULTS_HASH =
   8988448ac1efb1e566ecb2d035910bce8160ff696a11df70f8aaaea531b21049`. Ranking never changed after this point.
7. **§22 Unblinding** — only then mapped f-ids via the Statistician key. Ranking preserved; unblinding is interpretation only.

## The decisive finding — profitable SUBPOPULATIONS exist, a profitable META-STATE does not
**§30 meta-state (pooled across all 70 strategies, 505k trades).** The strongest cross-strategy discriminator is fine time-of-day, but its
BEST state is still a loser:

| Feature (unblinded) | best bin | pooled exp | drop-best-5% | worst bin | objects +ve |
|---|---|---|---|---|---|
| halfhour_bucket_utc (f011) | 28 | **−0.140R** | −0.250 | −0.328 | 12/44 |
| hour_utc (f017) | 14 | −0.171R | −0.283 | −0.321 | 10/49 |
| bars_to_sess_end (f016) | 1 | −0.175R | −0.287 | −0.272 | 9/39 |
| session_id (f039) | 3 | −0.198R | −0.311 | −0.272 | 6/57 |
| atr_over_atrma (f005) | 4 | −0.193R | −0.306 | −0.295 | 6/61 |

→ **`PROFITABLE_META_STATE_FOUND = NO`** (no single observable state makes the *pooled* graveyard profitable — best is −0.14R).
→ **`LOSE_LESS_META_STATE_FOUND = YES`** — fine time-of-day is a real, cross-mechanism **lose-less tilt** (best 30-min bucket −0.14 vs worst
−0.33 = +0.19R spread, recurring across ≥5 families & ≥3 mechanisms). This is the **same lose-less beta** the whole campaign has found, now
established rigorously and blindly — and it refines it: the **30-minute clock** beats the coarse session as the discriminator.

**§24 per-family autopsy (concentration drop-best-5%>0 AND chronological ≥2/3 thirds positive AND FDR):**

| rescue class | objects |
|---|---|
| **PROFITABLE_RESCUE** (a subpopulation with positive ABSOLUTE expectancy) | **15** |
| LOSE_LESS_OR_FRAGILE | 14 |
| NONE | 41 |

→ **15 of 70 analysed strategies contain a causally-observable condition under which they are outright profitable** (subset exp **+0.10 to
+0.49R** while the strategy's remainder is negative), surviving concentration + chronological + FDR gates. Examples: S14 mean-reversion at
prev-session-high distance ≈ 0 → **+0.49R** (remainder −0.19); S31 session-time at a specific intra-session bar → +0.42R; S23
vol-compression at hour 12 → +0.36R; S21 liquidity-sweep at range-location 0 → +0.39R. Full list in `ATTRIBUTION_V2_RESCUE_REGISTER.csv`.

**Reconciliation (why both are true and not contradictory):** each strategy's profitable window is *strategy-specific* — the recurrent
discriminator *type* is time/location, but the favorable *bin* differs per family, so the subpopulations do not stack into one shared
profitable regime. The graveyard is not globally rescuable; individual strategies have exploitable slivers.

## §28 Post-entry (10 POST_ENTRY_ELIGIBLE families, MFE/MAE path) — management signal, NOT a pre-entry edge
`favorable_early` (MFE≥0.5R, MAE>−0.5R) → **+1.41R, 95.7% WR** vs `immediate_fail` (MAE≤−1.0R) → **−1.14R, 0% WR**. The first few bars are
enormously predictive — but this is **post-entry path**, usable only as a time-stop / early-abort management rule, not a causal entry filter.

## §33 CEO questions — answers
1. **Failed families with a profitable subpopulation?** 29 objects raw (FDR-sig +ve bin); **15** survive concentration+chrono. 2. **Survive
frozen gates?** 15 (but history materially exposed → diagnostic). 3. **Strongest credible rescue?** S14 mean-reversion at prev-session
extreme (+0.49R subset, convergent with rloc_50≈0 +0.44R) and S31 session-time (5 convergent time conditions). 4. **Condition that explains
winners?** proximity to a reference extreme (mean-reversion families) and specific intra-session timing. 5/6. **Across families/mechanisms?**
the *type* (fine time-of-day / session-position) recurs across ≥5 families & ≥3 mechanisms; the specific window does not. 7. **Profitable
cross-strategy regime?** NO. 8. **Lose-less only, at the meta level?** YES. 9. **Strongest blind feature?** f011. 10. **Unblinded?**
halfhour_bucket_utc. 11. **Were prompt-emphasized features the winners / was V1 prompt-seeded?** PARTLY seeded — V1 emphasized session/vol/
H1-H4/side; blind ranking puts the **finer 30-min clock and session-position first**, ranks coarse session/vol lower, and **side (f025/f045)
and trend-state (f024/f031) do NOT rank** in the recurrent top. 12. **New unseeded discovery?** YES — 30-min clock granularity beats coarse
session, and bars_to_sess_end / bar_in_sess (session-position) are strong recurrent discriminators we never emphasized. 13. **LONG/SHORT
asymmetry recur?** NO — side is not a strong cross-mechanism discriminator here (contra V1's emphasis). 14. **Families profitable only in a
fixed time/calendar state?** YES (e.g. S23 @ hour 12, S31 @ hour 22, S1 @ halfhour 45). 15. **Vol vs time?** TIME > VOL. 16. **Anything worth
a separate retest?** the ~4 convergent rescues (S14, S31, S46, S23) — as hypotheses for a FRESH independent/prospective test, never promotion.

## §38 FINAL SUMMARY
```
STRATEGY_OUTCOME_ATTRIBUTION_EDGE_RESCUE_V2_COMPLETE = YES
IDENTITY_VERIFIED = YES · BLINDING_DISCIPLINE_PRESERVED = YES (scored blind, froze+hashed, then unblinded)
SOURCE_FAMILIES_TOTAL = 102 · ANALYSIS_OBJECTS_TOTAL = 115 · DISTINCT_MECHANISMS_TOTAL = 25
ANALYSIS_OBJECTS_SUCCESSFUL = 70 (scored) · FAILED_REGENERATION = 45 (kept in all denominators)
TOTAL_VALID_TRADES_ANALYSED = 505794 (joined at the DECISION bar, 0 unmatched)
BLIND_FEATURES_TESTED = 45 / 46 (f029 EXCLUDED, AT_FILL_POST_DECISION) · STAGE1_TESTS_SCORED = 2887 · MULTIPLICITY_DENOMINATOR = 5175
STAGE1_FDR_SIGNIFICANT = 368 · FDR_SIG_POSITIVE_BINS = 79 across 29 objects
PLACEBO_GATE = PASS (null 9-12 vs real 79) · BLIND_RESULTS_HASH = 8988448ac1efb1e566ecb2d035910bce8160ff696a11df70f8aaaea531b21049
FAMILIES_WITH_PROFITABLE_SUBPOPULATION_RAW = 29 · FAMILIES_WITH_CREDIBLE_RESCUE = 15
RESCUE_PROFITABLE = 15 · RESCUE_LOSE_LESS_OR_FRAGILE = 14 · RESCUE_NONE = 41
PROFITABLE_META_STATE_FOUND = NO · LOSE_LESS_META_STATE_FOUND = YES (fine time-of-day; best 30-min bucket -0.14R vs worst -0.33R)
TOP_RESCUE_HYPOTHESIS = S14 mean-reversion @ prev-session-extreme (subset +0.49R vs remainder -0.19R, N=65; convergent rloc_50~0 +0.44R)
STRONGEST_BLIND_FEATURE_ID = f011 · STRONGEST_UNBLINDED_FEATURE = halfhour_bucket_utc (30-min UTC clock)
NEW_UNSEEDED_DISCOVERY_FOUND = YES (fine clock + session-position beat coarse session/vol/side; side & trend de-emphasized)
POST_ENTRY = path-dependent management signal only (favorable_early +1.41R/95.7%WR vs immediate_fail -1.14R/0%WR) — NOT a pre-entry edge
HISTORICAL_REUSE_STATUS = MATERIALLY_EXPOSED (diagnostic only; no holdout manufactured; nothing validated)
READY_FOR_INDEPENDENT_RETEST = YES (15 rescue hypotheses; top ~4 convergent) — HYPOTHESIS GENERATION ONLY, no promotion
```

## Protection (§35/§36)
No strategy modified; nothing promoted; no Red Team routing; S5 / Q4 / AI-Trader / P007 / MGMT-004 / MT5 / StrategyCatalog untouched; no
holdout manufactured; the blind was held until `BLIND_RESULTS_HASH` was frozen. All rescue conditions are HYPOTHESES on materially-exposed
history and validate nothing.

NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```
V2_STATUS = ATTRIBUTION_V2_COMPLETE — 15 profitable subpopulations found (diagnostic), NO profitable meta-state, lose-less time-of-day confirmed
```
