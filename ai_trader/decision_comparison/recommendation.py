"""Recommendation-level comparison -- Phase 7 Checkpoint 15. Covers the CEO's own "final recommendation
/ NO TRADE frequency / edge selection" dimensions, computed directly from paired observations, never
assumed."""

from __future__ import annotations

from collections.abc import Sequence

from ai_trader.decision_comparison.types import RecommendationComparison
from ai_trader.decision_intelligence.types import DecisionReport
from ai_trader.decision_intelligence_v2.types import DecisionReportV2


def compare_recommendations(
    pairs: Sequence[tuple[DecisionReport, DecisionReportV2]],
) -> RecommendationComparison:
    n = len(pairs)
    divergences = 0
    divergent_as_of: list[int] = []
    no_trade_v1 = 0
    no_trade_v2 = 0
    edge_counts_v1: dict[str, int] = {}
    edge_counts_v2: dict[str, int] = {}
    agreements = 0

    for v1, v2 in pairs:
        if v1.recommended_strategy_id != v2.recommended_strategy_id:
            divergences += 1
            divergent_as_of.append(v1.as_of)
        else:
            agreements += 1

        if v1.recommended_strategy_id is None:
            no_trade_v1 += 1
        else:
            edge_counts_v1[v1.recommended_strategy_id] = edge_counts_v1.get(v1.recommended_strategy_id, 0) + 1

        if v2.recommended_strategy_id is None:
            no_trade_v2 += 1
        else:
            edge_counts_v2[v2.recommended_strategy_id] = edge_counts_v2.get(v2.recommended_strategy_id, 0) + 1

    return RecommendationComparison(
        n_compared=n,
        divergences=divergences,
        divergence_rate=(divergences / n) if n else 0.0,
        no_trade_count_v1=no_trade_v1,
        no_trade_count_v2=no_trade_v2,
        no_trade_frequency_v1=(no_trade_v1 / n) if n else 0.0,
        no_trade_frequency_v2=(no_trade_v2 / n) if n else 0.0,
        edge_selection_counts_v1=edge_counts_v1,
        edge_selection_counts_v2=edge_counts_v2,
        edge_selection_agreement_rate=(agreements / n) if n else 0.0,
        divergent_as_of=tuple(divergent_as_of),
    )
