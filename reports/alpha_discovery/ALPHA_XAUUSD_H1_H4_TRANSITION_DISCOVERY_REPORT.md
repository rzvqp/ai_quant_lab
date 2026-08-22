# ALPHA_XAUUSD_H1_H4_TRANSITION_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-H1-H4-TRANSITION-DISCOVERY-001` · **Date:** 2026-08-21 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_TRANSITION_ALPHA_DISCOVERY_COMPLETE` · **`TRANSITION_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW`** — 2 robust CALIB-passing candidates; primary `TR-H4-rng2trend_disponly-L` is a genuine, complementary **RANGE→TREND transition specialist**.
**Firewall (re-verified):** gated M5 loader (file sha `cbb6eebe…`) → causal H1/H4; no `read_csv` on `data/market/`; `N4_M5_TRIGGER_USAGE_COUNT = 0`; `ALPHA_ACCESS_2025_PLUS = 0`. 28 IDs (≤40). No promotion; broker disabled; existing candidates frozen.

---

## 0. Headline — answers to §21
1. **Is RANGE→TREND tradeable?** → **YES** — the strongest transition edge found (`TR-H4-rng2trend_disponly-L`, H4).
2. **Displacement alone, or acceptance required?** → **Displacement alone is enough — and better.** On H4, the displacement-breakout (`disponly` +0.443) **survives and CALIB-passes**, while the acceptance version (2 closes outside, `accept`) **FAILS** (−0.106). Waiting for acceptance misses the move.
3. **Breakout→retest vs immediate?** → **Roughly equivalent** — they are the *same* trades (Jaccard 0.978); retest marginally higher DEV, immediate higher CALIB. Retest is **not** clearly superior.
4. **Are false breakouts useful?** → **Inconclusive — too sparse** (H4 n=8, very profitable +1.0 but insufficient; H1 negative). Promising, not established.
5. **Trend exhaustion/reversal tradeable?** → **NO** — tail-fragile on both TFs; the SHORT (reversal-down) fails.
6. **H1 or H4 for transitions?** → **H4** — 3 CALIB-passers vs H1's 0.
7. **Does M5/M15 improve transition entry?** → **NO** — coarse H4 entry ≥ M5-timed (ΔavgR −0.019, same SL/TP). Consistent with the program-wide finding (M5 helps continuation, not large-move/transition).
8. **Robust SHORT transitions?** → **NO** — every SHORT transition fails (long-biased 2021–2024 population). The valuable SHORT specialist was **not** found.
9. **Which target 80–300+ pips?** → all H4 transition survivors (median TP **352–397 pips**).
10. **Most complementary?** → **`TR-H4-rng2trend_disponly-L`** (Jaccard **0.154** vs `MT-H4-efficiency-L`) — a genuine transition specialist, not a trend-continuation clone.

## 1. Search design
Transition-specific mechanisms on H1/H4 (primary edge), parent-TF structural SL (5-bar swing, **not** M5), economic RR target (H1 2.5 / H4 1.5, median TP ≥80p filter), coarse edge-TF entry, `mstrat` engine, cost tick 0.01 / STRESS 0.24. 7 mechanisms × 2 dir × 2 TF = 28 IDs. The comparison pairs are baked in: `rng2trend_accept` vs `rng2trend_disponly` (§2), `breakout_retest` vs `breakout_immediate` (§21.3), plus `false_break`, `trend_exhaustion`, `comp_expansion`. DEV screen; CALIB once after freeze.

## 2. RANGE→TREND (§4) — the productive branch
Signal: price was ranging (|efficiency|<0.4) then breaks the prior 12-bar structure. Two forms tested:
| form | H4 DEV STRESS | best-10%-rem | CALIB | verdict |
|---|---|---|---|---|
| **displacement-only** (big breakout bar, enter now) | **+0.443** | **+0.328** | **+0.658** (n=9, WR 67%) | **CALIB_PASS ★** |
| acceptance (2 closes outside + follow-through) | −0.106 | −0.229 | — | FAIL |
**Displacement alone is the transition signal; acceptance (waiting) destroys it** — because the H4 move is largely done by the time two closes confirm. On H1 both forms were tail-fragile (weak). **RANGE→TREND is tradeable, on H4, via displacement.**

## 3. TREND→REVERSAL / exhaustion (§7) — NOT robust
`trend_exhaustion` (failed new high/low + swing break + acceptance): H1-L +0.007 (tail-fragile), H4-L +0.069 (tail-fragile, best-5%-rem −0.000), both SHORT variants FAIL. **Trend exhaustion/reversal cannot be traded robustly** on this population — the reversal-down (SHORT) especially fails. Divergence-style reversal is not an edge here.

