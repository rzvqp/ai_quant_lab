"""`notify`/`notify_fire_and_forget` -- the Telegram Notification Service's public entry points. Never
raises past its own boundary (same "failure isolation" discipline established elsewhere in this project
for observational side-channels): every HTTP/network exception is caught, redacted, and turned into a
failed `SendResult`, never propagated."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from typing import Callable

from ai_trader.telegram_notifier.rate_limiter import RateLimiter
from ai_trader.telegram_notifier.redaction import redact_secrets
from ai_trader.telegram_notifier.types import (
    ChatTarget,
    NotificationEvent,
    NotificationOutcome,
    SendResult,
    TelegramCredentials,
    TelegramNotifierConfig,
)

#: (url, payload, timeout_seconds) -> (http_status, response_text). Injectable so tests never make a
#: real network call (mirrors this codebase's own `FakeBrokerAdapter`/`_sleep`-injection precedent).
Transport = Callable[[str, dict[str, object], float], "tuple[int, str]"]


def _real_transport(url: str, payload: dict[str, object], timeout: float) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 -- fixed https://api.telegram.org base, never a caller-supplied URL.
        body = response.read().decode("utf-8")
        return response.status, body


def _chat_ids_for(target: ChatTarget, credentials: TelegramCredentials) -> tuple[str, ...]:
    if target is ChatTarget.PRIMARY:
        return (credentials.primary_chat_id,)
    if target is ChatTarget.SECONDARY:
        return (credentials.secondary_chat_id,) if credentials.secondary_chat_id is not None else ()
    ids = [credentials.primary_chat_id]
    if credentials.secondary_chat_id is not None:
        ids.append(credentials.secondary_chat_id)
    return tuple(ids)


def _send_to_one_chat(
    chat_id: str, text: str, credentials: TelegramCredentials, config: TelegramNotifierConfig,
    transport: Transport, sleep: Callable[[float], None],
) -> SendResult:
    url = f"{config.api_base_url}/bot{credentials.bot_token}/sendMessage"
    payload: dict[str, object] = {"chat_id": chat_id, "text": text}
    delay = config.retry.base_delay_seconds
    last_error: str | None = None
    last_status: int | None = None

    for attempt in range(1, config.retry.max_attempts + 1):
        try:
            status, body = transport(url, payload, config.request_timeout_seconds)
            last_status = status
            parsed_ok = False
            try:
                parsed_ok = bool(json.loads(body).get("ok", False))
            except (json.JSONDecodeError, AttributeError):
                parsed_ok = False
            if 200 <= status < 300 and parsed_ok:
                return SendResult(chat_id=chat_id, success=True, attempts=attempt, http_status=status)
            last_error = redact_secrets(f"non-ok response: status={status} body={body}", credentials)
        except Exception as exc:  # noqa: BLE001 -- the network call is the untrusted boundary; never
            # propagate, classify as a retryable failure instead (same discipline as
            # execution_engine.adapters.base._call_with_retry).
            last_error = redact_secrets(f"{type(exc).__name__}: {exc}", credentials)

        if attempt < config.retry.max_attempts:
            sleep(delay)
            delay *= config.retry.backoff_multiplier

    return SendResult(
        chat_id=chat_id, success=False, attempts=config.retry.max_attempts, http_status=last_status,
        error=last_error,
    )


def notify(
    event: NotificationEvent, credentials: TelegramCredentials, config: TelegramNotifierConfig | None = None,
    transport: Transport | None = None, rate_limiter: RateLimiter | None = None,
    sleep: Callable[[float], None] | None = None,
) -> NotificationOutcome:
    resolved_config = config if config is not None else TelegramNotifierConfig()
    resolved_transport = transport if transport is not None else _real_transport
    resolved_sleep = sleep if sleep is not None else time.sleep

    if rate_limiter is not None and not rate_limiter.try_acquire():
        return NotificationOutcome(
            event_type=event.event_type, correlation_id=event.correlation_id, results=(), rate_limited=True,
        )

    try:
        chat_ids = _chat_ids_for(event.chat_target, credentials)
        text = event.render_text()
        results = tuple(
            _send_to_one_chat(chat_id, text, credentials, resolved_config, resolved_transport, resolved_sleep)
            for chat_id in chat_ids
        )
    except Exception as exc:  # noqa: BLE001 -- fail-closed: this function must NEVER raise past its own
        # boundary (CEO: "Telegram failure must never block the trading pipeline").
        error = redact_secrets(f"{type(exc).__name__}: {exc}", credentials)
        results = (SendResult(chat_id="__unknown__", success=False, attempts=0, error=error),)

    return NotificationOutcome(event_type=event.event_type, correlation_id=event.correlation_id, results=results)


def notify_fire_and_forget(
    event: NotificationEvent, credentials: TelegramCredentials, config: TelegramNotifierConfig | None = None,
    transport: Transport | None = None, rate_limiter: RateLimiter | None = None,
) -> None:
    """Spawns a daemon thread running `notify()` and returns immediately -- the calling pipeline never
    waits for Telegram at all, the strongest reading of "must never block the trading pipeline"."""
    thread = threading.Thread(
        target=notify, args=(event, credentials, config, transport, rate_limiter), daemon=True,
    )
    thread.start()
