"""Decision Intelligence public API -- Phase 7 Checkpoint 7. Answers: "what is the best decision right
now?" Pure and read-only: composes Edge Intelligence's own PRESENT verdicts with each strategy's own
declared Contract (and, optionally, caller-supplied research statistics) into a single, deterministic,
fully explainable recommendation -- never a trade, never an order, never a risk-sizing decision.
Completely independent from Signal Engine, Scoring Engine, Risk Manager, Shadow Evidence, Execution
Engine, and MT5 -- none of those packages is imported anywhere in this one.
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.decision_intelligence.eligibility import evaluate_candidate
from ai_trader.decision_intelligence.ranking import comparison_notes, rank_candidates
from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome, DecisionReport, ResearchStats
from ai_trader.edge_intelligence.contracts import load_strategy_contracts
from ai_trader.edge_intelligence.engine import evaluate_edges
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.strategy_runtime.context_access import MarketContext, as_of, symbol

#: The literal recommendation string this layer uses whenever no edge deserves execution -- "This is a
#: valid decision" (CEO Checkpoint 7 directive), never an error, never an empty/ambiguous result.
NO_TRADE = "NO TRADE"


def make_decision(
    context: MarketContext,
    research_stats: dict[str, ResearchStats] | None = None,
    library_path: Path | None = None,
) -> DecisionReport:
    """The single public entry point: "what is the best decision right now?" Evaluates every currently
    PRESENT edge (Edge Intelligence's own scope) against a small, disclosed set of eligibility gates,
    ranks the ACCEPTed candidates deterministically, and recommends the single best one -- or NO TRADE
    if none qualifies. ``research_stats`` is an OPTIONAL, caller-supplied mapping (this layer never
    computes or fabricates one itself, never imports :mod:`ai_trader.shadow_evidence`)."""
    edge_snapshot = evaluate_edges(context, library_path)
    contracts = load_strategy_contracts(library_path)

    present_ids = sorted(
        sid for sid, reading in edge_snapshot.readings.items() if reading.state is EdgeState.PRESENT
    )
    candidates: list[DecisionCandidate] = [
        evaluate_candidate(
            sid, edge_snapshot.readings[sid], contracts[sid],
            research_stats.get(sid) if research_stats is not None else None,
        )
        for sid in present_ids
        if sid in contracts
    ]

    accepted = tuple(c for c in candidates if c.outcome is DecisionOutcome.ACCEPT)
    ranked = rank_candidates(accepted, contracts, research_stats)
    notes = comparison_notes(ranked, contracts, research_stats)
    recommended = ranked[0].strategy_id if ranked else None

    return DecisionReport(
        symbol=symbol(context), as_of=as_of(context), candidates=tuple(candidates),
        recommended_strategy_id=recommended, comparison_notes=notes,
    )


def recommended_or_no_trade(report: DecisionReport) -> str:
    """The clean, execution-decoupled query surface future modules are meant to call: the recommended
    strategy id, or the literal string ``"NO TRADE"``."""
    return report.recommended_strategy_id if report.recommended_strategy_id is not None else NO_TRADE
