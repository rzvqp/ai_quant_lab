# ALPHA_XAUUSD_LONDON_PLH_FIXED80_CLEAN_PATH_REPORT

**Mandate:** `ALPHA-XAUUSD-LONDON-PLH-FIXED80-CLEAN-PATH-001` · **Date:** 2026-08-22.
**Statistician audit accepted:** `STAT-LONDON-PLH-ASIA-SPATIAL-FEATURE-AUDIT-001` (`6892bc6`, `PLH_ASIA_SPATIAL_FEATURE_NOT_SUPPORTED`) — the Asia-mid CLEAN label was target-geometry contaminated (26/133 events at/beyond objective at E0, 53.1% of class-A; AUC→0.522 under room control).
**Terminal verdict:** `LONDON_PLH_FIXED80_LABEL_RECONSTRUCTION_COMPLETE` · **`LONDON_PLH_FIXED80_PARENT_NOT_SUPPORTED`**.
**Scope:** LABEL RECONSTRUCTION + BASE-RATE ONLY. Parent UNCHANGED. No feature mining, no thresholds, no classifier, no execution. Price-only, native-M5, DEV-only. No promotion; broker disabled.

---

## 0. Headline
- **Under a position-independent fixed-80-project-pip clean-path target, the London/Pre-London-High parent's CLEAN base rate is only 0.060 (8 of 133).** It is dominated by **B new-high-first→80 (0.353)** and **C continuation (0.586)** — the right-direction-bad-path regime. **85% of the eventual ≥80p bearish moves happen only *after* a new high.**
- **The prior spatial feature `plh_minus_asiahigh` collapses exactly as the Statistician predicted:** AUC 0.12/0.23 (contaminated Asia-mid) → **0.579** (fixed80), and even that is on only 8 positive events (noise). → **graveyard.**
- **Failed-acceptance's prior 0.368→0.404 boost does not survive:** under fixed80 it is 0.060→0.085 (a tiny lift, mostly the trivial "sustained-above → 0.000").
- **The parent is NOT SUPPORTED for clean-path Alpha discovery** under the repaired label — but the parent EVENT itself is not rejected (per the CEO); it simply does not generate clean 80p shorts.

## 1. Parent reproduction (§2) — unchanged
Recovered mechanically from `frank_london.py` (`50b099d`): first native-M5 sweep of the causal Pre-London-High (max M5 high London-local 07:00–08:00) during London-local 08:00–10:00, one per day, DST-aware. **N = 133, unique days = 133** — matches lineage. No parent field modified.

