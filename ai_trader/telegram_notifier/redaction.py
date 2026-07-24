"""Defense-in-depth secret redaction -- strips `credentials.bot_token` from any string before it is
logged or placed in an error message, so a `urllib` exception echoing back a request URL (which embeds
the token) can never leak it."""

from __future__ import annotations

from ai_trader.telegram_notifier.types import TelegramCredentials

_REDACTED = "***REDACTED***"


def redact_secrets(text: str, credentials: TelegramCredentials) -> str:
    if not text:
        return text
    return text.replace(credentials.bot_token, _REDACTED)
