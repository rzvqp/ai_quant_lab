# MINIMUM STOP FLOOR — PRE-REGISTRATION (chosen BEFORE seeing results)

## Economic reason
R = pnl / initial_risk. If initial_risk (entry→initial_stop) is below the executable noise/cost floor,
R explodes on ordinary moves (S6: risk 0.19px, R up to +166). Such "trades" are not executable at that
risk and their R is a normalization artifact. A floor keeps R economically meaningful and executable.

## Official formula (v2 engine) — FROZEN, one rule
    min_executable_risk = max( k_spread * effective_spread,
                               k_tick   * tick_size,
                               k_atr    * ATR )
    executable_stop_distance = max( strategy_stop_distance, min_executable_risk )

## Pre-registered constants (justified, chosen before results)
- k_spread = 2   (stop must sit beyond 2x the round-trip spread to be fillable, not inside noise)
- k_tick   = 5   (>= 5 ticks = 0.5 px on XAUUSD; below this, rounding/quantization dominates)
- k_atr    = 0.10 (>= 10% of ATR; below this the stop is inside typical single-bar noise)
=> XAUUSD (tick 0.1, spread~0.2-0.4, ATR~10): min_executable_risk ≈ max(0.4-0.8, 0.5, 1.0) ≈ 1.0 px.

## Diagnostic variants (report only; NOT the official choice)
- V-A: k_atr=0.05 (looser)
- V-B: k_atr=0.15 (tighter)
Report V-A/V-B as sensitivity; the OFFICIAL is k_atr=0.10 above, decided now.

## INVALID EXECUTION rule (R-normalization audit)
initial_risk = abs(entry_price_after_spread - initial_stop_after_tick_rounding).
- Any trade whose strategy_stop_distance < min_executable_risk is FLOORED to min_executable_risk
  (stop widened to the executable floor) — it is still a trade but at the executable risk.
- A trade is marked **INVALID EXECUTION** (excluded, not counted) only if it cannot be executed at all:
  gap through the floored stop at entry, zero/negative risk after flooring, or entry/exit inside the
  same bar with ambiguous fill that the worst-case model cannot resolve.
- Audit per trade: tick-rounded stop, entry+exit spread, slippage, gap-over-stop, stop modification,
  break-even, partial exits, intrabar ordering, max-possible-R vs realized market move.

## Versioning & re-run policy
- Engine v2 = v1 + this floor + INVALID EXECUTION marking. Version-stamp all results.
- Results computed under v1 are INVALIDATED for comparison; re-run ALL families S1–S20 uniformly on v2.
- Do NOT tune k after seeing which value removes unfavorable outliers or improves p-values.
