"""A simple, deterministic, fixed-window rate limiter. `clock` is injectable (default `time.monotonic`)
so tests never depend on a real wall-clock -- mirrors `RealBrokerAdapterBase`'s own `_sleep` injection
precedent (Phase 1) for the same reason. When the window's budget is exhausted, `try_acquire()` returns
`False` -- it never blocks or sleeps waiting for the window to reset (this service's contract is
best-effort, never-blocking)."""

from __future__ import annotations

import time
from typing import Callable

from ai_trader.telegram_notifier.types import RateLimitPolicy


class RateLimiter:
    def __init__(self, policy: RateLimitPolicy, clock: Callable[[], float] | None = None) -> None:
        self._policy = policy
        self._clock = clock if clock is not None else time.monotonic
        self._window_start = self._clock()
        self._count_in_window = 0

    def try_acquire(self) -> bool:
        now = self._clock()
        if now - self._window_start >= self._policy.per_seconds:
            self._window_start = now
            self._count_in_window = 0
        if self._count_in_window >= self._policy.max_messages:
            return False
        self._count_in_window += 1
        return True
