from __future__ import annotations

from ai_trader.portfolio_manager_live.aggregation import build_exposure_snapshot, find_long_short_conflicts
from ai_trader.portfolio_manager_live.tests._fixtures import make_config, make_portfolio, make_position, make_request, make_risk_config
from ai_trader.signal_engine.types import Direction


def test_snapshot_includes_pending_request_even_with_empty_portfolio() -> None:
    snapshot = build_exposure_snapshot(make_request(approved_risk_pct=0.02), make_portfolio(), make_config())
    assert snapshot.total_exposure_pct == 0.02
    assert snapshot.per_symbol_exposure_pct["XAUUSD"] == 0.02
    assert snapshot.per_direction_exposure_pct["LONG"] == 0.02
    assert snapshot.per_strategy_exposure_pct["S1"] == 0.02


def test_snapshot_aggregates_existing_positions_plus_pending() -> None:
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAUUSD", strategy_id="S1", direction=Direction.LONG, risk_pct=0.01),
    ))
    snapshot = build_exposure_snapshot(make_request(approved_risk_pct=0.01), portfolio, make_config())
    assert snapshot.per_symbol_exposure_pct["XAUUSD"] == 0.02
    assert snapshot.per_strategy_exposure_pct["S1"] == 0.02
    assert snapshot.total_exposure_pct == 0.02


def test_snapshot_asset_class_bucket_uses_config_mapping() -> None:
    config = make_config(asset_class_map={"XAUUSD": "METALS"})
    snapshot = build_exposure_snapshot(make_request(), make_portfolio(), config)
    assert snapshot.per_asset_class_exposure_pct == {"METALS": 0.01}


def test_snapshot_available_capital_reflects_reserved_capital() -> None:
    config = make_config(reserved_capital_pct=0.25)
    snapshot = build_exposure_snapshot(make_request(), make_portfolio(), config)
    assert snapshot.available_capital_pct == 0.75


def test_no_conflict_when_portfolio_empty() -> None:
    conflicts = find_long_short_conflicts(make_request(), make_portfolio(), make_risk_config())
    assert conflicts == ()


def test_conflict_detected_via_correlation_group() -> None:
    risk_config = make_risk_config()
    risk_config.correlation_groups["XAUUSD"] = "METALS"
    risk_config.correlation_groups["XAGUSD"] = "METALS"
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAGUSD", direction=Direction.SHORT, risk_pct=0.01),
    ))
    conflicts = find_long_short_conflicts(
        make_request(direction=Direction.LONG, symbol="XAUUSD"), portfolio, risk_config,
    )
    assert len(conflicts) == 1


def test_no_conflict_when_same_direction() -> None:
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAUUSD", direction=Direction.LONG, risk_pct=0.01),
    ))
    conflicts = find_long_short_conflicts(
        make_request(direction=Direction.LONG, symbol="XAUUSD"), portfolio, make_risk_config(),
    )
    assert conflicts == ()
