# ALPHA_S5_C001_DEEP_RESEARCH_REPORT

**Mandate:** `ALPHA-PORTFOLIO-S5-C001-DEEP-RESEARCH-001` · **Date:** 2026-08-21 · **Status:** `ALPHA_PORTFOLIO_DEEP_RESEARCH_PASS` → `CANDIDATE_SPECIFICATIONS_READY_FOR_VALIDATION_DECISION`.
DEVELOPMENT (2011→2018, 160,888 bars) + bounded CALIBRATION (2020-01→2022-01, 47,325 bars). **VALIDATION_ACCESS = 0, FINAL_HOLDOUT_ACCESS = 0.** No unrestricted optimization; pre-registered neighborhoods only. Two independent lines, not merged.

## Headline
Deep research **reverses the Stage-1 ranking**: the historical **S5** is genuinely robust and **PASSES**; the flagship **Candidate-001 V1 FAILS** — its edge is an unstable outlier tail that does not reproduce on CALIBRATION. **S5 is the candidate to carry forward.**

## 1. Frozen baseline identities (unchanged, not merged)
- **`ALPHA_CANDIDATE_001_V1_BASELINE`**: displacement (\|close−open\| ≥ 0.8·ATR14) + 2-bar acceptance → trend-continuation, next-open entry at j+2, stop = displacement-origin open[j] (floored), exit = time-48. TRANSITION-triggered, trend-conditioned.
- **`S5_C_2d587447_HISTORICAL_BASELINE`**: `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` — NY opening-range up-breakout, next-open entry, stop = opposite OR boundary, exit = RR3. Long-only.

## 2. Candidate-001 deep analysis → **DEEP_RESEARCH_FAIL** (`UNSTABLE_OUTLIER_DEPENDENCE`)
| axis | result |
|---|---|
| baseline (DEV+CALIB) | GROSS +0.083 / BASE +0.067 / **STRESS +0.003** (barely) |
| **tail** | median trade **−1.009 R**; best 22.98; top-1% share **1.86** (186% of total R); **exp best-1%-removed −0.058, −2% −0.141, −5% −0.304, −10% −0.494** (monotonic collapse); winsor-99 +0.038 |
| **temporal (per block)** | **DEV +0.088 → CALIB −0.030** (does NOT reproduce out of the DEV block) |
| trend decomposition | trend-only +0.036, **non-trend −0.199** (needs trend gate) |
| param neighborhood (w0.6–1.2, a2–3) | +0.037 … +0.067 (param-stable) |
| delayed 1-bar entry | +0.082 (entry-timing robust) |
| exit family | time32 +0.039 · time48 +0.067 · time64 +0.108 · **time96 +0.141** (longer holds lift GROSS) |

**Verdict on the central question:** the best-1%-removed deterioration is **UNSTABLE_OUTLIER_DEPENDENCE**, not legitimate positive skew. Decisive evidence: (a) the edge is negative once even the top 1% is removed and worsens monotonically; (b) the median trade is a **full stop-out** and (c) — most importantly — the expectancy **fails to reproduce on CALIBRATION** (−0.030). A legitimate positive-skew trend-follower would stay positive on an independent block; this does not. → **V1 baseline FAILS.** The exit-side lead (time-96 doubling GROSS) is a genuine research direction but does **not** address the tail/calibration failure; it would require a **new version ID** and its own CALIBRATION reproduction before re-consideration. (Baseline preserved unchanged.)

## 3. S5 deep analysis → **DEEP_RESEARCH_PASS**
| axis | result |
|---|---|
| baseline (DEV+CALIB) | GROSS +0.073 / BASE +0.064 / **STRESS +0.032** (survives full stress cost) |
| **tail** | median −0.069 R; best 3.0 (RR3-bounded); top-1% share **0.44**; **exp best-1%-removed +0.036, −2% +0.006** (still positive), −5% −0.088; **winsor-99 = +0.064 (= full BASE → no single-outlier dependence)** → **LEGITIMATE positive skew** |
| **temporal (per block)** | **DEV +0.062 AND CALIB +0.080** (reproduces — actually stronger on CALIBRATION) |
| direction | **LONG +0.064 / SHORT −0.017** → clean long-only (short opening-range breakout has no edge) |
| **regime** | unconditional +0.064; TREND_UP +0.069; TREND_DOWN +0.073; **non-trend +0.165**; RANGE(V4.4,DEV) — works **in every regime** |
| param neighborhood (stop×exit) | or_opp/atr × rr2/rr3/time all **positive** (+0.023…+0.068); **rr3 is the best** → historical RR3 is structurally justified, not over-specific |
| delayed 1-bar entry | +0.048 (some degradation, still positive) |

