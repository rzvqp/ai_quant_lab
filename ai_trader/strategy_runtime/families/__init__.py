"""Importing this package registers every implemented family evaluator (each module calls
``ai_trader.strategy_runtime.registry.register(strategy_id)`` at import time). Add a new
``import ai_trader.strategy_runtime.families.sNN_...`` line here for every strategy as its evaluator
is implemented -- this file is the single, auditable manifest of which strategies actually have real
runtime logic wired in.
"""

from __future__ import annotations

import ai_trader.strategy_runtime.families.s01_confirmed_liquidity_sweep_reversal  # noqa: F401
import ai_trader.strategy_runtime.families.s02_failed_breakout_fade  # noqa: F401
import ai_trader.strategy_runtime.families.s06_session_transition  # noqa: F401
import ai_trader.strategy_runtime.families.s11_structure_break_reversal_choch  # noqa: F401
import ai_trader.strategy_runtime.families.s12_range_rotation  # noqa: F401
import ai_trader.strategy_runtime.families.s16_previous_day_levels  # noqa: F401
import ai_trader.strategy_runtime.families.s17_weekly_levels  # noqa: F401
import ai_trader.strategy_runtime.families.s18_time_of_day_edge  # noqa: F401
import ai_trader.strategy_runtime.families.s19_session_gap  # noqa: F401
import ai_trader.strategy_runtime.families.s21_equal_highs_lows_liquidity_pool_raid  # noqa: F401
import ai_trader.strategy_runtime.families.s22_round_number_magnet_rejection  # noqa: F401
import ai_trader.strategy_runtime.families.s24_overnight_variance_session_carry  # noqa: F401
import ai_trader.strategy_runtime.families.s29_day_of_week_effect  # noqa: F401
import ai_trader.strategy_runtime.families.s30_kill_zone_time_window  # noqa: F401
import ai_trader.strategy_runtime.families.s31_month_end_month_start_effect  # noqa: F401
