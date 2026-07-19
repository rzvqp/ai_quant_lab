"""Unit tests for :mod:`ai_trader.decision_intelligence.types`."""

from __future__ import annotations

import pytest

from ai_trader.decision_intelligence.types import DecisionCandidate, DecisionOutcome, ResearchStats


def test_research_stats_rejects_negative_n_trades() -> None:
    with pytest.raises(ValueError, match="n_trades must be >= 0"):
        ResearchStats(n_trades=-1, win_rate=None, expectancy_r=None, sharpe_ratio=None)


def test_decision_candidate_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError, match="at least one evidence item"):
        DecisionCandidate(
            strategy_id="S1", outcome=DecisionOutcome.REJECT, confidence="NONE", evidence=(), explanation="test",
        )
