# ALPHA_CURRENT_REGIME_RESCREEN_LEDGER — Phase 3/4 (first pass)

Mandate `ALPHA-XAUUSD-CURRENT-REGIME-SPECIALIST-DISCOVERY-001`. Re-screen of eligible candidates on `CURRENT_LIKE_POPULATION_V1` (frozen, fp c8f5a809), exact frozen defs (§8 no retuning), STRESS cost, time-partitioned DISC(≤2021)/CONF(2022-24)/OOS(2025-26). Non-current-like periods = DIAGNOSTIC only (§4). Harness `cur_screen.py`. Old cross-era verdicts remain historically valid.

## Key structural finding — the current regime is HARD for known edges
The current market = **high-vol DOWN-correction after a blowoff top** ($5288→$4085). Re-screen on current-like:
- **S5 (ORB_NY_L)** is essentially FLAT in the current regime (current-like DISC +0.003 / CONF −0.037 / OOS +0.062 ≈ 0) but strong on non-current-like/trending periods (DIAG **+0.072**). **S5's opening-range-breakout-long does not work in high-vol corrections** — it is naturally OFF now. A current-regime specialist must be a different mechanism.
- **Mean-reversion (MR_ext 2σ)**: catastrophically negative even on current-like (DISC −0.83 / CONF −0.54). The high-vol correction is NOT a clean reversion regime — fading gets run over.
- **RANGE_fade**: negative on current-like (−0.17/−0.14).

## Buckets
### A. CURRENT_REGIME_SURVIVOR
- **None clean** in the first pass.

### B. CURRENT_REGIME_NEAR_MISS
- **SB_break_S (Donchian breakdown short), rr3**: current-like DISC −0.038 / CONF **+0.067** / OOS **+0.123**. Positive in RECENT current-like corrections (2022-2026) but negative in OLDER (2011-2021). Down-correction-short edge is real recently; not robust across the full frozen current-like.
- **DISP_dn_S (displacement-down short), rr3**: DISC −0.064 / CONF +0.096 / OOS +0.051. Same pattern.
- Interpretation: the 2022-2026 corrections are a cleaner-down sub-type; the 2011-2015 high-vol episodes (different gold microstructure) drag DISC negative. The current-like population may be too broad (mixes structurally distinct high-vol episodes).

### C. CURRENT_REGIME_NEGATIVE / not-a-specialist
- S5 (off in regime; universal anchor, untouched), MR_ext_L/S, RANGE_fade_L/S, NYpm_disp_L (recent-only 2025-26 +, older negative), NYpm_comp_L (negative), REJECT_newhigh_S (flat ~0, OOS-negative), REJECT_newlow_L (negative).

## Honest verdict (first pass)
No clean CURRENT_REGIME_SURVIVOR yet. The lead is **short-continuation aligned with the down-correction**, which is positive in the *recent* current-like (2022-2026) but not the older current-like. This suggests the current market is a MORE SPECIFIC regime (recent high-vol post-blowoff down-correction) than the broad "high-vol + drawdown" signature captures. Next (Phase 4, continuing): investigate whether a tighter current-like sub-population (or an added down-trend descriptor) makes short-continuation robust across multiple independent occurrences — without P&L-fitting the signature (§8) — and continue new current-regime discovery on the down-correction structure. S5 remains untouched; it is the universal anchor that is simply OFF in this regime.

## Phase 4 continuation (short-rally + assessment)
- **SHORT_RALLY (fade bounce to EMA20/50 in down-context)**: NEGATIVE on current-like (DISC -0.32/-0.28, CONF -0.20/-0.16), only OOS 25-26 flat/+. Fading the high-vol counter-trend bounce gets run over. Not a specialist.
- **Consistent diagnostic across ALL short tests**: older current-like (2011-2021) behaves WORSE than recent current-like (2022-2026). Short-breakdown is +CONF/+OOS but -DISC; short-rally -DISC/-CONF/+OOS. This is strong evidence that SIGNATURE_V1 (5 coarse descriptors) POOLS structurally-distinct high-vol episodes (2011-2015 gold vs the current post-parabolic $4000+ correction).

