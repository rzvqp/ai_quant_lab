"""Decision Intelligence v2 -- Phase 7 Checkpoint 14.

A SEPARATE system from Decision Intelligence v1 (`ai_trader.decision_intelligence`), which remains
unmodified and unreplaced. v2 calls v1's own `make_decision()` untouched and attaches, per candidate, an
explainable Context Memory evidence report -- never allowed to change the recommendation
(`DecisionReportV2.__post_init__` enforces this structurally). Context Memory is consumed strictly as an
evidence source here: no eligibility change, no edge elimination, no ranking change, no scoring change,
no Risk/Position Sizing/Execution change, no BUY/SELL generation. Decision Intelligence remains the sole
party responsible for the recommendation.
"""

from __future__ import annotations

from ai_trader.decision_intelligence_v2.adapters import build_context_snapshot, build_present_edge_reference
from ai_trader.decision_intelligence_v2.engine import make_decision_v2
from ai_trader.decision_intelligence_v2.explanation import explain_candidate, explain_evidence, explain_retrieval
from ai_trader.decision_intelligence_v2.types import CandidateEvidence, DecisionCandidateV2, DecisionReportV2

__all__ = [
    "build_context_snapshot",
    "build_present_edge_reference",
    "make_decision_v2",
    "explain_candidate",
    "explain_evidence",
    "explain_retrieval",
    "CandidateEvidence",
    "DecisionCandidateV2",
    "DecisionReportV2",
]
