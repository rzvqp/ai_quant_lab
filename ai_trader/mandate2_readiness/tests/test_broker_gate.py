"""`BrokerOrderSubmissionGate` tests -- proves DISABLED is the only reachable default, and that nothing
short of an explicit, source-visible `enabled=True` can ever produce an enabled gate."""

from __future__ import annotations

import dataclasses
import os

import pytest

from ai_trader.mandate2_readiness.broker_gate import (
    BrokerOrderSubmissionDisabledError,
    BrokerOrderSubmissionGate,
)


def test_default_construction_is_disabled() -> None:
    gate = BrokerOrderSubmissionGate()
    assert gate.enabled is False


def test_authorize_raises_when_disabled() -> None:
    gate = BrokerOrderSubmissionGate()
    with pytest.raises(BrokerOrderSubmissionDisabledError):
        gate.authorize()


def test_authorize_error_message_carries_the_reason() -> None:
    gate = BrokerOrderSubmissionGate(reason="VE_HANDOFF_PASS not yet issued")
    with pytest.raises(BrokerOrderSubmissionDisabledError, match="VE_HANDOFF_PASS not yet issued"):
        gate.authorize()


def test_authorize_raises_nothing_when_explicitly_enabled() -> None:
    gate = BrokerOrderSubmissionGate(enabled=True, reason="test-only")
    gate.authorize()  # no exception -- this IS the assertion


def test_gate_is_frozen_no_setter_can_flip_it_after_construction() -> None:
    gate = BrokerOrderSubmissionGate()
    with pytest.raises(dataclasses.FrozenInstanceError):
        gate.enabled = True  # type: ignore[misc]


def test_no_environment_variable_influences_the_default() -> None:
    """The failure mode this rules out structurally: a missing or misspelled env var silently defaulting
    to "on". `BrokerOrderSubmissionGate()` reads no environment at all -- proven by constructing it under
    a variety of hostile `os.environ` states and confirming the result is identical every time."""
    hostile_environments = [
        {},
        {"BROKER_ORDER_SUBMISSION": "true"},
        {"BROKER_ORDER_SUBMISSION": "1"},
        {"BROKER_ORDER_SUBMISSION_ENABLED": "yes"},
        {"ORDER_SUBMISSION": "enabled"},
    ]
    original = dict(os.environ)
    try:
        for env in hostile_environments:
            os.environ.clear()
            os.environ.update(env)
            assert BrokerOrderSubmissionGate().enabled is False
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_two_independently_constructed_default_gates_are_equal() -> None:
    """Not load-bearing on its own, but confirms there is exactly ONE disabled state, not several subtly
    different ones a caller could confuse -- `enabled=False` with the default reason is the whole
    universe of "disabled"."""
    assert BrokerOrderSubmissionGate() == BrokerOrderSubmissionGate()
