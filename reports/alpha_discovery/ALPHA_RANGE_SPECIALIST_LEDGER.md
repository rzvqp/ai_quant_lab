# RANGE-Regime Specialist Program — Ledger

Mandate: MULTI-REGIME SPECIALIST PORTFOLIO (CEO 2026-08-23). Objective: a validated specialist for a structurally-distinct
XAUUSD regime lacking one, to sit alongside S5 (breakout/trend) and CRS-1 (high-vol correction). CRS-1 frozen & off-limits.

## Regime selection (evidence-driven, cur_regime.py)
Causal H4 taxonomy (trailing-median vol baseline, bounded efficiency — no global percentile). RANGE dominates ~50% of
classified H4 history (RANGE_LOWVOL 19.8% + MIDVOL 21.1% + HIGHVOL 9.7%); trends are minorities. RANGE is the **largest
population, highest opportunity frequency, and the clearest PORTFOLIO GAP** — neither S5 nor CRS-1 covers 'market goes
nowhere'. Low-vol bull (CEO's noted candidate) is smaller and likely redundant with S5's long-breakout edge. => SELECT RANGE.

## FROZEN regime: RANGE_REGIME_V1 (range_regime.py, BEFORE any P&L)
`fp=RANGE_REGIME_V1|H4|Rlow0.15|Nenter6|L12|margin0.25|Eexit0.40|causal-trailing`. Persistent causal state machine: enter
after N_ENTER=6 consecutive |effic|<0.15 H4 bars (box = trailing L=12 extremes); exit on breakout (close beyond box by
0.25×width) or trend ignition (|effic|≥0.40). CAUSAL at every timestamp (bounded efficiency + trailing extremes + shift(1),
no global stat — directly fixes the SIGNATURE_V1 global-percentile dependency flagged on CRS-1). Population: 31.6% of H4 bars
(7569), 350 episodes, median 2.7 days, present every year (2026=45%), box width ~3.5 ATR. Structural params, not P&L-tuned.

## RS-1-fade (re-screen of the old REVERSION/fade candidate, gated to RANGE_REGIME_V1) — FAIL
Natural range play: boundary-rejection fade back to mid, structural stop beyond boundary, 0.5×ATR stop floor, two-sided,
STRESS. Result: avgR **-0.108** gated (short -0.146 / long -0.061, both negative), WR 0.450, best-10%-removed -0.25, DISC
-0.090 / CONF -0.074 / OOS -0.266 (all negative). **The gate does NOT help** — gated (-0.108) is WORSE than ungated (-0.076):
inside a confirmed range, a boundary touch precedes the BREAK more often than a rejection, so fading it loses. Old reversion
verdict stands (negative) even regime-gated with structural stops + floor. No RS-1-fade survivor.

## RS-2 cross-scale range-continuation breakout (rs2_continuation.py) — NEAR-MISS (cross-scale confirmed, too sparse)
Trade the range breakout WITH the causal D1 trend (bull/bear-flag); stop=opposite boundary, target=measured move. Result: ALIGNED avgR +0.088 (PF 1.61, WR 0.571), stable across rr 1/2/3; COUNTER-trend control -0.054 -> D1 alignment MATERIALLY MATTERS (real cross-scale effect, same principle as CRS-1, different regime+mechanism). BUT fails the gate: CONF -0.027 (n26), best-10%-removed -0.015 (borderline), N=112 (sparse, ~7/yr, terminal breakouts only). Not a survivor; not mined. Confirmed lever: D1-alignment is the range regime's directional conditioner.

## RS-3 D1-aligned in-range pullback fade (rs3_pullback.py) — FAIL
Dense in-range population, one-sided by D1 trend (buy flag-dip when D1-up / sell rally when D1-down). Result: ALIGNED avgR -0.078 (both sides neg), best-10%-rm -0.218, DISC -0.101/CONF -0.002/OOS -0.063; COUNTER control -0.138. Aligned beats counter (lever confirmed AGAIN) but still NEGATIVE — the dense in-range fade loses even D1-aligned. Gold ranges don't mean-revert tradeably (boundaries break > reject).

## RANGE-regime program conclusion — NO CLEAN SURVIVOR
Fade (RS-1) FAIL, in-range pullback (RS-3) FAIL, terminal-breakout continuation (RS-2) NEAR-MISS (D1-aligned +0.088 but sparse N=112, CONF-negative). The cross-scale D1-alignment lever is REAL and consistent (aligned > counter across RS-2 & RS-3) but only yields a thin/sparse positive on terminal breakouts, nothing on the dense in-range population. RANGE_REGIME_V1 is a valid, frozen, causal regime with a clear contract but does not admit a robust tradeable specialist among tested mechanisms. Per mandate loop: no survivor is NOT a stop -> SELECT NEXT DISTINCT REGIME.
