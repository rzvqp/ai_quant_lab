"""Decision-level eligibility gates -- Phase 7 Checkpoint 7. Every currently-PRESENT edge (Edge
Intelligence's own verdict) is further checked against a small, disclosed set of already-declared
Contract fields (never invented, never re-scored) before it may become an ACCEPT candidate. A PRESENT
edge that fails one of these gates is REJECT here -- not the same statement as Edge Intelligence's own
ABSENT/POSSIBLE, which is about whether the edge exists in the market right now, not whether the
strategy itself is a legitimate execution candidate.
"""

from __future__ import annotations

from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome, ResearchStats
from ai_trader.edge_intelligence.types import StrategyEdgeReading
from ai_trader.strategy_manager.contract import ConfidenceLevel, Contract, ContractStatus, Maturity, maturity_rank

#: IMPLEMENTATION CHOICE: only a schema-valid, currently-implemented contract is eligible at all --
#: DEPRECATED/DISABLED/INVALID/NOT_IMPLEMENTED are all terminal-or-inactive states, never an execution
#: candidate, regardless of what Edge Intelligence found in the market.
_ELIGIBLE_STATUSES = frozenset({ContractStatus.IMPLEMENTED})

#: IMPLEMENTATION CHOICE: NEGATIVE means the strategy's own research process found active evidence
#: AGAINST it (worse than simply having none yet, NONE) -- both are "no positive evidence demonstrates a
#: genuine statistical edge" (the CEO's own Checkpoint 7 standard) and are therefore excluded here.
_INELIGIBLE_CONFIDENCE = frozenset({ConfidenceLevel.NONE, ConfidenceLevel.NEGATIVE})


def evaluate_candidate(
    strategy_id: str,
    edge_reading: StrategyEdgeReading,
    contract: Contract,
    research_stats: ResearchStats | None,
) -> DecisionCandidate:
    evidence: list[str] = [
        f"edge_intelligence: state={edge_reading.state.value} "
        f"({len(edge_reading.evidence)} disclosed dimensions, see EdgeIntelligenceSnapshot)",
        f"contract: lifecycle.status={contract.lifecycle.status.value}",
        f"contract: lifecycle.maturity={contract.lifecycle.maturity.value} "
        f"(rank {maturity_rank(contract.lifecycle.maturity)})",
        f"contract: evidence.confidence.level={contract.evidence.confidence.level.value}",
    ]
    if research_stats is not None:
        evidence.append(
            f"research: n_trades={research_stats.n_trades}, "
            f"expectancy_r={research_stats.expectancy_r}, win_rate={research_stats.win_rate}, "
            f"sharpe_ratio={research_stats.sharpe_ratio}"
        )

    if contract.lifecycle.status not in _ELIGIBLE_STATUSES:
        return DecisionCandidate(
            strategy_id=strategy_id, outcome=DecisionOutcome.REJECT,
            confidence=contract.evidence.confidence.level.value, evidence=tuple(evidence),
            explanation=f"contract lifecycle.status is {contract.lifecycle.status.value}, not IMPLEMENTED -- not eligible for execution",
        )

    if contract.lifecycle.maturity is Maturity.RETIRED:
        return DecisionCandidate(
            strategy_id=strategy_id, outcome=DecisionOutcome.REJECT,
            confidence=contract.evidence.confidence.level.value, evidence=tuple(evidence),
            explanation="contract lifecycle.maturity is RETIRED -- a terminal withdrawal, never an execution candidate",
        )

    if contract.evidence.confidence.level in _INELIGIBLE_CONFIDENCE:
        return DecisionCandidate(
            strategy_id=strategy_id, outcome=DecisionOutcome.REJECT,
            confidence=contract.evidence.confidence.level.value, evidence=tuple(evidence),
            explanation=f"contract evidence.confidence.level is {contract.evidence.confidence.level.value} -- "
            f"no positive research evidence demonstrates a genuine statistical edge",
        )

    if (
        research_stats is not None
        and research_stats.n_trades > 0
        and research_stats.expectancy_r is not None
        and research_stats.expectancy_r <= 0
    ):
        return DecisionCandidate(
            strategy_id=strategy_id, outcome=DecisionOutcome.REJECT,
            confidence=contract.evidence.confidence.level.value, evidence=tuple(evidence),
            explanation=f"research expectancy_r={research_stats.expectancy_r} over {research_stats.n_trades} trades "
            f"is not positive -- no statistically robust expectancy demonstrated",
        )

    return DecisionCandidate(
        strategy_id=strategy_id, outcome=DecisionOutcome.ACCEPT,
        confidence=contract.evidence.confidence.level.value, evidence=tuple(evidence),
        explanation=(
            f"edge is PRESENT; contract is IMPLEMENTED with maturity={contract.lifecycle.maturity.value} "
            f"and confidence={contract.evidence.confidence.level.value}; no eligibility gate was triggered"
        ),
    )
