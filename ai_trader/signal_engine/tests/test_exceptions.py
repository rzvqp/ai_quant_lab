"""Tests for :mod:`ai_trader.signal_engine.exceptions`."""

from __future__ import annotations

from ai_trader.signal_engine.exceptions import (
    EngineNotConfiguredError,
    SchemaLoadError,
    SignalEngineError,
)


class TestExceptionHierarchy:
    def test_engine_not_configured_is_a_signal_engine_error(self) -> None:
        assert issubclass(EngineNotConfiguredError, SignalEngineError)

    def test_schema_load_error_is_a_signal_engine_error(self) -> None:
        assert issubclass(SchemaLoadError, SignalEngineError)

    def test_signal_engine_error_is_an_exception(self) -> None:
        assert issubclass(SignalEngineError, Exception)

    def test_instances_carry_their_message(self) -> None:
        err = EngineNotConfiguredError("configure() must be called first")
        assert "configure()" in str(err)
