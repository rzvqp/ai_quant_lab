"""Tests for :mod:`ai_trader.risk_manager.exceptions`."""

from __future__ import annotations

from ai_trader.risk_manager.exceptions import (
    EngineNotConfiguredError,
    RiskManagerError,
    SchemaLoadError,
)


class TestExceptionHierarchy:
    def test_engine_not_configured_is_a_risk_manager_error(self) -> None:
        assert issubclass(EngineNotConfiguredError, RiskManagerError)

    def test_schema_load_error_is_a_risk_manager_error(self) -> None:
        assert issubclass(SchemaLoadError, RiskManagerError)

    def test_risk_manager_error_is_an_exception(self) -> None:
        assert issubclass(RiskManagerError, Exception)

    def test_instances_carry_their_message(self) -> None:
        err = EngineNotConfiguredError("configure() must be called first")
        assert "configure()" in str(err)
