# ALPHA_WAVE1_CHECKPOINT

**Mandate:** `ALPHA-DISCOVERY-AUTONOMOUS-CAMPAIGN-001` · **Date:** 2026-08-21 · **Partition:** DEVELOPMENT only (blocks 1–2, 2011-07→2018-04, 105,254 bars).
**Cost:** RATIFIED `AI_TRADER_SHADOW_COST_MODEL_v1` (config-fp `b7bb9a9aed17a1c8`) — BASE round-trip **0.05**, **STRESS round-trip 0.24** (CEO ruling). Floor `max(2·spread, 0.05, 0.10·ATR)` applied via scenario stop pre-widening; round-trip via slip_ticks (TICK=0.01). Entry next-open. No SEALED/VALIDATION access (OOS=0). Fast falsification — no post-hoc filters.

## Results (H14 / H05 / H11 / H02 / H08)

| Hyp | Family | Regime | N (gross) | Gross exp | BASE exp | STRESS exp | Win% | PF | best-share | temporal-conc | maxDD (R) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H11** | displacement+acceptance | TRANSITION | 3621 | **+0.124** | **+0.108** | **+0.047** | 33% | 1.17 | 0.11 | **0.29** | −63 | **FAST_FALSIFICATION_PASS** |
| H14 | session (NY momentum) | REGIME_INDEP | 1079 | +0.156 | +0.126 | +0.016 | 20% | 1.16 | 0.23 | **0.65** | −80 | FAST_FALSIFICATION_FAIL |
| H05 | breakdown-acceptance | TREND_DOWN | 960 | +0.027 | +0.020 | −0.007 | 42% | 1.05 | 0.68 | **2.24** | −34 | FAST_FALSIFICATION_FAIL |
| H02 | failed-bearish-counter | TREND_UP | 73 | +0.136 | +0.109 | +0.007 | 27% | 1.15 | 1.09 | 1.30 | −16 | INSUFFICIENT_EVIDENCE |
| H08 | boundary-rejection | RANGE (V4.4) | 823→365 | +0.258 | +0.176 | **−0.131** | **6%** | 1.17 | **2.12** | 1.86 | — | FAST_FALSIFICATION_FAIL |

**Directional consistency (regime concentration):** H11 balanced (UP 0.51 / DOWN 0.49 — works both directions); H05 all-DOWN by construction; H08 balanced.

## Per-hypothesis reading
- **H11 · displacement+acceptance → PASS (survivor).** The only Wave-1 survivor. Positive across GROSS/BASE/**STRESS**, large sample (n=3621), well-distributed in time (temporal-conc 0.29), no single-trade dependence (best-share 0.11), PF 1.17, works both directions. This validates the CEO's qualitative hypothesis that **displacement + acceptance discriminates structural change** — as a *measured* result on DEVELOPMENT, not proof. → `ALPHA_SURVIVOR_QUEUE` for robustness.
- **H14 · session → FAIL.** Real gross/BASE edge but **65% of total R from one year** (temporal-conc 0.65) — not time-stable. Cheap-killed, not rescued.
- **H05 · breakdown-acceptance → FAIL.** Weak gross (+0.027), STRESS-negative, temporal-conc 2.24, one trade = 68% of R. Confirms the canonical finding that naive short-side structural entries lack robust edge; *acceptance* alone did not rescue it.
- **H02 · failed-bearish-counter → INSUFFICIENT_EVIDENCE.** Gross/BASE positive but only n=73 on DEVELOPMENT (< min 150). Not falsified; needs more events — will re-test with a longer window / relaxed lookback *as a new version ID*, never by lowering the sample bar.
- **H08 · boundary-rejection → FAIL.** V4.4 CONFIRMED occupancy is real (**5.5%**, 5,832 bars), so the RANGE state is NOT event-sparse under V4.4 (unlike the retired 0.2.0 engine). But the naive boundary-fade has a **6% win rate** and one trade = 212% of R → a fat-tail lottery, not a repeatable mean-reversion edge: V4.4 boundaries mostly **break** rather than reject. STRESS-negative. *Implementation caveat:* my Wave-1 exit used a time-only exit (no mid-target); a mid-target variant is a legitimate **new version ID** for the campaign, not a post-hoc rescue of this one.

## Checkpoint accounting
- Hypotheses tested: 5. PASS: 1 (H11). FAIL: 3 (H14, H05, H08). INSUFFICIENT: 1 (H02). EVENT_SPARSE: 0.
- Survivor queue: **{H11}**. Graveyard: {H14, H05, H08}. Re-test-queue: {H02, H08-mid-target as new IDs}.
- Data consumed: DEVELOPMENT (repeatable). VALIDATION consumed: 0. FINAL_HOLDOUT_ACCESS_COUNT: **0**. Compute: ~V4.4 dev run 9 min + evals seconds.
- Integrity: no future leakage, no partition contamination, no MI mutation, no broker interaction. `V4_4_FROZEN_CONSERVATIVE_RESEARCH_BASELINE` (config_id `23d98c07…` verified). Broker disabled.

**Status: `ALPHA_WAVE1_COMPLETE`.** Autonomous campaign continues (no CEO wait required) under the frozen plan.
