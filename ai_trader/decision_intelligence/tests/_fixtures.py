"""Shared fixture builders for Decision Intelligence unit tests -- reuses
:mod:`ai_trader.edge_intelligence.tests._fixtures` for Contract construction and hand-builds minimal
:class:`~ai_trader.edge_intelligence.types.StrategyEdgeReading` objects directly (no need for a full
Market Intelligence snapshot at this layer -- eligibility/ranking only need the EdgeState and Contract).
"""

from __future__ import annotations

from ai_trader.decision_intelligence.types import ResearchStats
from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EdgeState, EvidenceContribution, StrategyEdgeReading
from ai_trader.strategy_manager.contract import Contract, parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

__all__ = ["make_contract", "make_reading", "make_research_stats"]


def make_contract(
    id: str = "S1", status: str = "IMPLEMENTED", maturity: str = "EXPLORATORY", confidence_level: str = "LOW",
) -> Contract:
    data = make_contract_dict(id=id, status=status, maturity=maturity)
    data["evidence"]["confidence"]["level"] = confidence_level
    return parse_contract(data)


def make_reading(strategy_id: str = "S1", state: EdgeState = EdgeState.PRESENT) -> StrategyEdgeReading:
    return StrategyEdgeReading(
        strategy_id=strategy_id, as_of=1_700_000_000, state=state,
        evidence=(EdgeEvidenceItem("test_dimension", EvidenceContribution.SUPPORTS, "test evidence"),),
    )


def make_research_stats(
    n_trades: int = 10, win_rate: float | None = 0.5, expectancy_r: float | None = 0.2,
    sharpe_ratio: float | None = 1.0,
) -> ResearchStats:
    return ResearchStats(n_trades=n_trades, win_rate=win_rate, expectancy_r=expectancy_r, sharpe_ratio=sharpe_ratio)