## First-pass current-regime conclusion
The current market (high-vol post-blowoff DOWN-correction) is a HARD regime: no simple mechanism has robust edge across the full frozen current-like population. S5 (breakout-long) is naturally OFF; reversion/fade negative; short-rally negative; short-breakdown is a recent-current-like edge (2022+) but not full-current-like-robust. **Best lead: down-correction SHORT-BREAKDOWN (SB_break_S rr3)**, positive across the 2 recent independent current-like corrections (2022 +0.067, 2025-26 +0.123).
**Next step (legitimate, mechanical, NOT P&L-fit):** SIGNATURE_V2 — refine the current-like definition to distinguish the recent post-parabolic high-price correction from older high-vol episodes (e.g., add an absolute-price-regime or prior-parabolic-run descriptor), re-freeze, and re-screen. Then continue Phase 4 discovery on the tightened current-like. Forward MT5 DEMO remains the true validation for any current-regime specialist (rebase addendum). S5/frozen objects untouched.

## CORRECTION — SIGNATURE_V2 NOT pursued (§8 integrity)
My earlier "SIGNATURE_V2 next step" is WITHDRAWN: refining the frozen signature AFTER seeing that short-breakdown works recently-but-not-older would be a P&L-DRIVEN post-hoc rescue (forbidden §8/§5, signature must be frozen before P&L). SIGNATURE_V1 stays frozen. No signature tuning to make a candidate pass.

## Phase 4b — aligned-SHORT structural events on FROZEN current-like (cur_p5.py; no rescue)
- **ORB_NY_S (S5 short mirror) rr3/rr2**: current-like -0.074 (DISC -0.138, CONF -0.034, OOS +0.166). Recent-only, not robust.
- **ORB_LON_S rr2**: +0.118 (DISC +0.143, CONF -0.051, OOS +0.235) — DISC+OOS positive but CONF NEGATIVE = inconsistent across partitions.
- **ORB_NY_S_wide rr3**: negative.

## COMPREHENSIVE FIRST-PASS CONCLUSION (current-regime)
Across the full first pass (breakout L/S, reversion, fade, short-rally, short-breakdown, opening-range L/S, displacement L/S), **NO mechanism is robust across all current-like partitions (DISC+CONF+OOS all positive)** on the frozen CURRENT_LIKE_POPULATION_V1. Every candidate has >=1 current-like partition negative. **The current high-vol post-blowoff DOWN-correction is a genuinely HARD regime with no robust directional specialist.**
- This is the §12 causal OFF-switch working as DESIGNED: the frozen signature identifies a regime where the portfolio should be LIGHT/OFF. S5 is naturally off (its edge is trending regimes) and RE-ACTIVATES on transition back to a trending signature.
- Best (non-qualifying) lead remains down-correction SHORT-BREAKDOWN, positive only in recent current-like (2022+) — a candidate for FORWARD MT5 DEMO observation (not a frozen survivor).
- **CURRENT_REGIME_SURVIVOR bucket: empty (first pass).** Honest, decision-relevant: in the current market the right posture is reduced exposure / await regime transition, not force a specialist. Discovery continues (new mechanism classes) but the hard-regime finding stands as the first-pass result.

## Data freshness check (CEO reactivation) — freshest authorized = 2026-07-27
Mechanically scanned all authorized sources: freshest XAUUSD = 2026-07-27 (OANDA canonical M15/M5, identical across wp5b/data-acq/alpha-automation). TradingView Desktop NOT installed (tv_launch failed) -> cannot pull live current bars. Static CSVs have no self-refresh. Data past 2026-07-27 requires the external data-acquisition pipeline (not autonomously triggerable). DISCLOSED: current-regime work rests on data through 2026-07-27 (~4wk stale); not claimed as today's tape. Proceeding on freshest authorized data (4wk minor for a structural regime); data-acquisition dependency noted as governance item, NOT a stop.

## Information-first structural asymmetry (cur_info.py / cur_info2.py) — GENUINE regime-specific finding
- **The current-like regime has a ROBUST DOWN-bias**: P(down 1.5ATR before up 1.5ATR) = 0.516/0.535/0.515 across DISC/CONF/OOS (all >0.5); non-current-like (trending) = 0.499 (symmetric). **First robust regime-specific directional asymmetry in the whole campaign** — the universal cross-era search never found a stable directional bias; the current-regime lens does. Validates the CEO approach.
- **But UNCONCENTRABLE**: no causal state robustly lifts it to a tradeable level across all current-like partitions. at-resistance concentrates DISC/CONF (0.559/0.542) but FLIPS up in OOS 25-26 (0.439); down-context near-symmetric; vol-expansion uniform mild (~0.533, immaterial). The down-bias (~52%) is ~breakeven at 1:1 after cost and cannot be concentrated robustly.
- **Refined current-regime conclusion**: the regime has a genuine mild down-foundation but no robustly-tradeable directional specialist. Consistent with the strategy screens. §12 posture: light/off. Alpha research continues (distinct mechanism classes), but the hard-regime result is now confirmed at the information level.

