# ALPHA_HISTORICAL_REREVIEW_WAVE1_REPORT

**Mandate:** `ALPHA-HISTORICAL-REREVIEW-WAVE1-001` · **Date:** 2026-08-21 · **Status:** `ALPHA_HISTORICAL_REREVIEW_WAVE1_COMPLETE` → `READY_FOR_CEO_ALPHA_PORTFOLIO_DECISION`.
Re-review of pre-RANGE candidates under **current** measurement, DEVELOPMENT only. **Not validated. No promotion. FINAL_HOLDOUT_ACCESS = 0.**

## 1. Provenance
Inventory `af41db8`; historical specs from `STRATEGY_CANDIDATE_REGISTRY.parquet` (canonical_strategy_spec) + `mstrat.py` family definitions (wp5b `discovery-mk-matrix-v1`); DC specs from `discovery_candidates/DC-000{3,8}` frozen docs; cost from RATIFIED `AI_TRADER_SHADOW_COST_MODEL_v1`. All from repository, not memory.

## 2–3. Exact historical candidate identities + HISTORICAL_BASELINE_SPEC
| ID | Family | Mechanism | Dir | Canonical spec | Historical (native window) metrics |
|---|---|---|---|---|---|
| C_2d587447 | S5 | opening-range momentum, NY | long | `S5{exit=rr3,mode=breakout,session=ny,side=up,stop=or_opp}` | exp +0.166, PF 1.48, robustness 2.14, n 287 |
| C_0bb5095b | S9 | MTF-trend momentum (H4 up, 1h any) | long | `S9{c4h=up,conf1h=any,exit=rr2,lb=20,stop=structural}` | exp +0.068, PF 1.15, robustness 1.76, n 545 |
| C_d008e0a4 | S9 | MTF-trend momentum (H4 up, 1h align) | long | `S9{c4h=up,conf1h=align,exit=rr3,lb=10,stop=structural}` | exp +0.063, PF 1.12, robustness 1.51, n 512 |
| C_09d2245b | S20 | hybrid sweep+MTF (H4 up, breakout) | long | `S20{ctx=h4up,exit=rr3,lb=50,stop=atr,trig=breakout}` | exp +0.075, PF 1.10, robustness 1.34, n 456 |
| C_954698b1 | S1 | liquidity-sweep MR (swing low, FVG) | long | `S1{confirm=close_beyond,exit=time,imb=fvg,liq_ref=swing,side=low,stop=beyond_sweep,window=8}` | exp +0.071, PF 1.17, robustness 1.26, n 193 |
| C_dca5629f | S1 | liquidity-sweep MR (PDH/PDL low) | long | `S1{confirm=consecutive2,exit=rr2,imb=none,liq_ref=pdh_pdl,side=low,...}` | exp +0.032, PF 1.05, robustness 1.22, n 399 |
| C_9214b37b | S1 | liquidity-sweep MR (PDH/PDL high) | short | `S1{confirm=displacement,exit=rr3,imb=none,liq_ref=pdh_pdl,side=high,...}` | exp +0.017, PF 1.03, robustness 1.06, n 241 |
| DC-0003 | discovery | scale-inversion (micro-C vs macro-C resolve oppositely) | — | frozen doc DC-0003 | 🟢 SURVIVED Red Team (descriptive) |
| DC-0008 | discovery | large M15 candle from sustained multi-minute volume | — | frozen doc DC-0008 | 🟢 SURVIVED Red Team (descriptive) |

## 4. Reproduction / migration audit (KEY FINDING)
Family logic reproduced faithfully from `mstrat.py`. **Critical constraint discovered:** the HTF/PDH context features (`h4_trend_up`, `h1_trend_up`, `pdh`, `pdl`) are populated **only from 2023-01-03 onward** in the feature pipeline — i.e. the S-family's original backtest window (≈2023–2025) **is the current VALIDATION partition**. Consequences:
- **S5** (opening-range: OR/session, M15-only) and **S1-swing** (M15 swing levels): fully DEVELOPMENT-replayable → replayed.
- **S9 (×2), S20, S1-PDH/PDL (×2)**: HTF/PDH context absent in DEVELOPMENT → 0 signals. A faithful DEVELOPMENT replay requires **recomputing HTF context from M15** (a measurement migration); evaluating them on their native 2023+ window would **consume VALIDATION** (prohibited, item 18). → `HISTORICAL_CANDIDATE_IMPLEMENTATION_MIGRATION_REQUIRED`. **Not approximated silently.**
- **DC-0008**: requires **M1 multi-minute volume anatomy** (absent from M15 DEVELOPMENT) → `IMPLEMENTATION_MIGRATION_REQUIRED`.
- **DC-0003**: the frozen doc itself states the micro-C/macro-C **class boundary was never operationalized** ("the operational question is where the boundary lies") → `IMPLEMENTATION_MIGRATION_REQUIRED` (spec under-defined).

