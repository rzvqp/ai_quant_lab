"""Controls 12-13 (CEO's own mandatory test list): bounded retry, idempotency for the common
foundation. Uses `NullBrokerAdapter`'s own injectable failure modes -- no real clock/network needed
(`_sleep` is overridden to a no-op so these tests run instantly)."""

from __future__ import annotations

import pytest

from ai_trader.execution_engine.adapters.base import RetryPolicy
from ai_trader.execution_engine.adapters.exceptions import RetryExhaustedError
from ai_trader.execution_engine.adapters.null_adapter import NullBrokerAdapter
from ai_trader.execution_engine.adapters.tests._fixtures_order import make_order_request


def _adapter_with_no_real_sleep(**kwargs: object) -> NullBrokerAdapter:
    adapter = NullBrokerAdapter(**kwargs)  # type: ignore[arg-type]
    adapter._sleep = lambda _seconds: None  # noqa: SLF001 -- test-only, avoids a real wall-clock wait
    return adapter


def test_retry_succeeds_within_bound() -> None:
    adapter = _adapter_with_no_real_sleep(
        simulated_connect_failures=2, retry_policy=RetryPolicy(max_attempts=3),
    )
    result = adapter.connect()
    assert result.accepted
    assert adapter.is_connected()


def test_retry_exhausted_raises_typed_error_never_hangs() -> None:
    adapter = _adapter_with_no_real_sleep(
        simulated_connect_failures=10, retry_policy=RetryPolicy(max_attempts=3),
    )
    with pytest.raises(RetryExhaustedError):
        adapter.connect()
    assert not adapter.is_connected()


def test_retry_is_bounded_not_infinite() -> None:
    """A genuinely infinite-retry bug would hang this test forever; completing at all (under the test
    runner's own timeout) is itself part of the proof, in addition to the explicit attempt count check."""
    policy = RetryPolicy(max_attempts=4, base_delay_seconds=0.0)
    adapter = _adapter_with_no_real_sleep(simulated_connect_failures=100, retry_policy=policy)
    with pytest.raises(RetryExhaustedError) as exc_info:
        adapter.connect()
    assert f"after {policy.max_attempts} attempt" in str(exc_info.value)


def test_retry_policy_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(base_delay_seconds=-1.0)
    with pytest.raises(ValueError):
        RetryPolicy(backoff_multiplier=0.5)


def test_permanent_failure_is_not_retried() -> None:
    """`always_disconnected=True` returns a non-retryable ConnectionResult(accepted=False, ...) directly
    -- not a TransientOperationError -- so it must NOT trigger the retry loop at all."""
    adapter = _adapter_with_no_real_sleep(always_disconnected=True, retry_policy=RetryPolicy(max_attempts=5))
    result = adapter.connect()
    assert not result.accepted
    assert result.reason == "SIMULATED_PERMANENT_FAILURE"
    assert not adapter.is_connected()


def test_submit_order_idempotent_for_same_client_order_id() -> None:
    adapter = NullBrokerAdapter()
    adapter.connect()
    order = make_order_request(client_order_id="IDEMPOTENT-CID-1")

    first_ack = adapter.submit_order(order)
    second_ack = adapter.submit_order(order)  # simulates a client-side retry after a false timeout

    assert first_ack.accepted
    assert first_ack == second_ack  # the ORIGINAL ack is returned, not a second, independent submission
    open_orders = adapter.query_open_orders()
    assert sum(1 for s in open_orders if s.client_order_id == "IDEMPOTENT-CID-1") == 1  # never doubled


def test_different_client_order_ids_are_independent() -> None:
    adapter = NullBrokerAdapter()
    adapter.connect()
    adapter.submit_order(make_order_request(client_order_id="CID-A"))
    adapter.submit_order(make_order_request(client_order_id="CID-B"))
    open_orders = {s.client_order_id for s in adapter.query_open_orders()}
    assert open_orders == {"CID-A", "CID-B"}
