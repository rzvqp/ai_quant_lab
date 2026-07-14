"""Tests for :mod:`ai_trader.execution_engine.exceptions`."""

from __future__ import annotations

import pytest

from ai_trader.execution_engine.exceptions import (
    EngineNotConfiguredError,
    ExecutionEngineError,
    SchemaLoadError,
)


class TestExceptionHierarchy:
    def test_engine_not_configured_is_an_execution_engine_error(self) -> None:
        assert issubclass(EngineNotConfiguredError, ExecutionEngineError)

    def test_schema_load_error_is_an_execution_engine_error(self) -> None:
        assert issubclass(SchemaLoadError, ExecutionEngineError)

    def test_execution_engine_error_is_an_exception(self) -> None:
        assert issubclass(ExecutionEngineError, Exception)

    def test_raisable_and_catchable_by_base(self) -> None:
        with pytest.raises(ExecutionEngineError):
            raise EngineNotConfiguredError("not configured")
