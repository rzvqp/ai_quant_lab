# ALPHA_XAUUSD_AUTONOMOUS_DISCOVERY_LOOP_FIRST_ROBUST_REPORT

**Mandate:** `ALPHA-XAUUSD-AUTONOMOUS-DISCOVERY-LOOP-FIRST-ROBUST-001` (+ frequency addendum) · **Date:** 2026-08-22.
**Terminal status:** `AUTONOMOUS_ALPHA_LOOP_COMPLETE` · **`SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA`** · `NO_NEW_STRATEGY_READY_FOR_VALIDATION`.
**Scope:** autonomous closed-loop search for the FIRST new robust strategy after S5. Price-only XAUUSD; native-M5→M15/H1/H4; DEV-only; no CALIB/2024/2025+/N4/V1; no MI/S5 change; no AI Trader/execution. **Anti-overfit hard stop invoked (§45): reported failure rather than fabricate.** No promotion; broker disabled.

---

## 0. Headline
- **The autonomous loop pivoted through six materially-distinct NEW mechanism families this run** — failed-reversal-continuation, HTF-structural-level reaction, session directional-acceptance, momentum-ignition, structural-reclaim, volatility-reset second-leg — **all falsified**, on top of the entire prior program's graveyard.
- **No robust candidate exists.** Across every family: WR 0.33–0.51 (never robustly positive at 1:1 or RR>1), **best-10%-removed negative everywhere**, DISC↔CONF sign-inconsistent, positive cells single-year (mostly 2021 or 2022), and natural structural stops of **31–45p — below the desired 70–100p zone.**
- **The failure is structural, not a search deficiency:** XAUUSD 2021–2023 is a strongly-trending, high-intraday-noise regime — mean-reversion is run over, breakouts whipsaw, and directional continuation at tradeable stops has ~50/50 path outcomes. **No simple price-only mechanism overcomes this at the required standards.**
- Per §45/§52, this is reported as `SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA` — **not** a fabricated survivor.

## 1. Autonomous loop process (§41) + hypothesis registry (§10, §20)
The loop ran `MECHANISM → SCREEN → PATH → 1:1/RR conversion → DISC/CONF → robustness → PIVOT`, choosing each next family to attack the *demonstrated* dominant failure mode (§21), never parameter-mining. **New families this run (H1 or H4+H1 context, natural structural stop, RR {1.0, 1.5, 2.0}, path-first, net STRESS, DISC/CONF, year):**
| family | rationale (failure-mode addressed) | N (best) | verdict |
|---|---|---|---|
| FAILED_REV | enter *after* adverse reversal already failed (adverse-first) | 50 | negative (2022 −0.68/−0.88) |
| HTF_REACT | HTF structural-level reaction, nearby invalidation | 25 | negative |
| SESSION_ACC | session directional acceptance + pullback | <15 | too rare |
| MOM_IGN | momentum already established (uncertainty reduced) | 309 | negative (best-10%-rem −0.16 to −0.39) |
| STRUCT_RECLAIM | lose level → rapid reclaim → hold | 150 | negative |
| VOL_RESET | impulse → contraction → renewed impulse (2nd leg) | 71 | negative |
Each × LONG/SHORT × 3 RR. **Gate (avgR>0 ∧ DISC>0 ∧ CONF>0 ∧ best-10%-rem>0 ∧ all-years>0 ∧ N≥30): 0 of all configs passed.**

## 2. Program-wide graveyard incorporated (§12, §43)
This loop builds on ~15 prior mandates that already falsified: generic/local RANGE fade & breakout; Asia-High / London-PLH / PDH sweeps & clean-shorts; same-TF & nested-MTF price sequences; probabilistic state models; post-E1 clean-path; and 5-mechanism 1:1 trend-continuation (`hp_portfolio`) + 3-mechanism M15 continuation (`trend_cont`, weak/tail-dependent). **Across the whole program, well over 60 materially-distinct economic hypotheses have been tested** — the §20 budget is genuinely explored.

