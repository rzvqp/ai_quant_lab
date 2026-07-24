from __future__ import annotations

import pytest

from ai_trader.portfolio_manager_live.tests._fixtures import make_config, make_daily_state, make_request
from ai_trader.portfolio_manager_live.types import PortfolioDecision


def test_request_requires_positive_approved_risk_pct() -> None:
    with pytest.raises(ValueError):
        make_request(approved_risk_pct=0.0)


def test_request_requires_concrete_direction_type() -> None:
    with pytest.raises(TypeError):
        make_request(direction="LONG")


def test_request_requires_nonempty_session() -> None:
    with pytest.raises(ValueError):
        make_request(session="")


def test_daily_state_rejects_negative_trades_opened() -> None:
    with pytest.raises(ValueError):
        make_daily_state(trades_opened_today=-1)


def test_config_rejects_reserved_capital_out_of_range() -> None:
    with pytest.raises(ValueError):
        make_config(reserved_capital_pct=1.0)


def test_config_asset_class_for_defaults_to_unclassified() -> None:
    config = make_config()
    assert config.asset_class_for("XAUUSD") == "UNCLASSIFIED"


def test_config_asset_class_for_uses_declared_mapping() -> None:
    config = make_config(asset_class_map={"XAUUSD": "METALS"})
    assert config.asset_class_for("XAUUSD") == "METALS"


def test_approved_decision_requires_nonempty_trace() -> None:
    with pytest.raises(ValueError):
        PortfolioDecision(approved=True, reason_codes=(), exposure_snapshot=None, warnings=(), calculation_trace=())


def test_denied_decision_requires_reason_codes() -> None:
    with pytest.raises(ValueError):
        PortfolioDecision(approved=False, reason_codes=(), exposure_snapshot=None, warnings=(), calculation_trace=())
