"""Shared fixture builders for `portfolio_manager_live` tests."""

from __future__ import annotations

from ai_trader.portfolio_manager_live.types import PortfolioAuthorizationRequest, PortfolioDailyState, PortfolioManagerConfig
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import OpenPosition, PortfolioState
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000


def make_request(**overrides: object) -> PortfolioAuthorizationRequest:
    kwargs: dict[str, object] = {
        "proposal_id": "P1", "correlation_id": "C1", "strategy_id": "S1", "symbol": "XAUUSD",
        "direction": Direction.LONG, "session": "LONDON", "monetary_risk": 1000.0,
        "approved_risk_pct": 0.01, "as_of": AS_OF,
    }
    kwargs.update(overrides)
    return PortfolioAuthorizationRequest(**kwargs)  # type: ignore[arg-type]


def make_position(**overrides: object) -> OpenPosition:
    kwargs: dict[str, object] = {
        "symbol": "EURUSD", "strategy_id": "S2", "direction": Direction.LONG, "size_units": 1.0,
        "entry_price": 1.1, "opened_bars_ago": 5, "risk_pct": 0.01,
    }
    kwargs.update(overrides)
    return OpenPosition(**kwargs)  # type: ignore[arg-type]


def make_portfolio(**overrides: object) -> PortfolioState:
    kwargs: dict[str, object] = {"as_of": AS_OF, "equity": 200_000.0, "equity_high_water_mark": 200_000.0}
    kwargs.update(overrides)
    return PortfolioState(**kwargs)  # type: ignore[arg-type]


def make_daily_state(**overrides: object) -> PortfolioDailyState:
    kwargs: dict[str, object] = {"as_of": AS_OF}
    kwargs.update(overrides)
    return PortfolioDailyState(**kwargs)  # type: ignore[arg-type]


def make_config(**overrides: object) -> PortfolioManagerConfig:
    kwargs: dict[str, object] = {}
    kwargs.update(overrides)
    return PortfolioManagerConfig(**kwargs)  # type: ignore[arg-type]


def make_risk_config() -> RiskConfig:
    return RiskConfig()
