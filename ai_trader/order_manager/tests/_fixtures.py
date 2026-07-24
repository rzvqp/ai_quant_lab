"""Shared fixture builders for `order_manager` tests."""

from __future__ import annotations

from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import BrokerCapabilities
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter, capabilities_for
from ai_trader.order_manager.types import ApprovedTradeIntent
from ai_trader.risk_manager.types import PortfolioState
from ai_trader.risk_manager_live.types import InstrumentSpecification
from ai_trader.signal_engine.types import Direction

AS_OF = 1_700_000_000


def make_intent(**overrides: object) -> ApprovedTradeIntent:
    kwargs: dict[str, object] = {
        "proposal_id": "P1", "correlation_id": "C1", "strategy_id": "S1", "symbol": "XAUUSD",
        "direction": Direction.LONG, "entry": 2000.003, "stop": 1990.0, "target": 2020.0, "as_of": AS_OF,
        "volume": 0.2, "monetary_risk": 200.0, "magic_number": 900001, "comment": "S1-P1",
    }
    kwargs.update(overrides)
    return ApprovedTradeIntent(**kwargs)  # type: ignore[arg-type]


def make_instrument(**overrides: object) -> InstrumentSpecification:
    kwargs: dict[str, object] = {
        "symbol": "XAUUSD", "tick_size": 0.01, "lot_step": 0.01, "min_volume": 0.01, "max_volume": 100.0,
        "contract_size": 100.0, "point_value": 1.0, "margin_currency": "USD",
    }
    kwargs.update(overrides)
    return InstrumentSpecification(**kwargs)  # type: ignore[arg-type]


def make_portfolio(**overrides: object) -> PortfolioState:
    kwargs: dict[str, object] = {"as_of": AS_OF, "equity": 200_000.0, "equity_high_water_mark": 200_000.0}
    kwargs.update(overrides)
    return PortfolioState(**kwargs)  # type: ignore[arg-type]


def make_capabilities(symbol: str = "XAUUSD", instrument: InstrumentSpecification | None = None) -> BrokerCapabilities:
    resolved = instrument if instrument is not None else make_instrument(symbol=symbol)
    return capabilities_for(symbol, resolved.tick_size, resolved.lot_step, resolved.min_volume, resolved.max_volume)


def make_connected_adapter(caps: BrokerCapabilities | None = None) -> DryRunBrokerAdapter:
    adapter = DryRunBrokerAdapter(caps if caps is not None else make_capabilities())
    adapter.connect()
    return adapter


def make_ledger() -> OrderLedger:
    return OrderLedger()
