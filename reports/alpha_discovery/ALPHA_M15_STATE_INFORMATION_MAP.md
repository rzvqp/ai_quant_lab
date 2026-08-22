# ALPHA_M15_STATE_INFORMATION_MAP

Mandate `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001`. Univariate M15 state -> P(+70/-50) 8h lift, event-deduped, LONG/SHORT separate, with per-year + DISC/CONF + cross-era (b0/b1) stability from the outset (`state_m15_discover.py`). Base (event-deduped): DEV L 0.276/S 0.265; b0 L 0.28/S 0.31; b1 L 0.17/S 0.18.

## CROSS-ERA-STABLE signals (same-sign across 2021/2022/2023 + b0 + b1, DISC+CONF, |lift|>=0.04) — FIRST in the program
| state | side | DEV lift | per-year | b0 / b1 | reading |
|---|---|---|---|---|---|
| **vol_hi (ATR>1.3x)** | **S** | **+0.058** (EffN 1615) | .06/.06/.06 | +0.051 / +0.043 | **high vol -> M15 SHORT bias (directional: vol_hi LONG NOT flagged, <0.04)** |
| vc_rise (>1.2) | S | +0.050 (EffN 2187) | .05/.03/.06 | +0.048 / +0.033 | rising vol -> SHORT bias |
| vol_lo (<0.8) | S | -0.084 | -.08/-.09/-.08 | -0.075 / -0.057 | quiet -> SHORT targets unreached (avoid) |
| vol_lo (<0.8) | L | -0.059 | -.05/-.07/-.06 | -0.045 / -0.047 | quiet -> LONG targets unreached (avoid) |
| vc_fall (<0.85) | S | -0.060 | | -0.045 / -0.040 | falling vol -> avoid short |
| compress | S | -0.064 | | -0.044 / -0.041 | compression -> avoid short |

## Interpretation
**Volatility state is the M15 information that is cross-era-stable** (the FIRST such signal across the whole H1+M15 program). The economically meaningful, directional one: **high/rising volatility -> the M15 forward path is biased DOWN** (vol_hi lifts SHORT +0.058 but NOT LONG) — consistent with gold down-moves being faster than rallies in high-vol/risk-off. Stable across every year AND both historical eras. The other vol signals are symmetric "quiet -> nothing moves" avoidance filters.

## Tradeability status (HONEST — not yet a strategy)
The lift is STABLE but MODEST: high-vol SHORT P(+70/-50)=0.32, still below the 0.417 breakeven for that 1.4:1 label. **Stable INFORMATION, tradeability TBD.** NEXT: characterize high-vol/rising-vol SHORT expectancy across RR/targets (find the geometry where it is net-positive after STRESS cost, §18-19), event-deduped effective-N/opportunities, same-regime recurrence, overlap vs frozen; only then Stage-C. If no RR yields material positive expectancy, record as STABLE_INFO_NOT_TRADEABLE and continue (M15 transitions + H1/H4 conditioning may sharpen it).

## Tradeability of ST-M15-HIGHVOL-SHORT (`state_m15_highvol.py`, STRESS, event-deduped)
**Univariate = NOT tradeable.** No fixed bracket or structural ATR stop is net-positive cross-era:
- DEV: all avgR negative (best +70/-50 -0.017; struct best -0.042). b0: marginally positive (+70/-50 +0.030). b1: all negative (-0.035..-0.21).
- The stable +0.058 P(+70/-50) lift raises P to 0.32 -> still below breakeven; expectancy stays <=0. `STABLE_INFO_NOT_TRADEABLE` at the univariate level.
**LEAD — parent-regime conditioning:** high-vol-short conditioned on the causal H1 **DOWN** parent regime is POSITIVE on DEV (struct 1.5ATR rr1.5): **avgR +0.102, WR 0.48, N=239** (best10 -0.048 slightly tail-carried). UP -0.027 / QUIET -0.167 / CHOP -0.090 / TRANSITION -0.091 all negative; raw down-displacement interaction -0.037 (doesn't help). Economically: high volatility CONFIRMS an existing downtrend. `ST-M15-HIGHVOL-SHORT-DOWNPARENT` = LEAD, cross-era TBD (same-regime DOWN-parent high-vol-short on b0/b1 — decisive; note H1 DOWN shorts were era-unstable, and b1 has little DOWN regime -> possible INSUFFICIENT_SAME_REGIME_EVIDENCE).
