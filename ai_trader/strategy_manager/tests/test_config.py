"""Tests for :mod:`ai_trader.strategy_manager.config`."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.strategy_manager.config import DEFAULT_LIBRARY_PATH, ManagerConfig, SupportedVersions


class TestSupportedVersions:
    def test_defaults(self) -> None:
        s = SupportedVersions()
        assert s.interface_major == 1
        assert s.runtime_api_major == 1
        assert s.feature_dictionary_major == 1

    @pytest.mark.parametrize("field", ["interface_major", "runtime_api_major", "feature_dictionary_major"])
    def test_rejects_zero_or_negative(self, field: str) -> None:
        with pytest.raises(ValueError):
            SupportedVersions(**{field: 0})


class TestManagerConfig:
    def test_defaults(self) -> None:
        cfg = ManagerConfig()
        assert cfg.library_path == DEFAULT_LIBRARY_PATH
        assert cfg.symbols == frozenset({"XAUUSD"})
        assert cfg.auto_admit_min_maturity is None
        assert cfg.stale_after_days == 180
        assert cfg.deprecated_field_paths == frozenset()

    def test_default_library_path_points_at_knowledge_strategies(self) -> None:
        assert DEFAULT_LIBRARY_PATH.name == "strategies"
        assert DEFAULT_LIBRARY_PATH.parent.name == "knowledge"

    def test_custom_library_path(self, tmp_path: Path) -> None:
        cfg = ManagerConfig(library_path=tmp_path)
        assert cfg.library_path == tmp_path

    def test_rejects_non_positive_stale_after_days(self) -> None:
        with pytest.raises(ValueError):
            ManagerConfig(stale_after_days=0)

    def test_rejects_empty_symbols(self) -> None:
        with pytest.raises(ValueError):
            ManagerConfig(symbols=frozenset())

    def test_accepts_valid_auto_admit_maturity(self) -> None:
        cfg = ManagerConfig(auto_admit_min_maturity="EXPLORATORY")
        assert cfg.auto_admit_min_maturity == "EXPLORATORY"

    def test_rejects_invalid_auto_admit_maturity(self) -> None:
        with pytest.raises(ValueError):
            ManagerConfig(auto_admit_min_maturity="NOT_A_REAL_MATURITY")
