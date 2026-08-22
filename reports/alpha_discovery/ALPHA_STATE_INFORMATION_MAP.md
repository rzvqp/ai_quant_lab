# ALPHA_STATE_INFORMATION_MAP

Stage-A univariate state->future-path information (mandate `ALPHA-XAUUSD-CAUSAL-STATE-PATH-DISCOVERY-001`). Method: for each CAUSAL price-state variable, decile response of the headline outcome `P(+100 before -70)` vs base rate, LONG/SHORT separate, DEV 2021-2023 H1 (N=10,168). Raw price-state features only (NOT the untrusted canonical RANGE/N1-N6). Continuous-first (§6), no thresholds mined. NOT yet DISC/CONF-validated -> promising != confirmed.

## Headline univariate lift (H=48h, base LONG 0.418 / SHORT 0.391) — ranked by decile spread
| var | LONG bot->top (spread, mono) | SHORT bot->top (spread, mono) | reading |
|---|---|---|---|
| **trend** (EMA20-EMA50)/ATR | 0.428->0.313 (0.19, -0.43) | 0.380->0.472 (0.115, +0.50) | **strongest+coherent**: extension-up = exhaustion -> hurts new LONG, favors SHORT (+0.081 abs SHORT lift) |
| vol_ratio ATR/ATR_ma | 0.389->0.447 (0.062,+0.63) | 0.450->0.348 (0.102,-0.79) | high vol favors LONG-continuation, disfavors SHORT (trend-expansion) |
| vol_change ATR/ATR[-12] | 0.405->0.428 (0.082,+0.60) | 0.433->0.374 (0.083,-0.85) | rising vol favors LONG, disfavors SHORT |
| effic (dir efficiency) | 0.412->0.360 (0.10,-0.20) | 0.421->0.378 (0.044,-0.88) | very monotone: strong up-efficiency suppresses SHORT |
| dist_ema (c-EMA20)/ATR | 0.417->0.367 (0.083,-0.53) | 0.426->0.409 (0.066,-0.22) | far-above-anchor hurts LONG (exhaustion, echoes trend) |
| pos_range, hour, impulse6, body_eff, persist | spreads 0.03-0.06 | spreads 0.03-0.09 | weaker; hour has mild session structure |

## Top findings (promising, pre-DISC/CONF)
1. **TREND-EXTENSION is the dominant causal state**: strongly-extended-up (top-decile `trend`) is an EXHAUSTION state — LONG P(+100/-70) drops to 0.313 (-0.105 vs base) and SHORT P rises to 0.472 (+0.081 vs base, +21% rel, monotone). Economically coherent, both horizons, both sides. **This is the highest-information causal state and points to a SHORT diversifier + a LONG-avoidance filter.**
2. **VOLATILITY STATE** (vol_ratio, vol_change) carries directional-continuation information (high/rising vol favors the prevailing up-trend). Candidate interaction: trend-extension x low/falling vol (exhaustion + stalling) may sharpen the SHORT.
3. **EFFICIENCY** monotonically gates SHORT (strong up-efficiency kills shorts) — a natural causal SHORT filter.

## Mandatory next steps (§13/§14) before any candidate
- Per-year + DISC/CONF stability of the trend-extension->SHORT lift (is it 2022-concentrated?).
- Multi-horizon response curve (15m..multi-session) for the top states.
- Small interaction: trend-extension x vol-state / x efficiency (§7, <=3 conditions).
- Cross-population check on b0/b1 where compatible.
Only a state surviving material lift + stability advances to Stage C (strategy). Ranked by INFORMATION, not P&L (§16).

## VALIDATION RESULT — ST-TREND-EXH KILLED (stability firewall, §13/§14)
The dominant univariate signal does NOT survive stability (`state_validate.py`):
- **DISC/CONF:** DISC lift +0.081 -> **CONF lift -0.076** (SHORT information INVERTS out-of-sample). Decisive kill (§14).
- **Per-year (lift over same-year base):** 2021 +0.074, 2022 +0.122, **2023 -0.029**. 2021-22-concentrated, inverts 2023.
- **Cross-population b0/b1:** SHORT lift -0.001 / -0.032 (no generalization). LONG-avoidance side also ~0 cross-pop.
- DEV-wide extended-region lift is small (+0.022); the "0.472" was the extreme top decile only. Interactions (ext x low-vol +0.062, ext x effic<0 +0.071) sharpen the SAME in-sample 2021-22 effect -> inherit the instability.
**Conclusion:** the single most-informative STATIC univariate causal state carries only a 2021-22 regime-transient, NOT stable path information. Method worked (flagged -> validated -> rejected). PIVOT to state TRANSITIONS (§8, next family) and other populations' baselines. This is NOT "price-only impossible" (§26) — the causal-state information space is still being mapped.
