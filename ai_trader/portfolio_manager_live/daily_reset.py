"""`reset_if_new_day` -- Demo Readiness precondition #11 fix (2026-07-25). `PortfolioDailyState`'s own
docstring names "a future Execution Orchestrator" as the owner responsible for tracking and resetting it
daily; Phase 9 was built without that owner ever materializing. Pure function, no state, no I/O, no
wall-clock (`as_of` always caller-supplied) -- the caller persists the result across calls, the exact
discipline already established for `PortfolioDailyState` itself.

**Disclosed IMPLEMENTATION CHOICE**: "a new day" means a UTC calendar-day boundary
(`as_of // 86_400`), not the account's own trading-day/session convention -- the simplest, timezone
-agnostic, deterministic definition, matching this codebase's own precedent for similarly-disclosed
placeholder policies (e.g. `ConstraintDefaults`, `QUALITY_FACTOR`). If a different day boundary is ever
required (broker rollover time, a specific trading session), this is the one place to change.
"""

from __future__ import annotations

from ai_trader.portfolio_manager_live.types import PortfolioDailyState

_SECONDS_PER_DAY = 86_400


def reset_if_new_day(current: PortfolioDailyState, as_of: int) -> PortfolioDailyState:
    """Returns a fresh `PortfolioDailyState` (zeroed counters, stamped with `as_of`) if `as_of` falls on
    a LATER UTC calendar day than `current.as_of`; otherwise returns `current` unchanged (including on a
    backward/stale `as_of` -- fail-safe: never resets on anything but a genuine forward move into a new
    day, so an out-of-order call can never wipe today's already-accumulated heat)."""
    current_day = current.as_of // _SECONDS_PER_DAY
    candidate_day = as_of // _SECONDS_PER_DAY
    if candidate_day > current_day:
        return PortfolioDailyState(as_of=as_of)
    return current
