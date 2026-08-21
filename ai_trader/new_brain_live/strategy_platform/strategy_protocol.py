"""The generic strategy plugin interface (AI Trader New Brain Architecture mandate, section 7). Every
future validated strategy implements the SAME `Strategy` protocol -- structural typing (`Protocol`), not
inheritance, so a strategy module needs no import from this package at all beyond this one interface,
keeping the hot-add promise of section 28 (`strategies/<id>/strategy.py` never needs to know about the
Router/Catalog/EV internals, only this one call shape)."""

from __future__ import annotations

import dataclasses
from typing import Mapping, Protocol

from ai_trader.new_brain_live.market_state import MarketState
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class StrategyEvaluationInput:
    """What a strategy receives -- MarketState, plus whatever causal features its OWN contract permits
    (deliberately generic here: a strategy allowed to consume Tower N2/N3/N4 receives them via
    `tower_context`; a REGIME_INDEPENDENT strategy that needs nothing beyond MarketState receives
    `tower_context=None` and must not require it), plus its own immutable configuration."""

    market_state: MarketState
    tower_context: object | None  # bridge._ChainQueryResult-shaped, when the Router fetched one; else None
    config: Mapping[str, object]


class Strategy(Protocol):
    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        """Returns `None` for NO_SIGNAL, or a `TradeHypothesis`. MUST NOT submit a broker order, MUST
        NOT call anything in `mt5_demo_execution`/`execution_engine`/`new_brain_bridge.execution_shadow`
        -- structurally enforced by this package's own AST guard
        (`tests/test_strategies_never_reach_broker.py`), not merely a convention."""
        ...
