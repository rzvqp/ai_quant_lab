"""Deterministic combination of evidence items into one :class:`EdgeState` -- Phase 7 Checkpoint
6. A single, disclosed rule, never a weighted score or learned model: any CONTRADICTS is a hard
disqualifier (ABSENT); with no contradiction, any UNKNOWN means the evidence is incomplete
(POSSIBLE); only when every checked dimension is resolved and at least one genuinely SUPPORTS the
edge is it called PRESENT; a snapshot with every dimension NEUTRAL has no evidence either way, so
it is POSSIBLE, never PRESENT.
"""

from __future__ import annotations

from ai_trader.edge_intelligence.types import EdgeEvidenceItem, EdgeState, EvidenceContribution


def determine_edge_state(evidence: tuple[EdgeEvidenceItem, ...]) -> EdgeState:
    contributions = {item.contribution for item in evidence}
    if EvidenceContribution.CONTRADICTS in contributions:
        return EdgeState.ABSENT
    if EvidenceContribution.UNKNOWN in contributions:
        return EdgeState.POSSIBLE
    if EvidenceContribution.SUPPORTS in contributions:
        return EdgeState.PRESENT
    return EdgeState.POSSIBLE
