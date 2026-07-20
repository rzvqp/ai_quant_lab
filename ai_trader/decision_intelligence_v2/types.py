"""Data structures for Decision Intelligence v2 -- Phase 7 Checkpoint 14.

Every type here embeds Decision Intelligence v1's own output VERBATIM rather than recomputing it --
Context Memory's evidence is attached ALONGSIDE the v1 decision, never allowed to change it.
`DecisionReportV2.__post_init__` enforces this structurally: constructing a `DecisionReportV2` whose own
`recommended_strategy_id` disagrees with the embedded `v1_report.recommended_strategy_id` raises,
guaranteeing by construction (not by convention) that this integration cannot silently redirect a
trading decision -- the CEO's own explicit Checkpoint 14 rule ("Context Memory NU are voie sa ...
modifice ranking-ul ... genereze BUY/SELL. Decision Intelligence ramane singurul responsabil pentru
recomandare").
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.context_memory import ContextualEvidenceReport, RetrievalStatus
from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionReport


@dataclass(frozen=True)
class CandidateEvidence:
    """One candidate's own Context Memory attachment -- purely explanatory. `evidence` is `None` only
    when retrieval itself did not succeed (`retrieval_status` explains why); `explanation` is always a
    non-empty, human-readable disclosure of why the context was (or was not) found, what historical
    evidence exists, what limitations apply, and why the evidence status is what it is -- never an
    opaque score."""

    retrieval_status: RetrievalStatus
    evidence: ContextualEvidenceReport | None
    explanation: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.explanation:
            raise ValueError(
                "CandidateEvidence requires at least one disclosed explanation line -- an opaque "
                "attachment with no reasoning is exactly what this integration must never produce"
            )


@dataclass(frozen=True)
class DecisionCandidateV2:
    """One PRESENT edge's v1 verdict (unmodified) plus its own Context Memory evidence attachment.
    ``context_evidence`` is `None` only when Context Memory was not consulted at all for this decision
    (no `HistoricalIndex` was supplied) -- distinguishable from "consulted, found nothing"
    (`CandidateEvidence` with a non-SUCCESSFUL `retrieval_status`)."""

    candidate: DecisionCandidate
    context_evidence: CandidateEvidence | None


@dataclass(frozen=True)
class DecisionReportV2:
    """The v2 report. `v1_report` is Decision Intelligence v1's own, complete, unmodified
    `DecisionReport` -- the sole source of the actual recommendation. `recommended_strategy_id` is
    validated to be byte-identical to `v1_report.recommended_strategy_id` (see module docstring)."""

    v1_report: DecisionReport
    candidates: tuple[DecisionCandidateV2, ...]
    recommended_strategy_id: str | None

    def __post_init__(self) -> None:
        if self.recommended_strategy_id != self.v1_report.recommended_strategy_id:
            raise ValueError(
                "DecisionReportV2.recommended_strategy_id must exactly match v1_report."
                "recommended_strategy_id -- Context Memory must never change the recommendation "
                f"(got v2={self.recommended_strategy_id!r}, v1={self.v1_report.recommended_strategy_id!r})"
            )
