# ALPHA_DISCOVERY_AUTONOMOUS_CAMPAIGN_REPORT

**Mandate:** `ALPHA-DISCOVERY-AUTONOMOUS-CAMPAIGN-001` · **Date:** 2026-08-21 · **Status:** `ALPHA_DISCOVERY_AUTONOMOUS_CAMPAIGN_COMPLETE` → `READY_FOR_CEO_ALPHA_SURVIVOR_REVIEW`.
**Early-stopped at 35 of 200 IDs** (item 31: marginal information gain collapsed — 17 distinct mechanism families tested across all regime classes, remaining ideas are threshold variants). **Zero-winner would have been acceptable; the campaign yielded exactly one candidate, with a disclosed limitation.**

## 1. Campaign provenance
Plan commit `db73f11`; VE closure `6120b5d`; frozen RANGE V4.4 `3bb61cf` (config_id `23d98c07…` verified). Cost = RATIFIED `AI_TRADER_SHADOW_COST_MODEL_v1` (config-fp `b7bb9a9aed17a1c8`) — BASE round-trip **0.05**, **STRESS round-trip 0.24** (CEO ruling, applied exactly via slip_ticks; floor `max(2·spread,0.05,0.10·ATR)` via scenario stop pre-widening; entry next-open; TICK=0.01). N1 regime = `ve_n1_replay` incremental ledger; RANGE feature = V4.4 CONFIRMED (`macro_state=="CONFIRMED"`).

## 2. Wave 1 results
See `ALPHA_WAVE1_CHECKPOINT.md`. H11 displacement+acceptance = PASS (sole survivor); H14 session FAIL (temporal-conc 0.65); H05 breakdown-acceptance FAIL; H02 failed-bearish-counter INSUFFICIENT (n=73); H08 boundary-rejection FAIL (6% win, fat-tail; V4.4 CONFIRMED occupancy real at 5.5%).

## 3–8. Counts
| metric | value |
|---|---|
| generated / tested | **35** hypothesis-version IDs (5 Wave-1 + 30 campaign) |
| FAST_FALSIFICATION_FAIL | 22 |
| COST_FRAGILE_STRESS_NEGATIVE (BASE+ / STRESS−) | 3 |
| INSUFFICIENT_EVIDENCE | 3 (H02, C-TU/TD-failedcounter) |
| EVENT_SPARSE | 1 (C-RI-gap) |
| excluded (impl bug) | 1 (C-R-boundary-mid, opp_liq path) |
| **FAST_FALSIFICATION_PASS (STRESS-gated)** | **5 versions of ONE mechanism** (displacement+acceptance) |
| **ALPHA_CANDIDATE** | **1** (displacement+acceptance, trend-conditioned, fat-tail caveat) |

## 9. Regime / family coverage
17 distinct families across all 5 regime classes: pullback, momentum, continuation, compression-accel, exhaustion, displacement-acceptance, multiscale-displacement, vol-expansion, structural-reversal (CHoCH), boundary-fade, range-breakout, vol-asymmetry, conditional-momentum, failed-counter, gap, session/session-regime, opening-range. No forced equality; RANGE and short-side each yielded zero robust survivors (accepted scientific result).

## 10. Hypothesis graveyard summary (`ALPHA_HYPOTHESIS_GRAVEYARD`)
Every failed ID retained with mechanism/test/result/reason/data in `campaign_records.json` + `campaign2_records.json` + `wave1_records.json`. Recurrent failure modes: **cost fragility at STRESS** (most trend/momentum/continuation mechanisms are BASE-marginal and STRESS-negative on M15), **temporal concentration** (session, breakdown-acceptance), **fat-tail lottery** (boundary-fade: 6% win, best-share 2.1). No idea resurrected with cosmetic changes.

## 11. Strongest mechanism — displacement + acceptance (the ALPHA_CANDIDATE)
The single mechanism surviving realistic (STRESS) cost. A ≥w·ATR displacement bar followed by N-bar acceptance in the displacement direction → enter continuation. Robust across a parameter neighborhood and both DEVELOPMENT sub-blocks (details in §Candidate package).

## 12. Failed mechanism families (informative negatives)
- **Short-side (TREND_DOWN)**: no robust survivor — pullback/momentum/continuation/compression/exhaustion/breakdown-acceptance all STRESS-negative or concentrated. Consistent with the prior canonical rerun. *Acceptance did not rescue shorts.*
- **RANGE (V4.4)**: CONFIRMED occupancy is real (5.5%), but boundary-fade is a fat-tail lottery and accepted-breakout is negative → **NO RANGE ALPHA ESTABLISHED** (a legitimate result per CEO §2).
- **Regime-independent**: session, vol-asymmetry, conditional-momentum, gap, opening-range — all cost-fragile or event-sparse. **No regime-independent alpha established** on M15.
- **Cost-fragile-but-real (BASE+/STRESS−)**: exhaustion-short, vol-expansion, CHoCH-reversal — real gross/BASE edge eaten by the 0.24 STRESS cost; flagged, not promoted.

## 13. Cost survival
Only displacement+acceptance survives BASE **and** STRESS. The dominant campaign lesson: **on XAUUSD M15, most mechanisms have gross edge but are eaten by realistic round-trip cost (0.24 STRESS)**; small-target mechanisms (mean-reversion, momentum scalps) fail hardest.

