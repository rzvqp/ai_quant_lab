# LEGACY RESEARCH LAB — STRATEGY STATUS REPORT

**Mandate:** LEGACY-RESEARCH-LAB-STRATEGY-STATUS-001 (inventory / reconstruction only) · **Author:** Research Lab · **Date:** 2026-07-28
**Reconstructed from:** `results/FAMILY_RESULTS.parquet` (canonical, D2-closed) + `results/FAMILY_RESULTS_pre_d2_baseline.parquet` (preserved) + `code/mstrat.py` grammar/ECON + the frozen status docs (`PROJECT_STATE_v1.0.md`, `SCOPED_FDR_RESULT_v1.0.md`, `THREE_REGIME_PERSISTENCE_RESULT_v1.0.md`, `DUPLICATE_AUDIT_v1.0.md`, `STRUCTURAL_R_UNVALIDATED_v1.0.md`, `PROJECT_AUDIT.md`, Statistician DC reviews, MK `trading_strategies.py`). **No code modified, no research re-run beyond descriptive inventory aggregation, nothing promoted, no AI Trader change, holdout SEALED.**

---

## 12. Repository state
- **Repo:** `github.com/rzvqp/ai_quant_lab.git` (remote `lab`) · local clone `C:\Users\MEDION GAMING\aql_stat_clone`.
- **Branch:** `stat-work` → tracks `statistician-foundation`. · **HEAD:** `c32373f`. · **Remote tip:** `b8d0447` (remote is AHEAD — other divisions pushed after my last push; concurrent shared branch).
- **Clean?** DIRTY — 3 untracked scratch files only (`code/four_regime_run.log`, `code/scoped_fdr_stdout.log`, `code/subset_probe.py`); no tracked modifications.
- **Authoritative registries:** `results/FAMILY_RESULTS.parquet` (per-hypothesis metrics, 1972 rows), the frozen docs above, and the MK state-machine modules on branch `discovery-mk-matrix-v1`.

## 0. Scope of "strategies" in this lab (three registers)
1. **20 grammar FAMILIES S1–S20** (`code/mstrat.py`, engine v2) — the primary objects. Each is a *grammar* (a family of parameterizations), NOT a deployable strategy. **1972 hypotheses total → 1440 distinct** after mechanical deduplication (D11; 27% redundant, lookback params inert when `ref≠swing`).
2. **9 SMC_S\* MK state machines** (`trading_strategies.py`, Mandate 5.9, branch `discovery-mk-matrix-v1`) — a *newer* re-formalization of a subset {S1,S2,S3,S7,S10,S11,S13,S16,S17}. **INERT** (no `.load()`, `net_R` defined-not-called, LM-001 locked). Cross-verified 2026-07-28 (`TS_CROSS_VERIFICATION_v1.0.md`, 17/17, 1 concept-reloop flag on S10).
3. **~26 Discovery Candidates DC-0001…DC-0026** (Alpha observation line) — market *observations/hypotheses*, not deployable strategies; three (DC-0003/0004/0008) reached the Statistician.

---

## 1. Strategy inventory + 2. Status + 3. Economics + 5. Profile (per family)
Common contract (all S1–S20): **primary TF M15**, **entry TF M15 next-open** (entry at `open[trigger+1]`), **SL** = `1.5×ATR` (option `atr`) or **structural** (`beyond_sweep/prev_ext/level/struct/ext/bar/or_opp/…`), floored to `max(2×spread,5×tick,0.10×ATR)` and (v2/D2-closed) excluding INVALID-EXECUTION trades; **TP/exit** = `rr2`(1:2) / `rr3`(1:3) / `time`(time-stop, 24 M15 bars ≈ 6h) / `trailing`(1.5×ATR trail) / `opp_liq`/`opp_struct`(opposite liquidity/structure level); **max hold** = window 48 bars (time-exit 24). **Direction: BOTH** for all (grammar `side`/`ctx` covers long & short). Statistic = mean R/trade; primary win-rates are LOW (0.29–0.38) across the board.

