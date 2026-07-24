from __future__ import annotations

from ai_trader.portfolio_manager_live.engine import evaluate_portfolio_authorization
from ai_trader.portfolio_manager_live.tests._fixtures import (
    make_config,
    make_daily_state,
    make_portfolio,
    make_position,
    make_request,
    make_risk_config,
)
from ai_trader.signal_engine.types import Direction


def test_well_formed_request_with_empty_portfolio_is_approved() -> None:
    decision = evaluate_portfolio_authorization(
        make_request(), make_portfolio(), make_daily_state(), make_risk_config(),
    )
    assert decision.approved is True
    assert decision.exposure_snapshot is not None
    assert decision.exposure_snapshot.total_exposure_pct == 0.01


def test_total_exposure_breach_denies() -> None:
    config = make_config(max_total_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_TOTAL_EXPOSURE",)


def test_reserved_capital_breach_denies() -> None:
    config = make_config(reserved_capital_pct=0.999)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_RESERVED_CAPITAL",)


def test_direction_exposure_breach_denies() -> None:
    config = make_config(max_direction_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_DIRECTION_EXPOSURE",)


def test_strategy_exposure_breach_denies() -> None:
    config = make_config(max_strategy_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_STRATEGY_EXPOSURE",)


def test_session_exposure_breach_denies() -> None:
    daily_state = make_daily_state(session_heat_used_pct={"LONDON": 0.145})
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), daily_state, make_risk_config())
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_SESSION_EXPOSURE",)


def test_asset_class_exposure_breach_denies() -> None:
    config = make_config(max_asset_class_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_ASSET_CLASS_EXPOSURE",)


def test_long_short_conflict_on_same_symbol_denies() -> None:
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAUUSD", direction=Direction.SHORT, risk_pct=0.01),
    ))
    decision = evaluate_portfolio_authorization(make_request(direction=Direction.LONG, symbol="XAUUSD"), portfolio, make_daily_state(), make_risk_config())
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_LONG_SHORT_CONFLICT",)


def test_long_short_conflict_can_be_allowed_via_config() -> None:
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAUUSD", direction=Direction.SHORT, risk_pct=0.01),
    ))
    config = make_config(allow_long_short_conflict=True)
    decision = evaluate_portfolio_authorization(make_request(direction=Direction.LONG, symbol="XAUUSD"), portfolio, make_daily_state(), make_risk_config(), config)
    assert decision.approved is True


def test_same_direction_same_symbol_is_not_a_conflict() -> None:
    portfolio = make_portfolio(open_positions=(
        make_position(symbol="XAUUSD", direction=Direction.LONG, risk_pct=0.01),
    ))
    decision = evaluate_portfolio_authorization(make_request(direction=Direction.LONG, symbol="XAUUSD"), portfolio, make_daily_state(), make_risk_config())
    assert decision.approved is True


def test_portfolio_heat_breach_denies() -> None:
    config = make_config(max_portfolio_heat_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_HEAT",)


def test_daily_trade_count_breach_denies() -> None:
    daily_state = make_daily_state(trades_opened_today=20)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), daily_state, make_risk_config())
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_DAILY_TRADE_COUNT",)


def test_daily_heat_breach_denies() -> None:
    daily_state = make_daily_state(daily_heat_used_pct=0.195)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), daily_state, make_risk_config())
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_DAILY_HEAT",)


def test_multiple_breaches_all_collected_never_short_circuited() -> None:
    config = make_config(max_total_exposure_pct=0.005, max_direction_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert decision.approved is False
    assert "PORTFOLIO_TOTAL_EXPOSURE" in decision.reason_codes
    assert "PORTFOLIO_DIRECTION_EXPOSURE" in decision.reason_codes


def test_denied_decision_carries_full_trace_and_snapshot() -> None:
    config = make_config(max_total_exposure_pct=0.005)
    decision = evaluate_portfolio_authorization(make_request(), make_portfolio(), make_daily_state(), make_risk_config(), config)
    assert len(decision.calculation_trace) == 10  # every check runs, never short-circuited
    assert decision.exposure_snapshot is not None


def test_malformed_portfolio_state_fails_closed_not_raises() -> None:
    decision = evaluate_portfolio_authorization(
        make_request(), None, make_daily_state(), make_risk_config(),  # type: ignore[arg-type]
    )
    assert decision.approved is False
    assert decision.reason_codes == ("PORTFOLIO_STATE_UNAVAILABLE",)
    assert decision.exposure_snapshot is None
