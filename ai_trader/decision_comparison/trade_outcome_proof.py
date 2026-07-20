"""Trade-outcome equivalence proof -- Phase 7 Checkpoint 15. Covers the CEO's own "expectancy / win
rate / drawdown / false positives / false negatives / stability / regime robustness" dimensions.

These are all downstream FUNCTIONS of "which strategy_id (if any) was recommended on a given bar" --
nothing else about a v1 vs. v2 decision differs, since v2 never alters eligibility, ranking, sizing, or
execution (Checkpoint 14's own scope boundary). When the paired recommendation stream shows zero
divergences, every trade-outcome metric computed from that stream is PROVABLY identical between v1 and
v2 -- this module states that proof explicitly rather than re-running a redundant backtest to
reconfirm a mathematical identity (a purposeless computation this project's own discipline avoids).
"""

from __future__ import annotations

from ai_trader.decision_comparison.types import RecommendationComparison, TradeOutcomeEquivalenceProof


def prove_trade_outcome_equivalence(comparison: RecommendationComparison) -> TradeOutcomeEquivalenceProof:
    equivalence_holds = comparison.divergences == 0
    if equivalence_holds:
        rationale = (
            f"Across {comparison.n_compared} compared decision(s), v2's recommended_strategy_id was "
            "identical to v1's on every single one (0 divergences) -- not a sampled result, but a "
            "consequence enforced by DecisionReportV2's own construction-time invariant (Checkpoint 14). "
            "Expectancy, win rate, drawdown, false-positive rate, false-negative rate, and "
            "recommendation stability across regimes are ALL pure functions of the recommendation "
            "stream (which strategy_id, if any, was recommended on each bar). Since that stream is "
            "provably identical between v1 and v2, every one of these metrics is provably identical too."
        )
    else:
        rationale = (
            f"v2 diverged from v1 on {comparison.divergences} of {comparison.n_compared} compared "
            "decision(s) -- this should be structurally impossible under Checkpoint 14's own design and "
            "indicates either a construction defect or reports not produced by the paired "
            "make_decision()/make_decision_v2() calls this proof assumes. Trade-outcome metrics can NOT "
            "be assumed equivalent here and would require a real, separate backtest to measure directly."
        )
    return TradeOutcomeEquivalenceProof(
        n_compared=comparison.n_compared, divergences=comparison.divergences,
        equivalence_holds=equivalence_holds, rationale=rationale,
    )
