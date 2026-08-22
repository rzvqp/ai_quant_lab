# ALPHA_XAUUSD_AUTONOMOUS_HIGH_WR_PORTFOLIO_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-AUTONOMOUS-HIGH-WR-PORTFOLIO-DISCOVERY-001` (+ architecture addendum) · **Date:** 2026-08-22.
**Terminal status:** `AUTONOMOUS_HIGH_WR_ALPHA_DISCOVERY_COMPLETE` · **`HIGH_WR_STRATEGY_SIGNALS_WEAK`** · `NO_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION`. **N_SURVIVORS = 0.**
**Scope:** autonomous portfolio search for the desired profile ~70–80% WR / ~1:1 RR / ~70–100p natural SL/TP. Price-only XAUUSD; native-M5→M15/H1/H4; DEV-only; no CALIB/2024/2025+/N4/V1; no MI/S5 change; no AI Trader/execution. Profile is a goal, not a forced filter. **Did not force 5 (§45).** No promotion; broker disabled.

---

## 0. Headline
- **The desired 70–80% WR at ~1:1 does NOT exist on XAUUSD 2021–2023 for price-only trend-continuation.** Across 5 mechanisms × LONG/SHORT × {H1-only, H4+H1-aligned} × {full-TP, horizon}, **no mechanism reaches even 65% WR at 1:1** (range 0.31–0.605), and expectancy is positive only in 2022-concentrated shorts.
- **Structural reason:** at a *natural* ~70p structural stop, gold's intraday noise makes the **+1R-before-−1R race ≈ 50/50** — so a 1:1 geometry caps WR near 50–60% and cannot deliver the high-WR profile. High WR at 1:1 would require a directional edge the price context does not provide at that stop distance.
- **One weak, regime-specific lead** (not promoted): `DISP_ACCEPT-SHORT` (H4+H1-aligned down, displacement+acceptance, H1 stop, 1:1, horizon exit) — WR 0.605, net-STRESS avgR +0.159, best-10%-removed +0.089, PF 1.45, but **N=38, 2022-dominated (+0.954), weak CONF (+0.051)/2023 (+0.049)** → regime-specific, below the WR zone, not validation-ready.
- **Zero candidates ready for independent validation.** Scientific standards were not lowered to fill the portfolio count (§45).

## 1. Evidence firewall + architecture (§8, §9, addendum)
Price-only. Native gated M5 → causal M15/H1/H4 (`m5_data.py`). DEV 2021-07-27→2023-12-29. **H4/H1 = trend context (`regime`), M15 = setup, M5 = optional entry (must earn value, addendum §1).** Per addendum §2, **structural invalidation owns the stop, preferring NATURAL ~70–100p setups** — the risk filter admits only 30–150p natural H1-structural stops (median ~50–75p), never forcing a wide thesis into a tight stop nor a tight one into 80p.

## 2. Prior graveyard review (§6, §7)
Incorporated: RANGE mean-reversion, research-local RANGE M15/M5, London-PLH, PDH, liquidity-sweep/trap, post-E1 clean-path — all closed/weak. The immediately-prior `d2c6577` returned a WEAK trend-continuation lead (`TREND-CONT-SHORT-PB-BREAK-H1STOP`). **Per addendum §4 this lead was NOT rescued, parameter-mined, or used as a template** — `TP_BREAK` appears only as one of five independent fresh mechanisms and again fails (below).

## 3. Hypothesis queue + mechanisms tested (§14, §15, addendum §3)
Five materially-distinct high-confidence trend/continuation mechanisms, all causal, targeting the CEO's preferred "uncertainty-reduced + reward-remaining" states:
| id | mechanism | falsifier |
|---|---|---|
| TP_PB | trend pullback (dip past ema20 → reclaim) | reclaim doesn't continue |
| TP_BREAK | shallow pullback → consolidation-extreme break | false break |
| FAILED_CT | failed countertrend extreme → reclaim | reclaim reverses |
| BREAK_1STPB | structural displacement break → first pullback holds | pullback fails |
| DISP_ACCEPT | displacement → 2nd-close acceptance | acceptance rejected |
Each × LONG/SHORT, 1:1 (H1 stop, TP=1R), net STRESS, DISC/CONF (cut 2023-05-03), year. Event ownership: dedup within 4 bars (§34/§35).