## 4. compression→expansion (§1H/J)
H1-comp_expansion-L survived DEV (+0.109) but **CALIB_FAIL (−0.126)**; H4 was SPARSE (n=9). Not robust.

## 5. breakout→acceptance vs →retest vs →immediate (§21.3)
| mechanism (H4 LONG) | DEV STRESS | best-10%-rem | CALIB | overlap w/ immediate |
|---|---|---|---|---|
| breakout_immediate | +0.283 | +0.148 | **+0.379** (n=18) | — |
| breakout_retest | +0.301 | +0.175 | +0.181 (n=21) | **Jaccard 0.978** |
Retest and immediate are **the same mechanism** (98% identical trades). Both CALIB-pass; immediate has the stronger CALIB. **Retest adds no material value.** Treated as one candidate: **`TR-H4-breakout-L`** (secondary).

## 6. false-break transition (§6) — inconclusive
`false_break` (break one side, fail, displace through the other): **too sparse** (H4 n=8, H1 n=11). The 8 H4 instances were extremely profitable (+1.0, WR 62%), but n=8 cannot support a claim. **Flagged PROMISING_BUT_INSUFFICIENT** — worth a dedicated future study, not a candidate now.

## 7–8. LONG / SHORT results (§10)
**LONG:** all robust survivors are LONG. **SHORT:** every SHORT transition FAILS or is SPARSE — `rng2trend-S`, `breakout-S`, `exhaustion-S`, `false_break-S` all negative or too few. **No robust SHORT transition specialist found** — the long-biased 2021–2024 population offers no bearish-transition edge (honest negative; the CEO's desired SHORT specialist is not available here).

## 9. H1 vs H4 (§21.6)
| TF | SURVIVE | CALIB_PASS | read-out |
|---|---|---|---|
| H1 | 1 (comp_expansion-L) | **0** (fails CALIB) | many positive-BASE but tail-fragile; none generalize |
| **H4** | 3 | **3** | rng2trend_disponly, breakout_immediate, breakout_retest all CALIB_PASS |
**H4 is decisively better for transition Alpha.** (Consistent with the multi-TF finding that H4 is the most productive edge TF.)

## 10. M5/M15 entry value (§11, §21.7)
On the primary candidate, coarse H4 vs M5-momentum entry (same H4 SL/TP): coarse avgR +0.260 vs M5 +0.241 → **ΔavgR −0.019, M5 does NOT add value.** M5/M15 entry not adopted; the H4 transition edge is best executed coarsely on H4.

## 11. PRIMARY CANDIDATE — `TR-H4-rng2trend_disponly-L` (full metrics §18)
RANGE→TREND displacement LONG on H4: after a ranging phase, a large displacement bar (body > 1.2·ATR) breaks the prior 12-bar high → LONG. Parent (H4) structural SL; RR 1.5 economic target.
| metric | DEV | CALIB |
|---|---|---|
| N | 33 | 9 |
| win rate | 0.455 | **0.667** |
| avg realized R (STRESS) | **+0.443** | **+0.658** |
| profit factor | 2.50 | — |
| best-1% / 5% / **10%-removed** | — / +0.401 / **+0.328** | — / +0.554 / — |
| median SL / TP | 264 / **397 pips** | — |
| %TP ≥80 / ≥150 | 1.00 / 1.00 | — |
| temporal (2021/22/23) | −0.143 / +0.291 / **+0.787** | — |
| CALIB class | — | **CALIB_PASS** |
**Tail-robust (best-10%-removed +0.328 — no IR-DIR-L-mid tail-concentration mistake), large-move (medTP 397p), CALIB-generalizing.** Caveat: modest DEV n=33, small CALIB n=9, and 2021 negative (up-trend-favoring, like the other H4 longs).

## 12. Economic geometry (§18) — both candidates
| candidate | median SL | median TP | %TP≥80 / ≥150 / ≥200 |
|---|---|---|---|
| TR-H4-rng2trend_disponly-L | 264 pips | **397 pips** | 1.00 / 1.00 / ~0.97 |
| TR-H4-breakout-L (immediate) | 234 pips | **352 pips** | 1.00 / 0.95 / — |
Both are large-move (352–397 pip median targets) — squarely the ≥80–300 pip regime (§8).

## 13. Tail robustness (§17)
`rng2trend_disponly-L`: best-5%-rem +0.401, **best-10%-removed +0.328**. `breakout_immediate-L`: best-5%-rem +0.217, best-10%-rem +0.148. Both survive removing the top 10% strongly — **not lottery edges.** (Contrast: `trend_exhaustion`, `comp_expansion`, all shorts had negative best-5%-removed → correctly killed.)

## 14. Temporal robustness (§19)
Both candidates: negative 2021, strongly positive 2022–2023 — **up-trend-favoring transition longs** (RANGE→TREND-UP breakouts profit when gold subsequently trends up). Honest caveat: regime-dependent, not all-weather; no periods deleted.

## 15. CALIBRATION (§20) — run once, frozen
`rng2trend_disponly-L` +0.658 (WR 67%), `breakout_immediate-L` +0.379 (WR 56%), `breakout_retest-L` +0.181 — all **CALIB_PASS**. `comp_expansion-L` CALIB_FAIL. Small CALIB n (9–21) is the honest H4 sampling limit — flagged for validation.

## 16. Overlap / complementarity (§13) — the specialist result
| pair (H4 LONG, DEV trade-days) | Jaccard |
|---|---|
| **rng2trend_disponly vs `MT-H4-efficiency-L`** | **0.154** |
| rng2trend_disponly vs `MT-H4-dispaccept-L` | 0.381 |
| rng2trend_disponly vs breakout_immediate | 0.353 |
| breakout_retest vs breakout_immediate | 0.978 |
**`TR-H4-rng2trend_disponly-L` is a genuine transition specialist** — only 15% day-overlap with the existing H4 trend-continuation long. It fires at the **trend's start** (range breakout) where continuation strategies are not yet active → **complementary Alpha**, exactly the §13 objective. The `breakout` mechanism is more generic (higher overlap) and less of a specialist.

## 17. Graveyard (§16, §33)
| idea | TF | failure | code |
|---|---|---|---|
| rng2trend **acceptance** (both TF) | H1/H4 | acceptance-wait misses the move | EXECUTION/NO_EDGE |
| trend_exhaustion (L tail-fragile, S fail) | H1/H4 | tail-fragile; reversal-short no edge | TAIL/NO_EDGE |
| comp_expansion | H1 | DEV+ but CALIB_FAIL | CALIB |
| all SHORT transitions | H1/H4 | negative (long-biased population) | NO_EDGE |
| false_break | H1/H4 | too few instances (n=8–11) | SPARSE |
| breakout_retest | H4 | duplicate of immediate (Jaccard 0.98) | REDUNDANCY |
Recorded in `transition_records.json`. New `TR-` IDs; existing candidates untouched.

## 18. Candidate portfolio + recommendation (§22)
1. **Forward `TR-H4-rng2trend_disponly-L` (PRIMARY) to Statistician/Red Team** as a robust, CALIB-passing, tail-robust, large-move **RANGE→TREND transition specialist** that is **genuinely complementary** (15% overlap) to the existing H4 trend-continuation Alpha — it captures the *start* of trends, filling a gap in the portfolio. Also forward **`TR-H4-breakout-L`** (secondary, generic H4 breakout long, CALIB_PASS) with the note that it overlaps more with existing longs. Flags: modest samples (DEV n=33 / CALIB n=9 primary), regime-dependent (up-trend-favoring, 2021 negative), `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (DEV WR 45% / CALIB WR 67% @ RR 1.5 — CALIB approaches Profile A).
2. **Transition findings (headline §0):** RANGE→TREND is tradeable via **displacement** (not acceptance); breakout retest ≈ immediate; trend-exhaustion/reversal and all SHORT transitions are **not** robust; false-breaks are promising-but-too-sparse; **H4 ≫ H1**; **M5 adds no entry value.**
3. **Portfolio position:** `TR-H4-rng2trend_disponly-L` adds a **TREND-INITIATION specialist** to the portfolio (`MT-H4-efficiency-L`/`dispaccept-L` = trend-continuation; `HR-TU-pb-L` = H1 trend; `IR-DIR-L-mid` = range; `H4-bo-raw-S` = short). Still **no robust SHORT specialist** exists in this population — an open gap.
4. **No promotion; broker disabled; highest status = research candidate.** All existing candidates unaltered.

**Terminal status:** `XAUUSD_TRANSITION_ALPHA_DISCOVERY_COMPLETE` · `TRANSITION_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` (primary `TR-H4-rng2trend_disponly-L`, secondary `TR-H4-breakout-L`). **STOP.**