| Fam | ECON name | Regime | n_hyp | hist_prof (base/D2) | research_worthy | best exp(R) | med win | med DD(R) | best val_exp(OOS) | SL/TP options | Status | Profile |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **S1** | liquidity-sweep mean-rev | RANGE/TRANSITION | 1152 | 261/293 | **90** | +0.391 | 0.384 | 30.7 | +0.450 | structural stops; rr2/rr3/opp/time | RESEARCH_SURVIVOR + **STRUCTURAL_R_UNVALIDATED** | OTHER |
| **S2** | failed-breakout fade | TRANSITION/RANGE | 144 | 18/20 | 6 | +0.075 | 0.321 | 124.6 | +0.256 | atr/beyond_ext; rr2/opp/time | RESEARCH_SURVIVOR (persister ×1) | OTHER |
| S3 | breakout-retest momentum | TREND | 96 | 2/24 | 0 | +0.063 | 0.381 | 405.2 | N/A | atr/beyond_level; rr2/rr3/trail | INSUFFICIENT_EVIDENCE | OTHER |
| S4 | volatility-regime expansion | TRANSITION | 32 | 0/0 | 0 | −0.145 | 0.255 | 296.9 | N/A | atr/bar | **FAILED** (neg exp) | OTHER |
| **S5** | opening-range momentum | REGIME_INDEP/TREND | 96 | 20/20 | 12 | +0.166 | 0.377 | 60.2 | **+0.336 (OOS-survivor)** | atr/or_opp; rr2/rr3/opp/time | RESEARCH_SURVIVOR (best OOS) | OTHER |
| S6 | session-transition momentum | TRANSITION | 32 | 7/7 | 3 | +0.497 | 0.289 | 84.2 | +0.190 | atr/prev_ext; rr2/time | RESEARCH_SURVIVOR | OTHER |
| S7 | trend-pullback continuation | TREND | 24 | 0/0 | 0 | −0.099 | 0.287 | 1187.9 | N/A | atr/ema; rr2/rr3/trail | **FAILED** (neg exp, huge DD) | OTHER |
| S8 | extension mean-reversion | RANGE | 48 | 4/12 | 2 | +0.029 | 0.298 | 202.4 | +0.118 | atr/ext; rr2/opp/time | RESEARCH_SURVIVOR (weak) | OTHER |
| **S9** | MTF-trend momentum | TREND_UP/DOWN | 32 | 12/12 | 6 | +0.068 | 0.352 | 54.0 | +0.282 | atr/structural; rr2/rr3 | RESEARCH_SURVIVOR (HTF) | OTHER |
| S10 | displacement continuation | TREND | 48 | 0/0 | 0 | −0.051 | 0.299 | 293.7 | N/A | atr/bar; rr2/rr3/trail | **FAILED** (neg exp) | OTHER |
| S11 | structure-break reversal | TRANSITION | 24 | 0/0 | 0 | −0.052 | 0.352 | 100.5 | N/A | atr/struct; rr2/rr3/time | **FAILED** (neg exp) | OTHER |
| S12 | range rotation | RANGE | 48 | 0/2 | 0 | −0.036 | 0.346 | 236.5 | N/A | atr/ext; rr2/opp/time | **FAILED** (neg exp) | OTHER |
| S13 | imbalance fill | REGIME_INDEP | 24 | 5/5 | 0 | +0.041 | 0.329 | 305.3 | N/A | atr/struct; rr2/rr3/time | CANDIDATE (high DD) | OTHER |
| S14 | momentum exhaustion | TRANSITION | 16 | 6/6 | 1 | +0.579 | 0.364 | **10.1** | −0.137 (OOS-fail) | atr/bar; rr2/time | RESEARCH_SURVIVOR (OOS-fail) | OTHER |
| S15 | trend acceleration | TREND | 24 | 0/0 | 0 | −0.050 | 0.307 | 174.7 | N/A | atr/struct; rr2/rr3/trail | **FAILED** (neg; MK-declared GENUIN GOL) | OTHER |
| S16 | previous-day levels | REGIME_INDEP | 40 | 1/2 | 0 | +0.032 | 0.304 | 220.2 | N/A | atr/level; rr2/time | CANDIDATE (weak) | OTHER |
| **S17** | weekly levels | REGIME_INDEP | 24 | 6/8 | 5 | +0.424 | 0.309 | 45.3 | +0.077 | atr/level; rr2/rr3/time | RESEARCH_SURVIVOR (persister ×1) | OTHER |
| S18 | time-of-day | REGIME_INDEP | 24 | 5/5 | 0 | +0.177 | 0.302 | 73.4 | N/A | atr; rr2/time | CANDIDATE — **scoped-FDR survivor (h13-short), FLAGGED-NOT-CERTIFIED** | OTHER |
| S19 | session gap | REGIME_INDEP | 12 | 4/4 | 0 | +0.915 | 0.342 | **7.4** | N/A | atr; rr2/opp/time | CANDIDATE (low DD, unscreened) | OTHER |
| S20 | hybrid sweep+MTF | TREND | 32 | 6/6 | 5 | +0.099 | 0.333 | 84.3 | +0.172 | atr/struct; rr2/rr3 | RESEARCH_SURVIVOR (HTF) | OTHER |

