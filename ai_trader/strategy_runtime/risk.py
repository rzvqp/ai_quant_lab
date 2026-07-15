"""Shared stop-floor / target helpers, mirroring the frozen research engine's own conventions
(``code/mstrat.py``, read only -- never imported at runtime, per
``STRATEGY_RUNTIME_INTEGRATION_GAP.md`` §8/§9). Every migrated strategy's own
``position_sizing.stop_floor`` field quotes the SAME formula
(e.g. S1: ``"max(2*spread_ticks*tick, 5*tick, 0.10*ATR)"``) -- centralizing it here means the 43
per-family evaluators share one, auditable implementation instead of 43 independent transcriptions.

IMPLEMENTATION CHOICE: the frozen research engine's own tick constant for XAUUSD is ``TICK=0.1``
(``code/mstrat.py``, confirmed by reading the file directly, and by S1's own contract:
``"costs": "(spread 1 + slippage 1) ticks/side * 0.1 = 0.10/side"``). This is DISTINCT from the
Simulation Framework's own ``SymbolMeta.tick_size`` (0.01 in the Phase 6.7 test fixtures, a plausible
live-quote tick) -- the two need not agree, and this module's own conformance tests use the
research engine's ``0.1`` value explicitly (never silently substituting the Simulation Framework's
own tick_size), so "conformance" means reproducing the frozen engine's OWN math, not inventing a new
one. Callers pass whichever tick value is contextually correct.
"""

from __future__ import annotations

#: The frozen research engine's own XAUUSD tick constant (`code/mstrat.py`: `TICK=0.1`).
RESEARCH_ENGINE_TICK = 0.1


def executable_stop_floor(spread_ticks: float, tick: float, atr: float | None) -> float:
    """``max(2*spread_ticks*tick, 5*tick, 0.10*ATR)`` -- the frozen engine's pre-registered
    stop-floor (``code/mstrat.py``: ``min_exec=max(2*cfg['spread_ticks']*TICK, 5*TICK,
    0.10*atr[si])``). ``atr=None`` (not yet available) falls back to the two tick-based floors only
    -- never fabricates an ATR-based number from missing data."""
    floor = max(2.0 * spread_ticks * tick, 5.0 * tick)
    if atr is not None and atr > 0:
        floor = max(floor, 0.10 * atr)
    return floor


def widen_stop_to_floor(entry: float, raw_stop: float, is_long: bool, floor: float) -> float:
    """If the strategy's own raw stop distance is tighter than ``floor``, widen it (never tighten) to
    the floor, preserving direction -- mirrors ``code/mstrat.py``'s own
    ``if risk<min_exec: risk=min_exec; stop=entry-dirn*risk``."""
    raw_risk = abs(entry - raw_stop)
    if raw_risk >= floor:
        return raw_stop
    return entry - floor if is_long else entry + floor


def rr_target(entry: float, stop: float, is_long: bool, rr: float) -> float:
    """A fixed-R:R target (e.g. ``rr2``/``rr3`` in the Strategy Library's own ``exit_rules``
    grammar): ``target = entry +/- rr * risk_distance``."""
    risk_distance = abs(entry - stop)
    return entry + rr * risk_distance if is_long else entry - rr * risk_distance


def risk_r_of(entry: float, exit_price: float, stop: float, is_long: bool) -> float | None:
    """The realized/prospective R-multiple of a price move, given the position's own stop distance.
    ``None`` if the stop distance is degenerate (entry == stop) -- never divides by zero."""
    risk_distance = abs(entry - stop)
    if risk_distance <= 0:
        return None
    direction_sign = 1.0 if is_long else -1.0
    return (direction_sign * (exit_price - entry)) / risk_distance
