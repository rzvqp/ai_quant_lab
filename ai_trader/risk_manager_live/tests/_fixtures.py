"""Shared fixture builders for `risk_manager_live` tests."""

from __future__ import annotations

from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification, TradeProposal
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000


def make_proposal(**overrides: object) -> TradeProposal:
    kwargs: dict[str, object] = {
        "proposal_id": "P1", "correlation_id": "C1", "strategy_id": "S1", "symbol": "XAUUSD",
        "direction": Direction.LONG, "entry": 2000.0, "stop": 1990.0, "target": 2020.0, "as_of": AS_OF,
    }
    kwargs.update(overrides)
    return TradeProposal(**kwargs)  # type: ignore[arg-type]


def make_account(**overrides: object) -> AccountState:
    kwargs: dict[str, object] = {
        "as_of": AS_OF, "currency": "USD", "balance": 200_000.0, "equity": 200_000.0,
        "margin_used": 0.0, "margin_free": 200_000.0, "margin_level": None, "leverage": 500.0,
        "is_demo": True,
    }
    kwargs.update(overrides)
    return AccountState(**kwargs)  # type: ignore[arg-type]


def make_portfolio(**overrides: object) -> PortfolioState:
    kwargs: dict[str, object] = {"as_of": AS_OF, "equity": 200_000.0, "equity_high_water_mark": 200_000.0}
    kwargs.update(overrides)
    return PortfolioState(**kwargs)  # type: ignore[arg-type]


def make_instrument(**overrides: object) -> InstrumentSpecification:
    kwargs: dict[str, object] = {
        "symbol": "XAUUSD", "tick_size": 0.01, "lot_step": 0.01, "min_volume": 0.01, "max_volume": 100.0,
        "contract_size": 100.0, "point_value": 1.0, "margin_currency": "USD",
    }
    kwargs.update(overrides)
    return InstrumentSpecification(**kwargs)  # type: ignore[arg-type]


def make_snapshot(**overrides: object) -> SymbolRiskSnapshot:
    kwargs: dict[str, object] = {
        "atr": 5.0, "atr_rolling_median": 5.0, "current_spread": 0.5, "liquidity_proxy": 1.0,
        "is_weekend_gap": False, "bars_since_gap": 100, "is_past_friday_cutoff": False,
        "is_near_session_close": False, "minutes_to_high_impact_event": 999.0,
        "data_quality": DataQualityLevel.OK,
    }
    kwargs.update(overrides)
    return SymbolRiskSnapshot(**kwargs)  # type: ignore[arg-type]


def make_risk_context(symbol: str = "XAUUSD", snapshot: SymbolRiskSnapshot | None = None) -> RiskContext:
    return RiskContext(as_of=AS_OF, per_symbol={symbol: snapshot if snapshot is not None else make_snapshot()})


def make_config(symbol: str = "XAUUSD") -> RiskConfig:
    """A RiskConfig with the two "unconfigured -> fail-closed" filters (spread/liquidity) and the
    sizing point_value populated for XAUUSD -- matching what a real deployment would configure, so the
    ALLOW path is actually reachable in tests, not perpetually fail-closed on missing config."""
    config = RiskConfig()
    config.filters.reference_spread[symbol] = 1.0
    config.filters.liquidity_floor[symbol] = 0.5
    config.sizing.point_value[symbol] = 1.0
    return config