## 5–6. Execution model + data partitions
Current ratified: TICK 0.01, entry next-bar-open, floor `max(2·spread,0.05,0.10·ATR)`, full bid-ask, **BASE round-trip 0.05 / STRESS round-trip 0.24** (CEO ruling), applied via slip_ticks. Partition: **DEVELOPMENT = contiguous `<2018-05-01`, 160,888 bars** (SEALED-safe, max dt < 2025-10-23). VALIDATION/FINAL-HOLDOUT untouched.

## 7. S5 — opening-range momentum → **HISTORICAL_CANDIDATE_CONFIRMED_FOR_DEEPER_RESEARCH**
DEV n=873: GROSS +0.071 / **BASE +0.063 / STRESS +0.031** (positive through STRESS), PF 1.17, win **47.3%**, avg_win/avg_loss healthy, temporal-conc **0.43** (distributed), best-trade share **0.055** (no single-trade dependence), max-DD −17.4 R, top-1% share 0.44 (moderate tail). Regime dist: **90% TREND_UP** (it is effectively a trend-uptrend opening-range breakout). Session-specificity is structural (NY only, by design). **Survives modern measurement.**

## 8. S9 variants → **MIGRATION_REQUIRED** (both C_0bb5095b, C_d008e0a4)
Cannot be replayed on DEVELOPMENT (HTF trend context begins 2023 = VALIDATION). Overlap-with-Candidate-001 (item 12) **deferred** to post-migration — flagged as the highest-value migration because S9 (MTF-trend momentum) is economically nearest to Candidate-001 (trend continuation).

## 9. S20 → **MIGRATION_REQUIRED** (HTF context). Component decomposition (item 13) deferred to post-migration.
## 10. S1 results
- **S1-swing (C_954698b1) → FAIL:** DEV n=385, GROSS −0.059 / BASE −0.068 / STRESS −0.102, PF 0.83, **89% TREND_DOWN** (fires mostly in downtrends and loses). The liquidity-sweep mean-reversion mechanism has **no edge** on DEVELOPMENT.
- **S1-PDH/PDL (C_dca5629f, C_9214b37b) → MIGRATION_REQUIRED** (PDH/PDL absent in DEVELOPMENT).
- **S1 × V4.4 RANGE conditioning (item 14):** cannot be measured on DEVELOPMENT for the PDH/PDL variant (0 signals); for the swing variant the mechanism already fails unconditionally, so RANGE conditioning is moot on DEV. Deferred to post-migration.

## 11. DC-0003 → **MIGRATION_REQUIRED** (class boundary never operationalized).
## 12. DC-0008 → **MIGRATION_REQUIRED** (needs M1 volume anatomy).
## 13. DC-0004 → **GOVERNANCE_PAUSED_REQUIRES_FRESH_EVIDENCE** (holdout burned; excluded from Wave 1 per mandate §3; evidence-recovery is a separate proposal).

## 14. BASE/STRESS comparison
S5: BASE +0.063 → STRESS +0.031 (survives, ~50% cost-haircut). S1-swing: negative at every level. (Migration-required candidates not evaluated.)

## 15. Temporal stability
S5 temporal-concentration 0.43 (< 0.6 threshold) — no single year dominates. (Full per-block stability deferred to the bounded deeper phase for survivors.)

## 16. Direction decomposition
S5: long-only by spec (NY up-breakout). S1-swing: long-only, but 89% of entries land in TREND_DOWN (why it loses). S9/S20 long-only (not evaluable on DEV).

## 17. Regime-conditioning analysis
S5 fires 90% in TREND_UP → it is **already a de-facto trend-conditioned mechanism** (a trend gate `DOES_NOT_MATERIALLY_CHANGE` it since it self-selects uptrends). S1-swing `DEGRADES` outside its (absent) intended context. Formal unconditional-vs-conditioned decomposition for S9/S20/S1-PDH deferred to post-migration.

