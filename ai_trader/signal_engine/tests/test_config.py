"""Tests for :mod:`ai_trader.signal_engine.config`."""

from __future__ import annotations

import pytest

from ai_trader.signal_engine.config import EngineConfig, SupportedVersions


class TestSupportedVersions:
    def test_defaults(self) -> None:
        v = SupportedVersions()
        assert v.interface_major == 1
        assert v.context_schema_major == 1

    @pytest.mark.parametrize("field_name", ["interface_major", "context_schema_major"])
    def test_rejects_below_one(self, field_name: str) -> None:
        with pytest.raises(ValueError):
            SupportedVersions(**{field_name: 0})

    def test_accepts_higher_majors(self) -> None:
        v = SupportedVersions(interface_major=2, context_schema_major=3)
        assert v.interface_major == 2
        assert v.context_schema_major == 3


class TestEngineConfig:
    def test_defaults(self) -> None:
        cfg = EngineConfig()
        assert cfg.eval_timeout_s == 1.0
        assert cfg.max_workers == 1
        assert cfg.signal_engine_version == "1.0.0"
        assert cfg.signal_schema_version == "1.0.0"
        assert cfg.explanation_schema_version == "1.0.0"

    def test_each_instance_gets_its_own_supported_versions(self) -> None:
        """Regression guard for the mutable-default-argument bug caught during implementation --
        two EngineConfig()s must not share one SupportedVersions instance."""
        a = EngineConfig()
        b = EngineConfig()
        assert a.supported is not b.supported
        a.supported.interface_major = 99
        assert b.supported.interface_major == 1

    def test_rejects_non_positive_timeout(self) -> None:
        with pytest.raises(ValueError):
            EngineConfig(eval_timeout_s=0)
        with pytest.raises(ValueError):
            EngineConfig(eval_timeout_s=-1.0)

    def test_rejects_sub_one_max_workers(self) -> None:
        with pytest.raises(ValueError):
            EngineConfig(max_workers=0)

    def test_accepts_custom_values(self) -> None:
        cfg = EngineConfig(eval_timeout_s=5.0, max_workers=4, signal_engine_version="2.0.0")
        assert cfg.eval_timeout_s == 5.0
        assert cfg.max_workers == 4
        assert cfg.signal_engine_version == "2.0.0"
