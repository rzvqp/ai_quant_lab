# Executable Strategy Library — INDEX

Official interface between the Research Lab and the future AI Trader. One folder per strategy (`S<NN>_<slug>/`) with a human `README.md` and a machine-readable `strategy.json`. Machine index: `library_manifest.json`.

**Provenance:** generated from FROZEN research (result parquets + frozen family code). NO re-backtest, NO optimisation, NO engine change, NO new strategy. **Overall verdict: EXPLORATORY — no confirmed alpha.** Holdout SEALED · global-FDR NOT run · walk-forward NOT run. Metrics are research-segment (60%); OOS is the validation segment (20%).

| id | strategy | status | exp (R) | OOS (R) | PF | maxDD (R) | confidence |
|---|---|---|---|---|---|---|---|
| S1 | [Confirmed Liquidity Sweep Reversal](S01_confirmed_liquidity_sweep_reversal/README.md) | IMPLEMENTED | 0.032 | -0.0614 | 1.054 | 20.74 | VERY LOW |
| S2 | [Failed-Breakout Fade](S02_failed_breakout_fade/README.md) | IMPLEMENTED | 0.0188 | -0.0311 | 1.03 | 22.48 | VERY LOW |
| S3 | [Breakout Retest Continuation](S03_breakout_retest_continuation/README.md) | IMPLEMENTED | 0.0634 | 0.1052 | 1.086 | 40.57 | VERY LOW |
| S4 | [Volatility Compression Expansion](S04_volatility_compression_expansion/README.md) | IMPLEMENTED | -0.3763 | -0.2415 | 0.269 | 1183.6 | NEGATIVE |
| S5 | [Opening-Range Breakout](S05_opening_range_breakout/README.md) | IMPLEMENTED | 0.0756 | 0.2371 | 1.135 | 14.3 | LOW |
| S6 | [Session-Transition](S06_session_transition/README.md) | IMPLEMENTED | 0.017 | 0.1604 | 1.027 | 23.91 | LOW |
| S7 | [Trend Pullback Continuation](S07_trend_pullback_continuation/README.md) | IMPLEMENTED | -0.5641 | -0.4291 | 0.449 | 1844.9 | NEGATIVE |
| S8 | [Extension Mean-Reversion](S08_extension_mean_reversion/README.md) | IMPLEMENTED | 0.0171 | 0.1094 | 1.026 | 24.62 | LOW |
| S9 | [Multi-Timeframe Alignment](S09_multi_timeframe_alignment/README.md) | IMPLEMENTED | 0.0624 | 0.1713 | 1.117 | 20.53 | LOW |
| S10 | [Displacement Continuation](S10_displacement_continuation/README.md) | IMPLEMENTED | -0.3217 | -0.3042 | 0.4 | 1076.09 | NEGATIVE |
| S11 | [Structure-Break Reversal (CHoCH)](S11_structure_break_reversal_choch/README.md) | IMPLEMENTED | -0.1668 | -0.0441 | 0.776 | 205.01 | NEGATIVE |
| S12 | [Range Rotation](S12_range_rotation/README.md) | IMPLEMENTED | -0.2384 | -0.1921 | 0.67 | 484.25 | NEGATIVE |
| S13 | [Imbalance Fill](S13_imbalance_fill/README.md) | IMPLEMENTED | 0.0199 | 0.0732 | 1.028 | 121.8 | VERY LOW |
| S14 | [Momentum Exhaustion](S14_momentum_exhaustion/README.md) | IMPLEMENTED | 0.0349 | -0.1374 | 1.061 | 14.01 | VERY LOW |
| S15 | [Trend Acceleration](S15_trend_acceleration/README.md) | IMPLEMENTED | -0.2812 | -0.1987 | 0.404 | 830.41 | NEGATIVE |
| S16 | [Previous-Day Levels](S16_previous_day_levels/README.md) | IMPLEMENTED | 0.0316 | 0.1368 | 1.042 | 90.31 | VERY LOW |
| S17 | [Weekly Levels](S17_weekly_levels/README.md) | IMPLEMENTED | 0.0567 | 0.0312 | 1.082 | 21.06 | LOW |
| S18 | [Time-of-Day Edge](S18_time_of_day_edge/README.md) | IMPLEMENTED | 0.0316 | 0.0132 | 1.037 | 75.15 | VERY LOW |
| S19 | [Session Gap](S19_session_gap/README.md) | IMPLEMENTED | 0.0596 | 0.6205 | 1.076 | 10.17 | VERY LOW |
| S20 | [Hybrid Sweep + MTF](S20_hybrid_sweep_mtf/README.md) | IMPLEMENTED | 0.0553 | 0.1371 | 1.121 | 10.76 | LOW |
| S21 | [Equal-Highs/Lows Liquidity-Pool Raid](S21_equal_highs_lows_liquidity_pool_raid/README.md) | IMPLEMENTED | -0.3669 | -0.2608 | 0.586 | 868.62 | NEGATIVE |
| S22 | [Round-Number Magnet / Rejection](S22_round_number_magnet_rejection/README.md) | IMPLEMENTED | 0.0819 | 0.1465 | 1.117 | 22.47 | LOW |
| S23 | [Squeeze Breakout + HTF Filter](S23_squeeze_breakout_htf_filter/README.md) | IMPLEMENTED | -0.2604 | -0.1659 | 0.332 | 423.44 | NEGATIVE |
| S24 | [Overnight Variance / Session Carry](S24_overnight_variance_session_carry/README.md) | IMPLEMENTED | 0.0815 | -0.0746 | 1.107 | 33.37 | VERY LOW |
| S25 | [Volatility-Regime Onset](S25_volatility_regime_onset/README.md) | IMPLEMENTED | -0.1246 | 0.0174 | 0.83 | 130.2 | NEGATIVE |
| S26 | [Value-Area Rejection / Acceptance](S26_value_area_rejection_acceptance/README.md) | IMPLEMENTED | -0.3336 | -0.1423 | 0.55 | 1286.82 | NEGATIVE |
| S27 | [VWAP Reclaim in Trend](S27_vwap_reclaim_in_trend/README.md) | IMPLEMENTED | -0.4462 | -0.2416 | 0.469 | 1952.65 | NEGATIVE |
| S28 | [Anchored-VWAP Reaction](S28_anchored_vwap_reaction/README.md) | IMPLEMENTED | -0.1113 | -0.0187 | 0.853 | 148.9 | NEGATIVE |
| S29 | [Day-of-Week Effect](S29_day_of_week_effect/README.md) | IMPLEMENTED | 0.2047 | -0.0259 | 1.332 | 17.7 | VERY LOW |
| S30 | [Kill-Zone Time-Window](S30_kill_zone_time_window/README.md) | IMPLEMENTED | -0.1073 | 0.0554 | 0.848 | 159.67 | NEGATIVE |
| S31 | [Month-End / Month-Start Effect](S31_month_end_month_start_effect/README.md) | IMPLEMENTED | 0.1249 | -0.4385 | 1.163 | 9.51 | VERY LOW |
| S38 | [Patient Pullback-into-Zone](S38_patient_pullback_into_zone/README.md) | IMPLEMENTED | -0.2386 | -0.1003 | 0.371 | 541.46 | NEGATIVE |
| S39 | [Trend-Efficiency-Gated Continuation](S39_trend_efficiency_gated_continuation/README.md) | IMPLEMENTED | 0.0289 | 0.0179 | 1.085 | 11.65 | LOW |
| S40 | [Regime Router](S40_regime_router/README.md) | IMPLEMENTED | -0.3109 | -0.1335 | 0.62 | 1073.11 | NEGATIVE |
| S41 | [Volume-Climax Reversal](S41_volume_climax_reversal/README.md) | IMPLEMENTED | -0.388 | -0.3384 | 0.575 | 535.55 | NEGATIVE |
| S42 | [Short-Term Return Reversal](S42_short_term_return_reversal/README.md) | IMPLEMENTED | 0.0833 | 0.0574 | 1.139 | 5.23 | LOW |
| S43 | [Momentum Divergence (RSI/Price)](S43_momentum_divergence_rsi_price/README.md) | IMPLEMENTED | -0.3331 | -0.3381 | 0.618 | 1319.21 | NEGATIVE |
| S44 | [Intrabar Pressure / Close-Location](S44_intrabar_pressure_close_location/README.md) | IMPLEMENTED | -0.1434 | -0.0965 | 0.8 | 372.51 | NEGATIVE |
| S45 | [Consecutive-Bar Streak](S45_consecutive_bar_streak/README.md) | IMPLEMENTED | 0.0448 | 0.1299 | 1.063 | 39.05 | VERY LOW |
| S46 | [Volume-Confirmed Breakout](S46_volume_confirmed_breakout/README.md) | IMPLEMENTED | 0.0172 | -0.017 | 1.052 | 24.33 | VERY LOW |
| S47 | [Weekend-Gap Fill / Continuation](S47_weekend_gap_fill_continuation/README.md) | INVALID | -0.0727 | -0.369 | 0.707 | 1.93 | INVALID |
| S48 | [Consolidation-Duration Breakout](S48_consolidation_duration_breakout/README.md) | IMPLEMENTED | -0.2184 | -0.1314 | 0.285 | 402.2 | NEGATIVE |
| S49 | [Narrowest-Range (NR) Breakout](S49_narrowest_range_nr_breakout/README.md) | INVALID | None | None | None | None | INVALID |
| S50 | [Outside-Bar / Engulfing Reversal](S50_outside_bar_engulfing_reversal/README.md) | IMPLEMENTED | -0.5859 | -0.5938 | 0.444 | 1892.1 | NEGATIVE |
| S51 | [Intraday Range-Position Reversion](S51_intraday_range_position_reversion/README.md) | IMPLEMENTED | -0.3491 | -0.2622 | 0.592 | 1190.79 | NEGATIVE |
| S32 | [S32 (not implemented)](S32_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |
| S33 | [S33 (not implemented)](S33_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |
| S34 | [S34 (not implemented)](S34_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |
| S35 | [S35 (not implemented)](S35_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |
| S36 | [S36 (not implemented)](S36_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |
| S37 | [S37 (not implemented)](S37_not_implemented/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |

## Reading guide
- **Positive-leaning (research-worthy + positive OOS):** the low-confidence exploratory candidates.
- **Beta caveat:** S5 opening-range is substantially session/regime BETA (Wave-1 EXP-04); S1 sweep survives a beta-matched null on research but with NEGATIVE OOS (Wave-1 EXP-03) — neither is confirmed alpha.
- **INVALID:** S47 (n<25), S49 (non-selective) — documented but not usable.
- **NOT_IMPLEMENTED:** S32-S37 need external Tier-1/2 data (CEO-gated).
- **No strategy here is validated alpha or production-ready.** The AI Trader must treat every spec as an exploratory hypothesis pending confirmatory testing (matched-null on the full universe, walk-forward, holdout).
