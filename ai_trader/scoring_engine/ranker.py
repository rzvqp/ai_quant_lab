"""The Ranker (``SCORING_ENGINE_ARCHITECTURE.md`` §5) — deterministic ordering + ``rank`` assignment
(``SCORING_MODEL.md`` §7). A batch barrier: needs every score in the group at once, so parallelism in
earlier stages never changes the final order (architecture §9).
"""

from __future__ import annotations

from dataclasses import replace

from ai_trader.scoring_engine.types import OpportunityScore


def rank_scores(scores: list[OpportunityScore]) -> tuple[OpportunityScore, ...]:
    """Sort by ``total_score`` desc, ``historical_confidence`` desc, ``signal_strength`` desc,
    ``strategy_id`` asc (``SCORING_MODEL.md`` §7 — the last key guarantees a total order, so there is
    never a stochastic tie-break), then stamp ``rank`` (1 = best) from that order."""
    ordered = sorted(
        scores,
        key=lambda s: (
            -s.total_score,
            -s.component_scores.historical_confidence,
            -s.component_scores.signal_strength,
            s.strategy_id,
        ),
    )
    return tuple(replace(s, rank=i + 1) for i, s in enumerate(ordered))
