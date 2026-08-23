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
