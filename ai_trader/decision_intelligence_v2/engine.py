"""Decision Intelligence v2 public API -- Phase 7 Checkpoint 14.

`make_decision_v2` answers exactly the same question v1 already answers -- "what is the best decision
right now?" -- and produces exactly the same recommendation (structurally guaranteed by
`DecisionReportV2.__post_init__`, see `types.py`). What v2 ADDS is a per-candidate Context Memory
attachment: an explainable account of what similar historical contexts existed and how the candidate's
own edge performed in them, entirely for a human (or a future, separately-authorized Checkpoint) to
read -- Context Memory's evidence NEVER feeds back into eligibility, ranking, scoring, sizing, or
execution here. Decision Intelligence v1 (`ai_trader.decision_intelligence`) is called UNMODIFIED and is
the sole source of the actual recommendation; this module never re-implements or duplicates its
eligibility/ranking logic.

Completely independent from Signal Engine, Scoring Engine, Risk Manager, Shadow Evidence, and Execution
Engine, same as v1 -- none of those packages is imported anywhere in this one, and Context Memory itself
remains untouched by this integration (nothing here writes to `ai_trader.context_memory`'s repository).
"""

from __future__ import annotations

from pathlib import Path

from ai_trader.context_memory import EvidencePolicy, HistoricalIndex, OutcomeKind, RetrievalQuery, aggregate_evidence, retrieve
from ai_trader.decision_intelligence.engine import make_decision
from ai_trader.decision_intelligence.types import ResearchStats
from ai_trader.decision_intelligence_v2.adapters import build_context_snapshot
from ai_trader.decision_intelligence_v2.explanation import explain_candidate
from ai_trader.decision_intelligence_v2.types import CandidateEvidence, DecisionCandidateV2, DecisionReportV2
from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.strategy_runtime.context_access import MarketContext


def make_decision_v2(
    context: MarketContext,
    context_memory_index: HistoricalIndex | None = None,
    research_stats: dict[str, ResearchStats] | None = None,
    library_path: Path | None = None,
    evidence_policy: EvidencePolicy | None = None,
) -> DecisionReportV2:
    """The v2 public entry point. ``context_memory_index`` is OPTIONAL: when `None` (no accumulated
    Context Memory history is available yet -- the expected state until a future, separately-authorized
    checkpoint populates one from real backtests), every candidate's own ``context_evidence`` is `None`
    ("Context Memory was not consulted"), an honest, disclosed degenerate case, never an error."""
    v1_report = make_decision(context, research_stats, library_path)

    candidates_v2: list[DecisionCandidateV2] = []
    if context_memory_index is not None:
        mi_snapshot = build_market_intelligence(context)
        query_snapshot = build_context_snapshot(mi_snapshot)
        for candidate in v1_report.candidates:
            query = RetrievalQuery(
                context_snapshot=query_snapshot, as_of_cutoff=query_snapshot.as_of,
                edge_scope=(candidate.strategy_id,),
            )
            retrieval = retrieve(context_memory_index, query)
            evidence = aggregate_evidence(
                context_memory_index, retrieval, candidate.strategy_id, OutcomeKind.STRATEGY, evidence_policy,
            )
            explanation = explain_candidate(retrieval, evidence)
            candidates_v2.append(
                DecisionCandidateV2(
                    candidate=candidate,
                    context_evidence=CandidateEvidence(
                        retrieval_status=retrieval.status, evidence=evidence, explanation=explanation,
                    ),
                )
            )
    else:
        candidates_v2 = [DecisionCandidateV2(candidate=c, context_evidence=None) for c in v1_report.candidates]

    return DecisionReportV2(
        v1_report=v1_report, candidates=tuple(candidates_v2),
        recommended_strategy_id=v1_report.recommended_strategy_id,
    )
