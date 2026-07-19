"""Unit tests for the timestamp policy -- :func:`ai_trader.context_memory.validation.as_of_from_datetime`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ai_trader.context_memory.validation import ContextMemoryValidationError, as_of_from_datetime


def test_naive_datetime_is_rejected() -> None:
    naive = datetime(2026, 1, 15, 12, 0, 0)
    with pytest.raises(ContextMemoryValidationError, match="naive datetime"):
        as_of_from_datetime(naive)


def test_utc_aware_datetime_converts_correctly() -> None:
    dt = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert as_of_from_datetime(dt) == int(dt.timestamp())


def test_non_utc_aware_datetime_is_converted_to_utc() -> None:
    plus_two = timezone(timedelta(hours=2))
    dt_local = datetime(2026, 1, 15, 14, 0, 0, tzinfo=plus_two)  # == 12:00 UTC
    dt_utc = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert as_of_from_datetime(dt_local) == as_of_from_datetime(dt_utc)


def test_result_is_a_plain_int() -> None:
    dt = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    result = as_of_from_datetime(dt)
    assert isinstance(result, int)