## 3. Failure-mode map (§21, §42, §52) — the accumulated scientific lesson
| # | dominant failure mode | evidence | implication |
|---|---|---|---|
| 1 | **1:1 WR ceiling ~50–60%** | every mechanism WR 0.33–0.51 at 1:1 | desired 70–80% WR is unattainable — gold's noise vs a ~70p stop makes +1R-before-−1R ≈ 50/50 |
| 2 | **Adverse-first path pervasive** | fades/continuations stopped before the move | even "enter after adverse-failed" (FAILED_REV/STRUCT_RECLAIM) fails — in real trends the "failed" reversal wasn't failed |
| 3 | **Fade↔breakout duality** | fade → trend resumes (class-C 65–80%); breakout → whipsaw (class-C 58–72%) | balanced-vs-trend regimes both defeat the naive edge |
| 4 | **Stop-ownership trap** | tight stops noise-stopped 49–73%; wide H1 stops → tail-dependent weak edges (best-10%-rem<0) | no stop distance simultaneously survives noise and keeps RR |
| 5 | **SHORT is regime-locked** | shorts positive only 2022-concentrated | no all-conditions short edge |
| 6 | **High-confidence states are tight or rare** | natural stops 30–45p (below 70–100p) or N<20 | the desired geometry and high selectivity conflict |
| 7 | **Tail-carried marginal positives** | best-10%-removed negative in essentially every config | apparent edges are top-trade luck, not robust |
**Root cause:** 2021–2023 XAUUSD is trend-dominated with high intraday noise; the microstructure structurally resists price-only intraday edges at the required robustness.

## 4. Frequency addendum (§1–§12 of addendum) — moot (no survivor)
No candidate reached validation, so per-strategy / portfolio effective-frequency reporting is N/A. (Diagnostic note: MOM_IGN naturally fired ~10/month — inside the preferred 8–15/month band — but is net-negative, so frequency is irrelevant. Quality-first held; frequency never traded against robustness.)

## 5. Why not promote the least-bad configs (§18, §32, §45)
The nearest-to-breakeven configs (MOM_IGN-SHORT rr2 avgR −0.062 CONF +0.137 but DISC −0.186 / 2022 −0.25; VOL_RESET-LONG rr2 avgR −0.090 scattered) all **fail the promotion gate (§40)** — negative expectancy, best-10%-removed negative, DISC↔CONF inconsistent, single-year positives. Promoting any would be the exact overfit the CEO's §45 hard stop forbids. **Sample honesty (§18) and top-trade-removal (§32) are held absolutely.**

## 6. Artifacts (§50) — complete, no hidden selection
`loop_discovery.py` (FAILED_REV / HTF_REACT / SESSION_ACC + the 3-mechanism extension), building on `hp_portfolio.py`, `trend_cont.py`, and the full prior discovery lineage. Config: H1/H4 `regime` context, natural structural stops (20–160p filter), RR {1,1.5,2}, HOR 48 M15, STRESS 2.4p, entry next-M15-open, dedup 4 bars (one opportunity per event — no re-entry spam per addendum §5).

## 7. CEO recommendation
1. **`SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA` — no new robust strategy found after S5.** A genuine autonomous, failure-mode-driven loop across 6 new families this run + the whole prior program finds **no price-only mechanism** that survives the full internal pipeline (DISC→CONF, multi-year, best-10%-removal, adequate N) at any profile. This is the honest, anti-overfit outcome the mandate explicitly authorized (§45/§52), **not** a fabricated result.
2. **What the failures teach (actionable for the CEO's next decision):** (a) the desired **70–80% WR at 1:1 is structurally unattainable** on 2021–2023 gold; (b) the only edges the program ever found (frozen `HR-TU-pb-L` / `MT-H4-dispaccept-L`, RR 1.5–3, ~50% WR) are **low-WR/high-payoff LONG trend-beta**, regime-dependent and already frozen — the achievable profile, not the desired one; (c) further price-only intraday mechanism search on this DEV window is unlikely to be productive.
3. **Genuinely different directions that would require CEO authorization (out of this mandate's firewall):** a different/genuinely range-bound evidence population; higher-timeframe (swing) horizons where noise is a smaller fraction of the stop; or the exogenous-data frontier (macro/DXY/yields) that the program has repeatedly identified as the likely true driver of gold — all explicitly outside price-only DEV scope.
4. **No fabrication; standards held. No MI/S5 change; no promotion; no AI Trader; broker disabled; DEV-only.** All 9 frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`; S5 remains the sole validated strategy.

**Terminal status:** `AUTONOMOUS_ALPHA_LOOP_COMPLETE` · `SEARCH_SPACE_EXHAUSTED_WITHOUT_ROBUST_ALPHA` · `NO_NEW_STRATEGY_READY_FOR_VALIDATION`. **STOP.**
