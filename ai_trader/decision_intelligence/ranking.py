"""Deterministic ranking among ACCEPTed candidates -- Phase 7 Checkpoint 7. A single, disclosed
tie-break chain, never a weighted score or learned model: contract maturity first, then declared
research confidence, then (if supplied) historical expectancy_r, then strategy_id as the final,
always-available deterministic tie-break. Also produces the pairwise "why stronger or weaker than
competing edges" narrative the CEO's own directive requires.
"""

from __future__ import annotations

from ai_trader.decision_intelligence.types import DecisionCandidate, ResearchStats
from ai_trader.strategy_manager.contract import Contract, maturity_rank

#: IMPLEMENTATION CHOICE: no ``confidence_rank`` helper exists in strategy_manager -- this ladder is
#: this package's own disclosed ordering (never tuned against results). NEGATIVE ranks below NONE (see
#: eligibility.py) but both are already excluded from ACCEPT, so only VERY_LOW..HIGH are ever compared
#: here in practice.
_CONFIDENCE_RANK = {"NEGATIVE": 0, "NONE": 1, "VERY_LOW": 2, "LOW": 3, "MEDIUM": 4, "HIGH": 5}


def _expectancy(strategy_id: str, research_stats: dict[str, ResearchStats] | None) -> float | None:
    if research_stats is None or strategy_id not in research_stats:
        return None
    return research_stats[strategy_id].expectancy_r


def _sort_key(
    candidate: DecisionCandidate, contracts: dict[str, Contract], research_stats: dict[str, ResearchStats] | None,
) -> tuple[int, int, bool, float, str]:
    contract = contracts[candidate.strategy_id]
    expectancy = _expectancy(candidate.strategy_id, research_stats)
    return (
        -maturity_rank(contract.lifecycle.maturity),
        -_CONFIDENCE_RANK[contract.evidence.confidence.level.value],
        expectancy is None,
        -(expectancy if expectancy is not None else 0.0),
        candidate.strategy_id,
    )


def rank_candidates(
    accepted: tuple[DecisionCandidate, ...],
    contracts: dict[str, Contract],
    research_stats: dict[str, ResearchStats] | None,
) -> tuple[DecisionCandidate, ...]:
    """Every ACCEPT candidate, best-first, by the disclosed tie-break chain above."""
    return tuple(sorted(accepted, key=lambda c: _sort_key(c, contracts, research_stats)))


def _first_differentiator(
    a: DecisionCandidate, b: DecisionCandidate, contracts: dict[str, Contract], research_stats: dict[str, ResearchStats] | None,
) -> str:
    ca, cb = contracts[a.strategy_id], contracts[b.strategy_id]
    ma, mb = maturity_rank(ca.lifecycle.maturity), maturity_rank(cb.lifecycle.maturity)
    if ma != mb:
        return (
            f"{a.strategy_id} outranks {b.strategy_id}: maturity={ca.lifecycle.maturity.value}(rank {ma}) "
            f"> {cb.lifecycle.maturity.value}(rank {mb})"
        )
    fa = _CONFIDENCE_RANK[ca.evidence.confidence.level.value]
    fb = _CONFIDENCE_RANK[cb.evidence.confidence.level.value]
    if fa != fb:
        return (
            f"{a.strategy_id} outranks {b.strategy_id}: confidence={ca.evidence.confidence.level.value} "
            f"> {cb.evidence.confidence.level.value}"
        )
    ea, eb = _expectancy(a.strategy_id, research_stats), _expectancy(b.strategy_id, research_stats)
    if ea != eb:
        return f"{a.strategy_id} outranks {b.strategy_id}: research expectancy_r={ea} > {eb}"
    return (
        f"{a.strategy_id} and {b.strategy_id} are tied on maturity, confidence, and expectancy_r -- "
        f"{a.strategy_id} ranked first only by strategy_id as the final deterministic tie-break"
    )


def comparison_notes(
    ranked: tuple[DecisionCandidate, ...], contracts: dict[str, Contract], research_stats: dict[str, ResearchStats] | None,
) -> tuple[str, ...]:
    """One note per adjacent pair of ACCEPTed, ranked candidates -- "why stronger or weaker than
    competing edges" (CEO Checkpoint 7 directive), including the honest tied-only-by-strategy_id case."""
    return tuple(
        _first_differentiator(ranked[i], ranked[i + 1], contracts, research_stats)
        for i in range(len(ranked) - 1)
    )
