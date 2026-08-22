from __future__ import annotations

import pytest

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.execution_mode import (
    ExecutionMode,
    UnknownExecutionModeError,
    resolve_execution_mode,
)


def test_none_resolves_to_disabled() -> None:
    assert resolve_execution_mode(None) is ExecutionMode.DISABLED


def test_explicit_demo_only() -> None:
    assert resolve_execution_mode("MT5_DEMO_ONLY") is ExecutionMode.MT5_DEMO_ONLY


def test_explicit_disabled() -> None:
    assert resolve_execution_mode("DISABLED") is ExecutionMode.DISABLED


def test_enum_value_passthrough() -> None:
    assert resolve_execution_mode(ExecutionMode.MT5_DEMO_ONLY) is ExecutionMode.MT5_DEMO_ONLY


@pytest.mark.parametrize("bad", ["ENABLED", "LIVE", "mt5_demo_only", "", "demo", "unknown"])
def test_unknown_value_fails_closed_never_silently_enables(bad: str) -> None:
    with pytest.raises(UnknownExecutionModeError):
        resolve_execution_mode(bad)
