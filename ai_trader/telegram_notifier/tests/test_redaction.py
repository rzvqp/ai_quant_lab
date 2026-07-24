from __future__ import annotations

from ai_trader.telegram_notifier.redaction import redact_secrets
from ai_trader.telegram_notifier.tests._fixtures import make_credentials


def test_redacts_bot_token_from_url() -> None:
    credentials = make_credentials(bot_token="123456:FAKE-TOKEN-abcDEF")
    text = "https://api.telegram.org/bot123456:FAKE-TOKEN-abcDEF/sendMessage failed"
    redacted = redact_secrets(text, credentials)
    assert "123456:FAKE-TOKEN-abcDEF" not in redacted
    assert "REDACTED" in redacted


def test_leaves_unrelated_text_unchanged() -> None:
    credentials = make_credentials()
    text = "some unrelated error"
    assert redact_secrets(text, credentials) == text


def test_empty_text_returns_empty() -> None:
    assert redact_secrets("", make_credentials()) == ""
