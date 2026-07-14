"""Tests for :mod:`ai_trader.risk_manager.config`."""

from __future__ import annotations

import pytest

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.scoring_engine.types import Quality


class TestRiskConfig:
    def test_defaults(self) -> None:
        cfg = RiskConfig()
        assert cfg.risk_engine_version == "1.0.0"
        assert cfg.risk_schema_version == "1.0.0"
        assert cfg.risk_policy_version == "1.0.0"
        assert cfg.portfolio_limits.max_positions == 5
        assert cfg.loss_drawdown.max_daily_loss_pct == 0.03
        assert cfg.sizing.risk_per_trade_pct == 0.005

    def test_each_instance_gets_its_own_sub_configs(self) -> None:
        a = RiskConfig()
        b = RiskConfig()
        assert a.portfolio_limits is not b.portfolio_limits
        assert a.correlation_groups is not b.correlation_groups

    def test_rejects_sub_one_scoring_schema_major(self) -> None:
        with pytest.raises(ValueError):
            RiskConfig(supported_scoring_schema_major=0)

    def test_rejects_sub_one_interface_major(self) -> None:
        with pytest.raises(ValueError):
            RiskConfig(supported_interface_major=0)

    def test_point_value_defaults_to_one(self) -> None:
        cfg = RiskConfig()
        assert cfg.point_value_for("XAUUSD") == 1.0

    def test_point_value_uses_configured_value(self) -> None:
        cfg = RiskConfig()
        cfg.sizing.point_value["XAUUSD"] = 100.0
        assert cfg.point_value_for("XAUUSD") == 100.0

    def test_correlation_group_defaults_to_symbol(self) -> None:
        cfg = RiskConfig()
        assert cfg.correlation_group_for("XAUUSD") == "XAUUSD"

    def test_correlation_group_uses_configured_mapping(self) -> None:
        cfg = RiskConfig()
        cfg.correlation_groups["XAUUSD"] = "METALS"
        assert cfg.correlation_group_for("XAUUSD") == "METALS"

    def test_quality_factor_bounds(self) -> None:
        cfg = RiskConfig()
        assert cfg.quality_factor_for(Quality.POOR) == 0.5
        assert cfg.quality_factor_for(Quality.STRONG) == 1.0
        assert cfg.quality_factor_for(Quality.PREMIUM) == 1.0
        assert 0.5 <= cfg.quality_factor_for(Quality.MODERATE) <= 1.0
