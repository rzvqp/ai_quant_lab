"""Shared fixture builders for `telegram_notifier` tests."""

from __future__ import annotations

from ai_trader.telegram_notifier.types import NotificationEvent, TelegramCredentials, TelegramNotifierConfig

AS_OF = 1_700_000_000


def make_credentials(**overrides: object) -> TelegramCredentials:
    kwargs: dict[str, object] = {
        "bot_token": "123456:FAKE-TOKEN-abcDEF", "primary_chat_id": "111", "secondary_chat_id": "222",
    }
    kwargs.update(overrides)
    return TelegramCredentials(**kwargs)  # type: ignore[arg-type]


def make_event(**overrides: object) -> NotificationEvent:
    kwargs: dict[str, object] = {
        "event_type": "RISK_DECISION_DENIED", "summary": "trade denied", "correlation_id": "C1",
        "as_of": AS_OF, "detail": {"symbol": "XAUUSD"},
    }
    kwargs.update(overrides)
    return NotificationEvent(**kwargs)  # type: ignore[arg-type]


def make_config(**overrides: object) -> TelegramNotifierConfig:
    kwargs: dict[str, object] = {}
    kwargs.update(overrides)
    return TelegramNotifierConfig(**kwargs)  # type: ignore[arg-type]


class FakeTransport:
    """A scripted, injectable transport -- no real network call, mirrors this codebase's own
    `FakeBrokerAdapter`/`FakeMT5Gateway` precedent."""

    def __init__(self, responses: list[tuple[int, str]] | None = None, raise_on_call: Exception | None = None) -> None:
        self._responses = responses if responses is not None else [(200, '{"ok": true}')]
        self._raise_on_call = raise_on_call
        self.calls: list[tuple[str, dict[str, object], float]] = []

    def __call__(self, url: str, payload: dict[str, object], timeout: float) -> tuple[int, str]:
        self.calls.append((url, payload, timeout))
        if self._raise_on_call is not None:
            raise self._raise_on_call
        index = min(len(self.calls) - 1, len(self._responses) - 1)
        return self._responses[index]


def no_sleep(_seconds: float) -> None:
    pass