**Overall status:** the whole lab is **STRICT VALIDATION PENDING** — *no family is VALIDATED*; nothing has passed independent OOS validation; the terminal holdout has never been opened. Totals: **1972 hyps, 357 hist-profitable (baseline) / 426 (D2-closed), 130 research-worthy, 133 fragile.**

**Profile (5):** ALL 20 families are **OTHER_PROFILE** — win rates 0.29–0.38 are too low for **Profile A** (needs ~70–80% WR) and below **Profile B**'s 45–55% band; RR is 1:2–1:3 (`rr2`/`rr3`). The lab's economic signature is *low-win-rate, tail-dependent* (median profitable hypothesis takes ~54% of net profit from a single trade — `NET_CONCENTRATION_INVENTORY_v1.0.md`). None fit A or B.

## 4. XAUUSD target geometry (research-worthy set; 10 pips = $1.00)
Median SL/TP over the research-worthy hypotheses (reconstructed on the research window; `rr`-exit hypotheses only for TP):

| Fam | med SL (pips / $) | med TP (pips) | %TP≥70 | %TP≥100 |
|---|---|---|---|---|
| **S5** | 104 / $10.3 | **236** | 100% | 96% |
| **S20** | 108 / $10.8 | **256** | 100% | 98% |
| **S9** | 97 / $9.7 | **254** | 99% | 93% |
| **S1** | 83 / $8.3 | **172** | 96% | 84% |
| S17 | 39 / $3.9 | 98 | 70% | 48% |
| S6 | 35 / $3.5 | 92 | 69% | 38% |
| S2 | 40 / $4.0 | 81 | 60% | 30% |
| S8 | 35 / $3.5 | 70 | 50% | 23% |

**Overall research-worthy: median SL 82 pips ($8.2), median TP 178 pips.** **These are MEANINGFUL Gold moves, not micro-scalping** — the strongest families (S5/S9/S20/S1) target TP 172–256 pips with 84–98% of trades intended ≥100 pips. (SL/TP in $/pips is N/A for `time`/`trailing`/`opp` exits, which have no fixed target.)

## 6. Evidence provenance
- **Splits (frozen):** research 60% (DEVELOPMENT+CALIBRATION), validation 20% (OOS), terminal holdout 20% **SEALED — never opened**.
- **Discovery Screen V1 was DEVELOPMENT-TUNED on S1–S10** (defect D4, selection bias) → S1–S10 evidence = **PARTIALLY_CONSUMED**; S11–S20 = first prospective test, closer to CLEAN but still under the same screen.
- **Global-FDR NEVER run with a valid p-value** on the full universe; the only FDR executed is the *scoped* one on the 412 ATR-regime hyps (`SCOPED_FDR_RESULT_v1.0.md`). Matched-null (Test B) is validated **only on the ATR-scaled regime** — structural stops are `STRUCTURAL_R_UNVALIDATED`.
- **DC-0004 holdout = CONSUMED** (contaminated: Alpha observed past the cutoff → `TESTABLE BUT INSUFFICIENT EVIDENCE`). DC-0003/DC-0008 evidence CLEAN-but-design-only.
- **Net verdict:** lab-wide evidence is **PARTIALLY_CONSUMED**; no family carries genuinely independent, validation-confirmed evidence.