## 4. Phase results (§16 funnel) — no survivor at 1:1
**H1-context, 1:1 (best cells shown):**
| mech-side | N | WR | avgR | PF | maxDD | best-10%-rem | medSL | DISC | CONF | 2021/22/23 |
|---|---|---|---|---|---|---|---|---|---|---|
| DISP_ACCEPT-SHORT | 109 | 0.51 | −0.011 | 0.98 | 14.0 | −0.111 | 63 | +0.155 | −0.162 | +0.10/+0.63/−0.15 |
| TP_PB-LONG | 195 | 0.47 | −0.115 | 0.79 | 26.3 | −0.233 | 49 | −0.156 | −0.030 | −0.27/+0.10/−0.10 |
| FAILED_CT-LONG | 122 | 0.43 | −0.194 | 0.68 | 28.6 | −0.321 | 54 | −0.291 | +0.005 | −0.48/−0.41/−0.02 |
| *(all others)* | | 0.31–0.42 | −0.19 to −0.42 | <0.7 | | negative | | negative | | mostly negative |
**H4+H1-aligned, 1:1:** FAILED_CT-SHORT WR 0.60 avgR +0.154 but **DISC −0.154, 2021 −0.378, N=20** (2022-dominated +0.961); DISP_ACCEPT-SHORT WR 0.47 avgR −0.092 (CONF −0.203, 2023 −0.228). **No cell clears the survivor gate** (WR≥0.55 ∧ avgR>0 ∧ DISC>0 ∧ CONF>0 ∧ best-10%-rem>0 ∧ all-years>0).

## 5. The one weak lead (§54) — DISP_ACCEPT-SHORT aligned + horizon exit
The only positive-all-years, both-splits-positive config (with a predeclared horizon exit, §25):
| metric | value |
|---|---|
| context / mechanism | H4+H1 aligned DOWN → M15 displacement + acceptance → SHORT |
| geometry | H1-structural stop (median ~63p), TP=1R, horizon exit (48 M15) |
| N / unique days / trades-per-month | **38 / 23 / ~1.3** |
| WR / avgR (net STRESS) / PF | 0.605 / **+0.159** / 1.45 |
| best-5%-rem / best-10%-rem / top-10% share | +0.137 / **+0.089** / 0.49 |
| maxDD / worst trade | 4.82R / −1.07R |
| DISC / CONF | +0.639 / **+0.051** |
| 2021 / 2022 / 2023 | +0.641 / **+0.954** / +0.049 |
**Passes best-trade-removal, DD, PF — but fails the §44 candidate bar:** N=38 (small, §29), CONF weak (+0.051 ≪ DISC +0.639, magnitude-inconsistent), and **profitability is 2022-dominated** → per §31 **classified regime-specific (bearish/volatile) and NOT promoted.** WR 0.60 is below even the CEO's fallback 65–69% zone.

## 6. Economic geometry + path + WR ceiling (§12, §13, §18) — why high-WR-1:1 is unattainable
Natural structural risk clusters at 44–75p (in/below the 70–100p zone); at 1:1 the target sits an equal distance away. **Measured WR ceiling ≈ 0.50–0.60**, because gold routinely makes a ~70p adverse excursion before a ~70p favorable one from trend-continuation entries. At 1:1, breakeven WR (post-cost) ≈ 0.53; the mechanisms land 0.31–0.605, so most are negative and none reaches the desired 0.70–0.80. **The high-WR profile requires either a closer target (RR<1, off-profile) or a mean-reversion extreme (graveyard) — neither is the 1:1 trend-continuation the mandate seeks.**

## 7. M5 value-add (§21, §22, addendum §1)
Not advanced: no M15 parent survived the H1→M15 stage, so M5 was correctly **not** added (addendum §1 — M5 must earn its place; prior mandate `d2c6577` already showed M5 confirmation reduces these continuation parents). H1→M15 alone was the tested architecture.

