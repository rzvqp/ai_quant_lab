"""Telegram Notification Service (Phase 5 -- `TELEGRAM_NOTIFIER_PHASE5_DESIGN.md`). Separate,
non-blocking, domain-free transport: never imports any trading-domain package, never imports the MT5
terminal API (verified by dedicated static tests), and cannot initiate a trading action. `notify()` never
raises past its own boundary; `notify_fire_and_forget()` never blocks the caller at all."""

from __future__ import annotations

from ai_trader.telegram_notifier.credentials import MissingTelegramCredentialsError, load_credentials_from_env
from ai_trader.telegram_notifier.rate_limiter import RateLimiter
from ai_trader.telegram_notifier.sender import notify, notify_fire_and_forget
from ai_trader.telegram_notifier.types import (
    ChatTarget,
    NotificationEvent,
    NotificationOutcome,
    RateLimitPolicy,
    RetryPolicy,
    SendResult,
    TelegramCredentials,
    TelegramNotifierConfig,
)

__all__ = [
    "notify",
    "notify_fire_and_forget",
    "load_credentials_from_env",
    "MissingTelegramCredentialsError",
    "RateLimiter",
    "ChatTarget",
    "NotificationEvent",
    "NotificationOutcome",
    "RateLimitPolicy",
    "RetryPolicy",
    "SendResult",
    "TelegramCredentials",
    "TelegramNotifierConfig",
]