## Payoff-asymmetry short candidate — REJECTED by skepticism gate (7th false positive)
Info-first found a REAL current-like payoff asymmetry (forward down-excursion > up-excursion, down-up = +0.55/+0.67/+0.23 ATR DISC/CONF/OOS, sign-robust; frequency P(down first) ~52%). Tradeable form: wide-stop (4 ATR, survive bounces) time-exit SHORT (`cur_p6/p7.py`). First-pass screen looked like a SURVIVOR (current-like DISC +0.061/CONF +0.078/OOS +0.274; non-cur -0.043 = proper OFF-switch).
**Skepticism gate (`cur_verify.py`) REJECTS it:**
- TAIL-DEPENDENT: best-10%-removed = **-0.226** (edge carried by a few big crash-shorts; PF 1.16, WR 0.39). Fails the test S5 passed.
- EPISODE-CONCENTRATED: positive ONLY in actual crash episodes (2011 +0.41, 2013 +0.20, 2022 +0.26, 2026 +0.62); NEGATIVE in high-vol-non-crash current-like years (2023 -0.17, 2024 -0.19, 2025 -0.42). OOS +0.274 was entirely 2026; 2025 was -0.42.
- The frozen signature (high-vol+drawdown) is a NOISY proxy for "actually crashing"; refining it to select crash-episodes AFTER seeing this P&L would be the §8 post-hoc rescue I refuse.
**Verdict: NO robust current-regime survivor.** The down-asymmetry is real (info) but its tradeable form is a crash-momentum bet, not a robust regime specialist. Survivor bucket stays empty. Skepticism gate has now caught 7 false positives across the campaign (S10, S4, +5). Alpha continues (distinct mechanisms) but the honest current-regime result: no robust specialist; §12 posture light/off; portfolio-short works only when the market is actually crashing (a directional-timing bet, not a robust edge).

## CONFIRMED_DOWNTREND short (distinct regime hypothesis, R4-principled) — also NEGATIVE
Tested "short in a confirmed 20-day downtrend (close<20dMA & MA declining)", wide 4ATR rr3 H96 (`cur_p8.py`). NEGATIVE overall (avgR -0.067, PF 0.89, best-10%-removed -0.402). Per-episode deteriorating (<=2016 +0.031, 2017-2022 -0.121, 2023+ -0.205); worst 2024 -0.51 / 2025 -0.43. A "20-day MA declining" is mostly a PULLBACK within gold's secular uptrend (bought, not crashed) -> shorting it loses. Confirms the short edge is confined to ACTUAL crash episodes and is not isolable by a causal downtrend definition.

## DEFINITIVE current-regime first-pass conclusion
Comprehensive investigation at every level -- strategy re-screen (breakout L/S, reversion, fade, short-rally, short-breakdown, opening-range L/S, displacement), information-first frequency asymmetry (down-bias ~52% robust but unconcentrable), payoff asymmetry (down-excursion bigger, sign-robust), wide-stop path-surviving short, confirmed-downtrend short -- plus the skepticism gate:
**NO ROBUST CURRENT-REGIME SURVIVOR.** The current high-vol post-blowoff DOWN-correction has a genuine but SMALL down-asymmetry whose only tradeable expression is a CRASH-MOMENTUM bet: tail-carried (best-10%-removed negative), episode-concentrated (only actual crashes profitable), unisolable by any causal regime definition without forbidden P&L-fitting.
- **CURRENT_REGIME_SURVIVOR bucket: EMPTY (definitive).** §12 posture: light/off exposure in the current regime; S5 reactivates on transition to a trending signature.
- **Genuine positive knowledge produced:** the current-regime LENS found the FIRST robust regime-specific directional asymmetry of the whole campaign (down-bias + down-payoff in high-vol corrections) that the universal search never found -- validating the CEO approach -- even though it is not robustly tradeable after cost + path + tail.
- Skepticism gate has caught 7 false positives total (S10, S4, + 5 in continuous/current-regime). Process integrity intact; S5/frozen objects untouched; SIGNATURE_V1 not P&L-tuned.
