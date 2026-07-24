from __future__ import annotations

import threading
import time

from ai_trader.telegram_notifier.rate_limiter import RateLimiter
from ai_trader.telegram_notifier.sender import notify, notify_fire_and_forget
from ai_trader.telegram_notifier.tests._fixtures import FakeTransport, make_config, make_credentials, make_event, no_sleep
from ai_trader.telegram_notifier.types import ChatTarget, RateLimitPolicy, RetryPolicy


def test_successful_send_to_primary_only() -> None:
    transport = FakeTransport(responses=[(200, '{"ok": true}')])
    outcome = notify(make_event(chat_target=ChatTarget.PRIMARY), make_credentials(), transport=transport, sleep=no_sleep)
    assert outcome.overall_success is True
    assert len(outcome.results) == 1
    assert outcome.results[0].chat_id == "111"
    assert len(transport.calls) == 1


def test_dual_send_to_both_chats() -> None:
    transport = FakeTransport(responses=[(200, '{"ok": true}')])
    outcome = notify(make_event(chat_target=ChatTarget.BOTH), make_credentials(), transport=transport, sleep=no_sleep)
    assert len(outcome.results) == 2
    assert {r.chat_id for r in outcome.results} == {"111", "222"}
    assert len(transport.calls) == 2


def test_secondary_absent_from_credentials_sends_nothing_for_secondary_target() -> None:
    transport = FakeTransport()
    credentials = make_credentials(secondary_chat_id=None)
    outcome = notify(make_event(chat_target=ChatTarget.SECONDARY), credentials, transport=transport, sleep=no_sleep)
    assert outcome.results == ()
    assert len(transport.calls) == 0


def test_one_chat_failure_does_not_affect_the_other_in_dual_send() -> None:
    call_count = {"n": 0}

    def flaky_transport(url: str, payload: dict[str, object], timeout: float) -> tuple[int, str]:
        call_count["n"] += 1
        if payload["chat_id"] == "111":
            return 200, '{"ok": true}'
        return 500, '{"ok": false}'

    outcome = notify(
        make_event(chat_target=ChatTarget.BOTH), make_credentials(),
        config=make_config(retry=RetryPolicy(max_attempts=1)), transport=flaky_transport, sleep=no_sleep,
    )
    results_by_chat = {r.chat_id: r for r in outcome.results}
    assert results_by_chat["111"].success is True
    assert results_by_chat["222"].success is False
    assert outcome.overall_success is False


def test_retries_up_to_max_attempts_then_succeeds() -> None:
    transport = FakeTransport(responses=[(500, "err"), (500, "err"), (200, '{"ok": true}')])
    outcome = notify(
        make_event(), make_credentials(), config=make_config(retry=RetryPolicy(max_attempts=3)),
        transport=transport, sleep=no_sleep,
    )
    assert outcome.overall_success is True
    assert outcome.results[0].attempts == 3
    assert len(transport.calls) == 3


def test_exhausts_retries_and_reports_failure_without_raising() -> None:
    transport = FakeTransport(responses=[(500, "err")])
    outcome = notify(
        make_event(), make_credentials(), config=make_config(retry=RetryPolicy(max_attempts=2)),
        transport=transport, sleep=no_sleep,
    )
    assert outcome.overall_success is False
    assert outcome.results[0].attempts == 2


def test_transport_exception_is_caught_and_never_raises() -> None:
    transport = FakeTransport(raise_on_call=ConnectionError("network down"))
    outcome = notify(
        make_event(), make_credentials(), config=make_config(retry=RetryPolicy(max_attempts=2)),
        transport=transport, sleep=no_sleep,
    )
    assert outcome.overall_success is False
    assert "network down" in (outcome.results[0].error or "")


def test_transport_exception_message_never_leaks_bot_token() -> None:
    credentials = make_credentials(bot_token="123456:SUPER-SECRET")

    def raising_transport(url: str, payload: dict[str, object], timeout: float) -> tuple[int, str]:
        raise ConnectionError(f"failed calling {url}")

    outcome = notify(
        make_event(), credentials, config=make_config(retry=RetryPolicy(max_attempts=1)),
        transport=raising_transport, sleep=no_sleep,
    )
    assert "SUPER-SECRET" not in (outcome.results[0].error or "")


def test_rate_limited_call_sends_nothing() -> None:
    clock = {"t": 0.0}
    limiter = RateLimiter(RateLimitPolicy(max_messages=0 + 1, per_seconds=60.0), clock=lambda: clock["t"])
    limiter.try_acquire()  # consume the only slot
    transport = FakeTransport()
    outcome = notify(make_event(), make_credentials(), transport=transport, rate_limiter=limiter, sleep=no_sleep)
    assert outcome.rate_limited is True
    assert outcome.results == ()
    assert len(transport.calls) == 0


def test_fire_and_forget_returns_immediately_and_still_delivers() -> None:
    delivered = threading.Event()

    def slow_transport(url: str, payload: dict[str, object], timeout: float) -> tuple[int, str]:
        time.sleep(0.05)
        delivered.set()
        return 200, '{"ok": true}'

    started = time.monotonic()
    notify_fire_and_forget(make_event(), make_credentials(), transport=slow_transport)
    elapsed = time.monotonic() - started
    assert elapsed < 0.05  # returned before the transport's own sleep completed
    assert delivered.wait(timeout=2.0) is True
