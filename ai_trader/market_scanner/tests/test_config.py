"""Unit tests for ai_trader.market_scanner.config.ScannerConfig validation."""

import pytest

from ai_trader.market_scanner.config import ScannerConfig


def test_default_config_is_valid() -> None:
    config = ScannerConfig()
    assert config.base_timeframe == "M15"
    assert config.strict_schema_validation is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("staleness_threshold_ms", 0),
        ("staleness_threshold_ms", -1),
        ("history_buffer_bars", 0),
        ("max_gap_bars_before_degraded", 0),
    ],
)
def test_rejects_invalid_values(field: str, value: int) -> None:
    with pytest.raises(ValueError):
        ScannerConfig(**{field: value})
