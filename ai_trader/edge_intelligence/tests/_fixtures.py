"""Shared fixture builders for Edge Intelligence unit tests -- reuses
:mod:`ai_trader.market_intelligence.tests._fixtures` for ``MarketContext``/snapshot construction
and :mod:`ai_trader.strategy_manager.tests.fixtures.contracts` for synthetic, schema-conformant
Contract construction -- no hand-duplicated fixture logic.
"""

from __future__ import annotations

from typing import Any

from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.market_intelligence.tests._fixtures import AS_OF, make_context
from ai_trader.market_intelligence.types import MarketIntelligenceSnapshot
from ai_trader.strategy_manager.contract import Contract, parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

__all__ = ["AS_OF", "make_context", "make_contract", "make_snapshot"]


def make_contract(
    id: str = "S1",
    timeframe: str = "M15",
    sessions: str = "All sessions",
    long_short: str = "BOTH",
    required_data: list[dict[str, Any]] | None = None,
) -> Contract:
    data = make_contract_dict(id=id, required_data=required_data)
    data["execution"]["timeframe"] = timeframe
    data["execution"]["sessions"] = sessions
    data["execution"]["long_short"] = long_short
    return parse_contract(data)


def make_snapshot(**context_kwargs: Any) -> MarketIntelligenceSnapshot:
    return build_market_intelligence(make_context(**context_kwargs))
