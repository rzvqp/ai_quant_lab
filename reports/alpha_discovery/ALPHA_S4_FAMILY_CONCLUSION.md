# ALPHA_S4_VOLATILITY_COMPRESSION_EXPANSION_CONCLUSION — CEO NEXT-FAMILY SELECTION REQUESTED

**Mandate:** `ALPHA-XAUUSD-S4-VOLATILITY-COMPRESSION-EXPANSION-001`. Bounded-complete under frozen MARKET_OPERATING_MODE_V1. Price-only, causal, event-deduped, cross-era within mode, structural stops, STRESS cost, strict execution realism, adversarial skepticism gate. Frozen objects untouched.

## §3 historical audit
Prior compression/expansion work (M15 path-shape HH_LL/LH_HL) = NO_MODE_CONDITIONING / NOT_COMPARABLE (bilateral, not mode-conditioned, no payoff characterization). Current S4 test now SUFFICIENTLY_FALSIFIED under the current architecture.

## What was tested (checkpoints #50-#52)
1. **§8 decomposition + §9 bilateral-vs-directional + §14 payoff** (#50): mechanical compression (range-box <0.7*box_ma + vr<0.9) -> directional expansion (break of envelope w/ range>1.3 ATR), per mode, BOTH long & short lift + MFE/MAE. **No stable directional alpha** — directional resolution FLIPS cross-era (PRIMARY_BULL EXP_UP directional-short b0 / directional-long b1); lifts small/weak. **§14 payoff rationale FALSIFIED** — MFE med ~= MAE med (ratio ~0.85-1.0); NO larger/better natural payoff (buying after a big expansion bar -> adverse excursion = favorable). Prior bilateral-vol finding partly holds.
2. **HOLD/FAIL + tradeability** (#51): HOLD/FAIL discriminator TRANSFERS (HOLD>FAIL, R6 confirmed). PRIMARY continuation cells SIGN-REVERSE across eras (era-trend leakage, fail §15). Correction-resumption cells (C3 BULL_CORR->L, C4 BEAR_CORR->S) positive both dense eras -> flagged for adversarial verification.
3. **Adversarial verification** (#52, §26/§28): C3/C4 with neighbor-stability + DISC/CONF + session + cross-era. **FATAL:** both are ~65-77% **ASIA-SESSION concentrated** (compression fires in the quiet Asia session -> the "edge" is a session/liquidity artifact, §24). **C4 sign-REVERSES in y2123** (avgR -0.19, DISC -0.44) -> fails §15. C3 survives the sign test + neighbor-stable but is Asia-confounded and its y2123 CONF half is negative. Neither is a clean, non-artifact S4 specialist.

## Conclusion
**S4 VOLATILITY COMPRESSION -> EXPANSION produces NO robust non-artifact specialist. BOUNDED_NEGATIVE, 0 survivors.**
- **VOLATILITY_INFORMATION vs DIRECTIONAL_ALPHA:** compression->expansion is bilateral / VOLATILITY_TIMING at the info level; mode-conditioning does NOT convert it to stable directional alpha (primary cells sign-reverse = era-trend leakage).
- **Natural payoff (§14) FALSIFIED:** MFE med ~= MAE med -> the payoff-advantage rationale for opening S4 does not hold.
- **Apparent correction-resumption edge is a SESSION ARTIFACT** (~70% Asia), not compression alpha (§24); C4 also era-reverses. Caught by the §26/§28 skepticism gate (as with the S10 false positive).

## Discovery Radar
- R9: compression->expansion no stable directional alpha + no payoff advantage (MFE~=MAE).
- R10: HOLD/FAIL discriminator transfers; primary continuation cells sign-reverse cross-era (era-trend leakage).
- R11: S4 correction-resumption candidates ~70% ASIA-session concentrated -> the compression edge is largely a time-of-day/liquidity artifact; C4 era-reverses. **-> ASIA-session compression/low-vol is a genuine lead for S18 (Time-of-Day).**

## §30 End-of-family output
- Verdict: BOUNDED_NEGATIVE, 0 survivors. Volatility info = bilateral/timing, not directional. Mode-specific: no mode yields a clean directional edge; correction cells are session artifacts.
- Effective portfolio opportunities added: 0.
- Historical reclassification: S4 compression->expansion SUFFICIENTLY_FALSIFIED (current architecture).
- Frequency/independence: moot (no survivor).

## Meta-pattern across S1/S10/S2/S4 (all BOUNDED_NEGATIVE)
Price-shape continuation, reversal, AND volatility-regime mechanisms all fail to yield a robust cross-era tradeable specialist under the mode architecture: real INFORMATION (displacement, HOLD/FAIL, vol-structure) but sub-breakeven expectancy after cost, OR apparent edges that are era-trend-leakage / session artifacts. The frozen S5 + COMP-CONT-L remain the only robust price-only edges.

## CEO DECISION REQUESTED — next structural family
The strongest NEW lead is R11: **compression/low-vol clusters in the Asia session and that is where the apparent edge lived.** This points directly to:
- **S18 Time-of-Day Edge (recommended):** external session/calendar structure (a fundamentally different information class than price-shape/vol-regime). Prior findings (NY-open bilateral burst, London range-expansion, Asia compression) suggest session structure carries real information; test it directly and honestly (not retrofitted).
- **S16 Previous-Day Levels / S17 Weekly Levels:** external reference levels (also non-price-shape).
- **S8 Mean Reversion:** the one major behavioral class untested under modes (NEUTRAL_ROTATION mode is the natural home).

**Recommendation: S18 Time-of-Day Edge** — directly motivated by R11, and a genuinely different information class after four price-shape/vol families all hit the same wall. Awaiting CEO selection.
