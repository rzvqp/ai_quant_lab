"""Importing this package registers every implemented family evaluator (each module calls
``ai_trader.strategy_runtime.registry.register(strategy_id)`` at import time). Add a new
``import ai_trader.strategy_runtime.families.sNN_...`` line here for every strategy as its evaluator
is implemented -- this file is the single, auditable manifest of which strategies actually have real
runtime logic wired in.
"""

from __future__ import annotations

import ai_trader.strategy_runtime.families.s01_confirmed_liquidity_sweep_reversal  # noqa: F401
import ai_trader.strategy_runtime.families.s02_failed_breakout_fade  # noqa: F401
import ai_trader.strategy_runtime.families.s03_breakout_retest_continuation  # noqa: F401
import ai_trader.strategy_runtime.families.s04_volatility_compression_expansion  # noqa: F401
import ai_trader.strategy_runtime.families.s05_opening_range_breakout  # noqa: F401
import ai_trader.strategy_runtime.families.s06_session_transition  # noqa: F401
import ai_trader.strategy_runtime.families.s07_trend_pullback_continuation  # noqa: F401
import ai_trader.strategy_runtime.families.s08_extension_mean_reversion  # noqa: F401
import ai_trader.strategy_runtime.families.s09_multi_timeframe_alignment  # noqa: F401
import ai_trader.strategy_runtime.families.s10_displacement_continuation  # noqa: F401
import ai_trader.strategy_runtime.families.s11_structure_break_reversal_choch  # noqa: F401
import ai_trader.strategy_runtime.families.s12_range_rotation  # noqa: F401
import ai_trader.strategy_runtime.families.s13_imbalance_fill  # noqa: F401
import ai_trader.strategy_runtime.families.s14_momentum_exhaustion  # noqa: F401
import ai_trader.strategy_runtime.families.s15_trend_acceleration  # noqa: F401
import ai_trader.strategy_runtime.families.s16_previous_day_levels  # noqa: F401
import ai_trader.strategy_runtime.families.s17_weekly_levels  # noqa: F401
import ai_trader.strategy_runtime.families.s18_time_of_day_edge  # noqa: F401
import ai_trader.strategy_runtime.families.s19_session_gap  # noqa: F401
import ai_trader.strategy_runtime.families.s20_hybrid_sweep_mtf  # noqa: F401
import ai_trader.strategy_runtime.families.s21_equal_highs_lows_liquidity_pool_raid  # noqa: F401
import ai_trader.strategy_runtime.families.s22_round_number_magnet_rejection  # noqa: F401
import ai_trader.strategy_runtime.families.s23_squeeze_breakout_htf_filter  # noqa: F401
import ai_trader.strategy_runtime.families.s24_overnight_variance_session_carry  # noqa: F401
import ai_trader.strategy_runtime.families.s25_volatility_regime_onset  # noqa: F401
import ai_trader.strategy_runtime.families.s26_value_area_rejection_acceptance  # noqa: F401
import ai_trader.strategy_runtime.families.s27_vwap_reclaim_in_trend  # noqa: F401
import ai_trader.strategy_runtime.families.s28_anchored_vwap_reaction  # noqa: F401
import ai_trader.strategy_runtime.families.s29_day_of_week_effect  # noqa: F401
import ai_trader.strategy_runtime.families.s30_kill_zone_time_window  # noqa: F401
import ai_trader.strategy_runtime.families.s31_month_end_month_start_effect  # noqa: F401
import ai_trader.strategy_runtime.families.s38_patient_pullback_into_zone  # noqa: F401
import ai_trader.strategy_runtime.families.s39_trend_efficiency_gated_continuation  # noqa: F401
import ai_trader.strategy_runtime.families.s40_regime_router  # noqa: F401
import ai_trader.strategy_runtime.families.s41_volume_climax_reversal  # noqa: F401
import ai_trader.strategy_runtime.families.s42_short_term_return_reversal  # noqa: F401
import ai_trader.strategy_runtime.families.s43_momentum_divergence_rsi_price  # noqa: F401
import ai_trader.strategy_runtime.families.s44_intrabar_pressure_close_location  # noqa: F401
import ai_trader.strategy_runtime.families.s45_consecutive_bar_streak  # noqa: F401
import ai_trader.strategy_runtime.families.s46_volume_confirmed_breakout  # noqa: F401
import ai_trader.strategy_runtime.families.s48_consolidation_duration_breakout  # noqa: F401
import ai_trader.strategy_runtime.families.s50_outside_bar_engulfing_reversal  # noqa: F401
import ai_trader.strategy_runtime.families.s51_intraday_range_position_reversion  # noqa: F401
