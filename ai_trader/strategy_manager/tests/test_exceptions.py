"""Tests for :mod:`ai_trader.strategy_manager.exceptions`.

``UnknownStrategyError`` and ``IllegalTransitionError`` are never raised by the public API (which
always follows the typed-result convention instead — see each class's own docstring) but exist as
documented internal/defensive tools; these tests only prove they construct correctly.
"""

from __future__ import annotations

import pytest

from ai_trader.strategy_manager.exceptions import (
    IllegalTransitionError,
    ManagerNotConfiguredError,
    SchemaLoadError,
    StrategyApiNotImplementedError,
    StrategyManagerError,
    UnknownStrategyError,
)


class TestExceptionHierarchy:
    @pytest.mark.parametrize("exc_cls", [
        ManagerNotConfiguredError, SchemaLoadError, StrategyManagerError,
    ])
    def test_derive_from_base(self, exc_cls: type[Exception]) -> None:
        assert issubclass(exc_cls, StrategyManagerError)


class TestUnknownStrategyError:
    def test_construction_and_message(self) -> None:
        err = UnknownStrategyError("S999")
        assert err.strategy_id == "S999"
        assert "S999" in str(err)
        assert isinstance(err, StrategyManagerError)


class TestIllegalTransitionError:
    def test_construction_and_message(self) -> None:
        err = IllegalTransitionError("PROMOTED", "NOT_IMPLEMENTED", "some_trigger")
        assert err.from_state == "PROMOTED"
        assert err.to_state == "NOT_IMPLEMENTED"
        assert err.trigger == "some_trigger"
        assert "PROMOTED" in str(err) and "NOT_IMPLEMENTED" in str(err)


class TestStrategyApiNotImplementedError:
    def test_construction_and_message(self) -> None:
        err = StrategyApiNotImplementedError("S1", "generate_signal")
        assert err.strategy_id == "S1"
        assert err.method == "generate_signal"
        assert "generate_signal" in str(err)
        assert isinstance(err, NotImplementedError)
