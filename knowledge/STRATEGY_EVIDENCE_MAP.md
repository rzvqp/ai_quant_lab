# STRATEGY_EVIDENCE_MAP — family → mechanism → primitive → result (S1–S51)

Traceable chain from each family to its behavioral primitive and observed result. Results are historical /
OOS-exploratory (research 60% / validation 20%; holdout SEALED). "→ result" = the on-disk verdict, NOT validation.

| family | mechanism | primitive | result |
|---|---|---|---|
| S1 | confirmed liquidity sweep | P001 Confirmed Sweep + P010 Liquidity Memory | positive hist / OOS mixed-positive / VALIDATION PENDING |
| S21 | raw liquidity sweep (no confirm) | P011 Raw Sweep | NEGATIVE |
| S2 | failed-breakout fade | P002 Failed-Breakout Fade | positive / OOS +.26 / VALIDATION PENDING |
| S5 | opening-range momentum | P003 Opening-Range Momentum | positive / OOS +.18 / VALIDATION PENDING |
| S22 | round-number breakout | P004 Round-Number Momentum | positive / OOS +.15 / VALIDATION PENDING |
| S22 (reject) | round-number rejection | P004 (negative leg) | NEGATIVE |
| S39 | efficiency-gated continuation | P005 Trend Efficiency | positive exploratory / OOS +.02 / small |
| S15, S38, S7, S10 | generic trend/pullback continuation | P012 Trend/Pullback Continuation | NEGATIVE |
| S42 | short-term large-return fade | P006 Short-Term Overreaction | positive exploratory / OOS +.18 / small n |
| S9, S20 | MTF-aligned momentum | P007 MTF Alignment | positive-but-correlated (beta-suspect) / MIXED |
| S6 | session transition | P008 Session Transition | weak positive OOS / MIXED |
| S45 | consecutive streak | P009 Streak Persistence | INCONCLUSIVE (weak, high DD) |
| S16, S17 | prior-day / weekly levels | P010 Liquidity Memory | MIXED (some +OOS, several −OOS) |
| S3, S4, S23, S46, S48 | breakout / squeeze / duration / volume-breakout | P013 Breakout-Chasing | NEGATIVE |
| S8, S26, S27, S28 | VWAP / value-area / anchored-VWAP | P014 Value/VWAP Reaction | NEGATIVE (S8 marginal exception) |
| S18, S29, S31 | day-of-week / month / time-of-day | P015 Calendar Seasonality | OVERFIT (OOS-refuted) |
| S40 | regime router | P016 Regime Routing | NEGATIVE |
| S44 | intrabar pressure | P017 Intrabar Pressure | NEGATIVE |
| S43 | RSI/price divergence | P018 Momentum Divergence | NEGATIVE |
| S41, S46 | volume climax / volume-confirmed breakout | P019 Volume Confirmation | NEGATIVE |
| S12 | range rotation | (P002 negative control) | NEGATIVE |
| S11 | structure-break reversal | (counter-trend, no primitive kept) | NEGATIVE |
| S13 | imbalance fill | (exploratory, no RW) | exploratory / no RW |
| S19 | session gap | (exploratory, n<25 profitable) | exploratory |
| S47 | weekend gap | (P—) | TECHNICALLY INVALID (n<25) |
| S49 | narrowest-range breakout | P013 (pattern variant) | TECHNICALLY INVALID (non-selective) |
| S50 | outside-bar / engulfing | (candlestick, no primitive kept) | NEGATIVE |
| S51 | intraday range-position | (range-envelope MR) | NEGATIVE |
| S14 | momentum exhaustion | (P006-adjacent) | FRAGILE (OOS −.14) |

Note: several families map to the SAME primitive (e.g., S9/S20 → P007), which is why 51 families reduce to 19
primitives (and the positive primitives further reduce under correlation — see CONTRADICTION_REGISTRY + the
project-root TOP_STRATEGIES_SHORTLIST). Full per-hypothesis metrics: STRATEGY_REGISTRY.parquet.