## 7. Why candidates stopped (primary reason)
- **S4, S7, S10, S11, S12, S15** — **SCIENTIFIC_FAIL** (negative research expectancy; not historically profitable).
- **S1 + all 1544 structural-stop hypotheses** — **STRUCTURAL_R_UNVALIDATED** (the R=pnl/risk outcome variable is unsuitable where the stop can be minuscule; *not falsified* — blocked at the variable-definition level; finer data does not fix it).
- **S9, S20 (MTF)** — historically **HTF_FEATURE_BLOCKED** (needed H4/H1/D1 context); HTF context is now derived + validated back to 2011.
- **S18 scoped-FDR survivor (h13-short)** — passes research-FDR but **fails OOS** (val_p 0.078) and is the prime unexcluded Volatility-primitive alternative → TEMPORALLY_UNSTABLE / not certified.
- **S2, S17 persisters** — **TAIL_DEPENDENT** (persist across 3 regimes but single-trade-dependent in ≥1 regime).
- **M5 extension** — **DATA_BLOCKED / HTF_FEATURE_BLOCKED** (no M5-aligned HTF context; CTO-cancelled).
- **Everything else** — **GOVERNANCE_PAUSED** (STRICT VALIDATION PENDING; global-FDR, walk-forward, Red Team, holdout all gated on the p-engine + R-variable decisions).

