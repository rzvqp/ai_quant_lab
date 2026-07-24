from __future__ import annotations

from ai_trader.telegram_notifier.rate_limiter import RateLimiter
from ai_trader.telegram_notifier.types import RateLimitPolicy


def test_allows_up_to_max_messages_in_window() -> None:
    clock = {"t": 0.0}
    limiter = RateLimiter(RateLimitPolicy(max_messages=3, per_seconds=60.0), clock=lambda: clock["t"])
    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is False


def test_window_resets_after_per_seconds_elapses() -> None:
    clock = {"t": 0.0}
    limiter = RateLimiter(RateLimitPolicy(max_messages=1, per_seconds=10.0), clock=lambda: clock["t"])
    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is False
    clock["t"] = 10.1
    assert limiter.try_acquire() is True


def test_rejects_invalid_policy() -> None:
    import pytest

    with pytest.raises(ValueError):
        RateLimitPolicy(max_messages=0)
    with pytest.raises(ValueError):
        RateLimitPolicy(per_seconds=0.0)
