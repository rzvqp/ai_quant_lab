from __future__ import annotations

import pytest

from ai_trader.telegram_notifier.tests._fixtures import make_credentials, make_event
from ai_trader.telegram_notifier.types import NotificationOutcome, SendResult


def test_credentials_requires_bot_token() -> None:
    with pytest.raises(ValueError):
        make_credentials(bot_token="")


def test_credentials_requires_primary_chat_id() -> None:
    with pytest.raises(ValueError):
        make_credentials(primary_chat_id="")


def test_credentials_repr_never_leaks_bot_token() -> None:
    credentials = make_credentials(bot_token="123456:SUPER-SECRET-TOKEN")
    assert "SUPER-SECRET-TOKEN" not in repr(credentials)
    assert "SUPER-SECRET-TOKEN" not in str(credentials)
    assert "REDACTED" in repr(credentials)


def test_event_requires_nonempty_event_type() -> None:
    with pytest.raises(ValueError):
        make_event(event_type="")


def test_event_requires_nonempty_correlation_id() -> None:
    with pytest.raises(ValueError):
        make_event(correlation_id="")


def test_event_render_text_includes_type_summary_and_detail() -> None:
    text = make_event(event_type="X", summary="Y", detail={"k": "v"}).render_text()
    assert "[X] Y" in text
    assert "k=v" in text


def test_outcome_overall_success_true_when_all_results_succeed() -> None:
    outcome = NotificationOutcome(
        event_type="X", correlation_id="C1",
        results=(SendResult(chat_id="1", success=True, attempts=1), SendResult(chat_id="2", success=True, attempts=1)),
    )
    assert outcome.overall_success is True


def test_outcome_overall_success_false_when_any_result_fails() -> None:
    outcome = NotificationOutcome(
        event_type="X", correlation_id="C1",
        results=(SendResult(chat_id="1", success=True, attempts=1), SendResult(chat_id="2", success=False, attempts=3)),
    )
    assert outcome.overall_success is False


def test_outcome_overall_success_false_when_no_results() -> None:
    outcome = NotificationOutcome(event_type="X", correlation_id="C1", results=())
    assert outcome.overall_success is False