## 2. Frozen label definition (§3, §4, §5, §6) — position-independent
Declared **before** outcome computation:
- **E0 reference = completed E0 sweep-bar close** (`close[E0]`). **Objective = ref − 80 project pips** (= ref − $8.00; 10 pips = $1).
- **Frozen parent sweep high = `high[E0]`** (the prior lineage's sweep extreme).
- **Horizon = 96 M5 bars (8h) OR same-UTC-day, whichever first** — frozen, chosen for the 80p economic scale (London+NY intraday), consistent with the PDH-80p study; not optimized. (The prior 48-bar horizon was tuned to the ~22p Asia-mid geometry and is inappropriate for an 80p target.)
- **4 classes (mutually exclusive, future labels only):** A CLEAN_80 (obj before any new high > sweep high) · B NEW_HIGH_FIRST_THEN_80 · C CONTINUATION · D STALLED.
- **Same-bar ambiguity (§5):** if the first resolving M5 bar contains BOTH a new high and the 80p objective, intrabar order is unknowable → classified **AMBIGUOUS, reported separately, never optimistically CLEAN** (no tick order inferred from OHLC). **AMB count = 0** here (objective is 80p below E0, sweep high above — no single M5 bar spans both).

## 3. Base-rate results (§8) — the primary answer
| | N | **P(A CLEAN_80)** | P(B new-high-first→80) | P(C continuation) | P(D stalled) | P(AMB) | eventual MFE≥80p |
|---|---|---|---|---|---|---|---|
| Full parent | 133 | **0.060** | 0.353 | 0.586 | 0.000 | 0.000 | **0.414** |
**Target IS available (41% eventually reach 80p) but the PATH is bad:** of the 0.413 that reach 80p, **0.353/0.413 = 85% do so only after a new high (class B).** Clean 80p = 8 events.

## 4. Secondary magnitude diagnostics (§7) — 80p PRIMARY, others diagnostic
| distance | P(clean before new high) | eventual MFE≥dist |
|---|---|---|
| 30p | 0.135 | 0.820 |
| 50p | 0.098 | 0.654 |
| **80p (PRIMARY)** | **0.060** | **0.414** |
| 100p | 0.060 | 0.316 |
| 150p | 0.030 | 0.143 |
Even at **30p**, clean-before-new-high is only **0.135** — the bad-path dominance is not a large-target artifact; it holds at every distance.

## 5. Year-by-year (§9) — stable but uniformly low
| year | N | A | B | C | MFE≥80p |
|---|---|---|---|---|---|
| 2021 | 27 | 0.074 | 0.333 | 0.593 | 0.407 |
| 2022 | 47 | 0.064 | 0.340 | 0.596 | 0.404 |
| 2023 | 59 | 0.051 | 0.373 | 0.576 | 0.424 |
Directionally stable across all three years — and uniformly weak (~5–7% clean). No year rescues it.

## 6. DISC / CONF (§10)
DISC (N=79): P(A) 0.063, P(B) 0.354, P(C) 0.582, MFE≥80p 0.418. CONF (N=54): P(A) 0.056, P(B) 0.352, P(C) 0.593, MFE≥80p 0.407. Consistent and low across the split.

## 7. Failed acceptance (§11) — prior boost does NOT survive
Prior definition (close back below PLH within E0–E2), unchanged, under fixed80:
| group | N | P(A) | P(B) | P(C) |
|---|---|---|---|---|
| ALL | 133 | 0.060 | 0.353 | 0.586 |
| failed_acc = TRUE | 94 | **0.085** | 0.309 | 0.606 |
| failed_acc = FALSE | 39 | **0.000** | 0.462 | 0.538 |
Under the position-independent label the lift is **0.060 → 0.085 (+0.025)** — a fraction of the contaminated Asia-mid "0.368 → 0.404", and largely the trivial "sustained-above-PLH → never a clean 80p short (0.000)." **The 0.368→0.404 observation does not survive label repair.**

## 8. Existing-feature sanity + PLH-AsiaHigh falsification (§12, §13)
AUC (A vs B+C) under fixed80 — **sanity check only; note only 8 class-A positives, so every AUC is on 8 positives and is NOISE, not a finding:**
| feature | overall | DISC | CONF |
|---|---|---|---|
| **plh_minus_asiahigh** | **0.579** | 0.584 | 0.569 |
| sweep_excursion | 0.445 | 0.514 | 0.346 |
| approach_vel | 0.210 | 0.203 | 0.203 |
| close_loc | 0.126 | 0.143 | 0.098 |
| upper_wick | 0.801 | 0.846 | 0.719 |
| failed_ext | 0.766 | 0.816 | 0.706 |
| early_downside | 0.780 | 0.722 | 0.863 |
- **§13 falsification — CONFIRMED:** `plh_minus_asiahigh` drops from a strong Asia-mid discriminator (AUC 0.12/0.23, |Δ|=0.38/0.27) to **0.579 (|Δ|=0.08)** under fixed80, and even that rests on 8 positives → **collapses to noise. → GRAVEYARD** (the Statistician's prediction is borne out exactly).
- The high AUCs (upper_wick 0.80, early_downside 0.78, failed_ext 0.77) are **computed on 8 positive events and are pure noise/overfit — explicitly NOT reported as findings** (reporting them as "surviving features" would repeat the very contamination this mandate corrects). No feature is promoted; no combinations; no new mining (§12).

## 9. Economic timeliness (§14)
For the 8 CLEAN_80 events: time-to-80p median 22 M5 bars (~110 min), P25 11 (~55 min), P75 41 (~205 min). Remaining distance at E0 = 80p by construction (position-independent).

## 10. Answers to §17
1. **Meaningful CLEAN_80 base rate?** **No — 0.060 (8/133).**
2. **How much ≥80p occurs only after a new high?** **85%** (P(B)/[P(A)+P(B)] = 0.353/0.413).
3. **Does failed acceptance still help?** Marginally (+0.025) and mostly trivially; the prior boost does not survive.
4. **Does PLH-AsiaHigh disappear as predicted?** **Yes** — AUC → 0.579 on 8 positives; collapsed; graveyard.
5. **Stable across 2021/2022/2023?** Yes, but uniformly low (0.074/0.064/0.051).
6. **Worth further signal discovery?** **No** — 6% clean base, 8 positive events, prior feature collapsed.

## 11. Graveyard + limitations
- **Graveyard:** the Asia-mid CLEAN label (target-geometry contaminated); `plh_minus_asiahigh` as a clean-path discriminator (collapses to 0.579/noise under fixed80); the failed-acceptance 0.368→0.404 boost (does not survive).
- **Limitations:** only **8 CLEAN_80 events** — no feature statement is possible at that N (all §12 AUCs are noise, reported as such). Native-M5 partial-2021 (from 2021-07). Result bounded to the 8h intraday horizon; the ≥80p move genuinely exists (41% MFE) but the path (new-high-first) is the binding problem, consistent with the whole SHORT program.

## 12. CEO recommendation
1. **`LONDON_PLH_FIXED80_PARENT_NOT_SUPPORTED`.** With the target-geometry contamination removed (Statistician-confirmed) and a position-independent fixed-80p clean-path label, the London/Pre-London-High parent produces a **clean 80p short only 6.0% of the time** — dominated by new-high-first (35%) and continuation (59%). The 80p move exists (41% eventual MFE) but 85% of it arrives only after a new high — the same right-direction-bad-path wall seen program-wide. The prior spatial feature is falsified (graveyard).
2. **The parent EVENT is not rejected** (per the CEO) — but it is **not a clean-path Alpha source** under the honest label. **No further signal discovery is warranted** on this parent for clean 80p shorts (8 positive events, no surviving feature).
3. **This mandate corrected a prior over-claim honestly:** the strong Asia-mid PLH-AsiaHigh finding was a labeling artifact; under position-independent labeling it collapses. Recorded, not defended.
4. **No promotion; no feature mining; no classifier; no execution; broker disabled; DEV-only; no CALIB.** Parent (`50b099d`) and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal verdict:** `LONDON_PLH_FIXED80_LABEL_RECONSTRUCTION_COMPLETE` · `LONDON_PLH_FIXED80_PARENT_NOT_SUPPORTED`. **STOP.**
