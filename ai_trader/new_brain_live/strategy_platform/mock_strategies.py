"""Deterministic MOCK strategies (AI Trader New Brain Architecture mandate, section 11) -- engineering
test fixtures ONLY, never Alpha, never broker-eligible, no profitability claims. Every one of these is
registered in a catalog with `status=StrategyStatus.MOCK_TEST_ONLY`, checked and enforced (not merely
documented) by `pipeline.py` and `tests/test_mock_strategies_never_broker_eligible.py`."""

from __future__ import annotations

import dataclasses

from ai_trader.new_brain_live.market_state import market_state_identity
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.signal_engine.types import Direction

MOCK_STRATEGY_CONFIG_FINGERPRINT = "mock-fixture-v1"
"""Every mock strategy shares this one fingerprint -- they have no real, versioned config; a single,
explicit, obviously-fake constant, never derived from anything that could be mistaken for a real
strategy's own fingerprint."""


def _fixed_hypothesis(
    *, strategy_id: str, strategy_version: str, instrument: str, direction: Direction, entry: float,
    stop: float, as_of: int, market_state_id: str,
) -> TradeHypothesis:
    return TradeHypothesis(
        strategy_id=strategy_id, strategy_version=strategy_version, instrument=instrument,
        direction=direction, signal_timestamp=as_of, eligible_entry_timestamp=as_of,
        entry_type="MARKET", intended_entry=entry, invalidation=stop, exit_specification="none",
        max_hold=1, expected_edge={"mock_decision": "TRADE"}, reason_codes=("MOCK_FIXTURE_SIGNAL",),
        market_state_identity=market_state_id, strategy_config_fingerprint=MOCK_STRATEGY_CONFIG_FINGERPRINT,
        research_validation_identity=None, provenance="mock_strategies.py",
    )


@dataclasses.dataclass(frozen=True, slots=True)
class MockAlwaysNoTrade:
    """NO_SIGNAL unconditionally -- proves the pipeline handles a strategy that never signals without
    treating that as an error."""

    strategy_id: str = "MOCK_ALWAYS_NO_TRADE"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        return None


@dataclasses.dataclass(frozen=True, slots=True)
class MockLongOnFixedFixture:
    """Deterministic LONG signal every time it is evaluated -- proves the positive TRADE_DECISION path
    end to end (Router -> EV -> Risk -> Execution -> Shadow Ledger), with the broker gate still blocking
    at the very end regardless."""

    strategy_id: str = "MOCK_LONG_ON_FIXED_FIXTURE"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        entry = state.entry_price if state.entry_price is not None else 100.0
        return _fixed_hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            direction=Direction.LONG, entry=entry, stop=entry - 1.0, as_of=state.market_timestamp,
            market_state_id=market_state_identity(state),
        )


@dataclasses.dataclass(frozen=True, slots=True)
class MockShortOnFixedFixture:
    """Deterministic SHORT signal every time it is evaluated -- the mirror of `MockLongOnFixedFixture`."""

    strategy_id: str = "MOCK_SHORT_ON_FIXED_FIXTURE"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        entry = state.entry_price if state.entry_price is not None else 100.0
        return _fixed_hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            direction=Direction.SHORT, entry=entry, stop=entry + 1.0, as_of=state.market_timestamp,
            market_state_id=market_state_identity(state),
        )


@dataclasses.dataclass(frozen=True, slots=True)
class MockConflictA:
    """Fires LONG on the SAME MarketState `MockConflictB` fires SHORT on -- the section 16 fixture for
    "multiple, directionally conflicting hypotheses on one market state." Deliberately no relationship
    to `MockConflictB` beyond both being eligible on the same fixture; nothing here resolves the
    conflict -- the pipeline must handle it, not this class."""

    strategy_id: str = "MOCK_CONFLICT_A"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        entry = state.entry_price if state.entry_price is not None else 100.0
        return _fixed_hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            direction=Direction.LONG, entry=entry, stop=entry - 1.0, as_of=state.market_timestamp,
            market_state_id=market_state_identity(state),
        )


@dataclasses.dataclass(frozen=True, slots=True)
class MockConflictB:
    strategy_id: str = "MOCK_CONFLICT_B"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        entry = state.entry_price if state.entry_price is not None else 100.0
        return _fixed_hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            direction=Direction.SHORT, entry=entry, stop=entry + 1.0, as_of=state.market_timestamp,
            market_state_id=market_state_identity(state),
        )
