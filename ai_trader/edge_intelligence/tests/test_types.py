"""Unit tests for :mod:`ai_trader.edge_intelligence.types`."""

from __future__ import annotations

import pytest

from ai_trader.edge_intelligence.types import EdgeState, StrategyEdgeReading


def test_strategy_edge_reading_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError, match="at least one evidence item"):
        StrategyEdgeReading(strategy_id="S1", as_of=0, state=EdgeState.POSSIBLE, evidence=())