## 8. LEGACY_CANDIDATES_WORTH_REREVIEWING (not scientifically falsified)
- **The 1544 STRUCTURAL_R_UNVALIDATED hypotheses (incl. ALL of S1, the lab's biggest, best-screened family)** — blocked by outcome-variable definition, not by evidence. Re-review requires the Statistician's outcome-variable spec (separate deliverable). Highest-leverage: unblocks 79% of the corpus.
- **S9 & S20 (MTF-trend)** — HTF context now exists back to 2011 (H4/H1/D1_from_M15_v2, CONTEXT_DERIVED_VALIDATED); large-TP (254–256 pips) trend families.
- **S5 (opening-range)** — the single **OOS-survivor** in the matched-null pilot; TP 236 pips.
- **S2 (pdh_pdl fade) & S17 (weekly levels)** — three-regime persisters.
- **The 9 SMC_S\* MK state machines** — inert, unlock when LM-001 / real prices are authorized.

## 9. Strongest historical candidates
**ROBUST_EVIDENCE:** *none.* Nothing has independent, validation-confirmed evidence; the one scoped-FDR research survivor fails OOS.
**PROMISING_BUT_UNPROVEN (ranked by existing evidence):**
1. **S5 opening-range** — only OOS-survivor in the pilot (research p 0.032 / OOS p 0.038), TP 236 pips, 100%≥70; ATR-regime (testable now).
2. **S1 liquidity-sweep** — 90 research-worthy, best OOS +0.45R, TP 172 pips — but STRUCTURAL_R_UNVALIDATED (re-review gated on the R variable).
3. **S9 MTF-trend** — 12/12 hist-profitable, OOS +0.28R, TP 254 pips; HTF now available.
4. **S20 hybrid sweep+MTF** — OOS +0.17R, TP 256 pips, 98%≥100.
5. **S17 weekly-levels** — persister, OOS +0.077R, RESEARCH_SURVIVOR.
6. **S18 h13-short (`ce76669a3b2a`)** — scoped-FDR research survivor (MC-3 p 6.8e-5 < BH 1.2e-4) — but OOS-fails and is likely the Volatility-primitive re-detection.
7. **S6 session-transition**, **S2 failed-breakout** — weaker RESEARCH_SURVIVORs with OOS>0.

## 10. Duplication with known archetypes (from ECON tags + logic)
opening-range momentum → **S5**; breakout continuation → **S3, S10**; pullback continuation → **S7**; liquidity sweep → **S1, S20**; failed breakout → **S2**; PDH/PDL → **S16**; weekly levels → **S17**; multi-timeframe trend → **S9, S20**; range mean-reversion → **S8, S12**; transition/reversal → **S11, S14, S6**; time/session → **S18, S19**; imbalance → **S13**. (These are the lab's own labels; not asserted identical to any external program without trade-log evidence.)

## 11. AI Trader status
**NONE of these strategies are implemented in, connected to, or shadowed by AI Trader.** They are **completely research-only**. The MK state machines are **INERT** (`net_R` defined-but-not-called; no `.load()`; LM-001 locked). No broker logic, no live, no demo, no runtime/shadow deployment. AI Trader is a separate implementation line (research-main) not fed by this lab.

## 13. Master table
| Strategy | ID | TF | Entry TF | Direction | Regime | WR | RR | TP pips | BASE (exp R) | STRESS | DD (R) | Evidence | Current Status | Why stopped | Re-review? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| liquidity-sweep | S1 | M15 | M15 next-open | BOTH | RANGE/TRANS | 0.38 | 1:2–3 | 172 | +0.39 | N/A | 30.7 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR / STRUCTURAL_R_UNVALIDATED | STRUCTURAL_R_UNVALIDATED | **YES** |
| failed-breakout fade | S2 | M15 | M15 | BOTH | TRANS/RANGE | 0.32 | 1:2 | 81 | +0.08 | N/A | 124.6 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR (persister) | TAIL_DEPENDENT | YES |
| breakout-retest | S3 | M15 | M15 | BOTH | TREND | 0.38 | 1:2–3 | N/A | +0.06 | N/A | 405.2 | PARTIALLY_CONSUMED | INSUFFICIENT_EVIDENCE | HIGH_DRAWDOWN | maybe |
| vol-regime expansion | S4 | M15 | M15 | BOTH | TRANS | 0.26 | 1:2–3 | N/A | −0.15 | N/A | 296.9 | CLEAN | FAILED | SCIENTIFIC_FAIL | no |
| opening-range mom | S5 | M15 | M15 | BOTH | REGIME_INDEP | 0.38 | 1:2–3 | 236 | +0.17 | N/A | 60.2 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR (OOS+) | GOVERNANCE_PAUSED | **YES** |
| session-transition | S6 | M15 | M15 | BOTH | TRANS | 0.29 | 1:2 | 92 | +0.50 | N/A | 84.2 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR | GOVERNANCE_PAUSED | YES |
| trend-pullback | S7 | M15 | M15 | BOTH | TREND | 0.29 | 1:2–3 | N/A | −0.10 | N/A | 1187.9 | CLEAN | FAILED | SCIENTIFIC_FAIL | no |
| extension mean-rev | S8 | M15 | M15 | BOTH | RANGE | 0.30 | 1:2 | 70 | +0.03 | N/A | 202.4 | CLEAN | RESEARCH_SURVIVOR (weak) | GOVERNANCE_PAUSED | maybe |
| MTF-trend | S9 | M15 | M15 | BOTH | TREND | 0.35 | 1:2–3 | 254 | +0.07 | N/A | 54.0 | CLEAN | RESEARCH_SURVIVOR | HTF_FEATURE_BLOCKED | **YES** |
| displacement cont | S10 | M15 | M15 | BOTH | TREND | 0.30 | 1:2–3 | N/A | −0.05 | N/A | 293.7 | CLEAN | FAILED | SCIENTIFIC_FAIL | no |
| structure-break rev | S11 | M15 | M15 | BOTH | TRANS | 0.35 | 1:2–3 | N/A | −0.05 | N/A | 100.5 | CLEAN | FAILED | SCIENTIFIC_FAIL | no |
| range rotation | S12 | M15 | M15 | BOTH | RANGE | 0.35 | 1:2 | N/A | −0.04 | N/A | 236.5 | CLEAN | FAILED | SCIENTIFIC_FAIL | no |
| imbalance fill | S13 | M15 | M15 | BOTH | REGIME_INDEP | 0.33 | 1:2–3 | N/A | +0.04 | N/A | 305.3 | CLEAN | CANDIDATE | HIGH_DRAWDOWN | maybe |
| momentum exhaustion | S14 | M15 | M15 | BOTH | TRANS | 0.36 | 1:2 | N/A | +0.58 | N/A | 10.1 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR (OOS-fail) | TEMPORALLY_UNSTABLE | maybe |
| trend acceleration | S15 | M15 | M15 | BOTH | TREND | 0.31 | 1:2–3 | N/A | −0.05 | N/A | 174.7 | CLEAN | FAILED / GENUIN GOL | SCIENTIFIC_FAIL | no |
| previous-day levels | S16 | M15 | M15 | BOTH | REGIME_INDEP | 0.30 | 1:2 | N/A | +0.03 | N/A | 220.2 | CLEAN | CANDIDATE (weak) | HIGH_DRAWDOWN | maybe |
| weekly levels | S17 | M15 | M15 | BOTH | REGIME_INDEP | 0.31 | 1:2–3 | 98 | +0.42 | N/A | 45.3 | PARTIALLY_CONSUMED | RESEARCH_SURVIVOR (persister) | TAIL_DEPENDENT | YES |
| time-of-day | S18 | M15 | M15 | BOTH | REGIME_INDEP | 0.30 | 1:2 | N/A | +0.18 | N/A | 73.4 | PARTIALLY_CONSUMED | scoped-FDR survivor FLAGGED-NOT-CERTIFIED | TEMPORALLY_UNSTABLE (OOS-fail) | maybe |
| session gap | S19 | M15 | M15 | BOTH | REGIME_INDEP | 0.34 | 1:2 | N/A | +0.92 | N/A | 7.4 | CLEAN | CANDIDATE (low DD, unscreened) | GOVERNANCE_PAUSED | maybe |
| hybrid sweep+MTF | S20 | M15 | M15 | BOTH | TREND | 0.33 | 1:2–3 | 256 | +0.10 | N/A | 84.3 | CLEAN | RESEARCH_SURVIVOR | HTF_FEATURE_BLOCKED | **YES** |

*(STRESS expectancy is N/A — the lab never computed a per-family cost-stress expectancy at this granularity; a 3× cost-stress convention exists but was not applied per-family.)*

---

## 14. Final answers
1. **How many strategy/candidate identities?** **20 grammar families → 1972 hypotheses → 1440 distinct strategies** (27% redundant, D11). Plus **9 SMC_S\* MK state machines** (re-formalization of a subset, inert) and **~26 Discovery Candidates** (Alpha observations). Distinct top-level "strategy identities" = **20 families / 9 MK machines / ~26 DCs**.
2. **How many failed/rejected?** **6 families FAILED** (S4, S7, S10, S11, S12, S15 — negative research expectancy). At hypothesis level: of the 428 ATR-regime hyps, **367 are profitable in zero of the 3 regimes** (Statistician label ZERO_ALPHA_BASE_RATE). No family has been *formally* REJECTED (no valid FDR verdict issued yet).
3. **How many remain scientifically plausible?** **9 families** carry ≥1 research-worthy hypothesis (S1, S2, S5, S6, S8, S9, S14, S17, S20) + the **1544 STRUCTURAL_R_UNVALIDATED** hypotheses that were *never falsified* (blocked on the outcome variable). Scientifically-alive top-level families ≈ **9–11**.
4. **How many passed deep research?** **Zero families** passed deep/independent validation. The deepest evidence anywhere: DC-0003/DC-0008 reached *READY FOR STATISTICAL VALIDATION* (design-only, not confirmed); the scoped-FDR produced **1 research-FDR survivor** (S18 h13-short) that **fails OOS**.
5. **How many have independent validation?** **ZERO.** No terminal-holdout test has ever been run; DC-0004's holdout was contaminated; nothing carries validation-confirmed independent evidence.
6. **5–10 most interesting today:** **S5 (opening-range, OOS-survivor)**, **S9 (MTF-trend, HTF now available)**, **S20 (hybrid sweep+MTF)**, **S1 (liquidity-sweep, gated on R-variable)**, **S17 (weekly-levels, persister)**, **S2 (failed-breakout, persister)**, **S18 h13-short (`ce76669a3b2a`, FDR survivor / OOS-fail)**, **S6 (session-transition)** — all target meaningful Gold moves (TP 81–256 pips), none independently validated.
7. **Re-evaluate under current infra:** **(a)** the STRUCTURAL_R_UNVALIDATED set incl. all of S1 — needs the Statistician's outcome-variable spec (biggest leverage, 79% of the corpus); **(b)** S9 & S20 (MTF) — HTF context now validated back to 2011; **(c)** S5 (opening-range) — clean ATR-regime OOS-survivor, testable now; **(d)** the 9 MK state machines once LM-001/prices unlock.
8. **Anything running / connected to AI Trader?** **NO.** Everything is research-only; MK modules inert; no broker/live/demo/shadow/runtime integration.
9. **Recommended next CEO action:** **Commission the Statistician's outcome-variable specification for the structural-stop regime** (the single gate that unblocks 79% of the corpus and all of S1, the best-screened family), **AND** authorize a scoped re-review of the three clean, ATR-regime, large-Gold-move survivors **S5 / S9 / S20** on the now-available 11-year, 3-regime discovery data — as *descriptive* persistence measurements, **not** as validation. **Do NOT open the terminal holdout** and **do NOT run global-FDR** until the R-variable decision and a validated p-engine exist. Everything remains research-only; no AI Trader connection.

**END — inventory/reconstruction only. No code modified, no research re-run beyond descriptive aggregation, nothing promoted, holdout SEALED, no AI Trader change.**
