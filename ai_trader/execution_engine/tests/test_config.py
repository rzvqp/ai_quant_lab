"""Tests for :mod:`ai_trader.execution_engine.config`."""

from __future__ import annotations

import pytest

from ai_trader.execution_engine.config import ExecConfig


class TestExecConfigDefaults:
    def test_default_construction(self) -> None:
        config = ExecConfig()
        assert config.supported_risk_schema_major == 1
        assert config.order_schema_version == "1.0.0"

    def test_invalid_supported_risk_schema_major_raises(self) -> None:
        with pytest.raises(ValueError):
            ExecConfig(supported_risk_schema_major=0)

    def test_open_and_close_tif_differ_by_default(self) -> None:
        config = ExecConfig()
        assert config.order_mapping.open_time_in_force != config.order_mapping.close_time_in_force
