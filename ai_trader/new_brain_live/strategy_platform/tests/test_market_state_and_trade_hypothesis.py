"""`MarketState` alias correctness + `TradeHypothesis`/`EVDecision` schema validation and determinism."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.new_brain_live.dual_clock.upstream_context import CachedUpstreamContext
from ai_trader.new_brain_live.market_state import MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform.ev_engine import NO_TRADE, TRADE_DECISION, EVDecision, MockEVDecisionEngine
from ai_trader.new_brain_live.strategy_platform.tests._fixtures import real_trend_up_market_state
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.signal_engine.types import Direction


def test_market_state_is_literally_cached_upstream_context_no_duplicate_class() -> None:
    assert MarketState is CachedUpstreamContext


def test_market_state_identity_matches_context_id() -> None:
    state = real_trend_up_market_state()
    assert market_state_identity(state) == state.context_id
    assert market_state_identity(state) != ""


def _hypothesis(**overrides: object) -> TradeHypothesis:
    kwargs: dict[str, object] = {
        "strategy_id": "S1", "strategy_version": "v1", "instrument": "XAUUSD", "direction": Direction.LONG,
        "signal_timestamp": 100, "eligible_entry_timestamp": 100, "entry_type": "MARKET",
        "intended_entry": 2000.0, "invalidation": 1990.0, "exit_specification": "none", "max_hold": 1,
        "expected_edge": None, "reason_codes": ("TEST",), "market_state_identity": "ms-1",
        "strategy_config_fingerprint": "fp-1", "research_validation_identity": None, "provenance": "test",
    }
    kwargs.update(overrides)
    return TradeHypothesis(**kwargs)  # type: ignore[arg-type]


def test_trade_hypothesis_rejects_long_with_stop_above_entry() -> None:
    with pytest.raises(ValueError, match="LONG requires invalidation"):
        _hypothesis(direction=Direction.LONG, intended_entry=2000.0, invalidation=2010.0)


def test_trade_hypothesis_rejects_short_with_stop_below_entry() -> None:
    with pytest.raises(ValueError, match="SHORT requires invalidation"):
        _hypothesis(direction=Direction.SHORT, intended_entry=2000.0, invalidation=1990.0)


def test_trade_hypothesis_dedup_key_is_strategy_instrument_market_state() -> None:
    h = _hypothesis(strategy_id="S1", instrument="XAUUSD", market_state_identity="ms-42")
    assert h.dedup_key == ("S1", "XAUUSD", "ms-42")


def test_mock_ev_engine_trades_only_on_explicit_fixture_flag() -> None:
    engine = MockEVDecisionEngine()
    trade_h = _hypothesis(expected_edge={"mock_decision": "TRADE"})
    no_trade_h = _hypothesis(expected_edge={"mock_decision": "NO_TRADE"})
    missing_h = _hypothesis(expected_edge=None)

    assert engine.decide(trade_h).decision == TRADE_DECISION
    assert engine.decide(no_trade_h).decision == NO_TRADE
    assert engine.decide(missing_h).decision == NO_TRADE


def test_ev_decision_requires_reason_codes_on_no_trade() -> None:
    with pytest.raises(ValueError, match="reason code"):
        EVDecision(hypothesis=_hypothesis(), decision=NO_TRADE, reason_codes=())
