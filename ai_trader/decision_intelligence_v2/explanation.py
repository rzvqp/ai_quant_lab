"""Pure explanation narration -- Phase 7 Checkpoint 14.

Every string produced here names a concrete, already-computed value from a `RetrievalResult`/
`ContextualEvidenceReport` -- never a vague phrase, never a hidden score. This is the CEO's own explicit
Checkpoint 14 requirement made literal: every recommendation must be able to explain why the context was
found, what historical evidence exists, what limitations exist, and why the evidence status is what it
is. No opaque algorithm.
"""

from __future__ import annotations

from ai_trader.context_memory import ContextualEvidenceReport, RetrievalResult, RetrievalStatus


def explain_retrieval(retrieval: RetrievalResult) -> tuple[str, ...]:
    """Why a historical context was (or was not) found."""
    if retrieval.status is RetrievalStatus.SUCCESSFUL:
        lines = [
            f"Historical context found at relaxation tier {retrieval.selected_relaxation_tier}: "
            f"{retrieval.returned_count} matching episode(s) returned out of "
            f"{retrieval.eligible_episode_count} eligible episode(s) "
            f"({retrieval.raw_eligible_observation_count} raw observation(s))."
        ]
        if retrieval.matches:
            best = retrieval.matches[0]
            lines.append(
                "Best match: matched dimensions "
                f"{', '.join(best.matched_dimensions)}; relaxed dimensions "
                f"{', '.join(best.relaxed_dimensions) if best.relaxed_dimensions else '(none -- exact match)'}."
            )
        lines.extend(f"Retrieval limitation: {lim}" for lim in retrieval.limitations)
        return tuple(lines)

    reason = retrieval.no_sufficient_history_reason or ", ".join(retrieval.exclusion_reasons) or "no reason disclosed"
    return (f"No historical context retrieved (status={retrieval.status.value}): {reason}.",)


def explain_evidence(evidence: ContextualEvidenceReport) -> tuple[str, ...]:
    """What historical evidence exists, and why the evidence status is what it is."""
    lines = [f"Evidence status: {evidence.evidence_status.value} -- {evidence.evidence_status_reason}"]
    if evidence.resolved_outcome_count > 0:
        summary = f"{evidence.resolved_outcome_count} resolved episode(s) (of {evidence.episode_count} PRESENT-edge episode(s) retrieved)"
        if (
            evidence.mean_normalized_result is not None
            and evidence.median_normalized_result is not None
            and evidence.contextual_win_rate is not None
        ):
            summary += (
                f": mean={evidence.mean_normalized_result:.4f}, median={evidence.median_normalized_result:.4f}, "
                f"win_rate={evidence.contextual_win_rate:.2%}"
            )
        lines.append(summary + ".")
        if evidence.confidence_interval_95 is not None:
            lo, hi = evidence.confidence_interval_95
            lines.append(f"95% confidence interval (normal-approximation, descriptive only): [{lo:.4f}, {hi:.4f}].")
    lines.extend(f"Evidence limitation: {lim}" for lim in evidence.limitations)
    return tuple(lines)


def explain_candidate(retrieval: RetrievalResult, evidence: ContextualEvidenceReport | None) -> tuple[str, ...]:
    """The full, per-candidate explanation: retrieval narration, then evidence narration (if any)."""
    lines = list(explain_retrieval(retrieval))
    if evidence is not None:
        lines.extend(explain_evidence(evidence))
    return tuple(lines)
