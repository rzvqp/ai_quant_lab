"""`MonotonicWallClock` -- RT-TIME-0001 section A (2026-08-17): the ONLY source of `wall_clock_now`
`bridge.py`'s tower-chain path may use. Deliberately separate from `event_as_of`/`data_cutoff` (see
`bridge.TowerDependencies`'s own docstring) -- this exists purely to answer "what time is it right now,
operationally" for health/staleness/latency reporting, and is NEVER consulted to decide which market
data a request may see. A caller that used this for data selection would silently reintroduce exactly
the `TowerDependencies.now`-frozen-at-startup defect this whole remediation exists to close."""

from __future__ import annotations

import time
from typing import Callable


class ClockRollbackError(Exception):
    """Raised when two successive reads of the underlying raw clock go backward (NTP correction, VM
    pause/resume/snapshot-restore, manual clock change). A caller must treat this as fail-closed --
    never silently accept a rolled-back timestamp as authoritative."""


class MonotonicWallClock:
    """Wraps a raw clock (`time.time` by default) with a monotonicity check across calls. Each instance
    keeps its own `_last_seen` -- two independent `MonotonicWallClock()` instances never share state,
    matching every other per-process, non-global state convention already established in this codebase."""

    def __init__(self, raw_clock: Callable[[], float] = time.time) -> None:
        self._raw_clock = raw_clock
        self._last_seen: float | None = None

    def __call__(self) -> int:
        current = self._raw_clock()
        if self._last_seen is not None and current < self._last_seen:
            raise ClockRollbackError(
                f"MonotonicWallClock: raw clock went backward: {current!r} < previously-seen {self._last_seen!r}"
            )
        self._last_seen = current
        return int(current)
