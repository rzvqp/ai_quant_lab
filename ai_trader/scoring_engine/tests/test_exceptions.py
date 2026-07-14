"""Tests for :mod:`ai_trader.scoring_engine.exceptions`."""

from __future__ import annotations

from ai_trader.scoring_engine.exceptions import (
    EngineNotConfiguredError,
    SchemaLoadError,
    ScoringEngineError,
)


class TestExceptionHierarchy:
    def test_engine_not_configured_is_a_scoring_engine_error(self) -> None:
        assert issubclass(EngineNotConfiguredError, ScoringEngineError)

    def test_schema_load_error_is_a_scoring_engine_error(self) -> None:
        assert issubclass(SchemaLoadError, ScoringEngineError)

    def test_scoring_engine_error_is_an_exception(self) -> None:
        assert issubclass(ScoringEngineError, Exception)

    def test_instances_carry_their_message(self) -> None:
        err = EngineNotConfiguredError("configure() must be called first")
        assert "configure()" in str(err)
