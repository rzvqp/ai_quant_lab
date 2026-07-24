"""Shared fixture builders for `execution_orchestrator` tests. Composes fixture patterns already
established in every prior phase's own test suite (`risk_manager_live`, `portfolio_manager_live`,
`order_manager`, `market_intelligence`)."""

from __future__ import annotations

from pathlib import Path

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_orchestrator.types import CandidateSignal, OrchestratorDependencies
from ai_trader.market_intelligence.tests._fixtures import make_context
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter, capabilities_for
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext, SymbolRiskSnapshot
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.portfolio_manager_live.types import PortfolioDailyState
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000


def make_candidate(**overrides: object) -> CandidateSignal:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "symbol": "XAUUSD", "direction": Direction.LONG, "entry": 2000.0,
        "stop": 1990.0, "target": 2020.0, "session": "LONDON", "magic_number": 900001,
        "comment": "S1-ORCH", "as_of": AS_OF,
    }
    kwargs.update(overrides)
    return CandidateSignal(**kwargs)  # type: ignore[arg-type]


def make_market_context(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {"as_of": AS_OF, "symbol": "XAUUSD", "data_quality_level": "OK"}
    kwargs.update(overrides)
    return make_context(**kwargs)  # type: ignore[arg-type]


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


def make_risk_context(symbol: str = "XAUUSD") -> RiskContext:
    return RiskContext(as_of=AS_OF, per_symbol={symbol: make_snapshot()})


def make_risk_config(symbol: str = "XAUUSD") -> RiskConfig:
    config = RiskConfig()
    config.filters.reference_spread[symbol] = 1.0
    config.filters.liquidity_floor[symbol] = 0.5
    config.sizing.point_value[symbol] = 1.0
    return config


def make_daily_state(**overrides: object) -> PortfolioDailyState:
    kwargs: dict[str, object] = {"as_of": AS_OF}
    kwargs.update(overrides)
    return PortfolioDailyState(**kwargs)  # type: ignore[arg-type]


def make_deps(tmp_path: Path, **overrides: object) -> OrchestratorDependencies:
    instrument = make_instrument()
    caps = capabilities_for("XAUUSD", instrument.tick_size, instrument.lot_step, instrument.min_volume, instrument.max_volume)
    adapter = DryRunBrokerAdapter(caps)
    adapter.connect()
    kwargs: dict[str, object] = {
        "account": make_account(), "portfolio": make_portfolio(), "daily_state": make_daily_state(),
        "instrument": instrument, "risk_context": make_risk_context(), "risk_config": make_risk_config(),
        "broker_caps": caps, "ledger": OrderLedger(), "order_journal": OrderManagerAuditJournal(tmp_path / "journal.jsonl"),
        "adapter": adapter, "repository": None, "telegram_credentials": None,
    }
    kwargs.update(overrides)
    return OrchestratorDependencies(**kwargs)  # type: ignore[arg-type]
