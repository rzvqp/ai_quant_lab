"""Explanation-quality comparison -- Phase 7 Checkpoint 15. A deterministic completeness checklist,
never a subjective "quality" score -- checks whether v2's per-candidate Context Memory attachment
discloses all four categories the CEO's own Checkpoint 14 directive requires."""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.decision_comparison.types import ExplanationQualityResult
from ai_trader.decision_intelligence_v2.types import DecisionReportV2


def score_explanation_quality(v2_reports: Sequence[DecisionReportV2]) -> ExplanationQualityResult:
    n_with_evidence = 0
    n_why_found = 0
    n_evidence_disclosed = 0
    n_limitations_when_present = 0
    n_status_reason = 0

    for report in v2_reports:
        for candidate in report.candidates:
            ce = candidate.context_evidence
            if ce is None:
                continue
            n_with_evidence += 1
            text = " ".join(ce.explanation).lower()

            if "context found" in text or "no historical context retrieved" in text:
                n_why_found += 1

            if ce.evidence is not None and ce.evidence.resolved_outcome_count > 0:
                if "resolved episode" in text:
                    n_evidence_disclosed += 1
            else:
                n_evidence_disclosed += 1  # nothing to disclose -- vacuously satisfied

            if ce.evidence is not None:
                n_status_reason += 1 if "evidence status" in text else 0
                has_real_limitations = bool(ce.evidence.limitations)
                if not has_real_limitations or "limitation" in text:
                    n_limitations_when_present += 1
            else:
                n_limitations_when_present += 1  # nothing to disclose -- vacuously satisfied

    return ExplanationQualityResult(
        n_v2_reports=len(v2_reports),
        n_candidates_with_context_evidence=n_with_evidence,
        n_candidates_disclosing_why_found=n_why_found,
        n_candidates_disclosing_evidence=n_evidence_disclosed,
        n_candidates_disclosing_limitations_when_present=n_limitations_when_present,
        n_candidates_disclosing_status_reason=n_status_reason,
        # v1 has ZERO Context-Memory-derived content on any candidate -- whenever v2 attaches evidence
        # to even one candidate, it strictly adds explanatory content v1 could never have produced.
        v2_strictly_more_explanatory_content=n_with_evidence > 0,
    )