## 18. Tail diagnostics
S5 top-1% share 0.44 (moderate — worth watching, but win-rate 47% and best-share 0.055 indicate it is NOT a single-trade lottery, unlike Candidate-001's fat-tail). S1-swing: negative, N/A.

## 19. Historical-vs-current table
| Candidate | Historical status | Historical evidence (native ≈2023+ window) | Current BASE (DEV) | Current STRESS (DEV) | Current status |
|---|---|---|---|---|---|
| S5 C_2d587447 | B_research (robust 2.14) | exp +0.166, PF 1.48 | **+0.063** | **+0.031** | **CONFIRMED** |
| S9 C_0bb5095b | B_research (1.76) | exp +0.068 | — (HTF absent) | — | MIGRATION_REQUIRED |
| S9 C_d008e0a4 | B_research (1.51) | exp +0.063 | — | — | MIGRATION_REQUIRED |
| S20 C_09d2245b | B_research (1.34) | exp +0.075 | — | — | MIGRATION_REQUIRED |
| S1 C_954698b1 (swing) | B_research (1.26) | exp +0.071 | **−0.068** | **−0.102** | **FAIL** |
| S1 C_dca5629f (PDH low) | B_research (1.22) | exp +0.032 | — | — | MIGRATION_REQUIRED |
| S1 C_9214b37b (PDH high) | B_research (1.06) | exp +0.017 | — | — | MIGRATION_REQUIRED |
| DC-0003 | 🟢 SURVIVED RT | descriptive | — | — | MIGRATION_REQUIRED |
| DC-0008 | 🟢 SURVIVED RT | descriptive | — | — | MIGRATION_REQUIRED |
| DC-0004 | INCONCLUSIVE (p=0.021) | holdout burned | — | — | GOVERNANCE_PAUSED |

## 20. Mechanism overlap analysis (vs ALPHA_CANDIDATE-001)
Candidate-001 (displacement+acceptance) DEV signal set = 5,387 bars. **S5 signal overlap = 321 bars, Jaccard 0.026 → `INDEPENDENT_ALPHA_SOURCE`.** Both are trend-following in bias (S5 90% TREND_UP; Candidate-001 trend-conditioned), but they take **different trades** (opening-range breakout vs displacement+acceptance) — i.e. shared market bias, decorrelated entries. S9 overlap (the economically nearest) deferred to post-migration.

## 21–23. Survivors / failures / insufficient
- **Survivor (deeper-research):** **S5 opening-range momentum** (1).
- **Fail:** S1-swing liquidity-sweep MR (1).
- **Migration-required:** S9 ×2, S20, S1-PDH ×2, DC-0003, DC-0008 (7).
- **Governance-paused:** DC-0004 (1).
- Insufficient-evidence: 0 (the 0-signal cases are migration issues, not sparse samples).

## 24. Recommended deeper-review portfolio
1. **S5 opening-range momentum** — the one clean survivor; independent of Candidate-001; proceed to the bounded deeper phase (per-block stability, tail, delay degradation, session-robustness).
2. **HTF-context migration (proposed, not executed)** — recompute H4/H1/D1 trend + PDH/PDL from M15 for DEVELOPMENT so S9/S20/S1-PDH can get a *clean* DEVELOPMENT re-review, **avoiding the circularity** of using their native (now-VALIDATION) window. S9 first (nearest to Candidate-001).

## 25. Comparison with ALPHA_CANDIDATE-001 (frozen, unchanged)
| | Candidate-001 (displacement+acceptance) | S5 (opening-range) |
|---|---|---|
| BASE / STRESS (DEV) | +0.114 / +0.053 | +0.063 / +0.031 |
| win rate | 33% | **47%** |
| tail | **fat (best-1%-removed → negative)** | moderate (best-share 0.055) |
| regime | trend-conditioned (needs gate) | 90% TREND_UP (self-selects) |
| overlap | — | Jaccard 0.026 (**independent**) |
Candidate-001 has higher expectancy; **S5 has a healthier win-rate and is decorrelated** — a genuinely distinct second source (item 25). Neither merged nor promoted.

## 26–27. FINAL_HOLDOUT_ACCESS_COUNT = 0 · Integrity
No FINAL-HOLDOUT access, no VALIDATION consumed, no SEALED access, no FB14/F441/MB3 tuning, no RANGE retuning, V4.4 frozen (config_id `23d98c07…`), no new strategy families generated, no AI Trader / N1–N6 / Strategy Router / MT5 touch, broker disabled. No integrity stop.

## 28. CEO next-step recommendation
1. **Advance S5 to bounded deeper research** alongside Candidate-001 — two decorrelated candidates is a better portfolio than one.
2. **Authorize a bounded HTF-context migration** (separate mandate) to re-review S9/S20/S1-PDH on DEVELOPMENT without touching VALIDATION — this is required to fairly judge the majority of the historical S-family.
3. **Decide DC-0004 evidence recovery** (fresh uncontaminated window) as a governance item.
4. **Keep S1-swing closed** (failed on merits); DC-0003/DC-0008 remain migration-blocked until M1 data / an operational boundary spec exist.

**STOP — awaiting CEO portfolio decision. No auto-proceed to validation/catalog/AI Trader.**