**Item-4 answer (is 90% TREND_UP a condition or just where signals land?):** S5's expectancy is positive in **every** regime and *highest in non-trend* (+0.165) — the 90% TREND_UP occupancy is **merely where signals happen**, NOT an expectancy-enhancing condition. A hard TREND_UP gate is **NOT justified** and is not added.

## 4–5. Direction + regime decomposition
S5: long-only (short fails). Candidate-001: both directions in trend, but the whole mechanism is trend-conditioned and fails outside trend. S5 is regime-agnostic; Candidate-001 is regime-dependent.

## 6. Tail diagnostics (direct comparison)
| | median R | top-1% share | best-1%-removed | best-2%-removed | winsor-99 | verdict |
|---|---|---|---|---|---|---|
| **S5** | −0.069 | 0.44 | **+0.036** | +0.006 | +0.064 | LEGITIMATE_POSITIVE_SKEW |
| Candidate-001 | −1.009 | 1.86 | −0.058 | −0.141 | +0.038 | UNSTABLE_OUTLIER_DEPENDENCE |

## 7. Cost robustness
S5 BASE +0.064 → STRESS +0.032 (survives). Candidate-001 BASE +0.067 → STRESS +0.003 (marginal). S5 is more cost-robust.

## 8. Temporal robustness
S5 positive on **both** DEV and CALIBRATION. Candidate-001 positive on DEV, **negative on CALIBRATION** — the key failure.

## 9. Parameter robustness
S5: all pre-registered stop×exit variants positive, RR3 best (historical choice justified). Candidate-001: param-stable in-DEV but the instability is temporal/tail, not parametric.

## 10. Execution degradation
Both survive a 1-bar delay (S5 +0.048, C-001 +0.082); no favorable-fill assumptions; STRESS 0.24 applied.

## 11. Exit research
S5: RR3 confirmed optimal in its bounded family (time exits weaker). Candidate-001: longer holds (time-96 +0.141) materially improve GROSS — a genuine lead, but unaddressed for tail/calibration; assign a new version for any follow-up.

## 12. Mechanism overlap (deeper)
- Signal Jaccard **0.025**; simultaneous same-bar signals **481**; **daily P&L correlation 0.128**; both predominantly LONG. → **INDEPENDENT.** Shared long/trend bias, but decorrelated entries and returns.

## 13. Diagnostic combined portfolio (equal-risk union; pre-registered neutral conflict = take both independently, no post-hoc routing)
| | trades | BASE avg_R | PF | maxDD (R) |
|---|---|---|---|---|
| C001 only | 4,594 | +0.067 | — | — |
| S5 only | 1,378 | +0.064 | — | — |
| **C001 + S5** | 5,972 | +0.066 | 1.11 | −76.7 |
Diagnostic only — NOT a validated portfolio, no weight optimization. Because Candidate-001 fails deep research, the meaningful forward portfolio is **S5 alone**; the combination is reported for completeness (adding a failing mechanism does not improve the robust one).

## 14–16. Governance
CALIBRATION used: 2020-01→2022-01 (bounded). **VALIDATION_ACCESS_COUNT = 0. FINAL_HOLDOUT_ACCESS_COUNT = 0.** No SEALED access, no FB14/F441/MB3, V4.4 frozen (`23d98c07…`), no new families, no AI Trader / Strategy Router / MT5, broker disabled.

## 17. Final candidate specifications
- **S5 (`S5_C_2d587447_HISTORICAL_BASELINE`)** — **DEEP_RESEARCH_PASS**, frozen as-is (NY opening-range up-breakout, RR3, or_opp stop, long-only, no regime gate). Ready for a validation decision.
- **Candidate-001 (`ALPHA_CANDIDATE_001_V1_BASELINE`)** — **DEEP_RESEARCH_FAIL** (unstable outlier-dependence + CALIBRATION non-reproduction). Frozen unchanged; a time-96 exit variant is a future new-version lead only.

## 18. Validation recommendation
1. **Advance S5 to the validation pipeline decision** (ROBUSTNESS_PASS already substantiated on DEV+CALIB; next gate = one VALIDATION pass under independent Statistician/Red Team, per the promotion chain). It is the strongest, most robust, cost-surviving, regime-agnostic, decorrelated candidate the program has produced.
2. **Do not advance Candidate-001 V1.** If desired, authorize a *separate, new-version* exit-side study (time-96) that must reproduce on CALIBRATION before re-entry — but the V1 baseline is closed.
3. **Portfolio note:** the program currently has **one** deep-research-passing Alpha (S5). That is an acceptable and honest outcome (no forced count).

**Final state:** at least one survivor → `ALPHA_PORTFOLIO_DEEP_RESEARCH_PASS` · `CANDIDATE_SPECIFICATIONS_READY_FOR_VALIDATION_DECISION`. STOP — no auto-proceed to validation/catalog/AI Trader.
