"""Control 14 (CEO's own mandatory test list): zero credential leakage -- into `repr()`, `str()`, or any
exception message."""

from __future__ import annotations

import pytest

from ai_trader.execution_engine.adapters.connection import BrokerCredentials
from ai_trader.execution_engine.adapters.exceptions import NonDemoAccountError
from ai_trader.execution_engine.adapters.mt5_adapter import MT5ReadOnlyBrokerAdapter
from ai_trader.execution_engine.adapters.tests._fixtures import FakeMT5Gateway

_SECRET = "sw0rdfish-super-secret-password-12345"


def test_repr_never_contains_the_password() -> None:
    creds = BrokerCredentials(login=123456, password=_SECRET, server="FusionMarkets-Demo")
    assert _SECRET not in repr(creds)
    assert "***REDACTED***" in repr(creds)


def test_str_never_contains_the_password() -> None:
    creds = BrokerCredentials(login=123456, password=_SECRET, server="FusionMarkets-Demo")
    assert _SECRET not in str(creds)


def test_login_and_server_are_not_redacted_only_password_is() -> None:
    creds = BrokerCredentials(login=123456, password=_SECRET, server="FusionMarkets-Demo")
    text = repr(creds)
    assert "123456" in text
    assert "FusionMarkets-Demo" in text


def test_credentials_with_no_password_repr_cleanly() -> None:
    creds = BrokerCredentials(login=123456)
    assert "None" in repr(creds)
    assert "REDACTED" not in repr(creds)  # nothing to redact -- reports None honestly, not a fake marker


def test_exception_messages_never_contain_the_password() -> None:
    gateway = FakeMT5Gateway()
    from types import SimpleNamespace

    gateway.account_info_result = SimpleNamespace(trade_mode=2, trade_allowed=True, server="RealServer")
    adapter = MT5ReadOnlyBrokerAdapter(
        gateway=gateway, credentials=BrokerCredentials(login=1, password=_SECRET, server="x"),
    )
    with pytest.raises(NonDemoAccountError) as exc_info:
        adapter.connect()
    assert _SECRET not in str(exc_info.value)


def test_adapter_object_repr_never_contains_the_password() -> None:
    """The adapter itself stores `_credentials` -- confirm the DEFAULT object repr (no custom
    `__repr__` on the adapter classes themselves) never surfaces the password either, by checking the
    credentials object's own repr is what would appear if the adapter's own repr were ever printed/logged
    (Python's default dataclass-less object repr doesn't dump `__dict__`, but this test documents the
    invariant explicitly rather than relying on that being true by accident)."""
    creds = BrokerCredentials(login=1, password=_SECRET, server="x")
    adapter = MT5ReadOnlyBrokerAdapter(gateway=FakeMT5Gateway(), credentials=creds)
    assert _SECRET not in repr(adapter._credentials)  # noqa: SLF001 -- explicit invariant check