## 8. Strategy correlation + S5 overlap (§40, §41)
With zero validation-ready candidates, no pairwise portfolio matrix applies. The weak lead (DISP_ACCEPT-SHORT, a downtrend displacement-acceptance short) is mechanistically distinct from **S5** (an opening-range/session breakout, both directions) → low conceptual overlap — but moot, as it is not promoted.

## 9. Candidate registry / graveyard (§28, §52) — complete, no hidden
~10 core hypotheses (5 mechanisms × LONG/SHORT) × context/exit variants (well within the 40 budget). **Graveyard (all fail the candidate bar):** every TP_PB, TP_BREAK, BREAK_1STPB, DISP_ACCEPT-LONG, FAILED_CT (both) at 1:1; the aligned FAILED_CT-SHORT (N=20, DISC-negative, 2022-only). **Weak lead (not promoted):** DISP_ACCEPT-SHORT aligned+horizon (regime-specific). Artifact: `hp_portfolio.py` (config: H1/H4 `regime` context, M15 mechanisms, H1-swing stop 30–150p, TP=1R, HOR 48, STRESS 2.4p, entry next-M15-open).

## 10. Autonomous pivots + stopping (§47)
Pivots taken: (1) five mechanisms at 1:1 H1-context → all sub-55% WR, negative; (2) H4+H1-aligned strong context → WR lifts to ≤0.60 but only 2022-concentrated shorts turn positive; (3) horizon-exit variant → surfaces the single weak regime-specific lead. **Stopping condition §47.D reached:** the evidence demonstrates further search along price-only trend-continuation is unproductive for the high-WR-1:1 profile — the WR ceiling (~0.50–0.60) is structural, not mechanism-specific. Reasonable trend-continuation mechanism space substantially explored (§47.C); budget far from exhausted but continuing would not change the structural ceiling.

## 11. Limitations
- Bounded to price-only trend-continuation mechanisms on 2021–2023 DEV. The WR ceiling is regime-driven (trend-dominated gold with high intraday noise). A genuinely range-bound population, or a different (non-1:1) profile, could differ — but both are outside this mandate's stated goal.
- The weak lead is small-N (38) and 2022-concentrated; it should be read as a *regime-specific* observation, not an edge.

## 12. CEO recommendation
1. **`HIGH_WR_STRATEGY_SIGNALS_WEAK` / `NO_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION` (N_SURVIVORS=0).** A genuine autonomous search finds **no strategy at the desired 70–80% WR / ~1:1 profile** on XAUUSD 2021–2023. The barrier is structural: at a natural ~70p stop, gold's noise caps the 1:1 win rate near 50–60%.
2. **One weak, regime-specific lead** (DISP_ACCEPT-SHORT, H4+H1-aligned, horizon exit) exists — positive net-STRESS (+0.159), best-trade-removal-robust, but N=38 and 2022-dominated → **not promoted, not forwarded to validation** (§31/§45).
3. **Actionable structural conclusions for the program:** (a) the high-WR-1:1 objective is likely unreachable for price-only XAUUSD trend-continuation — the profile that *has* shown life across the program is **low-WR/high-payoff trend-continuation** (RR 1.5–3, the frozen `HR-TU-pb-L`/`MT-H4-dispaccept-L` family), not high-WR-1:1; (b) if the CEO wants high WR, it would require accepting RR<1 (a different profile) or a validated mean-reversion context (currently graveyard). **The desired profile does not fit gold's 2021–2023 microstructure.**
4. **Did not force 5; standards held.** No MI/S5 change; no M5 promotion; no AI Trader; broker disabled; DEV-only. All 9 frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal status:** `AUTONOMOUS_HIGH_WR_ALPHA_DISCOVERY_COMPLETE` · `HIGH_WR_STRATEGY_SIGNALS_WEAK` · `NO_CANDIDATE_READY_FOR_INDEPENDENT_VALIDATION` · **N_SURVIVORS = 0.** **STOP.**