## 14. Robustness results (displacement+acceptance, rep C-TR-da-w08-a2, n≈3563)
| test | result |
|---|---|
| full BASE / STRESS avg_R | **+0.114 / +0.053** (positive both) |
| time stability | block1 2011-13 BASE **+0.145**; block2 2016-18 BASE **+0.082** (positive both) |
| parameter neighborhood (w0.6–1.2, a2–3) | BASE +0.078 … +0.114 (stable, not knife-edge) |
| **best-1%-trade removed** | BASE **−0.014** ⚠ **fat-tail dependence — edge carried by top ~1% of trades** |
| regime-conditioning | trend-only **+0.117**, non-trend **−0.199** → really a **trend-conditioned** mechanism; N1 router adds value |

## 15–17. Data / evidence / validation / holdout
Data consumed: **DEVELOPMENT only** (2011-07→2018-04, 105,254 bars; repeatable per plan). **VALIDATION consumed: 0** (untouched — reserved for the candidate's next stage). **FINAL_HOLDOUT_ACCESS_COUNT: 0.** V4.4 dev run consumed ~9 min compute.

## 18. Parameter / variant accounting
35 IDs; the displacement+acceptance mechanism has 5 versions (H11 + 4 param variants) counted as ONE mechanism cluster (parameter neighborhood), not 5 discoveries. No threshold-clone padding.

## 19. Anti-overfitting audit
Every material variant = new ID; no VALIDATION reuse; no cherry-picked periods; no post-hoc trade removal (best-trade-removal is a *robustness test*, not a rescue); no post-hoc cost change; complete graveyard retained; falsification criteria fixed before results; STRESS gate applied uniformly.

## 20. Checkpoint history
`ALPHA_WAVE1_CHECKPOINT` (5 IDs) → `campaign_checkpoint_final` (24 IDs) → campaign-2 extension (6 IDs) + robustness → this report. Checkpoints in `reports/alpha_discovery/`.

## 21. Integrity status
No future leakage; no partition contamination; **FINAL_HOLDOUT untouched (0)**; no MI code/config mutation; V4.4 frozen (config_id verified, `acknowledge_construction_only`); no FB14/F441/MB3 tuning; MB3-025→048 SEALED; `BROKER_ORDER_SUBMISSION` disabled; no AI Trader / Strategy Catalog / LIVE. No `ALPHA_DISCOVERY_INTEGRITY_STOP` condition encountered.

## 22. Recommended candidates for independent review
**ALPHA_CANDIDATE-001 — displacement+acceptance (trend-conditioned).** Recommended for Statistician + Red Team **with its fat-tail limitation front-and-center** (the top ~1% of trades carry the edge; best-1%-removed BASE is slightly negative). This is precisely the kind of concentration the Statistician must adjudicate before any promotion. Also worth a look: the 3 cost-fragile mechanisms (exhaustion / vol-expansion / CHoCH) as *gross-edge-but-cost-eaten* — not candidates, but evidence about where M15 cost drag binds.

## 23. Recommended next research direction
1. **Exit-side research on displacement+acceptance** — a better exit (trailing / structural, vs the current time-48) may reduce the top-1% dependence; test as new versions on DEVELOPMENT.
2. **Trend-gate is mandatory** for this mechanism (non-trend −0.199) — carry the N1 trend context into the candidate spec.
3. **RANGE**: no alpha under the naive fade; a *displacement-out-of-range* variant (not fade) is the only untested RANGE angle worth a small allocation.
4. **Do not** keep grinding threshold variants of the failed families — the STRESS-cost wall is structural on M15; a higher timeframe (H1) proposal (causal, timestamp-safe) may be the higher-information next step.

---

## ALPHA_CANDIDATE-001 — package (item 35)
| field | value |
|---|---|
| mechanism | displacement bar (\|close−open\| ≥ w·ATR14) + N-bar acceptance (closes hold the displacement direction) → enter continuation next-open |
| exact spec | rep: w=0.8·ATR, N_accept=2, entry=next-open at bar j+N, stop=displacement-origin open[j] widened to floor, exit=time-48 |
| version identity | C-TR-da-w08-a2 (+ neighborhood H11/w10-a2/w12-a2/w10-a3) |
| regime relationship | TRANSITION-triggered, **TREND-conditioned** (trend-only +0.117; non-trend −0.199) |
| development evidence | n≈3563; GROSS +0.130 / BASE +0.114 / STRESS +0.053; win 33%; PF 1.17; temporal-conc 0.29; both blocks positive |
| calibration/validation evidence | VALIDATION untouched (0) — reserved for the next authorized stage |
| cost sensitivity | positive through STRESS 0.24; degrades gracefully across BASE→STRESS |
| robustness | time-stable, param-stable; **⚠ fat-tail: best-1%-removed BASE −0.014** |
| failure modes | fat-tail dependence (top ~1% trades); fails outside trend regime; exit is naive (time-only) |
| sample size | 3563 signals on DEVELOPMENT |
| parameter sensitivity | stable across w0.6–1.2, N_accept 2–3 |
| known limitations | edge concentrated in the tail; requires N1 trend gate; DEVELOPMENT-only (no OOS yet); exit under-optimized |
| reproduction | `reports/alpha_discovery/campaign.py` + `campaign2.py`, DEVELOPMENT via official loader, n1_ledger regime, cost model as above |
| **promotion status** | **`ALPHA_CANDIDATE`** — NOT validated/promoted/live. Requires ROBUSTNESS_PASS → OOS_PASS → STATISTICAL_REVIEW → RED_TEAM → CEO_DECISION. |

**Final statuses:** `ALPHA_WAVE1_COMPLETE` · `ALPHA_DISCOVERY_AUTONOMOUS_CAMPAIGN_COMPLETE` · `READY_FOR_CEO_ALPHA_SURVIVOR_REVIEW`. No auto-proceed to validation. Returning to CEO.
