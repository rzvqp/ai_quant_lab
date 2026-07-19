"""Data availability evidence -- Phase 7 Checkpoint 6. A strategy's edge cannot be evaluated at
all if the timeframe(s) its own Contract declares as required have no bars in the current
context -- checked before any other evidence dimension is even meaningful.
"""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EvidenceContribution
from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_runtime import context_access
from ai_trader.strategy_runtime.context_access import MarketContext

DIMENSION = "data_availability"


def _required_timeframes(contract: Contract) -> tuple[str, ...]:
    timeframes = {contract.execution.timeframe}
    for spec in contract.semantics.required_data:
        timeframes.add(spec.timeframe)
        if spec.htf:
            timeframes.update(spec.htf)
    return tuple(sorted(timeframes))


def evaluate_data_availability(contract: Contract, context: MarketContext) -> EdgeEvidenceItem:
    required = _required_timeframes(contract)
    missing = tuple(tf for tf in required if not context_access.bars(context, tf))
    if missing:
        return EdgeEvidenceItem(
            DIMENSION, EvidenceContribution.CONTRADICTS,
            f"required timeframe(s) {missing} have no bars in the current context -- cannot "
            f"evaluate this strategy at all",
        )
    return EdgeEvidenceItem(
        DIMENSION, EvidenceContribution.SUPPORTS,
        f"all required timeframe(s) {required} have bars available",
    )
