"""Tests for :mod:`ai_trader.scoring_engine.config`."""

from __future__ import annotations

import pytest

from ai_trader.scoring_engine.config import (
    ComponentWeights,
    RiskPenaltyWeights,
    ScoringConfig,
)


class TestComponentWeights:
    def test_defaults_sum_to_one(self) -> None:
        w = ComponentWeights()
        total = (
            w.signal_strength + w.historical_confidence + w.market_alignment + w.regime_alignment
            + w.confirmation_quality + w.data_quality + w.execution_readiness
        )
        assert total == pytest.approx(1.0)

    def test_rejects_weights_not_summing_to_one(self) -> None:
        with pytest.raises(ValueError):
            ComponentWeights(signal_strength=0.5)


class TestRiskPenaltyWeights:
    def test_defaults_sum_to_one(self) -> None:
        w = RiskPenaltyWeights()
        assert w.drawdown + w.fragile + w.small_sample == pytest.approx(1.0)

    def test_rejects_weights_not_summing_to_one(self) -> None:
        with pytest.raises(ValueError):
            RiskPenaltyWeights(drawdown=0.9)


class TestScoringConfig:
    def test_defaults(self) -> None:
        cfg = ScoringConfig()
        assert cfg.scoring_engine_version == "1.0.0"
        assert cfg.scoring_schema_version == "1.0.0"
        assert cfg.scoring_model_version == "1.0.0"
        assert cfg.supported_signal_schema_major == 1
        assert cfg.supported_interface_major == 1

    def test_each_instance_gets_its_own_sub_configs(self) -> None:
        a = ScoringConfig()
        b = ScoringConfig()
        assert a.weights is not b.weights
        assert a.quality_bands is not b.quality_bands

    def test_rejects_sub_one_signal_schema_major(self) -> None:
        with pytest.raises(ValueError):
            ScoringConfig(supported_signal_schema_major=0)

    def test_rejects_sub_one_interface_major(self) -> None:
        with pytest.raises(ValueError):
            ScoringConfig(supported_interface_major=0)
